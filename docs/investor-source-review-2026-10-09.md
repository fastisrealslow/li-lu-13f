# Investor information and source review — 2026-10-09

All 14 investor tabs now use the same bilingual profile configuration. Profiles contain a dated biography, documented milestones, six investment/readings cards, and explicit source links. Method summaries are labeled as paraphrases, not fabricated quotations. Institutional filings do not establish an individual's personal holdings or reasons for trades.

## Source and identity checks

| Tab | Reporting identity | Corrections / primary biography sources |
| --- | --- | --- |
| Li Lu | Himalaya Capital Management LLC, CIK 1709323 | [Official firm biography and approach](https://www.himcap.com/); [publications](https://www.himcap.com/publications). Removed unsupported fallback prose. |
| Pabrai | Dalal Street, LLC, CIK 1549575 | [Personal website](https://www.chaiwithpabrai.com/); [fund history](https://pabraifunds.com/about/). Distinguish personal website from filing entity. |
| Duan Yongping | H&H International Investment, LLC, CIK 1759760 | [Verified Xueqiu account 1247347556](https://xueqiu.com/u/1247347556); [SEC adviser registration](https://adviserinfo.sec.gov/firm/summary/292451). Removed incorrect account/portfolio links and unsupported attribution of trades. |
| David Tepper | Appaloosa LP, CIK 1656456 | [Official owner biography](https://www.panthers.com/team/ownership_business/test-david-a-tepper); [CMU biography](https://admission.enrollment.cmu.edu/sites/default/files/2025-05/bio-tepper-david.pdf). MBA 1982; joined Goldman 1985; founded Appaloosa 1993. |
| David Webb | Historical HK disclosures, not SEC 13F | [Author's archive](https://webbhk.substack.com/); [database mirror](https://webbsite.0xmd.com/dbpub/webbchips); [HKEX person search](https://di.hkex.com.hk/di/NSSrchPerson.aspx?src=MAIN&lang=EN); [dated obituary](https://apnews.com/article/a7b7b3bc19b286eed7a7d0d518deeca4). Archive closure and deceased status clearly distinguish this tab from a live portfolio. |
| Buffett | Berkshire Hathaway, CIK 1067983 | [Official September 18, 2026 announcement](https://www.berkshirehathaway.com/news/sep1826.pdf). Buffett is chairman emeritus and remains a director; Greg Abel is CEO; Howard Buffett is chairman. Do not attribute all group trades to Buffett. |
| Chuck Akre | Akre Capital Management, CIK 1112520 | Corrected the resource card's unrelated CIK. [Firm website](https://www.akrecapital.com/) documents 1989 founding; [John Neff biography](https://www.akrecapital.com/people/john-neff/) confirms current CEO/CIO. Removed unsupported returns and current portfolio-size assertions. |
| Glenn Greenberg | Brave Warrior Advisors, CIK 1553733 | Corrected resource card's unrelated CIK. [SEC adviser record](https://adviserinfo.sec.gov/firm/summary/108894); [signed SEC comment](https://www.sec.gov/comments/s7-14-10/s71410-20.pdf). Removed unsupported mentorship claim and unverified social links. |
| Seth Klarman | Baupost Group, CIK 1061768 | [Official company history](https://www.baupost.com/About); [strategy](https://www.baupost.com/investment_philosophy). Broad multi-asset mandate, not just disclosed stocks. |
| Bill Ackman | Pershing Square Inc., CIK 2026053, from 2026 Q2 | [Predecessor's SEC notice](https://www.sec.gov/Archives/edgar/data/1336528/000117266126003777/xslForm13F_X02/primary_doc.xml) explicitly names the parent as reporting manager. Preserve legacy CIK 1336528 history before Q2. [Actual manager website](https://pershingsquareinc.com/) is distinct from the listed fund. |
| David Abrams | Abrams Capital Management, CIK 1358706 | [Official history](https://www.abramscapital.com/about); [leadership](https://www.abramscapital.com/leadership). Founded 1999; public/private and liquid/illiquid mandate. Removed unsupported ultra-concentrated assertions. |
| Bruce Berkowitz | Fairholme Capital Management, CIK 1056831 | [Official funds website](https://www.fairholmefunds.com/); [prospectus](https://www.fairholmefunds.com/s/StatutoryProspectus-raaj.pdf). Manager established 1997; do not describe an old fixed concentration as a permanent current fact. |
| Mason Hawkins | Southeastern Asset Management, CIK 807985 | [Official team](https://southeasternasset.com/our-people/); [Longleaf fund](https://southeasternasset.com/investment-offerings/longleaf-partners-fund/). Hawkins is chairman/co-manager; Ross Glotzbach is CEO. |
| Rob Vinall | RV Capital AG, CIK 1766596 | [Official company](https://www.rvcapital.ch/), [letters](https://www.rvcapital.ch/articles-en), [videos](https://www.rvcapital.ch/videos), [podcast](https://www.rvcapital.ch/podcast). Founded 2006; includes co-managing director Andreas Lechner and Business Owner Fund relationship. |

SEC submissions were checked for all 13 filing entities; the latest report period is 2026 Q2. Ackman's original fetch stayed at Q1 because the old adviser now files 13F-NT. The fixed fetch follows the confirmed parent from Q2 and the adviser before then. Parent filings before Q2 must not replace the adviser history, since those older parent reports have a narrower scope. The latest parent information table totals US$19,465,692,772; duplicate security rows consolidate into 14 positions without changing the total. Q2's expanded scope is explicitly disclosed and quarterly buy/sell labels and cost inference are suspended for the transition quarter.

56 distinct profile/official URLs were inspected. Direct requests loaded 44; 12 encountered bot restrictions, redirect loops, transient 503s or timeouts. Company/SEC identity and relevant pages were cross-checked against official pages and indexed primary content. Such responses do not prove a URL is broken or guarantee availability from every region. No unverified substitute domains are advertised as official sites.

## Data and update fixes

- Webb's cached holdings sum to HK$928,850,650, rather than the stale HK$14,262,909,000 summary. Use HKD throughout and sort positions before computing top-three concentration. Remove contradictory synthetic quarter/report dates. This is an archived, thresholded disclosure snapshot; cached valuation dates remain unverified. Retrieval timestamps never create a new filing quarter or a claim of purchase/sale. Refresh recomputes the sum, replaces the snapshot instead of retaining omitted rows as current holdings, and does not calculate costs from unverified quarterly history.
- Missing/error or fallback-stale quotes no longer produce percentage gains, margin-of-safety badges or value-screen candidates. Quarterly old holding prices are not a substitute for a quote. Refresh clears the value-screen HTML cache; cached HTML expires after five minutes. Versioned JSON requests prevent the new interface from using pre-release configuration or holdings cached under the previous URL.
- Investor-list load failure displays a recoverable message, and Refresh retries configuration before loading holdings.
- A successfully completed SEC history search with unavailable historical originals is an informational notice. Interrupted searches or unreadable complete-report candidates remain warnings. Notices survive the workflow's later success marker and cannot override a real failure. Existing historical status records are not rewritten.
- HK dated references no longer erase inherited business/project identities on the next run. Three actual reference chains were repaired and checked for repeated-run stability; associated dossiers now merge correctly.
- Vylor's original September 24 8-K defines the separation of “the Company”. Parse the defined company and exclude the “Item 8.01 Other Events” heading from its name. This avoids the unnecessary unreadable supplementary-exhibit request and restores the source-bound Vylor identity. Prior run warnings still describe the prior run; the next automation run exercises the repaired resolver.
- All current portfolio totals are checked against their component holdings before deployment.

## Remaining source limits

Li Lu's stored history lacks 2018 Q4 and 2019 Q1–Q3. SEC submissions and expanded quarterly indexes were checked; there is no verified complete portfolio to backfill. Keep gaps visible, name the missing quarters, and retry incomplete searches. Do not fabricate zeros or interpolate holdings.

Baupost's 2026 Q1/Q2 amounts match the SEC information tables but imply implausible per-share scales for major securities. A corrected filing or authoritative unit clarification was not found. Preserve the raw filed amounts with an explicit warning, suspend cost inference, and exclude those valuation points from the trend chart. Do not silently multiply the reported values by 1,000. Share quantities remain available.

## Verification

145 Python regression tests, 53 JavaScript tests, and validation of all 50 data files pass. Chrome checks cover every investor in Chinese and English at 375px and 1440px (56 scenarios), cold-start configuration recovery, all dashboard tabs, and the status drawer at 320/375/390/430/812/1440px. No JavaScript page errors or document-width overflow in those checks. Source checks include actual SEC reporter transitions, sum reconciliation, repeated HK reference resolution and the cached original Vylor filing.
