# Start Prompt — German Content Production Kit v3.1.10

Use `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.10.md` as the active entrypoint.
It is a normative completeness overlay on v3.1.9; therefore also load `Prompt/CONTENT-GENERATION-MASTER-PROMPT-v3.1.9.md` and all authoritative Architecture v3.1.5 files resolved by v3.1.9.

For Menschen A1 rich Verb production additionally load:

- `Prompt/MENSCHEN-A1-CONTENT-COMPLETENESS-v1.0.0.json`
- `Prompt/CONTENT-COMPLETENESS-PROFILE-SCHEMA-v1.0.0.json`
- `Verification/validate_content_completeness_v1_0_0.py`

Critical rules:

1. `CONTENT_VALIDATED` and `PRODUCT_CONTENT_COMPLETE` are separate.
2. A structurally valid card with missing required learner-facing content must still fail product completeness.
3. Menschen A1 Verb requires at least 3 verified collocations; target 4, preferred max 6.
4. Synonym/Antonym are preferred, not mandatory; never fabricate them.
5. Present Synonym/Antonym/Rektion/Collocation claims require appropriate explicit evidence.
6. Legacy columns named `NVV1..NVV6` are untyped recovery candidates. `NVV != collocation`; classify before canonical migration.
7. Preserve stable Card/Example IDs and valid existing content.
8. Continue agentically through all executable stages; do not stop in arbitrary small batches.
9. On failure, repair root cause and rerun gates. No fake PASS.
