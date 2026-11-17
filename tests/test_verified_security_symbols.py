import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime,timezone
from verified_security_symbols import identity_for,project,quote_matches
from security_identity import project as project_data
from trade_price_history import build
from batch_market_data import SERIES

H={'name':'FERRARI N V','cls':'COM','cusip':'N3167Y103','ticker':'?FERRARI N V','shares':10,'value':500,'shareType':'SH','putCall':''}
Q={'symbol':'RACE','currency':'USD','verifiedName':'Ferrari N.V.','shareActions':[],'c':400,'t':1794862802}
class VerifiedSymbolsTests(unittest.TestCase):
    def test_exact_class_identity_and_period_required(self):
        self.assertEqual(project(H,'2016 Q1')['ticker'],'RACE')
        for changes in [{'cusip':'N3167J106'},{'cusip':'UNKNOWN'},{'cls':'SPECIAL VOTING'},{'cls':''},{'putCall':'Put'},{'shareType':'PRN'},{'name':'Another Ferrari'}]:
            row={**H,**changes};self.assertIsNone(identity_for(row,'2016 Q1'));self.assertEqual(project(row,'2016 Q1'),row)
        self.assertIsNone(identity_for(H,'2015 Q4'))
        self.assertIsNone(identity_for(H,''))
        mapped=project(H,'2016 Q1');self.assertEqual(mapped['reportedIdentity']['ticker'],H['ticker']);self.assertTrue(quote_matches(mapped,Q))
        for extra in [{'symbol':'OTHER'},{'currency':'EUR'},{'verifiedName':'Other issuer'}]:self.assertFalse(quote_matches(mapped,{**Q,**extra}))

    def test_known_ferrari_history_projects_without_rewriting_source_or_counts(self):
        source=json.loads(Path('pabrai_data.json').read_text());before=copy.deepcopy(source)
        out=project_data(source);self.assertEqual(source,before);self.assertEqual(project_data(out),out)
        for quarter in ['2016 Q1','2018 Q2']:
            row=next(h for h in out['history']['holdings'][quarter] if h.get('cusip')=='N3167Y103')
            self.assertEqual(row['ticker'],'RACE');self.assertIn('reportedIdentity',row)
        for quarter,rows in source['history']['holdings'].items():
            self.assertEqual(sum(r['value'] for r in rows),sum(r['value'] for r in out['history']['holdings'][quarter]))

    def test_window_excludes_old_security_dates_before_effective_day(self):
        stamp=lambda d:datetime.fromisoformat(d).replace(tzinfo=timezone.utc).timestamp()
        series={'timestamps':[stamp('2015-12-31'),stamp('2016-01-02'),stamp('2016-01-04'),stamp('2016-02-01')],
                'values':{'close':[1000,1000,10,20],'low':[900,900,8,18],'high':[1100,1100,12,22]}}
        data={'current':{'quarter':'2016 Q1','holdings':[H]},'history':{'holdings':{}}}
        with patch.dict(SERIES,{'RACE':series},clear=True):got=build(data,{'RACE':Q},download_limit=0,refresh_quotes=False)
        entry=got['entries'][H['cusip']]
        self.assertEqual(entry['averageBuy'],10.1)
        self.assertEqual(entry['candles']['2016 Q1']['days'],2)
        self.assertEqual(entry['candles']['2016 Q1']['high'],22)

    def test_wrong_issuer_response_cannot_supply_estimates(self):
        stamp=datetime(2016,2,1,tzinfo=timezone.utc).timestamp()
        loader=lambda tk,start:({'timestamps':[stamp],'values':{'close':[10],'low':[8],'high':[12]}},{**Q,'verifiedName':'Wrong Company'})
        data={'current':{'quarter':'2016 Q1','holdings':[H]},'history':{'holdings':{}}}
        with patch.dict(SERIES,{},clear=True):got=build(data,{},download_limit=1,loader=loader,refresh_quotes=False)
        self.assertIsNone(got['entries'][H['cusip']]['averageBuy'])

    def test_generated_browser_registry_matches_canonical_evidence(self):
        from verified_security_symbols import browser_records_source
        self.assertEqual(Path('verified_security_symbols.js').read_text(),browser_records_source())

    def test_identity_boundary_cannot_inherit_predecessor_shares_or_cost(self):
        stamp=datetime(2016,2,1,tzinfo=timezone.utc).timestamp()
        series={'timestamps':[stamp],'values':{'close':[10],'low':[8],'high':[12]}}
        data={'current':{'quarter':'2016 Q1','holdings':[H]},'history':{'holdings':{'2015 Q4':[{**H,'shares':100}]}}}
        with patch.dict(SERIES,{'RACE':series},clear=True):got=build(data,{'RACE':Q},download_limit=0,refresh_quotes=False)
        e=got['entries'][H['cusip']]
        self.assertEqual(e['quarters'][0]['quarter'],'2016 Q1')
        self.assertEqual(e['quarters'][0]['action'],'observed')
        self.assertIsNone(e['averageSell'])

    def test_projection_never_overwrites_known_symbol_or_existing_source_bridge(self):
        known={**H,'ticker':'KNOWN_DIFFERENT'}
        self.assertEqual(project(known,'2016 Q1'),known)
        bridge={'ticker':'?Original','name':'Original raw name'}
        mapped=project({**H,'reportedIdentity':bridge,'identityEvidence':{'method':'existing_source_bridge'}},'2016 Q1')
        self.assertEqual(mapped['reportedIdentity'],bridge)
        self.assertEqual(mapped['identityEvidence'],{'method':'existing_source_bridge'})

    def test_browser_compaction_keeps_price_identity_proof(self):
        from build_browser_assets import compact_row
        mapped=project(H,'2016 Q1')
        self.assertEqual(compact_row(mapped)['priceIdentityEvidence'],mapped['priceIdentityEvidence'])
