"""OP-02 nonactive archive/member/card evidence-binding contract synthetic tests.

All fixtures are original synthetic data; no registered learner/source ZIPs
are checked into Git and no active Stage3C writer is modified.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import zipfile

import pytest

MODULE = Path(__file__).resolve().parents[1] / "validate_stage3c_proof_binding.py"
spec = importlib.util.spec_from_file_location("op02_stage3c_binding", MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

SOURCE = "01-Source-Inventory/SOURCE-OCCURRENCES.json"
EDITORIAL = "20-Stage3C/REVIEWED-EDITORIAL.json"
LOCKED = "04-Historical-Parent-Audit/EXACT-IMMUTABLE-REUSE.json"
LEDGER = "20-Stage3C/ENRICHMENT-COMPLETENESS.json"


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def zip_bytes(members):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return out.getvalue()


def fixture():
    original = {"id": "locked-synthetic", "back": "ثبت تاریخی"}
    parent_blob = encoded([original])
    parent_zip = zip_bytes({LOCKED: parent_blob})
    parent_sha = m.sha(parent_zip)
    editorial_blob = encoded({"authored_targets": [{"id": "new-synthetic", "de": "lernen"}]})
    source_blob = encoded({"occurrences": [
        {"occurrence_id": "test-row-0001", "source_id": "synthetic-source",
         "locator": {"row": 1}, "source_row_payload_sha256": "f" * 64}
    ]})
    stage3c = {
        "summary": {"stage3c_editorial_sha256": m.sha(editorial_blob),
                    "targets": 2, "dimension_cells": 4, "unresolved_cells": 0,
                    "status_counts": {"VERIFIED_PRESENT": 3, "CLOSED_NO_FORCE": 1}},
        "targets": [
            {"id": "new-synthetic", "dimensions": {
                "sense": {"status": "VERIFIED_PRESENT", "basis_refs": [{
                    "kind": "EDITORIAL_REVIEW", "archive_id": "candidate",
                    "path": EDITORIAL, "artifact_sha256": m.sha(editorial_blob),
                    "target_id": "new-synthetic", "dimension": "sense",
                }]},
                "audio": {"status": "VERIFIED_PRESENT", "basis_refs": [{
                    "kind": "SOURCE", "source_archive_id": "candidate",
                    "source_member_sha256": m.sha(source_blob),
                    "source_id": "synthetic-source", "source_occurrence_id": "test-row-0001",
                    "source_ordinal": 1, "source_row_payload_sha256": "f" * 64,
                }]},
                "combinations": {"status": "CLOSED_NO_FORCE", "reason_code": "NO_DELTA",
                                 "basis_refs": []},
            }},
            {"id": "locked-synthetic", "dimensions": {
                "examples": {"status": "VERIFIED_PRESENT", "basis_refs": [{
                    "kind": "LOCKED_PARENT", "archive_id": "parent",
                    "archive_sha256": parent_sha, "path": LOCKED,
                    "member_sha256": m.sha(parent_blob),
                    "artifact_snapshot_sha256": m.sha(encoded(original)),
                    "snapshot_sha_scope": "JSON_CANONICAL_RECORD_V1",
                    "target_id": "locked-synthetic",
                }]},
            }},
        ],
    }
    data = {SOURCE: source_blob, EDITORIAL: editorial_blob, LEDGER: encoded(stage3c)}
    candidate_zip = zip_bytes(data)
    contract = {
        "schema": m.SCHEMA, "status": m.STATUS,
        "candidate_archive_id": "candidate",
        "archives": [
            {"id": "candidate", "sha256": m.sha(candidate_zip)},
            {"id": "parent", "sha256": parent_sha},
        ],
        "completeness": {"path": LEDGER, "sha256": m.sha(data[LEDGER])},
        "source_inventory": {
            "archive_id": "candidate", "archive_sha256": m.sha(candidate_zip),
            "path": SOURCE, "sha256": m.sha(source_blob)
        },
    }
    return contract, {"candidate": candidate_zip, "parent": parent_zip}, data, stage3c


def rewrite_ledger(contract, archives, data, stage3c):
    data[LEDGER] = encoded(stage3c)
    archives["candidate"] = zip_bytes(data)
    contract["archives"][0]["sha256"] = m.sha(archives["candidate"])
    contract["completeness"]["sha256"] = m.sha(data[LEDGER])
    contract["source_inventory"]["archive_sha256"] = m.sha(archives["candidate"])


def errors(c, a):
    return m.validate(c, a)["errors"]


def test_positive_exact_zip_member_card_and_three_distinct_evidence_kinds():
    c,a,_,_ = fixture()
    result = m.validate(c, a)
    assert result["errors"] == []
    assert result["status"] == "PASS_SCOPED_DETERMINISTIC_PROOF_BINDING_ONLY"
    assert result["counts"]["refs_editorial_review"] == 1
    assert result["counts"]["refs_source"] == 1
    assert result["counts"]["refs_locked_parent"] == 1
    assert any("Stage5/6/7" in x for x in result["claims_not_proven"])


def test_candidate_hash_pinned_outside_zip_not_recursively_embedded():
    c,a,_,_ = fixture()
    assert "archive_sha256" not in json.loads(
        zipfile.ZipFile(io.BytesIO(a["candidate"])).read(LEDGER)
    )["targets"][0]["dimensions"]["sense"]["basis_refs"][0]
    assert errors(c, a) == []


def test_archive_byte_swap_rejected_without_any_fallback():
    c,a,_,_ = fixture()
    a["parent"] = zip_bytes({LOCKED: b"replacement"})
    assert any("ARCHIVE_SHA_OR_SIZE_MISMATCH" in x for x in errors(c,a))


def test_wrong_reference_to_previous_version_rejected():
    c,a,data,l = fixture()
    l["targets"][1]["dimensions"]["examples"]["basis_refs"][0]["archive_sha256"] = "0"*64
    rewrite_ledger(c,a,data,l)
    assert any("IMMUTABLE_PREDECESSOR_ARCHIVE_SHA_REQUIRED" in x for x in errors(c,a))


def test_unknown_parent_archive_never_inferred_from_matching_basename():
    c,a,data,l = fixture()
    l["targets"][1]["dimensions"]["examples"]["basis_refs"][0]["archive_id"] = "unknown"
    rewrite_ledger(c,a,data,l)
    assert any("IMMUTABLE_PREDECESSOR_ARCHIVE_SHA_REQUIRED" in x for x in errors(c,a))


def test_stale_member_sha_mismatch_fails_closed():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["sense"]["basis_refs"][0]["artifact_sha256"] = "0"*64
    rewrite_ledger(c,a,data,l)
    assert any("EDITORIAL_REVIEW_MEMBER_SHA_MISMATCH" in x for x in errors(c,a))


def test_summary_sha_stale_blocks_even_if_member_path_exists():
    c,a,data,l = fixture()
    l["summary"]["stage3c_editorial_sha256"] = "0"*64
    rewrite_ledger(c,a,data,l)
    assert "EDITORIAL_REFERENCE_DIFFERS_FROM_SUMMARY" in errors(c,a)


def test_circular_archive_sha_inside_candidate_zip_rejected():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["sense"]["basis_refs"][0]["archive_sha256"] = "a"*64
    rewrite_ledger(c,a,data,l)
    assert "CIRCULAR_CANDIDATE_ARCHIVE_SHA" in errors(c,a)


def test_editorial_wrong_card_id_rejected():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["sense"]["basis_refs"][0]["target_id"] = "another"
    rewrite_ledger(c,a,data,l)
    assert "EDITORIAL_REVIEW_CARD_ID_DRIFT" in errors(c,a)


def test_editorial_wrong_facet_rejected():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["sense"]["basis_refs"][0]["dimension"] = "translations"
    rewrite_ledger(c,a,data,l)
    assert "EDITORIAL_DIMENSION_DRIFT" in errors(c,a)


def test_locked_record_sha_distinct_from_full_member_sha():
    c,a,data,l = fixture()
    ref = l["targets"][1]["dimensions"]["examples"]["basis_refs"][0]
    assert ref["artifact_snapshot_sha256"] != ref["member_sha256"]
    ref["artifact_snapshot_sha256"] = ref["member_sha256"]
    rewrite_ledger(c,a,data,l)
    assert "LOCKED_PARENT_RECORD_DIGEST_MISMATCH" in errors(c,a)


def test_locked_member_sha_stale_rejected():
    c,a,data,l = fixture()
    l["targets"][1]["dimensions"]["examples"]["basis_refs"][0]["member_sha256"] = "b"*64
    rewrite_ledger(c,a,data,l)
    assert any("LOCKED_PARENT_MEMBER_SHA_MISMATCH" in x for x in errors(c,a))


def test_source_ordinal_drift_rejected():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["audio"]["basis_refs"][0]["source_ordinal"] = 999
    rewrite_ledger(c,a,data,l)
    assert "SOURCE_ID_ROW_OR_PAYLOAD_HASH_DRIFT" in errors(c,a)


def test_source_row_content_hash_drift_rejected():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["audio"]["basis_refs"][0][
        "source_row_payload_sha256"] = "9"*64
    rewrite_ledger(c,a,data,l)
    assert "SOURCE_ID_ROW_OR_PAYLOAD_HASH_DRIFT" in errors(c,a)


def test_source_inventory_version_mismatch_rejected():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["audio"]["basis_refs"][0][
        "source_member_sha256"] = "9"*64
    rewrite_ledger(c,a,data,l)
    assert "SOURCE_REFERENCE_NOT_ARCHIVE_BOUND" in errors(c,a)


def test_no_evidence_means_verified_is_blocked():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["sense"]["basis_refs"] = []
    rewrite_ledger(c,a,data,l)
    assert "VERIFIED_WITHOUT_EVIDENCE" in errors(c,a)


def test_no_reason_for_closed_no_force_rejected():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["combinations"].pop("reason_code")
    rewrite_ledger(c,a,data,l)
    assert "CLOSED_NO_FORCE_WITHOUT_REASON" in errors(c,a)


def test_duplicate_target_id_rejected():
    c,a,data,l = fixture()
    l["targets"][1]["id"] = "new-synthetic"
    rewrite_ledger(c,a,data,l)
    assert "DUPLICATE_OR_MISSING_TARGET_ID" in errors(c,a)


def test_missing_member_is_not_implicit_predecessor_lookup():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["sense"]["basis_refs"][0]["path"] = "other/name.json"
    rewrite_ledger(c,a,data,l)
    assert "EDITORIAL_REVIEW_MEMBER_NOT_PRESENT_IN_EXACT_ARCHIVE" in errors(c,a)


def test_unknown_kind_blocked_no_auto_approval():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["sense"]["basis_refs"][0]["kind"] = "HUMAN_CONFIRMED"
    rewrite_ledger(c,a,data,l)
    assert "UNKNOWN_EVIDENCE_KIND" in errors(c,a)


def test_symlink_archive_member_rejected():
    c,a,_,_ = fixture()
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        info = zipfile.ZipInfo(EDITORIAL)
        info.create_system = 3
        info.external_attr = (0o120777 << 16)
        archive.writestr(info, b"symlink-target")
    z = out.getvalue()
    with pytest.raises(ValueError, match="UNSAFE_ARCHIVE_MEMBERS"):
        m.read_exact_zip(z, m.sha(z))


def test_missing_archive_set_rejected():
    c,a,_,_ = fixture()
    del a["parent"]
    assert "ARCHIVE_SET_NOT_EXACTLY_PINNED" in errors(c,a)


def test_unapproved_active_mode_is_denied():
    c,a,_,_ = fixture()
    c["status"] = "ACTIVE_PRODUCTION"
    assert "NONACTIVE_SCHEMA_OR_STATUS_REQUIRED" in errors(c,a)


def test_zip_path_traversal_rejected():
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("../secret.txt", "secret")
    data = out.getvalue()
    with pytest.raises(ValueError, match="UNSAFE_ARCHIVE_MEMBERS"):
        m.read_exact_zip(data, m.sha(data))


def test_malformed_unhashable_candidate_archive_id_fail_closed():
    c,a,_,_ = fixture()
    c["candidate_archive_id"] = []
    assert "CANDIDATE_ARCHIVE_UNPINNED" in errors(c,a)


def test_malformed_unhashable_editorial_archive_id_fail_closed():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["sense"]["basis_refs"][0]["archive_id"] = []
    rewrite_ledger(c,a,data,l)
    assert "EVIDENCE_ARCHIVE_ID_MALFORMED" in errors(c,a)


def test_malformed_unhashable_evidence_kind_fail_closed():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["sense"]["basis_refs"][0]["kind"] = []
    rewrite_ledger(c,a,data,l)
    assert "UNKNOWN_EVIDENCE_KIND" in errors(c,a)


def test_malformed_unhashable_source_occurrence_id_fail_closed():
    c,a,data,l = fixture()
    l["targets"][0]["dimensions"]["audio"]["basis_refs"][0]["source_occurrence_id"] = []
    rewrite_ledger(c,a,data,l)
    assert "SOURCE_OCCURRENCE_NOT_FOUND" in errors(c,a)


def test_historical_legacy_editorial_ref_without_version_not_promoted():
    c,a,data,l = fixture()
    ref = l["targets"][0]["dimensions"]["sense"]["basis_refs"][0]
    ref.pop("archive_id")
    rewrite_ledger(c,a,data,l)
    assert "EVIDENCE_ARCHIVE_ID_MALFORMED" in errors(c,a)


def test_parent_ref_wrong_target_does_not_pass_exact_card_identity():
    c,a,data,l = fixture()
    l["targets"][1]["dimensions"]["examples"]["basis_refs"][0]["target_id"] = "missing-parent"
    rewrite_ledger(c,a,data,l)
    assert "LOCKED_PARENT_CARD_ID_DRIFT" in errors(c,a)


def test_parent_target_absent_even_with_self_consistent_ledger_and_ref():
    c,a,data,l = fixture()
    l["targets"][1]["id"] = "missing-parent"
    l["targets"][1]["dimensions"]["examples"]["basis_refs"][0]["target_id"] = "missing-parent"
    rewrite_ledger(c,a,data,l)
    assert "LOCKED_PARENT_TARGET_MISSING_OR_DUPLICATE" in errors(c,a)


def test_locked_parent_from_current_candidate_archive_is_forbidden():
    c,a,data,l = fixture()
    ref = l["targets"][1]["dimensions"]["examples"]["basis_refs"][0]
    ref["archive_id"] = "candidate"
    ref.pop("archive_sha256")
    rewrite_ledger(c,a,data,l)
    assert "LOCKED_PARENT_IMMUTABLE_PREDECESSOR_REQUIRED" in errors(c,a)


def test_forged_stage3c_status_count_cannot_pass():
    c,a,data,l = fixture()
    l["summary"]["status_counts"]["VERIFIED_PRESENT"] = 4
    rewrite_ledger(c,a,data,l)
    assert "STAGE3C_STATUS_COUNTS_DRIFT" in errors(c,a)
