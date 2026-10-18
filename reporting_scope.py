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
