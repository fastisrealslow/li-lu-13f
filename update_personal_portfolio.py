"""Discover annual filings, replay issuer rules, validate, and refresh quotes.

Financial values never come from Yahoo, news, or an LLM. Issuer extraction is
transactional: a failed report preserves all of that issuer's verified years.
"""
import argparse
import copy
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import quote as urlquote, urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from magic_formula import calculate, validate_company, validate_dataset
from personal_reports import InlineReport, PDFReport, extract_recipe, ads_conversion

ROOT=Path(__file__).resolve().parent
UA='PersonalPortfolioResearch/1.0 (+https://github.com/fastisrealslow/li-lu-13f)'
FAILED_HOSTS=set()


def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')


def request(url, data=None):
    host=urlsplit(url).hostname
    if host in FAILED_HOSTS:raise OSError('Source temporarily unavailable in this run: '+str(host))
    deadline=time.monotonic()+60
    headers={'User-Agent':UA,'Accept':'application/json,text/html,application/pdf,*/*'}
    if 'sec.gov' in url:
        from fetch_13f_all import USER_AGENT
        headers['User-Agent']=USER_AGENT
    if 'cninfo.com.cn' in url: headers.update({'User-Agent':'Mozilla/5.0','Referer':'https://www.cninfo.com.cn/'})
    if 'yahoo.com' in url: headers['User-Agent']='Mozilla/5.0'
    body=urlencode(data).encode() if data else None
    if body:headers['Content-Type']='application/x-www-form-urlencoded'
    last=None
    for attempt in range(2):
        try:
            if time.monotonic()>=deadline:raise TimeoutError('Total source download deadline exceeded')
            with urlopen(Request(url,data=body,headers=headers),timeout=15) as res:
                chunks=[];size=0;read=getattr(res,'read1',res.read)
                while True:
                    if time.monotonic()>=deadline:raise TimeoutError('Total source download deadline exceeded')
                    chunk=read(65536)
                    if not chunk:return b''.join(chunks)
                    size+=len(chunk)
                    if size>60_000_000:raise ValueError('Source document exceeds download limit')
                    chunks.append(chunk)
        except Exception as exc:
            last=exc
            if not attempt:time.sleep(1)
    if not isinstance(last,HTTPError) or last.code in (403,429,500,502,503,504):FAILED_HOSTS.add(host)
    raise last


def report_bytes(url, cache):
    key=hashlib.sha256(url.encode()).hexdigest();path=cache/key
    if path.exists() and time.time()-path.stat().st_mtime<7*86400: return path.read_bytes()
    raw=request(url)
    if not raw.startswith(b'%PDF') and b'<html' not in raw[:5000].lower():raise ValueError('Financial report response is not PDF/HTML')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    return raw


def original_report(url, cache):
    raw=report_bytes(url,cache)
    return PDFReport(raw) if raw.startswith(b'%PDF') else InlineReport(raw)


def read_period(profile, sources, reports, year=None):
    year=year or profile['year'];sid=profile['sourceId'];report=reports[sid]
    p={'end':f'{year}-12-31','months':12,'audited':profile.get('audited',True),'facts':{},'ebitAdjustments':[]}
    for field,selector in profile['selectors'].items():
        override=profile.get('overrides',{}).get(field)
        field_sid=override['sourceId'] if override else sid
        selector=override['selector'] if override else selector
        fact=extract_recipe(reports[field_sid],selector,year)
        fact.update(sourceId=field_sid,label=profile['labels'][field]);p['facts'][field]=fact
    for spec in profile.get('adjustments',[]):
        f=extract_recipe(report,spec['selector'],year);f['value']*=spec['coefficient']
        f.update(sourceId=sid,label=spec['label']);p['ebitAdjustments'].append(f)
    p['evCashLikeFinancialAssets']=dict(extract_recipe(report,profile['cashLike'],year),sourceId=sid,label='可抵扣 EV 的流动存款／证券')
    return p


