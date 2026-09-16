"""Backfill target identities from primary filings on every scheduled update.

Checks are document/version cached in the data, failures remain retryable. Older
announcements are processed in bounded batches so missing identities make progress
across runs without downloading every historical filing on every update.
"""
import argparse
import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import re
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, build_opener

from spinoff_events import (parse_evidence, source_url, direct_source, filing_url,
                            merge_evidence, normalize, validate_events, iso_date)
from spinoff_identity import IDENTITY_VERSION

_request_lock = threading.Lock()
_next_request = 0.0

USER_AGENT = 'li-lu-13f public filing research fastisrealslow@163.com'


def read_url(url, opener):
    if urlparse(url).hostname not in {'www1.hkexnews.hk', 'www.hkexnews.hk', 'www.sec.gov', 'data.sec.gov'}:
        raise ValueError('Only HKEX / SEC primary sources are accepted')
    global _next_request
    with _request_lock:
        time.sleep(max(0, _next_request-time.monotonic()))
        _next_request=time.monotonic()+.22  # Global cap across all workers.
    with opener.open(Request(url, headers={'User-Agent': USER_AGENT}), timeout=25) as response:
        body = response.read(20_000_001)
    if len(body) > 20_000_000:
        raise ValueError('Filing exceeds download limit')
    return body


def recover_sec_announcements(company, opener):
    """Resolve legacy directory links by exact date + form, never guess an accession."""
    anns = company.get('announcements', [])
    pending = [a for a in anns if not a.get('adsh') and not direct_source(source_url(a))]
    cik = str(company.get('cik', ''))
    if not pending or not cik.isdigit(): return
    submissions = json.loads(read_url(f'https://data.sec.gov/submissions/CIK{int(cik):010d}.json', opener))
    dates = {a['date'] for a in pending}
    tables = [submissions.get('filings', {}).get('recent', {})]
    for old in submissions.get('filings', {}).get('files', [])[:3]:
        if any(old.get('filingFrom','') <= d <= old.get('filingTo','') for d in dates):
            name = old.get('name','')
            if re.fullmatch(r'CIK\d+-submissions-\d+\.json',name):
                tables.append(json.loads(read_url('https://data.sec.gov/submissions/'+name,opener)))
    for ann in pending:
        hits=[]
        for table in tables:
            for i, date in enumerate(table.get('filingDate', [])):
                if date==ann['date'] and table['form'][i] in ('8-K','8-K/A'):
                    hits.append((table['accessionNumber'][i], table['primaryDocument'][i]))
        if len(set(hits))==1:
            accession,document=hits[0]
            ann.update(adsh=accession, primaryDocument=document, url=filing_url(cik,accession,document))


def html_text(raw):
    import html
    value=raw.decode('utf-8','replace')
    value=re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' ',value,flags=re.I|re.S)
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',value))).strip()


