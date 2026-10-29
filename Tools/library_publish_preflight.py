#!/usr/bin/env python3
"""Read-only Library publish preflight. It never uploads, deletes or renames files.

Catalog JSON: {"scope":"workstream"|"library","workstream":"source-slug",
"complete":true,"entries":[{"path":"/Library/file.zip","size_bytes":123,
"library_file_id":"libfile_...","sha256":"64-hex-digest",
"readback_sha256":"the-same-digest","hash_verified":true,
"verification_receipt":"a verifiable prior readback receipt path"}]}.
Mark complete only after exhausting pagination for the declared scope. Entries
from files.list with name+size but no readback MUST remain unverified.

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
        # A caller-supplied boolean alone is not readback evidence. Reuse needs
        # an independently documented hash-bound Library readback receipt.
        has_proof = (entry.get("hash_verified") is True and
                     entry.get("readback_sha256") == entry.get("sha256") and
                     bool(entry.get("verification_receipt")) and
                     bool(entry.get("library_file_id")))
        signed = entry.get("sha256") if has_proof else None
        if entry.get("sha256") == sha and not has_proof:
            return report("HOLD", "UNVERIFIED_MATCHING_HASH_CLAIM",
                          archive_sha256=sha, existing_path=path)
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



def catalog_from_list_pages(pages, *, library_path, scope, workstream):
    """Normalize *actual files.list pages*; never infer SHA256 from metadata.

    Each page envelope must preserve the requested path and cursor as well as
    the result's items and next_cursor. Complete means that the cursor chain
    exhausted the explicitly requested folder. A partial search is not enough.
    """
    if not library_path.startswith("/") or ".." in PurePosixPath(library_path).parts:
        raise ValueError("invalid library_path")
    if scope != "workstream" or not workstream or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", workstream):
        raise ValueError("a scoped workstream listing is required")
    # A workstream folder must actually be isolated; a flat shared Checkpoints
    # listing cannot be misrepresented as a complete one-workstream inventory.
    if PurePosixPath(library_path.rstrip("/")).name != workstream:
        raise ValueError("library_path must end with the exact workstream slug")
    if not isinstance(pages, list) or not pages:
        raise ValueError("listing must contain at least one page")
    expected_cursor = None
    entries = []
    seen = set()
    complete = False
    for number, page in enumerate(pages):
        if not isinstance(page, dict):
            raise ValueError("invalid page")
        if (page.get("surface") != "library" or
                page.get("requested_library_path") != library_path or
                page.get("requested_cursor") != expected_cursor):
            raise ValueError("mismatched library path or pagination cursor")
        for item in page.get("items", []):
            if item.get("kind") != "file":
                continue
            path = item.get("path")
            if not isinstance(path, str) or not path.startswith(library_path.rstrip("/") + "/"):
                raise ValueError("item outside requested directory")
            if path in seen:
                raise ValueError("duplicate catalog path")
            seen.add(path)
            entries.append({
                "path": path,
                "size_bytes": item.get("size_bytes"),
                "library_file_id": item.get("library_file_id"),
                # Crucially, NO SHA or hash_verified field: files.list has no
                # byte-level readback proof, even if similarly named metadata
                # happens to be present on an item.
            })
        expected_cursor = page.get("next_cursor")
        if expected_cursor is None:
            if number != len(pages) - 1:
                raise ValueError("additional pages after end-of-list")
            complete = True
        elif not isinstance(expected_cursor, str) or not expected_cursor:
            raise ValueError("invalid continuation cursor")
    return {
        "scope": scope,
        "workstream": workstream,
        "source": "files.list:metadata-only",
        "library_path": library_path,
        "pages": len(pages),
        "complete": complete,
        "entries": entries,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", type=Path)
    ap.add_argument("--purpose")
    ap.add_argument("--destination")
    ap.add_argument("--workstream", required=True)
    ap.add_argument("--catalog", type=Path)
    ap.add_argument("--list-pages-json", type=Path,
                    help="JSON with ordered files.list page envelopes and requested cursors")
    ap.add_argument("--library-path", help="New scoped folder ending with --workstream")
    ap.add_argument("--catalog-output", type=Path,
                    help="Optional new JSON catalog file (never overwrites)")
    ap.add_argument("--evidence", type=Path)
    ap.add_argument("--user-request")
    a = ap.parse_args()
    if a.list_pages_json:
        if not a.library_path:
            ap.error("--library-path is required for --list-pages-json")
        try:
            source = read_json(a.list_pages_json)
            cat = catalog_from_list_pages(source.get("pages"), library_path=a.library_path,
                                          scope="workstream", workstream=a.workstream)
        except (OSError, ValueError) as exc:
            print(json.dumps(report("HOLD", "INCOMPLETE_OR_INVALID_PAGE_EXPORT",
                                    message=str(exc)), ensure_ascii=False))
            return 2
        encoded = json.dumps(cat, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if a.catalog_output:
            try:
                with a.catalog_output.open("x", encoding="utf-8") as stream:
                    stream.write(encoded)
            except FileExistsError:
                print(json.dumps(report("BLOCK", "CATALOG_OUTPUT_ALREADY_EXISTS")))
                return 2
        print(encoded.rstrip())
        return 0 if cat["complete"] else 2
    if not all((a.archive, a.purpose, a.destination, a.catalog)):
        ap.error("--archive, --purpose, --destination and --catalog are required for audit")
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


def screen_library_name_size_candidates(entries, *, complete=False):
    """Read-only Library metadata screen. Name/size is NEVER byte equality.

    Uses folder-local groups, keeping differently sized or differently scoped
    files out of the equal-size candidate set. This is not an erase decision.
    The result is provisional even when all supplied pages were enumerated.
    """
    groups = {}
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("invalid Library metadata item")
        path = item.get("path")
        size = item.get("size_bytes")
        identity = item.get("library_file_id")
        if not isinstance(path, str) or not path.startswith("/") or not identity:
            continue
        if not isinstance(size, int) or size < 0:
            continue
        parent = str(PurePosixPath(path).parent).casefold()
        name = PurePosixPath(path).name
        # Remove user-upload numeric collision labels only before extension.
        while True:
            new = re.sub(r"\(\d+\)(?=\.[^.]+$)", "", name)
            if new == name:
                break
            name = new
        key = parent + "/" + name.casefold()
        groups.setdefault(key, []).append({"library_file_id": identity,
                                          "path": path, "size_bytes": size})
    output = []
    for key, values in groups.items():
        if len(values) < 2:
            continue
        sizes = {x["size_bytes"] for x in values}
        same_size = len(sizes) == 1
        output.append({
            "normalized_path": key,
            "member_ids": sorted(x["library_file_id"] for x in values),
            "copies": len(values),
            "evidence": "SAME_BASENAME_AND_SIZE_ONLY" if same_size else "DIFFERENT_SIZES",
            "potential_bytes_if_verified": (len(values) - 1) * values[0]["size_bytes"]
                                           if same_size else 0,
            "decision": "HOLD_HASH_AND_DEPENDENCY_CHECK" if same_size
                        else "NOT_BYTE_IDENTICAL",
        })
    output.sort(key=lambda x: (-x["potential_bytes_if_verified"], x["normalized_path"]))
    return {
        "scope_complete": bool(complete),
        "group_count": len(output),
        "same_size_groups": sum(x["evidence"] == "SAME_BASENAME_AND_SIZE_ONLY"
                                for x in output),
        "upper_bound_bytes_if_verified": sum(x["potential_bytes_if_verified"] for x in output),
        "verified_reclaimable_bytes": 0,
        "authorized_cleanup": False,
        "groups": output,
    }
