# START PROMPT v3.1.13

Use `CONTENT-GENERATION-MASTER-PROMPT-v3.1.13.md` as the current production overlay.
Also use:

- `SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`
- `NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md`
- `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`
- `GERMAN-RICH-CARD-PRODUCT-FLOOR-v1.0.0.json`

Architecture v3.1.5 and semantic contract 3.1.3 remain unchanged.

Mandatory correction over v3.1.12:

1. Resolve and record **two separate profile layers** for every source: `source_canonical_profile` for Stage 1/2 and `product_completeness_profile` for Stage 3/4/6.
2. Never use a sparse source-canonical profile as proof that a Flashcards Pro rich card is product-complete.
3. For rich-card targets, `GERMAN-RICH-CARD-PRODUCT-FLOOR-v1.0.0.json` is mandatory unless the user explicitly approves a named relaxation. Source-specific profiles may tighten/specialize it, never silently weaken it.
4. Stage 3 may not PASS for a non-empty rich-card verb dataset if external lexical enrichment was never attempted. Record per-unit attempt results; missing evidence is allowed, a disabled enrichment path is not.
5. Stage 4 must run `Verification/validate_rich_card_product_floor_v1_0_0.py` in addition to canonical, linguistic, lexical-quality and coverage validators.
6. Runtime/Presentation acceptance must assert the product floor after import and learner-visible richness on representative cards: required verb definitions, minimum examples, English example translations, morphology, separate multi-value items and no raw JSON leakage.
7. A transport/import PASS cannot rescue a thin-card product failure.
8. If this defect is found in an existing release, preserve valid Stage 1/2 source work, invalidate Stage 3-7, repair, and rerun downstream gates.
9. All v3.1.12 rules remain binding: Git-backed PASS only, current `main` inspection, source authority, no legacy reuse without named recovery, quality over density, no fabricated lexical claims, exact runtime acceptance and independent post-package verification.
10. Execute agentically through Stage 7 and stop only for a real evidence/tooling/access blocker recorded in `CHECKPOINT.json`.

Current generic product authorities:

- lexical quality/coverage: `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`
- pedagogical/product floor: `GERMAN-RICH-CARD-PRODUCT-FLOOR-v1.0.0.json`
- floor validator: `Verification/validate_rich_card_product_floor_v1_0_0.py`
