"""Versioned, bounded source audit before prices and AI run.

Legacy caches are re-read from SEC information tables. A filing that uses the
wrong dollar/thousand unit is normalized only with at least three independent
ordinary-share quarter-end prices. Options, principal and ambiguous symbols do
not vote. Failed lookups are retried; they never turn missing quarters into zero.
"""
import argparse
import calendar
import copy
import hashlib
import json
import math
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlencode, quote, urlparse
from urllib.request import Request, urlopen

VERSION = 1
_QUOTES = {}


def digest(rows):
    return hashlib.sha256(json.dumps(sorted([(h.get('cusip'), h.get('ticker'), h.get('putCall',''),h.get('shareType','SH'),h.get('shares'),h.get('value')) for h in rows],key=str),separators=(',',':')).encode()).hexdigest()


def actual_close(chart, end):
    """Yahoo close is split adjusted: undo ONLY splits after the sampled day."""
    meta = chart.get('meta',{})
    if meta.get('currency') != 'USD': raise ValueError('Non-USD quote')
    prices = chart['indicators']['quote'][0]['close']
    samples = [(stamp,price) for stamp,price in zip(chart.get('timestamp',[]),prices)
               if isinstance(price,(int,float)) and math.isfinite(price) and price>0 and
               datetime.fromtimestamp(stamp,timezone.utc).date() <= end]
    if not samples: raise ValueError('No quarter-end quote')
    stamp,price=max(samples)
    day=datetime.fromtimestamp(stamp,timezone.utc).date()
    if (end-day).days > 5: raise ValueError('Quote too far from quarter end')
    for split in chart.get('events',{}).get('splits',{}).values():
        if split['date'] > stamp:
            factor=float(split['numerator'])/float(split['denominator'])
            if not math.isfinite(factor) or factor<=0: raise ValueError('Invalid split')
            price *= factor
    return {'price':price,'date':day.isoformat(),'currency':'USD'}


def quarter_price(ticker, quarter):
    symbol=re.sub(r'[./]([AB])$',r'-\1',ticker)
    if not re.fullmatch(r'[A-Z][A-Z0-9-]{0,12}',symbol): raise ValueError('Unmapped symbol')
    year,q=map(int,quarter.replace(' Q',' ').split());month=q*3
    end=datetime(year,month,calendar.monthrange(year,month)[1]).date()
    if symbol not in _QUOTES:
        error=None
        # One split-inclusive history per ticker serves every audited quarter.
        for host in ['query1.finance.yahoo.com','query2.finance.yahoo.com']:
            url=f'https://{host}/v8/finance/chart/{quote(symbol)}?'+urlencode({'period1':0,'period2':int(time.time())+86400,'interval':'1d','events':'splits'})
            try:
                with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=15) as response:
                    result=json.load(response)['chart']['result'][0]
                if result['meta'].get('symbol','').upper() != symbol: raise ValueError('Symbol mismatch')
                _QUOTES[symbol]=(result,url);break
            except Exception as exc:error=exc
        if symbol not in _QUOTES:
            _QUOTES[symbol]=(None,str(error))
    chart,url=_QUOTES[symbol]
    if chart is None:raise ValueError('Quote unavailable')
    return {**actual_close(chart,end),'url':url}


def verify_units(rows, quarter, price=quarter_price):
    anchors=[]; seen=set();errors=[]
    candidates=sorted(rows,key=lambda h:(not priority([h]),-h.get('shares',0)))
    for h in candidates:
        tk=h.get('ticker','')
        if re.search(r'WARRANT|WTS|W EXP|NOTE|DEBENTURE|BOND|RIGHT',h.get('cls',''),re.I):continue
        if tk in seen or h.get('putCall') or h.get('shareType','SH')!='SH' or not h.get('shares') or not h.get('value') or not re.fullmatch(r'[A-Z][A-Z0-9./-]{0,12}',tk):continue
        seen.add(tk)
        try:
            proof=price(tk,quarter)
            if not isinstance(proof.get('price'),(int,float)) or proof['price']<=0:raise ValueError('Invalid anchor')
            per_share=h['value']/h['shares']
            agrees=[factor for factor in (1,1000,.001) if abs(per_share*factor/proof['price']-1)<=.025]
            anchors.append({'ticker':tk,'cusip':h.get('cusip'),'filedPrice':per_share,**proof,'candidates':agrees})
        except Exception as error:errors.append(tk+': '+type(error).__name__)
        if len(anchors)>=5 or len(seen)>=8:break
    agreed=set.intersection(*(set(a['candidates']) for a in anchors)) if anchors else set()
    if len(anchors)>=3 and len(agreed)==1:
        return {'status':'verified','factor':agreed.pop(),'anchors':anchors}
    return {'status':'pending','anchors':anchors,'errors':errors}


