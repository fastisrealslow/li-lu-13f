"""Build detailed collection guides from reviewed profiles and real catalogues.

The reading commentary is editorial AI explanation, never an original transcript.
No inference about an unread individual work is made here.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def pair(zh, en): return {'zh': zh, 'en': en}

def build_guides(root=ROOT):
    root=Path(root)
    people=json.loads((root/'investors.json').read_text())['investors']
    catalog=json.loads((root/'archive/catalog.json').read_text())
    guides={}
    for p in people:
        profile=p['profile']; works=sorted([w for w in catalog['works'] if w['investor']==p['id']],key=lambda w:w.get('date') or '')
        principles=profile.get('principles',[])
        # Collection context comes from the person's reviewed life and method.
        # Individual work arguments belong to the work's own source-based guide.
        context=profile['about'][-2:]
        reading=profile['about'][-2]
        sections=[{'heading':pair(*profile['signature']['title']), 'paragraphs':[pair(*profile['signature']['text']),pair(*reading)]},
                  {'heading':pair('研究方法与判断重点','Research and judgment'), 'paragraphs':[pair(x['title'][0]+'：'+x['text'][0],x['title'][1]+': '+x['text'][1]) for x in principles]},
                  {'heading':pair('经历与思想脉络','Experience and intellectual development'),'paragraphs':[pair(*x) for x in context]}]
        extensions={}
        anchor_works=works
        guides[p['id']]={'kind':'ai_collection_guide','investor':p['id'],'title':pair(p['name']+' · 作品阅读导读',p['nameEn']+' · Collection guide'),
                         'lead':pair(*profile['about'][0]),'sections':sections,'works':[{'id':w['id'],'title':w['title'],'date':w.get('date'),'publisher':w['publisher']} for w in anchor_works],
                         'sourceURLs':profile.get('sources',[]),'sourceHash':hashlib.sha256(json.dumps([profile,works,extensions.get(p['id'],[])],sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                         'label':pair('作品集导读 · 人物经历与研究方法','Collection guide · Experience and research approach')}
    path=root/'archive/guides.json';path.write_text(json.dumps({'version':1,'guides':guides},ensure_ascii=False,indent=2)+'\n')
    return guides

if __name__=='__main__':
    guides=build_guides();print('Detailed collection guides:',len(guides))
