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

## Durability rule

A stage is **not DONE** merely because an assistant, Codex session, local workspace, `/mnt/data`, or chat attachment produced a file. It becomes durably DONE only after its authoritative artifact(s) are committed to the configured Git branch and recorded in `CHECKPOINT.json`.

At the beginning of a new session, read `CHECKPOINT.json` and resume from the last durable commit. Do not rebuild completed stages from chat memory.

## Artifact policy

- Source images/files remain authoritative for inventory and lineage.
- Large/binary source files may be referenced by immutable source locator/hash if repository limits make direct storage inappropriate, but the inventory, stable IDs, hashes, lineage and resume state must still be committed.
- Canonical JSON, QA reports, delivery projections, runtime evidence, manifests, hashes and release metadata must be committed.
- Final delivery may be mirrored as a GitHub Release artifact when binary ZIP size or repository policy makes direct Git storage undesirable; `CHECKPOINT.json` must record the release/tag/asset identity and SHA-256.

See `Prompt/NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md` §2A for the normative checkpoint policy.
