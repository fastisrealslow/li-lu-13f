import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from magic_formula import BALANCE_FIELDS, calculate, financial_components, rank, validate_dataset
from personal_reports import InlineReport, PDFReport, extract_recipe, ads_conversion
from update_personal_portfolio import update, retarget, quote_data

ROOT=Path(__file__).resolve().parents[1]


def fixture():
    source={'annual':{'url':'https://www.sec.gov/Archives/report.htm','kind':'annual_report','sha256':'a'*64}}
    annuals=[]
    for y,ebit in [(2025,100),(2024,200),(2023,300)]:
        values={k:0 for k in BALANCE_FIELDS}
        values.update(currentAssets=1000,cash=100,restrictedCash=20,currentFinancialAssets=30,
            currentLiabilities=400,currentDebt=40,noncurrentDebt=80,currentLeases=10,noncurrentLeases=20,
            ppe=500,rou=100,minorityInterest=50,preferredEquity=10,ordinaryShares=100,operatingProfit=ebit)
        facts={k:{'value':v,'sourceId':'annual','label':k,'evidence':'Original consolidated report row'} for k,v in values.items()}
        annuals.append({'end':f'{y}-12-31','months':12,'facts':facts,'ebitAdjustments':[],
            'evCashLikeFinancialAssets':{'value':30,'sourceId':'annual','label':'deposit','evidence':'bank deposit'}})
    c={'id':'sample','currency':'CNY','annuals':annuals,'sources':source,'listings':[{'ticker':'SAMPLE','currency':'USD','ordinarySharesPerQuoteUnit':4}]}
    q={'price':10,'currency':'USD','fxToReportCurrency':7,'ordinarySharesPerQuoteUnit':4,'asOf':'2026-10-09','sourceUrl':'https://finance.yahoo.com/quote/SAMPLE/'}
    return c,q


