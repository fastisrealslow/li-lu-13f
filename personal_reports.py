"""Read original iXBRL/PDF reports; never use a quote vendor's financials.

Selectors are issuer-specific, but numbers are always read from the document.
Ambiguous cells, changed layouts and conflicting tags fail closed.
"""
import hashlib
import html
import re
from html.parser import HTMLParser


class FinancialTables(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tables=[]; self.depth=0; self.row=None; self.cell=None; self.rows=None
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        if tag=='table':
            self.depth+=1
            if self.depth==1:self.rows=[]
        if self.depth==1 and tag=='tr':self.row=[]
        if self.depth==1 and tag in ('td','th'):self.cell=[]
    def handle_data(self, data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self, tag):
        if self.depth==1 and tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(' '.join(self.cell).split()));self.cell=None
        if self.depth==1 and tag=='tr' and self.row is not None:
            self.rows.append(self.row);self.row=None
        if tag=='table':
            if self.depth==1:self.tables.append(self.rows)
            self.depth-=1


def decimal(text):
    text = text.strip().replace(',', '').replace('\u00a0', '').replace('−', '-')
    text = re.sub(r'^(?:HK\$|RMB|US\$)', '', text)
    text = text.rstrip('.,;')
    if text in ('-', '—', '–'): return 0.0
    if text.startswith('(') and text.endswith(')'): text = '-' + text[1:-1]
    if not re.fullmatch(r'-?\d+(?:\.\d+)?', text): raise ValueError('Not a financial number: ' + text)
    return float(text)


def attributes(text):
    return {k.lower(): html.unescape(v) for k, _, v in re.findall(r'([\w:.-]+)\s*=\s*([\"\'])(.*?)\2', text, re.S)}


def ads_conversion(report):
    text=report.raw.decode('utf-8')
    text=re.sub(r'<ix:header\b[^>]*>.*?</ix:header>','',text,flags=re.S|re.I)
    text=' '.join(html.unescape(re.sub('<[^>]*>',' ',text)).split())
    pattern=r'each\s+(?:American depositary share|ADS|of (?:which|our ADSs))\s*,?\s*(?:represents|representing)\s+(\d+|one|two|three|four|five|ten|twenty|fifty|one hundred)\s+(?:Class A\s+)?ordinary shares'
    match=re.search(pattern,text,re.I)
    if not match:raise ValueError('No original-report ADS conversion statement')
    words={'one':1,'two':2,'three':3,'four':4,'five':5,'ten':10,'twenty':20,'fifty':50,'one hundred':100}
    ratio=int(match[1]) if match[1].isdigit() else words[match[1].lower()]
    return {'value':ratio,'label':'每份 ADS 对应普通股数量','evidence':text[max(0,match.start()-100):match.end()+70]}


class InlineReport:
    def __init__(self, raw):
        self.raw = raw
        self.digest = hashlib.sha256(raw).hexdigest()
        text = raw.decode('utf-8')
        self.contexts = {}
        for match in re.finditer(r'<(?:xbrli:)?context\b([^>]*)>(.*?)</(?:xbrli:)?context>', text, re.S | re.I):
            attrs, body = attributes(match[1]), match[2]
            ctx = {k.lower(): v for k, v in re.findall(r'<(?:xbrli:)?(startDate|endDate|instant)>(.*?)</', body, re.I)}
            ctx['dimensions'] = bool(re.search(r'explicitMember|typedMember', body, re.I))
            self.contexts[attrs['id']] = ctx
        self.units = {}
        for match in re.finditer(r'<(?:xbrli:)?unit\b([^>]*)>(.*?)</(?:xbrli:)?unit>', text, re.S | re.I):
            measures = re.findall(r'<(?:xbrli:)?measure>(.*?)</', match[2], re.I)
            self.units[attributes(match[1])['id']] = measures[0].split(':')[-1] if len(measures) == 1 else 'ratio'
        self.facts = []
        for match in re.finditer(r'<ix:nonFraction\b([^>]*)>(.*?)</ix:nonFraction>', text, re.S | re.I):
            attrs = attributes(match[1])
            if attrs.get('xsi:nil') == 'true' or attrs.get('xs:nil') == 'true': continue
            ctx = self.contexts.get(attrs.get('contextref'), {})
            if ctx.get('dimensions'): continue
            val = html.unescape(re.sub('<[^>]*>', '', match[2])).strip()
            try: value = decimal(val) * 10 ** int(attrs.get('scale', 0)) * (-1 if attrs.get('sign') == '-' else 1)
            except ValueError: continue
            self.facts.append(dict(concept=attrs['name'], unit=self.units.get(attrs.get('unitref')),
                value=value, context=ctx, raw=val, contextId=attrs.get('contextref'), scale=attrs.get('scale', '0')))

    def extract(self, selector, year):
        if 'htmlRow' in selector:
            if not hasattr(self, 'tables'):self.tables=FinancialTables(self.raw.decode('utf-8')).tables
            matches=[]
            for table in self.tables:
                for row in table:
                    if row and re.fullmatch(selector['htmlRow'], row[0], re.I) and len(row)==selector['cellCount']:
                        matches.append(row)
            if len(matches)!=selector['matches']:raise ValueError('Changed annual-report comparative table')
            row=matches[selector.get('occurrence',0)]
            return dict(value=decimal(row[selector['cellIndex']])*selector.get('multiplier',1000), evidence=' | '.join(row), raw=row[selector['cellIndex']])
        concept, unit = selector['concept'], selector.get('unit', 'CNY')
        target = f'{year}-12-31'
        candidates = [f for f in self.facts if f['concept'] == concept and f['unit'] == unit
            and (f['context'].get('instant') == target if selector.get('instant', True) else
                 f['context'].get('enddate') == target and f['context'].get('startdate') == f'{year}-01-01')]
        if not candidates: raise ValueError(f'Missing original report fact: {concept} / {year}')
        if len({f['value'] for f in candidates}) != 1: raise ValueError(f'Conflicting original report facts: {concept}')
        f = candidates[0]
        return dict(value=f['value'], evidence=f"{concept}; {f['context']}; {f['raw']} × 10^{f['scale']}",
            concept=concept, contextId=f['contextId'], raw=f['raw'], scale=f['scale'])


