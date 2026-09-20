import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import monitor_hk_disclosures as hk


class DisclosureEvidenceTests(unittest.TestCase):
    def update(self, payload, hits):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'hk.json'
            path.write_text(json.dumps(payload))
            hk.update_hk_file(str(path), hits)
            return json.loads(path.read_text())

    def test_search_hit_cannot_refresh_disclosure_or_assert_active(self):
        row = dict(ticker='01658.HK', evidence_schema=2, last_disclosure='2021-01-15',
                   first_disclosure='2020-12-18', current_status='unknown', pct_date='2021-01-15')
        result = self.update({'holdings':[row]}, [dict(ticker='1658.HK', noticeUrl='https://di.hkex.com.hk/di/NSNoticePersonList.aspx')])
        for field in ['last_disclosure','first_disclosure','current_status','pct_date']:
            self.assertEqual(result['holdings'][0][field], row[field])
        self.assertIn('last_search_seen', result['holdings'][0])

    def test_partial_and_empty_search_do_not_infer_below_threshold(self):
        rows = [dict(ticker=t, evidence_schema=2, current_status='unknown') for t in ['01211.HK','01658.HK']]
        for hits in [[], [dict(ticker='01211.HK')]]:
            result = self.update({'holdings':rows}, hits)
            self.assertEqual([h['current_status'] for h in result['holdings']], ['unknown','unknown'])

    def test_new_discovery_has_no_invented_first_date_or_peak(self):
        result = self.update({'holdings':[]}, [dict(ticker='1766.HK', stockName='CRRC', entity='Li Lu')])
        row=result['holdings'][0]
        self.assertIsNone(row['first_disclosure'])
        self.assertIsNone(row['last_disclosure'])
        self.assertIsNone(row['peak_shares'])
        self.assertEqual(row['current_status'], 'unknown')

    def test_legacy_assertions_are_quarantined_idempotently(self):
        row=dict(ticker='1211.HK', last_disclosure='2026', current_status='active', pct='6.27%', notes='obsolete')
        once=self.update([row], [])
        twice=self.update(once, [])
        self.assertEqual(once['holdings'], twice['holdings'])
        result=once['holdings'][0]
        self.assertEqual(result['legacy_unverified']['current_status'], 'active')
        self.assertEqual(result['current_status'], 'unknown')
        self.assertIsNone(result['last_disclosure'])
        self.assertIsNone(result['pct'])

    def test_verified_postal_records_survive_refresh(self):
        data=json.loads(Path('hk_holdings.json').read_text())
        original=copy.deepcopy(data['holdings'][2]['verified_disclosures'])
        result=self.update(data, [dict(ticker='01658.HK')])
        self.assertEqual(result['holdings'][2]['verified_disclosures'], original)
        postal_2021 = [r for r in original if r['event_date']=='2021-01-15']
        self.assertTrue(any(r['shares']==1274411000 and r['pct']==6.42 for r in postal_2021))
