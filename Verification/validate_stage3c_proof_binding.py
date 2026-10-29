#!/usr/bin/env python3
"""OP-02 proposed (NONACTIVE) Stage3C archive/member/card evidence integrity gate.

Input is a *separate versioned sidecar*, not a mutation of a historical ZIP.
Requires exact, supplied archive bytes. PASS means deterministic reference
closure only, never German linguistic QA, independent Stage4 or Stage5-7 PASS.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

SCHEMA = "gcpk-stage3c-proof-binding@1"
STATUS = "NONACTIVE_VERSIONED_DRY_RUN"
HEX = re.compile(r"[0-9a-f]{64}\Z")
KINDS = {"EDITORIAL_REVIEW", "SOURCE", "LOCKED_PARENT"}
MAX_ARCHIVE = 80_000_000


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_name(path: object) -> bool:
    return (isinstance(path, str) and bool(path) and
            not path.startswith("/") and "\\" not in path and
            all(p not in ("", ".", "..") for p in path.split("/")) and
            not any(c in path for c in ("\x00", "\r", "\n")))


def read_exact_zip(data: bytes, expected_sha: str) -> dict[str, bytes]:
    if not isinstance(expected_sha, str) or not HEX.fullmatch(expected_sha):
        raise ValueError("ARCHIVE_SHA_MALFORMED")
    if len(data) > MAX_ARCHIVE or sha(data) != expected_sha:
        raise ValueError("ARCHIVE_SHA_OR_SIZE_MISMATCH")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            infos = z.infolist()
            names = [x.filename for x in infos]
            if (len(infos) > 500 or len(names) != len(set(names)) or
                    sum(x.file_size for x in infos) > 100_000_000 or
                    any(x.file_size > 12_000_000 or x.is_dir() or
                        x.flag_bits & 1 or not safe_name(x.filename) or
                        stat.S_ISLNK(x.external_attr >> 16) for x in infos)):
                raise ValueError("UNSAFE_ARCHIVE_MEMBERS")
            if z.testzip() is not None:
                raise ValueError("ARCHIVE_CRC_FAILURE")
            return {name: z.read(name) for name in names}
    except (zipfile.BadZipFile, RuntimeError) as exc:
        raise ValueError("INVALID_ZIP_BYTES") from exc


def validate(contract: dict, archive_bytes: dict[str, bytes]) -> dict:
    errors: list[str] = []
    counts: Counter = Counter()

    def error(code: str) -> None:
        errors.append(code)

    if not isinstance(contract, dict) or contract.get("schema") != SCHEMA or contract.get("status") != STATUS:
        return {"status": "BLOCKED", "errors": ["NONACTIVE_SCHEMA_OR_STATUS_REQUIRED"]}
    decl = contract.get("archives")
    if not isinstance(decl, list) or not decl or len(decl) > 8:
        return {"status": "BLOCKED", "errors": ["INVALID_EXPLICIT_ARCHIVE_INVENTORY"]}
    archive_meta = {}
    for entry in decl:
        if (not isinstance(entry, dict) or
                not isinstance(entry.get("id"), str) or
                not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", entry["id"]) or
                not isinstance(entry.get("sha256"), str) or
                not HEX.fullmatch(entry["sha256"]) or
                entry["id"] in archive_meta):
            error("INVALID_OR_DUPLICATE_ARCHIVE_DECLARATION")
            continue
        archive_meta[entry["id"]] = entry["sha256"]
    if set(archive_bytes) != set(archive_meta):
        error("ARCHIVE_SET_NOT_EXACTLY_PINNED")
    members: dict[str, dict[str, bytes]] = {}
    for archive_id, digest in archive_meta.items():
        raw = archive_bytes.get(archive_id)
        if not isinstance(raw, bytes):
            error("ARCHIVE_BYTES_UNAVAILABLE: " + archive_id)
            continue
        try:
            members[archive_id] = read_exact_zip(raw, digest)
        except ValueError as exc:
            error(str(exc) + ": " + archive_id)

    def evidence(archive_id, archive_hash, path, content_hash, prefix) -> bytes | None:
        if (not isinstance(archive_id, str) or archive_id not in archive_meta or
                archive_meta[archive_id] != archive_hash):
            error(prefix + "_ARCHIVE_VERSION_NOT_PINNED")
            return None
        if not safe_name(path) or not isinstance(content_hash, str) or not HEX.fullmatch(content_hash):
            error(prefix + "_MEMBER_PATH_OR_SHA_MALFORMED")
            return None
        data = members.get(archive_id, {}).get(path)
        if data is None:
            error(prefix + "_MEMBER_NOT_PRESENT_IN_EXACT_ARCHIVE")
            return None
        if sha(data) != content_hash:
            error(prefix + "_MEMBER_SHA_MISMATCH")
            return None
        return data

    candidate = contract.get("candidate_archive_id")
    if not isinstance(candidate, str) or candidate not in archive_meta:
        return {"status": "BLOCKED", "errors": errors + ["CANDIDATE_ARCHIVE_UNPINNED"]}
    completeness = contract.get("completeness")
    if not isinstance(completeness, dict):
        return {"status": "BLOCKED", "errors": errors + ["COMPLETENESS_LOCATOR_REQUIRED"]}
    original = evidence(candidate, archive_meta.get(candidate),
                        completeness.get("path"), completeness.get("sha256"),
                        "COMPLETENESS")
    if original is None:
        return {"status": "BLOCKED", "errors": errors, "counts": dict(counts)}
    try:
        ledger = json.loads(original)
        targets = ledger["targets"]
        summary = ledger["summary"]
        if not isinstance(targets, list) or not isinstance(summary, dict):
            raise ValueError()
    except (ValueError, TypeError, KeyError, UnicodeError):
        return {"status": "BLOCKED", "errors": errors + ["MALFORMED_COMPLETENESS_LEDGER"]}

    source = contract.get("source_inventory")
    if not isinstance(source, dict):
        return {"status": "BLOCKED", "errors": errors + ["SOURCE_INVENTORY_REQUIRED"]}
    source_bytes = evidence(source.get("archive_id"), source.get("archive_sha256"),
                            source.get("path"), source.get("sha256"), "SOURCE_INVENTORY")
    occurrences = {}
    if source_bytes is not None:
        try:
            source_json = json.loads(source_bytes)
            source_items = source_json["occurrences"]
            for item in source_items:
                sid = item["occurrence_id"]
                if sid in occurrences:
                    error("DUPLICATE_SOURCE_OCCURRENCE")
                occurrences[sid] = item
        except (ValueError, KeyError, TypeError, UnicodeError):
            error("MALFORMED_SOURCE_INVENTORY")

    claimed_sha = summary.get("stage3c_editorial_sha256")
    if not isinstance(claimed_sha, str) or not HEX.fullmatch(claimed_sha):
        error("EDITORIAL_SUMMARY_SHA_MALFORMED")
    def reference_archive_sha(ref: dict, id_key: str, sha_key: str) -> str | None:
        aid = ref.get(id_key)
        if not isinstance(aid, str):
            error("EVIDENCE_ARCHIVE_ID_MALFORMED")
            return None
        if aid == candidate:
            # Whole ZIP SHA cannot be embedded within that same ZIP: use the
            # external exact-sha sidecar and disallow circular in-ZIP digest.
            if sha_key in ref:
                error("CIRCULAR_CANDIDATE_ARCHIVE_SHA")
            return archive_meta.get(candidate)
        pinned = ref.get(sha_key)
        if not isinstance(pinned, str) or archive_meta.get(aid) != pinned:
            error("IMMUTABLE_PREDECESSOR_ARCHIVE_SHA_REQUIRED")
            return None
        return pinned

    seen_targets = set()
    for target in targets:
        if not isinstance(target, dict):
            error("INVALID_TARGET"); continue
        target_id = target.get("id")
        if not isinstance(target_id, str) or not target_id or target_id in seen_targets:
            error("DUPLICATE_OR_MISSING_TARGET_ID"); continue
        seen_targets.add(target_id)
        dimensions = target.get("dimensions")
        if not isinstance(dimensions, dict) or not dimensions:
            error("NO_STAGE3C_DIMENSIONS"); continue
        counts["targets"] += 1
        for dimension, cell in dimensions.items():
            if not isinstance(cell, dict):
                error("MALFORMED_DIMENSION"); continue
            counts["cells"] += 1
            state = cell.get("status")
            refs = cell.get("basis_refs")
            if state not in ("VERIFIED_PRESENT", "CLOSED_NO_FORCE"):
                error("UNRESOLVED_STAGE3C_CELL")
            if not isinstance(refs, list):
                error("CELL_REFS_NOT_ARRAY"); continue
            if state == "VERIFIED_PRESENT" and not refs:
                error("VERIFIED_WITHOUT_EVIDENCE")
            if state == "CLOSED_NO_FORCE" and not (cell.get("reason_code") or cell.get("stage3c_review_note")):
                error("CLOSED_NO_FORCE_WITHOUT_REASON")
            for ref in refs:
                if (not isinstance(ref, dict) or
                        not isinstance(ref.get("kind"), str) or ref["kind"] not in KINDS):
                    error("UNKNOWN_EVIDENCE_KIND"); continue
                kind = ref["kind"]
                counts["refs_" + kind.lower()] += 1
                if kind in {"EDITORIAL_REVIEW", "LOCKED_PARENT"}:
                    current_sha = (ref.get("artifact_sha256") if kind == "EDITORIAL_REVIEW"
                                   else ref.get("member_sha256"))
                    archive_hash = reference_archive_sha(ref, "archive_id", "archive_sha256")
                    data = evidence(ref.get("archive_id"), archive_hash,
                                    ref.get("path"), current_sha, kind)
                    if ref.get("target_id") != target_id:
                        error(kind + "_CARD_ID_DRIFT")
                    if kind == "EDITORIAL_REVIEW" and ref.get("dimension") != dimension:
                        error("EDITORIAL_DIMENSION_DRIFT")
                    if kind == "EDITORIAL_REVIEW" and current_sha != claimed_sha:
                        error("EDITORIAL_REFERENCE_DIFFERS_FROM_SUMMARY")
                    if data is not None:
                        try:
                            document = json.loads(data)
                            cards = (document["authored_targets"]
                                     if kind == "EDITORIAL_REVIEW" else document)
                            if not isinstance(cards, list):
                                raise ValueError("not a list")
                            cards_by_id = {c["id"]: c for c in cards}
                            if len(cards_by_id) != len(cards) or target_id not in cards_by_id:
                                error(kind + "_TARGET_MISSING_OR_DUPLICATE")
                            elif kind == "LOCKED_PARENT":
                                # Deliberately specified canonical-record hash;
                                # legacy artifact_snapshot_sha256 format differs.
                                row = cards_by_id[target_id]
                                record = json.dumps(row, ensure_ascii=False,
                                    sort_keys=True, separators=(",", ":")).encode("utf-8")
                                if (ref.get("snapshot_sha_scope") != "JSON_CANONICAL_RECORD_V1"
                                        or ref.get("artifact_snapshot_sha256") != sha(record)):
                                    error("LOCKED_PARENT_RECORD_DIGEST_MISMATCH")
                        except (ValueError, TypeError, KeyError, UnicodeError):
                            error(kind + "_MALFORMED_TARGET_MEMBER")
                else:
                    # SOURCE evidence is checked against the captured exact
                    # inventory member; original RAR itself is not reread here.
                    source_hash = reference_archive_sha(
                        ref, "source_archive_id", "source_archive_sha256")
                    if (ref.get("source_archive_id") != source.get("archive_id") or
                            source_hash != source.get("archive_sha256") or
                            ref.get("source_member_sha256") != source.get("sha256")):
                        error("SOURCE_REFERENCE_NOT_ARCHIVE_BOUND")
                    occurrence_id = ref.get("source_occurrence_id")
                    item = (occurrences.get(occurrence_id)
                            if isinstance(occurrence_id, str) else None)
                    if item is None:
                        error("SOURCE_OCCURRENCE_NOT_FOUND"); continue
                    if (item.get("source_id") != ref.get("source_id") or
                            item.get("locator", {}).get("row") != ref.get("source_ordinal") or
                            item.get("source_row_payload_sha256") != ref.get("source_row_payload_sha256")):
                        error("SOURCE_ID_ROW_OR_PAYLOAD_HASH_DRIFT")
    if (summary.get("targets") != len(seen_targets) or
            summary.get("dimension_cells") != counts["cells"] or
            summary.get("unresolved_cells") != 0):
        error("STAGE3C_COMPLETENESS_COUNTER_DRIFT")
    if counts["refs_editorial_review"] == 0:
        error("EDITORIAL_REVIEW_EVIDENCE_REQUIRED")
    return {
        "schema": "gcpk-stage3c-proof-binding-result@1",
        "status": "PASS_SCOPED_DETERMINISTIC_PROOF_BINDING_ONLY" if not errors else "BLOCKED",
        "errors": sorted(set(errors)),
        "counts": dict(counts),
        "claims_not_proven": [
            "Independence or accuracy of linguistic AI Stage4 assessment",
            "Original external RAR extraction and original raw-source SHA verification",
            "Semantic/didactic teaching_delta for displayed combinations",
            "Mutable production CURRENT or Stage5/6/7 acceptance",
            "Approval to activate a new writer/schema migration",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--archive", action="append", required=True, metavar="ID=ZIP")
    args = p.parse_args()
    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        paths = {}
        for param in args.archive:
            id_, sep, path = param.partition("=")
            if not sep or id_ in paths:
                raise ValueError("DUPLICATE_OR_BAD_ARCHIVE_ARGUMENT")
            paths[id_] = Path(path).read_bytes()
        result = validate(contract, paths)
    except (ValueError, OSError, UnicodeError) as exc:
        result = {"status": "BLOCKED", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS_SCOPED_DETERMINISTIC_PROOF_BINDING_ONLY" else 2


if __name__ == "__main__":
    sys.exit(main())
