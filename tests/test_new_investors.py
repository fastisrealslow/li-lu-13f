import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import fetch_13f_all as sec
import fetch_public_projects as projects
import speech_archive as archive
import update_investors
from security_lifecycle import event_for

ROOT=Path(__file__).resolve().parents[1]

class NewInvestors(unittest.TestCase):
    def test_registry_routes_non_13f_investors_without_manufacturing_quarterly_positions(self):
        people={i['id']:i for i in json.loads((ROOT/'investors.json').read_text())['investors']}
        for ident in ['marks','mclemore']:
            self.assertEqual(update_investors.commands(people[ident])[0][1][0],'fetch_13f_all.py')
        self.assertEqual(update_investors.commands(people['wolfe']),[('disclosures',['fetch_public_projects.py','--investor','wolfe'])])
        self.assertFalse(people['wolfe']['inValueScreen'])
        for ident in ['marks','wolfe','mclemore']:
            p=people[ident]['profile']
            self.assertGreaterEqual(len(p['about']),5)
            self.assertGreaterEqual(len(p['timeline']),8)
            self.assertTrue(all(x.get('source','').startswith('https://') for x in p['timeline']))

    def test_a_repeated_raw_unit_filing_is_normalized_before_price_and_cost_calculation(self):
        import copy, contextlib, io, os, subprocess
        from datetime import datetime, timezone
        import audit_13f_history as audit
        import fetch_prices_all as pricing
        from validate_data import validate_history
        normalized=[dict(ticker=t,cusip=t,name=t,cls='COM',shares=1000,value=100000,putCall='',shareType='SH') for t in ['AAA','BBB','CCC']]
        raw=[{**h,'value':100} for h in normalized]
        proof=dict(version=audit.VERSION,status='verified',factor=1000,sourceHash=audit.digest(raw),normalizedHash=audit.digest(normalized),checkedAt=datetime.now(timezone.utc).date().isoformat(),source='https://www.sec.gov/Archives/unit-proof.xml',anchors=[dict(ticker=h['ticker'],currency='USD',candidates=[1000]) for h in raw])
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'data.json';prices=Path(tmp)/'prices.json'
            data=dict(meta={},current=dict(quarter='2026 Q1',holdings=normalized,totalValue=300000),history=dict(quarters=['2026 Q1'],values=[.3],holdings={'2026 Q1':normalized},valueAudit={'2026 Q1':proof}))
            path.write_text(json.dumps(data))
            def runner(args,**kwargs):
                script=args[2]
                if script=='fetch_13f_all.py':
                    d=json.loads(path.read_text());d['current']['holdings']=copy.deepcopy(raw);d['current']['totalValue']=300;d['history']['holdings']['2026 Q1']=copy.deepcopy(raw);d['history']['values']=[.0003];path.write_text(json.dumps(d))
                elif script=='audit_13f_history.py':
                    audit.audit_investor('test',dict(path=str(path),cik='1'),0)
                elif script=='fetch_prices_all.py':
                    d=json.loads(path.read_text());validate_history(d['history'])
                    with patch.object(pricing,'finnhub',return_value=dict(c=100,h=100,l=100,o=100,pc=100,t=1)),patch.object(pricing,'yahoo_chart',return_value=None),patch.object(pricing.time,'sleep'):
                        pricing.fetch_us('test',dict(data=str(path),prices=str(prices)))
                return subprocess.CompletedProcess(args,0)
            with patch.dict(os.environ,{'TRACK_RUN_STATUS':'0'}),contextlib.redirect_stdout(io.StringIO()):
                failed=update_investors.run([dict(id='test',name='Test',source13F=True)],runner)
            self.assertEqual(failed,[])
            self.assertEqual(json.loads(prices.read_text())['costBasis']['AAA']['recent']['buy'],100)
            self.assertEqual(json.loads(path.read_text())['current']['totalValue'],300000)

    def test_failed_unit_audit_cannot_overwrite_the_previous_price_snapshot(self):
        import os,subprocess
        attempted=[]
        with tempfile.TemporaryDirectory() as tmp:
            prices=Path(tmp)/'prices.json';prices.write_text('previous verified prices')
            def runner(args,**kwargs):
                attempted.append(args[2])
                if args[2]=='fetch_prices_all.py':prices.write_text('invalid replacement')
                return subprocess.CompletedProcess(args,1 if args[2]=='audit_13f_history.py' else 0)
            with patch.dict(os.environ,{'TRACK_RUN_STATUS':'0'}):
                failed=update_investors.run([dict(id='test',name='Test',source13F=True)],runner)
            self.assertEqual(failed,['test_audit'])
            self.assertNotIn('fetch_prices_all.py',attempted)
            self.assertEqual(prices.read_text(),'previous verified prices')

    def test_project_discovery_excludes_navigation_and_rejects_changed_attribution(self):
        html='<a href="https://unrelated.test">Another company</a><p>Lux was the first investor in companies including '+', '.join(f'<a href="https://company{i}.test">Company {i}</a>' for i in range(9))+'</p>'
        result=projects.project_links(html.encode(),'https://www.luxcapital.com/people/josh-wolfe')
        self.assertEqual(len(result),9)
        self.assertNotIn('Another company',[p['name'] for p in result])
        with self.assertRaises(ValueError):projects.project_links(b'<p>All holdings are now different</p>','https://www.luxcapital.com/')

    def test_source_failure_keeps_previous_published_projects_and_prices(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'wolfe.json';path.write_text('{"verified":"previous"}')
            prices=Path(tmp)/'prices_wolfe.json';prices.write_text('{"quotes":{}}')
            config=dict(portfolioSources={'profile':'https://www.luxcapital.com/'},dataFile='wolfe.json',pricesFile='prices_wolfe.json')
            with self.assertRaises(ValueError):projects.refresh(config,tmp,get=lambda url:b'changed page')
            self.assertEqual(path.read_text(),'{"verified":"previous"}')
            self.assertEqual(prices.read_text(),'{"quotes":{}}')

    def test_sec_filer_must_match_the_requested_entity(self):
        with self.assertRaises(ValueError):projects.sec_filings({'cik':'123'},'1592843')

    def test_latest_complete_restatement_replaces_original_but_additive_amendment_does_not(self):
        recent=dict(form=['13F-HR/A','13F-HR/A','13F-HR','13F-HR'],accessionNumber=['0000000001-26-000004','0000000001-26-000003','0000000001-26-000002','0000000001-26-000001'],filingDate=['2026-05-21','2026-05-20','2026-05-15','2026-02-15'],reportDate=['2026-03-31']*3+['2025-12-31'],primaryDocument=['primary.xml']*4)
        def get(path):
            if path.startswith('submissions/'):return json.dumps({'filings':{'recent':recent}}).encode()
            kind='NEW HOLDINGS' if '26000004' in path else 'RESTATEMENT'
            return f'<edgarSubmission><periodOfReport>03-31-2026</periodOfReport><amendmentType>{kind}</amendmentType></edgarSubmission>'.encode()
        with patch.object(sec,'sec_fetch',side_effect=get):rows=sec.get_recent_filings('1',include_restatements=True)
        self.assertEqual(len(rows),2)
        self.assertTrue(rows[0]['accession'].endswith('000003'))
        self.assertEqual(rows[0]['amendmentType'],'RESTATEMENT')
        self.assertEqual(rows[1]['reportDate'],'2025-12-31')

    def test_publisher_catalogue_extracts_literal_pdf_urls_without_executing_javascript(self):
        html=b'''<div><time datetime=">2001-11-20T05:00:00Z"></time><a href="javascript:openPDF('Title','https://www.oaktreecapital.com/docs/default-source/memos/test.pdf?x=1')">You Cannot Predict</a><a href="javascript:alert('bad')">Unsafe</a></div>'''
        source=dict(investor='marks',adapter='oaktree_author',url='https://www.oaktreecapital.com/insights/memos',publisher='Oaktree')
        works=archive.primary_author_catalog(source,get=lambda url:(html,'text/html'))
        self.assertEqual(len(works),1);self.assertEqual(works[0]['date'],'2001-11-20');self.assertTrue(works[0]['sources'][0]['url'].startswith('https://'))

    def test_patient_catalogue_keeps_author_attribution_and_excludes_colleagues(self):
        cards=''.join(f'<div class="article_item" data-author="{author}"><a href="/articles/{i}"></a><p class="title">{title}</p><p class="date">{author} | 10/09/26</p></div>' for i,(author,title) in enumerate([('Samantha McLemore','Expectations'),('Another Author','Weekly Update')]))
        source=dict(investor='mclemore',adapter='patient_author',url='https://patientcapitalmanagement.com/insights',publisher='Patient',authors=['Samantha McLemore'])
        works=archive.primary_author_catalog(source,get=lambda url:(cards.encode(),'text/html'))
        self.assertEqual([w['title']['en'] for w in works],['Expectations'])
        self.assertEqual(works[0]['date'],'2026-10-09')

    def test_warrant_filing_reference_never_claims_a_live_market_price(self):
        from quote_coverage import warrant_reference
        holding=dict(ticker='TEST-WT',cusip='123456789',cls='WARRANT',shares=100,value=75)
        current=dict(periodEnd='2026-06-30',sourceFiling='https://www.sec.gov/Archives/edgar/data/1/test-index.html')
        ref=warrant_reference(holding,current)
        self.assertEqual(ref['filedUnitValue'],.75)
        self.assertEqual(ref['status'],'filing_reference')
        self.assertNotIn('c',ref);self.assertNotIn('t',ref)
        self.assertIsNone(warrant_reference({**holding,'cls':'COMMON STOCK'},current))

    def test_lifecycle_event_is_class_specific_and_has_primary_evidence(self):
        event=event_for(dict(cusip='8676EP108',ticker='STKL'))
        self.assertEqual(event['status'],'ceased_trading')
        self.assertTrue(event['sourceURL'].endswith('.pdf'))
        self.assertIsNone(event_for(dict(cusip='8676EP108',ticker='OTHER')))
        self.assertIsNone(event_for(dict(cusip='67623C307',ticker='OPI')))

if __name__=='__main__':unittest.main()
