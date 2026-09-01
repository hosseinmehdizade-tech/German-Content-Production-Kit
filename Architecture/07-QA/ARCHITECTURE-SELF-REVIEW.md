# Architecture Self-Review — Prompt/Delivery Gate v3.1.4

## Scope

This release fixes **runtime-finality claims**. The semantic model remains `gfp-german-language-content@3.1.3`; no vocabulary field, example shape, source policy, type rule, or connection semantics were redesigned.

## Triggering defect

The prior 30-card pilot exposed a real false-finality gap: the Universal-v2 TSV was recognized as 30 rows by v343, but the user's live browser was still recovery/write-blocked, so transactional persistence failed and the previous library was restored. The prior prompt had treated an isolated runtime PASS as sufficient for a single `IMPORT_READY` label.

## Fix review

| Requirement | Result |
|---|---|
| Artifact compatibility separated from live browser readiness | PASS |
| Ambiguous `IMPORT_READY` deprecated/forbidden | PASS |
| Existing non-empty library mandatory in isolated compatibility matrix | PASS |
| Recovery/write-block scenario defined as fail-closed safety PASS, not import success | PASS |
| Official recovery→READY path required before retry | PASS |
| Live preflight requires READY + no write block + canWrite + writer authority | PASS |
| Live blocked state produces `RUNTIME_BLOCKED` without blaming the artifact | PASS |
| Actual success requires persistent transactional commit + reload/reopen | PASS |
| Machine-readable runtime evidence schema added | PASS |
| Isolated evidence forbidden from claiming current-runtime status | PASS |
| Automatic database reset/delete workaround forbidden | PASS |

## Executed QA

- Python unit/regression tests: **61/61 PASS**.
- Draft 2020-12 schema meta-validation: **6 schemas PASS**.
- Schema instance validation: **19 instances PASS**.
- Structural/typed semantic sample validation: **PASS**, 0 errors, 0 warnings.
- Universal-v2 delivery parity validation: **PASS**, 10 rows, 0 errors, 0 warnings.
- Runtime-evidence validator sample: **PASS** with `APP_COMPATIBLE + CURRENT_RUNTIME_NOT_VERIFIED`, proving the two axes can coexist without a false current-browser claim.
- Flashcards Pro v343 shipped content-contract validator on the sample TSV: **PASS**, 10 rows, 0 errors, 0 warnings (`target-de=2`, `target-en=1`).

## Negative regression coverage added

The test suite explicitly rejects:

1. an isolated Runtime claiming `IMPORT_VERIFIED` or another current-runtime state;
2. `RUNTIME_PREFLIGHT_PASS` when `writes_blocked=true`;
3. `APP_COMPATIBLE` without an existing-library scenario;
4. `IMPORT_VERIFIED` without verified persistent commit/reload;
5. artifact SHA mismatch between evidence and delivered file.

## Important honesty boundary

This package **does not claim** that the user's current browser is writable. That can only be known at execution time through Stage 13 live preflight. The purpose of v3.1.4 is precisely to make the prompt refuse to invent that claim from static or isolated evidence.

## Freeze recommendation

**PASS — Freeze Candidate for prompt/delivery-governance v3.1.4.**

The next content pilot may use this prompt, but the pilot must report artifact status and current-runtime status separately. A current browser in recovery must be reported `RUNTIME_BLOCKED`, even when the TSV is `APP_COMPATIBLE`.
