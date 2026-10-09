# Portfolio, AI and HK disclosure review — 2026-10-09

Downloaded the latest two original SEC information tables for all 13 filers.
Current and previous value totals agree with those XML files. Every share change,
including small reductions and all exited securities, contributes to the full
counts and expandable lists. AI highlights are explicitly a partial selection.

Same-security manager/discretion rows are grouped by CUSIP and PUT/CALL / SH/PRN,
never ticker alone. Hawkins' 81 latest filing rows become 47 securities without
changing total value. Akre's CRM common stock and CALL remain separate. Tepper's
AAPL and BRK/B PUTs show underlying shares and do not receive equity cost or
price signals. The classification follows the [SEC Form 13F instructions](https://www.sec.gov/files/form13f.pdf).

Berkshire's Lennar A/B and Liberty Live A/C positions now have distinct symbols:
LEN, LEN/B, LLYVA and LLYVK. Sources: [Lennar B SEC table](https://www.sec.gov/Archives/edgar/data/714364/000071436426000004/xslForm13F_X02/Ogorek_Holdings_13F_2026Q1.xml)
and [Liberty Live official FAQ](https://www.libertyliveholdings.com/investors/company-information/faq).
Old instrument history is repaired automatically from SEC tables, at most four
quarters per affected investor per update. Unverified ranges are excluded from
affected securities' share timelines. Values are never rescaled by price heuristics.

## Complete latest report changes

Counts refer to securities, including separately identified option positions.

| Investor | Current | New | Added | Reduced | Exited | Unchanged |
|---|---:|---:|---:|---:|---:|---:|
| Li Lu | 8 | 0 | 2 | 0 | 6 | 6 |
| Pabrai | 4 | 1 | 1 | 2 | 0 | 0 |
| Duan | 18 | 1 | 3 | 7 | 2 | 7 |
| Tepper | 27 | 8 | 11 | 5 | 12 | 3 |
| Buffett | 29 | 1 | 7 | 6 | 1 | 15 |
| Akre | 20 | 0 | 2 | 13 | 0 | 5 |
| Greenberg | 40 | 7 | 6 | 15 | 3 | 12 |
| Klarman | 23 | 3 | 6 | 9 | 2 | 5 |
| Abrams | 11 | 0 | 0 | 1 | 0 | 10 |
| Berkowitz | 13 | 3 | 4 | 1 | 0 | 5 |
| Hawkins | 47 | 2 | 8 | 24 | 4 | 13 |
| Vinall | 13 | 0 | 1 | 6 | 0 | 6 |

Ackman's 14 current securities cannot be interpreted as quarterly trades during
the 2026 Q2 reporting-scope transition. Webb remains a historical snapshot.
Missing intervening quarters suppress quarterly trade inferences. Klarman's
unresolved reported-value scale is retained and cost signals stay suspended.

## AI and automated publishing

Renderer v4 binds summaries to previous quarter, reporting scope, value-quality
flags, instrument types and split evidence. Code computes every count and number.
The model selects fact IDs only and must cover each available new/add/reduce/exit
direction. Publisher and browser reconstruct factual text; changed sources or
altered text fall back to current deterministic summaries. Scope transitions
consume no inference slots.

Value-screen sources include each investor's report quarter. Stock notes must
match that exact source. Share trends require consecutive reports and split
adjustment. Reentry requires a verified report showing absence; missing reports
are not exits. Cost-history continuity resets across any missing holding quarter.

Every data publication refreshes safe summaries, independently of inference.
Model-setup failures still publish current deterministic summaries and remain
eligible for retries. Summaries are rebound after automated merges. Validation
checks AI source/text consistency, financial totals and HK evidence units.

## Hong Kong

All 14 investors' configured entities were searched in both HKEX archives.
Holdings now includes dated HK cards with quantities, entities, share classes,
ownership percentages, original filings and history. Other reporting entities
are expandable. Overlapping interests are not added together, and HK quantities
are not included in the USD 13F total or allocation weights. Changes require
two original forms for the same entity and share class.

Old disclosures and completed searches cannot establish live holdings. Below
the substantial-interest threshold, subsequent changes may no longer produce
continuing disclosures. See [HKEX's official disclosure explanation](https://www.hkex.com.hk/global/exchange/faq/getting-started?sc_lang=en).

Li Lu's latest verified PSBC event is 2025-05-08: 985,618,000 shares / 4.96%.
BYD and CRRC records are dated 2021-11-08 and 2018-06-26. Their old quantities
are explicitly historical, with current holdings unverified.

Berkshire's BYD card adds identified BHE investment-value facts from
[2025 Q1](https://www.sec.gov/Archives/edgar/data/75594/000108131625000010/bhe-20250331.htm)
and the [2025 annual report](https://www.sec.gov/Archives/edgar/data/75594/000108131626000003/bhe-20251231.htm).
Both report zero investment value at million-dollar precision. These facts do
not establish exact zero shares or a sale date. The updater scans this filer's
latest 10-Q/10-K for the same IXBRL investment dimension; missing facts produce
no position inference and existing evidence is retained.

## Verification

154 Python regressions, 56 JavaScript regressions and 51 published JSON files.
Browser checks cover all 14 investors, both languages, at 375 and 1440 pixels.
Cross-runtime tests compare complete Python/browser facts and exact summary
strings, including smallest changes, exits, separate instruments and source flags.
