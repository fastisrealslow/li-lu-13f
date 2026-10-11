"""Publish only a failed run's status, never its unvalidated data files."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from update_status import MAX_RUNS


def merge_failure_status(published, failed):
    runs = copy.deepcopy(published.get('runs', []))
    # Only this workflow's latest record, not its stale copy of old history.
    run = copy.deepcopy(failed['runs'][0])
    if not run.get('completedAt') or not any(
            step.get('status') == 'fail' for step in run.get('steps', {}).values()):
        raise ValueError('Failure publication requires a completed failed run')
    runs = [old for old in runs if old.get('run_id') != run['run_id']]
    runs.append(run)
    runs.sort(key=lambda row: row['run_id'], reverse=True)
    return {**published, 'runs': runs[:MAX_RUNS]}


def publish_failure(repo, source_sha):
    repo = Path(repo).resolve()
    failed = json.loads((repo / 'run_status.json').read_text())

    def git(*args, cwd=repo):
        return subprocess.run(['git', *args], cwd=cwd, check=True,
                              capture_output=True, text=True).stdout.strip()

    for attempt in range(3):
        git('fetch', 'origin', 'master')
        check = subprocess.run(['git', 'diff', '--quiet', source_sha, 'origin/master',
                                '--', '*.py', '.github/workflows/*.yml', 'investors.json'], cwd=repo)
        if check.returncode == 1:
            print('Source rules changed; the queued fresh run owns publication.')
            return False
        if check.returncode:
            raise RuntimeError('Could not verify source rules')
        # A separate clean checkout contains only the last published data.
        with tempfile.TemporaryDirectory(prefix='tracker-failure-status-') as tmp:
            checkout = Path(tmp) / 'published'
            git('worktree', 'add', '--detach', str(checkout), 'origin/master')
            try:
                status = checkout / 'run_status.json'
                published = json.loads(status.read_text())
                status.write_text(json.dumps(merge_failure_status(published, failed),
                                             ensure_ascii=False, indent=2) + '\n')
                subprocess.run([sys.executable, 'validate_data.py'], cwd=checkout, check=True)
                git('add', '--', 'run_status.json', cwd=checkout)
                changed = git('diff', '--cached', '--name-only', cwd=checkout).splitlines()
                if not changed:
                    return True
                if changed != ['run_status.json']:
                    raise RuntimeError('Refusing to publish data from a failed update')
                git('-c', 'user.name=github-actions[bot]', '-c',
                    'user.email=github-actions[bot]@users.noreply.github.com',
                    'commit', '-m', 'auto: report failed update; retain last validated data', cwd=checkout)
                try:
                    git('push', 'origin', 'HEAD:master', cwd=checkout)
                    return True
                except subprocess.CalledProcessError:
                    if attempt == 2:
                        raise
                    # A concurrent data/AI commit won the race. Re-read it;
                    # never force push or overwrite its newer run history.
            finally:
                git('worktree', 'remove', '--force', str(checkout))
    return False


if __name__ == '__main__':
    publish_failure(Path(__file__).resolve().parent, os.environ['TRACKER_SOURCE_SHA'])
