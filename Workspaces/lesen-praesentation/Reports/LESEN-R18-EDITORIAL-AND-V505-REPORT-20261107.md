# Lesen R18 — 26 Schlussfolgerungen in 15 Lerneinheiten (053–068)

**Status:** Scoped authoring and structural QA PASS; content remains **CANDIDATE**, not native/final release.

## Source and scope

- Parent is user-curated R17 (SHA256 `593deb6e5ec7cdba2d95f7445589ae5bf6cf17750eb0f8cdbb9c3f4f1a605ad7`), **not** an older textbook PDF.
- 26 previously identical concluding German sentences in p02-s03/p03-s03 rewritten individually in units 053–058 and 060–068. Already improved unit 059 preserved.
- Seven already-specific Persian and English concluding pairs preserved exactly; 19 generic pairs rewritten in both FA and EN. The original first two sentences in all 26 sections remain unchanged in all three languages.
- 53 of 68 units and all 340 question identities, 350 vocabulary entries, and 669 curated grammar IDs remain exact.
- **All previously identified identical generic conclusions p02/p03 now absent (0 + 0).** This is an exact-string observation, not a declaration that every passage has high educational quality.

## Grammar (scoped)

- Previously: 4,097 full-text grammar occurrences. Removed **82 obsolete** spans formerly attached to replaced generic sentences.
- Added **26** manually checked, actually occurring relative clauses, subordinate clauses, or `ohne … zu` infinitive groups, with exact offsets; **11** existing g06 relative-clause curated examples retargeted to real new relative clauses.
- **Now 4,041 exact fulltext occurrences.** Original full nine-lens grammar extraction was **not** rerun.

## QA and compatibility

- Independent structural/source/runtime checks: **12,769 / 12,769 PASS**, 0 errors. Adversarial mutation probes: **9/9 rejected**.
- Exact current v505 source `reading-content-import-v38.js`: **PASS**, 0 warnings, 7 malformed-input probes rejected; isolated in-memory projection 68 units and 340 exercises.
- No browser IndexedDB transaction; no Stage6 or independent holistic Stage4, no Stage7 final release.
- Both main candidates must pass independent post-upload Library SHA and byte CMP prior to durable Git checkpoint finalization.

## Remaining issues after eliminating the old p02/p03 generic endings

- Wholepack exact repetition audit found **58 identical occurrences in p06-s02** and many repeated p07 synthesis formulations and p01 framing sentences. Those require topic-by-topic semantic review rather than mass synonym replacement.
- The DE/FA/EN wholepack semantic Stage4 and original complete nine-lens grammar regeneration remain open, along with real native browser Stage6.

## Candidate outputs

- Content: `Lesen-Production-Master-v1.3.0-R18-26CONCLUSIONS-TRILINGUAL-CANDIDATE.json`, SHA256 `bfd469d4027f59d97cb25baabbefd79b0576f47f13acdc965f82850fc8a63c37`
- Runtime preentry: `Lesen-R18-v505-26CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json`, SHA256 `a4d9669ff3db155380a69c74dcad5006d307e68718abdf8fa8a24fe83c64fe9f`
- Source-specific before/after: `LESEN-R18-26CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json`
- Trilingual scoped ledger: `LESEN-R18-TRILINGUAL-SCOPED-REVIEW.json`
- Wholepack repetition/risk audit: `LESEN-R18-WHOLEPACK-TEXT-RISK-AUDIT.json`
- Independent and v505 machine reports: `LESEN-R18-INDEPENDENT-SOURCE-QA.json` and `LESEN-R18-v505-NATIVE-PREENTRY.json`

**Original current v1.3.0 ZIP remains unchanged:** SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`. No app UI, user SRS/FSRS or other family changes.