import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import archive_explanations as e
import archive_generator as generator


class SectionGenerationTests(unittest.TestCase):
    def test_validated_sections_resume_without_restarting_the_work(self):
        headings=['竞争','现金','资本','风险','组织','估值']
        outline={'sourceSummary':{'zh':'测试资料讨论企业研究。','en':'Synthetic material about business research.'},'sections':[{'heading':{'zh':h,'en':h+' analysis'},'evidenceIds':['s0']} for h in headings]}
        work={'id':'synthetic-test','title':{'zh':'测试','en':'Synthetic'}}
        chunks=[{'id':'s0','text':'Synthetic evidence about business research.'},{'id':'s1','text':'Distinct material for the test.'}]
        failed=True;requested=[]
        def ask(system,prompt,model,tokens):
            if prompt['task'].startswith('Plan'):return copy.deepcopy(outline)
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

if __name__=='__main__':unittest.main()
