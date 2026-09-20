import json
import unittest
from unittest.mock import patch
import fetch_13f_all as fetch


def filing(q):
    return dict(accession=f'2019{q}',accessionDashed=f'2019-{q}',reportDate=f'2019-{q*3:02d}-30',filingDate='2019-11-14')


def data():
    return {'history':{'quarters':['2018 Q3','2019 Q4'],'values':[10,420], 'holdings':{}}}


def table():
    return f'<informationTable xmlns="{fetch.NS["ns"]}"><infoTable><nameOfIssuer>APPLE INC</nameOfIssuer><value>1234</value><shrsOrPrnAmt><sshPrnamt>100</sshPrnamt></shrsOrPrnAmt></infoTable></informationTable>'.encode()


class BackfillTests(unittest.TestCase):
    def test_archive_index_is_read_sorted_and_deduplicated(self):
        current={'form':['13F-HR'],'accessionNumber':['new'],'filingDate':['2026-08-14'],'reportDate':['2026-06-30']}
        archive={'form':['13F-HR','8-K','13F-HR'],'accessionNumber':['old','ignore','new'],'filingDate':['2019-05-14','2019-01-01','2026-08-14'],'reportDate':['2019-03-31','','2026-06-30']}
        meta={'filings':{'recent':current,'files':[{'name':'CIK0001709323-submissions-001.json'}]}}
        with patch.object(fetch,'sec_fetch',side_effect=[json.dumps(meta).encode(),json.dumps(archive).encode()]) as get:
            result=fetch.get_recent_filings('1709323',include_archives=True)
        self.assertEqual([f['accession'] for f in result],['new','old'])
        self.assertEqual(get.call_args_list[-1].args[0],'submissions/CIK0001709323-submissions-001.json')

    def test_actual_lilu_missing_quarters(self):
        self.assertEqual(fetch.missing_history_quarters(data()),['2018 Q4','2019 Q1','2019 Q2','2019 Q3'])

    def test_backfill_uses_dated_filing_units_and_records_source(self):
        d=data()
        with patch.object(fetch,'get_recent_filings',return_value=[filing(1)]), patch.object(fetch,'find_info_table_xml',return_value='/Archives/table.xml'), patch.object(fetch,'sec_fetch',return_value=table()):
            fetch.backfill_history_gaps('1709323',d,[])
        self.assertEqual(d['history']['holdings']['2019 Q1'][0]['value'],1234000)
        self.assertEqual(d['history']['filing_sources']['2019 Q1']['filingDate'],'2019-11-14')
        self.assertNotIn('2019 Q1',d['history']['coverage']['missingQuarters'])
        self.assertIn('2018 Q4',d['history']['coverage']['errors'])

    def test_fetch_failure_keeps_gap_and_later_run_retries(self):
        d=data()
        with patch.object(fetch,'get_recent_filings',return_value=[filing(1)]), patch.object(fetch,'find_info_table_xml',return_value='/Archives/table.xml'), patch.object(fetch,'sec_fetch',side_effect=OSError('outage')):
            fetch.backfill_history_gaps('1709323',d,[])
        self.assertNotIn('2019 Q1',d['history']['quarters'])
        self.assertIn('outage',d['history']['coverage']['errors']['2019 Q1'])
        with patch.object(fetch,'get_recent_filings',return_value=[filing(1)]), patch.object(fetch,'find_info_table_xml',return_value='/Archives/table.xml'), patch.object(fetch,'sec_fetch',return_value=table()):
            fetch.backfill_history_gaps('1709323',d,[])
        self.assertIn('2019 Q1',d['history']['quarters'])

    def test_empty_table_is_not_a_zero_portfolio(self):
        d=data()
        with patch.object(fetch,'get_recent_filings',return_value=[filing(1)]), patch.object(fetch,'find_info_table_xml',return_value='/Archives/table.xml'), patch.object(fetch,'sec_fetch',return_value=b'<empty/>'):
            fetch.backfill_history_gaps('1709323',d,[])
        self.assertNotIn('2019 Q1',d['history']['quarters'])
        self.assertIn('Empty information table',d['history']['coverage']['errors']['2019 Q1'])

    def test_complete_range_does_not_fetch_archives(self):
        d={'history':{'quarters':['2026 Q1','2026 Q2'],'values':[1,2]}}
        with patch.object(fetch,'get_recent_filings') as get, patch.object(fetch,'sec_fetch') as request:
            fetch.backfill_history_gaps('1709323',d,[])
        get.assert_not_called();request.assert_not_called()
        self.assertEqual(d['history']['coverage']['missingQuarters'],[])