def document(ann, cik, opener, cache=None):
    url=source_url(ann,cik)
    key=hashlib.sha256(url.encode()).hexdigest()
    cached=cache/(key+'.json') if cache else None
    prior = json.loads(cached.read_text()) if cached and cached.exists() else None
    if prior and prior.get('cacheVersion') == 3 and not prior.get('supplementUnavailable'):return prior
    if url.lower().endswith('.pdf'):
        from pdfminer.high_level import extract_text
        # Definition tables often come after page 6, which the old fetcher omitted.
        raw=None if prior else read_url(url,opener)
        text=prior['text'] if prior else extract_text(io.BytesIO(raw),maxpages=30)
        result={'text':text,'url':url}
        if not parse_evidence(text,ann,cik)['targetName']:
            # A second reading order handles mixed Chinese/English text boxes.
            from pdfminer.layout import LAParams
            try:
                raw=raw or read_url(url,opener)
                extra=extract_text(io.BytesIO(raw),maxpages=30,laparams=LAParams(boxes_flow=None))
                found=parse_evidence(extra,ann,cik)
                if found.get('targetName'):
                    result['identitySupplement']={**found,'identitySourceUrl':url}
                result['identityAlternateText']=extra
            except Exception:
                result['supplementUnavailable']=True
    else:
        from fetch_spinoff_us import fetch_8k_text
        # Existing helper resolves the precise primary document if needed.
        if prior:
            text=prior['text']
            raw=read_url(url,opener) if not parse_evidence(text,ann,cik)['targetName'] else b''
        elif not ann.get('primaryDocument'):
            text=fetch_8k_text(cik,ann['adsh'],opener,ann)
            url=source_url(ann,cik)
            raw=read_url(url,opener) if text else b''
        else:
            raw=read_url(url,opener);text=html_text(raw)
        result={'text':text,'url':url}
        identity=parse_evidence(text,ann,cik)
        if not identity.get('targetName'):
            # Follow only press-release / information-statement exhibits linked
            # by this filing, restricted to its own SEC accession directory.
            base=url.rsplit('/',1)[0]+'/'
            links=[]
            for match in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',raw.decode('utf-8','replace'),re.I|re.S):
                href,label=match.groups(); linked=urljoin(url,href)
                if linked.startswith(base) and re.search(r'99[._-]?[12]|press release|information statement',href+' '+html_text(label.encode()),re.I) and re.search(r'\.html?$',linked,re.I):
                    if linked not in links:links.append(linked)
            for linked in links[:2]:
                try:
                    extra=html_text(read_url(linked,opener))
                    found=parse_evidence(extra,{'date':ann.get('date'), 'url':linked})
                    if found.get('targetName'):
                        result['identitySupplement']={**found,'identitySourceUrl':linked}
                        result.pop('supplementUnavailable',None)
                        break
                except Exception:
                    result['supplementUnavailable']=True
    if len(result['text'].strip())<30:raise ValueError('No readable filing text')
    result['cacheVersion']=3
    if cached:cached.write_text(json.dumps(result,ensure_ascii=False))
    return result


def link_references(proofs):
    """Unnamed updates inherit identities only through explicit dated references."""
    by_date={}
    for proof in proofs:by_date.setdefault(proof.get('date'),[]).append(proof)
    def explicit_sources(proof,visited):
        marker=proof.get('accession') or proof.get('url') or id(proof)
        if marker in visited:return []
        if proof.get('targetName') and proof.get('identityReason') != 'dated_reference':return [proof]
        visited=visited|{marker}
        return [q for date in proof.get('identityReferences',[]) for p in by_date.get(date,[]) for q in explicit_sources(p,visited)]
    for p in proofs:
        business = p.get('targetName') and p.get('identityKind') == 'business'
        if p.get('targetName') and p.get('identityReason') != 'dated_reference' and not business:continue
        linked=([q for date in p.get('identityReferences',[]) for source in by_date.get(date,[]) for q in explicit_sources(source,{p.get('url')})] if business else explicit_sources(p,set()))
        if business and not re.match('若干',p['targetName']):
            linked=[q for q in linked if q.get('identityKind')=='entity']
        from spinoff_events import target_key
        names={target_key(q['targetName']) for q in linked}
        if len(names)==1:
            q=linked[0]
            old_name=p.get('targetName') if business else None
            for field in ('targetName','targetAliases','identityKind','distributedEntity','separatedEntity'):
                p[field]=q.get(field)
            if old_name:p['targetAliases']=list(dict.fromkeys([*(p.get('targetAliases') or []),old_name]))
            p.update(identityQuote=q.get('identityQuote',''), identitySourceUrl=q.get('identitySourceUrl') or q['url'], identitySourceDate=q.get('date'), identityReason='dated_reference')
        elif p.get('identityReason')=='dated_reference':
            p.update(targetName='',targetAliases=[],identityQuote='',identityReason='conflicting_names' if names else 'not_identified')
    return proofs


