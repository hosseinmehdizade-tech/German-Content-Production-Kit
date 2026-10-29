#!/usr/bin/env python3
"""OP-02 NONACTIVE Stage5 role-selector ambiguity + exact postbuild byte binding.

This validates the unchanged Tools/build_clean_delivery.py contract WITHOUT
modifying it. No production writer grant, content edit or release approval.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
from pathlib import Path
import re
import stat
import sys

from audit_stage5_clean_zip_v486 import _read_safe_zip
from validate_stage45_teaching_delta_parity import hexsha, read_json, sha

SCHEMA = "gcpk-op02-stage5-input-role-binding@1"
STATUS = "NONACTIVE_VERSIONED_DRY_RUN"
ROLES = {
    "direct-import-tsv": ("*universal*.tsv", "*import*.tsv", "*cards*.tsv"),
    "canonical-json": ("*canonical*.json",),
    "source-output-map-tsv": ("*source-output-map*.tsv",),
    "qa-report": ("*verification*.json", "*qa*.json"),
}
CONTROL = frozenset({"DELIVERY-MANIFEST.json", "SHA256SUMS.txt"})
ROOT = "CONTENT-DELIVERY/"
MAX_SINGLE = 80_000_000

def _match(name: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(name.lower(), pat) for pat in patterns)

def scan_input(folder: Path) -> dict:
    """Only returns PASS when every original builder role has one safe candidate."""
    problems = []
    roles = {}
    try:
        if not folder.is_dir() or folder.is_symlink():
            return {"status": "BLOCKED", "errors": ["INPUT_DIR_NOT_ORDINARY_DIRECTORY"], "roles": {}}
        entries = list(folder.iterdir())
    except OSError as exc:
        return {"status": "BLOCKED", "errors": ["INPUT_DIR_UNREADABLE:" + type(exc).__name__], "roles": {}}
    hits = {role: [] for role in ROLES}
    for entry in entries:
        matching = [role for role, patterns in ROLES.items()
                    if _match(entry.name, patterns)]
        if not matching:
            continue
        for role in matching:
            hits[role].append(entry)
        if entry.is_symlink() or not entry.is_file():
            problems.append("UNSAFE_ROLE_CANDIDATE:" + entry.name)
        if entry.name in CONTROL or "/" in entry.name or "\\" in entry.name:
            problems.append("INVALID_ROLE_FILENAME:" + entry.name)
    for role, files in hits.items():
        if not files:
            problems.append("MISSING_ROLE:" + role)
        elif len(files) != 1:
            # Duplicate candidates are unsafe even if their bytes coincide:
            # a future update or filesystem-dependent order may change which
            # candidate the old unchanged builder picks.
            problems.append("AMBIGUOUS_ROLE:" + role)
        elif not files[0].is_symlink() and files[0].is_file():
            try:
                raw = files[0].read_bytes()
                if len(raw) > MAX_SINGLE:
                    problems.append("ROLE_BYTES_OVERSIZED:" + role)
                else:
                    roles[role] = {
                        "filename": files[0].name,
                        "size": len(raw),
                        "sha256": sha(raw)
                    }
            except OSError:
                problems.append("ROLE_BYTES_UNREADABLE:" + role)
    names = [v["filename"] for v in roles.values()]
    if len(names) != len(set(names)):
        problems.append("ROLE_COLLISION_ACROSS_TYPES")
    if any("source-inventory" in x.lower() or "source_inventory" in x.lower()
           for x in [v["filename"] for k,v in roles.items()
                     if k == "direct-import-tsv"]):
        problems.append("SOURCE_INVENTORY_IS_NOT_DIRECT_IMPORT")
    return {
        "schema": SCHEMA,
        "status": "PASS_SCOPED_SINGLE_CANDIDATE_INPUT_ONLY" if not problems else "BLOCKED",
        "errors": sorted(set(problems)),
        "roles": roles,
        "candidate_counts": {k:len(v) for k,v in hits.items()},
        "notes": "This is a read-time local snapshot; it is not a writer lock or persistent production CURRENT authority."
    }

def verify_postbuild(proof: dict, zip_bytes: bytes, expected_zip_sha: str) -> dict:
    errors = []
    if not isinstance(proof, dict) or proof.get("schema") != SCHEMA or proof.get("status") != "PASS_SCOPED_SINGLE_CANDIDATE_INPUT_ONLY":
        return {"status": "BLOCKED", "errors": ["INPUT_SELECTION_PROOF_NOT_PASS"]}
    role_data = proof.get("roles")
    if not isinstance(role_data, dict) or set(role_data) != set(ROLES):
        return {"status": "BLOCKED", "errors": ["INPUT_SELECTION_PROOF_NOT_COMPLETE"]}
    if not hexsha(expected_zip_sha) or sha(zip_bytes) != expected_zip_sha:
        return {"status": "BLOCKED", "errors": ["POSTBUILD_ZIP_EXACT_SHA_MISMATCH"]}
    try:
        members = _read_safe_zip(zip_bytes)
        manifest = read_json(members["DELIVERY-MANIFEST.json"])
        if not isinstance(manifest, dict) or not isinstance(manifest.get("roles"), dict):
            raise ValueError("INVALID_DELIVERY_MANIFEST")
        if set(manifest["roles"]) != set(ROLES):
            raise ValueError("POSTBUILD_ROLES_NOT_EXACT")
        for role, selection in role_data.items():
            name = selection.get("filename") if isinstance(selection, dict) else None
            digest = selection.get("sha256") if isinstance(selection, dict) else None
            size = selection.get("size") if isinstance(selection, dict) else None
            if (not isinstance(name,str) or not name or "/" in name or "\\" in name
                    or not hexsha(digest) or type(size) is not int or size < 0
                    or manifest["roles"].get(role) != name):
                errors.append("POSTBUILD_ROLE_NAME_OR_SELECTION_DRIFT:" + role)
                continue
            body = members.get(name)
            if body is None:
                errors.append("POSTBUILD_ROLE_MEMBER_MISSING:" + role)
            elif sha(body) != digest or len(body) != size:
                errors.append("POSTBUILD_ROLE_BYTES_CHANGED:" + role)
        required = {record["filename"] for record in role_data.values()} | CONTROL
        if set(members) != required:
            errors.append("POSTBUILD_EXTRA_OR_MISSING_MEMBERS")
    except (KeyError, ValueError, TypeError, UnicodeError) as exc:
        errors.append("POSTBUILD_INVALID_ZIP_OR_MANIFEST:" + str(exc))
    return {
        "schema": "gcpk-op02-stage5-input-role-binding-result@1",
        "status": "PASS_SCOPED_LOCAL_ROLE_BYTES_RETAINED_IN_ZIP_ONLY" if not errors else "BLOCKED",
        "errors": sorted(set(errors)),
        "zip_sha256": expected_zip_sha,
        "not_proven": [
            "Independent Stage4 linguistic QA, source authority or editorial fidelity",
            "Stage5 full final organized content ZIP or user workstream CURRENT",
            "Real app importer/browser Stage6/Stage7 acceptance",
            "Remote Git/Library CAS, writer authorization or time-of-check locking",
            "Whether a concurrent temporary edit occurred and was restored before the snapshot",
        ]
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--finished-zip", type=Path)
    parser.add_argument("--finished-zip-sha256")
    args = parser.parse_args()
    before = scan_input(args.input_dir)
    if args.finished_zip is None:
        result = before
    else:
        if not args.finished_zip_sha256 or before["status"] == "BLOCKED":
            result = {"status": "BLOCKED", "errors": ["INPUT_PRECHECK_OR_EXACT_ZIP_HASH_MISSING"] + before["errors"]}
        else:
            try:
                result = verify_postbuild(before, args.finished_zip.read_bytes(),
                                          args.finished_zip_sha256)
                after = scan_input(args.input_dir)
                if after["status"] != "PASS_SCOPED_SINGLE_CANDIDATE_INPUT_ONLY" or after["roles"] != before["roles"]:
                    result["status"] = "BLOCKED"
                    result["errors"].append("INPUT_SELECTION_CHANGED_DURING_PREFLIGHT_POSTBUILD")
            except (OSError, ValueError) as exc:
                result = {"status": "BLOCKED", "errors": ["FINISHED_ZIP_UNREADABLE:" + str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status", "").startswith("PASS_SCOPED") else 2

if __name__ == "__main__":
    sys.exit(main())
