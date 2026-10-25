"""Dated, source-verified security events, keyed by class-specific CUSIP."""
import json
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit
import re
ROOT=Path(__file__).resolve().parent

def events(root=ROOT):
    path=Path(root)/'security_lifecycle.json'
    if not path.exists():return {}
    data=json.loads(path.read_text())['events']
    for cusip,event in data.items():
        url=urlsplit(event.get('sourceURL',''))
        if not re.fullmatch(r'[A-Z0-9]{9}',cusip) or event.get('status')!='ceased_trading' or not event.get('ticker') or url.scheme!='https' or not url.netloc or url.username or url.password:
            raise ValueError('Invalid verified security lifecycle evidence')
        date.fromisoformat(event['effectiveDate'])
        if not all(event.get(k) for k in ['reason','reasonEn','issuer']):raise ValueError('Missing lifecycle explanation')
    return data

def event_for(holding,root=ROOT):
    event=events(root).get(holding.get('cusip'))
    if event and event['ticker']==holding.get('ticker') and date.fromisoformat(event['effectiveDate'])<=date.today():return event
    return None


def lifecycle_name(name):
    from quote_coverage import issuer_key
    words={'CMNTYS':'COMMUNITIES','MNG':'MINING','MED':'MEDICAL','INDL':'INDUSTRIAL'}
    value=' '.join(words.get(w,w) for w in issuer_key(name).split())
    return re.sub(r' (?:TRUST|NEW)$','',value)


def retirement_from_form25(raw,holding,candidate):
    """Accept only an extinguished/replaced class, never a listing transfer."""
    from xml.etree import ElementTree as ET
    from quote_coverage import issuer_key
    node=ET.fromstring(raw)
    if node.tag!='notificationOfRemoval':raise ValueError('Not an original Form 25 XML')
    issuer=node.find('issuer')
    if issuer is None or int(issuer.findtext('cik'))!=int(candidate['cik']):raise ValueError('Issuer differs from the SEC index')
    name=issuer.findtext('entityName','')
    if lifecycle_name(name)!=lifecycle_name(holding['name']):raise ValueError('Issuer differs from the filed holding')
    title=node.findtext('descriptionClassSecurity','')
    if not re.search(r'common|ordinary',title,re.I) or re.search(r'preferred|warrant|note|bond',title,re.I):raise ValueError('Removal concerns another security type')
    expected=re.search(r'CL(?:ASS)?\s+([A-Z])\b',holding.get('cls',''),re.I)
    actual=re.search(r'CL(?:ASS)?\s+([A-Z])\b',title,re.I)
    if actual and not expected:raise ValueError('Filed share class is unspecified')
    if expected and (not actual or expected[1].upper()!=actual[1].upper()):raise ValueError('Share class cannot be bound')
    rule=node.findtext('ruleProvision','')
    if not re.search(r'12d2-2\(a\)\([1-4]\)',rule):raise ValueError('Voluntary removal/transfer does not prove retirement')
    signed=node.findtext('signatureData/signatureDate','')
    if signed!=candidate['filingDate'] or date.fromisoformat(signed)>date.today():raise ValueError('Removal date is not a verified past date')
    return dict(ticker=holding['ticker'],issuer=name,status='ceased_trading',effectiveDate=signed,reason='交易所已申报该类证券赎回、转换或注销；保留原报告期持仓，不显示虚构现价。',reasonEn='The exchange reported the retirement or replacement of this security class. The original dated position is retained without an invented current quote.',sourceURL=candidate['url'],checkedAt=date.today().isoformat(),issuerCIK=str(candidate['cik']),evidenceType='SEC Form 25-NSE',ruleProvision=rule)


def discover_retirements(holdings,since,fetch,limit=8):
    """Search SEC quarterly indexes only after quotes and symbol recovery fail."""
    import gzip
    from quote_coverage import issuer_key
    pending={lifecycle_name(h['name']):h for h in holdings if h.get('cusip') and not h.get('putCall') and h.get('shareType','SH')=='SH' and re.search(r'COM|ORD|CL ',h.get('cls',''),re.I)}
    start=date.fromisoformat(since);today=date.today();first=start.year*4+(start.month-1)//3;last=today.year*4+(today.month-1)//3
    found={};attempts=0
    for i in range(first,last+1):
        if not pending:break
        path=f'/Archives/edgar/full-index/{i//4}/QTR{i%4+1}/master.gz'
        body=gzip.decompress(fetch(path)).decode('utf-8',errors='replace')
        if 'CIK|Company Name|Form Type|Date Filed|Filename' not in body:raise ValueError('Invalid SEC retirement index')
        for line in body.splitlines():
            cells=line.split('|')
            if len(cells)!=5 or cells[2]!='25-NSE' or not cells[0].isdigit() or not since<=cells[3]<=today.isoformat():continue
            cik,name,_,filed,submission=cells;key=lifecycle_name(name)
            if key not in pending:continue
            m=re.fullmatch(r'edgar/data/(\d+)/(\d{10}-\d{2}-\d{6})\.txt',submission)
            if not m or int(m[1])!=int(cik) or attempts>=limit:continue
            attempts+=1;url=f'/Archives/edgar/data/{cik}/{m[2].replace("-","")}/primary_doc.xml'
            try:
                raw=fetch(url);candidate=dict(cik=cik,filingDate=filed,url='https://www.sec.gov'+url)
                event=retirement_from_form25(raw,pending[key],candidate)
                found[pending[key]['cusip']]=event;pending.pop(key)
            except (ValueError,TypeError,AttributeError,ETError):continue
    return found

# ElementTree raises a ValueError subclass on some runtimes and ParseError on others.
from xml.etree.ElementTree import ParseError as ETError
