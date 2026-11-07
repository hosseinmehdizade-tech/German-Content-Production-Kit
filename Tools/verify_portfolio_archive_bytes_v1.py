#!/usr/bin/env python3
"""Verify exact downloaded curated ZIP bytes against accepted portfolio SHA-256.

This is an on-demand LOCAL binary verifier. It cannot download from private
Library or Drive on GitHub CI, cannot accept a new release, and never writes a
source, a user profile, or a registry pointer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

REGISTRY="Optimization-Program/Control-Center/DYNAMIC-CONTENT-PORTFOLIO-REGISTRY-v1.json"
EVIDENCE="Optimization-Program/Control-Center/Provider-Observations/2026-11-07-EXACT-BYTE-EVIDENCE.json"

def records(root:Path):
    p=json.loads((root/REGISTRY).read_text(encoding="utf-8"))
    result={}
    for row in p["items"]:
        fid=row["id"]
        if fid in result:
            raise ValueError("Duplicate family in registry")
        result[fid]=row["active_baseline"]
    if len(result)!=10:
        raise ValueError("Exactly 10 registered families required")
    return result

def verify_file(path:Path,expected_sha:str,expected_size:int):
    path=path.resolve(strict=True)
    if not path.is_file() or path.suffix.lower()!=".zip":
        raise ValueError("A real ZIP file is required")
    h=hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda:fp.read(1024*1024),b""):
            h.update(chunk)
    sha=h.hexdigest()
    try:
        with zipfile.ZipFile(path) as z:
            member_count=len(z.infolist())
            bad_member=z.testzip()
    except (zipfile.BadZipFile,OSError,EOFError) as e:
        return {"status":"FAIL_INVALID_ZIP","sha256":sha,"file_size_bytes":path.stat().st_size,
                "error":type(e).__name__}
    size=path.stat().st_size
    status="PASS_EXACT_SHA256_AND_ZIP_CRC" if (sha==expected_sha and size==expected_size and bad_member is None) else "FAIL_BYTES_OR_ZIP_CRC"
    return {"status":status,"file_size_bytes":size,"sha256":sha,
            "zip_entries":member_count,"zip_crc_pass":bad_member is None,
            "expected_sha256":expected_sha,"expected_size_bytes":expected_size}

def verify_recorded_as_of(root:Path):
    """Check historical evidence metadata, not rehash any missing downloaded file."""
    known=records(root)
    report=json.loads((root/EVIDENCE).read_text(encoding="utf-8"))
    if report.get("schema")!="gfp-opt-curated-portfolio-exact-byte-evidence@1.0.0":
        raise ValueError("Unexpected evidence schema")
    entries=report.get("evidence")
    if not isinstance(entries,list) or len(entries)!=11:
        raise ValueError("Expected eleven historic binary observations")
    seen=set()
    for entry in entries:
        key=(entry.get("family_id"),entry.get("provider"))
        if key in seen or key[0] not in known or key[1] not in ("google_drive","library"):
            raise ValueError("Duplicate/unknown provider observation")
        seen.add(key)
        base=known[key[0]]
        if (entry.get("artifact_name")!=base.get("artifact_name")
            or entry.get("measured_size_bytes")!=base.get("artifact_size_bytes")
            or entry.get("expected_sha256")!=base.get("artifact_sha256")
            or entry.get("measured_sha256")!=base.get("artifact_sha256")
            or entry.get("comparison")!="PASS_EXACT_SOURCE_ACCEPTED_SHA256"
            or entry.get("zip_crc_test")!="PASS_ALL_MEMBERS"
            or type(entry.get("zip_entries")) is not int or entry["zip_entries"]<=0):
            raise ValueError("Recorded observation disagrees with accepted baseline")
    if {x[0] for x in seen}!={x for x in known if x!="family:menschen-a1-verben"}:
        raise ValueError("Unexpected verified-family set")
    if len([k for k in seen if k[1]=="library"])!=4 or len([k for k in seen if k[1]=="google_drive"])!=7:
        raise ValueError("Unexpected provider observation counts")
    for fam in ("family:menschen-a2-verben","family:nomen-verb-verbindungen"):
        if (fam,"google_drive") not in seen or (fam,"library") not in seen:
            raise ValueError("Missing cross-provider repeat")
    if report.get("distinct_families_reverified")!=9 or not report.get("all_measured_sha256_and_zip_crc_pass"):
        raise ValueError("Evidence statement mismatch")
    if report.get("unresolved_families",[{}])[0].get("family_id")!="family:menschen-a1-verben":
        raise ValueError("Unresolved family not preserved")
    return {"status":"PASS_RECORDED_AS_OF_METADATA_CONSISTENCY__NO_LIVE_BINARY_REHASH",
            "families_with_measured_zip_bytes":9,"provider_byte_observations":11,
            "current_source_bytes_rehashed_now":False,
            "unresolved":"family:menschen-a1-verben"}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check-recorded",action="store_true",help="Static as-of proof consistency only; no binary rerun")
    parser.add_argument("--family",help="Exact family ID to verify from raw downloaded ZIP")
    parser.add_argument("--file",type=Path,help="Raw local ZIP from Library/Drive, not a Git metadata record")
    args=parser.parse_args(argv)
    try:
        root=args.repo_root.resolve()
        if args.check_recorded and not (args.family or args.file):
            result=verify_recorded_as_of(root)
        elif args.family and args.file and not args.check_recorded:
            known=records(root)
            if args.family not in known:
                raise ValueError("Unregistered family")
            b=known[args.family]
            if args.file.name!=b["artifact_name"]:
                raise ValueError("ZIP filename differs from accepted current artifact")
            result=verify_file(args.file,b["artifact_sha256"],b["artifact_size_bytes"])
            result["family_id"]=args.family
            result["result_scope"]="RAW_DOWNLOADED_ZIP_ONLY__NO_STAGE_OR_SRS_PROMOTION"
        else:
            parser.error("Choose --check-recorded OR --family ... --file ...")
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result["status"].startswith("PASS") else 2
    except (ValueError,KeyError,OSError,TypeError,json.JSONDecodeError) as e:
        print(json.dumps({"status":"HOLD_INVALID_INPUT_OR_MISSING_ARTIFACT","reason":type(e).__name__+": "+str(e)[:250]}))
        return 2

if __name__=="__main__":
    sys.exit(main())
