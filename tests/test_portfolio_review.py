import copy
import unittest
from holdings_diff import compare_holdings,consolidate_holdings
from portfolio_review import review,investor_facts
from ai_supplement import fallback_selection,validate_selection,investor_source
from enrich_metadata import _ticker_quarter_series,_analyze_holding_pattern,_gen_verdict


class PortfolioReviewTests(unittest.TestCase):
    def test_stock_context_keeps_opposite_directions_and_does_not_invent_conviction(self):
        mixed={'holders':[{'investor':'Test','chg':'added','weight':5},{'investor':'Other','chg':'trimmed','weight':2}]}
        zh,en=_gen_verdict(mixed,'深度折价')
        self.assertIn('有人增加股数、有人减少股数',zh)
        self.assertIn('opposing share-count directions',en)
        zh,en=_gen_verdict({'holders':[{'investor':'Test','chg':'new','weight':.4}]},'深度折价')
        self.assertIn('0.4%',zh);self.assertNotIn('更像是试探性布局',zh)
        self.assertNotIn('signals very strong conviction',en)

    def test_cost_record_span_is_not_a_verified_continuous_holding_record(self):
        zh,en=_gen_verdict({'holders':[{'investor':'Test','chg':'hold','weight':4,'hold_quarters':8}]},'深度折价')
        self.assertIn('8 个季度',zh);self.assertIn('时间跨度不证明连续持仓',zh)
        self.assertNotIn('8 个可核实季度',zh)
        self.assertIn('does not prove continuous holdings',en)

    def test_discretion_rows_are_grouped_before_matching(self):
        current=[dict(ticker='A',cusip='1',shares=40,value=400),dict(ticker='A',cusip='1',shares=50,value=500)]
        previous=[dict(ticker='A',cusip='1',shares=100,value=1000)]
        result=compare_holdings(current,previous)
        self.assertEqual(len(result),1)
        self.assertEqual((result[0]['shares'],result[0]['prevShares']),(90,100))
        self.assertFalse(result[0].get('exited'))
        self.assertEqual(sum(h['value'] for h in consolidate_holdings(current)),900)

    def test_put_call_equity_and_principal_are_distinct(self):
        common=dict(ticker='A',cusip='1',shares=10,value=100)
        rows=compare_holdings([{**common,'putCall':'Put'},{**common,'putCall':'Call'},{**common,'shareType':'PRN'}],[common])
        self.assertEqual(len(rows),4)
        self.assertEqual(sum(h.get('exited',False) for h in rows),1)
        self.assertTrue(all(h['prevShares']==0 for h in rows[:3]))

    def test_smallest_cut_and_all_exits_are_counted_and_candidates_cover_directions(self):
        large=[dict(ticker=f'ADD{i}',shares=110,value=10000-i,prevShares=100) for i in range(30)]
        data={'current':{'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':large+[dict(ticker='TINY',shares=99999,value=1),dict(ticker='NEW',shares=1,value=1)],
            'previousHoldings':[dict(ticker=h['ticker'],shares=100,value=h['value']) for h in large]+[dict(ticker='TINY',shares=100000,value=2),dict(ticker='EXIT',shares=1,value=1)]}}
        facts=investor_facts(data,'测试')
        self.assertEqual(facts['stats'],dict(new=1,added=30,trimmed=1,exited=1,hold=0,unknown=0))
        self.assertEqual({f['category'] for f in facts['items']},{'new','added','trimmed','exited'})
        self.assertIn('微量变动',next(f['change'] for f in facts['items'] if f['ticker']=='TINY'))
        selected=fallback_selection(facts);validate_selection(selected,facts)
        with self.assertRaises(ValueError):validate_selection({'factIds':[facts['items'][0]['id']]},facts)

    def test_changed_scope_and_missing_quarter_cannot_be_called_trades(self):
        data={'meta':{'reportingTransition':{'fromQuarter':'2026 Q2','comparisonScopeChanged':True}},'current':{
            'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':[dict(ticker='A',shares=200,value=200)],'previousHoldings':[dict(ticker='A',shares=100,value=100)]}}
        self.assertEqual(review(data)['stats']['unknown'],1)
        source=investor_source(data);data['meta']={}
        self.assertNotEqual(source,investor_source(data))
        data['current']['prevQuarter']='2025 Q4'
        self.assertEqual(review(data)['state'],'gap')
        self.assertEqual(review(data)['stats']['added'],0)

    def test_missing_previous_and_empty_previous_are_different(self):
        data={'current':{'quarter':'2026 Q2','holdings':[dict(ticker='A',shares=10,value=10)]}}
        self.assertEqual(review(data)['stats']['unknown'],1)
        data['current']['previousHoldings']=[]
        self.assertEqual(review(data)['stats']['new'],1)

    def test_trends_need_consecutive_reports_and_reentry_needs_explicit_absence(self):
        self.assertEqual(_analyze_holding_pattern([('2025 Q1',100),('2025 Q3',200),('2026 Q2',300)])['trend'],'stable')
        self.assertFalse(_analyze_holding_pattern([('2024 Q1',10),('2026 Q1',10)])['reentry'])
        self.assertTrue(_analyze_holding_pattern([('2025 Q1',10),('2025 Q2',0),('2025 Q3',10)])['reentry'])
        data={'current':{'quarter':'2026 Q2'},'meta':{'shareActions':[{'ticker':'CVNA','cusip':'1','quarter':'2026 Q2','factor':5}]},'history':{
            'quarters':['2025 Q4','2026 Q1','2026 Q2'],'holdings':{'2025 Q4':[dict(ticker='CVNA',shares=100)],'2026 Q1':[dict(ticker='CVNA',shares=100)],'2026 Q2':[dict(ticker='CVNA',shares=490)]}}}
        series=_ticker_quarter_series(data,'CVNA')
        self.assertEqual(series,[('2025 Q4',500),('2026 Q1',500),('2026 Q2',490)])
        self.assertEqual(_analyze_holding_pattern(series)['trend'],'stable')
