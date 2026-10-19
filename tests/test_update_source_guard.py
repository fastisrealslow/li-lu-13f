from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from update_source_guard import watched_paths,unchanged


class SourceGuardTests(unittest.TestCase):
    def test_data_guard_tracks_its_actual_trigger_paths(self):
        root=Path(__file__).resolve().parents[1]
        paths=watched_paths((root/'.github/workflows/update.yml').read_text())
        self.assertIn('fetch_13f_all.py',paths)
        self.assertIn('reporting_scope.py',paths)
        self.assertIn('.github/workflows/update.yml',paths)
        self.assertNotIn('archive_generator.py',paths)
        self.assertNotIn('.github/workflows/speech-archive.yml',paths)

    def test_unrelated_archive_change_does_not_discard_a_finished_data_batch(self):
        root=Path(__file__).resolve().parents[1]
        with patch('update_source_guard.subprocess.run',return_value=subprocess.CompletedProcess([],0)) as git:
            self.assertTrue(unchanged('base','latest',root))
            args=git.call_args.args[0]
            self.assertNotIn('*.py',args)
            self.assertIn('validate_data.py',args)
        with patch('update_source_guard.subprocess.run',return_value=subprocess.CompletedProcess([],1)):
            self.assertFalse(unchanged('base','latest',root))


if __name__=='__main__':unittest.main()
