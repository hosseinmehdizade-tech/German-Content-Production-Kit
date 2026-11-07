#!/usr/bin/env python3
"""Read-only accepted-successor discovery across catalog-mapped parallel workspaces.

This is a conservative notification tool, NOT a release resolver. It can flag
a new source-owned accepted artifact for review but cannot prove that it
supersedes a different accepted release without the exact user approval,
immediate-parent CAS, storage byte checks, and independent stage gates.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import sys

REGISTRY = "Optimization-Program/Control-Center/DYNAMIC-CONTENT-PORTFOLIO-REGISTRY-v1.json"
CATALOG = "Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
SCHEMA = "gfp-opt-parallel-accepted-source-discovery@1.0.0"
DOCUMENTS = ("LATEST.json", "CHECKPOINT.json", "STAGE7-LATEST.json")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
REPO = "hosseinmehdizade-tech/German-Content-Production-Kit"
SOURCE_FIELDS = (
    ("final_content_authority", ("sha256", "zip_sha256"), ("name", "filename")),
    ("final_delivery", ("zip_sha256", "sha256", "file_sha256"), ("zip_name", "filename", "name")),
    ("artifact", ("sha256", "zip_sha256"), ("name", "filename")),
    ("current_content_only_delivery", ("sha256",), ("filename", "name", "artifact")),
    ("final_content_only_v18", ("sha256",), ("filename", "name")),
)
ACCEPTED = re.compile(r"USER[_-]ACCEPTED|USER[_-]IMPORT[_-]ACCEPTED", re.I)
NEGATED_ACCEPTED = re.compile(r"(?:^|[_-])(?:NOT|PENDING|UNVERIFIED)[_-]USER[_-]ACCEPTED", re.I)
DRAFT_FILENAME = re.compile(r"(?:^|[-_])(WIP|PREVIEW|CANDIDATE|NOT[-_]IMPORT)(?:[-_.]|$)", re.I)


def below(root: Path, rel: str) -> Path:
    if not isinstance(rel, str) or not rel.startswith("Workspaces/"):
        raise ValueError("Expected a Workspaces/ path")
    if "\\" in rel or any(s in ("", ".", "..") for s in rel.split("/")):
        raise ValueError("Unsafe workspace path")
    home = root.resolve()
    path = (home / rel).resolve()
    if not path.is_relative_to(home):
        raise ValueError("Path escapes checkout")
    return path


def load(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("Expected JSON object")
    return obj


def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + bytes([0]) + data).hexdigest()


def pointer(obj: dict, route: str):
    if not isinstance(route, str) or not route.startswith("/"):
        raise ValueError("Invalid selected owner pointer")
    cur = obj
    for key in route.split("/")[1:]:
        token = key.replace("~1", "/").replace("~0", "~")
        if not isinstance(cur, dict):
            raise KeyError(route)
        cur = cur[token]
    return cur


def source_date(doc: dict) -> str | None:
    for key in ("date", "updated_at", "observed_date", "last_verified_update_date"):
        val = doc.get(key)
        if isinstance(val, str) and re.fullmatch(r"20\d{2}-\d{2}-\d{2}", val[:10]):
            return val[:10]
    return None


def qualifying(doc: dict, path: str, family_id: str) -> list[dict]:
    # These are evidence leads, not automatic acceptance/promotion decisions.
    status = str(doc.get("status") or doc.get("state") or "")
    if not ACCEPTED.search(status) or NEGATED_ACCEPTED.search(status):
        return []
    found = []
    for field, hash_fields, name_fields in SOURCE_FIELDS:
        piece = doc.get(field)
        if not isinstance(piece, dict):
            continue
        sha = next((piece.get(k) for k in hash_fields
                    if isinstance(piece.get(k), str) and SHA256.fullmatch(piece[k])), None)
        name = next((piece.get(k) for k in name_fields
                     if isinstance(piece.get(k), str) and piece[k].lower().endswith(".zip")), None)
        if not sha or not name or DRAFT_FILENAME.search(name):
            continue
        found.append({
            "family_id": family_id,
            "source_path": path,
            "field": field,
            "artifact_sha256": sha,
            "artifact_name": name,
            "source_status": status[:230],
            "source_date": source_date(doc),
            "acceptance_signal": "EXPLICIT_USER_ACCEPTED_STATUS__NOT_INDEPENDENT_USER_DECISION_OR_STAGE_PROOF",
        })
    return found


def investigate(root: Path) -> dict:
    root = root.resolve()
    reg = load(root / REGISTRY)
    cat = load(root / CATALOG)
    items = reg.get("items")
    workspaces = cat.get("workspaces")
    if reg.get("schema") != "gfp-opt-dynamic-content-portfolio-registry@1.0.0":
        raise ValueError("Unexpected central portfolio registry")
    if not isinstance(items, list) or len(items) != 10 or not isinstance(workspaces, list):
        raise ValueError("Invalid ten-family registry/catalog")
    families = {entry["id"]: entry for entry in items}
    if len(families) != 10:
        raise ValueError("Duplicate family")
    dirs: dict[str, set[str]] = defaultdict(set)
    all_dirs = set()
    for w in workspaces:
        rel = w.get("git_dir")
        fid = w.get("parent_family_id")
        if not isinstance(rel, str) or len(rel.split("/")) != 2:
            raise ValueError("Bad catalog workspace path")
        below(root, rel)
        if rel in all_dirs:
            raise ValueError("Duplicate catalog workspace")
        all_dirs.add(rel)
        if fid in families:
            dirs[fid].add(rel)
    # No guessing family identity from workspace slug for new/unmapped dirs.
    workspace_root = root / "Workspaces"
    unexpected = sorted(p.name for p in workspace_root.iterdir()
                        if p.is_dir() and ("Workspaces/" + p.name) not in all_dirs) if workspace_root.exists() else []
    results = []
    counters = {"source_documents_checked": 0, "mapped_workspace_directories_scanned": 0,
                "accepted_alternatives_require_review": 0,
                "accepted_alternatives_older_date_hint": 0,
                "ignored_unqualified_or_draft_candidates": 0,
                "unmapped_workspaces": len(unexpected)}
    for fid, entry in sorted(families.items()):
        selected = entry["active_baseline"]["artifact_sha256"]
        if not SHA256.fullmatch(selected):
            raise ValueError("Bad selected SHA " + fid)
        current_owner = entry["owner_locator"]
        if current_owner.get("repository") != REPO:
            raise ValueError("Unexpected current owner repository " + fid)
        chosen_path = current_owner["path"]
        owner_file = below(root, chosen_path)
        if not owner_file.is_file():
            raise ValueError("Missing selected source owner " + chosen_path)
        owner_bytes = owner_file.read_bytes()
        owner = json.loads(owner_bytes)
        owner_sha = pointer(owner, current_owner["artifact_sha_json_pointer"])
        owner_blob_matches = blob(owner_bytes) == current_owner["git_blob_observed"]
        if owner_sha != selected or not owner_blob_matches:
            results.append({"family_id":fid,"status":"HOLD_SELECTED_OWNER_DRIFT",
                            "registry_sha256": selected, "selected_source_path": chosen_path,
                            "owner_blob_matches":owner_blob_matches,"owner_sha256_matches":owner_sha==selected,
                            "alternatives":[]})
            continue
        selected_date = source_date(owner)
        observed_paths = {chosen_path}
        leads = []
        for directory in sorted(dirs[fid]):
            counters["mapped_workspace_directories_scanned"] += 1
            for name in DOCUMENTS:
                rel = directory + "/" + name
                p = below(root, rel)
                if not p.is_file() or rel in observed_paths:
                    continue
                observed_paths.add(rel)
                doc = load(p)
                counters["source_documents_checked"] += 1
                candidates = qualifying(doc, rel, fid)
                if not candidates:
                    counters["ignored_unqualified_or_draft_candidates"] += 1
                for candidate in candidates:
                    if candidate["artifact_sha256"] != selected:
                        leads.append(candidate)
        by_sha = defaultdict(list)
        for lead in leads:
            by_sha[lead["artifact_sha256"]].append(lead)
        alternatives = []
        for sha, group in sorted(by_sha.items()):
            # Date fields are hints only; NEVER enough to make a new CURRENT.
            dated = [a["source_date"] for a in group if a["source_date"]]
            hint = (max(dated) if dated else None)
            older_hint = bool(selected_date and hint and hint < selected_date)
            status = ("HISTORICAL_ACCEPTED_SIBLING__NOT_RECOMMENDED_FOR_PROMOTION"
                      if older_hint else "ACCEPTED_PARALLEL_SOURCE__AUTHORITY_REVIEW_REQUIRED")
            if older_hint:
                counters["accepted_alternatives_older_date_hint"] += 1
            else:
                counters["accepted_alternatives_require_review"] += 1
            alternatives.append({
                "sha256":sha,"status":status,"source_date_hint":hint,
                "date_comparison_is_proof_of_promotion":False,
                "evidence":group[:12],
            })
        results.append({
            "family_id":fid, "status":"REVIEW_ALTERNATIVE_USER_ACCEPTED_SOURCE"
            if any(a["status"].startswith("ACCEPTED_PARALLEL") for a in alternatives)
            else ("OLDER_ACCEPTED_SIBLINGS_RECORDED" if alternatives else "NO_QUALIFIED_ALTERNATE_ACCEPTED_SOURCE"),
            "selected_source_path":chosen_path,"selected_source_blob":current_owner["git_blob_observed"],
            "current_sha256":selected,"selected_source_date_hint":selected_date,
            "workspaces_scanned":len(dirs[fid]),"alternatives":alternatives,
        })
    overall = ("HOLD_SELECTED_OWNER_DRIFT" if any(r["status"]=="HOLD_SELECTED_OWNER_DRIFT" for r in results)
               else "REVIEW_PARALLEL_ACCEPTED_SOURCE" if counters["accepted_alternatives_require_review"]
               else "REVIEW_UNMAPPED_WORKSPACES" if unexpected
               else "NO_QUALIFIED_NEWER_ACCEPTED_SOURCE_OBSERVED")
    return {
        "schema":SCHEMA,"status":overall,
        "scope":"CATALOG_MAPPED_PARALLEL_WORKSPACE_POINTER_DOCS__READ_ONLY",
        "all_catalog_workspaces":len(workspaces),
        "portfolio_families":len(families),
        "counters":counters,
        "unmapped_workspace_names":unexpected,
        "limits":[
            "Only LATEST/CHECKPOINT/STAGE7-LATEST in catalog-mapped workspaces; additional Stage7 receipts require explicit owner review",
            "New acceptance is a source-file signal, not independent user approval or exact ZIP byte proof",
            "Dated source metadata is a triage hint, never promotion evidence",
            "Not a live Library/Drive watcher and not a full repository content search",
            "Never replaces a curated accepted TSV/ZIP, source-owner LATEST, SRS or app runtime",
            "Review means inspect user-acceptance receipt, exact SHA, immediate parent and CAS",
        ],
        "families":results,
    }


def summary(report: dict) -> str:
    lines=["# Parallel Accepted Source Discovery — read-only",
           "", "**Status:** `"+report["status"]+"`",
           "", "Family | Status | Accepted sibling versions requiring review | Older hints",
           "--- | --- | ---: | ---:"]
    for row in report["families"]:
        alt=row.get("alternatives",[])
        lines.append(row["family_id"]+" | "+row["status"]+" | "+
                     str(sum(x["status"].startswith("ACCEPTED_PARALLEL") for x in alt))+" | "+
                     str(sum(x["status"].startswith("HISTORICAL") for x in alt)))
    lines.extend(["","This scans only catalog-mapped pointers. Date is only a hint.",
                  "**No release auto-promotion, ZIP semantic verification, Library/Drive access, app or SRS change.**",""])
    return "\n".join(lines)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out-dir",type=Path)
    ap.add_argument("--github-summary",action="store_true")
    ap.add_argument("--fail-on-review",action="store_true")
    args=ap.parse_args(argv)
    try:
        report=investigate(args.repo_root)
        if args.out_dir:
            folder=args.out_dir.resolve()
            if folder.is_relative_to(args.repo_root.resolve()):
                raise ValueError("Derived outputs must be outside Git checkout")
            folder.mkdir(parents=True,exist_ok=True)
            (folder/"PARALLEL-SOURCES.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
            (folder/"PARALLEL-SOURCES.md").write_text(summary(report),encoding="utf8")
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as out:
                out.write(summary(report))
        print(json.dumps(report,ensure_ascii=False,indent=2))
        return 2 if args.fail_on_review and report["status"] != "NO_QUALIFIED_NEWER_ACCEPTED_SOURCE_OBSERVED" else 0
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"INVALID_SOURCE_DISCOVERY_HOLD",
                          "reason":type(exc).__name__+": "+str(exc)[:250]}))
        return 2


if __name__=="__main__":
    sys.exit(main())
