"""Bounded, resumable live quotes for every known historical security."""
import copy
from datetime import datetime, timedelta, timezone
from batch_market_data import normalized_symbol, prefetch_quotes, merge_actions
from quote_coverage import fresh_quote
from security_lifecycle import event_for

SESSION_QUOTES={}


def latest_close(now):
    day=now.date()
    if now.hour<22:day-=timedelta(days=1)
    while day.weekday()>4:day-=timedelta(days=1)
    return day


def due(q, now):
    if not fresh_quote(q,now.timestamp()):return True
    if datetime.fromtimestamp(q['t'],timezone.utc).date()>=latest_close(now):return False
    try:return (now-datetime.fromisoformat(q.get('fetchedAt','').replace('Z','+00:00'))).total_seconds()>=20*3600
    except (ValueError,TypeError,AttributeError):return True


def refresh(data, quotes, previous=None, *, limit=24, now=None, loader=None):
    from trade_price_history import equity
    now=now or datetime.now(timezone.utc);loader=loader or prefetch_quotes
    state=copy.deepcopy(previous or {});holdings={}
    history=dict(data.get('history',{}).get('holdings',{}))
    current=data.get('current',{});history[current.get('quarter','9999')]=current.get('holdings',[])
    for quarter,rows in sorted(history.items()):
        for h in rows:
            tk=h.get('ticker','')
            if equity(h) and tk and not tk.startswith('?') and not tk.endswith('.HK'):holdings[tk]=h
    active={h['ticker'] for h in current.get('holdings',[])}
    pending=[]
    for tk,h in holdings.items():
        if event_for(h):continue
        q=quotes.get(tk,{})
        if not due(q,now):
            prior=SESSION_QUOTES.get(normalized_symbol(tk),{})
            if not fresh_quote(prior,now.timestamp()) or q['t']>=prior.get('t',0):SESSION_QUOTES[normalized_symbol(tk)]=q
            continue
        old=state.get(tk,{})
        if old.get('cusip')!=h.get('cusip'):old={}
        cached=SESSION_QUOTES.get(normalized_symbol(tk),{})
        if old.get('nextAttemptAt','')>now.isoformat() and (not cached or due(cached,now)):continue
        pending.append((tk,h,old))
    pending.sort(key=lambda row:(row[0] not in active,row[2].get('lastAttemptAt',''),row[0]))
    # Reuse a valid quote across investors before spending network requests.
    selected=[];results={};requests=[]
    for tk,h,old in pending:
        cached=SESSION_QUOTES.get(normalized_symbol(tk))
        if cached is not None and not cached.get('error') and due(cached,now):cached=None
        if cached is not None:
            selected.append((tk,h,old));results[tk]=cached
        elif len(requests)<max(0,limit):
            selected.append((tk,h,old));requests.append(tk)
    if requests:
        try:fetched=loader(requests)
        except Exception:fetched={}
        if not isinstance(fetched,dict):fetched={}
        for tk in requests:
            q=fetched.get(tk,{'error':True})
            if not isinstance(q,dict):q={'error':True}
            results[tk]=q;SESSION_QUOTES[normalized_symbol(tk)]=q
    for tk,h,old in selected:
        q=results[tk];error=None
        try:
            if q.get('error') or not fresh_quote(q,now.timestamp()):raise ValueError('quote_unavailable')
            if normalized_symbol(q.get('symbol',tk)).upper()!=normalized_symbol(tk).upper() or q.get('currency','USD')!='USD':raise ValueError('quote_identity')
            quotes[tk]=merge_actions(quotes.get(tk,{}),q)
        except (ValueError,TypeError,KeyError) as exc:error=str(exc)
        failures=min(8,old.get('failures',0)+1) if error else 0
        delay=min(14,2**(failures-1)) if failures else 1
        state[tk]={'cusip':h.get('cusip'),'lastAttemptAt':now.isoformat(),'nextAttemptAt':(now+timedelta(days=delay)).isoformat(),'failures':failures}
        if error:state[tk]['error']=error
    return {tk:row for tk,row in state.items() if tk in holdings}


if __name__=='__main__':
    import argparse,json
    from pathlib import Path
    from trade_price_history import build,exit_performance
    from fetch_prices_all import write_prices_atomic
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=100);args=parser.parse_args()
    root=Path(__file__).resolve().parent
    configs=[c for c in json.loads((root/'investors.json').read_text())['investors'] if c.get('source13F')]
    for cfg in configs:
        for tk,q in json.loads((root/cfg['pricesFile']).read_text()).get('quotes',{}).items():
            if q.get('status')!='ceased_trading' and q.get('symbol') and not due(q,datetime.now(timezone.utc)):
                prior=SESSION_QUOTES.get(normalized_symbol(tk),{})
            if not fresh_quote(prior,now.timestamp()) or q['t']>=prior.get('t',0):SESSION_QUOTES[normalized_symbol(tk)]=q
    for cfg in configs:
        data=json.loads((root/cfg['dataFile']).read_text());path=root/cfg['pricesFile'];prices=json.loads(path.read_text());quotes=prices.setdefault('quotes',{})
        before=sum(fresh_quote(q) for q in quotes.values())
        ledger=prices.get('tradePrices',{})
        state=refresh(data,quotes,ledger.get('quoteRefresh'),limit=args.limit)
        ledger=build(data,quotes,ledger,download_limit=0);ledger['quoteRefresh']=state
        prices.update(tradePrices=ledger,exitPerf=exit_performance(ledger));write_prices_atomic(path,prices)
        print(cfg['id'],before,'->',sum(fresh_quote(q) for q in quotes.values()),flush=True)
