import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import historical_labels as labels
from legacy_13f import parse_legacy
from hk_disclosures import parse_form

class HistoricalLabelsTests(unittest.TestCase):
    def test_usb_identity_corrects_existing_label_without_changing_financials(self):
        row={'ticker':'USB','cusip':'902973304','name':'US BANCORP DEL',
             'cnName':'美国银行','cls':'COM NEW','shares':73600,'value':2431744,
             'shareType':'SH','putCall':'','quarter':'2023 Q2'}
        before=copy.deepcopy(row)
        self.assertTrue(labels.apply_row(row))
        self.assertEqual(row['cnName'],'美国合众银行（U.S. Bancorp）')
        self.assertEqual(row['displayName'],'U.S. Bancorp')
        for key,value in before.items():
            if key!='cnName':self.assertEqual(row[key],value)
        self.assertFalse(labels.apply_row(row))

    def test_usb_name_cannot_override_conflicting_nonempty_cusip(self):
        row={'ticker':'USB','cusip':'999999999','name':'US BANCORP DEL',
             'cnName':'Other issuer','shares':12,'value':34}
        before=copy.deepcopy(row)
        self.assertFalse(labels.apply_row(row))
        self.assertEqual(row,before)
        # A known CUSIP takes precedence even if a supplied name conflicts.
        row={'ticker':'BAC','cusip':'060505104','name':'US BANCORP DEL'}
        labels.apply_row(row)
        self.assertEqual(row['cnName'],'美国银行')
        self.assertEqual(row['displayName'],'Bank of America')

    def test_usb_name_fallback_only_without_asserted_identity(self):
        row={'ticker':'?US BANCORP DEL','name':'US BANCORP DEL'}
        self.assertTrue(labels.apply_row(row))
        self.assertEqual(row['displayName'],'U.S. Bancorp')
        self.assertNotIn('cusip',row)
        self.assertEqual(row['ticker'],'?US BANCORP DEL')

    def test_process_file_repairs_all_periods_despite_old_bad_cache(self):
        from enrich_metadata import process_file
        usb={'ticker':'USB','cusip':'902973304','name':'US BANCORP DEL',
             'cnName':'美国银行','sector':'金融','shares':73600,'value':2431744}
        bac={'ticker':'BAC','cusip':'060505104','name':'BANK AMER CORP',
             'cnName':'美国银行','sector':'金融','shares':101,'value':202}
        data={'current':{'holdings':[copy.deepcopy(usb),bac],
                         'previousHoldings':[copy.deepcopy(usb)]},
              'history':{'holdings':{'2023 Q2':[copy.deepcopy(usb)]}}}
        cache={'USB':{'cnName':'美国银行','sector':'金融'},
               'BAC':{'cnName':'美国银行','sector':'金融'}}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'data.json';path.write_text(json.dumps(data))
            with patch('enrich_metadata.fetch_yf_info',side_effect=AssertionError('offline test')):
                process_file(path,cache)
                updated=json.loads(path.read_text())
                rows=updated['current']['holdings']+updated['current']['previousHoldings']+updated['history']['holdings']['2023 Q2']
                for row in rows:
                    self.assertEqual(row['cnName'],'美国银行' if row['ticker']=='BAC' else '美国合众银行（U.S. Bancorp）')
                    self.assertEqual((row['shares'],row['value']),(101,202) if row['ticker']=='BAC' else (73600,2431744))
                once=path.read_bytes();process_file(path,cache)
                self.assertEqual(path.read_bytes(),once)
                # Once USB is no longer current, its already populated historical
                # label is still repaired independently of live ticker metadata.
                data['current']={'holdings':[bac],'previousHoldings':[]}
                path.write_text(json.dumps(data));process_file(path,cache)
                self.assertEqual(json.loads(path.read_text())['history']['holdings']['2023 Q2'][0]['cnName'],'美国合众银行（U.S. Bancorp）')

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
