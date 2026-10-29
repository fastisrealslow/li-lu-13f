"""Build small, immutable browser snapshots from the validated source files.

The original financial datasets remain the source of truth. History is a
separate download; the first screen never needs the complete filing archive.
"""
import argparse
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path

import ai_supplement as ai
from security_identity import project as project_identities, project_prices

ROOT = Path(__file__).resolve().parent
ROW_FIELDS = ('ticker', 'cusip', 'name', 'cnName', 'cls', 'shares', 'value',
              'shareType', 'putCall', 'sector', 'shareAdjustment', 'reportedIdentity', 'identityEvidence',
              'investmentDiscretion', 'votingAuthority', 'managerAllocations')


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def read(path):
    return json.loads(path.read_text())


def browser_entry(entry):
    fields = ('source', 'sourceHash', 'facts', 'briefing', 'selection',
              'renderVersion', 'summary', 'mode', 'model')
    return copy.deepcopy({key: entry[key] for key in fields if key in entry})


def compact_row(row, managers=False):
    fields = (*ROW_FIELDS, 'prevShares', 'prevValue',
              *(('managerAllocations',) if managers else ()))
    return {key: value for key, value in row.items() if key in fields}


def display_data(data, limit=None):
    if not limit or len(data.get('current', {}).get('holdings', [])) <= limit:
        return data
    result = copy.deepcopy(data)
    current, history = result['current'], result.setdefault('history', {})
    original = current['holdings']
    current['holdings'] = sorted(original, key=lambda h: -h['value'])[:limit]
    key = lambda h: (h.get('cusip') or h.get('ticker'), h.get('shareType', 'SH'), h.get('putCall', ''))
    selected = {key(h) for h in current['holdings']}
    current['previousHoldings'] = [h for h in current.get('previousHoldings', history.get('holdings', {}).get(current.get('prevQuarter'), [])) if key(h) in selected]
    values = [sum(h['value'] for h in history['holdings'][q])/1e6 if history.get('holdings', {}).get(q) else history['values'][i]
              for i, q in enumerate(history.get('quarters', []))]
    history['portfolioValues'] = values
    result.setdefault('meta', {})['browserScope'] = {'limit':limit, 'reportedHoldings':len(original), 'shownValue':sum(h['value'] for h in current['holdings']), 'historyScope':'full_filing'}
    return result


def current_data(data, prices):
    result = copy.deepcopy(data)
    history = result.setdefault('history', {})
    all_rows = history.pop('holdings', {})
    history['values'] = history.get('portfolioValues') or [sum(row['value'] for row in all_rows[q]) / 1e6
        if all_rows.get(q) and all(type(row.get('value')) in (int, float)
            and math.isfinite(row['value']) and row['value'] >= 0 for row in all_rows[q])
        else history['values'][index] for index, q in enumerate(history.get('quarters', []))]
    history.pop('valueAudit', None)
    history['holdings'] = {}
    transition = result.get('meta', {}).get('reportingTransition', {})
    current = result['current']
    managers = bool(transition or current.get('reportingScope'))
    if 'previousHoldings' not in current and isinstance(all_rows.get(current.get('prevQuarter')), list):
        current['previousHoldings'] = all_rows[current['prevQuarter']]
    for key in ('holdings', 'previousHoldings'):
        if key in current:
            current[key] = [dict(row) for row in current[key]]
    bridge = transition.get('fromQuarter')
    if bridge and bridge != current.get('quarter') and bridge in all_rows:
        history['holdings'][bridge] = all_rows[bridge]
    # Preserve exactly the evidence the existing security-class cost check uses,
    # without shipping thousands of unrelated rows for each reference quarter.
    needed = {}
    for row in current['holdings']:
        cost = prices.get('costBasis', {}).get(row['ticker'], {})
        for quarter in ((cost.get('recent') or {}).get('quarter'),
                        (cost.get('allTime') or {}).get('first')):
            if quarter:
                needed.setdefault(quarter, set()).add((row['ticker'], row.get('cusip')))
    history['costReferenceProofs'] = {
        quarter: [list(key) for key in sorted({(row['ticker'], row.get('cusip'))
            for row in all_rows.get(quarter, [])
            if row.get('shareType') == 'SH' and row.get('putCall') == ''
            and row.get('shares', 0) > 0
            and (row['ticker'], row.get('cusip')) in wanted}, key=str)]
        for quarter, wanted in needed.items()}
    return result


