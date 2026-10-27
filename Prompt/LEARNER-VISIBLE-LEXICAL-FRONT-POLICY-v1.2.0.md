# Learner-Visible Lexical Front Policy v1.2.0 — governed-construction amendment

Status: **OWNER-REQUESTED OPT-IN CONTRACT**, 2026-10-27. Backward compatible; no silent global exception.

## Existing rules remain binding

HF2 v1.1.0 remains the exact validator for all standard noun, verb, adjective and expression records. The same `de-vocabulary` card type and `gfp-vocabulary-neutral@1` presentation contract remain. No `verb`-class record may escape the HF2 v1.1.0 requirements merely by carrying an invented field or changing `category`.

## Explicit, source-pinned governed-verb-construction subtype

A `category=Verb` card may opt into `hf2_governed_construction_v1` only if its ID is expressly listed in an immutable, exact-input/source-identity registry and the original source front is of the form `clean infinitive + preposition(s) + case` (e.g. `abhängen von + D`, `sparen auf/für + A`). The registry preserves card identity, order, source text, original target, clean lemma and attested principal forms. The opt-in metadata MUST provide the clean lemma separately, source preposition and case, and a full rich/generic presentation string containing **both** the exact construction and all three principal forms. All values are validated against the source and cannot be self-certified by arbitrary metadata.

The source construction **must not be erased** from the front. `typingCore` remains exactly the source construction, not the comma-separated morphology string. Source ID, front, typing target, category, card type, meaning/examples/translations and stable SRS identity must be preserved. For the governed subtype, generic/study/quick projected display is:

`<SOURCE CONSTRUCTION> — <CLEAN LEMMA>, <3SG PRESENT>, <PRÄTERITUM>, <PERFEKT>`

Example: `abhängen von + D — abhängen, hängt ab, hing ab, hat abgehangen`. This combined display must eventually be wired to the actual current app UI; a value in TSV metadata does not prove that UI renders it. Study/Quick must NOT duplicate morphology if they already render a morphology area. Typing must accept the unmodified `typingCore`.

## Gates and migration boundary

The opt-in v1.2.0 validator routes *only registered* governed cards through the pinned subtype contract and runs the unmodified v1.1.0 validator over every remaining card. Both must PASS. A missing, extra, duplicated or reordered source card; changed source front or typingCore; missing morphology; switched case/preposition; unsupported opt-in; or changed generic display fails closed. Existing v1.1.0 validation still reports the 201 governed-card failures by design; this is a versioned policy amendment, **not** retroactively falsifying a v1.1.0 report.

Exact Stage5 requires an approved current payload registry and content/semantic QA. Stage6 requires real current-origin import, IndexedDB/SRS identity, study and quick renders, typing, reload and backup. Stage7 cannot be claimed merely because the amended content validator PASSES. This opt-in is currently limited to `250-verben-mit-praepositionen-kombinationen-repair1-v336`, preserving all other German Content Production Kit workstreams.