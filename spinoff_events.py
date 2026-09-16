"""Evidence-backed spin-off dossiers. No AI or network required to normalize data."""
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

STATUSES = {'needs_review', 'announced', 'approved', 'record_set', 'prospectus', 'completed', 'terminated'}


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
    for fmt in ('%Y-%m-%d', '%B %d, %Y', '%b %d, %Y', '%B %d %Y', '%b %d %Y', '%Y年%m月%d日'):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return ''


def clean_name(value):
    name = re.sub(r'\s+', ' ', str(value or '')).strip(' .,')
    name = re.sub(r'^(?:所屬子公司|所属子公司)', '', name)
    name = re.sub(r'(有限公司)及$', r'\1', name)
    if (not 2 <= len(name) <= 90 or name.lower() in {'tbd', 'spinco', 'newco', '(解析中)', '子公司', '附屬公司'}
            or re.search(r'\b(?:will|would|shall|entitlement|shares|common stock|receive|expects|from|including|owned)\b|建議分拆及|建议分拆及|公司的建議|交易所|董事會|董事会|股票價格|股票价格|分拆|獨立上市|独立上市|上市董事|本集團|本集团|並於|并于', name, re.I)):
        return ''
    return name


def entity_key(value):
    value = re.sub(r'\([^)]*\)', '', str(value or ''))
    return re.sub(r'[^a-z0-9\u4e00-\u9fff]', '', re.sub(r'\b(?:inc|corp|corporation|co|ltd|llc)\b', '', value.lower()))


def extract_name(text):
    # Bounded, capitalized legal names; never consume an entire prose sentence.
    patterns = [
        r'(?:spin[- ]off|separation) of ([A-Z][\w&.-]*(?: [A-Z][\w&.-]*){0,7}(?:,? (?:Inc\.?|Corporation|Corp\.?|LLC|Ltd\.?|Holdings|Group)))',
        r'distribut\w*\s+(?:all (?:of )?(?:the )?)?(?:outstanding )?shares of ([A-Z][\w&.-]*(?: [A-Z][\w&.-]*){0,6}(?:,? (?:Inc\.?|Corporation|Corp\.?|LLC|Ltd\.?)))',
    ]
    patterns.append(r'(?:建議分拆|建议分拆|分拆)(?:(?:其|本公司|所屬|所属|附屬|附属|子公司|非全資|非全资)\s*)*([\u4e00-\u9fffA-Za-z（）()]{2,45}?(?:股份有限公司|有限公司))')
    names = {clean_name(m.group(1)) for p in patterns for m in re.finditer(p, text)} - {''}
    return next(iter(names)) if len(names) == 1 else ''


def infer_status(text):
    """Return a rule match and its exact sentence, never infer completion from a date."""
    text = html.unescape(text or '')
    sentences = re.split(r'(?<=[.!?。；;])\s+|[\n。；]', re.sub(r'[ \t]+', ' ', text or ''))
    candidates = []
    for sentence in sentences:
        s = sentence.strip()
        if not s or len(s) > 1200:
            continue
        spin = re.search(r'spin[- ]?off|separat|distribution|分拆|分派|分拆上市', s, re.I)
        if not spin:
            continue
        uncertain = re.search(r'\b(?:not|no|never|expect\w*|anticipat\w*|intend\w*|would|could|may|might|will|subject to|if|upon|until|prior to|before)\b|預計|预计|將|将|尚未|未完成|待|倘|如獲|如获|計劃|计划', s, re.I)
        status = None
        if not uncertain:
            if re.search(r'(?:has|have|was|is|had)\s+(?:been\s+)?(?:terminated|cancelled|canceled|abandoned)|(?:terminated|cancelled|canceled|abandoned)\s+(?:the\s+)?(?:proposed\s+)?spin[- ]?off|(?:終止|终止|取消)(?:建議|建议)?分拆|分拆.*(?:已終止|已终止)', s, re.I):
                status = 'terminated'
            elif re.search(r'(?:has|have|had|successfully)\s+(?:been\s+)?completed\s+(?:the\s+|its\s+)?(?:spin[- ]?off|separation|distribution)|(?:spin[- ]?off|separation|distribution)\s+(?:(?:of|to)\s+[^,;]{1,60}\s+)?(?:has been|was|is|had been)\s+(?:successfully\s+)?completed|(?:分拆|分派).{0,12}(?:已完成|已生效)|已完成.{0,12}(?:分拆|分派)|(?:分拆|分派).{0,80}(?:已開始買賣|已开始买卖)', s, re.I):
                status = 'completed'
            elif re.search(r'(?:has|have)\s+approved\s+(?:the\s+)?(?:proposed\s+)?spin[- ]?off|(?:分拆).{0,30}(?:獲.{0,8}批准|获.{0,8}批准)|(?:spin[- ]?off).{0,30}(?:has been|was) approved', s, re.I):
                status = 'approved'
        if status is None and re.search(r'招股章程|招股書|招股书|prospectus', s, re.I):
            status = 'prospectus'
        if status is None and re.search(r'plan\w*|propos\w*|intend\w*|expect\w*|建議|建议|擬|拟', s, re.I):
            status = 'announced'
        if status:
            candidates.append((status, s))
    for status in ('terminated', 'completed', 'approved', 'prospectus', 'announced'):
        match = next((s for st, s in candidates if st == status), None)
        if match:
            return {'status': status, 'quote': match}
    return {'status': 'needs_review', 'quote': ''}


