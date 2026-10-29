# OP-02 — Exact externally pinned Stage5 CURRENT role authority (v0.1)

**Scope:** NONACTIVE_VERSIONED_DRY_RUN. Process-only hardening. No original
source, workstream learner cards, LOCKED artifact, app/runtime/UI, Library,
LATEST pointer or active production builder is changed.

## Problem proved before this proposal
The real `Tools/build_clean_delivery.py` selects the alphabetically first
filename matching each role. The previous independent preflight catches
ambiguous duplicate filenames, and postbuild SHA checks catch altered member
bytes. But a **single** valid TSV that is NOT the authorized workstream CURRENT
can still package successfully. Package health is not source authority.

## New independent opt-in validator
`Verification/audit_stage5_current_authority.py` requires all of:
- A versioned external sidecar, including workstream/artifact identity, exact
  parent artifact SHA, registered source SHA, EDITABLE_CURRENT state, and exact
  role filenames, sizes and file SHA-256 values.
- The **whole sidecar SHA-256 supplied independently** from an authorized
  checkpoint/portable-current receipt (NOT computed from the candidate).
- Separately supplied expected workstream ID, artifact ID, registered source
  SHA and parent SHA, grounded in that same independently resolved current
  authority. It rejects missing or mismatched pins.
- Existing one-and-only-one role scanner, source byte snapshot, exact packaged
  ZIP SHA and finished member/manifest byte binding.
- Second input-directory snapshot in CLI (not a transactional filesystem lock).

This validator **does not select inputs or build ZIPs**; it audits the unchanged
builder's result. A syntactically valid, semantically wrong single CURRENT
candidate is rejected against the original independently pinned sidecar.

**Important trust boundary:** The validator cannot know whether someone
invented the sidecar *and also* supplied a matching forged "external" digest.
The source of trust must be a separately authenticated CURRENT/LATEST portable
checkpoint, and the operator must resolve the exact immutable parent, source
and workstream before use. A sidecar is NOT a self-authorizing writer grant.
It does not prove Stage4 linguistic quality, source bytes, remote CAS, or real
Stage6/7 acceptance. The status remains NONACTIVE, and OP-01 writer grants
remain DENY_ALL. Never use this tool to mutate a LOCKED artifact.

## Synthetic checks
New CI test `test_stage5_current_authority.py` reuses the actual existing
Stage5 builder's synthetic-card fixture. It covers a valid-but-wrong unique
TSV repackaged successfully by the real builder; forged document digest;
wrong source/workstream/artifact/parent; LOCKED; mismatched role metadata;
duplicate filename; wrong final ZIP digest and missing independent pin.
Nothing from actual learner sources is used.

**Promotion:** Separate explicit authorized scope, trust-root provenance,
real CURRENT content/source verification, rollback and compatibility are
required before any production writer/builder changes.

## Fail-closed parser hardening (2026-10-29, CI verification pending)

The independent sidecar JSON parser now rejects duplicate keys at both top-level
and nested `roles` levels. Nonstandard non-finite JSON constants (NaN,
Infinity) also fail closed, even if an attacker supplies a matching checksum
for malformed text. Unhashable/wrong-typed role filenames return `BLOCKED`
rather than an uncaught Python exception. Seven parameterized negative
cases were added (five wrong-typed filenames and two duplicate-key scopes),
bringing the synthetic file to **28 declared test cases**, counting the
pre-existing six-case parametrization.

**Evidence boundary:** The exact source and test files were persisted/read
back from GitHub, and 4/4 local standalone Python JSON parser mechanics
sanity checks passed; this is NOT full exact repository test execution. GitHub
connector exposed no push-run listing/check statuses for the new commits.
**Ubuntu/Windows CI remains UNVERIFIED** for this new version. Previous
Stage5 single-role binding 27/27 Ubuntu, 26+1 skip Windows PASS is prior,
independent evidence only; do not promote the new guard without job logs.
