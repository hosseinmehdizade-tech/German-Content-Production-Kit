# START PROMPT v3.3.4

The active production framework is v3.3.4 — Unified Vocabulary Delivery Hard Gate.

The exact full master prompt is inside the verified portable authority recorded in PROJECT-STATE.json.
Portable package: `German-Content-Production-Kit-v3.3.4-Unified-Vocabulary-Delivery-Hard-Gate-CANDIDATE.zip`. Its outer SHA-256 is recorded externally in the sidecar and PROJECT-STATE after packaging; it is intentionally not embedded in the ZIP to avoid a self-referential hash.
Internal master SHA-256: `1ee37adefffb743f149e7ae60634fb719b0bf4540a3c00063c20fcd9d84b4dc3`.

Mandatory vocabulary rules:
- every ordinary lexical Sense/Expression uses the neutral `de-vocabulary` envelope regardless of POS;
- POS, morphology, Rektion and expression structure remain semantic data, never layout selectors;
- `german-verb` is legacy input compatibility only;
- Stage 5 must run the unified projection validator;
- **the clean-delivery builder must independently enforce the same rule and may not trust that Stage 5 already ran**;
- direct-import TSV must explicitly contain `card_type` and `category`; every row must have `card_type=de-vocabulary`;
- missing `card_type`, missing category, `german-verb`, or mixed outer types must fail before a release ZIP is created;
- Stage 6 must check cross-POS presentation parity.

Enforce `Prompt/UNIFIED-VOCABULARY-IMPORT-PRESENTATION-POLICY-v1.0.0.md` and `Architecture/05-CONTRACTS/GFP-V411-VOCABULARY-PROJECTION-v1.1.0.md`.
