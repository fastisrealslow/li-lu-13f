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

    def test_cpu_output_schema_binds_evidence_and_requires_substantial_sections(self):
        schema=generator.output_schema({'task':'Write one section','minimumChineseCharacters':600,'evidence':[{'id':'s17'}]})
        self.assertEqual(schema['properties']['evidenceIds']['items']['enum'],['s17'])
        self.assertEqual(schema['properties']['paragraphs']['minItems'],3)
        self.assertGreaterEqual(schema['properties']['paragraphs']['items']['properties']['zh']['minLength'],280)

    def test_validated_sections_resume_without_restarting_the_work(self):
        headings=['竞争','现金','资本','风险','组织','估值']
        outline={'sourceSummary':{'zh':'测试资料讨论企业研究。','en':'Synthetic material about business research.'},'sections':[{'heading':{'zh':h,'en':['Competition','Cash','Capital','Risk','Organization','Valuation'][i]},'evidenceIds':['s0']} for i,h in enumerate(headings)]}
        work={'id':'synthetic-test','title':{'zh':'测试','en':'Synthetic'}}
        chunks=[{'id':'s0','text':'Synthetic evidence about business research.'},{'id':'s1','text':'Distinct material for the test.'}]
        failed=True;requested=[]
        def ask(system,prompt,model,tokens):
            if prompt['task'].startswith('Plan'):return copy.deepcopy(outline)
            if prompt['task'].startswith('Review'):return {'valid':True,'problems':[]}
            h=prompt['topic']['heading']['zh'];requested.append(h)
            if failed and h=='资本':raise TimeoutError('synthetic failure')
            return {**copy.deepcopy(prompt['topic']),'paragraphs':[{'zh':h+'。'+h.join(['这个段落是用于验证断点续写的独立合成分析。']*35),'en':'An original synthetic analytical paragraph for verification.'}]}
        with tempfile.TemporaryDirectory() as tmp,patch.object(generator,'ask',side_effect=ask),patch.object(generator.time,'sleep'):
            with self.assertRaises(TimeoutError):generator.generate(work,chunks,'official_text','synthetic',2600,Path(tmp))
            checkpoint=e.read(Path(tmp)/'.archive-work/partials/synthetic-test.json')
            self.assertEqual(len(checkpoint['sections']),2)
            requested.clear();failed=False
            note=generator.generate(work,chunks,'official_text','synthetic',2600,Path(tmp))
            self.assertEqual(len(note['sections']),6)
            self.assertNotIn('竞争',requested);self.assertNotIn('现金',requested)
            self.assertTrue(e.validate(note,work,chunks,2600))

    def test_editorial_rejection_never_saves_an_approved_outline(self):
        headings=['竞争','现金','资本','风险','组织','估值']
        outline={'sourceSummary':{'zh':'测试资料。','en':'Synthetic material.'},'sections':[{'heading':{'zh':h,'en':'Concept'},'evidenceIds':['s0']} for h in headings]}
        def ask(system,prompt,model,tokens):
            return {'valid':False,'problems':['The two languages identify different people.']} if prompt['task'].startswith('Review') else copy.deepcopy(outline)
        with tempfile.TemporaryDirectory() as tmp,patch.object(generator,'ask',side_effect=ask),patch.object(generator.time,'sleep'):
            with self.assertRaisesRegex(ValueError,'editorial review'):
                generator.generate({'id':'review-test','title':{'zh':'测试','en':'Test'}},[{'id':'s0','text':'Synthetic source.'},{'id':'s1','text':'Other evidence.'}],'official_text','synthetic',2600,Path(tmp))
            self.assertFalse((Path(tmp)/'.archive-work/partials/review-test.json').exists())

if __name__=='__main__':unittest.main()
