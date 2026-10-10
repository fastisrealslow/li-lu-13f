# Visual alignment with Himalaya Capital

Reference: https://www.himcap.com/ (reviewed 2026-10-10).

The reference uses a white navigation bar, dark gray body text, blue branding, regular-weight Playfair Display headings, generous section spacing and dark charcoal philosophy sections. The tracker previously emphasized navy gradients, gold pill buttons, decorative emoji and rounded cards. These accumulated treatments made the data and reading sections feel more crowded than the reference.

## Changes

- Added one shared `theme.css` for the dashboard, Munger game and companion essay. Aligned page margins, lighter heading weights, white surfaces, muted colors and thin rules give these pages a consistent visual rhythm.
- Self-hosted the original variable Playfair Display font with its SIL Open Font License. Chinese headings use the available system Songti font; body text retains readable system fonts. Arrows fall back to system fonts rather than decorative Playfair glyphs. There is no new external font request.
- Replaced desktop investor pills with text buttons and an active underline. On small screens, all 14 investors are available through a labeled native selector. Failed data loads restore the previous selection together with its unchanged profile and holdings.
- Simplified the phone's four headline metrics into a two-column grid with rules, keeping all metric labels and numbers.
- Separated weight percentages from their bars and made each bar represent its actual percentage, capped at its track width. The previous `percentage * 3.5` display could overflow for concentrated portfolios.
- Removed decorative icons from primary tab navigation, and numbered the six investment principles. Biography text, distinctive investor descriptions, source links, numerical calculations and individual tab summaries are preserved.
- Restyled summaries below their tables as report sections. The profile, reading resources and quotations use larger headings and less boxed decoration. Philosophy sections use the reference's charcoal background with readable light text.
- Converted the mobile navigation trigger into a keyboard-accessible button with an expanded state. Anchor offsets account for the fixed header. Game and essay headers wrap at narrow widths so return links remain fully visible.
- Updated dashboard and game cache versions. The game retains its existing save format and progress key.

The tracker retains its data-first opening. The reference's full-screen mountain photograph, logo and promotional text are not copied.

## Verification

- Existing JavaScript suite: 74 passing tests.
- Pages Python checks: 48 spin-off evidence tests and 6 filing-unit tests passing; all 51 published data files validated.
- Browser review at 320, 390, 768, 1024 and 1440 px: all seven research tabs, biographies, philosophy, resources, game and essay layouts. Overflow checks use the requested viewport width because mobile browsers can expand their layout viewport around overflowing elements.
- All 14 investors in Chinese and English at phone and desktop widths: 56 profile cases. Verified profile text, six principles, selection state, displayed holding counts, distinct summaries and their position below data. Simulated a failed investor fetch and confirmed the selector, profile and dataset remain consistent.
- Mobile navigation tested with Enter and Space, then anchor navigation and expanded-state reset.
- Full game playthroughs at 320, 375, 768, 1024 and 1440 px, including calculator experiments, budget constraints, personalized review, saving/reloading, reset, article round trip, keyboard input, blocked storage and invalid saved state. Embedded game checked at phone and desktop widths.

Responsive verification uses Chrome browser emulation and screenshots; physical-device testing was not performed.
