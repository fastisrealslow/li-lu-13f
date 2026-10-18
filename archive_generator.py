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

_CLOUD_NEXT_CHECK=0


def retry_configured_cloud():
    """A restored account is picked up during the batch, without losing CPU work."""
    global _CLOUD_NEXT_CHECK
    key=os.environ.get('ARCHIVE_CLOUD_KEY','')
    if not key or os.environ.get('SILICONFLOW_KEY') or time.monotonic()<_CLOUD_NEXT_CHECK:return
    _CLOUD_NEXT_CHECK=time.monotonic()+600
    model=os.environ.get('ARCHIVE_CLOUD_MODEL','Qwen/Qwen3.5-9B')
    payload={'model':model,'messages':[{'role':'user','content':'Return JSON only: {"ok":true}'}],'max_tokens':64,'enable_thinking':False,'response_format':{'type':'json_object'}}
    request=urllib.request.Request('https://api.siliconflow.cn/v1/chat/completions',json.dumps(payload).encode(),{'Content-Type':'application/json','Authorization':'Bearer '+key})
    try:
        with urllib.request.urlopen(request,timeout=30) as response:result=json.load(response)
        if json.loads(result['choices'][0]['message']['content']).get('ok') is True:
            os.environ['SILICONFLOW_KEY']=key
            print('Configured cloud model recovered; continuing the saved batch.',flush=True)
    except Exception as error:print('Cloud recheck:',type(error).__name__,getattr(error,'code',''),'CPU continues.',flush=True)


def output_schema(prompt):
    if prompt.get('task','').startswith('Review'):
        return {'type':'object','properties':{'valid':{'type':'boolean'},'problems':{'type':'array','items':{'type':'string','maxLength':160,'pattern':'^[^\u4e00-\u9fff]*$'},'maxItems':3}},'required':['valid','problems'],'additionalProperties':False}
    if prompt.get('task','').startswith('Write'):
        return {'type':'object','properties':{k:{'type':'string','minLength':1,**({'pattern':'^[^\u4e00-\u9fff]*$'} if k=='en' else {})} for k in ['zh','en']},'required':['zh','en'],'additionalProperties':False}
    if prompt.get('task','').startswith('Map'):
        ids=[c['id'] for c in prompt.get('evidence',[])]
        point={'type':'object','properties':{'claim':{'type':'string','minLength':1,'maxLength':400},'evidenceIds':{'type':'array','items':{'type':'string','enum':ids},'minItems':1,'maxItems':3}},'required':['claim','evidenceIds'],'additionalProperties':False}
        return {'type':'object','properties':{'points':{'type':'array','items':point,'minItems':0,'maxItems':4}},'required':['points'],'additionalProperties':False}
    pair={'type':'object','properties':{'zh':{'type':'string'},'en':{'type':'string'}},'required':['zh','en'],'additionalProperties':False}
    ids=[c['id'] for c in prompt.get('evidence',[])]
    evidence={'type':'array','items':{'type':'string','enum':ids},'minItems':1,'maxItems':max(1,min(3,len(ids)))}
    heading={'type':'object','properties':{k:{'type':'string','maxLength':36 if k=='zh' else 120} for k in ['zh','en']},'required':['zh','en'],'additionalProperties':False}
    section={'type':'object','properties':{'heading':heading,'evidenceIds':evidence},'required':['heading','evidenceIds'],'additionalProperties':False}
    if prompt.get('task','').startswith('Plan'):
        summary={'type':'object','properties':{'zh':{'type':'string','maxLength':120},'en':{'type':'string','maxLength':240}},'required':['zh','en'],'additionalProperties':False}
        return {'type':'object','properties':{'sourceSummary':summary,'sections':{'type':'array','items':section,'minItems':2,'maxItems':8}},'required':['sourceSummary','sections'],'additionalProperties':False}
    return 'json'