class PDFReport:
    def __init__(self, raw):
        import pymupdf
        self.raw = raw
        self.digest = hashlib.sha256(raw).hexdigest()
        self.document = pymupdf.open(stream=raw, filetype='pdf')
        self.pages = []
        for page in self.document:
            rows = []
            for w in sorted(page.get_text('words'), key=lambda w: (round(w[1] / 2), w[0])):
                if not rows or abs(rows[-1]['y'] - w[1]) > 2:
                    rows.append({'y': w[1], 'words': []})
                rows[-1]['words'].append(w)
            for row in rows:
                row['words'].sort(key=lambda w: w[0])
                row['text'] = ' '.join(w[4] for w in row['words'])
            self.pages.append(rows)

    def selected_page(self, selector):
        if selector.get('signature'):
            matches=[i for i,rows in enumerate(self.pages) if all(t in '\n'.join(r['text'] for r in rows) for t in selector['signature'])]
            if len(matches)!=1:raise ValueError('Financial table page signature changed or ambiguous')
            return matches[0]
        return selector['page']-1

    def financial_group(self, selector):
        start=self.selected_page(selector);inside=False;saw=False;values=[];seen=set()
        for pi in range(start,min(len(self.pages),start+1+selector.get('scopePages',0))):
            rows=self.pages[pi]
            for ri,row in enumerate(rows):
                text=row['text']
                if re.search(r'^(?:CURRENT ASSETS\b|Current assets\b|流动资产：?)',text):inside=True;saw=True
                if re.search(r'^(?:Total current assets\b|Total assets\b|CURRENT LIABILITIES\b|Current liabilities\b|Equity\b|流动资产合计|资产总计|流动负债：?)',text,re.I):inside=False
                if not inside or not re.search(selector['sumRows'],text,re.I):continue
                candidates=[]
                for following in rows[ri:]:
                    if following['y']>row['y']+selector.get('below',14):break
                    for w in following['words']:
                        if abs(w[2]/self.document[pi].rect.width-selector['xEnd'])>selector.get('xTolerance',.009):continue
                        try:value=decimal(w[4])*selector.get('multiplier',1000)
                        except ValueError:continue
                        candidates.append((following['y'],value,text+' | '+following['text'],pi,w))
                if candidates:
                    closest=min(candidates,key=lambda c:c[0]);identity=(closest[3],closest[4][0],closest[4][1])
                    if identity in seen:continue
                    seen.add(identity);values.append({'value':closest[1],'evidence':closest[2],'page':pi+1})
        if not saw:raise ValueError('No complete current-assets section for financial classification')
        return {'value':sum(v['value'] for v in values),'evidence':'; '.join(v['evidence'] for v in values) or '合并资产负债表流动资产段未单列本规则覆盖的金融资产。',
            'terms':values,'page':start+1,'policy':not values}

    def extract(self, selector, year):
        # Page anchors move with new reports; offset isolates e.g. the second
        # liability page without confusing current and non-current leases.
        anchor = selector.get('anchor')
        if anchor:
            matches = [i for i, rows in enumerate(self.pages)
                if re.search(anchor, '\n'.join(r['text'] for r in rows), re.I)]
            if len(matches) != 1: raise ValueError(f'Ambiguous financial statement anchor: {anchor} ({len(matches)})')
            page_indices = [matches[0] + selector.get('pageOffset', 0)]
        else:
            page_indices = [self.selected_page(selector)]
        candidates = []
        for pi in page_indices:
            rows = self.pages[pi]
            for ri, row in enumerate(rows):
                if not re.search(selector['row'], row['text'], re.I): continue
                candidates.append((pi, ri, row))
        occurrence = selector.get('occurrence', 0)
        if len(candidates) <= occurrence: raise ValueError('Missing PDF financial row: ' + selector['row'])
        if len(candidates) != selector.get('matches', occurrence + 1): raise ValueError('Ambiguous PDF financial row: ' + selector['row'])
        pi, ri, row = candidates[occurrence]
        if selector.get('unitPattern') and not re.search(selector['unitPattern'],'\n'.join(r['text'] for r in self.pages[pi]),re.I):
            raise ValueError('Financial statement units changed')
        # Coordinates, rather than reading order, handle wrapped Chinese
        # cells where last year's number appears above the current one.
        words = [] if selector.get('belowOnly') else list(row['words'])
        if selector.get('below'):
            words += [w for r in self.pages[pi][ri + 1:] if r['y'] <= row['y'] + selector['below'] for w in r['words']]
        nums = []
        for w in words:
            try: val = decimal(w[4])
            except ValueError: continue
            if selector.get('xEnd') is not None and abs(w[2] / self.document[pi].rect.width - selector['xEnd']) > selector.get('xTolerance', .008): continue
            nums.append((w[0], val, w[4]))
        nums.sort(key=lambda x: x[0])
        if selector.get('xEnd') is not None:
            if len(nums) != 1: raise ValueError('Missing/ambiguous PDF column: ' + selector['row'])
            item = nums[0]
        else:
            if len(nums) != selector['numberCount']: raise ValueError('Changed PDF table layout: ' + selector['row'])
            item = nums[selector['numberIndex']]
        return dict(value=item[1] * selector.get('multiplier', 1000),
            evidence=row['text'] + (' | ' + ' '.join(w[4] for w in words[len(row['words']):]) if len(words)>len(row['words']) else ''),
            page=pi + 1, raw=item[2])


