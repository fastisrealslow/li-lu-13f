import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import update_investors as updater


def snapshot(phase):
    return json.dumps({'meta':{'phase':phase},'current':{'quarter':'2026 Q2','holdings':[],'totalValue':0}})


class InvestorTransactions(unittest.TestCase):
    def test_failed_phase_rolls_back_both_files_and_other_investors_continue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);people=[dict(id=i,name=i,source13F=True,dataFile=i+'.json',pricesFile=i+'_prices.json') for i in ['bad','good']]
            for p in people:
                (root/p['dataFile']).write_text(snapshot('before'))
                (root/p['pricesFile']).write_text('{"quotes":{},"phase":"before"}')
            def runner(args,**kwargs):
                if '--cached-only' in args:return subprocess.CompletedProcess(args,0)
                ident=args[args.index('--investor')+1]
                (root/(ident+'.json')).write_text(snapshot('after'))
                (root/(ident+'_prices.json')).write_text('{"quotes":{},"phase":"after"}')
                return subprocess.CompletedProcess(args,1 if ident=='bad' and args[2]=='audit_13f_history.py' else 0)
            with patch.object(updater,'ROOT',root),patch.dict('os.environ',{'TRACK_RUN_STATUS':'0'}):
                self.assertEqual(updater.run(people,runner,pause=lambda _:None),['bad_audit'])
            self.assertEqual((root/'bad.json').read_text(),snapshot('before'))
            self.assertEqual(json.loads((root/'bad_prices.json').read_text())['phase'],'before')
            self.assertEqual((root/'good.json').read_text(),snapshot('after'))

    def test_retry_restores_the_phase_before_a_second_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'fund.json';path.write_text(snapshot('before'));attempts=[]
            investor=dict(id='fund',name='Fund',source13F=False,dataFile='fund.json')
            def runner(args,**kwargs):
                if args[2]!='fetch_webb_holdings.py':return subprocess.CompletedProcess(args,0)
                attempts.append(path.read_text());path.write_text('partial' if len(attempts)==1 else snapshot('complete'))
                if len(attempts)==1:raise subprocess.TimeoutExpired(args,1)
                return subprocess.CompletedProcess(args,0)
            with patch.object(updater,'ROOT',root),patch.dict('os.environ',{'TRACK_RUN_STATUS':'0'}):
                self.assertEqual(updater.run([investor],runner,pause=lambda _:None),[])
            self.assertEqual(attempts,[snapshot('before')]*2);self.assertEqual(path.read_text(),snapshot('complete'))

    def test_successful_process_with_broken_output_is_rolled_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'fund.json';path.write_text(snapshot('before'))
            investor=dict(id='fund',name='Fund',source13F=False,dataFile='fund.json')
            def runner(args,**kwargs):
                if '--cached-only' not in args:path.write_text('{incomplete')
                return subprocess.CompletedProcess(args,0)
            with patch.object(updater,'ROOT',root),patch.dict('os.environ',{'TRACK_RUN_STATUS':'0'}):
                self.assertEqual(updater.run([investor],runner,pause=lambda _:None),['fund_snapshot'])
            self.assertEqual(path.read_text(),snapshot('before'))

    def test_preflight_timeout_cannot_leave_partially_changed_holdings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'fund.json';path.write_text(snapshot('before'))
            def runner(args,**kwargs):
                path.write_text('partial');raise subprocess.TimeoutExpired(args,1)
            with patch.object(updater,'ROOT',root),patch.dict('os.environ',{'TRACK_RUN_STATUS':'0'}):
                self.assertEqual(updater.run([dict(id='fund',name='Fund',dataFile='fund.json')],runner),['resolve_cusip'])
            self.assertEqual(path.read_text(),snapshot('before'))

    def test_process_start_failure_does_not_block_the_next_investor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);seen=[]
            people=[dict(id=i,name=i,source13F=True,dataFile=i+'.json') for i in ['bad','good']]
            for person in people:(root/person['dataFile']).write_text(snapshot('before'))
            def runner(args,**kwargs):
                if '--cached-only' in args:return subprocess.CompletedProcess(args,0)
                ident=args[args.index('--investor')+1];seen.append(ident)
                if ident=='bad':raise OSError('Resource temporarily unavailable')
                return subprocess.CompletedProcess(args,0)
            with patch.object(updater,'ROOT',root),patch.dict('os.environ',{'TRACK_RUN_STATUS':'0'}):
                self.assertEqual(updater.run(people,runner,pause=lambda _:None),['bad_13f'])
            self.assertIn('good',seen)
            self.assertEqual((root/'bad.json').read_text(),snapshot('before'))