class FormulaTests(unittest.TestCase):
    def test_cash_debt_leases_and_ads_have_exactly_one_treatment(self):
        c,q=fixture();r=calculate(c,q)
        self.assertEqual(r['equityValue'],1750)
        self.assertEqual(r['enterpriseValue'],1830)
        self.assertEqual(r['annualComponents'][0]['workingCapital'],500)
        self.assertEqual(r['investedCapital'],1100)
        self.assertAlmostEqual(r['earningsYield'],100/1830)
        self.assertAlmostEqual(r['returnOnCapital'],100/1100)

    def test_three_years_are_ratio_of_averages_not_mean_of_ratios(self):
        c,q=fixture();c['annuals'][1]['facts']['ppe']['value']=100
        r=calculate(c,q,3)
        self.assertEqual(r['ebit'],200)
        self.assertAlmostEqual(r['investedCapital'],(1100+700+1100)/3)
        self.assertAlmostEqual(r['returnOnCapital'],600/2900)
        self.assertEqual(r['enterpriseValue'],calculate(c,q,1)['enterpriseValue'])

    def test_restricted_cash_cannot_reduce_enterprise_value(self):
        c,q=fixture();before=calculate(c,q);c['annuals'][0]['facts']['restrictedCash']['value']=300
        after=calculate(c,q);self.assertEqual(after['enterpriseValue'],before['enterpriseValue'])
        self.assertLess(after['investedCapital'],before['investedCapital'])

    def test_negative_capital_loss_and_nonpositive_ev_do_not_rank(self):
        c,q=fixture();c['annuals'][0]['facts']['currentLiabilities']['value']=3000
        r=calculate(c,q);self.assertEqual(r['status'],'not_ranked');self.assertIsNone(r['returnOnCapital'])
        c,q=fixture();c['annuals'][0]['facts']['operatingProfit']['value']=-1
        self.assertEqual(calculate(c,q)['status'],'not_ranked')
        c,q=fixture();q['price']=.01;c['annuals'][0]['facts']['noncurrentDebt']['value']=0
        c['annuals'][0]['facts']['minorityInterest']['value']=0
        c['annuals'][0]['facts']['preferredEquity']['value']=0
        self.assertIsNone(calculate(c,q)['earningsYield'])

    def test_half_year_and_gaps_are_rejected(self):
        c,q=fixture();c['annuals'][1]['months']=6;self.assertEqual(calculate(c,q,3)['status'],'incomplete')
        c,q=fixture();c['annuals'][1]['end']='2022-12-31';self.assertEqual(calculate(c,q,3)['status'],'incomplete')

    def test_ties_are_competition_ranks_and_losses_do_not_distort_ranks(self):
        rows=[{'id':str(i),'status':'ranked','earningsYield':ey,'returnOnCapital':roc} for i,(ey,roc) in enumerate([(3,1),(3,2),(1,3)])]
        rows.append({'id':'loss','status':'not_ranked','earningsYield':100,'returnOnCapital':100})
        results=rank(rows);self.assertEqual([r['id'] for r in results],['1','0','2','loss'])
        self.assertEqual(rows[0]['earningsRank'],1);self.assertEqual(rows[2]['earningsRank'],3)

    def test_published_dataset_has_eight_holdings_and_reproducible_results(self):
        data=json.loads((ROOT/'personal_portfolio.json').read_text());validate_dataset(data)
        self.assertEqual({c['id'] for c in data['companies']},{'pdd','trt','lining','viva','langham','tme','wuliangye','miniso'})
        for c in data['companies']:
            latest=max(int(p['end'][:4]) for p in c['annuals'])
            self.assertEqual([p['end'] for p in c['annuals']],[f'{y}-12-31' for y in range(latest,latest-3,-1)])
            self.assertTrue(c['results'],c['id'])
        miniso=next(c for c in data['companies'] if c['id']=='miniso')
        calendar2023=next((p for p in miniso['annuals'] if p['end']=='2023-12-31'),None)
        if calendar2023:
            self.assertFalse(calendar2023['audited'])
            self.assertEqual(calendar2023['facts']['operatingProfit']['value'],2819648000)

    def test_tampered_numbers_sources_or_ads_ratios_fail_validation(self):
        original=json.loads((ROOT/'personal_portfolio.json').read_text())
        for change in ['amount','source','ratio','eligibility']:
            data=copy.deepcopy(original);c=data['companies'][0];r=c['results']['PDD']['1']
            if change=='amount':r['enterpriseValue']+=10000
            if change=='source':next(iter(c['sources'].values()))['url']='https://example.com/news'
            if change=='ratio':r['quote']['ordinarySharesPerQuoteUnit']=1
            if change=='eligibility':r['status']='ranked' if r['status']!='ranked' else 'not_ranked'
            with self.assertRaises(ValueError,msg=change):validate_dataset(data)

    def test_explanatory_other_gains_have_report_evidence_and_never_add_to_ebit_twice(self):
        data=json.loads((ROOT/'personal_portfolio.json').read_text())
        c=next(c for c in data['companies'] if c['id']=='tme')
        annual=c['annuals'][0];q=c['results'][c['listings'][0]['ticker']]['1']['quote']
        before=calculate(c,q)
        annual['facts']['otherGains']['value']*=2
        self.assertEqual(calculate(c,q)['ebit'],before['ebit'])
        annual['facts']['otherGains']['sourceId']='missing-original-report'
        with self.assertRaises(ValueError):validate_dataset(data)