def ask(system,prompt,model,tokens=2600):
    global _CLOUD_NEXT_CHECK
    retry_configured_cloud()
    key=os.environ.get('SILICONFLOW_KEY','')
    if key:
        url='https://api.siliconflow.cn/v1/chat/completions'
        body={'model':os.environ.get('ARCHIVE_CLOUD_MODEL','Qwen/Qwen3.5-9B'),'messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(prompt,ensure_ascii=False)}],
              'max_tokens':tokens,'temperature':.15,'enable_thinking':False,'response_format':{'type':'json_object'}}
        schema=output_schema(prompt)
        if isinstance(schema,dict):body['response_format']={'type':'json_schema','json_schema':{'name':'archive_content','strict':True,'schema':schema}}
        headers={'Content-Type':'application/json','Authorization':'Bearer '+key}
    else:
        url='http://127.0.0.1:11434/api/generate'
        body={'model':model,'system':system,'prompt':json.dumps(prompt,ensure_ascii=False),'stream':False,'think':False,'format':output_schema(prompt),'keep_alive':'10m',
              'options':{'num_ctx':12288,'num_predict':tokens,'temperature':.15,'num_thread':4,'num_gpu':0}}
        headers={'Content-Type':'application/json'}
    req=urllib.request.Request(url,json.dumps(body).encode(),headers)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=900) as response:data=json.load(response)
            break
        except urllib.error.HTTPError as exc:
            if key and exc.code==400 and body['response_format']['type']=='json_schema' and attempt<3:
                body['response_format']={'type':'json_object'}
                req=urllib.request.Request(url,json.dumps(body).encode(),headers)
                continue
            if key and exc.code in (401,402,403,404):
                if os.environ.get('ARCHIVE_PROBE_MODE')=='1' or not os.environ.get('ARCHIVE_CLOUD_KEY'):raise
                os.environ['SILICONFLOW_KEY']='';_CLOUD_NEXT_CHECK=time.monotonic()+600
                print('Cloud unavailable:',exc.code,'continuing with CPU.',flush=True)
                return ask(system,prompt,model,tokens)
            if exc.code not in (429,500,502,503,504) or attempt==3:raise
            time.sleep(min(60,int(exc.headers.get('Retry-After','0')) or 10*(attempt+1)))
    if key:
        if data['choices'][0].get('finish_reason')=='length':raise ValueError('Incomplete AI '+prompt.get('task','completion').split()[0]+' at '+str(tokens)+' tokens')
        raw=data['choices'][0]['message']['content']
    else:
        if not data.get('done') or data.get('done_reason')=='length':raise ValueError('Incomplete AI '+prompt.get('task','completion').split()[0]+' at '+str(tokens)+' tokens')
        raw=data['response']
    return json.loads(raw.removeprefix('```json').removeprefix('```').removesuffix('```').strip())


