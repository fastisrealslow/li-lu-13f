import copy,json,unittest
from unittest.mock import patch
import hk_listing_completion as listing
from spinoff_events import normalize,RULE_VERSION

class ListingCompletion(unittest.TestCase):
 def test_distribution_completion_requires_actual_payment_and_correct_parent_and_child(self):
  ann={'url':'https://www1.hkexnews.hk/listedco/results.pdf','date':'2026-08-26','title':'Interim results'}
  text='Issuer (Stock Code: 41) A special dividend was distributed on 2 April 2026 in the form of distribution in specie of share stapled units of Child (Stock Code: 1270) to qualifying Shareholders.'
  proof=listing.distribution_proof(text,ann,'Child','01270.HK','00041')
  self.assertEqual(proof['dates']['distributionDate']['date'],'2026-04-02')
  from spinoff_events import merge_evidence
  weaker={**ann,'targetName':'','status':'needs_review','quote':''}
  self.assertEqual(merge_evidence([proof],[weaker])[0]['status'],'completed')
  self.assertIsNone(listing.distribution_proof(text,ann,'Other','09876.HK','00041'))
  self.assertIsNone(listing.distribution_proof(text,ann,'Child','01270.HK','00042'))
  self.assertIsNone(listing.distribution_proof(text.replace('was distributed','is expected to be distributed'),ann,'Child','01270.HK','00041'))
  self.assertIsNone(listing.distribution_proof(text,{**ann,'date':'2026-04-01'},'Child','01270.HK','00041'))
  logo='The Board of Directors of Example Holdings Limited (the “Company”) announces results. '+text.split(') ',1)[1]
  bound={**ann,'issuerName':'EXAMPLE','issuerCode':'00041'}
  self.assertIsNotNone(listing.distribution_proof(logo,bound,'Child','01270.HK','00041'))
  self.assertIsNone(listing.distribution_proof(logo,{**bound,'issuerCode':'00042'},'Child','01270.HK','00041'))
  self.assertIsNone(listing.distribution_proof(logo,{**bound,'issuerName':'OTHER'},'Child','01270.HK','00041'))

 def test_glossary_binds_listed_security_code_without_parent_code(self):
  from spinoff_events import listed_target_code
  text='本公司（股份代號：41）。信託及 LHI 之股份合訂單位於聯交所上市（股份代號：1270）。「信託」 指根據信託契約組成的朗廷酒店投資。'
  self.assertEqual(listed_target_code(text,'朗廷酒店投資'),'01270.HK')
  self.assertEqual(listed_target_code(text,'另一信託'),'')

 def test_later_distribution_round_is_not_completed_by_old_listing_or_distribution(self):
  old={'url':'https://www1.hkexnews.hk/listedco/old.pdf','date':'2025-11-01','title':'實物分派','targetName':'Child','targetTicker':'01270.HK','status':'completed','quote':'分派已完成','dates':{'distributionDate':{'date':'2025-10-30','kind':'actual'}}}
  new={**old,'url':'https://www1.hkexnews.hk/listedco/new.pdf','date':'2026-02-25','status':'record_set','quote':'分派記錄日為2026年3月17日','dates':{'recordDate':{'date':'2026-03-17','kind':'scheduled'}}}
  data={'companies':[{'stockCode':'00041','filingEvidence':[old,new]}]}
  normalize(data,'hk');self.assertEqual(data['events'][0]['status'],'record_set')
  self.assertEqual(len(data['events']),1)

 def setUp(self):
  self.target='測試能源股份有限公司';self.ann={'url':'https://www1.hkexnews.hk/listedco/test.pdf','date':'2026-08-27','title':'INTERIM RESULTS'}
  self.header=self.target+' (Stock Code: 4321) '
 def test_actual_listing_is_bound_to_issuer_not_parent_quote(self):
  text=self.header+'The shares of the Company have been listed on the Main Board of the Stock Exchange of Hong Kong Limited since 19 March 2026.'
  p=listing.listing_proof(text,self.ann,self.target,'04321.HK')
  self.assertEqual(p['status'],'completed');self.assertEqual(p['dates']['listingDate']['date'],'2026-03-19')
  self.assertIsNone(listing.listing_proof(text,self.ann,self.target,'01234.HK'))
  self.assertIsNone(listing.listing_proof(text,self.ann,'另一公司股份有限公司','04321.HK'))
  parent='母公司股份有限公司 (Stock Code: 4321) '+self.target+' is a subsidiary. The shares of the Company have been listed on the Stock Exchange since 19 March 2026.'
  self.assertIsNone(listing.listing_proof(parent,self.ann,self.target,'04321.HK'))
 def test_future_timetable_and_negation_do_not_complete_listing(self):
  for wording in ['The shares of the Company are expected to be listed on the Stock Exchange on March 19, 2026.', 'The shares of the Company have not been listed on the Stock Exchange since 19 March 2026.']:
   self.assertIsNone(listing.listing_proof(self.header+wording,self.ann,self.target,'04321.HK'))
  future={**self.ann,'date':'2026-03-18'}
  self.assertIsNone(listing.listing_proof(self.header+'The shares of the Company were listed on the Stock Exchange on March 19, 2026.',future,self.target,'04321.HK'))
 def test_financial_report_listing_date_and_chinese_actual_listing(self):
  for text in ['During the period from March 19, 2026 (the “Listing Date”) to June 30, the Company did not purchase the Company’s listed securities.', '本公司股份已於2026年3月19日在香港聯交所主板上市。']:
   p=listing.listing_proof(self.header+text,self.ann,self.target,'04321.HK')
   self.assertEqual(p['dates']['listingDate']['date'],'2026-03-19')
 def test_source_followup_completes_and_replaces_announcement_date_proxy(self):
  company={'ticker':'01234.HK','type':'intro_hk','announcements':[], 'filingEvidence':[{'targetName':self.target,'identityKind':'entity','targetTicker':'04321.HK','url':'https://www1.hkexnews.hk/listedco/old.pdf','status':'announced','quote':'建議分拆'}], 'spinoffPricePerf':[{'spinoff':'4321.HK','spinoffDate':'2026-02-12','spinoffPriceAtListing':4,'spinoffChangePct':20}]}
  text=self.header+'The shares of the Company have been listed on the Stock Exchange since 19 March 2026.'
  with patch.object(listing,'issuer_lookup',return_value=[{'stockId':1,'code':'04321','name':'測試能源'}]),patch.object(listing,'issuer_filings',return_value=[self.ann]),patch.object(listing,'listing_document',return_value={'text':text}):
   count,errors=listing.follow_company(company,None)
   self.assertEqual(count,1);self.assertFalse(errors)
   listing.follow_company(company,None)
  self.assertEqual(company['filingEvidence'][-1]['status'],'completed')
  pair=company['spinoffPricePerf'][0];self.assertEqual(pair['spinoffDate'],'2026-03-19');self.assertIsNone(pair['spinoffPriceAtListing'])
  data={'companies':[company]};normalize(data,'hk')
  event=next(e for e in data['events'] if e['targetName']==self.target)
  self.assertEqual(event['status'],'completed');self.assertEqual(event['targetTicker'],'04321.HK')

 def test_a_rule_upgrade_preserves_source_bound_completed_listing(self):
  text=self.header+'The shares of the Company have been listed on the Stock Exchange since 19 March 2026.'
  proof=listing.listing_proof(text,self.ann,self.target,'04321.HK');proof['ruleVersion']=RULE_VERSION-1
  data={'companies':[{'ticker':'01234.HK','type':'intro_hk','announcements':[],'filingEvidence':[proof]}]}
  normalize(data,'hk');self.assertEqual(data['events'][0]['status'],'completed')

if __name__=='__main__':unittest.main()
