"""Separate estimates for source-verified pre-boundary filing scopes.

These archives never populate the current ledger or its combined averages.
Eligibility is fail-closed: a modern symbol/name match is not historic class
continuity. The producer must supply dated original SEC identity evidence.
"""
import re
import json
from functools import lru_cache
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit


def sec_document(url, cik=None):
    parsed = urlsplit(url or '')
    match = re.fullmatch(r'/Archives/edgar/data/(\d+)/[^?#]+', parsed.path)
    return bool(parsed.scheme == 'https' and parsed.netloc == 'www.sec.gov'
                and not parsed.query and not parsed.fragment and match
                and (cik is None or int(match[1]) == int(cik)))


def original_scope(source, quarter):
    from trade_price_history import quarter_index
    if not isinstance(source, dict) or not str(source.get('cik', '')).isdigit():
        return None, 'missing_filing_scope'
    if not sec_document(source.get('url'), source['cik']):
        return None, 'missing_original_filing'
    try:
        end = date.fromisoformat(source.get('reportDate', ''))
    except (ValueError, TypeError):
        return None, 'filing_period_mismatch'
    if (quarter_index(quarter) != end.year * 4 + (end.month - 1) // 3
            or (end.month, end.day) not in ((3, 31), (6, 30), (9, 30), (12, 31))):
        return None, 'filing_period_mismatch'
    audit = source.get('sourceReconciliation', {})
    if audit.get('status') != 'reconciled' or audit.get('difference') != 0:
        return None, 'unreconciled_original_filing'
    if (type(audit.get('reportedEntries')) is not int or audit['reportedEntries'] <= 0
            or audit.get('reportedEntries') != audit.get('parsedEntries')):
        return None, 'unreconciled_original_filing'
    if source.get('format') == 'legacy_13f':
        return None, 'legacy_identity_requires_review'
    return str(int(source['cik'])), None


@lru_cache(maxsize=1)
def reviewed_identities():
    path = Path(__file__).with_name('historical_security_identities.json')
    return json.loads(path.read_text()).get('entries', {}) if path.exists() else {}


def identity_for(holding, quote, quarter):
    """Require dated, explicitly bound evidence; directory/name matches fail."""
    from quote_coverage import issuer_key, symbol
    from trade_price_history import quarter_index, equity
    ticker, cusip = holding.get('ticker', ''), holding.get('cusip', '')
    if not equity(holding) or holding.get('reportedIdentity') or not re.fullmatch(r'[A-Z0-9]{8}[0-9]', cusip) or not ticker or ticker.startswith('?'):
        return None
    evidence = reviewed_identities().get(cusip)
    if not isinstance(evidence, dict) or evidence.get('method') != 'sec_cusip_symbol_endpoints':
        return None
    if evidence.get('cusip') != cusip or evidence.get('ticker') != ticker or not sec_document(evidence.get('sourceURL')) or not sec_document(evidence.get('currentSourceURL')):
        return None
    if re.sub(r'\s+', ' ', holding.get('cls', '').strip().upper()) not in evidence.get('classes', []):
        return None
    start, end = evidence.get('fromQuarter'), evidence.get('throughQuarter')
    if quarter_index(start) is None or quarter_index(end) is None or not start <= quarter <= end:
        return None
    if symbol(quote.get('symbol', '')).upper() != symbol(ticker).upper() or quote.get('currency') != 'USD':
        return None
    expected = issuer_key(evidence.get('issuer', ''))
    if not expected or issuer_key(holding.get('name', '')) != expected or issuer_key(quote.get('verifiedName', '')) != expected:
        return None
    if quote.get('quoteTransition') or quote.get('quotedForCUSIP', cusip) != cusip:
        return None
    return {k: evidence[k] for k in ('method', 'cusip', 'ticker', 'sourceURL', 'currentSourceURL', 'issuer', 'classes', 'fromQuarter', 'throughQuarter')}


