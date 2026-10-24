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
    if investor.get('source13F'):
        return [('13f',['fetch_13f_all.py','--investor',ident]),
                ('audit',['audit_13f_history.py','--investor',ident,'--limit','6']),
                ('identities',['resolve_unmapped_tickers.py','--cached-only','--investor',ident]),
                ('prices',['fetch_prices_all.py','--investor',ident])]
    return [('holdings',['fetch_webb_holdings.py']),('prices',['fetch_prices_all.py','--investor',ident])]

def run(people, runner=subprocess.run):
    from update_status import update_step, STEP_LABELS
    failed=[]
    # Preserve verified, CUSIP-bound alias proofs before reparsing raw SEC units.
    # Numeric changes cannot be blessed by this cached-only identity pass.
    preflight=runner([sys.executable,'-u','resolve_unmapped_tickers.py','--cached-only'],cwd=ROOT,timeout=300,check=False)
    if preflight.returncode:
        if os.environ.get('TRACK_RUN_STATUS')=='1':update_step('resolve_cusip','fail','Cached identity preflight failed; existing snapshots retained')
        return ['resolve_cusip']
    for investor in people:
        for kind,args in commands(investor):
            key=investor['id']+'_'+kind
            STEP_LABELS[key]=investor['name']+' '+{'13f':'13F','audit':'申报金额复核','identities':'证券代码核对','holdings':'港股披露','prices':'股价与成本','disclosures':'项目与权益披露'}[kind]
            try:
                result=runner([sys.executable,'-u',*args],cwd=ROOT,timeout=1200,check=False)
                if result.returncode:raise RuntimeError(f'Updater exited {result.returncode}; previous published snapshot retained on source failure')
                if os.environ.get('TRACK_RUN_STATUS')=='1':update_step(key,'ok')
            except (subprocess.SubprocessError,RuntimeError) as exc:
                failed.append(key)
                if os.environ.get('TRACK_RUN_STATUS')=='1':update_step(key,'fail',str(exc))
                print(f'{key}: {exc}',file=sys.stderr,flush=True)
                if kind in ('audit','identities'):
                    break  # never price or estimate costs from an unverified refresh
    return failed

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--investor');args=parser.parse_args()
    people=json.loads((ROOT/'investors.json').read_text())['investors']
    if args.investor:people=[p for p in people if p['id']==args.investor]
    if not people:raise ValueError('Unknown investor')
    raise SystemExit(bool(run(people)))
