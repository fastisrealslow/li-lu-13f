"""Registry-driven updates: every configured investor is scheduled automatically."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent

def commands(investor):
    ident=investor['id']
    if investor.get('portfolioMode')=='public_projects':
        return [('disclosures',['fetch_public_projects.py','--investor',ident])]
    if investor.get('source13F'):
        return [('13f',['fetch_13f_all.py','--investor',ident]),
                ('audit',['audit_13f_history.py','--investor',ident,'--limit','6']),
                ('identities',['resolve_unmapped_tickers.py','--active-only','--investor',ident]),
                ('prices',['fetch_prices_all.py','--investor',ident])]
    return [('holdings',['fetch_webb_holdings.py']),('prices',['fetch_prices_all.py','--investor',ident])]

def snapshot_files(investor):
    paths=[ROOT/investor[k] for k in ('dataFile','pricesFile') if investor.get(k)]
    if os.environ.get('TRACK_RUN_STATUS')=='1' and (ROOT/'run_status.json').exists():paths.append(ROOT/'run_status.json')
    return paths

def checkpoint(paths):
    return {path:path.read_bytes() if path.exists() else None for path in paths}

def restore(saved):
    for path,body in saved.items():
        if body is None:
            path.unlink(missing_ok=True)
        else:
            temp=path.with_suffix(path.suffix+'.rollback')
            temp.write_bytes(body);temp.replace(path)

def run(people, runner=subprocess.run, pause=time.sleep, retries=2):
    from update_status import update_step, STEP_LABELS
    failed=[]
    # Preserve verified, CUSIP-bound alias proofs before reparsing raw SEC units.
    # Numeric changes cannot be blessed by this cached-only identity pass.
    before_preflight=checkpoint([p for person in people for p in snapshot_files(person)])
    try:
        preflight=runner([sys.executable,'-u','resolve_unmapped_tickers.py','--cached-only'],cwd=ROOT,timeout=300,check=False)
        preflight_failed=bool(preflight.returncode)
    except (subprocess.SubprocessError,OSError):
        preflight_failed=True
    if preflight_failed:
        restore(before_preflight)
        if os.environ.get('TRACK_RUN_STATUS')=='1':update_step('resolve_cusip','fail','Cached identity preflight failed; existing snapshots retained')
        return ['resolve_cusip']
    del before_preflight
    for investor in people:
        original=checkpoint(snapshot_files(investor))
        for kind,args in commands(investor):
            key=investor['id']+'_'+kind
            STEP_LABELS[key]=investor['name']+' '+{'13f':'13F','audit':'申报金额复核','identities':'证券代码核对','holdings':'港股披露','prices':'股价与成本','disclosures':'项目与权益披露'}[kind]
            try:
                phase=checkpoint(snapshot_files(investor))
                for attempt in range(retries):
                    try:
                        timeout={'13f':600,'audit':300,'identities':180,'holdings':120,'prices':900,'disclosures':300}[kind]
                        result=runner([sys.executable,'-u',*args],cwd=ROOT,timeout=timeout,check=False)
                        if result.returncode:raise RuntimeError(f'Updater exited {result.returncode}')
                        break
                    except (subprocess.SubprocessError,RuntimeError,OSError):
                        restore(phase)
                        if attempt+1==retries:raise
                        print(f'{key}: temporary failure; retrying from the previous verified phase',flush=True)
                        pause(2)
                if os.environ.get('TRACK_RUN_STATUS')=='1':update_step(key,'ok','短暂故障已自动重试恢复' if attempt else '')
            except (subprocess.SubprocessError,RuntimeError,OSError) as exc:
                restore(original)
                failed.append(key)
                if os.environ.get('TRACK_RUN_STATUS')=='1':update_step(key,'fail',str(exc)+'；本轮变更已回退，保留上次持仓与报价，下轮自动重试。')
                print(f'{key}: {exc}',file=sys.stderr,flush=True)
                break  # Other investors continue; this investor remains a coherent snapshot.
        else:
            try:
                from validate_data import validate_holdings_snapshot, read_json
                if investor.get('dataFile'):
                    snapshot=read_json(ROOT/investor['dataFile'])
                    if 'totalValue' not in snapshot.get('current',{}):raise ValueError('Missing current total value')
                    validate_holdings_snapshot(snapshot)
                if investor.get('pricesFile') and not isinstance(read_json(ROOT/investor['pricesFile']).get('quotes'),dict):
                    raise ValueError('Missing price quotes')
            except (ValueError,OSError,TypeError,KeyError,AttributeError) as exc:
                restore(original)
                key=investor['id']+'_snapshot';failed.append(key)
                if os.environ.get('TRACK_RUN_STATUS')=='1':update_step(key,'fail','快照校验失败，已自动回退；'+str(exc))
    return failed

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--investor');args=parser.parse_args()
    people=json.loads((ROOT/'investors.json').read_text())['investors']
    if args.investor:people=[p for p in people if p['id']==args.investor]
    if not people:raise ValueError('Unknown investor')
    raise SystemExit(bool(run(people)))
