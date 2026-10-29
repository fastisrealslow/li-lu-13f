"""Read original pre-XML 13F tables, rejecting partial or ambiguous extraction.

Legacy forms report values in thousands. Both the unconsolidated entry count
and declared value total must reconcile before a table can enter history.
"""
import re
from decimal import Decimal
from bs4 import BeautifulSoup

VERSION = 5
NUMBER = r'[\d,]+(?:\.\d+)?'
CUSIP=r'(?:[A-Z0-9*@#]{6} {0,3}[A-Z0-9*@#]{2} {0,3}[A-Z0-9*@#]|[0-9]{7,8})'
ROW=re.compile(r'\b('+CUSIP+r')\s+\$?\s*('+NUMBER+r')\s+('+NUMBER+r')\s*(SH|PRN|PR|PUT|CALL|CO)?(?:\s+(PUT|CALL)\b)?(?=\s|$)',re.I)
CLASS=re.compile(r'^(.*?)\s+((?:COM(?:MON)?(?:\s+STOCK)?(?:\s+NEW)?|CL(?:ASS)?\s+[A-Z](?:\s+NEW)?|ORD(?:INARY)?|SHS?(?:\s+.*)?|ADR(?:\s+NEW)?|SP(?:ON(?:SORED|S))?\s+ADR.*|SPONSORED.*|PREF.*|PFD.*|LEA|NOTE.*|DEB.*|(?:SUB|SB|SR|JR|SD|SDCV|DBCV|CV)\b.*|PUT|CALL))$',re.I)

def amendment_type(raw):
    text=BeautifulSoup(raw.decode('utf-8',errors='replace'),'html.parser').get_text(' ',strip=True)
    checked=r'(?:\[\s*[xX]\s*\]|\|\s*[xX]\s*\||\(\s*[xX]\s*\))'
    rest=bool(re.search(checked+r'\s*(?:is\s+)?a\s+restatement',text,re.I))
    adds=bool(re.search(checked+r'\s*adds?\s+new\s+holdings?\s+entries',text,re.I))
    if rest and not adds:return 'RESTATEMENT'
    if adds and not rest:return 'NEW HOLDINGS'
    return None

def verify_report_file_number(raw, expected):
    # SEC indexing headers can use an old registrant number. The actual 13F
    # cover must match the explicitly configured manager report file number.
    source=raw.decode('utf-8',errors='replace')
    xml_number=re.search(r'<(?:\w+:)?form13FFileNumber>\s*([0-9]+)[ -]+([0-9]+)',source,re.I)
    text=BeautifulSoup(source,'html.parser').get_text(' ',strip=True)
    match=re.search(r'13F\s+File\s+Number\s*:\s*([0-9]+)[ -]+([0-9]+)',text,re.I)
    parts=re.findall(r'\d+',expected)
    match=xml_number or match
    # The initial 13F may explicitly say Unassigned. Its SEC-assigned header
    # number can bind that initial report; a missing or different cover cannot.
    if not match and re.search(r'13F\s+File\s+Number\s*:\s*(?:Unassigned\b|(?=The institutional))',text,re.I):
        header=source.split('</SEC-HEADER>',1)[0]
        if 'CENTRAL INDEX KEY:' in header and re.search(r'CONFORMED SUBMISSION TYPE:\s*13F-HR\s*(?:\n|$)',header):
            match=re.search(r'SEC FILE NUMBER:\s*([0-9]+)[ -]+([0-9]+)',header)
    if not match or len(parts)!=2 or tuple(map(int,match.groups()))!=tuple(map(int,parts)):
        raise ValueError('Historical reporter 13F cover file number does not match the verified manager')


class LegacyHoldings(list):
    def __init__(self, rows, reconciliation=None):
        super().__init__(rows)
        self.reconciliation = reconciliation

def identity(prefix):
    prefix=re.sub(r'^D\s+','',prefix.strip())
    m=CLASS.match(prefix)
    if m:return m[1].strip(),m[2].strip()
    if re.search(r'[a-z]com$', prefix): return prefix[:-3].strip(), 'COM'
    fields=re.split(r'\s{2,}',prefix)
    if len(fields)>=2:return ' '.join(fields[:-1]),fields[-1]
    raise ValueError('Legacy issuer/class columns are ambiguous')

