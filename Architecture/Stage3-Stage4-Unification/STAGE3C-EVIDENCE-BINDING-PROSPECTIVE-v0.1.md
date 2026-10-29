# OP-02 — Prospective Stage3C Evidence Binding, v0.1

**Status: NONACTIVE_VERSIONED_DRY_RUN — proposal only (2026-10-29).**
Active v3.3.6 prompt, legacy Stage3A/3B/3C, source/LOCKED authorities,
app runtime and Stage4/5/6/7 acceptance remain unchanged.
Implementation: Verification/validate_stage3c_proof_binding.py.
Tests: Verification/tests-v3.3.6/test_stage3c_proof_binding.py.

## Proven need, exact historical scope

The archived 2026-10-18 Menschen A2 L24 Stage3C completeness contains 1,424
positive basis references: **1,213 EDITORIAL_REVIEW, 151 SOURCE, 60 LOCKED_PARENT**.
These are three distinct evidence kinds and must not share a superficial
hash check.

The exact historical Stage3C ledger and 1,213 editorial references cite
SHA256 **9aa0f362...**, while the named archived editorial member has exact
SHA256 **36c0fa4b...** in both Stage3C and Stage4. The old referenced bytes
were not located in the three available Stage3B/3C/4 archives. This remains
an unresolved reference to potentially separate historical bytes, NOT a
finding of wrong German, not a reason to alter original checkpoints, and
not a reason to downgrade an existing historical scoped receipt.

## Sidecar scheme — external to the candidate ZIP

A separately versioned contract JSON holds:

- schema = gcpk-stage3c-proof-binding@1
- status = NONACTIVE_VERSIONED_DRY_RUN
- candidate_archive_id = candidate
- archives = distinct ID + exact whole-ZIP SHA256 for candidate and any
  immutable predecessors, supplied as authenticated exact byte snapshots
- completeness = path + SHA256 of the Stage3C completeness JSON member
- source_inventory = archive_id + exact whole-ZIP SHA256 (here in the external
  sidecar) + path + SHA256 of the captured Stage1 source inventory member.

**No self-referential hashes.** A basis reference INSIDE its own candidate ZIP
carries only archive_id and exact member SHA256, not the whole candidate ZIP
SHA256 (which would create a cyclic digest). The sidecar alone pins the
candidate whole ZIP SHA. An immutable predecessor reference instead carries
both predecessor archive_id AND its whole archive_sha256, which must agree
with the sidecar. No guessing by filename or automatic cross-version fallback.

## Type-specific basis references

**EDITORIAL_REVIEW** requires archive_id, path, artifact_sha256,
target_id and dimension. Its exact ZIP member hash, authored_targets ID,
dimension/cell identity and Stage3C summary editorial SHA must all agree.
When referring to a predecessor ZIP, archive_sha256 is additionally required.

**SOURCE** requires source_archive_id, source_member_sha256, source_id,
source_occurrence_id, source_ordinal, and source_row_payload_sha256. The
validator compares those fields with the exact captured source inventory
member: occurrence ID, source ID, locator.row, and recorded source-row hash.
Original external RAR/PDF extraction and licensing remain separately
verified Stage1 evidence; the source inventory member alone is not raw
source attestation. Candidate archive whole SHA is resolved via the sidecar.

**LOCKED_PARENT** requires predecessor archive_id, archive_sha256,
path, member_sha256, target_id, snapshot_sha_scope and
artifact_snapshot_sha256. The predecessor ZIP and its member are separately
hashed; target_id is checked against the exact reused record. The new explicit
snapshot_sha_scope JSON_CANONICAL_RECORD_V1 means JSON with sorted keys,
UTF-8, compact separators and SHA256 of the selected individual card record.
Never substitute member/whole-ZIP SHA for record SHA. Legacy historical
snapshot hashes have their own older semantics and are NOT automatically
treated as if this prospective encoding applied.

**Other closure checks:** unique target and archive IDs, legal exact member
paths, ZIP CRC and file safety, every VERIFIED_PRESENT dimension has actual
evidence, CLOSED_NO_FORCE retains a reason, no held/unresolved cells, and
source/completeness counts agree. The sentinel result
PASS_SCOPED_DETERMINISTIC_PROOF_BINDING_ONLY is NOT a linguistic QA result,
a per-item teaching_delta adjudication, or Stage4/5/6/7 promotion.

## Rollout and preservation

This schema and validator are new nonactive opt-in dry-run tools. They are not
wired into a production builder or permitted to edit archived ZIPs, registered
source, LOCKED cards, workstream LATEST, CURRENT app or UI. Activating them
in a production writer requires explicit user authorization, newest exact
mutable CURRENT/source/parent bytes, reversible backup, CAS, independent AI
linguistic Stage4 and all downstream gates.

Run synthetic CI on Windows and Linux with:
python -m pytest -q Verification/tests-v3.3.6/test_stage3c_proof_binding.py

Run against an explicitly authorized standalone sidecar/ZIP set with:
python Verification/validate_stage3c_proof_binding.py --contract sidecar.json
--archive candidate=exact-stage3c.zip --archive parent=exact-parent.zip

Real private source archives are not committed to Git. Historical A2 L24
remains a read-only regression fixture; its unresolved 9aa0... reference is
not auto-repaired or declared valid by this prospective contract.
