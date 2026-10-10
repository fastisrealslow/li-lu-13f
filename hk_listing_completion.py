"""Follow a known spin-off target's own HKEX filings through listing completion.

A trading quote triggers discovery, never proves a parent completed a spin-off.
Only an issuer-bound primary document with an actual past listing date can move
an event to completed. Work is bounded, version cached and retryable.
"""
import json
import hashlib
import io
import re
from datetime import datetime, timezone
from urllib.parse import urlencode, urljoin
from pathlib import Path

from spinoff_events import (filing_text,target_key,iso_date,parse_evidence,merge_evidence,normalize,validate_events,RULE_VERSION,listed_target_code)
VERSION=2


def listing_proof(text, ann, target, ticker):
    text=re.sub(r'\s+',' ',filing_text(text));header=text[:3000]
    # A parent's quote, subsidiary mention or another entity's IPO cannot vote.
    if not target:return None
    code=re.search(r'(?:Stock Code|股份代號|股份代号)\s*[:：]?\s*(\d{1,5})(?!\d)',header,re.I)
    if not code or code[1].zfill(5)+'.HK'!=ticker:return None
    issuer_block=header[max(0,code.start()-300):code.start()]
    if target_key(target) not in target_key(issuer_block):return None
    token=r'(?:[A-Z][a-z]+ \d{1,2},? 20\d{2}|\d{1,2} [A-Z][a-z]+ 20\d{2}|20\d{2}年\d{1,2}月\d{1,2}日|[二零〇一三四五六七八九]{4}年[一二三四五六七八九十]{1,3}月[一二三四五六七八九十]{1,3}日)'
    subjects=r'(?:The (?:H )?[Ss]hares of the Company|The Company[’\']s (?:H )?[Ss]hares|本公司(?:的)?(?:H股|股份))'
    patterns=[subjects+r'[^。;]{0,160}?(?:have been|were|was|已)[^。;]{0,30}?(?:listed|上市)[^。;]{0,130}?(?:since|on|於|于)\s*('+token+')',
              subjects+r'[^。;]{0,25}?(?:已)?(?:於|于)('+token+r')[^。;]{0,70}?(?:聯交所|联交所)[^。;]{0,35}?上市',
              r'(?:During the period from|自)\s*('+token+r')\s*[（(][^()（）]{0,20}(?:Listing Date|上市日期)[^()（）]{0,5}[）)][^。;]{0,200}?(?:Company[’\']s listed securities|本公司.{0,10}上市證券|本公司.{0,10}上市证券)']
    matches=[m for pattern in patterns for m in re.finditer(pattern,text,re.I)]
    matches=[m for m in matches if not re.search(r'\b(?:expect\w*|will|would|subject to|not|proposed)\b|預期|預計|预计|將|将|擬|拟|尚未',m[0][:m.start(1)-m.start()],re.I)]
    matches=[m for m in matches if iso_date(m[1]) and iso_date(m[1])<=iso_date(ann.get('date'))]
    dates={iso_date(m[1]) for m in matches}
    if len(dates)!=1:return None
    date=dates.pop();match=matches[0]
    proof=parse_evidence(header[:1000],ann)
    proof.update(status='completed',quote=match[0],targetName=target,targetTicker=ticker,targetAliases=[],identityKind='entity',identityReason='issuer_bound_listing',
                 identityQuote=header[:700],listingCompletionVersion=VERSION,ruleVersion=RULE_VERSION,
                 dates={**proof.get('dates',{}),'listingDate':{'date':date,'quote':match[0],'kind':'actual'}})
    return proof


def issuer_lookup(name,opener,lang='ZH'):
    from resolve_spinoff_names import read_url
    url='https://www1.hkexnews.hk/search/partial.do?'+urlencode({'lang':lang,'type':'A','name':name,'market':'SEHK','callback':'callback'})
    body=read_url(url,opener).decode('utf-8','replace')
    match=re.fullmatch(r'\s*callback\((.*)\);?\s*',body,re.S)
    if not match:raise ValueError('Invalid HKEX issuer lookup')
    return json.loads(match[1]).get('stockInfo',[])


