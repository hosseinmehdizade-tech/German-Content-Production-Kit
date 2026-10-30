#!/usr/bin/env python3
"""OP-01 NONACTIVE simulation of a one-file staged edit proposed via a PR.

No GitHub network, no clone, no credential, no PUT, no merge, no scope grant.
Caller-supplied snapshots are UNTRUSTED. A green result means only that the
provided shape is internally consistent; it cannot authenticate approval,
branch protection, source of required checks or actual currentness.
"""
from __future__ import annotations

import hashlib
import json
import re

from persist_verified_git_edit import PersistenceBlocked, git_blob_sha, verify_target

REPOSITORY = "hosseinmehdizade-tech/German-Content-Production-Kit"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
STAGING = re.compile(r"op01-staging/[a-z0-9][a-z0-9._-]{2,90}\Z")
SCHEMA = "gcpk-op01-feature-branch-pr-contract-simulation@1"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def assess(plan: dict, observed: dict, *, parent: bytes, candidate: bytes,
           staged: bytes) -> dict:
    blockers = []
    output = {
        "schema": SCHEMA,
        "status": "BLOCKED_PR_TRANSPORT_SIMULATION",
        "observations_are_authenticated": False,
        "test_only": True,
        "blockers": blockers,
        "checked_target": None,
        "checked_staging_branch": None,
        "base_head_unchanged_within_snapshot": False,
        "pr_head_unchanged_within_snapshot": False,
        "exact_one_file_modified": False,
        "file_bytes_match_claimed_candidate": False,
        "main_branch_protection_independently_verified": False,
        "required_status_source_authenticated": False,
        "independent_current_issuer_authenticated": False,
        "independent_owner_approval": False,
        "workstream_content_approved": False,
        "op01_writer_granted": False,
        "production_write_allowed": False,
        "pr_merge_allowed": False,
        "stage4_semantic_pass": False,
        "stage5_allowed": False,
        "stage6_pass": False,
        "stage7_release_final": False,
        "performed_writes": False,
        "github_settings_changed": False,
    }
    if not isinstance(plan, dict) or not isinstance(observed, dict):
        output["blockers"] = ["INVALID_PLAN_OR_SNAPSHOT"]
        return output

    path = plan.get("target_path")
    branch = plan.get("staging_branch")
    expected_main = plan.get("expected_main_commit_sha")
    expected_parent = plan.get("expected_parent_git_blob_sha")
    expected_candidate = plan.get("expected_candidate_sha256")
    if plan.get("repository") != REPOSITORY or plan.get("target_branch") != "main":
        blockers.append("UNEXPECTED_REPOSITORY_OR_TARGET_BRANCH")
    if not isinstance(path, str):
        blockers.append("INVALID_EDIT_PATH")
    else:
        try:
            verify_target(path, "main")
        except PersistenceBlocked:
            blockers.append("EDIT_PATH_OUTSIDE_MUTABLE_WORKSPACE")
        else:
            if plan.get("workstream") != path.split("/")[1]:
                blockers.append("WORKSTREAM_TARGET_PATH_MISMATCH")
            output["checked_target"] = path

    if not isinstance(branch, str) or not STAGING.fullmatch(branch) or branch == "main":
        blockers.append("INVALID_DEDICATED_STAGING_BRANCH")
    else:
        output["checked_staging_branch"] = branch
    for name, value, rx in (
        ("EXPECTED_MAIN_COMMIT", expected_main, HEX40),
        ("EXPECTED_PARENT_BLOB", expected_parent, HEX40),
        ("EXPECTED_CANDIDATE_BYTES", expected_candidate, HEX64),
    ):
        if not isinstance(value, str) or rx.fullmatch(value) is None:
            blockers.append(name + "_SHA_INVALID")
    if not all(isinstance(v, bytes) and 0 < len(v) <= 1_000_000
               for v in (parent, candidate, staged)):
        blockers.append("RAW_PARENT_CANDIDATE_STAGED_BYTES_INVALID")
    else:
        if parent == candidate:
            blockers.append("NO_EDIT")
        if not isinstance(expected_parent, str) or git_blob_sha(parent) != expected_parent:
            blockers.append("LOCAL_PARENT_GIT_BLOB_MISMATCH")
        if not isinstance(expected_candidate, str) or _sha256(candidate) != expected_candidate:
            blockers.append("CANDIDATE_SHA256_MISMATCH")
        if staged != candidate:
            blockers.append("STAGING_BRANCH_READBACK_BYTES_DIFFER")
        else:
            output["file_bytes_match_claimed_candidate"] = True

    pr = observed.get("pull_request")
    if not isinstance(pr, dict):
        blockers.append("PR_METADATA_MISSING")
    else:
        if (type(pr.get("number")) is not int or pr["number"] < 1 or
                pr.get("state") != "open" or pr.get("merged") is not False or
                pr.get("base") != "main" or pr.get("head") != branch or
                pr.get("head_repo_full_name") != REPOSITORY):
            blockers.append("PR_IDENTITY_OR_REVIEW_STATE_MISMATCH")
        if (pr.get("base_sha") != expected_main or
                not isinstance(pr.get("head_sha"), str) or
                not HEX40.fullmatch(pr["head_sha"])):
            blockers.append("PR_BASE_OR_HEAD_PIN_MISMATCH")
        if pr.get("changed_files") != 1:
            blockers.append("PR_CHANGED_FILE_COUNT_MISMATCH")

    files = observed.get("changed_files")
    if (not isinstance(files, list) or len(files) != 1 or
            not isinstance(files[0], dict) or
            files[0].get("filename") != path or
            files[0].get("status") != "modified" or
            set(files[0]).difference({"filename", "status"})):
        blockers.append("PR_FILE_SCOPE_NOT_EXACT_ONE_MODIFIED_WORKING_FILE")
    elif isinstance(pr, dict) and pr.get("changed_files") == 1:
        output["exact_one_file_modified"] = True
    if observed.get("changed_files_paginated_complete") is not True:
        blockers.append("PR_FILES_PAGINATION_NOT_PROVEN_COMPLETE")

    first_main = observed.get("main_commit_before")
    last_main = observed.get("main_commit_after")
    if first_main != expected_main or last_main != expected_main:
        blockers.append("MAIN_HEAD_CHANGED_OR_STALE_BASE")
    else:
        output["base_head_unchanged_within_snapshot"] = True
    first_head = observed.get("pr_head_before")
    last_head = observed.get("pr_head_after")
    if (not isinstance(pr, dict) or not isinstance(first_head, str)
            or not HEX40.fullmatch(first_head) or
            first_head != last_head or first_head != pr.get("head_sha")):
        blockers.append("PR_HEAD_MOVED_OR_UNPINNED")
    else:
        output["pr_head_unchanged_within_snapshot"] = True

    if observed.get("parent_git_blob_sha_at_main") != expected_parent:
        blockers.append("REMOTE_PARENT_BLOB_STALE_OR_UNVERIFIED")
    if observed.get("candidate_git_blob_sha_at_head") != (
            git_blob_sha(staged) if isinstance(staged, bytes) else None):
        blockers.append("REMOTE_STAGING_BLOB_MISMATCH")
    if observed.get("main_protected") is not True:
        blockers.append("PROTECTED_MAIN_NOT_SHOWN_IN_SUPPLIED_SNAPSHOT")
    if observed.get("writer_scope_status") != "DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL":
        blockers.append("WRITER_SCOPE_DENY_ALL_NOT_PRESERVED")

    output["blockers"] = sorted(set(blockers))
    if not blockers:
        output["status"] = "PASS_SIMULATED_ONE_FILE_PR_SHAPE_ONLY_NOT_AUTHORIZED"
    return output


def main() -> int:
    # Intentionally no CLI that could read arbitrary user data or access GitHub:
    # synthetic callers and CI unit tests only until owner approves architecture.
    print(json.dumps({
        "schema": SCHEMA,
        "status": "NONACTIVE_USE_TEST_FIXTURES_ONLY",
        "perform_writes": False,
        "owner_approval_still_required": True
    }, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
