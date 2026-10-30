#!/usr/bin/env python3
"""OP-01 NONACTIVE GitHub main governance policy-shape preflight.

READ ONLY. Never writes to GitHub, authenticates the owner, grants writer
scopes, approves a candidate CURRENT or validates Stage4/5/6/7.
A matching protection bit alone is explicitly not trusted.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

REPO = "hosseinmehdizade-tech/German-Content-Production-Kit"
API = "https://api.github.com/repos/" + REPO
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
SCHEMA = "gcpk-op01-main-governance-shape-readonly@1"


def evaluate(repo, branch, rulesets, details, *, live=False):
    blockers = []
    findings = []
    result = {
        "schema": SCHEMA,
        "scope": "PUBLIC_CONTENT_KIT_MAIN_POLICY_STRUCTURE_ONLY",
        "status": "BLOCKED_GOVERNANCE_UNVERIFIED",
        "source": "GITHUB_API_LIVE_READ_ONLY" if live else "CALLER_SUPPLIED_UNTRUSTED_SNAPSHOT",
        "current_git_head": None,
        "active_ruleset_ids_examined": [],
        "evaluate_ruleset_ids": [],
        "blockers": blockers,
        "findings": findings,
        "branch_protection_bit_verified": False,
        "pr_only_enforcement_structurally_seen": False,
        "non_fast_forward_and_deletion_rules_seen": False,
        "required_check_source_authentication_verified": False,
        "independent_current_issuer_authenticated": False,
        "trusted_base_workflow_origin_verified": False,
        "branch_protection_is_atomic_with_write": False,
        "op01_writer_granted": False,
        "stage4_semantic_pass": False,
        "stage5_allowed": False,
        "stage6_pass": False,
        "stage7_release_final": False,
        "github_settings_changed": False,
        "performed_writes": False,
    }
    try:
        if not isinstance(repo, dict) or repo.get("full_name") != REPO or repo.get("private") is not False or repo.get("default_branch") != "main":
            blockers.append("REPOSITORY_IDENTITY_OR_VISIBILITY_UNVERIFIED")
        if not isinstance(branch, dict) or branch.get("name") != "main":
            blockers.append("BRANCH_IDENTITY_UNVERIFIED")
        else:
            sha = branch.get("commit", {}).get("sha") if isinstance(branch.get("commit"), dict) else None
            if not isinstance(sha, str) or not HEX40.fullmatch(sha):
                blockers.append("BRANCH_HEAD_SHA_MALFORMED")
            else:
                result["current_git_head"] = sha
            if branch.get("protected") is not True:
                blockers.append("MAIN_UNPROTECTED")
            else:
                result["branch_protection_bit_verified"] = live
                findings.append("MAIN_PROTECTED_BIT_REPORTED_NOT_A_COMPLETE_TRUST_PROOF")
        if not isinstance(rulesets, list) or not isinstance(details, dict):
            blockers.append("RULESET_INVENTORY_UNVERIFIABLE")
        else:
            candidates = []
            ids = set()
            for item in rulesets:
                if not isinstance(item, dict) or type(item.get("id")) is not int or item["id"] <= 0 or item["id"] in ids:
                    blockers.append("RULESET_INDEX_MALFORMED")
                    continue
                ident = item["id"]
                ids.add(ident)
                if item.get("enforcement") == "evaluate":
                    result["evaluate_ruleset_ids"].append(ident)
                elif item.get("enforcement") in ("active", "enabled"):
                    if item.get("target") not in ("branch", None):
                        continue
                    candidates.append(ident)
            for ident in candidates:
                result["active_ruleset_ids_examined"].append(ident)
                obj = details.get(str(ident))
                if not isinstance(obj, dict) or obj.get("id") != ident or obj.get("target") != "branch":
                    blockers.append("ACTIVE_RULESET_DETAILS_MISSING_OR_MISMATCHED:" + str(ident))
                    continue
                if obj.get("enforcement") not in ("active", "enabled"):
                    blockers.append("ACTIVE_RULESET_DETAILS_NOT_ACTIVE:" + str(ident))
                    continue
                cond = obj.get("conditions")
                names = cond.get("ref_name") if isinstance(cond, dict) else None
                include = names.get("include") if isinstance(names, dict) else None
                exclude = names.get("exclude") if isinstance(names, dict) else None
                # Conservative: wildcard/regex/negative conditions require owner review.
                if not isinstance(include, list) or "refs/heads/main" not in include or not isinstance(exclude, list) or exclude:
                    blockers.append("MAIN_RULESET_CONDITIONS_NOT_EXACT:" + str(ident))
                    continue
                bypass = obj.get("bypass_actors")
                if bypass is None:
                    blockers.append("BYPASS_INVENTORY_UNVERIFIABLE:" + str(ident))
                    continue
                if not isinstance(bypass, list) or bypass:
                    blockers.append("MAIN_RULESET_HAS_BYPASS:" + str(ident))
                    continue
                rules = obj.get("rules")
                if not isinstance(rules, list) or not all(isinstance(q, dict) and isinstance(q.get("type"), str) for q in rules):
                    blockers.append("RULES_UNVERIFIABLE:" + str(ident))
                    continue
                types = {q["type"] for q in rules}
                needed = {"pull_request", "required_status_checks", "non_fast_forward", "deletion"}
                absent = sorted(needed - types)
                if absent:
                    blockers.append("REQUIRED_RULE_TYPES_MISSING:" + str(ident) + ":" + ",".join(absent))
                    continue
                statuses = [q.get("parameters") for q in rules if q["type"] == "required_status_checks"]
                if len(statuses) != 1 or not isinstance(statuses[0], dict):
                    blockers.append("REQUIRED_STATUS_CONFIGURATION_INVALID:" + str(ident))
                    continue
                checks = statuses[0].get("required_status_checks")
                if not isinstance(checks, list) or len(checks) < 1 or any(
                    not isinstance(check, dict)
                    or not isinstance(check.get("context"), str)
                    or not check["context"].strip()
                    or type(check.get("integration_id")) is not int
                    or check["integration_id"] <= 0
                    for check in checks
                ):
                    blockers.append("STATUS_SOURCE_UNPINNED_OR_MALFORMED:" + str(ident))
                    continue
                # A pinned GitHub Actions integration id is NOT sufficient when
                # untrusted pull_request YAML can spoof the same green job.
                result["pr_only_enforcement_structurally_seen"] = True
                result["non_fast_forward_and_deletion_rules_seen"] = True
                findings.append("STRUCTURAL_RULESET_CANDIDATE:" + str(ident))
            if not candidates:
                blockers.append("NO_ACTIVE_MAIN_BRANCH_RULESET")
            if candidates and not result["pr_only_enforcement_structurally_seen"]:
                blockers.append("NO_COMPLETE_STRICT_MAIN_RULESET_PROVEN")
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError):
        blockers.append("UNEXPECTED_GOVERNANCE_DATA_SHAPE")
    # Even complete shape is not independent issuer/source verification.
    if result["pr_only_enforcement_structurally_seen"] and not blockers:
        result["status"] = "PASS_SCOPED_RULESET_SHAPE_ONLY_NOT_TRUSTED"
        findings.append("TRUSTED_CHECK_ORIGIN_INDEPENDENT_ISSUER_STILL_NOT_PROVEN")
    else:
        result["status"] = "BLOCKED_GOVERNANCE_READINESS"
    if not live:
        result["branch_protection_bit_verified"] = False
        findings.append("CALLER_SUPPLIED_GITHUB_JSON_IS_NOT_AUTHENTICATED_EVIDENCE")
    result["blockers"] = sorted(set(blockers))
    return result



def assess_check_origin_snapshot(checks_payload, *, pr_head_sha: str,
                                 expected_name: str, expected_app_id: int,
                                 changed_paths) -> dict:
    """Inspect *untrusted* check-run metadata; NEVER certify an issuer.

    Real PR #33 demonstrated that replacing the workflow definition in the
    PR head could emit the same green job name from GitHub Actions app 15368.
    Even an exact check name, GitHub App integration ID, and head SHA do not
    establish protected/base-defined check implementation.
    """
    blocks = []
    findings = []
    result = {
        "schema": "gcpk-op01-pr-check-origin-snapshot@1",
        "status": "BLOCKED_CHECK_ORIGIN_NOT_AUTHENTICATED",
        "source": "CALLER_SUPPLIED_CHECK_RUN_SNAPSHOT_NOT_AUTHENTICATED",
        "blockers": blocks,
        "findings": findings,
        "matching_check_count": 0,
        "matching_check_success_observed": False,
        "expected_app_id_matched": False,
        "pr_head_workflow_mutation_observed": False,
        "check_definition_protected_base_verified": False,
        "trusted_check_origin_verified": False,
        "independent_issuer_authenticated": False,
        "writer_granted": False,
        "stage4_semantic_pass": False,
        "release_final": False,
        "performed_writes": False,
    }
    if (not isinstance(pr_head_sha, str) or not HEX40.fullmatch(pr_head_sha)
            or not isinstance(expected_name, str) or not expected_name.strip()
            or type(expected_app_id) is not int or expected_app_id <= 0):
        blocks.append("INVALID_CHECK_IDENTITY_ARGUMENTS")
    if (not isinstance(changed_paths, list)
            or not all(isinstance(x, str) and x and len(x) < 1025
                       for x in changed_paths)
            or len(changed_paths) != len(set(changed_paths))):
        blocks.append("PR_CHANGED_FILE_INVENTORY_UNVERIFIED")
    else:
        if any(p.startswith(".github/workflows/") for p in changed_paths):
            result["pr_head_workflow_mutation_observed"] = True
            blocks.append("PR_HEAD_MODIFIED_WORKFLOW_DEFINITION")
    if (not isinstance(checks_payload, dict)
            or type(checks_payload.get("total_count")) is not int
            or not isinstance(checks_payload.get("check_runs"), list)):
        blocks.append("CHECK_RUN_RESPONSE_INVALID")
    else:
        checks = checks_payload["check_runs"]
        if (checks_payload["total_count"] != len(checks) or len(checks) > 100):
            blocks.append("CHECK_RUN_PAGINATION_UNVERIFIED")
        matches = [x for x in checks if isinstance(x, dict)
                   and x.get("name") == expected_name]
        result["matching_check_count"] = len(matches)
        if len(matches) != 1:
            blocks.append("REQUIRED_CHECK_MISSING_OR_DUPLICATED")
        else:
            check = matches[0]
            app = check.get("app")
            if check.get("head_sha") != pr_head_sha:
                blocks.append("CHECK_RUN_WRONG_PR_HEAD_SHA")
            if (check.get("status") != "completed"
                    or check.get("conclusion") != "success"):
                blocks.append("CHECK_RUN_NOT_COMPLETED_SUCCESSFULLY")
            elif check.get("head_sha") == pr_head_sha:
                result["matching_check_success_observed"] = True
            if not isinstance(app, dict) or type(app.get("id")) is not int:
                blocks.append("CHECK_SOURCE_APP_UNVERIFIABLE")
            else:
                result["expected_app_id_matched"] = (
                    app["id"] == expected_app_id)
                if not result["expected_app_id_matched"]:
                    blocks.append("CHECK_SOURCE_APP_ID_DRIFT")
                if app.get("slug") == "github-actions":
                    findings.append(
                        "GITHUB_ACTIONS_INTEGRATION_ID_CANNOT_PROVE_BASE_DEFINED_CHECK")
                    # PR #33 proved this specific weakness in the real repo.
                    if app.get("id") == 15368:
                        findings.append(
                            "REAL_PR33_SAME_GITHUB_ACTIONS_APP_EMITTED_BYPASSED_GREEN_JOB")
                elif not isinstance(app.get("slug"), str):
                    blocks.append("CHECK_SOURCE_APP_SLUG_UNVERIFIABLE")
    if result["matching_check_success_observed"]:
        findings.append("GREEN_CHECK_ONLY_NOT_ISSUER_OR_POLICY_CERTIFICATION")
    # No reachable PASS/authority state: the snapshot itself comes from an
    # untrusted PR/API view and cannot prove independent check definition.
    result["blockers"] = sorted(set(blocks))
    result["findings"] = sorted(set(findings))
    return result


def fetch_live():
    def get(path):
        req = urllib.request.Request(API + path, headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "gcpk-op01-governance-readonly"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("OVERSIZED_GITHUB_API_RESPONSE")
        return json.loads(raw)
    repo = get("")
    branch = get("/branches/main")
    rulesets = get("/rulesets?includes_parents=true&per_page=100&page=1")
    # Paging is fail-closed: do not certify if later pages could be missing.
    if not isinstance(rulesets, list) or len(rulesets) == 100:
        raise ValueError("RULESET_INVENTORY_PAGINATION_UNVERIFIED")
    details = {}
    for row in rulesets:
        if isinstance(row, dict) and row.get("enforcement") in ("active", "enabled"):
            ident = row.get("id")
            if type(ident) is not int or ident <= 0:
                raise ValueError("ACTIVE_RULESET_ID_INVALID")
            details[str(ident)] = get("/rulesets/" + str(ident))
    return repo, branch, rulesets, details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true",
                      help="Only public GitHub REST GET; never a privileged action")
    mode.add_argument("--snapshot", type=Path,
                      help="Untrusted offline JSON with repo/branch/rulesets/details")
    args = parser.parse_args()
    try:
        if args.live:
            data = fetch_live()
        else:
            snap = json.loads(args.snapshot.read_text(encoding="utf-8"))
            data = tuple(snap[k] for k in ("repo", "branch", "rulesets", "details"))
        out = evaluate(*data, live=args.live)
    except (OSError, ValueError, TypeError, KeyError, urllib.error.URLError, RecursionError) as exc:
        out = evaluate({}, {}, [], {}, live=False)
        out["status"] = "BLOCKED_GOVERNANCE_READ_FAILURE"
        out["blockers"].append("READ_FAILURE:" + type(exc).__name__)
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    # Even structural shape PASS isn't authority to write, but allow separate
    # policy-shape diagnostics to exit 0. Never call this a production gate.
    return 0 if out["status"] == "PASS_SCOPED_RULESET_SHAPE_ONLY_NOT_TRUSTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
