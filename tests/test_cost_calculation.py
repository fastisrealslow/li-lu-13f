import copy,contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import fetch_prices_all
from holdings_diff import compare_holdings

class CostCalculationTests(unittest.TestCase):
    def test_historical_corrections_invalidate_cost_cache_but_descriptions_do_not(self):
        history={'2026 Q1':[{'cusip':'1','shares':100,'value':10000,'cnName':'旧名称'}]}
        before=fetch_prices_all.cost_history_fingerprint(history)
        history['2026 Q1'][0]['cnName']='新名称'
        self.assertEqual(fetch_prices_all.cost_history_fingerprint(history),before)
        history['2026 Q1'][0]['shares']=200
        self.assertNotEqual(fetch_prices_all.cost_history_fingerprint(history),before)

    def calculate(self,holding,history):
        snapshot={'meta':{},'current':{'quarter':'2026 Q2','prevQuarter':'2026 Q1','holdings':[holding]},'history':{'holdings':history}}
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp)/'data.json';prices=Path(tmp)/'prices.json';data.write_text(json.dumps(snapshot))
            with patch.object(fetch_prices_all,'finnhub',return_value={'c':100,'h':100,'l':100,'o':100,'pc':100,'t':1}),patch.object(fetch_prices_all,'yahoo_chart',return_value={'closes':[100],'lows':[100],'highs':[100]}),patch.object(fetch_prices_all.time,'sleep'),contextlib.redirect_stdout(io.StringIO()):
                fetch_prices_all.fetch_us('test',{'data':str(data),'prices':str(prices)})
            return json.loads(prices.read_text())['costBasis'][holding['ticker']]

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

