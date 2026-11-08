"""Source-bound quarterly trade estimates; no trade dates or executions are invented."""
import copy
import hashlib
import json
import math
import re
from datetime import datetime, timezone

VERSION = 1


def quarter_index(q):
    m = re.fullmatch(r'(\d{4}) Q([1-4])', q or '')
    return int(m[1])*4+int(m[2])-1 if m else None


def equity(h):
    return (not h.get('putCall') and h.get('shareType', 'SH') == 'SH'
            and not re.search(r'WARRANT|\bW EXP|\bUNIT|\bNOTE|\bBOND|PFD|PREF', h.get('cls', ''), re.I))


def key(h):
    return h.get('cusip') or h.get('ticker', '')


def candle_estimates(candle):
    if not candle:
        return None
    values = [candle.get(k, []) for k in ('closes', 'lows', 'highs')]
    if any(not v or any(type(x) not in (float, int) or not math.isfinite(x) or x <= 0 for x in v) for v in values):
        return None
    closes, lows, highs = values
    avg = sum(closes)/len(closes)
    return {'buy': round(min(lows)*.7+avg*.3, 4),
            'sell': round(max(highs)*.7+avg*.3, 4), 'low': min(lows), 'high': max(highs), 'mean': avg, 'days': len(closes), 'source': 'historical_daily_prices'}


def calculate(rows, candles, excluded=(), boundary='', scope_boundary=''):
    """Rows include known zero-holding quarters. Missing quarters break continuity."""
    timeline = []
    previous = None
    cost = None
    buys = sells = buy_value = sell_value = 0.0
    missing_buys = missing_sells = 0
    for quarter, h in sorted(rows.items()):
        if quarter < boundary:
            continue
        shares = h.get('shares', 0)
        contiguous = previous is not None and quarter_index(quarter)-quarter_index(previous[0]) == 1
        if quarter == scope_boundary:
            contiguous = False
        old = previous[1] if contiguous else None
        if not contiguous:
            cost = None
        if not shares and not old:
            previous = (quarter, shares)
            continue
        action = ('observed' if old is None else 'new' if not old else 'added' if shares > old
                  else 'exited' if not shares else 'trimmed' if shares < old else 'hold')
        delta = shares - (old or 0)
        price = candles.get(quarter, {}) if quarter not in excluded else {}
        row = dict(quarter=quarter, action=action, shares=shares, previousShares=old)
        if action != 'hold' and price:
            row['priceEvidence'] = price
        if action in ('observed', 'new', 'added'):
            buy = price.get('buy')
            row['buy'] = buy
            if buy:
                cost = buy if not old else ((cost*old+buy*delta)/shares if cost is not None else None)
                buys += delta
                buy_value += delta*buy
            else:
                cost = None
                missing_buys += 1
        elif action in ('trimmed', 'exited'):
            sell = price.get('sell')
            row['sell'] = sell
            row['costBeforeSale'] = round(cost, 4) if cost is not None else None
            if sell:
                sells += -delta
                sell_value += -delta*sell
            else:
                missing_sells += 1
        row['averageCost'] = round(cost, 4) if cost is not None and shares else None
        timeline.append(row)
        if not shares:
            cost = None
        previous = (quarter, shares)
    return {'quarters': timeline,
            'averageBuy': round(buy_value/buys, 4) if buys and not missing_buys else None,
            'averageSell': round(sell_value/sells, 4) if sells and not missing_sells else None,
            'missingBuyQuarters': missing_buys, 'missingSellQuarters': missing_sells,
            'first': timeline[0]['quarter'] if timeline else '',
            'last': timeline[-1]['quarter'] if timeline else ''}


