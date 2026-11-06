# Aspekte B2 · Kapitel 1 R45 — 4 ID-HOLDs, real current preview delta (NONIMPORT)

Source authority: verified R42/R43 curated B2 drafts; original book/CSV not reopened. Date: 2026-11-06.

## Evidence and actual changes

- B1 user-accepted final package and its 3,088-card TSV were independently fetched from verified owner Drive URL and SHA256 matched the authoritative GitHub handoff (`60ca66...` ZIP / `bcf041...` TSV); read only, no B1 edits.
- Latest A2 R21-R2-R1 content-only ZIP 1,778 cards read and verified (`774b8b...` ZIP, `ca913c...` TSV); not proof of app import.
- B2 158-unit R43 preview (`720154...`) and R42 160-row canonical working (`9da456...`) passed immutable hash checks.
- New **R45 158-row current review** has exactly **2 modified unit IDs**, retaining all 158 distinct draft IDs. New **R45 2-row non-card** retains both facet/reuse objects and updates only their review-gate descriptions. No ZIP duplication; prior R43 stays recoverable.

## Four identity decisions (content evidence ≠ live app/SRS proof)

| B2 ordinal | Verified current content | R45 operational disposition |
|---:|---|---|
| 1575 ständig | B1 final `mb1m-lu-1040` (adverbial) **and** `mb1m-lu-2338` (`ständiger Streit`, attributive). Duden records both under adjective `ständig`. | R45 preview tagged **EXISTING_B1_LEXEME_ENRICHMENT_CANDIDATE**; not independently publishable as second B2 card, exact SRS ID remains uninspected. |
| 1616 die Art | Current A2 content-only `ma2m-lu-0281` (`die Art, Arten`), covers types/manner. | Keep one noun identity with `Fragen jeglicher Art` as collocation; A2 reuse **if actually imported**, else B2 fallback. Fixed plural front and redundant Persian examples, retained all four common sense glosses. |
| 1630 intolerant | B1 final `mb1m-lu-2779` same adjective+meaning, user-reported imported. | Continue **non-card B1 reuse**; strengthened target evidence, but no live SRS proof or B2 duplicate import. |
| 1660 gekommen | Inflected Partizip II of `kommen`. No bare standalone `kommen` card in examined current B1/A2 TSV; do not confuse with `ankommen` or `zusammenkommen`. | Continue **non-card grammatical facet**; specific target identity in A1 or learner profile unresolved. No new `gekommen` word card. |

## Exact changed fields

- Unit `ab2-l01-u-1575`: `unit_policy`, `qa_status`, `note` (3 fields); DE/FA examples and gloss unchanged.
- Unit `ab2-l01-u-1616`: `front_de_preview`, `back_fa_preview`, `example_1_fa`, `example_2_fa`, `POS_or_unit_type`, `unit_policy`, `qa_status`, `note` (8 fields).
- Non-card objects: only `next_gate` for #1630 and #1660 (2 fields).

## QA and safety

- 158/158 preview IDs distinct; 160/160 original curated source ordinals mapped via unchanged R43 coverage; 2 noncard objects and split/alias exceptions retained.
- 158/158 still have 2 DE+FA example pairs; all `export_importable=FALSE`, all `linguistic_release_approved=FALSE`; no original source, B1/A2 content or SRS edits.
- **R45 provides evidence-backed editorial improvement but does not close the 17 historical formal release HOLDs, does not certify independent semantic QA, and does not start Stage3/4/5/6/7.**
- App identity decision requires the actual user-profile/imported-card status. Do not repeatedly reread historical original word lists.

## Current project handoff

- `Current/L01-CURRENT-158-UNIT-REVIEW-R45-NONIMPORT.csv` is the latest owner-local **draft**.
- `Current/L01-CURRENT-2-NONCARD-OBJECTS-R45-NONIMPORT.csv` supplements it; the R42 source working and R43 preview remain unchanged/recoverable.
- `Reports/L01-R45-IDENTITY-DELTA-QA.json` contains hashes, counts, four blocker states and explicit nonclaims.
- Next: targeted verification of accepted A1 `kommen` or live profile ID (if accessible), then independent bilingual QA on changed/affected fields and 13 other outstanding R44 editorial proposals; only after approved Stage2 move to Stage3.