def quantity(value):
    value=amount(value)
    return int(value) if value==value.to_integral() else float(value)


def amount(value):
    return Decimal(re.sub(r'[$,\s]','',value))


def fixed_width_tables(source):
    """Use SEC column markers so manager IDs cannot become invented holdings."""
    rows = []
    found = False
    layouts = set()
    previous = waiting = None
    name_parts = []
    for table in re.findall(r'<TABLE\b[^>]*>(.*?)</TABLE>', source, re.I | re.S):
        lines = table.expandtabs(8).splitlines()
        marker = next((i for i, line in enumerate(lines)
                       if len(re.findall(r'<[SC]>', line, re.I)) >= 5), None)
        if marker is None:
            continue
        positions = [m.start() for m in re.finditer(r'<[SC]>', lines[marker], re.I)]
        if not re.search(r'CUSIP', '\n'.join(lines[:marker]), re.I) and tuple(positions) not in layouts:
            continue
        layouts.add(tuple(positions))
        name_end, cusip_start, value_start, shares_start = positions[1:5]
        for line in lines[marker + 1:]:
            if '<' in line or not line.strip():
                continue
            offset=max(name_end,cusip_start-3)
            candidate=re.search(r'(?:[A-Z0-9*@#]{6} {0,3}[A-Z0-9*@#]{2} {0,3}[A-Z0-9*@#]|[A-Z0-9*@#]{7} [A-Z0-9*@#]{2} [A-Z0-9*@#])(?=\s|$)',line[offset:value_start+2],re.I)
            code=candidate[0] if candidate else ''
            if candidate and any(c.isdigit() for c in code):
                found = True
                prefix=line[:offset+candidate.start()].strip()
                try:name,cls=identity(prefix)
                except ValueError:
                    if re.fullmatch(r'COM|ADR|PFD.*|PREF.*|CL [AB]',prefix,re.I):name,cls=(previous or {}).get('name',''),prefix
                    else:name,cls=line[:name_end].strip(),line[name_end:offset+candidate.start()].strip()
                name = ' '.join([*name_parts,name]).strip() or (previous or {}).get('name','')
                name_parts = []
                tail = line[offset+candidate.end():]
                tail=re.sub(r'(\d+\.\d+)\.0+(?=SH\b)',r'\1',tail)
                match = re.match(r'\s*\$?\s*('+NUMBER+r')\s+('+NUMBER+r')\s*(SH|PRN|PR|PUT|CALL|CO)?(?:\s+(PUT|CALL)\b)?(?=\s|$)', tail, re.I)
                row = dict(name=name, cls=cls, cusip=re.sub(r'\s', '', code).upper())
                if match:
                    kind = (match[3] or 'SH').upper()
                    if kind=='PR':kind='PRN'
                    side = (match[4] or '').title() or (kind.title() if kind in ('PUT', 'CALL') else '')
                    if kind in ('PUT', 'CALL'):
                        kind = 'SH'
                    if kind == 'CO':
                        kind = 'CONTRACTS'
                        side = 'Put' if re.search('put', cls, re.I) else 'Call' if re.search('call', cls, re.I) else ''
                        if not side:
                            raise ValueError('Legacy option contract side unavailable')
                    row.update(value=int(amount(match[1])*1000), shares=quantity(match[2]), shareType=kind, putCall=side)
                    rows.append(row)
                    previous, waiting = row, None
                else:
                    # Fixed-width numeric fields may touch. Split only when
                    # the separately filed voting total proves one quantity.
                    joined=re.match(r'\s*(\d{8,})\s*(SH|PRN)\b',tail,re.I)
                    if joined and len(positions)>=11:
                        votes=re.findall(NUMBER,line[max(0,positions[-3]-2):])
                        voting=sum(amount(v) for v in votes)
                        choices=[(joined[1][:i],joined[1][i:]) for i in range(1,len(joined[1])) if amount(joined[1][i:])==voting and voting>0]
                        if len(choices)==1:
                            value,shares=choices[0]
                            row.update(value=int(amount(value)*1000),shares=quantity(shares),shareType=joined[2].upper(),putCall='')
                            rows.append(row);previous,waiting=row,None
                            continue
                    # Some filers put the value on the following physical line.
                    match = re.match(r'\s*('+NUMBER+r')\s*(SH|PRN|PR)\b(?:\s+(PUT|CALL)\b)?', tail, re.I)
                    if not match:
                        raise ValueError('Incomplete fixed-width holdings row: '+line.strip())
                    row.update(shares=quantity(match[1]), shareType=match[2].upper(), putCall=(match[3] or '').title())
                    waiting = row
                continue
            value = line[value_start:shares_start].strip()
            # Historical option rows sometimes omit the underlying CUSIP.
            # Preserve the explicit PUT/CALL and filed quantity, never borrow
            # the preceding stock's identifier.
            if not code and line[:name_end].strip() and line[name_end:cusip_start].strip():
                match = re.match(r'\s*('+NUMBER+r')\s+('+NUMBER+r')\s*(SH|PRN|PR)\b', line[value_start:], re.I)
                if match:
                    row = dict(name=line[:name_end].strip(), cls=line[name_end:cusip_start].strip(), cusip='',
                               value=int(amount(match[1])*1000), shares=quantity(match[2]), shareType=match[3].upper(),
                               putCall='Put' if re.search(r'\bPUT\b', line[:cusip_start], re.I) else 'Call' if re.search(r'\b(?:CLL|CALL)\s+OPT',line[:cusip_start],re.I) else '')
                    rows.append(row)
                    previous = row
                    continue
            if waiting and re.fullmatch(r'\$?\s*'+NUMBER, value):
                waiting['value'] = int(amount(value)*1000)
                rows.append(waiting)
                previous, waiting = waiting, None
                continue
            # Continuation rows share the previous issuer but need their own
            # value AND quantity in the financial columns, not the manager list.
            if previous and not line[:cusip_start].strip():
                match = re.match(r'\s*\$?\s*('+NUMBER+r')\s+('+NUMBER+r')\s*(SH|PRN|PUT|CALL)?(?=\s|$)', line[cusip_start:], re.I)
                if match and cusip_start + match.start(1) >= shares_start:
                    match = None
                if match:
                    kind = (match[3] or previous['shareType']).upper()
                    side = previous['putCall']
                    if kind in ('PUT', 'CALL'):
                        side, kind = kind.title(), 'SH'
                    rows.append({**previous, 'value':int(amount(match[1])*1000), 'shares':quantity(match[2]), 'shareType':kind, 'putCall':side})
                    continue
            fragment = line[:name_end].strip()
            if fragment and not line[name_end:].strip() and re.search(r'[A-Za-z]', fragment) and not re.search(r'column|issuer|table|total|cusip|value|authority|shares|thousands|\d', fragment, re.I):
                name_parts.append(fragment)
        if waiting:
            raise ValueError('Unfinished wrapped legacy value')
    return rows if found else None


