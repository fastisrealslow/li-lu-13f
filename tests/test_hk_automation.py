"""Regression cases from HKEX public HTML, including the 2017 archive split."""
import json
from contextlib import chdir
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit, parse_qs

import hk_disclosures as hk

FIXTURES = Path(__file__).parent / 'fixtures' / 'hkex'
ALIASES = ['Li Lu', 'Himalaya Capital Investors, L.P.']
LIST = hk.BASE + 'NSNoticePersonList.aspx?scpid1=35238&scpid2=142788&scpid3=2'
HIT = {'noticeUrl': LIST, 'entity': 'Li Lu', 'stockName': 'PSBC'}


def fixture(name):
    return (FIXTURES / (name + '.html')).read_text()


class FixtureClient:
    def __init__(self, fail_form=False):
        self.calls = []
        self.fail_form = fail_form

    def get(self, url):
        self.calls.append(url)
        if 'NSForm' in url:
            if self.fail_form:
                raise OSError('fixture unavailable')
            return fixture('psbc_form')
        return fixture('lilu_psbc_notices')


class HKAutomationTests(unittest.TestCase):
    def test_exact_entity_identity_excludes_similar_people(self):
        hits, total, _ = hk.parse_search(fixture('lilu_search'), hk.BASE+'NSSrchPersonList.aspx', ALIASES)
        self.assertEqual(len(hits), 3)
        self.assertGreater(total, len(hits))
        self.assertEqual({h['entity'] for h in hits}, {'Li Lu'})
        self.assertFalse(hk.entity_matches('Li Luqiang', ALIASES))
        self.assertTrue(hk.entity_matches('Himalaya Capital Investors, L.P. (formerly known as LL Investment Partners, L.P.)', ALIASES))

    def test_webb_does_not_include_spouse(self):
        hits, _, _ = hk.parse_search(fixture('webb_search'), hk.BASE+'NSSrchPersonList.aspx', ['Webb David Michael'])
        self.assertEqual(len(hits), 28)
        self.assertEqual({h['entity'] for h in hits}, {'WEBB DAVID MICHAEL'})

    def test_notice_uses_post_event_holding_not_transaction(self):
        records, total, _, rejected = hk.parse_notices(fixture('lilu_psbc_notices'), LIST)
        self.assertFalse(rejected)
        self.assertEqual(len(records), total)
        latest = records[0]
        self.assertEqual(latest['event_date'], '2025-05-08')
        self.assertEqual(latest['shares'], 985618000)
        self.assertNotEqual(latest['shares'], 10387000)
        self.assertEqual(latest['pct'], 4.96)

    def test_modern_and_legacy_forms(self):
        cases = [('psbc_form', hk.BASE, '01658.HK', 985618000, '2025-05-08'),
                 ('psbc_corporate', hk.BASE, '01658.HK', 1274411000, '2021-01-15'),
                 ('byd_legacy_form', hk.LEGACY, '01211.HK', 57404700, '2014-12-18')]
        for name, base, ticker, shares, event in cases:
            with self.subTest(name=name):
                r = hk.parse_form(fixture(name), base+'NSForm1.aspx', ALIASES)
                self.assertEqual((r['ticker'], r['shares'], r['event_date']), (ticker, shares, event))
                self.assertNotEqual(r['filing_date'], r['event_date'])

    def test_form_requires_trusted_source_and_correct_entity(self):
        with self.assertRaises(ValueError):
            hk.parse_form(fixture('psbc_form'), 'https://example.com/NSForm1.aspx', ALIASES)
        with self.assertRaises(ValueError):
            hk.parse_form(fixture('psbc_form'), hk.BASE+'NSForm1.aspx', ['Li Luqian'])

    def test_unknown_page_is_failure_not_zero(self):
        with self.assertRaises(ValueError):
            hk.parse_search('<html>Service unavailable</html>', hk.BASE+'NSSrchPersonList.aspx', ALIASES)
        hits, total, pages = hk.parse_search('<p>No records found</p>', hk.BASE+'NSSrchPersonList.aspx', ALIASES)
        self.assertEqual((hits, total, pages), ([], 0, []))

    def test_only_long_positions_and_valid_dates(self):
        self.assertEqual(hk.long_number('1,234 (L) 98 (S)', True), 1234)
        for bad in ['98 (S)', '-', '1.5 (L)', '1 (L) 2 (L)']:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                hk.long_number(bad, True)
        with self.assertRaises(ValueError):
            hk.dated('31/02/2025')

    def test_binding_checks_notice_against_original_form(self):
        client = FixtureClient()
        records, binding, errors = hk.crawl_notices(client, HIT, ALIASES, [])
        self.assertFalse(errors)
        self.assertTrue(binding['history_complete'])
        self.assertEqual(binding['ticker'], '01658.HK')
        self.assertTrue(all(r['ticker'] == '01658.HK' for r in records))
        bad = FixtureClient()
        original = bad.get
        bad.get = lambda url: original(url).replace('985,618,000', '985,618,001') if 'NSForm' in url else original(url)
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            hk.crawl_notices(bad, HIT, ALIASES, [])

    def test_verified_binding_can_be_reused_without_refetching_form(self):
        records, binding, _ = hk.crawl_notices(FixtureClient(), HIT, ALIASES, [])
        client = FixtureClient(fail_form=True)
        again, _, _ = hk.crawl_notices(client, HIT, ALIASES, records, binding)
        self.assertEqual(len(again), len(records))
        self.assertFalse(any('NSForm' in u for u in client.calls))

    def test_notice_pagination_failure_is_partial(self):
        real_parse = hk.parse_notices
        def parsed(html, url):
            records, total, _, errors = real_parse(html, url)
            return records, total + 1, [LIST+'&pg=2'], errors
        client = FixtureClient()
        get = client.get
        def fail_page(url):
            if 'pg=2' in url:
                raise OSError('second page unavailable')
            return get(url)
        client.get = fail_page
        with patch.object(hk, 'parse_notices', side_effect=parsed):
            records, binding, errors = hk.crawl_notices(client, HIT, ALIASES, [])
        self.assertTrue(records)
        self.assertFalse(binding['history_complete'])
        self.assertIn('second page unavailable', str(errors))

    def test_pagination_preserves_search_identity(self):
        url = hk.BASE+'NSSrchPersonList.aspx?pn=Li+Lu&lang=EN'
        html = '<p>Total records: 60</p><a href="?pn=Li+Lu&lang=EN&pg=1">1</a><a href="?pn=Li+Lu&lang=EN&pg=2">2</a><a href="?pn=Other&lang=EN&pg=3">3</a>'
        _, pages = hk.page_info(hk.BeautifulSoup(html, 'html.parser'), url)
        self.assertEqual(len(pages), 1)
        self.assertEqual(parse_qs(urlsplit(pages[0]).query)['pg'], ['2'])

    def test_search_failure_preserves_verified_holdings(self):
        records, binding, _ = hk.crawl_notices(FixtureClient(), HIT, ALIASES, [])
        initial = {'holdings': [{'ticker':'01658.HK', 'evidence_schema':2, 'current_status':'unknown', 'verified_disclosures':records}]}
        class BrokenClient:
            def get(self, url):
                raise OSError('offline')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'hk.json'
            path.write_text(json.dumps(initial))
            inv = {'id':'test', 'hkFile':'hk.json', 'queries':['Li Lu'], 'entities':ALIASES}
            result = hk.run_investor(inv, directory, BrokenClient())
            output = json.loads(path.read_text())
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(output['holdings'][0]['verified_disclosures'], records)
        self.assertEqual(output['holdings'][0]['current_status'], 'unknown')
        self.assertEqual(result['verifiedSecurities'], 1)

    def test_all_investors_have_automatic_hk_coverage(self):
        configs = list(hk.load_configs('investors.json'))
        self.assertEqual(len(configs), 13)
        for inv in configs:
            self.assertTrue(inv['queries'])
            self.assertTrue(inv['entities'])
            self.assertTrue(Path(inv['hkFile']).exists())
        self.assertEqual(len({c['hkFile'] for c in configs}), 13)

    def test_webb_secondary_fetch_does_not_overwrite_official_evidence(self):
        import fetch_webb_holdings as webb
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'webb.json'
            path.write_text(json.dumps({'meta':{}, 'current':{'holdings':[], 'totalValue':0}}))
            hkpath = Path(directory)/'webb_hk.json'
            hkpath.write_text('official evidence')
            with patch.object(webb, 'WEBB_JSON', str(path)), chdir(directory):
                webb.update_webb_json([])
            self.assertEqual(hkpath.read_text(), 'official evidence')

    def test_publish_validation_rejects_bad_evidence(self):
        from validate_data import validate_hk_evidence
        record = hk.parse_form(fixture('psbc_form'), hk.BASE+'NSForm1.aspx', ALIASES)
        value = {'holdings':[{'ticker':'01658.HK','verified_disclosures':[record]}]}
        validate_hk_evidence(value)
        record['source_url'] = 'https://example.com/unverified'
        with self.assertRaises(ValueError):
            validate_hk_evidence(value)
