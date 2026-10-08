# Aber Hallo v467-R101 — Independent Deep Final-ZIP Audit (2026-10-08)

## Verdict
**STRUCTURAL/RUNTIME PASS; STANDALONE RELEASE METADATA ADVISORIES.** The exact locked artifact is unchanged.

Archive: `German-Flashcards-Pro-v467-R101-Aber-Hallo-v3.3.6-LOCKED-CONTENT.zip`; SHA-256 `28c255cf898ca8e4bbea346c396c966d11a8dc50be514dedc457474dcf272104`; 366 members; CRC PASS; 365/365 root hashes PASS; zero duplicate paths. Stage6/Stage7 files byte-identical.

Independent validation: 40/40 structural checks PASS; 787 unique cards (647 verbs, 140 adjectives); 3,148 examples each in German/Persian/English with nonblank text; verb tense core 647/647; 920/920 lexical source labels located on the declared pages in the two SHA-verified original PDFs; 926 source-output mappings to 788 targets and no membership mismatch. These mechanical checks do not certify full linguistic quality of every generated learner explanation.

Runtime validation: 169 grammar entries (168 baseline + 1 Aber Hallo), 346 exercises, 4 added examples; fresh Node + Chromium grammar tests PASS; Pomodoro 18/18 PASS; assets 138 refs / 62 static PASS; shell cohort 62 + 3 negative controls PASS; JavaScript syntax 35/35 PASS; inline 3/3 PASS; Vocabulary envelope 21 PASS; v462/v464/v465 browser regressions PASS; 73/73 runtime file parity with v466, CSS and Pomodoro byte-identical.

## Findings
- **F-01, MEDIUM:** `RELEASE-MANIFEST.json` says `grammar_runtime_lessons=168`; actual runtime pack has **169** entries. Stale manifest count.
- **F-02, MEDIUM:** packaged `06-Content/vocabulary/Aber-Hallo-Selected-Pages-v3.3.6/BUILD-METADATA.json` references `ABER-HALLO-CANONICAL-v3.3.6-STAGE5.json` and its digest, but that canonical file is **absent** from the release ZIP. The project may retain it in an earlier checkpoint, but the ZIP-alone reference is dangling.
- **F-03, DOCUMENTED LIMITATION:** card-level CEFR `level` is empty in **787/787** rows; Grammar CEFR is `null`. No unsupported per-card level was invented, but CEFR-based filtering is not offered by this payload.
- **F-04, DELIVERY BOUNDARY:** `02-Source` contains only source lineage/README, no original source PDFs; manifest explicitly states `raw_source_pdfs_bundled=false`.
- **F-05, STANDALONE FINALITY:** embedded manifest intentionally remains `status=CANDIDATE`, `release_final=false`, and pre-postpackage status. Stage7 LOCKED acceptance lives in an external sidecar per immutable-candidate policy; standalone ZIP users need that sidecar to verify finality.
- **F-06, OPERATIONAL:** 787 Vocabulary cards are importable external TSVs, not preloaded in a fresh app database. Runtime-compatible transport is the `...v465-IMPORT-REPAIR1.tsv`.
- **F-07, SEPARATE DURABILITY:** exact v467 `01-App` Git source mirror was PENDING at audit start; no Git-backed full runtime verification claim.

## Environment test boundary
An independent attempt to launch the entire `index.html` through headless Chromium on both temporary localhost and `file://` was rejected by `net::ERR_BLOCKED_BY_ADMINISTRATOR`. Therefore a fresh actual 787-card end-to-end import/persistence run on this v467 candidate was **NOT TESTED**, not falsely marked PASS. Isolated grammar Chromium and historical/unchanged import contract tests did PASS.

## Disposition
Preserve locked semantic content and exact hash. Repair F-01/F-02 only in a properly versioned, freshly sealed successor (or separate corrected handoff metadata where valid); do not silently patch the locked ZIP. Re-run exact real-origin import/persistence acceptance where access is permitted. Record explicit limitations for CEFR and unbundled PDF. No content regeneration is justified by these findings.

Full downloadable independent machine-readable reports were also produced in the conversation artifact workspace.
