"""HKEX DI evidence pipeline for every investor in investors.json.

The official notice table supplies event-dated positions. A matching Form 1/2
binds each security/entity list to a stock code and verifies the newest position.
No observation, search miss, or stale disclosure is a current holding assertion.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import http.cookiejar
import json
import math
from pathlib import Path
import re
import threading
import time
from urllib.parse import urljoin, urlsplit, parse_qs, urlencode, urlunsplit
from urllib.request import build_opener, HTTPCookieProcessor

from bs4 import BeautifulSoup

ORIGIN = 'https://di.hkex.com.hk'
BASE = ORIGIN + '/di/'
LEGACY = ORIGIN + '/filing/di/'
SCHEMA = 3
_RATE_LOCK = threading.Lock()
_LAST_REQUEST = 0.0


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def official_url(url):
    u = urlsplit(url)
    return u.scheme == 'https' and u.netloc == 'di.hkex.com.hk' and u.path.startswith(('/di/', '/filing/di/'))


def canonical_entity(name):
    name = re.split(r'\(\s*(?:formerly|previously)', name, flags=re.I)[0]
    return re.sub(r'[^\w]', '', name).casefold()


def entity_matches(name, aliases):
    return canonical_entity(name) in {canonical_entity(a) for a in aliases}


def text(node):
    return node.get_text(' ', strip=True) if node else ''


def dated(value):
    m = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', value)
    if not m:
        raise ValueError('Missing event date')
    return datetime.strptime(m[1], '%d/%m/%Y').strftime('%Y-%m-%d')


def long_number(value, integer=False):
    # Never use a short position or a transaction quantity as a long holding.
    matches = re.findall(r'(?<![\w,.+\-])((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*\(\s*L\s*\)', value, re.I)
    if len(matches) != 1:
        raise ValueError(f'Expected one long position: {value!r}')
    n = float(matches[0].replace(',', ''))
    if not math.isfinite(n) or n < 0 or integer and not n.is_integer():
        raise ValueError('Invalid position quantity')
    return int(n) if integer else n


def page_info(soup, url):
    body = text(soup)
    total = re.search(r'Total records\s*:\s*([\d,]+)', body, re.I)
    if not total:
        if re.search(r'No (?:record|result)s? (?:was |were )?found|No matching record', body, re.I):
            return 0, []
        raise ValueError('Unrecognized HKEX result page (not an empty result)')
    pages = []
    current = urlsplit(url)
    identity = {k:v for k,v in parse_qs(current.query).items() if k != 'pg'}
    for a in soup.find_all('a', href=True):
        link = urljoin(url, a['href'])
        target = urlsplit(link)
        query = parse_qs(target.query)
        if query.get('pg', ['1']) == parse_qs(current.query).get('pg', ['1']):
            continue
        if official_url(link) and target.path == current.path and query.get('pg', [''])[0].isdigit():
            if all(query.get(k) == v for k,v in identity.items() if k not in ('g_lang',)):
                pages.append(link)
    return int(total[1].replace(',', '')), pages


def parse_search(html, url, aliases):
    soup = BeautifulSoup(html, 'html.parser')
    total, pages = page_info(soup, url)
    hits = []
    anchors = soup.find_all('a', href=re.compile('NSNoticePersonList\\.aspx', re.I))
    if total and not anchors:
        raise ValueError('Search result links missing; layout may have changed')
    if total > len(anchors) and not pages:
        raise ValueError('Search pagination missing; result incomplete')
    for a in anchors:
        if 'NSNoticePersonList.aspx' not in a['href'] or not entity_matches(text(a), aliases):
            continue
        row = a.find_parent('tr')
        cells = row.find_all(['td','th'], recursive=False) if row else []
        notice = urljoin(url, a['href'])
        if len(cells) >= 2 and official_url(notice):
            hits.append({'entity':text(a), 'stockName':text(cells[1]), 'noticeUrl':notice})
    return hits, total, pages


def filing_identity(value):
    identifier = r'[A-Z]{2}\d{8}[A-Z]?\d+'
    match = re.fullmatch(r'(' + identifier + r')(?:\s*\(\s*(Amendment to|Superseded by)\s+(' + identifier + r')\s*\))?', value)
    if not match:
        raise ValueError('Unrecognized form identifier / revised record marker')
    relation = {'amends': match[3]} if match[2] == 'Amendment to' else {'superseded_by': match[3]} if match[2] else {}
    return match[1], relation


def parse_notices(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    total, pages = page_info(soup, url)
    records, headers, ignored = [], None, []
    for row in soup.find_all('tr'):
        cells = row.find_all(['td','th'], recursive=False)
        values = [text(c) for c in cells]
        if any(v.startswith('Form Serial') for v in values) and len(values) >= 8:
            headers = values
            continue
        if not headers or len(values) != len(headers):
            continue
        links = row.find_all('a', href=re.compile(r'NSForm[123][^/]*\.aspx', re.I))
        if not links:
            continue
        fields = dict(zip(headers, values))
        def field(prefix):
            return next(v for k,v in fields.items() if k.startswith(prefix))
        serial = field('Form Serial')
        try:
            serial, relation = filing_identity(serial)
            form_url = urljoin(url, links[0]['href'])
            if not official_url(form_url):
                raise ValueError('Non-HKEX form URL')
            shares = long_number(field('No. of shares held after'), True)
            pct = long_number(field('% of issued'))
            if pct > 100:
                raise ValueError('Invalid percentage')
            records.append(dict(filing_ref=serial, event_date=dated(field('Date of relevant event')),
                                shares=shares, pct=pct, position='long',
                                issuer_name=field('Name of listed corporation'),
                                reason=field('Reason for disclosure'), source_url=url,
                                form_url=form_url, verification='hkex_notice_table', **relation))
        except (ValueError, StopIteration) as exc:
            ignored.append({'filing_ref':serial, 'reason':str(exc)})
    if total and headers is None:
        raise ValueError('Disclosure column layout changed')
    if total > len(records) + len(ignored) and not pages:
        raise ValueError('Notice pagination missing or rows unrecognized')
    return records, total, pages, ignored


def parse_form(html, url, aliases):
    if not official_url(url):
        raise ValueError('Untrusted form URL')
    soup = BeautifulSoup(html, 'html.parser')
    get = lambda name: text(soup.find(id=name))
    code, serial = get('lblDStockCode'), get('lblDSerialNo') or get('lblDLogNo')
    name = get('lblDName') or ' '.join(filter(None, [get('lblDSurname'),get('lblDFirstname')]))
    if not re.fullmatch(r'\d{4,5}', code) or not serial or not entity_matches(name, aliases):
        raise ValueError(f'Form stock/entity identity mismatch: {code}, {name}')
    table = soup.find(id='grdSh_AEvt')
    long_rows = []
    if table:
        for row in table.find_all('tr'):
            values = [text(c) for c in row.find_all('td', recursive=False)]
            if len(values) == 3 and values[0].casefold() == 'long position':
                long_rows.append(values)
    if len(long_rows) != 1:
        raise ValueError('No unique post-event long position in form')
    shares = int(long_rows[0][1].replace(',', ''))
    pct = float(long_rows[0][2].replace(',', ''))
    if shares < 0 or not math.isfinite(pct) or not 0 <= pct <= 100:
        raise ValueError('Invalid post-event position')
    return dict(ticker=code.zfill(5)+'.HK', filing_ref=serial, entity=name,
                event_date=dated(get('lblDEventDate')), filing_date=dated(get('lblDSignDate')),
                issuer_name=get('lblViewCorpName'), share_class=get('lblDClass'),
                shares=shares, pct=pct, position='long', source_url=url, form_url=url,
                verification='hkex_form', supplementary=get('lblDSuppInfo'))


class Client:
    def __init__(self):
        self.opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.opener.addheaders = [('User-Agent','Mozilla/5.0 (compatible; PublicDisclosureTracker/1.0)'), ('Accept-Language','en')]
        self.cache = {}

    def get(self, url):
        global _LAST_REQUEST
        if not official_url(url):
            raise ValueError('Only public HKEX disclosure URLs are accepted')
        if url in self.cache:
            return self.cache[url]
        error = None
        for attempt in range(2):
            try:
                with _RATE_LOCK:
                    delay = .35 - (time.monotonic() - _LAST_REQUEST)
                    if delay > 0:
                        time.sleep(delay)
                    _LAST_REQUEST = time.monotonic()
                with self.opener.open(url, timeout=22) as response:
                    html = response.read().decode('utf-8', errors='replace')
                self.cache[url] = html
                return html
            except Exception as exc:
                error = exc
                if attempt == 0:
                    time.sleep(1)
        raise OSError(f'HKEX fetch failed: {error}')


def source_key(url):
    u = urlsplit(url)
    q = parse_qs(u.query)
    return u.path + '?' + urlencode({k:q[k][0] for k in ('scpid','scpid1','scpid2','scpid3') if k in q})


def crawl_search(client, url, aliases, max_pages=20):
    queue, visited, hits = [url], set(), []
    while queue:
        if len(visited) >= max_pages:
            raise ValueError('Search pagination limit reached; result incomplete')
        link = queue.pop(0)
        if link in visited:
            continue
        visited.add(link)
        parsed, _, pages = parse_search(client.get(link), link, aliases)
        hits.extend(parsed)
        queue.extend(p for p in pages if p not in visited and p not in queue)
    return list({source_key(h['noticeUrl']):h for h in hits}.values())


def crawl_notices(client, hit, aliases, cached_records, binding=None, max_pages=30):
    url = hit['noticeUrl']
    records, total, pages, ignored = parse_notices(client.get(url), url)
    if not records:
        raise ValueError(f'No usable long-position rows ({total} source records, {len(ignored)} rejected)')
    applicable = [r for r in records if not r.get('superseded_by')]
    if not applicable:
        raise ValueError('No non-superseded long-position disclosure')
    newest = max(applicable, key=lambda r:(r['event_date'],r['filing_ref']))
    # Reuse an already validated exact form, never a guessed security mapping.
    if binding and all(binding.get(k) == newest[k] for k in ('filing_ref', 'event_date', 'shares', 'pct')):
        form = binding
    else:
        form = parse_form(client.get(newest['form_url']),newest['form_url'],aliases)
    if not entity_matches(form['entity'], [hit['entity']]):
        raise ValueError('Form entity disagrees with notice list')
    if (form['filing_ref'],form['event_date'],form['shares'],form['pct']) != (newest['filing_ref'],newest['event_date'],newest['shares'],newest['pct']):
        raise ValueError('Notice table disagrees with the original form')
    previous = {r.get('filing_ref') for r in cached_records}
    # Full history is cached only after every page was read. New runs read page one
    # and stop at previously verified records; unknown pages are still backfilled.
    cached_complete = bool(binding and binding.get('history_complete'))
    queue = [] if cached_complete and all(r['filing_ref'] in previous for r in records) else list(pages)
    visited = {url}
    complete = True
    errors = list(ignored)
    while queue:
        link=queue.pop(0)
        if link in visited:
            continue
        if len(visited) >= max_pages:
            complete=False;errors.append({'reason':'Notice pagination limit reached'});break
        visited.add(link)
        try:
            more, _, further, rejected = parse_notices(client.get(link),link)
            records.extend(more);errors.extend(rejected)
            queue.extend(p for p in further if p not in visited and p not in queue)
        except Exception as exc:
            complete=False;errors.append({'reason':str(exc)})
    by_ref={}
    for record in records:
        record.update(ticker=form['ticker'], entity=hit['entity'], share_class=form['share_class'],
                      source_key=source_key(url), checked_at=now_iso())
        by_ref[record['filing_ref']]=record
    by_ref[form['filing_ref']]={**by_ref[form['filing_ref']],**form}
    binding={**form,'history_complete':complete and not errors,'notice_url':url}
    return list(by_ref.values()),binding,errors


def load_configs(path):
    configs=json.loads(Path(path).read_text())['investors']
    for inv in configs:
        options=inv.get('hkDisclosure',{})
        aliases=options.get('entities') or [inv['manager'],*inv.get('people',[])]
        queries=options.get('queries') or [inv['manager'],*inv.get('people',[])]
        yield {**inv,'hkFile':inv.get('hkFile') or f"{inv['id']}_hk.json",'entities':aliases,'queries':queries}


def run_investor(inv,root,client=None):
    from monitor_hk_disclosures import update_hk_file, normalize_hk_ticker
    root=Path(root);path=root/inv['hkFile'];client=client or Client()
    if not path.exists():
        path.write_text('{"holdings":[]}\n')
    update_hk_file(str(path),[])
    data=json.loads(path.read_text());stamp=now_iso()
    bindings=data.get('source_bindings',{})
    rows={normalize_hk_ticker(h['ticker']):h for h in data['holdings']}
    errors=[];hits={};query_results=[]
    end=datetime.now(timezone.utc).strftime('%d/%m/%Y')
    # Both archives are official and overlap in 2017; deduplicate by form ID.
    for base,start,stop in [(BASE,'03/07/2017',end),(LEGACY,'01/04/2003','02/10/2017')]:
        for query in inv['queries']:
            url=base+'NSSrchPersonList.aspx?'+urlencode(dict(sa1='pl',scsd=start,sced=stop,pn=query,src='MAIN',lang='EN',g_lang='en'))
            try:
                print(f"HK {inv['id']}: search {base.split('/')[-3]} {query}",flush=True)
                found=crawl_search(client,url,inv['entities'])
                hits.update({source_key(h['noticeUrl']):h for h in found})
                query_results.append({'query':query,'archive':'legacy' if base==LEGACY else 'dion','status':'ok','matchedSecurities':len(found),'url':url})
            except Exception as exc:
                errors.append({'query':query,'url':url,'reason':str(exc)})
                query_results.append({'query':query,'status':'failed','url':url})
    # Preserve discoveries across transient search failures. Refresh their date
    # range so a stored search never silently stops before the present day.
    for h in rows.values():
        for hit in h.get('discovery_sources',[]):
            if not entity_matches(hit.get('entity', ''), inv['entities']):
                continue
            key=source_key(hit['noticeUrl'])
            if key not in hits:
                parts=urlsplit(hit['noticeUrl']);q=parse_qs(parts.query)
                if parts.path.startswith('/di/'):
                    q['sced']=[end]
                link=urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode({k:v[0] for k,v in q.items()}),''))
                hits[key]={**hit,'noticeUrl':link}
    collected=[]
    for key,hit in hits.items():
        try:
            print(f"HK {inv['id']}: verify {hit['entity']} / {hit['stockName']}",flush=True)
            cached=[r for h in rows.values() for r in h.get('verified_disclosures',[]) if r.get('source_key')==key]
            records,binding,rejected=crawl_notices(client,hit,inv['entities'],cached,bindings.get(key))
            bindings[key]=binding;ticker=binding['ticker']
            row=rows.setdefault(ticker,dict(ticker=ticker,sector='',evidence_schema=2,verified_disclosures=[]))
            old_name=row.get('name','')
            if old_name and old_name!=hit['stockName']:
                row.setdefault('legacy_name',old_name)
            # Use official issuer text, retaining the old name only for audit.
            row.update(name=hit['stockName'],cnName='',entity=hit['entity'],current_status='unknown',data_quality='verified_historical')
            combined={r['filing_ref']:r for r in row.get('verified_disclosures',[])}
            for r in records:
                combined[r['filing_ref']]=r
            row['verified_disclosures']=sorted(combined.values(),key=lambda r:(r['event_date'],r.get('filing_date',''),r['filing_ref']))
            row['first_disclosure']=row['verified_disclosures'][0]['event_date']
            row['last_disclosure']=row['verified_disclosures'][-1]['event_date']
            row['notes']='港交所原始披露自动核验；数量为对应主体当次披露的多头权益，不合并重复申报主体，不代表当前持仓或历史峰值。'
            discoveries={source_key(h['noticeUrl']):h for h in row.get('discovery_sources',[])}
            discoveries[key]=hit;row['discovery_sources']=list(discoveries.values())
            row['last_checked_at']=stamp;row['evidence_schema']=2
            collected.extend(records)
            if rejected:
                errors.append({'entity':hit['entity'],'security':hit['stockName'],'rejected':rejected})
        except Exception as exc:
            errors.append({'entity':hit['entity'],'security':hit['stockName'],'url':hit['noticeUrl'],'reason':str(exc)})
    # Pending rows are retained as leads and never silently converted to zero.
    for ticker,row in rows.items():
        row['ticker']=ticker
    verified=sum(bool(h.get('verified_disclosures')) for h in rows.values())
    data.update(schemaVersion=SCHEMA,investor=inv['id'],holdings=list(rows.values()),source_bindings=bindings,lastUpdated=stamp,
                source='HKEX DI 原始申报表及权益披露列表（DION + 2003–2017历史库）',
                audit={'checkedAt':stamp,'status':'partial' if errors else 'checked',
                       'queries':query_results,'discoveredSources':len(hits),'verifiedSecurities':verified,
                       'pendingSecurities':len(rows)-verified,'recordsFetched':len(collected),'errors':errors,
                       'scope':'匹配已配置主体的公开多头权益披露；不等于完整投资组合或当前持仓'})
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temporary.replace(path)
    print(f"HK {inv['id']}: verified={verified}, pending={len(rows)-verified}, records={len(collected)}, errors={len(errors)}",flush=True)
    return {'investor':inv['id'],**data['audit']}


def run(root='.',investors=None,workers=3):
    root=Path(root);configs=[i for i in load_configs(root/'investors.json') if not investors or i['id'] in investors]
    results=[]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures={executor.submit(run_investor,c,root):c for c in configs}
        for future in as_completed(futures):
            config=futures[future]
            try:results.append(future.result())
            except Exception as exc:
                results.append({'investor':config['id'],'status':'failed','errors':[{'reason':str(exc)}]})
    # Status writes are sequential; concurrent investors cannot lose warnings.
    from update_status import record_source_warning
    for r in results:
        if r['status']!='checked':
            record_source_warning('hk_disclosures',f"{r['investor']} 港股披露部分未核实，保留已有证据")
    status_path=root/'alerts_hk_persons.json'
    previous=json.loads(status_path.read_text()) if status_path.exists() else {}
    runs={r['investor']:r for r in previous.get('verificationRuns',[])}
    runs.update({r['investor']:r for r in results})
    previous.update(updatedAt=now_iso(),verificationRuns=sorted(runs.values(),key=lambda r:r['investor']))
    status_path.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n')
    import os
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:
            f.write('\n## HKEX disclosure verification\n\n| Investor | Verified securities | Pending | Result |\n|---|---:|---:|---|\n')
            for r in results:f.write(f"| {r['investor']} | {r.get('verifiedSecurities',0)} | {r.get('pendingSecurities',0)} | {r['status']} |\n")
    if not results or all(r['status']=='failed' for r in results):
        raise RuntimeError('No investor verification completed')
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--investor',action='append');parser.add_argument('--root',default='.');parser.add_argument('--workers',type=int,default=3)
    args=parser.parse_args();run(args.root,args.investor,max(1,min(4,args.workers)))
