"""Synthetic-only fail-closed Stage4 corrected-application byte binding."""
import copy
import json
import sys
from pathlib import Path
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from audit_stage4_snapshot_review_receipt import digest, unit_hash, DISPOSITIONS
from verify_stage4_corrected_application import bind_corrections, SCHEMA
from test_stage4_snapshot_review_receipt import fixtures, encoded


def case():
    f = fixtures()
    after = json.loads(f[1])
    after["learning_units"][0]["persian_meaning"] = "پاسخ دادن یا جواب گفتن"
    updated = encoded(after)
    review = f[5]["reviews"][0]
    review["disposition"] = "corrected"
    review["applied_change_sha256"] = unit_hash(after["learning_units"][0])
    f[5]["disposition_counts"] = {k: (1 if k in ("corrected", "verified_keep") else 0)
                                 for k in DISPOSITIONS}
    return f, updated


def check(f, updated, *, readback=None, expected=None):
    return bind_corrections(
        f[0], f[1], f[2], f[3], f[4], encoded(f[5]), updated,
        updated if readback is None else readback,
        digest(updated) if expected is None else expected
    )


def must_block(result, code):
    assert result["status"] == "BLOCKED_CORRECTED_APPLICATION_BYTES", result
    assert code in result["errors"], result
    for key in ("remote_cas_verified", "issuer_authenticated", "source_fidelity_verified",
                "stage4_semantic_pass", "stage5_allowed", "stage6_pass",
                "stage7_release_final", "production_authorized", "performed_writes"):
        assert result[key] is False


def test_real_before_after_byte_binding_stays_nonactive():
    f, updated = case()
    result = check(f, updated)
    assert result["schema"] == SCHEMA
    assert result["status"] == "PASS_SCOPED_CORRECTED_BYTES_ONLY_NOT_STAGE4_SIGNOFF", result
    assert result["claimed_corrected_units"] == ["ahl-lu-synthetic-0"]
    assert result["observed_changed_units"] == ["ahl-lu-synthetic-0"]
    assert result["original_receipt_status"] == "BLOCKED_REVIEW_RECEIPT_BINDING"
    assert result["errors"] == []
    assert result["postedit_bytes_read"] is True
    assert result["remote_cas_verified"] is False
    assert result["stage4_semantic_pass"] is False
    assert result["stage5_allowed"] is False
    assert result["performed_writes"] is False


def test_no_change_cannot_be_claimed_as_applied_correction():
    f, _ = case()
    must_block(check(f, f[1]), "CHANGED_UNITS_DIFFER_FROM_CORRECTED_RECEIPT")


def test_unlisted_additional_unit_edit_rejected():
    f, after = case()
    doc = json.loads(after)
    doc["learning_units"][1]["definition_de"] = "extra edit"
    must_block(check(f, encoded(doc)), "CHANGED_UNITS_DIFFER_FROM_CORRECTED_RECEIPT")


def test_changed_unit_hash_not_writable_from_self_claim():
    f, after = case()
    f[5]["reviews"][0]["applied_change_sha256"] = "a"*64
    must_block(check(f, after), "CORRECTED_POSTEDIT_UNIT_SHA_MISMATCH:ahl-lu-synthetic-0")


def test_unrelated_reviewer_ledger_corruption_is_not_ignored():
    f, after = case()
    f[5]["disposition_counts"]["verified_keep"] = 0
    must_block(check(f, after), "BASE_RECEIPT:DISPOSITION_COUNT_MISMATCH")


def test_wrong_external_postedit_sha_rejected():
    f, after = case()
    must_block(check(f, after, expected="f"*64), "POSTEDIT_EXPECTED_SHA_MISMATCH")


def test_correct_content_but_wrong_readback_bytes_rejected():
    f, after = case()
    must_block(check(f, after, readback=after+b"\n"), "POSTEDIT_READBACK_BYTE_MISMATCH")


