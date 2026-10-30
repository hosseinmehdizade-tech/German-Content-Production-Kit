#!/usr/bin/env python3
"""Read-only OP02 parent/current pointer lineage check; no release authority.

Tests original parent and candidate ZIP bytes. Never repairs an immutable
ZIP, updates LATEST, authenticates a producer or authorizes Stage4–7.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import zipfile

MAX_ZIP = 256_000_000
POINTER = "07-Checkpoint-State/CURRENT-WORKSTREAM-POINTER.json"
CANON = "02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json"
IMPORT = "01-Final-Import/IMPORT.WORKING.tsv"
SHA = re.compile(r"[0-9a-f]{64}\Z")
WIP = re.compile(r"^WIP([1-9][0-9]*)_")
SNAPSHOT_FIELDS = {
    "workstream", "current_sha256", "parent_sha256",
    "current_milestone", "parent_version"
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def valid_sha(value):
    return type(value) is str and bool(SHA.fullmatch(value)) and value != "0" * 64


def no_duplicate_json(raw):
    def pairs(entries):
        obj = {}
        for k, v in entries:
            if k in obj:
                raise ValueError("DUPLICATE_JSON_FIELD")
            obj[k] = v
        return obj
    def constant(value):
        raise ValueError("NONFINITE_JSON")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=constant)


def _read_zip(path, sha, kind, errors):
    if not valid_sha(sha):
        errors.append(kind + "_SHA_PIN_INVALID")
        return None
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        errors.append(kind + "_RAW_FILE_MISSING_OR_SYMLINK")
        return None
    size = p.stat().st_size
    if not 0 < size <= MAX_ZIP:
        errors.append(kind + "_ZIP_SIZE_INVALID")
        return None
    raw = p.read_bytes()
    if digest(raw) != sha:
        errors.append(kind + "_ZIP_SHA256_DRIFT")
        return None
    try:
        with zipfile.ZipFile(p) as z:
            files = z.infolist()
            names = [x.filename for x in files]
            if len(names) != len(set(names)):
                errors.append(kind + "_DUPLICATE_MEMBERS")
                return None
            if len(names) > 2000 or sum(x.file_size for x in files) > 512_000_000:
                errors.append(kind + "_ZIP_LIMIT_EXCEEDED")
                return None
            for entry in files:
                name = entry.filename
                if (name.startswith("/") or "\\" in name or
                        any(x in ("", ".", "..") for x in name.split("/")) or
                        stat.S_ISLNK((entry.external_attr >> 16) & 0xffff) or
                        entry.flag_bits & 1):
                    errors.append(kind + "_UNSAFE_MEMBER")
                    return None
            if not {POINTER, CANON, IMPORT, "MANIFEST.json"}.issubset(names):
                errors.append(kind + "_REQUIRED_MEMBER_MISSING")
                return None
            bad = z.testzip()
            if bad is not None:
                errors.append(kind + "_CRC_FAILURE")
                return None
            pointer_bytes = z.read(POINTER)
            pointer = no_duplicate_json(pointer_bytes)
            manifest = no_duplicate_json(z.read("MANIFEST.json"))
            canonical_sha = digest(z.read(CANON))
            import_sha = digest(z.read(IMPORT))
            return {
                "pointer_bytes": pointer_bytes,
                "pointer": pointer,
                "manifest": manifest,
                "canonical_sha": canonical_sha,
                "import_sha": import_sha,
                "members": len(files),
                "pointer_sha256": digest(pointer_bytes),
            }
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError,
            zipfile.BadZipFile, UnicodeError) as exc:
        errors.append(kind + "_ZIP_PARSE_FAILURE_" + type(exc).__name__)
        return None


def audit(current_zip, parent_zip, snapshot):
    errors = []
    result = {
        "schema": "gcpk-op02-parent-pointer-lineage-diagnostic@1",
        "status": "BLOCKED",
        "errors": errors,
        "same_pointer_bytes": None,
        "current_pointer_sha256": None,
        "parent_pointer_sha256": None,
        "required_producer_repairs": [],
        "issuer_authenticated": False,
        "stage4_semantic_pass": False,
        "stage5_7_authorized": False,
        "release_authorized": False,
        "writer_granted": False,
        "performed_writes": False,
    }
    if (type(snapshot) is not dict or set(snapshot) != SNAPSHOT_FIELDS or
            snapshot.get("workstream") != "aber-hallo-listen-tabellen" or
            not valid_sha(snapshot.get("current_sha256")) or
            not valid_sha(snapshot.get("parent_sha256")) or
            snapshot["current_sha256"] == snapshot["parent_sha256"] or
            type(snapshot.get("current_milestone")) is not str or
            not WIP.match(snapshot["current_milestone"]) or
            type(snapshot.get("parent_version")) is not int or
            snapshot["parent_version"] < 1):
        errors.append("INDEPENDENT_SNAPSHOT_SHAPE_INVALID")
        return result
    version = int(WIP.match(snapshot["current_milestone"]).group(1))
    if version != snapshot["parent_version"] + 1:
        errors.append("PARENT_CURRENT_VERSION_GAP")
    current = _read_zip(current_zip, snapshot["current_sha256"], "CURRENT", errors)
    parent = _read_zip(parent_zip, snapshot["parent_sha256"], "PARENT", errors)
    if current is None or parent is None:
        return result
    result["current_pointer_sha256"] = current["pointer_sha256"]
    result["parent_pointer_sha256"] = parent["pointer_sha256"]
    result["same_pointer_bytes"] = current["pointer_bytes"] == parent["pointer_bytes"]

    def check(role, bundle, expected_version):
        ptr = bundle["pointer"]
        if type(ptr) is not dict or ptr.get("workstream") != snapshot["workstream"]:
            errors.append(role + "_POINTER_WORKSTREAM_INVALID")
            return
        claim = ptr.get("current")
        match = WIP.match(claim) if type(claim) is str else None
        if not match or int(match.group(1)) != expected_version:
            errors.append(role + "_POINTER_VERSION_STALE")
        for key, current_hash in (
            ("canonical_sha256", bundle["canonical_sha"]),
            ("import_sha256", bundle["import_sha"]),
            ("working_canonical_sha256", bundle["canonical_sha"]),
            ("working_import_sha256", bundle["import_sha"]),
        ):
            if ptr.get(key) != current_hash:
                errors.append(role + "_POINTER_DIGEST_STALE:" + key)
                if role == "CURRENT":
                    result["required_producer_repairs"].append(key)
        manifest_summary = bundle["manifest"].get("summary") if type(bundle["manifest"]) is dict else None
        status = manifest_summary.get("status") if type(manifest_summary) is dict else None
        if (type(status) is not str or not status.startswith(f"CURRENT_WIP{expected_version}_") or
                manifest_summary.get("canonical_sha256") != bundle["canonical_sha"] or
                manifest_summary.get("import_sha256") != bundle["import_sha"]):
            errors.append(role + "_MANIFEST_VERSION_OR_DIGEST_DRIFT")
    check("PARENT", parent, snapshot["parent_version"])
    check("CURRENT", current, version)
    if result["same_pointer_bytes"]:
        errors.append("EXACT_PARENT_POINTER_REUSED")
        result["required_producer_repairs"].append("current")
    if "CURRENT_POINTER_VERSION_STALE" in errors:
        result["required_producer_repairs"].append("current")
    result["required_producer_repairs"] = sorted(set(result["required_producer_repairs"]))
    result["observed"] = {
        "expected_version": version,
        "parent_version": snapshot["parent_version"],
        "current_pointer_current": current["pointer"].get("current") if type(current["pointer"]) is dict else None,
        "parent_pointer_current": parent["pointer"].get("current") if type(parent["pointer"]) is dict else None,
        "current_canonical_sha256": current["canonical_sha"],
        "current_import_sha256": current["import_sha"],
    }
    result["errors"] = sorted(set(errors))
    result["status"] = ("PASS_SCOPED_ORIGINAL_POINTER_LINEAGE_ONLY_NOT_RELEASE"
                        if not errors else "BLOCKED")
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--current-zip", type=Path, required=True)
    ap.add_argument("--parent-zip", type=Path, required=True)
    ap.add_argument("--snapshot", type=Path, required=True,
                    help="Independently pinned workstream metadata JSON (not self-authentication)")
    args = ap.parse_args()
    result = audit(args.current_zip, args.parent_zip,
                   no_duplicate_json(args.snapshot.read_bytes()))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"].startswith("PASS_SCOPED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
