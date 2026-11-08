import copy
import unittest
from unittest.mock import patch
from trade_price_history import calculate, candle_estimates, build, exit_performance

class TradePricesTests(unittest.TestCase):
    def test_existing_price_weights_and_weighted_buys_sales(self):
        price=candle_estimates({'closes':[100,120],'lows':[80,90],'highs':[130,140]})
        self.assertEqual(price['buy'],89);self.assertEqual(price['sell'],131)
        rows={'2025 Q4':{'shares':0},'2026 Q1':{'shares':10},'2026 Q2':{'shares':20},'2026 Q3':{'shares':15},'2026 Q4':{'shares':0}}
        out=calculate(rows,{'2026 Q1':{'buy':10},'2026 Q2':{'buy':20},'2026 Q3':{'sell':30},'2026 Q4':{'sell':40}})
        self.assertEqual(out['averageBuy'],15);self.assertEqual(out['averageSell'],37.5)
        self.assertEqual(out['quarters'][2]['averageCost'],15)
        self.assertEqual(out['quarters'][3]['costBeforeSale'],15)
        self.assertEqual(out['quarters'][3]['quarter'],'2026 Q4')

    def test_exit_is_next_complete_quarter_not_last_held_quarter(self):
        result=calculate({'2026 Q1':{'shares':10},'2026 Q2':{'shares':0}}, {'2026 Q1':{'buy':10,'sell':99},'2026 Q2':{'sell':20}})
        ledger={'entries':{'id':{'ticker':'TEST',**result}}}
        self.assertEqual(exit_performance(ledger)['TEST']['exitQuarter'],'2026 Q2')
        self.assertEqual(exit_performance(ledger)['TEST']['exitPrice'],20)

    def test_missing_quarter_does_not_invent_exit_or_purchase(self):
        out=calculate({'2025 Q4':{'shares':10},'2026 Q2':{'shares':0},'2026 Q3':{'shares':5}}, {'2025 Q4':{'buy':10},'2026 Q2':{'sell':100},'2026 Q3':{'buy':20}})
        self.assertEqual([r['action'] for r in out['quarters']],['observed','new'])
        self.assertIsNone(out['averageSell'])
        out=calculate({'2025 Q4':{'shares':10},'2026 Q2':{'shares':20}}, {'2025 Q4':{'buy':10},'2026 Q2':{'buy':20}})
        self.assertEqual(out['quarters'][-1]['action'],'observed')
        self.assertEqual(out['quarters'][-1]['averageCost'],20)

    def test_partial_price_coverage_never_presents_a_complete_average(self):
        out=calculate({'2026 Q1':{'shares':10},'2026 Q2':{'shares':20},'2026 Q3':{'shares':5},'2026 Q4':{'shares':0}}, {'2026 Q1':{'buy':10},'2026 Q3':{'sell':30}})
        self.assertIsNone(out['averageBuy']);self.assertIsNone(out['averageSell'])
        self.assertIsNone(out['quarters'][2]['averageCost'])
        self.assertEqual(out['missingBuyQuarters'],1);self.assertEqual(out['missingSellQuarters'],1)

    def test_reentry_resets_holding_cost_and_retains_prior_sales(self):
        out=calculate({'2025 Q4':{'shares':10},'2026 Q1':{'shares':0},'2026 Q2':{'shares':5}}, {'2025 Q4':{'buy':10},'2026 Q1':{'sell':30},'2026 Q2':{'buy':40}})
        self.assertEqual(out['quarters'][-1]['averageCost'],40)
        self.assertEqual(out['averageSell'],30)
        self.assertEqual(exit_performance({'entries':{'x':{'ticker':'T',**out}}}),{})

    def test_short_recent_series_does_not_block_older_missing_quarters(self):
        import batch_market_data as market
        from fetch_prices_all import quarter_ts
        h=dict(ticker='TEST',cusip='123456789',cls='COM',shares=10,value=100)
        data={'current':{'quarter':'2026 Q2','holdings':[h]},'history':{'holdings':{'2025 Q4':[h],'2026 Q1':[h]}}}
        recent={'timestamps':[quarter_ts('2026 Q1')[0]],'values':{'close':[10],'high':[12],'low':[8]}}
        calls=[]
        def loader(ticker,start):
            calls.append((ticker,start))
            return {'timestamps':[quarter_ts('2025 Q4')[0]+86400],'values':{'close':[10],'high':[12],'low':[8]}},{'shareActions':[]}
        with patch.dict(market.SERIES,{'TEST':recent},clear=True):
            out=build(data,{},download_limit=1,loader=loader,refresh_quotes=False)
        self.assertEqual(len(calls),1)
        self.assertEqual(out['entries']['123456789']['averageBuy'],8.6)

    def test_corrected_symbol_retries_even_when_old_symbol_failed_today(self):
        from datetime import datetime,timezone
        import batch_market_data as market
        from fetch_prices_all import quarter_ts
        h=dict(ticker='NEW',cusip='123456789',cls='COM',shares=10,value=100)
        data={'current':{'quarter':'2026 Q2','holdings':[h]},'history':{'holdings':{'2026 Q1':[h]}}}
        previous={'version':1,'entries':{'123456789':{'ticker':'WRONG','checkedAt':datetime.now(timezone.utc).isoformat()}}}
        calls=[]
        def loader(ticker,start):
            calls.append(ticker)
            return {'timestamps':[quarter_ts('2026 Q1')[0]+86400],'values':{'close':[10],'high':[12],'low':[8]}},{'shareActions':[]}
        with patch.dict(market.SERIES,{},clear=True):
            out=build(data,{},previous,download_limit=1,loader=loader,refresh_quotes=False)
        self.assertEqual(calls,['NEW']);self.assertEqual(out['entries']['123456789']['averageBuy'],8.6)

    def test_historical_prices_cannot_clear_confirmed_retirement(self):
        h=dict(ticker='OLD',cusip='123456789',cls='COM',shares=10,value=100)
        data={'current':{'quarter':'2026 Q2','holdings':[h]},'history':{'holdings':{}}}
        event={'ticker':'OLD','status':'ceased_trading','effectiveDate':'2026-07-01'}
        quotes={'OLD':{'c':10,'t':1000}}
        with patch('security_lifecycle.event_for',return_value=event):
            build(data,quotes,download_limit=0)
        self.assertEqual(quotes['OLD']['status'],'ceased_trading')
        self.assertEqual(quotes['OLD']['event'],event)

    def test_split_before_first_holding_does_not_redownload_complete_history(self):
        h=dict(ticker='TEST',cusip='123456789',cls='COM',shares=10,value=100)
        data={'current':{'quarter':'2026 Q2','holdings':[h]},'history':{'holdings':{'2026 Q1':[h]}}}
        with patch('batch_market_data.window',return_value=(True,{'closes':[10],'highs':[12],'lows':[8]})):
            prior=build(data,{},download_limit=0)
        quotes={'TEST':{'shareActions':[{'date':'2000-01-01','factor':2}]}}
        with patch('batch_market_data.window',return_value=(False,None)):
            result=build(data,quotes,prior,download_limit=0)
        self.assertEqual(result['entries']['123456789']['averageBuy'],8.6)

    def test_invalid_candles_are_rejected(self):
        for c in [None,{}, {'closes':[float('nan')],'lows':[1],'highs':[2]}, {'closes':[1],'lows':[0],'highs':[2]}]:
            self.assertIsNone(candle_estimates(c))

    def test_build_preserves_identity_and_excludes_options_and_warrants(self):
        h=dict(ticker='TEST',cusip='123456789',cls='COM',shares=100,value=1000)
        snapshot={'current':{'quarter':'2026 Q2','holdings':[h]},'history':{'holdings':{'2026 Q1':[h], '2026 Q2':[h,{**h,'cusip':'option','putCall':'Put'},{**h,'cusip':'warrant','cls':'WARRANT'}]}}}
        before=copy.deepcopy(snapshot)
        with patch('batch_market_data.window',return_value=(True,{'closes':[10],'highs':[12],'lows':[8]})):
            out=build(snapshot,{},download_limit=0)
        self.assertEqual(set(out['entries']),{'123456789'})
        self.assertEqual(snapshot,before)
        self.assertEqual(out['entries']['123456789']['averageBuy'],8.6)

    def test_split_does_not_create_trade_and_cached_price_basis_invalidates(self):
        h=dict(ticker='TEST',cusip='123456789',cls='COM',shares=10,value=1000)
        snapshot={'current':{'quarter':'2026 Q2','holdings':[{**h,'shares':20}]},'history':{'holdings':{'2026 Q1':[h]}}}
        quotes={'TEST':{'shareActions':[{'date':'2026-04-02','factor':2}]}}
        with patch('batch_market_data.window',return_value=(True,{'closes':[10],'highs':[12],'lows':[8]})):
            out=build(snapshot,quotes,download_limit=0)
        self.assertEqual(out['entries'][h['cusip']]['quarters'][-1]['action'],'hold')
        self.assertIsNone(out['entries'][h['cusip']]['averageSell'])

    def test_economic_adjustment_is_not_treated_as_a_split_or_reliable_old_cost(self):
        h=dict(ticker='TEST',cusip='123456789',cls='COM',shares=10,value=1000)
        snapshot={'current':{'quarter':'2026 Q2','holdings':[h]},'history':{'holdings':{'2026 Q1':[h]}}}
        quotes={'TEST':{'shareActions':[{'date':'2026-04-02','factor':1.2345}]}}
        with patch('batch_market_data.window',return_value=(True,{'closes':[10],'highs':[12],'lows':[8]})):
            out=build(snapshot,quotes,download_limit=0)
        entry=out['entries'][h['cusip']]
        self.assertIsNone(entry['averageBuy']);self.assertIsNone(entry['quarters'][-1]['averageCost'])
