#!/usr/bin/env python3
"""Read-only, BASE-defined PR control-path check. PR data is NEVER executed.

This is a prospective companion pilot, NOT an adopted required check and NOT a
CURRENT issuer, semantic Stage4, or native Stage5 acceptance authority.
"""
from __future__ import annotations
import json
import os
import re
import sys
import urllib.error
import urllib.request

# Exact sensitive paths: a verified, protected branch's trusted workflow must
# decide any future edits to these. This is deliberately NOT a generic change
# freeze across every ordinary content/source-owner workspace.
PROTECTED = frozenset({
    ".github/workflows/gfp-required-governance-gate.yml",
    ".github/workflows/gfp-op01-trusted-base-guard.yml",
    "Verification/check_op01_trusted_base_pr_paths_v1.py",
    "Verification/tests/test_gfp_required_governance_gate_contract_v1.py",
    "Optimization-Program/WRITER-SCOPES.json",
})
ACCEPTED_STATUSES = frozenset({
    "added", "removed", "modified", "renamed", "copied", "changed",
})
REPO_PATTERN = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
SHA_PATTERN = re.compile(r"[a-f0-9]{40}\Z")


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def safe_path(value: object) -> str:
    require(isinstance(value, str) and bool(value) and len(value) <= 4096,
            "UNSAFE_CHANGED_PATH")
    require(not value.startswith("/") and "\\" not in value and
            not any(x in ("", ".", "..") for x in value.split("/")) and
            not any(ord(ch) < 32 for ch in value),
            "UNSAFE_CHANGED_PATH")
    return value


def assess(pr: dict, files: list, repository: str, expected_number: int,
           event_head_sha: str) -> dict:
    """Validate a complete GitHub provider snapshot, not self-attested PR text."""
    require(isinstance(pr, dict) and isinstance(files, list),
            "INVALID_PR_PROVIDER_RESPONSE")
    require(pr.get("number") == expected_number, "PR_NUMBER_MISMATCH")
    base = pr.get("base")
    head = pr.get("head")
    require(isinstance(base, dict) and isinstance(head, dict),
            "MISSING_PROVIDER_PR_REFS")
    require(base.get("ref") == "main", "UNSUPPORTED_TARGET_BRANCH")
    require(isinstance(base.get("repo"), dict) and
            base["repo"].get("full_name") == repository,
            "WRONG_BASE_REPOSITORY")
    require(isinstance(head.get("sha"), str) and
            SHA_PATTERN.fullmatch(head["sha"]) and
            head["sha"] == event_head_sha, "PR_HEAD_SHA_MOVED_OR_UNATTESTED")
    count = pr.get("changed_files")
    require(type(count) is int and 0 < count <= 3000 and count == len(files),
            "INCOMPLETE_OR_OVERSIZED_PR_FILE_LIST")
    changed = set()
    for item in files:
        require(isinstance(item, dict) and
                item.get("status") in ACCEPTED_STATUSES,
                "INVALID_CHANGED_FILE_RECORD")
        for field in ("filename", "previous_filename"):
            if item.get(field) is not None:
                changed.add(safe_path(item[field]))
    blocked = sorted(PROTECTED.intersection(changed))
    require(not blocked,
            "TRUSTED_GOVERNANCE_CONTROL_PATH_EDIT_REQUIRES_SEPARATE_OWNER_DECISION:"+
            ",".join(blocked))
    return {"schema": "gfp-op01-trusted-base-path-preflight@1.0.0",
            "status": "PASS_BASE_DEFINED_CONTROL_PATHS_UNCHANGED",
            "scope": "PROTECTED_PATHS_ONLY__NOT_ALL_SOURCE_CONTENT_QA",
            "pr_number": expected_number,
            "head_sha": event_head_sha,
            "changed_files_checked": count}


def get_json(url: str, token: str) -> object:
    req = urllib.request.Request(
        url, headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GFP-OP01-trusted-base-readonly",
        })
    with urllib.request.urlopen(req, timeout=20) as response:
        require(response.status == 200, "UNEXPECTED_GITHUB_RESPONSE")
        return json.load(response)


def run(env: dict | None = None, fetch=get_json) -> dict:
    env = os.environ if env is None else env
    require(env.get("GITHUB_EVENT_NAME") == "pull_request_target",
            "BASE_DEFINED_PR_EVENT_REQUIRED")
    repository = env.get("GITHUB_REPOSITORY", "")
    require(bool(REPO_PATTERN.fullmatch(repository)),
            "INVALID_REPOSITORY")
    try:
        number = int(env.get("PR_NUMBER", ""))
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_PR_NUMBER") from exc
    require(0 < number < 100000000, "INVALID_PR_NUMBER")
    head = env.get("PR_HEAD_SHA", "")
    require(bool(SHA_PATTERN.fullmatch(head)), "INVALID_EVENT_HEAD_SHA")
    token = env.get("GITHUB_TOKEN", "")
    require(bool(token), "MISSING_READ_ONLY_TOKEN")
    api = "https://api.github.com/repos/" + repository + "/pulls/" + str(number)
    pr = fetch(api, token)
    require(isinstance(pr, dict), "INVALID_PR_PROVIDER_RESPONSE")
    count = pr.get("changed_files")
    require(type(count) is int and 0 < count <= 3000,
            "INCOMPLETE_OR_OVERSIZED_PR_FILE_LIST")
    files = []
    for page in range(1, (count + 99) // 100 + 1):
        page_rows = fetch(api + "/files?per_page=100&page=" + str(page), token)
        require(isinstance(page_rows, list), "INVALID_PR_FILE_PAGE")
        require(0 < len(page_rows) <= 100, "INCOMPLETE_PR_FILE_PAGE")
        files.extend(page_rows)
    result = assess(pr, files, repository, number, head)
    # A moving PR head must not reuse the old positive result as current proof.
    latest = fetch(api, token)
    require(isinstance(latest, dict) and
            isinstance(latest.get("head"), dict) and
            latest["head"].get("sha") == head and
            latest.get("changed_files") == count,
            "PR_HEAD_OR_FILE_SET_MOVED_DURING_BASE_CHECK")
    return result


if __name__ == "__main__":
    try:
        print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
    except (ValueError, OSError, urllib.error.URLError,
            UnicodeError, json.JSONDecodeError) as error:
        print("OP01_TRUSTED_BASE_PILOT_BLOCKED:" + str(error), file=sys.stderr)
        raise SystemExit(2)
