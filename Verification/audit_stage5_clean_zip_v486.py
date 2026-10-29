#!/usr/bin/env python3
"""OP-02 NONACTIVE post-build Stage5 clean ZIP / exact v486 consumer audit.

Reads the *finished ZIP bytes*, never modifies it and never builds/releases a
production ZIP. Stage4 independent AI review and source fidelity are NOT
created by this deterministic contract/receipt test.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import re
import stat
import sys
import zipfile

from validate_stage45_teaching_delta_parity import (
    sha, hexsha, read_json, load_tsv,
)
from validate_stage45_v486_consumer_bridge import validate as validate_bridge
from validate_unified_vocabulary_projection_v1_1_0 import validate as neutral_validate

SCHEMA = "gcpk-op02-stage5-clean-zip-v486-postbuild@1"
STATUS = "NONACTIVE_VERSIONED_DRY_RUN"
ROOT = "CONTENT-DELIVERY/"
REQUIRED_ROLES = ("direct-import-tsv", "canonical-json",
                  "source-output-map-tsv", "qa-report")
MAX_ZIP_BYTES = 80_000_000
MAX_TOTAL_BYTES = 150_000_000
MAX_FILE_BYTES = 80_000_000
MAX_MEMBERS = 32
SHA_LINE = re.compile(r"([0-9a-f]{64})  ([^/\x00\r\n\\]+)\Z")


def _read_safe_zip(blob: bytes) -> dict[str, bytes]:
    if len(blob) > MAX_ZIP_BYTES:
        raise ValueError("STAGE5_ZIP_TOO_LARGE")
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            info = z.infolist()
            names = [i.filename for i in info]
            if (not names or len(names) > MAX_MEMBERS or
                    len(names) != len(set(names)) or
                    sum(i.file_size for i in info) > MAX_TOTAL_BYTES):
                raise ValueError("STAGE5_ZIP_INVENTORY_UNSAFE")
            for i in info:
                p = i.filename
                if (not p.startswith(ROOT) or
                        p == ROOT or p.count("/") != 1 or
                        "\\" in p or ":" in p or
                        i.is_dir() or i.flag_bits & 1 or
                        i.file_size > MAX_FILE_BYTES or
                        (i.external_attr >> 16) & 0o170000 == 0o120000 or
                        p.split("/", 1)[1] in (".", "..")):
                    raise ValueError("STAGE5_ZIP_MEMBER_UNSAFE")
            if z.testzip() is not None:
                raise ValueError("STAGE5_ZIP_CRC_MISMATCH")
            return {i.filename[len(ROOT):]: z.read(i) for i in info}
    except (zipfile.BadZipFile, RuntimeError, OSError, UnicodeError) as exc:
        raise ValueError("STAGE5_ZIP_CORRUPT_OR_UNREADABLE") from exc


def audit(zip_blob: bytes, expected_zip_sha: str, stage4_bytes: bytes,
          stage4_review_bytes: bytes, stage45: dict,
          bridge: dict) -> dict:
    problems: list[str] = []

    def blocked(code: str):
        problems.append(code)

    if not hexsha(expected_zip_sha) or sha(zip_blob) != expected_zip_sha:
        return {"status": "BLOCKED", "errors": ["EXACT_POSTBUILD_ZIP_SHA_MISMATCH"]}
    try:
        files = _read_safe_zip(zip_blob)
        manifest_bytes = files.get("DELIVERY-MANIFEST.json")
        sums_bytes = files.get("SHA256SUMS.txt")
        if not isinstance(manifest_bytes, bytes) or not isinstance(sums_bytes, bytes):
            raise ValueError("STAGE5_INTERNAL_MANIFEST_MISSING")
        declared_sums = {}
        for line in sums_bytes.decode("utf-8").splitlines():
            match = SHA_LINE.fullmatch(line)
            if not match or match[2] in declared_sums or match[2] == "SHA256SUMS.txt":
                raise ValueError("STAGE5_SHA256SUMS_INVALID_OR_DUPLICATE")
            declared_sums[match[2]] = match[1]
        actual = {p: sha(b) for p, b in files.items() if p != "SHA256SUMS.txt"}
        if not declared_sums or declared_sums != actual:
            raise ValueError("STAGE5_INTERNAL_SHA256SUMS_CONTENT_MISMATCH")
        manifest = read_json(manifest_bytes)
        if not isinstance(manifest, dict) or not isinstance(manifest.get("roles"), dict):
            raise ValueError("STAGE5_DELIVERY_MANIFEST_NOT_OBJECT")
        if (manifest.get("artifact_type") != "clean-content-delivery" or
                manifest.get("required_card_type") != "de-vocabulary" or
                manifest.get("required_presentation_contract") !=
                "gfp-vocabulary-neutral@1"):
            raise ValueError("STAGE5_DELIVERY_MANIFEST_POLICY_DRIFT")
        roles = manifest["roles"]
        if set(roles) != set(REQUIRED_ROLES):
            raise ValueError("STAGE5_DELIVERY_ROLES_MISMATCH")
        paths = [roles[k] for k in REQUIRED_ROLES]
        if (any(not isinstance(p, str) or p not in files or
                "/" in p or "\\" in p or p in
                ("DELIVERY-MANIFEST.json", "SHA256SUMS.txt") for p in paths)
                or len(set(paths)) != len(paths)):
            raise ValueError("STAGE5_ROLE_MISSING_OR_REUSED")
        if set(files) != set(paths) | {"DELIVERY-MANIFEST.json", "SHA256SUMS.txt"}:
            raise ValueError("STAGE5_UNEXPECTED_OR_MISSING_MEMBER")
        direct = files[roles["direct-import-tsv"]]
        if not roles["direct-import-tsv"].lower().endswith(".tsv"):
            raise ValueError("STAGE5_DIRECT_IMPORT_NOT_TSV")
        rows = load_tsv(direct)
        neutral = neutral_validate(rows)
        if neutral["status"] != "PASS":
            blocked("STAGE5_EXTRACTED_NEUTRAL_PROJECTION_NOT_PASS")
    except (ValueError, TypeError, KeyError, UnicodeError, OverflowError) as exc:
        return {"status": "BLOCKED", "errors": ["STAGE5_POSTBUILD_ARCHIVE_INVALID:" + str(exc)]}

    # No alternate 'raw' pre-package TSV is accepted by this audit: the only
    # bytes passed to both semantic validators are the *post-build ZIP member*.
    outcome = validate_bridge(stage45, bridge, stage4_bytes,
                              stage4_review_bytes, direct)
    if outcome["status"] != "PASS_SCOPED_DETERMINISTIC_CONSUMER_PROFILE_ONLY":
        blocked("STAGE5_PACKAGED_SEMANTIC_OR_VIEW_PARITY_BLOCKED")
        problems.extend(outcome.get("errors", []))

    return {
        "schema": "gcpk-op02-stage5-clean-zip-v486-postbuild-result@1",
        "status": "PASS_SCOPED_NONACTIVE_EXACT_PACKAGED_TSV_ONLY"
                  if not problems else "BLOCKED",
        "errors": sorted(set(problems)),
        "zip_sha256": expected_zip_sha,
        "packaged_tsv_sha256": sha(direct),
        "packaged_member_count": len(files),
        "semantic_profile": outcome.get("status"),
        "card_count": len(rows),
        "not_proven": [
            "A true independent Stage4 AI semantic and registered-source review",
            "Full organized vocabulary-production release ZIP (this audits only clean Stage5 delivery)",
            "Active/importer schema or writer approval",
            "Real learner data or full Stage6/Stage7 release",
            "Git/Library persistence, CURRENT program promotion or licensing",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip", type=Path, required=True)
    ap.add_argument("--zip-sha256", required=True)
    ap.add_argument("--stage4", type=Path, required=True)
    ap.add_argument("--stage4-review", type=Path, required=True)
    ap.add_argument("--stage45-contract", type=Path, required=True)
    ap.add_argument("--bridge-contract", type=Path, required=True)
    args = ap.parse_args()
    try:
        result = audit(
            args.zip.read_bytes(), args.zip_sha256,
            args.stage4.read_bytes(), args.stage4_review.read_bytes(),
            read_json(args.stage45_contract.read_bytes()),
            read_json(args.bridge_contract.read_bytes()),
        )
    except (OSError, TypeError, ValueError, UnicodeError) as exc:
        result = {"status": "BLOCKED", "errors": ["INPUT_OR_CONTRACT_INVALID:" + str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "PASS_SCOPED_NONACTIVE_EXACT_PACKAGED_TSV_ONLY" else 2


if __name__ == "__main__":
    sys.exit(main())
