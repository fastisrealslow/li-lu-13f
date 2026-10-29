import json
import tempfile
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
import automation_health as health

NOW=datetime(2026,10,29,10,tzinfo=timezone.utc)
def run(hours=1,conclusion='success',status='completed',event='schedule',ident=1):
    stamp=(NOW-timedelta(hours=hours)).isoformat()
    return dict(id=ident,created_at=stamp,updated_at=stamp,conclusion=conclusion,status=status,event=event)

class AutomationHealthTests(unittest.TestCase):
    def test_healthy_and_cancelled_obsolete_runs_do_not_trigger_recovery(self):
        self.assertFalse(health.recovery_decision([run(),run(.5,'cancelled')],NOW,18)['dispatch'])

    def test_missing_schedule_and_failure_after_success_are_recovered(self):
        for rows in ([],[run(24)],[run(1,'failure'),run(2)]):
            self.assertTrue(health.recovery_decision(rows,NOW,18)['dispatch'])

    def test_active_work_and_manual_cooldown_prevent_a_dispatch_storm(self):
        self.assertEqual(health.recovery_decision([run(1,None,'queued')],NOW,18,True)['reason'],'already_active')
        self.assertEqual(health.recovery_decision([run(2,'failure',event='workflow_dispatch')],NOW,18,True)['reason'],'recovery_cooldown')

    def test_a_stuck_job_is_cancelled_without_cancelling_a_fresh_job(self):
        decision=health.recovery_decision([run(5,None,'in_progress',ident=17)],NOW,18)
        self.assertEqual(decision['cancel'],[17]);self.assertTrue(decision['dispatch'])
        decision=health.recovery_decision([run(5,None,'queued',ident=17),run(1,None,'pending',ident=18)],NOW,18)
        self.assertEqual(decision['cancel'],[17]);self.assertFalse(decision['dispatch'])

    def test_publication_is_recovered_only_after_a_grace_period(self):
        evidence={'data':[run(1)],'pages':[run(2)],'ai':[run(1)]}
        result=health.plan(evidence,[],NOW)
        self.assertTrue(result['workflows']['pages']['dispatch'])
        self.assertIn({'code':'publication_missing'},result['issues'])
        evidence['data']=[run(.2)]
        self.assertFalse(health.plan(evidence,[],NOW)['workflows']['pages']['dispatch'])

    def test_partial_published_update_is_retried_but_old_history_warnings_are_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'investors.json').write_text(json.dumps({'investors':[]}))
            (root/'run_status.json').write_text(json.dumps({'runs':[{'steps':{'history':{'status':'warn'}}}]}))
            with patch('quote_coverage.coverage',return_value={'missing':[]}):
                self.assertEqual(health.data_health(root,NOW),[])
                (root/'run_status.json').write_text(json.dumps({'runs':[{'steps':{'fund_13f':{'status':'fail'}}}]}))
                self.assertEqual(health.data_health(root,NOW),[{'code':'partial_update','steps':['fund_13f']}])

    def test_indeterminate_dispatch_is_not_retried_and_get_requests_can_retry(self):
        api=health.GitHub('owner/repo','test-token')
        with patch.object(health,'urlopen',side_effect=URLError('interrupted')) as request,patch.object(health.time,'sleep'):
            with self.assertRaises(URLError):api.dispatch('update.yml')
            self.assertEqual(request.call_count,1)
            with self.assertRaises(URLError):api.runs('update.yml')
            self.assertEqual(request.call_count,4)

    def test_repository_and_stalled_job_identifiers_are_checked(self):
        with self.assertRaises(ValueError):health.GitHub('owner/repo/../../secrets','x')
        with self.assertRaises(ValueError):health.GitHub('owner/repo','x').cancel('1/anything')


    def test_long_archive_job_has_its_own_timeout_and_personal_failure_targets_its_workflow(self):
        evidence={'data':[run()],'pages':[run(.1)],'ai':[run()],'personal':[run()],'archive':[run(5,None,'in_progress')]}
        result=health.plan(evidence,[{'code':'personal_partial'}],NOW)
        self.assertTrue(result['workflows']['personal']['dispatch'])
        self.assertFalse(result['workflows']['data']['dispatch'])
        self.assertFalse(result['workflows']['archive']['dispatch'])
        self.assertEqual(result['workflows']['archive']['cancel'],[])

    def test_a_rerun_uses_its_new_start_time_instead_of_the_original_creation_time(self):
        row=run(48,None,'in_progress');row['run_started_at']=(NOW-timedelta(minutes=10)).isoformat()
        result=health.recovery_decision([row],NOW,18)
        self.assertEqual(result['reason'],'already_active');self.assertEqual(result['cancel'],[])


    def test_live_site_probe_checks_asset_identity_hash_and_large_portfolio_limit(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'investors.json').write_text(json.dumps({'investors':[{'id':'test','browserHoldingLimit':2}]}))
            asset='browser/test-current-'+'a'*24+'.json'
            body=json.dumps({'investor':'test','data':{'current':{'holdings':[{},{}]}}}).encode()
            manifest={'investors':{'test':{'snapshot':{'file':asset,'sha256':hashlib.sha256(body).hexdigest()}}}}
            files={'index.html':b'<div id="summaryCards"></div><select id="investorSelect"></select><script src="app.js?v=1"></script>','app.js?v=1':b'function switchInvestor() {}',asset:body}
            def get(path):return json.dumps(manifest).encode() if path=='browser/manifest.json' else files[path]
            self.assertEqual(health.published_site_health(root,'owner/repo',get)['status'],'checked')
            files[asset]=body+b' '
            with self.assertRaisesRegex(ValueError,'digest'):health.published_site_health(root,'owner/repo',get)
            files[asset]=json.dumps({'investor':'test','data':{'current':{'holdings':[{}, {}, {}]}}}).encode()
            manifest['investors']['test']['snapshot']['sha256']=hashlib.sha256(files[asset]).hexdigest()
            with self.assertRaisesRegex(ValueError,'limit'):health.published_site_health(root,'owner/repo',get)

    def test_an_old_report_is_detected_even_while_the_newest_quarter_is_not_due(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);now=datetime(2027,1,10,tzinfo=timezone.utc)
            (root/'investors.json').write_text(json.dumps({'investors':[{'id':'test','source13F':True,'dataFile':'fund.json'}]}))
            (root/'run_status.json').write_text('{"runs":[]}')
            (root/'fund.json').write_text(json.dumps({'meta':{'lastUpdated':now.isoformat()},'current':{'periodEnd':'2026-06-30'}}))
            with patch('quote_coverage.coverage',return_value={'missing':[]}):
                self.assertIn({'code':'report_overdue','investor':'test'},health.data_health(root,now))

    def test_website_failure_targets_publication_instead_of_financial_collection(self):
        evidence={key:[run()] for key in health.WORKFLOWS}
        decisions=health.plan(evidence,[{'code':'publication_probe_failed'}],NOW)['workflows']
        self.assertTrue(decisions['pages']['dispatch']);self.assertFalse(decisions['data']['dispatch'])
