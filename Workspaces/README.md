# Persistent Production Workspaces

`Workspaces/` is the durable Git-backed checkpoint area for active content-production datasets.

Every production source gets a stable folder:

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

## Seven-stage production model

All current and future content sources use the same human-trackable seven-stage model defined in:

`Prompt/SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md`

1. Source & Inventory
2. Canonicalization
3. Evidence & Enrichment
4. Linguistic & Lexical QA
5. Delivery Projection
6. Runtime & Presentation Acceptance
7. Release & Post-Package Verification

Execution remains agentic and end-to-end. The seven stages are durable checkpoints and recovery boundaries, not manual approval stops.

Allowed states are:

`NOT_STARTED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, `INVALIDATED`.

## Durability rule

A stage is **not PASS** merely because an assistant, Codex session, local workspace, `/mnt/data`, or chat attachment produced a file. It becomes durably `PASS` only after its authoritative artifact(s) and gate evidence are committed to the configured Git branch and recorded in `CHECKPOINT.json` with the establishing commit SHA.

At the beginning of a new session, read `CHECKPOINT.json` and resume from the first non-PASS/non-valid stage. Do not rebuild completed stages from chat memory.

If an upstream authoritative artifact changes, dependent downstream stages must be marked `INVALIDATED` and rerun; unaffected upstream PASS stages are preserved.

## Artifact policy

- Source images/files remain authoritative for inventory and lineage.
- Large/binary source files may be referenced by immutable source locator/hash if repository limits make direct storage inappropriate, but the inventory, stable IDs, hashes, lineage and resume state must still be committed.
- Canonical JSON, evidence index/cache state, QA reports, delivery projections, runtime/presentation evidence, manifests, hashes and release metadata must be committed.
- Final delivery may be mirrored as a GitHub Release artifact when binary ZIP size or repository policy makes direct Git storage undesirable; `CHECKPOINT.json` must record the release/tag/asset identity and SHA-256.

See `Prompt/NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md` §2A and `Prompt/SEVEN-STAGE-PRODUCTION-PIPELINE-v1.0.0.md` for the normative checkpoint policy.
