# Changelog v3.1.12

## Purpose

v3.1.12 fixes the integration defect where the repository had gained Git-backed checkpointing and a seven-stage production policy, but the active README / START-PROMPT / Master Prompt still pointed to v3.1.11 and did not make that lifecycle normative.

## Changes

- Promotes `SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md` to normative production authority for all current and future content sources.
- Makes a Git-backed `Workspaces/<source-slug>/CHECKPOINT.json` mandatory for production progress and resume.
- Standardizes stage states: `NOT_STARTED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, `INVALIDATED`.
- Defines `PASS` as a durable Git-backed claim requiring committed artifacts and gate evidence.
- Introduces `PERSISTENCE_BLOCKED` for cases where Git write/persistence is unavailable; local-only work cannot be called DONE/FINAL/VERIFIED.
- Requires every resumed session to inspect current `main`, active prompt authorities, source checkpoint, and current Flashcards Pro runtime before continuing.
- Formalizes downstream invalidation and repair propagation so valid upstream checkpoints are preserved.
- Preserves agentic end-to-end execution: no manual approval or arbitrary batch stops between stages.
- Keeps all v3.1.11 lexical-quality, evidence, runtime acceptance, Universal v2, and no-fabrication rules binding.
- Keeps historical/legacy datasets disabled by default except through named recovery workflows.
- Final now requires all seven stages to PASS for the exact release inputs, with Git-backed checkpoint, runtime/presentation evidence, package/hash, and post-package verification.

## Unchanged authorities

- Architecture: v3.1.5
- Semantic contract: `gfp-german-language-content@3.1.3`
- Generic rich-card policy: `GERMAN-RICH-CARD-CONTENT-COMPLETENESS-v1.1.0.json`
- Menschen A1-specific policy remains source-specific and must not be reused for other datasets.

v3.1.12 is a production orchestration/persistence overlay, not an Architecture rewrite.
