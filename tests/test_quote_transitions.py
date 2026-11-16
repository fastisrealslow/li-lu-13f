import copy,json,tempfile,time,unittest
from pathlib import Path
from datetime import date
from unittest.mock import patch
from quote_transitions import ACTION,apply,transition_for
import quote_coverage as qc

H={'ticker':'INDV','cusip':'45579U109','shareType':'SH','putCall':'','shares':94850,'value':3891696,'name':'INDIVIOR PHARMACEUTICALS INC'}
OLD={'ticker':'SUPN','cusip':'868459108','shareType':'SH','shares':7422,'value':345197,'name':'SUPERNUS PHARMACEUTICALS'}
def quote():return dict(c=29.72,t=int(time.time())-60,symbol='SUPN',currency='USD',verifiedName='Supernus, Inc.',source='test',sourceURL='https://finance.yahoo.com/quote/SUPN/')
class Transitions(unittest.TestCase):
 def test_strict_identity_date_and_instrument(self):
  self.assertIsNotNone(transition_for(H,date(2026,11,3)))
  self.assertIsNone(transition_for(H,date(2026,11,2)))
  for h in [OLD,{**H,'putCall':'PUT'},{**H,'shareType':'PRN'},{**H,'cusip':'other'},{**H,'ticker':'SUPN'}]:self.assertIsNone(transition_for(h))
 def test_quote_only_no_history_no_ratio_no_dividend_addition(self):
  hs=copy.deepcopy([H,OLD]);saved=copy.deepcopy(hs)
  p={'quotes':{'INDV':{'c':36.28,'t':100,'shareActions':[{'date':'2022-10-11','factor':.2}]},'SUPN':{'status':'ceased_trading'}},'costBasis':{'INDV':{'buy':30},'SUPN':{'buy':45}},'exitPerf':{'INDV':{'return':10}},'tradePrices':{'entries':{'45579U109':{'ticker':'INDV','quarters':[{'quarter':'2026 Q2','buy':40}]}}}}
  trades=copy.deepcopy(p['tradePrices'])
  apply(p,hs,lambda s:{**quote(),'shareActions':[{'date':'2026-11-02','factor':1.5401}]})
  self.assertEqual(hs,saved);self.assertEqual(p['quotes']['INDV']['c'],29.72)
  self.assertEqual(p['quotes']['SUPN'],{'status':'ceased_trading'})
  self.assertEqual(p['quotes']['INDV']['shareActions'],[{'date':'2022-10-11','factor':.2}])
  self.assertNotIn('INDV',p['costBasis']);self.assertEqual(p['costBasis']['SUPN'],{'buy':45})
  self.assertEqual(p['tradePrices'],trades);self.assertNotIn('INDV',p['exitPerf'])
  self.assertEqual(p['corporateActions']['45579U109']['specialDividend']['amount'],8.13)
 def test_bad_or_failed_quote_keeps_actual_old_date(self):
  for q in [{'error':True},{**quote(),'verifiedName':'Supernus Pharmaceuticals, Inc.'},{**quote(),'symbol':'INDV'},{**quote(),'currency':'HKD'},{**quote(),'t':time.time()-20*86400}]:
   p={'quotes':{'INDV':{'c':36.28,'t':100}}};apply(p,[H],lambda _:q)
   self.assertEqual(p['quotes']['INDV'],{'c':36.28,'t':100,'stale':True})
 def test_real_collision_refresh_and_publication(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);cfg={'id':'test','dataFile':'fund.json','pricesFile':'prices.json'}
   event=json.loads(Path('security_lifecycle.json').read_text())['events']['868459108']
   files={'investors.json':{'investors':[cfg]},'fund.json':{'current':{'quarter':'2026 Q2','periodEnd':'2026-06-30','holdings':[H,OLD]}},'prices.json':{'quotes':{'INDV':{'c':36.28,'t':100},'SUPN':quote()},'costBasis':{'INDV':{'recent':{'buy':40}}}},'security_lifecycle.json':{'events':{'868459108':event}}}
   for p,d in files.items():(root/p).write_text(json.dumps(d))
   original=(root/'fund.json').read_bytes()
   with patch.object(qc,'resolve_active'),patch.object(qc,'market_quote',side_effect=lambda s:quote() if s=='SUPN' else {'error':True}),patch('resolve_unmapped_tickers.backfill_data_files'):
    self.assertEqual(qc.refresh(root)['missing'],[])
   p=json.loads((root/'prices.json').read_text())
   self.assertEqual((root/'fund.json').read_bytes(),original)
   self.assertEqual(p['quotes']['INDV']['c'],29.72);self.assertEqual(p['quotes']['SUPN']['status'],'ceased_trading')
   self.assertFalse(p['corporateActions']['45579U109']['preserveCost'])
   self.assertEqual(qc.publication_coverage(root)['unhandled'],[])
 def test_value_screen_never_uses_reused_symbol_or_unadjusted_dividend_cost(self):
  import enrich_metadata as e
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);d=root/'fund.json';p=root/'quotes.json'
   d.write_text(json.dumps({'meta':{},'current':{'quarter':'2026 Q2','totalValue':5000000,'holdings':[H,OLD]}}))
   p.write_text(json.dumps({'quotes':{'INDV':quote(),'SUPN':quote()},'costBasis':{k:{'recent':{'buy':50,'quarter':'2026 Q2'}} for k in ['INDV','SUPN']}}))
   with patch.object(e,'load_investors',return_value=[{'id':'test','name':'test','nameEn':'test','dataFile':str(d),'pricesFile':str(p),'inValueScreen':True}]):
    screen=e._build_value_screen()
   self.assertEqual(screen['candidates'],[])
   self.assertNotIn('SUPN',screen['nearMissMap'])
   self.assertIsNone(screen['nearMissMap']['INDV'][0]['buy'])
if __name__=='__main__':unittest.main()
