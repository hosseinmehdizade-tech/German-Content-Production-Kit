# OP-02 — Stage5 input role selection and finished-ZIP byte binding v0.1

**Mission:** continuous optimization, not content production.
**Date:** 2026-10-29.
**Status:** NONACTIVE_VERSIONED_DRY_RUN; no production builder, content, app or writer changes.

## Real gap and proof boundary

The actual Tools/build_clean_delivery.py uses case-insensitive fnmatch
selection on the top-level Stage5 input directory, and sorts matching paths
before choosing **files[0]** for four distinct roles:

| Role | Existing builder matching pattern |
|---|---|
| direct-import-tsv | *universal*.tsv, *import*.tsv, *cards*.tsv |
| canonical-json | *canonical*.json |
| source-output-map-tsv | *source-output-map*.tsv |
| qa-report | *verification*.json, *qa*.json |

When multiple candidates match a role, the builder does not require an exact
workstream/CURRENT SHA or explicitly selected role path. A stale or wrong but
otherwise schema-valid file could be chosen before generating a perfectly
self-consistent ZIP and manifest. This is a **potential data-selection defect**,
not proof of incorrect existing learner cards or historical deliveries.

**Concrete real-builder reproduction, synthetic only:** the nonmodified builder also accepts an additional valid file named `A-Universal-older.tsv` while `Synthetic-Universal.tsv` is present, then selects `A-Universal-older.tsv` because it sorts filename matches and chooses index zero. Its ZIP and manifest are internally valid, but the chosen TSV differs from the intended original synthetic file. The new role-selector preflight returns `BLOCKED` when both are present. This demonstrates an actual silent file-selection behavior, not corruption of any existing user package.

This is separate from the previously solved **post-ZIP semantic integrity**
proposal in Verification/audit_stage5_clean_zip_v486.py: a finished package
can faithfully preserve precisely the wrong selected input.

## Nonactive opt-in preflight

Verification/audit_stage5_input_role_binding.py:

1. Scans only the existing builder's top-level role matching patterns (no
   recursive guessing). It requires one and only one safe ordinary file per
   role, even if additional candidates contain the *same bytes*. It rejects
   symlinks, missing files, multi-role filename reuse, and source inventory
   masquerading as a direct import TSV.
2. Produces role filename, byte length and SHA256 of each exact selected
   file, with no personal/learner text copied into its JSON response.
3. Given the finished immutable ZIP bytes + a supplied whole-ZIP SHA256,
   reads the actual CONTENT-DELIVERY/DELIVERY-MANIFEST.json and selected
   member bytes, then checks that role path, exact selected file SHA and byte
   length match the earlier preflight.
4. The CLI re-scans the original inputs after reading the ZIP to catch
   role file changes observed at postbuild verification.

**Scope limit:** Even a double snapshot cannot detect a concurrent mutation
that happens and is reverted between checks, cannot prove the declared
source is the authorized newest CURRENT and cannot replace transactional
writer locks or CAS. This local-only proof must be paired with the existing
post-ZIP semantic validator plus independent source, Stage4 and Stage5–7
acceptance. It does not validate the ZIP's internal SHA256SUMS itself — that
is the separate postpackage guard's job.

This tooling is independent and **NOT wired into the active Stage5 builder**.
Activation, new defaults or any output selection change on a real workstream
requires exact current/LOCKED resolution and explicit approval for production
writer/schema behavior. The proposed adapter remains inactive.

## Reproduction

The test Verification/tests-v3.3.6/test_stage5_input_role_binding.py
calls the unmodified existing clean ZIP builder with **synthetic** cards
using temporary directories, then exercises real postbuild byte binding.
Adversarial scenarios include identical-content duplicate TSVs, different
import/canonical/QA/map naming collisions, source-inventory false candidates,
multiple-role matching, case variants, symlinks, absent role, modified source,
a forged ZIP role change, rehashed ZIP manifests and substituted content,
and wrong whole-ZIP SHA.

CI is wired to Stage3–Stage4 Proposal Compatibility on Ubuntu and Windows.
No registered original source, learner content, workstream LATEST, LOCKED,
Library record, Flashcards runtime v486-R120 or UI is modified.

**Separately unresolved:** historical A2-L24 reference digest 9aa0f362...
has not been materialized; OP-01 remains DENY_ALL (zero active writer grants).
Stage4 linguistic authority is never inferred from synthetic fixtures.
The user-required final 8-section vocabulary content ZIP is not created
or accepted by this Stage5 clean-package regression.
