#!/usr/bin/env python3
"""OP-02 read-only trust-root/rollback contract proof; NOT a production writer.

Only synthetic NORMALIZED checkpoint receipts are supported. Native heterogeneous
workstream LATEST/CHECKPOINT layouts require a separately reviewed adapter.
"""
from __future__ import annotations
import hashlib
import json
import re

SCHEMA = "gcpk-op02-stage5-trust-root-plan@1"
CHECKPOINT_SCHEMA = "gcpk-op02-normalized-checkpoint-PROPOSAL@1"
SIDECAR_SCHEMA = "gcpk-op02-stage5-current-role-authority@1"
REPO = "hosseinmehdizade-tech/German-Content-Production-Kit"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}\Z")
FIELDS = (
    "workstream_id", "artifact_id", "registered_source_sha256",
    "parent_artifact_sha256", "current_tsv_sha256", "authority_sidecar_sha256"
)
CHECKPOINT_KEYS = {"schema", "lock_state", "activation_state", *FIELDS}
ROOT_KEYS = {"repository", "commit_sha", "checkpoint_path", "checkpoint_blob_sha",
             "checkpoint_sha256", *FIELDS}
EXPECTED_SIDECAR_KEYS = {
    "schema","status","lock_state","workstream_id","artifact_id",
    "registered_source_sha256","parent_artifact_sha256","roles"
}

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

def strict_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("DUPLICATE_KEY")
        value[key] = item
    return value

def invalid_constant(_):
    raise ValueError("NONFINITE_JSON")

def parse(raw: bytes):
    if not isinstance(raw, bytes) or len(raw) > 1_000_000:
        raise ValueError("INVALID_INPUT_BYTES")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=strict_object,
                      parse_constant=invalid_constant)

def hexof(value, length):
    return (isinstance(value, str) and
            (HEX40 if length == 40 else HEX64).fullmatch(value) is not None and
            value != "0" * length)

def result(errors):
    return {
        "schema": SCHEMA,
        "status": "PASS_NONACTIVE_PIN_CONSISTENCY_ONLY" if not errors else "BLOCKED",
        "errors": sorted(set(errors)),
        "production_approved": False,
        "writer_authorized": False,
        "real_latest_resolved": False,
        "not_proven": [
            "Anchor issuer authentication and native workstream LATEST adapter",
            "Independent semantic Stage4, actual source provenance and real user data",
            "Live Git/Library binary readback, active builder migration or Stage5-7 release",
        ],
    }

