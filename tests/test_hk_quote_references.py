import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fetch_prices_all as prices


class HKQuoteReferenceTests(unittest.TestCase):
    def test_only_original_identified_hk_classes_are_quoted(self):
        r={'verification':'hkex_form','position':'long','shares':100,'share_class':'H Shares','form_url':'https://di.hkex.com.hk/di/NSForm2.aspx'}
        payload={'holdings':[{'ticker':'01658.HK','verified_disclosures':[r]},
            {'ticker':'01211.HK','verified_disclosures':[{**r,'share_class':'A Shares'}]},
            {'ticker':'09992.HK','verified_disclosures':[{**r,'verification':'search_result'}]}]}
        self.assertEqual(prices.disclosed_hk_tickers(payload),['01658.HK'])

    def test_quote_keeps_actual_market_time_and_hkd_currency(self):
        fields=['PSBC','邮储银行','5','5','5','5','5.42']+['0']*10+['2026/10/09','16:08']
        response=io.BytesIO(('var hq_str_hk01658="'+','.join(fields)+'";').encode('gbk'))
        with patch.object(prices.urllib.request,'urlopen',return_value=response),patch.object(prices.time,'sleep'),patch.object(prices.time,'time',return_value=1791600000):
            q=prices.get_hk_prices(['01658.HK'])['01658.HK']
        self.assertEqual(q['c'],5.42);self.assertEqual(q['currency'],'HKD')
        self.assertEqual(q['t'],1791533280)
        self.assertEqual(q['source'],'sina_hk')

    def test_hk_supplement_does_not_modify_us_quotes_or_cost_basis(self):
        with tempfile.TemporaryDirectory() as root:
            file=Path(root)/'hk.json'
            file.write_text(json.dumps({'holdings':[{'ticker':'01658.HK','verified_disclosures':[{'verification':'hkex_form','position':'long','shares':100,'share_class':'H Shares','form_url':'https://di.hkex.com.hk/di/NSForm2.aspx'}]}]}))
            us={'ABC':{'c':50,'currency':'USD'}}
            with patch.object(prices,'get_hk_prices',return_value={'01658.HK':{'c':5.42,'currency':'HKD','t':1791533280}}):
                result=prices.supplement_hk_quotes({'hk':str(file)},dict(us))
            self.assertEqual(result['ABC'],us['ABC'])
            self.assertEqual(result['01658.HK']['currency'],'HKD')
            self.assertEqual(set(result),{'ABC','01658.HK'})


if __name__=='__main__':
    unittest.main()
