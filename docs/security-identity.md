# Legacy security identity audit — 2026-10-29

All 17 configured investors scanned from master 830baad4b. These are display
identities (CUSIP + option direction + quantity type), not transaction counts.

| Investor | Before timeline rows | After | Confirmed examples |
|---|---:|---:|---|
| Li Lu | 26 | 21 | Baidu ADR, Micron common, Sina ordinary, Weibo ADR, Alibaba ADS |
| Mohnish Pabrai | 54 | 39 | POSCO ADR, Micron common, Southwest common, AerCap shares; GM warrants and WL Ross units remain separate from common stock |
| Chuck Akre | 312 | 297 | CarMax, Monarch Casinos, Toll Brothers, historical Chubb names |

The other 14 investors have no matches under this rule. This is not a claim
that every possible corporate action or historic identifier error is resolved.
Full per-row evidence and all 17 before/after counts are in
`security-identity-audit.json`.

The projection joins a row **without** a CUSIP only when that investor's own
history contains one unique nine-character CUSIP for the exact issuer name,
share class, put/call direction and share/principal type (case/whitespace only).
Baidu's `Spon ADR A` and `Spon ADR REP A` are explicitly equivalent class-A ADR
labels, supported by the same Himalaya history. No fuzzy names or blanket ticker
matching. Different existing CUSIPs never join. In particular, old/new Google
CUSIPs and Pabrai's eight-character `84670702` remain separate, pending further
source verification. Ordinary stock, ADR, classes A/B, warrants, units, call/put
and principal remain distinct. Ambiguous exact signatures remain unresolved.

Raw source JSON and its filing provenance are unchanged. Derived browser rows
carry `reportedIdentity` plus `identityEvidence` (supporting quarter, source,
CUSIP and matching rule). Python price/history calculations and JS raw-data
fallback use the same rules, checked for equality across all 17 investors.
Within-quarter consolidation sums separate source lines once; original row
counts, shares, values and quarterly totals are tested unchanged.

Missing reports remain missing: Li Lu 2018 Q4 through 2019 Q3 are unknown, with
an explicit timeline notice where the holding's span crosses the gap. A filed
quarter without a position still establishes disclosed absence; later disclosure
remains a reappearance. No zero filling, interpolation or continuity inferred
through unknown quarters. Historic first/last labels describe disclosed holdings,
not transaction dates.

Estimates cached before identity reconciliation are suppressed for affected
securities. The next normal price update recomputes with projected histories and
writes `securityIdentityVersion: 1`; old exit-performance caches are not reused.
Pabrai's history explanation was refreshed deterministically from corrected
facts without calling an LLM. The deployment workflow runs identity and cost
regressions in addition to existing checks; no paid workflow is invoked.
