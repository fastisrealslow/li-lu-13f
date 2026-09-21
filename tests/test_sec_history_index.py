import gzip
import unittest
from unittest.mock import patch
import sec_history_index as index
import fetch_13f_all as fetcher

CIK='1709323'
ACC='0001709323-19-000001'
PATH='/Archives/edgar/data/1709323/'+ACC+'.txt'
CANDIDATE=dict(accessionDashed=ACC,accession=ACC.replace('-',''),form='13F-HR',filingDate='2019-05-14',submissionPath=PATH)


def master(rows):
    return gzip.compress(('CIK|Company Name|Form Type|Date Filed|Filename\n'+ '\n'.join(rows)).encode())


def row(cik=CIK,form='13F-HR'):
    return f'{cik}|Himalaya Capital Management LLC|{form}|2019-05-14|edgar/data/{cik}/{ACC}.txt'


def submission(form='13F-HR',amendment=''):
    return f'''<SEC-HEADER>
ACCESSION NUMBER: {ACC}
CONFORMED SUBMISSION TYPE: {form}
CONFORMED PERIOD OF REPORT: 20190331
FILED AS OF DATE: 20190514
FILER:
 COMPANY DATA:
  CENTRAL INDEX KEY: 0001709323
</SEC-HEADER>
<amendmentType>{amendment}</amendmentType>'''.encode()


class HistoryIndexTests(unittest.TestCase):
    def test_master_requires_gzip_and_known_columns(self):
        for payload in [b'Service unavailable',gzip.compress(b'Error page')]:
            with self.assertRaises((ValueError,OSError)):
                index.parse_index(payload,CIK)

    def test_match_cik_not_familiar_manager_name_and_exclude_form_d(self):
        records=index.parse_index(master([row(),row('1576745'),row(form='D')]),CIK)
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['submissionPath'],PATH)

    def test_header_controls_report_quarter(self):
        record=index.bind_submission(submission(),CANDIDATE,CIK)
        self.assertEqual(record['reportDate'],'2019-03-31')
        self.assertEqual(record['filingDate'],'2019-05-14')
        self.assertTrue(record['completePortfolio'])
        with self.assertRaisesRegex(ValueError,'CIK/accession'):
            index.bind_submission(submission(),CANDIDATE,'1576745')

    def test_full_restatement_allowed_but_additive_amendment_not_whole_portfolio(self):
        for amendment,complete in [('RESTATEMENT',True),('ADD NEW HOLDINGS',False),('',False)]:
            result=index.bind_submission(submission('13F-HR/A',amendment),{**CANDIDATE,'form':'13F-HR/A'},CIK)
            self.assertEqual(result['completePortfolio'],complete)

    def test_filings_outside_requested_report_period_are_not_backfilled(self):
        def request(path):return master([row()]) if path.endswith('.gz') else submission()
        filings,audit=index.discover(CIK,['2018 Q4'],request)
        self.assertEqual(filings,[])
        self.assertEqual(audit['status'],'checked')

    def test_valid_empty_search_cached_but_not_zero_portfolio(self):
        with patch('sec_history_index.stamp',return_value=index.stamp()):
            request=lambda path:master([row('1576745',form='D')])
            filings,audit=index.discover(CIK,['2019 Q1'],request)
        self.assertFalse(filings)
        self.assertEqual(audit['status'],'checked')
        with patch('sec_history_index.parse_index',side_effect=AssertionError('Must reuse cache')):
            again,result=index.discover(CIK,['2019 Q1'],lambda p:self.fail('Unexpected fetch'),audit)
        self.assertFalse(again)
        self.assertEqual(result['checkedAt'],audit['checkedAt'])

    def test_error_is_partial_and_next_run_retries(self):
        def offline(path):raise OSError('unavailable')
        filings,audit=index.discover(CIK,['2019 Q1'],offline)
        self.assertFalse(filings)
        self.assertEqual(audit['status'],'partial')
        _,recovered=index.discover(CIK,['2019 Q1'],lambda p:master([row('123')]),audit)
        self.assertEqual(recovered['status'],'checked')

    def test_bounded_index_scan_records_deferred_work(self):
        _,audit=index.discover(CIK,['2018 Q4','2019 Q1','2019 Q2','2019 Q3'],lambda p:master([row('123')]),max_indexes=2)
        self.assertEqual(len(audit['indexes']),2)
        self.assertEqual(audit['status'],'partial')
        self.assertTrue(audit['deferred'])

    def test_discovery_recovers_quarter_missing_from_submissions(self):
        data={'history':{'quarters':['2018 Q4','2019 Q2'],'values':[1,2],'holdings':{}}}
        table=b'<informationTable xmlns="http://www.sec.gov/edgar/document/thirteenf/informationtable"><infoTable><nameOfIssuer>APPLE INC</nameOfIssuer><value>1000</value><shrsOrPrnAmt><sshPrnamt>500</sshPrnamt></shrsOrPrnAmt></infoTable></informationTable>'
        def request(path):
            if path.endswith('.gz'):return master([row()])
            if path.endswith('.txt'):return submission()
            return table
        with patch.object(fetcher,'get_recent_filings',return_value=[]),patch.object(fetcher,'sec_fetch',side_effect=request),patch.object(fetcher,'find_info_table_xml',return_value='/Archives/test-table.xml'):
            fetcher.backfill_history_gaps(CIK,data,[])
        self.assertEqual(data['history']['coverage']['missingQuarters'],[])
        self.assertEqual(data['history']['holdings']['2019 Q1'][0]['value'],1000000)
        self.assertEqual(data['history']['filing_sources']['2019 Q1']['source'],'sec_quarterly_master_index')
