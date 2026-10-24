"""Registry-driven updates: every configured investor is scheduled automatically."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent

def commands(investor):
    ident=investor['id']
    if investor.get('portfolioMode')=='public_projects':
        return [('disclosures',['fetch_public_projects.py','--investor',ident])]
    holdings=['fetch_13f_all.py','--investor',ident] if investor.get('source13F') else ['fetch_webb_holdings.py']
    return [('13f' if investor.get('source13F') else 'holdings',holdings),('prices',['fetch_prices_all.py','--investor',ident])]

def run(people, runner=subprocess.run):
    from update_status import update_step, STEP_LABELS
    failed=[]
    for investor in people:
        for kind,args in commands(investor):
            key=investor['id']+'_'+kind
            STEP_LABELS[key]=investor['name']+' '+{'13f':'13F','holdings':'港股披露','prices':'股价与成本','disclosures':'项目与权益披露'}[kind]
            try:
                result=runner([sys.executable,'-u',*args],cwd=ROOT,timeout=1200,check=False)
                if result.returncode:raise RuntimeError(f'Updater exited {result.returncode}; previous published snapshot retained on source failure')
                if os.environ.get('TRACK_RUN_STATUS')=='1':update_step(key,'ok')
            except (subprocess.SubprocessError,RuntimeError) as exc:
                failed.append(key)
                if os.environ.get('TRACK_RUN_STATUS')=='1':update_step(key,'fail',str(exc))
                print(f'{key}: {exc}',file=sys.stderr,flush=True)
    return failed

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--investor');args=parser.parse_args()
    people=json.loads((ROOT/'investors.json').read_text())['investors']
    if args.investor:people=[p for p in people if p['id']==args.investor]
    if not people:raise ValueError('Unknown investor')
    raise SystemExit(bool(run(people)))
