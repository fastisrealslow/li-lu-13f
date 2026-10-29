import shutil,subprocess,tempfile,unittest
from pathlib import Path
from publish_validated_update import publish

ROOT=Path(__file__).resolve().parents[1]

def git(root,*args):
 return subprocess.check_output(['git',*args],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()

class PublicationRetryTests(unittest.TestCase):
 def test_competing_archive_commit_is_preserved_and_retried_without_force_push(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);remote=root/'remote.git';subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
   a=root/'updater';git(root,'clone',str(remote),str(a));git(a,'checkout','-b','master');git(a,'config','user.name','Test');git(a,'config','user.email','test@example.org')
   (a/'.github/workflows').mkdir(parents=True);(a/'.github/workflows/update.yml').write_text('on:\n  push:\n    paths:\n      - "rules.py"\n')
   shutil.copy(ROOT/'update_source_guard.py',a/'update_source_guard.py');(a/'rules.py').write_text('VERSION=1\n');(a/'portfolio.json').write_text('{"value":1}');git(a,'add','.');git(a,'commit','-m','initial');git(a,'push','-u','origin','master');base=git(a,'rev-parse','HEAD')
   b=root/'archive';git(root,'clone','-b','master',str(remote),str(b));git(b,'config','user.name','Archive');git(b,'config','user.email','archive@example.org')
   (a/'portfolio.json').write_text('{"value":2}');git(a,'add','.');git(a,'commit','-m','computed data')
   checks=[]
   def prepare(repo):
    checks.append((repo/'portfolio.json').read_text())
    if len(checks)==1:
     (b/'archive.json').write_text('{"new":true}');git(b,'add','.');git(b,'commit','-m','concurrent archive');git(b,'push','origin','HEAD:master')
   self.assertTrue(publish(a,base,prepare=prepare,pause=lambda _:None))
   self.assertEqual(len(checks),2)
   self.assertEqual(git(remote,'show','master:portfolio.json'),'{"value":2}')
   self.assertEqual(git(remote,'show','master:archive.json'),'{"new":true}')
   self.assertEqual(git(a,'rev-parse','HEAD'),git(remote,'rev-parse','master'))
