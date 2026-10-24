"""Discover original documents and accept verified, permitted verbatim texts.

Third-party source text is ephemeral and is never committed or republished.
No full-text translation is produced without an explicit republication licence.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import re
import signal
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
import unicodedata
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path
from collections import Counter
import archive_budget as budget

ROOT = Path(__file__).resolve().parent
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PublicInvestorArchive/1.0)"}
MAX_BYTES = 18 * 1024 * 1024
MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], 1)}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def canonical(url):
    u = urllib.parse.urlsplit(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise ValueError("Only public HTTPS source links are accepted")
    host = u.hostname.lower().removeprefix("www.")
    if host in {"youtube.com", "m.youtube.com", "youtu.be"}:
        video = u.path.strip("/") if host == "youtu.be" else urllib.parse.parse_qs(u.query).get("v", [""])[0]
        if re.fullmatch(r"[\w-]{11}", video):
            return "https://www.youtube.com/watch?v=" + video
    query = urllib.parse.parse_qsl(u.query, keep_blank_values=True)
    query = [(k, v) for k, v in query if not k.lower().startswith("utm_") and k not in {"fbclid", "gclid"}]
    return urllib.parse.urlunsplit(("https", host, u.path.rstrip("/") or "/", urllib.parse.urlencode(query), ""))


def fetch(url):
    budget.check()
    if not url.startswith("https://"):
        raise ValueError("HTTPS required")
    candidates = [url]
    if urllib.parse.urlsplit(url).hostname == "cdn.prod.website-files.com":
        candidates.append(url.replace("cdn.prod.website-files.com", "cdn.website-files.com"))
    last_error = None
    for candidate in candidates:
        try:
            req = urllib.request.Request(candidate, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=budget.timeout(25)) as r:
                raw = r.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise ValueError("Source exceeds size limit")
                if not raw or r.status != 200:
                    raise ValueError("Empty or incomplete source response")
                return raw, r.headers.get("Content-Type", "")
        except Exception as exc:
            last_error = exc
    raise last_error


def soup(raw):
    from bs4 import BeautifulSoup
    return BeautifulSoup(raw, "html.parser")


def extract_text(raw, content_type=""):
    if "pdf" in content_type.lower() or raw.startswith(b"%PDF"):
        import fitz
        doc = fitz.open(stream=raw, filetype="pdf")
        if len(doc) > 400:
            raise ValueError("PDF page limit exceeded")
        return "\n".join(page.get_text() for page in doc)
    tree = soup(raw)
    for el in tree(["script", "style", "nav", "header", "footer", "form"]):
        el.decompose()
    body = tree.select_one("article, #artibody, #contentText, .entry-content, .post-content, main") or tree
    return body.get_text("\n", strip=True)


def event_date(title):
    """Never turn filename publication dates into event dates."""
    m = re.search(r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2})(?:st|nd|rd|th)?[,]?\s+(20\d{2}|19\d{2})\b", title, re.I)
    if m:
        try:
            return dt.date(int(m[3]), MONTHS[m[1].lower()], int(m[2])).isoformat()
        except ValueError:
            return None
    m = re.search(r"\b(" + "|".join(MONTHS) + r")\s+(20\d{2}|19\d{2})\b", title, re.I)
    if m:
        return f"{m[2]}-{MONTHS[m[1].lower()]:02d}"
    m = re.search(r"\b(?:19|20)\d{2}\b", title)
    return m[0] if m else None


def inferred_kind(title):
    t = title.lower()
    if any(s in t for s in ["q&a", "annual meeting", "annual gathering", "问答", "见面会"]):
        return "qa"
    if any(s in t for s in ["letter", "foreword", "remembering", "postcard", "序言", "文章"]):
        return "essay"
    if any(s in t for s in ["lecture", "speech", "mental models", "演讲"]):
        return "speech"
    return "interview"


def event_key(w):
    # Titles are essential: a person can have several different events per day.
    title = w["title"]["en"].lower()
    title = re.sub(r"\btranscript\b|\bmohnish pabrai[’']?s?\b|\bli lu[’']?s?\b", "", title)
    title = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", title).strip()
    return w["investor"], w.get("date") or "", title


def make_work(investor, title, url, publisher, source_page=None, date=None, kind=None, zh=None, date_kind="event"):
    canonical_url = canonical(url)
    url = url.replace("http://", "https://", 1)
    ident = hashlib.sha256((investor + "|" + canonical_url).encode()).hexdigest()[:14]
    if not zh:
        names = {p["id"]: p["name"] for p in read(ROOT / "investors.json")["investors"]}
        label = {"speech": "演讲", "interview": "访谈", "qa": "公开问答", "essay": "文章与序言"}[kind or inferred_kind(title)]
        zh = f"{names.get(investor, investor)} · {publisher} · {label}"
        if date or event_date(title):
            zh += f"（{date or event_date(title)}）"
    work = {"id": investor + "-" + ident, "investor": investor,
            "title": {"zh": zh, "en": title.removesuffix(" Transcript")},
            "date": date or event_date(title), "dateKind": date_kind,
            "kind": kind or inferred_kind(title), "publisher": publisher,
            "sourceLevel": "primary", "sources": [{"url": url,
                "label": {"zh": "原始作品", "en": "Original work"}}],
            "textStatus": "not_obtained", "checkedAt": now()[:10], "topics": [], "media": []}
    if source_page and canonical(source_page) != url:
        work["sources"].append({"url": source_page.replace("http://", "https://", 1), "label": {"zh": "发布方目录", "en": "Publisher catalogue"}})
    if "youtube.com/watch?v=" in url:
        work["media"].append({"kind": "youtube", "id": urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)["v"][0]})
    return work


def merge_works(existing, incoming):
    """Union sources without replacing an existing note, verified date or title."""
    merged = {w["id"]: dict(w) for w in existing}
    def indices():
        urls, events = {}, {}
        for w in merged.values():
            events[event_key(w)] = w["id"]
            for s in w["sources"]:
                urls[(w["investor"], canonical(s["url"]))] = w["id"]
        return urls, events
    for new in incoming:
        urls, events = indices()
        target = next((urls[(new["investor"], canonical(s["url"]))] for s in new["sources"][:1]
                       if (new["investor"], canonical(s["url"])) in urls), None)
        target = target or events.get(event_key(new))
        if target:
            old = merged[target]
            known = {canonical(s["url"]) for s in old["sources"]}
            # Index pages are not identity keys; distinct works share one index.
            for src in new["sources"]:
                if canonical(src["url"]) not in known:
                    old["sources"].append(src)
                    known.add(canonical(src["url"]))
            known_media = {json.dumps(m, sort_keys=True) for m in old.get("media", [])}
            old.setdefault("media", []).extend(m for m in new.get("media", []) if json.dumps(m, sort_keys=True) not in known_media)
            old["checkedAt"] = new["checkedAt"]
        else:
            merged[new["id"]] = new
    for work in merged.values():
        work['media']=[m for m in work.get('media',[]) if not (m.get('kind')=='audio' and re.search(r'\.(?:png|jpe?g|gif|webp|svg|pdf)(?:$|\?)',urllib.parse.unquote(m.get('url','')),re.I))]
    return sorted(merged.values(), key=lambda w: (w.get("date") or "", w["id"]), reverse=True)


def link_catalog(source, get=fetch):
    works, visited, pending = [], set(), [source["url"]]
    while pending:
        url = pending.pop(0)
        if url in visited:
            continue
        visited.add(url)
        if len(visited) > 100:
            raise ValueError("Pagination limit exceeded; partial discoveries retained next run")
        raw, _ = get(url)
        tree = soup(raw)
        for a in tree.select("a[href]"):
            title = a.get_text(" ", strip=True)
            href = urllib.parse.urljoin(url, a["href"])
            if source.get("excludePattern") and re.search(source["excludePattern"], title, re.I):
                continue
            if title.lower() == "next" and urllib.parse.urlsplit(href).netloc == urllib.parse.urlsplit(source["url"]).netloc:
                pending.append(href)
            if source["adapter"] == "pabrai":
                valid = ".pdf" in href.lower() and len(title) > 15
            elif source["adapter"] == "lilu":
                valid = ".pdf" in href.lower() and len(title) > 25 and title.lower() != "view document" and "book list" not in title.lower()
            elif source["adapter"] == "buffett":
                m = re.search(r"/(\d{4})-berkshire-hathaway-annual-meeting/?$", href)
                # The 2026 general meeting was chaired by Greg Abel; don't attribute it to Buffett.
                valid = bool(m and int(m[1]) <= 2025)
                if valid:
                    title = f"{m[1]} Berkshire Hathaway Annual Meeting"
            elif source["adapter"] == "buffett_letters":
                year=title if re.fullmatch(r'\d{4}',title) else ''
                valid=bool(year and int(year)<=2024 and re.search(r'/letters/\d{4}(?:ltr\.pdf|\.html)$',href))
                if valid:
                    works.append(make_work('buffett',f'{year} Letter to Berkshire Shareholders',href,source['publisher'],source['url'],date=year,kind='essay',zh=f'{year} 年致伯克希尔股东信',date_kind='report_year'))
                    continue
            else:
                valid = bool(re.search(source["includePattern"], title, re.I))
            if valid and href.startswith("https://"):
                works.append(make_work(source["investor"], title, href, source["publisher"], source["url"]))
    return works


def primary_author_catalog(source, get=fetch):
    """Publisher catalogues with explicit attribution; never harvest other staff."""
    raw, _ = get(source['url'])
    tree = soup(raw)
    works = []
    if source['adapter'] == 'patient_author':
        for card in tree.select('.article_item'):
            if card.get('data-author', '').strip() not in source['authors']:
                continue
            anchor, heading = card.select_one('a[href]'), card.select_one('.title')
            date = card.select_one('.date')
            if not anchor or not heading:
                continue
            title = heading.get_text(' ', strip=True)
            match = re.search(r'\b(\d{2}/\d{2}/\d{2})\b', date.get_text(' ', strip=True) if date else '')
            published = dt.datetime.strptime(match[1], '%m/%d/%y').strftime('%Y-%m-%d') if match else None
            works.append(make_work(source['investor'], title, urllib.parse.urljoin(source['url'], anchor['href']), source['publisher'], source['url'], date=published,
                                   kind='interview' if re.search(r'CNBC|interview|Bloomberg|podcast', title, re.I) else 'essay', date_kind='published'))
    else:
        for anchor in tree.select('a[href]'):
            title = anchor.get_text(' ', strip=True)
            href = anchor['href']
            if href.startswith('javascript:'):
                # Extract a literal official PDF URL; never execute publisher JS.
                match = re.fullmatch(r"javascript:openPDF\('[^']*','(https://www\.oaktreecapital\.com/docs/default-source/memos/[^'\s]+\.pdf(?:\?[^'\s]*)?)'\)", href)
                if not match:
                    continue
                href = match[1]
            url = urllib.parse.urljoin(source['url'], href)
            host = (urllib.parse.urlsplit(url).hostname or '').removeprefix('www.')
            if host != 'oaktreecapital.com' or not title or title == 'The Complete Collection':
                continue
            if '/insights/memo/' not in url and '/docs/default-source/memos/' not in url:
                continue
            time = anchor.parent.find('time')
            match = re.search(r'\d{4}-\d{2}-\d{2}', time.get('datetime', '')) if time else None
            works.append(make_work(source['investor'], title, url, source['publisher'], source['url'], kind='essay', date=match[0] if match else None, date_kind='published'))
    if not works:
        raise ValueError('Publisher author catalogue changed; retain verified works')
    return merge_works([], works)


def rss_catalog(source, get=fetch):
    raw, _ = get(source["url"])
    feed = ET.fromstring(raw)
    works = []
    for item in feed.findall(".//item"):
        if source.get('authorPattern') and not re.search(source['authorPattern'],item.findtext('{http://purl.org/dc/elements/1.1/}creator',''),re.I):continue
        title, url = item.findtext("title", ""), item.findtext("link", "")
        if source.get("includePattern") and not re.search(source["includePattern"], title, re.I):
            continue
        if source.get("excludePattern") and re.search(source["excludePattern"], title, re.I):
            continue
        if not url.startswith("https://"):
            continue
        date = None
        try:
            date = parsedate_to_datetime(item.findtext("pubDate")).date().isoformat()
        except (TypeError, ValueError):
            pass
        work = make_work(source["investor"], title, url, source["publisher"], source["url"],
                         date=event_date(title) or date, kind=source.get('kind'), date_kind="event" if event_date(title) else "published")
        enclosure = item.find("enclosure")
        if enclosure is not None and enclosure.get("url", "").startswith("https://") and (
            enclosure.get('type','').lower().startswith('audio/') or
            not enclosure.get('type','').lower().startswith(('image/','text/')) and re.search(r'\.(?:mp3|m4a|aac|ogg|opus|wav)(?:$|\?)',enclosure.get('url',''),re.I)):
            work["media"].append({"kind": "audio", "url": enclosure.get("url")})
        works.append(work)
    return works


def spotify_catalog(source, get=fetch):
    """Spotify's public SSR state is a fallback when the original RSS is down."""
    raw, _ = get(source["url"])
    page = soup(raw)
    script = next((s.get_text() for s in page.select("script") if "window.__STATE__ =" in s.get_text()), None)
    if not script:
        raise ValueError("Public podcast catalogue unavailable")
    start = script.index("=", script.index("window.__STATE__")) + 1
    state = json.JSONDecoder().raw_decode(script[start:].lstrip())[0]
    works = []
    for episode in state["episodePreview"]["episodes"]:
        title = episode["title"]
        if re.search(source.get("excludePattern", r"^$"), title, re.I):
            continue
        url = "https://podcasters.spotify.com/pod/show" + episode["shareLinkPath"]
        description = soup(episode.get("description", "")).get_text(" ", strip=True)
        # Historical titles often mention the letter year, not the recording date.
        event = event_date(description) if "annual gathering" in title.lower() or "anniversary" in title.lower() else None
        work = make_work(source["investor"], title, url, source["publisher"], source["url"],
                         date=event or episode["publishOn"][:10], date_kind="event" if event else "published")
        work["basis"] = "publisher_description"
        enclosure = episode.get("episodeEnclosureUrl", "")
        # The enclosure embeds a direct audio URL after /podcast/play/<id>/.
        direct = re.search(r"/podcast/play/\d+/(https[%:]\S+)", enclosure)
        enclosure = urllib.parse.unquote(direct[1]) if direct else enclosure
        if enclosure.startswith("https://"):
            work["media"].append({"kind": "audio", "url": enclosure})
        for a in soup(episode.get("description", "")).select("a[href]"):
            href = a["href"]
            if "youtu" in href:
                video_url = canonical(href)
                match = re.search(r"[?&]v=([\w-]{11})", video_url)
                if match:
                    work["media"].append({"kind": "youtube", "id": match[1]})
                    work["sources"].append({"url": video_url, "label": {"zh": "发布方视频", "en": "Publisher video"}})
        works.append(work)
    return works


