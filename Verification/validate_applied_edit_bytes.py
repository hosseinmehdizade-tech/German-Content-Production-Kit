#!/usr/bin/env python3
"""OP-01: independently compare an applied-edit claim against actual local bytes.

Prospective opt-in proof for synthetic/JSON-item writers. It does not by itself
establish remote Library/Git persistence, linguistic Stage4, or full Stage5-7.
No source, CURRENT, checkpoint or archive bytes are ever modified here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCHEMA = "gcpk-applied-edit-bytes-proof@1"
FILE_KEYS = ("parent", "current", "readback", "source_before", "source_after", "qa", "pointer")
HASH_KEYS = ("parent", "current", "readback", "source_before", "source_after", "qa")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        before = json.loads(contents["parent"])
        after = json.loads(contents["current"])
        pointer = json.loads(contents["pointer"])
        qa = json.loads(contents["qa"])
    except (ValueError, UnicodeError):
        return errors + ["invalid JSON content in parent/current/pointer/qa"]
    if not all(isinstance(x, dict) for x in (before, after, pointer, qa)):
        return errors + ["parent/current/pointer/qa must be JSON objects"]
    if pointer.get("workstream") != proof["workstream"] or pointer.get("artifact_id") != proof["artifact_id"]:
        errors.append("currentness pointer identity mismatch")
    if pointer.get("current_sha256") != digest(contents["current"]):
        errors.append("currentness pointer does not resolve edited bytes")
    if qa.get("result") != "PASS" or not isinstance(qa.get("test_suite"), str) or not qa["test_suite"].strip():
        errors.append("post-edit QA not PASS with named test suite")
    if qa.get("assessed_sha256") != digest(contents["current"]):
        errors.append("post-edit QA assessed wrong/stale artifact")
    if not isinstance(before.get("cards"), list) or not isinstance(after.get("cards"), list):
        return errors + ["JSON_ITEMS_V1 requires cards arrays"]
    prior, updated = before["cards"], after["cards"]
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
    observed: dict[str, set[str]] = {}
    for b, a in zip(prior, updated):
        if b["id"] != a["id"]:
            continue
        changed = {key for key in set(b) | set(a) if b.get(key) != a.get(key)}
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
