#!/usr/bin/env python3
"""Read-only Control Center: identity catalog + exact Git-index status hints."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = "Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
STATE = "PROJECT-STATE.json"
SCHEMA = "gcpk-control-center-snapshot@1.0.0"


def git(*args, root=ROOT):
    return subprocess.run(["git", *args], cwd=root, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def git_index(root=ROOT):
    output = {}
    raw = git("ls-files", "--stage", "-z", "--", "Workspaces/", STATE,
              CATALOG, root=root)
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, name = item.split(b"\t", 1)
        mode, sha, stage = metadata.decode("ascii").split(" ")
        if stage != "0":
            raise ValueError("UNMERGED_GIT_INDEX")
        path = name.decode("utf-8")
        if path in output:
            raise ValueError("DUPLICATE_GIT_INDEX_PATH")
        output[path] = sha
    return output


def load_json_from_index(path, index, root=ROOT):
    if path not in index:
        return None
    try:
        obj = json.loads(git("show", ":" + path, root=root).decode("utf-8-sig"))
    except (subprocess.CalledProcessError, UnicodeError, json.JSONDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def tracked_dirs(index):
    return sorted({"/".join(p.split("/")[:2]) for p in index
                   if p.startswith("Workspaces/") and len(p.split("/")) >= 3})


def catalog_errors(cat):
    errors = []
    if cat.get("schema") != "gcpk-master-project-catalog@1.0.0":
        errors.append("CATALOG_SCHEMA")
    if cat.get("authority") != "IDENTITY_RELATION_CATALOG_ONLY__DO_NOT_STORE_OR_PROMOTE_STAGE_STATUS":
        errors.append("CATALOG_WRONGLY_AUTHORIZES_STAGE")
    families, workspaces, roots = (
        cat.get("families"), cat.get("workspaces"), cat.get("root_workstreams"))
    if not all(isinstance(x, list) for x in (families, workspaces, roots)):
        return ["CATALOG_COLLECTION_INVALID"]
    fids = [x.get("id") for x in families if isinstance(x, dict)]
    if len(fids) != len(families) or len(fids) != len(set(fids)) or any(
            not isinstance(x, str) or not x.startswith("family:") for x in fids):
        errors.append("FAMILY_IDENTITY_COLLISION")
    valid = set(fids)
    paths, ids = [], []
    for w in workspaces:
        if not isinstance(w, dict):
            errors.append("WORKSPACE_NOT_OBJECT")
            continue
        path, wid = w.get("git_dir"), w.get("id")
        paths.append(path)
        ids.append(wid)
        if (not isinstance(path, str) or len(path.split("/")) != 2
                or not path.startswith("Workspaces/")
                or wid != "workspace:" + path.split("/")[1]):
            errors.append("WORKSPACE_ID_MISMATCH")
        if w.get("parent_family_id") not in valid:
            errors.append("DANGLING_WORKSPACE_PARENT")
        if w.get("mapping_basis") != "EXPLICIT_REVIEWED_PARENT_ASSOCIATION__NOT_STAGE_AUTHORITY":
            errors.append("UNAUTHORIZED_WORKSPACE_MAPPING")
    if len(paths) != len(set(paths)) or len(ids) != len(set(ids)):
        errors.append("DUPLICATE_WORKSPACE_ID_OR_PATH")
    keys = []
    for w in roots:
        if not isinstance(w, dict):
            errors.append("ROOT_ENTRY_NOT_OBJECT")
            continue
        keys.append(w.get("key"))
        if w.get("parent_family_id") not in valid:
            errors.append("DANGLING_ROOT_PARENT")
    if len(keys) != len(set(keys)):
        errors.append("DUPLICATE_ROOT_WORKSTREAM_KEY")
    preservation = cat.get("preservation", {})
    for key in ("no_card_or_source_or_locked_edit",
                "does_not_assert_currentness_or_stage_acceptance",
                "unmapped_future_workspaces_are_reported_not_automatically_attached"):
        if preservation.get(key) is not True:
            errors.append("PRESERVATION_DISABLED:" + key)
    forbidden = ("status", "stage", "current_stage", "stage4_pass", "import_ready")
    if any(key in row for row in families + workspaces + roots
           if isinstance(row, dict) for key in forbidden):
        errors.append("VOLATILE_PROGRESS_STORED_IN_IDENTITY_CATALOG")
    return sorted(set(errors))


def short_text(data, *keys, limit=200):
    if not isinstance(data, dict):
        return None
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())[:limit]
    return None


def build(cat, index, root_state, pointers):
    errors = catalog_errors(cat)
    if errors:
        raise ValueError("INVALID_CATALOG:" + ",".join(errors))
    root_ws = root_state.get("workstreams")
    if not isinstance(root_ws, dict):
        raise ValueError("ROOT_WORKSTREAMS_NOT_OBJECT")
    observed = tracked_dirs(index)
    registered = {x["git_dir"]: x for x in cat["workspaces"]}
    rootmap = {x["key"]: x for x in cat["root_workstreams"]}
    issues = []
    for path in sorted(set(observed) - set(registered)):
        issues.append({"type": "UNMAPPED_NEW_WORKSPACE", "path": path})
    for path in sorted(set(registered) - set(observed)):
        issues.append({"type": "CATALOGED_WORKSPACE_NOT_TRACKED", "path": path})
    for key in sorted(set(root_ws) - set(rootmap)):
        issues.append({"type": "ROOT_WORKSTREAM_UNMAPPED", "path": key})
    for key in sorted(set(rootmap) - set(root_ws)):
        issues.append({"type": "CATALOG_ROOT_WORKSTREAM_NOT_PRESENT", "path": key})
    root_rows = []
    for key, info in sorted(root_ws.items()):
        if not isinstance(info, dict):
            issues.append({"type": "ROOT_WORKSTREAM_INVALID", "path": key})
            continue
        ck = info.get("checkpoint")
        ck = ck if isinstance(ck, str) else None
        root_rows.append({
            "key": key,
            "family_id": rootmap.get(key, {}).get("parent_family_id"),
            "summary_status_hint": short_text(info, "status"),
            "checkpoint_path": ck,
            "checkpoint_in_git": bool(ck and ck in index),
            "authority": "ROOT_SUMMARY_ONLY_MAY_BE_STALE",
        })
        if ck and ck not in index:
            issues.append({"type": "ROOT_CHECKPOINT_UNTRACKED", "path": ck})
    rows = []
    for directory in observed:
        ent = registered.get(directory)
        latest, checkpoint = directory + "/LATEST.json", directory + "/CHECKPOINT.json"
        lp, cp = pointers.get(latest), pointers.get(checkpoint)
        if latest in index and not isinstance(lp, dict):
            issues.append({"type": "INVALID_LATEST_JSON", "path": latest})
        if checkpoint in index and not isinstance(cp, dict):
            issues.append({"type": "INVALID_CHECKPOINT_JSON", "path": checkpoint})
        if isinstance(lp, dict):
            selected, obj, trust = latest, lp, "LATEST_INDEX_HINT__RECEIPT_NOT_CHECKED"
        elif isinstance(cp, dict):
            selected, obj, trust = checkpoint, cp, "CHECKPOINT_INDEX_HINT__RECEIPT_NOT_CHECKED"
        else:
            selected, obj, trust = None, None, "NO_PARSEABLE_POINTER_NO_PROGRESS_CLAIM"
            issues.append({"type": "NO_PARSEABLE_PRIMARY_POINTER", "path": directory})
        rows.append({
            "id": ent.get("id") if ent else None,
            "git_dir": directory,
            "parent_family_id": ent.get("parent_family_id") if ent else None,
            "kind": ent.get("kind") if ent else "UNMAPPED",
            "latest_index_blob_sha": index.get(latest),
            "checkpoint_index_blob_sha": index.get(checkpoint),
            "display_pointer": selected,
            "reported_status_hint": short_text(
                obj, "status", "current_stage", "latest_completed_milestone",
                "latest_milestone", "stage1", limit=160),
            "next_action_hint": short_text(obj, "next_action", limit=210),
            "authority": trust,
            "stage_pass_or_release_attested_by_control_center": False,
        })
    family_rows = []
    for fam in cat["families"]:
        fid = fam["id"]
        descendants = [r for r in rows if r["parent_family_id"] == fid]
        parent_roots = [r for r in root_rows if r["family_id"] == fid]
        family_rows.append({
            "id": fid, "name": fam["name"], "library_path": fam["library_path"],
            "library_proof": "CATALOGED_SNAPSHOT_NOT_LIVE_LIBRARY_SCAN",
            "git_workspace_count": len(descendants),
            "parseable_pointer_count": sum(x["display_pointer"] is not None for x in descendants),
            "root_summary_entries": len(parent_roots),
            "independent_semantic_stage_proof": "NOT_VERIFIED_BY_THIS_TOOL",
        })
    return {
        "schema": SCHEMA,
        "authority": "GIT_INDEX_METADATA_ONLY__NO_PASS_PROMOTION",
        "source": {"catalog_git_blob_sha": index.get(CATALOG),
                   "root_state_git_blob_sha": index.get(STATE),
                   "git_index_not_working_tree": True,
                   "newer_user_artifact_not_checked": True,
                   "library_list_is_snapshotted_not_live": True},
        "counts": {
            "families": len(family_rows),
            "git_workspaces": len(observed),
            "mapped_workspaces": sum(x["id"] is not None for x in rows),
            "root_workstreams": len(root_ws),
            "missing_or_unparsed_primary_pointers": sum(x["display_pointer"] is None for x in rows),
            "untracked_root_checkpoint_paths": sum(x["type"] == "ROOT_CHECKPOINT_UNTRACKED" for x in issues),
            "stage4_stage5_stage6_stage7_certificates_generated": 0,
        },
        "issues": sorted(issues, key=lambda x: (x["type"], x["path"])),
        "families": family_rows, "workspaces": rows, "root_workstreams": root_rows,
    }


def dashboard_md(snapshot):
    count = snapshot["counts"]
    lines = [
        "# German Content Production — Project Control Center",
        "",
        "**READ-ONLY GIT METADATA. This is not content/Stage4–7 acceptance.**",
        "Newer user-supplied artifacts and verified portable sources may outrank Git.",
        "",
        f"Families cataloged: **{count['families']}**; Git workspace directories: **{count['git_workspaces']}**; mapped: **{count['mapped_workspaces']}**.",
        f"Central root workstreams: **{count['root_workstreams']}**; absent/unparseable workspace pointers: **{count['missing_or_unparsed_primary_pointers']}**.",
        "",
        "## Family navigation",
        "",
        "| Family | Git workspace directories | Parseable pointers | Central root entries |",
        "|---|---:|---:|---:|",
    ]
    for fam in snapshot["families"]:
        lines.append(f"| {fam['name']} | {fam['git_workspace_count']} | {fam['parseable_pointer_count']} | {fam['root_summary_entries']} |")
    lines.extend(["", "## Workspace status hints — NOT verified Stage PASS", "",
                  "| Workspace | Parent ID | Reported status | Display source |",
                  "|---|---|---|---|"])
    for ws in snapshot["workspaces"]:
        def esc(s):
            return str(s or "—").replace("|", "\\|").replace("\n", " ")
        lines.append("| " + " | ".join(esc(x) for x in (
            ws["git_dir"], ws["parent_family_id"],
            (ws["reported_status_hint"] or "")[:95], ws["display_pointer"])) + " |")
    lines.extend(["", "## Navigation and metadata issues", "",
                  "| Type | Path |",
                  "|---|---|"])
    for issue in snapshot["issues"]:
        lines.append(f"| {issue['type']} | {issue['path']} |")
    lines.extend(["", "Next: inspect each local LATEST, then its exact receipt/sha, portable source authority, independent QA and current runtime if needed.",
                  "Do not repair source or LOCKED artifacts from dashboard metadata.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--github-summary", action="store_true")
    args = parser.parse_args()
    try:
        index = git_index()
        cat = load_json_from_index(CATALOG, index)
        state = load_json_from_index(STATE, index)
        if not isinstance(cat, dict) or not isinstance(state, dict):
            raise ValueError("MISSING_OR_INVALID_CATALOG_OR_ROOT_STATE")
        pointers = {}
        for directory in tracked_dirs(index):
            for part in ("LATEST.json", "CHECKPOINT.json"):
                path = directory + "/" + part
                if path in index:
                    pointers[path] = load_json_from_index(path, index)
        snapshot = build(cat, index, state, pointers)
        report = dashboard_md(snapshot)
        print(json.dumps({"schema": SCHEMA, "status": "CATALOG_INTEGRITY_OK_NOT_CONTENT_QA",
                          "counts": snapshot["counts"], "issue_count": len(snapshot["issues"])},
                         ensure_ascii=False, indent=2))
        if args.output_dir:
            out = args.output_dir.resolve()
            protected = ("Workspaces", "Data", "Prompt", "01-App", "06-Content")
            if out == ROOT.resolve() or any(
                out == (ROOT / x).resolve() or (ROOT / x).resolve() in out.parents
                for x in protected):
                raise ValueError("UNSAFE_OUTPUT_ALIASES_CONTENT_OR_SOURCE")
            out.mkdir(parents=True, exist_ok=True)
            (out / "CONTROL-CENTER.json").write_text(
                json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (out / "CONTROL-CENTER.md").write_text(report, encoding="utf-8")
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
                f.write(report)
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"schema": SCHEMA, "status": "BLOCKED", "error": str(exc),
                          "stage_certification": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
