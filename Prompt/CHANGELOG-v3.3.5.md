# CHANGELOG v3.3.5

- Generalized the fix into semantic/presentation orthogonality rather than a verb-specific exception.
- Explicit supported outer card type is authoritative; linguistic morphology never selects presentation.
- Added mandatory `gfp-vocabulary-neutral@1` presentation contract.
- Projector preserves `vnext_pos`, `vnext_morphology`, and `vnext_gender` while keeping one `de-vocabulary` envelope.
- Validator v1.1 rejects top-level and arbitrarily nested presentation selector namespaces case-insensitively while permitting semantic morphology.
- `source_schema_profile` is provenance-only; `presentation_examples` remains non-selector content.
- Clean-delivery requires `custom_fields` and invokes validator v1.1 internally.
- Runtime counterpart is German Flashcards Pro v451/R85.
