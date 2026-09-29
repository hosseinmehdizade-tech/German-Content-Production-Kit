# GFP v411 Vocabulary Projection v1.2.0 — Semantic/Presentation Separation

Purpose: project lexical Sense/Expression objects losslessly without allowing linguistic POS to control Flashcard geometry.

- Every new ordinary lexical card uses `cardType = de-vocabulary`.
- `schemaProfile = german-v411-lexical` identifies semantic projection lineage, not a visual template.
- `customFields.presentation_contract = gfp-vocabulary-neutral@1` is mandatory.
- Preserve POS in `category` + `vnext_pos`; morphology in `vnext_morphology`; gender in `vnext_gender`; preserve Rektion/structure/relations without changing card type.
- Legacy `german-verb` / `de-verb-v8.x` identifiers are compatibility-only.
- Presentation-selector namespaces are closed recursively and case-insensitively. `source_schema_profile` is provenance-only; `presentation_examples` is non-selector content.
- Run `Verification/validate_unified_vocabulary_projection_v1_1_0.py` at Stage 5.
- Clean delivery invokes the same validator internally.
- Stage 6 verifies noun/verb/adjective/expression parity plus explicit legacy compatibility.
