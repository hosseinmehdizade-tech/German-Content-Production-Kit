#!/usr/bin/env python3
"""Resolve exact personal ChatGPT Library upload destination BEFORE saving.

Pure preflight. Does NOT upload, intercept platform auto-saves, or claim persisted.
Use files.manage_library(upload, destination_path=...), then read back Library
record and stable library_file_id. A failed write must not fallback to root.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

BASE = "/Flasch kart/German-Content-Production-Kit/Content"
EXACT = {
    "optimization:OP01": "/Flasch kart/German-Content-Production-Kit/Optimization-Program/OP01",
    "optimization:OP02": "/Flasch kart/German-Content-Production-Kit/Optimization-Program/OP02",
    "optimization:shared": "/Flasch kart/German-Flashcards-Optimization",
    "app:runtime": "/Flasch kart/German-Flashcards-Pro",
    "sources:shared": "/Flasch kart/German-Flashcards-Reference-Library",
}
ROLES = {
    "current": "Current",
    "checkpoint": "Checkpoints",
    "report": "Reports",
    "release": "Releases",
    "history": "History",
    "import": "Root-Imports",
    "tool": "Tools",
    "test": "Tests",
}


def resolve_destination(owner, role, filename, registry):
    """Require explicit true owner, registered workstream and safe basename."""
    if not owner or not isinstance(owner, str):
        raise ValueError("owner missing: never choose generic folder")
    if role not in ROLES:
        raise ValueError("unknown artifact role")
    if (not isinstance(filename, str) or not filename or filename in {".", ".."}
            or filename.strip() != filename or "/" in filename or "\\" in filename
            or filename.startswith(".") or chr(0) in filename):
        raise ValueError("unsafe filename; basename required")
    if owner.startswith("content:"):
        slug = owner[len("content:"):]
        if not isinstance(registry, dict):
            raise ValueError("registry required for content owner")
        rows = registry.get("project_folders")
        if not isinstance(rows, list):
            raise ValueError("invalid registry project_folders")
        matches = [x for x in rows if isinstance(x, dict) and x.get("name") == slug]
        if len(matches) != 1:
            raise ValueError("unknown or ambiguous content owner")
        base = matches[0].get("library_path")
        if (not isinstance(base, str) or not base.startswith(BASE + "/")
                or base.rstrip("/").split("/")[-1] != slug or slug == "00-Unclassified"):
            raise ValueError("invalid registered content path")
    elif owner in EXACT:
        base = EXACT[owner]
    else:
        raise ValueError("unknown owner; root fallback prohibited")
    target = str(PurePosixPath(base) / ROLES[role] / filename)
    if not target.startswith("/Flasch kart/") or target == "/Flasch kart/" + filename:
        raise ValueError("forbidden unscoped destination")
    return {
        "status": "ROUTED_NOT_SAVED",
        "owner": owner,
        "role": role,
        "destination_path": target,
        "destination_folder": str(PurePosixPath(target).parent),
        "overwrite": False,
        "readback_required": ["path", "library_file_id"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True, help="Exact content:Menschen-A1 / optimization:OP02 / app:runtime etc.")
    parser.add_argument("--role", required=True, choices=sorted(ROLES))
    parser.add_argument("--source-file", type=Path, required=True)
    parser.add_argument("--registry", type=Path, help="Local copy of CONTENT-PROJECT-FOLDERS.json")
    args = parser.parse_args(argv)
    try:
        if not args.source_file.is_file():
            raise ValueError("source file not present")
        registry = json.loads(args.registry.read_text(encoding="utf-8")) if args.registry else None
        result = resolve_destination(args.owner, args.role, args.source_file.name, registry)
        result["source_sha256"] = hashlib.sha256(args.source_file.read_bytes()).hexdigest()
        result["source_size_bytes"] = args.source_file.stat().st_size
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
