"""Bounded market-history downloads for broad institutional portfolios.

One original, unadjusted-for-dividends daily series serves every cost quarter
for a security. Failed downloads stay unavailable; filing proxies remain labeled.
"""
import bisect
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.parse import quote, urlencode
import zlib

ROOT=Path(__file__).resolve().parent
SERIES={}


def is_share_split(event,holding):
    # Price vendors also put spin-off adjustments in the "splits" feed.
    # Fractional economic adjustments need issuer proof before changing shares.
    from holdings_diff import VERIFIED_SPLITS
    ratio=event['factor']
    if abs(ratio-round(ratio))<1e-9 or abs(1/ratio-round(1/ratio))<1e-9:return True
    return any((holding.get('cusip')==a['cusip'] or holding.get('ticker')==a['ticker']) and abs(ratio-a['factor'])<1e-9 and abs((datetime.fromisoformat(event['date'])-datetime.fromisoformat(a['date'])).days)<=10 for a in VERIFIED_SPLITS)


def split_events(result):
    """Read explicit exchange-event fields; never infer a split from prices."""
    rows=[]
    for row in result.get('events',{}).get('splits',{}).values():
        stamp=row.get('date');num=row.get('numerator');den=row.get('denominator')
        if any(type(x) not in (int,float) for x in (stamp,num,den)) or not stamp>0 or not 0<num<1e12 or not 0<den<1e12:raise ValueError('Invalid reported split event')
        if stamp>time.time()+600:continue  # announced but not yet effective
        rows.append({'date':datetime.fromtimestamp(stamp,timezone.utc).date().isoformat(),'factor':num/den})
    return sorted(rows,key=lambda r:r['date'])


def merge_actions(old,fresh):
    rows={r['date']:r for r in old.get('shareActions',[])}
    for row in fresh.get('shareActions',[]):
        if row['date'] in rows and abs(rows[row['date']]['factor']-row['factor'])>1e-9:raise ValueError('Conflicting split evidence')
        rows[row['date']]=row
    result={**fresh,'shareActions':sorted(rows.values(),key=lambda r:r['date'])}
    starts=[q['shareActionsSince'] for q in (old,fresh) if q.get('shareActionsSince')]
    if starts:result['shareActionsSince']=min(starts)
    return result


def normalized_symbol(ticker):
    return re.sub(r'[./]([AB])$',r'-\1',ticker)


def checked_series(result,ticker):
    meta=result['meta'];expected=normalized_symbol(ticker)
    if meta.get('symbol','').upper()!=expected.upper() or meta.get('currency')!='USD':
        raise ValueError('Market series identity/currency differs from requested security')
    stamps=result.get('timestamp',[]);values=result.get('indicators',{}).get('quote',[{}])[0]
    if stamps!=sorted(set(stamps)):raise ValueError('Market timestamps are not unique and ordered')
    if any(len(values.get(k,[]))!=len(stamps) for k in ['close','low','high']):raise ValueError('Incomplete daily candle columns')
    q={'c':meta.get('regularMarketPrice'),'t':meta.get('regularMarketTime'),'currency':'USD','symbol':meta['symbol'],'verifiedName':meta.get('longName') or meta.get('shortName'),'source':'yahoo_chart','sourceURL':'https://finance.yahoo.com/quote/'+quote(expected,safe='')+'/','fetchedAt':datetime.now(timezone.utc).isoformat()}
    from quote_coverage import valid_quote
    if not valid_quote(q) or time.time()-q['t']>7*86400:raise ValueError('No current dated trading quote')
    q['shareActions']=split_events(result)
    return {'timestamps':stamps,'values':values},q


def download(ticker,start,root=ROOT,get=None):
    cache=Path(root)/'.cache/market-series';cache.mkdir(parents=True,exist_ok=True)
    path=cache/(hashlib.sha256((ticker+'|'+str(start)).encode()).hexdigest()+'.json.z')
    if path.exists() and time.time()-path.stat().st_mtime<6*3600:
        try:
            series,q=checked_series(json.loads(zlib.decompress(path.read_bytes())),ticker)
            q['shareActionsSince']=datetime.fromtimestamp(start,timezone.utc).date().isoformat()
            return series,q
        except (ValueError,KeyError,zlib.error,json.JSONDecodeError):pass
    if get is None:
        import requests
        get=lambda url: requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=30)
    last=None
    for host in ['query1.finance.yahoo.com','query2.finance.yahoo.com']:
        url=f'https://{host}/v8/finance/chart/{quote(normalized_symbol(ticker),safe="")}?'+urlencode(dict(period1=start,period2=int(time.time())+86400,interval='1d',events='splits'))
        try:
            response=get(url);response.raise_for_status();result=response.json()['chart']['result'][0]
            series,q=checked_series(result,ticker)
            q['shareActionsSince']=datetime.fromtimestamp(start,timezone.utc).date().isoformat()
            path.write_bytes(zlib.compress(json.dumps(result).encode()))
            return series,q
        except Exception as exc:last=exc
    raise ValueError(str(last))


def window(ticker,start,end):
    if ticker not in SERIES:return False,None
    series=SERIES[ticker]
    if series is None:return True,None
    stamps=series['timestamps'];a=bisect.bisect_left(stamps,start);b=bisect.bisect_left(stamps,end)
    # Preserve dates and weights: exclude incomplete candles, never fill a gap.
    rows=list(zip(*(series['values'][k][a:b] for k in ['close','high','low'])))
    rows=[r for r in rows if all(isinstance(x,(int,float)) and x>0 for x in r)]
    if not rows:return True,None
    return True,dict(zip(['closes','highs','lows'],map(list,zip(*rows))))


def prefetch(tickers,start,workers=4,loader=download):
    quotes={};tickers=sorted(set(tickers))
    with ThreadPoolExecutor(max_workers=min(4,max(1,workers))) as pool:
        futures={pool.submit(loader,tk,start):tk for tk in tickers}
        for n,future in enumerate(as_completed(futures),1):
            tk=futures[future]
            try:SERIES[tk],quotes[tk]=future.result()
            except Exception as exc:SERIES[tk]=None;quotes[tk]={'error':True,'reason':type(exc).__name__}
            if n%50==0 or n==len(tickers):print(f'Market history {n}/{len(tickers)}; {sum(not q.get("error") for q in quotes.values())} verified',flush=True)
    return quotes


def prefetch_quotes(tickers,workers=4):
    def quote_and_actions(ticker):
        import requests
        for host in ['query1.finance.yahoo.com','query2.finance.yahoo.com']:
            try:
                response=requests.get(f'https://{host}/v8/finance/chart/{quote(normalized_symbol(ticker),safe="")}?range=2y&interval=1mo&events=splits',headers={'User-Agent':'Mozilla/5.0'},timeout=30)
                response.raise_for_status();result=response.json()['chart']['result'][0]
                _,q=checked_series(result,ticker)
                q['shareActionsSince']=datetime.fromtimestamp(time.time()-2*365*86400,timezone.utc).date().isoformat()
                return q
            except Exception:continue
        return {'error':True}
    result={}
    with ThreadPoolExecutor(max_workers=min(4,max(1,workers))) as pool:
        futures={pool.submit(quote_and_actions,tk):tk for tk in sorted(set(tickers))}
        for future in as_completed(futures):
            tk=futures[future]
            try:result[tk]=future.result()
            except Exception:result[tk]={'error':True}
    return result
