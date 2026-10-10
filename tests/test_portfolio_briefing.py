import copy
import json
from pathlib import Path
import unittest

import ai_supplement as ai
from portfolio_briefing import holdings_briefing, changes_briefing, history_briefing, share_clause, pct
from tab_insights import history_source

ROOT=Path(__file__).resolve().parents[1]


def text(b):
    return b['headline'][0]+b['lead'][0]+''.join(d['text'][0] for d in b['details'])+' '.join(n[0] for n in b['notes'])


class PortfolioBriefingTests(unittest.TestCase):
    def test_reading_guides_are_source_bound_and_do_not_turn_disclosures_into_buy_signals(self):
        d=json.loads((ROOT/'data.json').read_text())
        for fn in (holdings_briefing, changes_briefing, history_briefing):
            b=fn(d)
            self.assertEqual(len(b['readerGuide']),2)
            self.assertTrue(all(b['readerGuide']))
        self.assertIn('不等于今天仍值得买入',holdings_briefing(d)['readerGuide'][0])
        self.assertIn('不能证明经理买卖的理由',changes_briefing(d)['readerGuide'][0])
        self.assertIn('不是收益率',history_briefing(d)['readerGuide'][0])
        task=next(t for t in ai.tasks(ROOT) if t['id']=='holdings:lilu')
        entry=ai.make_entry(task,ai.fallback_selection(task['facts']))
        entry['briefing']['readerGuide'][0]='捏造的确定买入建议'
        self.assertFalse(ai.valid_entry(entry,task))

    def test_principal_quantities_are_not_shares_and_tiny_percentages_are_nonzero(self):
        h=dict(ticker='BOND',shareType='PRN',shares=200,prevShares=100,value=300)
        self.assertIn('本金',share_clause(h));self.assertIn('principal',share_clause(h,True))
        self.assertNotEqual(pct(.0000001),'0')

    def test_issuer_share_classes_combine_but_options_do_not(self):
        d={'current':{'quarter':'2026 Q2','holdings':[
            dict(ticker='A',cusip='123456101',shares=10,value=400),
            dict(ticker='B',cusip='123456202',shares=10,value=300),
            dict(ticker='A',cusip='123456101',shares=10,value=100,putCall='PUT'),
            dict(ticker='C',cusip='654321101',shares=10,value=200)]}}
        b=holdings_briefing(d)
        self.assertIn('70.0%',b['details'][0]['text'][0])
        self.assertNotIn('80.0%',b['details'][0]['text'][0])
        self.assertIn('不同股份类别',b['details'][0]['text'][0])
        self.assertIn('不是权利金',text(b))

    def test_tiny_new_position_is_visible_in_holdings_and_quarter_narrative(self):
        d={'current':{'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':[
            dict(ticker='A',shares=100,value=400000),dict(ticker='B',shares=100001,value=350000),
            dict(ticker='C',shares=90,value=249500),dict(ticker='NEW',shares=10,value=500)],
            'previousHoldings':[dict(ticker='A',shares=110,value=440000),dict(ticker='B',shares=100000,value=350000),dict(ticker='C',shares=100,value=260000)]}}
        h=holdings_briefing(d);c=changes_briefing(d)
        self.assertIn('99.95%',h['headline'][0]);self.assertIn('0.05%',h['lead'][0])
        self.assertIn('新仓体量很小',c['lead'][0]);self.assertIn('0.001%',text(c))
        self.assertIn('减持 2 项',c['lead'][0])

    def test_unchanged_shares_with_rising_values_are_not_called_additions(self):
        d={'current':{'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':[dict(ticker='A',shares=10,value=200)],'previousHoldings':[dict(ticker='A',shares=10,value=100)]}}
        b=changes_briefing(d)
        self.assertIn('股数没有变化',b['headline'][0]);self.assertIn('+100.0%',b['lead'][0])
        self.assertIn('不能算作加仓',text(b));self.assertIn('股数没有变化',b['headline'][0])

    def test_rising_reported_value_with_falling_shares_is_explained_as_opposite_directions(self):
        d={'current':{'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':[dict(ticker='A',shares=80,value=150)],'previousHoldings':[dict(ticker='A',shares=100,value=100)]}}
        b=changes_briefing(d)
        self.assertIn('股数减少 20.0%，申报市值却增加 50.0%',text(b))
        self.assertIn('两项方向相反',text(b));self.assertIn('减持 1 项',b['lead'][0])

    def test_split_adjusted_reduction_remains_a_reduction(self):
        d={'current':{'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':[dict(ticker='CVNA',cusip='146869102',shares=400,value=200)],'previousHoldings':[dict(ticker='CVNA',cusip='146869102',shares=100,value=100)]}}
        b=changes_briefing(d)
        self.assertIn('-20.0%',text(b));self.assertIn('拆股后可比',text(b));self.assertIn('减持 1 项',b['lead'][0])

    def test_scope_gaps_and_unverified_values_cannot_get_value_growth(self):
        d={'current':{'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':[dict(ticker='A',shares=10,value=200)],'previousHoldings':[dict(ticker='A',shares=5,value=100)]},'history':{'quarters':['2026 Q1','2026 Q2'],'values':[.0001,.0002]}}
        for meta in [{'snapshotType':'archive'},{'reportingTransition':{'comparisonScopeChanged':True,'fromQuarter':'2026 Q2'}}]:
            d['meta']=meta;b=changes_briefing(d)
            self.assertEqual(b['details'],[]);self.assertNotIn('+100',text(b))
        self.assertNotIn('+100',text(history_briefing(d)))
        d['meta']={};d['current']['valueQuality']='unverified'
        self.assertNotIn('申报市值由',text(changes_briefing(d)))
        self.assertNotIn('集中在少数',text(holdings_briefing(d)))
        d['current'].pop('valueQuality');d['current']['prevQuarter']='2025 Q4'
        self.assertIn('中间季度缺失',text(changes_briefing(d)))

    def test_legacy_missing_cusip_is_not_a_fictitious_portfolio_replacement(self):
        rows=lambda value,cusip=None:[dict(ticker='CORE',shares=10,value=value,**({'cusip':cusip} if cusip else {}))]
        d={'current':{'quarter':'2026 Q2','holdings':rows(200,'123456101')},'history':{'quarters':['2026 Q1','2026 Q2'],'values':[.0001,.0002],'holdings':{'2026 Q1':rows(100),'2026 Q2':rows(200,'123456101')}}}
        b=history_briefing(d)
        self.assertIn('保留 1 项，新增 0 项、退出 0 项',b['headline'][0])
        self.assertIn('CORE',b['details'][0]['text'][0])
        d['history']['holdings']['2026 Q1'][0]['putCall']='CALL'
        self.assertIn('新增 1 项、退出 1 项',history_briefing(d)['headline'][0])

    def test_recent_distribution_correction_invalidates_history_even_if_total_is_unchanged(self):
        d={'current':{'quarter':'2026 Q2','holdings':[dict(ticker='A',shares=10,value=200)]},'history':{'quarters':['2026 Q1'],'values':[.0003],'holdings':{'2026 Q1':[dict(ticker='A',shares=10,value=100),dict(ticker='B',shares=10,value=200)]}}}
        before=history_source(d)
        d['history']['holdings']['2026 Q1'][0]['value']+=1;d['history']['holdings']['2026 Q1'][1]['value']-=1
        self.assertEqual(before['holdings'],history_source(d)['holdings'])
        self.assertNotEqual(before,history_source(d))

    def test_published_narrative_is_recomputed_and_mutations_are_rejected(self):
        t=next(t for t in ai.tasks(ROOT) if t['id']=='investor:lilu')
        e=ai.make_entry(t,ai.fallback_selection(t['facts']))
        self.assertTrue(ai.valid_entry(e,t))
        original=copy.deepcopy(t['facts']['briefing'])
        e['briefing']['lead'][0]='错误数字 999'
        self.assertFalse(ai.valid_entry(e,t));self.assertEqual(t['facts']['briefing'],original)

    def test_model_can_prioritize_evidence_but_cannot_change_numbers_or_drop_sections(self):
        t=next(t for t in ai.tasks(ROOT) if t['id']=='investor:lilu')
        selection=ai.fallback_selection(t['facts']);selection['topicIds']=['t2','t0']
        e=ai.make_entry(t,selection,ai.MODEL)
        self.assertTrue(ai.valid_entry(e,t))
        self.assertEqual(e['briefing']['headline'],t['facts']['briefing']['headline'])
        self.assertEqual(e['briefing']['lead'],t['facts']['briefing']['lead'])
        self.assertEqual(e['briefing']['details'],[t['facts']['briefing']['details'][i] for i in [2,0,1]])
        for ids in [['t999'],['t0','t0'],['<script>'],[],[True]]:
            with self.subTest(ids=ids),self.assertRaises(ValueError):ai.make_entry(t,{**selection,'topicIds':ids},ai.MODEL)


if __name__=='__main__':unittest.main()
