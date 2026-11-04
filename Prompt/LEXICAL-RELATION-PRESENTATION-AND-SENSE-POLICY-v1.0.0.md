# Global lexical-relation content & display contract v1.0.0

**Status:** ACTIVE, prospective. Applies to **all German lexical workstreams and import sources**, not just Menschen, a specific book, or verbs. Do not mutate historical LOCKED/raw source or imported user cards. A new editable successor must retain exact parent authority/hashes.

## Separate semantics from rendering

Every item in `Synonyme`, `Antonyme`, `Verwandte Wörter`, and `Wortfamilie` must be assessed against its own reviewed **sense**. Explicit record fields for new/changed items:

- `kind`: `synonyms | antonyms | related_words | word_family`. Never infer synonyms from surface similarity alone.
- `term_de`: German lexical target with essential reflexive/argument structure, **not** a German mini-essay.
- `translation_fa`: concise, sense-aligned Persian translation. Do not invent one if missing; HOLD the item.
- `usage_note_de`: optional contextual restriction, register, argument frame, contrast, exception or non-interchangeability. Keep notes separate from lexical term and Persian meaning.
- `sense_key` and `target_id`: only when proven by source-grounded identity, never fabricated. Graph links remain independent of presentation.
- `provenance`, `source_ref`, `review_status`: distinguish registered-source evidence, curated interpretations and AI reviewer decisions. Do not claim a licensed source without evidence.
- `display_item`: the exact compatible learner-facing string projected into the standard `details` section.

Optional sidecar: `customFields.lexical_relations_v1` maps relation kinds to arrays of these explicit objects; retain the ordinary `details` array for backwards-compatible TSV/JSON imports. Runtime **uses the sidecar only when its `display_item` exactly matches the displayed item**. Ambiguous/mismatched records must not override existing text. Do not put raw IDs/QA notes inside the learner-visible lemma.

## Display contract, every source

Render each lexical relation on its own readable line, with distinct German term, Persian translation and optional separately styled `Hinweis`. German uses `lang=de dir=ltr`; Persian `lang=fa dir=rtl`, with Unicode bidirectional isolation. No midword breaking except necessary safe fallback for unbroken oversized tokens. Preserve all note text and semantic Wortnetz targets, source strings, original bilingual order and source identities.

The legacy string `term (brief German scope note) — Persian translation` is a **transport fallback**, not preferred authoring. A semicolon inside a bracket, quote or translation is not automatically an item separator. A parser can present an unambiguous note separately, but must never claim to have corrected sense fidelity. Uncertain entries must remain visible and get an audit advisory; never silently delete or invent.

## Pipeline / QA

Run `Verification/audit_lexical_relation_fields_v1.py` on the exact full current projection before Stage4/Stage5. Malformed typed sidecars and broken projection reconciliation are **BLOCKER**. Legacy embedded notes, opaque relation IDs, missing Persian glosses and mixed unstructured prose are **ADVISORY** for immutable predecessors, but demand explicit source/sense review on new editable work. No quota; do not populate synonyms with distant associations just to achieve a count. Prevent duplicate synonyms/antonyms or same source phrase in unrelated categories unless separate sense evidence supports them.

For each **new/changed** item: check German naturalness, semantic fit, lexical identity, term-vs-note separation, Persian accuracy, relation taxonomy, graph target validity, source/provenance, and negative mutation tests. Record KEEP/CORRECT/HOLD dispositions; leave historical cards immutable. New display-only UI changes require source-bound exact-current candidate, Study/Quick tests, escaping and bidi tests, front/back semantics, exact SW/SRI cohort, and a real browser/IndexedDB check before runtime FINAL. **Static QA is not Stage6 PASS.**

## Architecture boundary

Changes apply globally to the Presentation layer and future Content Production Kit outputs, **not** to any single imported book. Keep the established card layout, theme, order, runtime storage, importer, FSRS/SRS, user profile and existing data unchanged. No automatic large-scale migration of historical content.