def search_catalog(source, get=fetch):
    """Public search discovers leads; original publisher text verifies identity.

    Search snippets are never used to generate study editions. Only configured
    original publishers and clearly titled speeches/interviews are admitted.
    """
    query = source["query"]
    raw, _ = get("https://www.bing.com/search?format=rss&q=" + urllib.parse.quote(query))
    tree = ET.fromstring(raw)
    works = []
    for item in tree.findall(".//item"):
        title, url = item.findtext("title", ""), item.findtext("link", "")
        host = (urllib.parse.urlsplit(url).hostname or "").removeprefix("www.").lower()
        if not any(host == h or host.endswith("." + h) for h in source["publishers"]):
            continue
        if not any(name.lower() in title.lower() for name in source["names"]):
            continue
        if not re.search(r"interview|conversation|speech|lecture|commencement|q&a|访谈|演讲|对谈|专访|见面会|问答", title, re.I):
            continue
        try:
            body, typ = get(url)
            text = extract_text(body, typ)
            if len(text) < 600 or not any(term.lower() in text.lower() for term in source["identityTerms"]):
                continue
            w = make_work(source["investor"], title, url, host)
            # The index/sitemap can be a publication; don't manufacture an event date.
            w["basis"] = "publisher_description"
            w["discoveredBy"] = "public_search_then_original_publisher_identity_check"
            works.append(w)
        except Exception:
            continue
    return works


