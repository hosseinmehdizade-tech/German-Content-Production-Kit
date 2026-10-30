# OP-02 — Original PDF byte proof + Git-object identity + CAS preflight

**Date:** 2026-10-30. **Scope:** Nonactive process optimization; no
content, original source, workstream LATEST, LOCKED, ZIP, runtime/UI
or producer writer changed. No Stage4/5/6/7 approval is implied.

## Real source-byte evidence (not just a matching pair of Git claims)

The two PDF files were already mounted from this project's original user
attachments in the active execution container. The verifier read their
actual bytes and computed SHA-256; no OCR, extraction or copying of the
copyrighted PDF contents was needed. Match to the separately read
`Workspaces/aber-hallo-listen-tabellen/00-source/SOURCE-MANIFEST.json`:

| Original source ID | Original upload filename | Actual length | Actual SHA256 | Source manifest |
| --- | --- | ---: | --- | --- |
| deutsch-aber-hallo-listen-tabellen-a1-a2 | listen-tabellen A1-A2(1).pdf | 155245 | 4125ed49efa3c4e72500a9c80b8d39021c8933d9a387fc96a637fd4b457e3cf3 | MATCH |
| deutsch-aber-hallo-listen-tabellen-b1-c2 | listen-tabellen B1-C2(1).pdf | 268085 | ebaa3896c3c383808b832241afaf6c38ef4f498eb4dc1b38f26c12087cc97a04 | MATCH |

**Observed result:** `PASS_SCOPED_BYTES_ONLY_NOT_AUTHORITY`;
2/2 PDF SHA256 and exact sizes matched, 0 byte errors. Source IDs and
ordering were checked against the registered manifest. Uploaded file
labels use `(1)` while Git manifest may reference `(2)`; the
content SHA256 is the immutable byte identity, so filenames alone
are not authority. Original PDF bytes were NOT written into Git.

This result verifies the **two original source attachments presently
mounted**, not the WIP65 learner ZIP or a future WIP. It is not an
independent semantic/source-fidelity review.

## New nonactive executable checker

`Verification/audit_op02_byte_anchor_cas.py` exposes:

- `source_bytes`: accepts source declarations and source raw byte
  values **separately** from explicit expected digest pins. Checks
  uniqueness, no unregistered/missing sources, exact length, SHA256,
  basic modality header (PDF/RAR5/ZIP), no boolean count tricks. Caller
  controls those pins; agreement does NOT independently authenticate
  them. The actual original PDFs above were read and hashed in the
  current session. CI uses synthetic noncopyrighted byte fixtures.
- `git_control_blob`: Git SHA-1 blob algorithm
  `SHA1(b"blob <len>\\0" + exact_bytes)`, additionally SHA256 of
  the exact control-file bytes, exact path and full repository ID,
  commit/blob format, separately supplied pin comparison and read-only
  scoped result. A Git commit SHA is not a Git *blob* SHA; the checker
  does not confuse them.
- `rollback_preflight`: checks expected-vs-observed remote HEAD,
  bytes/hashes of both postimage and immutable parent, denies
  same-parent/no-op, rejects caller-supplied self-approved issuer claims.
  Even when all preconditions match, it ALWAYS returns
  `BLOCKED_NO_ROLLBACK_WRITER` and `rollback_authorized=false`.
  No Git write, force update or rollback is exposed.
- `read_regular_file`: rejects symlinks and nonregular, empty or
  oversized local inputs. It does not fetch URL or GitHub data.

## Genuine trust gap — DO NOT mark as closed

The GitHub PR-head CI and GitHub file blob SHA/readback are byte/
schema-consistency evidence, NOT an independently authenticated user
grant. The OP-01 writer-scope registry remains
`DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL`, with `scopes=[]`.
A party that can rewrite both Git pins and candidate receipt can
self-attest an apparent match. This tool does not authenticate the
expected commit, a branch owner, who approved release, or independently
re-fetch remote HEAD immediately before a write. The public repository
branch-protection/source and issuer hardening needs separately approved
architecture and external enforcement.

## What remains to reach an actual production gate

1. Materialize **exact current** learner ZIP/TSV bytes; verify SHA256,
   canonical/import equivalence, ZIP members and packaging against
   current (not historical) content workstream LATEST.
2. Resolve an immutable Git commit/blob anchor and separate
   **independently authenticated** approval with named workstream,
   target, proposed artifact digest, authorization and freshness.
3. Trust a protected policy source external to PR-head code; OP-01
   spoofing showed a green workflow isn't sufficient.
4. Full AI semantic Stage4 review with independent-method adversarial
   pass; Stage5-7 original integration validation, including CURRENT
   Flashcards runtime and rollback recovery material.
5. Use real remote CAS with single-writer controls and postwrite
   independent readback only after explicit approval. Any drift must
   abort and preserve actual CURRENT; rollback also needs fresh
   exact-postimage CAS and independently verified predecessor.
6. No changes to producer/receipts or security controls in this PR.
   An adoption PR would be an architectural change requiring approval.

**Security outcome:** Original-source byte identity can be proven,
but publisher issuer authority and actual current learner release
remain OPEN/BLOCKED. Synthetic CI cannot close these independently.