def verify_readonly(anchor: dict, readback: dict, checkpoint_bytes: bytes,
                    sidecar_bytes: bytes, writer_scopes: dict) -> dict:
    """Check independently PROVIDED pins against authenticated-readback-shaped bytes.

    The caller MUST independently authenticate the anchor and Git commit.
    Self-authored matching objects never establish approval or trusted CURRENT.
    """
    errors = []
    if not isinstance(anchor, dict) or set(anchor) != ROOT_KEYS:
        return result(["ANCHOR_SCHEMA_INVALID"])
    if (anchor["repository"] != REPO or not hexof(anchor["commit_sha"], 40)
            or not hexof(anchor["checkpoint_blob_sha"], 40)
            or not hexof(anchor["checkpoint_sha256"], 64)):
        errors.append("EXTERNAL_ROOT_IDENTITY_INVALID")
    ws = anchor["workstream_id"]
    if (not isinstance(ws, str) or not IDENT.fullmatch(ws)
            or not isinstance(anchor["checkpoint_path"], str)
            or anchor["checkpoint_path"] != f"Workspaces/{ws}/LATEST.json"):
        errors.append("UNSUPPORTED_NATIVE_LATEST_PATH_OR_SCOPE")
    for key in FIELDS:
        value = anchor[key]
        if key in ("workstream_id", "artifact_id"):
            if not isinstance(value, str) or not IDENT.fullmatch(value):
                errors.append("EXTERNAL_FIELD_INVALID:" + key)
        elif not hexof(value, 64):
            errors.append("EXTERNAL_FIELD_INVALID:" + key)
    if errors:
        return result(errors)
    if (not isinstance(readback, dict) or
            set(readback) != {"repository", "commit_sha", "path", "blob_sha"} or
            readback != {"repository": REPO, "commit_sha": anchor["commit_sha"],
                         "path": anchor["checkpoint_path"],
                         "blob_sha": anchor["checkpoint_blob_sha"]}):
        errors.append("GIT_READBACK_IDENTITY_MISMATCH")
    if (sha(checkpoint_bytes) != anchor["checkpoint_sha256"] or
            git_blob(checkpoint_bytes) != anchor["checkpoint_blob_sha"]):
        errors.append("CHECKPOINT_EXACT_BYTES_MISMATCH")
    try:
        checkpoint = parse(checkpoint_bytes)
        sidecar = parse(sidecar_bytes)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        return result(errors + ["STRICT_JSON_OR_BYTES_INVALID"])
    if not isinstance(checkpoint, dict) or set(checkpoint) != CHECKPOINT_KEYS:
        errors.append("NORMALIZED_CHECKPOINT_SCHEMA_INVALID")
    else:
        if (checkpoint["schema"] != CHECKPOINT_SCHEMA or
                checkpoint["lock_state"] != "EDITABLE_CURRENT" or
                checkpoint["activation_state"] != "NONACTIVE_ONLY"):
            errors.append("LOCKED_OR_ACTIVATION_STATE_INVALID")
        for key in FIELDS:
            if checkpoint[key] != anchor[key]:
                errors.append("CHECKPOINT_ANCHOR_DRIFT:" + key)
    if not isinstance(sidecar, dict) or set(sidecar) != EXPECTED_SIDECAR_KEYS:
        errors.append("SIDECAR_SCHEMA_INVALID")
    else:
        if (sidecar["schema"] != SIDECAR_SCHEMA or
                sidecar["status"] != "NONACTIVE_EXTERNAL_PIN" or
                sidecar["lock_state"] != "EDITABLE_CURRENT"):
            errors.append("SIDECAR_STATUS_INVALID")
        for key in ("workstream_id", "artifact_id",
                    "registered_source_sha256", "parent_artifact_sha256"):
            if sidecar[key] != anchor[key]:
                errors.append("SIDECAR_ANCHOR_DRIFT:" + key)
        if not isinstance(sidecar["roles"], dict) or set(sidecar["roles"]) != {
            "direct-import-tsv","canonical-json","source-output-map-tsv","qa-report"
        }:
            errors.append("SIDECAR_ROLE_INVENTORY_INVALID")
        if sha(sidecar_bytes) != anchor["authority_sidecar_sha256"]:
            errors.append("SIDECAR_EXACT_BYTES_MISMATCH")
        if isinstance(sidecar["roles"],dict):
            tsv = sidecar["roles"].get("direct-import-tsv")
            if (not isinstance(tsv,dict) or
                    tsv.get("sha256") != anchor["current_tsv_sha256"]):
                errors.append("DIRECT_TSV_IS_NOT_CHECKPOINT_CURRENT")
    if (not isinstance(writer_scopes, dict) or
            writer_scopes.get("status") != "DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL"
            or writer_scopes.get("scopes") != []):
        errors.append("WRITER_AUTHORIZATION_NOT_DENY_ALL")
    return result(errors)

def plan_recovery(*, write_occurred: bool, pinned_preimage_sha: str,
                  expected_written_sha: str, observed_remote_sha: str,
                  immutable_parent_sha256: str, verified_parent_sha256: str) -> dict:
    """Return advice only, never PUT/DELETE or silently move a CURRENT pointer."""
    if not all(hexof(x, 40) for x in (pinned_preimage_sha, expected_written_sha,
                                      observed_remote_sha)):
        return {"status":"BLOCKED", "reason":"MISSING_GIT_CAS_IDENTITY",
                "action":"STOP_NO_WRITE"}
    if not hexof(immutable_parent_sha256,64) or immutable_parent_sha256 != verified_parent_sha256:
        return {"status":"BLOCKED", "reason":"PARENT_RECOVERY_NOT_VERIFIED",
                "action":"STOP_NO_WRITE"}
    if not write_occurred:
        return {"status":"ABORT_CANDIDATE_KEEP_CURRENT",
                "reason":"NO_PRODUCTION_WRITE",
                "action":"KEEP_PINNED_CURRENT_UNCHANGED"}
    if observed_remote_sha != expected_written_sha:
        return {"status":"BLOCKED", "reason":"POSTWRITE_REMOTE_CAS_DRIFT",
                "action":"STOP_FOR_MANUAL_RECONCILIATION"}
    if pinned_preimage_sha == expected_written_sha:
        return {"status":"BLOCKED", "reason":"NO_DISTINCT_PREIMAGE",
                "action":"STOP_NO_WRITE"}
    return {"status":"MANUAL_CAS_RECOVERY_ELIGIBILITY_ONLY",
            "reason":"EXACT_POSTWRITE_OBSERVED_AND_PARENT_VERIFIED",
            "action":"REQUIRE_NEW_APPROVAL_AND_CAS_EXPECTED_POSTIMAGE",
            "performed_write":False}