def vertical_tables(soup):
    """Old one-cell-per-line tables; accept only explicit financial column runs."""
    rows=[]
    for table in soup.find_all('table'):
        lines=[line.strip() for line in table.get_text('\n').splitlines() if line.strip()]
        for i,code in enumerate(lines):
            if i<2 or i+4>=len(lines) or not re.fullmatch(r'[A-Z0-9*@#]{8}[0-9]',code):continue
            if not all(re.fullmatch(NUMBER,lines[n]) for n in (i+1,i+2)):continue
            kind=lines[i+3].upper();side='';discretion=i+4
            if kind not in ('SH','PRN','PR'):continue
            if lines[discretion].upper() in ('PUT','CALL'):
                side=lines[discretion].title();discretion+=1
            if discretion>=len(lines) or lines[discretion].upper() not in ('SOLE','DEFINED','DFND','OTHER','SHARED'):continue
            name,cls=lines[i-2:i]
            if not re.search(r'[A-Za-z]',name) or not re.search(r'[A-Za-z]',cls):continue
            rows.append(dict(name=name,cls=cls,cusip=code,value=int(amount(lines[i+1])*1000),
                             shares=quantity(lines[i+2]),shareType='PRN' if kind=='PR' else kind,putCall=side))
    return rows


def pipe_tables(source):
    rows=[]
    for table in re.findall(r'<TABLE\b[^>]*>(.*?)</TABLE>',source,re.I|re.S):
        pending=[]
        for line in table.splitlines():
            cells=[c.strip() for c in line.split('|')]
            if len(cells)<8:continue
            code=re.sub(r'\s','',cells[2]).upper()
            if (re.fullmatch(r'[A-Z0-9*@#]{8}[0-9]',code) and all(re.fullmatch(NUMBER,cells[i]) for i in (3,4))
                and cells[5].upper() in ('SH','PRN') and cells[6].upper() in ('','PUT','CALL')
                and cells[7].upper() in ('SOLE','DEFINED','OTHER','SHARED')):
                rows.append(dict(name=' '.join([*pending,cells[0]]).strip(),cls=cells[1],cusip=code,
                    value=int(amount(cells[3])*1000),shares=quantity(cells[4]),shareType=cells[5].upper(),putCall=cells[6].title()));pending=[]
            elif cells[0] and not any(cells[1:]) and re.search(r'[A-Za-z]',cells[0]):pending.append(cells[0])
    return rows


