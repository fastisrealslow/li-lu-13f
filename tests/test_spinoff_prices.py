import json
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

import spinoff_price_refresh as prices


class SpinoffPriceTests(unittest.TestCase):
    def setUp(self):
        prices._historical_price.cache_clear()
        prices._latest_price.cache_clear()
    def test_yahoo_hk_symbols_keep_at_least_four_digits(self):
        for original, expected in {
            "00656.HK": "0656.HK", "656.HK": "0656.HK",
            "00041.HK": "0041.HK", "19.HK": "0019.HK",
            "07618.HK": "7618.HK", "0656.HK": "0656.HK",
            "41.hk": "0041.HK", "80011.HK": "80011.HK",
            "AAPL": "AAPL", "600000.SS": "600000.SS",
        }.items():
            with self.subTest(symbol=original):
                self.assertEqual(prices.normalize_ticker(original), expected)

    def test_historical_and_latest_downloads_use_normalized_symbol(self):
        frame = pd.DataFrame({"Close": [10.0, 12.0]})
        with patch.object(prices.yf, "download", return_value=frame) as download:
            self.assertEqual(prices.fetch_price_on_date("00656.HK", "2026-08-01"), 10)
            self.assertEqual(prices.fetch_price_latest("656.HK"), 12)
        self.assertEqual([c.args[0] for c in download.call_args_list], ["0656.HK"] * 2)

    def test_quote_fallback_and_market_cap_use_normalized_symbol(self):
        ticker = Mock(info={"currentPrice": 12, "marketCap": 10000000000})
        with patch.object(prices.yf, "download", return_value=pd.DataFrame()), \
                patch.object(prices.yf, "Ticker", return_value=ticker) as lookup:
            self.assertEqual(prices.fetch_price_latest("00041.HK"), 12)
            self.assertEqual(prices.fetch_target_market_cap("00041.HK"), 12.8)
        self.assertEqual([c.args[0] for c in lookup.call_args_list], ["0041.HK"] * 2)

    def test_parent_refresh_skips_non_hk_without_reusing_previous_symbol(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spinoff.json"
            companies = [
                {"ticker": symbol, "firstDate": "2026-08-01"}
                for symbol in ["AAPL", "00656.HK", "MSFT", "00041.HK"]
            ]
            path.write_text(json.dumps({"companies": companies}))
            with patch.object(prices, "SPINOFF_JSON", path), \
                    patch.object(prices, "fetch_price_on_date", return_value=10) as historic, \
                    patch.object(prices, "fetch_price_latest", return_value=12) as latest:
                self.assertEqual(prices.refresh_hk_parent_priceperf(), 2)
            self.assertEqual([c.args[0] for c in historic.call_args_list], ["0656.HK", "0041.HK"])
            self.assertEqual([c.args[0] for c in latest.call_args_list], ["0656.HK", "0041.HK"])
            result = json.loads(path.read_text())["companies"]
            self.assertNotIn("pricePerf", result[0])
            self.assertNotIn("pricePerf", result[2])
            self.assertEqual(result[1]["pricePerf"]["changePct"], 20)

    def test_historical_empty_response_is_requested_once_not_fifteen_times(self):
        with patch.object(prices.yf,'download',return_value=pd.DataFrame()) as download:
            self.assertIsNone(prices.fetch_price_on_date('00041.HK','2026-08-01'))
        download.assert_called_once()
        self.assertEqual(download.call_args.kwargs['start'],'2026-07-25')
        self.assertEqual(download.call_args.kwargs['end'],'2026-08-10')

    def test_historical_window_prefers_following_close_then_nearest_prior(self):
        frame=pd.DataFrame({'Close':[9,10,12,13]},index=pd.to_datetime(['2026-07-30','2026-07-31','2026-08-03','2026-08-04']).tz_localize('Asia/Hong_Kong'))
        for data,expected in [(frame,12),(frame.iloc[:2],10)]:
            prices._historical_price.cache_clear()
            with self.subTest(expected=expected),patch.object(prices.yf,'download',return_value=data) as request:
                self.assertEqual(prices.fetch_price_on_date('0041.HK','2026-08-01'),expected)
                request.assert_called_once()

    def test_invalid_prices_are_never_published_and_latest_can_fall_back(self):
        frame=pd.DataFrame({'Close':[float('inf')]})
        with patch.object(prices.yf,'download',return_value=frame),patch.object(prices.yf,'Ticker',return_value=Mock(info={'currentPrice':12})):
            self.assertIsNone(prices.fetch_price_on_date('0041.HK','2026-08-01'))
            self.assertEqual(prices.fetch_price_latest('0041.HK'),12)
        for value in [float('nan'),float('inf'),-1,0,None,'unavailable']:
            self.assertIsNone(prices.positive_price(value))

    def test_failed_name_database_is_retried_and_never_saved_as_empty_success(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);hk=root/'hk.json';a=root/'a.json'
            hk.write_text('{"0041.HK":"GREAT EAGLE"}');a.write_text('{}')
            provider=Mock(side_effect=[ValueError('empty upstream response'),pd.DataFrame([['600000','测试公司']])])
            with patch.object(prices,'BKTEST_DIR',root),patch.object(prices,'HK_DB_PATH',hk),patch.object(prices,'A_DB_PATH',a),patch.dict('sys.modules',{'akshare':SimpleNamespace(stock_info_a_code_name=provider)}):
                prices.ensure_dbs();self.assertEqual(a.read_text(),'{}')
                prices.ensure_dbs();self.assertEqual(prices.read_stock_db(a)['600000.SS'],'测试公司')
            self.assertEqual(provider.call_count,2)

    def test_missing_market_database_does_not_break_an_available_market(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);hk=root/'hk.json';a=root/'a.json';a.write_text('{"600000.SS":"测试公司"}')
            with patch.object(prices,'BKTEST_DIR',root),patch.object(prices,'HK_DB_PATH',hk),patch.object(prices,'A_DB_PATH',a),patch.object(prices,'_hk_names',None),patch.object(prices,'_a_names',None),patch.dict('sys.modules',{'openpyxl':SimpleNamespace()}),patch('requests.get',side_effect=TimeoutError) as request:
                prices.ensure_dbs();self.assertFalse(hk.exists());request.assert_called_once()
                hk_names,a_names=prices.load_dbs();self.assertEqual(hk_names,[])
                self.assertEqual(a_names,[('测试公司','600000.SS')])

    def test_empty_registry_cannot_replace_a_valid_database(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'names.json';p.write_text('{"0041.HK":"GREAT EAGLE"}');before=p.read_bytes()
            with self.assertRaises(ValueError):prices.save_stock_db(p,{})
            self.assertEqual(p.read_bytes(),before)

    def test_normalized_duplicates_share_a_request_and_misses_retry_next_batch(self):
        with patch.object(prices.yf,'download',return_value=pd.DataFrame()) as request,patch.object(prices.yf,'Ticker',return_value=Mock(info={})):
            for symbol in ['00041.HK','0041.HK','41.hk']:
                self.assertIsNone(prices.fetch_price_on_date(symbol,'2026-08-01'))
                self.assertIsNone(prices.fetch_price_latest(symbol))
            self.assertEqual(request.call_count,2)
            prices._historical_price.cache_clear();prices._latest_price.cache_clear()
            prices.fetch_price_on_date('0041.HK','2026-08-01');prices.fetch_price_latest('0041.HK')
            self.assertEqual(request.call_count,4)

    def test_nonfinite_capitalization_is_not_a_valid_number(self):
        with patch.object(prices.yf,'Ticker',return_value=Mock(info={'marketCap':float('inf')})):
            self.assertIsNone(prices.fetch_target_market_cap('0041.HK'))


if __name__ == "__main__":
    unittest.main()