class ExtractionTests(unittest.TestCase):
    def inline(self, extra=''):
        return InlineReport(('''<html><xbrli:unit id="CNY"><xbrli:measure>iso4217:CNY</xbrli:measure></xbrli:unit>
        <xbrli:unit id="USD"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
        <xbrli:context id="total"><xbrli:period><xbrli:instant>2025-12-31</xbrli:instant></xbrli:period></xbrli:context>
        <xbrli:context id="segment"><xbrli:period><xbrli:instant>2025-12-31</xbrli:instant></xbrli:period><xbrldi:explicitMember>segment</xbrldi:explicitMember></xbrli:context>
        <ix:nonFraction name="test:Cash" contextRef="total" unitRef="CNY" scale="3">1,200</ix:nonFraction>
        <ix:nonFraction name="test:Cash" contextRef="total" unitRef="USD" scale="3">170</ix:nonFraction>
        <ix:nonFraction name="test:Cash" contextRef="segment" unitRef="CNY" scale="3">600</ix:nonFraction>
        '''+extra+'</html>').encode())

    def test_unit_scale_and_consolidated_context_are_required(self):
        r=self.inline();f=r.extract({'concept':'test:Cash'},2025);self.assertEqual(f['value'],1200000)
        with self.assertRaises(ValueError):r.extract({'concept':'test:Missing'},2025)

    def test_conflicting_tagged_totals_fail_closed(self):
        r=self.inline('<ix:nonFraction name="test:Cash" contextRef="total" unitRef="CNY" scale="3">1,300</ix:nonFraction>')
        with self.assertRaises(ValueError):r.extract({'concept':'test:Cash'},2025)

    def test_newly_disclosed_debt_replaces_an_explicit_absence_policy(self):
        r=self.inline();f=extract_recipe(r,{'zeroPolicy':'Previously no debt','proof':'html','captureConcepts':['test:Cash']},2025)
        self.assertEqual(f['value'],1200000)

    def test_wrapped_pdf_columns_use_coordinates_not_reading_order(self):
        try:import pymupdf
        except ImportError:self.skipTest('PDF reader only needed by extraction workflow')
        doc=pymupdf.open();page=doc.new_page(width=600,height=400)
        page.insert_text((25,30),'CONSOLIDATED BALANCE SHEET')
        page.insert_text((25,100),'Current assets')
        page.insert_text((490,100),'2,000')
        page.insert_text((330,110),'1,000')
        report=PDFReport(doc.tobytes())
        words=[w for row in report.pages[0] for w in row['words'] if w[4]=='1,000'];x=words[0][2]/600
        f=report.extract({'signature':['CONSOLIDATED BALANCE SHEET'],'row':'^Current assets','below':14,'xEnd':x,'multiplier':1},2025)
        self.assertEqual(f['value'],1000)

    def test_failed_discovery_keeps_verified_financials_and_existing_quotes(self):
        data=json.loads((ROOT/'personal_portfolio.json').read_text());config=json.loads((ROOT/'personal_report_profiles.json').read_text());before=copy.deepcopy(data)
        with tempfile.TemporaryDirectory() as tmp,patch('update_personal_portfolio.discover',side_effect=ValueError('ambiguous report')):
            after,_=update(data,config,Path(tmp),quotes_enabled=False)
        for old,new in zip(before['companies'],after['companies']):
            self.assertEqual(old['annuals'],new['annuals'])
            for ticker,group in old['results'].items():
                for years,result in group.items():
                    self.assertEqual(result['quote'],new['results'][ticker][years]['quote'])
                    self.assertEqual(calculate(old,result['quote'],int(years)),new['results'][ticker][years])
            self.assertEqual(new['financialStatus']['status'],'retained')

    def test_future_report_retargets_year_text_without_templating_numbers(self):
        p={'year':2025,'sourceId':'old','selectors':{'ebit':{'row':'Year ended 2025','signature':['二零二五年 二零二四年'],'xEnd':.75}},'labels':{},'cashLike':{'concept':'ifrs:Cash'}}
        new=retarget(p,2026,'new');self.assertEqual(new['selectors']['ebit']['row'],'Year ended 2026');self.assertEqual(new['selectors']['ebit']['xEnd'],.75)
        self.assertEqual(new['selectors']['ebit']['signature'],['二零二六年 二零二五年'])

    def test_new_current_financial_categories_are_combined_from_the_statement(self):
        try:import pymupdf
        except ImportError:self.skipTest('PDF reader only needed by extraction workflow')
        doc=pymupdf.open();page=doc.new_page(width=600,height=400)
        page.insert_text((25,30),'CONSOLIDATED BALANCE SHEET')
        page.insert_text((25,70),'Current assets')
        page.insert_text((25,100),'Time deposits');page.insert_text((400,100),'1,000')
        page.insert_text((25,130),'Financial assets');page.insert_text((400,130),'2,000')
        page.insert_text((25,170),'Total current assets');page.insert_text((400,170),'9,000')
        report=PDFReport(doc.tobytes());w=next(w for row in report.pages[0] for w in row['words'] if w[4]=='1,000')
        f=extract_recipe(report,{'signature':['CONSOLIDATED BALANCE SHEET'],'sumRows':'Time deposits|Financial assets','xEnd':w[2]/600,'multiplier':1},2025)
        self.assertEqual(f['value'],3000);self.assertEqual(len(f['terms']),2)

    def test_ads_ratio_is_read_from_the_original_filing(self):
        r=InlineReport(b'<html>American depositary shares, each ADS represents two Class A ordinary shares.</html>')
        self.assertEqual(ads_conversion(r)['value'],2)

    def future_update(self,fail_prior=False):
        from types import SimpleNamespace
        c,q=fixture();c['listings'][0]['ordinarySharesPerQuoteUnit']=1
        data={'version':1,'companies':[c]}
        specs=[{'year':y,'sourceId':'annual','selectors':{},'labels':{},'cashLike':{}} for y in [2025,2024,2023]]
        config={'companies':[{'id':'sample','annuals':specs,'discovery':{'kind':'sec','code':1}}],'sources':{'annual':c['sources']['annual']['url']}}
        before=copy.deepcopy(data)
        def read(spec,*args):
            if fail_prior and spec['year']==2025:raise ValueError('ambiguous comparative')
            p=copy.deepcopy(c['annuals'][0]);p['end']=str(spec['year'])+'-12-31'
            p['facts']['operatingProfit']['value']=400 if spec['year']==2026 else 190
            for f in p['facts'].values():f['sourceId']=spec['sourceId']
            p['evCashLikeFinancialAssets']['sourceId']=spec['sourceId'];return p
        records=[{'year':2026,'url':'https://www.sec.gov/Archives/new.htm','date':'2027-04-01','amendment':False}]
        with tempfile.TemporaryDirectory() as tmp,patch('update_personal_portfolio.discover',return_value=records),patch('update_personal_portfolio.original_report',return_value=SimpleNamespace(digest='b'*64)),patch('update_personal_portfolio.read_period',side_effect=read):
            after,cfg=update(data,config,Path(tmp),quotes_enabled=False)
        return before,after,cfg

    def test_new_annual_report_refreshes_revised_comparatives(self):
        _,after,cfg=self.future_update();c=after['companies'][0]
        self.assertEqual([p['end'] for p in c['annuals']],['2026-12-31','2025-12-31','2024-12-31'])
        self.assertEqual(c['annuals'][1]['facts']['operatingProfit']['value'],190)
        self.assertEqual(c['financialStatus']['status'],'updated')

    def test_bad_new_comparatives_roll_back_the_entire_issuer(self):
        before,after,cfg=self.future_update(True)
        self.assertEqual(before['companies'][0]['annuals'],after['companies'][0]['annuals'])
        self.assertEqual(after['companies'][0]['financialStatus']['status'],'retained')
        self.assertEqual(max(p['year'] for p in cfg['companies'][0]['annuals']),2025)

    def test_quote_ignores_incomplete_current_session_and_carries_trading_date(self):
        payload={'chart':{'result':[{'meta':{'symbol':'SAMPLE','currency':'USD','exchangeTimezoneName':'America/New_York','priceHint':2,'currentTradingPeriod':{'regular':{'start':1000,'end':2000}}},'timestamp':[0,1500],'indicators':{'quote':[{'close':[10.1234,99]}]}}],'error':None}}
        with patch('update_personal_portfolio.request',return_value=json.dumps(payload).encode()),patch('update_personal_portfolio.time.time',return_value=2100):
            q=quote_data('SAMPLE','USD')
        self.assertEqual(q['price'],10.12);self.assertEqual(q['sessionTimestamp'],0);self.assertEqual(q['quoteType'],'daily_close')