def accession_from_url(url):
    if not sec_document(url):
        return None
    parts = urlsplit(url).path.split('/')[5:]
    found = {match.replace('-', '') for part in parts
             for match in re.findall(r'(?<![0-9])(?:[0-9]{10}-[0-9]{2}-[0-9]{6}|[0-9]{18})(?![0-9])', part)}
    return next(iter(found)) if len(found) == 1 else None


def independently_reviewed_row(data, quarter, holding, source):
    """A checked original row can survive an older parser; no absence inferred."""
    from trade_price_history import key
    evidence = reviewed_identities().get(holding.get('cusip', ''), {})
    originals = [r for r in data.get('history', {}).get('holdings', {}).get(quarter, []) if key(r) == key(holding)]
    if len(originals) != 1:
        return False
    row = originals[0]
    fields = ('name', 'cls', 'cusip', 'shares', 'value', 'shareType', 'putCall')
    for checked in evidence.get('reviewedFilingRows', []):
        if (checked.get('quarter') == quarter and checked.get('reporterCIK') == str(int(source['cik']))
                and checked.get('accession') == str(source.get('accession', '')).replace('-', '')
                and accession_from_url(source.get('url')) == checked.get('accession')
                and accession_from_url(checked.get('sourceURL')) == checked.get('accession')
                and sec_document(checked.get('sourceURL'), source['cik'])
                and all(row.get(k, '' if k == 'putCall' else None) == checked.get(k) for k in fields)):
            return True
    return False


def plan(data, history, holding, boundary, blocked, quote):
    """Partition eligible old quarters, including verified absence, by scope."""
    from trade_price_history import quarter_index, key, equity
    from holdings_diff import consolidate_holdings
    if not boundary:
        return [], {}
    sources = data.get('history', {}).get('filing_sources', {})
    groups, reasons = [], {}
    group = None
    target = key(holding)
    for quarter, rows in sorted(history.items()):
        if quarter >= boundary:
            break
        matching = [r for r in consolidate_holdings(rows) if key(r) == target and equity(r)]
        scope, reason = original_scope(sources.get(quarter), quarter)
        if quarter in blocked:
            reason = 'corporate_action_or_unreconciled_values'
        candidate = matching[0] if len(matching) == 1 else None
        if (reason == 'legacy_identity_requires_review' and candidate
                and independently_reviewed_row(data, quarter, candidate, sources[quarter])):
            scope, reason = str(int(sources[quarter]['cik'])), None
        # Multiple versions / classes of one identity must never be combined.
        if len(matching) > 1 or candidate and candidate.get('ticker') != holding.get('ticker'):
            reason = 'security_identity_ambiguous'
        evidence = identity_for(candidate or holding, quote, quarter)
        if not evidence:
            reason = reason or 'historical_class_identity_unverified'
        if reason:
            if matching:
                reasons[quarter] = reason
            group = None
            continue
        if not group or group['reporterCIK'] != scope or quarter_index(quarter) != quarter_index(group['lastQuarter']) + 1:
            if not candidate:
                group = None
                continue
            group = {'reporterCIK': scope, 'firstQuarter': quarter, 'lastQuarter': quarter,
                     'rows': {}, 'filingSources': {}, 'identityEvidence': evidence}
            groups.append(group)
        group['rows'][quarter] = candidate or {'shares': 0}
        group['filingSources'][quarter] = sources[quarter]['url']
        group['lastQuarter'] = quarter
    return groups, reasons


def estimates(plans, candles, quote):
    from trade_price_history import calculate
    result = []
    for segment in plans:
        # A recent-only actions query cannot prove an old price/share basis.
        first = segment['firstQuarter']
        start = first[:4] + '-' + str((int(first[-1])-1)*3+1).zfill(2) + '-01'
        if not quote.get('shareActionsSince') or quote['shareActionsSince'] > start:
            continue
        values = calculate(segment['rows'], candles)
        if not values['quarters']:
            continue
        result.append({k: v for k, v in segment.items() if k != 'rows'} | values |
                      {'kind': 'separate_reporter_reference', 'notCombinedWithCurrent': True,
                       'marketSource': {k: quote[k] for k in ('source', 'sourceURL', 'symbol', 'fetchedAt', 'shareActionsSince') if k in quote}})
    return result