def issuer_filings(issuer,opener,lang='EN'):
    from resolve_spinoff_names import read_url
    from fetch_spinoff import parse_rows
    url='https://www1.hkexnews.hk/search/titlesearch.xhtml?'+urlencode({'category':0,'lang':lang,'market':'SEHK','stockId':issuer['stockId']})
    body=read_url(url,opener).decode('utf-8','replace')
    rows=parse_rows(body)
    return [{**r,'url':urljoin(url,r.get('docUrl',''))} for r in rows if r.get('stockCode')==issuer['code']]


def listing_document(ann,cik,opener,cache):
    from resolve_spinoff_names import read_url
    from pdfminer.high_level import extract_text
    key=hashlib.sha256(ann["url"].encode()).hexdigest()
    cached=cache/(key+".listing.json") if cache else None
    previous=cache/(key+".json") if cache else None
    if cached and cached.exists():return json.loads(cached.read_text())
    if previous and previous.exists():result=json.loads(previous.read_text())
    else:result={"text":extract_text(io.BytesIO(read_url(ann["url"],opener)),maxpages=30),"url":ann["url"]}
    if cached:cached.write_text(json.dumps(result,ensure_ascii=False))
    return result


def distribution_proof(text, ann, target, ticker, parent_code):
    """Confirm an actual in-specie distribution, never the child's old IPO."""
    text=re.sub(r'\s+',' ',filing_text(text));header=text[:3000]
    issuer=ann.get('sourceIssuerName','') or ann.get('issuerName','')
    issuer_code=ann.get('sourceIssuerCode','') or ann.get('issuerCode','')
    issuer_pattern=r'\s+'.join(re.escape(v) for v in issuer.split())
    named_issuer=re.search(issuer_pattern+r'[^.;]{0,65}\(the [“\"]Company[”\"]\)',header[:1200],re.I) if len(issuer)>=4 else None
    code_limit=named_issuer.end() if named_issuer else 700
    code=re.search(r'(?:Stock Code|股份代號|股份代号)\s*[:：]?\s*(\d{1,5})(?!\d)',header[:code_limit],re.I)
    expected=str(parent_code).removesuffix('.HK').zfill(5)
    if code:
        if code[1].zfill(5)!=expected:return None
    else:
        # Some issuer letterheads are bitmap logos. The HKEX result is bound
        # to the parent's exact code; its own "Company" definition must also
        # match the exchange's issuer name, not a subsidiary mention.
        if issuer_code!=expected or not named_issuer:return None
    token=r'(?:\d{1,2} [A-Z][a-z]+ 20\d{2}|[A-Z][a-z]+ \d{1,2},? 20\d{2}|20\d{2}年\d{1,2}月\d{1,2}日|[二零〇一三四五六七八九]{4}年[一二三四五六七八九十]{1,3}月[一二三四五六七八九十]{1,3}日)'
    patterns=[r'(?:A |The )?special dividend was distributed on ('+token+r')[^.。;]{0,380}?distribution in specie[^.。;]{0,280}',
              r'(?:本公司[^。；]{0,15})?(?:已)?於('+token+r')[^。；]{0,160}?(?:以實物分派|以实物分派)[^。；]{0,200}']
    matches=[]
    for pattern in patterns:
        for m in re.finditer(pattern,text,re.I):
            date=iso_date(m[1])
            if not date or date>iso_date(ann.get('date')):continue
            if re.search(r'\b(?:will|would|expect\w*|not|proposed)\b|預期|預計|预计|將|将|擬|拟|尚未',m[0],re.I):continue
            named=target and target_key(target) in target_key(m[0])
            codes=re.findall(r'(?:Stock Code|股份代號|股份代号)\s*[:：]?\s*(\d{1,5})(?!\d)',m[0],re.I)
            bound=ticker and ticker.removesuffix('.HK').zfill(5) in [v.zfill(5) for v in codes]
            if named or bound:matches.append(m)
    if len({iso_date(m[1]) for m in matches})!=1:return None
    m=matches[0];date=iso_date(m[1])
    return {'status':'completed','quote':m[0],'url':ann['url'],'date':ann['date'],'title':ann.get('title',''),
        'targetName':target,'targetTicker':ticker,'identityKind':'instrument','identityQuote':'','issuerQuote':header[:700],
        'identityReason':'issuer_bound_distribution','identityVersion':3,'method':'rule','ruleVersion':RULE_VERSION,
        'sourceIssuerName':ann.get('sourceIssuerName') or ann.get('issuerName',''),
        'sourceIssuerCode':expected,
        'distributionCompletionVersion':2,'dates':{'distributionDate':{'date':date,'quote':m[0],'kind':'actual'}}}


