import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

import spinoff_price_refresh as prices


class SpinoffPriceTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
