# Lesen – R4 runtime transport / exact v505 pre-entry check (2026-11-07)

**Scope:** 68-lesson Lesen Präsentation B2–C1. **Result: source-verifiable runtime JSON candidate, not final.**

## Authority and fixed inputs

- Immutable CURATED_CURRENT is the `v1.3.0-CONTENT-PRODUCTION-DELIVERY.zip` in `/Flasch kart/German-Content-Production-Kit/Content/Lesen/Current`, SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`.
- Parent R3 edited content: `Lesen-Production-Master-v1.3.0-R3-3UNIT-GRAMMAR-CANDIDATE.json`, SHA256 `2b7e29acb973d34e878f76df5135be740c0819934b457265a1fd281ca97c2a8e`. Only LES-PRES-035, 051 and 059 were revised; 55 lessons remain educational review backlog.
- Exact current user-accepted app v505-R141 Wordlinks R3 ZIP SHA256 `6f64c7de6027169595bdf18f73dad633a2990bce5270471a95216378474dc7ef`. Pre-entry code module `01-App/modules/reading-content-import-v38.js` SHA256 `b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc`.

## New artifact

`Lesen-R3-v505-PREENTRY-RUNTIME-CANDIDATE.json` (7,124,419 bytes), SHA256 `53b2746c2ed2ee6938773d850ccc8a287f2d81608422a38aba481ef059ebc683`, Library `Content/Lesen/Candidates`, ID `libfile_6e4143b48a388191a26807fd6f2749c9`, **byte-for-byte re-readback PASS**. Schema `lesen.runtime.v1.0.0`.

Unlike rewriting the 68 original runtime records, the transport builder independently checks the exact historical compiled master and its original `entries_sha256`, retains the 65 unmodified compiled entries untouched, projects only the three changed entries from R3, and rechecks the entire 68-entry output against the R3 source. Historical R41 compiler identity is NOT claimed for the delta transport. Entries SHA256 and a separately defined whole-payload (excluding the integrity field) SHA256 are added and reproducible.

## Evidence

- **Exact original runtime/master mapping:** all 68 original entries and original hash checked.
- **Source-to-runtime field parity:** 68 units, 478 German sections with Persian/English translations and preserved sentence IDs, 340 question prompts/answers/evidence references, 350 inline vocabulary items, 669 curated grammar annotations, and 4,620 offset-checked fulltext grammar occurrences.
- **Current app source validator:** actual code from the exact v505 ZIP returns PASS, zero warnings for candidate. Six negative corruptions (duplicate ID, missing FA, mismatched question reference, bad grammar offset, empty answer, incorrect grammar count) are rejected. In isolated JS VM, `validateRecord` + `adoptCommittedMirrorV505` project 68 units and 340 questions. No browser/DB mutation is performed.
- **Library integrity:** exact candidate bytes re-materialized and `cmp` + SHA256 PASS.
- Reproducible read-only tools under `Content/Lesen/Tools`: `build_lesen_r3_runtime_candidate.py`, `verify_lesen_r3_runtime_candidate.py`, `verify_v505_native_source_preentry.js`.

## HOLD and next acceptance

**This is not Stage4 full linguistic PASS, Stage5 official FINAL, Stage6 actual installed native-browser import, or Stage7 release.** Original nine-lens grammar engine was not located or rerun; R3 only has scoped exact-offset grammar QA. The other 55 templated reading units have unresolved educational quality concerns, and the previous eight word-count metadata drifts remain recorded. Native browser import/persistence and semantic acceptance are separate gates. Do not deploy this candidate into a user's live Reading data until a disposable-profile test and authorized acceptance.

**Next actionable work:** validate the R3 candidate in an isolated real browser profile (Reading import + sections/questions/grammar + IndexedDB persistence/reload and rollback), independently check repaired multilingual claims and address remaining 55 lessons in meaningful quality batches, then package only the accepted successor. No UI, app code, SRS/FSRS, published CURRENT, source or historical LOCKED changed.