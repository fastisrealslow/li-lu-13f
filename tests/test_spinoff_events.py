import copy
import unittest
from pathlib import Path
from unittest.mock import patch
from spinoff_events import (infer_status, extract_name, extract_dates, filing_url, normalize, validate_events, parse_evidence, merge_evidence, iso_date, classify_hk_type)


class SpinEvidenceTests(unittest.TestCase):
    def test_source_warning_survives_repeated_warning_and_final_success(self):
        import update_status
        state = {'runs': [{'steps': {}}]}
        with patch.object(update_status, 'load', return_value=state), patch.object(update_status, 'save'):
            update_status.update_step('spinoff_us', 'warn', 'AI unavailable')
            update_status.update_step('spinoff_us', 'warn', 'SEC unavailable')
            update_status.update_step('spinoff_us', 'warn', 'SEC unavailable')
            update_status.update_step('spinoff_us', 'ok')
        self.assertEqual(state['runs'][0]['steps']['spinoff_us']['status'], 'warn')
        self.assertEqual(state['runs'][0]['steps']['spinoff_us']['msg'], 'AI unavailable；SEC unavailable')

    def test_distribution_is_not_automatically_a_hong_kong_introduction(self):
        self.assertEqual(classify_hk_type(['以實物分派方式宣派特別股息'])['code'], 'distribution')
        foreign = classify_hk_type(['分拆MAYNILAD WATER SERVICES, INC.及於菲律賓證券交易所獨立上市：以實物分派方式提供保證的權利'])
        self.assertEqual(foreign['code'], 'ipo_other_dist')
        self.assertEqual(foreign['exchange_en'], 'PSE')
        self.assertEqual(classify_hk_type(['以介紹方式於香港聯合交易所主板上市'])['code'], 'intro_hk')

    def test_separate_targets_do_not_inherit_company_wide_reit_type(self):
        data = {'companies': [{'stockCode': '00656', 'ticker': '00656.HK', 'spinType': {'code': 'reit_sh', 'is_reit': True},
            'announcements': [
                {'date': '2026-08-28', 'title': '建議分拆CLUBMED LIFESTYLE並於香港聯交所主板獨立上市', 'docUrl': '/listedco/clubmed.pdf'},
                {'date': '2026-05-01', 'title': '擬通過中國商業不動產證券投資基金在上海證券交易所分拆上市', 'docUrl': '/listedco/reit.pdf'}]}]}
        result = normalize(data, 'hk')
        club = next(e for e in result['events'] if e['targetName'] == 'CLUBMED LIFESTYLE')
        self.assertFalse(club['type']['is_reit'])
        self.assertEqual(club['type']['code'], 'ipo_hk')
        self.assertTrue(any(e['type']['is_reit'] for e in result['events']))

    def test_script_variants_and_explicit_alias_share_one_event(self):
        text = '分拆复星安特金（成都）生物制药股份有限公司（以下简称“复星安特金”）於香港主板上市。'
        proof = parse_evidence(text, {'date': '2026-06-26', 'docUrl': '/listedco/latest.pdf'})
        data = {'companies': [{'stockCode': '02196', 'filingEvidence': [proof], 'announcements': [
            {'date': '2026-02-01', 'title': '建議分拆復星安特金並於香港聯合交易所有限公司主板獨立上市', 'docUrl': '/listedco/old.pdf'}]}]}
        self.assertEqual(len(normalize(data, 'hk')['events']), 1)

    def test_legacy_candidate_name_keeps_watchlist_identity(self):
        data = self.fixture()
        first = normalize(data, 'us')
        second = normalize(copy.deepcopy(first), 'us')
        self.assertEqual(first['events'][0]['id'], second['events'][0]['id'])

    def test_status_categories_reject_boilerplate_and_future_prospectus(self):
        for text in [
            'In the event of any stock split, recapitalization, spin-off or reclassification, the Plan will adjust the award.',
            'The Plan provides distributions after Separation from Service.',
            'The distribution of the Offered Securities is described in the prospectus.',
            'The Renesas Base Distribution Date under the Plan is expected next year.',
        ]:
            self.assertEqual(infer_status(text)['status'], 'needs_review', text)
        self.assertNotEqual(infer_status('For the proposed spin-off, the parties intend to file a prospectus.')['status'], 'prospectus')
        self.assertEqual(infer_status('The spin-off has been completed on May 1, 2026.')['status'], 'completed')
        self.assertEqual(infer_status('完成建議分拆MAYNILAD WATER SERVICES, INC.及於菲律賓上市')['status'], 'completed')
        self.assertEqual(infer_status('擬議分拆獲香港聯交所批准')['status'], 'approved')

    def test_paused_is_distinct_from_terminated(self):
        self.assertEqual(infer_status('本公司決定於現階段不進行建議分拆及建議於美國上市。')['status'], 'paused')
        self.assertEqual(infer_status('本公司已終止建議分拆。')['status'], 'terminated')
        self.assertEqual(infer_status('The spin-off has been terminated.')['status'], 'terminated')
        self.assertNotEqual(infer_status('The company has terminated an employment agreement during the spin-off.')['status'], 'terminated')

    def test_record_date_status_and_dates_before_labels(self):
        for text in ['The Board has approved a record date of June 26, 2026 for the spin-off.',
                     '釐定股東於實物分派的權利的記錄日期為二零二六年三月十七日。']:
            self.assertEqual(infer_status(text)['status'], 'record_set')
        self.assertEqual(extract_dates('June 26, 2026 (the “Record Date”).')['recordDate']['date'], '2026-06-26')
        self.assertEqual(iso_date('二零二六年十十月一日'), '')
        self.assertNotEqual(infer_status('The Board has not set the record date of May 1, 2026 for the spin-off.')['status'], 'record_set')

    def test_primary_sec_document_does_not_select_equity_plan_attachment(self):
        import fetch_spinoff_us as fetch
        index = '''<table><tr><td>2</td><td>Stock Plan</td><td><a href="/Archives/edgar/data/123/000000012326000001/plan.htm">plan</a></td><td>EX-10.1</td></tr>
        <tr><td>1</td><td>Current report</td><td><a href="/ix?doc=/Archives/edgar/data/123/000000012326000001/report.htm">report</a></td><td>8-K</td></tr></table>'''
        ann = {'adsh': '0000000123-26-000001'}
        with patch.object(fetch, 'sec_get', side_effect=[index.encode(), b'<p>The spin-off has been completed.</p>']) as get:
            text = fetch.fetch_8k_text('123', ann['adsh'], None, ann)
        self.assertIn('completed', text)
        self.assertTrue(get.call_args.args[0].endswith('/report.htm'))
        self.assertEqual(ann['primaryDocument'], 'report.htm')

    def test_document_history_retains_prior_proof_and_terminal_categories(self):
        import fetch_spinoff_us, fetch_spinoff
        first = {'url': 'https://example.org/old.pdf', 'status': 'completed'}
        later = {'url': 'https://example.org/new.pdf', 'status': 'announced'}
        self.assertEqual(merge_evidence([first], []), [first])
        self.assertEqual(merge_evidence([first], [later]), [first, later])
        rows = [{'status': 'terminated'}, {'status': 'completed'}]
        self.assertEqual(fetch_spinoff_us.filter_status(rows), rows)
        self.assertEqual(fetch_spinoff.filter_status_driven(rows), rows)

    def test_generic_ipo_and_debt_exchange_do_not_reclassify_spinoff(self):
        import fetch_spinoff_us as fetch
        self.assertEqual(fetch.classify_type('The spin-off was announced. The parent had an initial public offering in 1990.'), 'spinoff')
        self.assertEqual(fetch.classify_type('An exchange offer of senior notes.'), 'spinoff')
        self.assertEqual(fetch.classify_type('The equity carve-out of a subsidiary.'), 'carveout')
        self.assertEqual(fetch.classify_type('The split-off of its business.'), 'splitoff')

    def test_headline_target_does_not_inherit_another_fosun_business(self):
        ann = {'title': '建議分拆CLUBMED LIFESTYLE並於香港聯交所主板獨立上市', 'date': '2026-08-28', 'docUrl': '/listedco/clubmed.pdf'}
        proof = parse_evidence(ann['title'], ann)
        self.assertEqual(proof['targetName'], 'CLUBMED LIFESTYLE')
        self.assertEqual(extract_name('建議分拆獲聯交所批准兹提述中國海外發展有限公司'), '')

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