def discover(profile):
    d=profile['discovery'];kind=d['kind'];code=d['code']
    if kind=='sec':
        table=json.loads(request(f'https://data.sec.gov/submissions/CIK{int(code):010d}.json'))['filings']['recent']
        candidates=[]
        for i,form in enumerate(table['form']):
            if form not in ('20-F','20-F/A') or not table['reportDate'][i].endswith('-12-31'):continue
            year=int(table['reportDate'][i][:4]);acc=table['accessionNumber'][i].replace('-','')
            candidates.append({'year':year,'url':f'https://www.sec.gov/Archives/edgar/data/{int(code)}/{acc}/{table["primaryDocument"][i]}','date':table['filingDate'][i],'amendment':form.endswith('/A')})
        return sorted(candidates,key=lambda r:(r['year'],r['date']),reverse=True)
    if kind=='cninfo':
        stamp=datetime.now(timezone.utc).date();begin=f'{stamp.year-2}-01-01'
        result=json.loads(request('https://www.cninfo.com.cn/new/hisAnnouncement/query',{
            'stock':str(code)+',gssz0000858','tabName':'fulltext','pageNum':1,'pageSize':50,
            'column':'szse','plate':'sz','category':'category_ndbg_szsh;',
            'seDate':begin+'~'+stamp.isoformat(),'isHLtitle':'false'}))
        records=[]
        for row in result.get('announcements',[]):
            title=re.sub('<[^>]+>','',row['announcementTitle'])
            m=re.search(r'(20\d{2})\s*年?年度报告',title)
            if not m or re.search(r'摘要|英文|取消|关于|提示',title):continue
            records.append({'year':int(m[1]),'url':urljoin('https://static.cninfo.com.cn/',row['adjunctUrl']),
                'date':str(row.get('announcementTime','')),'amendment':bool(re.search('更新|修订',title))})
        return sorted(records,key=lambda r:(r['year'],r['date']),reverse=True)
    # This is a separate issuer-bound annual-report query, not a spin-off feed.
    from fetch_spinoff import get_opener
    from hk_listing_completion import issuer_lookup,issuer_filings
    opener=get_opener();issuers=issuer_lookup(str(code),opener,'EN')
    issuer=next((i for i in issuers if i['code']==str(code).zfill(5)),None)
    if not issuer:raise ValueError('HKEX issuer not found')
    rows=issuer_filings(issuer,opener,'EN');records=[]
    for r in rows:
        title=r.get('title','')
        m=re.search(r'Annual Report\s*[-–:]?\s*(20\d{2})|(20\d{2})\s*Annual Report',title,re.I)
        if m and not re.search(r'ESG|Environmental|Cancellation',title,re.I):records.append({'year':int(m[1] or m[2]),'url':r['url'],'date':r.get('date',''),'amendment':bool(re.search(r'revised|amended|restated|updated',title,re.I))})
    return sorted(records,key=lambda r:(r['year'],r['date']),reverse=True)


def retarget(profile, year, sid):
    result=copy.deepcopy(profile);old=str(profile['year'])
    result['year']=year;result['sourceId']=sid
    # Fiscal-year text in selectors moves; numerical facts are never templated.
    digits='零一二三四五六七八九';delta=year-profile['year']
    chinese=lambda n:''.join(digits[int(d)] for d in str(n))
    replacements={str(y):str(y+delta) for y in range(profile['year']-3,profile['year']+2)}
    replacements.update({chinese(y):chinese(y+delta) for y in range(profile['year']-3,profile['year']+2)})
    pattern='|'.join(map(re.escape,sorted(replacements,key=len,reverse=True)))
    def visit(value):
        if isinstance(value,str):return re.sub(pattern,lambda m:replacements[m[0]],value)
        if isinstance(value,list):return [visit(v) for v in value]
        if isinstance(value,dict):return {k:visit(v) for k,v in value.items()}
        return value
    result['selectors']=visit(result['selectors']);result['adjustments']=visit(result.get('adjustments',[]));result['cashLike']=visit(result['cashLike'])
    result.pop('overrides',None)
    return result


