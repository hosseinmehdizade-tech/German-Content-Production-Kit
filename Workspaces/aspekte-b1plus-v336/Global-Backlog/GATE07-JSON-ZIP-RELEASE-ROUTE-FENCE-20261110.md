# Aspekte B1+ — Global Gate07: Native JSON / ZIP preview release-route gap and isolated guard

**2026-11-10 · EXECUTED_SOURCE_EXACT_QA · PRODUCT_NONIMPORT / RELEASE BLOCKED.**
No changes to original app, user profile or 1,571-card curated learner data.

## Authoritative inputs

- **Current GFP app:** v505-R141 WORDLINKS_FRONTBACK_R3, Library current `libfile_ae33f334c1bc8191aa65dd079f710d01`, exact immutable ZIP SHA256 `6f64c7de6027169595bdf18f73dad633a2990bce5270471a95216378474dc7ef`; `01-App/index.html` original SHA256 `f38877d7ff39ad24294303125ae60d77955c251768fffa059cf7452a0a3aef26`. Historical main v486 was **not** used.
- **Current B1+ curated owner UNCHANGED:** Library `libfile_261160dae9508191904f55a410076d40`, ZIP SHA256 `a2fa93f3389b43db12e562331cc3302e24e51f0cb028a494ce61b3e825e6a50b`, primary JSONL SHA256 `829a1d9e16df96cf1467659835f7fcaa14aefa705f7d639910a150e9d37bfe22`. All 359 HOLD statuses and 3,524 DE–FA examples remain in place.
- **New QA-only evidence:** Library `libfile_880e95e6923c8191bd529acd840a3b6a` `Aspekte-B1plus-GATE07-JSON-ZIP-IMPORT-ROUTE-FENCE-NONPROD-20261110.zip`, SHA256 `5729c5ea63c6c161be6d38acced1ab3f4d1c233570b8790f768bf02af070e634`, 10 ZIP members / 9 SHA manifest entries; CRC and Library readback byte-for-byte PASS.

## Actual-current isolated runtime: discovered distinct transport gap

A **single intentionally marked synthetic Native German Content JSON** (contract 3.1.3, one valid example; `b1plus_release_gate:BLOCKED_NONIMPORT`) was accepted as **Preview OK** by the real `GFP_CONTENT_V360.validateNative` (0 schema errors), and accepted in the actual `handleContentSelectionV345` Native JSON preview. The exact same JSON inside an ordinary ZIP was also **Preview OK**, because `GFP_ARCHIVE_V454.resolvePackage` classifies the contained dataset as Native JSON, then the unified selection delegates to the same Native JSON handler. **This is a bypass of the proposed Gate06 TSV-only import fence at Preview, NOT proof of successful import/commit.** The currently staged TSV guard blocks a curated `NONIMPORT` TSV even when wrapped in ZIP; normal unmarked Universal TSV has Preview OK.

## Bounded nonproductive patch proposal + executed checks

- A second REQUIRED source-side guard at **Native JSON Preview** and **Native JSON Submit** in current `01-App/index.html`, separate from Gate06 raw TSV guard. ZIP→Native JSON reuses those handlers, so both entry types are covered by one contract. The guard checks known draft release markers and B1+ `AB1P-` unit IDs, rejecting before any durable work.
- A separate `gfp-b1plus-native-release-fence-v2.NONPROD.js` module is provided in the ZIP with a unified source patch against the **exact unchanged v505 app**, plus two runnable Chromium test scripts.
- **9/9 isolated test observations match expectations:** direct JSON preview/submit blocked, ZIP JSON preview/submit blocked, missing guard fails closed at both handlers, ordinary unrelated Native JSON preview allowed, positive validator case, no browser page errors.
- Staged JavaScript source and guard module pass `node --check`. **No production code was installed, merged or changed.**
- A separate legitimate generic Universal TSV and a valid canonical Native JSON both reached accepted **Preview**. This is more useful than just testing rejected files but **NOT** a successful durable import/restart.

## Open blockers, not waived

1. **Editable marker is not a trusted authorization.** A malicious or accidentally reconstructed dataset can remove/rename `b1plus_release_gate` and circumvent this nonproductive candidate. An app-owner-governed trusted release manifest/digest plus explicit approval is required. Do NOT call this a security-complete guard.
2. Native JSON `importPendingNativeGermanContentV345`, ZIP/JSON/TSV alternative routes and their real durable commit are not end-to-end proven. Every test intentionally avoided user IndexedDB; local origin navigation is blocked by `ERR_BLOCKED_BY_ADMINISTRATOR` in this environment.
3. Native typed multi-sense right-card/Wortnetz Presentation, canonical-rich precedence, SRS preservation, full content semantic QA and all 359 inherited HOLDs remain unresolved.
4. The original curated Gate01 ZIP is an internal JSONL archive, not a guaranteed app import package. Don't equate parser tests on QA transport with a user-ready file.

## Next necessary work

Track this finding in [GFP Issue #40](https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/issues/40). **Stop generating further purely isolated 'gates' until the app owner can review and test native candidate integration under a working browser origin.** The next productive work is a trusted release manifest decision, actual normal TSV+Native JSON+ZIP import with persistent readback, sense-identity right-card regression and full bilingual QA. If no safe origin is available, keep status BLOCKED rather than pretend a test passed. Gate01 curated learner owner remains the sole source of truth.
