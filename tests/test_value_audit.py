import copy,json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
import audit_13f_history as audit
import fetch_13f_all as sec
import validate_data
from resolve_unmapped_tickers import backfill_data_files


def rows(scale=1):
 return [dict(ticker=tk,cusip=tk,name=tk,cls='COM',shares=1000,value=100000*scale,shareType='SH',putCall='') for tk in ['AAA','BBB','CCC']]

def price(tk,q):return dict(price=100,date='2023-03-31',currency='USD',url='https://quote.example/'+tk)

def xml():
 return ('<informationTable xmlns="'+sec.NS['ns']+'">'+''.join(f'<infoTable><nameOfIssuer>{h["ticker"]}</nameOfIssuer><titleOfClass>COM</titleOfClass><cusip>{h["cusip"]}</cusip><value>{h["value"]}</value><shrsOrPrnAmt><sshPrnamt>1000</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt></infoTable>' for h in rows())+'</informationTable>').encode()

class ValueAudit(unittest.TestCase):
 def setUp(self):
  self.resolver=patch.object(sec,"resolve_ticker",side_effect=lambda n,c,k:k);self.resolver.start();self.addCleanup(self.resolver.stop)
 def test_units_need_three_distinct_consistent_ordinary_securities(self):
  self.assertEqual(audit.verify_units(rows(.001),'2023 Q1',price)['factor'],1000)
  self.assertEqual(audit.verify_units(rows(1000),'2023 Q1',price)['factor'],.001)
  self.assertEqual(audit.verify_units(rows()[:2],'2023 Q1',price)['status'],'pending')
  mixed=rows();mixed[0]['value']*=1000
  self.assertEqual(audit.verify_units(mixed,'2023 Q1',price)['status'],'pending')
  duplicates=[rows()[0]]*5
  self.assertEqual(audit.verify_units(duplicates,'2023 Q1',price)['status'],'pending')
 def test_penny_stocks_and_options_do_not_trigger_guessing(self):
  result=audit.verify_units(rows(.001),'2023 Q1',lambda tk,q:{**price(tk,q),'price':.1})
  self.assertEqual(result['factor'],1)
  holdings=rows(.001);holdings[0]['putCall']='CALL';holdings.append({**rows(.001)[0],'cls':'W EXP 2019'})
  self.assertEqual(audit.verify_units(holdings,'2023 Q1',price)['status'],'pending')
 def test_one_nonmatching_corporate_action_quote_does_not_block_four_price_proofs(self):
  holdings=rows(.001)+[{**rows(.001)[0],'ticker':'DDD'},{**rows(.001)[0],'ticker':'EEE'}]
  result=audit.verify_units(holdings,'2023 Q1',lambda tk,q:{**price(tk,q),'price':103 if tk=='EEE' else 100})
  self.assertEqual(result['factor'],1000)
  self.assertEqual(result['outlierTickers'],['EEE'])
  holdings[-1]['value']=100000
  self.assertEqual(audit.verify_units(holdings,'2023 Q1',price)['status'],'pending')
 def test_split_adjusted_price_is_restored_without_undoing_past_splits(self):
  stamp=int(datetime(2023,3,31,15,tzinfo=timezone.utc).timestamp());future=stamp+86400
  chart={'meta':{'currency':'USD'},'timestamp':[stamp], 'indicators':{'quote':[{'close':[5]}]},'events':{'splits':{'old':{'date':stamp-86400,'numerator':2,'denominator':1},'future':{'date':future,'numerator':20,'denominator':1}}}}
  self.assertEqual(audit.actual_close(chart,datetime(2023,3,31).date())['price'],100)
  chart['meta']['currency']='HKD'
  with self.assertRaises(ValueError):audit.actual_close(chart,datetime(2023,3,31).date())
 def test_source_reparse_repairs_mixed_cache_and_rebuilds_current(self):
  bad=rows();bad[0]['value']*=1000
  source={'url':'https://www.sec.gov/Archives/test.xml','filingDate':'2023-05-15'}
  d={'meta':{},'current':{'quarter':'2023 Q1','holdings':bad},'history':{'quarters':['2023 Q1'],'values':[sum(h['value'] for h in bad)/1e6],'holdings':{'2023 Q1':bad},'filing_sources':{'2023 Q1':source}}}
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'d.json';path.write_text(json.dumps(d));cfg={'path':str(path),'cik':'1'}
   result=audit.audit_investor('test',cfg,1,lambda u:xml(),price)
   self.assertEqual(result['current']['totalValue'],300000)
   self.assertEqual(result['history']['values'],[.3])
   self.assertEqual(result['history']['valueAudit']['2023 Q1']['status'],'verified')
   with patch.object(sec,'sec_fetch',side_effect=AssertionError('verified immutable source fetched again')):
    audit.audit_investor('test',cfg,1)
 def test_failed_source_is_retryable_and_never_zero_filled(self):
  d={'meta':{},'current':{'quarter':'2023 Q1','holdings':rows()},'history':{'quarters':['2023 Q1'],'values':[.3],'holdings':{'2023 Q1':rows()},'filing_sources':{'2023 Q1':{'url':'https://www.sec.gov/x.xml','filingDate':'2023-05-15'}}}}
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'d.json';path.write_text(json.dumps(d));cfg={'path':str(path),'cik':'1'}
   def fail(u):raise TimeoutError('temporary source timeout')
   result=audit.audit_investor('test',cfg,1,fail,price)
   self.assertEqual(result['history']['values'],[.3]);record=result['history']['valueAudit']['2023 Q1']
   self.assertEqual(record['status'],'pending');record['checkedAt']='2020-01-01';path.write_text(json.dumps(result))
   result=audit.audit_investor('test',cfg,1,lambda u:xml(),price)
   self.assertEqual(result['history']['valueAudit']['2023 Q1']['status'],'verified')
 def test_cached_proof_normalizes_a_repeated_nonconforming_latest_filing(self):
  source=rows(.001);normalized=rows();record={'version':audit.VERSION,'status':'verified','factor':1000,'sourceHash':audit.digest(source),'normalizedHash':audit.digest(normalized),'checkedAt':datetime.now(timezone.utc).date().isoformat()}
  d={'meta':{},'current':{'quarter':'2023 Q1','holdings':source},'history':{'quarters':['2023 Q1'],'values':[.0003],'holdings':{'2023 Q1':source},'valueAudit':{'2023 Q1':record}}}
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'d.json';path.write_text(json.dumps(d));result=audit.audit_investor('test',{'path':str(path),'cik':'1'},0)
   self.assertEqual(result['history']['values'],[.3]);self.assertEqual(result['current']['totalValue'],300000)

 def test_release_validation_rejects_a_stale_source_audit(self):
  holdings=rows();proof={'version':audit.VERSION,'status':'verified','factor':1,'normalizedHash':audit.digest(holdings),'source':'https://www.sec.gov/Archives/test.xml','anchors':audit.verify_units(holdings,'2023 Q1',price)['anchors']}
  h={'quarters':['2023 Q1'],'values':[.3],'holdings':{'2023 Q1':holdings},'valueAudit':{'2023 Q1':proof}}
  validate_data.validate_history(h)
  holdings[0]['value']*=1000;h['values'][0]=sum(r['value'] for r in holdings)/1e6
  with self.assertRaisesRegex(ValueError,'no longer match'):validate_data.validate_history(h)

 def test_only_restatement_amendments_can_replace_original_portfolios(self):
  table={'form':['13F-HR/A','13F-HR/A'],'reportDate':['2023-03-31','2023-03-31'],'accessionNumber':['0000000001-23-000002','0000000001-23-000003'],'filingDate':['2023-05-20','2023-05-21'],'primaryDocument':['additive.xml','restatement.xml']}
  def fetch(path):
   if path.startswith('submissions/'):return json.dumps({'filings':{'recent':table}}).encode()
   return ('<root><amendmentType>'+('NEW HOLDINGS' if path.endswith('additive.xml') else 'RESTATEMENT')+'</amendmentType></root>').encode()
  history={'filing_sources':{'2023 Q1':{'filingDate':'2023-05-15'}}}
  with patch.object(sec,'find_info_table_xml',return_value='/Archives/restated.xml'):
   replacements=audit.discover_restatements({'cik':'1'},history,{'2023 Q1'},fetch)
  self.assertEqual(replacements['2023 Q1']['accessionDashed'],'0000000001-23-000003')
  self.assertEqual(history['restatementChecks']['0000000001-23-000002']['result'],'additive')

 def test_symbol_resolution_preserves_intact_source_proof_and_is_idempotent(self):
  holdings=rows();holdings[0]['ticker']='?UNRESOLVED COMPANY'
  proof={'version':audit.VERSION,'status':'verified','factor':1,'normalizedHash':audit.digest(holdings),'sourceHash':audit.digest(holdings),'source':'https://www.sec.gov/Archives/test.xml','anchors':audit.verify_units(rows(),'2023 Q1',price)['anchors']}
  d={'current':{'holdings':copy.deepcopy(holdings)},'history':{'quarters':['2023 Q1'],'values':[.3],'holdings':{'2023 Q1':holdings},'valueAudit':{'2023 Q1':proof}}}
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'d.json';p.write_text(json.dumps(d))
   self.assertEqual(backfill_data_files([str(p)],{'AAA':'AAA'}),(1,2))
   resolved=json.loads(p.read_text());validate_data.validate_history(resolved['history'])
   self.assertEqual(resolved['history']['holdings']['2023 Q1'][0]['ticker'],'AAA')
   self.assertEqual(resolved['history']['valueAudit']['2023 Q1']['sourceHash'],audit.digest(rows()))
   self.assertEqual(backfill_data_files([str(p)],{'AAA':'AAA'}),(0,0))
   self.assertEqual([(r['shares'],r['value']) for r in holdings],[(r['shares'],r['value']) for r in resolved['history']['holdings']['2023 Q1']])

 def test_symbol_resolution_does_not_bless_changed_source_facts(self):
  for field in ['shares','value','cusip','putCall','shareType']:
   with self.subTest(field=field),tempfile.TemporaryDirectory() as tmp:
    holdings=rows();holdings[0]['ticker']='?UNRESOLVED COMPANY'
    proof={'version':audit.VERSION,'status':'verified','normalizedHash':audit.digest(holdings)}
    holdings[1][field]=holdings[1][field]+1 if field in ['shares','value'] else 'CHANGED'
    h={'quarters':['2023 Q1'],'values':[sum(r['value'] for r in holdings)/1e6],'holdings':{'2023 Q1':holdings},'valueAudit':{'2023 Q1':proof}}
    p=Path(tmp)/'d.json';p.write_text(json.dumps({'history':h}))
    backfill_data_files([str(p)],{'AAA':'AAA'})
    with self.assertRaisesRegex(ValueError,'no longer match'):
     validate_data.validate_history(json.loads(p.read_text())['history'])

 def test_resolved_symbol_keeps_raw_unit_replay_and_rejects_quantity_changes(self):
  for factor in (1000, .001):
   with self.subTest(factor=factor),tempfile.TemporaryDirectory() as tmp:
    normalized=rows()+[{**rows()[0],'cusip':'DDD','ticker':'?UNRESOLVED'}]
    raw=copy.deepcopy(normalized)
    for row in raw:row['value']=round(row['value']/factor)
    proof={'version':audit.VERSION,'status':'verified','factor':factor,
           'sourceHash':audit.digest(raw),'normalizedHash':audit.digest(normalized),
           'sourceDigest':'unchanged-primary-document',
           'source':'https://www.sec.gov/Archives/test.xml',
           'checkedAt':datetime.now(timezone.utc).date().isoformat(),
           'anchors':audit.verify_units(raw,'2023 Q1',lambda tk,q:price(tk,q))['anchors']}
    d={'meta':{},'current':{'quarter':'2023 Q1','holdings':copy.deepcopy(normalized)},
       'history':{'quarters':['2023 Q1'],'values':[.4],'holdings':{'2023 Q1':normalized},'valueAudit':{'2023 Q1':proof}}}
    p=Path(tmp)/'d.json';p.write_text(json.dumps(d))
    backfill_data_files([str(p)],{'DDD':'DDD'})
    resolved=json.loads(p.read_text());validate_data.validate_history(resolved['history'])
    rebound=resolved['history']['valueAudit']['2023 Q1']
    self.assertEqual(rebound['sourceDigest'],proof['sourceDigest'])
    self.assertEqual(rebound['sourceHash'],proof['sourceHash'])
    raw[-1]['ticker']='DDD'
    self.assertTrue(audit.matches_source(raw,rebound))
    tampered=copy.deepcopy(raw);tampered[0]['shares']+=1
    self.assertFalse(audit.matches_source(tampered,rebound))
    resolved['history']['holdings']['2023 Q1']=raw
    resolved['history']['values']=[sum(row['value'] for row in raw)/1e6]
    resolved['current']['holdings']=copy.deepcopy(raw);p.write_text(json.dumps(resolved))
    replayed=audit.audit_investor('test',{'path':str(p),'cik':'1'},0)
    self.assertEqual(replayed['current']['totalValue'],400000)
    validate_data.validate_history(replayed['history'])

if __name__=='__main__':unittest.main()

class ParserProofReplayTests(unittest.TestCase):
    def test_identical_original_replays_independent_quotes_and_changed_original_is_rejected(self):
        import hashlib
        import audit_13f_history as a
        rows=[dict(ticker=t,cusip=str(i),shares=10,value=100,putCall='',shareType='SH') for i,t in enumerate(['AAA','BBB','CCC'])]
        raw=b'original SEC filing'
        proof=a.verify_units(rows,'2000 Q1',lambda t,q:dict(price=10,date='2000-03-31',currency='USD',url='https://query1.finance.yahoo.com/'+t))
        data={'history':{'valueAudit':{'2000 Q1':dict(proof,sourceDigest=hashlib.sha256(raw).hexdigest())}}}
        a.refresh_parser_proof(data,'2000 Q1',rows,raw)
        self.assertEqual(data['history']['valueAudit']['2000 Q1']['normalizedHash'],a.digest(rows))
        with self.assertRaises(ValueError):a.refresh_parser_proof(data,'2000 Q1',rows,b'revised original')
