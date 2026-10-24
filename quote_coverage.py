"""Repair current security identities and quotes; never manufacture a market price."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import time
import urllib.request
from urllib.parse import quote

ROOT=Path(__file__).resolve().parent

def warrant_reference(holding, current):
    if re.search(r'\bWARRANT\b',holding.get('cls',''),re.I) and holding.get('shares',0)>0 and current.get('sourceFiling'):
        return dict(status='filing_reference',ticker=holding['ticker'],cusip=holding['cusip'],
                    filedUnitValue=holding['value']/holding['shares'],asOf=current['periodEnd'],sourceURL=current['sourceFiling'])
    return None

def load(path):return json.loads(path.read_text())
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def symbol(ticker):
    if ticker.endswith('.HK'):return ticker[:-3].lstrip('0').zfill(4)+'.HK'
    return re.sub(r'[/.]([AB])$',r'-\1',ticker)

def yahoo_quote(ticker):
    expected=symbol(ticker)
    for host in ['query1.finance.yahoo.com','query2.finance.yahoo.com']:
        try:
            url=f'https://{host}/v8/finance/chart/{quote(expected,safe="")}?interval=1d&range=5d'
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(req,timeout=15) as response:payload=json.load(response)
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                if isinstance(exc, urllib.error.HTTPError) and exc.code in (401,403,429):
                    raise
                # A second HTTP transport handles transient TLS/proxy failures;
                # identity, currency and trading-date checks below still apply.
                import requests
                response=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=15)
                response.raise_for_status();payload=response.json()
            result=payload['chart']['result'][0];meta=result['meta']
            if symbol(meta['symbol']).upper()!=expected.upper():raise ValueError('Quote identity mismatch')
            currency='HKD' if ticker.endswith('.HK') else 'USD'
            if meta.get('currency')!=currency:raise ValueError('Quote currency mismatch')
            price=meta['regularMarketPrice'];stamp=meta['regularMarketTime']
            if not isinstance(price,(int,float)) or price<=0 or not isinstance(stamp,(int,float)) or not 0<stamp<=time.time()+600:raise ValueError('Invalid quote')
            if time.time()-stamp>7*86400:raise ValueError('No recent trading price; review listing status')
            q={'c':price,'t':stamp,'currency':currency,'source':'yahoo_chart','sourceURL':f'https://finance.yahoo.com/quote/{quote(expected,safe="")}/','symbol':meta['symbol'],'verifiedName':meta.get('longName') or meta.get('shortName'),'fetchedAt':datetime.now(timezone.utc).isoformat()}
            for key,field in [('h','regularMarketDayHigh'),('l','regularMarketDayLow')]:
                if isinstance(meta.get(field),(int,float)):q[key]=meta[field]
            closes=[n for n in result.get('indicators',{}).get('quote',[{}])[0].get('close',[]) if isinstance(n,(int,float)) and n>0]
            if len(closes)>1:q['pc']=closes[-2]
            return q
        except Exception:
            continue
    return {'error':True}

def valid_quote(q):return type(q.get('c')) in (int,float) and math.isfinite(q['c']) and q['c']>0 and not q.get('error') and type(q.get('t')) in (int,float) and math.isfinite(q['t']) and 0<q['t']<=time.time()+600

def market_quote(ticker):
    q=yahoo_quote(ticker)
    if valid_quote(q):return q
    if ticker.endswith('.HK'):
        from fetch_prices_all import get_hk_prices
        q=get_hk_prices([ticker]).get(ticker,{})
        if valid_quote(q) and q.get('currency')=='HKD' and time.time()-q['t']<=7*86400:
            return {**q,'symbol':symbol(ticker),'fetchedAt':datetime.now(timezone.utc).isoformat()}
    return {'error':True}

def issuer_key(name):
    words=re.findall(r'[A-Z0-9]+',name.upper())
    aliases={'HLDGS':'HOLDINGS','HLDG':'HOLDINGS','HL':'HOLDINGS','INTL':'INTERNATIONAL','SYS':'SYSTEMS','PUB':'PUBLIC','CO':'COMPANY'}
    legal={'INC','INCORPORATED','CORP','CORPORATION','LTD','LIMITED','PLC','PUBLIC','COMPANY','DEL'}
    return ' '.join(w for w in (aliases.get(w,w) for w in words) if w not in legal)

def resolve_active(root,configs):
    import resolve_unmapped_tickers as resolver
    candidates=[]
    for inv in configs:
        quotes=load(root/inv['pricesFile']).get('quotes',{})
        for h in load(root/inv['dataFile'])['current']['holdings']:
            q=quotes.get(h['ticker'],{})
            if h.get('cusip') and h.get('shareType','SH')=='SH' and (h['ticker'].startswith('?') or not valid_quote(q) or q.get('stale') or time.time()-q.get('t',0)>3*86400):
                candidates.append(h)
    if not candidates:return
    try:
        from fetch_13f_all import sec_fetch
        directory=json.loads(sec_fetch('/files/company_tickers.json')).values()
    except Exception:return
    names={}
    for row in directory:names.setdefault(issuer_key(row['title']),[]).append(row)
    path=root/'security_symbol_changes.json';changes=load(path) if path.exists() else {'version':1,'entries':{}}
    resolved=load(root/'resolved_cusip_map.json') if (root/'resolved_cusip_map.json').exists() else {};renames={}
    for h in candidates:
        matches=names.get(issuer_key(h['name']),[])
        tickers={r['ticker'] for r in matches}
        if len(tickers)!=1 or re.search(r'PFD|PREF|WARRANT|NOTE',h.get('cls','').upper()):continue
        tk=tickers.pop();q=yahoo_quote(tk)
        if not valid_quote(q) or issuer_key(q.get('verifiedName') or '')!=issuer_key(h['name']):continue
        resolved[h['cusip']]=tk
        record={'ticker':tk,'oldSymbols':[h['ticker']] if not h['ticker'].startswith('?') and h['ticker']!=tk else [],'issuer':h['name'],'sourceURL':'https://www.sec.gov/files/company_tickers.json','quoteSource':q['sourceURL'],'checkedAt':datetime.now(timezone.utc).isoformat()}
        previous=changes['entries'].get(h['cusip'],{})
        record['oldSymbols']=sorted(set(record['oldSymbols']+previous.get('oldSymbols',[])))
        changes['entries'][h['cusip']]=record;renames[h['cusip']]=record
    if renames:
        save(path,changes);save(root/'resolved_cusip_map.json',resolved)
        resolver.backfill_data_files([str(root/i['dataFile']) for i in configs],resolved,renames)

def coverage(root=ROOT):
    root=Path(root);issues=[];count=0
    for inv in load(root/'investors.json')['investors']:
        data=load(root/inv['dataFile']);prices=load(root/inv['pricesFile'])
        for h in data['current']['holdings']:
            if h.get('shareType','SH')!='SH':continue
            from security_lifecycle import event_for
            if event_for(h,root):continue
            if qref := warrant_reference(h,data['current']):
                if prices.get('quotes',{}).get(h['ticker']) == qref:
                    continue  # dated filed unit value, explicitly not a live quote
            count+=1;tk=h['ticker'];q=prices.get('quotes',{}).get(tk,{})
            if tk.startswith('?') or not valid_quote(q) or q.get('stale') or time.time()-q.get('t',0)>7*86400:issues.append({'investor':inv['id'],'ticker':tk,'cusip':h.get('cusip'),'name':h['name'],'reason':'unmapped' if tk.startswith('?') else 'missing_or_outdated_quote'})
    return {'checkedAt':datetime.now(timezone.utc).isoformat(),'positions':count,'missing':issues}

def refresh(root=ROOT,all_quotes=False,workers=4):
    root=Path(root)
    import resolve_unmapped_tickers as resolver
    from fetch_13f_all import CUSIP_TICKER_MAP
    configs=load(root/'investors.json')['investors']
    resolver.backfill_data_files([str(root/i['dataFile']) for i in configs],{**resolver.load_resolved_map(),**CUSIP_TICKER_MAP})
    resolve_active(root,configs)
    files={i['pricesFile']:load(root/i['pricesFile']) for i in configs};wanted=set()
    aliases=load(root/'security_symbol_changes.json').get('entries',{}) if (root/'security_symbol_changes.json').exists() else {}
    for inv in configs:
        for h in load(root/inv['dataFile'])['current']['holdings']:
            alias=aliases.get(h.get('cusip'),{})
            costs=files[inv['pricesFile']].get('costBasis',{})
            if alias.get('preserveCost',True) and alias.get('ticker')==h['ticker'] and h['ticker'] not in costs:
                prior=next((costs[old] for old in alias.get('oldSymbols',[]) if old in costs),None)
                if prior is not None:costs[h['ticker']]=prior
            from security_lifecycle import event_for
            event=event_for(h,root)
            if event:
                files[inv['pricesFile']].setdefault('quotes',{})[h['ticker']]={'status':'ceased_trading','event':event}
                continue
            if re.search(r'\bWARRANT\b',h.get('cls',''),re.I):
                q=files[inv['pricesFile']].get('quotes',{}).get(h['ticker'],{})
                if not valid_quote(q):
                    files[inv['pricesFile']].setdefault('quotes',{})[h['ticker']]=warrant_reference(h,load(root/inv['dataFile'])['current'])
                    continue
            if h.get('shareType','SH')!='SH' or h['ticker'].startswith('?'):continue
            q=files[inv['pricesFile']].get('quotes',{}).get(h['ticker'],{})
            if all_quotes or not valid_quote(q) or q.get('stale') or time.time()-q.get('t',0)>3*86400:wanted.add(h['ticker'])
    results={}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(market_quote,tk):tk for tk in wanted}
        for future in as_completed(futures):
            tk=futures[future];results[tk]=future.result()
            print('Quote',tk,'ok' if valid_quote(results[tk]) else 'retry',flush=True)
    for inv in configs:
        path=root/inv['pricesFile'];data=files[inv['pricesFile']];quotes=data.setdefault('quotes',{})
        for h in load(root/inv['dataFile'])['current']['holdings']:
            tk=h['ticker'];fresh=results.get(tk);old=quotes.get(tk,{})
            if fresh and valid_quote(fresh) and (not valid_quote(old) or fresh['t']>=old['t']):quotes[tk]=fresh
            elif fresh and not valid_quote(fresh) and valid_quote(old):quotes[tk]={**old,'stale':True}
        data['quoteCoverageCheckedAt']=datetime.now(timezone.utc).isoformat()
        if any(valid_quote(results.get(h['ticker'],{})) for h in load(root/inv['dataFile'])['current']['holdings']):data['updatedAt']=data['quoteCoverageCheckedAt']
        save(path,data)
    return coverage(root)

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--all',action='store_true');p.add_argument('--root',default=str(ROOT));a=p.parse_args()
    if not a.check:refresh(Path(a.root),a.all)
    report=coverage(Path(a.root));print(json.dumps(report,ensure_ascii=False))
    if report['missing']:raise SystemExit('Current stock quote coverage is incomplete')

if __name__=='__main__':main()
