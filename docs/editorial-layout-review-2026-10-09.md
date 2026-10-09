# Investor page revision — 2026-10-09

The holdings and quarterly changes tables now appear before the quarterly summary and AI highlights. The dated HK disclosure cards have been removed from both the holdings and history views; Webb's existing main table remains a clearly marked historical snapshot, without a second copy of its disclosures.

The profile presentation restores distinctive headings and six-card investment frameworks from the version before `3a20bc9`, while retaining corrected reporting identities, links, founding dates and present-day management roles. Biographies now explain each investor's approach rather than substituting generic research instructions. Li Lu's macro/micro passage, Pabrai's Dhandho principle and the sunlight/transparency maxim are visible again with source links. The transparency maxim is credited to Louis D. Brandeis, rather than invented as Webb's original wording. Unverified old quotations and performance/portfolio-size claims were not blindly restored. Tepper's description focuses on credit research, distressed assets and macro conditions.

Primary editorial references:

- [Himalaya biography and investment framework](https://www.himcap.com/), [Li Lu's December 2024 speech](https://www.himcap.com/publications). The official English transcript says the macro environment can only be accepted, while the micro level is where investors can make a difference. The short English line displayed on this page is labeled a translation.
- [Pabrai's University of Nebraska session transcript](https://www.chaiwithpabrai.com/uploads/5/5/1/3/55139655/20240620_mohnish_pabrais_session_at_the_university_of_nebraska_omaha_on_may_3_2024_v2.pdf), [original interviews and articles](https://www.chaiwithpabrai.com/).
- [Webb's article archive](https://webbhk.substack.com/), [historical database mirror](https://webbsite.0xmd.com/dbpub/webbchips).
- [Tepper's official biography](https://www.panthers.com/team/ownership_business/test-david-a-tepper).
- [Baupost's investment framework](https://www.baupost.com/investment_philosophy), [RV Capital's owner approach](https://www.rvcapital.ch/).

## Recent HK positions in the main table

There is one qualifying supplementary record in the checked data: H&H International Investment, LLC's Pop Mart interest, **106,716,000 ordinary shares**, event date **2026-09-01**, original filing **CS20260905E00003**, disclosed long interest **8.01%**. The matching individual filing describes overlapping interests and is not added a second time.

The frontend reads the existing automatically updated HK files. A row requires a successful automated audit no more than seven days old, a verified original HKEX form, completed filing history, an exact match to the reporting manager, a known share class, positive long shares, and at least 5% disclosed interest. The event must be at or after the displayed 13F quarter-end, no more than 120 days old, and not in the future. A newer below-threshold record or ambiguous share classes cannot promote an older record. Later zero-value financial evidence excludes a record without inventing zero shares. The row represents holdings **on its displayed disclosure date**, not a live trading position.

Li Lu's last original HK events in the automated October 9 check are BYD (2021), CRRC (2018) and PSBC (May 2025). All have unknown present holdings and fail the recency check. They are retained as research evidence in the data files and are absent from the portfolio view.

HK shares appear directly in the existing main table with their date and original link. Undisclosed value, price, cost, portfolio weight and margin of safety are left blank. The summary count, USD value and quarterly change statistics remain explicitly scoped to 13F. Loading, refresh and investor changes update the supplementary rows atomically with their corresponding investor. A delayed HK response cannot overwrite a later selection.

The SEC numerical fixes, complete change counts, split/option handling, source-bound AI summaries and daily automated updates remain in place. The asset/configuration version is 68 to avoid mixed browser caches.

## Verification

Python regression suite and all 51 data-file validations pass. JavaScript checks include layout order, restored bilingual source links, recent HK inclusion/exclusion, exact share quantities, duplicated controlled interests, stale/partial checks, below-threshold records and delayed investor responses. Chrome checks cover all 14 investors in both languages at mobile and desktop widths, plus narrow-phone checks for the four requested profiles. Tables precede AI, Webb has no duplicate HK block, Li Lu has no stale HK rows, and H&H has one dated Pop Mart row. No page errors or document-width overflow were found.
