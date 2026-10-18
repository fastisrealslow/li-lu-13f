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
    try:data['current']['reportingScope']=parse_cover(fetch(path),'https://www.sec.gov'+path,quarter)
    except Exception as error:
        data['meta']['reportingScopeRetry']=type(error).__name__
    else:data['meta'].pop('reportingScopeRetry',None)
