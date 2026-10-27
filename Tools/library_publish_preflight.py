#!/usr/bin/env python3
"""Read-only Library publish preflight. It never uploads, deletes or renames files.

Library listing metadata does not contain verified SHA256 hashes. A positive
duplicate decision therefore requires a hash-bound receipt, never filename/size
equality. This gate cannot intercept unrelated ChatGPT upload calls.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

SCHEMA = "gcpk-library-publish-preflight@1"
PUBLISHABLE = {"final_delivery", "validated_major_checkpoint",
               "required_recovery", "explicit_user_checkpoint"}
HEX64 = re.compile(r"^[a-f0-9]{64}$")
WIP = re.compile(r"(?:^|[-_.])(?:WIP\d+|BATCH\d+|MICRO[-_]?EDIT)(?:[-_.]|$)", re.I)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def report(decision, code, **fields):
    return {"schema": SCHEMA, "decision": decision, "reason": code, **fields}


def read_json(path):
    with Path(path).open("r", encoding="utf-8-sig") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise ValueError("JSON root must be an object")
    return obj


def audit(archive, *, purpose, destination, workstream, catalog, evidence=None,
          user_request=None):
    archive = Path(archive)
    if not archive.is_file() or archive.suffix.lower() != ".zip":
        return report("BLOCK", "ARCHIVE_MISSING_OR_NOT_ZIP")
    if purpose not in PUBLISHABLE:
        return report("BLOCK", "ROUTINE_WIP_NOT_LIBRARY_PUBLISHABLE")
    if not workstream or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", workstream):
        return report("BLOCK", "WORKSTREAM_ID_REQUIRED")
    if not destination.startswith("/") or ".." in PurePosixPath(destination).parts:
        return report("BLOCK", "INVALID_LIBRARY_DESTINATION")
    if PurePosixPath(destination).name != archive.name:
        return report("BLOCK", "DESTINATION_FILENAME_MISMATCH")
    if WIP.search(archive.stem) and purpose not in {"required_recovery", "explicit_user_checkpoint"}:
        return report("BLOCK", "ROUTINE_WIP_ZIP")
    if purpose == "explicit_user_checkpoint" and not (user_request or "").strip():
        return report("BLOCK", "USER_CHECKPOINT_REQUEST_MISSING")

    size = archive.stat().st_size
    sha = digest(archive)
    try:
        with zipfile.ZipFile(archive) as z:
            infos = z.infolist()
            names = [i.filename for i in infos]
            if not infos or len(names) != len(set(names)) or z.testzip() is not None:
                return report("BLOCK", "ZIP_INTEGRITY_FAILED")
            if any(n.startswith(("/", "\\")) or "\\" in n or ".." in PurePosixPath(n).parts
                   or ":" in PurePosixPath(n).parts[0] for n in names):
                return report("BLOCK", "UNSAFE_ZIP_MEMBER")
    except (OSError, zipfile.BadZipFile, RuntimeError, ValueError):
        return report("BLOCK", "ZIP_INTEGRITY_FAILED")

    if purpose in {"final_delivery", "validated_major_checkpoint", "required_recovery"}:
        if not evidence:
            return report("HOLD", "QUALITY_OR_RECOVERY_EVIDENCE_MISSING", archive_sha256=sha)
        try:
            ev = read_json(evidence)
        except (OSError, ValueError):
            return report("HOLD", "INVALID_EVIDENCE", archive_sha256=sha)
        recorded = ev.get("archive_sha256") or ev.get("zip_sha256") or ev.get("artifact_sha256")
        if recorded != sha:
            return report("HOLD", "EVIDENCE_HASH_NOT_CURRENT", archive_sha256=sha)
        if purpose == "required_recovery":
            if not ev.get("recovery_gap"):
                return report("HOLD", "RECOVERY_GAP_NOT_EVIDENCED", archive_sha256=sha)
        elif ev.get("status") not in {"PASS", "CLOSED", "VERIFIED",
                                      "USER_ACCEPTED_FINAL_WITH_EXCEPTIONS"}:
            return report("HOLD", "REQUIRED_MILESTONE_NOT_ACCEPTED", archive_sha256=sha)
        elif purpose == "final_delivery" and not (ev.get("stage7") == "PASS" or
                        ev.get("status") == "USER_ACCEPTED_FINAL_WITH_EXCEPTIONS"):
            return report("HOLD", "FINAL_STAGE7_OR_USER_EXCEPTION_MISSING", archive_sha256=sha)

    if not isinstance(catalog, dict) or not isinstance(catalog.get("entries"), list):
        return report("HOLD", "LIBRARY_CATALOG_MISSING", archive_sha256=sha)
    for entry in catalog["entries"]:
        if not isinstance(entry, dict):
            return report("HOLD", "INVALID_CATALOG_RECORD", archive_sha256=sha)
        path = entry.get("path") or ""
        signed = entry.get("sha256") if entry.get("hash_verified") is True else None
        if signed and not HEX64.fullmatch(str(signed)):
            return report("HOLD", "INVALID_VERIFIED_HASH", archive_sha256=sha)
        if signed == sha and entry.get("library_file_id") and path:
            return report("SKIP_IDENTICAL", "EXACT_VERIFIED_LIBRARY_COPY_EXISTS",
                          archive_sha256=sha, existing_path=path,
                          library_file_id=entry["library_file_id"])
        if path == destination:
            if signed:
                return report("BLOCK", "DESTINATION_OCCUPIED_BY_DIFFERENT_BYTES",
                              archive_sha256=sha, existing_path=path)
            return report("HOLD", "DESTINATION_OCCUPIED_UNVERIFIED",
                          archive_sha256=sha, existing_path=path)
        if (entry.get("size_bytes") == size and
                PurePosixPath(path).name == archive.name and not signed):
            return report("HOLD", "POSSIBLE_DUPLICATE_NEEDS_HASH_READBACK",
                          archive_sha256=sha, existing_path=path)
    if catalog.get("complete") is not True:
        return report("HOLD", "INCOMPLETE_LIBRARY_CATALOG", archive_sha256=sha)
    if catalog.get("scope") == "workstream" and catalog.get("workstream") != workstream:
        return report("HOLD", "WRONG_WORKSTREAM_CATALOG", archive_sha256=sha)
    if catalog.get("scope") not in {"workstream", "library"}:
        return report("HOLD", "UNDECLARED_CATALOG_SCOPE", archive_sha256=sha)
    return report("ALLOW", "PURPOSE_HASH_AND_CATALOG_VERIFIED",
                  archive_sha256=sha, archive_bytes=size, library_destination=destination,
                  catalog_scope=catalog["scope"], workstream=workstream)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--destination", required=True)
    ap.add_argument("--workstream", required=True)
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--evidence", type=Path)
    ap.add_argument("--user-request")
    a = ap.parse_args()
    try:
        cat = read_json(a.catalog)
    except (OSError, ValueError):
        cat = None
    result = audit(a.archive, purpose=a.purpose, destination=a.destination,
                   workstream=a.workstream, catalog=cat,
                   evidence=a.evidence, user_request=a.user_request)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["decision"] in {"ALLOW", "SKIP_IDENTICAL"} else 2


if __name__ == "__main__":
    sys.exit(main())