def build(data, quotes, previous=None, *, download_limit=12, loader=None, now=None, refresh_quotes=True):
    from fetch_prices_all import comparable_price_history, quarter_ts
    from holdings_diff import consolidate_holdings
    from security_identity import project
    from reporting_scope import same_manager_history
    from batch_market_data import SERIES, prefetch, window, is_share_split, download_history
    from security_lifecycle import events
    now = now or datetime.now(timezone.utc).isoformat()
    if data.get('meta', {}).get('snapshotType') or data.get('history', {}).get('verification', {}).get('status') == 'unverified':
        return {'version': VERSION, 'entries': {}}
    old = (previous or {}).get('entries', {}) if (previous or {}).get('version') == VERSION else {}
    data = project(data)
    current = data.get('current', {})
    raw = dict(data.get('history', {}).get('holdings', {}))
    if quarter_index(current.get('quarter')) is not None:
        raw[current['quarter']] = current.get('holdings', [])
    if current.get('prevQuarter') and isinstance(current.get('previousHoldings'), list):
        raw.setdefault(current['prevQuarter'], current['previousHoldings'])
    raw = {q: rows for q, rows in raw.items() if quarter_index(q) is not None and q <= current.get('quarter', q)}
    if refresh_quotes and download_limit > 0:
        from quote_coverage import fresh_quote
        from batch_market_data import prefetch_quotes, merge_actions
        from security_lifecycle import event_for
        recent = current.get('previousHoldings',raw.get(current.get('prevQuarter'),[]))
        wanted = {h['ticker'] for h in recent if equity(h) and not h['ticker'].startswith('?')
                  and not h['ticker'].endswith('.HK') and not event_for(h) and not fresh_quote(quotes.get(h['ticker'],{}))}
        wanted.update(tk for tk,q in quotes.items() if q.get('status')!='ceased_trading'
                      and not tk.startswith('?') and not tk.endswith('.HK') and not fresh_quote(q))
        for tk,q in prefetch_quotes(sorted(wanted)[:max(24,download_limit)]).items() if wanted else []:
            if not q.get('error'):
                quotes[tk]=merge_actions(quotes.get(tk,{}),q)
    history = comparable_price_history(raw, current.get('quarter', ''), quotes)
    securities = {}
    for q, holdings in sorted(history.items()):
        for h in consolidate_holdings(holdings):
            if not equity(h):
                continue
            k = key(h)
            if not k:
                continue
            item = securities.setdefault(k, {'holding': h, 'rows': {}})
            item['holding'] = h
            item['rows'][q] = h
    excluded = set(data.get('history', {}).get('excludedValueQuarters', []))
    if current.get('valueQuality'):
        excluded.add(current.get('quarter'))
    transition = data.get('meta', {}).get('reportingTransition', {})
    lifecycle = events()
    prepared = []
    for k, item in securities.items():
        h = item['holding']; tk = h['ticker']; first = min(item['rows'])
        rows = {q: item['rows'].get(q, {'shares': 0}) for q in history if q >= first}
        scope = transition.get('fromQuarter', '') if transition.get('comparisonScopeChanged') and not same_manager_history(data, h) else ''
        meta = data.get('meta', {})
        boundary = max(scope, meta.get('costHistoryFrom', ''), meta.get('instrumentHistoryFrom', '') if tk in meta.get('instrumentHistoryTickers', []) else '')
        actions = quotes.get(tk, {}).get('shareActions', [])
        basis = hashlib.sha256(json.dumps([tk, actions, meta.get('shareActions', [])], sort_keys=True).encode()).hexdigest()
        blocked=set(excluded)
        uncertain=[a for a in actions if not is_share_split(a,h)]
        if uncertain:
            last_action=max(a['date'] for a in uncertain)
            action_quarter=last_action[:4]+' Q'+str((int(last_action[5:7])-1)//3+1)
            blocked.update(q for q in rows if q<=action_quarter)
        cached = old.get(k, {})
        candles = copy.deepcopy(cached.get('candles', {})) if cached.get('priceBasis') == basis else {}
        preliminary = calculate(rows, candles, blocked, boundary, scope)
        needed = [r['quarter'] for r in preliminary['quarters'] if ('buy' in r or 'sell' in r) and r['quarter'] not in candles and r['quarter'] not in blocked]
        prepared.append(dict(k=k, h=h, rows=rows, boundary=boundary, scope=scope, candles=candles,
                             basis=basis, needed=needed, cached=cached, blocked=blocked, currentTrade=any(r['quarter']==current.get('quarter') and r['action'] in ('new','added','trimmed','exited') for r in preliminary['quarters'])))
    # The latest displayed portfolio gets priority; historical names rotate by
    # last attempt so one unavailable security cannot starve the remaining queue.
    active = {key(h): h.get('value', 0) for h in current.get('holdings', [])}
    prepared.sort(key=lambda p: (0 if p['currentTrade'] else 1 if p['k'] in active else 2, p['cached'].get('checkedAt', ''), -max(active.get(p['k'], 0),p['h'].get('value',0)), p['k']))
    eligible = [p for p in prepared if p['needed'] and not p['h']['ticker'].startswith('?')
                and not p['h']['ticker'].endswith('.HK') and p['h']['ticker'] not in SERIES
                and p['cached'].get('checkedAt', '')[:10] != now[:10]]
    historic = [p for p in eligible if p['k'] not in active and not p['currentTrade']]
    reserved = historic[:min(4, download_limit//3)]
    selected = [p for p in eligible if p not in reserved][:max(0,download_limit-len(reserved))]+reserved
    if selected:
        start = quarter_ts(min(min(p['rows']) for p in selected))[0]
        fresh = prefetch([p['h']['ticker'] for p in selected], start, loader=loader or download_history)
        from batch_market_data import merge_actions
        for tk, quote in fresh.items():
            if not quote.get('error'):
                quotes[tk] = merge_actions(quote,quotes[tk]) if quote.get('historyOnly') and quotes.get(tk,{}).get('t',0)>quote.get('t',0) else merge_actions(quotes.get(tk, {}), quote)
        # New split evidence changes both price and share bases. Rebuild them
        # together before using the downloaded historical series.
        rebuilt = build(data, quotes, previous, download_limit=0, now=now, refresh_quotes=False)
        for p in selected:
            if p['k'] in rebuilt['entries']:
                rebuilt['entries'][p['k']]['checkedAt'] = now
        return rebuilt
    checked = {p['k'] for p in selected}
    result = {}
    for p in prepared:
        h = p['h']; tk = h['ticker']; candles = p['candles']
        for q in p['needed']:
            covered, raw_candle = window(tk, *quarter_ts(q))
            estimate = candle_estimates(raw_candle) if covered else None
            if estimate:
                candles[q] = estimate
        computed = calculate(p['rows'], candles, p['blocked'], p['boundary'], p['scope'])
        entry = dict(ticker=tk, cusip=h.get('cusip'), **computed, candles=candles, priceBasis=p['basis'],
                     checkedAt=now if p['k'] in checked else p['cached'].get('checkedAt', ''))
        event = lifecycle.get(h.get('cusip'))
        if event and event['ticker'] == tk and event['effectiveDate'] <= now[:10]:
            entry['lifecycle'] = event
        result[p['k']] = entry
    return {'version': VERSION, 'entries': result}


def exit_performance(ledger):
    """Compatibility output: only a consecutive report can establish an exit."""
    result = {}
    for entry in ledger.get('entries', {}).values():
        rows = entry['quarters']
        if not rows or rows[-1]['action'] != 'exited':
            continue
        last = rows[-1]; buy = last.get('costBeforeSale'); sell = last.get('sell')
        if not buy or not sell:
            continue
        start = next((r['quarter'] for r in reversed(rows[:-1]) if r['action'] in ('new', 'observed')), rows[0]['quarter'])
        result[entry['ticker']] = dict(entryQuarter=start, entryPrice=buy, exitQuarter=last['quarter'],
                                      exitPrice=sell, changePct=round((sell/buy-1)*100, 1), methodVersion=VERSION)
    return result


def refresh_file(person, root, limit=12):
    from pathlib import Path
    root=Path(root)
    data=json.loads((root/person['dataFile']).read_text())
    price_path=root/person['pricesFile']
    prices=json.loads(price_path.read_text())
    prices['tradePrices']=build(data,prices.setdefault('quotes',{}),prices.get('tradePrices'),download_limit=limit)
    prices['exitPerf']=exit_performance(prices['tradePrices'])
    temp=price_path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(prices,ensure_ascii=False,indent=None if len(prices['tradePrices']['entries'])>200 else 2,separators=(',',':') if len(prices['tradePrices']['entries'])>200 else None)+'\n');temp.replace(price_path)
    entries=prices['tradePrices']['entries']
    return {'investor':person['id'],'securities':len(entries),'buyAverages':sum(e.get('averageBuy') is not None for e in entries.values()),'saleAverages':sum(e.get('averageSell') is not None for e in entries.values())}


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser();parser.add_argument('--investor');parser.add_argument('--limit',type=int,default=12)
    args=parser.parse_args();root=Path(__file__).resolve().parent
    for person in json.loads((root/'investors.json').read_text())['investors']:
        if person.get('source13F') and (not args.investor or person['id']==args.investor):
            print(refresh_file(person,root,args.limit),flush=True)