class AutomaticIdentityTests(unittest.TestCase):
    def test_headline_order_and_business_label(self):
        from spinoff_identity import resolve_identity
        for title, expected in [
            ('內幕消息：PROBIO TECHNOLOGY LIMITED建議分拆及獨立上市','PROBIO TECHNOLOGY LIMITED'),
            ('華潤新能源控股有限公司建議分拆及A股上市之最新情況','華潤新能源控股有限公司'),
            ('建議分拆卡松科技於全國中小企業股份轉讓系統掛牌之進展','卡松科技'),
        ]:
            self.assertEqual(resolve_identity('',title)['name'],expected)
        business=resolve_identity('','內幕消息 光伏業務擬分立獨立上市')
        self.assertEqual(business['name'],'光伏業務')
        self.assertEqual(business['kind'],'business')

    def test_alias_and_parenthetical_separation(self):
        from spinoff_identity import resolve_identity
        text='Teyame AI Holdings, Inc. (“Teyame”), a subsidiary. The planned spin-off of Teyame from the Company.'
        self.assertEqual(resolve_identity(text)['name'],'Teyame AI Holdings, Inc')
        text='The separation (the “Spin-Off”) of Versigent Limited (“Versigent”) from the Company.'
        self.assertEqual(resolve_identity(text)['name'],'Versigent Limited')

    def test_self_filing_child_is_kept_only_with_distribution_evidence(self):
        ann={'date':'2026-06-15','url':'https://www.sec.gov/Archives/edgar/data/123/filing.htm'}
        text='Child Technologies Inc. (the “Company”), a subsidiary of Parent Inc. Parent will distribute all of the issued shares of Company common stock to holders of record of Parent common stock in the spin-off.'
        proof=parse_evidence(text,ann)
        result=normalize({'companies':[{'ticker':'C','name':'Child Technologies Inc.','announcements':[ann],'filingEvidence':[proof]}]},'us')
        self.assertEqual(result['events'][0]['targetName'],'Child Technologies Inc')
        self.assertTrue(result['events'][0]['identityVerified'])
        self.assertEqual(result['events'][0]['identityEvidence']['url'],ann['url'])

    def test_ambiguous_entities_and_compensation_not_filled(self):
        from spinoff_identity import resolve_identity
        result=resolve_identity('The spin-off of Alpha Inc. and the separation of Beta Inc.')
        self.assertEqual(result['name'],'')
        self.assertEqual(result['reason'],'conflicting_names')
        self.assertEqual(resolve_identity('Alpha Inc. (the “Company”). The Plan adjusts awards for a stock split, recapitalization or spin-off.')['name'],'')
        # A conditional definition must not capture the next definition-table row.
        self.assertEqual(resolve_identity('「分拆公司」 指 (i) 目標公司或其他公司 「目標公司」 指電子商務發展有限公司')['name'],'')

    def test_full_name_resolution_preserves_watch_identity_and_is_idempotent(self):
        ann={'date':'2026-06-15','url':'https://www.sec.gov/Archives/edgar/data/123/filing.htm'}
        first=normalize({'companies':[{'ticker':'P','name':'Parent','announcements':[ann], 'filingEvidence':[{'url':ann['url'],'date':ann['date'],'status':'announced','quote':'The company plans a spin-off.'}]}]},'us')
        updated=copy.deepcopy(first)
        updated['companies'][0]['filingEvidence']=[parse_evidence('The company plans a spin-off of Child Inc.',ann)]
        updated=normalize(updated,'us',previous=first)
        self.assertEqual(updated['events'][0]['id'],first['events'][0]['id'])
        again=normalize(copy.deepcopy(updated),'us')
        self.assertEqual(again['changes'],updated['changes'])

    def test_name_from_attachment_survives_shallow_reread(self):
        old={'url':'https://www.sec.gov/Archives/report.htm','targetName':'Child Inc','identityVersion':1,'identityQuote':'The spin-off of Child Inc.','identitySourceUrl':'https://www.sec.gov/Archives/ex99.htm'}
        new={'url':old['url'],'targetName':'','identityVersion':1,'status':'announced'}
        merged=merge_evidence([old],[new])[0]
        self.assertEqual(merged['targetName'],'Child Inc')
        self.assertEqual(merged['identitySourceUrl'],old['identitySourceUrl'])
        self.assertEqual(merged['status'],'announced')

    def test_success_is_cached_and_failure_is_retryable(self):
        from resolve_spinoff_names import refresh_company
        ann={'date':'2026-01-01','title':'建議分拆甲乙有限公司於香港上市','docUrl':'/listedco/one.pdf'}
        company={'stockCode':'00123','announcements':[ann]}
        with patch('resolve_spinoff_names.document',side_effect=OSError('offline')):
            _,errors=refresh_company(company,'hk',None)
        self.assertEqual(len(errors),1)
        self.assertEqual(company['identityChecks'],{})
        with patch('resolve_spinoff_names.document',return_value={'text':ann['title']}) as read:
            refresh_company(company,'hk',None)
            refresh_company(company,'hk',None)
        self.assertEqual(read.call_count,1)
        self.assertEqual(company['filingEvidence'][0]['targetName'],'甲乙有限公司')

    def test_dated_reference_requires_unambiguous_target(self):
        from resolve_spinoff_names import link_references
        update={'date':'2026-03-01','identityReferences':['2026-02-01']}
        old={'date':'2026-02-01','targetName':'Child Inc','url':'https://www.sec.gov/Archives/a.htm','identityQuote':'spin-off of Child Inc.'}
        self.assertEqual(link_references([dict(update),old])[0]['targetName'],'Child Inc')
        conflict={**old,'targetName':'Other Inc'}
        self.assertFalse(link_references([dict(update),old,conflict])[0].get('targetName'))

    def test_legacy_sec_url_recovered_only_for_unique_same_date_filing(self):
        import json
        from resolve_spinoff_names import recover_sec_announcements
        ann={'date':'2026-06-01','url':'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=123'}
        c={'cik':'123','announcements':[ann]}
        table={'filingDate':['2026-06-01'],'form':['8-K'],'accessionNumber':['0000000123-26-000001'],'primaryDocument':['report.htm']}
        with patch('resolve_spinoff_names.read_url',return_value=json.dumps({'filings':{'recent':table}}).encode()):
            recover_sec_announcements(c,None)
        self.assertEqual(ann['adsh'],'0000000123-26-000001')
        self.assertTrue(ann['url'].endswith('/report.htm'))

    def test_advisors_and_broken_legal_names_are_rejected(self):
        from spinoff_identity import resolve_identity
        from spinoff_events import clean_name
        text='分拆所属子公司江西省江铜铜箔科技股份有限公司。分拆独立财务顾问中国国际金融股份有限公司。'
        self.assertEqual(resolve_identity(text)['name'],'江西省江铜铜箔科技股份有限公司')
        self.assertEqual(clean_name('）生物製藥股份有限公司'),'')

    def test_reference_chain_upgrades_business_name_without_crossing_entities(self):
        from resolve_spinoff_names import link_references
        old={'url':'https://example.org/a.pdf','date':'2026-01-01','targetName':'Child Inc','identityKind':'entity','identityQuote':'spin-off of Child Inc.'}
        middle={'url':'https://example.org/b.pdf','date':'2026-02-01','identityReferences':['2026-01-01']}
        latest={'url':'https://example.org/c.pdf','date':'2026-03-01','targetName':'光伏業務','identityKind':'business','identityReferences':['2026-02-01']}
        out=link_references([latest,middle,old])
        self.assertEqual(out[0]['targetName'],'Child Inc')
        self.assertIn('光伏業務',out[0]['targetAliases'])
        self.assertEqual(out[0]['identitySourceUrl'],old['url'])

    def test_simplified_and_traditional_names_have_same_identity(self):
        from spinoff_events import target_key
        self.assertEqual(target_key('中車戚墅堰機車車輛工藝研究所股份有限公司'),target_key('中车戚墅堰机车车辆工艺研究所股份有限公司'))
        self.assertEqual(target_key('Vylor, Inc.'),target_key('Vylor Inc'))

    def test_conflicting_new_identity_does_not_reuse_old_name(self):
        before={'url':'https://example.org/a.pdf','targetName':'Alpha Inc','identityVersion':1}
        after={'url':before['url'],'targetName':'','identityVersion':1,'identityReason':'conflicting_names'}
        self.assertFalse(merge_evidence([before],[after])[0]['targetName'])

    def test_reference_identity_survives_next_daily_fetch(self):
        from resolve_spinoff_names import link_references
        origin={'url':'https://example.org/old.pdf','date':'2026-01-01','targetName':'Child Inc','identityKind':'entity','identityQuote':'spin-off of Child Inc.','identityVersion':1}
        latest={'url':'https://example.org/new.pdf','date':'2026-02-01','identityVersion':1,'identityReferences':['2026-01-01']}
        history=link_references([origin,latest])
        shallow={**latest,'targetName':'光伏業務','identityKind':'business','identityReason':''}
        shallow.pop('identityReferences')
        refreshed=link_references(merge_evidence(history,[shallow]))
        self.assertEqual(refreshed[1]['targetName'],'Child Inc')
        self.assertEqual(refreshed[1]['identityReferences'],['2026-01-01'])
