# OP-02 — Externally pinned CURRENT trust root & rollback contract (proposal v0.1)

**NONACTIVE / synthetic / no content changes.** Depends on earlier 36/36
Ubuntu + Windows guard, [CI run 40946431973](https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/actions/runs/40946431973).

## Core distinction

A SHA-256 printed by the candidate sidecar cannot certify the sidecar.
Actual trust must come from an **independently resolved authoritative workstream
CURRENT/LATEST**, with exact immutable Git commit identity plus Git blob SHA,
file bytes SHA256, source SHA, parent SHA, current TSV SHA, and sidecar SHA,
and independently authenticated issuer/authorization. Git readback of a file
at a known commit proves byte identity only, not that the commit is the
authorized current release or that a human approved a migration.

## Proposed read-only adapter

`Verification/plan_stage5_current_adoption.py` checks a synthetic
**normalized checkpoint proposal** against an independently PROVIDED trust
root, exact Git blob bytes and a versioned sidecar. It requires workstream
scope and explicit editable status; original sources, LOCKED and writer
scope remain untouched. The existing active workstream LATEST/CHECKPOINT
schemas are HETEROGENEOUS. The normalized proposal is **not** their
replacement; a verified adapter keyed to a real named workstream, plus
independent authentication of the root and approval, is missing and must
be supplied separately. Thus `PASS_NONACTIVE_PIN_CONSISTENCY_ONLY` never
means CURRENT authority verified or production approved.

It is intentionally **not connected** to `build_clean_delivery.py`,
`persist_verified_git_edit.py`, Stage4 or the user app. The OP-01 writer
registry must remain `DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL` with zero
scopes for this optimization project.

## Activation contract (separate user approval required)

1. Resolve actual exact workstream CURRENT and immutable parent/source;
   do not rely on this synthetic normalized schema for a real file.
2. Obtain an independently authenticated trust anchor: original exact
   LATEST/CHECKPOINT bytes from a pinned Git commit and separately verified
   currentness/approved scope, with hashes. Any missing/contradictory
   evidence -> BLOCKED.
3. Run existing Stage3/4 linguistic and provenance checks, Stage5 four-role
   uniqueness, exact role byte and SHA256SUMS checks, packaged TSV semantic/
   v486 bridge review; test Stage6 importer and Stage7 for **real** content.
4. Only on explicit user-approved named editable target: single-writer
   coordination and CAS exact expected preimage; keep immutable parent,
   current portable artifact and rollback material independently recoverable.
5. Pre-promotion abort: keep CURRENT unchanged. If a write may have
   occurred, independently re-read the remote; never blind retry.
   CAS mismatch -> stop for reconciliation, no overwrite.
6. Proposed rollback can only be considered if exact expected postwrite
   blob remains present and original immutable parent bytes/hash are verified;
   another explicit approval and a fresh CAS expected-postwrite are required.
   No automatic force-push, downgrading CURRENT or rewriting LOCKED.

## Verification boundary

The module only **plans**; it does not make network requests, mutate Git,
sign approvals, import content, issue releases or perform a rollback.
All tests are synthetic. Two-platform CI is required for a scoped
code-contract PASS, but would still not authorize production use.
