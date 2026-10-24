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

    def test_old_positive_quote_triggers_symbol_recheck_and_cannot_pass_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'investors.json').write_text(json.dumps({'investors':[{'id':'test','dataFile':'fund.json','pricesFile':'prices.json'}]}))
            (root/'fund.json').write_text(json.dumps({'current':{'holdings':[{'ticker':'IAC','name':'PEOPLE INC','cusip':'44891N208','shares':10,'value':100}]}}))
            (root/'prices.json').write_text(json.dumps({'quotes':{'IAC':{'c':36.98,'t':time.time()-20*86400}}}))
            self.assertEqual(len(quotes.coverage(root)['missing']),1)
            directory={'0':{'title':'People Inc','ticker':'PPLI'}}
            fresh={'c':38.76,'t':time.time(),'verifiedName':'People Incorporated','sourceURL':'https://finance.yahoo.com/quote/PPLI/'}
            with patch('fetch_13f_all.sec_fetch',return_value=json.dumps(directory).encode()),patch.object(quotes,'yahoo_quote',return_value=fresh):
                quotes.resolve_active(root,[{'dataFile':'fund.json','pricesFile':'prices.json'}])
            self.assertEqual(json.loads((root/'fund.json').read_text())['current']['holdings'][0]['ticker'],'PPLI')
            self.assertEqual(json.loads((root/'security_symbol_changes.json').read_text())['entries']['44891N208']['oldSymbols'],['IAC'])

    def test_hk_secondary_quote_requires_recent_hkd_and_preserves_its_actual_trade_date(self):
        fresh={'c':.285,'t':time.time()-86400,'currency':'HKD'}
        with patch.object(quotes,'yahoo_quote',return_value={'error':True}),patch('fetch_prices_all.get_hk_prices',return_value={'0125.HK':fresh}):
            self.assertEqual(quotes.market_quote('0125.HK')['t'],fresh['t'])
        for bad in [{**fresh,'currency':'USD'},{**fresh,'t':time.time()-20*86400}]:
            with patch.object(quotes,'yahoo_quote',return_value={'error':True}),patch('fetch_prices_all.get_hk_prices',return_value={'0125.HK':bad}):
                self.assertTrue(quotes.market_quote('0125.HK')['error'])

    def test_same_cusip_symbol_change_preserves_historical_cost_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);cfg={'id':'test','dataFile':'fund.json','pricesFile':'prices.json'}
            (root/'investors.json').write_text(json.dumps({'investors':[cfg]}))
            (root/'fund.json').write_text(json.dumps({'current':{'holdings':[{'ticker':'CCC','cusip':'12510Q100','shares':10,'value':100}]}}))
            cost={'recent':{'buy':8,'quarter':'2026 Q1'},'allTime':{'avg':9}}
            (root/'prices.json').write_text(json.dumps({'quotes':{'CCC':{'c':7,'t':time.time()}},'costBasis':{'CCCS':cost}}))
            (root/'security_symbol_changes.json').write_text(json.dumps({'entries':{'12510Q100':{'ticker':'CCC','oldSymbols':['CCCS']}}}))
            self.assertEqual(quotes.refresh(root)['missing'],[])
            self.assertEqual(json.loads((root/'prices.json').read_text())['costBasis']['CCC'],cost)
            self.assertEqual(json.loads((root/'fund.json').read_text())['current']['holdings'][0]['shares'],10)

    def test_share_class_correction_does_not_copy_the_other_class_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);cfg={'id':'test','dataFile':'fund.json','pricesFile':'prices.json'}
            (root/'investors.json').write_text(json.dumps({'investors':[cfg]}))
            (root/'fund.json').write_text(json.dumps({'current':{'holdings':[{'ticker':'LBTYK','cusip':'G61188127','shares':10,'value':100}]}}))
            (root/'prices.json').write_text(json.dumps({'quotes':{'LBTYK':{'c':7,'t':time.time()}},'costBasis':{'LBTYA':{'recent':{'buy':8}}}}))
            (root/'security_symbol_changes.json').write_text(json.dumps({'entries':{'G61188127':{'ticker':'LBTYK','oldSymbols':['LBTYA'],'preserveCost':False}}}))
            self.assertEqual(quotes.refresh(root)['missing'],[])
            self.assertNotIn('LBTYK',json.loads((root/'prices.json').read_text())['costBasis'])
            self.assertEqual(filings.resolve_ticker('LIBERTY GLOBAL LTD','SHS CL C','G61188127'),'LBTYK')

if __name__=='__main__':unittest.main()
