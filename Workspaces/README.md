# Persistent Production Workspaces

> **2026-11-07 canonical Workspace routing (prospective, non-destructive):** Before starting a new content task or creating any `Workspaces/*` directory, resolve the family in [the 21-family canonical routing registry](../Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json). Each family has **at most one canonical Git Workspace** and one stable Library family folder. Existing noncanonical Workspace directories are preserved for historical QA, source evidence and necessary compatibility, not second CURRENT owners; **no folder was moved/deleted by this policy**. Five families with no Git Workspace yet stay Library-only; first Git Workspace creation requires a reviewed routing change and a real user-approval receipt. New work for represented families belongs inside the canonical Workspace's own workstream subfolders or Git branches, rather than another top-level Workspace. The [read-only CI guard](../.github/workflows/canonical-family-workspaces.yml) rejects silent sibling creation and contradictory canonical ownership; it does not auto-promote content or alter app/UI/SRS/FSRS.

`Workspaces/` is the durable Git-backed checkpoint area for active content-production datasets.

For new canonical content work, use **the existing family-selected canonical folder**, not an automatically generated source-/repair-specific sibling. A canonical folder may organize tasks internally as follows:

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

## Prior Workspace dependency preservation

Before any cleanup or link rewrite for a historical Workspace, use the [canonical family route](../Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json) and the [legacy inbound reference audit](../Tools/audit_legacy_workspace_dependencies_v1.py). A Workspace with **zero exact tracked-text inbound references** is **not deletion-safe**; binary ZIP interiors, Library, Drive, and untracked references are not covered. New task outputs belong under the canonical destination; existing historical references can remain stable. The [preservation handoff](../Optimization-Program/Control-Center/LEGACY-WORKSPACE-DEPENDENCY-HANDOFF-v1.md) records this boundary.

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

## Automatic file lifecycle contract (all projects)

**FILE_LIFECYCLE_RULE_V1_0_0**: Every workstream must use `Library-Organization/FILE-LIFECYCLE-AND-SAFE-CLEANUP-v1.0.0.md` and its own `FILE-LIFECYCLE-RULE.md` before saving new file versions, after each validated milestone and when resuming. A new workstream must add the anchor at creation. Keep one compact per-project artifact registry within existing checkpoint or one separate manifest if necessary; proactively identify exact redundant/superseded files in normal handoff. The assistant must not wait for a cleanup reminder; **deletion still requires user confirmation for the exact candidates**. Source/LOCKED/final and recovery checkpoints are protected.

## Curated current lexical authority (all current and future workspaces)

At every workstream resume read `Prompt/CURATED-CURRENT-AUTHORITY-AND-DELTA-QA-POLICY-v1.0.0.md` from the version-pinned global registry and the **actual owner-specific** latest verified final/current TSV/CSV/JSON or recoverable accepted bundle. Mature curated current content, not the initial textbook inventory, is the basis for additions/removals and QA. Review changes versus the immediate accepted curated predecessor and impacted dependencies; do not redo entire raw-source fidelity audits on each lesson/release. Keep historical originals, exact SOURCE_EXACT attribution and unresolved HOLDs for scoped evidence. Full current-state structural and required Stage4–7 gates still apply. If the current owner file cannot be verified, HOLD rather than fall back silently to raw originals.
