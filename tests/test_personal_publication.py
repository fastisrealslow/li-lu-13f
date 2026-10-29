import subprocess
import tempfile
import unittest
from pathlib import Path

from publish_personal_portfolio import publish


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True,
                                   stderr=subprocess.DEVNULL).strip()


class PersonalPublicationTests(unittest.TestCase):
    def scenario(self, change):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); remote = root / 'remote.git'; repo = root / 'updater'
            subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
            git(root, 'clone', str(remote), str(repo)); git(repo, 'checkout', '-b', 'master')
            git(repo, 'config', 'user.name', 'Test'); git(repo, 'config', 'user.email', 'test@example.org')
            (repo / '.github/workflows').mkdir(parents=True)
            (repo / '.github/workflows/personal-portfolio.yml').write_text(
                'on:\n  push:\n    paths:\n      - "rules.py"\n      - "personal_report_profiles.json"\n')
            (repo / 'rules.py').write_text('VERSION=1\n')
            (repo / 'personal_portfolio.json').write_text('{"value":1}')
            (repo / 'personal_report_profiles.json').write_text('{"sources":[]}')
            git(repo, 'add', '.'); git(repo, 'commit', '-m', 'initial'); git(repo, 'push', '-u', 'origin', 'master')
            base = git(repo, 'rev-parse', 'HEAD')
            other = root / 'archive'; git(root, 'clone', '-b', 'master', str(remote), str(other))
            git(other, 'config', 'user.name', 'Archive'); git(other, 'config', 'user.email', 'archive@example.org')
            (repo / 'personal_portfolio.json').write_text('{"value":2}')
            git(repo, 'add', '.'); git(repo, 'commit', '-m', 'verified calculations')
            checks = []

            def prepare(path):
                checks.append((path / 'personal_portfolio.json').read_text())
                if len(checks) <= 3:
                    target = other / (change or ('archive-' + str(len(checks)) + '.json'))
                    target.write_text('{"revision":' + str(len(checks)) + '}')
                    git(other, 'add', '.'); git(other, 'commit', '-m', 'competing update')
                    git(other, 'push', 'origin', 'HEAD:master')

            result = publish(repo, base, prepare=prepare, pause=lambda _: None)
            if change:
                self.assertFalse(result); self.assertEqual(len(checks), 1)
                self.assertEqual(git(remote, 'show', 'master:' + change), '{"revision":1}')
            else:
                self.assertTrue(result); self.assertEqual(checks, ['{"value":2}'] * 4)
                self.assertEqual(git(remote, 'show', 'master:personal_portfolio.json'), '{"value":2}')
                for i in range(1, 4):
                    self.assertEqual(git(remote, 'show', 'master:archive-' + str(i) + '.json'), '{"revision":' + str(i) + '}')

    def test_three_competing_archive_pushes_reuse_calculation_and_preserve_every_commit(self):
        self.scenario(None)

    def test_new_financial_rules_stop_old_calculations(self):
        self.scenario('rules.py')

    def test_independently_updated_ledger_is_preserved(self):
        self.scenario('personal_portfolio.json')
