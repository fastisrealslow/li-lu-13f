import copy,contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import fetch_prices_all
from holdings_diff import compare_holdings

class CostCalculationTests(unittest.TestCase):
    def test_a_reported_split_is_not_an_increase_in_the_position(self):
        current=dict(ticker='TEST',cusip='1',shares=90,value=900,shareAdjustment={'factor':10,'date':'2026-06-12','source':'https://finance.yahoo.com/quote/TEST/','sourceKind':'market_share_split','fromQuarter':'2026 Q1','toQuarter':'2026 Q2','reportedShares':10})
        old=dict(ticker='TEST',cusip='1',shares=10,value=100)
        row=compare_holdings([current],[old],previous_quarter='2026 Q1',current_quarter='2026 Q2')[0]
        self.assertEqual(row['prevShares'],100);self.assertEqual(row['shares'],90)
        self.assertEqual(current['shares'],90)
        current['shareAdjustment']['source']='https://unrelated.example/quote/TEST/'
        self.assertEqual(compare_holdings([current],[old],previous_quarter='2026 Q1',current_quarter='2026 Q2')[0]['prevShares'],10)

    def test_quarter_price_windows_have_explicit_utc_boundaries(self):
        from datetime import datetime,timezone
        start,end=fetch_prices_all.quarter_ts('2026 Q2')
        self.assertEqual(datetime.fromtimestamp(start,timezone.utc).isoformat(),'2026-04-01T00:00:00+00:00')
        self.assertEqual(datetime.fromtimestamp(end,timezone.utc).isoformat(),'2026-06-30T23:59:59+00:00')

    def test_provider_split_uses_quote_basis_without_mutating_filed_shares(self):
        h=dict(ticker='TEST',cusip='123456789',shares=100,value=1000)
        raw={'2020 Q2':[h],'2020 Q3':[{**h,'shares':400}],'2026 Q2':[{**h,'shares':400}]}
        quotes={'TEST':{'shareActions':[{'date':'2020-08-31','factor':4},{'date':'2026-07-01','factor':2}]}}
        rows=fetch_prices_all.comparable_price_history(raw,'2026 Q2',quotes)
        self.assertEqual([rows[q][0]['shares'] for q in raw],[800,800,800])
        self.assertEqual(raw['2020 Q2'][0]['shares'],100)
        self.assertEqual(rows['2020 Q2'][0]['value'],1000)

    def test_exchange_ex_date_and_issuer_distribution_date_are_one_split(self):
        h=dict(ticker='GOOG',cusip='02079K107',shares=100,value=1000)
        rows=fetch_prices_all.comparable_price_history({'2022 Q2':[h]},'2026 Q2',{'GOOG':{'shareActions':[{'date':'2022-07-18','factor':20}]}})
        self.assertEqual(rows['2022 Q2'][0]['shares'],2000)

    def test_prefix_backfill_does_not_change_cost_but_an_internal_gap_does(self):
        holding=dict(cusip='1',shares=100,value=10000)
        history={'2026 Q1':[holding],'2026 Q2':[holding]}
        original=fetch_prices_all.cost_history_fingerprint(history)
        self.assertEqual(fetch_prices_all.cost_history_fingerprint({'2025 Q4':[],**history}),original)
        self.assertNotEqual(fetch_prices_all.cost_history_fingerprint({**history,'2026 Q1':[]}),original)

    def test_historical_corrections_invalidate_cost_cache_but_descriptions_do_not(self):
        history={'2026 Q1':[{'cusip':'1','shares':100,'value':10000,'cnName':'旧名称'}]}
        before=fetch_prices_all.cost_history_fingerprint(history)
        history['2026 Q1'][0]['cnName']='新名称'
        self.assertEqual(fetch_prices_all.cost_history_fingerprint(history),before)
        history['2026 Q1'][0]['shares']=200
        self.assertNotEqual(fetch_prices_all.cost_history_fingerprint(history),before)

    def calculate(self,holding,history,meta=None):
        snapshot={'meta':meta or {},'current':{'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':[holding]},'history':{'holdings':history}}
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp)/'data.json';prices=Path(tmp)/'prices.json';data.write_text(json.dumps(snapshot))
            with patch.object(fetch_prices_all,'finnhub',return_value={'c':100,'h':100,'l':100,'o':100,'pc':100,'t':1}),patch.object(fetch_prices_all,'yahoo_chart',return_value={'closes':[100],'lows':[100],'highs':[100]}),patch.object(fetch_prices_all.time,'sleep'),contextlib.redirect_stdout(io.StringIO()):
                fetch_prices_all.fetch_us('test',{'data':str(data),'prices':str(prices)})
            return json.loads(prices.read_text())['costBasis'][holding['ticker']]

    def test_expanded_scope_has_a_price_reference_without_inventing_a_purchase(self):
        h=dict(ticker='TEST',cusip='test',shares=20,value=2000,putCall='',shareType='SH')
        cost=self.calculate(h,{'2026 Q1':[{**h,'shares':10}],'2026 Q2':[h]},
                            {'reportingTransition':{'fromQuarter':'2026 Q2','comparisonScopeChanged':True}})
        self.assertEqual(cost['recent']['buy'],100)
        self.assertEqual(cost['recent']['kind'],'scope_initial')
        self.assertEqual(cost['allTime']['first'],'2026 Q2')
        self.assertEqual(cost['allTime']['buy_quarters'],1)

    def test_verified_same_manager_history_keeps_its_original_cost_run(self):
        h=dict(ticker='TEST',cusip='test',shares=20,value=2000,putCall='',shareType='SH')
        with patch('reporting_scope.same_manager_history',return_value=True):
            cost=self.calculate(h,{'2026 Q1':[h],'2026 Q2':[h]}, {'reportingTransition':{'fromQuarter':'2026 Q2','comparisonScopeChanged':True}})
        self.assertEqual(cost['allTime']['first'],'2026 Q1')
        self.assertEqual(cost['recent']['quarter'],'2026 Q1')
        self.assertNotIn('kind',cost['recent'])

    def test_reentry_resets_last_buying_quarter_and_buy_count(self):
        holding=dict(ticker='TEST',cusip='test',shares=20,value=2000,prevShares=20,putCall='',shareType='SH')
        history={'2020 Q1':[{**holding,'shares':100}], '2020 Q2':[{**holding,'shares':200}], '2025 Q1':[], '2025 Q2':[{**holding,'shares':50}], '2025 Q3':[{**holding,'shares':30}], '2025 Q4':[{**holding,'shares':30}], '2026 Q1':[holding], '2026 Q2':[holding]}
        cost=self.calculate(holding,history)
        self.assertEqual(cost['recent']['quarter'],'2025 Q2')
        self.assertEqual(cost['allTime']['first'],'2025 Q2')
        self.assertEqual(cost['allTime']['buy_quarters'],1)
        # A zero-position quarter breaks continuity in both calculations.
        self.assertEqual(cost['recent']['quarter'],cost['allTime']['first'])

    def test_option_rows_do_not_change_the_ordinary_share_estimate(self):
        h=dict(ticker='TEST',cusip='test',shares=20,value=2000,prevShares=20,putCall='',shareType='SH')
        history={'2026 Q1':[h,{**h,'putCall':'CALL','shares':500}], '2026 Q2':[h]}
        cost=self.calculate(h,history);self.assertEqual(cost['recent']['quarter'],'2026 Q1');self.assertEqual(cost['allTime']['buy_quarters'],1)

    def test_alphabet_split_does_not_look_like_net_buying_or_mutate_raw_reports(self):
        old=dict(ticker='GOOG',cusip='02079K107',shares=10,value=20000,putCall='',shareType='SH')
        new={**old,'shares':200,'value':20000}
        history={'2022 Q2':[old],'2022 Q3':[new],'2026 Q1':[new],'2026 Q2':[new]};original=copy.deepcopy(history)
        adjusted=fetch_prices_all.comparable_price_history(history,'2026 Q2')
        self.assertEqual(adjusted['2022 Q2'][0]['shares'],200);self.assertEqual(history,original)
        rows=compare_holdings([new],[old],previous_quarter='2022 Q2',current_quarter='2022 Q3');self.assertEqual(rows[0]['prevShares'],200)


    def test_unverified_amount_quarter_keeps_shares_and_never_invents_reentry(self):
        h=dict(ticker='TEST',cusip='test',shares=20,value=2000,putCall='',shareType='SH')
        history={'2025 Q3':[h],'2025 Q4':[{**h,'value':2}],'2026 Q1':[h],'2026 Q2':[h]}
        snapshot={'meta':{},'current':{'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':[h]},'history':{'holdings':history,'excludedValueQuarters':['2025 Q4']}}
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp)/'data.json';prices=Path(tmp)/'prices.json';data.write_text(json.dumps(snapshot))
            with patch.object(fetch_prices_all,'finnhub',return_value={'c':100,'h':100,'l':100,'o':100,'pc':100,'t':1}),patch.object(fetch_prices_all,'yahoo_chart',return_value={'closes':[100],'lows':[100],'highs':[100]}),patch.object(fetch_prices_all.time,'sleep'),contextlib.redirect_stdout(io.StringIO()):
                fetch_prices_all.fetch_us('test',{'data':str(data),'prices':str(prices)})
            cost=json.loads(prices.read_text())['costBasis']['TEST']
            self.assertEqual(cost['recent']['quarter'],'2025 Q3')
            self.assertIsNone(cost['allTime']);self.assertEqual(cost['averageUnavailable'],'units')
