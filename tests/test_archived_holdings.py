import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fetch_webb_holdings as webb
import fetch_prices_all as prices
import hk_disclosures as hk


class ArchivedHoldingsTests(unittest.TestCase):
    def test_archive_mode_never_requests_mirror_or_rewrites_holdings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);config=root/'investors.json';archive=root/'webb.json'
            config.write_text(json.dumps({'investors':[{'id':'webb','holdingsUpdateMode':'archived'}]}))
            archive.write_text(json.dumps({'current':{'holdings':[{'ticker':'0709.HK','shares':100,'value':125}]}}))
            original=archive.read_bytes()
            with patch.object(webb,'CONFIG_PATH',config),patch.object(webb,'WEBB_JSON',str(archive)),patch.object(webb,'fetch_webbchips',side_effect=AssertionError('Retired feed must not be requested')),patch('update_status.record_source_notice'),contextlib.redirect_stdout(io.StringIO()):
                webb.main()
            self.assertEqual(archive.read_bytes(),original)

    def test_archived_hk_evidence_keeps_original_verification_dates_and_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'webb_hk.json';path.write_text(json.dumps({'lastUpdated':'2025-05-31','holdings':[{'ticker':'00709.HK','verified_disclosures':[{'event_date':'2025-05-31'}]}]}))
            original=path.read_bytes()
            class ForbiddenNetwork:
                def get(self,*args):raise AssertionError('An archive does not query ownership records')
            result=hk.run_investor({'id':'webb','hkFile':path.name,'holdingsUpdateMode':'archived'},tmp,ForbiddenNetwork())
            self.assertEqual(result['status'],'archived');self.assertEqual(result['verifiedSecurities'],1)
            self.assertEqual(path.read_bytes(),original)

    def test_quotes_refresh_without_revaluing_or_changing_archived_shares(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);archive=root/'webb.json';quote_file=root/'prices_webb.json'
            archive.write_text(json.dumps({'meta':{'snapshotType':'historical_disclosure_snapshot'},'current':{'quarter':'历史快照','totalValue':125,'holdings':[{'ticker':'0709.HK','shares':100,'value':125}]},'history':{'holdings':{}}}))
            original=archive.read_bytes();quote={'c':1.5,'currency':'HKD','source':'test_source','t':1791770280}
            with patch.object(prices,'get_hk_prices',return_value={'0709.HK':quote}),patch.object(prices,'supplement_hk_quotes'),patch.object(prices,'yahoo_chart',side_effect=AssertionError('An archive has no estimated buying quarters')),contextlib.redirect_stdout(io.StringIO()):
                prices.fetch_hk('webb',{'data':str(archive),'prices':str(quote_file)})
            self.assertEqual(archive.read_bytes(),original)
            output=json.loads(quote_file.read_text());self.assertEqual(output['quotes']['0709.HK']['c'],1.5)
            self.assertEqual(output['costBasis'],{})

    def test_missing_archive_is_a_real_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);config=root/'investors.json';archive=root/'webb.json'
            config.write_text(json.dumps({'investors':[{'id':'webb','holdingsUpdateMode':'archived'}]}))
            archive.write_text('{"current":{"holdings":[]}}')
            with patch.object(webb,'CONFIG_PATH',config),patch.object(webb,'WEBB_JSON',str(archive)),contextlib.redirect_stdout(io.StringIO()),self.assertRaises(ValueError):webb.main()
