# Aspekte B2 — consolidated portfolio status (2026-11-08)

**All 10 lessons have complete source-level draft coverage: 1,726 / 1,726 owner-current source rows (100%).** Total provisional lexical card units: **1,719**. Approved/importable: **0**. No recorded app imports or SRS mutations.

| Kapitel | Title | Source rows | Draft cards | Stage |
|---|---|---:|---:|---|
| 1 | Heimat ist … | 160 | 158 | R47; closure pending |
| 2 | Sprich mit mir! | 108 | 110 | 3/3 BLOCKED_NONIMPORT |
| 3 | Arbeit ist das halbe Leben? | 186 | 186 | 3/3 BLOCKED_NONIMPORT |
| 4 | Zusammen leben | 184 | 183 | 3/3 BLOCKED_NONIMPORT |
| 5 | Wer Wissen schafft, macht Wissenschaft | 231 | 227 | 3/3 BLOCKED_NONIMPORT |
| 6 | Fit für … | 141 | 141 | 3/3 BLOCKED_NONIMPORT |
| 7 | Kulturwelten | 222 | 222 | 3/3 BLOCKED_NONIMPORT |
| 8 | Das macht(e) Geschichte | 179 | 180 | 3/3 BLOCKED_NONIMPORT |
| 9 | Mit viel Gefühl … | 162 | 161 | 3/3 BLOCKED_NONIMPORT |
| 10 | Ein Blick in die Zukunft | 153 | 151 | 3/3 BLOCKED_NONIMPORT |

## What is closed versus open

- **Kapitel 2–10:** completed the 3-pass *content workflow* with documented `BLOCKED_NONIMPORT` disposition. They are *not* published.
- **Kapitel 1:** 158 draft cards (R47), but three-pass closure **not yet completed**.
- **Crosslevel identity:** at least **38 flagged source ordinals for Kapitel 6–10** (8 + 4 + 11 + 6 + 9) require comparison with actual accepted imported card IDs/SRS. The full-project number is not established.
- **Linguistic approval:** independent meaning/morphology, German–Persian examples, and lexical relation checks have **no full release sign-off**.
- **Native app safety:** SRS-preserving import, rollback and persistence tests are **not evidenced**.
- **Curation source:** the latest user-edited B2 material; do not restart a comparison against the publisher's original book or older B1+ files.

## Next work (not another ten rounds of word edits)

1. Close Kapitel 1 with `BLOCKED_NONIMPORT` if the release evidence remains absent.
2. Build one centralized release manifest from all 1,719 draft cards, preserving the source identities and all meaning-specific relationships.
3. Check actual accepted live app IDs against the unresolved crosslevel entries, then perform independent content QA and non-destructive native import/SRS roundtrip gates.
4. Release only after **all** applicable gates are evidenced; otherwise keep content in `NONIMPORT` state.

**Current canonical L10 draft:** `Current/L10-PASS2-151-CARD-EDITORIAL-REVIEW-NONIMPORT.csv`; SHA256 `c1acbd41371c4cf1bcc7d7bdcbf92d3cdf0b217fbd6aac85248202681f80b0b0`.