def priority(rows):
    return any(h.get('shares',0)>0 and h.get('value',0)>0 and not h.get('putCall') and h.get('shareType','SH')=='SH' and
               (h['value']/h['shares']<.5 or h['value']/h['shares']>10000) and
               not re.search(r'(?:[./-]A$)',h.get('ticker','')) for h in rows)


def sync_current(data):
    from holdings_diff import attach_previous
    cur=data.get('current',{});history=data['history'];rows=history.get('holdings',{})
    if cur.get('quarter') in rows:
        old={(h.get('cusip'),h.get('putCall',''),h.get('shareType','SH')):h for h in cur.get('holdings',[])}
        for h in rows[cur['quarter']]:
            display=old.get((h.get('cusip'),h.get('putCall',''),h.get('shareType','SH')), {})
            if not h.get('cnName') and display.get('cnName'):h['cnName']=display['cnName']
        cur['holdings']=copy.deepcopy(rows[cur['quarter']]);cur['totalValue']=sum(h['value'] for h in cur['holdings'])
    if cur.get('prevQuarter') in rows:
        cur['previousHoldings']=copy.deepcopy(rows[cur['prevQuarter']]);cur['prevTotalValue']=sum(h['value'] for h in cur['previousHoldings'])
        attach_previous(cur['holdings'],cur['previousHoldings'],previous_quarter=cur['prevQuarter'],current_quarter=cur['quarter'])
    latest_source=history.get('filing_sources',{}).get(cur.get('quarter'),{})
    if latest_source.get('amendmentType')=='RESTATEMENT':
        cur.setdefault('originalFilingDate',cur.get('filingDate'))
        cur['filingDate']=latest_source['filingDate']
    pending=history.get('excludedValueQuarters',[])
    if cur.get('quarter') in pending:
        cur['valueQuality']={'status':'units_unverified','source':history.get('filing_sources',{}).get(cur['quarter'],{}).get('url','')}
    elif cur.get('valueQuality',{}).get('status')=='units_unverified':cur.pop('valueQuality',None)


def discover_restatements(config,history,quarters,fetch,limit=3):
    """Check new 13F-HR/A filings; additive amendments are never full portfolios."""
    from fetch_13f_all import quarter_label,find_info_table_xml
    checks=history.setdefault('restatementChecks',{})
    replacements={};attempts=0
    ciks={str(history.get('filing_sources',{}).get(q,{}).get('cik') or config['cik']) for q in quarters}
    for cik in sorted(ciks):
        submissions=json.loads(fetch(f'submissions/CIK{int(cik):010d}.json'))
        table=submissions.get('filings',{}).get('recent',{})
        for i,form in enumerate(table.get('form',[])):
            if form!='13F-HR/A':continue
            q=quarter_label(table['reportDate'][i])
            if q not in quarters:continue
            accession=table['accessionNumber'][i];old=checks.get(accession,{})
            if old.get('result')=='additive':continue
            if attempts>=limit:break
            attempts+=1
            primary=table.get('primaryDocument',[])[i]
            if not re.fullmatch(r'[\w.-]+',primary):continue
            path=f"/Archives/edgar/data/{int(cik)}/{accession.replace('-','')}/{primary}"
            root=sec_xml(fetch(path))
            kind=next((e.text.strip().upper() for e in root.iter() if e.tag.split('}')[-1]=='amendmentType' and e.text),'')
            checks[accession]={'result':'restatement' if kind=='RESTATEMENT' else 'additive' if kind=='NEW HOLDINGS' else 'pending','checkedAt':datetime.now(timezone.utc).date().isoformat()}
            if kind!='RESTATEMENT':continue
            if old.get('url'):url=old['url']
            else:
                info=find_info_table_xml(cik,accession.replace('-',''),accession);url='https://www.sec.gov'+info;checks[accession]['url']=url
            f={'cik':cik,'accession':accession.replace('-',''),'accessionDashed':accession,'filingDate':table['filingDate'][i],'reportDate':table['reportDate'][i],'amendmentType':kind,'url':url}
            if f['filingDate']>history.get('filing_sources',{}).get(q,{}).get('filingDate','') and f['filingDate']>replacements.get(q,{}).get('filingDate',''):replacements[q]=f
    return replacements


def sec_xml(raw):
    from xml.etree.ElementTree import fromstring
    return fromstring(raw)


