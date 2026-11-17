# Source-bound historical price segments

Earlier filing scopes are not the current manager's acquisition ledger. `costHistoryFrom` and reporting-scope guards remain in force. `historicalSegments` is a separate, lazy history presentation; no segment contributes to the top-level averages or `costBasis`.

Eligibility requires all of:
- Original SEC filing URL bound to its CIK and quarter-end report date.
- Reconciled original counts and monetary total, with zero difference.
- Dated CUSIP, symbol and common-share-class evidence in `historical_security_identities.json`. A directory/name match alone is insufficient.
- For fixed-width legacy forms, an independently reviewed original row with exact accession, CIK, quarter, name, class, CUSIP, shares, value and instrument fields. A parser version is not an identity audit. A reviewed row does not certify neighboring rows or an absent position.
- The live historical series' symbol, issuer and currency match the reviewed class. Corporate-action history covers the segment start; non-pure-split and existing value-quality exclusions continue to block incompatible quarters.

Every CIK change, missing/unverified quarter, or reporting boundary starts a separate segment. The first position is `observed`, not an inferred purchase. Weighted averages are never combined across segments. The generic bounded downloader receives eligible segment quarters through its existing queue and caches; no new unbounded network job is introduced.

## Verified example (17 November 2026)

BAC / CUSIP 060505104:
- SEC 2010 proxy-voting report explicitly binds BAC and 060505104; the 2026 Q2 SEC table identifies Bank of America (BAC), COM, with the same CUSIP. URLs are retained in the registry.
- Pabrai's 2011 Q4 original row reports 2,135,986 shares and USD 11,876,000 (11,876 in thousands). That exact row was independently reviewed. The stored parser remains version 6; no version or portfolio data was rewritten to create eligibility.
- A real Yahoo historical-series retrieval on 17 November 2026 covered 63 trading days in 2011 Q4. The separate reporter CIK 1173334 buy reference was 5.2211 USD. The existing 2012-onward top-level BAC buy average stayed 6.3133 USD. No sale was inferred.

These are the site's existing low/mean/high-based estimates, not actual execution prices or a claim about the manager's true cost. The example is a local read-only verification; this change does not ship rewritten production portfolio or price JSON. Other pre-boundary records without sufficient evidence stay unavailable.

## Regression coverage

`tests/test_historical_price_segments.py` verifies original-row identity binding, class rejection, period/CIK/reconciliation, independent scopes, discontinuities, company-action coverage, bounded queue participation, and lazy snapshot preservation. `tests/test_historical_price_segments.cjs` verifies separate UI labeling and HTML/link safety.

## Verified symbol projection and real Ferrari example

`verified_security_symbols.json` binds an exact CUSIP, common-share class, issuer name and effective date to a symbol. The original reported identity is retained. Python and browser projections share the registry; regenerate the small browser asset with `python3 verified_security_symbols.py` when changing evidence. Tests reject divergent generated assets and compare all 17 investor projections. If the browser asset is unavailable, unknown symbols remain unknown rather than breaking the page.

Ferrari's issuer SEC announcement (https://www.sec.gov/Archives/edgar/data/1605484/000160548416000106/exhibit991nv1-4x16.htm) confirms NYSE RACE common shares and new CUSIP N3167Y103 from 2016-01-04. The predecessor N3167J106 and special voting shares are not interchangeable. A future corporate action or successor class requires new evidence; effectiveDate is not proof that every future identity change is safe.

A real free Yahoo response contained 2,734 daily observations starting on 2016-01-04. An offline replay with socket connections blocked filled Pabrai's five trade-reference quarters: 2016 Q1/Q2/Q3/Q4 and 2018 Q3. Buy reference 34.2716 USD, sale reference 79.3575 USD; missing buy/sale quarters 1/4 became 0/0. These remain estimates, not transactions. Pabrai's priced buy/sale ledger entries each increased 22 to 23 and quoted entries 31 to 32 in the dry run. The source portfolio and price files were byte-for-byte unchanged. Latest response quote: 404.77 USD, original trading timestamp 1794862802 (2026-11-16). This is a timestamped validation result, not a promise of a real-time price.

No production data JSON is shipped by this change. After an authorized deployment and the existing bounded updater run, validate the generated historical ledger and the actual Cloudflare website before claiming the backfill is live. Other unresolved mappings, ambiguous legacy rows, and unavailable source prices remain unavailable.
