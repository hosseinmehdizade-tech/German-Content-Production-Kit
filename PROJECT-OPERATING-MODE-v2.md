# PROJECT OPERATING MODE v2 — ARTIFACT-FIRST, ASYNC GIT

Status: ACTIVE
Scope: German Content Production Kit and all source/workstream production

## Purpose

This operating mode removes GitHub from the critical path of ordinary project work. GitHub remains a durable coordination and backup layer, but it is not the live execution engine and must not be used as a mandatory transport mechanism for every batch, ZIP, checkpoint or chat turn.

## 1. Working-authority order

Use this order when resuming work:

1. Explicitly newer user-supplied current/latest artifact in the current chat.
2. Newest valid portable state/checkpoint artifact available from ChatGPT Project Sources, current conversation files, or ChatGPT Library.
3. Current workstream `CHECKPOINT.json` / project state from GitHub when needed to resolve ambiguity or when no newer portable state is available.
4. Historical branches, old ZIPs and chat memory only for recovery/comparison.

A newer valid artifact/checkpoint must never be downgraded merely because GitHub is older or another state has stronger verification evidence.

## 2. GitHub role

GitHub is an asynchronous durability mirror and coordination layer.

Use GitHub for:
- small text checkpoints, manifests, provenance, contracts, source identities and hashes;
- code history and collaboration;
- meaningful milestone synchronization.

Do NOT use GitHub as the default transport for:
- generated release ZIPs;
- large binary checkpoint packages;
- Base64-split binary reconstruction;
- per-card/per-small-step persistence;
- mandatory startup reads when an unambiguous newer verified state artifact is already available.

Binary/release/checkpoint packages should live in Project/Library/user-delivery surfaces. GitHub may store their filename, SHA-256, manifest summary and synchronization status.

## 3. Quality state and persistence state are separate

A work product can be locally verified independently of Git synchronization.

Track two dimensions:
- `quality_state`: `NOT_STARTED`, `RUNNING`, `PASS`, `FAIL`, `BLOCKED`, `INVALIDATED`
- `persistence.git`: `IN_SYNC`, `PENDING`, `FAILED`, `NOT_REQUIRED`

Git failure must not erase or downgrade valid QA evidence. Do not call something `Git-backed PASS/FINAL/VERIFIED` unless Git synchronization actually completed.

## 4. Turn-budget / timeout rule

Do not consume an entire user turn trying to repair GitHub.

- Resolve the working state first.
- Continue safe production from the newest valid/current authority.
- Make at most one Git synchronization/recovery attempt in the same turn unless the user explicitly asks for Git repair.
- If Git sync still fails, record `persistence.git=PENDING` or `FAILED`, preserve exact hashes/resume instructions, and continue the real project work.

The user should receive a normal answer even when GitHub is unhealthy.

## 5. Portable state bundle

Each workstream should maintain a portable, self-verifying state bundle at meaningful boundaries. The bundle should contain or reference:
- `CHECKPOINT.json`;
- canonical/derived data needed to resume;
- QA/acceptance reports;
- review queue / unresolved issues;
- artifact manifest with SHA-256;
- exact next action.

The bundle may be a ZIP or organized folder stored in Project/Library. GitHub should keep compact metadata about it rather than reconstructing the binary from text chunks.

## 6. Sync cadence

Sync to GitHub at meaningful boundaries, not continuously:
- after a completed batch or milestone;
- after architecture/contract changes;
- before handoff when practical;
- when the user explicitly asks for repository synchronization.

Do not write one commit per card or use GitHub Actions merely to materialize a local/Library ZIP.

## 7. Startup behavior

A new/resumed chat should be able to continue from one sentence such as “continue NVV”. If a current verified state bundle is already available in Project/Library/current context, use it directly and do not block on a deep GitHub audit. Consult GitHub only as much as needed to resolve authority, not as a ritual.

## 8. Conflict handling

If GitHub and a newer valid state bundle disagree:
- keep the newer valid artifact as working authority;
- mark Git synchronization pending;
- do not spend the production turn performing destructive reconciliation;
- sync deliberately at the next meaningful boundary.

## 9. Safety / no-loss rule

Never delete or overwrite a newer artifact merely to make repository history look clean. Reconciliation must preserve hashes, manifests and the newest valid state.

This operating mode supersedes older project text that made live Git persistence a prerequisite for ordinary safe work. Git remains the durable mirror, not the blocker.

## 10. Bounded / deferred / coalesced Git synchronization

Git synchronization is deliberately **not continuous**.

- Portable/current workstream state may advance while Git metadata/tree temporarily lags.
- Multiple intermediate batches/versions should be coalesced and synchronized only at a meaningful boundary.
- Do not commit every card, tiny edit, or runtime version.
- Do not block content production on GitHub Actions.
- At most one Git sync/recovery attempt is allowed in an ordinary production turn unless the user explicitly requests Git repair.
- On failure, set `persistence.git=PENDING` or `FAILED`, preserve artifact/hash/checkpoint/resume instructions, and continue production.
- Large ZIP/checkpoint artifacts stay in Library/Project/user-delivery; Git stores compact source/metadata/hashes.

See `GIT-SYNC-POLICY.json`.

## 11. Durable project memory / reconsideration gate

`PROJECT-MEMORY.json` is mandatory cross-chat decision memory.

Before proposing automation, Git workflow changes, authority/versioning changes, packaging changes, source-governance changes, or noticeable UI/UX changes:

1. Read `PROJECT-MEMORY.json`.
2. Check for an ACTIVE prior decision or incident that the proposal would conflict with.
3. If there is a conflict, tell Hossein what happened before and recommend the recorded safe default instead of simply agreeing.
4. Only supersede a guardrail after explicit user approval and record the superseding decision.

The user should not need to remember old project failures for the system to avoid repeating them.
