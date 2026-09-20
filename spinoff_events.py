"""Evidence-backed spin-off dossiers. No AI or network required to normalize data."""
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from spinoff_identity import resolve_identity, IDENTITY_VERSION

STATUSES = {'needs_review', 'announced', 'approved', 'record_set', 'prospectus', 'completed', 'terminated', 'paused'}
RULE_VERSION = 2
TYPE_RULE_VERSION = 1
INTRO_PATTERN = r'以介紹方式|以介绍方式|以介紹式|以介绍式|介紹(?:式)?上市|介绍(?:式)?上市|listing by (?:way of )?introduction'


def merge_evidence(previous, current):
    """Retain document history; replace only a successfully re-read document."""
    merged = {p.get('accession') or p.get('url'): p for p in previous if p.get('accession') or p.get('url')}
    for proof in current:
        key = proof.get('accession') or proof.get('url')
        if key:
            old = merged.get(key, {})
            same_rules = old.get('identityVersion', 0) >= proof.get('identityVersion', 0)
            if same_rules and old.get('identityReferences') and 'identityReferences' not in proof:
                proof = {**proof, 'identityReferences': old['identityReferences']}
            weaker_name = not proof.get('targetName') or (proof.get('identityKind') == 'business' and old.get('identityReason') == 'dated_reference')
            if weaker_name and proof.get('identityReason') != 'conflicting_names' and old.get('targetName') and same_rules:
                proof = {**proof, **{field: old[field] for field in ('targetName', 'targetAliases', 'identityQuote', 'identityKind', 'identityVersion', 'identityReason', 'identitySourceUrl', 'identitySourceDate', 'distributedEntity', 'separatedEntity') if field in old}}
            merged[key] = proof
    return list(merged.values())


def filing_text(value):
    """Join PDF layout whitespace inside Chinese prose, preserving English words."""
    value = html.unescape(value or '')
    return re.sub(r'(?<=[\u3400-\u9fff0-9，。；：（）()])\s+(?=[\u3400-\u9fff0-9，。；：（）()])', '', value)


def filing_url(cik, accession, document=''):
    if not str(cik).isdigit() or not re.fullmatch(r'\d{10}-\d{2}-\d{6}', accession or ''):
        return ''
    if not re.fullmatch(r'[\w.\-]+', document or ''):
        document = accession + '-index.html'
    return f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace("-", "")}/{document}'


