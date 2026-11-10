#!/usr/bin/env python3
"""250 Verben canonical OWNER entrypoint for a NEW, non-final lexical Stage5 candidate.

This binds the source-owned curated CURRENT to the existing CENTRAL quality
launcher. It never revises the accepted v1.8 ZIP, card contents or LATEST, and
it does not authenticate remote Git/Library publication or Stage6/Stage7.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWNER = "Workspaces/250-verben-mit-praepositionen-lexical-enrichment-v1"
FAMILY = "family:250-verben-mit-praepositionen"
ROUTES = "Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def document(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise ValueError("MISSING_OR_UNSAFE_EVIDENCE:" + str(path))
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("EVIDENCE_NOT_OBJECT:" + str(path))
    return value

def require(value: bool, code: str) -> None:
    if not value:
        raise ValueError(code)

def preflight(root: Path, source: Path, output: Path, receipt: Path,
              policy_report: Path, stage4: Path, review_path: Path) -> dict:
    root = root.resolve()
    require(source.is_dir() and not source.is_symlink(), "INVALID_SOURCE_ROLE_DIRECTORY")
    latest_path = root / OWNER / "LATEST.json"
    latest = document(latest_path)
    routes = document(root / ROUTES)
    review = document(review_path)
    stage4_digest = digest(stage4)  # Require the actual Stage4 bytes, not a filename.

    require(latest.get("workstream") == OWNER.removeprefix("Workspaces/"),
            "SOURCE_OWNER_LATEST_MISMATCH")
    require("FINAL_USER_ACCEPTED_CONTENT_ONLY_V1_8" in latest.get("status", ""),
            "CURRENT_OWNER_CONTENT_STATUS_UNATTESTED")
    parent = latest.get("final_content_only_v18", {}).get("sha256")
    require(isinstance(parent, str) and re.fullmatch(r"[0-9a-f]{64}", parent),
            "CURATED_PARENT_NOT_PINNED")
    families = [x for x in routes.get("families", [])
                if x.get("family_id") == FAMILY]
    require(len(families) == 1, "CANONICAL_FAMILY_NOT_UNIQUE")
    family = families[0]
    require(family.get("canonical_git_workspace") == OWNER and
            family.get("active_content_sha256") == parent and
            family.get("route_state", "").startswith(
                "CANONICAL_ROUTED__USER_ACCEPTED_CURATED_OWNER_PIN"),
            "STALE_OR_WRONG_CANONICAL_OWNER_CURRENT")
    require(review.get("schema") == "gcpk-lexical-cross-tile-acceptance@1.0.0"
            and review.get("workstream") in (OWNER, OWNER.removeprefix("Workspaces/"))
            and review.get("curated_current_parent_sha256") == parent,
            "CROSS_TILE_REVIEW_NOT_FOR_CURRENT_OWNER")
    require(review.get("stage4_receipt_sha256") == stage4_digest,
            "STAGE4_RECEIPT_BYTES_NOT_REVIEWED")

    sys.path.insert(0, str(root / "Tools"))
    from build_governed_clean_delivery_v1 import select_roles
    roles = select_roles(source)
    tsv_digest = digest(roles["direct-import-tsv"])
    require(review.get("source_tsv_sha256") == tsv_digest,
            "DIRECT_IMPORT_TSV_NOT_EXACT_REVIEWED_SOURCE")

    paths = (output, receipt, policy_report)
    require(len({p.resolve() for p in paths}) == 3, "OUTPUT_RECEIPT_PATH_COLLISION")
    for path in paths:
        require(not path.exists() and not path.is_symlink(),
                "EXISTING_OUTPUT_OR_RECEIPT")
        require(path.parent.is_dir() and not path.parent.is_symlink(),
                "INVALID_OUTPUT_PARENT")
        require(not path.resolve().is_relative_to(root) and
                not path.resolve().is_relative_to(source.resolve()),
                "PUBLIC_GIT_OR_SOURCE_OUTPUT_FORBIDDEN")

    return {
        "family_id": FAMILY, "canonical_owner": OWNER,
        "curated_current_parent_sha256": parent,
        "latest_source_sha256": digest(latest_path),
        "candidate_tsv_sha256": tsv_digest,
        "stage4_receipt_sha256": stage4_digest,
        "cross_tile_review_sha256": digest(review_path),
        "status": "OWNER_AND_SOURCE_PREFLIGHT_PASS_NOT_STAGE5_OR_ADOPTED"
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("output_zip", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--policy-report", type=Path, required=True)
    parser.add_argument("--stage4-receipt", type=Path, required=True)
    parser.add_argument("--cross-tile-review", type=Path, required=True)
    args = parser.parse_args()
    try:
        proof = preflight(ROOT, args.source_dir, args.output_zip, args.receipt,
                          args.policy_report, args.stage4_receipt, args.cross_tile_review)
        command = [sys.executable, "-B",
                   str(ROOT / "Tools" / "build_quality_gated_lexical_candidate_v1.py"),
                   str(args.source_dir), str(args.output_zip),
                   "--family-id", FAMILY,
                   "--receipt", str(args.receipt),
                   "--policy-report", str(args.policy_report),
                   "--stage4-receipt", str(args.stage4_receipt),
                   "--cross-tile-review", str(args.cross_tile_review)]
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            return result.returncode
        report = document(args.policy_report)
        require(report.get("status") ==
                "PASS_STAGE5_CANDIDATE_WITH_EXACT_SOURCE_STAGE4_AND_RULE_COVERAGE",
                "CENTRAL_QUALITY_REPORT_NOT_PASS")
        require(report.get("family_authority", {}).get("family_id") == FAMILY,
                "CENTRAL_QUALITY_FAMILY_MISMATCH")
        require(digest(ROOT / OWNER / "LATEST.json") == proof["latest_source_sha256"],
                "CURRENT_OWNER_MOVED_DURING_BUILD")
        require(digest(args.source_dir / next(
                p.name for p in args.source_dir.iterdir()
                if p.is_file() and "import" in p.name.lower() and p.suffix == ".tsv"))
                == proof["candidate_tsv_sha256"],
                "CANDIDATE_TSV_MOVED_DURING_BUILD")
        print(json.dumps({"status": "OWNER_NATIVE_STAGE5_CANDIDATE_PASS_NOT_ADOPTED",
                          "family_id": FAMILY,
                          "candidate_sha256": digest(args.output_zip),
                          "stage6": "NOT_RUN", "stage7": "NOT_FINAL"}))
        return 0
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        print("VMP_OWNER_STAGE5_BLOCKED:" + str(error), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
