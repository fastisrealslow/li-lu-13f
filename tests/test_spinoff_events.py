import copy
import unittest
from spinoff_events import (infer_status, extract_name, extract_dates, filing_url, normalize, validate_events)


class SpinEvidenceTests(unittest.TestCase):
    def test_completion_requires_actual_positive_statement(self):
        for text in [
            'The spin-off is expected to be completed in 2027.',
            'The spin-off has not been completed.',
            'The spin-off will be completed tomorrow.',
            'If the spin-off is completed, holders receive shares.',
            'The spin-off has never been completed.',
            '建議分拆預計將於明年完成。',
            '分拆尚未完成。',
        ]:
            with self.subTest(text=text):
                self.assertNotEqual(infer_status(text)['status'], 'completed')
        for text in ['The company has completed the spin-off.', 'The spin-off has been completed.', '本公司已完成分拆。']:
            self.assertEqual(infer_status(text)['status'], 'completed', text)

    def test_prospectus_and_expected_date_are_not_completion(self):
        self.assertEqual(infer_status('建議分拆及刊發招股章程')['status'], 'prospectus')
        self.assertEqual(infer_status('The distribution date is January 4, 2020.')['status'], 'needs_review')
        self.assertEqual(infer_status('建議分拆獲聯交所批准')['status'], 'approved')
        self.assertNotEqual(infer_status('The spin-off has not been approved.')['status'], 'approved')

    def test_prose_is_not_a_child_company_name(self):
        self.assertEqual(extract_name('Corteva common stock will trade without an entitlement to receive the Vylor Co'), '')
        self.assertEqual(extract_name('The spin-off of Example Holdings was announced.'), 'Example Holdings')
        self.assertEqual(extract_name('The spin-off of Alpha Holdings and separation of Beta Holdings.'), '')

    def test_dates_are_normalized_and_conflicts_remain_unknown(self):
        self.assertEqual(extract_dates('The record date is September 15, 2026.')['recordDate']['date'], '2026-09-15')
        self.assertEqual(extract_dates('distribution date: 2026-10-01')['distributionDate']['date'], '2026-10-01')
        self.assertNotIn('recordDate', extract_dates('Record date: May 1, 2026. Record date: May 2, 2026.'))
        self.assertFalse(extract_dates('record date: February 31, 2026'))

    def fixture(self):
        ann = {'adsh':'0001234567-26-000001', 'date':'2026-09-16', 'title':'Spin-off filing'}
        return {'updatedAt':'2026-09-16', 'companies':[{'ticker':'PARENT','cik':'1234567', 'spinoffName':'Child Holdings',
            'status':'completed', 'distributionDate':'2020-01-01', 'announcements':[ann]}]}

    def test_exact_accession_links_and_legacy_status_not_trusted(self):
        result = normalize(self.fixture(), 'us')
        e = result['events'][0]
        self.assertEqual(e['status'], 'needs_review')
        self.assertFalse(e['dates'])
        self.assertIn('000123456726000001/0001234567-26-000001-index.html', e['announcements'][0]['url'])
        self.assertEqual(filing_url('123','../bad'), '')
        validate_events(result)

    def test_multi_target_events_and_semantic_changes(self):
        data = self.fixture()
        proof = {'targetName':'Alpha Holdings','status':'completed','quote':'The company has completed the spin-off.',
                 'date':'2026-09-16','url':filing_url('1234567','0001234567-26-000001'),'dates':{}}
        data['companies'][0]['filingEvidence']=[proof,{**proof,'targetName':'Beta Holdings'}]
        first = normalize(data, 'us', now='2026-09-16T00:00:00Z')
        self.assertEqual(len(first['events']),2)
        self.assertEqual(first['changes'],[])
        again = normalize(copy.deepcopy(first),'us',now='2026-09-17T00:00:00Z')
        self.assertEqual(again['changes'],[])
        again['companies'][0]['filingEvidence'][0]['status']='terminated'
        again['companies'][0]['filingEvidence'][0]['quote']='The spin-off has been terminated.'
        changed = normalize(again,'us',now='2026-09-18T00:00:00Z')
        self.assertEqual(len(changed['changes']),1)
        self.assertEqual(changed['changes'][0]['fields'],['status'])
        validate_events(changed)

    def test_publishing_rejects_status_without_source(self):
        data=normalize(self.fixture(),'us')
        data['events'][0]['status']='completed'
        with self.assertRaises(ValueError): validate_events(data)

    def test_company_directory_and_routine_filings_do_not_establish_status(self):
        data=self.fixture()
        data['companies'][0]['announcements']=[{'date':'2026-09-16','title':'The spin-off has been completed.',
            'url':'https://www.sec.gov/cgi-bin/browse-edgar?CIK=123'}]
        self.assertEqual(normalize(data,'us')['events'][0]['status'],'needs_review')


if __name__ == '__main__': unittest.main()
