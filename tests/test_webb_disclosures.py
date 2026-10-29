import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fetch_webb_holdings as webb


def evidence(**changes):
    return dict(ticker='00709.HK', entity='Webb David Michael',
                event_date='2025-01-01', filing_date='2025-01-02',
                filing_ref='IS1', verification='hkex_form', shares=100,
                pct=6, position='long', share_class='Ordinary shares',
                form_url='https://di.hkex.com.hk/di/NSForm1.aspx?fn=IS1',
                **changes)


class WebbDisclosuresTests(unittest.TestCase):
    def test_latest_exit_and_unverified_newer_notice_never_reuse_old_quantity(self):
        original=evidence()
        row={'name':'Test', 'verified_disclosures':[original]}
        payload={'holdings':[row]}
        self.assertEqual(len(webb.disclosed_positions(payload,['Webb David Michael'])),1)
        row['verified_disclosures'].append({**original,'filing_ref':'IS2','event_date':'2025-02-01','pct':4.9})
        self.assertEqual(webb.disclosed_positions(payload,['Webb David Michael']),[])
        row['verified_disclosures']=[original]
        row['pending_newer_notices']=[{'event_date':'2025-03-01'}]
        self.assertEqual(webb.disclosed_positions(payload,['Webb David Michael']),[])

    def test_only_active_same_isin_modern_forms_are_valued_and_failure_preserves_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); investor={'dataFile':'webb.json','hkFile':'webb_hk.json','hkDisclosure':{'entities':['Webb David Michael']}}
            prior={'meta':{},'current':{'holdings':[{'ticker':'00709.HK','isin':'OLD','shares':1}]}}
            path=root/'webb.json';path.write_text(json.dumps(prior))
            (root/'webb_hk.json').write_text(json.dumps({'audit':{'status':'checked','checkedAt':webb.datetime.now(webb.timezone.utc).isoformat()},'holdings':[{'name':'Test','verified_disclosures':[evidence()]}]}))
            listed=lambda:{'00709.HK':{'isin':'NEW'}}
            with patch('update_status.record_source_warning'),patch('update_status.record_source_notice'):
                self.assertFalse(webb.update_from_disclosures(investor,root,lambda _: {},listed))
                self.assertEqual(json.loads(path.read_text()),prior)
                listed=lambda:{'00709.HK':{'isin':'OLD'}}
                self.assertFalse(webb.update_from_disclosures(investor,root,lambda _: {'00709.HK':{'error':True}},listed))
                self.assertEqual(json.loads(path.read_text()),prior)
                self.assertTrue(webb.update_from_disclosures(investor,root,lambda _: {'00709.HK':{'c':2,'t':1793232000,'currency':'HKD'}},listed))
                result=json.loads(path.read_text())
                self.assertEqual(result['current']['totalValue'],200)
                self.assertEqual(result['current']['holdings'][0]['shares'],100)
                self.assertEqual(result['meta']['snapshotType'],'verified_disclosure_snapshot')
                self.assertIsNone(result['current']['prevQuarter'])

    def test_incomplete_or_stale_audit_cannot_be_relabeled_as_a_new_verified_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); prior={'current':{'holdings':[{'ticker':'00709.HK','shares':1}]}}
            path=root/'webb.json';path.write_text(json.dumps(prior))
            investor={'dataFile':'webb.json','hkFile':'webb_hk.json','hkDisclosure':{'entities':['Webb David Michael']}}
            for audit in ({'status':'partial','checkedAt':webb.datetime.now(webb.timezone.utc).isoformat()},{'status':'checked','checkedAt':'2000-01-01T00:00:00Z'},{}):
                (root/'webb_hk.json').write_text(json.dumps({'audit':audit,'holdings':[{'verified_disclosures':[evidence()]}]}))
                with patch('update_status.record_source_warning'):
                    self.assertFalse(webb.update_from_disclosures(investor,root,listed_reader=lambda:self.fail('Incomplete audits must stop before another source is read')))
                self.assertEqual(json.loads(path.read_text()),prior)

            stamp=webb.datetime.now(webb.timezone.utc)
            earlier=webb.datetime.fromtimestamp(stamp.timestamp()-60,webb.timezone.utc)
            (root/'webb_hk.json').write_text(json.dumps({'audit':{'status':'checked','checkedAt':earlier.isoformat()}}))
            with patch.dict('os.environ',{'TRACK_RUN_STATUS':'1'}),patch('update_status.load',return_value={'runs':[{'run_id':stamp.isoformat()}]}),patch('update_status.record_source_warning'):
                self.assertFalse(webb.update_from_disclosures(investor,root,listed_reader=lambda:self.fail('A failed scheduled check cannot reuse the previous run as a fresh verification')))
