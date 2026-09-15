import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import fetch_13f_all
from holdings_diff import compare_holdings, update_history
import update_status
import validate_data


ROOT = Path(__file__).resolve().parents[1]


class HoldingsTests(unittest.TestCase):
    def test_renamed_and_sold_securities(self):
        previous = [dict(ticker="OLD", cusip="111", shares=10, value=100),
                    dict(ticker="SOLD", cusip="222", shares=5, value=50)]
        current = [dict(ticker="NEW", cusip="111", shares=8, value=90)]
        rows = compare_holdings(current, previous)
        self.assertEqual(rows[0]["prevShares"], 10)
        self.assertTrue(rows[1]["exited"])
        self.assertEqual(rows[1]["shares"], 0)
        self.assertEqual(len(current), 1)

    def test_refreshed_history_replaces_old_snapshot_and_sorts_new_quarters(self):
        data = {"history": {"quarters": ["2026 Q2"], "values": [999], "holdings": {"2026 Q2": []}}}
        update_history(data, "2026 Q2", [dict(value=3_000_000)])
        update_history(data, "2026 Q1", [dict(value=2_000_000)])
        self.assertEqual(data["history"]["quarters"], ["2026 Q1", "2026 Q2"])
        self.assertEqual(data["history"]["values"], [2, 3])

    def test_fetcher_persists_previous_report_for_liquidation_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "data.json"
            filings = [dict(reportDate="2026-06-30", filingDate="2026-08-14", accession="new", accessionDashed="new"),
                       dict(reportDate="2026-03-31", filingDate="2026-05-14", accession="old", accessionDashed="old")]
            current = [dict(ticker="NEW", cusip="111", shares=8, value=80)]
            previous = [dict(ticker="OLD", cusip="111", shares=10, value=100),
                        dict(ticker="EXIT", shares=5, value=50)]
            config = dict(path=str(output), manager="Test", people=[], cik="1")
            with patch.object(fetch_13f_all, "get_recent_filings", return_value=filings), \
                 patch.object(fetch_13f_all, "find_info_table_xml", return_value="fixture"), \
                 patch.object(fetch_13f_all, "sec_fetch", return_value=b"fixture"), \
                 patch.object(fetch_13f_all, "parse_holdings", side_effect=[current, previous]), \
                 contextlib.redirect_stdout(io.StringIO()):
                fetch_13f_all.process_investor("test", config, False)
            saved = json.loads(output.read_text())
            self.assertEqual(saved["current"]["previousHoldings"], previous)
            self.assertEqual(saved["current"]["holdings"][0]["prevShares"], 10)
            self.assertEqual(saved["current"]["totalValue"], 80)
            self.assertEqual(saved["history"]["holdings"]["2026 Q1"], previous)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "investors.json").write_text(json.dumps({"investors": [
            {"dataFile": "fund.json", "pricesFile": "quotes.json", "hkFile": "hk.json"}]}))
        for name in validate_data.EXTRA_FILES:
            (self.root / name).write_text("{}")
        (self.root / "run_status.json").write_text('{"runs": []}')
        (self.root / "fund.json").write_text('{"current":{"quarter":"2026 Q2","holdings":[]}}')
        (self.root / "quotes.json").write_text('{"quotes":{}}')
        (self.root / "hk.json").write_text('{}')

    def test_all_data_and_mapping_cache_are_validated_and_included(self):
        (self.root / "resolved_cusip_map.json").write_text('{"111":"ABC"}')
        files = validate_data.validate(self.root)
        self.assertIn("resolved_cusip_map.json", files)
        self.assertIn("hk.json", files)
        self.assertIn("spinoff.json", files)

    def test_malformed_extra_file_causes_nonzero_cli_exit(self):
        (self.root / "spinoff.json").write_text('{broken')
        result = subprocess.run([sys.executable, str(ROOT / "validate_data.py")], cwd=self.root,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("spinoff.json", result.stderr)

    def test_missing_required_file_is_rejected(self):
        (self.root / "fund.json").unlink()
        with self.assertRaisesRegex(ValueError, "fund.json"):
            validate_data.validate(self.root)

    def test_valid_json_with_wrong_shape_or_invalid_numbers_is_rejected(self):
        for bad in ('null', '[]', '{"current":{"quarter":"Q2","holdings":[{"ticker":"ABC","shares":NaN,"value":1}]}}',
                    '{"current":{"quarter":"Q2","holdings":[{"ticker":"ABC","shares":1,"value":-1}]}}'):
            with self.subTest(bad=bad):
                (self.root / "fund.json").write_text(bad)
                with self.assertRaises(ValueError):
                    validate_data.validate(self.root)


class RunStatusTests(unittest.TestCase):
    def test_warning_survives_success_and_failure_remains_failure(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(update_status, "STATUS_FILE", str(Path(directory) / "run_status.json")), \
             patch.dict(os.environ, {"TRACK_RUN_STATUS": "1"}), \
             contextlib.redirect_stdout(io.StringIO()):
            update_status.init_run("test")
            update_status.record_ai_warning("metadata", 402)
            update_status.update_step("metadata", "ok")
            run = update_status.load()["runs"][0]
            self.assertEqual(run["steps"]["metadata"]["status"], "warn")
            self.assertIn("余额不足", run["steps"]["metadata"]["msg"])
            update_status.update_step("metadata", "fail", "Process failed")
            update_status.finish_run()
            run = update_status.load()["runs"][0]
            self.assertEqual(run["steps"]["metadata"]["status"], "fail")
            self.assertTrue(run["completedAt"])
            self.assertEqual(run["schemaVersion"], 2)

    def test_local_ai_warning_does_not_create_a_status_file(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(update_status, "STATUS_FILE", str(Path(directory) / "run_status.json")), \
             patch.dict(os.environ, {"TRACK_RUN_STATUS": "0"}):
            update_status.record_ai_warning("metadata", 402)
            self.assertFalse(Path(update_status.STATUS_FILE).exists())


if __name__ == "__main__":
    unittest.main()