def follow_distributions(company,opener,cache=None,limit=3):
    """Keyword headlines miss completion confirmed later in financial results."""
    proofs=company.get('filingEvidence',[]);checks=company.setdefault('listingChecks',{})
    errors=[];done=0
    try:
        # Older short PDF reads can miss the glossary and listed-child code.
        # Re-read once with a bounded body before following financial reports.
        for old in sorted(proofs,key=lambda p:p.get('date',''),reverse=True):
            if not old.get('targetName') or old.get('targetTicker'):continue
            key=old['url']+'|distribution_identity'
            if checks.get(key,{}).get('version')==2:continue
            if done>=limit:break
            done+=1
            content=listing_document(old,'',opener,cache)
            ticker=listed_target_code(content['text'],old['targetName'])
            if ticker:
                parsed={**old,'targetTicker':ticker}
                proofs=merge_evidence(proofs,[parsed]);company['filingEvidence']=proofs
            checks[key]={'version':2,'checkedAt':datetime.now(timezone.utc).date().isoformat(),'result':'bound_code' if ticker else 'read'}
            if ticker:break
        targets={p['targetName']:p.get('targetTicker','') for p in sorted(proofs,key=lambda p:p.get('date','')) if p.get('targetName') and p.get('targetTicker')}
        if not targets:return done,errors
        issuers=[i for i in issuer_lookup(company['stockCode'],opener,'EN') if i['code']==company['stockCode']]
        if len(issuers)!=1:return 0,[]
        anns=issuer_filings(issuers[0],opener)
        anns=[{**a,'issuerName':issuers[0]['name'],'issuerCode':issuers[0]['code']} for a in anns]
        anns=[a for a in anns if re.search(r'RESULTS|REPORT|DISTRIBUTION IN SPECIE|業績|報告|實物分派',a.get('title',''),re.I)]
        # Most recent results first within each document category.
        anns=sorted(anns,key=lambda a:a['date'],reverse=True)
        anns=sorted(anns,key=lambda a:0 if re.search(r'RESULTS|業績',a.get('title',''),re.I) else 1)
        for target,ticker in targets.items():
            latest_record=max((p.get('dates',{}).get('recordDate',{}).get('date','') for p in proofs if p.get('targetName')==target),default='')
            if any(p.get('targetName')==target and p.get('distributionCompletionVersion') and
                   p.get('dates',{}).get('distributionDate',{}).get('date','')>=latest_record for p in proofs):continue
            for ann in anns:
                if ann['date']<latest_record:continue
                key=ann['url']+'|distribution|'+target
                if checks.get(key,{}).get('version')==2:continue
                if done>=limit:break
                done+=1
                content=listing_document(ann,'',opener,cache)
                proof=distribution_proof(content['text'],ann,target,ticker,company['stockCode'])
                checks[key]={'version':2,'checkedAt':datetime.now(timezone.utc).date().isoformat(),'result':'completed' if proof else 'no_actual_distribution'}
                if proof:
                    proofs=merge_evidence(proofs,[proof]);company['filingEvidence']=proofs
                    # This is a scoped transaction source, not all issuer filings.
                    if not any(a.get('url')==ann['url'] for a in company.get('announcements',[])):
                        company.setdefault('announcements',[]).append({'date':ann['date'],'title':ann['title'],'url':ann['url']})
                    company['latestDate']=max(company.get('latestDate',''),ann['date'])
                    break
    except Exception as error:errors.append(type(error).__name__+': '+str(error))
    return done,errors

