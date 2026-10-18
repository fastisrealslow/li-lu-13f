import copy
import io
import json
import os
import subprocess
from pathlib import Path
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

import archive_explanations as e
import archive_generator as generator
import speech_archive


class SectionGenerationTests(unittest.TestCase):
    def test_human_source_checked_guide_survives_automatic_retranscription(self):
        approved={'file':'archive/explanations/reviewed.json','inputHash':'current','sourceDigest':'reviewed-full-recording','reviewStatus':'verified','reviewMethod':'editorial_source_check'}
        fresh={'entries':{'test':approved},'attempts':{}}
        commands=[]
        def git(args,**kwargs):
            commands.append(args)
            output=json.dumps(fresh) if args[1:3]==['show','origin/master:archive/explanations/index.json'] else ''
            return subprocess.CompletedProcess(args,0,stdout=output,stderr='')
        with tempfile.TemporaryDirectory() as tmp,patch.object(generator.subprocess,'run',side_effect=git),patch.object(generator,'request_deployment') as deploy:
            (Path(tmp)/'archive/explanations').mkdir(parents=True)
            local={**approved,'file':'archive/explanations/automatic.json','sourceDigest':'different-asr-segmentation','reviewMethod':'automated'}
            result=generator.publish(tmp,{'entries':{'test':local},'attempts':{'test':{'status':'ok','inputHash':'current'}},'updatedAt':'now'},'test')
            self.assertEqual(result['entries']['test'],approved)
            self.assertFalse(any('archive/explanations/automatic.json' in cmd for cmd in commands))
            deploy.assert_not_called()

    def test_same_source_cannot_overwrite_an_already_approved_current_introduction(self):
        approved={'file':'archive/explanations/reviewed.json','inputHash':'current','sourceDigest':'same-source','reviewStatus':'verified'}
        fresh={'entries':{'test':approved},'attempts':{}}
        commands=[]
        def git(args,**kwargs):
            commands.append(args)
            return subprocess.CompletedProcess(args,1 if args[1:4]==['diff','--cached','--quiet'] else 0,stdout=json.dumps(fresh) if args[1:3]==['show','origin/master:archive/explanations/index.json'] else '',stderr='')
        with tempfile.TemporaryDirectory() as tmp,patch.object(generator.subprocess,'run',side_effect=git),patch.object(generator,'request_deployment') as deploy:
            (Path(tmp)/'archive/explanations').mkdir(parents=True)
            result=generator.publish(tmp,{'entries':{'test':{**approved,'file':'archive/explanations/redundant.json'}},'attempts':{'test':{'status':'ok','inputHash':'current'}},'updatedAt':'now'},'test')
            self.assertEqual(result['entries']['test'],approved)
            self.assertFalse(any('archive/explanations/redundant.json' in c for c in commands))
            deploy.assert_not_called()

    def test_approved_work_can_dispatch_pages_without_waiting_for_the_whole_batch(self):
        with patch.dict(os.environ,{'ARCHIVE_DEPLOY_TOKEN':'synthetic-test-key','GITHUB_REPOSITORY':'owner/repository'}),patch.object(generator.urllib.request,'urlopen',return_value=io.BytesIO(b'')) as request:
            generator.request_deployment()
            call=request.call_args.args[0]
            self.assertEqual(call.full_url,'https://api.github.com/repos/owner/repository/actions/workflows/deploy-pages.yml/dispatches')
            self.assertEqual(json.loads(call.data),{'ref':'master'})
            self.assertEqual(call.method,'POST')

    def test_retry_cannot_overwrite_a_newer_approved_text_or_success_status(self):
        approved={'file':'archive/explanations/test.json','inputHash':'current','reviewStatus':'verified'}
        fresh={'entries':{'test':approved},'attempts':{'test':{'status':'ok'}}}
        commands=[]
        def git(args,**kwargs):
            commands.append(args)
            output=json.dumps(fresh) if args[1:3]==['show','origin/master:archive/explanations/index.json'] else ''
            code=1 if args[1:4]==['diff','--cached','--quiet'] else 0
            return subprocess.CompletedProcess(args,code,stdout=output,stderr='')
        with tempfile.TemporaryDirectory() as tmp,patch.object(generator.subprocess,'run',side_effect=git):
            (Path(tmp)/'archive/explanations').mkdir(parents=True)
            result=generator.publish(tmp,{'entries':{'test':{'file':'archive/explanations/old.json','inputHash':'old'}},'attempts':{'test':{'status':'retry','inputHash':'current'}},'updatedAt':'now'},'test')
            self.assertEqual(result['entries']['test'],approved)
            self.assertEqual(result['attempts']['test']['status'],'ok')
            self.assertFalse(any('archive/explanations/old.json' in c for c in commands))

    def test_restored_cloud_credit_is_rechecked_without_restarting_cpu_work(self):
        payload={'choices':[{'message':{'content':'{"ok":true}'}}]}
        with patch.dict(os.environ,{'ARCHIVE_CLOUD_KEY':'synthetic-test-key','SILICONFLOW_KEY':''}),patch.object(generator,'_CLOUD_NEXT_CHECK',0),patch.object(generator.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(payload).encode())):
            generator.retry_configured_cloud()
            self.assertEqual(os.environ['SILICONFLOW_KEY'],'synthetic-test-key')

    def test_credit_failure_falls_back_to_cpu_and_does_not_publish_a_failed_cloud_result(self):
        failure=urllib.error.HTTPError('https://api.siliconflow.cn',402,'Credit unavailable',{},None)
        cpu=io.BytesIO(json.dumps({'done':True,'response':'{"ok":true}'}).encode())
        with patch.dict(os.environ,{'ARCHIVE_CLOUD_KEY':'synthetic-test-key','SILICONFLOW_KEY':'synthetic-test-key'}),patch.object(generator,'_CLOUD_NEXT_CHECK',0),patch.object(generator.urllib.request,'urlopen',side_effect=[failure,cpu]) as request:
            self.assertEqual(generator.ask('JSON only',{},'synthetic'),{'ok':True})
            self.assertEqual(request.call_count,2)
            self.assertEqual(os.environ['SILICONFLOW_KEY'],'')

    def test_only_unambiguous_primary_publisher_video_is_selected(self):
        page=b'<main><iframe src="https://www.youtube.com/embed/abcdefghijk"></iframe></main>'
        self.assertEqual(speech_archive.embedded_source_media(page,'https://publisher.example/interview'),[{'kind':'youtube','id':'abcdefghijk'}])
        self.assertEqual(speech_archive.embedded_source_media(page.replace(b'</main>',b'<iframe src="https://www.youtube.com/embed/zyxwvutsrqp"></iframe></main>'),'https://publisher.example/interview'),[])

    def test_output_schema_requires_bilingual_evidence_without_padding_targets(self):
        outline=generator.output_schema({'task':'Plan source-specific sections','evidence':[{'id':'s17'}]})
        self.assertEqual(outline['properties']['sections']['items']['properties']['evidenceIds']['items']['enum'],['s17'])
        self.assertEqual(outline['properties']['sections']['minItems'],2)
        self.assertEqual(outline['properties']['sections']['maxItems'],8)
        schema=generator.output_schema({'task':'Write one source-specific guide section'})
        self.assertEqual(schema['required'],['zh','en'])
        self.assertEqual(schema['properties']['zh']['minLength'],1)

    def test_every_passage_is_mapped_and_approved_sections_resume(self):
        work={'id':'synthetic-test','title':{'zh':'测试','en':'Synthetic'}}
        chunks=[{'id':'s'+str(i),'text':'Synthetic evidence about business research.'} for i in range(13)]
        outline={'sourceSummary':{'zh':'企业研究。','en':'Business research.'},'sections':[{'heading':{'zh':h,'en':'Cash' if h=='现金' else 'Competition'},'evidenceIds':[sid]} for h,sid in [('现金','s0'),('竞争','s12')]]}
        mapped=[];written=[];failed=True
        def ask(system,prompt,model,tokens):
            if prompt['task'].startswith('Map'):
                mapped.extend(c['id'] for c in prompt['evidence']);return {'points':[{'claim':'A supported argument','evidenceIds':[prompt['evidence'][0]['id']]}]}
            if prompt['task'].startswith('Plan'):return copy.deepcopy(outline)
            if prompt['task'].startswith('Review'):return {'valid':True,'problems':[]}
            topic=prompt['topic']['heading']['zh'];written.append(topic)
            if failed and topic=='竞争':raise TimeoutError('synthetic failure')
            return {'zh':topic+'的论证与材料相连。','en':'A source-specific argument about '+('cash' if topic=='现金' else 'competition')+'.'}
        with tempfile.TemporaryDirectory() as tmp,patch.object(generator,'ask',side_effect=ask):
            with self.assertRaises(TimeoutError):generator.generate(work,chunks,'official_text','synthetic',0,Path(tmp))
            self.assertEqual(mapped,[c['id'] for c in chunks])
            saved=e.read(Path(tmp)/'.archive-work/partials/synthetic-test.json')
            self.assertEqual(len(saved['sections']),1)
            self.assertEqual(saved['inputHash'],e.input_hash(work))
            mapped.clear();written.clear();failed=False
            note=generator.generate(work,chunks,'official_text','synthetic',0,Path(tmp))
            self.assertEqual(mapped,[])
            self.assertEqual(written,['竞争'])
            self.assertTrue(e.validate(note,work,chunks,0))

    def test_editorial_errors_prevent_publication(self):
        work={'id':'review-test','title':{'zh':'测试','en':'Test'}}
        chunks=[{'id':'s0','text':'Synthetic source.'},{'id':'s1','text':'Other evidence.'}]
        outline={'sourceSummary':{'zh':'企业研究。','en':'Business research.'},'sections':[{'heading':{'zh':h,'en':'Concept'},'evidenceIds':['s0']} for h in ['现金','竞争']]}
        def ask(system,prompt,model,tokens):
            task=prompt['task']
            if task.startswith('Map'):return {'points':[{'claim':'Supported argument','evidenceIds':['s0']}]}
            if task.startswith('Plan'):return copy.deepcopy(outline)
            if task.startswith('Review'):return {'valid':False,'problems':['The languages attribute different positions.']}
            return {'zh':'材料中的具体论证。','en':'A supported argument.'}
        with tempfile.TemporaryDirectory() as tmp,patch.object(generator,'ask',side_effect=ask):
            with self.assertRaisesRegex(ValueError,'editorial review'):generator.generate(work,chunks,'official_text','synthetic',0,Path(tmp))
            saved=e.read(Path(tmp)/'.archive-work/partials/review-test.json')
            self.assertEqual(saved['sections'],[])


if __name__=='__main__':unittest.main()
