import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import ai_supplement as ai


class AISupplementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        ai.write(self.root/'investors.json', {'investors':[{'id':'test','name':'测试','source13F':True,'dataFile':'data.json'}]})
        self.data = {'current': {'quarter':'2026Q2','holdings':[{'ticker':'AAA','shares':200,'value':2000}],
                                 'previousHoldings':[{'ticker':'AAA','shares':100,'value':1000}, {'ticker':'EXIT','shares':10,'value':100}]}}
        ai.write(self.root/'data.json', self.data)
        self.task = ai.tasks(self.root)[0]
        self.summary = '本季增持AAA，清仓EXIT。摘要仅涵盖所列主要持仓变动。'

    def test_comparison_includes_exit_and_correct_share_change(self):
        facts = self.task['facts']['largestChanges']
        self.assertEqual(facts[0]['change'],'增持100.0%')
        self.assertEqual(facts[1]['change'],'清仓')

    def test_same_data_cached_but_new_model_or_correction_requeues(self):
        cache={'entries':{self.task['id']:{'sourceHash':self.task['sourceHash'],'model':ai.MODEL,'summary':self.summary}}}
        self.assertEqual(ai.pending([self.task],cache,ai.MODEL),[])
        self.assertEqual(len(ai.pending([self.task],cache,'other')),1)
        self.data['current']['holdings'][0]['shares']=250
        ai.write(self.root/'data.json',self.data)
        self.assertEqual(len(ai.pending(ai.tasks(self.root),cache,ai.MODEL)),1)

    def test_failure_preserves_old_summary_and_checkpoints_retry(self):
        ai.write(self.root/'ai_supplement.json',{'entries':{self.task['id']:{'summary':'旧摘要'}},'attempts':{}})
        def fail(*args): raise TimeoutError('local inference timeout')
        report=ai.run(self.root,ai.MODEL,6,10,self.root/'report.json',fail)
        ai.merge(self.root,report)
        cache=ai.read(self.root/'ai_supplement.json')
        self.assertEqual(cache['entries'][self.task['id']]['summary'],'旧摘要')
        self.assertEqual(cache['lastRun']['failed'],1)
        self.assertEqual(len(ai.pending(ai.tasks(self.root),cache,ai.MODEL)),1)

    def test_publish_rejects_results_if_source_changed_during_inference(self):
        report=ai.run(self.root,ai.MODEL,6,10,self.root/'report.json',lambda *args:(self.summary,{'seconds':1}))
        self.data['current']['holdings'][0]['shares']=300
        ai.write(self.root/'data.json',self.data)
        self.assertEqual(ai.merge(self.root,report),0)
        self.assertEqual(ai.read(self.root/'data.json'),self.data)

    def test_valid_output_does_not_touch_source_files(self):
        before=(self.root/'data.json').read_bytes()
        report=ai.run(self.root,ai.MODEL,6,10,self.root/'report.json',lambda *args:(self.summary,{'seconds':1}))
        self.assertEqual(ai.merge(self.root,report),1)
        self.assertEqual((self.root/'data.json').read_bytes(),before)

    def test_rejects_invented_numbers_html_and_prompt_echo(self):
        for text in ['本季增持AAA约999.9%，清仓EXIT，主要持仓有所调整。', '<script>这是一个不应发布的模型输出示例。</script>', '若提供其他信息，可以补充归纳主要股票持仓变化。']:
            with self.assertRaises(ValueError): ai.validate_summary(text,self.task['facts'])

    def test_empty_predecessor_is_not_fabricated_from_missing_data(self):
        self.data['current'].pop('previousHoldings')
        ai.write(self.root/'data.json',self.data)
        self.assertIn('未知',ai.tasks(self.root)[0]['facts']['largestChanges'][0]['change'])

    def test_failed_record_does_not_starve_other_records(self):
        other={**self.task,'id':'investor:other'}
        cache={'attempts':{self.task['id']:{'at':'2026-09-16'}}}
        self.assertEqual(ai.pending([self.task,other],cache,ai.MODEL)[0]['id'],other['id'])

    def test_nonfinite_or_short_output_rejected(self):
        with self.assertRaises(ValueError): ai.validate_summary('好的',{})


if __name__ == '__main__': unittest.main()
