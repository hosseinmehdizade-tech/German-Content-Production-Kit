#!/usr/bin/env python3
"""Read-only reconciliation of ten curated content-family registry pointers.

Compares a checked-out Git tree and its source-owner JSON files. This never
reads Library/Drive bytes, never promotes a release, and never writes to Git.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import sys

REGISTRY = "Optimization-Program/Control-Center/DYNAMIC-CONTENT-PORTFOLIO-REGISTRY-v1.json"
CATALOG = "Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
HEX40 = re.compile(r"^[a-f0-9]{40}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")
SCHEMA = "gfp-opt-content-portfolio-reconciliation@1.0.0"


def safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("invalid path")
    rel = Path(relative)
    if rel.is_absolute() or any(part in ("", ".", "..") for part in rel.parts):
        raise ValueError("unsafe path: " + relative)
    base = root.resolve()
    full = (base / rel).resolve()
    if not full.is_relative_to(base):
        raise ValueError("path escapes root: " + relative)
    return full


def load_json(root: Path, relative: str) -> dict:
    value = json.loads(safe_path(root, relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("expected JSON object: " + relative)
    return value


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\\0" + data).hexdigest()


def json_pointer(obj: dict, pointer: str):
    if not isinstance(pointer, str) or not pointer.startswith("/") or pointer == "/":
        raise ValueError("invalid JSON pointer")
    current = obj
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            raise KeyError(pointer)
        current = current[token]
    return current


def validate_registry(registry: dict, catalog: dict) -> list[dict]:
    if registry.get("schema") != "gfp-opt-dynamic-content-portfolio-registry@1.0.0":
        raise ValueError("unsupported registry schema")
    families = catalog.get("families")
    items = registry.get("items")
    if not isinstance(families, list) or not isinstance(items, list) or len(items) != 10:
        raise ValueError("expected 10 registry entries and a family catalog")
    known = {x.get("id") for x in families}
    ids, total = set(), 0
    for item in items:
        fid = item.get("id")
        if fid in ids or fid not in known or not isinstance(fid, str):
            raise ValueError("missing, duplicate or unknown family id")
        ids.add(fid)
        owner, baseline = item.get("owner_locator"), item.get("active_baseline")
        if not isinstance(owner, dict) or not isinstance(baseline, dict):
            raise ValueError("owner and baseline required: " + fid)
        if not HEX40.fullmatch(str(owner.get("git_blob_observed", ""))):
            raise ValueError("invalid recorded Git blob: " + fid)
        if not HEX64.fullmatch(str(baseline.get("artifact_sha256", ""))):
            raise ValueError("invalid selected artifact SHA256: " + fid)
        if not isinstance(owner.get("artifact_sha_json_pointer"), str):
            raise ValueError("missing owner artifact JSON pointer: " + fid)
        if not str(owner.get("path", "")).startswith("Workspaces/"):
            raise ValueError("owner must be an independent workspace path: " + fid)
        count = item.get("metrics", {}).get("cards")
        if type(count) is not int or count < 1:
            raise ValueError("bad card count: " + fid)
        total += count
    if total != registry.get("total_cards_including_cross_family_overlap"):
        raise ValueError("non-unique card sum changed")
    return items


def inspect_item(root: Path, item: dict) -> dict:
    owner, baseline = item["owner_locator"], item["active_baseline"]
    result = {
        "family_id": item["id"],
        "owner_path": owner["path"],
        "json_pointer": owner["artifact_sha_json_pointer"],
        "recorded_git_blob": owner["git_blob_observed"],
        "observed_git_blob": None,
        "recorded_artifact_sha256": baseline["artifact_sha256"],
        "observed_owner_artifact_sha256": None,
        "classification": "OWNER_UNRESOLVED_HOLD",
        "release_or_runtime_acceptance": "NOT_EVALUATED",
        "library_drive_artifact_bytes": "NOT_CHECKED",
    }
    try:
        path = safe_path(root, owner["path"])
        raw = path.read_bytes()
        result["observed_git_blob"] = git_blob_sha(raw)
        owner_doc = json.loads(raw)
        selected = json_pointer(owner_doc, owner["artifact_sha_json_pointer"])
        if not isinstance(selected, str) or not HEX64.fullmatch(selected):
            raise ValueError("selected owner field is not SHA256")
        result["observed_owner_artifact_sha256"] = selected
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        result["detail"] = type(exc).__name__ + ": " + str(exc)[:200]
        return result
    if selected != baseline["artifact_sha256"]:
        result["classification"] = "OWNER_ARTIFACT_POINTER_DRIFT_REVIEW"
    elif result["observed_git_blob"] != owner["git_blob_observed"]:
        result["classification"] = "OWNER_METADATA_DRIFT_REVIEW"
    else:
        result["classification"] = "GIT_REFERENCES_MATCH"
    return result


def reconcile(root: Path) -> dict:
    registry = load_json(root, REGISTRY)
    catalog = load_json(root, CATALOG)
    items = validate_registry(registry, catalog)
    rows = [inspect_item(root, x) for x in items]
    counter = Counter(row["classification"] for row in rows)
    status = ("HOLD_OWNER_UNRESOLVED" if counter.get("OWNER_UNRESOLVED_HOLD")
              else "REVIEW_REQUIRED" if any(k.endswith("_REVIEW") for k in counter)
              else "GIT_REFERENCES_MATCH__ARTIFACT_BYTES_UNCHECKED")
    return {
        "schema": SCHEMA,
        "scope": "TEN_CURATED_FAMILIES__GIT_CHECKOUT_ONLY",
        "registry_state": registry["registry_state"],
        "status": status,
        "counts": {"families": len(rows), "matching_git_pointers": counter["GIT_REFERENCES_MATCH"],
                   "owner_metadata_changed": counter["OWNER_METADATA_DRIFT_REVIEW"],
                   "owner_artifact_pointer_changed": counter["OWNER_ARTIFACT_POINTER_DRIFT_REVIEW"],
                   "unresolved": counter["OWNER_UNRESOLVED_HOLD"]},
        "explicit_exclusions": [
            "Not a live ChatGPT Library or Google Drive byte check",
            "Not a newer user-upload discovery; owner Git can lag a newer accepted artifact",
            "Not content/semantic Stage4, app Stage6, runtime, FSRS, SRS or Stage7 certification",
            "Never automatic promotion or old-publisher source rebase",
        ],
        "items": rows,
    }


def summary_md(report: dict) -> str:
    rows = [
        "# Dynamic Content Portfolio: read-only reconciliation",
        "",
        "**Result:** `" + report["status"] + "`",
        "",
        "Family | Git reference | Owner artifact pointer",
        "--- | --- | ---",
    ]
    for item in report["items"]:
        label = item["classification"]
        pointer = item["observed_owner_artifact_sha256"] or "UNRESOLVED"
        rows.append(item["family_id"] + " | " + label + " | " + pointer[:14])
    rows += [
        "",
        "This checks checked-out Git blobs and selected owner JSON pointers only.",
        "Library/Drive bytes, independently accepted newer artifacts and real app/SRS are **not checked**.",
        "All differences require human/authorized source-owner review; nothing is promoted.",
        "",
    ]
    return "\n".join(rows)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, help="Optional output directory OUTSIDE the Git repo")
    parser.add_argument("--github-summary", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true",
                        help="Opt-in strict mode; never modifies repository")
    args = parser.parse_args(argv)
    try:
        report = reconcile(args.repo_root)
        if args.out_dir:
            root = args.repo_root.resolve()
            out = args.out_dir.resolve()
            if out.is_relative_to(root):
                raise ValueError("output directory inside repository forbidden")
            out.mkdir(parents=True, exist_ok=True)
            (out / "RECONCILIATION.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (out / "RECONCILIATION.md").write_text(summary_md(report), encoding="utf-8")
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
                fh.write(summary_md(report))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2 if args.fail_on_review and not report["status"].startswith("GIT_REFERENCES_MATCH") else 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID_REGISTRY_HOLD",
                          "error": type(exc).__name__ + ": " + str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
