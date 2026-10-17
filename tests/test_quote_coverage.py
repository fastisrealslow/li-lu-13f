import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import quote_coverage as quotes
import fetch_13f_all as filings
import resolve_unmapped_tickers as resolver


class QuoteCoverageTests(unittest.TestCase):
    def test_source_identity_currency_and_quote_time_are_verified(self):
        meta={'symbol':'CB','currency':'USD','regularMarketPrice':359.79,'regularMarketTime':int(time.time())}
        def response(m):return io.BytesIO(json.dumps({'chart':{'result':[{'meta':m}]}}).encode())
        with patch.object(quotes.urllib.request,'urlopen',side_effect=lambda *a,**k:response(meta)):
            self.assertEqual(quotes.yahoo_quote('CB')['c'],359.79)
        for key,value in [('symbol','CBOE'),('currency','CHF'),('regularMarketTime',time.time()+10000),('regularMarketTime',time.time()-10*86400)]:
            with self.subTest(key=key),patch.object(quotes.urllib.request,'urlopen',side_effect=lambda *a,**k:response({**meta,key:value})):
                self.assertTrue(quotes.yahoo_quote('CB')['error'])

    def test_verified_cusips_survive_names_and_symbol_changes(self):
        for name,cusip,ticker in [('CHUBB LIMITED','H1467J104','CB'),('ICON PUB LTD CO','G4705A100','ICLR'),('NU HLDGS LTD','G6683N103','NU'),('AXALTA COATING SYS LTD','G0750C108','AXTA'),('CCC INTELLIGENT SOLUTIONS HL','12510Q100','CCC')]:
            self.assertEqual(filings.resolve_ticker(name,'COM',cusip),ticker)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'sample.json';p.write_text(json.dumps({'current':{'holdings':[{'ticker':'CCCS','cusip':'12510Q100','shares':10,'value':20}]}}))
            resolver.backfill_data_files([str(p)],{'12510Q100':'CCC'})
            self.assertEqual(json.loads(p.read_text())['current']['holdings'][0],{'ticker':'CCC','cusip':'12510Q100','shares':10,'value':20})

    def test_listing_class_aliases_do_not_change_currency_or_security(self):
        self.assertEqual(quotes.symbol('BRK/B'),'BRK-B')
        self.assertEqual(quotes.symbol('00992.HK'),'0992.HK')
        self.assertFalse(quotes.valid_quote({'c':0,'t':time.time()}))

if __name__=='__main__':unittest.main()
