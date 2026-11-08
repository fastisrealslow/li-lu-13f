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
    from security_lifecycle import events, event_for
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
    quote_state=copy.deepcopy((previous or {}).get('quoteRefresh',{}))
    if refresh_quotes and download_limit > 0:
        from historical_quote_refresh import refresh
        quote_state=refresh(data,quotes,quote_state,limit=max(24,download_limit),now=datetime.fromisoformat(now.replace('Z','+00:00')))
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
        first_date=first[:4]+'-'+str((int(first[-1])-1)*3+1).zfill(2)+'-01'
        relevant_actions=[a for a in actions if a['date']>=first_date]
        basis = hashlib.sha256(json.dumps([tk, relevant_actions, meta.get('shareActions', [])], sort_keys=True).encode()).hexdigest()
        legacy_basis=hashlib.sha256(json.dumps([tk, actions, meta.get('shareActions', [])], sort_keys=True).encode()).hexdigest()
        blocked=set(excluded)
        uncertain=[a for a in actions if not is_share_split(a,h)]
        if uncertain:
            last_action=max(a['date'] for a in uncertain)
            action_quarter=last_action[:4]+' Q'+str((int(last_action[5:7])-1)//3+1)
            blocked.update(q for q in rows if q<=action_quarter)
        cached = old.get(k, {})
        same_basis=cached.get('priceBasis') in (basis,legacy_basis)
        if not same_basis:cached={**cached,'checkedAt':''}
        candles = copy.deepcopy(cached.get('candles', {})) if same_basis else {}
        preliminary = calculate(rows, candles, blocked, boundary, scope)
        needed = [r['quarter'] for r in preliminary['quarters'] if ('buy' in r or 'sell' in r) and r['quarter'] not in candles and r['quarter'] not in blocked]
        prepared.append(dict(k=k, h=h, rows=rows, boundary=boundary, scope=scope, candles=candles,
                             basis=basis, needed=needed, cached=cached, blocked=blocked, currentTrade=any(r['quarter']==current.get('quarter') and r['action'] in ('new','added','trimmed','exited') for r in preliminary['quarters'])))
    # The latest displayed portfolio gets priority; historical names rotate by
    # last attempt so one unavailable security cannot starve the remaining queue.
    active = {key(h): h.get('value', 0) for h in current.get('holdings', [])}
    prepared.sort(key=lambda p: (0 if p['currentTrade'] else 1 if p['k'] in active else 2, p['cached'].get('checkedAt', ''), -max(active.get(p['k'], 0),p['h'].get('value',0)), p['k']))
    def needs_series(p):
        tk=p['h']['ticker']
        if tk not in SERIES:return True
        series=SERIES[tk]
        return bool(series and series.get('timestamps') and p['needed']
                    and series['timestamps'][0]>quarter_ts(min(p['needed']))[1])
    eligible = [p for p in prepared if p['needed'] and not p['h']['ticker'].startswith('?')
                and not p['h']['ticker'].endswith('.HK') and needs_series(p)
                and (p['cached'].get('ticker')!=p['h']['ticker'] or p['cached'].get('checkedAt', '')[:10] != now[:10])]
    historic = [p for p in eligible if p['k'] not in active and not p['currentTrade']]
    reserved = historic[:min(4, download_limit//3)]
    selected = [p for p in eligible if p not in reserved][:max(0,download_limit-len(reserved))]+reserved
    if selected:
        start = quarter_ts(min(min(p['rows']) for p in selected))[0]
        fresh = prefetch([p['h']['ticker'] for p in selected], start, loader=loader or download_history)
        from batch_market_data import merge_actions
        for tk, quote in fresh.items():
            if not quote.get('error'):
                try:
                    quotes[tk] = merge_actions(quote,quotes[tk]) if quotes.get(tk,{}).get('status')=='ceased_trading' or (quote.get('historyOnly') and quotes.get(tk,{}).get('t',0)>quote.get('t',0)) else merge_actions(quotes.get(tk, {}), quote)
                except ValueError:SERIES.pop(tk,None)
        # New split evidence changes both price and share bases. Rebuild them
        # together before using the downloaded historical series.
        rebuilt = build(data, quotes, {**(previous or {}),'quoteRefresh':quote_state}, download_limit=0, now=now, refresh_quotes=False)
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
    # Historical responses must never undo a confirmed current-class retirement.
    for h in current.get('holdings',[]):
        event=event_for(h)
        if event:quotes.setdefault(h['ticker'],{}).update(status='ceased_trading',event=event)
    return {'version': VERSION, 'entries': result, 'quoteRefresh':quote_state}


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


def refresh_file(person, root, limit=12, cached=None):
    from pathlib import Path
    root=Path(root)
    data=json.loads((root/person['dataFile']).read_text())
    price_path=root/person['pricesFile']
    prices=json.loads(price_path.read_text())
    quotes=prices.setdefault('quotes',{})
    if cached:
        from batch_market_data import SERIES, normalized_symbol, merge_actions
        holdings=list(data.get('current',{}).get('holdings',[]))
        for rows in data.get('history',{}).get('holdings',{}).values():holdings.extend(rows)
        from fetch_prices_all import quarter_ts
        starts={}
        for quarter,rows in data.get('history',{}).get('holdings',{}).items():
            if quarter_index(quarter) is None:continue
            for h in rows:
                tk=h.get('ticker','');starts[tk]=min(starts.get(tk,float('inf')),quarter_ts(quarter)[0])
        for ticker in {h.get('ticker','') for h in holdings}:
            item=cached.get(normalized_symbol(ticker))
            if not item:continue
            series,q=item
            start=starts.get(ticker,0)
            first_trade=q.get('historyFirstTrade') or 0
            if series['timestamps'][0]>max(start,first_trade)+7*86400:continue
            old=quotes.get(ticker,{})
            try:
                quotes[ticker]=merge_actions(q,old) if old.get('status')=='ceased_trading' or old.get('t',0)>q.get('t',0) else merge_actions(old,q)
                SERIES[ticker]=series
            except ValueError:continue
    prices['tradePrices']=build(data,quotes,prices.get('tradePrices'),download_limit=limit)
    prices['exitPerf']=exit_performance(prices['tradePrices'])
    from fetch_prices_all import write_prices_atomic
    write_prices_atomic(price_path,prices)
    entries=prices['tradePrices']['entries']
    return {'investor':person['id'],'securities':len(entries),'buyAverages':sum(e.get('averageBuy') is not None for e in entries.values()),'saleAverages':sum(e.get('averageSell') is not None for e in entries.values())}


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser();parser.add_argument('--investor');parser.add_argument('--limit',type=int,default=12)
    parser.add_argument('--reuse-cache',action='store_true')
    args=parser.parse_args();root=Path(__file__).resolve().parent
    from batch_market_data import cached_histories
    cached=cached_histories(root) if args.reuse_cache else None
    for person in json.loads((root/'investors.json').read_text())['investors']:
        if person.get('source13F') and (not args.investor or person['id']==args.investor):
            print(refresh_file(person,root,args.limit,cached),flush=True)
