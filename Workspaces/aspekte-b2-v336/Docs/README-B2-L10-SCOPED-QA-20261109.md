# Aspekte B2 — Kapitel 10, scoped linguistic QA

**Date:** 2026-11-09. **Scope:** 151 owner-curated nonimport cards, source SHA `c1acbd41371c4cf1bcc7d7bdcbf92d3cdf0b217fbd6aac85248202681f80b0b0`.

- **24 cards** with **33 exact field edits**, **127 unchanged cards**.
- **23** front field (Artikel + full Plural) edits; remaining changes include German–Persian meaning/sense annotations and direct noun-sense collocation repair.
- Important: `die Waise` (not `der/die Waise`); Duden records both orphan and specialized verse-theory senses. `der Vormund, die Vormünder` (also `die Vormunde`); `der Astronom` is weak-declension (`des Astronomen`). `Menschenleben`: lifetime vs life at risk. `Schwarm`: distinguish actual nominal collocation from `schwärmen` word-family phrase.
- All **302** existing L10 German–Persian pairs preserved byte-for-byte at cell level; IDs, source columns, examples and row order unchanged.
- All ten lesson structural QA **PASS**, **1719** distinct cards, **3438** standard German–Persian pairs, **4891** collocation units and **0** within-card duplicated collocations.
- **27/27** positive and negative checks PASS. No human external reviewer needed per `MEM-031`.
- **Release remains `BLOCKED_NONIMPORT`** because a full projectwide semantic Stage4 pass and safe native app/SRS identity/rollback tests have not been evidenced. This does not prevent content curation.

## Files

- `L10-PRE-24-CARD-QA-20261109.csv`: exact pre-change Current.
- `L10-PASS2-151-CARD-EDITORIAL-REVIEW-NONIMPORT.csv`: proposed new owner-curated Current, only 24 card identities affected.
- `L10-EXACT-SEMANTIC-DELTA-20261109.csv`: 33 old→new cell changes, with grounded Duden evidence.
- `L10-SCOPED-LEXICAL-QA-RECEIPT-20261109.json`: source/target SHA, scope, no-release claims.
- `L10-REGRESSION-AND-FAULT-INJECTION-20261109.json`: exact 27 checks.
- `B2-CENTRAL-QA-POST-L10-20261109.json`: 10-lesson read-only structural audit.
- `apply_l10_qa.py` and `test_l10_qa.py`: local reproducibility, not app importers.

The legacy all-1719-card external signature handoff is **obsolete** after earlier accepted edits; it is not a release gate. Source authority is `Library/Current`, not the book or unsigned worksheet.
