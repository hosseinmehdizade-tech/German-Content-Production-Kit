# Aspekte B2 — Kapitel 1 R30 / 50 source rows, 100 bilingual example drafts

Date: 2026-11-05. This is a **Stage2 editorial pilot**, not approved Stage3 production, not an accepted flashcard release, and not independent human linguistic QA.

## Concrete production

- Original user-CSV-backed L01 source ordinals **1549–1598**, exactly **50** consecutive rows from **160** in Kapitel 1.
- Authored **two complete German sentences per row (100)** with **100 Persian translations**; distinct example fields, no source-example substitutions.
- Retained the original DE headword, FA definition, original example, source ordinal, original source IDs, R6 correction display and R6 release status in separate CSV fields.
- **Five** of these 50 source rows already had source example text; original example text was preserved.
- All generated content marked `AI_AUTHORED_NOT_USER_CSV` and `AI_EDITORIAL_FIRSTPASS_UNRELEASED`; `importable=FALSE`, `stage3_card_created=FALSE`.
- **Two unresolved earlier-level duplicate gates (#1556 abenteuerlich and #1575 ständig)** remain explicitly open in the 50-row file. **Two source lexical unit/synonym interpretation gates (#1586 vielsprachig / Mehrsprachigkeit and #1588 Vielsprachigkeit)** likewise remain open. No merge or suppression performed.

## Linguistic guardrails for this batch

- #1552 `auflösen` is separable, and two example frames distinguish ending a household and dispersing an assembly.
- #1559 `auswandern` is shown with both destination frames `nach Kanada` and `in die USA`, as attested by [Duden](https://www.duden.de/rechtschreibung/auswandern).
- #1567 `leichtfallen` has a Dativ experiencer and Perfekt `ist leichtgefallen`; see [Duden](https://www.duden.de/rechtschreibung/leichtfallen).
- #1568 `die Erfahrung machen, dass …` is used as a full-sentence pedagogical construction, without imposing the mistaken requirement that it must always be `eine Erfahrung machen`.
- #1574 `Position` is exemplified as a stance and a financial line item, to avoid overrestricting a polysemous noun.
- #1586 keeps original multi-lexeme row content without silently resolving the proposed adjective+noun split. Both source expressions are demonstrated separately across its two examples.
- #1588 remains a separate source row; semantic overlap with `Mehrsprachigkeit` requires explicit later adjudication; do not auto-drop.

## Technical verification

Deterministic local checks passed: exactly 50 ordered source IDs, original source DE/FA/example immutability, all 200 bilingual sentence strings nonblank, all 100 DE examples end with sentence punctuation, all cross-level holds preserved, and no approved/Stage3/Import flags.

CSV SHA-256: `a654a8ecdb5f83539600da8c9ef70ba18253d317cb433d76591b71c6118a64b1`. CSV size **31,339 bytes**. These are **structural** checks and do not independently certify idiomaticity or semantic quality of every translation.

## B2 Library only

`/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Reports/L01-R30-50-SOURCE-BOUND-TWO-DEFA-EXAMPLE-DRAFTS.csv`

Upload succeeded. Stable Library ID `libfile_fab4fdeb105081918b96a3239685b137`. **Do not publish as learner cards.** No user app/SRS, earlier-level project or source CSV modified.

## Release status / next action

- Kapitel 1: examples drafted for **50/160** source rows at 2 each; **110** source rows still need paired draft generation, plus whole-lesson bilingual semantic QA and evidence-based duplicate gates.
- Stage2 **NOT_APPROVED**; Stage3–7 **NOT_STARTED**, final/importable cards **0**.
- Prior R25 chapter-5 portable checkpoint remains the principal portable project ZIP, while this R30 is a narrower **new L01 scoped report**.
