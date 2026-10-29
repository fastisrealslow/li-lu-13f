"""Publish verified calculations without re-downloading after unrelated commits."""
import os
from pathlib import Path
import subprocess
import sys
import time

from update_source_guard import watched_paths


def validate(repo):
    subprocess.run([sys.executable, '-c',
        "import json; from magic_formula import validate_dataset; "
        "validate_dataset(json.load(open('personal_portfolio.json')))"], cwd=repo, check=True)
    subprocess.run(['node', '--test', 'tests/personal_portfolio.cjs'], cwd=repo, check=True)


def publish(repo, source_sha, attempts=8, prepare=validate, pause=time.sleep):
    repo = Path(repo)

    def git(*args):
        return subprocess.run(['git', *args], cwd=repo, check=True,
                              capture_output=True, text=True).stdout.strip()

    workflow = '.github/workflows/personal-portfolio.yml'
    paths = watched_paths((repo / workflow).read_text())
    # An independently edited ledger must not be overwritten by an older job.
    paths = sorted(set(paths + [workflow, 'personal_portfolio.json']))
    for attempt in range(attempts):
        git('fetch', 'origin', 'master')
        changed = subprocess.run(['git', 'diff', '--quiet', source_sha,
                                  'origin/master', '--', *paths], cwd=repo)
        if changed.returncode == 1:
            print('Personal source or ledger changed; a fresh update owns publication.', flush=True)
            return False
        if changed.returncode:
            raise RuntimeError('Cannot verify personal calculation source revision')
        # The serialized personal workflow owns these two generated files;
        # unrelated source/archive changes must survive the ordinary merge.
        git('merge', 'origin/master', '--no-edit')
        prepare(repo)
        try:
            git('push', 'origin', 'HEAD:master')
            print(f'Personal portfolio published (attempt {attempt + 1}).', flush=True)
            return True
        except subprocess.CalledProcessError:
            if attempt + 1 == attempts:
                raise
            pause(min(attempt + 1, 5))
    return False


if __name__ == '__main__':
    publish(Path(__file__).resolve().parent, os.environ['PERSONAL_SOURCE_SHA'])
