"""Independent, bounded recovery of stalled collection and publication."""
import argparse
import hashlib
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ACTIVE={'queued','pending','waiting','requested','in_progress'}
WORKFLOWS={'data':'update.yml','pages':'deploy-pages.yml','ai':'ai-supplement.yml','personal':'personal-portfolio.yml','archive':'speech-archive.yml'}

def parsed(value):
    try:
        result=datetime.fromisoformat(value.replace('Z','+00:00'))
        return result if result.tzinfo else None
    except (ValueError,TypeError,AttributeError):return None

def finished(run):
    return parsed(run.get('updated_at')) or parsed(run.get('created_at'))

def recovery_decision(runs, now, max_age, needed=False, active_timeout=4):
    """A fresh active run owns recovery; manual dispatches have a six-hour cooldown."""
    active=[r for r in runs if r.get('status') in ACTIVE]
    stalled=[r for r in active if (parsed(r.get('run_started_at')) or parsed(r.get('created_at'))) and now-(parsed(r.get('run_started_at')) or parsed(r['created_at']))>timedelta(hours=active_timeout)]
    current=[r for r in active if r not in stalled]
    cancellations={'cancel':[r['id'] for r in stalled]}
    # Workflows themselves have finite timeouts. Do not multiply a queued job
    # during runner shortages, or cancel a healthy collection halfway through.
    if current:return {'dispatch':False,'reason':'already_active',**cancellations}
    manual=[parsed(r.get('created_at')) for r in runs if r.get('event')=='workflow_dispatch']
    if any(t and now-t<timedelta(hours=6) for t in manual):
        return {'dispatch':False,'reason':'recovery_cooldown',**cancellations}
    successes=[r for r in runs if r.get('conclusion')=='success' and finished(r)]
    last=max(successes,key=finished) if successes else None
    failures=[r for r in runs if r.get('conclusion') in ('failure','timed_out','action_required') and finished(r)]
    failed_after_success=any(not last or finished(r)>finished(last) for r in failures)
    stale=not last or now-finished(last)>timedelta(hours=max_age)
    return {'dispatch':bool(needed or stale or failed_after_success or stalled),**cancellations,
            'reason':'stalled_run' if stalled else 'data_health' if needed else 'last_run_failed' if failed_after_success else 'overdue' if stale else 'healthy'}

