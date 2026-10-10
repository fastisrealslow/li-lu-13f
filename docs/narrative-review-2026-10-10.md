# Readable disclosure summaries — 2026-10-10

The previous interpretation mainly listed counts, the largest holding and top-three concentration. It did not connect those figures, distinguish large changes from tiny ones, or explain why reported value could rise while shares fell. Generic investor-framework guidance also occupied the first reading position.

Each tab now starts with one concrete headline, a connected overview and up to three labeled explanations. Investor philosophy remains in the profile section. Scope and calculation notes are available in a closed disclosure beneath the summary; material data limitations remain explicit in the main text when they prevent analysis.

## What the summaries explain

- Holdings: the leading securities versus the rest of the portfolio, ordinary-share issuer concentration, sector composition and the actual aggregate size of small positions. Distinct share classes stay separate in the table; ordinary shares of the same CUSIP issuer can be combined for issuer concentration. Options are excluded from that grouping and never netted against shares. The grouping follows the [CGS description of the issuer prefix](https://www.cusip.com/pdf/Processes%20-%20CUSIP_Template_2019.pdf).
- Quarterly changes: the direction and extent of the complete changes, where the major adjustments are, the scale of new positions and exits, and reported-value contributions. The narrative identifies unchanged-share value changes and opposite share/value directions. It does not attribute trades to a motive, infer transaction cash flows or turn quarter-end differences into a trade log. Split-adjusted comparisons are retained; principal quantities are not labeled shares.
- History: the latest continuous, comparable window of up to four quarters, retention and entry/exit appearances, concentration changes, persistent core securities and the position of the latest value in the longer disclosed record. Missing legacy CUSIPs are matched conservatively using the existing security matcher; different supplied CUSIPs and instrument types remain distinct. Instrument-history boundaries shorten the comparison window. Reporting-scope transitions prevent cross-scope growth claims.
- Value screen: the actual distribution of estimated-cost gaps, the number of candidates with additions versus reductions versus unchanged shares, examples with current prices/costs, opposing holder directions and truly qualifying common holders. A price gap and an increase in shares are separate observations. Other holders that do not pass the cost threshold do not become qualifying consensus holders.

For the checked snapshot, Pabrai's new position represents about **0.045%** of his reported portfolio, and RIG's share increase is about **0.029%**; these are distinguished from the larger old-position reductions. Li Lu's additions center on PDD and BRK/B, while six securities leave the quarterly disclosure. Vinall has six reductions and just one addition (MSFT), while total reported value changes only slightly. These examples are generated from source records and will update with the data.

## Calculation and model responsibilities

`portfolio_briefing.py` calculates and composes the connected narrative from the disclosed records. Every published narrative is recomputed during validation, including its numbers, subjects, units, limitations and selected topic order. A model cannot insert arbitrary prose or change these values.

The CPU model receives the computed main point and a finite list of evidence topics. It selects supporting fact IDs and ranks topic IDs so the most useful explanation appears first. All calculated explanation sections remain available even if only some topics are prioritized. Foreign/duplicate topic IDs, rewritten text and unsupported source snapshots are rejected. Deterministic summaries remain complete while inference is pending or unavailable.

Recent historical source signatures now include per-security values and quantities for the relevant four quarters. Redistributing value between securities therefore invalidates a concentration narrative even when the quarter total is unchanged. Current and previous figures remain bound to their existing exact investor sources. Value-screen explanations are computed from the freshly fetched candidate set, independently of cached holder highlights.

Both automatic workflows include the new module and regression tests. The independent model remains bounded by the existing runtime limit. Version 70 refreshes frontend/configuration caches; the independently loaded summary request has a longer timeout without blocking holdings.

## Verification

Regression coverage includes tiny new positions, nonzero tiny percentages, issuer/share-class grouping, separate option and principal treatment, unchanged-share value changes, opposing share/value directions, confirmed splits, missing legacy identifiers, scope transitions, history redistribution with unchanged totals, modified narrative text and model topic ordering that preserves all sections. 172 Python tests, 67 JavaScript tests and all 51 data-file validations passed. Browser checks cover all 14 investors in both languages at mobile and desktop widths, including summary placement, distinct tab content, readable headings and absence of generic philosophy prompts inside data summaries.
