"""Use the data workflow's own trigger paths to detect obsolete calculations."""
from pathlib import Path
import re
import shlex
import subprocess
import sys


def watched_paths(text):
    push=re.search(r'^  push:\s*\n(.*?)(?=^  \w+:|\Z)',text,re.M|re.S)
    paths=re.search(r'^    paths:\s*\n((?:^      - .*\n?)+)',push[1] if push else '',re.M)
    if not paths:raise ValueError('Data workflow must declare its source trigger paths')
    return [shlex.split(line.strip()[2:],comments=True)[0] for line in paths[1].splitlines()]


def unchanged(base,target,root=Path('.')):
    paths=watched_paths((root/'.github/workflows/update.yml').read_text())
    result=subprocess.run(['git','diff','--quiet',base,target,'--',*paths],cwd=root)
    if result.returncode not in (0,1):raise RuntimeError('Cannot compare source revisions')
    return result.returncode==0


if __name__=='__main__':
    raise SystemExit(0 if unchanged(sys.argv[1],sys.argv[2]) else 1)