def test_unit_order_change_is_not_a_correction():
    f, after = case()
    doc = json.loads(after)
    doc["learning_units"].reverse()
    must_block(check(f, encoded(doc)), "POSTEDIT_UNIT_IDENTITY_OR_ORDER_DRIFT")


def test_unreviewed_unit_addition_rejected():
    f, after = case()
    doc = json.loads(after)
    doc["learning_units"].append(dict(doc["learning_units"][1], id="ahl-extra"))
    must_block(check(f, encoded(doc)), "POSTEDIT_UNIT_COUNT_CHANGED")


def test_non_unit_root_metadata_edit_rejected():
    f, after = case()
    doc = json.loads(after)
    doc["fake_finality"] = True
    must_block(check(f, encoded(doc)), "POSTEDIT_ROOT_METADATA_DRIFT")


def test_source_provenance_cannot_silently_change():
    f, after = case()
    doc = json.loads(after)
    doc["learning_units"][0]["provenance"] = {"sources": ["fabricated"]}
    f[5]["reviews"][0]["applied_change_sha256"] = unit_hash(doc["learning_units"][0])
    must_block(check(f, encoded(doc)), "CORRECTED_UNIT_PROVENANCE_MUTATED:ahl-lu-synthetic-0")


def test_stale_old_baseline_or_receipt_blocked():
    f, after = case()
    f[1] += b" "
    must_block(check(f, after), "BASE_RECEIPT:SNAPSHOT_BYTE_PIN_MISMATCH:canonical_sha256")


def test_self_claimed_new_field_does_not_authorize():
    f, after = case()
    f[5]["issuer_authenticated"] = True
    must_block(check(f, after), "BASE_RECEIPT:RECEIPT_SHAPE_INVALID")


def test_no_corrected_review_is_not_positive():
    f, after = case()
    f[5]["reviews"][0]["disposition"] = "verified_keep"
    f[5]["reviews"][0]["applied_change_sha256"] = None
    f[5]["disposition_counts"]["corrected"] = 0
    f[5]["disposition_counts"]["verified_keep"] = 2
    must_block(check(f, after), "NO_CORRECTED_UNITS_CLAIMED")


def test_wrong_source_pdf_pin_remains_blocked():
    f, after = case()
    f[4]["b1-c2"] = b"tampered source"
    must_block(check(f, after), "BASE_RECEIPT:SOURCE_RAW_SHA_MISMATCH:b1-c2")


def test_replayed_stale_whole_unit_hash_is_blocked():
    f, after = case()
    f[5]["reviews"][0]["unit_sha256"] = "f"*64
    must_block(check(f, after), "BASE_RECEIPT:UNIT_CONTENT_SHA_DRIFT:ahl-lu-synthetic-0")


def test_unparseable_postedit_cannot_pass():
    f, _ = case()
    result = check(f, b'{"learning_units": invalid}')
    assert result["status"] == "BLOCKED_CORRECTED_APPLICATION_BYTES"
    assert any(x.startswith("MALFORMED_CORRECTION_BINDING:") for x in result["errors"])


def test_duplicate_json_key_postedit_cannot_pass():
    f, after = case()
    corrupt = after.replace(b'"learning_units":', b'"learning_units":[],"learning_units":', 1)
    result = check(f, corrupt)
    assert result["status"] == "BLOCKED_CORRECTED_APPLICATION_BYTES"


def test_missing_external_pin_is_blocked():
    f, after = case()
    must_block(check(f, after, expected=""), "EXPECTED_POSTEDIT_SHA256_INVALID")


def test_partial_original_review_may_bind_bytes_but_never_sign_off():
    f, after = case()
    f[5]["reviews"].pop()
    f[5]["unreviewed"] = 1
    f[5]["reviewed_unique"] = 1
    f[5]["disposition_counts"]["verified_keep"] = 0
    result = check(f, after)
    assert result["status"] == "PASS_SCOPED_CORRECTED_BYTES_ONLY_NOT_STAGE4_SIGNOFF", result
    assert not result["stage4_semantic_pass"] and not result["production_authorized"]