def quote_data(ticker, currency):
    error=None
    for host in ('query1.finance.yahoo.com','query2.finance.yahoo.com'):
        try:
            url='https://'+host+'/v8/finance/chart/'+urlquote(ticker,safe='')+'?range=1mo&interval=1d'
            payload=json.loads(request(url))['chart']
            if payload.get('error') or not payload.get('result'):raise ValueError('Quote provider did not return '+ticker)
            chart=payload['result'][0];meta=chart['meta']
            if meta.get('symbol','').upper()!=ticker.upper() or meta.get('currency')!=currency:raise ValueError('Quote symbol or currency mismatch')
            break
        except Exception as exc:error=exc
    else:raise error
    # Use the most recent actual DAILY close and that session's timestamp.
    regular=meta.get('currentTradingPeriod',{}).get('regular',{})
    session_duration=regular.get('end',0)-regular.get('start',0)
    pairs=[(ts,price) for ts,price in zip(chart.get('timestamp',[]),chart['indicators']['quote'][0]['close'])
        if price is not None and price>0 and (session_duration<=0 or ts+session_duration<=time.time())]
    if not pairs:raise ValueError('No valid dated closing quote')
    ts,price=pairs[-1]
    date=datetime.fromtimestamp(ts,ZoneInfo(meta.get('exchangeTimezoneName','UTC'))).date().isoformat()
    return {'price':round(price,int(meta.get('priceHint',6))),'currency':currency,'asOf':date,'sessionTimestamp':ts,'quoteType':'daily_close',
        'sourceUrl':'https://finance.yahoo.com/quote/'+urlquote(ticker,safe='')+'/','source':'Yahoo Finance daily close'}


def rebuild_results(c, quotes, failures):
    c.setdefault('results',{})
    for listing in c['listings']:
        ticker=listing['ticker']
        try:
            key=(ticker,listing['currency']);q=copy.deepcopy(quotes.setdefault(key,quote_data(*key))) if key not in quotes else copy.deepcopy(quotes[key])
            q.update(ticker=ticker,ordinarySharesPerQuoteUnit=listing['ordinarySharesPerQuoteUnit'])
            if q['currency']==c['currency']:q.update(fxToReportCurrency=1,fxDate=q['asOf'][:10])
            else:
                pair=q['currency']+c['currency']+'=X';fk=(pair,c['currency'])
                fx=quotes[fk] if fk in quotes else quote_data(*fk);quotes[fk]=fx
                q.update(fxToReportCurrency=fx['price'],fxDate=fx['asOf'][:10],fxSourceUrl=fx['sourceUrl'])
            c['results'][ticker]={str(years):calculate(c,q,years) for years in (1,3)}
        except Exception as exc:
            failures.append(c['id']+' / '+ticker+' quote: '+str(exc))
            # Recalculate against retained dated quote after financial updates.
            old=c['results'].get(ticker,{}).get('1',{}).get('quote')
            if old:c['results'][ticker]={str(years):calculate(c,old,years) for years in (1,3)}


