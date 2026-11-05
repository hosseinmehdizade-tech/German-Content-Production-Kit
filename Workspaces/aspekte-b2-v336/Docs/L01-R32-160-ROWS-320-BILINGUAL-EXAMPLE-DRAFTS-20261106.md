# Aspekte B2 — Kapitel 1, R32: bilingual example drafting complete

**Date:** 2026-11-06 · **Scope:** exclusively `Workspaces/aspekte-b2-v336/` and B2 Library.

## Outcome

- **160/160** exact user-CSV source rows in Kapitel 1 (source ordinals **1549–1708**) now each have **two** newly AI-authored German full-sentence example drafts and **two** Persian translations.
- R32 added the remaining **60** rows (`1649–1708`), exactly **120 DE sentences** and **120 FA translations**.
- Cumulative draft output: **320 DE sentences + 320 FA translations**, across all **160** source records. Original German headwords, original FA meanings, and **13** original example strings preserved separately byte-for-byte against R6 source-bound overlay.
- The generated sentences are labeled `AI_AUTHORED_NOT_USER_CSV` and `AI_EDITORIAL_FIRSTPASS_UNRELEASED`. **Zero cards created, zero approved for import, zero source mutations and no actual merges or suppressions.**

## Source and release gates preserved

- Five previously recorded lower-level accepted-card proof gates **#1556, #1575, #1609, #1630, #1671** are still unresolved. The R32 output does not suppress any of these.
- Other source-context and learner-unit issues from this final batch are flagged at **#1671 zerreißen** (transitive `hat zerrissen` vs intransitive `ist zerrissen`, B1+ identity), **#1675 einig** (agreement construction), **#1693 Juryvorsitz** (chairship versus chairperson) and **#1697 Kinokasse** (standalone lower-level learner-unit status).
- Earlier source duplication **#1640/#1641 Migrantenfamilie** has both immutable CSV records retained. Distinct draft sentences do **not** justify two canonical import cards.
- Specific editorial usages in R32: `fernliegen` has Perfekt `hat ferngelegen`; `entstammen` governs Dativ and Perfekt `ist entstammt`; `in Windeseile` and `mit Windeseile` both preserved; `entsprechend` shown with Dativ preposition and adverbial use. Contextual examples do not certify all source senses.

## R32 verification

Deterministic checks on the locally generated R32 cumulative sheet:
- Exactly **160** unique IDs, exactly ordinals `1549..1708`.
- Original headword / FA definition / example strings identical for each row against the prior R6 source overlay.
- Exactly **320** nonempty, distinct DE example sentences and **320** nonempty FA translations, two of each per source row.
- The 60 R32 draft rows contain 120 DE and 120 FA examples; prior 100 rows remain untouched.
- All rows have `importable=FALSE` and `stage3_card_created=FALSE`.
- After uploading, each CSV was downloaded/materialized afresh from Library and compared byte-for-byte against the locally built file; **exact matches**.

## B2-only Library artifacts

**Current complete draft sheet** (overwrites previous R31 version in same B2-only Library path):
`/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Current/L01-EXAMPLE-EDITORIAL-WORKING-160.csv`
- Stable Library ID: `libfile_0e3ba6a83e3481918c689f7a80794aca`
- SHA256: `50297fddcc6c3f46592956df415e2c4c9c22613e18c69d76b72b06a632e0ea1c`
- Size: `100858` bytes.

**R32 incremental 60-row sheet**:
`/Flasch kart/German-Content-Production-Kit/Content/Aspekte-B2/Reports/L01-R32-60-SOURCE-BOUND-TWO-DEFA-EXAMPLE-DRAFTS.csv`
- Stable Library ID: `libfile_e87112bb7c5c8191a5ce758991980138`
- SHA256: `f6baa3b562f6f1d719e953ef7c7f3edbb93eecb36d3d4c549af8e85015f3862c`
- Size: `37978` bytes.

**QA interpretation:** structural traceability and completeness PASS; **independent German–Persian semantic quality / pedagogical acceptance NOT PASSED or claimed**. Full 160-entry independent bilingual QA (including morphology, meaning and generated-example idiomaticity) and five accepted-card identity gates still pending. This remains a Stage 2 **editorial draft**; Stage 3–7 **NOT STARTED**. The global project R25 L05 ZIP remains the most recent fully portable checkpoint; R32 is the current narrower L01 content-draft progress.
