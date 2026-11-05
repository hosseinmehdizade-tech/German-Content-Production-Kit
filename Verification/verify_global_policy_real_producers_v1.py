#!/usr/bin/env python3
"""GFP-OPT P1: one exact central Stage5 policy -> real, independently pinned producers.

Read-only. GitHub CI covers code/policy/attacks but does NOT have private Library
ZIPs. Real output verification requires each complete original --archive ZIP.
Never certify newest CURRENT, original-source semantics, Stage4/6/7 from this gate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
POLICY_REGISTRY = "Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
PROFILE = "Optimization-Program/Control-Center/Profiles/P1-NEUTRAL-STAGE5-REAL-PRODUCERS-v1.json"
BINDING = "stage5_neutral_validator"
VALIDATOR = "Verification/validate_unified_vocabulary_projection_v1_1_0.py"
SCHEMA = "gfp-opt-policy-real-producer-conformance-profiles@1.0.0"
MAX_ZIP_UNCOMPRESSED = 150_000_000
MAX_TSV_BYTES = 35_000_000

class PolicyConformanceError(ValueError):
    pass

def guard(test: bool, code: str) -> None:
    if not test:
        raise PolicyConformanceError(code)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def blob_sha(data: bytes) -> str:
    """Git blob SHA-1, not a file SHA-1; supports offline exact pin readback."""
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def read_json(root: Path, relpath: str) -> dict:
    return json.loads((root / relpath).read_text(encoding="utf-8"))

def policy_authority(root: Path, profile: dict) -> tuple[str, Path]:
    guard(profile.get("schema") == SCHEMA
          and profile.get("program_id") == "GFP-OPT-2026"
          and profile.get("policy_binding_id") == BINDING
          and profile.get("policy_registry_path") == POLICY_REGISTRY,
          "PROFILE_OR_POLICY_OWNER_INVALID")
    registry_file = root / POLICY_REGISTRY
    guard(registry_file.is_file()
          and blob_sha(registry_file.read_bytes()) ==
          profile.get("policy_registry_git_blob"),
          "REGISTRY_BLOB_NOT_EXACT")
    registry = read_json(root, POLICY_REGISTRY)
    guard(registry.get("schema") == "gcpk-global-policy-registry@1.0.0"
          and registry.get("status") == "ACTIVE_PROSPECTIVE_POLICY_ROUTER_NOT_BULK_CONTENT_MIGRATION",
          "POLICY_REGISTRY_NOT_ACTIVE")
    binding = registry.get("policy_bindings", {}).get(BINDING, {})
    guard(binding.get("path") == VALIDATOR
          and binding.get("scope") == "NEUTRAL_VOCABULARY_PROJECTION"
          and binding.get("stages") == [5], "WRONG_POLICY_BINDING")
    validator = root / VALIDATOR
    guard(validator.is_file() and
          blob_sha(validator.read_bytes()) == binding.get("blob_sha"),
          "POLICY_VALIDATOR_BLOB_DRIFT")
    return binding["blob_sha"], validator

def verify_profile(profile: dict) -> None:
    guard(profile.get("policy_scope") ==
          "STAGE5_NEUTRAL_VOCABULARY_FORMAT_ONLY_NOT_SOURCE_FIRST_SEMANTIC_QA"
          and profile.get("snapshot_type") ==
          "EXACT_HISTORICAL_LIBRARY_ZIPS__NOT_CURRENTNESS",
          "HISTORICAL_SCOPE_PROMOTED")
    guard(profile.get("unverified_other_producers") ==
          "NOT_COVERED__NO_34_WORKSPACE_ADOPTION_PROMOTION",
          "FALSE_GLOBAL_PRODUCER_PASS")
    limits = profile.get("nonclaims", {})
    for key in (
        "newest_current_portable_verified", "all_producers_verified",
        "source_first_kombinationen_semantic_policy_certified",
        "independent_linguistic_stage4", "stage5_release_final",
        "stage6_native_browser", "stage7_release"
    ):
        guard(limits.get(key) is False, "FALSE_STAGE_OR_CURRENT_PASS:" + key)
    profiles = profile.get("profiles")
    guard(isinstance(profiles, list) and len(profiles) >= 2,
          "NO_TWO_SOURCE_WITNESS")
    ids, zips = set(), set()
    for item in profiles:
        guard(isinstance(item, dict), "INVALID_PRODUCER_PROFILE")
        ident = item.get("id")
        guard(isinstance(ident, str) and ident.startswith("producer:")
              and ident not in ids, "DUPLICATE_OR_BAD_PRODUCER_ID")
        ids.add(ident)
        for key in ("zip_sha256", "import_tsv_sha256"):
            value = item.get(key)
            guard(isinstance(value, str) and len(value) == 64
                  and all(ch in "0123456789abcdef" for ch in value),
                  "INVALID_DIGEST:" + key)
        name = item.get("zip_name")
        guard(isinstance(name, str) and name.endswith(".zip")
              and Path(name).name == name and name not in zips,
              "AMBIGUOUS_ZIP_ID")
        zips.add(name)
        member = item.get("import_tsv_member")
        guard(isinstance(member, str) and member.endswith(".tsv")
              and member and ".." not in Path(member).parts
              and not member.startswith("/") and "\\" not in member,
              "UNSAFE_IMPORT_MEMBER")
        guard(isinstance(item.get("expected_rows"), int)
              and item["expected_rows"] > 0
              and isinstance(item.get("source_value"), str)
              and bool(item["source_value"].strip())
              and item.get("claimed_gate") ==
              "FULL_REAL_ARCHIVE_BYTE_AND_NEUTRAL_FORMAT_ONLY",
              "INCORRECT_PRODUCER_SCOPE")
        guard(item.get("source_to_card_semantics") == "NOT_CHECKED",
              "FALSE_SEMANTIC_STAGE")
        for field in ("stage4_reverified", "stage5_release_promotion",
                      "stage6_browser", "stage7_final"):
            guard(item.get(field) is False, "FALSE_RELEASE_SCOPE:" + field)

def load_zip_rows(item: dict, archive_path: Path) -> tuple[list[dict], dict]:
    guard(archive_path.is_file() and not archive_path.is_symlink(),
          "ARCHIVE_NOT_REGULAR_FILE")
    guard(archive_path.name == item["zip_name"], "ARCHIVE_FILENAME_WRONG_PRODUCER")
    archive_bytes = archive_path.read_bytes()
    guard(sha256(archive_bytes) == item["zip_sha256"], "ARCHIVE_SHA_MISMATCH")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        infos = archive.infolist()
        names = [entry.filename for entry in infos]
        guard(len(names) == len(set(names)), "DUPLICATE_ZIP_MEMBER")
        guard(len(infos) <= 1000, "EXCESSIVE_MEMBER_COUNT")
        guard(sum(info.file_size for info in infos) <= MAX_ZIP_UNCOMPRESSED,
              "EXCESSIVE_UNCOMPRESSED_BYTES")
        for info in infos:
            name = info.filename
            guard(name and not name.startswith("/") and
                  ".." not in name.replace("\\", "/").split("/") and
                  "\\" not in name and ":" not in name,
                  "ZIP_PATH_TRAVERSAL")
            guard((info.external_attr >> 16) & 0o170000 != 0o120000,
                  "ZIP_SYMLINK_REFUSED")
            guard(info.flag_bits & 1 == 0, "ENCRYPTED_ZIP_MEMBER_REFUSED")
        guard(item["import_tsv_member"] in names, "MISSING_EXACT_IMPORT_MEMBER")
        guard(archive.testzip() is None, "ZIP_CRC_FAIL")
        member_info = archive.getinfo(item["import_tsv_member"])
        guard(member_info.file_size <= MAX_TSV_BYTES, "IMPORTED_TSV_TOO_LARGE")
        tsv = archive.read(item["import_tsv_member"])
    guard(sha256(tsv) == item["import_tsv_sha256"],
          "IMPORT_TSV_SHA_MISMATCH")
    reader = csv.DictReader(io.StringIO(tsv.decode("utf-8-sig"), newline=""),
                            delimiter="\t", strict=True)
    header = reader.fieldnames or []
    guard(len(header) == len(set(header))
          and {"id", "front", "back", "card_type", "category", "details", "custom_fields", "source"} <= set(header),
          "TSV_SCHEMA_MISMATCH")
    rows = list(reader)
    guard(len(rows) == item["expected_rows"], "TSV_ROW_COUNT_MISMATCH")
    guard(all(None not in row and
              row.get("id", "").strip() and
              row.get("source") == item["source_value"]
              for row in rows), "TSV_ROW_OR_SOURCE_MISMATCH")
    ids = [row["id"] for row in rows]
    guard(len(ids) == len(set(ids)), "DUPLICATE_CARD_ID")
    return rows, {
        "zip_sha256": item["zip_sha256"],
        "zip_member_count": len(names),
        "import_tsv_sha256": item["import_tsv_sha256"],
        "import_tsv_member": item["import_tsv_member"],
        "tsv_row_count": len(rows),
        "independent_zip_crc": "PASS",
        "source_value": item["source_value"]
    }

def audit(profile: dict, archive_paths: dict[str, Path], root: Path = ROOT,
          allow_partial: bool = False) -> dict:
    verify_profile(profile)
    binding_sha, validator_path = policy_authority(root, profile)
    mapping = {p["id"]: p for p in profile["profiles"]}
    guard(bool(archive_paths), "NO_REAL_ARCHIVES")
    guard(set(archive_paths) <= set(mapping), "UNKNOWN_PRODUCER")
    if not allow_partial:
        guard(set(archive_paths) == set(mapping), "MISSING_REQUIRED_PRODUCER")
    guard(len({str(p.resolve()) for p in archive_paths.values()}) ==
          len(archive_paths), "REUSED_ARCHIVE_PATH")
    spec = importlib.util.spec_from_file_location("gfp_opt_native_validator", validator_path)
    guard(spec is not None and spec.loader is not None, "VALIDATOR_IMPORT_FAIL")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = []
    for ident in sorted(archive_paths):
        item = mapping[ident]
        rows, integrity = load_zip_rows(item, archive_paths[ident])
        outcome = module.validate(rows)
        guard(outcome.get("status") == "PASS",
              "REAL_PRODUCER_NEUTRAL_POLICY_FAIL:" + ident + ":" +
              ",".join(str(x.get("error")) for x in outcome.get("errors", [])[:4]))
        output.append({
            "id": ident,
            "family_id": item["family_id"],
            "result": "PASS_FULL_REAL_ARCHIVE_STAGE5_NEUTRAL_FORMAT_ONLY",
            "validator_git_blob": binding_sha,
            "neutral_profile": outcome.get("neutral_schema_profile"),
            "presentation_contract": outcome.get("presentation_contract"),
            "validated_rows": outcome.get("cards"),
            **integrity
        })
    return {
        "schema": "gfp-opt-p1-cross-producer-policy-execution-receipt@1.0.0",
        "program_id": "GFP-OPT-2026",
        "status": "PASS_READONLY_EXACT_HISTORICAL_REAL_ARCHIVE_FORMAT_ONLY",
        "policy_binding_id": BINDING,
        "validator_git_blob": binding_sha,
        "verified_producers": len(output),
        "verified_real_rows": sum(x["validated_rows"] for x in output),
        "profiles_expected": len(mapping),
        "omitted_producers": sorted(set(mapping) - set(archive_paths)),
        "observations": output,
        "machine_semantic_stage4": "NOT_CHECKED",
        "native_browser_stage6": "NOT_CHECKED",
        "content_stage7_final": "NOT_CHECKED",
        "actual_currentness": "HISTORICAL_ZIP_HASH_ONLY",
        "app_runtime_ui_srs_fsrs_mutated": False,
        "original_and_locked_mutated": False,
        "all_34_git_workspaces_adopted": False,
        "github_ci_rehashed_private_archives": False
    }

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", default=PROFILE)
    ap.add_argument("--archive", action="append", default=[], metavar="PRODUCER_ID=PATH")
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()
    try:
        profile = read_json(ROOT, args.profile)
        targets: dict[str, Path] = {}
        for a in args.archive:
            ident, sep, p = a.partition("=")
            guard(bool(sep) and bool(ident) and bool(p) and
                  ident not in targets, "INVALID_OR_DUPLICATE_PRODUCER_ARGUMENT")
            targets[ident] = Path(p)
        result = audit(profile, targets, allow_partial=args.allow_partial)
        if args.report is not None:
            target = args.report
            guard(not target.exists() and target.suffix == ".json" and
                  target.resolve() not in {p.resolve() for p in targets.values()},
                  "REPORT_MUST_BE_NEW_AND_NOT_SOURCE")
            with target.open("x", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=False, indent=2, sort_keys=True)
                handle.write("\n")
    except (OSError, ValueError, UnicodeError, csv.Error, zipfile.BadZipFile) as exc:
        print("POLICY_REAL_PRODUCER_FAIL:" + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
