"""Retry an ordinary push when another automated writer advances master.

Every retry fetches the current source rules, merges the remote changes, binds
summaries again, and validates the complete result. Never force-push.
"""
import os
from pathlib import Path
import subprocess
import sys
import time


def publish(repo, source_sha, attempts=8, prepare=None, pause=time.sleep):
    repo = Path(repo)
    def git(*args):
        return subprocess.run(['git', *args], cwd=repo, check=True,
                              capture_output=True, text=True).stdout.strip()
    for attempt in range(attempts):
        git('fetch', 'origin', 'master')
        guard = subprocess.run([sys.executable, 'update_source_guard.py', source_sha,
                                'origin/master'], cwd=repo)
        if guard.returncode == 1:
            print('Source rules changed; a fresh update owns publication.', flush=True)
            return False
        if guard.returncode:
            raise RuntimeError('Could not verify the source rules before publication')
        git('merge', 'origin/master', '--no-edit', '-X', 'ours')
        if prepare:
            prepare(repo)
        else:
            subprocess.run([sys.executable, 'ai_supplement.py', '--refresh-fallbacks'], cwd=repo, check=True)
            subprocess.run([sys.executable, 'update_status.py', '--step', 'publication',
                            '--status', 'ok', '--msg', '有效数据已提交，网站自动发布。'], cwd=repo, check=True)
            subprocess.run([sys.executable, 'validate_data.py', '--stage'], cwd=repo, check=True)
        if git('diff', '--cached', '--name-only'):
            git('commit', '-m', 'auto: validate and bind merged update for publication')
        try:
            git('push', 'origin', 'HEAD:master')
            print(f'Validated update published (attempt {attempt + 1}).', flush=True)
            return True
        except subprocess.CalledProcessError:
            if attempt + 1 == attempts:
                raise
            print('Remote changed or push was interrupted; rechecking before retry.', flush=True)
            pause(min(attempt + 1, 5))
    return False


if __name__ == '__main__':
    publish(Path(__file__).resolve().parent, os.environ['TRACKER_SOURCE_SHA'])
