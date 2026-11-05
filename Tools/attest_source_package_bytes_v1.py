#!/usr/bin/env python3
"""Read-only byte-bound source/package evidence attestation.

A dated profile is NOT a current-version resolver, a linguistic verdict or a
runtime release. The tool never changes source, package, Checkpoint, or app.
A scoped approved embedded Stage4 gate can be rerun only when its exact Git
blob hash is pinned in the profile; arbitrary archive scripts are not run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import zipfile

SCHEMA = "gcpk-source-package-byte-attestation@1.0.0"
PROFILE_SCHEMA = "gcpk-scoped-byte-attestation-profile@1.0.0"
MAX_FILES = 1000
MAX_UNCOMPRESSED = 160 * 1024 * 1024


class AttestationBlocked(Exception):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def require(condition, code):
    if not condition:
        raise AttestationBlocked(code)


def safe_member(name: str) -> bool:
    if not isinstance(name, str) or not name or "\\" in name or "\0" in name:
        return False
    p = PurePosixPath(name)
    return not p.is_absolute() and ".." not in p.parts and str(p) == name


def check_manifest(z: zipfile.ZipFile) -> dict:
    members = z.infolist()
    require(0 < len(members) <= MAX_FILES, "ZIP_MEMBER_COUNT_INVALID")
    require(len({x.filename for x in members}) == len(members), "ZIP_DUPLICATE_MEMBER")
    payloads = {}
    total = 0
    for info in members:
        require(safe_member(info.filename), "UNSAFE_ZIP_MEMBER_PATH")
        require(not stat.S_ISLNK(info.external_attr >> 16), "ZIP_SYMLINK_FORBIDDEN")
        require(not bool(info.flag_bits & 0x1), "ENCRYPTED_ZIP_FORBIDDEN")
        require(info.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED),
                "UNSUPPORTED_COMPRESSION_METHOD")
        total += info.file_size
        require(total <= MAX_UNCOMPRESSED, "ZIP_UNCOMPRESSED_LIMIT_EXCEEDED")
        require(not info.is_dir(), "DIRECTORY_MEMBER_NOT_ALLOWED")
        payloads[info.filename] = z.read(info)
    require(z.testzip() is None, "ZIP_CRC_FAILURE")
    require("SHA256SUMS.txt" in payloads, "MISSING_SHA256_MANIFEST")
    try:
        lines = payloads["SHA256SUMS.txt"].decode("utf-8").splitlines()
    except UnicodeError:
        raise AttestationBlocked("MANIFEST_NON_UTF8")
    declared = {}
    for line in lines:
        match = re.fullmatch(r"([a-f0-9]{64})  ([^\r\n]+)", line)
        require(bool(match), "MANIFEST_INVALID_ENTRY")
        digest, name = match.groups()
        require(safe_member(name), "UNSAFE_MANIFEST_PATH")
        require(name not in declared, "MANIFEST_DUPLICATE_ENTRY")
        declared[name] = digest
    require(set(declared) == (set(payloads) - {"SHA256SUMS.txt"}),
            "MANIFEST_NOT_EXACT_COVERAGE")
    for name, expected in declared.items():
        require(sha256_bytes(payloads[name]) == expected, "MEMBER_SHA256_MISMATCH:" + name)
    return {"members": payloads, "manifest_entries": len(declared),
            "member_count": len(payloads), "total_uncompressed": total}


def profile_format(profile):
    require(isinstance(profile, dict) and profile.get("schema") == PROFILE_SCHEMA,
            "INVALID_PROFILE_SCHEMA")
    fields = ("workstream", "artifact_filename", "artifact_sha256",
              "artifact_size_bytes", "original_source_sha256",
              "original_source_member", "content_member", "content_sha256")
    require(all(profile.get(x) is not None for x in fields), "PROFILE_REQUIRED_FIELD_MISSING")
    for key in ("artifact_sha256", "original_source_sha256", "content_sha256"):
        require(isinstance(profile[key], str)
                and re.fullmatch(r"[a-f0-9]{64}", profile[key]), "INVALID_PROFILE_HASH:" + key)
    for key in ("original_source_member", "content_member"):
        require(safe_member(profile[key]), "UNSAFE_PROFILE_MEMBER")
    require(type(profile["artifact_size_bytes"]) is int and profile["artifact_size_bytes"] > 0,
            "INVALID_PROFILE_ARTIFACT_SIZE")
    gate = profile.get("pinned_stage4_gate")
    if gate is not None:
        require(isinstance(gate, dict), "INVALID_GATE_PROFILE")
        require(all(safe_member(gate.get(k)) for k in ("script_member", "policy_member",
                                                       "risk_receipt_member")),
                "UNSAFE_STAGE4_GATE_MEMBER")
        for key in ("script_git_blob_sha", "policy_git_blob_sha"):
            require(isinstance(gate.get(key), str) and re.fullmatch(r"[a-f0-9]{40}", gate[key]),
                    "INVALID_STAGE4_GATE_GIT_PIN")
    return profile


def rerun_gate(payloads, gate, content_member):
    script = gate["script_member"]
    policy = gate["policy_member"]
    receipt = gate["risk_receipt_member"]
    require(all(x in payloads for x in (script, policy, receipt)),
            "STAGE4_GATE_SOURCE_MISSING_FROM_PACKAGE")
    require(git_blob_sha(payloads[script]) == gate["script_git_blob_sha"],
            "STAGE4_GATE_SCRIPT_PIN_MISMATCH")
    require(git_blob_sha(payloads[policy]) == gate["policy_git_blob_sha"],
            "STAGE4_GATE_POLICY_PIN_MISMATCH")
    with tempfile.TemporaryDirectory(prefix="gcpk-attest-stage4-") as tmp:
        root = Path(tmp)
        # Extract only exact validated Python gate, risk policy, receipt, source TSV.
        needed = (script, policy, receipt, content_member)
        for name in needed:
            dst = root.joinpath(*PurePosixPath(name).parts)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(payloads[name])
        cmd = [sys.executable, "-I", "-B", str(root / script),
               "--policy", str(root / policy),
               "--receipt", str(root / receipt),
               "--current-bytes", str(root / content_member)]
        try:
            result = subprocess.run(cmd, cwd=root, capture_output=True,
                                    text=True, timeout=30, check=False,
                                    env={"PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1",
                                         "PATH": os.environ.get("PATH", "")})
        except subprocess.TimeoutExpired:
            raise AttestationBlocked("STAGE4_GATE_TIMED_OUT")
        require(result.returncode == 0, "STAGE4_GATE_EXIT_NONZERO")
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise AttestationBlocked("STAGE4_GATE_NON_JSON")
        require(data.get("status") == "PASS_RISK_BASED_STAGE4"
                and data.get("blockers") == [], "STAGE4_GATE_REJECTED")
    return {"status": "RERUN_PASS_RISK_BASED_STAGE4_EXACT_PINNED_SCRIPT_AND_BYTES",
            "meaning": "Risk evidence admissible, NOT full linguistic correctness or Stage5/6/7",
            "script_git_blob_sha": gate["script_git_blob_sha"],
            "policy_git_blob_sha": gate["policy_git_blob_sha"]}


def attest(profile, archive: Path, source: Path):
    profile_format(profile)
    require(archive.is_file() and source.is_file(), "ARTIFACT_OR_SOURCE_NOT_MOUNTED")
    require(archive.name == profile["artifact_filename"], "ARTIFACT_FILENAME_MISMATCH")
    require(archive.stat().st_size == profile["artifact_size_bytes"], "ARTIFACT_SIZE_MISMATCH")
    require(sha256_file(archive) == profile["artifact_sha256"], "ARTIFACT_SHA256_MISMATCH")
    require(sha256_file(source) == profile["original_source_sha256"],
            "ORIGINAL_SOURCE_SHA256_MISMATCH")
    try:
        with zipfile.ZipFile(archive) as z:
            bundle = check_manifest(z)
    except (zipfile.BadZipFile, RuntimeError, OSError, EOFError):
        raise AttestationBlocked("UNSAFE_OR_CORRUPT_ARCHIVE")
    members = bundle.pop("members")
    require(profile["original_source_member"] in members,
            "PACKAGE_ORIGINAL_SOURCE_MEMBER_MISSING")
    require(profile["content_member"] in members, "PACKAGE_CONTENT_MEMBER_MISSING")
    require(sha256_bytes(members[profile["original_source_member"]])
            == profile["original_source_sha256"], "EMBEDDED_SOURCE_SHA256_MISMATCH")
    require(source.read_bytes() == members[profile["original_source_member"]],
            "SOURCE_BYTE_READBACK_MISMATCH")
    require(sha256_bytes(members[profile["content_member"]])
            == profile["content_sha256"], "CONTENT_SHA256_MISMATCH")
    result = {"schema": SCHEMA,
              "status": "PASS_EXACT_SOURCE_PACKAGE_BYTES_AND_MANIFEST__SCOPED_NOT_FINAL",
              "workstream": profile["workstream"],
              "artifact": {"filename": archive.name,
                           "sha256_verified": profile["artifact_sha256"],
                           "bytes": archive.stat().st_size},
              "original_source_sha256_verified": profile["original_source_sha256"],
              "embedded_source_identical_to_external": True,
              "content_member": profile["content_member"],
              "content_sha256_verified": profile["content_sha256"],
              "manifest_entries_verified": bundle["manifest_entries"],
              "zip_members": bundle["member_count"],
              "crc": "PASS", "unsafe_members": 0,
              "stage4_gate": {"status": "NOT_RERUN"},
              "stage5_final": "NOT_ATTESTED",
              "stage6_real_browser": "NOT_ATTESTED",
              "stage7_release": "NOT_ATTESTED",
              "original_and_artifact_files_mutated": False}
    if profile.get("pinned_stage4_gate"):
        result["stage4_gate"] = rerun_gate(
            members, profile["pinned_stage4_gate"], profile["content_member"])
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=Path, required=True)
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--original-source", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    try:
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        report = attest(profile, args.archive, args.original_source)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (AttestationBlocked, ValueError, OSError, json.JSONDecodeError) as e:
        print(json.dumps({"schema": SCHEMA, "status": "BLOCKED", "reason": str(e),
                          "stage_accepted": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
