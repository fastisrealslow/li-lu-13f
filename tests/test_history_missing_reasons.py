import unittest
from pathlib import Path
from legacy_13f import fixed_width_tables
from trade_price_history import calculate

class HistoricalIdentitySafety(unittest.TestCase):
    def test_original_sec_wrapping_does_not_contaminate_neighbor(self):
        source=Path('tests/fixtures/pabrai-2011-q4-wrapped-excerpt.txt').read_text()
        rows={h['cusip']:h for h in fixed_width_tables(source)}
        self.assertEqual(rows['084670207']['name'],'Berkshire Hathaway')
        self.assertEqual(rows['11283W104']['name'],'Brookfield Residential Properties, Inc.')
        self.assertEqual(rows['38141GDG6']['name'],'Goldman Sachs Group Inc.')
        self.assertNotIn('38141G104',rows) # Never repair identifiers by guessing common stock.
        self.assertEqual(rows['11283W104']['shares'],226155)
        self.assertEqual(rows['084670207']['value'],33949000)

    def test_original_suffix_layout_still_attaches_to_previous_issuer(self):
        rows={h['cusip']:h for h in fixed_width_tables(Path('tests/fixtures/legacy_wrapped_issuers.txt').read_text())}
        self.assertEqual(rows['22282E102']['name'],'Covanta Holding Corporation')
        self.assertEqual(rows['Y2685T107']['name'],'Genco Shipping & Trading Ltd.')
        self.assertEqual(rows['913837100']['name'],'Universal Stainless & Alloy, Inc.')

    def test_reporting_boundary_cannot_inherit_legacy_cost_or_net_trade(self):
        rows={'2011 Q4':{'shares':100},'2012 Q1':{'shares':80}}
        got=calculate(rows,{'2011 Q4':{'buy':1},'2012 Q1':{'buy':10,'sell':20}},boundary='2012 Q1')
        self.assertEqual(got['averageBuy'],10)
        self.assertIsNone(got['averageSell'])
        self.assertEqual(got['quarters'][0]['action'],'observed')

    def test_indented_next_issuer_never_steals_an_explicit_prior_suffix(self):
        original=Path('tests/fixtures/legacy_wrapped_issuers.txt').read_text()
        # Move only the next name, not its class/CUSIP/financial columns.
        raw=original.replace('Dr. Reddys Labs Ltd        ADR',' Dr. Reddys Labs Ltd       ADR')
        raw=raw.replace('Harvest Nat Res Inc.       COM',' Harvest Nat Res Inc.      COM')
        rows={h['cusip']:h for h in fixed_width_tables(raw)}
        self.assertEqual(rows['22282E102']['name'],'Covanta Holding Corporation')
        self.assertEqual(rows['256135203']['name'],'Dr. Reddys Labs Ltd')
        self.assertEqual(rows['Y2685T107']['name'],'Genco Shipping & Trading Ltd.')
        self.assertEqual(rows['41754V103']['name'],'Harvest Nat Res Inc.')
