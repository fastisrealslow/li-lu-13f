"""Find the newest resumable artifact for one scheduled archive shard."""
import argparse
import json
import os
import sys
import urllib.request


def latest_run(repository,shard,current_run='',requested='',get=None):
    def request(path):
        req=urllib.request.Request('https://api.github.com/repos/'+repository+path,
            headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','User-Agent':'archive-continuation'})
        with urllib.request.urlopen(req,timeout=20) as response:return json.load(response)
    get=get or request
    runs=[{'id':requested}] if requested else get('/actions/workflows/speech-archive.yml/runs?status=completed&per_page=20').get('workflow_runs',[])
    for run in runs:
        ident=str(run['id'])
        if ident==str(current_run):continue
        artifacts=get('/actions/runs/'+ident+'/artifacts?per_page=100').get('artifacts',[])
        if any(a.get('name')=='archive-drafts-'+str(shard) and not a.get('expired') for a in artifacts):return ident
    return ''


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--shard',required=True);p.add_argument('--resume',default='');args=p.parse_args()
    try:ident=latest_run(os.environ['GITHUB_REPOSITORY'],args.shard,os.environ.get('GITHUB_RUN_ID',''),args.resume)
    except Exception as error:
        print('Artifact discovery unavailable; cached drafts remain usable: '+type(error).__name__,file=sys.stderr);ident=''
    print('run_id='+ident)