if __name__=='__main__':unittest.main()


class FinancialReplayStabilityTests(unittest.TestCase):
    def test_cosmetic_changes_need_all_numbers_to_replay_before_accepting_new_digest(self):
        from types import SimpleNamespace
        from update_personal_portfolio import verify_existing_reports
        c,_=fixture();specs={'annuals':[{'year':int(p['end'][:4])} for p in c['annuals']]}
        by_year={int(p['end'][:4]):copy.deepcopy(p) for p in c['annuals']}
        with patch('update_personal_portfolio.read_period',side_effect=lambda p,*_:copy.deepcopy(by_year[p['year']])):
            self.assertEqual(verify_existing_reports(c,specs,{'annual':SimpleNamespace(digest='b'*64)},'2026-10-29T00:00:00Z'),1)
        self.assertEqual(c['sources']['annual']['sha256'],'b'*64)
        self.assertEqual(c['sources']['annual']['previousSha256'],'a'*64)
        self.assertEqual(c['sources']['annual']['verificationMethod'],'exact_financial_replay')

    def test_a_changed_financial_input_cannot_be_treated_as_a_cosmetic_change(self):
        from types import SimpleNamespace
        from update_personal_portfolio import verify_existing_reports
        c,_=fixture();before=copy.deepcopy(c)
        def changed(*_):
            p=copy.deepcopy(c['annuals'][0]);p['facts']['cash']['value']+=1;return p
        with patch('update_personal_portfolio.read_period',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'cash'):
                verify_existing_reports(c,{'annuals':[{'year':2025}]},{'annual':SimpleNamespace(digest='b'*64)},'2026-10-29T00:00:00Z')
        self.assertEqual(c,before)


