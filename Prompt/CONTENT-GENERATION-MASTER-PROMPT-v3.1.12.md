# General German Content Generation Master Prompt v3.1.12
## Seven-Stage Git-Backed Production + Durable Resume Hardening

This file is the normative v3.1.12 overlay on `CONTENT-GENERATION-MASTER-PROMPT-v3.1.11.md`.
Architecture v3.1.5 and semantic contract 3.1.3 remain unchanged.

v3.1.12 does not weaken any lexical, evidence, runtime or delivery rule from v3.1.11. It makes the production lifecycle itself durable, resumable and human-trackable through a mandatory seven-stage Git-backed pipeline.

## 1. Normative seven-stage lifecycle

Every current and future content source MUST use `SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md` as the production state model:

1. Source & Inventory
2. Canonicalization
3. Evidence & Enrichment
4. Linguistic & Lexical QA
5. Delivery Projection
6. Runtime & Presentation Acceptance
7. Release & Post-Package Verification

These seven stages are the user-facing tracking model. Each stage may internally execute multiple validators, scripts, repair loops and hard gates.

Execution remains agentic and end-to-end. The agent does not wait for manual approval between stages unless a real blocker requires user action.

## 2. Standard stage states

Every stage uses exactly one state:

- `NOT_STARTED`
- `RUNNING`
- `PASS`
- `FAIL`
- `BLOCKED`
- `INVALIDATED`

`PASS` is a durable claim, not a conversational status.

A stage can become `PASS` only when:

1. its authoritative output artifacts exist;
2. its required hard gate evidence exists;
3. those artifacts/evidence are committed to the configured Git branch;
4. `CHECKPOINT.json` records the state, paths, and commit identity.

Local ChatGPT/Codex files, `/mnt/data`, desktop workspaces, generated ZIPs, or chat attachments do not establish `PASS` by themselves.

If Git write/persistence is unavailable, use `PERSISTENCE_BLOCKED`. Never relabel local-only work as `PASS`, `DONE`, `FINAL` or `VERIFIED`.

## 3. Persistent source workspace

Every production source MUST establish a durable workspace before substantial downstream production:

```text
Workspaces/<source-slug>/
  00-source/
  01-inventory/
  02-canonical/
  03-evidence/
  04-qa/
  05-delivery/
  06-runtime/
  07-release/
  CHECKPOINT.json
```

An explicitly designated project-specific repository may use the same logical structure elsewhere, but repository, branch and path must be recorded in `CHECKPOINT.json`.

`CHECKPOINT.json` is the resume authority for production progress. Chat history is not.

## 4. Resume-before-work rule

At the start of every new or resumed session:

1. inspect `German-Content-Production-Kit/main`;
2. resolve the active START-PROMPT / Master Prompt / Runbook / Seven-Stage policy from the repository, not memory;
3. inspect the source workspace and `CHECKPOINT.json` when it exists;
4. inspect `German-Flashcards-Pro/main` and resolve the actual intended target runtime;
5. resume from the last durable checkpoint.

Do not rebuild a stage already durably `PASS` unless new evidence invalidates it.

## 5. Invalidation and repair propagation

When an upstream authoritative artifact changes, dependent downstream stages become `INVALIDATED`.

The repair policy is:

- repair the earliest affected stage;
- preserve upstream stages whose evidence remains valid;
- rerun every downstream stage whose inputs changed;
- update `CHECKPOINT.json` after each durable transition;
- never restart the full pipeline merely because a later-stage unit failed.

Typical dependency chain:

`1 → 2 → 3 → 4 → 5 → 6 → 7`

Example: a Stage 4 linguistic repair that changes canonical learner-facing content invalidates Stages 5–7, but does not automatically invalidate source inventory or evidence cache.

## 6. Source authority and named recovery

The user-provided source remains authoritative for inventory, source spelling, lesson/chapter placement and lineage.

External dictionaries and lexicons verify/enrich; they do not silently replace source inventory.

Legacy enriched datasets, historical mappings, old NVV fields, previous card sets and prior `FINAL` labels are disabled by default. They may enter only through an explicitly named recovery workflow.

A named recovery must:

- identify the historical artifact and hash when possible;
- bind it to the current authoritative source inventory;
- record which stages are reusable and which are invalidated;
- rerun all current-contract gates affected by the historical artifact age/differences;
- commit recovered outputs before claiming durable progress.

## 7. Lexical-quality rules remain binding

All v3.1.11 quality rules remain mandatory:

- quality outranks field density;
- no learner-facing fact/evidence may be fabricated to satisfy a count;
- example-derived phrases are not collocations;
- collocations are atomic, sense-aligned and evidence-backed;
- synonym/antonym relations require sense-bound evidence;
- explicit learner valency requires explicit Rektion evidence;
- source sense markers are evidence locators, not learner-facing content;
- missing preferred coverage is reported, not filled mechanically.

## 8. Incremental evidence is a durable Stage 3 asset

External evidence retrieval is cached incrementally by normalized lexical identity + source + access/version key.

Successful evidence must be committed so it survives later failures and sessions.

Retry only missing, stale or failed units. A repeated full-source refetch without a source/version invalidation is a pipeline defect.

## 9. Delivery and runtime authority

Universal v2 remains the default delivery transport when selected by the current contract.

At Stage 6, resolve the actual current intended `German-Flashcards-Pro/main` runtime. `v354` is the verified baseline at the time v3.1.12 is introduced, not a forever-pinned target.

Runtime/presentation acceptance must prove, as applicable:

- all rows import;
- no invalid/duplicate stable IDs;
- runtime field shapes are correct;
- canonical payload round-trips without silent loss;
- DE/FA/EN example grouping is preserved as required;
- verb core forms and learner-facing details render;
- multi-value arrays render as separate items;
- no raw JSON leaks into learner-facing UI;
- relevant practice modes accept the projected content.

If the target runtime cannot be executed or equivalently pinned, Stage 6 is `BLOCKED`, not `PASS`.

## 10. Finality rule

`Final` is allowed only when Stages 1–7 are all `PASS` for the exact release inputs.

Stage 7 must include:

- direct import TSV separately accessible;
- canonical JSON;
- inventory/stable-ID evidence;
- linguistic/lexical QA and coverage reports;
- delivery validation;
- runtime/importer acceptance evidence;
- presentation acceptance evidence;
- manifest/build metadata;
- SHA-256;
- package ZIP or immutable release-asset locator/hash;
- independent post-package verification;
- final Git-backed `CHECKPOINT.json`.

A parse-only or transport-only artifact is not Final.

## 11. Session-end durability rule

Before a session ends after meaningful production progress:

- commit every completed stage artifact/evidence;
- update `CHECKPOINT.json`;
- record blockers and exact resume instruction;
- leave incomplete local-only work as `RUNNING`, `BLOCKED`, or `PERSISTENCE_BLOCKED` as appropriate.

No important production state should exist only in the chat transcript.