def current_prices(prices, tickers=None):
    result = copy.deepcopy(prices)
    result.pop('exitPerf', None)
    result.pop('sourceHistoryFingerprint', None)
    if tickers is not None:
        result['quotes'] = {k:v for k,v in result.get('quotes', {}).items() if k in tickers}
        result['costBasis'] = {k:v for k,v in result.get('costBasis', {}).items() if k in tickers}
    for quote in result.get('quotes', {}).values():
        for key in ('shareActions', 'shareActionsSince', 'fetchedAt', 'verifiedName', 'symbol'):
            quote.pop(key, None)
    for cost in result.get('costBasis', {}).values():
        cost.pop('historyFingerprint', None)
    return result


def history_data(data, prices):
    history = copy.deepcopy(data.get('history', {}))
    history.pop('valueAudit', None)
    managers = bool(data.get('meta', {}).get('reportingTransition'))
    history['holdings'] = {quarter: [compact_row(row, managers) for row in rows]
        for quarter, rows in history.get('holdings', {}).items()}
    return {'version': 1, 'history': history, 'exitPerf': prices.get('exitPerf', {})}


def build(root=ROOT, output=None):
    root = Path(root)
    output = Path(output) if output else root / 'browser'
    output.mkdir(parents=True, exist_ok=True)
    people = read(root / 'investors.json')['investors']
    cached = read(root / 'ai_supplement.json') if (root / 'ai_supplement.json').exists() else {}
    tasks = {task['id']: task for task in ai.tasks(root)}
    manifest = {'version': 1, 'investors': {}}
    def asset(ident, kind, value):
        body = encoded(value)
        digest = hashlib.sha256(body).hexdigest()
        name = f'{ident}-{kind}-{digest[:24]}.json'
        (output / name).write_bytes(body)
        compressed = gzip.compress(body, mtime=0)
        (output / (name + '.gz')).write_bytes(compressed)
        return {'file': 'browser/' + name, 'bytes': len(body), 'sha256': digest,
                'gzipFile': 'browser/' + name + '.gz', 'gzipBytes': len(compressed)}
    for person in people:
        ident = person['id']
        data, prices = read(root / person['dataFile']), read(root / person['pricesFile'])
        prices = project_prices(data, prices)
        data = display_data(project_identities(data), person.get('browserHoldingLimit'))
        tickers = {h['ticker'] for h in data['current']['holdings']} if data.get('meta', {}).get('browserScope') else None
        overview = current_data(data, prices)
        entries, source_keys = {}, {}
        for kind in ('investor', 'holdings', 'history'):
            key = kind + ':' + ident
            task = tasks.get(key)
            if not task:
                continue
            entry = cached.get('entries', {}).get(key)
            if not ai.valid_entry(entry, task):
                entry = ai.make_entry(task, ai.fallback_selection(task['facts']))
            entry = browser_entry(entry)
            digest = hashlib.sha256(encoded(task['source'])).hexdigest()
            entry['source'] = {'browserSource': digest}
            entries[key] = entry
            source_keys[kind] = digest
        value = tasks.get('value')
        if value:
            entry = cached.get('entries', {}).get('value')
            entries['value'] = browser_entry(entry if ai.valid_entry(entry, value) else ai.make_entry(value, ai.fallback_selection(value['facts'])))
        overview['browserProjection'] = {'version': 1, 'sources': source_keys}
        history = asset(ident, 'history', {**history_data(data, prices), 'investor': ident})
        hk = read(root / person['hkFile']) if person.get('hkFile') and (root / person['hkFile']).exists() else None
        snapshot = asset(ident, 'current', {'version': 1, 'investor': ident,
            'data': overview, 'prices': current_prices(prices, tickers), 'hk': hk,
            'insights': {'schemaVersion': 2, 'entries': entries}, 'history': history})
        manifest['investors'][ident] = {'snapshot': snapshot, 'history': history}
    (output / 'manifest.json').write_bytes(encoded(manifest))
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(ROOT))
    parser.add_argument('--output')
    args = parser.parse_args()
    result = build(args.root, args.output)
    print('Browser snapshots:', len(result['investors']))
    for ident, entry in result['investors'].items():
        print(ident, entry['snapshot']['bytes'], 'bytes; history loaded on demand')