def verify_existing_reports(company,profile,reports,checked):
    """A byte change is acceptable only after replaying every consumed number."""
    changed={sid for sid,report in reports.items() if report.digest!=company['sources'][sid]['sha256']}
    replayed={};covered=set()
    for spec in profile['annuals']:
        extracted=read_period(spec,company['sources'],reports)
        stored=next(p for p in company['annuals'] if int(p['end'][:4])==spec['year'])
        if set(extracted['facts'])!=set(stored['facts']):raise ValueError('Report fact scope changed')
        for field,fact in extracted['facts'].items():
            if abs(fact['value']-stored['facts'][field]['value'])>.001:raise ValueError('Report replay mismatch: '+field)
            covered.add(fact['sourceId'])
        if abs(extracted['evCashLikeFinancialAssets']['value']-stored['evCashLikeFinancialAssets']['value'])>.001:raise ValueError('Cash-like replay mismatch')
        covered.add(extracted['evCashLikeFinancialAssets']['sourceId'])
        if [a['value'] for a in extracted['ebitAdjustments']]!=[a['value'] for a in stored['ebitAdjustments']]:raise ValueError('EBIT adjustments replay mismatch')
        covered.update(a['sourceId'] for a in extracted['ebitAdjustments'])
        replayed[extracted['end']]=extracted
    ads=None
    if company.get('adsConversion'):
        sid=company['adsConversion']['sourceId'];ads=ads_conversion(reports[sid])
        if ads['value']!=company['adsConversion']['value']:raise ValueError('Original-report ADS conversion no longer matches')
        covered.add(sid)
    if changed-covered:raise ValueError('Changed source has no complete financial replay: '+', '.join(sorted(changed-covered)))
    if changed:
        for sid in changed:
            source=company['sources'][sid];source['previousSha256']=source['sha256'];source['sha256']=reports[sid].digest
            source.update(verificationMethod='exact_financial_replay',verifiedAt=checked)
        company['annuals']=[replayed.get(p['end'],p) for p in company['annuals']]
        if ads:company['adsConversion']={**ads,'sourceId':company['adsConversion']['sourceId']}
        if company.get('financialStatus',{}).get('status')!='updated':
            company['financialStatus']={'checkedAt':checked,'status':'checked','message':'原始财报已复核，利润、现金、债务、股本及 ADS 比例等计算数据均与留存记录一致。'}
    return len(changed)


