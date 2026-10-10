# Thinking trials and companion reading revision — 2026-10-10

## Delivered behavior

The main site's last tab now opens a five-chapter learning game with 13 decisions, three verified numerical experiments, a resource-allocation finale, and individual chapter reviews. Answers remain first attempts: an incorrect response receives specific reasoning and is never silently awarded a correct score. Completion and correctness are separate. Previous chapters can be revisited; later ones remain locked until their prerequisites are complete.

A versioned local notebook saves answers, experiment completion, parameters, allocation, and screen. Reloads and switching between the reading and game preserve progress. Invalid storage is bounded and cannot skip unfinished chapters; unavailable browser storage keeps play functional and reports that progress cannot be saved. Restart uses an inline confirmation, with a cancellation path.

Desktop uses a chapter sidebar, generous reading width, and a two-column calculator. Mobile uses a compact chapter grid, stacked content, native buttons, range controls and explicit increment/decrement buttons. Native keyboard interaction works, with 1–3 shortcuts for decisions. Browser zoom is enabled; reduced motion, visible focus, live feedback, landmarks and a skip link are provided.

The new companion essay is accessible both from the game and the host tab. It covers the premise, five thinking lenses, numerical derivation, operating chain, inversion, partner incentives, historical dates, and reusable research questions, with a contents navigation and source links. Shared navy, cream and gold styling matches the host's visual identity. These are original exercises and commentary, not a reproduction of the speech.

## Corrected numerical and factual issues

- The former calculator divided USD by 1 billion while labeling the result 亿美元. The new conversion explicitly divides by 100 million.
- The two percentages now have distinct denominators: beverage category share of total liquid volume, and company share of that category. Original 25% × 50% parameters produce 2.92 trillion annual servings and USD 116.8 billion (1,168 亿美元) profit at 4 cents per serving.
- Valuation is separate from annual profit. 18× and 12× multiples are declared game assumptions, not values specified by Munger. Each stress case changes only one variable; results refresh when inputs change. Zero-profit cases cannot produce an infinite implied multiple.
- The fictional USD 2 million is fully invested for half the equity held by the foundation, rather than half donated and half invested. The non-alcoholic beverage restriction and continued distributions are explained.
- Historical dates and fictional setup are separated. Unverified attributed quotations and undated “current” company valuation were removed. New Coke's 79-day period refers to restoration of the original formula, not permanent discontinuation of New Coke.
- Final allocation arithmetic retains the stated 0.6-cent increments exactly; it does not round them to the calculator's 0.5-cent slider grid.

Primary references checked:

1. [Publisher's original text](https://www.stripe.press/poor-charlies-almanack/fullbook), “Practical Thought About Practical Thought?”
2. [Coca-Cola's official 140-year history](https://www.coca-colacompany.com/media-center/founders-day-2026-140-years-of-moments-html).
3. [Coca-Cola's New Coke history](https://www.coca-colacompany.com/about-us/history/new-coke-the-most-memorable-marketing-blunder-ever).

## Verification

- 74 JavaScript tests pass, including seven new arithmetic tests. Every valid integer allocation of 10 tokens is reconciled to the disclosed rules.
- The 54 Python checks required by the Pages workflow pass; 51 published data files validate.
- Browser full playthroughs at 320, 375, 768, 1024 and 1440 pixels pass: choices, wrong-first-answer persistence, experiment prerequisites, zero-volume handling, fresh stress results, budget enforcement, ending score, weak-allocation review, reading return, and reset cancellation/confirmation. No horizontal overflow or uncaught errors.
- Actual host iframe verified at 375 and 1440 pixels. Additional checks cover keyboard shortcuts, blocked storage, corrupt saves and mission restoration.
- Native synthetic touch checks verify choosing an answer, dragging the range control, increment/decrement taps, vertical document swipe, and interacting inside the real host iframe. These are browser device emulations rather than physical-device tests.
- Article anchors resolve internally and all three primary-source links return HTTP 200.

An unrelated existing deployment test assumed the latest live HKEX retrieval always succeeds. The latest automated data had correctly marked a timed-out retrieval as partial, causing the test to fail. The positive evidence test now uses a fixed, original verified manager/co-filer fixture and a fixed evaluation clock. The manager identity, duplicate-interest rejection, stale-date, incomplete-audit, threshold and verification guards are retained. No holdings data or production evidence rule was changed to make this test pass.