def extract_recipe(report, recipe, year):
    if 'sumRows' in recipe:return report.financial_group(recipe)
    if 'sumConcepts' in recipe:
        values=[]
        for concept in recipe['sumConcepts']:
            if any(f['concept']==concept and f['unit']==recipe.get('unit','CNY') and f['context'].get('instant')==f'{year}-12-31' for f in report.facts):
                values.append(report.extract({'concept':concept,'unit':recipe.get('unit','CNY')},year))
        if not values:raise ValueError('No supported financial-asset category in consolidated statements')
        return dict(value=sum(v['value'] for v in values),evidence='; '.join(v['evidence'] for v in values),terms=values)
    if 'terms' in recipe:
        terms = [dict(extract_recipe(report, term['selector'], year), coefficient=term.get('coefficient', 1)) for term in recipe['terms']]
        return dict(value=sum(t['value'] * t['coefficient'] for t in terms),
            evidence='; '.join(f"{t['coefficient']:+g} × ({t['evidence']})" for t in terms), terms=terms,
            page=next((t.get('page') for t in terms if t.get('page')), None))
    if 'zeroPolicy' in recipe:
        # Explicit issuer policy, attached to the complete consolidated
        # statement, is displayed as such. It is never a missing-value fallback.
        if isinstance(report, PDFReport):
            page = report.selected_page(recipe)+1; text = '\n'.join(r['text'] for r in report.pages[page-1])
            if recipe.get('captureRow'):
                rows=[r for pg in report.pages[page-1:page+recipe.get('scopePages',0)] for r in pg]
                section=None;captures=[]
                for row in rows:
                    t=row['text']
                    if re.search(r'母公司资产负债表',t):break
                    if re.search(r'^(?:Current liabilities|CURRENT LIABILITIES|流动负债：?)$',t):section='current'
                    if re.search(r'^(?:Non-current liabilities|NON-CURRENT LIABILITIES|非流动负债：?)$',t):section='noncurrent'
                    if section!=recipe.get('scope') or not re.search(recipe['captureRow'],t,re.I):continue
                    for w in row['words']:
                        if abs(w[2]/report.document[page-1].rect.width-recipe['xEnd'])>recipe.get('xTolerance',.009):continue
                        try:val=decimal(w[4])*recipe.get('multiplier',1000)
                        except ValueError:continue
                        captures.append((val,t))
                if len(captures)>1:raise ValueError('New financing needs unambiguous debt classification')
                if captures:return dict(value=captures[0][0],evidence=captures[0][1],page=page)
        else:
            page = None; text = html.unescape(re.sub('<[^>]*>', ' ', report.raw.decode('utf-8')))
            # Previously absent financing can become nonzero in a later year.
            # Read its actual tagged value instead of silently retaining zero.
            captured=[]
            for concept in recipe.get('captureConcepts',[]):
                candidates=[f for f in report.facts if f['concept']==concept and f['unit']==recipe.get('unit','CNY') and f['context'].get('instant')==f'{year}-12-31']
                if candidates:captured.append(report.extract({'concept':concept,'unit':recipe.get('unit','CNY')},year))
            if captured:
                return dict(value=sum(f['value'] for f in captured),evidence='; '.join(f['evidence'] for f in captured),terms=captured)
        if not re.search(recipe['proof'], text, re.I): raise ValueError('Zero policy no longer supported')
        if recipe.get('forbid') and re.search(recipe['forbid'], text, re.I): raise ValueError('A formerly absent financial line now exists')
        return dict(value=0, evidence=recipe['zeroPolicy'], page=page, policy=True)
    return report.extract(recipe, year)
