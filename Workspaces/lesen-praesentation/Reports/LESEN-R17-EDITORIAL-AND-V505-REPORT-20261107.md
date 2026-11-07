# Lesen R17 – Editorial and v505 pre-entry report (7 November 2026)

**Status: SOURCE-GROUNDED EDITORIAL CANDIDATE; NOT CURRENT, NOT FULL STAGE4, NOT A RELEASE.**

## Scope and actual changes

- Continued byte-verified **R16**, never the original PDF or older app main.
- On lessons **039–050 and 052**, replaced **23 identical German p02-s03/p03-s03 conclusions** with lesson-specific conclusions grounded in the accepted preceding sentences. Lesson **051**, previously corrected, is **byte-identical**. **55/68 lessons are unchanged**.
- **19** German conclusions now explicitly agree with their **already curated** FA/EN third-sentence meanings; their translations were retained unchanged. The remaining **4** generic translation-ending pairs were rewritten in both FA and EN, without changing preceding sentences (p03 of 046, 047, 050; p02 of 052).
- Original lesson titles, passages outside the 23 sections, 340 questions, 350 vocabulary entries, 669 curated grammar annotation identities, and source provenance remain intact.
- **72** former source-offset grammar occurrences associated with deleted generic sentences were retired, rather than silently left pointing to wrong text. **9** existing curated g06 samples were retargeted to real new relative clauses; **9** narrowly reviewed exact-offset fulltext relative-clause occurrences added. Fulltext counts **4,160 → 4,097**. The original native nine-lens grammar engine **was not rerun**.
- Identical generic conclusions remaining: **p02-s03 = 15, p03-s03 = 11** (26 sentence occurrences, not 26 lessons).

## Technical quality evidence

- Independent read-only structural/source/runtime checks **12,559/12,559 PASS**, with **9/9** deliberate negative cases rejected. This does **not** establish complete learner-facing multilingual correctness.
- Actual current-v505 source module `reading-content-import-v38.js` SHA-256 `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc`: `validate()` **PASS, zero warnings**; 7/7 corrupted inputs rejected; `validateRecord()` and **isolated in-memory** `adoptCommittedMirrorV505()` PASSED (68 units / 340 exercises).
- **NO browser navigation, IndexedDB write or production app import. NO user review state, UI, SRS or FSRS modification.**

## File identities

| Artifact | SHA-256 | Bytes |
|---|---|---:|
| R17 editorial master | `593deb6e5ec7cdba2d95f7445589ae5bf6cf17750eb0f8cdbb9c3f4f1a605ad7` | 6161772 |
| R17 v505 pre-entry runtime | `b6258670d91951c05fdc409886c538558388889f3ea0217533aa08c5dd7d1ccd` | 6619772 |

Source-aware parent: R16 content `0b31f21ed6cd65b2562d3806e58269294196d161b05ba87cc7af35e3ab87ffa5`; v505 pre-entry `afec137c5868eb26051c913e3dedefcc848a4a932d5e4cf23e5e21409516f641`.

## Remaining gates and work

- **Stage 4 independent full 68-lesson German–Persian–English semantic review: HOLD.** The 23-change scoped review in `LESEN-R17-TRILINGUAL-SCOPED-REVIEW.json` is AI-authored and not this gate.
- **Stage 5 official finalized compiler/grammar regeneration: HOLD** (this runtime is a reversible exact-v505 delta).
- **Stage 6 real browser/IndexedDB native import: NOT RUN** (prior Chromium environment blocked navigation).
- **Stage 7 release: NOT RELEASED.** Do not claim native import compatibility beyond v505 source validation.
- Next: inspect 26 remaining generic endings, likely lessons 053–068; avoid replacing high-quality specific sentences. Then examine p01–p05 reasoning and independent semantic quality, plus potential original word count drift.
- **Immutable CURRENT source-owner v1.3.0 ZIP** SHA-256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`; R16 retained as recovery parent. No new redundant sibling workspace, no auto-cleanup.