def follow_company(company,opener,cache=None,limit=3):

    checks=company.setdefault('listingChecks',{});proofs=company.get('filingEvidence',[])
    names=sorted({p.get('targetName') for p in proofs if p.get('targetName') and p.get('identityKind','entity')=='entity'})
    errors=[];done=0
    for target in names:
        if any(p.get('targetName')==target and p.get('status')=='completed' for p in proofs):continue
        candidates={p['targetTicker'] for p in proofs if p.get('targetName')==target and p.get('targetTicker','').endswith('.HK')}
        pairs=company.get('spinoffPricePerf',[])
        if isinstance(pairs,dict):pairs=[pairs]
        candidates.update(p.get('spinoff') for p in pairs if p.get('spinoff','').endswith('.HK'))
        searches=[s.removesuffix('.HK') for s in sorted(candidates)] or [re.sub(r'(?:科技)?股份有限公司$|有限公司$','',target)]
        for search in searches[:2]:
            try:
                issuers=issuer_lookup(search,opener)
                if re.fullmatch(r'\d{4,5}',search):issuers=[i for i in issuers if i['code']==search.zfill(5)]
                if len(issuers)!=1:continue
                issuer=issuers[0];ticker=issuer['code']+'.HK'
                anns=issuer_filings(issuer,opener)
                # Results usually state the issuer's actual listing date in <30 pages.
                anns.sort(key=lambda a:(0 if re.search(r'INTERIM RESULTS|年度業績|中期業績|FINANCIAL RESULTS',a.get('title',''),re.I) else 1 if re.search(r'LISTING|上市|開始買賣',a.get('title',''),re.I) else 2 if re.search(r'REPORT|報告',a.get('title',''),re.I) else 3,a.get('date','')))
                for ann in anns:
                    key=ann['url']+'|'+target
                    if checks.get(key,{}).get('version')==VERSION:continue
                    if done>=limit:break
                    done+=1
                    content=listing_document(ann,'',opener,cache);proof=listing_proof(content['text'],ann,target,ticker)
                    checks[key]={'version':VERSION,'checkedAt':datetime.now(timezone.utc).date().isoformat(),'result':'completed' if proof else 'no_actual_listing'}
                    if proof:
                        proofs=merge_evidence(proofs,[proof]);company['filingEvidence']=proofs
                        # Actual date supersedes the former announcement-date proxy.
                        for pair in pairs:
                            if pair.get('spinoff','').lstrip('0')==ticker.lstrip('0'):
                                actual=proof['dates']['listingDate']['date']
                                if pair.get('spinoffDate')!=actual:
                                    pair.update(spinoffDate=actual,spinoffPriceAtListing=None,spinoffChangePct=None)
                                pair['listingDateSource']=proof['url']
                        break
                if any(p.get('targetName')==target and p.get('status')=='completed' for p in proofs):break
            except Exception as error:errors.append(type(error).__name__+': '+str(error))
    return done,errors


def main():
    import argparse
    from urllib.request import build_opener
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=3);p.add_argument('--cache-dir');a=p.parse_args()
    cache=Path(a.cache_dir) if a.cache_dir else None
    if cache:cache.mkdir(parents=True,exist_ok=True)
    path=Path('spinoff.json');data=json.loads(path.read_text());previous=json.loads(path.read_text())
    for company in data['companies']:
        kind=company.get('spinType') or company.get('type','')
        kind=kind.get('code','') if isinstance(kind,dict) else kind
        if kind=='distribution':done,errors=follow_distributions(company,build_opener(),cache,a.limit)
        elif re.search(r'intro',kind):done,errors=follow_company(company,build_opener(),cache,a.limit)
        else:continue
        print(f"{company['ticker']}: {done} listing sources; {len(errors)} retryable failures",flush=True)
    normalize(data,'hk',previous=previous);validate_events(data);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
