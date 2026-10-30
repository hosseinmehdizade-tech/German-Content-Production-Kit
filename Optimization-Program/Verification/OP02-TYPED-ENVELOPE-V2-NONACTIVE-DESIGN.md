# OP-02 — Typed Envelope v2: cross-domain feasibility and security boundaries

**Status:** NONACTIVE PROTOTYPE. This is a scoped *process* test. It is
NOT a producer migration, user authorization, Stage4 linguistic acceptance,
Stage5/6/7 release, or app/runtime change. Do not edit learner or LOCKED data.

## Why v1 is insufficient

The v1 fixed envelope is tailored to Aber Hallo WIP+ZIP+981 rektion patterns.
Actual Menschen B1 uses an RAR5 source plus CSV/audio, and Lesen
Präsentation currently has a PDF source and Stage1 inventory without a
learner release ZIP. Requiring the grammar fields of other workstreams
would forge evidence or falsely advance Stage status. The v2 pilot provides
one stable envelope with **strict registered, source-specific payloads**.

## Common envelope

`gcpk-op02-typed-envelope@2` contains exactly:
`schema, workstream, domain, contract, anchor, sources, payload, gates`.

- `anchor` = `kind,path,blob_sha,milestone` referring to a separately
  observed control file (grammar's LATEST or B1/Lesen CHECKPOINT).
- `sources` = ordered identities, modalities, SHA256 fixed in explicit
  pilot profiles. Archive, CSV and PDF are distinct; no modality inference.
- `payload` = registered type for Grammar WIP open, Vocabulary
  Memrise audio-source inventory or Reading Stage1 source inventory.
- `gates` = explicit `NOT_APPROVED/NOT_AUTHORIZED/UNAUTHENTICATED`.
  The evaluator rejects extra keys, unknown workstreams/contracts and
  content pretending to be a different payload. No positive result can
  promote to production.

The pilot requires the claimed anchor and separately provided observed
anchor to match; it checks Git SHA-format and exact expected workstream
path. **This is comparison, not a trust root.** Observed data are provided
by the test caller. The same attacker able to forge both envelope and
observed anchor could obtain a *scoped metadata PASS*. The return fields
`independent_anchor_authenticated` and `issuer_authenticated` remain
FALSE. A real publisher needs a separate identity/authorization service.

## Domain mapping, rooted in tracked source metadata

| Type | Source and scope | Exact stage and role boundary |
| --- | --- | --- |
| Grammar Aber Hallo | Two PDF identities and source hashes; WIP65 historical tracked receipt; 845 attested + 136 held = 981 governed patterns, 788 units, 787 lexical cards | 64-hex ZIP/parent and changed-ID integrity; current Stage4 OPEN, not a semantic PASS |
| Vocabulary Menschen B1 | Memrise RAR5 113,754,051 bytes + CSV SHA, 9,109 rows; B1 L01 126 source rows/audio refs, 24 B1 lessons | Source/audio inventory only. No mandatory grammar ZIP, no assumption that B1 L01 is CURRENT curriculum |
| Lesen Präsentation | One PDF SHA, 76 pages, 68 topics | Source Stage1 PASS, Stages2–7 NOT_STARTED. No synthetic final delivery package |

Snapshots used by tests are historical **fixture input** from tracked Git.
They cannot attest original archive/CSV/PDF binary contents in this job.
No source material, content artifacts, or LATEST pointers are rewritten.
The WIP66 simulation uses the same v2 schema without per-WIP code editing.

## Threat matrix / negative tests

Test scenarios include: schema/contract/workstream spoofing; extra/missing
fields; cross-domain payload mix-ups; stale/mismatched anchor; path
traversal; source hash order/modality drift and coordinated source
mutation against registered profiles; boolean-as-integer, duplicate JSON
keys, NaN, grammar conservation errors, duplicated/forged changed IDs,
self-parent, reading false Stage7, vocabulary audio/row drift, and forged
issuer/semantic/release claims. All must BLOCK. Green tests attest only
this isolated pilot's behavior.

## Production go/no-go and rollback (NOT APPROVED HERE)

1. Establish externally authenticated source and issuer policy outside
   editable PR metadata. Git commit SHA/blob and self-reported checks
   prove identity consistency, **not permission**. OP-01 remains DENY_ALL.
2. Implement a versioned producer-side *opt-in* output for a named
   workstream. Keep legacy receipt readers; do not auto-translate old
   WIP receipts nor overwrite LOCKED/source archives. Every change is
   subject to user approval of the visible architecture/scope.
3. Read exact user-authoritative current portable bytes and source
   archive/PDF files, verify SHA256 and Git blob identity at the
   independently pinned commit and compare the candidate against them.
   On absent bytes, fail closed; never downgrade CURRENT.
4. Require the full independent-method AI Stage4 trilingual/source
   semantic review, deterministic tests, and applicable Stage5-7 gates.
   Missing external human signature is not itself required under
   the active user-approved override; linguistic review remains mandatory.
5. Confirm single writer/CAS expected preimage, independently
   authenticated issuer and release scope. Never turn a PR-head
   green check into trusted authority (OP-01 spoofing history).
6. Rollout by explicit named opt-in only. Pre-write failure aborts
   with CURRENT unchanged. Post-write ambiguity requires fresh remote
   readback. Rollback would need separately approved CAS against the
   exact post-image and verified parent bytes; no force push or
   silent downgrade to a prior content or app version.
7. If adoption fails, disable only the new typed producer path and
   retain legacy receipts + unchanged CURRENT. Record versioned rollback
   rationale. Do not delete legacy Library recovery copies automatically.

## Current outcome boundary

A v2 synthetic metadata PASS can never authorize a real content
producer, Stage4/5/6/7, user SRS import, App update or FINAL release.
These are nonrequired GitHub Actions, not independent trusted checks.
Existing v1 and native source checks remain intact and unmodified.
