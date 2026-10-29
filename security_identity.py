"""Conservative, dataset-local identities for legacy rows without CUSIPs.

Never joins two different nonempty CUSIPs, guesses issuer names, or crosses
share classes/instruments. Source rows stay untouched; projections retain the
reported fields and the exact later filing that supports the bridge.
"""
import copy
import re


def text(value):
    return re.sub(r"\s+", " ", str(value or "").strip()).upper()


def signature(row):
    name, cls = text(row.get('name')), text(row.get('cls'))
    # Himalaya's two legacy labels describe the same Baidu class-A ADR.
    if name == 'BAIDU INC' and cls in ('SPON ADR A', 'SPON ADR REP A'):
        cls = 'SPON ADR REP A'
    return (name, cls, text(row.get('putCall')), text(row.get('shareType') or 'SH'))


def identity_index(data):
    candidates = {}
    history = data.get('history', {})
    groups = list(sorted(history.get('holdings', {}).items()))
    current = data.get('current', {})
    groups += [(current.get('quarter', ''), current.get('holdings', [])),
               (current.get('prevQuarter', ''), current.get('previousHoldings', []))]
    for quarter, rows in groups:
        for row in rows:
            key = signature(row)
            cusip = row.get('cusip')
            if not key[0] or not key[1] or not re.fullmatch(r'[A-Z0-9*@#]{8}[0-9]', cusip or ''):
                continue
            found = candidates.setdefault(key, {})
            old = found.get(cusip)
            if old is None or (old['ticker'].startswith('?') and not row.get('ticker', '').startswith('?')):
                found[cusip] = dict(cusip=cusip, ticker=row.get('ticker', ''), quarter=quarter,
                    source=history.get('filing_sources', {}).get(quarter, {}))
    return {key: next(iter(values.values())) for key, values in candidates.items() if len(values) == 1}


def project_row(row, index):
    if row.get('cusip'):
        return dict(row)
    evidence = index.get(signature(row))
    if not evidence:
        return dict(row)
    result = dict(row, cusip=evidence['cusip'])
    if row.get('ticker', '').startswith('?'):
        result['ticker'] = evidence['ticker']
    result['reportedIdentity'] = {k: row[k] for k in ('ticker', 'cusip', 'name', 'cls') if k in row}
    result['identityEvidence'] = dict(evidence, method='unique_exact_name_class_instrument')
    return result


def project(data):
    result = copy.deepcopy(data)
    # Exact source anomaly only, not a general CUSIP-padding heuristic.
    if str(data.get('meta',{}).get('managerCIK','')).lstrip('0')=='1549575':
        for row in result.get('history',{}).get('holdings',{}).get('2016 Q3',[]):
            if (row.get('cusip')=='84670702' and text(row.get('cls'))=='CL B'
                    and text(row.get('shareType') or 'SH')=='SH' and not row.get('putCall')
                    and row.get('shares')==47400 and text(row.get('name'))=='BERKSHIRE HATHAWAY INC DEL'):
                row['reportedIdentity']={k:row[k] for k in ('ticker','cusip','name','cls') if k in row}
                row['cusip']='084670702'
                row['identityEvidence']={'method':'source_scoped_missing_leading_zero','quarter':'2016 Q3','source':{'url':'https://www.sec.gov/Archives/edgar/data/1549575/000154957516000021/infotable.xml'},'cusip':'084670702'}
    index = identity_index(result)
    for quarter, rows in result.get('history', {}).get('holdings', {}).items():
        result['history']['holdings'][quarter] = [project_row(row, index) for row in rows]
    for key in ('holdings', 'previousHoldings'):
        if key in result.get('current', {}):
            result['current'][key] = [project_row(row, index) for row in result['current'][key]]
    return result


def project_prices(data, prices):
    """Discard estimates computed before these aliases shared one history."""
    result = copy.deepcopy(prices)
    if result.get('securityIdentityVersion', 0) >= 1:
        return result
    affected = {h['ticker'] for rows in project(data).get('history', {}).get('holdings', {}).values()
                for h in rows if h.get('reportedIdentity')}
    for field in ('costBasis', 'exitPerf'):
        for ticker in affected:
            result.get(field, {}).pop(ticker, None)
    return result
