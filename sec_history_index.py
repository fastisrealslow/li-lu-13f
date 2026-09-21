"""Independent SEC quarterly-index discovery for holes in submissions JSON.

An index date is a filing date, never a portfolio date. Bind candidates to the
original submission header before using them; Form D and additive amendments
cannot supply a complete 13F portfolio. Index misses never create zero holdings.
"""
import gzip
import re
from datetime import datetime, timezone, timedelta

FORMS = {'13F-HR', '13F-HR/A', '13F-NT', '13F-NT/A'}
SCHEMA = 1


def stamp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def index_keys(quarters):
    """Normal filing quarter plus the following quarter for delayed filings."""
    result = set()
    now = datetime.now(timezone.utc)
    current = now.year * 4 + (now.month - 1) // 3
    for quarter in quarters:
        match = re.fullmatch(r'(\d{4}) Q([1-4])', quarter)
        if not match:
            raise ValueError('Invalid requested report quarter')
        start = int(match[1]) * 4 + int(match[2]) - 1
        for offset in (1, 2):
            i = start + offset
            if i <= current:
                result.add(f'{i // 4}/QTR{i % 4 + 1}')
    return sorted(result)


def parse_index(raw, cik):
    body = gzip.decompress(raw).decode('utf-8', errors='replace')
    if 'CIK|Company Name|Form Type|Date Filed|Filename' not in body:
        raise ValueError('Unrecognized SEC master index; not an empty search')
    records, valid_rows = [], 0
    for line in body.splitlines():
        cells = line.split('|')
        if len(cells) != 5 or not cells[0].isdigit():
            continue
        valid_rows += 1
        number, name, form, filed, path = cells
        if int(number) != int(cik) or form not in FORMS:
            continue
        match = re.fullmatch(r'edgar/data/(\d+)/(\d{10}-\d{2}-\d{6})\.txt', path)
        if not match or int(match[1]) != int(cik):
            raise ValueError('Unexpected SEC submission path')
        datetime.strptime(filed, '%Y-%m-%d')
        records.append(dict(accessionDashed=match[2], accession=match[2].replace('-', ''),
                            filingDate=filed, form=form, manager=name, submissionPath='/Archives/'+path))
    if not valid_rows:
        raise ValueError('SEC index has no recognizable entries')
    return records


def bind_submission(raw, candidate, cik):
    body = raw.decode('utf-8', errors='replace')
    header = body.split('</SEC-HEADER>', 1)[0]
    def field(name):
        match = re.search(r'^\s*'+name+r':\s*([^\r\n]+)', header, re.M)
        if not match:
            raise ValueError('SEC submission header missing '+name)
        return match[1].strip()
    if int(field('CENTRAL INDEX KEY')) != int(cik) or field('ACCESSION NUMBER') != candidate['accessionDashed']:
        raise ValueError('Submission CIK/accession differs from index')
    if field('CONFORMED SUBMISSION TYPE') != candidate['form']:
        raise ValueError('Submission form differs from index')
    filed = datetime.strptime(field('FILED AS OF DATE'), '%Y%m%d').strftime('%Y-%m-%d')
    if filed != candidate['filingDate']:
        raise ValueError('Submission filing date differs from index')
    period = datetime.strptime(field('CONFORMED PERIOD OF REPORT'), '%Y%m%d').strftime('%Y-%m-%d')
    amendment = re.search(r'<(?:\w+:)?amendmentType>\s*([^<]+)', body, re.I)
    amendment = amendment[1].strip().upper() if amendment else ''
    complete = candidate['form'] == '13F-HR' or (candidate['form'] == '13F-HR/A' and amendment == 'RESTATEMENT')
    return {**candidate, 'reportDate':period, 'completePortfolio':complete,
            'amendmentType':amendment, 'source':'sec_quarterly_master_index',
            'submissionUrl':'https://www.sec.gov'+candidate['submissionPath']}


def discover(cik, quarters, fetch, previous=None, max_indexes=8, max_candidates=16):
    """Return dated complete-portfolio candidates and auditable lookup outcomes."""
    previous = previous or {}
    cache = previous.get('indexes', {}) if previous.get('schemaVersion') == SCHEMA and previous.get('cik') == str(cik) else {}
    keys = index_keys(quarters)
    indexes, errors, deferred, found = {}, [], [], {}
    requests = 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    for key in keys:
        url = 'https://www.sec.gov/Archives/edgar/full-index/'+key+'/master.gz'
        old = cache.get(key, {})
        try:
            recent = datetime.fromisoformat(old.get('checkedAt', '').replace('Z', '+00:00')) >= cutoff
        except ValueError:
            recent = False
        if old.get('status') == 'checked' and recent and old.get('url') == url:
            entry = old
        elif requests >= max_indexes:
            deferred.append(key)
            continue
        else:
            requests += 1
            try:
                rows = parse_index(fetch(url.removeprefix('https://www.sec.gov')), cik)
                entry = {'status':'checked','checkedAt':stamp(),'url':url,'filings':rows}
            except Exception as exc:
                entry = {'status':'failed','checkedAt':stamp(),'url':url,'error':str(exc)}
        indexes[key] = entry
        if entry['status'] != 'checked':
            errors.append({'url':url,'reason':entry.get('error','Index fetch failed')})
        for row in entry.get('filings', []):
            found[row['accessionDashed']] = row
    resolved_cache = previous.get('resolved', {}) if previous.get('cik') == str(cik) else {}
    resolved, filings, related = {}, [], []
    requests = 0
    for accession, candidate in sorted(found.items()):
        try:
            old = resolved_cache.get(accession)
            if old and all(old.get(k) == candidate.get(k) for k in ('submissionPath','filingDate','form')):
                filing = old
            elif requests < max_candidates:
                requests += 1
                filing = bind_submission(fetch(candidate['submissionPath']), candidate, cik)
            else:
                deferred.append(accession)
                continue
            resolved[accession] = filing
            d = datetime.strptime(filing['reportDate'], '%Y-%m-%d')
            quarter = f'{d.year} Q{(d.month-1)//3+1}'
            if quarter in quarters:
                related.append(filing)
                if filing['completePortfolio']:
                    filings.append(filing)
        except Exception as exc:
            errors.append({'accession':accession,'reason':str(exc)})
    checks = [e['checkedAt'] for e in indexes.values() if e.get('status') == 'checked']
    partial = bool(errors or deferred or len(indexes) != len(keys))
    audit = dict(schemaVersion=SCHEMA, cik=str(cik), checkedAt=max(checks) if checks else None,
                 attemptedAt=stamp(), status='partial' if partial else 'checked',
                 indexes=indexes, resolved=resolved, errors=errors, deferred=deferred,
                 requestedQuarters=list(quarters), candidateFilings=related,
                 scope='SEC季度总索引：报告期之后两个申报季度；同一CIK。未检索到不等于未持仓或未申报。')
    return sorted(filings, key=lambda r:(r['reportDate'],r['filingDate']), reverse=True), audit
