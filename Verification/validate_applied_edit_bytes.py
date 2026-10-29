#!/usr/bin/env python3
"""OP-01: independently compare an applied-edit claim against actual local bytes.

Prospective opt-in proof for synthetic/JSON-item writers. It does not by itself
establish remote Library/Git persistence, linguistic Stage4, or full Stage5-7.
No source, CURRENT, checkpoint or archive bytes are ever modified here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

SCHEMA = "gcpk-applied-edit-bytes-proof@1"
FILE_KEYS = ("parent", "current", "readback", "source_before", "source_after", "qa", "pointer")
HASH_KEYS = ("parent", "current", "readback", "source_before", "source_after", "qa")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()



def parse_tsv(data: bytes, id_column: str) -> list[dict[str, str]]:
    if not isinstance(id_column, str) or not id_column:
        raise ValueError("TSV must name a nonempty id_column")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("TSV is not UTF-8") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter="\t", restkey="_EXTRA_FIELDS")
    headers = reader.fieldnames
    if not headers or len(headers) != len(set(headers)) or id_column not in headers or "_EXTRA_FIELDS" in headers:
        raise ValueError("TSV missing/duplicate columns or stable id_column")
    cards = list(reader)
    if not cards or any(
        not isinstance(r, dict) or any(r.get(k) is None for k in headers) or "_EXTRA_FIELDS" in r
        or not r.get(id_column) or any("\r" in r[k] or "\n" in r[k] for k in headers)
        for r in cards
    ):
        raise ValueError("TSV empty, ragged, multiline, or missing stable id")
    return [{"id": r[id_column], **{k: v for k, v in r.items() if k != id_column}} for r in cards]



def tsv_headers(data: bytes) -> list[str]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("TSV is not UTF-8") from exc
    reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t")
    headers = next(reader, [])
    if (not headers or len(headers) != len(set(headers))
            or any(not x or "\r" in x or "\n" in x for x in headers)):
        raise ValueError("TSV missing/duplicate columns")
    return headers


def nested_diff(before: object, after: object, prefix: str) -> set[str]:
    if isinstance(before, dict) and isinstance(after, dict):
        changed: set[str] = set()
        for key in set(before) | set(after):
            if not isinstance(key, str) or not key or "." in key:
                raise ValueError("unsupported nested JSON key")
            name = prefix + "." + key
            if key not in before or key not in after:
                changed.add(name)
            else:
                changed.update(nested_diff(before[key], after[key], name))
        return changed
    return {prefix} if before != after else set()


def item_diff(before: dict, after: dict, nested_columns: list[str]) -> set[str]:
    changed: set[str] = set()
    for key in set(before) | set(after):
        if key in nested_columns:
            if key not in before or key not in after:
                changed.add(key)
                continue
            if before[key] == after[key]:
                continue
            if not isinstance(before[key], str) or not isinstance(after[key], str):
                raise ValueError("nested columns must hold JSON text")
            try:
                old, new = json.loads(before[key]), json.loads(after[key])
            except (ValueError, UnicodeError) as exc:
                raise ValueError("invalid embedded JSON in " + key) from exc
            if not isinstance(old, dict) or not isinstance(new, dict):
                raise ValueError("nested JSON column must be an object: " + key)
            changed.update(nested_diff(old, new, key))
        elif before.get(key) != after.get(key):
            changed.add(key)
    return changed


def zip_members(data: bytes, *, member: str, manifest: str) -> dict[str, bytes]:
    if not isinstance(member, str) or not member.endswith(".tsv") or not member or "\\" in member:
        raise ValueError("ZIP_TSV_V1 needs a safe TSV member")
    if not isinstance(manifest, str) or manifest != "SHA256SUMS":
        raise ValueError("ZIP_TSV_V1 requires root SHA256SUMS manifest")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            names = [entry.filename for entry in entries]
            if (len(names) != len(set(names)) or len(names) < 3 or len(names) > 1000
                    or member not in names or manifest not in names
                    or any(n.startswith("/") or "\\" in n or ".." in Path(n).parts for n in names)
                    or any(entry.is_dir() for entry in entries)
                    or any(entry.file_size > 100 * 1024 * 1024 for entry in entries)
                    or sum(entry.file_size for entry in entries) > 256 * 1024 * 1024
                    or any(entry.file_size > 1024 * 1024 and entry.file_size > 500 * max(1, entry.compress_size) for entry in entries)):
                raise ValueError("ZIP missing, duplicate, unsafe, oversized or malformed members")
            if archive.testzip() is not None:
                raise ValueError("ZIP CRC failure")
            payloads = {name: archive.read(name) for name in names}
    except (OSError, zipfile.BadZipFile, RuntimeError, EOFError) as exc:
        raise ValueError("ZIP unreadable or CRC failure") from exc
    try:
        lines = payloads[manifest].decode("utf-8").splitlines()
        digest_map = {}
        for line in lines:
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
            if not match or match[2] in digest_map:
                raise ValueError("invalid or duplicate manifest record")
            digest_map[match[2]] = match[1]
        if set(digest_map) != set(payloads) - {manifest}:
            raise ValueError("ZIP manifest does not cover all members exactly")
        for name, expected in digest_map.items():
            if digest(payloads[name]) != expected:
                raise ValueError("ZIP member SHA256 mismatch")
    except UnicodeDecodeError as exc:
        raise ValueError("ZIP manifest not UTF-8") from exc
    return payloads


def card_rows(before: bytes, after: bytes, proof: dict) -> tuple[list[dict], list[dict]]:
    format_name = proof.get("format", "JSON_ITEMS_V1")
    if format_name == "JSON_ITEMS_V1":
        a, b = json.loads(before), json.loads(after)
        if not isinstance(a, dict) or not isinstance(b, dict):
            raise ValueError("JSON items parent/current must be objects")
        return a.get("cards"), b.get("cards")
    if format_name == "TSV_ITEMS_V1":
        if tsv_headers(before) != tsv_headers(after):
            raise ValueError("TSV header/order/schema changed")
        col = proof.get("id_column")
        return parse_tsv(before, col), parse_tsv(after, col)
    if format_name == "ZIP_TSV_V1":
        member = proof.get("member")
        manifest = proof.get("manifest_member")
        old_members = zip_members(before, member=member, manifest=manifest)
        new_members = zip_members(after, member=member, manifest=manifest)
        if set(old_members) != set(new_members):
            raise ValueError("ZIP member inventory changed")
        for name, data in old_members.items():
            if name not in (member, manifest) and data != new_members[name]:
                raise ValueError("unrelated ZIP member payload changed: " + name)
        if tsv_headers(old_members[member]) != tsv_headers(new_members[member]):
            raise ValueError("TSV header/order/schema changed")
        if old_members[member] == new_members[member]:
            raise ValueError("target ZIP TSV unchanged")
        col = proof.get("id_column")
        return parse_tsv(old_members[member], col), parse_tsv(new_members[member], col)
    raise ValueError("unsupported format; only JSON_ITEMS_V1, TSV_ITEMS_V1, ZIP_TSV_V1")


def verify(proof_file: Path) -> list[str]:
    errors: list[str] = []
    try:
        root = proof_file.resolve().parent
        proof = json.loads(proof_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        return ["cannot load proof: " + str(exc)]
    if not isinstance(proof, dict) or proof.get("schema") != SCHEMA:
        return ["invalid proof schema"]
    if proof.get("status") != "APPLIED_SCOPED":
        errors.append("not a scoped APPLIED claim")
    if not isinstance(proof.get("workstream"), str) or not proof["workstream"].strip():
        errors.append("missing workstream")
    if not isinstance(proof.get("artifact_id"), str) or not proof["artifact_id"].strip():
        errors.append("missing artifact_id")
    paths: dict[str, Path] = {}
    contents: dict[str, bytes] = {}
    for key in FILE_KEYS:
        item = proof.get("files", {}).get(key) if isinstance(proof.get("files"), dict) else None
        if not isinstance(item, str) or not item or Path(item).is_absolute():
            errors.append(f"missing/absolute {key} path")
            continue
        p = (root / item).resolve()
        if p == root or root not in p.parents:
            errors.append(f"unsafe {key} path")
            continue
        try:
            contents[key] = p.read_bytes()
            paths[key] = p
        except OSError:
            errors.append(f"unreadable {key} file")
    if errors:
        return errors
    if paths["current"] == paths["readback"]:
        errors.append("readback must be a separate file")
    if paths["parent"] == paths["current"]:
        errors.append("parent and current must be distinct paths")
    if paths["source_before"] == paths["source_after"]:
        errors.append("source before/after snapshots need separate paths")
    expected = proof.get("sha256", {})
    if not isinstance(expected, dict):
        expected = {}
    for key in HASH_KEYS:
        if expected.get(key) != digest(contents[key]):
            errors.append(f"SHA256 mismatch: {key}")
    if contents["parent"] == contents["current"]:
        errors.append("report-only: CURRENT bytes unchanged")
    if contents["current"] != contents["readback"]:
        errors.append("persisted readback differs from CURRENT bytes")
    if contents["source_before"] != contents["source_after"]:
        errors.append("immutable source bytes mutated")
    try:
        prior, updated = card_rows(contents["parent"], contents["current"], proof)
        pointer = json.loads(contents["pointer"])
        qa = json.loads(contents["qa"])
    except (ValueError, UnicodeError, TypeError) as exc:
        return errors + ["unverified content format/JSON receipt: " + str(exc)]
    if not all(isinstance(x, dict) for x in (pointer, qa)):
        return errors + ["pointer and qa must be JSON objects"]
    if pointer.get("workstream") != proof["workstream"] or pointer.get("artifact_id") != proof["artifact_id"]:
        errors.append("currentness pointer identity mismatch")
    if pointer.get("current_sha256") != digest(contents["current"]):
        errors.append("currentness pointer does not resolve edited bytes")
    if qa.get("result") != "PASS" or not isinstance(qa.get("test_suite"), str) or not qa["test_suite"].strip():
        errors.append("post-edit QA not PASS with named test suite")
    if qa.get("assessed_sha256") != digest(contents["current"]):
        errors.append("post-edit QA assessed wrong/stale artifact")
    if not isinstance(prior, list) or not isinstance(updated, list):
        return errors + ["current format requires cards arrays/rows"]
    if any(not isinstance(x, dict) or not isinstance(x.get("id"), str) or not x["id"] for x in prior + updated):
        return errors + ["invalid stable card IDs"]
    old_ids, new_ids = [x["id"] for x in prior], [x["id"] for x in updated]
    if len(set(old_ids)) != len(old_ids) or len(set(new_ids)) != len(new_ids):
        errors.append("duplicate stable IDs")
    if old_ids != new_ids:
        errors.append("card count/order/identity changed")
    requested = proof.get("edits")
    if not isinstance(requested, list) or not requested:
        return errors + ["no explicitly enumerated applied edits"]
    declared: dict[str, set[str]] = {}
    for entry in requested:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            errors.append("invalid applied edit record")
            continue
        fields = entry.get("fields")
        if (entry["id"] in declared or not isinstance(fields, list) or not fields
                or any(not isinstance(f, str) or not f or f == "id" for f in fields)
                or len(set(fields)) != len(fields)):
            errors.append("duplicate/invalid edit fields or ID")
        else:
            declared[entry["id"]] = set(fields)
    nested_columns = proof.get("nested_json_columns", [])
    if not isinstance(nested_columns, list) or any(
        not isinstance(name, str) or not name or name == "id" or "." in name
        for name in nested_columns
    ) or len(set(nested_columns)) != len(nested_columns):
        return errors + ["invalid nested_json_columns list"]
    if nested_columns and proof.get("format") not in ("TSV_ITEMS_V1", "ZIP_TSV_V1"):
        return errors + ["nested_json_columns require TSV/ZIP format"]
    observed: dict[str, set[str]] = {}
    for b, a in zip(prior, updated):
        if b["id"] != a["id"]:
            continue
        try:
            changed = item_diff(b, a, nested_columns)
        except (ValueError, UnicodeError) as exc:
            return errors + ["nested diff format error: " + str(exc)]
        if changed:
            observed[b["id"]] = changed
    if declared != observed:
        errors.append("actual changed IDs/fields differ from applied-edit ledger")
    if qa.get("changed_ids") != sorted(observed):
        errors.append("QA changed-ID scope mismatches actual edit")
    if proof.get("applied_count") != len(observed) or len(observed) == 0:
        errors.append("APPLIED count inconsistent with actual current diff")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", type=Path)
    args = parser.parse_args()
    errors = verify(args.proof)
    print(json.dumps({
        "status": "PASS_SCOPED_LOCAL_BYTE_PROOF_NOT_STAGE4_OR_REMOTE_PERSISTENCE"
                  if not errors else "BLOCKED",
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
