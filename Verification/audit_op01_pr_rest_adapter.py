#!/usr/bin/env python3
"""OP-01 NONACTIVE adapter for actual GitHub REST /pulls/:n and /pulls/:n/files.

The existing staged-PR simulator intentionally uses an internal flat model.
Real GitHub's REST PR has *nested* head/base refs and file records with
provider-owned blob SHAs. This adapter validates the real shape before passing
untrusted snapshots to that simulator. NO HTTP CLIENT OR GITHUB WRITE HERE.
"""
from __future__ import annotations

import re
from typing import Any

from audit_op01_pr_staging_simulation import assess, git_blob_sha, REPOSITORY

HEX40 = re.compile(r"[0-9a-f]{40}\Z")


class RestShapeBlocked(Exception):
    pass


def _sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or not HEX40.fullmatch(value):
        raise RestShapeBlocked("INVALID_REST_SHA:" + field)
    return value


def _ref(item: Any, field: str) -> tuple[str, str, str]:
    if not isinstance(item, dict):
        raise RestShapeBlocked("REST_PR_REF_NOT_OBJECT:" + field)
    repo = item.get("repo")
    if not isinstance(repo, dict) or not isinstance(repo.get("full_name"), str):
        raise RestShapeBlocked("REST_PR_REF_REPO_MISSING:" + field)
    name = item.get("ref")
    if not isinstance(name, str) or not name:
        raise RestShapeBlocked("REST_PR_REF_NAME_INVALID:" + field)
    return name, _sha(item.get("sha"), field), repo["full_name"]


def normalize(
    raw_pr: Any,
    raw_files: Any,
    *,
    page_size: int,
    page_number: int,
    next_page_present: bool,
) -> dict:
    """Strictly map a complete, first-page GitHub REST snapshot to flat input.

    The pagination metadata remains caller-supplied and UNAUTHENTICATED.
    No positive status from this function can authorize approval/merge.
    """
    if not isinstance(raw_pr, dict) or not isinstance(raw_files, list):
        raise RestShapeBlocked("REST_PR_OR_FILES_INVALID")
    if (type(page_size) is not int or page_size != 100 or
            type(page_number) is not int or page_number != 1 or
            type(next_page_present) is not bool or next_page_present):
        raise RestShapeBlocked("REST_FILES_PAGE_NOT_EXHAUSTIVELY_READ")
    count = raw_pr.get("changed_files")
    if type(count) is not int or count < 1 or count != len(raw_files):
        raise RestShapeBlocked("REST_PR_FILE_COUNT_OR_PAGINATION_DRIFT")
    if len(raw_files) > 100:
        raise RestShapeBlocked("REST_FILES_PAGE_OVERSIZED")
    base_name, base_sha, base_repo = _ref(raw_pr.get("base"), "base")
    head_name, head_sha, head_repo = _ref(raw_pr.get("head"), "head")
    if base_repo != REPOSITORY or head_repo != REPOSITORY:
        raise RestShapeBlocked("REST_BASE_OR_HEAD_REPO_NOT_EXPECTED")
    num = raw_pr.get("number")
    if (type(num) is not int or num <= 0 or
            raw_pr.get("state") not in ("open", "closed") or
            type(raw_pr.get("merged")) is not bool or
            type(raw_pr.get("draft")) is not bool):
        raise RestShapeBlocked("REST_PR_STATUS_INVALID")
    if raw_pr.get("state") == "open" and raw_pr.get("merged") is True:
        raise RestShapeBlocked("REST_PR_IMPOSSIBLE_MERGED_OPEN")
    seen: set[str] = set()
    normalized = []
    for item in raw_files:
        if not isinstance(item, dict):
            raise RestShapeBlocked("REST_FILE_ITEM_MALFORMED")
        filename = item.get("filename")
        status = item.get("status")
        blob = _sha(item.get("sha"), "file")
        if not isinstance(filename, str) or not filename or filename in seen:
            raise RestShapeBlocked("REST_FILE_DUPLICATE_OR_MISSING_PATH")
        seen.add(filename)
        if not isinstance(status, str) or status not in (
            "modified", "added", "removed", "renamed", "copied", "changed",
            "unchanged",
        ):
            raise RestShapeBlocked("REST_FILE_STATUS_UNRECOGNIZED")
        if status == "renamed" or item.get("previous_filename"):
            raise RestShapeBlocked("REST_RENAMED_FILE_FORBIDDEN")
        normalized.append({
            "filename": filename,
            "status": status,
            "git_blob_sha": blob,
        })
    return {
        "number": num,
        "state": raw_pr["state"],
        "merged": raw_pr["merged"],
        "draft": raw_pr["draft"],
        "base": base_name,
        "base_sha": base_sha,
        "head": head_name,
        "head_sha": head_sha,
        "head_repo_full_name": head_repo,
        "changed_files": count,
        "changed_files_normalized": normalized,
        "changed_files_paginated_complete": True,
    }


def assess_rest(plan: dict, observed: dict, *, rest_pr: Any, rest_files: Any,
                parent: bytes, candidate: bytes, staged: bytes,
                page_size: int = 100, page_number: int = 1,
                next_page_present: bool = False) -> dict:
    """Never promotes a REST snapshot to actual issuer or policy authority."""
    observation = dict(observed) if isinstance(observed, dict) else {}
    try:
        normalized = normalize(
            rest_pr, rest_files,
            page_size=page_size, page_number=page_number,
            next_page_present=next_page_present,
        )
        if len(normalized["changed_files_normalized"]) != 1:
            raise RestShapeBlocked("REST_PR_MUST_CHANGE_EXACTLY_ONE_FILE")
        file = normalized["changed_files_normalized"][0]
        if file["status"] != "modified":
            raise RestShapeBlocked("REST_NOT_MODIFIED_WORKING_FILE")
        if not isinstance(staged, bytes) or file["git_blob_sha"] != git_blob_sha(staged):
            raise RestShapeBlocked("REST_FILE_GIT_BLOB_DIFFERS_FROM_STAGING_BYTES")
        flat = {key: value for key, value in normalized.items()
                if key not in ("draft", "changed_files_normalized")}
        observation["pull_request"] = flat
        observation["changed_files"] = [{
            "filename": file["filename"],
            "status": file["status"],
        }]
        observation["changed_files_paginated_complete"] = normalized["changed_files_paginated_complete"]
        # Caller still must supply independently observed main/head pin reads.
        result = assess(plan, observation, parent=parent, candidate=candidate,
                        staged=staged)
    except (RestShapeBlocked, ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        result = assess(plan, {}, parent=parent, candidate=candidate, staged=staged)
        code = str(exc) if isinstance(exc, RestShapeBlocked) else type(exc).__name__
        result["blockers"] = sorted(set(result["blockers"] + [
            "REAL_REST_SHAPE_OR_SCOPE_REJECTED:" + code,
        ]))
        result["status"] = "BLOCKED_PR_TRANSPORT_SIMULATION"
    result["real_rest_shape_parsed_only"] = True
    result["rest_api_identity_authenticated"] = False
    result["rest_pagination_independently_authenticated"] = False
    result["github_network_requests_performed"] = False
    return result
