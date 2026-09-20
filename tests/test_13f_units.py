import unittest
from unittest.mock import patch
import validate_data
import fetch_13f_all as fetch
from holdings_diff import update_history


def table(values):
    rows = ''.join(f'<infoTable><nameOfIssuer>{name}</nameOfIssuer><titleOfClass>COM</titleOfClass><cusip>{name}</cusip><value>{value}</value><shrsOrPrnAmt><sshPrnamt>{shares}</sshPrnamt></shrsOrPrnAmt></infoTable>' for name, shares, value in values)
    return f'<informationTable xmlns="{fetch.NS["ns"]}">{rows}</informationTable>'.encode()


class ValueUnits(unittest.TestCase):
    def test_old_filing_with_expensive_share_uses_thousands(self):
        xml = table([('BRK.A', 1, 450), ('JOE', 26491533, 514466)])
        rows = fetch.parse_holdings(xml, filing_date='2022-11-14')
        self.assertEqual(sum(h['value'] for h in rows), 514916000)

    def test_new_filing_penny_stock_is_not_multiplied(self):
        rows = fetch.parse_holdings(table([('PENNY', 10000, 5000)]), filing_date='2023-01-03')
        self.assertEqual(rows[0]['value'], 5000)

    def test_old_report_filed_after_transition_uses_dollars(self):
        rows = fetch.parse_holdings(table([('OLD_REPORT', 100, 50)]), filing_date='2023-02-14')
        self.assertEqual(rows[0]['value'], 50)
        with self.assertRaises(ValueError):
            fetch.parse_holdings(table([]), filing_date='')

    def test_history_preserves_dollar_precision_and_replaces_existing(self):
        data = {'history': {'quarters': ['2020 Q1'], 'values': [6000], 'holdings': {}}}
        update_history(data, '2020 Q1', [{'value': 5657250123}])
        self.assertEqual(data['history']['values'], [5657.250123])
        self.assertEqual(data['history']['quarters'], ['2020 Q1'])

    def test_validator_rejects_bad_quarter_alignment_and_rounded_billions(self):
        for history in [
            {'quarters': ['2020 Q1'], 'values': []},
            {'quarters': ['2020 Q1', '2020 Q1'], 'values': [1, 1]},
            {'quarters': ['2020 Q1'], 'values': [float('nan')]},
            {'quarters': ['2020 Q1'], 'values': [6000], 'holdings': {'2020 Q1': [{'value': 5657250000}]}},
        ]:
            with self.assertRaises(ValueError):
                validate_data.validate_history(history)

    def test_full_refresh_replaces_cached_wrong_units(self):
        filings = [dict(accession='2', accessionDashed='2', reportDate='2022-06-30', filingDate='2022-08-14'),
                   dict(accession='1', accessionDashed='1', reportDate='2022-03-31', filingDate='2022-05-14')]
        data = {'meta': {}, 'history': {'quarters': ['2022 Q1', '2022 Q2'], 'values': [1, 2], 'holdings': {}}}
        config = {'cik':'1','path':'unused.json'}
        with patch.object(fetch, 'find_info_table_xml', return_value='/unused'), patch.object(fetch, 'sec_fetch', return_value=table([('JOE', 100, 2000)])), patch.object(fetch, 'save_data') as save, patch.object(fetch, 'warn_unmapped'):
            fetch.process_full('test', config, filings, data)
        self.assertEqual(data['history']['values'], [2, 2])
        self.assertEqual(data['history']['holdings']['2022 Q1'][0]['value'], 2000000)
        save.assert_called_once()

if __name__ == '__main__':
    unittest.main()