def refresh_company(company, market, opener, cache=None, limit=3):
    failures=[]
    if market=='us':
        try:recover_sec_announcements(company,opener)
        except Exception as error:failures.append('SEC index: '+type(error).__name__)
    checks=company.setdefault('identityChecks',{})
    proofs=list(company.get('filingEvidence',[]))
    done=0
    # Original spin-off announcements get priority over generic item labels.
    anns=sorted(company.get('announcements',[]),key=lambda a:(not bool(re.search(r'SEC 8-K:|建議|分拆|分立',a.get('title',''))), a.get('date','')))
    for ann in anns:
        url=source_url(ann,company.get('cik',''))
        if not direct_source(url) or checks.get(url,{}).get('version')==IDENTITY_VERSION:continue
        if done>=limit:break
        done+=1
        try:
            content=document(ann,company.get('cik',''),opener,cache)
            proof=parse_evidence(content['text'],ann,company.get('cik',''))
            supplement=content.get('identitySupplement')
            if supplement and not proof['targetName']:
                for field in ('targetName','targetAliases','identityQuote','identityKind','distributedEntity','separatedEntity','identitySourceUrl'):
                    proof[field]=supplement.get(field)
            # Track dates only in the explicit introductory cross-reference passage.
            refs=[]
            from spinoff_events import filing_text
            body=filing_text(content['text'])
            for m in re.finditer(r'(?:茲提述|兹提述|謹此提述)[^。]{0,1300}',body):
                refs.extend(iso_date(t) for t in re.findall(r'(?:20\d{2}年\d{1,2}月\d{1,2}日|[二零〇一三四五六七八九]{4}年[一二三四五六七八九十]{1,3}月[一二三四五六七八九十]{1,3}日)',m.group()))
            for m in re.finditer(r'本公司日期為(20\d{2}年\d{1,2}月\d{1,2}日)的公告，內容有關(?:建議)?分拆',body):
                refs.append(iso_date(m[1]))
            proof['identityReferences']=sorted(set(refs)-{''})
            proofs=merge_evidence(proofs,[proof])
            if content.get('supplementUnavailable'):
                failures.append(url+': supplemental source unavailable')
            else:
                checks[url]={'version':IDENTITY_VERSION,'checkedAt':datetime.now(timezone.utc).strftime('%Y-%m-%d'),'result':'named' if proof['targetName'] else 'no_name'}
        except Exception as error:
            failures.append(url+': '+type(error).__name__)
    company['filingEvidence']=link_references(proofs)
    return done,failures


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cache-dir');parser.add_argument('--limit',type=int,default=3);parser.add_argument('--market',choices=['hk','us']);args=parser.parse_args()
    cache=Path(args.cache_dir) if args.cache_dir else None
    if cache:cache.mkdir(parents=True,exist_ok=True)
    for market,filename in [('hk','spinoff.json'),('us','spinoff_us.json')]:
        if args.market and args.market != market:continue
        original=json.loads(Path(filename).read_text()); data=copy.deepcopy(original); failures=[]
        def process(c):
            checkpoint=cache/(market+'-'+c['ticker']+'.company.json') if cache else None
            if checkpoint and checkpoint.exists():
                saved=json.loads(checkpoint.read_text())
                for ann in c.get('announcements',[]):
                    matches=[a for a in saved.get('announcements',[]) if a.get('date')==ann.get('date') and a.get('title')==ann.get('title')]
                    if len(matches)==1:ann.update(matches[0])
                c['filingEvidence']=merge_evidence(c.get('filingEvidence',[]),saved.get('filingEvidence',[]))
                c.setdefault('identityChecks',{}).update(saved.get('identityChecks',{}))
            count,errors=refresh_company(c,market,build_opener(),cache,args.limit)
            if cache:(cache / (market+'-'+c['ticker']+'.company.json')).write_text(json.dumps(c,ensure_ascii=False))
            print(f"{market} {c.get('ticker')}: {count} filings, {len(errors)} unavailable",flush=True)
            return errors
        with ThreadPoolExecutor(max_workers=6) as pool:
            for errors in pool.map(process, data['companies']): failures.extend(errors)
        normalize(data,market,previous=original);validate_events(data)
        Path(filename).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
        print(f"{market}: {sum(bool(e['targetName']) for e in data['events'])}/{len(data['events'])} named; {len(failures)} source failures",flush=True)
        if failures:
            from update_status import record_source_warning
            record_source_warning('spinoff_'+market,f'{len(failures)} 份名称补全来源暂不可读，将自动重试；已保留历史证据')

if __name__=='__main__':main()
