import unittest
from holdings_diff import consolidate_holdings
from reporting_scope import parse_cover,same_manager_history
import speech_archive as archive
from validate_data import validate_manager_allocations


class ReportingScopeTests(unittest.TestCase):
    def test_blank_na_and_joint_manager_rows_round_trip_with_complete_totals(self):
        from fetch_13f_all import parse_holdings
        for field in ['', '<otherManager/>','<otherManager>N/A</otherManager>','<otherManager>NONE</otherManager>']:
            row=lambda manager,shares,value:f'<infoTable><nameOfIssuer>TEST</nameOfIssuer><titleOfClass>COM</titleOfClass><cusip>123456789</cusip><value>{value}</value><shrsOrPrnAmt><sshPrnamt>{shares}</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt>{manager}</infoTable>'
            xml=('<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable">'+row(field,10,100)+row('<otherManager>1, 1, 3</otherManager>',20,200)+'</informationTable>').encode()
            for filed,factor in [('2026-08-14',1),('2022-08-14',1000)]:
                with self.subTest(field=field,filed=filed):
                    holdings=parse_holdings(xml,filing_date=filed)
                    self.assertEqual(len(holdings),1)
                    h=holdings[0];validate_manager_allocations(h)
                    self.assertEqual((h['shares'],h['value']),(30,300*factor))
                    self.assertEqual([a['managerIds'] for a in h['managerAllocations']],[[],['1','3']])

    def test_absent_manager_references_are_valid_but_malformed_ids_and_totals_are_not(self):
        h={'shares':10,'value':100,'managerAllocations':[{'managerIds':[],'shares':10,'value':100}]}
        validate_manager_allocations(h)
        for ids in [None,['1','1'],['invalid'],[{'id':'1'}]]:
            h['managerAllocations'][0]['managerIds']=ids
            with self.assertRaisesRegex(ValueError,'Invalid manager'):validate_manager_allocations(h)

    def test_history_bridge_requires_cover_cik_previous_filing_and_every_allocation(self):
        h={'ticker':'TEST','cusip':'test','shares':10,'value':100,'shareType':'SH','putCall':'','managerAllocations':[{'managerIds':['7','8'],'shares':10,'value':100}]}
        scope={'quarter':'2026 Q2','managers':{'7':{'cik':'0001'},'8':{'cik':'0002'}}}
        data={'meta':{'reportingTransition':{'fromQuarter':'2026 Q2','fromCIK':'1'}},'current':{'quarter':'2026 Q2','reportingScope':scope,'holdings':[h]},'history':{'filing_sources':{'2026 Q1':{'cik':'1'}},'holdings':{'2026 Q2':[h]},'reportingScopes':{'2026 Q2':scope}}}
        self.assertTrue(same_manager_history(data,h))
        data['current']={'quarter':'2026 Q3'}
        self.assertTrue(same_manager_history(data,h))
        h['managerAllocations']=[{'managerIds':['7'],'shares':6,'value':60},{'managerIds':['8'],'shares':4,'value':40}]
        self.assertFalse(same_manager_history(data,h))
        h['managerAllocations']=[{'managerIds':['7'],'shares':10,'value':100}]
        data['history']['filing_sources']['2026 Q1']['cik']='different'
        self.assertFalse(same_manager_history(data,h))

    def test_numbered_managers_are_resolved_from_cover_not_guessed_from_ticker(self):
        cover=b'<root><otherManager2><sequenceNumber>6</sequenceNumber><otherManager><cik>123</cik><name>Separate vehicle</name></otherManager></otherManager2></root>'
        result=parse_cover(cover,'https://www.sec.gov/Archives/cover.xml','2026 Q2')
        self.assertEqual(result['managers']['6'],{'name':'Separate vehicle','cik':'123'})

    def test_one_row_with_multiple_managers_is_not_counted_multiple_times(self):
        base={'ticker':'TEST','cusip':'1','shares':10,'value':100,'managerAllocations':[{'managerIds':['1','2'],'shares':10,'value':100}]}
        other={**base,'shares':20,'value':200,'managerAllocations':[{'managerIds':['1','6'],'shares':20,'value':200}]}
        row=consolidate_holdings([base,other])[0]
        self.assertEqual((row['shares'],row['value']),(30,300))
        self.assertEqual(len(row['managerAllocations']),2)
        self.assertEqual(len(base['managerAllocations']),1)
        validate_manager_allocations(row)
        row['managerAllocations'][0]['shares']+=1
        with self.assertRaisesRegex(ValueError,'disagree'):validate_manager_allocations(row)

    def test_buffett_letters_do_not_attribute_abels_annual_letter_to_buffett(self):
        source={'adapter':'buffett_letters','url':'https://www.berkshirehathaway.com/letters/letters.html','publisher':'Berkshire Hathaway'}
        html=b'<a href="2023ltr.pdf">2023</a><a href="2025ltr.pdf">2025</a><a href="other.html">Company news</a>'
        works=archive.link_catalog(source,lambda url:(html,'text/html'))
        self.assertEqual([w['date'] for w in works],['2023'])
        self.assertEqual(works[0]['kind'],'essay')

    def test_feed_author_filter_does_not_assign_another_authors_work(self):
        source={'url':'https://publisher.example/feed','investor':'webb','publisher':'Publisher','authorPattern':'^Webb-site.com$'}
        raw=b'<rss xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><item><title>Another author</title><link>https://publisher.example/other</link><dc:creator>Other guest</dc:creator></item><item><title>Verified essay</title><link>https://publisher.example/own</link><dc:creator>Webb-site.com</dc:creator></item></channel></rss>'
        self.assertEqual([w['title']['en'] for w in archive.rss_catalog(source,lambda u:(raw,'text/xml'))],['Verified essay'])