def verified_document(source,get=fetch):
    """Recheck a researched original, preserving its exact author and page scope."""
    raw,typ=get(source['url']);text=extract_text(raw,typ)
    normalized=re.sub(r'\s+',' ',unicodedata.normalize('NFKC',text)).casefold()
    if len(text)<600 or not any(name.casefold() in normalized for name in source['identityTerms']):raise ValueError('Original author could not be verified')
    work=make_work(source['investor'],source['title']['en'],source['url'],source['publisher'],date=source.get('date'),kind=source.get('kind','essay'),zh=source['title']['zh'],date_kind=source.get('dateKind','published'))
    for key in ['sourceScope','sourcePageRange','media','basis','participants']:
        if source.get(key):work[key]=source[key]
    return [work]


def source_chunks(text):
    """Rejoin PDF line wraps and remove repeated running headers/footers.

    Sampling isolated printed lines loses reasoning and overweights repeated
    disclaimers. Coherent passages remain bounded and span the whole source.
    """
    lines = [re.sub(r"[ \t]+", " ", unicodedata.normalize("NFKC", line)).strip()
             for line in text.splitlines()]
    bounded=[]
    for line in lines:
        # Some publishers put an entire article in one HTML text node.
        # Bound that node before grouping; otherwise a single source passage
        # can silently consume the model's complete context window.
        while len(line)>1500:
            stops=list(re.finditer(r'[.!?。！？]["’”\']?(?:\s|$)',line[:1450]))
            end=stops[-1].end() if stops and stops[-1].end()>=700 else line.rfind(' ',0,1450)
            if end<700:end=1400
            bounded.append(line[:end].strip());line=line[end:].strip()
        bounded.append(line)
    lines=bounded
    counts = Counter(line for line in lines if len(line) > 30)
    boilerplate = r"educational (?:and entertainment )?purposes|financial, legal, accounting|not investment advice|past performance|copyright|before making any investment|do not take into account your particular"
    lines = [line for line in lines if not (len(line) > 30 and counts[line] > 2 and re.search(boilerplate, line, re.I))
             and not re.fullmatch(r"(?:Page\s+)?\d+(?:\s+of\s+\d+|\s*\|\s*P\s*a\s*g\s*e)?", line, re.I)]
    chunks, current = [], []
    def flush():
        if current:
            passage = " ".join(current).strip()
            if len(passage) >= 80:
                chunks.append(passage)
            current.clear()
    for line in lines:
        if not line:
            if len(" ".join(current)) >= 300:
                flush()
            continue
        # Keep interlocutor markers with the following answer.
        if re.match(r"^(?:\[\d|Mohnish:|G&D:|LL:|GG:|CONSUELO|WILLIAM GREEN|Bruce:)", line, re.I) and len(" ".join(current)) >= 300:
            flush()
        current.append(line)
        if len(" ".join(current)) >= 1100 and re.search(r"[.!?。！？][\"’”']?$", line):
            flush()
        elif len(" ".join(current)) >= 1500:
            flush()
    flush()
    return [{"id": f"s{i}", "text": passage} for i, passage in enumerate(chunks)]


