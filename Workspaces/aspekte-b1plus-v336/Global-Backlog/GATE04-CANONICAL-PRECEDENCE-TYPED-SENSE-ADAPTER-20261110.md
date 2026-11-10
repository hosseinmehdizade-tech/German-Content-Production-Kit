# Aspekte B1+ — Global Gate04 (2026-11-10)

**Status: ISOLATED_EXPERIMENTS_COMPLETED / NATIVE_APP_AND_DURABLE_INTEGRATION_BLOCKED / NONIMPORT**

## Proven current authorities, unchanged

- **B1+ curated learner owner (1571 cards):** Library `libfile_261160dae9508191904f55a410076d40`, ZIP SHA256 `a2fa93f3389b43db12e562331cc3302e24e51f0cb028a494ce61b3e825e6a50b`, PRIMARY SHA256 `829a1d9e16df96cf1467659835f7fcaa14aefa705f7d639910a150e9d37bfe22`. No changed card data or status.
- **Current app:** GFP v505-R141 R3, Library `libfile_ae33f334c1bc8191aa65dd079f710d01`, exact ZIP SHA256 `6f64c7de6027169595bdf18f73dad633a2990bce5270471a95216378474dc7ef`. No app source commit, promotion or deployment.
- **New owner-local evidence:** Library `libfile_d284c7df656081919defd543111c0954`, ZIP `Aspekte-B1plus-GATE04-CANONICAL-SENSE-IDENTITY-ISOLATED-QA-NONIMPORT-20261110.zip`, SHA256 `c209efe020a60951b8284d7fca426e5f26947edbb16211420a449b9b83a1af1f`, 8 ZIP members, 7 verified SHA256 entries, CRC PASS and exact Library byte readback PASS.

## Executed controlled tests

1. **Canonical/rich precedence under exact current code:** Gate03's three edits were applied to an in-memory HTML test document, then a fourth isolated candidate was added to `presentationExampleGroupsForModeV348`. For canonical groups lacking plural `sense_ids`, it proposes copying explicit IDs from rich examples only when **one** candidate has the exact same ID, German text, language, full translation list and compatible scalar `sense_id`. No text-only guessed joins, no override of explicit canonical IDs.
2. **Real learner ordinal 363** (`alle / alles / aller-`): S1+S2 survive before/after compaction for exact matching canonical/rich examples. Unrelated translations, conflicting scalar IDs, mismatched stable IDs or absent rich data do not acquire invented associations.
3. **16/16 expected test observations in headless Chromium**, including a reproduced **remaining negative problem**. Do **NOT** interpret this number as 16 native release acceptance passes. A synthetic duplicated rich example is rejected **before** compaction, but the runtime can collapse the source duplicates so the ambiguity no longer remains detectable **after** compaction. Native import MUST reject conflicting duplicate identities at ingress before this transformation. This weakness is still **NOT FIXED** in actual app.
4. **Entire curated dataset preflight:** all 1571 cards, 3524 DE–FA example pairs, 713 network-bearing cards, 1097 sense blocks, 2122 sense-anchored lexical relation entries examined; 0 invalid sense routes, 0 contradictory repeated equal DE+FA example pairs, 359 inherited HOLDs preserved; **9/9 data checks PASS**.
5. **Typed right-card preview:** separate QA-only Chromium DOM test for one real multiple-sense card, retaining exact `data-sense-id` for each section and associated relation, using `textContent`. No fake clickable targets. This **does not** prove that the current native card's Wortnetz panel projects or links all curated networks.

## Blockers, deliberately unresolved

- Ingest preflight for duplicate/conflicting example identities is not yet a native importer guard.
- Native current right card/lexical link, visual sense grouping and multiple target resolution were not integrated or tested.
- Stable-origin IndexedDB/localStorage navigation testing is denied in this environment (`ERR_BLOCKED_BY_ADMINISTRATOR`). No real durable save/restart test passed; in-memory testing is insufficient.
- No complete bilingual idiomatic QA or formal content release signoff. **All 359 HOLDs unchanged; release remains BLOCKED_NONIMPORT.**

## Next bounded step: Gate05, app-owner integration evidence

Coordinate with [app issue #40](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/issues/40) to make ingress validation mandatory, decide conflict/precedence behavior in the exact current runtime, integrate an actual native typed sense-anchored right card, and run durable origin-backed save/restart across Study/Quick/Typing. If a supported environment is unavailable, keep durable work explicitly BLOCKED rather than repeating useless origin navigation attempts. The B1+ content owner is unchanged. Do not cycle back through earlier lessons or regenerate source from textbook/CSV.

**Evidence content** inside the Library ZIP: `GATE04-SUMMARY.md`, `GATE04-CANONICAL-STRICT-IDENTITY-TEST.json`, `GATE04-EXACT-IDENTITY-ISOLATED-PATCH.json`, `GATE04-NETWORK-AND-AMBIGUITY-PREFLIGHT.json`, `GATE04-TYPED-NETWORK-PREVIEW-ONLY.json`, two reproducible QA scripts and SHA manifest.
