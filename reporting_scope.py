"""Resolve numbered 13F manager references from the filing's own cover page."""
import re
from xml.etree import ElementTree as ET


def parse_cover(raw, source_url, quarter):
    root=ET.fromstring(raw)
    local=lambda node,name:next((e.text.strip() for e in node.iter() if e.tag.split('}')[-1]==name and e.text),'')
    managers={}
    for node in root.iter():
        if node.tag.split('}')[-1]=='otherManager2':
            number=local(node,'sequenceNumber')
            if number:managers[number]={'name':local(node,'name'),'cik':local(node,'cik')}
    return {'quarter':quarter,'source':source_url,'managers':managers}


def refresh(data,config,filing,fetch):
    if not config.get('reportingTransition'):return
    quarter=data['current']['quarter']
    path=f"/Archives/edgar/data/{int(filing.get('cik',config['cik']))}/{filing['accession']}/primary_doc.xml"
    try:
        scope=parse_cover(fetch(path),'https://www.sec.gov'+path,quarter)
        data['current']['reportingScope']=scope
        data.setdefault('history',{}).setdefault('reportingScopes',{})[quarter]=scope
    except Exception as error:
        data['meta']['reportingScopeRetry']=type(error).__name__
    else:data['meta'].pop('reportingScopeRetry',None)


def same_manager_history(data,holding):
    """Carry a security's history only when every transition row names the old CIK.

    A successor's larger aggregate filing is not itself proof. Numbered manager
    references in the transition table, its cover and the predecessor filing
    must agree. Store the bridge quarter so later quarters retain this evidence.
    """
    from holdings_diff import same_security
    transition=data.get('meta',{}).get('reportingTransition',{})
    boundary=transition.get('fromQuarter','');match=re.fullmatch(r'(\d{4}) Q([1-4])',boundary)
    if not match or not transition.get('fromCIK'):return False
    year,number=map(int,match.groups());previous=f'{year if number>1 else year-1} Q{number-1 if number>1 else 4}'
    history=data.get('history',{});current=data.get('current',{})
    scope=history.get('reportingScopes',{}).get(boundary) or current.get('reportingScope',{})
    normalize=lambda cik:str(cik or '').lstrip('0')
    if scope.get('quarter')!=boundary or normalize(history.get('filing_sources',{}).get(previous,{}).get('cik'))!=normalize(transition['fromCIK']):return False
    ids={key for key,manager in scope.get('managers',{}).items() if normalize(manager.get('cik'))==normalize(transition['fromCIK'])}
    rows=history.get('holdings',{}).get(boundary) or (current.get('holdings',[]) if current.get('quarter')==boundary else [])
    row=next((r for r in rows if same_security(holding,r)),{})
    allocations=row.get('managerAllocations',[])
    return bool(holding.get('cusip') and ids and allocations
                and all(ids.intersection(a.get('managerIds',[])) for a in allocations)
                and all(sum(a.get(k,0) for a in allocations)==row.get(k) for k in ['shares','value']))


class FilingBatch(list):
    """Holdings reports plus separate notice evidence; notices are never rows."""
    def __init__(self, rows=(), notices=()):
        super().__init__(rows)
        self.notices=list(notices)


def notice_candidates(cik, submissions):
    recent=submissions.get('filings',{}).get('recent',{})
    candidates=[]
    for i,form in enumerate(recent.get('form',[])):
        if form not in ('13F-NT','13F-NT/A'):continue
        row={k:recent[k][i] for k in ('accessionNumber','reportDate','filingDate','primaryDocument')}
        if not re.fullmatch(r'\d{10}-\d{2}-\d{6}',row['accessionNumber']):raise ValueError('Invalid notice accession')
        document=re.fullmatch(r'(?:xslForm13F_[A-Za-z0-9]+/)?([A-Za-z0-9_.-]+\.xml)',row['primaryDocument'])
        if not document:continue
        row['primaryDocument']=document[1]
        candidates.append({**row,'form':form,'cik':str(cik).zfill(10)})
    return candidates


def refresh_notice(data, config, candidates, fetch):
    if candidates is None:return
    from datetime import datetime
    import hashlib
    meta=data.setdefault('meta',{});current=data.get('current',{}).get('periodEnd','')
    latest=max(candidates,key=lambda n:(n['reportDate'],n['filingDate'],n['accessionNumber']),default=None)
    if not latest or latest['reportDate']<=current:
        if meta.get('reportingNotice',{}).get('periodEnd','')<=current:meta.pop('reportingNotice',None)
        return
    cik=str(config['cik']).zfill(10)
    if latest['cik']!=cik:raise ValueError('Notice reporter differs from configured manager')
    path=f"/Archives/edgar/data/{int(cik)}/{latest['accessionNumber'].replace('-','')}/{latest['primaryDocument']}"
    raw=fetch(path);root=ET.fromstring(raw)
    value=lambda name:next((n.text.strip() for n in root.iter() if n.tag.split('}')[-1]==name and n.text),'')
    if value('submissionType')!=latest['form'] or value('cik').zfill(10)!=cik or value('reportType')!='13F NOTICE':
        raise ValueError('Notice cover identity mismatch')
    period=datetime.strptime(value('reportCalendarOrQuarter'),'%m-%d-%Y').date().isoformat()
    if period!=latest['reportDate']:raise ValueError('Notice cover period mismatch')
    managers=[]
    for node in root.iter():
        if node.tag.split('}')[-1]!='otherManager':continue
        fields={n.tag.split('}')[-1]:(n.text or '').strip() for n in node.iter()}
        if fields.get('name') and fields.get('form13FFileNumber'):
            managers.append({'name':fields['name'],'fileNumber':fields['form13FFileNumber']})
    if not managers:raise ValueError('Notice does not identify reporting managers')
    year,month=map(int,period.split('-')[:2])
    meta['reportingNotice']={'status':'verified','form':latest['form'],'managerCIK':cik,
        'periodEnd':period,'quarter':f'{year} Q{(month-1)//3+1}',
        'filingDate':latest['filingDate'],'accession':latest['accessionNumber'],
        'source':'https://www.sec.gov'+path,'sourceSha256':hashlib.sha256(raw).hexdigest(),
        'otherManagers':managers}


def notice_covers(data, required_period):
    n=data.get('meta',{}).get('reportingNotice',{});cik=str(data.get('meta',{}).get('managerCIK','')).zfill(10)
    accession=n.get('accession','')
    if not cik.isdigit() or not re.fullmatch(r'\d{10}-\d{2}-\d{6}',accession):return False
    prefix=f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-','')}/"
    return bool(n.get('status')=='verified' and n.get('form') in ('13F-NT','13F-NT/A')
        and n.get('managerCIK')==cik and n.get('periodEnd')==required_period
        and n.get('periodEnd','')>data.get('current',{}).get('periodEnd','')
        and n.get('otherManagers') and re.fullmatch(r'[a-f0-9]{64}',n.get('sourceSha256',''))
        and n.get('source','').startswith(prefix) and re.fullmatch(r'[A-Za-z0-9_.-]+\.xml',n['source'][len(prefix):]))