def parse_captions(raw):
    text = raw.decode("utf-8", "replace")
    if text.lstrip().startswith("{"):
        data = json.loads(text)
        lines = ["".join(s.get("utf8", "") for s in e.get("segs", [])) for e in data.get("events", [])]
    else:
        lines = [re.sub(r"<[^>]+>", "", l).strip() for l in text.splitlines()
                 if l and not re.match(r"WEBVTT|Kind:|Language:|\d+$|\d\d:\d\d|NOTE", l)]
    # Rolling auto-captions repeat lines; deduplicate only adjacent lines.
    result = []
    for line in lines:
        if line and (not result or line != result[-1]):
            result.append(line)
    return "\n".join(result)


def embedded_source_media(raw, url):
    page=soup(raw);scope=page.find('article') or page.find('main') or page
    primary=[m.get('content','') for m in page.select('meta[property="og:video"],meta[property="og:video:url"],meta[name="twitter:player"]')]
    candidates=primary or [m.get('src') or m.get('data-src') or '' for m in scope.select('iframe,video,source,audio')]
    result=[]
    for value in candidates:
        value=urllib.parse.urljoin(url,value);parsed=urllib.parse.urlsplit(value)
        host=(parsed.hostname or '').removeprefix('www.')
        if parsed.scheme!='https':continue
        if host in ('youtube.com','youtube-nocookie.com','youtu.be'):
            ident=parsed.path.split('/embed/')[-1].split('/')[0] if '/embed/' in parsed.path else urllib.parse.parse_qs(parsed.query).get('v',[''])[0]
            if host=='youtu.be':ident=parsed.path.strip('/')
            if re.fullmatch(r'[\w-]{11}',ident):result.append({'kind':'youtube','id':ident})
        elif host in ('player.vimeo.com','vimeo.com','players.brightcove.net','fast.wistia.net'):
            result.append({'kind':'publisher_embed','url':value})
    unique={json.dumps(m,sort_keys=True):m for m in result}
    return list(unique.values()) if len(unique)==1 else []


