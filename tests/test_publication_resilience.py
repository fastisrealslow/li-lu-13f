import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import quote_coverage as q

class PublicationResilienceTests(unittest.TestCase):
    def test_retirement_discovered_after_price_fetch_is_applied_in_the_same_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.setup_root(root,{'error':True})
            fund=json.loads((root/'fund.json').read_text());fund['current']['periodEnd']='2020-03-31'
            (root/'fund.json').write_text(json.dumps(fund))
            event={'ticker':'OLD','issuer':'EXAMPLE CORP','status':'ceased_trading',
                   'effectiveDate':'2020-04-01','reason':'已注销','reasonEn':'Retired',
                   'sourceURL':'https://www.sec.gov/Archives/example.xml'}
            with patch.object(q,'resolve_active'),patch.object(q,'market_quote',return_value={'error':True}),patch('security_lifecycle.discover_retirements',return_value={'123456789':event}):
                self.assertEqual(q.refresh(root)['missing'],[])
            self.assertEqual(json.loads((root/'prices.json').read_text())['quotes']['OLD'],{'status':'ceased_trading','event':event})

    def test_new_retirement_evidence_replaces_cached_quotes_for_every_holder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.setup_root(root,{'c':20,'t':time.time()})
            config=json.loads((root/'investors.json').read_text())
            config['investors'].append({'id':'second','dataFile':'fund.json','pricesFile':'second.json'})
            (root/'investors.json').write_text(json.dumps(config))
            (root/'second.json').write_text(json.dumps({'quotes':{'OLD':{'error':True}}}))
            event={'ticker':'OLD','issuer':'EXAMPLE CORP','status':'ceased_trading',
                   'effectiveDate':'2020-01-01','reason':'已注销','reasonEn':'Retired',
                   'sourceURL':'https://www.sec.gov/Archives/example.xml'}
            (root/'security_lifecycle.json').write_text(json.dumps({'events':{'123456789':event}}))
            self.assertEqual(len(q.coverage(root)['missing']),2)
            self.assertEqual(len(q.publication_coverage(root)['unhandled']),2)
            q.prepare_publication(root)
            for file in ('prices.json','second.json'):
                price=json.loads((root/file).read_text())['quotes']['OLD']
                self.assertEqual(price,{'status':'ceased_trading','event':event})
            self.assertEqual(q.coverage(root)['missing'],[])
            before=(root/'prices.json').read_bytes();q.prepare_publication(root)
            self.assertEqual((root/'prices.json').read_bytes(),before)

    def test_retirement_does_not_apply_to_another_class_or_future_event(self):
        for ticker,date in [('OTHER','2020-01-01'),('OLD','2999-01-01')]:
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);self.setup_root(root,{'c':20,'t':time.time()})
                event={'ticker':ticker,'issuer':'EXAMPLE CORP','status':'ceased_trading',
                       'effectiveDate':date,'reason':'已注销','reasonEn':'Retired',
                       'sourceURL':'https://www.sec.gov/Archives/example.xml'}
                (root/'security_lifecycle.json').write_text(json.dumps({'events':{'123456789':event}}))
                q.prepare_publication(root)
                self.assertEqual(json.loads((root/'prices.json').read_text())['quotes']['OLD']['c'],20)

    def setup_root(self,root,price):
        (root/'investors.json').write_text(json.dumps({'investors':[{'id':'test','dataFile':'fund.json','pricesFile':'prices.json'}]}))
        (root/'fund.json').write_text(json.dumps({'current':{'holdings':[{'ticker':'OLD','cusip':'123456789','name':'EXAMPLE CORP','shares':5,'value':100}]}}))
        (root/'prices.json').write_text(json.dumps({'quotes':{'OLD':price}}))

    def test_unavailable_quote_does_not_block_other_data_and_never_changes_trade_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);price={'c':20,'t':time.time()-10*86400,'sourceURL':'https://finance.yahoo.com/quote/OLD/'}
            self.setup_root(root,price)
            self.assertEqual(len(q.publication_coverage(root)['unhandled']),1)
            q.prepare_publication(root)
            saved=json.loads((root/'prices.json').read_text())['quotes']['OLD']
            self.assertEqual(saved['c'],price['c']);self.assertEqual(saved['t'],price['t'])
            self.assertTrue(saved['stale']);self.assertFalse(q.fresh_quote(saved))
            self.assertEqual(q.publication_coverage(root)['unhandled'],[])
            self.assertEqual(len(q.coverage(root)['missing']),1)
            # A later successful provider response clears the fallback.
            fresh={'c':21,'t':time.time()}
            from batch_market_data import merge_actions
            self.assertNotIn('availability',merge_actions(saved,fresh))
            self.assertTrue(q.fresh_quote(merge_actions(saved,fresh)))

    def test_corrupt_numbers_and_foreign_fallback_identity_still_block_publication(self):
        for price in [{'c':-1,'t':time.time()},{'c':20,'t':time.time()+86400}]:
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);self.setup_root(root,price)
                with self.assertRaises(ValueError):q.prepare_publication(root)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.setup_root(root,{'error':True});q.prepare_publication(root)
            p=json.loads((root/'prices.json').read_text());p['quotes']['OLD']['availability']['cusip']='999999999';(root/'prices.json').write_text(json.dumps(p))
            self.assertEqual(len(q.publication_coverage(root)['unhandled']),1)

    def test_spin_off_cost_is_not_carried_to_the_reduced_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.setup_root(root,{'c':20,'t':time.time()})
            (root/'security_symbol_changes.json').write_text(json.dumps({'entries':{'123456789':{'kind':'spin_off_rename','ticker':'NEW','preserveCost':False}}}))
            p=json.loads((root/'prices.json').read_text());p['costBasis']={'OLD':{'recent':{'buy':40}}};(root/'prices.json').write_text(json.dumps(p))
            q.prepare_publication(root);p=json.loads((root/'prices.json').read_text())
            self.assertNotIn('OLD',p['costBasis']);self.assertFalse(p['corporateActions']['123456789']['preserveCost'])

if __name__=='__main__':unittest.main()
