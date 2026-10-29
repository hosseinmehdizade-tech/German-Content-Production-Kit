# OP-01/OP-02 — Materialized Stage3 output identity guard (nonactive)

**Scope:** Validation of raw bytes, not content editing or release. This follows the 2026-10-29 PR35 per-ID metadata guard.

## Actual security/quality gap

The existing proposed Stage3/4 compatibility check compares Stage3's self-reported `unit_sha256_by_id` to Stage4's `unit_dispositions[].unit_sha256`. A consistent but false hash in both reports can pass. The Stage3 `output_sha256` and Stage4 `reviewed_output_sha256` can likewise agree without any real bytes being read. A green metadata check cannot be reported as exact CURRENT content authentication.

## Additive nonactive diagnostic

`Verification/verify_stage34_materialized_output.py` reads a real candidate Stage3 output JSON with `learning_units`, checks its **whole raw-file SHA256** against a separately supplied expected digest, independently rehashes every full unit object using sorted-key compact UTF-8 JSON, checks unique stable IDs and exact unit-set parity with Stage3 and Stage4 claims, and preserves all original metadata guards.

Usage (only with independently obtained source bytes/hash):

```bash
python Verification/verify_stage34_materialized_output.py \
  --stage3 stage3-metadata.json --stage4 stage4-metadata.json \
  --materialized-output exact-stage3-output.json \
  --external-output-sha256 ACTUAL_64_HEX_SHA256
```

This supports **JSON learning_units only**. Other formats must receive a separately validated adapter. A caller-provided pin is not independently authenticated merely because the numbers agree. Direct source provenance, PDF citations, AI semantic quality, real reviewer identity, and user authorization for CURRENT remain distinct requirements.

Even if every byte and unit digest matches, the only positive status is `PASS_SCOPED_OUTPUT_BYTES_UNIT_IDENTITY_ONLY`; response fields `stage4_semantic_pass=false`, `issuer_authenticated=false`, `production_authorized=false`, `source_fidelity_verified=false`, and `performed_writes=false`.

## Regression safety

Synthetic tests exercise synchronized false unit hashes (which the old metadata-only validator accepts), modified real Persian field, raw byte changes and separately pinned SHA drift, duplicate IDs and duplicate JSON keys, NaN, hidden extra unit, missing reviewed-unit entries, unsupported format and false issuer claims. CI runs the tests on Ubuntu and Windows. No real source, Content/LOCKED/LATEST, Library, writer scope, app runtime or visible UI is changed.

**Next actual stage:** Independently resolve a trusted CURRENT authority/pin and execute real source/DE-FA-EN semantic review in an explicitly authorized content workstream. Until then OP01 remains DENY_ALL and Stage4 real remains OPEN.
