#!/usr/bin/env python3
"""OP-02 NONACTIVE exact CURRENT authority pin for Stage5 selected roles.

An externally recorded sidecar SHA256 + independent workstream/artifact/source/
parent identity are REQUIRED; this code cannot attest who issued those pins.
Does not alter any production builder, source or user data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from audit_stage5_input_role_binding import ROLES, scan_input, verify_postbuild

SCHEMA = "gcpk-op02-stage5-current-role-authority@1"
RESULT_SCHEMA = "gcpk-op02-stage5-current-role-authority-result@1"
ROLE_KEYS = {"filename", "sha256", "size"}
PIN_KEYS = {
    "schema", "status", "workstream_id", "artifact_id",
    "registered_source_sha256", "parent_artifact_sha256",
    "lock_state", "roles"
}
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _valid_sha(value: object) -> bool:
    return isinstance(value, str) and SHA.fullmatch(value) is not None and value != "0" * 64


def _valid_id(value: object) -> bool:
    return isinstance(value, str) and SAFE_ID.fullmatch(value) is not None


def verify(
    authority_bytes: bytes, externally_pinned_authority_sha256: str,
    expected_workstream_id: str, expected_artifact_id: str,
    expected_source_sha256: str, expected_parent_sha256: str,
    selected_inputs: dict, finished_zip_bytes: bytes, expected_zip_sha256: str,
) -> dict:
    """Fail closed unless exact external identity, input bytes AND ZIP bytes agree.

    Expected values MUST be read from a separately trusted current checkpoint,
    never derived from the candidate sidecar or its own ZIP.
    """
    errors: list[str] = []
    if not _valid_sha(externally_pinned_authority_sha256):
        errors.append("MISSING_INDEPENDENT_AUTHORITY_SHA256")
    elif digest(authority_bytes) != externally_pinned_authority_sha256:
        errors.append("AUTHORITY_SIDECAR_SHA256_MISMATCH")
    for value, name in (
        (expected_workstream_id, "WORKSTREAM"),
        (expected_artifact_id, "ARTIFACT"),
    ):
        if not _valid_id(value):
            errors.append("MISSING_OR_INVALID_EXTERNAL_" + name + "_IDENTITY")
    for value, name in (
        (expected_source_sha256, "SOURCE"),
        (expected_parent_sha256, "PARENT"),
    ):
        if not _valid_sha(value):
            errors.append("MISSING_OR_INVALID_EXTERNAL_" + name + "_SHA256")
    if errors:
        return _result(errors)

    try:
        authority = json.loads(authority_bytes.decode("utf-8"))
    except (UnicodeError, ValueError):
        return _result(["AUTHORITY_SIDECAR_INVALID_JSON"])
    if not isinstance(authority, dict) or set(authority) != PIN_KEYS:
        return _result(["AUTHORITY_SIDECAR_UNEXPECTED_SCHEMA_KEYS"])
    if authority["schema"] != SCHEMA or authority["status"] != "NONACTIVE_EXTERNAL_PIN":
        errors.append("AUTHORITY_SIDECAR_SCHEMA_OR_STATUS_INVALID")
    if authority["lock_state"] != "EDITABLE_CURRENT":
        errors.append("LOCKED_OR_UNPROVEN_EDITABILITY")
    for key, expected in (
        ("workstream_id", expected_workstream_id),
        ("artifact_id", expected_artifact_id),
        ("registered_source_sha256", expected_source_sha256),
        ("parent_artifact_sha256", expected_parent_sha256),
    ):
        if authority[key] != expected:
            errors.append("EXTERNAL_IDENTITY_MISMATCH:" + key)

    role_data = authority["roles"]
    if not isinstance(role_data, dict) or set(role_data) != set(ROLES):
        errors.append("AUTHORITY_ROLES_NOT_COMPLETE")
    else:
        selected = selected_inputs.get("roles") if isinstance(selected_inputs, dict) else None
        if (not isinstance(selected_inputs, dict) or
                selected_inputs.get("status") != "PASS_SCOPED_SINGLE_CANDIDATE_INPUT_ONLY"):
            errors.append("INPUT_ROLE_PREFLIGHT_NOT_PASS")
        if not isinstance(selected, dict) or set(selected) != set(ROLES):
            errors.append("INPUT_ROLE_DATA_NOT_COMPLETE")
        for role, entry in role_data.items():
            if not isinstance(entry, dict) or set(entry) != ROLE_KEYS:
                errors.append("AUTHORITY_ROLE_INVALID:" + role)
                continue
            name, size, hex_digest = entry["filename"], entry["size"], entry["sha256"]
            if (not isinstance(name, str) or not name or len(name) > 180
                    or "/" in name or "\\" in name
                    or any(ord(c) < 32 for c in name)
                    or name in {".", ".."} or not _valid_sha(hex_digest)
                    or type(size) is not int or not (0 <= size <= 80_000_000)):
                errors.append("AUTHORITY_ROLE_UNSAFE:" + role)
            if not isinstance(selected, dict) or selected.get(role) != entry:
                errors.append("SELECTED_INPUT_NOT_PINNED_CURRENT:" + role)
        if len({entry.get("filename") for entry in role_data.values()
                if isinstance(entry, dict)}) != len(ROLES):
            errors.append("AUTHORITY_ROLE_FILENAME_COLLISION")

    if not errors:
        post = verify_postbuild(selected_inputs, finished_zip_bytes, expected_zip_sha256)
        if post.get("status") != "PASS_SCOPED_LOCAL_ROLE_BYTES_RETAINED_IN_ZIP_ONLY":
            errors.extend("POSTBUILD:" + x for x in post.get("errors", ["UNKNOWN"]))
    return _result(errors)


def _result(errors: list[str]) -> dict:
    return {
        "schema": RESULT_SCHEMA,
        "status": "PASS_SCOPED_EXTERNALLY_PINNED_CURRENT_ROLE_BYTES_ONLY"
                  if not errors else "BLOCKED",
        "errors": sorted(set(errors)),
        "production_active": False,
        "not_proven": [
            "The independent pin issuer's legitimacy or CURRENT/LOCKED provenance",
            "Cryptographic authenticity when the caller supplies a forged matching external pin",
            "The registered source file's actual bytes or Stage4 linguistic QA",
            "Final organized eight-directory content production ZIP",
            "Real learner Stage6/Stage7/runtime acceptance, transaction lock or remote persistence",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authority-sidecar", type=Path, required=True)
    parser.add_argument("--expected-authority-sha256", required=True)
    parser.add_argument("--expected-workstream-id", required=True)
    parser.add_argument("--expected-artifact-id", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--expected-parent-sha256", required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--finished-zip", type=Path, required=True)
    parser.add_argument("--finished-zip-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.authority_sidecar.is_symlink() or not args.authority_sidecar.is_file():
            raise OSError("sidecar must be an ordinary file, not a symlink")
        raw_sidecar = args.authority_sidecar.read_bytes()
        if len(raw_sidecar) > 1_000_000:
            raise OSError("oversized authority sidecar")
        before = scan_input(args.input_dir)
        result = verify(raw_sidecar, args.expected_authority_sha256,
                        args.expected_workstream_id, args.expected_artifact_id,
                        args.expected_source_sha256, args.expected_parent_sha256,
                        before, args.finished_zip.read_bytes(), args.finished_zip_sha256)
        after = scan_input(args.input_dir)
        if after != before:
            result["status"] = "BLOCKED"
            result["errors"].append("INPUT_CHANGED_BETWEEN_PRE_AND_POST_CHECK")
    except OSError as exc:
        result = _result(["UNREADABLE_OR_UNSAFE_INPUT:" + type(exc).__name__])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"].startswith("PASS_SCOPED") else 2


if __name__ == "__main__":
    sys.exit(main())
