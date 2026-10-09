# Independent tab interpretations — 2026-10-10

The three portfolio tabs no longer share a global quarterly summary. Each interpretation follows its own table or timeline inside that tab. The value screen also places its interpretation after the full candidate table and cost-method explanation.

- Holdings: current security types, leading positions and concentration. Share classes and options stay separate. Archived snapshots and unverified dollar scales keep their explicit limitations.
- Quarterly changes: current versus previous reported shares, including every reduction and exit. Model-selected highlights are followed by complete counts and expandable lists; small changes have no exclusion threshold.
- History: dated coverage, reported-value evolution, consecutive quarterly appearances and missing records. Neither reported-value growth nor a peak is presented as investment return. A reporting-scope transition breaks the chart line and suppresses cross-scope growth and holding-streak claims.
- Value screen: candidate totals, estimated-cost gaps, qualifying shared holders and opposing share directions. Stock context is expandable beneath this overview. Price-versus-estimated-cost gaps are not business fair-value estimates.

## Sources and automation

`tab_insights.py` generates separate bilingual facts and source signatures for `holdings:<investor>` and `history:<investor>`. Existing `investor:<investor>` entries remain specific to quarter changes; `value` remains specific to the cross-investor screen. Python and JavaScript agree on the source representation for every published investor. Historical signatures preserve exact quarter totals and security presence, rather than duplicating unused transaction-sized records in the download.

The model selects fact IDs; it cannot write numbers, motives or arbitrary prose. Scope, value-quality, option-value and gap limitations are mandatory selections. Publication recomputes the facts and rejects modified text. The browser rejects mismatched source snapshots, unknown IDs, inconsistent text and omitted mandatory limitations. Correct deterministic interpretations are immediately available while the independent CPU model selects highlights; failed inference does not block holdings or replace validated model results.

Both scheduled workflows include the new module. The CPU job processes up to 20 changed summaries within its existing time limit; remaining tasks continue through subsequent runs. The data updater refreshes valid interpretations automatically. The latest concurrently published, validated value-screen model result was preserved during this revision.

Value-screen stock notes now describe disclosed facts instead of guessing conviction, trading intent, fundamental concerns or future returns. Cost-reference elapsed time is not described as a verified continuous holding record; a last-positive quarter is not labeled the exit date. Fresh price, estimated cost and percentage checks prevent old numerical notes from accompanying refreshed candidates. Request IDs and language-specific caches prevent a delayed response from replacing a newer language or cached result.

## Presentation

All 14 profiles keep their source-backed biographies, quotations and six principles. Each now has a concise, distinctive investment framework and separate reading perspectives for composition, changes and history. Examples include Li Lu's circle of competence and patient compounding, Pabrai's Dhandho asymmetry, Akre's three-legged stool, Klarman's margin of safety, Webb's transparency, and Vinall's patient partnership with management. These are research perspectives, not explanations invented for particular trades.

Desktop data width increases to 1280 pixels. Six philosophy cards use three columns; interpretation cards fit their content count, including full-width quarterly highlights. Mobile retains stacked cards and scrolling tables. Asset/configuration URLs use version 69 to refresh cached releases.

## Verification

161 Python tests, 65 JavaScript tests and all 51 data-file validations passed. New regressions cover tab/source separation, stale historical corrections, modified facts, mandatory option limitations, cross-scope chart breaks, opposite value-screen directions and delayed language/cache responses.

Chrome checks covered all 14 investors in Chinese and English at 375- and 1440-pixel widths, plus selected profiles at 320 pixels. Each portfolio tab displays exactly one appropriate interpretation below its data; the value interpretation is below its table. Descriptions and complete reduction/exit counts match the selected investor. No page errors or document-width overflow were found. Existing HK recency rules and original disclosure links remain intact.