def source_url(ann, cik=''):
    if ann.get('adsh') and cik:
        return filing_url(cik, ann['adsh'], ann.get('primaryDocument', ''))
    url = ann.get('url') or ann.get('docUrl') or ''
    if url.startswith('/listedco/'):
        url = 'https://www1.hkexnews.hk' + url
    p = urlparse(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password:
        return ''
    return url


def direct_source(url):
    return bool(url) and not any(x in url for x in ('browse-edgar', '/edgar/browse', '/search/'))


def iso_date(value):
    value = html.unescape(str(value or '')).strip()
    if '年' in value:
        value = re.sub(r'\s+', '', value)
        digits = dict(zip('零〇一二三四五六七八九', '00123456789'))
        def number(m):
            token = m.group(0)
            if '十' in token:
                if token.count('十') != 1:
                    return token
                a, b = token.split('十')
                return str(int(digits.get(a, '1')) * 10 + int(digits.get(b, '0')))
            return ''.join(digits[c] for c in token)
        value = re.sub(r'[零〇一二三四五六七八九十]+', number, value)
    for fmt in ('%Y-%m-%d', '%B %d, %Y', '%b %d, %Y', '%B %d %Y', '%b %d %Y', '%Y年%m月%d日'):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return ''


def clean_name(value):
    name = re.sub(r'\s+', ' ', str(value or '')).strip(' .,')
    name = re.sub(r'^(?:(?:所屬子公司|所属子公司|內容有關|内容有关|本公司|控股|子公司|附屬公司|附属公司|非全資|非全资|主体指|主體指|指))+', '', name)
    if any(name.count(a) != name.count(b) for a, b in [('(', ')'), ('（', '）')]):
        return ''
    name = re.sub(r'(有限公司)及$', r'\1', name)
    if (not 2 <= len(name) <= 90 or name.lower() in {'tbd', 'spinco', 'newco', '(解析中)', '子公司', '附屬公司'}
            or re.search(r'\b(?:will|would|shall|entitlement|shares|common stock|receive|expects|from|including|owned)\b|建議分拆及|建议分拆及|公司的建議|交易所|董事會|董事会|股票價格|股票价格|分拆|獨立上市|独立上市|上市董事|本集團|本集团|並於|并于|批准|公告|茲提|兹提|拆上|上市市|本次發行|本次发行|財務顧問|财务顾问|法律顧問|法律顾问|最新情況|最新情况', name, re.I)):
        return ''
    return name


def entity_key(value):
    value = re.sub(r'\([^)]*\)', '', str(value or ''))
    value = re.sub(r'\s*[/\\][A-Z]{2}[/\\]?\s*$', '', value)
    return re.sub(r'[^a-z0-9\u4e00-\u9fff]', '', re.sub(r'\b(?:inc|corp|corporation|co|ltd|llc)\b', '', value.lower()))


def extract_name(text):
    text = filing_text(text)
    # Bounded, capitalized legal names; never consume an entire prose sentence.
    patterns = [
        r'(?:spin[- ]off|separation) of ([A-Z][\w&.-]*(?: [A-Z][\w&.-]*){0,7}(?:,? (?:Inc\.?|Corporation|Corp\.?|LLC|Ltd\.?|Holdings|Group)))',
        r'distribut\w*\s+(?:all (?:of )?(?:the )?)?(?:outstanding )?shares of ([A-Z][\w&.-]*(?: [A-Z][\w&.-]*){0,6}(?:,? (?:Inc\.?|Corporation|Corp\.?|LLC|Ltd\.?)))',
    ]
    patterns.append(r'(?:建議分拆|建议分拆|分拆)(?:(?:其|本公司|所屬|所属|附屬公司|附属公司|附屬|附属|子公司|非全資|非全资)\s*)*([\u4e00-\u9fffA-Za-z（）()]{2,45}?(?:股份有限公司|有限公司))')
    patterns.append(r'分拆\s*([A-Z][A-Z0-9 &,.-]{3,80}?(?:INC\.|LIMITED|LTD\.))(?:及於|並於|并于|於)')
    # HKEX titles also use a short name before "於…獨立上市".
    patterns.append(r'(?:建議分拆|建议分拆)及([\u4e00-\u9fff]{2,20}?)於香港聯合交易所有限公司主板獨立上市')
    names = {target_key(clean_name(m.group(1))): clean_name(m.group(1)) for p in patterns for m in re.finditer(p, text) if clean_name(m.group(1))}
    return next(iter(names.values())) if len(names) == 1 else ''


def title_target(title):
    """A bounded headline name outranks old company-wide enrichment."""
    title = filing_text(title)
    matches = re.findall(r'分拆(?:及)?\s*([^。；:\n]{2,85}?)(?:並於|并于|及於|於|至)(?:香港|泰國|菲律賓|中國|上海|深圳)', title)
    names = {target_key(clean_name(n)): clean_name(n) for n in matches if clean_name(n)}
    return next(iter(names.values())) if len(names) == 1 else extract_name(title)


def target_key(name):
    # Script/spacing variants only; aliases require an explicit filing definition.
    variants = str.maketrans('復國際製藥業華東車環醫術資產廣實體屬銅箔聯網紡織潤龍電寶慶機輛藝寧', '复国际制药业华东车环医术资产广实体属铜箔联网纺织润龙电宝庆机辆艺宁')
    return re.sub(r'[\s,]+', '', str(name or '')).translate(variants).casefold().rstrip('.')


def introduction_quote(text):
    """Explicit listing method only; in-specie distribution alone proves no method."""
    for sentence in re.split(r'[。；;\n]', filing_text(text)):
        if not re.search(INTRO_PATTERN, sentence, re.I):
            continue
        if not re.search(r'上市|listing|listed', sentence, re.I):
            continue
        if re.search(r'(?:並非|并非|不會|不会|不擬|不拟|不以|非以|並不|并不).{0,30}(?:介紹|介绍)|(?:not|no longer).{0,40}(?:listing|listed|introduction)', sentence, re.I):
            continue
        return sentence.strip()
    return ''


def classify_hk_type(titles):
    text = filing_text(' '.join(titles))
    exchange = next(((zh, en, code) for pattern, zh, en, code in [
        ('菲律賓|菲律宾', '菲律宾交易所', 'PSE', 'other'), ('泰國|泰国', '泰国交易所', 'SET', 'other'),
        ('深圳證券|深圳证券|深交所', '深交所', 'SZSE', 'a_sz'), ('上海證券|上海证券|上交所', '上交所', 'SSE', 'a_sh'),
        ('聯交所|联交所|香港聯合交易所|港交所|香港主板', '港交所', 'HKEX', 'hk'),
        ('納斯達克|纳斯达克|Nasdaq', '纳斯达克', 'Nasdaq', 'other'), ('A股', 'A股', 'A-Share', 'a')
    ] if re.search(pattern, text, re.I)), ('待定', 'TBD', 'other'))
    zh, en, suffix = exchange
    is_reit = bool(re.search(r'REIT|不動產.*基金|不动产.*基金|基礎設施.*基金|基础设施.*基金|公募基金', text, re.I))
    distribution = bool(re.search(r'實物分派|实物分派|distribution in specie', text, re.I))
    if is_reit:
        code = 'reit_' + suffix.removeprefix('a_') if suffix != 'other' else 'reit'
        label, label_en = 'REIT·' + zh, 'REIT·' + en
    elif introduction_quote(text):
        code, label, label_en = 'intro_' + suffix, '介绍上市·' + zh, 'Introduction·' + en
    elif re.search(r'獨立上市|独立上市|上市|IPO|掛牌|挂牌', text, re.I):
        code = 'ipo_' + suffix + ('_dist' if distribution else '')
        label = ('IPO+实物分派·' if distribution else '分拆上市·') + zh
        label_en = ('IPO+distribution·' if distribution else 'Spin-off IPO·') + en
    elif distribution:
        code, label, label_en = 'distribution', '实物分派', 'Distribution in specie'
    else:
        code, label, label_en = 'unknown', '类型待核实', 'Type to verify'
    return dict(code=code, exchange_zh=zh, exchange_en=en, label_zh=label, label_en=label_en, is_reit=is_reit)


def infer_status(text):
    """Return a rule match and its exact sentence, never infer completion from a date."""
    text = filing_text(text)
    sentences = re.split(r'(?<=[.!?。；;])\s+|[\n。；]', re.sub(r'[ \t]+', ' ', text or ''))
    candidates = []
    for sentence in sentences:
        s = sentence.strip()
        if not s or len(s) > 1200:
            continue
        # Equity compensation, employment separation and underwriting boilerplate
        # are not evidence of a corporate separation transaction.
        if re.search(r'separation from service|severance|stock split.{0,180}(?:recapitalization|reclassification)|annual award limits|adjustment.{0,100}outstanding award|distribution of (?:the )?offered securities|renesas base distribution|non-binding.*compensation proposal', s, re.I):
            continue
        spin = re.search(r'spin[- ]?off|split[- ]?off|separation|分拆|分派|分立|\bDistribution\b', s)
        spin = spin or re.search(r'spin[- ]?off|split[- ]?off|separation|distribution of.{0,90}shares', s, re.I)
        if not spin:
            continue
        uncertain = re.search(r'\b(?:not|no|never|expect\w*|anticipat\w*|intend\w*|would|could|might|will|subject to|if|upon|until|prior to|before)\b|\bmay\s+(?:be|not|have|result|occur)\b|預計|预计|將|将|尚未|未完成|未開始|未开始|未上市|待|倘|如獲|如获|若|假如|一旦|計劃|计划|擬(?:於|完成|上市)|拟(?:于|完成|上市)', s, re.I)
        status = None
        if re.search(r'決定(?:於現階段)?不進行(?:建議)?分拆|决定(?:于现阶段)?不进行(?:建议)?分拆|(?:已|決定|决定)(?:暫緩|暂缓|暫停|暂停).{0,12}分拆', s):
            status = 'paused'
        if not uncertain:
            if re.search(r'(?:has|have|had)\s+(?:terminated|cancelled|canceled|abandoned)\s+(?:the\s+|its\s+)?(?:proposed\s+)?(?:spin[- ]?off|separation)|(?:spin[- ]?off|separation).{0,60}(?:has been|was|is|had been)\s+(?:terminated|cancelled|canceled|abandoned)|(?:終止|终止|取消)(?:建議|建议)?分拆|分拆.*(?:已終止|已终止)', s, re.I):
                status = 'terminated'
            elif re.search(r'(?:has|have|had|successfully)\s+(?:been\s+)?completed\s+(?:the\s+|its\s+)?(?:spin[- ]?off|separation|distribution)|(?:spin[- ]?off|separation|distribution)\s+(?:(?:of|to)\s+[^,;]{1,60}\s+)?(?:has been|was|is|had been)\s+(?:successfully\s+)?completed|(?:分拆|分派).{0,12}(?:已完成|已生效)|已完成.{0,12}(?:分拆|分派)|(?:分拆|分派).{0,80}(?:已開始買賣|已开始买卖)|分拆.{0,160}(?:上市及[^。；]{0,45}開始買賣|上市及[^。；]{0,45}开始买卖)|分拆公司.{0,90}開始於聯交所主板買賣', s, re.I):
                status = 'completed'
            elif re.search(r'(?:has|have)\s+approved\s+(?:the\s+)?(?:proposed\s+)?spin[- ]?off|(?:分拆).{0,30}(?:獲.{0,8}批准|获.{0,8}批准)|(?:spin[- ]?off).{0,30}(?:has been|was) approved', s, re.I):
                status = 'approved'
        if status is None and not uncertain and re.search(r'完成(?:建議|建议)?分拆', s):
            status = 'completed'
        if status is None and re.search(r'(?:has|have)\s+(?:set|fixed|established|declared|approved).{0,40}record date|(?:記錄日期|记录日期|記錄日|记录日)(?:為|为|定於|定于)|(?:訂定|订定|確定|确定).{0,20}(?:記錄日期|记录日期)', s, re.I) and extract_dates(s).get('recordDate'):
            if not re.search(r'not (?:set|fixed)|proposed record date|尚未|擬定|拟定|預計|预计', s, re.I):
                status = 'record_set'
        if status is None and not uncertain and re.search(r'招股章程|招股書|招股书|prospectus', s, re.I):
            status = 'prospectus'
        if status is None and re.search(r'plan\w*|propos\w*|intend\w*|expect\w*|建議|建议|擬|拟', s, re.I):
            status = 'announced'
        if status:
            candidates.append((status, s))
    for status in ('terminated', 'paused', 'completed', 'record_set', 'approved', 'prospectus', 'announced'):
        match = next((s for st, s in candidates if st == status), None)
        if match:
            return {'status': status, 'quote': match}
    return {'status': 'needs_review', 'quote': ''}


def extract_dates(text):
    text = html.unescape(text or '').replace('\u00a0', ' ')
    result = {}
    text = filing_text(text)
    token = r'(?:[A-Z][a-z]+ \d{1,2},? \d{4}|\d{4}-\d{2}-\d{2}|20\d{2}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日|[二零〇一三四五六七八九]{4}年[一二三四五六七八九十]{1,3}月[一二三四五六七八九十]{1,3}日)'
    for field, label in [('recordDate', r'record date|記錄日期|记录日期|記錄日|记录日'), ('distributionDate', r'distribution date|分派日期|分派日')]:
        matches = list(re.finditer(r'(?:' + label + r')[^.;。；\n]{0,65}?(' + token + ')', text, re.I))
        reverse = list(re.finditer('(' + token + r')[^.;。；\n]{0,35}?(?:' + label + ')', text, re.I))
        matches += reverse
        dates = {iso_date(m.group(1)) for m in matches} - {''}
        if len(dates) == 1:
            result[field] = {'date': dates.pop(), 'quote': matches[0].group(0), 'kind': 'scheduled'}
    return result


def parse_evidence(text, ann, cik=''):
    text = filing_text(text)
    url = source_url(ann, cik)
    match = infer_status(text)
    if match['status'] == 'needs_review':
        match = infer_status(ann.get('title', ''))
    identity = resolve_identity(text, ann.get('title', ''))
    target_name = identity['name'] or (extract_name(text) if identity.get('reason') != 'conflicting_names' else '')
    if target_name and not identity.get('quote'):
        start = text.find(target_name)
        identity['quote'] = text[max(0, start - 100):start + len(target_name) + 150] if start >= 0 else ann.get('title', '')
        identity['kind'] = 'entity'
    target_aliases = re.findall(re.escape(target_name) + r'（(?:以下简称|以下簡稱)?[「“"]([^」”"]{2,40})[」”"]', text) if target_name else []
    target_aliases = list(dict.fromkeys([*target_aliases, *identity.get('aliases', [])]))
    dates = extract_dates(text)
    if match['status'] == 'record_set':
        dates.update(extract_dates(match['quote']))
    ticker = ''
    if target_name and urlparse(url).hostname in {'www1.hkexnews.hk', 'www.hkexnews.hk'}:
        aliases = re.findall(re.escape(target_name) + r'（「([^」]{2,30})」）', text)
        subject = '(?:' + '|'.join(re.escape(n) for n in [target_name, '分拆公司', *aliases]) + ')'
        # Bind the code to the child, not the parent's code in the letterhead.
        codes = set(re.findall(subject + r'[^。\n]{0,100}?股份代號(?:為|：|:)\s*(\d{1,5})(?!\d)', text))
        if len(codes) == 1:
            ticker = codes.pop().zfill(5) + '.HK'
        if match['status'] == 'completed':
            token = r'(?:20\d{2}年\d{1,2}月\d{1,2}日|[二零〇一三四五六七八九]{4}年[一二三四五六七八九十]{1,3}月[一二三四五六七八九十]{1,3}日)'
            found = list(re.finditer(subject + r'於(' + token + r')在(?:香港)?聯交所主板上市', text))
            values = {iso_date(m.group(1)) for m in found} - {''}
            if len(values) == 1:
                dates['listingDate'] = {'date': values.pop(), 'quote': found[0].group(0), 'kind': 'actual'}
    type_quote = introduction_quote(text) if urlparse(url).hostname in {'www1.hkexnews.hk', 'www.hkexnews.hk'} else ''
    type_fields = {'typeVersion': TYPE_RULE_VERSION}
    if type_quote and identity.get('reason') != 'conflicting_names':
        type_fields.update(listingType=classify_hk_type([ann.get('title', ''), type_quote]), typeQuote=type_quote)
    return {**match, **type_fields, 'url': url, 'date': iso_date(ann.get('date')), 'targetName': target_name,
            'targetTicker': ticker, 'targetAliases': target_aliases,
            'identityVersion': IDENTITY_VERSION, 'identityQuote': identity.get('quote', ''),
            'identityKind': identity.get('kind', ''), 'distributedEntity': identity.get('distributedEntity', False), 'separatedEntity': identity.get('separatedEntity', False), 'identityReason': identity.get('reason', ''), 'dates': dates, 'method': 'rule', 'ruleVersion': RULE_VERSION, 'accession': ann.get('adsh', '')}


def normalize(data, market, previous=None, now=None):
    now = now or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    old_events = {e['id']: e for e in (previous or data).get('events', [])}
    initialized = bool((previous or data).get('eventsSchemaVersion'))
    changes = list((previous or data).get('changes', []))
    events = []
    for c in data.get('companies', []):
        parent = str(c.get('stockCode') if market == 'hk' else c.get('ticker'))
        announcements = []
        for ann in c.get('announcements', []):
            url = source_url(ann, c.get('cik', ''))
            # Legacy generic Item labels are not evidence that a filing concerns a spin-off.
            relevant = market == 'hk' or bool(ann.get('adsh')) or not re.search(r'公告（|签订.*（|交割完成.*（|变动.*（', ann.get('title', ''))
            announcements.append({**ann, 'url': url, 'direct': direct_source(url), 'relevance': 'candidate' if relevant else 'unverified'})
        announcements.sort(key=lambda a: a.get('date', ''), reverse=True)
        proofs = [{**p, 'quote': html.unescape(p.get('quote', ''))} for p in c.get('filingEvidence') or []]
        for proof in proofs:
            if proof.get('method') == 'rule' and proof.get('ruleVersion', 0) < RULE_VERSION:
                # Revalidate legacy status quotes when rules change. Missing full
                # text must never preserve a known boilerplate false positive.
                proof.update(infer_status(proof.get('quote', '')), ruleVersion=RULE_VERSION)
        parsed_urls = {p.get('url') for p in proofs}
        parsed_ids = {p.get('accession') for p in proofs if p.get('accession')}
        proofs += [parse_evidence(a.get('title', ''), a, c.get('cik', '')) for a in announcements
                   if a['direct'] and a['relevance'] == 'candidate' and a['url'] not in parsed_urls and a.get('adsh') not in parsed_ids]
        # Separate explicit legal entities; unresolved material is kept in its own dossier.
        groups = {}
        aliases = {}
        for proof in proofs:
            canonical = target_key(clean_name(proof.get('targetName')))
            if canonical:
                for alias in proof.get('targetAliases', []):
                    aliases.setdefault(target_key(alias), set()).add(canonical)
        def group_key(name):
            key = target_key(clean_name(name))
            return next(iter(aliases[key])) if len(aliases.get(key, [])) == 1 else key
        for proof in proofs:
            name = clean_name(proof.get('targetName'))
            groups.setdefault(group_key(name), []).append(proof)
        if not groups:
            groups[''] = []
        for key, group in groups.items():
            named = next((clean_name(p.get('targetName')) for p in group if clean_name(p.get('targetName'))), '')
            candidate_name = clean_name(c.get('spinTarget') or c.get('spinoffName'))
            parent_key = entity_key(c.get('stockName') or c.get('name'))
            if candidate_name and entity_key(candidate_name) == parent_key:
                candidate_name = ''
            if named and entity_key(named) == parent_key and not any(p.get('distributedEntity') or p.get('separatedEntity') for p in group):
                named = ''
            target_name = named or (candidate_name if len(groups) == 1 and not any(p.get('identityReason') == 'conflicting_names' for p in group) else '')
            identity_proofs = [p for p in group if named and p.get('identityQuote') and direct_source(p.get('url', ''))]
            identity_proof = max(identity_proofs, key=lambda p: p.get('date', ''), default=None)
            eid = f'{market}:{parent}:' + (hashlib.sha256(key.encode()).hexdigest()[:12] if key else 'unresolved')
            # Preserve local watch/note identity as an unresolved dossier gains a name.
            prior = [e for e in old_events.values() if e.get('market') == market and e.get('parentTicker') == (c.get('ticker') or parent)]
            matching = [e for e in prior if named and group_key(e.get('targetName', '')) == key]
            group_urls = {p.get('url') for p in group}
            # One filing may describe several targets. Only transfer a prior ID
            # by URL when that source belongs to one group, and never take an ID
            # away from another group whose target name still matches it.
            source_matching = [e for e in prior
                if (e.get('evidence') or {}).get('url') in group_urls
                and (group_key(e.get('targetName', '')) not in groups
                     or group_key(e.get('targetName', '')) == key)
                and sum(any(p.get('url') == (e.get('evidence') or {}).get('url')
                            for p in ps) for ps in groups.values()) == 1]
            if not matching and len(source_matching) == 1:
                matching = source_matching
            if len(matching) == 1:
                eid = matching[0]['id']
            elif len(groups) == 1 and len(prior) == 1 and prior[0]['id'].endswith(':unresolved') and not prior[0].get('targetName'):
                eid = prior[0]['id']
            elif not key and len(groups) > 1 and (old_events.get(eid, {}).get('targetName') or any(p.get('url') == (old_events.get(eid, {}).get('evidence') or {}).get('url') for k, ps in groups.items() if k for p in ps)):
                eid = f'{market}:{parent}:unattributed'
            valid = [p for p in group if direct_source(p.get('url', '')) and p.get('quote') and p.get('status') in STATUSES - {'needs_review'}]
            valid.sort(key=lambda p: p.get('date', ''), reverse=True)
            # Later prospectus references must not undo an evidenced completion.
            terminal = [p for p in valid if p['status'] in {'completed', 'terminated'}]
            completed = [p for p in terminal if p['status'] == 'completed']
            # Completion cannot regress to a prospectus reference. A terminated
            # proposal may, however, be explicitly restarted by a later filing.
            evidence = terminal[0] if completed else valid[0] if valid else None
            if evidence and evidence['status'] not in {'completed', 'terminated', 'paused'}:
                cutoff = max((p.get('date', '') for p in valid if p['status'] in {'terminated', 'paused'}), default='')
                ranks = {'announced': 1, 'approved': 2, 'prospectus': 3, 'record_set': 4}
                progress = [p for p in valid if p.get('date', '') >= cutoff and p['status'] in ranks]
                if progress:
                    evidence = max(progress, key=lambda p: (ranks[p['status']], p.get('date', '')))
            status = evidence['status'] if evidence else 'needs_review'
            date_fields = {}
            for p in sorted(group, key=lambda p: p.get('date', '')):
                if direct_source(p.get('url', '')):
                    for key, value in p.get('dates', {}).items():
                        if iso_date(value.get('date')):
                            date_fields[key] = {**value, 'url': p['url'], 'sourceDate': p.get('date', '')}
            # Do not attach legacy tickers/prices to a different parsed target.
            same_target = len(groups) == 1 and (not named or candidate_name.casefold() == named.casefold())
            child_ticker = (c.get('spinoffTicker') or '') if same_target else ''
            verified_tickers = {p['targetTicker'] for p in group if p.get('targetTicker') and direct_source(p.get('url', ''))}
            if len(verified_tickers) == 1:
                child_ticker = verified_tickers.pop()
            if child_ticker in ('TBD', 'N/A'):
                child_ticker = ''
            missing = [key for key, ok in [('target', target_name), ('ticker', child_ticker), ('evidence', evidence), ('recordDate', date_fields.get('recordDate')), ('distributionDate', date_fields.get('distributionDate'))] if not ok]
            event_announcements = announcements
            if len(groups) > 1:
                accessions = {p.get('accession') for p in group if p.get('accession')}
                urls = {p.get('url') for p in group if p.get('url')}
                event_announcements = [{**a, 'relevance': a['relevance'] if a.get('adsh') in accessions or a.get('url') in urls else 'unverified'} for a in announcements]
            relevant_dates = [a.get('date', '') for a in event_announcements if a['relevance'] == 'candidate']
            type_evidence = None
            event_type = c.get('spinType') or c.get('type', 'spinoff')
            if market == 'hk':
                scoped_type = classify_hk_type([a.get('title', '') for a in event_announcements if a['relevance'] == 'candidate'])
                if len(groups) > 1 or scoped_type['code'] != 'unknown':
                    event_type = scoped_type
                # Body evidence is scoped to this target, never inherited from a sibling.
                typed = [p for p in group if p.get('listingType') and p.get('typeQuote')
                         and direct_source(p.get('url', ''))]
                if typed:
                    proof = max(typed, key=lambda p: p.get('date', ''))
                    event_type = proof['listingType']
                    type_evidence = {'url': proof['url'], 'date': proof.get('date', ''), 'quote': proof['typeQuote']}
            merged_ids = {alias for e in [*matching, *source_matching, *([old_events[eid]] if eid in old_events else [])] for alias in [e['id'], *e.get('mergedIds', [])]} - {eid}
            event = {'id': eid, 'mergedIds': sorted(merged_ids), 'market': market, 'parentTicker': c.get('ticker') or parent, 'parentName': c.get('stockName') or c.get('name', ''),
                     'targetName': target_name, 'targetTicker': child_ticker, 'identityVerified': bool(named),
                     'identityKind': identity_proof.get('identityKind', 'entity') if identity_proof else '',
                     'identityEvidence': {'url': identity_proof.get('identitySourceUrl') or identity_proof['url'], 'date': identity_proof.get('identitySourceDate') or identity_proof.get('date', ''), 'quote': identity_proof['identityQuote']} if identity_proof else None,
                     'identityState': 'resolved' if named else 'legacy' if target_name else 'conflicting_names' if any(p.get('identityReason') == 'conflicting_names' for p in group) else 'missing_name' if evidence else 'unconfirmed_event',
                     'status': status, 'evidence': evidence, 'dates': date_fields, 'missing': missing,
                     'type': event_type, 'announcements': event_announcements,
                     'latestDate': max(relevant_dates, default=''), 'sourceUpdatedAt': data.get('updatedAt', ''),
                     'parentMarketCap': c.get('parentMarketCap'), 'pricePairs': c.get('spinoffPricePerf', []) if same_target else [],
                     'parentPrice': c.get('parentPricePerf') or c.get('pricePerf') or {}}
            if type_evidence:
                event['typeEvidence'] = type_evidence
            old = old_events.get(eid)
            def snapshot(value):
                result = {k: value.get(k) for k in ('status', 'targetName', 'targetTicker')}
                result['dates'] = {k: v['date'] for k, v in value.get('dates', {}).items()}
                return result
            semantic = snapshot(event)
            old_semantic = snapshot(old) if old else {}
            fingerprint = hashlib.sha256(json.dumps(semantic, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            event['fingerprint'] = fingerprint
            event['firstSeenAt'] = old.get('firstSeenAt', now) if old else now
            event['changedAt'] = old.get('changedAt', now) if old and old.get('fingerprint') == fingerprint else now
            if initialized and (not old or old.get('fingerprint') != fingerprint):
                fields = [k for k in semantic if not old or old_semantic.get(k) != semantic[k]]
                if fields or not old:
                    changes.append({'eventId': eid, 'at': now, 'kind': 'updated' if old else 'new',
                                    'parentTicker': event['parentTicker'], 'parentName': event['parentName'],
                                    'fields': fields, 'before': old_semantic if old else None, 'after': semantic,
                                    'fromStatus': old.get('status') if old else None, 'toStatus': status})
            events.append(event)
    live_ids = {e['id'] for e in events}
    for event in events:
        event['mergedIds'] = [key for key in event['mergedIds'] if key not in live_ids]
    data.update(events=events, eventsSchemaVersion=1, eventsNormalizedAt=now, changes=changes[-300:],
                trackingStartedAt=(previous or data).get('trackingStartedAt', now))
    return data


def validate_events(data):
    if 'eventsSchemaVersion' not in data:
        return  # Legacy data remains readable during rollout.
    ids = set()
    for event in data.get('events', []):
        if event['id'] in ids or event.get('status') not in STATUSES:
            raise ValueError('Duplicate event identity or invalid spin-off status')
        ids.add(event['id'])
        if event['status'] != 'needs_review':
            ev = event.get('evidence') or {}
            if not ev.get('quote') or not direct_source(source_url(ev)) or ev.get('status') != event['status']:
                raise ValueError('Spin-off status requires matching direct-source evidence')
        identity = event.get('identityEvidence')
        if identity and (not event.get('targetName') or not identity.get('quote') or not direct_source(source_url(identity))):
            raise ValueError('Target identity requires a name, quote and direct source')
        for value in event.get('dates', {}).values():
            if not iso_date(value.get('date')) or not direct_source(source_url(value)):
                raise ValueError('Invalid milestone evidence')


def main():
    for market, filename in [('hk', 'spinoff.json'), ('us', 'spinoff_us.json')]:
        path = Path(filename)
        data = normalize(json.loads(path.read_text()), market)
        validate_events(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        print(f'{market}: {len(data["events"])} dossiers; {sum(e["status"] == "needs_review" for e in data["events"])} need evidence review')


if __name__ == '__main__':
    main()
