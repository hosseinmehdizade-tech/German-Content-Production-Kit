# Lesen — R8 question-level editorial + v505 pre-entry acceptance

**Date:** 2026-11-07  
**Canonical family owner:** `Workspaces/lesen-praesentation` · `family:lesen`  
**Status:** `R8 EDITORIAL CANDIDATE / SOURCE-BOUND STRUCTURAL QA PASS / NATIVE v505 PREENTRY PASS / SEMANTIC STAGE4 + NATIVE BROWSER STAGE6 + RELEASE STAGE7 HOLD`

## Authority and preservation

- **CURRENT remains unchanged:** `Lesen-Praesentation-B2-C1-v1.3.0-CONTENT-PRODUCTION-DELIVERY.zip`, SHA-256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565` in `Content/Lesen/Current`. This is the currently pinned owner editorial baseline, not a claim of Stage4–7 FINAL.
- **Immediate editable parent R7, not the original textbook:** `Lesen-Production-Master-v1.3.0-R7-20UNIT-Q123-CANDIDATE.json`, SHA-256 `f472a6260b29f7112bfdf71894f1004957ade61d8ec9bc842992f5a6e4c718d9`.
- Runtime parent R7, SHA-256 `043126b22cc256a911ec9697888b5f944a4520ddb3e22ef74de423abc3c9c6b3`.
- **R8 source-content candidate:** `Lesen-Production-Master-v1.3.0-R8-18UNIT-Q123-CANDIDATE.json`, SHA-256 `f3e22d1f62aa78590f44ccfe358a9240319a99c9d8a1f39fc8a1ee81ac6d4cf2`, 6,623,102 bytes.
- **R8 v505 runtime pre-entry candidate:** `Lesen-R8-v505-18UNIT-Q123-RUNTIME-CANDIDATE.json`, SHA-256 `da770588aee670e60cf985dbfdcfd4fe0715847b43822f214ce90ba27bba4608`, 7,131,690 bytes.

## Actual editorial work

- Reviewed the **18 lessons LES-PRES-051..068** against the R7 curated passages, not raw-source word inventories.
- Rewrote **50 question prompts and 50 German model answers** under q01/q02/q03; for the already specifically corrected LES-PRES-051 and LES-PRES-059, **four q02/q03 prompts and answers were preserved exactly**.
- All 68 lessons now have **distinct q01, q02, q03, q04 prompts** (`68/68` distinct per question position); q05 is an open-transfer question and is intentionally not subject to this uniqueness goal. Distinct prompt text alone is not independent semantic or pedagogy certification.
- All nonquestion content, q04/q05, 478 DE+FA+EN reading sections, all sentences and full-text grammar positions, 340 durable question IDs, lesson IDs and previous editorial modifications 001..050 remain **unchanged**.
- Evidence with exact source `p01`/`p02`/`p03` passage text, before/after pairs, and question IDs is in `Reports/LESEN-R8-50Q-SOURCE-EVIDENCE.json`. Evidence is scoped AI editorial grounding, not human-independent linguistic QA.

## Independently executed acceptance

- Read-only `Tools/verify_r8_independent.py`: **7,480 of 7,480 structural and transport conditions PASS**, **9/9 negative mutations rejected**. These include exact R7→R8 approved delta, stable question and section IDs, cross-language text preservation, **4,620 of 4,620** exact grammar offset/target matches, **478 of 478** section checks, runtime question/answer parity, whole-pack integrity hashes and unchanged prior accepted source/editorial content.
- Exact **v505 Wordlinks R3** `01-App/modules/reading-content-import-v38.js` source validator (pinned module SHA-256 `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc`) **PASS, zero warnings**, with **6/6 malformed-input checks rejected**. The validator executed in Node's isolated VM and tested in-memory projection, **not** a real browser/IndexedDB transaction.
- The independent QA initially (correctly) caught two overly strict assumptions in the new verifier: R7's top-level `status` did not change and historic already-accepted q05 answer guidance can be brief. The test was corrected to compare the exact changed root fields and to permit inherited short answers. The affected R8 new Q/A pairs are separately constrained to longer meaningful responses. This is a test-tool correction, **not** content mutation to obtain green QA.

## Known remaining risks

- **55 p04 reading passages** still begin with the same generic construction (`Entscheidend ist deshalb die konkrete Ausgestaltung.`); R8 does not touch the text. These need individual editorial review, not a bulk text replacement that breaks grammatical offsets or translations.
- Many q05 model-answer grading guides repeat a generic phrase; personal-opinion answers are a distinct open-response contract and should be evaluated for instructional usefulness, not blindly rewritten for uniqueness.
- Independent holistic Stage4 DE–FA–EN semantic and didactic review **HOLD**. Three earlier revised reading passages need final human-level semantic verification. The original native full nine-lens grammar generator was **not rerun**.
- Official native compiler/full Stage5 not invoked; transport is a verified **question-only bounded delta** from parent runtime, not a full compiler replacement.
- Native **Stage6 browser import/IndexedDB transaction, reload, UI, SRS/FSRS preservation not executed**. Stage7 FINAL not released.
- **No app/runtime code, CURRENT, original source, user SRS/FSRS or user profile was modified; no Library files deleted.**

## Next bounded work

Address p04 templating in a small **evidence-led** batch (e.g., 8–12 units) with simultaneous DE/FA/EN and full-text grammar anchor regeneration or explicit relocation, plus independent semantic QA. Do not mechanically replace p04 across 55 lessons or silently reuse stale offsets. Separately, when an isolated permitted browser environment is available, test native Stage6 and user-data-preserving roundtrip. Maintain `CURRENT v1.3.0` and `R8 candidate` as distinct authorities.