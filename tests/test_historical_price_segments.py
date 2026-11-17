import copy
import unittest
from unittest.mock import patch
import historical_price_segments as seg
from trade_price_history import build


def source(q, cik='1173334'):
    return {'cik':cik,'reportDate':q[:4]+'-'+{'1':'03-31','2':'06-30','3':'09-30','4':'12-31'}[q[-1]],
            'url':f'https://www.sec.gov/Archives/edgar/data/{cik}/0001193125-12-060916.txt',
            'format':'xml13f',
            'sourceReconciliation':{'status':'reconciled','difference':0,'reportedEntries':1,'parsedEntries':1}}


def fixture():
    h={'ticker':'BAC','cusip':'060505104','name':'Bank of America','cls':'COM','shareType':'SH','shares':10,'value':100}
    history={'2011 Q2':[h], '2011 Q3':[{**h,'shares':20}], '2011 Q4':[{**h,'shares':15}], '2012 Q1':[{**h,'shares':30}]}
    d={'meta':{'costHistoryFrom':'2012 Q1'},'current':{'quarter':'2012 Q1','holdings':history['2012 Q1']},
       'history':{'holdings':history,'filing_sources':{q:source(q, '1549575' if q=='2012 Q1' else '1173334') for q in history}}}
    q={'symbol':'BAC','currency':'USD','verifiedName':'Bank of America Corporation','shareActions':[],'shareActionsSince':'2004-01-01'}
    return d,h,q

class Segments(unittest.TestCase):
    def test_explicit_original_identity_evidence_required_not_name_or_symbol_only(self):
        d,h,q=fixture()
        self.assertIsNotNone(seg.identity_for(h,q,'2011 Q1'))
        for change in ({'ticker':'?Bank of America'}, {'cusip':'060505999'}, {'putCall':'Put'}, {'cls':'PFD'}, {'cls':'SPON ADR'}, {'cls':'CL B'}, {'name':'Another Company'}, {'reportedIdentity':{'cusip':''}}):
            self.assertIsNone(seg.identity_for({**h,**change},q,'2011 Q1'))
        self.assertIsNone(seg.identity_for(h,q,'2009 Q4'))
        self.assertIsNone(seg.identity_for(h,{**q,'quoteTransition':{'ticker':'NEW'}},'2011 Q1'))

    def test_old_reporter_is_separate_and_cannot_change_current_averages(self):
        d,h,q=fixture();before=copy.deepcopy(d)
        with patch('batch_market_data.window',return_value=(True,{'closes':[10], 'lows':[8], 'highs':[12]})):
            out=build(d,{'BAC':q},download_limit=0,refresh_quotes=False)['entries']['060505104']
        self.assertEqual(d,before)
        self.assertEqual([r['quarter'] for r in out['quarters']],['2012 Q1'])
        self.assertEqual(out['quarters'][0]['action'],'observed')
        self.assertIsNone(out['averageSell'])
        old=out['historicalSegments'][0]
        self.assertEqual(old['reporterCIK'],'1173334')
        self.assertEqual(old['firstQuarter'],'2011 Q2')
        self.assertEqual(old['lastQuarter'],'2011 Q4')
        self.assertEqual(old['averageBuy'],8.6)
        self.assertEqual(old['averageSell'],11.4)
        self.assertTrue(old['notCombinedWithCurrent'])

    def test_every_cik_gap_and_invalid_source_resets_segment(self):
        d,h,q=fixture()
        d['history']['filing_sources']['2011 Q3']=source('2011 Q3','123')
        plans,gaps=seg.plan(d,d['history']['holdings'],h,'2012 Q1',set(),q)
        self.assertEqual(len(plans),3)
        for p in seg.estimates(plans,{z:{'buy':10,'sell':20} for z in d['history']['holdings']},q):
            self.assertEqual(p['quarters'][0]['action'],'observed');self.assertIsNone(p['averageSell'])
        d['history']['filing_sources']['2011 Q3']['sourceReconciliation']['status']='cover_total_mismatch'
        plans,gaps=seg.plan(d,d['history']['holdings'],h,'2012 Q1',set(),q)
        self.assertEqual(len(plans),2);self.assertEqual(gaps['2011 Q3'],'unreconciled_original_filing')

    def test_parser_v6_and_unverified_adjustments_do_not_backfill(self):
        d,h,q=fixture();d['history']['filing_sources']['2011 Q2']['format']='legacy_13f'
        plans,gaps=seg.plan(d,d['history']['holdings'],h,'2012 Q1',{'2011 Q3'},q)
        self.assertEqual(gaps['2011 Q2'],'legacy_identity_requires_review')
        self.assertEqual(gaps['2011 Q3'],'corporate_action_or_unreconciled_values')
        self.assertEqual(len(plans),1)
        self.assertEqual(seg.estimates(plans,{}, {**q,'shareActionsSince':'2024-01-01'}),[])

    def test_original_scope_requires_bound_cik_period_and_reconciliation(self):
        for k,v in [('cik','different'),('url','https://evil.test/filing'),('reportDate','2010-03-31'),('format','legacy_13f')]:
            f=source('2011 Q1');f[k]=v
            self.assertIsNotNone(seg.original_scope(f,'2011 Q1')[1])

    def test_needed_old_periods_join_bounded_download_queue(self):
        d,h,q=fixture();calls=[]
        from fetch_prices_all import quarter_ts
        def loader(ticker,start):
            calls.append((ticker,start));stamps=[quarter_ts(z)[0]+86400 for z in d['history']['holdings']]
            return {'timestamps':stamps,'values':{'close':[10]*4,'low':[8]*4,'high':[12]*4}},q
        with patch.dict('batch_market_data.SERIES',{},clear=True):
            result=build(d,{'BAC':q},download_limit=1,loader=loader,refresh_quotes=False)
        self.assertEqual(len(calls),1)
        self.assertTrue(result['entries']['060505104']['historicalSegments'][0]['averageBuy'])