def video_text(work, allow_asr=False):
    """No cookies, login, paywall bypass, or downloaded media in the public tree."""
    budget.check()
    video = next((m for m in work.get("media", []) if m["kind"] in {"youtube", "publisher_embed"}), None)
    audio = next((m for m in work.get("media", []) if m["kind"] == "audio"), None)
    if not video and not audio and allow_asr:
        for item in work.get('sources',[]):
            if '.pdf' in item['url'].lower() or item.get('label',{}).get('zh')=='发布方目录':continue
            try:
                raw,_=fetch(item['url']);found=embedded_source_media(raw,item['url'])
                if found:video=found[0];break
            except Exception:continue
    with tempfile.TemporaryDirectory(prefix="investor-speech-") as tmp:
        out = Path(tmp)
        if video:
            url = "https://www.youtube.com/watch?v=" + video["id"] if video["kind"] == "youtube" else video["url"]
            cmd = ["yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
                   "--sub-langs", "en.*,zh.*", "--sub-format", "json3/vtt", "--no-playlist",
                   "--socket-timeout", "20", "--retries", "1", "-o", str(out / "source.%(ext)s"), url]
            run = subprocess.run(cmd, capture_output=True, timeout=budget.timeout(120))
            captions = sorted(list(out.glob("*.json3")) + list(out.glob("*.vtt")))
            if captions:
                text = parse_captions(captions[0].read_bytes())
                if len(text) > 600:
                    return text, "captions"
            if not allow_asr:
                raise ValueError("Video captions unavailable; speech recognition not enabled for this run")
            download = subprocess.run(["yt-dlp", "-f", "bestaudio", "--no-playlist", "--max-filesize", "250M",
                            "--socket-timeout", "20", "--retries", "1", "-o", str(out / "audio.%(ext)s"), url],
                           capture_output=True, timeout=budget.timeout(180))
            if download.returncode:
                for f in out.glob("audio.*"):
                    f.unlink()
        files = [f for f in out.glob("audio.*") if f.suffix != ".part"]
        if not files and audio and allow_asr:
            req = urllib.request.Request(audio["url"], headers=HEADERS)
            with urllib.request.urlopen(req, timeout=budget.timeout(45)) as r, (out / "audio.media").open("wb") as target:
                if r.headers.get('Content-Type','').lower().startswith(('image/','text/','application/pdf')):
                    raise ValueError('Publisher enclosure is not an audio recording')
                total = 0
                expected_length = int(r.headers.get("Content-Length", "0"))
                while chunk := r.read(1024 * 1024):
                    budget.check()
                    total += len(chunk)
                    if total > 250 * 1024 * 1024:
                        raise ValueError("Audio exceeds download limit")
                    target.write(chunk)
                if expected_length and total != expected_length:
                    raise ValueError("Incomplete audio download; do not label a partial recording as fully processed")
        files = [f for f in out.glob("audio.*") if f.suffix != ".part"]
        if not files:
            raise ValueError("No audio obtained")
        from faster_whisper import WhisperModel
        model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
        # Recognition uses the entire available recording, not an opening excerpt.
        segments, info = model.transcribe(str(files[0]), vad_filter=True)
        parts=[]
        for s in segments:
            budget.check()
            parts.append(f"[{int(s.start)//60:02d}:{int(s.start)%60:02d}] {s.text}")
        text="\n".join(parts)
        if len(text) < 600:
            raise ValueError("Insufficient speech recognition output")
        return text, "asr"


