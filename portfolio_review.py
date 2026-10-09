"""Complete, reproducible share changes. AI may select highlights, never numbers."""
import re
from holdings_diff import compare_holdings, consolidate_holdings

CATEGORIES = ('new', 'added', 'trimmed', 'exited', 'hold', 'unknown')
LABELS = dict(zip(CATEGORIES, ('新建仓', '增持', '减持', '清仓', '股数不变', '上季股数未知，不判断增减')))


def comparison_state(data):
    cur = data.get('current', {})
    meta = data.get('meta', {})
    if meta.get('snapshotType'):
        return 'snapshot'
    transition = meta.get('reportingTransition', {})
    if transition.get('comparisonScopeChanged') and transition.get('fromQuarter') == cur.get('quarter'):
        return 'scope_changed'
    def index(q):
        m = re.fullmatch(r'(\d{4}) ?Q([1-4])', q or '')
        return int(m[1])*4+int(m[2]) if m else None
    old, new = index(cur.get('prevQuarter')), index(cur.get('quarter'))
    if old is not None and new is not None and new-old != 1:
        return 'gap'
    if not isinstance(cur.get('previousHoldings'), list) and not isinstance(data.get('history', {}).get('holdings', {}).get(cur.get('prevQuarter')), list):
        return 'partial'
    return 'comparable'


def category(h):
    cur, prev = h.get('shares', 0), h.get('prevShares')
    if prev is None: return 'unknown'
    if not prev: return 'new' if cur else 'hold'
    if not cur: return 'exited'
    return 'added' if cur > prev else 'trimmed' if cur < prev else 'hold'


def change_text(h):
    kind = category(h)
    change = LABELS[kind]
    if kind in ('added', 'trimmed'):
        pct = abs(h['shares']/h['prevShares']-1)*100
        change += f'{pct:.1f}%' if pct >= .05 else '（微量变动）'
    if h.get('shareAdjustment'): change += '（拆股调整后）'
    return change


def review(data):
    cur = data.get('current', {})
    state = comparison_state(data)
    previous = cur.get('previousHoldings', data.get('history', {}).get('holdings', {}).get(cur.get('prevQuarter')))
    rows = compare_holdings(cur.get('holdings', []), previous,
        previous_quarter=cur.get('prevQuarter'), current_quarter=cur.get('quarter')) if isinstance(previous, list) else consolidate_holdings(cur.get('holdings', []))
    if state in ('snapshot', 'scope_changed', 'gap'):
        rows = [dict(h, prevShares=None, prevValue=None) for h in consolidate_holdings(cur.get('holdings', []))]
    rows.sort(key=lambda h: max(h.get('value') or 0, h.get('prevValue') or 0), reverse=True)
    stats = {k: sum(category(h) == k for h in rows) for k in CATEGORIES}
    return dict(state=state, complete=state=='comparable', stats=stats, rows=rows)


def investor_facts(data, name):
    result = review(data)
    facts = []
    for h in result['rows']:
        suffix = (' '+h['putCall'].upper()) if h.get('putCall') else (' PRN' if h.get('shareType', 'SH')!='SH' else '')
        facts.append(dict(ticker=h['ticker']+suffix, name=h.get('cnName') or h.get('name', ''),
                          change=change_text(h), category=category(h), metric='披露股数相对上季变化'))
    # Include each direction even when its largest holding is outside the top ten.
    chosen = [next((f for f in facts if f['category']==k), None) for k in CATEGORIES[:4]]
    chosen = [f for f in chosen if f is not None]
    chosen += [f for f in facts if f['category'] not in ('hold','unknown') and f not in chosen][:16]
    chosen += [f for f in facts if f not in chosen][:max(0,20-len(chosen))]
    ranked = [f for f in facts if f in chosen]
    return dict(kind='investor', investor=name, quarter=data['current']['quarter'],
                comparisonState=result['state'], complete=result['complete'], stats=result['stats'],
                items=[dict(f,id=f'f{i}') for i,f in enumerate(ranked)])
