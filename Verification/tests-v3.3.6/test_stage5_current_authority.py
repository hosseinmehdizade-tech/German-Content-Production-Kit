"""Synthetic real-builder tests for NONACTIVE Stage5 exact CURRENT sidecar binding."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from test_stage5_clean_zip_v486 import (
    built as underlying_built, DIRECT, SUMS, package_members, repack
)
from audit_stage5_clean_zip_v486 import ROOT as ZROOT
from audit_stage5_input_role_binding import verify_postbuild
from audit_stage5_input_role_binding import scan_input
from audit_stage5_current_authority import SCHEMA, digest, verify

WORKSTREAM = "synthetic-op02-workstream"
ARTIFACT = "synthetic-op02-v1"
SOURCE_SHA = digest(b"separately registered original source")
PARENT_SHA = digest(b"separately verified parent artifact")


@pytest.fixture
def built(underlying_built):
    return underlying_built


def sidecar(b):
    pre = scan_input(b["input_dir"])
    assert pre["status"] == "PASS_SCOPED_SINGLE_CANDIDATE_INPUT_ONLY"
    return {
        "schema": SCHEMA, "status": "NONACTIVE_EXTERNAL_PIN",
        "workstream_id": WORKSTREAM, "artifact_id": ARTIFACT,
        "registered_source_sha256": SOURCE_SHA,
        "parent_artifact_sha256": PARENT_SHA,
        "lock_state": "EDITABLE_CURRENT",
        "roles": copy.deepcopy(pre["roles"]),
    }


def assess(b, document=None, *, pinned=None, **overrides):
    document = sidecar(b) if document is None else document
    raw = json.dumps(document, ensure_ascii=False, sort_keys=True).encode("utf-8")
    args = dict(
        authority_bytes=raw,
        externally_pinned_authority_sha256=digest(raw) if pinned is None else pinned,
        expected_workstream_id=WORKSTREAM,
        expected_artifact_id=ARTIFACT,
        expected_source_sha256=SOURCE_SHA,
        expected_parent_sha256=PARENT_SHA,
        selected_inputs=scan_input(b["input_dir"]),
        finished_zip_bytes=b["zip"],
        expected_zip_sha256=digest(b["zip"]),
    )
    args.update(overrides)
    return verify(**args)


def test_exact_external_pin_with_real_builder_passes(built):
    assert assess(built)["status"] == "PASS_SCOPED_EXTERNALLY_PINNED_CURRENT_ROLE_BYTES_ONLY"


def test_valid_wrong_single_tsv_without_ambiguity_rejected(built):
    pinned_original = sidecar(built)
    f = built["input_dir"] / DIRECT
    old = f.read_bytes()
    assert b"synthetic DE" in old
    f.write_bytes(old.replace(b"synthetic DE", b"different DE"))
    assert scan_input(built["input_dir"])["status"].startswith("PASS_SCOPED")
    result = assess(built, pinned_original)
    assert "SELECTED_INPUT_NOT_PINNED_CURRENT:direct-import-tsv" in result["errors"]


def test_actual_builder_can_package_wrong_unique_valid_tsv_but_pin_blocks(built, tmp_path):
    original = sidecar(built)
    target = built["input_dir"] / DIRECT
    target.write_bytes(target.read_bytes().replace(b"synthetic DE", b"revised  DE"))
    output = tmp_path / "altered-unique.zip"
    run = subprocess.run(
        [sys.executable, str(HERE.parent.parent / "Tools" / "build_clean_delivery.py"),
         str(built["input_dir"]), str(output), "--purpose", "stage5_acceptance"],
        text=True, capture_output=True, timeout=90,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
    b2 = dict(built, zip=output.read_bytes())
    result = assess(b2, original)
    assert result["status"] == "BLOCKED"
    assert "SELECTED_INPUT_NOT_PINNED_CURRENT:direct-import-tsv" in result["errors"]


@pytest.mark.parametrize("field,new_value,error", [
    ("workstream_id","other-workstream","EXTERNAL_IDENTITY_MISMATCH:workstream_id"),
    ("artifact_id","other-artifact","EXTERNAL_IDENTITY_MISMATCH:artifact_id"),
    ("registered_source_sha256",digest(b"wrong-source"),"EXTERNAL_IDENTITY_MISMATCH:registered_source_sha256"),
    ("parent_artifact_sha256",digest(b"wrong-parent"),"EXTERNAL_IDENTITY_MISMATCH:parent_artifact_sha256"),
    ("lock_state","LOCKED","LOCKED_OR_UNPROVEN_EDITABILITY"),
    ("status","ACTIVE_PRODUCTION","AUTHORITY_SIDECAR_SCHEMA_OR_STATUS_INVALID"),
])
def test_external_identity_and_immutable_lock_fail_closed(built, field,new_value,error):
    doc = sidecar(built)
    doc[field] = new_value
    assert error in assess(built, doc)["errors"]


def test_sidecar_forgery_with_rehashed_zip_manifest_does_not_pass_original_pin(built):
    doc = sidecar(built)
    original_raw = json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    external_pin = digest(original_raw)
    doc["artifact_id"] = "forged-artifact"
    result = assess(built, doc, pinned=external_pin)
    assert "AUTHORITY_SIDECAR_SHA256_MISMATCH" in result["errors"]


def test_missing_independent_pin_blocks(built):
    assert "MISSING_INDEPENDENT_AUTHORITY_SHA256" in assess(built, pinned="")["errors"]


def test_unregistered_parent_hash_blocks_even_with_matching_sidecar(built):
    result = assess(built, expected_parent_sha256=digest(b"different-parent"))
    assert "EXTERNAL_IDENTITY_MISMATCH:parent_artifact_sha256" in result["errors"]


def test_wrong_zip_digest_blocks(built):
    assert "POSTBUILD:POSTBUILD_ZIP_EXACT_SHA_MISMATCH" in assess(
        built, expected_zip_sha256=digest(b"other zip"))["errors"]


def test_role_metadata_false_size_rejected_even_with_self_consistent_sidecar(built):
    doc = sidecar(built)
    doc["roles"]["qa-report"]["size"] += 1
    assert "SELECTED_INPUT_NOT_PINNED_CURRENT:qa-report" in assess(built, doc)["errors"]


def test_role_filename_collision_rejected(built):
    doc = sidecar(built)
    doc["roles"]["qa-report"]["filename"] = doc["roles"]["canonical-json"]["filename"]
    assert "AUTHORITY_ROLE_FILENAME_COLLISION" in assess(built, doc)["errors"]


def test_sidecar_unknown_field_not_accepted(built):
    doc = sidecar(built)
    doc["i_am_approved"] = True
    assert assess(built, doc)["errors"] == ["AUTHORITY_SIDECAR_UNEXPECTED_SCHEMA_KEYS"]


def test_zero_sha_external_source_not_accepted(built):
    assert "MISSING_OR_INVALID_EXTERNAL_SOURCE_SHA256" in assess(
        built, expected_source_sha256="0" * 64)["errors"]


def test_duplicate_candidate_rejected_even_when_pinned_original_is_valid(built):
    registered = sidecar(built)
    (built["input_dir"] / "Other-Universal.tsv").write_bytes(
        (built["input_dir"] / DIRECT).read_bytes()
    )
    result = assess(built, registered)
    assert result["status"] == "BLOCKED"
    assert "INPUT_ROLE_PREFLIGHT_NOT_PASS" in result["errors"]


def test_wrong_source_pin_cannot_self_attest(built):
    assert "EXTERNAL_IDENTITY_MISMATCH:registered_source_sha256" in assess(
        built, expected_source_sha256=digest(b"new source nobody approved"))["errors"]

def test_selection_snapshot_wrong_type_rejected_cleanly(built):
    result = assess(built, selected_inputs=[])
    assert result["status"] == "BLOCKED"
    assert "INPUT_ROLE_PREFLIGHT_NOT_PASS" in result["errors"]


def test_sidecar_invalid_roles_type_rejected_cleanly(built):
    doc = sidecar(built)
    doc["roles"] = []
    assert "AUTHORITY_ROLES_NOT_COMPLETE" in assess(built, doc)["errors"]


@pytest.mark.parametrize("invalid_filename", [[], {}, ["untrusted.tsv"], 3, None])
def test_malformed_role_filename_type_returns_blocked_not_exception(built, invalid_filename):
    doc = sidecar(built)
    doc["roles"]["qa-report"]["filename"] = invalid_filename
    result = assess(built, doc)
    assert result["status"] == "BLOCKED"
    assert "AUTHORITY_ROLE_UNSAFE:qa-report" in result["errors"]


@pytest.mark.parametrize("scope", ["top-level", "nested-role"])
def test_duplicate_json_key_is_rejected_even_if_own_digest_matches(built, scope):
    doc = sidecar(built)
    raw = json.dumps(doc, ensure_ascii=False, sort_keys=True)
    if scope == "top-level":
        raw = raw.replace('"lock_state": "EDITABLE_CURRENT"',
                          '"lock_state": "LOCKED", "lock_state": "EDITABLE_CURRENT"', 1)
    else:
        name = doc["roles"]["qa-report"]["filename"]
        fragment = '"filename": ' + json.dumps(name, ensure_ascii=False)
        raw = raw.replace(fragment, '"filename": "forged.tsv", ' + fragment, 1)
    assert raw.count('"filename"') >= 4
    data = raw.encode("utf-8")
    result = verify(
        data, digest(data), WORKSTREAM, ARTIFACT, SOURCE_SHA, PARENT_SHA,
        scan_input(built["input_dir"]), built["zip"], digest(built["zip"])
    )
    assert result["status"] == "BLOCKED"
    assert "AUTHORITY_SIDECAR_INVALID_JSON" in result["errors"]

@pytest.mark.parametrize("mutation", ["wrong-digest", "removed-entry", "invalid-sums"])
def test_rehashed_whole_zip_with_damaged_internal_sums_blocks(built, mutation):
    """An otherwise valid ZIP role byte projection must not mask a bad SHA256SUMS."""
    doc = sidecar(built)
    parts = package_members(built["zip"])
    p = ZROOT + SUMS
    original = parts[p].decode("utf-8")
    if mutation == "wrong-digest":
        lines = original.splitlines()
        lines[0] = ("0" * 64) + lines[0][64:]
        parts[p] = ("\n".join(lines) + "\n").encode("utf-8")
    elif mutation == "removed-entry":
        parts[p] = ("\n".join(original.splitlines()[1:]) + "\n").encode("utf-8")
    else:
        parts[p] = b"NOT-A-HASH-SUMS-LINE\n"
    altered = repack(parts)
    snap = scan_input(built["input_dir"])
    # Prior role-byte binding alone may pass despite corrupt internal sums.
    assert verify_postbuild(snap, altered, digest(altered))["status"].startswith("PASS_SCOPED")
    revised = dict(built, zip=altered)
    result = assess(revised, doc)
    assert result["status"] == "BLOCKED"
    assert any(x.startswith("STAGE5_INTERNAL_SHA256SUMS_") for x in result["errors"])


def test_deeply_nested_json_returns_blocked_not_exception(built):
    deeply_nested = ("[" * 10000 + "0" + "]" * 10000).encode("utf-8")
    result = verify(
        deeply_nested, digest(deeply_nested),
        WORKSTREAM, ARTIFACT, SOURCE_SHA, PARENT_SHA,
        scan_input(built["input_dir"]), built["zip"], digest(built["zip"])
    )
    assert result["status"] == "BLOCKED"
    assert "AUTHORITY_SIDECAR_INVALID_JSON" in result["errors"]