def obtain_text(work, allow_asr=False, get=fetch):
    failures = []
    urls = [s["url"] for s in work["sources"] if "发布方目录" != s.get("label", {}).get("zh")]
    urls.sort(key=lambda u: 0 if ".pdf" in u.lower() else 1)
    for url in urls:
        if "youtube.com" in url or "youtu.be" in url:
            continue
        try:
            raw, typ = get(url)
            if (urllib.parse.urlsplit(url).hostname or '').removeprefix('www.') in {'buffett.cnbc.com','charlierose.com'}:
                from publisher_transcripts import obtain
                text,origins=obtain(raw,url,get)
                work['_materialURLs']=origins
                return text,'official_transcript',url
            text = extract_text(raw, typ)
            # Reject challenge pages and bare metadata; never summarise a denied page.
            if len(text) < 1000 or any(s in text[:500].lower() for s in ["access denied", "just a moment", "enable javascript and cookies"]):
                continue
            if work.get("sourceScope") == "pdf_excerpt":
                start, end = work["sourcePageRange"]
                import fitz
                doc = fitz.open(stream=raw, filetype="pdf")
                text = "\n".join(doc[i-1].get_text() for i in range(start, end+1))
            # Rich show notes are not the transcript of a podcast/video.
            if work.get("basis") == "publisher_description":
                if allow_asr:
                    try:
                        recording, kind = video_text(work, allow_asr=True)
                        return recording, kind, url
                    except Exception:
                        pass
                return text, "description", url
            return text, "official_text", url
        except Exception as exc:
            failures.append(type(exc).__name__)
    text, kind = video_text(work, allow_asr)
    return text, kind, urls[0] if urls else ""


