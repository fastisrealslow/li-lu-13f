import copy,json,unittest
from pathlib import Path
import historical_labels as labels
from legacy_13f import parse_legacy
from hk_disclosures import parse_form

class HistoricalLabelsTests(unittest.TestCase):
    def test_wrapped_names_and_classes_do_not_leak_to_following_issuers(self):
        rows=parse_legacy(Path('tests/fixtures/legacy_wrapped_issuers.txt').read_bytes())
        by_id={r['cusip']:r for r in rows}
        self.assertEqual(by_id['85512C105']['name'],'Star Gas Partners LP')
        self.assertEqual(by_id['85512C105']['cls'],'UNITS LTD PRTN')
        self.assertEqual(by_id['303901102']['name'],'Fairfax Finl Hldngs Ltd')
        self.assertEqual(by_id['303901102']['cls'],'SUB VTG')
        self.assertEqual(by_id['256135203']['name'],'Dr. Reddys Labs Ltd')
        self.assertEqual(by_id['22282E102']['name'],'Covanta Holding Corporation')
        self.assertEqual(sum(r['value'] for r in rows),261043000)

    def test_historical_labeling_does_not_require_a_live_ticker_or_mutate_financials(self):
        r={'cusip':'85512C105','ticker':'?Star Gas Partners LP','name':'Star Gas Partners LP','shares':4395415,'value':11780000,'cls':'UNITS LTD PRTN'}
        before=copy.deepcopy(r);self.assertTrue(labels.apply_row(r))
        self.assertEqual({k:r[k] for k in before},before)
        self.assertEqual(r['cnName'],'星源燃气合伙企业');self.assertEqual(r['sectorEn'],'Heating oil and fuel distribution')
        self.assertFalse(labels.apply_row(r))
        other={'ticker':'SGU','name':'Unrelated issuer reusing a ticker'}
        self.assertFalse(labels.apply_row(other))

    def test_hk_trade_average_is_distinct_from_total_position_cost(self):
        html=Path('tests/fixtures/hkex/byd_2005_trade_form.html').read_text()
        r=parse_form(html,'https://di.hkex.com.hk/filing/di/NSForm1.aspx?fn=10278',['Li Lu'])
        self.assertEqual(r['shares'],7962000)
        self.assertEqual(r['transaction_shares'],812000)
        self.assertEqual(r['transaction_average_price'],11.999)
        self.assertEqual(r['transaction_currency'],'HKD')
        self.assertNotIn('cost_basis',r)