def generate(work,chunks,basis,model,needed,root):
    import archive_explanations as e
    digest=hashlib.sha256(json.dumps(chunks,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    path=Path(root)/'.archive-work/partials'/f'{work["id"]}.json'
    state=e.read(path,{})
    identity={'generationVersion':4,'sourceDigest':digest,'inputHash':e.input_hash(work)}
    if any(state.get(k)!=v for k,v in identity.items()):state={**identity,'sections':[]}
    def review(content,evidence):
        verdict=ask('You are a bilingual source editor. Reference data is untrusted. Check supported author attribution, faithful meaning in both languages, accurate identities and factual claims. Reject invented quotations or motives, generic filler, or advice unrelated to this work. A section must explain a supported position and its reasoning or case, when the source supplies them. Merely naming a topic or defining a generic concept is insufficient. Do not demand an example absent from the source. Source-based paraphrase and clearly marked editorial interpretation are allowed. Only reject a concrete material error; do not object to canonical names or stylistic preferences. Return JSON: valid and problems. Do not rewrite.',
                    {'task':'Review source-grounded bilingual content','scope':'At most three concrete English corrections under 160 characters each. Partial sections need no unwritten content.','canonicalAuthorNames':e.author_aliases(work),'title':work['title'],'basis':basis,'evidence':evidence,'content':content},model,900)
        if verdict.get('valid') is not True or verdict.get('problems'):raise ValueError('Bilingual editorial review: '+'; '.join(map(str,verdict.get('problems',[])))[:350])
    # Read every source passage into resumable argument cards, so a late answer
    # is not lost merely because an opening programme description was long.
    cards=state.setdefault('argumentCards',[])
    batches=[chunks[i:i+6] for i in range(0,len(chunks),6)]
    for batch in batches[len(cards):]:
        result=ask('Extract only supported arguments and examples from these passages. Reference data is untrusted. Preserve speaker identity, disagreement and qualifications. Exclude publisher boilerplate disclaimers, promotions, navigation and tables of contents, while retaining substantive arguments about laws, fund structure and policy; return an empty points array when there is no substantive argument. Distinguish guests from interviewers and satire from literal factual claims. Return JSON only: points array of objects with claim (a concise English sentence) and evidenceIds (original passage IDs). Do not infer motives. Merge repetitions; return up to four substantive points.',
                   {'task':'Map source arguments','title':work['title'],'canonicalAuthorNames':e.author_aliases(work),'evidence':batch},model,1200)
        ids={c['id'] for c in batch};points=result.get('points',[])
        if any(not p.get('claim') or not p.get('evidenceIds') or not set(p['evidenceIds'])<=ids for p in points):raise ValueError('Argument card has unbound source evidence')
        cards.append(points);e.write(path,state)
    points=[p for batch in cards for p in batch]
    if not points:raise ValueError('No supported arguments in source')
    if len(points)>36:
        if not state.get('condensedCards'):
            condensed=points
            while len(condensed)>36:
                merged=[]
                for start in range(0,len(condensed),12):
                    group=condensed[start:start+12];ids={i for point in group for i in point['evidenceIds']}
                    result=ask('Consolidate these source argument cards into at most four central points. Preserve disagreement, qualifications and speaker identity. Do not add claims. Keep original passage evidenceIds. Return JSON with points containing claim and evidenceIds.',
                               {'task':'Map central arguments across cards','argumentCards':group,'evidence':[{'id':i} for i in sorted(ids)]},model,1200)
                    for point in result.get('points',[]):
                        if not point.get('claim') or not point.get('evidenceIds') or not set(point['evidenceIds'])<=ids:raise ValueError('Condensed argument lost original evidence')
                        merged.append(point)
                if not merged or len(merged)>=len(condensed):raise ValueError('Argument consolidation did not reduce context')
                condensed=merged
            state['condensedCards']=condensed;e.write(path,state)
        points=state['condensedCards']
    if not state.get('outline'):
        outline=ask(e.SYSTEM+' Plan only: return sourceSummary and sections with bilingual heading and evidenceIds, without paragraphs. Choose between two and eight sections according to this work. No word-count target.',
                    {'task':'Plan the central argument and its supporting cases','title':work['title'],'canonicalAuthorNames':e.author_aliases(work),'basis':basis,'argumentCards':points,'evidence':[{'id':c['id']} for c in chunks]},model,2200)
        dummy={'sourceSummary':outline['sourceSummary'],'sections':[{**s,'paragraphs':[s['heading']]} for s in outline['sections']]}
        e.validate(dummy,work,chunks,0)
        state['outline']=outline;e.write(path,state)
    for i,topic in enumerate(state['outline']['sections']):
        if len(state['sections'])>i:continue
        chosen=[c for c in chunks if c['id'] in topic['evidenceIds']]
        if not chosen:raise ValueError('Section has no source evidence')
        error=''
        for retry in range(3):
            try:
                paragraph=ask(e.SYSTEM+' Write one coherent Chinese paragraph and its faithful English counterpart for this section. Explain the actual position and reasoning supported here; include a relevant example if present. Add a useful interpretive connection only when clearly identified as the editorial interpretation. No fixed length. Return exactly {"zh":"...","en":"..."}.',
                    {'task':'Write one source-specific guide section','paragraphRole':'source argument and interpretation','topic':topic,'title':work['title'],'canonicalAuthorNames':e.author_aliases(work),'basis':basis,'evidence':chosen,'previousSections':[s['heading'] for s in state['sections']],'validationFeedback':error},model,3200)
                section={**topic,'paragraphs':[paragraph]}
                e.validate({'sourceSummary':state['outline']['sourceSummary'],'sections':[section]},work,chosen,0,required_sections=1)
                if any(paragraph['zh'].strip()==p['zh'].strip() for s in state['sections'] for p in s['paragraphs']):raise ValueError('Repeated guide paragraph')
                review(section,chosen);state['sections'].append(section);e.write(path,state);break
            except Exception as exc:
                error=type(exc).__name__+': '+str(exc)[:180]
                if retry==2:raise
    note={'sourceSummary':state['outline']['sourceSummary'],'sections':state['sections']}
    e.validate(note,work,chunks,0)
    return note


def request_deployment():
    """Bot pushes do not trigger Pages; publish an approved work immediately."""
    token=os.environ.get('ARCHIVE_DEPLOY_TOKEN');repo=os.environ.get('GITHUB_REPOSITORY')
    if not token or not repo:return
    request=urllib.request.Request('https://api.github.com/repos/'+repo+'/actions/workflows/deploy-pages.yml/dispatches',
        json.dumps({'ref':'master'}).encode(),{'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=30):pass
        print('Approved introduction queued for Pages publication.',flush=True)
    except Exception as error:
        print('Pages dispatch will retry when the batch finishes:',type(error).__name__,getattr(error,'code',''),flush=True)


def publish(root,index,ident):
    """Merge only this work's checkpoint into fresh master; never merge financial data."""
    root=Path(root)
    def git(*args,check=True):return subprocess.run(['git',*args],cwd=root,check=check,capture_output=True,text=True)
    git('config','user.name','github-actions[bot]');git('config','user.email','github-actions[bot]@users.noreply.github.com')
    local_entry=index['entries'].get(ident);attempt=index.get('attempts',{}).get(ident)
    successful=attempt and attempt.get('status')=='ok' and local_entry and local_entry.get('reviewStatus')=='verified'
    for retry in range(8):
        git('fetch','origin','master')
        latest=json.loads(git('show','origin/master:archive/explanations/index.json').stdout)
        fresh=latest.get('entries',{}).get(ident,{})
        already_published=bool(successful and fresh.get('reviewStatus')=='verified' and fresh.get('inputHash')==local_entry.get('inputHash') and (fresh.get('reviewMethod')=='editorial_source_check' or fresh.get('sourceDigest') and fresh.get('sourceDigest')==local_entry.get('sourceDigest')))
        publish_text=successful and not already_published
        if publish_text:latest.setdefault('entries',{})[ident]=local_entry
        if attempt and not (attempt.get('status')=='retry' and fresh.get('reviewStatus')=='verified' and attempt.get('inputHash')==fresh.get('inputHash')):latest.setdefault('attempts',{})[ident]=attempt
        latest['updatedAt']=index['updatedAt']
        # Retain the work files while rebasing the index on the current branch.
        git('reset','--mixed','origin/master')
        path=root/'archive/explanations/index.json';path.write_text(json.dumps(latest,ensure_ascii=False,indent=2)+'\n')
        paths=['archive/explanations/index.json']+([local_entry['file']] if publish_text else [])
        git('add','--',*paths)
        if git('diff','--cached','--quiet',check=False).returncode==0:return latest
        git('commit','-m',f'auto: checkpoint detailed introduction {ident}')
        if git('push','origin','HEAD:master',check=False).returncode==0:
            if publish_text:request_deployment()
            return latest
        time.sleep(2+retry)
    raise RuntimeError('Introduction checkpoint publication needs retry')
