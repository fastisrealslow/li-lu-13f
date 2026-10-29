# Complete historical research — 2026-10-29

The history download retains all quarters and all historical securities. A
current-screen Top 50 limit affects only current holdings and that screen's
comparisons. Greenblatt's history retains 63 filings / 65,845 source rows /
4,600 legal identities; 2010 Q4 retains all 358 securities, not six survivors.
It is gzip-compressed and fetched only when History is opened. Tables are
bounded: security data 24 quarters/page, complete portfolios 50 rows/page,
concentration 24 quarters/page, and the timeline 200 identities/page. Searching
covers the full dataset before pagination.

The History explorer offers:

- All historic securities, including positions no longer disclosed: search by
  ticker, issuer, CUSIP and class; choose a range and shares/principal, weight or
  filed-value chart. The same model supplies chart points and exact table rows.
- Any historical complete portfolio: rank, shares, value, weight, adjacent
  quarter share changes, disclosure status, sorting, filtering and pagination.
  Prior positions absent in a filed quarter appear as no longer disclosed.
- Complete-filing Top3/Top5 concentration over time with historical leaders,
  source tables and scope-aware adjacent-quarter changes.
- Filed source links, legal class and identifier, reported-identity corrections,
  manager allocation lines, discretion and voting authority when collected.

A missing report is unknown, not a zero portfolio. A filed report without a
security produces a disclosed absence (zero for that security). Value-excluded
quarters such as Hawkins 2024 Q3 retain their share records while values,
weights, concentration and ranks remain unverified. Webb's unverified history
is not graphed. Cross-manager scope transitions and split/action quarters do
not produce unsupported net-trade claims. Source snapshots cannot establish
personal trading instructions, net purchases or an investment return.

Li Lu's GOOGL example is reproducible by choosing 2024 Q3–2026 Q2: eight
quarters at 2,543,300 shares, with weight moving from 17.06% to 24.55%. PDD's
4,608,000→10,761,119 is reported share growth, distinguished from weight drift.
Timeline latest-filing status is always shown separately from historical
reappearance events. First/last dates are disclosure dates; nonzero sub-1%
peak-share ratios retain a decimal or <0.1%.

## Source-bound lifecycle evidence

Google class C (`38259P706`) before 2015 Q4 and Alphabet class C (`02079K107`)
from 2015 Q4 are linked economically using the 1:1 holding-company conversion
of 2015-10-02. The source rows and legal CUSIPs remain intact; the transition is
an explicit event, not a fabricated exit/reentry or a silent alias replacement.
It does not link class A, options, warrants or principal instruments.

- Nasdaq: https://www.nasdaqtrader.com/TraderNews.aspx?id=dtn2015-21
- SEC: https://www.sec.gov/Archives/edgar/data/1288776/000119312515336550/d56649d8k.htm

Only Pabrai's exact 2016 Q3 Berkshire class B, SH, non-option, 47,400-share row
with reported CUSIP `84670702` is corrected in a derived projection to
`084670702`, retaining `reportedIdentity` and a source-scoped correction record:
https://www.sec.gov/Archives/edgar/data/1549575/000154957516000021/infotable.xml
No general eight-character CUSIP padding is performed.

The SEC XML parser now preserves investmentDiscretion and votingAuthority
Sole/Shared/None on each source allocation. Missing historic fields remain
uncollected; no bulk network backfill was attempted without cached original
tables. Mixed discretion lines remain separate instead of inventing one code.
Original financial JSON and shares/values are not rewritten.

Deterministic Python facts and browser summaries derive from filing numbers.
No new paid model calls or model workflows are required. Model and rendering
regressions cover all 17 datasets, totals, complete Greenblatt history, gaps,
class/tool separation, lifecycle boundaries, pagination and a large-data timing
budget. Browser QA covers range/metric switching, sorting/search, repeated
pagination, investor switching and a mobile viewport.
