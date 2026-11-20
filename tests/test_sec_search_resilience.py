import io
import json
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
import fetch_spinoff_us as sec


class SearchResilienceTests(unittest.TestCase):
    def http_error(self,code,headers=None):
        return HTTPError('https://www.sec.gov/test',code,'synthetic',headers or {},None)

    def test_transient_server_error_retries_and_closes_response(self):
        response=io.BytesIO(b'original source');opener=Mock()
        opener.open.side_effect=[self.http_error(500),response]
        with patch.object(sec.time,'sleep'):
            self.assertEqual(sec.sec_get('https://www.sec.gov/test',opener),b'original source')
        self.assertEqual(opener.open.call_count,2);self.assertTrue(response.closed)

    def test_retry_limit_and_permanent_denial(self):
        for code,expected in [(503,3),(403,1),(404,1)]:
            with self.subTest(code=code),patch.object(sec.time,'sleep'):
                opener=Mock();opener.open.side_effect=self.http_error(code)
                with self.assertRaises(HTTPError):sec.sec_get('https://www.sec.gov/test',opener)
                self.assertEqual(opener.open.call_count,expected)

    def test_retry_after_cannot_create_an_unbounded_sleep(self):
        opener=Mock();opener.open.side_effect=[self.http_error(429,{'Retry-After':'inf'}),io.BytesIO(b'ok')]
        with patch.object(sec.time,'sleep') as sleep:
            self.assertEqual(sec.sec_get('https://www.sec.gov/test',opener),b'ok')
        self.assertTrue(all(0<=c.args[0]<=60 for c in sleep.call_args_list))

    def test_timeout_retries_read_only_request(self):
        opener=Mock();opener.open.side_effect=[TimeoutError(),io.BytesIO(b'ok')]
        with patch.object(sec.time,'sleep'):
            self.assertEqual(sec.sec_get('https://www.sec.gov/test',opener),b'ok')
        self.assertEqual(opener.open.call_count,2)

    def test_interrupted_second_page_retains_first_page_and_is_not_complete(self):
        hits=[{'_source':{'ciks':['000123'],'display_names':['Example (EX)'],'adsh':str(i),'file_date':'2026-11-19'}} for i in range(40)]
        first=json.dumps({'hits':{'total':{'value':80},'hits':hits}}).encode()
        with patch.object(sec,'sec_get',side_effect=[first,URLError('offline')]),patch.object(sec,'record_source_warning') as warning:
            result=sec.search_edgar(None,'synthetic query')
        self.assertEqual(len(result),40);self.assertFalse(result.complete);warning.assert_called_once()

    def test_true_empty_result_is_complete_but_malformed_success_is_not(self):
        for payload,complete in [({'hits':{'total':{'value':0},'hits':[]}},True),({},False),({'hits':{'total':{'value':5},'hits':[]}},False)]:
            with self.subTest(payload=payload),patch.object(sec,'sec_get',return_value=json.dumps(payload).encode()),patch.object(sec,'record_source_warning') as warning:
                result=sec.search_edgar(None,'synthetic query')
                self.assertEqual(result.complete,complete);self.assertEqual(warning.called,not complete)

    def test_incomplete_search_cannot_retire_unseen_old_events(self):
        current=[{'ticker':'NEW','announcements':[]}]
        old={'OLD':{'ticker':'OLD','announcements':[{'date':'2020-01-01'}]},'NEW':{'ticker':'NEW','old':True}}
        self.assertEqual(len(sec.retain_previous(current,old,'2025-01-01',complete=True)),1)
        retained=sec.retain_previous(current,old,'2025-01-01',complete=False)
        self.assertEqual([c['ticker'] for c in retained],['NEW','OLD']);self.assertNotIn('old',retained[0])

    def test_all_failed_queries_cannot_write_a_replacement_dataset(self):
        result=sec.SearchResults();result.complete=False
        with patch.object(sec,'_load_prev_us',return_value={'OLD':{'ticker':'OLD'}}),patch.object(sec,'search_edgar',return_value=result),patch('builtins.open') as write:
            with self.assertRaisesRegex(RuntimeError,'refusing to overwrite'):sec.main()
        write.assert_not_called()

    def test_short_pages_advance_by_actual_results_without_skipping_filings(self):
        hit=lambda i:{'_source':{'ciks':['000123'],'display_names':['Example (EX)'],'adsh':str(i),'file_date':'2026-11-19'}}
        pages=[json.dumps({'hits':{'total':{'value':2},'hits':[hit(i)]}}).encode() for i in range(2)]
        with patch.object(sec,'sec_get',side_effect=pages) as request:
            results=sec.search_edgar(None,'synthetic query')
        self.assertEqual(len(results),2);self.assertTrue(results.complete)
        self.assertIn('from=1&',request.call_args_list[1].args[0])
