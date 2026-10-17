"""Generate and validate one bilingual section at a time; checkpoint without source text."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time
import urllib.request
import urllib.error


def ask(system,prompt,model,tokens=2600):
    key=os.environ.get('SILICONFLOW_KEY','')
    if key:
        url='https://api.siliconflow.cn/v1/chat/completions'
        body={'model':os.environ.get('ARCHIVE_CLOUD_MODEL','Qwen/Qwen3.5-9B'),'messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(prompt,ensure_ascii=False)}],
              'max_tokens':tokens,'temperature':.15,'enable_thinking':False,'response_format':{'type':'json_object'}}
        headers={'Content-Type':'application/json','Authorization':'Bearer '+key}
    else:
        url='http://127.0.0.1:11434/api/generate'
        body={'model':model,'system':system,'prompt':json.dumps(prompt,ensure_ascii=False),'stream':False,'think':False,'format':'json','keep_alive':'10m',
              'options':{'num_ctx':8192,'num_predict':tokens,'temperature':.15,'num_thread':4,'num_gpu':0}}
        headers={'Content-Type':'application/json'}
    req=urllib.request.Request(url,json.dumps(body).encode(),headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=480) as response:data=json.load(response)
            break
        except urllib.error.HTTPError as exc:
            if exc.code not in (429,500,502,503,504) or attempt==3:raise
            time.sleep(min(60,int(exc.headers.get('Retry-After','0')) or 10*(attempt+1)))
    if key:
        if data['choices'][0].get('finish_reason')=='length':raise ValueError('Incomplete AI section')
        raw=data['choices'][0]['message']['content']
    else:
        if not data.get('done') or data.get('done_reason')=='length':raise ValueError('Incomplete AI section')
        raw=data['response']
    return json.loads(raw.removeprefix('```json').removeprefix('```').removesuffix('```').strip())


def generate(work,chunks,basis,model,needed,root):
    import archive_explanations as e
    digest=hashlib.sha256(json.dumps(chunks,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    path=Path(root)/'.archive-work/partials'/f'{work["id"]}.json'
    state=e.read(path,{})
    if state.get('sourceDigest')!=digest or state.get('minimum')!=needed:state={'sourceDigest':digest,'minimum':needed,'sections':[]}
    candidates=chunks if len(chunks)<=12 else [chunks[round(i*(len(chunks)-1)/11)] for i in range(12)]
    # Complete passages, with their exact IDs. The model never selects from invisible IDs.
    evidence=[];budget=0
    for c in candidates:
        size=e.chinese_size(c['text'])+(len(c['text'])-e.chinese_size(c['text']))/4
        if budget+size<=2600:evidence.append(c);budget+=size
    if len(evidence)<2:raise ValueError('Insufficient source evidence')
    if not state.get('outline'):
        error=''
        for retry in range(3):
            try:
                outline=ask(e.SYSTEM,{'task':'Plan six distinct work-specific conceptual explanations. Return sourceSummary and sections with bilingual heading and evidenceIds only. Do not write the paragraphs yet. No numbered headings. sourceSummary: <=80 Chinese characters and <=40 English words.',
                    'title':work['title'],'basis':basis,'evidence':evidence,'validationFeedback':error},model,1600)
                if len(outline.get('sections',[]))!=6:raise ValueError('Outline needs six sections')
                dummy={'sourceSummary':outline['sourceSummary'],'sections':[{**s,'paragraphs':[s['heading']]} for s in outline['sections']]}
                e.validate(dummy,work,evidence,0)
                state['outline']=outline;e.write(path,state);break
            except Exception as exc:
                error=type(exc).__name__+': '+str(exc)[:150]
                if retry==2:raise
                time.sleep(2*(retry+1))
    per_section=math.ceil(needed/6)+80
    for i,topic in enumerate(state['outline']['sections']):
        if len(state['sections'])>i:continue
        error=''
        chosen=[c for c in evidence if c['id'] in topic['evidenceIds']]
        for retry in range(3):
            try:
                section=ask(e.SYSTEM,{'task':'Write exactly this ONE independent analytical section, not a source retelling. Return heading, paragraphs (zh/en pairs), evidenceIds. At least three coherent paragraphs. Explain a mechanism, its conditions, and how it can fail; make this specific to the supplied material. Do not attribute your independent reasoning to the speaker.',
                    'title':work['title'],'basis':basis,'topic':topic,'otherTopics':[s['heading'] for s in state['outline']['sections'] if s!=topic],
                    'evidence':chosen,'minimumChineseCharacters':per_section,'targetChineseCharacters':per_section+100,'validationFeedback':error},model,3000)
                e.validate({'sourceSummary':{'zh':'独立分析。','en':'Independent analysis.'},'sections':[section]},work,chosen,per_section,required_sections=1)
                state['sections'].append(section);e.write(path,state);break
            except Exception as exc:
                error=type(exc).__name__+': '+str(exc)[:150]
                if retry==2:raise
                time.sleep(2*(retry+1))
    note={'sourceSummary':state['outline']['sourceSummary'],'sections':state['sections']}
    e.validate(note,work,chunks,needed)
    return note


def publish(root,index,ident):
    """Merge only this work's checkpoint into fresh master; never merge financial data."""
    root=Path(root)
    def git(*args,check=True):return subprocess.run(['git',*args],cwd=root,check=check,capture_output=True,text=True)
    git('config','user.name','github-actions[bot]');git('config','user.email','github-actions[bot]@users.noreply.github.com')
    local_entry=index['entries'].get(ident);attempt=index.get('attempts',{}).get(ident)
    for retry in range(8):
        git('fetch','origin','master')
        latest=json.loads(git('show','origin/master:archive/explanations/index.json').stdout)
        if local_entry:latest.setdefault('entries',{})[ident]=local_entry
        if attempt:latest.setdefault('attempts',{})[ident]=attempt
        latest['updatedAt']=index['updatedAt']
        # Retain the work files while rebasing the index on the current branch.
        git('reset','--mixed','origin/master')
        path=root/'archive/explanations/index.json';path.write_text(json.dumps(latest,ensure_ascii=False,indent=2)+'\n')
        paths=['archive/explanations/index.json']+([local_entry['file']] if local_entry else [])
        git('add','--',*paths)
        if git('diff','--cached','--quiet',check=False).returncode==0:return latest
        git('commit','-m',f'auto: checkpoint detailed introduction {ident}')
        if git('push','origin','HEAD:master',check=False).returncode==0:return latest
        time.sleep(2+retry)
    raise RuntimeError('Introduction checkpoint publication needs retry')
