#!/usr/bin/env python3
"""OP-01 opt-in GitHub Contents CAS writer for *already verified* mutable text edits.

This is a narrow working-data writer, NOT a release/Stage4-7 gate or Library writer.
No default workstream mutation: execution needs an explicit proof, path, expected
remote blob SHA, GITHUB_TOKEN and a separate exact-scope Git allowlist grant.
Original sources and LOCKED paths are forbidden.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from validate_applied_edit_bytes import verify as verify_local, digest

REPOSITORY = "hosseinmehdizade-tech/German-Content-Production-Kit"
MAX_TEXT_BYTES = 1_000_000
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
SAFE_SEGMENT = re.compile(r"[A-Za-z0-9._-]+\Z")
SCOPE_PATH = "Optimization-Program/WRITER-SCOPES.json"
SCOPE_SCHEMA = "gcpk-remote-git-writer-scopes@1"


class PersistenceBlocked(Exception):
    pass


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify_target(path: str, branch: str) -> None:
    segments = path.split("/") if isinstance(path, str) else []
    if (len(segments) < 3 or segments[0] != "Workspaces"
            or any(not SAFE_SEGMENT.fullmatch(s) or s in {".", ".."} for s in segments)
            or segments[-1].lower().endswith((".zip", ".rar", ".pdf"))
            or not segments[-1].lower().endswith((".tsv", ".json"))
            or branch != "main"):
        raise PersistenceBlocked("UNAUTHORIZED_TARGET: only named Workspaces text file on main")
    forbidden = {"00-source", "source", "sources", "locked", "archive", "archives",
                 "recovery", "protected-history", "final"}
    if (any(s.lower() in forbidden or "locked" in s.lower() for s in segments[1:])
            or segments[-1].lower() in {"latest.json", "checkpoint.json", "source-manifest.json"}
            or segments[-1].lower().startswith(("source-", "original-"))):
        raise PersistenceBlocked("IMMUTABLE_OR_AUTHORITY_PATH: refusing protected/source/checkpoint target")


def decode_github_file(payload: dict) -> tuple[bytes, str]:
    if (not isinstance(payload, dict) or payload.get("type") != "file"
            or payload.get("encoding") != "base64" or not isinstance(payload.get("content"), str)
            or not isinstance(payload.get("sha"), str)
            or not HEX40.fullmatch(payload["sha"])):
        raise PersistenceBlocked("REMOTE_CONTENTS_UNUSABLE: expected base64 file with blob SHA")
    try:
        data = base64.b64decode("".join(payload["content"].split()), validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise PersistenceBlocked("REMOTE_CONTENTS_INVALID_BASE64") from exc
    if (len(data) > MAX_TEXT_BYTES or payload.get("size") != len(data)
            or git_blob_sha(data) != payload["sha"]):
        raise PersistenceBlocked("REMOTE_CONTENTS_UNTRUSTED: size or Git blob hash mismatch")
    return data, payload["sha"]


def github_api(method: str, path: str, branch: str, token: str, payload: dict | None = None) -> dict:
    encoded = "/".join(urllib.parse.quote(s, safe="") for s in path.split("/"))
    url = f"https://api.github.com/repos/{REPOSITORY}/contents/{encoded}"
    if method == "GET":
        url += "?ref=" + urllib.parse.quote(branch, safe="")
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "Authorization": "Bearer " + token}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(3_000_001)
    except urllib.error.HTTPError as exc:
        if method == "PUT" and exc.code in (409, 422):
            raise PersistenceBlocked("CAS_CONFLICT: GitHub rejected stale expected blob SHA") from exc
        if method == "PUT":
            raise PersistenceBlocked("WRITE_OUTCOME_UNCERTAIN: inspect remote before any retry") from exc
        raise PersistenceBlocked(f"REMOTE_READ_BLOCKED: HTTP {exc.code}") from exc
    except (urllib.error.URLError, OSError) as exc:
        label = "WRITE_OUTCOME_UNCERTAIN" if method == "PUT" else "REMOTE_READ_BLOCKED"
        raise PersistenceBlocked(label + ": inspect remote before retry") from exc
    if len(raw) > 3_000_000:
        raise PersistenceBlocked("REMOTE_RESPONSE_OVERSIZED")
    try:
        response = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise PersistenceBlocked("REMOTE_RESPONSE_NOT_JSON") from exc
    if not isinstance(response, dict):
        raise PersistenceBlocked("REMOTE_RESPONSE_NOT_OBJECT")
    return response


def verify_remote_scope(payload: dict, *, proof: dict, proof_bytes: bytes,
                        path: str, branch: str, parent_sha: str,
                        current: bytes) -> tuple[str, str]:
    """Match an independently stored exact-scope allowlist; never auto-authorize.

    A grant is separate Git state, not a certificate of the user's identity,
    independent Stage4, or an atomic cross-file revocation guarantee.
    """
    raw, registry_blob = decode_github_file(payload)
    try:
        registry = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise PersistenceBlocked("REMOTE_SCOPED_PERMISSION_INVALID_JSON") from exc
    if not isinstance(registry, dict) or registry.get("schema") != SCOPE_SCHEMA:
        raise PersistenceBlocked("REMOTE_SCOPED_PERMISSION_BAD_SCHEMA")
    if registry.get("status") != "ACTIVE_SCOPED_GRANTS":
        raise PersistenceBlocked("REMOTE_SCOPED_PERMISSION_DENY_ALL")
    entries = registry.get("scopes")
    if not isinstance(entries, list):
        raise PersistenceBlocked("REMOTE_SCOPED_PERMISSION_MALFORMED")
    expected = {
        "status": "APPROVED",
        "workstream": proof.get("workstream"),
        "artifact_id": proof.get("artifact_id"),
        "path": path,
        "branch": branch,
        "expected_parent_blob_sha": parent_sha,
        "approved_current_sha256": digest(current),
        "approved_proof_sha256": digest(proof_bytes),
        "source_sha256": proof.get("sha256", {}).get("source_before"),
    }
    matches = [e for e in entries if isinstance(e, dict)
               and all(e.get(key) == value for key, value in expected.items())
               and isinstance(e.get("authorization_ref"), str)
               and e["authorization_ref"].strip()]
    if len(matches) != 1:
        raise PersistenceBlocked("REMOTE_SCOPED_PERMISSION_NO_EXACT_APPROVED_GRANT")
    return registry_blob, matches[0]["authorization_ref"]


def persist(proof_file: Path, path: str, expected_blob_sha: str, token: str,
            *, branch: str = "main", api=github_api) -> dict:
    verify_target(path, branch)
    if not isinstance(token, str) or not token.strip():
        raise PersistenceBlocked("AUTH_REQUIRED: GITHUB_TOKEN must be configured")
    if not isinstance(expected_blob_sha, str) or not HEX40.fullmatch(expected_blob_sha):
        raise PersistenceBlocked("EXPECTED_BLOB_SHA_REQUIRED: exactly 40 hex chars")
    failures = verify_local(proof_file)
    if failures:
        raise PersistenceBlocked("LOCAL_APPLIED_PROOF_FAILED: " + " | ".join(failures))
    proof = json.loads(proof_file.read_text(encoding="utf-8"))
    if proof.get("format", "JSON_ITEMS_V1") not in {"JSON_ITEMS_V1", "TSV_ITEMS_V1"}:
        raise PersistenceBlocked("GIT_TEXT_ONLY: ZIP/binary content is never committed as transport")
    base = proof_file.resolve().parent
    before = (base / proof["files"]["parent"]).read_bytes()
    current = (base / proof["files"]["current"]).read_bytes()
    if (len(before) > MAX_TEXT_BYTES or len(current) > MAX_TEXT_BYTES
            or before == current):
        raise PersistenceBlocked("GIT_TEXT_ONLY: too large or no actual edit")
    # Distinct authenticated Git configuration defaults to deny-all. The grant
    # pins the exact proof, source, target, parent and candidate byte hashes.
    proof_bytes = proof_file.read_bytes()
    registry_sha, approval_ref = verify_remote_scope(
        api("GET", SCOPE_PATH, branch, token), proof=proof,
        proof_bytes=proof_bytes, path=path, branch=branch,
        parent_sha=expected_blob_sha, current=current)
    old_data, actual_sha = decode_github_file(api("GET", path, branch, token))
    if actual_sha != expected_blob_sha or old_data != before:
        raise PersistenceBlocked("STALE_CURRENT: remote mutable bytes/parent blob differ; no write")
    new_sha = git_blob_sha(current)
    message = "apply(OP-01): verified mutable working bytes " + proof["workstream"]
    written = api("PUT", path, branch, token, {
        "message": message, "content": base64.b64encode(current).decode("ascii"),
        "sha": actual_sha, "branch": branch})
    if (not isinstance(written.get("content"), dict)
            or written["content"].get("sha") != new_sha
            or not isinstance(written.get("commit"), dict)
            or not HEX40.fullmatch(str(written["commit"].get("sha", "")))):
        raise PersistenceBlocked("WRITE_OUTCOME_UNCERTAIN: unexpected GitHub write response")
    # Independent second GET by path, not a trusted PUT echo or a local copy.
    remote_data, remote_sha = decode_github_file(api("GET", path, branch, token))
    if remote_data != current or remote_sha != new_sha:
        raise PersistenceBlocked("REMOTE_READBACK_MISMATCH: cannot claim persisted APPLIED")
    return {
        "schema": "gcpk-remote-git-applied-edit@1",
        "result": "PASS_SCOPED_GIT_CAS_AND_INDEPENDENT_REMOTE_READBACK",
        "repository": REPOSITORY, "path": path, "branch": branch,
        "workstream": proof["workstream"], "artifact_id": proof["artifact_id"],
        "old_blob_sha": actual_sha, "new_blob_sha": new_sha,
        "scope_registry_path": SCOPE_PATH, "scope_registry_blob_sha": registry_sha,
        "scope_authorization_ref": approval_ref,
        "scope_is_independent_user_approval_proof": False,
        "parent_sha256": digest(before), "current_sha256": digest(current),
        "remote_readback_sha256": digest(remote_data),
        "commit_sha": written["commit"]["sha"],
        "applied_items_local_verified": proof["applied_count"],
        "source_immutable_local_proof": True,
        "global_writer_coverage": False,
        "independent_linguistic_stage4": False,
        "library_readback_verified": False,
        "stage5_6_7_acceptance": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--path", required=True, help="Exact mutable Workspaces .tsv/.json path")
    parser.add_argument("--expected-blob-sha", required=True)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--receipt", type=Path, required=True,
                        help="A new file; never overwrite a prior outcome")
    args = parser.parse_args()
    try:
        if args.receipt.exists():
            raise PersistenceBlocked("RECEIPT_EXISTS: refuse to overwrite prior evidence")
        outcome = persist(args.proof, args.path, args.expected_blob_sha,
                          os.environ.get("GITHUB_TOKEN", ""), branch=args.branch)
        with args.receipt.open("x", encoding="utf-8") as output:
            json.dump(outcome, output, ensure_ascii=False, indent=2)
            output.write("\n")
        print(json.dumps({"result": outcome["result"], "receipt": str(args.receipt),
                          "commit_sha": outcome["commit_sha"]}))
        return 0
    except (PersistenceBlocked, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"result": "BLOCKED", "reason": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