def validate_note(note, chunks):
    """Require aligned languages, evidence for every chapter, bounded paraphrase."""
    ids = {c["id"] for c in chunks}
    pairs = [note.get("lead", {})]
    if not 3 <= len(note.get("chapters", [])) <= 6:
        raise ValueError("A study edition needs 3–6 substantive chapters")
    for chapter in note["chapters"]:
        if not chapter.get("evidenceIds") or not set(chapter["evidenceIds"]) <= ids:
            raise ValueError("Chapter has no valid source evidence")
        pairs.append(chapter.get("heading", {}))
        if not chapter.get("paragraphs"):
            raise ValueError("Empty chapter")
        pairs.extend(chapter["paragraphs"])
    if any(not isinstance(p.get(k), str) or not p[k].strip() for p in pairs for k in ["zh", "en"]):
        raise ValueError("Missing aligned Chinese or English text")
    chinese = " ".join(p["zh"] for p in pairs)
    if len(re.findall(r"[\u4e00-\u9fff]", chinese)) < 100:
        raise ValueError("Chinese study edition is too short")
    original = " ".join(c["text"] for c in chunks)
    for p in pairs:
        for number in re.findall(r"\b\d[\d,.]*%?\b", p["zh"] + " " + p["en"]):
            if number.replace(",", "") not in original.replace(",", ""):
                raise ValueError("Unsupported numeric claim")
        words = re.findall(r"\b[\w’'-]+\b", p["en"])
        # Long verbatim runs are not accepted; this is an original study edition.
        for i in range(max(0, len(words)-15)):
            if " ".join(words[i:i+16]).lower() in original.lower():
                raise ValueError("Study edition contains a long copied passage")
    total_words = sum(len(re.findall(r"\b\w+\b", p["en"])) for p in pairs)
    if total_words > 320:
        raise ValueError("Study edition exceeds conservative paraphrase budget")
    return True


