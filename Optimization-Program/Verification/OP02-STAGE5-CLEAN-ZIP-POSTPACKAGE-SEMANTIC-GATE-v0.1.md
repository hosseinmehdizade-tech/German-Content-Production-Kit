# OP-02 — Read-only post-package Stage5 → v486 semantic gate

**Date:** 2026-10-29
**Status:** PASS_SCOPED_SYNTHETIC_POSTPACKAGE_CI / NONACTIVE_VERSIONED_DRY_RUN.
**Mission:** Process integrity only, not production content or runtime release.

## Real inspected builder

Tools/build_clean_delivery.py selects four top-level source roles: direct
import TSV, canonical JSON, source-output-map TSV and QA report. It validates
the neutral vocabulary envelope, stages those files, writes a delivery
manifest and SHA256SUMS, builds a CONTENT-DELIVERY ZIP and re-extracts and
validates its member hashes.

But ordinary package integrity does NOT prove that the ACTUAL packaged TSV
retains Stage4 item-level translation, provenance, teaching_delta and the
v486-R120 view envelope.

The builder's output is a clean-content-delivery scoped Stage5 ZIP,
NOT the complete eight-directory vocabulary content-production ZIP required
by CONTENT-OUTPUT-DELIVERY-POLICY.json for user-facing final delivery.
It currently picks the first matching candidate filename for each role;
multiple matching input files remain an upstream selection ambiguity that
this finished-ZIP-only audit does NOT independently resolve. Future releases
should explicitly record/refuse ambiguous role inputs.

## New exact post-package audit — NONACTIVE

Verification/audit_stage5_clean_zip_v486.py takes the finished ZIP bytes,
an externally pinned exact whole ZIP SHA256, exact Stage4 content bytes,
a separate Stage4 review receipt, and the two existing nonactive Stage45
and exact-v486 bridge sidecars.

It checks every ZIP member name and bound, duplicate/path traversal, symlink,
encryption, CRC, exact exhaustive SHA256SUMS, DELIVERY-MANIFEST role identity
and uniqueness, and exact set of the four role files plus the two manifests.

It then extracts the actual direct TSV member from ZIP, validates the neutral
vocabulary envelope, and feeds those exact POSTBUILD TSV BYTES to:

1. Verification/validate_stage45_teaching_delta_parity.py — full item
   list/order, German/Persian/English, kind, provenance, teaching_delta,
   separately reviewed item hashes and Stage4 authority.
2. Verification/validate_stage45_v486_consumer_bridge.py — exact pinned
   v486-R120 view metadata, rich Kombinationen visibility and guards against
   missing view bridge, altered items, stale details override.

Its Stage4 review receipt is structurally checked, not independently
substantiated AI linguistic review. Real source semantics, actual workstream
CURRENT, final organized vocabulary release, current populated app profile,
true production Stage6 and release Stage7 remain separate gates.

No active Stage5 writer, source registration, importer, user UI, content ZIP,
Library file, LATEST, LOCKED or original source was modified. This is a
standalone nonactive post-package audit, not a production schema activation.

## Reproducible CI

Verification/tests-v3.3.6/test_stage5_clean_zip_v486.py runs the existing
UNCHANGED Tools/build_clean_delivery.py using an original synthetic
two-card corpus, keeps all files inside disposable pytest temporary
directories, and independently opens the finished ZIP to audit its bytes.

19 positive and adversarial cases cover exact result parity, changed whole
ZIP SHA, changed/added/missing/duplicate ZIP members, tampered manifests,
malicious TSV content despite rehashed internal SHA256SUMS and updated
external sidecars, lost view envelope, removed teaching_delta, stale details
and nonneutral card type. Also checks that input modifications after
packaging do not change the audited ZIP content.

- Stage3–4 compatibility CI run:
  https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/actions/runs/40877198409
  Ubuntu and Windows PASS, 19/19 new cases per OS plus 56, 18, 14,
  33, 43, 28 pytest and 49, 23 unittest per OS PASS.
- Existing content ZIP safety CI:
  https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit/actions/runs/40877198346
  Ubuntu and Windows PASS.
- Existing exact-current v486 real-browser isolated positive and negative
  import/export lifecycle CI: https://github.com/hosseinmehdizade-tech/German-Flashcards-Pro/actions/runs/40875222868
  7/7 checks per OS PASS, still only synthetic users/cards.

**Not claimed:** independent actual linguistic Stage4 signoff, original
source re-extraction, complete final vocabulary delivery, true end-to-end
production Stage5–7, real learner data safety, license to publish, or
authorization to migrate the proposed Stage45 format.

Historical A2-L24 editorial reference SHA 9aa0f362... stays unresolved.
OP-01 remote Git writer registry stays DENY_ALL with 0 grants.
