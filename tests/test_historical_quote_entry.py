import json,tempfile,unittest
from pathlib import Path
from datetime import datetime,timezone
from unittest.mock import patch
import historical_quote_refresh as refresh

class QuoteEntryTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,11,17,12,tzinfo=timezone.utc)
        self.quote={'c':100,'t':datetime(2026,11,16,21,tzinfo=timezone.utc).timestamp(),
                    'symbol':'TEST','currency':'USD','fetchedAt':self.now.isoformat()}
    def test_empty_retired_and_stale_do_not_require_prior_or_undefined_now(self):
        with patch.dict(refresh.SESSION_QUOTES,{},clear=True),tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'prices.json'
            for quotes in ({},{'TEST':{**self.quote,'status':'ceased_trading'}},{'TEST':{**self.quote,'t':1}}):
                p.write_text(json.dumps({'quotes':quotes}))
                refresh.seed_session_quotes([{'pricesFile':p.name}],root,self.now)
                self.assertEqual(refresh.SESSION_QUOTES,{})
    def test_newest_verified_quote_wins_and_symbol_mismatch_is_not_shared(self):
        with patch.dict(refresh.SESSION_QUOTES,{},clear=True),tempfile.TemporaryDirectory() as d:
            root=Path(d);configs=[]
            for i,q in enumerate([self.quote,{**self.quote,'t':self.quote['t']-60},
                                  {**self.quote,'symbol':'WRONG'},{**self.quote,'currency':'HKD'}]):
                p=root/f'{i}.json';p.write_text(json.dumps({'quotes':{'TEST':q}}));configs.append({'pricesFile':p.name})
            refresh.seed_session_quotes(configs,root,self.now)
            self.assertEqual(refresh.SESSION_QUOTES,{'TEST':self.quote})
    def test_share_class_alias_reuses_same_symbol_only(self):
        with patch.dict(refresh.SESSION_QUOTES,{},clear=True),tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'prices.json';q={**self.quote,'symbol':'BRK-B'}
            p.write_text(json.dumps({'quotes':{'BRK.B':q}}))
            refresh.seed_session_quotes([{'pricesFile':p.name}],root,self.now)
            self.assertEqual(refresh.SESSION_QUOTES,{'BRK-B':q})

    def test_real_cli_handles_empty_and_populated_quote_files_without_network(self):
        import os,subprocess,sys,time,shutil
        repo=Path(__file__).resolve().parents[1]
        for quotes in ({},{'TEST':{**self.quote,'t':int(time.time()),'fetchedAt':datetime.now(timezone.utc).isoformat()}}):
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);shutil.copyfile(repo/'historical_quote_refresh.py',root/'historical_quote_refresh.py')
                (root/'investors.json').write_text(json.dumps({'investors':[{'id':'sample','source13F':True,'dataFile':'data.json','pricesFile':'prices.json'}]}))
                (root/'data.json').write_text(json.dumps({'current':{'quarter':'2026 Q3','holdings':[]},'history':{'holdings':{}}}))
                (root/'prices.json').write_text(json.dumps({'quotes':quotes}))
                env={**os.environ,'PYTHONPATH':str(repo)}
                out=subprocess.run([sys.executable,str(root/'historical_quote_refresh.py'),'--limit','0'],cwd=root,env=env,text=True,capture_output=True,timeout=30)
                self.assertEqual(out.returncode,0,out.stderr)
                self.assertIn('sample',out.stdout)
                self.assertEqual(json.loads((root/'prices.json').read_text())['quotes'],quotes)
