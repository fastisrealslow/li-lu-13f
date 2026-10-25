"""Read original pre-XML 13F tables, rejecting partial or ambiguous extraction.

Legacy forms report values in thousands. Both the unconsolidated entry count
and declared value total must reconcile before a table can enter history.
"""
import re
from decimal import Decimal
from bs4 import BeautifulSoup

VERSION = 2
NUMBER = r'[\d,]+(?:\.\d+)?'
CUSIP=r'[A-Z0-9*@#]{6} ?[A-Z0-9*@#]{2} ?[0-9]'
ROW=re.compile(r'\b('+CUSIP+r')\s+\$?\s*('+NUMBER+r')\s+('+NUMBER+r')\s*(SH|PRN|PUT|CALL|CO)?(?:\s+(PUT|CALL)\b)?(?=\s|$)',re.I)
CLASS=re.compile(r'^(.*?)\s+((?:COM(?:MON)?(?:\s+STOCK)?|CL(?:ASS)?\s+[A-Z](?:\s+NEW)?|ORD(?:INARY)?|SHS?(?:\s+.*)?|ADR|SPONSORED.*|PREF.*|PFD.*|LEA|NOTE.*|DEB.*|PUT|CALL))$',re.I)

def identity(prefix):
    prefix=re.sub(r'^D\s+','',prefix.strip())
    m=CLASS.match(prefix)
    if m:return m[1].strip(),m[2].strip()
    fields=re.split(r'\s{2,}',prefix)
    if len(fields)>=2:return ' '.join(fields[:-1]),fields[-1]
    raise ValueError('Legacy issuer/class columns are ambiguous')

def quantity(value):
    value=amount(value)
    return int(value) if value==value.to_integral() else float(value)


def amount(value):
    return Decimal(re.sub(r'[$,\s]','',value))


def parse_legacy(raw):
    source=raw.decode('utf-8',errors='replace')
    if not re.search(r'CONFORMED SUBMISSION TYPE:\s*13F-HR\b|<TYPE>13F-HR\b',source,re.I):
        raise ValueError('Legacy source is not a complete 13F holdings report')
    if re.search(r'CONFORMED SUBMISSION TYPE:\s*13F-HR/A\b|<TYPE>13F-HR/A\b',source,re.I):
        raise ValueError('Legacy amendments need explicit restatement evidence')
    soup=BeautifulSoup(source,'html.parser')
    text=re.sub(r'\s+',' ',soup.get_text(' ',strip=True))
    count=re.search(r'Table\s+Entry\s+Total\s*:\s*('+NUMBER+')',text,re.I)
    total=re.search(r'Table\s+Value\s+Total(?:\s*\([^)]*\))?\s*:\s*\$?\s*('+NUMBER+')',text,re.I)
    if not count or not total:
        raise ValueError('Legacy cover does not declare both entry count and value total')
    rows=[]
    for tr in soup.find_all('tr'):
        if tr.find('tr'):continue
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'],recursive=False)]
        for i,c in enumerate(cells):
            cusip=re.sub(r'\s','',c).upper()
            if i<2 or not re.fullmatch(r'[A-Z0-9*@#]{9}',cusip):continue
            rest=' '.join(cells[i+1:]);m=re.match(r'\$?\s*('+NUMBER+r')\s+('+NUMBER+r')\s+(SH|PRN)\b(?:\s+(PUT|CALL)\b)?',rest,re.I)
            if not m:continue
            rows.append(dict(name=cells[i-2],cls=cells[i-1],cusip=cusip,value=int(amount(m[1])*1000),shares=int(amount(m[2])),shareType=m[3].upper(),putCall=(m[4] or '').title()))
            break
    if not rows:
        tables=re.findall(r'<TABLE\b[^>]*>(.*?)</TABLE>',source,re.I|re.S)
        # Early plaintext filings can have a tabular <TEXT> without TABLE tags.
        if not tables:tables=re.findall(r'<TEXT>(.*?)</TEXT>',source,re.I|re.S)
        for table in tables:
            previous=None;pending=''
            for line in table.splitlines():
                m=ROW.search(line)
                missing_cusip=None
                if not m and re.search(r'\b(?:CLL|CALL|PUT)\s+OPT',line,re.I):
                    missing_cusip=re.match(r'^(.+?)\s{2,}('+NUMBER+r')\s+('+NUMBER+r')\s*(SH|PRN)\b',line,re.I)
                    if missing_cusip:
                        name,cls=identity(missing_cusip[1]);row=dict(name=name,cls=cls,cusip='',value=int(amount(missing_cusip[2])*1000),shares=quantity(missing_cusip[3]),shareType=missing_cusip[4].upper(),putCall='Put' if re.search(r'\bPUT\b',name,re.I) else 'Call')
                        rows.append(row);previous=row;continue
                if m:
                    prefix=line[:m.start()].strip()
                    if not prefix:raise ValueError('Missing legacy issuer/class')
                    name,cls=identity(prefix)
                    if pending:name=pending+' '+name;pending=''
                    kind=(m[4] or 'SH').upper();pc=(m[5] or '').title() or (kind.title() if kind in ('PUT','CALL') else '')
                    if kind in ('PUT','CALL'):kind='SH'
                    if kind=='CO':
                        kind='CONTRACTS';pc='Put' if re.search(r'\bput\b',cls,re.I) else 'Call' if re.search(r'\bcall\b',cls,re.I) else ''
                        if not pc:raise ValueError('Legacy option contract side unavailable')
                    row=dict(name=name,cls=cls,cusip=m[1].replace(' ','').upper(),value=int(amount(m[2])*1000),shares=quantity(m[3]),shareType=kind,putCall=pc)
                    rows.append(row);previous=row
                elif previous:
                    continuation=re.match(r'^\s+('+NUMBER+r')\s+('+NUMBER+r')\s*(SH|PRN|PUT|CALL)?(?=\s|$)',line,re.I)
                    if continuation:
                        kind=(continuation[3] or previous['shareType']).upper();pc=previous['putCall']
                        if kind in ('PUT','CALL'):pc=kind.title();kind='SH'
                        rows.append({**previous,'value':int(amount(continuation[1])*1000),'shares':quantity(continuation[2]),'shareType':kind,'putCall':pc})
                    elif re.fullmatch(r'\s*[A-Za-z][A-Za-z &.,-]*\s*',line) and len(line.strip())<45:
                        pending=line.strip()
    expected_count=int(amount(count[1]));expected_total=int(amount(total[1])*1000)
    identities={(h['cusip'] or h['name'],h['shareType'],h['putCall']) for h in rows}
    if expected_count not in (len(rows),len(identities)) or abs(sum(h['value'] for h in rows)-expected_total)>500*(expected_count+1):
        raise ValueError(f'Legacy table reconciliation failed: {len(rows)}/{expected_count} rows, ${sum(h["value"] for h in rows)}/${expected_total}')
    if any(not h['name'] or not h['cls'] for h in rows):raise ValueError('Legacy row missing issuer or class')
    for h in rows:h['managerAllocations']=[dict(managerIds=[],shares=h['shares'],value=h['value'])]
    return rows
