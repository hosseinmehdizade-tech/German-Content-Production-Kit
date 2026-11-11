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
    require(stage4.is_file() and not stage4.is_symlink(),
            "MISSING_OR_UNSAFE_STAGE4_RECEIPT")
    stage4_digest = digest(stage4)  # Require actual immutable bytes, not a filename.

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
    from build_quality_gated_lexical_candidate_v1 import select_roles
    roles = select_roles(source)
    tsv_digest = digest(roles["direct-import-tsv"])
    # An unchanged accepted v1.8 import is a recovery baseline, NOT a NEW
    # content delta. Do not generate another 292-card candidate ZIP from it.
    accepted_import = latest.get("final_content_only_v18", {}).get("source_tsv_sha256")
    require(isinstance(accepted_import, str) and
            re.fullmatch(r"[0-9a-f]{64}", accepted_import),
            "ACCEPTED_CURRENT_IMPORT_TSV_NOT_PINNED")
    require(tsv_digest != accepted_import,
            "NO_NEW_IMPORT_TSV_DELTA_FROM_ACCEPTED_CURRENT")
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

def verify_postbuild_snapshot(root: Path, source: Path, output: Path,
                              receipt: Path, report: dict) -> str:
    """One last owner-side byte check AFTER the central Stage5 subprocess.

    Central QA checks the ZIP and proofs during packaging; the owner must not
    claim success if the output, format receipt, source roles or route then
    change before the final source-owned handoff. No file is edited here.
    """
    require(isinstance(report, dict), "POSTBUILD_REPORT_NOT_OBJECT")
    require(output.is_file() and not output.is_symlink(),
            "POSTBUILD_ZIP_MISSING_OR_UNSAFE")
    expected = report.get("exact_governed_output_zip_sha256")
    require(isinstance(expected, str) and re.fullmatch(r"[a-f0-9]{64}", expected),
            "POSTBUILD_ZIP_SHA_UNATTESTED")
    require(digest(output) == expected, "POSTBUILD_ZIP_CHANGED_AFTER_CENTRAL_QA")

    format_build = report.get("governed_format_build")
    require(isinstance(format_build, dict)
            and format_build.get("status") ==
            "PASS_GOVERNED_STAGE5_FORMAT_AND_BYTE_PARITY_ONLY"
            and format_build.get("output_zip_sha256") == expected,
            "POSTBUILD_CENTRAL_RECEIPT_NOT_BOUND")
    format_receipt = document(receipt)
    require(format_receipt == format_build,
            "POSTBUILD_FORMAT_RECEIPT_CHANGED_OR_FORGED")

    sys.path.insert(0, str(root / "Tools"))
    from build_quality_gated_lexical_candidate_v1 import select_roles
    role_paths = select_roles(source)
    actual = {name: digest(path) for name, path in role_paths.items()}
    require(report.get("exact_all_source_roles_sha256") == actual
            and format_receipt.get("source_role_sha256") == actual,
            "POSTBUILD_SOURCE_ROLE_BYTES_MOVED")
    family_authority = report.get("family_authority")
    require(isinstance(family_authority, dict)
            and family_authority.get("family_id") == FAMILY
            and family_authority.get("route_file_sha256") ==
            digest(root / ROUTES),
            "POSTBUILD_CANONICAL_ROUTER_MOVED")
    return expected


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
        sys.path.insert(0, str(ROOT / "Tools"))
        from build_quality_gated_lexical_candidate_v1 import select_roles
        require(digest(select_roles(args.source_dir)["direct-import-tsv"]) ==
                proof["candidate_tsv_sha256"], "CANDIDATE_TSV_MOVED_DURING_BUILD")
        require(digest(args.stage4_receipt) == proof["stage4_receipt_sha256"],
                "STAGE4_RECEIPT_MOVED_DURING_BUILD")
        require(digest(args.cross_tile_review) == proof["cross_tile_review_sha256"],
                "CROSS_TILE_REVIEW_MOVED_DURING_BUILD")
        verified_output_sha256 = verify_postbuild_snapshot(
            ROOT, args.source_dir, args.output_zip, args.receipt, report)
        print(json.dumps({"status": "OWNER_NATIVE_STAGE5_CANDIDATE_PASS_NOT_ADOPTED",
                          "family_id": FAMILY,
                          "candidate_sha256": verified_output_sha256,
                          "stage6": "NOT_RUN", "stage7": "NOT_FINAL"}))
        return 0
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        print("VMP_OWNER_STAGE5_BLOCKED:" + str(error), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