def update(data,config,cache,verify=False,discovery=True,quotes_enabled=True):
    checked=now();failures=[];quotes={}
    for c in data['companies']:
        print(f"Personal {c['id']}: checking original reports",flush=True)
        profile=next(p for p in config['companies'] if p['id']==c['id'])
        original_company=copy.deepcopy(c);original_profile=copy.deepcopy(profile);original_sources=copy.deepcopy(config['sources'])
        try:
            latest=max(profile['annuals'],key=lambda p:p['year'])
            candidates=discover(profile) if discovery else []
            current_sources={s['url'] for s in c['sources'].values()}
            new=next((r for r in candidates if (r['year']>latest['year'] or r['year']==latest['year'] and r.get('amendment')) and r['url'] not in current_sources),None)
            if new:
                sid=c['id']+'-'+str(new['year'])+'-'+hashlib.sha256(new['url'].encode()).hexdigest()[:10]
                report=original_report(new['url'],cache)
                if new.get('amendment') and isinstance(report,InlineReport) and not any('ProfitLossFromOperatingActivities' in f['concept'] or 'OperatingIncomeLoss' in f['concept'] for f in report.facts):
                    # Cover/auditor-only amendment: keep the complete 20-F and
                    # retain its identity in the status for the next check.
                    c['financialStatus']={'checkedAt':checked,'status':'amendment_without_tables','message':'已检查年度报告修订文件；修订文件未重列经营利润报表，计算仍采用原完整年报。','url':new['url']}
                    new=None
                else:
                    new_profile=retarget(latest,new['year'],sid);reports={sid:report}
                    candidate=copy.deepcopy(c);candidate['sources'][sid]={'url':new['url'],'kind':'annual_report','title':str(new['year'])+' 年度报告','sha256':report.digest}
                    if any(l['ordinarySharesPerQuoteUnit']>1 for l in candidate['listings']):
                        proof=dict(ads_conversion(report),sourceId=sid);candidate['adsConversion']=proof
                        for listing in candidate['listings']:
                            if listing['ordinarySharesPerQuoteUnit']>1:
                                if listing['ordinarySharesPerQuoteUnit']!=proof['value']:candidate.get('results',{}).pop(listing['ticker'],None)
                                listing['ordinarySharesPerQuoteUnit']=proof['value']
                    p=read_period(new_profile,candidate['sources'],reports)
                    candidate['annuals']=[p]+[a for a in candidate['annuals'] if a['end']!=p['end']]
                    candidate['annuals']=sorted(candidate['annuals'],key=lambda a:a['end'],reverse=True)[:3]
                    # Re-read the prior year's comparative column too. A new
                    # report may restate it; old values cannot silently survive.
                    comparative_template=next((a for a in profile['annuals'] if a['year']==latest['year']-1 and a['sourceId']==latest['sourceId']),None)
                    comparative_profile=None
                    if comparative_template:
                        comparative_profile=retarget(comparative_template,new['year']-1,sid)
                        prior=read_period(comparative_profile,candidate['sources'],reports)
                        candidate['annuals']=[prior if a['end']==prior['end'] else a for a in candidate['annuals']]
                    validate_company(candidate)
                    c.update(candidate);profile['annuals']=[new_profile]+[a for a in profile['annuals'] if a['year']!=new['year']]
                    if comparative_profile:profile['annuals']=[comparative_profile if a['year']==comparative_profile['year'] else a for a in profile['annuals']]
                    profile['annuals']=sorted(profile['annuals'],key=lambda a:a['year'],reverse=True)[:3];config['sources'][sid]=new['url']
                    c['financialStatus']={'checkedAt':checked,'status':'updated','message':'新年度原始财报已通过读取、分类与计算校验；上年度采用新年报的比较数。' if comparative_profile else '新年度原始财报已通过读取、分类与计算校验。'}
            if verify:
                reports={sid:original_report(source['url'],cache) for sid,source in c['sources'].items()}
                verify_existing_reports(c,profile,reports,checked)
            if c.get('financialStatus',{}).get('checkedAt')!=checked:c['financialStatus']={'checkedAt':checked,'status':'checked','message':'已检查原始年报来源，未发现可替代的新完整年度报表。'}
        except Exception as exc:
            c.clear();c.update(original_company);profile.clear();profile.update(original_profile);config['sources']=original_sources
            failures.append(c['id']+' report: '+str(exc));c['financialStatus']={'checkedAt':checked,'status':'retained','message':'本次财报读取／校验未完成，沿用已核实年报：'+str(exc)}
        if quotes_enabled:rebuild_results(c,quotes,failures)
        else:
            for ticker,group in list(c.get('results',{}).items()):
                q=group['1']['quote'];c['results'][ticker]={str(y):calculate(c,q,y) for y in (1,3)}
        validate_company(c)
        print(f"Personal {c['id']}: {c.get('financialStatus',{}).get('status','unknown')}",flush=True)
    data['checkedAt']=checked;data['updatedAt']=checked;data['updateStatus']={'failures':failures,'status':'partial' if failures else 'checked'}
    validate_dataset(data)
    return data,config


def atomic_json(path,data):
    text=json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n';temp=path.with_suffix('.tmp');temp.write_text(text,encoding='utf-8');os.replace(temp,path)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-reports',action='store_true');parser.add_argument('--no-discovery',action='store_true');parser.add_argument('--no-quotes',action='store_true');parser.add_argument('--cache-dir',type=Path,default=ROOT/'.cache/personal-reports');args=parser.parse_args()
    data=json.loads((ROOT/'personal_portfolio.json').read_text());config=json.loads((ROOT/'personal_report_profiles.json').read_text())
    data,config=update(data,config,args.cache_dir,args.verify_reports,not args.no_discovery,not args.no_quotes)
    atomic_json(ROOT/'personal_portfolio.json',data);atomic_json(ROOT/'personal_report_profiles.json',config)
    print(json.dumps({'companies':len(data['companies']),**data['updateStatus']},ensure_ascii=False))


if __name__=='__main__':main()
