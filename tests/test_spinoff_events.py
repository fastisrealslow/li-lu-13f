import copy
import unittest
from pathlib import Path
from unittest.mock import patch
from spinoff_events import (infer_status, extract_name, extract_dates, filing_url, normalize, validate_events, parse_evidence)


class SpinEvidenceTests(unittest.TestCase):
    def hk_proof(self):
        text = (Path(__file__).parent / 'fixtures/hk_listing_completion.txt').read_text()
        ann = {'date': '2025-10-15', 'title': '建議分拆及軒竹生物於香港聯合交易所有限公司主板獨立上市之更新資料 - 軒竹生物上市及開始買賣',
               'docUrl': '/listedco/listconews/sehk/2025/1015/2025101500144_c.pdf'}
        return ann, parse_evidence(text, ann)

    def test_hk_listing_pdf_layout_and_child_identity(self):
        ann, proof = self.hk_proof()
        self.assertEqual(proof['status'], 'completed')
        self.assertEqual(proof['targetName'], '軒竹生物')
        self.assertEqual(proof['targetTicker'], '02575.HK')
        self.assertEqual(proof['dates']['listingDate']['date'], '2025-10-15')
        self.assertEqual(proof['dates']['listingDate']['kind'], 'actual')
        data = {'companies': [{'stockCode': '00460', 'ticker': '00460.HK', 'stockName': '四環醫藥',
                              'announcements': [ann], 'filingEvidence': [proof]}]}
        previous = normalize({'companies': [{'stockCode': '00460', 'ticker': '00460.HK'}]}, 'hk')
        result = normalize(data, 'hk', previous=previous)
        self.assertEqual(len(result['events']), 1)
        self.assertEqual(result['events'][0]['id'], previous['events'][0]['id'])
        self.assertEqual(result['events'][0]['targetTicker'], '02575.HK')
        validate_events(result)

    def test_hk_expected_and_negative_trading_are_not_completion(self):
        for s in ['分拆公司H股預計開始於聯交所主板買賣', '分拆公司H股未開始於聯交所主板買賣',
                  '分拆公司若完成上市及開始買賣', '建議分拆及預計上市及開始買賣',
                  '分拆公司股份將於明日上市及開始買賣']:
            self.assertNotEqual(infer_status(s)['status'], 'completed', s)

    def test_hk_named_child_and_alias_exclude_parent_code(self):
        text = ('股份代號：9618。分拆京東工業股份有限公司於香港聯合交易所有限公司主板獨立上市。'
                '分拆京東工業股份有限公司上市及京東工業股份有限公司股份開始買賣。'
                '京東工業股份有限公司（「京東工業」）於2025年12月11日在香港聯交所主板上市。'
                '京東工業於2025年12月11日在香港聯交所主板上市。'
                '京東工業股份以每手200股進行買賣，股份代號為7618。')
        proof = parse_evidence(text, {'date': '2025-12-11',
            'docUrl': '/listedco/listconews/sehk/2025/1211/2025121101039_c.pdf'})
        self.assertEqual(proof['status'], 'completed')
        self.assertEqual(proof['targetTicker'], '07618.HK')
        self.assertEqual(proof['dates']['listingDate']['date'], '2025-12-11')

    def test_completion_survives_later_prospectus_reference(self):
        ann, proof = self.hk_proof()
        data = {'companies': [{'stockCode': '00460', 'filingEvidence': [proof, {
            **proof, 'date': '2026-01-01', 'status': 'prospectus', 'quote': '建議分拆的招股章程更新',
            'url': 'https://www1.hkexnews.hk/later.pdf'}]}]}
        result = normalize(data, 'hk')
        self.assertEqual(result['events'][0]['status'], 'completed')
        self.assertEqual(result['events'][0]['evidence']['date'], ann['date'])

    def test_pdf_download_failure_preserves_previous_evidence(self):
        import fetch_spinoff
        ann, proof = self.hk_proof()
        c = {'stockCode': '00460', 'stockName': '四環醫藥', 'announcements': [ann]}
        with patch.object(fetch_spinoff, 'load_prev_data', return_value={'00460': {'filingEvidence': [proof]}}), \
             patch.object(fetch_spinoff.time, 'sleep'), patch.object(fetch_spinoff, 'get_opener') as opener:
            opener.open.side_effect = OSError('offline')
            fetch_spinoff.refine_status_from_pdf([c], opener)
        self.assertEqual(c['filingEvidence'], [proof])

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
        self.assertEqual(extract_name('建議分拆所屬子公司江西省江銅銅箔科技股份有限公司及獨立上市'), '江西省江銅銅箔科技股份有限公司')
        self.assertEqual(extract_name('建議分拆物泊科技於香港聯合交易所有限公司上市'), '')
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

    def test_resolving_one_of_multiple_targets_keeps_unique_ids(self):
        data = self.fixture()
        old = normalize(copy.deepcopy(data), 'us')
        data['companies'][0]['filingEvidence'] = [{'targetName': 'Child Holdings', 'status': 'announced',
            'quote': 'We plan the spin-off.', 'url': filing_url('1234567','0001234567-26-000001'),
            'accession': '0001234567-26-000001', 'date': '2026-09-16', 'dates': {}},
            {'targetName': '', 'status': 'needs_review', 'quote': '', 'url': '', 'dates': {}}]
        result = normalize(data, 'us', previous=old)
        self.assertEqual(len({e['id'] for e in result['events']}), 2)
        validate_events(result)

    def test_encoded_dates_are_readable(self):
        dates = extract_dates('Record date: September&#160;15, 2026. distribution date: 2026 年 10 月 1 日。')
        self.assertEqual(dates['recordDate']['date'], '2026-09-15')
        self.assertEqual(dates['distributionDate']['date'], '2026-10-01')

    def test_parent_name_is_not_reused_as_child(self):
        data = self.fixture()
        data['companies'][0].update(name='Parent Holdings, Inc. (PARENT)', spinoffName='PARENT HOLDINGS INC')
        self.assertEqual(normalize(data, 'us')['events'][0]['targetName'], '')

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
        self.assertEqual(changed['changes'][0]['parentTicker'], 'PARENT')
        self.assertEqual(changed['changes'][0]['before']['status'], 'completed')
        self.assertEqual(changed['changes'][0]['after']['status'], 'terminated')
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
