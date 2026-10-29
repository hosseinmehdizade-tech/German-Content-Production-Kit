#!/usr/bin/env python3
"""Generate/check a compact ROUTING-ONLY resume index. Never copies stage status.

The huge PROJECT-STATE.json may lag workstream-local LATEST; this index is a
directory, NOT authority. Use exact LATEST + cited milestone receipt and newer
portable artifact to decide currentness.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "PROJECT-STATE.json"
OUTPUT = ROOT / "Optimization-Program" / "RESUME-ROUTES.json"


def tracked_files() -> set[str]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return set(filter(None, raw.decode("utf-8").split("\0")))


def route_pointer(path: object, tracked: set[str]) -> dict | None:
    if not isinstance(path, str) or not path.strip():
        return None
    if path.startswith("/") or "\\" in path or ".." in Path(path).parts:
        raise ValueError("invalid source route path: " + path)
    return {"path": path, "tracked": path in tracked}


def build_routes() -> dict:
    state = json.loads(STATE.read_text(encoding="utf-8-sig"))
    workstreams = state.get("workstreams")
    if not isinstance(workstreams, dict):
        raise ValueError("workstreams must be an object")
    tracked = tracked_files()
    routes = []
    explicit_latest = set()
    for key, values in sorted(workstreams.items()):
        if not isinstance(values, dict):
            raise ValueError("workstream entry must be an object: " + key)
        checkpoint = values.get("checkpoint")
        latest = values.get("latest") or values.get("latest_path")
        # Derive a navigation hint, not an assertion of stage/progress.
        if not latest and isinstance(checkpoint, str):
            suggestion = str(Path(checkpoint).parent / "LATEST.json").replace("\\", "/")
            if suggestion in tracked:
                latest = suggestion
        src = values.get("source_manifest")
        route = {
            "key": key,
            "latest": route_pointer(latest, tracked),
            "checkpoint": route_pointer(checkpoint, tracked),
            "source_manifest": route_pointer(src, tracked),
        }
        if route["latest"]:
            explicit_latest.add(route["latest"]["path"])
        routes.append(route)

    # Top-level LATEST routes cover newer workstreams absent from old global state.
    # Detailed per-lesson LATEST filenames are discovered inside their parent only
    # when that lesson is requested: avoids an enormous repetitive index.
    extra_latest = sorted(
        p for p in tracked
        if p.startswith("Workspaces/") and p.endswith("/LATEST.json")
        and len(p.split("/")) == 3 and p not in explicit_latest
    )
    missing = sorted({
        obj["path"]
        for route in routes
        for name in ("latest", "checkpoint", "source_manifest")
        if (obj := route[name]) is not None and not obj["tracked"]
    })
    return {
        "schema": "gfp-optimization-resume-routes@1",
        "role": "NAVIGATION_ONLY_NEVER_PROGRESS_OR_QUALITY_AUTHORITY",
        "sources": {
            "global_workstreams": "PROJECT-STATE.json#workstreams",
            "extra_primary_latest": "tracked Workspaces/*/LATEST.json",
            "active_prompt_pointer": "Prompt/ACTIVE-PROMPT.txt",
            "app_current_pointer": "German-Flashcards-Pro/RUNTIME-AUTHORITY-PIN.json",
            "workstream_rule": "WORKSTREAM-RESUME-CURRENTNESS-POLICY.json"
        },
        "rule": "Resolve newer explicit user artifact first; then exact portable authority; verify local LATEST plus receipt/hash, then CHECKPOINT; global state is a last summary. A missing Git route does not imply source loss.",
        "routes": routes,
        "unmapped_primary_latest": extra_latest,
        "unresolved_git_paths": missing,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the tracked route inventory changed")
    args = parser.parse_args()
    expected = json.dumps(build_routes(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
        if actual != expected:
            print("STALE_RESUME_ROUTES: regenerate with python Tools/build_resume_routes.py")
            return 1
        print("PASS: resume routes match tracked paths; progress authority is NOT asserted")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected, encoding="utf-8")
        print("UPDATED: " + str(OUTPUT.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