def audit_investor(key,config,limit=6,fetcher=None,price=quarter_price):
    import fetch_13f_all as sec
    from holdings_diff import update_history, attach_previous
    data=json.loads(Path(config['path']).read_text());history=data.setdefault('history',{});rows=history.get('holdings',{})
    records=history.setdefault('valueAudit',{});today=datetime.now(timezone.utc).date().isoformat()
    excluded=set(history.get('excludedValueQuarters',[]));changed=[];attempts=0
    # Enforce previously verified normalization after a normal latest-two fetch.
    for q,record in records.items():
        if record.get('version')==VERSION and record.get('status')=='verified' and q in rows and digest(rows[q])==record.get('sourceHash') and record.get('factor')!=1:
            normalized=copy.deepcopy(rows[q])
            for h in normalized:h['value']=round(h['value']*record['factor'])
            update_history(data,q,normalized);changed.append(q)
    def due(q):
        r=records.get(q,{})
        if r.get('version')!=VERSION or r.get('normalizedHash')!=digest(rows[q]):return True
        if r.get('status')!='verified':return r.get('checkedAt')!=today
        # Rolling re-verification also discovers replacement/amended sources.
        return r.get('checkedAt','')<(datetime.now(timezone.utc).date()-timedelta(days=180)).isoformat()
    queue=sorted((q for q in rows if due(q)),key=lambda q:(q not in excluded,not priority(rows[q]),q!=data.get('current',{}).get('quarter'),records.get(q,{}).get('checkedAt',''),q))
    filings=None;replacements={}
    if fetcher is None and (excluded or any(r.get('status')=='pending' for r in records.values())):
        unresolved=excluded | {q for q,r in records.items() if r.get('status')=='pending'}
        try:replacements=discover_restatements(config,history,unresolved,sec.sec_fetch)
        except Exception as error:history['restatementLookupError']=type(error).__name__+': '+str(error)
        for q in replacements:
            if q in queue:queue.remove(q)
        queue=list(replacements)+queue
    for q in queue[:limit]:
        attempts+=1;print(f'{key} audit {q}',flush=True)
        try:
            source=replacements.get(q) or history.get('filing_sources',{}).get(q)
            if not source or not source.get('url') or not source.get('filingDate'):
                if filings is None:filings=sec.investor_filings(config,True)
                hits=[f for f in filings if sec.quarter_label(f['reportDate'])==q]
                if not hits:raise ValueError('No complete primary filing for quarter')
                f=hits[0];path=sec.find_info_table_xml(f.get('cik',config['cik']),f['accession'],f['accessionDashed'])
                source={**f,'url':'https://www.sec.gov'+path}
            raw=fetcher(source['url']) if fetcher else sec.sec_fetch(urlparse(source['url']).path)
            parsed=sec.parse_holdings(raw,filing_date=source['filingDate'])
            proof=verify_units(parsed,q,price)
            record={'version':VERSION,'checkedAt':today,'source':source['url'],'filingDate':source['filingDate'],
                    'sourceDigest':hashlib.sha256(raw).hexdigest(),'sourceHash':digest(parsed),**proof}
            if proof['status']=='verified':
                factor=proof['factor']
                for h in parsed:h['value']=round(h['value']*factor)
                previous={ (h.get('cusip'),h.get('putCall',''),h.get('shareType','SH')):h for h in rows[q] }
                for h in parsed:
                    old=previous.get((h.get('cusip'),h.get('putCall',''),h.get('shareType','SH')), {})
                    for field in ('cnName',):
                        if old.get(field):h[field]=old[field]
                if digest(rows[q])!=digest(parsed):changed.append(q)
                update_history(data,q,parsed);history.setdefault('filing_sources',{})[q]=source
                excluded.discard(q)
            elif q in excluded or any(a['candidates'] and 1 not in a['candidates'] for a in proof['anchors']):
                excluded.add(q)
            record['normalizedHash']=digest(rows[q]);records[q]=record
        except Exception as error:
            records[q]={'version':VERSION,'status':'pending','checkedAt':today,'normalizedHash':digest(rows[q]),'error':str(error)}
    history['excludedValueQuarters']=sorted(excluded)
    if excluded:history['valueQualityNote']='金额单位尚未通过原始申报与独立季末行情交叉核验；暂不计入趋势或价格估算，后续自动重试。'
    else:history.pop('valueQualityNote',None)
    # Rebuild comparisons from consecutive actual quarters after source repairs.
    qs=sorted(rows,key=sec._quarter_sort_key)
    for i,q in enumerate(qs):
        if i:
            y,n=map(int,q.replace(' Q',' ').split());py,pn=map(int,qs[i-1].replace(' Q',' ').split())
            if y*4+n==py*4+pn+1:attach_previous(rows[q],rows[qs[i-1]],previous_quarter=qs[i-1],current_quarter=q)
    sync_current(data);sec.save_data(config['path'],data)
    print(f'{key}: {attempts} sources checked; {len(set(changed))} quarters repaired; {len(excluded)} withheld',flush=True)
    return data


def main():
    import fetch_13f_all as sec
    p=argparse.ArgumentParser();p.add_argument('--investor',choices=list(sec.INVESTOR_CONFIG));p.add_argument('--limit',type=int,default=6);a=p.parse_args()
    for key,config in sec.INVESTOR_CONFIG.items():
        if a.investor and key!=a.investor:continue
        if Path(config['path']).exists():audit_investor(key,config,a.limit)

if __name__=='__main__':main()
