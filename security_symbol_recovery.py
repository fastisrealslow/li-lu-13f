"""Recover renamed common shares from SEC cover pages and unchanged-CUSIP evidence.

The issuer directory is only a locator. A new price or similar company name is
never sufficient to move a filed security to a different issuer/share class.
"""
from datetime import date, timedelta, datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup


def cover(raw, cik, holding):
    soup=BeautifulSoup(raw,'html.parser')
    def facts(name):return [n.get_text(' ',strip=True) for n in soup.find_all(attrs={'name':lambda v:v and v.lower()=='dei:'+name.lower()})]
    if set(facts('EntityCentralIndexKey'))!={str(cik).zfill(10)}:return None
    expected=re.search(r'CL(?:ASS)?\s+([A-Z])\b',holding.get('cls',''),re.I)
    candidates=[]
    for n in soup.find_all(attrs={'name':lambda v:v and v.lower()=='dei:tradingsymbol'}):
        row=n.find_parent('tr');text=row.get_text(' ',strip=True) if row else ''
        if not re.search(r'common|ordinary',text,re.I) or re.search(r'warrant|preferred|note',text,re.I):continue
        actual=re.search(r'class\s+([A-Z])\b',text,re.I)
        if expected and (not actual or expected[1].upper()!=actual[1].upper()):continue
        # An unspecified filed class may bind only to a unique listed common class.
        tk=n.get_text(' ',strip=True)
        if re.fullmatch(r'[A-Z][A-Z0-9.-]{0,11}',tk):candidates.append(tk)
    if len(set(candidates))!=1:return None
    return {'ticker':candidates[0],'issuer':next(iter(facts('EntityRegistrantName'))),'soup':soup}


def unchanged_cusip(text,cusip):
    text=' '.join(text.split())
    # The same sentence must identify the filed class, its CUSIP and continuity.
    return bool(re.search(r'CUSIP[^.!?]{0,150}\b(?:remain|unchanged|continue)\w*[^.!?]{0,100}\b'+re.escape(cusip)+r'\b',text,re.I)
                or re.search(r'CUSIP[^.!?]{0,100}\b'+re.escape(cusip)+r'\b[^.!?]{0,100}\b(?:remain|unchanged)\w*',text,re.I))


def discover(holdings,directory,fetch,quote,now=None,limit=4):
    today=now or date.today();since=(today-timedelta(days=120)).isoformat();found={}
    by_ticker={}
    for r in directory:by_ticker.setdefault(r['ticker'],[]).append(r)
    unique={h['cusip']:h for h in holdings if h.get('cusip') and not h.get('putCall') and h.get('shareType','SH')=='SH'}
    pending=list(unique.values())
    if len(pending)>limit:
        offset=(today.toordinal()*limit)%len(pending)
        pending=(pending+pending)[offset:offset+limit]
    for h in pending:
        rows=by_ticker.get(h['ticker'],[])
        if len(rows)!=1 or 'cik_str' not in rows[0]:continue
        cik=str(rows[0]['cik_str']);sub=json.loads(fetch('submissions/CIK'+cik.zfill(10)+'.json'))
        if int(sub.get('cik',0))!=int(cik):continue
        recent=sub.get('filings',{}).get('recent',{});documents=[]
        for i,form in enumerate(recent.get('form',[])):
            filed=recent['filingDate'][i]
            if form not in ('8-K','8-K/A') or not since<=filed<=today.isoformat():continue
            path='/Archives/edgar/data/'+str(int(cik))+'/'+recent['accessionNumber'][i].replace('-','')+'/'+recent['primaryDocument'][i]
            raw=fetch(path);item=cover(raw,cik,h)
            if item:documents.append({**item,'path':path,'filed':filed})
            if len(documents)>=6:break
        if not documents:continue
        newest=documents[0]
        if newest['ticker']==h['ticker']:continue
        newest=min((d for d in documents if d['ticker']==newest['ticker']),key=lambda d:d['filed'])
        evidence=None;spinoff=False
        for doc in documents:
            if doc['ticker']!=h['ticker']:continue
            texts=[(doc['soup'].get_text(' ',strip=True),doc['path'])]
            for a in doc['soup'].select('a[href]'):
                href=a.get('href','')
                if not re.fullmatch(r'[A-Za-z0-9_.-]*ex99[0-9]*\.htm[l]?',href):continue
                path=urljoin(doc['path'],href)
                if not path.startswith(doc['path'].rsplit('/',1)[0]+'/'):continue
                texts.append((BeautifulSoup(fetch(path),'html.parser').get_text(' ',strip=True),path))
                if len(texts)>=3:break
            for text,path in texts:
                if unchanged_cusip(text,h['cusip']) and re.search(r'\b'+re.escape(newest['ticker'])+r'\b',text):
                    evidence='https://www.sec.gov'+path;spinoff=bool(re.search(r'spin[ -]?off|distribution of.*shares',text,re.I));break
            if evidence:break
        if not evidence:continue
        q=quote(newest['ticker'])
        from quote_coverage import fresh_quote,issuer_key
        if not fresh_quote(q) or issuer_key(q.get('verifiedName',''))!=issuer_key(newest['issuer']):continue
        found[h['cusip']]={'ticker':newest['ticker'],'oldSymbols':[h['ticker']],'issuer':newest['issuer'],
            'issuerCIK':str(int(cik)),'sourceURL':'https://www.sec.gov'+newest['path'],'identitySourceURL':evidence,
            'checkedAt':datetime.now(timezone.utc).isoformat(),'effectiveDate':newest['filed'],
            'kind':'spin_off_rename' if spinoff else 'same_class_rename','preserveCost':not spinoff}
    return found
