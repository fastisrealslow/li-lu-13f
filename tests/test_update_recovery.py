import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from publish_update_failure import merge_failure_status, publish_failure


def failed_run(timestamp='2026-10-11T02:00:00Z'):
    return {'run_id':timestamp,'completedAt':timestamp,'schemaVersion':2,
            'steps':{'validation':{'status':'fail','msg':'Source proof mismatch'}}}


class UpdateRecoveryTests(unittest.TestCase):
    def test_failure_history_preserves_newer_success_and_published_history(self):
        published={'runs':[{'run_id':'2026-10-11T03:00:00Z','steps':{'validation':{'status':'ok'}}},
                           {'run_id':'2026-10-10T03:00:00Z','steps':{'metadata':{'status':'warn'}}}]}
        saved=copy.deepcopy(published)
        result=merge_failure_status(published,{'runs':[failed_run(),{'run_id':'stale-local-history'}]})
        self.assertEqual(published,saved)
        self.assertEqual(len(result['runs']),3)
        self.assertEqual(result['runs'][0],published['runs'][0])
        self.assertEqual(result['runs'][1]['steps']['validation']['status'],'fail')
        self.assertEqual(merge_failure_status(result,{'runs':[failed_run()]}),result)

    def test_incomplete_or_successful_run_cannot_be_published_as_failure(self):
        for run in ({'run_id':'x','steps':{'test':{'status':'fail'}}},
                    {'run_id':'x','completedAt':'x','steps':{'test':{'status':'ok'}}}):
            with self.assertRaises(ValueError):merge_failure_status({'runs':[]},{'runs':[run]})

    def test_failure_publishes_status_only_from_clean_last_good_checkout(self):
        with tempfile.TemporaryDirectory(prefix='failure-publish-test-') as tmp:
            root=Path(tmp);bare=root/'origin.git';repo=root/'repo';repo.mkdir()
            def git(*args,cwd=repo):
                return subprocess.run(['git',*args],cwd=cwd,check=True,capture_output=True,text=True).stdout.strip()
            git('init','--bare',str(bare));git('init','-b','master')
            git('config','user.name','Test');git('config','user.email','test@example.invalid')
            git('remote','add','origin',str(bare))
            (repo/'run_status.json').write_text(json.dumps({'runs':[]}))
            (repo/'fund.json').write_text('{"value":123}')
            # The isolated publisher must run validation against clean data,
            # not the deliberately invalid JSON in the failed job workspace.
            (repo/'validate_data.py').write_text(
                "import json\nfrom pathlib import Path\n"
                "assert json.loads(Path('fund.json').read_text())['value']==123\n"
                "assert json.loads(Path('run_status.json').read_text())['runs'][0]['steps']['validation']['status']=='fail'\n")
            git('add','.');git('commit','-m','Last good data');git('push','-u','origin','master')
            source=git('rev-parse','HEAD')
            (repo/'fund.json').write_text('{unvalidated, broken')
            (repo/'run_status.json').write_text(json.dumps({'runs':[failed_run()]}))
            self.assertTrue(publish_failure(repo,source))
            git('fetch','origin','master')
            self.assertEqual(git('diff','--name-only',source,'origin/master'), 'run_status.json')
            self.assertEqual(json.loads(git('show','origin/master:fund.json')),{'value':123})
            self.assertEqual((repo/'fund.json').read_text(),'{unvalidated, broken')
            self.assertEqual(json.loads(git('show','origin/master:run_status.json'))['runs'][0],failed_run())
            # A newer source implementation owns publication; old failures
            # cannot overwrite it or launch old source rules.
            newer=root/'newer'
            git('clone','--branch','master',str(bare),str(newer))
            git('config','user.name','Test',cwd=newer)
            git('config','user.email','test@example.invalid',cwd=newer)
            (newer/'validate_data.py').write_text('print("new rules")\n')
            git('add','validate_data.py',cwd=newer)
            git('commit','-m','New source rules',cwd=newer)
            git('push','origin','master',cwd=newer)
            self.assertFalse(publish_failure(repo,source))


if __name__=='__main__':
    unittest.main()
