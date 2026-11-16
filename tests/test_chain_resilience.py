import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
import archive_generator as g
import archive_explanations as e
import automation_health as health
from test_archive_stability import CHUNKS,OUTLINE,answer

class ChainResilienceTests(unittest.TestCase):
    def test_stale_invalid_outline_is_repaired_without_remapping_source(self):
        work={'id':'repair-outline','title':{'zh':'测试','en':'Test'}}
        broken=copy.deepcopy(OUTLINE);broken['sourceSummary']['en']='An invented 999999 forecast.'
        state={'generationVersion':4,'sourceDigest':hashlib.sha256(json.dumps(CHUNKS,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'inputHash':e.input_hash(work),'outline':broken,'sections':[],
               'argumentCards':[[{'claim':'Business research.','evidenceIds':[CHUNKS[i]['id']]}] for i in range(0,len(CHUNKS),6)]}
        prompts=[]
        def model(system,prompt,model,tokens):
            prompts.append(prompt)
            return answer(system,prompt,model,tokens)
        with tempfile.TemporaryDirectory() as tmp,patch.object(g,'ask',side_effect=model),redirect_stdout(io.StringIO()):
            path=Path(tmp)/'.archive-work/partials/repair-outline.json';e.write(path,state)
            note=g.generate(work,CHUNKS,'official_text','test',0,Path(tmp))
            self.assertTrue(e.validate(note,work,CHUNKS,0))
            self.assertTrue(prompts[0]['task'].startswith('Plan'))
            self.assertIn('999999',prompts[0]['validationFeedback'])
            self.assertFalse(any(p['task']=='Map source arguments' for p in prompts))

    def test_http_success_does_not_mask_an_mcp_tool_error(self):
        def request(path,message=None):
            if path=='/':return b'<h3 id="mcpAccessTitle">MCP</h3>'
            if message['method']=='tools/list':return json.dumps({'result':{'tools':[{'name':n} for n in ['get_holdings','get_history','get_reading_guide','get_update_status']]}}).encode()
            return json.dumps({'result':{'isError':True,'content':[{'type':'text','text':'Upstream unavailable'}]}}).encode()
        with self.assertRaisesRegex(ValueError,'MCP tool failed'):health.public_service_health(request)

    def test_public_probe_reads_real_data_after_tool_discovery(self):
        def request(path,message=None):
            if path=='/':return b'<h3 id="mcpAccessTitle">MCP</h3>'
            if message['method']=='tools/list':return json.dumps({'result':{'tools':[{'name':n} for n in ['get_holdings','get_history','get_reading_guide','get_update_status']]}}).encode()
            return json.dumps({'result':{'content':[{'type':'text','text':json.dumps({'data':{'investor':'lilu','quarter':'2026 Q2','holdings':{'items':[{'ticker':'GOOG'}]}}})}]}}).encode()
        self.assertEqual(health.public_service_health(request)['status'],'checked')

if __name__=='__main__':unittest.main()
