"""Bounded, resumable historical symbol and class-retirement verification."""
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_state(root):
    path = Path(root)/'security_lifecycle.json'
    return json.loads(path.read_text()) if path.exists() else {'version': 1, 'events': {}}


def write_state(root, state):
    path = Path(root)/'security_lifecycle.json'
    temp = path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n')
    temp.replace(path)


def historical_candidates(root):
    from trade_price_history import equity
    people = json.loads((Path(root)/'investors.json').read_text())['investors']
    found = {}
    for person in people:
        if not person.get('source13F'):
            continue
        data = json.loads((Path(root)/person['dataFile']).read_text())
        for quarter, rows in data.get('history', {}).get('holdings', {}).items():
            for row in rows:
                cusip = row.get('cusip', '')
                if not re.fullmatch(r'[A-Z0-9]{9}', cusip) or not equity(row):
                    continue
                item = found.setdefault(cusip, {'holding': row, 'firstQuarter': quarter, 'lastQuarter': quarter, 'investors': set()})
                item['firstQuarter'] = min(item['firstQuarter'], quarter)
                item['lastQuarter'] = max(item['lastQuarter'], quarter)
                item['investors'].add(person['id'])
                if not row.get('ticker', '').startswith('?'):
                    item['holding'] = row
    return found


def refresh(root=ROOT, *, index_limit=2, filing_limit=8, fetch=None):
    from fetch_13f_all import sec_fetch
    from security_lifecycle import discover_retirements
    from trade_price_history import quarter_index
    root = Path(root); state = read_state(root); audit = state.setdefault('historyAudit', {})
    candidates = historical_candidates(root)
    pending = {k:v for k,v in candidates.items() if k not in state['events']}
    if not pending:
        return {'checkedIndexes': 0, 'retirements': 0}
    today = date.today(); last = today.year*4+(today.month-1)//3
    first = min(quarter_index(v['firstQuarter']) for v in pending.values())
    cursor = audit.get('nextIndex', last)
    if not first <= cursor <= last:
        cursor = last
    total = 0
    for _ in range(index_limit):
        y, q = cursor//4, cursor%4+1
        begin = date(y, (q-1)*3+1, 1)
        end = date(y+1, 1, 1) if q==4 else date(y, q*3+1, 1)
        from datetime import timedelta
        end = min(today, end-timedelta(days=1))
        # Do not bind a pre-existing retirement to a subsequently issued class.
        rows = [v['holding'] for v in pending.values() if quarter_index(v['firstQuarter']) <= cursor and quarter_index(v['lastQuarter']) <= cursor]
        found = discover_retirements(rows, begin.isoformat(), fetch or sec_fetch,
                                     limit=filing_limit, until=end.isoformat())
        state['events'].update(found); total += len(found)
        audit.pop('lastFailure',None)
        audit.update(nextIndex=cursor-1 if cursor>first else last,
                     checkedAt=datetime.now(timezone.utc).isoformat(), lastIndex=f'{y} Q{q}')
        write_state(root, state)
        cursor = audit['nextIndex']
    return {'checkedIndexes': index_limit, 'retirements': total}


if __name__ == '__main__':
    try:
        print(refresh())
    except (OSError, ValueError) as error:
        state=read_state(ROOT)
        state.setdefault('historyAudit', {})['lastFailure'] = {'at':datetime.now(timezone.utc).isoformat(),'reason':type(error).__name__}
        write_state(ROOT,state)
        from update_status import record_source_warning
        message='历史退市核对来源暂不可读；保留已核实记录与扫描进度，下轮自动重试'
        record_source_warning('resolve_cusip',message)
        print(message+': '+type(error).__name__,flush=True)
