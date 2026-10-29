"""Read original pre-XML 13F tables, rejecting partial or ambiguous extraction.

Legacy forms report values in thousands. Both the unconsolidated entry count
and declared value total must reconcile before a table can enter history.
"""
import re
from decimal import Decimal
from bs4 import BeautifulSoup

VERSION = 3
NUMBER = r'[\d,]+(?:\.\d+)?'
CUSIP=r'(?:[A-Z0-9*@#]{6} {0,3}[A-Z0-9*@#]{2} {0,3}[A-Z0-9*@#]|[0-9]{7,8})'
ROW=re.compile(r'\b('+CUSIP+r')\s+\$?\s*('+NUMBER+r')\s+('+NUMBER+r')\s*(SH|PRN|PR|PUT|CALL|CO)?(?:\s+(PUT|CALL)\b)?(?=\s|$)',re.I)
CLASS=re.compile(r'^(.*?)\s+((?:COM(?:MON)?(?:\s+STOCK)?|CL(?:ASS)?\s+[A-Z](?:\s+NEW)?|ORD(?:INARY)?|SHS?(?:\s+.*)?|ADR|SPONSORED.*|PREF.*|PFD.*|LEA|NOTE.*|DEB.*|PUT|CALL))$',re.I)

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
        lines = table.splitlines()
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


def parse_legacy(raw, *, retain_source_discrepancies=False):
    source=raw.decode('utf-8',errors='replace')
    if not re.search(r'CONFORMED SUBMISSION TYPE:\s*13F-HR\b|<TYPE>13F-HR\b',source,re.I):
        raise ValueError('Legacy source is not a complete 13F holdings report')
    if re.search(r'CONFORMED SUBMISSION TYPE:\s*13F-HR/A\b|<TYPE>13F-HR/A\b',source,re.I):
        raise ValueError('Legacy amendments need explicit restatement evidence')
    soup=BeautifulSoup(source,'html.parser')
    text=re.sub(r'\s+',' ',soup.get_text(' ',strip=True))
    count=re.search(r'Table\s+Entry\s+Total\s*:[.\s]*('+NUMBER+')',text,re.I)
    total=re.search(r'Table\s+Value\s+Total(?:\s*\([^)]*\))?\s*:[.\s]*\$?\s*('+NUMBER+')',text,re.I)
    if (not count or not total) and not retain_source_discrepancies:
        raise ValueError('Legacy cover does not declare both entry count and value total')
    rows=[]
    for tr in soup.find_all('tr'):
        if tr.find('tr'):continue
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'],recursive=False)]
        for i,c in enumerate(cells):
            cusip=re.sub(r'\s','',c).upper()
            if i<2 or not re.fullmatch(r'[A-Z0-9*@#]{9}',cusip):continue
            rest=' '.join(cells[i+1:]);m=re.match(r'\$?\s*('+NUMBER+r')\s+('+NUMBER+r')\s+(SH|PRN|PR)\b(?:\s+(PUT|CALL)\b)?',rest,re.I)
            if not m:continue
            rows.append(dict(name=cells[i-2],cls=cells[i-1],cusip=cusip,value=int(amount(m[1])*1000),shares=int(amount(m[2])),shareType=m[3].upper(),putCall=(m[4] or '').title()))
            break
    fixed = fixed_width_tables(source) if not rows else None
    if fixed is not None:
        rows = fixed
    if not rows:
        tables=re.findall(r'<TABLE\b[^>]*>(.*?)</TABLE>',source,re.I|re.S)
        # Early plaintext filings can have a tabular <TEXT> without TABLE tags.
        if not tables:tables=re.findall(r'<TEXT>(.*?)</TEXT>',source,re.I|re.S)
        for table in tables:
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
                    name,cls=identity(prefix)
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
