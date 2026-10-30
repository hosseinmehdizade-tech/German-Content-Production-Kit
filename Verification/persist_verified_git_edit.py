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
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from validate_applied_edit_bytes import verify as verify_local, digest, FILE_KEYS

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
    # A protected component can be version-numbered, or use hyphens,
    # underscores or dots. Do not mistake "02-Source" or
    # "03-source-pdfs" for an editable working directory.
    def protected_component(segment: str) -> bool:
        parts = re.split(r"[-_.]+", segment.lower())
        return any(part in forbidden or part == "original" for part in parts)

    if (any(protected_component(s) for s in segments[1:])
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
    if method == "GET_BRANCH":
        # Read GitHub's actual branch metadata, not a repository-authored JSON
        # claim. This is a necessary but NOT sufficient trust precondition.
        url = (f"https://api.github.com/repos/{REPOSITORY}/branches/"
               + urllib.parse.quote(branch, safe=""))
    elif method in {"GET", "PUT"}:
        encoded = "/".join(urllib.parse.quote(s, safe="") for s in path.split("/"))
        url = f"https://api.github.com/repos/{REPOSITORY}/contents/{encoded}"
        if method == "GET":
            url += "?ref=" + urllib.parse.quote(branch, safe="")
    else:
        raise PersistenceBlocked("UNSUPPORTED_GITHUB_API_OPERATION")
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "Authorization": "Bearer " + token}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers,
                                     method="GET" if method == "GET_BRANCH" else method)
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
    # A grant with duplicate keys (e.g. two different "status" values) can
    # be interpreted differently by two tools. Never normalize ambiguity.
    def unique_pairs(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("DUPLICATE_REGISTRY_JSON_KEY")
            out[key] = value
        return out

    def no_nonfinite(value):
        raise ValueError("NONFINITE_REGISTRY_JSON_VALUE")

    try:
        registry = json.loads(raw, object_pairs_hook=unique_pairs,
                              parse_constant=no_nonfinite)
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
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


def verify_remote_branch_protected(payload: dict, *, branch: str) -> None:
    """Necessary GitHub-provided precondition, not independent issuer approval.

    Branch "protected" can be true under a weak rule. This check DOES NOT
    establish strict review requirements, secure check provenance, immutability,
    or atomic protection across the subsequent PUT.
    """
    if not isinstance(payload, dict) or payload.get("name") != branch:
        raise PersistenceBlocked("REMOTE_BRANCH_STATUS_UNVERIFIABLE")
    if payload.get("protected") is not True:
        raise PersistenceBlocked("REMOTE_MAIN_UNPROTECTED: no scoped write")


def capture_verified_local_snapshot(proof_file: Path):
    """Validate and return immutable input bytes; never re-open the CURRENT for PUT.

    The copied evidence is independently verified in a private temporary
    directory. Changes to the original files during verification fail closed.
    """
    try:
        original_root = proof_file.resolve().parent
        proof_bytes = proof_file.read_bytes()
        if len(proof_bytes) > MAX_TEXT_BYTES:
            raise PersistenceBlocked("LOCAL_SNAPSHOT_OVERSIZED_PROOF")
        proof = json.loads(proof_bytes)
        if not isinstance(proof, dict) or not isinstance(proof.get("files"), dict):
            raise PersistenceBlocked("LOCAL_SNAPSHOT_INVALID_PROOF")
        file_bytes, sources = {}, {}
        for key in FILE_KEYS:
            name = proof["files"].get(key)
            if not isinstance(name, str) or not name:
                raise PersistenceBlocked("LOCAL_SNAPSHOT_INVALID_PATH: " + key)
            relative = Path(name)
            if (relative.is_absolute() or not relative.parts
                    or any(part in ("..", ".") for part in relative.parts)
                    or "\\" in name):
                raise PersistenceBlocked("LOCAL_SNAPSHOT_UNSAFE_PATH: " + key)
            source = original_root / relative
            if any((original_root.joinpath(*relative.parts[:i])).is_symlink()
                   for i in range(1, len(relative.parts) + 1)):
                raise PersistenceBlocked("LOCAL_SNAPSHOT_SYMLINK_REJECTED: " + key)
            resolved = source.resolve()
            if original_root not in resolved.parents:
                raise PersistenceBlocked("LOCAL_SNAPSHOT_UNSAFE_PATH: " + key)
            size = source.stat().st_size
            if size > 256 * 1024 * 1024:
                raise PersistenceBlocked("LOCAL_SNAPSHOT_OVERSIZED_INPUT: " + key)
            data = source.read_bytes()
            if len(data) != size:
                raise PersistenceBlocked("LOCAL_SNAPSHOT_INPUT_CHANGED: " + key)
            file_bytes[key] = data
            sources[key] = source
        with tempfile.TemporaryDirectory(prefix="op01-immutable-proof-") as directory:
            root = Path(directory)
            for key, name in proof["files"].items():
                if key not in FILE_KEYS:
                    continue
                target = root / name
                if target.name == "_OP01-snapshot-proof.json":
                    raise PersistenceBlocked("LOCAL_SNAPSHOT_RESERVED_NAME")
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() and target.read_bytes() != file_bytes[key]:
                    raise PersistenceBlocked("LOCAL_SNAPSHOT_FILE_ALIAS_CONFLICT")
                target.write_bytes(file_bytes[key])
            candidate = root / "_OP01-snapshot-proof.json"
            candidate.write_bytes(proof_bytes)
            errors = verify_local(candidate)
            if errors:
                raise PersistenceBlocked("LOCAL_APPLIED_PROOF_FAILED: " + " | ".join(errors))
        # File bytes and proof were read once, verified together and retained
        # in memory; this freshness check protects local concurrent writers.
        assert_local_snapshot_unchanged(proof_file, proof_bytes, sources, file_bytes)
        return proof, proof_bytes, file_bytes, sources
    except (OSError, ValueError, UnicodeError) as exc:
        raise PersistenceBlocked("LOCAL_SNAPSHOT_UNREADABLE_OR_INVALID") from exc


def assert_local_snapshot_unchanged(proof_file, proof_bytes, sources, file_bytes):
    try:
        if proof_file.read_bytes() != proof_bytes:
            raise PersistenceBlocked("LOCAL_SNAPSHOT_CHANGED: proof")
        for key, source in sources.items():
            if source.is_symlink() or source.read_bytes() != file_bytes[key]:
                raise PersistenceBlocked("LOCAL_SNAPSHOT_CHANGED: " + key)
    except OSError as exc:
        raise PersistenceBlocked("LOCAL_SNAPSHOT_INPUT_DISAPPEARED") from exc


def persist(proof_file: Path, path: str, expected_blob_sha: str, token: str,
            *, branch: str = "main", api=github_api) -> dict:
    verify_target(path, branch)
    if not isinstance(token, str) or not token.strip():
        raise PersistenceBlocked("AUTH_REQUIRED: GITHUB_TOKEN must be configured")
    if not isinstance(expected_blob_sha, str) or not HEX40.fullmatch(expected_blob_sha):
        raise PersistenceBlocked("EXPECTED_BLOB_SHA_REQUIRED: exactly 40 hex chars")
    proof, proof_bytes, inputs, original_paths = capture_verified_local_snapshot(proof_file)
    if proof.get("format", "JSON_ITEMS_V1") not in {"JSON_ITEMS_V1", "TSV_ITEMS_V1"}:
        raise PersistenceBlocked("GIT_TEXT_ONLY: ZIP/binary content is never committed as transport")
    before = inputs["parent"]
    current = inputs["current"]
    if (len(before) > MAX_TEXT_BYTES or len(current) > MAX_TEXT_BYTES
            or before == current):
        raise PersistenceBlocked("GIT_TEXT_ONLY: too large or no actual edit")
    # Distinct authenticated Git configuration defaults to deny-all. The grant
    # pins the exact proof, source, target, parent and candidate byte hashes.
    registry_sha, approval_ref = verify_remote_scope(
        api("GET", SCOPE_PATH, branch, token), proof=proof,
        proof_bytes=proof_bytes, path=path, branch=branch,
        parent_sha=expected_blob_sha, current=current)
    old_data, actual_sha = decode_github_file(api("GET", path, branch, token))
    if actual_sha != expected_blob_sha or old_data != before:
        raise PersistenceBlocked("STALE_CURRENT: remote mutable bytes/parent blob differ; no write")
    # Reject a concurrent local editor before remote mutation. The actual
    # uploaded payload is ALWAYS from the previously validated snapshot.
    assert_local_snapshot_unchanged(proof_file, proof_bytes, original_paths, inputs)
    # The registry may have been replaced/revoked after our first GET. Fail
    # closed before uploading if even one registry byte changed during local
    # verification or target read. This is NOT an atomic cross-file lock:
    # Git branch protection/trusted issuer controls are still required.
    _, scope_blob_before_put = decode_github_file(api("GET", SCOPE_PATH, branch, token))
    if scope_blob_before_put != registry_sha:
        raise PersistenceBlocked("REMOTE_SCOPE_CHANGED_PRE_PUT: approval altered or revoked")
    # Even a syntactically exact grant inside Git cannot authorize a write if
    # its policy file lives on an unprotected mutable main branch. GitHub's
    # branch protected bit is only a necessary (not sufficient) condition.
    verify_remote_branch_protected(
        api("GET_BRANCH", "", branch, token), branch=branch)
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
        "scope_rechecked_identical_pre_put": True,
        "scope_recheck_is_atomic_with_target_put": False,
        "branch_protected_bit_checked_pre_put": True,
        "branch_protection_is_independent_issuer_proof": False,
        "branch_protection_is_atomic_with_put": False,
        "parent_sha256": digest(before), "current_sha256": digest(current),
        "remote_readback_sha256": digest(remote_data),
        "commit_sha": written["commit"]["sha"],
        "applied_items_local_verified": proof["applied_count"],
        "source_immutable_local_proof": True,
        "input_snapshot_exact": True,
        "local_input_freshness_pre_put": True,
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
