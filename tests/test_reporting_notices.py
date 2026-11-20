import copy
import json
import unittest
from unittest.mock import Mock,patch
from datetime import datetime,timezone
import reporting_scope as scope
import fetch_13f_all as filings
import automation_health as health

COVER=b'''<edgarSubmission xmlns="http://www.sec.gov/edgar/thirteenffiler"><headerData><submissionType>13F-NT</submissionType><filerInfo><filer><credentials><cik>0000949509</cik></credentials></filer></filerInfo></headerData><formData><coverPage><reportCalendarOrQuarter>09-30-2026</reportCalendarOrQuarter><reportType>13F NOTICE</reportType><otherManagersInfo><otherManager><name>Reporting Manager</name><form13FFileNumber>028-12345</form13FFileNumber></otherManager></otherManagersInfo></coverPage></formData></edgarSubmission>'''

class NoticeTests(unittest.TestCase):
    def setUp(self):
        self.data={'meta':{'managerCIK':'0000949509'},'current':{'periodEnd':'2026-06-30','quarter':'2026 Q2','holdings':[{'ticker':'KEEP','shares':12}]},'history':{'holdings':{'2026 Q2':[{'ticker':'KEEP','shares':12}]}}}
        self.candidate={'cik':'0000949509','form':'13F-NT','reportDate':'2026-09-30','filingDate':'2026-11-17','accessionNumber':'0001193125-26-464327','primaryDocument':'primary_doc.xml'}

    def test_verified_notice_is_metadata_and_never_a_portfolio_or_zero_position(self):
        original=copy.deepcopy(self.data);fetch=Mock(return_value=COVER)
        scope.refresh_notice(self.data,{'cik':'949509'},[self.candidate],fetch)
        self.assertEqual(self.data['current'],original['current']);self.assertEqual(self.data['history'],original['history'])
        self.assertTrue(scope.notice_covers(self.data,'2026-09-30'))
        self.assertFalse(scope.notice_covers(self.data,'2026-12-31'))
        self.assertEqual(self.data['meta']['reportingNotice']['otherManagers'][0]['name'],'Reporting Manager')
        fetch.assert_called_once_with('/Archives/edgar/data/949509/000119312526464327/primary_doc.xml')

    def test_wrong_identity_period_or_form_cannot_acknowledge_overdue_report(self):
        for raw in [COVER.replace(b'0000949509',b'0000000001'),COVER.replace(b'09-30-2026',b'06-30-2026'),COVER.replace(b'13F-NT',b'13F-HR')]:
            with self.subTest(raw=raw),self.assertRaises(ValueError):scope.refresh_notice(self.data,{'cik':'949509'},[self.candidate],lambda _:raw)
        self.assertNotIn('reportingNotice',self.data['meta'])

    def test_new_independent_filing_retires_old_notice(self):
        scope.refresh_notice(self.data,{'cik':'949509'},[self.candidate],lambda _:COVER)
        self.data['current']['periodEnd']='2026-09-30'
        scope.refresh_notice(self.data,{'cik':'949509'},[self.candidate],Mock(side_effect=AssertionError('No request needed')))
        self.assertNotIn('reportingNotice',self.data['meta'])

    def test_forged_metadata_or_other_manager_never_suppresses_warning(self):
        scope.refresh_notice(self.data,{'cik':'949509'},[self.candidate],lambda _:COVER)
        for field,value in [('managerCIK','0000000001'),('source','https://example.org/cover.xml'),('sourceSha256',''),('otherManagers',[])]:
            bad=copy.deepcopy(self.data);bad['meta']['reportingNotice'][field]=value
            self.assertFalse(scope.notice_covers(bad,'2026-09-30'))

    def test_submissions_collect_notices_without_exposing_them_as_holdings_reports(self):
        rec={'form':['13F-NT','13F-HR'],'accessionNumber':['0001193125-26-464327','0000949509-26-000005'],'reportDate':['2026-09-30','2026-06-30'],'filingDate':['2026-11-17','2026-08-14'],'primaryDocument':['primary_doc.xml','primary_doc.xml']}
        with patch.object(filings,'sec_fetch',return_value=json.dumps({'filings':{'recent':rec}}).encode()):
            batch=filings.get_recent_filings('949509')
        self.assertEqual(len(batch),1);self.assertEqual(batch[0]['reportDate'],'2026-06-30')
        self.assertEqual(batch.notices[0]['reportDate'],'2026-09-30')

    def test_failed_notice_read_preserves_holdings_and_is_not_blessed(self):
        batch=scope.FilingBatch([], [self.candidate]);before=copy.deepcopy(self.data)
        with patch.object(filings,'sec_fetch',side_effect=TimeoutError),patch('update_status.record_source_warning') as warn:
            filings.update_reporting_notice('marks',{'cik':'949509'},self.data,batch)
        self.assertEqual(self.data['current'],before['current']);warn.assert_called_once()
        self.assertFalse(scope.notice_covers(self.data,'2026-09-30'))

    def test_health_acknowledges_verified_notice_but_keeps_true_missing_reports(self):
        import tempfile
        from pathlib import Path
        scope.refresh_notice(self.data,{'cik':'949509'},[self.candidate],lambda _:COVER)
        now=datetime(2026,11,20,12,tzinfo=timezone.utc)
        self.data['meta']['lastUpdated']=now.isoformat()
        with tempfile.TemporaryDirectory() as d,patch('quote_coverage.coverage',return_value={'missing':[]}):
            root=Path(d);(root/'investors.json').write_text(json.dumps({'investors':[{'id':'marks','source13F':True,'dataFile':'marks.json'}]}));(root/'run_status.json').write_text('{"runs":[]}')
            (root/'marks.json').write_text(json.dumps(self.data))
            self.assertEqual(health.data_health(root,now),[])
            self.data['meta'].pop('reportingNotice');(root/'marks.json').write_text(json.dumps(self.data))
            self.assertIn({'code':'report_overdue','investor':'marks'},health.data_health(root,now))

    def test_notice_from_predecessor_cannot_change_current_reporter_scope(self):
        latest=scope.FilingBatch([{'reportDate':'2026-06-30','filingDate':'2026-08-14'}],[self.candidate])
        old=scope.FilingBatch([{'reportDate':'2019-12-31','filingDate':'2020-02-14'}],[{**self.candidate,'cik':'0000000001'}])
        with patch.object(filings,'get_recent_filings',side_effect=[latest,old]):
            result=filings.investor_filings({'cik':'949509','legacyFilers':[{'cik':'1','beforePeriod':'2020-01-01'}]})
        self.assertEqual(result.notices,[self.candidate])

    def test_sec_xsl_display_prefix_resolves_only_to_its_own_raw_xml(self):
        rec={'form':['13F-NT'],'accessionNumber':['0001193125-26-464327'],'reportDate':['2026-09-30'],'filingDate':['2026-11-17'],'primaryDocument':['xslForm13F_X02/primary_doc.xml']}
        result=scope.notice_candidates('949509',{'filings':{'recent':rec}})
        self.assertEqual(result[0]['primaryDocument'],'primary_doc.xml')
        for path in ['../../primary_doc.xml','https://other.test/primary_doc.xml','unknown/primary_doc.xml']:
            rec['primaryDocument']=[path]
            self.assertEqual(scope.notice_candidates('949509',{'filings':{'recent':rec}}),[])
