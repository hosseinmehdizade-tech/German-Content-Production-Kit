#!/usr/bin/env python3
"""OP02 exact-byte source + Git blob + CAS rollback preflight, read-only.

Pins are independently SUPPLIED, not authenticated here. Never grants a
writer, issuer identity, Stage4 semantic PASS or Stage5–7 release.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import re
import stat

HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
MAX_BYTES = 256 * 1024 * 1024
MODALITIES = {"pdf", "rar5", "csv", "json", "zip"}


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob_sha1(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def valid_sha(x):
    return type(x) is str and bool(HEX64.fullmatch(x)) and x != "0"*64


def valid_git(x):
    return type(x) is str and bool(HEX40.fullmatch(x)) and x != "0"*40


def result(scope, errors, **extra):
    return {
        "schema": "gcpk-op02-exact-byte-cas-diagnostic@1",
        "scope": scope,
        "status": ("BLOCKED" if errors else "PASS_SCOPED_BYTES_ONLY_NOT_RELEASE"),
        "errors": sorted(set(errors)),
        "authenticated_trust_root": False,
        "authenticated_issuer": False,
        "stage4_semantic_pass": False,
        "stage5_7_authorized": False,
        "writer_granted": False,
        "performed_writes": False,
        **extra,
    }


def source_bytes(specs, byte_map, independent_pins):
    """Exact SHA256, size and format-header binding of source bytes.

    `independent_pins` MUST come from an independently resolved authority:
    agreement of two caller-controlled dicts is NOT authentication.
    """
    errors, evidence = [], []
    if (type(specs) is not list or not specs or type(byte_map) is not dict
            or type(independent_pins) is not dict):
        return result("SOURCE", ["INPUT_SHAPE"], byte_matches=False, items=[])
    ids = [s.get("source_id") if type(s) is dict else None for s in specs]
    if (any(type(i) is not str or not i for i in ids) or
            len(set(ids)) != len(ids) or
            set(ids) != set(byte_map) or set(ids) != set(independent_pins)):
        errors.append("SOURCE_UNIVERSE_DRIFT")
    for spec in specs:
        if (type(spec) is not dict or
                set(spec) != {"source_id", "modality", "sha256", "size_bytes"}):
            errors.append("SOURCE_SPEC_INVALID")
            continue
        sid = spec["source_id"]
        if (type(sid) is not str or not sid or spec["modality"] not in MODALITIES
                or not valid_sha(spec["sha256"])
                or type(spec["size_bytes"]) is not int
                or not 0 < spec["size_bytes"] <= MAX_BYTES):
            errors.append("SOURCE_SPEC_INVALID")
            continue
        pin = independent_pins.get(sid)
        if not valid_sha(pin) or pin != spec["sha256"]:
            errors.append("PIN_OR_MANIFEST_DRIFT:" + sid)
        data = byte_map.get(sid)
        if type(data) is not bytes or not 0 < len(data) <= MAX_BYTES:
            errors.append("MISSING_OR_INVALID_SOURCE_BYTES:" + sid)
            continue
        actual = sha256(data)
        magic = (spec["modality"] != "pdf" or data.startswith(b"%PDF-"))
        magic &= (spec["modality"] != "rar5" or data.startswith(b"Rar!\x1a\x07\x01\x00"))
        magic &= (spec["modality"] != "zip" or data.startswith(b"PK\x03\x04"))
        match = (actual == spec["sha256"] == pin
                 and len(data) == spec["size_bytes"] and magic)
        evidence.append({"source_id":sid, "sha256":actual,
                         "size_bytes":len(data), "byte_match":bool(match)})
        if not match:
            errors.append("BYTE_HASH_SIZE_OR_MAGIC_DRIFT:" + sid)
    return result("SOURCE", errors, byte_matches=not errors and
                  len(evidence) == len(specs), items=evidence)


def git_control_blob(raw, anchor, pin):
    """Check original Git blob bytes (SHA-1 Git object + SHA256).

    The supplied commit identifier is only compared to a distinct pin; its
    Git ancestry, HEAD currentness, issuer scope and trust aren't proven.
    """
    fields = {"repository", "path", "commit_sha", "blob_sha", "sha256"}
    if (type(anchor) is not dict or set(anchor) != fields or
            type(pin) is not dict or set(pin) != fields):
        return result("GIT_BLOB", ["ANCHOR_SHAPE"])
    e = []
    if anchor != pin:
        e.append("ANCHOR_NOT_BOUND_TO_INDEPENDENT_PIN")
    path, repo = anchor["path"], anchor["repository"]
    if (type(repo) is not str or
            not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or
            type(path) is not str or not path.startswith("Workspaces/") or
            not path.endswith(".json") or "\\" in path or
            any(part in ("", ".", "..") for part in path.split("/")) or
            not valid_git(anchor["commit_sha"]) or
            not valid_git(anchor["blob_sha"]) or not valid_sha(anchor["sha256"])):
        e.append("ANCHOR_PATH_OR_IDENTITY_INVALID")
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_BYTES:
        e.append("GIT_BLOB_RAW_BYTES_MISSING")
        return result("GIT_BLOB", e, byte_matches=False)
    git_hash, full_hash = git_blob_sha1(raw), sha256(raw)
    if git_hash != anchor["blob_sha"] or full_hash != anchor["sha256"]:
        e.append("GIT_BLOB_BYTE_HASH_DRIFT")
    return result("GIT_BLOB", e, byte_matches=not e,
                  observed_git_blob_sha=git_hash, observed_sha256=full_hash)


def rollback_preflight(observed_head, expected_head, post_bytes, post_hash,
                       immutable_parent_bytes, parent_hash, *, issuer_claim=None):
    """CAS preconditions diagnostic ONLY. NO rollback is possible here."""
    e = []
    if not valid_git(observed_head) or not valid_git(expected_head):
        e.append("GIT_COMMIT_INVALID")
    elif observed_head != expected_head:
        e.append("REMOTE_HEAD_CHANGED")
    if (type(post_bytes) is not bytes or not post_bytes or
            type(immutable_parent_bytes) is not bytes or
            not immutable_parent_bytes):
        e.append("POST_OR_PARENT_BYTES_MISSING")
    if not valid_sha(post_hash) or not valid_sha(parent_hash):
        e.append("POST_OR_PARENT_PIN_INVALID")
    if type(post_bytes) is bytes and valid_sha(post_hash):
        if sha256(post_bytes) != post_hash:
            e.append("POSTIMAGE_BYTES_DRIFT")
    if type(immutable_parent_bytes) is bytes and valid_sha(parent_hash):
        if sha256(immutable_parent_bytes) != parent_hash:
            e.append("IMMUTABLE_PARENT_BYTES_DRIFT")
    if (type(post_bytes) is bytes and type(immutable_parent_bytes) is bytes
            and post_bytes == immutable_parent_bytes):
        e.append("SAME_PARENT_NOT_ROLLBACK")
    if issuer_claim is not None:
        e.append("SELF_ATTESTED_ISSUER_IS_NOT_AUTHENTICATION")
    return {
        **result("ROLLBACK", e),
        "status": "BLOCKED_NO_ROLLBACK_WRITER",
        "preconditions_consistent": not e,
        "rollback_authorized": False,
        "fresh_remote_cas_required": True,
        "explicit_owner_approval_required": True,
    }


def read_regular_file(path, *, max_bytes=MAX_BYTES):
    """Local input helper rejects symlinks, special files and oversized bytes."""
    p = Path(path)
    fd = os.open(str(p), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) |
                 getattr(os, "O_NONBLOCK", 0))
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or not 0 < st.st_size <= max_bytes:
            raise ValueError("FILE_NOT_REGULAR_NONEMPTY_WITHIN_LIMIT")
        with os.fdopen(os.dup(fd), "rb") as f:
            raw = f.read(max_bytes + 1)
        if len(raw) != st.st_size:
            raise ValueError("FILE_CHANGED_OR_TOO_LARGE")
        return raw
    finally:
        os.close(fd)
