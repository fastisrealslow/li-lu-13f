"""Fault-injection batches exercise the real checkpoint and validation paths."""
import copy
import datetime as dt
import io
import json
import hashlib
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import archive_budget as budget
import archive_explanations as e
import archive_generator as g


CHUNKS=[{'id':'s'+str(i),'text':'Research of cash generation and competition supports patient business ownership.'} for i in range(13)]
OUTLINE={'sourceSummary':{'zh':'研究企业经营。','en':'Investigating businesses.'},'sections':[
    {'heading':{'zh':'现金','en':'Cash'},'evidenceIds':['s0']},
    {'heading':{'zh':'竞争','en':'Competition'},'evidenceIds':['s12']}]}


def answer(system,prompt,model,tokens):
    task=prompt['task']
    if task.startswith('Map'):return {'points':[{'claim':'Study business economics.','evidenceIds':[prompt['evidence'][0]['id']]}]}
    if task.startswith('Plan'):return copy.deepcopy(OUTLINE)
    if task.startswith('Review'):return {'valid':True,'problems':[]}
    heading=prompt['topic']['heading']
    return {'zh':heading['zh']+'的研究以企业经营为基础。','en':'Business analysis considers '+heading['en'].lower()+'.'}


class BatchStabilityTests(unittest.TestCase):
    def test_fourteen_shards_resume_at_every_model_boundary(self):
        # 3 map calls, outline, two write/review pairs: 112 interrupted runs.
        works=[]
        for shard in range(14):
            n=0
            while int(hashlib.sha256(f'batch-{shard}-{n}'.encode()).hexdigest(),16)%14!=shard:n+=1
            works.append({'id':f'batch-{shard}-{n}','investor':'synthetic','title':{'zh':'测试','en':'Test'}})
        for work in works:
            for boundary in range(8):
                with self.subTest(work=work['id'],boundary=boundary),tempfile.TemporaryDirectory() as tmp,redirect_stdout(io.StringIO()):
                    calls=[]
                    def interrupted(system,prompt,model,tokens):
                        calls.append(prompt)
                        if len(calls)==boundary+1:raise budget.BatchDeadline()
                        return answer(system,prompt,model,tokens)
                    with patch.object(g,'ask',side_effect=interrupted):
                        with self.assertRaises(budget.BatchDeadline):g.generate(work,CHUNKS,'official_text','local-test',0,Path(tmp))
                    resumed=[]
                    def continuing(system,prompt,model,tokens):
                        resumed.append(prompt)
                        return answer(system,prompt,model,tokens)
                    with patch.object(g,'ask',side_effect=continuing):note=g.generate(work,CHUNKS,'official_text','local-test',0,Path(tmp))
                    self.assertTrue(e.validate(note,work,CHUNKS,0))
                    self.assertEqual(resumed[0]['task'],calls[-1]['task'])
                    self.assertEqual(len(resumed),8-boundary)
                    self.assertEqual(len(e.read(Path(tmp)/'.archive-work/partials'/f'{work["id"]}.json')['sections']),2)

    def test_three_complete_rounds_of_fourteen_short_shards(self):
        works=[]
        for shard in range(14):
            n=0
            while int(hashlib.sha256(f'round-{shard}-{n}'.encode()).hexdigest(),16)%14!=shard:n+=1
            works.append({'id':f'round-{shard}-{n}','investor':'synthetic','title':{'zh':'测试','en':'Test'},'sources':[{'url':'https://publisher.example/source'}]})
        with tempfile.TemporaryDirectory() as tmp,redirect_stdout(io.StringIO()),patch.dict('os.environ',{'ARCHIVE_PUBLISH_EACH':'0'}),patch.object(e,'obtain_material',return_value=('Synthetic source','official_text','https://publisher.example/source')),patch.object(e.source,'source_chunks',return_value=CHUNKS):
            root=Path(tmp);e.write(root/'archive/catalog.json',{'works':works})
            results=[]
            for round_no in range(3):
                for shard in range(14):
                    calls=0
                    def short_batch(system,prompt,model,tokens):
                        nonlocal calls
                        calls+=1
                        if round_no<2 and calls==4:raise budget.BatchDeadline()
                        return answer(system,prompt,model,tokens)
                    with patch.object(g,'ask',side_effect=short_batch):
                        result=e.run(root,model='local-test',minutes=2,shard=shard,shards=14)
                    results.append(result)
                    if round_no<2:
                        self.assertTrue(result['continuation'])
                        self.assertGreater(result['checkpointProgress'],0)
                        self.assertEqual(result['failed'],0)
            self.assertEqual(sum(r['generated'] for r in results),14)
            self.assertEqual(results[-1]['pending'],0)
            index=e.read(root/'archive/explanations/index.json')
            self.assertEqual(len(index['entries']),14)
            self.assertTrue(all(a['status']=='ok' for a in index['attempts'].values()))

    def test_failed_editorial_feedback_survives_the_next_batch(self):
        work={'id':'feedback','title':{'zh':'测试','en':'Test'}}
        with tempfile.TemporaryDirectory() as tmp,redirect_stdout(io.StringIO()):
            def reject(system,prompt,model,tokens):
                if prompt['task'].startswith('Review'):return {'valid':False,'problems':['Explain the cash argument.']}
                return answer(system,prompt,model,tokens)
            with patch.object(g,'ask',side_effect=reject):
                with self.assertRaisesRegex(ValueError,'Explain the cash'):g.generate(work,CHUNKS,'official_text','local-test',0,Path(tmp))
            prompts=[]
            def resume(system,prompt,model,tokens):
                prompts.append(prompt)
                return answer(system,prompt,model,tokens)
            with patch.object(g,'ask',side_effect=resume):g.generate(work,CHUNKS,'official_text','local-test',0,Path(tmp))
            self.assertIn('Explain the cash argument',prompts[0]['validationFeedback'])

    def test_unavailable_source_backs_off_but_changed_sources_retry_immediately(self):
        work={'id':'retry','title':{'en':'Test'}}
        attempt={}
        now=dt.datetime.now(dt.timezone.utc)
        for count in range(1,25):
            attempt=e.retry_attempt(work,attempt,ValueError('No audio obtained'))
            self.assertFalse(e.retry_due(work,attempt,now))
            self.assertTrue(e.retry_due(work,attempt,now+dt.timedelta(hours=73)))
            self.assertTrue(e.retry_due({**work,'sources':[{'url':'https://publisher.example/new'}]},attempt,now))
        self.assertEqual(attempt['failures'],20)

    def test_corrupt_partial_is_quarantined_without_blocking_a_work(self):
        work={'id':'broken','title':{'zh':'测试','en':'Test'}}
        with tempfile.TemporaryDirectory() as tmp,redirect_stdout(io.StringIO()),patch.object(g,'ask',side_effect=answer):
            path=Path(tmp)/'.archive-work/partials/broken.json';path.parent.mkdir(parents=True);path.write_text('{broken')
            note=g.generate(work,CHUNKS,'official_text','local-test',0,Path(tmp))
            self.assertTrue(e.validate(note,work,CHUNKS,0))
            self.assertEqual(path.with_suffix('.corrupt').read_text(),'{broken')

    def test_failed_atomic_save_leaves_previous_checkpoint_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'draft.json';e.write(path,{'sections':['approved']})
            with patch.object(Path,'replace',side_effect=OSError('disk interrupted')):
                with self.assertRaises(OSError):e.write(path,{'sections':['approved','new']})
            self.assertEqual(e.read(path),{'sections':['approved']})


if __name__=='__main__':unittest.main()
