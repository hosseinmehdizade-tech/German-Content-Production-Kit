"""OP-02 nonactive role uniqueness and postbuild byte-binding with real builder.

Existing clean builder remains unchanged; every archive here is synthetic and
confined to disposable pytest temporary storage.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from test_stage5_clean_zip_v486 import built as underlying_built
from test_stage5_clean_zip_v486 import (
    DIRECT, CANON, QA, MAP, DELIVERY, SUMS,
    package_members, repack, fix_internal_sums
)
from audit_stage5_input_role_binding import scan_input, verify_postbuild
from validate_stage45_teaching_delta_parity import sha
from audit_stage5_clean_zip_v486 import ROOT as ZROOT


@pytest.fixture
def built(underlying_built):
    return underlying_built

def audit(b):
    preflight = scan_input(b["input_dir"])
    return verify_postbuild(preflight, b["zip"], sha(b["zip"]))

def duplicate(b, name, from_name):
    (b["input_dir"] / name).write_bytes((b["input_dir"] / from_name).read_bytes())

def rebuild_with_rehash(b, member, data):
    parts = package_members(b["zip"])
    parts[ZROOT + member] = data
    fix_internal_sums(parts)
    return repack(parts)


def test_unique_real_builder_inputs_and_exact_output_pass(built):
    check = scan_input(built["input_dir"])
    assert check["status"] == "PASS_SCOPED_SINGLE_CANDIDATE_INPUT_ONLY"
    assert set(check["roles"]) == {
        "direct-import-tsv", "canonical-json", "source-output-map-tsv", "qa-report"
    }
    out = audit(built)
    assert out["status"] == "PASS_SCOPED_LOCAL_ROLE_BYTES_RETAINED_IN_ZIP_ONLY"
    assert out["zip_sha256"] == sha(built["zip"])


def test_original_input_bytes_have_four_distinct_filenames_and_hashes(built):
    s = scan_input(built["input_dir"])
    names = [v["filename"] for v in s["roles"].values()]
    assert len(set(names)) == 4
    assert all((built["input_dir"]/v["filename"]).stat().st_size == v["size"]
               for v in s["roles"].values())


@pytest.mark.parametrize("new_name,existing_name,which_role", [
    ("Synthetic-Universal-v0.tsv", DIRECT, "direct-import-tsv"),
    ("Synthetic-Import.tsv", DIRECT, "direct-import-tsv"),
    ("Synthetic-cards.tsv", DIRECT, "direct-import-tsv"),
    ("Second-canonical.json", CANON, "canonical-json"),
    ("Second-source-output-map.tsv", MAP, "source-output-map-tsv"),
    ("Second-verification.json", QA, "qa-report"),
    ("Second-QA.json", QA, "qa-report"),
])
def test_two_matching_candidates_block_even_if_exact_same_bytes(
        built, new_name, existing_name, which_role):
    duplicate(built, new_name, existing_name)
    s = scan_input(built["input_dir"])
    assert s["status"] == "BLOCKED"
    assert "AMBIGUOUS_ROLE:" + which_role in s["errors"]
    assert s["candidate_counts"][which_role] == 2


def test_case_insensitive_same_role_collision_blocks(built):
    duplicate(built, "Synthetic-universal.TSV", DIRECT)
    s = scan_input(built["input_dir"])
    assert s["status"] == "BLOCKED"
    assert "AMBIGUOUS_ROLE:direct-import-tsv" in s["errors"]


def test_no_selected_direct_import_is_blocked(built):
    (built["input_dir"]/DIRECT).unlink()
    s = scan_input(built["input_dir"])
    assert "MISSING_ROLE:direct-import-tsv" in s["errors"]


def test_no_required_canonical_is_blocked(built):
    (built["input_dir"]/CANON).unlink()
    assert "MISSING_ROLE:canonical-json" in scan_input(built["input_dir"])["errors"]


def test_role_filename_matching_more_than_one_type_blocks(built):
    (built["input_dir"]/QA).unlink()
    (built["input_dir"]/CANON).unlink()
    (built["input_dir"]/"combo-canonical-QA.json").write_bytes(b"{}")
    s = scan_input(built["input_dir"])
    assert s["status"] == "BLOCKED"
    assert "ROLE_COLLISION_ACROSS_TYPES" in s["errors"]


def test_source_inventory_cannot_masquerade_as_direct_import(built):
    (built["input_dir"]/DIRECT).unlink()
    (built["input_dir"]/"source-inventory-cards.tsv").write_bytes(b"not import")
    s = scan_input(built["input_dir"])
    assert "SOURCE_INVENTORY_IS_NOT_DIRECT_IMPORT" in s["errors"]


def test_changed_selected_input_after_package_detected(built):
    s = scan_input(built["input_dir"])
    assert s["status"].startswith("PASS_SCOPED")
    selected = built["input_dir"] / QA
    selected.write_bytes(selected.read_bytes() + b" ")
    after = scan_input(built["input_dir"])
    assert after["roles"] != s["roles"]


def test_preflight_pinned_unchanged_zip_stays_pass_when_source_modified_later(built):
    # Postbuilt ZIP binding proves its own exact selected preflight bytes.
    # The CLI also does a second source directory scan to catch later edits.
    s = scan_input(built["input_dir"])
    selected = built["input_dir"] / QA
    selected.write_bytes(selected.read_bytes() + b" ")
    assert verify_postbuild(s, built["zip"], sha(built["zip"]))["status"].startswith("PASS_SCOPED")
    assert scan_input(built["input_dir"])["roles"] != s["roles"]


@pytest.mark.parametrize("role_name,member_name", [
    ("direct-import-tsv", DIRECT),
    ("canonical-json", CANON),
    ("source-output-map-tsv", MAP),
    ("qa-report", QA),
])
def test_self_consistent_rebuilt_zip_manifest_still_rejects_unapproved_content(
        built, role_name, member_name):
    parts = package_members(built["zip"])
    changed = parts[ZROOT + member_name] + b" "
    forged = rebuild_with_rehash(built, member_name, changed)
    before = scan_input(built["input_dir"])
    outcome = verify_postbuild(before, forged, sha(forged))
    assert outcome["status"] == "BLOCKED"
    assert "POSTBUILD_ROLE_BYTES_CHANGED:" + role_name in outcome["errors"]


def test_renamed_role_in_manifest_refused_even_when_zip_sums_updated(built):
    parts = package_members(built["zip"])
    j = json.loads(parts[ZROOT + DELIVERY])
    j["roles"]["direct-import-tsv"] = "DIFFERENT-IMPORT.tsv"
    parts[ZROOT + DELIVERY] = json.dumps(j).encode("utf-8")
    fix_internal_sums(parts)
    forged = repack(parts)
    out = verify_postbuild(scan_input(built["input_dir"]), forged, sha(forged))
    assert "POSTBUILD_ROLE_NAME_OR_SELECTION_DRIFT:direct-import-tsv" in out["errors"]


def test_wrong_final_zip_digest_blocks(built):
    p = scan_input(built["input_dir"])
    out = verify_postbuild(p, built["zip"], "0"*64)
    assert out["errors"] == ["POSTBUILD_ZIP_EXACT_SHA_MISMATCH"]


def test_ambiguous_input_proof_cannot_be_overridden_by_valid_older_zip(built):
    duplicate(built, "Other-Universal.tsv", DIRECT)
    s = scan_input(built["input_dir"])
    assert s["status"] == "BLOCKED"
    assert verify_postbuild(s, built["zip"], sha(built["zip"]))["status"] == "BLOCKED"


def test_path_symlink_matching_role_fails_closed_if_supported(built, tmp_path):
    other = tmp_path / "untrusted.tsv"
    other.write_text("id\tfront\tback\n", encoding="utf-8")
    link = built["input_dir"] / "malicious-cards.tsv"
    try:
        link.symlink_to(other)
    except (OSError, NotImplementedError):
        pytest.skip("OS does not permit unprivileged symlinks")
    s = scan_input(built["input_dir"])
    assert "UNSAFE_ROLE_CANDIDATE:malicious-cards.tsv" in s["errors"]


def test_unknown_extra_unmatched_document_does_not_authorize_role_switch(built):
    (built["input_dir"]/"notes.txt").write_text("not a role", encoding="utf-8")
    assert audit(built)["status"].startswith("PASS_SCOPED")
