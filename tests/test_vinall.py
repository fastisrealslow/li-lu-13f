import copy
import unittest

import fetch_13f_all as filings
import fetch_prices_all as prices
from holdings_diff import attach_previous, compare_holdings


class VinallTests(unittest.TestCase):
    def test_rv_configuration_and_current_security_identifiers(self):
        self.assertEqual(filings.INVESTOR_CONFIG['vinall']['cik'], '1766596')
        self.assertEqual(prices.INVESTOR_CONFIG['vinall']['prices'], 'prices_vinall.json')
        for cusip, ticker in [('146869102', 'CVNA'), ('45841N107', 'IBKR'),
                              ('244199105', 'DE'), ('617700109', 'MORN'),
                              ('70432V102', 'PAYC'), ('L8681T102', 'SPOT')]:
            self.assertEqual(filings.resolve_ticker('TRUNCATED ISSUER NAME', '', cusip), ticker)

    def test_confirmed_split_is_a_reduction_and_preserves_original_filing(self):
        current = [dict(ticker='CVNA', cusip='146869102', shares=1763296, value=116060143)]
        previous = [dict(ticker='CVNA', cusip='146869102', shares=377298, value=118818309)]
        original = copy.deepcopy(previous)
        attach_previous(current, previous, previous_quarter='2026 Q1', current_quarter='2026 Q2')
        row = current[0]
        self.assertEqual(row['prevShares'], 1886490)
        self.assertAlmostEqual((row['shares'] / row['prevShares'] - 1) * 100, -6.5303288117)
        self.assertEqual(row['shareAdjustment']['reportedShares'], 377298)
        self.assertEqual(previous, original)
        # AI and metadata recomparison use the persisted adjustment, too.
        self.assertEqual(compare_holdings(current, previous)[0]['prevShares'], 1886490)
        # The next report must not apply an old adjustment again.
        attach_previous(current, previous, previous_quarter='2026 Q2', current_quarter='2026 Q3')
        self.assertEqual(current[0]['prevShares'], 377298)
        self.assertNotIn('shareAdjustment', current[0])

    def test_cost_history_uses_comparable_shares_without_changing_market_values(self):
        history = {'2026 Q1': [dict(ticker='CVNA', shares=377298, value=118818309)],
                   '2026 Q2': [dict(ticker='CVNA', shares=1763296, value=116060143)]}
        original = copy.deepcopy(history)
        comparable = prices.comparable_price_history(history, '2026 Q2')
        self.assertEqual(comparable['2026 Q1'][0]['shares'], 1886490)
        self.assertEqual(comparable['2026 Q1'][0]['value'], 118818309)
        self.assertEqual(comparable['2026 Q2'][0]['shares'], 1763296)
        self.assertEqual(history, original)


if __name__ == '__main__':
    unittest.main()
