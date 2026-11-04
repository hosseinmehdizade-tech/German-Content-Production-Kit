# RELATED / VERWANDT — Precise semantic role and no-duplicate projection v1.0.0

**Approved 2026-11-04 for new mutable lexical production and separately labeled successors.** Historical registered source, user-imported data, IDs, LOCKED packages and all SRS are immutable. Apply with the same one-pass Stage3A/B/C and independent risk-based Stage4; no new manual review round or density quota.

## Role boundaries

- `Verwandte Wörter` / legacy `Verwandt` is a **learner-visible semantic or topical relatedness category**, not a fallback for every linked expression, translation, collocation or example sentence.
- `Wortfamilie`: verified derivational family of a lemma. Prefer already evidenced typed `WORD_FAMILY` with exact target ID; free-text words without a target remain visible only when independently source-validated; do not invent graph edges.
- `Synonyme`: genuinely sense-substitutable in the relevant context (not general topical proximity). Use typed `SYNONYM` where established; preserve register/sense differences.
- `Antonyme`: genuine sense-specific opposites. Do not derive antonymy by string negation.
- `Kombinationen`: **concrete useful reusable phrases** with varied structural categories and real didactic delta, following source-first v1.2. Keep DE/FA/EN as one structured item. `COLLOCATION`, `NVV`, `REKTION` backend typing/provenance stay distinct.
- `Beispiele`: fully translated sense-aligned complete sentences under established example profile; do not append full sentences to examples simply because they were previously listed in `Verwandt`. A full-sentence target may be its own expression / Redemittel card and link in Wortnetz.
- `RELATED`: genuine non-equivalent contextual/semantic relation. A typed edge is **not** license to show exactly the same item in different right-side tiles. Keep `RELATED` edges untouched unless targeted independent linguistic and source review justifies a typed replacement.

## Machine-safe handling

1. On exact normalized German string match to accepted existing `Kombinationen`, hide the redundant learner-facing `Verwandt` copy; retain original source, review evidence, structured accepted combination and graph.
2. On exact match to the **same card's** established example, hide only the redundant right-side copy; do not remove/renumber examples or invent translated equivalents.
3. On exact target ID + target headword/visible form match, with pre-existing typed canonical `WORD_FAMILY`, `SYNONYM` or `ANTONYM`, the physical learner-facing item can be moved into the matching section; do not alter graph edges, target IDs or source provenance. If conflicting types, HOLD.
4. For punctuation, multiword expressions, very long items, unlinked text or different semantic meanings: produce `HOLD` for targeted independent semantic QA. Never auto-convert sentences, all related phrases, or fuzzy-close strings into a different type.
5. The `Custom` section must not absorb unknown typed relations due to serializer mapping faults. A separate runtime fix needs exact app authority and tests before claiming its UI corrected.
6. Any source-derived successor must record parent SHA256, exact edited card IDs, changed columns, retained typed graph, and negative mutation checks. Stage4 acceptance, Stage5 projector, Stage6 actual browser and Stage7 package/promotion are separate mandatory gates.

## Existing A1 V24 targeted pilot

Exact user ZIP parent SHA256 `19a9edb447286e4d5bb796a882da471cb666f39f81acfcc0c0b9c69a937d19ff`; 2997 cards. 75 cards get precisely justified display-content successor changes, 91 duplicate related-items hidden in the successor, 18 moved into typed `Wortfamilie` or `Synonyme`, 6 field-level combo item removals in 3 cards. 142 unresolved items are held for targeted QA. **No V24 source or LOCKED mutation; V25 successor is pre-Stage4 and not import-ready.**

## Cross-source rollout

- Apply on next SAFE editable source/lesson boundary in Menschen A2/B1 and lexical streams using current source-specific CHECKPOINT and exact parent hash. Never auto-rewrite completed LOCKED lessons.
- For individual high-confidence relations, emit a canonical successor; if a source explicitly establishes two different pedagogical roles for the same surface phrase, allow separate displays only with documented independent teaching value.
- No required per-card related-word count. `CLOSED_NO_FORCE` is acceptable.