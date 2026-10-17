"""Read the same public transcript data that the publisher's page loads.

Source text is used transiently for grounded analysis and is never published.
"""
import json
import math
import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup


def page(raw):
    return BeautifulSoup(raw.decode('utf-8') if isinstance(raw,bytes) else raw,'html.parser')


def state(raw):
    for script in page(raw).select('script'):
        value=script.get_text()
        marker='window.__s_data='
        if marker in value:
            return json.JSONDecoder().raw_decode(value.split(marker,1)[1].lstrip())[0]
    raise ValueError('Publisher page state unavailable')


def objects(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from objects(child)
    elif isinstance(value,list):
        for child in value:yield from objects(child)


def cnbc(raw,url,get):
    year=re.fullmatch(r'/((?:19|20)\d{2})-berkshire-hathaway-annual-meeting/?',urlsplit(url).path)
    if not year:raise ValueError('Unrecognized meeting page')
    year=year[1];sessions={}
    for asset in objects(state(raw)):
        target=urlsplit(asset.get('url',''))
        if asset.get('type')!='cnbcvideo' or asset.get('subType')!='full_length':continue
        if target.hostname!='buffett.cnbc.com' or not target.path.startswith('/video/'+year+'/'):continue
        if asset.get('premium') or asset.get('videoStatus') not in (None,'Unrestricted'):continue
        if not asset.get('vcpsId'):continue
        sessions.setdefault(asset['vcpsId'],asset)
    if not sessions:raise ValueError('No matching full meeting sessions')
    result=[];origins=[]
    for ident,asset in sessions.items():
        body,_=get(asset['url'])
        active=[a for a in objects(state(body)) if a.get('vcpsId')==ident and isinstance(a.get('transcript'),dict)]
        if not active:raise ValueError('A full meeting session has no transcript')
        transcript=active[0]['transcript'];chapters=transcript.get('chapters',[])
        if not chapters:raise ValueError('A full meeting session has no transcript chapters')
        statements=[]
        for chapter in chapters:
            parts=chapter.get('transcript',[])
            if not parts:raise ValueError('Incomplete meeting transcript chapter')
            for part in parts:
                at=part.get('in');text=part.get('title')
                if type(at) not in (int,float) or not math.isfinite(at) or at<0:raise ValueError('Invalid transcript timestamp')
                if not isinstance(text,str) or not text.strip():raise ValueError('Empty publisher transcript cue')
                # Publisher captions can overlap by a few seconds. Preserve
                # their supplied word order instead of sorting or dropping cues.
                statements.append(f'[{int(at)//60:02d}:{int(at)%60:02d}] '+page(text).get_text(' ',strip=True))
        if len('\n'.join(statements))<1000:raise ValueError('Meeting transcript too short')
        result.append(asset.get('title','')+'\n\n'+'\n'.join(statements));origins.append(asset['url'])
    return '\n\n'.join(result),origins


def charlie_rose(raw,url,get):
    match=re.fullmatch(r'/videos/(\d+)/?',urlsplit(url).path)
    if not match:raise ValueError('Unrecognized interview page')
    element=page(raw).select_one('.transcript[data-url]')
    target=urljoin(url,element.get('data-url','')) if element else ''
    parsed=urlsplit(target)
    if parsed.hostname!='charlierose.com' or parsed.path!='/video/transcripts/'+match[1]:
        raise ValueError('No matching publisher transcript endpoint')
    body,_=get(target);tree=page(body);times=tree.select('dl > dt');answers=tree.select('dl > dd')
    if len(answers)<5 or len(times)!=len(answers):raise ValueError('Incomplete publisher transcript')
    lines=[];last=-1
    for time,answer in zip(times,answers):
        label=time.get_text(strip=True);m=re.fullmatch(r'(\d+):(\d{2})',label)
        if not m:raise ValueError('Invalid transcript timestamp')
        at=int(m[1])*60+int(m[2]);spans=answer.select('span[data-time]')
        if at<last or not spans:raise ValueError('Incomplete or unordered interview transcript')
        last=at
        speaker=answer.find('a');name=speaker.get_text(' ',strip=True) if speaker else ''
        text=' '.join(span.get_text(' ',strip=True) for span in spans)
        if not text:raise ValueError('Empty interview answer')
        lines.append('['+label+'] '+name+' '+text)
    result='\n'.join(lines)
    if len(result)<1000:raise ValueError('Interview transcript too short')
    return result,[target]


def obtain(raw,url,get):
    host=(urlsplit(url).hostname or '').removeprefix('www.')
    if host=='buffett.cnbc.com':return cnbc(raw,url,get)
    if host=='charlierose.com':return charlie_rose(raw,url,get)
    raise ValueError('No dedicated publisher transcript reader')
