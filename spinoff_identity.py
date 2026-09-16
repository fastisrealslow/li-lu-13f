"""Deterministic, source-bound target identity extraction (no paid AI dependency)."""
import re

IDENTITY_VERSION = 1
# Capitalization bounds prevent consuming prose before an English legal name.
LEGAL = r"[A-Z][A-Za-z0-9&’'\-]*(?: [A-Z][A-Za-z0-9&’'\-]*){0,7},? (?:Inc\.?|Corporation|Corp\.?|Limited|LIMITED|Ltd\.?|LTD\.?|PLC|LLC|Group)"
ZHLEGAL = r'[\u4e00-\u9fffA-Za-z（）()]{2,45}?(?:股份有限公司|有限公司)'
SPIN = r'spin[-‑ ]off|separation|分拆|分立|實物分派|实物分派'


def resolve_identity(text, title=''):
    from spinoff_events import filing_text, clean_name, title_target, target_key
    text = re.sub(r'\s+', ' ', filing_text(text)).strip()
    title = re.sub(r'^(?:內幕消息|内幕消息)[：: ]*', '', filing_text(title))
    definitions = []
    # Legal entity + explicitly defined alias. Legal qualifiers before parentheses
    # are allowed, but never cross sentences or another entity definition.
    for pattern in [rf'({LEGAL})(?:,? (?:a|an) [^();]{{0,120}}?)?\s*[（(]([^()（）]{{1,100}})[）)]',
                    rf'({ZHLEGAL})\s*[（(]([^()（）]{{1,60}})[）)]']:
        for m in re.finditer(pattern, text):
            name = clean_name(re.sub(r'^.*(?:茲提述|兹提述|本公佈乃|本公告乃|分拆所属子公司|分拆所屬子公司|关于分拆所属子公司)', '', m[1]))
            aliases = [a.strip(' ,') for a in re.findall(r'[“"「]\s*([^”"」]{1,65}?)\s*[”"」]', m[2])]
            if name and aliases:
                definitions.append((name, aliases, m.group()))
    candidates = []
    def add(name, quote, kind='entity'):
        name = clean_name(name)
        if not name or re.match(r'可比|可比較|參考|参考', name):
            return
        aliases = []
        # Resolve an explicit short name, including SpinCo and Company, in context.
        defs = [(n, a, q) for n, a, q in definitions if target_key(name) == target_key(n) or any(target_key(name) == target_key(x) for x in a)]
        if len({target_key(n) for n, _, _ in defs}) == 1:
            full, aliases, definition = defs[0]
            if target_key(full) != target_key(name): aliases = [*aliases, name]
            name = full
            quote = definition + ' … ' + quote if definition not in quote else quote
        candidates.append(dict(name=name, aliases=[a for a in aliases if a not in ('Company', '本公司', '本集團', '本集团', '公司', 'SpinCo', 'we', 'us', 'our')], quote=quote[:1100], kind=kind))
    # First consider explicit headline subjects, including names before 分拆.
    headline = title_target(title)
    if headline: add(headline, title, 'business' if re.search(r'業務|业务|物業|物业|REIT|項目|项目', headline, re.I) else 'entity')
    for p in [rf'({LEGAL}|{ZHLEGAL})(?:的|之)?\s*(?:建議|建议|擬議|拟议|擬|拟)?(?:分拆|獨立上市|独立上市)',
              r'分拆(?:及)?([\u4e00-\u9fff]{2,20}?)(?:於全國|于全国|獨立上市|独立上市)',
              r'(?:本集團|本集团)?([\u4e00-\u9fff]{2,20}(?:業務|业务))(?:擬|拟|的建議|之建議)?(?:分立|分拆)',
              r'上市之([\u4e00-\u9fff]{2,25}項目)']:
        for m in re.finditer(p, title):add(m[1], title, 'business' if re.search('業務|业务|項目|项目',m[1]) else 'entity')
    if candidates:
        unique = {target_key(c['name']):c for c in candidates}
        if len(unique)==1:
            headline_identity = next(iter(unique.values()))
            if headline_identity['kind'] == 'business':
                body_identity = resolve_identity(text)
                if body_identity.get('name') and body_identity.get('kind') == 'entity':
                    body_identity['aliases'] = [*body_identity.get('aliases', []), headline_identity['name']]
                    return body_identity
            return headline_identity
    candidates = []
    # Match the object of a separation/distribution, then resolve any defined alias.
    atom = rf'(?:{LEGAL}|[A-Z][A-Za-z0-9&-]*(?: [A-Z][A-Za-z0-9&-]*){{0,4}})'
    for p in [rf'(?:spin[-‑ ]off|separation)(?:\s*\([^)]{{1,65}}\))?\s+of\s+({atom})(?=\s*(?:[,(.;]|from\b))',
              rf'distribut\w*[^.;]{{0,150}}?(?:common stock|ordinary shares|shares)\s+(?:of|in)\s+({atom})(?=\s*(?:[,(.;]|to\b|from\b))',
              rf'(?:independent,? publicly traded company|company named)\s*,?\s*[“"]?({LEGAL})',
              rf'(?:分拆|分立)(?:(?:其|本公司|所屬|所属|附屬公司|附属公司|非全資|非全资|子公司)\s*)*({ZHLEGAL})']:
        for m in re.finditer(p, text):
            raw=m[1]
            distributed = bool(re.match('distribut', m.group(), re.I))
            # Generic defined names are accepted only when exactly mapped to a legal entity.
            if raw in ('SpinCo','Company','NewCo'):
                defs=[(n,a,q) for n,a,q in definitions if raw in a]
                if len({n for n,_,_ in defs})==1:add(defs[0][0], defs[0][2]+' … '+m.group())
            else:add(raw, m.group())
            if distributed and candidates: candidates[-1]['distributedEntity'] = True
            if candidates and re.match(r'\s+from\s+(?!the Company\b|Company\b)[A-Z]',text[m.end():]):
                candidates[-1]['separatedEntity'] = True
    # A child can file its own 8-K. Company is usable only when its shares
    # are explicitly distributed to another issuer's stockholders.
    company_distribution = re.search(r"distribut\w*[^.;]{0,100}?(?:shares of (?:the )?Company(?:[’']s)? common stock|(?:the )?Company[’']s (?:common stock|ordinary shares)|ordinary shares of the Company)[^;]{0,180}?(?:by|holders of(?: record of)?) (?!Company\b|the Company\b)[A-Z][\w-]*",text)
    if company_distribution and re.search(SPIN,text,re.I):
        defs=[(n,a,q) for n,a,q in definitions if 'Company' in a]
        if len({n for n,_,_ in defs})==1:
            add(defs[0][0],defs[0][2]+' … '+company_distribution.group())
            if candidates:candidates[-1]['distributedEntity']=True
    zh_distribution=re.search(r'實物分派本公司(?:普通股|股份)|將獲得[^。]{0,40}?本公司(?:內資股|H股)',text)
    if zh_distribution:
        defs=[(n,a,q) for n,a,q in definitions if '本公司' in a]
        if len({n for n,_,_ in defs})==1:
            add(defs[0][0],defs[0][2]+' … '+zh_distribution.group())
            if candidates:candidates[-1]['distributedEntity']=True
    # A legal entity explicitly defined as SpinCo is strong transaction evidence.
    if re.search(SPIN, text, re.I):
        for n,a,q in definitions:
            if any(alias in a for alias in ('SpinCo', '分拆公司', '分拆實體', '分拆实体')):add(n,q)
    unique={target_key(c['name']):c for c in candidates}
    # Collapse script variants and short aliases by their explicit definitions.
    if len(unique)==1:return next(iter(unique.values()))
    if len(unique)>1:return {'name':'','reason':'conflicting_names','quote':'','kind':''}
    # HK definition tables: "分拆公司" 指 <legal entity>. Bounded to one row.
    for m in re.finditer(r'[「“"](?:分拆公司|分拆實體|分拆实体)[」”"]\s*指\s*([^。；「」]{2,120})',text):
        legal=re.search(rf'({LEGAL}|{ZHLEGAL})',m[1])
        if legal and not re.match(r'\s*[(（]',m[1]):add(legal[1],m.group())
    for m in re.finditer(r'[「“"](?:分拆公司|分拆實體|分拆实体)[」”"]指[「“"]([^」”"]{2,30})[」”"]',text):
        add(m[1],m.group())
    if re.search('實物分派|实物分派',title):
        trust=re.search(r'[「“"]信託[」”"]\s*指根據信託契約組成的([\u4e00-\u9fff]{2,35})',text)
        if trust:return {'name':trust[1],'aliases':[], 'quote':trust.group(), 'kind':'instrument'}
    # Titles sometimes omit the target but define the distributed trust/issuer.
    for m in re.finditer(r'[「“\"](?:信託|信托|LHI)[」”\"]\s*指\s*([^。；「」]{2,100})',text):
        legal=re.match(r'([\u4e00-\u9fffA-Za-z（）()]{2,40}(?:信託|信托|有限公司))',m[1])
        if legal and re.search('實物分派|实物分派',title):add(legal[1],m.group())
    for m in re.finditer(rf'[‘’“"\']{{1,2}}SpinCo[‘’”"\']{{1,2}}\s+(?:means\s+)?({LEGAL})',text):
        add(m[1],m.group())
    # Business-only plans are useful identities, but are labelled as businesses.
    if not candidates:
        for m in re.finditer(r"(?:separation(?: and distribution)?|spin[-‑ ]off) of [A-Z][\w&’'\-]*[’']s ([A-Z][\w&\-]*(?: [A-Z][\w&\-]*){0,7}) (?:business|segment|programs)",text):add(m[1],m.group(),'business')
    if not candidates:
        for m in re.finditer(r'(?:分拆|分立)(?:本集團|本集团|其|旗下)?([\u4e00-\u9fff]{2,16}(?:業務|业务|REITs))',title):add(m[1],title,'business')
    if not candidates:
        for m in re.finditer(r'[（(](?:即|簡稱|简称)?[「“"]([^」”"]{2,35}REITs?)[」”"][）)]',text,re.I):add(m[1],m.group(),'business')
    if not candidates:
        for m in re.finditer(r'REIT\s*的相關資產為([^。]{2,65}?)，即',text,re.I):add(m[1],m.group(),'business')
    if not candidates:
        for m in re.finditer(r'REIT[^。]{0,50}相關資產為[^。]{0,65}（([^（）]{2,30}項目)）',text,re.I):add(m[1],m.group(),'business')
    if not candidates:
        for m in re.finditer(r'(?:分拆的底層資產為|分拆的底层资产为)([\u4e00-\u9fff]{2,25})(?=[，。])',text):add(m[1],m.group(),'business')
    unique={target_key(c['name']):c for c in candidates}
    if len(unique)==1:return next(iter(unique.values()))
    return {'name':'','reason':'not_identified','quote':'','kind':''}