class SegmentSnapshots(unittest.TestCase):
    def test_segments_ship_only_in_lazy_history_not_current_summary(self):
        import build_browser_assets as browser
        d,h,q=fixture()
        entry={'ticker':'BAC','quarters':[],'historicalSegments':[{'reporterCIK':'1173334','quarters':[]}],'historicalSegmentGaps':{'2010 Q1':'unverified'}}
        p={'tradePrices':{'entries':{'060505104':entry}},'quotes':{'BAC':q}}
        summary=browser.current_prices(p)
        full=browser.history_data(d,p)
        self.assertNotIn('historicalSegments',summary['tradePrices']['entries']['060505104'])
        self.assertEqual(full['tradePrices']['entries']['060505104']['historicalSegments'],entry['historicalSegments'])

class OriginalRowReview(unittest.TestCase):
    def test_real_pabrai_row_is_individually_bound_without_upgrading_parser(self):
        import json
        from pathlib import Path
        d=json.loads(Path('tests/fixtures/pabrai-bac-legacy-scope.json').read_text())
        h=next(h for h in d['history']['holdings']['2011 Q4'] if h.get('cusip')=='060505104')
        q={'symbol':'BAC','currency':'USD','verifiedName':'Bank of America Corporation'}
        plans,gaps=seg.plan(d,d['history']['holdings'],h,'2012 Q1',set(),q)
        self.assertEqual([(p['firstQuarter'],p['lastQuarter']) for p in plans],[('2011 Q4','2011 Q4')])
        self.assertEqual(d['history']['filing_sources']['2011 Q4']['parserVersion'],6)
        changed=copy.deepcopy(d);changed['history']['holdings']['2011 Q4'][d['history']['holdings']['2011 Q4'].index(h)]['shares']+=1
        self.assertFalse(seg.plan(changed,changed['history']['holdings'],h,'2012 Q1',set(),q)[0])
        changed=copy.deepcopy(d);changed['history']['filing_sources']['2011 Q4']['sourceReconciliation']['status']='cover_total_mismatch'
        self.assertFalse(seg.plan(changed,changed['history']['holdings'],h,'2012 Q1',set(),q)[0])

class ScopeProofRegressions(unittest.TestCase):
    def test_missing_zero_and_noninteger_counts_are_not_reconciled_evidence(self):
        for invalid in (None,0,-1,'1',1.0,True):
            s=source('2011 Q1')
            s['sourceReconciliation'].update(reportedEntries=invalid,parsedEntries=invalid)
            self.assertEqual(seg.original_scope(s,'2011 Q1')[1],'unreconciled_original_filing')

    def test_same_quarter_midperiod_date_is_not_a_quarter_end_filing(self):
        s=source('2011 Q1');s['reportDate']='2011-02-28'
        self.assertEqual(seg.original_scope(s,'2011 Q1')[1],'filing_period_mismatch')

    def test_reviewed_row_url_must_resolve_to_the_reviewed_accession(self):
        import json
        from pathlib import Path
        d=json.loads(Path('tests/fixtures/pabrai-bac-legacy-scope.json').read_text())
        h=d['history']['holdings']['2011 Q4'][0];s=d['history']['filing_sources']['2011 Q4']
        self.assertTrue(seg.independently_reviewed_row(d,'2011 Q4',h,s))
        for url in ('https://www.sec.gov/Archives/edgar/data/1173334/000119312511317251/other.txt',
                    'https://www.sec.gov/Archives/edgar/data/1173334/other.txt',
                    'https://www.sec.gov/Archives/edgar/data/1173334/000119312512060916/000119312511317251.txt'):
            self.assertFalse(seg.independently_reviewed_row(d,'2011 Q4',h,{**s,'url':url}))