def split_column_tables(source):
    """Join separately printed value/share tables by unique exact issuer names."""
    values=[];quantities=[]
    for table in re.findall(r'<TABLE\b[^>]*>(.*?)</TABLE>',source,re.I|re.S):
        lines=table.expandtabs(8).splitlines()
        marker=next((i for i,line in enumerate(lines) if len(re.findall(r'<[SC]>',line,re.I))>=4),None)
        if marker is None:continue
        positions=[m.start() for m in re.finditer(r'<[SC]>',lines[marker],re.I)]
        header=' '.join(lines[:marker]);pending=[];class_parts=[]
        value_table=len(positions)==4 and re.search('CUSIP',header,re.I) and re.search('VALUE',header,re.I)
        quantity_table='CUSIP' not in header.upper() and re.search('PRINCIPAL',header,re.I) and re.search('DISCRETION',header,re.I)
        if not value_table and not quantity_table:continue
        for line in lines[marker+1:]:
            if not line.strip() or '<' in line or re.search(r'COLUMN TOTAL|GRAND TOTAL',line,re.I):continue
            if value_table:
                name=line[:positions[1]].strip();cls=line[positions[1]:positions[2]].strip()
                code=re.sub(r'\s','',line[positions[2]:positions[3]]).upper();value=line[positions[3]:].strip()
                if re.fullmatch(r'[A-Z0-9*@#]{8}[0-9]',code) and re.fullmatch(NUMBER,value):
                    values.append(dict(name=' '.join([*pending,name]).strip(),cls=' '.join([*class_parts,cls]).strip(),cusip=code,value=int(amount(value)*1000)))
                    pending=[];class_parts=[]
                elif not line[positions[2]:].strip():
                    if name:pending.append(name)
                    if cls:class_parts.append(cls)
            else:
                row=re.match(r'^\s*(.+?)\s+('+NUMBER+r')\s+(SH|PRN)(?:\s+(PUT|CALL))?\s+(?:SOLE|DEFINED|OTHER|SHARED)\b',line,re.I)
                if row:
                    quantities.append(dict(name=' '.join([*pending,row[1]]).strip(),shares=quantity(row[2]),shareType=row[3].upper(),putCall=(row[4] or '').title()));pending=[]
                elif re.fullmatch(r'\s*[A-Za-z][A-Za-z &.,-]*\s*',line):pending.append(line.strip())
    key=lambda row:re.sub(r'[^A-Z0-9]','',row['name'].upper())
    v={key(r):r for r in values};q={key(r):r for r in quantities}
    if not v or len(v)!=len(values) or len(q)!=len(quantities) or v.keys()!=q.keys():return []
    return [{**row,**{k:q[key(row)][k] for k in ('shares','shareType','putCall')}} for row in values]


