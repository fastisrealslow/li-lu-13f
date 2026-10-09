import copy
import json
from pathlib import Path
import unittest

import ai_supplement as ai
from tab_insights import holdings_facts, history_facts, holdings_source, history_source


class TabInsightsTests(unittest.TestCase):
    def sample(self):
        return {'current':{'quarter':'2026 Q2','holdings':[{'ticker':'CORE','cusip':'ONE','shares':100,'value':300},
                {'ticker':'OPT','cusip':'TWO','shares':20,'value':100,'putCall':'PUT'}]},
                'history':{'quarters':['2025 Q4','2026 Q1','2026 Q2'],'values':[.0002,.0003,.0004],
                'holdings':{q:[{'ticker':'CORE','cusip':'ONE','shares':100,'value':v}] for q,v in [('2025 Q4',200),('2026 Q1',300),('2026 Q2',400)]}}}

    def test_scopes_have_different_facts_and_preserve_option_limitation(self):
        d=self.sample();current=holdings_facts(d,'Test');history=history_facts(d,'Test')
        self.assertNotEqual(current['items'],history['items'])
        text=''.join(i['text'][0] for i in current['items'])
        self.assertIn('PUT 1 项',text);self.assertIn('75.0%',text);self.assertIn('不能当作期权权利金',text)
        selection=ai.fallback_selection(current)
        self.assertTrue(set(current['requiredIds'])<=set(selection['factIds']))
        with self.assertRaises(ValueError):ai.validate_selection({'factIds':['f0']},current)

    def test_history_streak_stops_at_missing_quarter_and_type_change(self):
        d=self.sample()
        self.assertIn('连续出现在 3 个',str(history_facts(d,'Test')))
        del d['history']['holdings']['2026 Q1']
        self.assertNotIn('连续出现在 3 个',str(history_facts(d,'Test')))
        d=self.sample();d['history']['holdings']['2026 Q1'][0]['putCall']='CALL'
        self.assertNotIn('连续出现在 3 个',str(history_facts(d,'Test')))

    def test_scope_change_never_reports_growth_and_gap_is_required(self):
        d=self.sample();d['meta']={'reportingTransition':{'comparisonScopeChanged':True,'fromQuarter':'2026 Q2'}}
        facts=history_facts(d,'Test');text=''.join(i['text'][0] for i in facts['items'])
        self.assertIn('申报范围在 2026 Q2 改变',text)
        self.assertNotIn('披露市值从',text);self.assertNotIn('变化 +',text)
        self.assertNotIn('连续出现在 3 个',text)
        self.assertTrue(facts['requiredIds'])
        d=self.sample();d['history']['excludedValueQuarters']=['2026 Q1']
        facts=history_facts(d,'Test');summary=ai.render_summary(ai.fallback_selection(facts),facts)
        self.assertIn('缺少或排除',summary);self.assertIn('2026 Q1',summary)

    def test_unverified_values_and_archives_are_not_current_value_analysis(self):
        d=self.sample();d['current']['valueQuality']='units_unverified'
        facts=holdings_facts(d,'Test');self.assertNotIn('75.0%',str(facts));self.assertIn('暂不解读金额',str(facts))
        d=self.sample();d['meta']={'snapshotType':'historical'}
        self.assertIn('不是当前完整组合',str(holdings_facts(d,'Test')))
        d['history']['verification']={'status':'unverified'}
        self.assertEqual(history_facts(d,'Test')['items'],[])

    def test_sources_follow_relevant_data_and_published_facts_cannot_be_altered(self):
        d=self.sample();before=copy.deepcopy(d)
        hsrc=holdings_source(d);tsrc=history_source(d)
        d['history']['holdings']['2025 Q4'][0]['value']=201
        self.assertEqual(hsrc,holdings_source(d));self.assertNotEqual(tsrc,history_source(d))
        self.assertEqual(before['current'],d['current'])
        root=Path(__file__).resolve().parents[1]
        task=next(t for t in ai.tasks(root) if t['id']=='holdings:lilu')
        entry=ai.make_entry(task,ai.fallback_selection(task['facts']))
        self.assertTrue(ai.valid_entry(entry,task))
        entry['facts']['items'][0]['text'][0]='错误数字 999'
        # The artifact holds a separate copy during serialization/publication.
        clean=next(t for t in ai.tasks(root) if t['id']=='holdings:lilu')
        self.assertFalse(ai.valid_entry(entry,clean))


if __name__=='__main__':unittest.main()