def extract_dates(text):
    text = html.unescape(text or '').replace('\u00a0', ' ')
    result = {}
    token = r'(?:[A-Z][a-z]+ \d{1,2},? \d{4}|\d{4}-\d{2}-\d{2}|20\d{2}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)'
    for field, label in [('recordDate', r'record date|記錄日期|记录日期|記錄日|记录日'), ('distributionDate', r'distribution date|分派日期|分派日')]:
        matches = list(re.finditer(r'(?:' + label + r')[^.;。；\n]{0,65}?(' + token + ')', text, re.I))
        dates = {iso_date(m.group(1)) for m in matches} - {''}
        if len(dates) == 1:
            result[field] = {'date': dates.pop(), 'quote': matches[0].group(0), 'kind': 'scheduled'}
    return result


def parse_evidence(text, ann, cik=''):
    text = html.unescape(text or '')
    url = source_url(ann, cik)
    match = infer_status(text)
    return {**match, 'url': url, 'date': iso_date(ann.get('date')), 'targetName': extract_name(text),
            'dates': extract_dates(text), 'method': 'rule', 'accession': ann.get('adsh', '')}


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
        parsed_urls = {p.get('url') for p in proofs}
        parsed_ids = {p.get('accession') for p in proofs if p.get('accession')}
        proofs += [parse_evidence(a.get('title', ''), a, c.get('cik', '')) for a in announcements
                   if a['direct'] and a['relevance'] == 'candidate' and a['url'] not in parsed_urls and a.get('adsh') not in parsed_ids]
        # Separate explicit legal entities; unresolved material is kept in its own dossier.
        groups = {}
        for proof in proofs:
            name = clean_name(proof.get('targetName'))
            groups.setdefault(name.casefold(), []).append(proof)
        if not groups:
            groups[''] = []
        for target_key, group in groups.items():
            named = next((clean_name(p.get('targetName')) for p in group if clean_name(p.get('targetName'))), '')
            candidate_name = clean_name(c.get('spinTarget') or c.get('spinoffName'))
            parent_key = entity_key(c.get('stockName') or c.get('name'))
            if candidate_name and entity_key(candidate_name) == parent_key:
                candidate_name = ''
            if named and entity_key(named) == parent_key:
                named = ''
            target_name = named or (candidate_name if len(groups) == 1 else '')
            eid = f'{market}:{parent}:' + (hashlib.sha256(target_key.encode()).hexdigest()[:12] if target_key else 'unresolved')
            # Preserve local watch/note identity as an unresolved dossier gains a name.
            prior = [e for e in old_events.values() if e.get('market') == market and e.get('parentTicker') == (c.get('ticker') or parent)]
            matching = [e for e in prior if named and e.get('targetName', '').casefold() == named.casefold()
                        and (len(groups) == 1 or not e['id'].endswith(':unresolved'))]
            if len(matching) == 1:
                eid = matching[0]['id']
            elif len(groups) == 1 and len(prior) == 1 and prior[0]['id'].endswith(':unresolved'):
                eid = prior[0]['id']
            valid = [p for p in group if direct_source(p.get('url', '')) and p.get('quote') and p.get('status') in STATUSES - {'needs_review'}]
            valid.sort(key=lambda p: p.get('date', ''), reverse=True)
            evidence = valid[0] if valid else None
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
            if child_ticker in ('TBD', 'N/A'):
                child_ticker = ''
            missing = [key for key, ok in [('target', target_name), ('ticker', child_ticker), ('evidence', evidence), ('recordDate', date_fields.get('recordDate')), ('distributionDate', date_fields.get('distributionDate'))] if not ok]
            event_announcements = announcements
            if len(groups) > 1:
                accessions = {p.get('accession') for p in group if p.get('accession')}
                urls = {p.get('url') for p in group if p.get('url')}
                event_announcements = [{**a, 'relevance': a['relevance'] if a.get('adsh') in accessions or a.get('url') in urls else 'unverified'} for a in announcements]
            relevant_dates = [a.get('date', '') for a in event_announcements if a['relevance'] == 'candidate']
            event = {'id': eid, 'market': market, 'parentTicker': c.get('ticker') or parent, 'parentName': c.get('stockName') or c.get('name', ''),
                     'targetName': target_name, 'targetTicker': child_ticker, 'identityVerified': bool(named),
                     'status': status, 'evidence': evidence, 'dates': date_fields, 'missing': missing,
                     'type': c.get('spinType') or c.get('type', 'spinoff'), 'announcements': event_announcements,
                     'latestDate': max(relevant_dates, default=''), 'sourceUpdatedAt': data.get('updatedAt', ''),
                     'parentMarketCap': c.get('parentMarketCap'), 'pricePairs': c.get('spinoffPricePerf', []) if same_target else [],
                     'parentPrice': c.get('parentPricePerf') or c.get('pricePerf') or {}}
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
