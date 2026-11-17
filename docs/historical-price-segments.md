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

## Cross-investor checks of already-correct symbols

Three further real-data replays on 2026-11-17 used existing mappings, without changing any holding, share count, action sequence, or production file. Each interval is within one reporter CIK and after its applicable cost boundary. Downloaded USD series matched the ticker/issuer and had no split events during the requested interval. These examples demonstrate available historical prices, not a deployment or permission to overwrite unknown identities.

| Investor / security | Missing buy/sale quarters, before → after | Buy / sale reference (USD) |
| --- | --- | --- |
| Klarman / VRSN / 92343E102 | 1/1 → 0/0 | 170.3901 / 188.1759 |
| Berkowitz / USB / 902973304 | 1/1 → 0/0 | 28.7847 / 39.2443 |
| Tepper / KMX / 143130102 | 1/4 → 0/0 | 87.4224 / 128.7291 |

Original filings and issuer identity evidence:
- VRSN: [2024 Q2 holding](https://www.sec.gov/Archives/edgar/data/1061768/000156761924000363/xslForm13F_X02/form13fInfoTable.xml), [2024 Q3 complete table](https://www.sec.gov/Archives/edgar/data/1061768/000106176824000005/xslForm13F_X02/BGLLCQ32024.xml), [issuer common-stock/CUSIP/ticker document](https://investor.verisign.com/static-files/83f6e7e5-17a1-4f47-aa2d-0c06a004d010). The 2011 action in the issuer document predates this 2024 interval.
- USB: [2023 Q2 holding](https://www.sec.gov/Archives/edgar/data/1056831/000091957423004811/xslForm13F_X02/infotable.xml), [2023 Q3 complete table](https://www.sec.gov/Archives/edgar/data/1056831/000091957423006407/xslForm13F_X02/infotable.xml), [issuer common USB versus preferred classes](https://www.sec.gov/Archives/edgar/data/36104/000003610426000011/usb-20251231.htm).
- KMX: [2020 Q4](https://www.sec.gov/Archives/edgar/data/1656456/000165645621000001/xslForm13F_X01/Form13FInfoTable.xml), [2021 Q1](https://www.sec.gov/Archives/edgar/data/1656456/000165645621000002/xslForm13F_X01/Form13FInfoTable.xml), [2021 Q2](https://www.sec.gov/Archives/edgar/data/1656456/000165645621000003/xslForm13F_X01/Form13FInfoTable.xml), [2021 Q3](https://www.sec.gov/Archives/edgar/data/1656456/000165645621000004/xslForm13F_X01/Form13FInfoTable.xml), [2021 Q4](https://www.sec.gov/Archives/edgar/data/1656456/000165645622000001/xslForm13F_X01/Form13FInfoTable.xml), [2022 Q1 complete table](https://www.sec.gov/Archives/edgar/data/1656456/000165645622000002/xslForm13F_X01/Form13FInfoTable.xml), [contemporaneous issuer ticker/class](https://www.sec.gov/Archives/edgar/data/1170010/000117001021000040/R1.htm).

A negative control remains unavailable: MOD's 2026-10-02 factor 1.086 is not a pure share split. The [issuer completion announcement](https://www.sec.gov/Archives/edgar/data/67347/000110465926112870/tm2626618d1_ex99-1.htm) confirms the Performance Technologies separation and Gentherm combination. Offline verification makes zero MOD historical requests and leaves the Q3 buy average null. A ready market price alone cannot resolve the distribution's cost allocation.