class AuthorityEvidenceTests(unittest.TestCase):
    def test_original_discretion_voting_and_separate_source_lines_survive_consolidation(self):
        from fetch_13f_all import parse_holdings
        import build_browser_assets as browser
        row=lambda code,votes:f'''<infoTable><nameOfIssuer>TEST</nameOfIssuer><titleOfClass>COM</titleOfClass><cusip>123456789</cusip><value>100</value><shrsOrPrnAmt><sshPrnamt>10</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt><investmentDiscretion>{code}</investmentDiscretion><otherManager>1</otherManager><votingAuthority><Sole>{votes[0]}</Sole><Shared>{votes[1]}</Shared><None>{votes[2]}</None></votingAuthority></infoTable>'''
        xml=('<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable">'+row('SOLE',(10,0,0))+row('DEFINED',(0,4,6))+'</informationTable>').encode()
        h=parse_holdings(xml,filing_date='2026-08-14')[0]
        self.assertEqual((h['shares'],h['value']),(20,200))
        self.assertNotIn('investmentDiscretion',h)
        self.assertEqual(h['votingAuthority'],{'Sole':10,'Shared':4,'None':6})
        self.assertEqual([a['investmentDiscretion']for a in h['managerAllocations']],['SOLE','DEFINED'])
        self.assertEqual(browser.compact_row(h)['managerAllocations'],h['managerAllocations'])

    def test_uncollected_authority_is_absent_instead_of_invented_zero(self):
        from fetch_13f_all import parse_holdings
        xml=b'<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable"><infoTable><nameOfIssuer>TEST</nameOfIssuer><titleOfClass>COM</titleOfClass><cusip>123456789</cusip><value>100</value><shrsOrPrnAmt><sshPrnamt>10</sshPrnamt></shrsOrPrnAmt></infoTable></informationTable>'
        h=parse_holdings(xml,filing_date='2026-08-14')[0]
        self.assertNotIn('investmentDiscretion',h);self.assertNotIn('votingAuthority',h)
