import copy
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
        self.selection = ai.fallback_selection(self.task['facts'])

    def generate(self, task, model):
        return ai.fallback_selection(task['facts']), {'seconds':1}

    def test_comparison_includes_exit_and_correct_share_change(self):
        facts = self.task['facts']['items']
        self.assertEqual(facts[0]['change'],'增持100.0%')
        self.assertEqual(facts[1]['change'],'清仓')
        self.assertEqual(len({f['ticker'] for f in facts}),len(facts))

    def test_same_data_cached_but_new_model_or_correction_requeues(self):
        entry=ai.make_entry(self.task,self.selection,ai.MODEL)
        cache={'entries':{self.task['id']:entry}}
        self.assertEqual(ai.pending([self.task],cache,ai.MODEL),[])
        self.assertEqual(len(ai.pending([self.task],cache,'other')),1)
        self.data['current']['holdings'][0]['shares']=250
        ai.write(self.root/'data.json',self.data)
        self.assertEqual(len(ai.pending(ai.tasks(self.root),cache,ai.MODEL)),1)

    def test_failure_replaces_unverified_legacy_prose_with_current_facts_and_retries(self):
        ai.write(self.root/'ai_supplement.json',{'entries':{self.task['id']:{'summary':'旧的错误摘要'}},'attempts':{}})
        def fail(*args): raise TimeoutError('local inference timeout')
        report=ai.run(self.root,ai.MODEL,13,10,self.root/'report.json',fail)
        ai.merge(self.root,report)
        cache=ai.read(self.root/'ai_supplement.json')
        entry=cache['entries'][self.task['id']]
        self.assertTrue(ai.valid_entry(entry,self.task))
        self.assertEqual(entry['mode'],'deterministic')
        self.assertNotIn('旧的错误摘要',entry['summary'])
        self.assertEqual(cache['lastRun']['failed'],1)
        self.assertEqual(cache['lastRun']['accepted'],0)
        self.assertEqual(cache['lastRun']['fallback'],1)
        self.assertEqual(cache['lastRun']['pendingAfter'],1)
        self.assertTrue((self.root/'report.json').exists())

    def test_publish_rejects_results_if_source_changed_during_inference(self):
        report=ai.run(self.root,ai.MODEL,13,10,self.root/'report.json',self.generate)
        self.data['current']['holdings'][0]['shares']=300
        ai.write(self.root/'data.json',self.data)
        self.assertEqual(ai.merge(self.root,report),0)
        entry=ai.read(self.root/'ai_supplement.json')['entries'][self.task['id']]
        self.assertIn('增持200.0%',entry['summary'])
        self.assertEqual(entry['mode'],'deterministic')
        self.assertEqual(ai.read(self.root/'data.json'),self.data)

    def test_valid_output_does_not_touch_source_files(self):
        before=(self.root/'data.json').read_bytes()
        report=ai.run(self.root,ai.MODEL,13,10,self.root/'report.json',self.generate)
        self.assertEqual(ai.merge(self.root,report),1)
        self.assertEqual((self.root/'data.json').read_bytes(),before)
        self.assertEqual(ai.read(self.root/'ai_supplement.json')['lastRun']['pendingAfter'],0)

    def test_selection_rejects_model_prose_duplicates_foreign_ids_and_empty(self):
        for selection in [{'summary':'增持阿里巴巴'}, {'factIds':['f0'],'summary':'减持AAA'},
                          {'factIds':['unknown']}, {'factIds':['f0','f0']}, {'factIds':[]},
                          {'factIds':[True]}, {'factIds':['f0']*20}]:
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                ai.validate_selection(selection,self.task['facts'])

    def test_tepper_direction_and_percentage_are_bound_to_stock(self):
        self.data['current']={'quarter':'2026 Q2','holdings':[
            {'ticker':'BABA','cnName':'阿里巴巴','shares':2000000,'value':10},
            {'ticker':'META','cnName':'Meta','shares':675000,'value':9}],
            'previousHoldings':[{'ticker':'BABA','shares':3465000,'value':11},
                                {'ticker':'META','shares':436500,'value':8}]}
        ai.write(self.root/'data.json',self.data)
        facts=ai.tasks(self.root)[0]['facts'];selection=ai.fallback_selection(facts)
        text=ai.render_summary(selection,facts)
        self.assertIn('阿里巴巴（BABA）：减持42.3%',text)
        self.assertIn('Meta（META）：增持54.6%',text)
        for bad in [text.replace('减持42.3%','增持42.3%'),text.replace('增持54.6%','增持42.3%'),
                    '增持阿里巴巴，同时对阿里巴巴的减持幅度为42.3%。']:
            with self.assertRaises(ValueError):ai.validate_summary(bad,facts,selection)

    def test_value_weight_is_bound_to_correct_investor_and_metric(self):
        ai.write(self.root/'value_screen.json',{'candidates':[{'ticker':'BN','cnName':'布鲁克菲尔德','investors':[
            {'id':'akre','name':'阿克瑞','weight':10.1,'chg':'trimmed'},
            {'id':'ackman','name':'阿克曼','weight':17.6,'chg':'hold'}]}]})
        task=next(t for t in ai.tasks(self.root) if t['id']=='value')
        selection=ai.fallback_selection(task['facts']);text=ai.render_summary(selection,task['facts'])
        self.assertIn('阿克瑞：布鲁克菲尔德（BN）减持，占其披露组合市值10.1%',text)
        self.assertIn('阿克曼：布鲁克菲尔德（BN）股数不变，占其披露组合市值17.6%',text)
        self.assertNotIn('持股比例',text)
        for bad in [text.replace('组合市值','股权'),text.replace('10.1','17.6'),
                    '布鲁克菲尔德持股10.1%被削减，阿克曼持有17.6%。']:
            with self.assertRaises(ValueError):ai.validate_summary(bad,task['facts'],selection)

    def test_unknown_predecessor_and_micro_change_are_not_new_or_zero(self):
        self.data['current'].pop('previousHoldings')
        ai.write(self.root/'data.json',self.data)
        self.assertIn('未知',ai.tasks(self.root)[0]['facts']['items'][0]['change'])
        self.data['current']['holdings'][0].update(shares=100001,prevShares=100000)
        ai.write(self.root/'data.json',self.data)
        fact=ai.tasks(self.root)[0]['facts']['items'][0]
        self.assertEqual(fact['change'],'增持（微量变动）')
        self.assertNotIn('value',fact)

    def test_failed_record_does_not_starve_other_records(self):
        other={**self.task,'id':'investor:other'}
        cache={'attempts':{self.task['id']:{'at':'2026-09-16'}}}
        self.assertEqual(ai.pending([self.task,other],cache,ai.MODEL)[0]['id'],other['id'])

    def test_mutated_published_text_is_rejected_and_cache_repaired(self):
        entry=ai.make_entry(self.task,self.selection,ai.MODEL)
        entry['summary']=entry['summary'].replace('增持','减持')
        cache={'entries':{self.task['id']:entry}}
        self.assertFalse(ai.valid_entry(entry,self.task))
        ai.ensure_safe_entries(cache,[self.task])
        self.assertIn('增持100.0%',cache['entries'][self.task['id']]['summary'])
        self.assertEqual(cache['entries'][self.task['id']]['mode'],'deterministic')

    def test_model_request_uses_enum_selection_and_no_free_text(self):
        from io import BytesIO
        output={'done':True,'response':json.dumps(self.selection),'total_duration':1000000000,'eval_count':10}
        with patch.object(ai.urllib.request,'urlopen',return_value=BytesIO(json.dumps(output).encode())) as call:
            selection,metrics=ai.generate(self.task,ai.MODEL)
        body=json.loads(call.call_args.args[0].data)
        self.assertFalse(body['think'])
        self.assertEqual(body['options']['num_gpu'],0)
        self.assertEqual(set(body['format']['properties']),{'factIds'})
        self.assertEqual(body['format']['properties']['factIds']['items']['enum'],['f0','f1'])
        self.assertEqual(selection,self.selection)

    def test_invalid_model_selection_falls_back_without_being_counted_as_success(self):
        report=ai.run(self.root,ai.MODEL,13,10,self.root/'report.json',lambda *a:({'factIds':['f999']},{'seconds':1}))
        ai.merge(self.root,report)
        cache=ai.read(self.root/'ai_supplement.json')
        self.assertEqual(cache['lastRun']['accepted'],0)
        self.assertEqual(cache['lastRun']['pendingAfter'],1)
        self.assertTrue(ai.valid_entry(cache['entries'][self.task['id']],self.task))

    def test_fallback_does_not_replace_valid_same_source_model_output(self):
        entry=ai.make_entry(self.task,self.selection,ai.MODEL)
        ai.write(self.root/'ai_supplement.json',{'entries':{self.task['id']:entry}})
        def fail(*a):raise TimeoutError('unavailable')
        report=ai.run(self.root,'other',13,10,self.root/'report.json',fail)
        ai.merge(self.root,report)
        self.assertEqual(ai.read(self.root/'ai_supplement.json')['entries'][self.task['id']],entry)


if __name__ == '__main__': unittest.main()