def data_health(root, now):
    from quote_coverage import coverage
    root=Path(root);issues=[]
    # This reads sources only: it cannot repair a number by inventing a quote.
    quote_report=coverage(root)
    if quote_report['missing']:issues.append({'code':'quote_coverage','count':len(quote_report['missing'])})
    config=json.loads((root/'investors.json').read_text())['investors']
    status=json.loads((root/'run_status.json').read_text()).get('runs',[])
    if status:
        failed=[key for key,row in status[0].get('steps',{}).items() if row.get('status')=='fail']
        if failed:issues.append({'code':'partial_update','steps':failed})
    for person in config:
        if person.get('hkFile'):
            hk=json.loads((root/person['hkFile']).read_text())
            if any(h.get('pending_newer_notices') for h in hk.get('holdings',[])):
                issues.append({'code':'new_hk_notice_unverified','investor':person['id']})
        if not person.get('source13F'):continue
        data=json.loads((root/person['dataFile']).read_text())
        stamp=parsed(data.get('meta',{}).get('lastUpdated'))
        if not stamp or now-stamp>timedelta(hours=36):
            issues.append({'code':'source_stale','investor':person['id']})
        period=parsed(str(data.get('current',{}).get('periodEnd',''))+'T00:00:00+00:00')
        if not period:issues.append({'code':'report_period_missing','investor':person['id']})
        if period:
            # Allow the filing window plus a small weekend/holiday margin.
            month=((now.month-1)//3)*3+1
            quarter_end=datetime(now.year,month,1,tzinfo=timezone.utc)-timedelta(days=1)
            if (now-quarter_end).days<50:
                index=now.year*12+month-1-3
                quarter_end=datetime(index//12,index%12+1,1,tzinfo=timezone.utc)-timedelta(days=1)
            if period.date()<quarter_end.date():
                issues.append({'code':'report_overdue','investor':person['id']})
    personal_path=root/'personal_portfolio.json'
    if personal_path.exists():
        personal=json.loads(personal_path.read_text())
        if personal.get('updateStatus',{}).get('status')=='partial':
            issues.append({'code':'personal_partial','details':personal['updateStatus'].get('failures',[])})
    ai_path=root/'ai_supplement.json'
    if ai_path.exists():
        last=json.loads(ai_path.read_text()).get('lastRun',{})
        if last.get('failed',0) and last.get('pendingAfter',0):issues.append({'code':'ai_incomplete','count':last['pendingAfter']})
    return issues

def plan(evidence, issues, now):
    def target(issue):
        code=str(issue['code'])
        for prefix,key in (('personal_','personal'),('publication_','pages'),('ai_','ai')):
            if code.startswith(prefix):return key
        return 'data'
    decisions={}
    for key in WORKFLOWS:
        max_age={'data':18,'personal':18,'archive':24}.get(key,36)
        decisions[key]=recovery_decision(evidence.get(key,[]),now,max_age,
                                        needed=any(target(issue)==key for issue in issues),
                                        active_timeout=8 if key=='archive' else 4)
    good_data=[r for key in ('data','personal','ai','archive') for r in evidence.get(key,[]) if r.get('conclusion')=='success' and finished(r)]
    good_pages=[r for r in evidence['pages'] if r.get('conclusion')=='success' and finished(r)]
    if good_data:
        data_time=max(map(finished,good_data));page_time=max(map(finished,good_pages),default=None)
        if now-data_time>timedelta(minutes=30) and (page_time is None or page_time<data_time):
            decisions['pages']=recovery_decision(evidence['pages'],now,36,needed=True)
            issues=[*issues,{'code':'publication_missing'}]
    return {'checkedAt':now.isoformat(),'issues':issues,'workflows':decisions}

def published_site_health(root, repository, fetch=None):
    """Check the real deployed entry point and immutable browser snapshots."""
    owner,name=repository.split('/')
    base=f'https://{owner}.github.io/{name}/'
    def get(path):
        request=Request(base+path+('&' if '?' in path else '?')+'health='+str(int(time.time())),headers={'User-Agent':'13f-automation-health'})
        with urlopen(request,timeout=15) as response:
            body=response.read(2_000_001)
        if len(body)>2_000_000:raise ValueError('Unexpectedly large browser asset')
        return body
    fetch=fetch or get
    index=fetch('index.html').decode()
    if 'id="summaryCards"' not in index or 'id="investorSelect"' not in index:raise ValueError('Published page entry point is incomplete')
    script=re.search(r'<script\s+src="(app\.js(?:\?[^"<>]*)?)"',index)
    if not script or 'function switchInvestor' not in fetch(script[1]).decode():raise ValueError('Published application script is missing')
    manifest=json.loads(fetch('browser/manifest.json'))
    people=json.loads((Path(root)/'investors.json').read_text())['investors']
    for person in people:
        if person!=people[0] and not person.get('browserHoldingLimit'):continue
        record=manifest['investors'][person['id']]['snapshot'];path=record['file']
        if not re.fullmatch(r'browser/[a-z0-9_-]+-current-[0-9a-f]{24}\.json',path):raise ValueError('Invalid published asset path')
        raw=fetch(path)
        if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Published snapshot digest mismatch')
        bundle=json.loads(raw)
        if bundle.get('investor')!=person['id']:raise ValueError('Published investor snapshot mismatch')
        limit=person.get('browserHoldingLimit')
        if limit and len(bundle['data']['current']['holdings'])>limit:raise ValueError('Published portfolio limit was not applied')
    return {'status':'checked','url':base}

class GitHub:
    def __init__(self,repository,token):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repository):raise ValueError('Invalid repository')
        self.base='https://api.github.com/repos/'+repository
        self.token=token

    def request(self,path,body=None):
        headers={'Accept':'application/vnd.github+json','User-Agent':'13f-automation-health','X-GitHub-Api-Version':'2022-11-28'}
        if self.token:headers['Authorization']='Bearer '+self.token
        if body is not None:headers['Content-Type']='application/json'
        req=Request(self.base+path,headers=headers,data=json.dumps(body).encode() if body is not None else None)
        # A lost dispatch response is ambiguous. Never blindly retry a POST.
        for attempt in range(1 if body is not None else 3):
            try:
                with urlopen(req,timeout=25) as response:
                    raw=response.read()
                    return json.loads(raw) if raw else None
            except (HTTPError,URLError,TimeoutError) as exc:
                if body is not None or attempt==2 or isinstance(exc,HTTPError) and exc.code not in (429,500,502,503,504):raise
                time.sleep(2**attempt)

    def runs(self,workflow):
        value=self.request('/actions/workflows/'+workflow+'/runs?branch=master&per_page=50')
        if not isinstance(value.get('workflow_runs'),list):raise ValueError('Unexpected workflow response')
        return value['workflow_runs']

    def dispatch(self,workflow):
        if not self.token:raise ValueError('Workflow recovery requires the repository token')
        return self.request('/actions/workflows/'+workflow+'/dispatches',{'ref':'master'})

    def cancel(self,run_id):
        if type(run_id) is not int or run_id<=0:raise ValueError('Invalid stalled run ID')
        return self.request('/actions/runs/'+str(run_id)+'/cancel',{})

def main():
    args=argparse.ArgumentParser();args.add_argument('--repair',action='store_true');args.add_argument('--output',default='automation-health-report.json');options=args.parse_args()
    root=Path(__file__).resolve().parent;now=datetime.now(timezone.utc)
    repository=os.environ['GITHUB_REPOSITORY']
    api=GitHub(repository,os.environ.get('GITHUB_TOKEN',''))
    report={'checkedAt':now.isoformat(),'issues':[],'workflows':{}}
    try:
        evidence={};unavailable={}
        for key,file in WORKFLOWS.items():
            try:evidence[key]=api.runs(file)
            except Exception as exc:evidence[key]=[];unavailable[key]=str(exc)
        try:issues=data_health(root,now)
        except Exception as exc:issues=[{'code':'health_validation_failed','reason':str(exc)}]
        try:site=published_site_health(root,repository)
        except Exception as exc:
            site={'status':'unavailable','reason':str(exc)}
            issues.append({'code':'publication_probe_failed','reason':str(exc)})
        report=plan(evidence,issues,now)
        report['site']=site
        for key,error in unavailable.items():report['workflows'][key]={'dispatch':False,'reason':'workflow_api_unavailable','error':error}
        for key,decision in report['workflows'].items():
            try:
                if options.repair:
                    for run_id in decision.get('cancel',[]):
                        try:api.cancel(run_id)
                        except HTTPError as exc:
                            if exc.code not in (404,409):raise
                if options.repair and decision['dispatch']:
                    api.dispatch(WORKFLOWS[key]);decision['action']='dispatched'
            except Exception as exc:
                decision.update(action='recovery_failed',error=str(exc))
        print(json.dumps(report,ensure_ascii=False,indent=2))
        if unavailable or any(r.get('action')=='recovery_failed' for r in report['workflows'].values()):raise RuntimeError('Some automatic recovery actions could not complete; see retained report')
    finally:
        Path(options.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        if summary:=os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(summary,'a') as f:
                f.write('## 自动巡检\n\n'+''.join(f"- {key}: {row.get('action',row['reason'])}\n" for key,row in report['workflows'].items()))

if __name__=='__main__':main()