def parse_legacy(raw, *, retain_source_discrepancies=False, _use_fixed=True):
    source=raw.decode('utf-8',errors='replace')
    source=re.sub(r'(?<=\d)SHR\b','SH ',source,flags=re.I)
    if not re.search(r'CONFORMED SUBMISSION TYPE:\s*13F-HR\b|<TYPE>13F-HR\b',source,re.I):
        raise ValueError('Legacy source is not a complete 13F holdings report')
    if re.search(r'CONFORMED SUBMISSION TYPE:\s*13F-HR/A\b|<TYPE>13F-HR/A\b',source,re.I):
        if amendment_type(raw)!='RESTATEMENT':
            raise ValueError('Legacy amendments need explicit restatement evidence')
    soup=BeautifulSoup(source,'html.parser')
    text=re.sub(r'\s+',' ',soup.get_text(' ',strip=True))
    count=re.search(r'Table\s+Entry\s+Total\s*:[.\s]*('+NUMBER+')',text,re.I)
    total=re.search(r'Table\s+Value\s+Total(?:\s*\([^)]*\))?\s*:[.\s]*\$?\s*('+NUMBER+')',text,re.I)
    if (not count or not total) and not retain_source_discrepancies:
        raise ValueError('Legacy cover does not declare both entry count and value total')
    rows=pipe_tables(source) or split_column_tables(source)
    for tr in ([] if rows else soup.find_all('tr')):
        if tr.find('tr'):continue
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'],recursive=False)]
        for i,c in enumerate(cells):
            cusip=re.sub(r'\s','',c).upper()
            if i<2 or not re.fullmatch(r'[A-Z0-9*@#]{9}',cusip):continue
            rest=' '.join(cells[i+1:]);m=re.match(r'\$?\s*('+NUMBER+r')\s+('+NUMBER+r')\s+(SH|PRN|PR)\b(?:\s+(PUT|CALL)\b)?',rest,re.I)
            if not m:continue
            rows.append(dict(name=cells[i-2],cls=cells[i-1],cusip=cusip,value=int(amount(m[1])*1000),shares=int(amount(m[2])),shareType=m[3].upper(),putCall=(m[4] or '').title()))
            break
    if not rows:rows=vertical_tables(soup)
    fixed = fixed_width_tables(source) if not rows and _use_fixed else None
    if fixed is not None:
        rows = fixed
    if not rows:
        tables=re.findall(r'<TABLE\b[^>]*>(.*?)</TABLE>',source,re.I|re.S)
        # Early plaintext filings can have a tabular <TEXT> without TABLE tags.
        if not tables:tables=re.findall(r'<TEXT>(.*?)</TEXT>',source,re.I|re.S)
        for table in tables:
            table=re.sub(r'(\d)[ \t]*\n[ \t]*(SH|PRN|PR)\b',r'\1 \2',table,flags=re.I)
            table=re.sub(r'(?<=\d)\s*SHR\b',' SH',table,flags=re.I)
            header=next((line.expandtabs(8) for line in table.splitlines() if re.search(r'NAME OF ISSUER',line,re.I) and re.search(r'TITLE OF CLASS',line,re.I) and re.search(r'CUSIP',line,re.I)),None)
            class_start=re.search(r'TITLE OF CLASS',header,re.I).start() if header else None
            previous=None;pending=''
            for line in table.splitlines():
                m=ROW.search(line)
                while m and not any(c.isdigit() for c in m[1]):
                    m = ROW.search(line, m.start()+1)
                missing_cusip=None
                if not m and re.search(r'\b(?:CLL|CALL|PUT)\s+OPT',line,re.I):
                    missing_cusip=re.match(r'^(.+?)\s{2,}('+NUMBER+r')\s+('+NUMBER+r')\s*(SH|PRN|PR)\b',line,re.I)
                    if missing_cusip:
                        name,cls=identity(missing_cusip[1]);row=dict(name=name,cls=cls,cusip='',value=int(amount(missing_cusip[2])*1000),shares=quantity(missing_cusip[3]),shareType=missing_cusip[4].upper(),putCall='Put' if re.search(r'\bPUT\b',name,re.I) else 'Call')
                        rows.append(row);previous=row;continue
                if m:
                    prefix=line[:m.start()].strip()
                    if not prefix:raise ValueError('Missing legacy issuer/class')
                    try:name,cls=identity(prefix)
                    except ValueError:
                        if class_start is None or not line[:class_start].strip() or not line[class_start:m.start()].strip():raise
                        name,cls=line[:class_start].strip(),line[class_start:m.start()].strip()
                    if pending:name=pending+' '+name;pending=''
                    kind=(m[4] or 'SH').upper();kind='PRN' if kind=='PR' else kind;pc=(m[5] or '').title() or (kind.title() if kind in ('PUT','CALL') else '')
                    if kind in ('PUT','CALL'):kind='SH'
                    if kind=='CO':
                        kind='CONTRACTS';pc='Put' if re.search(r'\bput\b',cls,re.I) else 'Call' if re.search(r'\bcall\b',cls,re.I) else ''
                        if not pc:raise ValueError('Legacy option contract side unavailable')
                    row=dict(name=name,cls=cls,cusip=m[1].replace(' ','').upper().zfill(9),value=int(amount(m[2])*1000),shares=quantity(m[3]),shareType=kind,putCall=pc)
                    rows.append(row);previous=row
                elif previous:
                    continuation=re.match(r'^\s+('+NUMBER+r')\s+('+NUMBER+r')\s*(SH|PRN|PUT|CALL)?(?=\s|$)',line,re.I)
                    if continuation:
                        kind=(continuation[3] or previous['shareType']).upper();pc=previous['putCall']
                        if kind in ('PUT','CALL'):pc=kind.title();kind='SH'
                        rows.append({**previous,'value':int(amount(continuation[1])*1000),'shares':quantity(continuation[2]),'shareType':kind,'putCall':pc})
                    elif re.fullmatch(r'\s*[A-Za-z][A-Za-z &.,-]*\s*',line) and len(line.strip())<45:
                        pending=line.strip()
    for row in rows:
        if not row.get('putCall') and re.search(r'\b(?:CLL|CALL|PUT)\s+OPT',row['name']+' '+row['cls'],re.I):
            row['putCall']='Put' if re.search(r'\bPUT\s+OPT',row['name']+' '+row['cls'],re.I) else 'Call'
    expected_count=int(amount(count[1])) if count else None
    expected_total=int(amount(total[1])*1000) if total else None
    identities={(h['cusip'] or h['name'],h['shareType'],h['putCall']) for h in rows}
    actual_total=sum(h['value'] for h in rows)
    count_matches=expected_count is None or expected_count in (len(rows),len(identities))
    total_matches=expected_total is not None and abs(actual_total-expected_total)<=500*((expected_count or len(rows))+1)
    if fixed is not None and (not count_matches or not total_matches):
        # Some ASCII tables mix tabs and spaces. Admit a token-based fallback
        # only if BOTH cover count and value reconcile independently.
        try:return parse_legacy(raw,_use_fixed=False)
        except ValueError:pass
        if retain_source_discrepancies and not count_matches:
            try:return parse_legacy(raw,retain_source_discrepancies=True,_use_fixed=False)
            except ValueError:pass
    count_discrepancy_proven = retain_source_discrepancies and fixed is not None and total_matches
    if (not count_matches and not count_discrepancy_proven) or (not total_matches and not retain_source_discrepancies):
        raise ValueError(f'Legacy table reconciliation failed: {len(rows)}/{expected_count} rows, ${sum(h["value"] for h in rows)}/${expected_total}')
    if not rows or (expected_count is None and fixed is None):
        raise ValueError('Legacy extraction has no independent completeness evidence')
    if any(not h['name'] for h in rows):raise ValueError('Legacy row missing issuer')
    for h in rows:h['managerAllocations']=[dict(managerIds=[],shares=h['shares'],value=h['value'])]
    return LegacyHoldings(rows, {'status':'cover_count_mismatch' if not count_matches else 'reconciled' if total_matches and expected_count is not None else 'missing_cover_totals' if expected_count is None or expected_total is None else 'cover_total_mismatch',
                                'reportedEntries':expected_count, 'parsedEntries':len(rows),
                                'reportedValue':expected_total, 'tableValue':actual_total,
                                'difference':actual_total-expected_total if expected_total is not None else None})
