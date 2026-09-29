# START PROMPT v3.3.5

The active production framework is v3.3.5 — Semantic/Presentation Separation.

Resolve the full master prompt from `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.3.5.md` inside the verified portable authority recorded in PROJECT-STATE.json.

Mandatory vocabulary architecture:
- `card_type=de-vocabulary` is the single new ordinary-vocabulary presentation/transport family;
- POS/morphology/gender/Rektion/expression structure remain semantic data and may be rich without changing card type;
- `custom_fields.presentation_contract=gfp-vocabulary-neutral@1` is mandatory for new production;
- explicit supported outer card type is authoritative; semantic inference must not override it;
- presentation-selector namespaces are closed recursively and case-insensitively; `source_schema_profile` is provenance-only;
- Stage 5 uses `Verification/validate_unified_vocabulary_projection_v1_1_0.py`;
- the clean-delivery builder invokes that validator internally and fails closed before packaging;
- Stage 6 verifies cross-POS parity plus legacy compatibility separately.

Enforce `Prompt/UNIFIED-VOCABULARY-IMPORT-PRESENTATION-POLICY-v1.1.0.md` and `Architecture/05-CONTRACTS/GFP-V411-VOCABULARY-PROJECTION-v1.2.0.md`.