def validate_catalog(catalog, root=ROOT):
    people = {p["id"] for p in read(root / "investors.json")["investors"]}
    seen, seen_urls = set(), set()
    for w in catalog["works"]:
        if w["id"] in seen or w["investor"] not in people:
            raise ValueError("Duplicate work or unknown investor")
        seen.add(w["id"])
        if not w.get("title", {}).get("zh") or not w["title"].get("en"):
            raise ValueError("Missing translated title")
        if w.get("date"):
            date = w["date"]
            if not re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", date):
                raise ValueError("Invalid historical date")
            dt.date.fromisoformat(date + ("-01-01" if len(date) == 4 else "-01" if len(date) == 7 else ""))
        if w.get("date") and w["date"] > now()[:len(w["date"])]:
            raise ValueError("Future event cannot be published as a historical work")
        if w["sources"][0]["url"]:
            key = w["investor"], canonical(w["sources"][0]["url"])
            if key in seen_urls:
                raise ValueError("A source work appears more than once")
            seen_urls.add(key)
        for s in w["sources"]:
            canonical(s["url"])
        if w.get("fullTextFile"):
            if w.get("fullTextStatus") != "ready" or not re.fullmatch(r"archive/texts/[a-z0-9_-]+\.json", w["fullTextFile"]):
                raise ValueError("Invalid full-text publication state")
            from verbatim_texts import validate_document
            validate_document(read(root / w["fullTextFile"]), w["id"])
    if people - {w["investor"] for w in catalog["works"]}:
        raise ValueError("One or more investors have no archive entries")
    return True


def discover(root=ROOT):
    config = read(root / "archive/sources.json")
    catalog = read(root / "archive/catalog.json", {"schemaVersion": 1, "works": []})
    report, incoming = [], []
    for source in config["catalogues"]:
        try:
            works = (primary_author_catalog(source) if source['adapter'] in ('patient_author','oaktree_author') else
                     verified_document(source) if source['adapter']=='verified_document' else
                     rss_catalog(source) if source["adapter"] == "rss" else
                     spotify_catalog(source) if source["adapter"] == "spotify" else
                     search_catalog(source) if source["adapter"] == "search" else link_catalog(source))
            incoming.extend(w for w in works if not w.get("date") or w["date"] <= now()[:len(w["date"])])
            report.append({"investor": source["investor"], "url": source.get("url", "https://www.bing.com/search"), "status": "ok", "found": len(works)})
        except Exception as exc:
            report.append({"investor": source["investor"], "url": source.get("url", "https://www.bing.com/search"), "status": "retained", "error": type(exc).__name__})
    catalog["works"] = merge_works(catalog["works"], incoming)
    catalog["updatedAt"] = now()
    catalog["discovery"] = report
    validate_catalog(catalog, root)
    write(root / "archive/catalog.json", catalog)
    if (root / 'investors.json').exists():
        from archive_guides import build_guides
        build_guides(root)
    return catalog


def process(*args, **kwargs):
    raise ValueError("Summary generation has been removed. Import a permitted, reviewed original text instead.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["discover", "validate", "plan", "import-text"])
    p.add_argument("--work")
    p.add_argument("--input", type=Path)
    args = p.parse_args()
    if args.action == "discover":
        c = discover()
        print("Catalogued", len(c["works"]), "documents")
    elif args.action == "import-text":
        if not args.work or not args.input:
            p.error("--work and --input are required")
        from verbatim_texts import import_document
        print(import_document(ROOT, args.work, args.input))
    elif args.action == "validate":
        c = read(ROOT / "archive/catalog.json")
        validate_catalog(c)
        print("Valid:", len(c["works"]), "entries;", sum(w.get("fullTextStatus") == "ready" for w in c["works"]), "verified full texts")
    else:
        c = read(ROOT / "archive/catalog.json")
        print(json.dumps({"summaryGeneration": "disabled", "fullTexts": sum(w.get("fullTextStatus") == "ready" for w in c["works"])}))


if __name__ == "__main__":
    main()
