# Aspekte B1+ — Global Gate05 raw TSV ingress guard (NONPROD)

**Date:** 2026-11-10. **Status: SOURCE-EXACT ISOLATED QA COMPLETED, NOT INSTALLED/NOT RELEASED.** User-current app and all learner records remain unchanged.

## Verified authorities

- **Current curated learner owner:** Library `libfile_261160dae9508191904f55a410076d40`, archive `Aspekte-B1plus-GLOBAL-BACKLOG-GATE01-1571-CARD-REPAIRS-NONIMPORT-20261110.zip`, SHA256 `a2fa93f3389b43db12e562331cc3302e24e51f0cb028a494ce61b3e825e6a50b`, primary `829a1d9e16df96cf1467659835f7fcaa14aefa705f7d639910a150e9d37bfe22`. Do not promote.
- **Current app:** v505-R141 WORDLINKS_FRONTBACK_R3 Library ZIP SHA256 `6f64c7de6027169595bdf18f73dad633a2990bce5270471a95216378474dc7ef`; exact `01-App/index.html` SHA256 `f38877d7ff39ad24294303125ae60d77955c251768fffa059cf7452a0a3aef26`. Historical main app is not current.
- **New evidence:** Library `libfile_6fa7e4a4629c81918ac7bd488dc69e73`, `Aspekte-B1plus-GATE05-RAW-TSV-IMPORT-GUARD-26-ASSERTIONS-NONIMPORT-20261110.zip`, SHA256 **`ffee4505ca9fba2de8fe7e632bc32fbacc30273334bd6180556d0f183b9bfcb8`**, 8 evidence members, ZIP CRC / all 8 manifest SHA / exact Library byte readback PASS.

## Root cause, confirmed using the exact current parser

The QA-only transport TSV for **real ordinal 363** (`alle / alles / aller-`) was deliberately modified to contain two rich examples with **identical stable example ID** but conflicting `sense_ids`. The **original current GFP parser** `GFP_CONTENT_V360.parseTsvText` silently normalized the 4 raw entries into only 3; after that, inspecting parsed cards cannot tell the conflicting source ever existed. This is why a post-parse validator is insufficient. This does NOT claim the native durable import succeeded, because no real import commit or `auditCards` was run.

## Implemented NONPROD pre-parser guard (not app source)

- Reuses the current app's **exact native raw TSV tokenizer** `parseTsv` as a required passed callback; inspects `custom_fields` JSON **before** normalization. Does not implement a competing TSV parser.
- Explicitly blocks: duplicated/empty stable example IDs; contradictory `canonical` vs `rich` identity, translations and sense routes; malformed/duplicate/unknown plural sense links; duplicate network senses; and `BLOCKED_NONIMPORT` B1+ preview metadata by default. An isolated test-only `allowQaOnly:true` allows verifying draft data; NEVER use it for productive import.
- **26/26 browser test observations PASS** using current R3 app, including true source conflict, mutation controls, QA corpus passes and deliberate NONIMPORT fence checks. One set of tests explicitly confirms the **baseline silently loses duplicate evidence**; not a release acceptance condition.
- **Whole raw TSV preflight** in isolated QA mode: 1571 cards, 3524 bilingual example pairs, 1097 sense blocks, zero new problems. With default production mode, all 1571 B1+ cards remain blocked until formally authorized.
- Exact source integration patch proposal targets **two and only two** callsites in current `01-App/index.html`: TSV preview and TSV import submit, both **before** `GFP_CONTENT_V360.parseTsvText`. Source anchors match 1 each. Full original modified inline app JS passed `node --check`. No script was installed into original runtime, no durable mutation was tested.

## Immutable outputs & next owner decision

- Reusable guard source kept as [NONPROD JS module](../Tools/gfp-b1plus-ingress-guard-v1.NONPROD.js); application owner [Issue #40](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/issues/40).
- Required import checks after app-owner integration: current runtime sources, ready-to-parse raw TSV, QA-only rejection, duplicate/contradictory source rejection **before** dedup, legitimate normal TSV unchanged, and actual origin-backed durable write/restart.
- Still **not tested or fixed:** right-card typed Wortnetz projection and click target IDs; current runtime canonical/rich precedence integration; actual SQLite/IndexedDB (app uses browser persistence) save/restart, SRS state preservation, real import or formal linguistic quality acceptance. The native durability-audit API was unavailable in the isolated HTML harness. Keep all 359 HOLDs.

**Decision: GATE05_INGRESS_CANDIDATE_VERIFIED; APP_INTEGRATION_AND_RELEASE_BLOCKED_NONIMPORT.** Do not regenerate card data from publisher sources, make another curated ZIP or re-run L10 phases. Proceed with app-owner review of Issue #40 and actual native testability, without asserting false completion.