class SourceRequestStabilityTests(unittest.TestCase):
    def test_total_download_deadline_is_bounded_and_a_failed_host_does_not_block_other_hosts(self):
        from io import BytesIO
        import itertools
        import update_personal_portfolio as u
        clock=itertools.chain([0,0,1],itertools.repeat(61))
        with patch.object(u,'FAILED_HOSTS',set()),patch.object(u.time,'monotonic',side_effect=lambda:next(clock)),patch.object(u.time,'sleep'),patch.object(u,'urlopen',return_value=BytesIO(b'x')) as fetch:
            with self.assertRaises(TimeoutError):u.request('https://slow.example/report')
            self.assertEqual(fetch.call_count,1)
            with self.assertRaises(OSError):u.request('https://slow.example/another')
            self.assertEqual(fetch.call_count,1)
            with patch.object(u.time,'monotonic',return_value=0),patch.object(u,'urlopen',return_value=BytesIO(b'ok')):
                self.assertEqual(u.request('https://working.example/report'),b'ok')

    def test_an_alternate_quote_endpoint_still_verifies_the_symbol_and_currency(self):
        import update_personal_portfolio as u
        payload={'chart':{'result':[{'meta':{'symbol':'SAMPLE','currency':'USD','exchangeTimezoneName':'UTC','priceHint':2},'timestamp':[1000],'indicators':{'quote':[{'close':[10] }]}}],'error':None}}
        with patch.object(u,'request',side_effect=[TimeoutError('primary unavailable'),json.dumps(payload).encode()]) as fetch:
            result=u.quote_data('SAMPLE','USD')
        self.assertEqual(result['price'],10)
        self.assertIn('query2.finance.yahoo.com',fetch.call_args.args[0])
