#!/usr/bin/env python3
"""Read-only dependency inventory for the 20 preserved noncanonical Git Workspaces.

Scans exact tracked Git HEAD paths and literal inbound references in textual
tracked blobs. It cannot prove safe deletion or determine whether historical
checkpoints are active. No file moves, source mutations, or release promotions.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import subprocess
import sys

ROUTING = "Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"
SCHEMA = "gcpk-legacy-workspace-dependency-inventory@1.0.0"
EXPECTED_ROUTING = "gcpk-canonical-family-workspace-routing@1.0.0"
MAX_TEXT_BLOB = 8 * 1024 * 1024

def git(root: Path, args: list[str], *, codes=(0,)) -> bytes:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    if result.returncode not in codes:
        raise ValueError("Git read-only command failed: " + " ".join(args[:4])
                         + " (exit=" + str(result.returncode) + ")")
    return result.stdout

def route_path(path: str) -> str:
    if (not isinstance(path, str) or not path.startswith("Workspaces/")
            or path.count("/") != 1 or "\\" in path
            or any(part in ("", ".", "..") for part in path.split("/"))):
        raise ValueError("Unsafe top-level Git Workspace directory")
    return path

def blob_paths(root: Path) -> list[tuple[str, int]]:
    raw = git(root, ["ls-tree", "-r", "-l", "-z", "HEAD", "--"])
    result = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        meta, sep, p = item.partition(b"\t")
        fields = meta.split()
        if not sep or len(fields) < 4 or fields[1] != b"blob":
            raise ValueError("Unexpected git ls-tree blob record")
        size = int(fields[3]) if fields[3] != b"-" else 0
        path = p.decode("utf-8")
        result.append((path, size))
    if not result:
        raise ValueError("Git HEAD tree is empty")
    return result

def paths_with_literal_refs(root: Path, terms: list[str]) -> list[str]:
    if not terms:
        return []
    args = ["grep", "-l", "-I", "-F", "-z"]
    for term in terms:
        args.extend(["-e", term])
    raw = git(root, [*args, "HEAD", "--"], codes=(0, 1))
    result = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        text = item.decode("utf-8")
        if not text.startswith("HEAD:"):
            raise ValueError("Unexpected git grep ref (expected HEAD:path)")
        result.append(text[len("HEAD:"):])
    return sorted(set(result))

def classify(source: str, canonical: set[str], legacy: set[str]) -> str:
    if source.startswith((".github/", "Tools/", "Verification/")):
        return "CODE_OR_CI"
    if source in ("PROJECT-BOOTSTRAP.md", "PROJECT-STATE.json",
                  "README.md", "Workspaces/README.md"):
        return "ROOT_ENTRYPOINT_OR_STATE"
    if any(source.startswith(folder + "/") for folder in canonical):
        return "CANONICAL_WORKSPACE"
    if any(source.startswith(folder + "/") for folder in legacy):
        return "OTHER_LEGACY_WORKSPACE"
    if source.startswith("Workspaces/"):
        return "OTHER_WORKSPACE"
    if source.startswith("Optimization-Program/Control-Center/"):
        return "GOVERNANCE_ROUTING_OR_REPORT"
    return "OTHER_TRACKED_REFERENCE"

def analyze(root: Path) -> dict:
    root = root.resolve()
    routing = json.loads((root / ROUTING).read_text(encoding="utf-8"))
    if routing.get("schema") != EXPECTED_ROUTING:
        raise ValueError("Unexpected canonical routing version")
    roles = routing.get("workspaces", [])
    if not isinstance(roles, list):
        raise ValueError("Missing roles")
    legacy = [x for x in roles if x.get("role") == "COMPATIBILITY_LEGACY"]
    canonical = [x for x in roles if x.get("role") == "CANONICAL"]
    if not legacy or not canonical:
        raise ValueError("Both canonical and historical compatibility mappings are required")
    legacy_dirs = [route_path(x["git_dir"]) for x in legacy]
    canonical_dirs = [route_path(x["git_dir"]) for x in canonical]
    if (len(set(legacy_dirs)) != len(legacy_dirs)
        or len(set(canonical_dirs)) != len(canonical_dirs)
        or set(legacy_dirs) & set(canonical_dirs)):
        raise ValueError("Duplicate/overlapping routing")
    if any(x.get("future_accepted_current_pointer_location") not in canonical_dirs
           for x in legacy):
        raise ValueError("Legacy path has no valid canonical handoff")

    objects = blob_paths(root)
    text_matches = paths_with_literal_refs(root, legacy_dirs)
    by_dir: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for path, size in objects:
        for directory in legacy_dirs:
            if path.startswith(directory + "/"):
                by_dir[directory].append((path, size))
                break
    all_git_paths = {p for p, _ in objects}
    missing = [x for x in legacy_dirs if not by_dir[x]]
    if missing:
        raise ValueError("Grandfathered Workspace has no tracked Git files: " + repr(missing[:4]))

    inbound: dict[str, list[str]] = {p: [] for p in legacy_dirs}
    unreadable_but_matched: dict[str, list[str]] = {p: [] for p in legacy_dirs}
    for source in text_matches:
        if source not in all_git_paths:
            raise ValueError("Git grep found missing tracked file")
        content = git(root, ["show", "HEAD:" + source])
        if len(content) > MAX_TEXT_BLOB:
            for directory in legacy_dirs:
                unreadable_but_matched[directory].append(source)
            continue
        for directory in legacy_dirs:
            if directory.encode("utf-8") not in content:
                continue
            if source.startswith(directory + "/"):
                continue  # a path describing itself is not an inbound dependency
            inbound[directory].append(source)

    canonical_set = set(canonical_dirs)
    legacy_set = set(legacy_dirs)
    items = []
    for link in sorted(legacy, key=lambda x: x["git_dir"]):
        directory = link["git_dir"]
        rows = by_dir[directory]
        files = sorted({path for path, _ in rows})
        refs = sorted(set(inbound[directory]))
        grouped: dict[str, list[str]] = defaultdict(list)
        for source in refs:
            grouped[classify(source, canonical_set, legacy_set)].append(source)
        risk_rank = (
            "P0_REVIEW_CODE_OR_CANONICAL_INBOUND" if grouped["CODE_OR_CI"] or grouped["CANONICAL_WORKSPACE"]
            else "P1_REVIEW_OTHER_INBOUND" if refs or unreadable_but_matched[directory]
            else "P2_NO_EXACT_TRACKED_INBOUND_OBSERVED_NOT_DELETION_SAFE"
        )
        return_ref = link["future_accepted_current_pointer_location"]
        items.append({
            "family_id": link["family_id"],
            "legacy_workspace": directory,
            "canonical_future_work_target": return_ref,
            "tracked_git_file_count": len(files),
            "tracked_git_blob_bytes": sum(size for _, size in rows),
            "checkpoint_or_latest_document_count": sum(
                file.split("/")[-1] in ("CHECKPOINT.json", "LATEST.json", "STAGE7-LATEST.json")
                for file in files),
            "file_extensions": dict(sorted(Counter(
                Path(p).suffix.lower() or "<none>" for p in files).items())),
            "textual_inbound_reference_files": len(refs),
            "ref_sources_by_class": dict(sorted((kind, len(v)) for kind, v in grouped.items() if v)),
            "reference_examples": {
                kind: value[:8] for kind, value in sorted(grouped.items()) if value
            },
            "unclassified_oversized_git_grep_matches": len(set(unreadable_but_matched[directory])),
            "priority": risk_rank,
            "transfer_decision": "PRESERVE_HISTORICAL_BYTES__FUTURE_NEW_TASKS_ROUTE_TO_CANONICAL",
            "delete_decision": "PROHIBITED_NO_COMPLETE_IMMUTABLE_DEPENDENCY_AND_EXTERNAL_PROVIDER_PROOF",
        })
    output = {
        "schema": SCHEMA,
        "status": "COMPLETE_GIT_TEXT_INVENTORY__PHYSICAL_MIGRATION_NOT_AUTHORIZED",
        "source": "GIT_HEAD_TRACKED_BLOBS__EXACT_FULL_PATH_LITERAL_REFERENCES",
        "git_head": git(root, ["rev-parse", "HEAD"]).decode("ascii").strip(),
        "counts": {
            "legacy_workspaces": len(legacy_dirs),
            "canonical_target_workspaces": len(canonical_dirs),
            "legacy_tracked_files": sum(x["tracked_git_file_count"] for x in items),
            "legacy_tracked_blob_bytes": sum(x["tracked_git_blob_bytes"] for x in items),
            "legacy_with_any_text_inbound": sum(x["textual_inbound_reference_files"] > 0 for x in items),
            "legacy_with_code_or_canonical_inbound": sum(x["priority"].startswith("P0") for x in items),
            "legacy_with_unresolved_big_text_ref": sum(x["unclassified_oversized_git_grep_matches"] > 0 for x in items),
            "exact_textual_reference_file_edges": sum(x["textual_inbound_reference_files"] for x in items),
        },
        "limits": [
            "Git HEAD tracked blobs only; uncommitted files, Library, Drive, private app runtime and binary interiors are not searched",
            "Only exact full Workspaces/<name> path literals: relative paths, aliases or indirect imports may be missed",
            "Reference presence is not proof a job is actively executing; absence is NEVER proof safe to delete",
            "Historical source-owner CHECKPOINTS and accepted ZIP/TSV remain unchanged",
            "All compatibility folders retained; no reparenting or release promotion",
        ],
        "workspaces": items,
    }
    return output

def markdown(data: dict) -> str:
    out = [
        "# Legacy Workspace Dependency Inventory — read-only",
        "",
        "Git HEAD: `" + data["git_head"] + "`",
        "",
        "This is a Git tracked-text inventory, not an authorization to delete any folder.",
        "",
        "| Legacy workspace | Files | Exact inbound files | Priority | Canonical future target |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for x in data["workspaces"]:
        out.append("| `" + x["legacy_workspace"] + "` | " +
                   str(x["tracked_git_file_count"]) + " | " +
                   str(x["textual_inbound_reference_files"]) + " | " +
                   x["priority"] + " | `" + x["canonical_future_work_target"] + "` |")
    out.extend(["", "**All 20 historic folders stay unchanged. No Library/Drive or binary content attested.**", ""])
    return "\n".join(out)

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--github-summary", action="store_true")
    ap.add_argument("--expect-legacy", type=int, default=20)
    args=ap.parse_args(argv)
    try:
        data=analyze(args.repo_root)
        if args.expect_legacy and data["counts"]["legacy_workspaces"] != args.expect_legacy:
            raise ValueError("Legacy workspace count unexpectedly changed")
        if args.out_dir:
            output=args.out_dir.resolve()
            if output.is_relative_to(args.repo_root.resolve()):
                raise ValueError("Reports must live outside version-controlled checkout")
            output.mkdir(parents=True, exist_ok=True)
            (output/"LEGACY-WORKSPACE-DEPENDENCIES.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            (output/"LEGACY-WORKSPACE-DEPENDENCIES.md").write_text(markdown(data),encoding="utf-8")
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as fp:
                fp.write(markdown(data))
        print(json.dumps({
            "status":data["status"], "git_head":data["git_head"],
            "counts":data["counts"],
            "workspaces":[{
                "workspace":x["legacy_workspace"],"files":x["tracked_git_file_count"],
                "inbound":x["textual_inbound_reference_files"],
                "by_class":x["ref_sources_by_class"],"priority":x["priority"],
                "canonical":x["canonical_future_work_target"],
            } for x in data["workspaces"]],
        },ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError,UnicodeError) as e:
        print(json.dumps({"status":"HOLD_UNVERIFIED_LEGACY_DEPENDENCIES","error":type(e).__name__+": "+str(e)[:350]}))
        return 2

if __name__=="__main__":
    sys.exit(main())
