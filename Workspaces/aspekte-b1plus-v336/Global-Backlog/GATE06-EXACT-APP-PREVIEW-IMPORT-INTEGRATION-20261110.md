# Aspekte B1+ — Global Gate06: exact-current Preview & Import handler integration

**Date:** 2026-11-10  
**Status:** EXECUTED_NATIVE_FUNCTION_ISOLATED_QA_PASS / STAGED_ASSET_QA_PASS / **PRODUCT RELEASE BLOCKED (NONIMPORT)**  
**Source changes to app default branch:** **0** · **Curated learner data changes:** **0**

## 1. Exact sources

- **Current app:** German Flashcards Pro **v505-R141 WORDLINKS_FRONTBACK_R3**, immutable user-current Library ZIP `libfile_ae33f334c1bc8191aa65dd079f710d01` SHA-256 `6f64c7de6027169595bdf18f73dad633a2990bce5270471a95216378474dc7ef`. The original `01-App/index.html` SHA-256 is `f38877d7ff39ad24294303125ae60d77955c251768fffa059cf7452a0a3aef26`. Historical `main/01-App` v486 is **not** current and was **not** patched.
- **Aspekte B1+ curated data:** immutable Library `libfile_261160dae9508191904f55a410076d40` (Global Gate01 1,571-card owner), ZIP SHA-256 `a2fa93f3389b43db12e562331cc3302e24e51f0cb028a494ce61b3e825e6a50b`; primary JSONL `829a1d9e16df96cf1467659835f7fcaa14aefa705f7d639910a150e9d37bfe22`; original 359 HOLDs preserved. Neither archive was rewritten.
- **New exact-byte evidence owner:** Library `libfile_c98a133b51d081919aacc592011bc12d`, `Aspekte-B1plus-GATE06-REAL-IMPORT-HANDLERS-NONPROD-20261110.zip`, SHA-256 `8bc615fb95fb16e64eee97e331ad98d5beb1379c443471a27ff4d87854d459d0`. 11 ZIP entries / 10 SHA256 manifest records, CRC PASS, exact Library byte readback PASS.

## 2. Actual improvement beyond Gate05

From exact-current `index.html`, the original `handleTsvSelection` (Preview) and `importPendingTsv` (Submit) functions were executed **themselves** via a disposable test-only hook into the native closure, with the Gate05 proposed raw TSV guard injected at each **source-exact** callsite before the original `GFP_CONTENT_V360.parseTsvText`.

Controlled in-memory current-runtime Chromium cases:

| Input | Original parser calls | Entered native durable mutation? | Result |
| --- | ---: | ---: | --- |
| 3 real curated B1+ NONIMPORT cards — Preview + Submit | 0 | 0 | Rejected for NONIMPORT |
| 3-card fixture with duplicated example ID and conflicting `sense_ids` — Preview + Submit | 0 | 0 | Rejected for raw duplicate **and** NONIMPORT |
| Ordinary unrelated but incomplete TSV — Preview + Submit | 1 per handler | 0 | Guard allowed; original schema parser rejected invalid educational fields |
| Missing Guard runtime dependency — Preview + Submit | 0 | 0 | **Fail-closed**; explicit missing dependency error, not bypass |
| **Full curated 1571-card** TSV — Preview + Submit | 0 | 0 | Blocked all 1571 as NONIMPORT (in-memory test time ~490ms) |

This is stronger than isolated Guard unit tests: both actual production function bodies and exception handling paths executed. **It still does not prove a successful real import or storage durability** because every rejected input stopped before commit by design.

## 3. Real staged asset, no patch promotion

A reproducible hash-locked builder applied only **three narrow changes** to the original source (two callsites plus one required synchronous Guard script in `<head>`) and created **two staged files**:

1. A staged copy of `01-App/index.html`, SHA-256 `8539de8b1197e23ab890eb0b4b728c4cf9ae90020c28491479eb514116145383`.
2. `01-App/modules/gfp-b1plus-ingress-guard-v1.NONPROD.js`, SHA-256 `d221a208c64659cd3d3dbb3c094dd4b11f7dce336cdae7bac50e71b189ac6130`.

The **actual changed original inline script passed** `node --check`. The staged HTML plus **39 exact original runtime JavaScript assets** (including the required Guard, in original dependency order) was loaded into a disposable headless Chromium document. Both native Preview and Submit rejected curated and conflicting samples before the parser; no JS page errors occurred. It was **not packaged as an installable app**, merged or deployed.

The evidence archive contains the exact 28-line unified diff, nonproductive Guard JS, reproducible builder, two browser test scripts, and machine-readable 20/20 scoped assertions. App owner issue: [German Flashcards Pro #40](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/issues/40).

## 4. Critical limits and next decision

- This Guard rejects B1+ markers, but those editable markers are **not cryptographic authorization**; a trusted release manifest or signed sidecar is needed for a robust release gate.
- Valid generic TSV's *native success path* has not been demonstrated. One deliberately incomplete generic TSV reached the original parser and failed in schema validation. **Do not infer universal TSV backward compatibility** from that observation.
- The exact guard handles the tested TSV callsites only. Other import surfaces (JSON, ZIP, Reading Pack) have not been instrumented or covered.
- No stable-origin IndexedDB write, persisted restart, SRS progress migration, or native right-card/Wortnetz multi-sense display test was possible/finished. Existing Gate03/04 canonical-rich and typed sense blockers remain open.
- All **1,571 curated cards, 3,524 German–Persian examples and 359 HOLDs** remain unchanged. Release remains **BLOCKED_NONIMPORT**.

**Next substantive step (Gate07 / app owner #40):** do not repeat previous Gate01–Gate06. Broaden native ingress routing coverage; establish a trusted release-authorization source; validate legitimate success-path TSV and ZIP/JSON imports in a supported origin, then native typed right-card and durable save/restart / SRS. If a compatible origin is not available, state it as blocked rather than claiming acceptance.
