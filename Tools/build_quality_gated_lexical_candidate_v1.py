#!/usr/bin/env python3
"""Only candidate-release entrypoint for a NEW mutable lexical direct-import TSV.

The old governed launcher remains a format/byte gate, NOT a semantic release
authorization. This entrypoint refuses to build if any applicable QA evidence
is missing or fails; it does not mutate owner sources or learner data.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Verification"))
sys.path.insert(0,str(ROOT/"Tools"))
from guard_lexical_rule_coverage_v1 import evaluate
from verify_lexical_family_release_route_v1 import verify_family, ROUTE
from build_governed_clean_delivery_v1 import run as format_build,select_roles,sha256

def frozen_source_proofs(roles, stage4, review, router):
    """Capture exact source/Stage4/review/owner bytes BEFORE any gate or builder.

    A PASS quality evaluation is valid only for the snapshot that was reviewed.
    Never re-label a changed receipt or a changed source role as a successful
    Stage5 candidate. This helper is read-only and never edits input files.
    """
    paths={**roles, "stage4-receipt":stage4,
           "cross-tile-review":review, "canonical-router":router}
    out={}
    for name,path in paths.items():
        if not path.is_file() or path.is_symlink():
            raise ValueError("MISSING_OR_UNSAFE_STAGE5_PROOF_ROLE:"+name)
        out[name]=(path,sha256(path.read_bytes()))
    return out

def require_frozen_proofs(pins):
    for name,(path,expected) in pins.items():
        if (not path.is_file() or path.is_symlink() or
                sha256(path.read_bytes())!=expected):
            raise ValueError("SOURCE_OR_PROOF_CHANGED_DURING_STAGE5:"+name)

def verify_governed_build(output_zip, built, pins, quality, family):
    """A returned PASS is not enough: bind every role and the actual ZIP bytes."""
    if (not isinstance(built,dict) or
            built.get("status")!="PASS_GOVERNED_STAGE5_FORMAT_AND_BYTE_PARITY_ONLY"):
        raise ValueError("GOVERNED_FORMAT_BUILD_NOT_PASS")
    role_hashes=built.get("source_role_sha256")
    if (not isinstance(role_hashes,dict) or
            role_hashes!={name:pins[name][1] for name in
                          ("direct-import-tsv","canonical-json",
                           "source-output-map-tsv","qa-report")}):
        raise ValueError("GOVERNED_STAGE5_ROLE_HASH_MISMATCH")
    if quality.get("source_tsv_sha256")!=pins["direct-import-tsv"][1]:
        raise ValueError("QUALITY_GATE_TSV_NOT_FROZEN_SOURCE")
    if family.get("route_file_sha256")!=pins["canonical-router"][1]:
        raise ValueError("FAMILY_ROUTER_CHANGED_BEFORE_BUILD")
    if not output_zip.is_file() or output_zip.is_symlink():
        raise ValueError("GOVERNED_STAGE5_OUTPUT_NOT_REGULAR")
    zip_hash=built.get("output_zip_sha256")
    if (not isinstance(zip_hash,str) or len(zip_hash)!=64 or
            any(c not in "0123456789abcdef" for c in zip_hash) or
            sha256(output_zip.read_bytes())!=zip_hash):
        raise ValueError("GOVERNED_STAGE5_OUTPUT_BYTES_MISMATCH")
    return zip_hash

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_dir",type=Path)
    p.add_argument("output_zip",type=Path)
    p.add_argument("--receipt",type=Path,required=True)
    p.add_argument("--policy-report",type=Path,required=True)
    p.add_argument("--stage4-receipt",type=Path,required=True)
    p.add_argument("--cross-tile-review",type=Path,required=True)
    p.add_argument("--family-id",required=True,help="Registered canonical family:... ID")
    a=p.parse_args()
    try:
        selected=(a.output_zip,a.receipt,a.policy_report)
        if any(x.exists() or x.is_symlink() for x in selected):
            raise ValueError("OUTPUT_OR_RECEIPT_ALREADY_EXISTS")
        if len({x.resolve() for x in selected})!=3:
            raise ValueError("OUTPUT_PATH_ROLE_COLLISION")
        roles=select_roles(a.source_dir)
        pins=frozen_source_proofs(roles,a.stage4_receipt,a.cross_tile_review,
                                  ROOT/ROUTE)
        family=verify_family(a.family_id,a.cross_tile_review)
        require_frozen_proofs(pins)
        tsv=roles["direct-import-tsv"]
        quality=evaluate(tsv,a.stage4_receipt,a.cross_tile_review)
        if quality["status"]!="PASS_FOR_GOVERNED_STAGE5_CANDIDATE_ONLY":
            print(json.dumps({"status":"BLOCKED_BEFORE_PACKAGING",
                "source_sha256":quality["source_tsv_sha256"],
                "cross_tile":quality["cross_tile"],
                "blockers":quality["blockers"][:30]},ensure_ascii=False),file=sys.stderr)
            return 2
        require_frozen_proofs(pins)
        output=format_build(a.source_dir,a.output_zip,a.receipt)
        require_frozen_proofs(pins)
        zip_hash=verify_governed_build(a.output_zip,output,pins,quality,family)
        report={"schema":"gcpk-lexical-quality-gated-stage5-candidate@1.0.0",
                "status":"PASS_STAGE5_CANDIDATE_WITH_EXACT_SOURCE_STAGE4_AND_RULE_COVERAGE",
                "quality_gate":quality,"family_authority":family,
                "governed_format_build":output,
                "exact_stage4_receipt_sha256":pins["stage4-receipt"][1],
                "exact_cross_tile_review_sha256":pins["cross-tile-review"][1],
                "exact_all_source_roles_sha256":{
                    name:pins[name][1] for name in
                    ("direct-import-tsv","canonical-json",
                     "source-output-map-tsv","qa-report")},
                "exact_governed_output_zip_sha256":zip_hash,
                "stage6":"NOT_RUN","stage7":"NOT_FINAL",
                "source_and_srs_untouched":True}
        with a.policy_report.open("x",encoding="utf-8") as f:
            json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
        print(json.dumps({"status":report["status"],
             "quality_receipt":str(a.policy_report),
             "zip_sha256":output["output_zip_sha256"]},ensure_ascii=False))
        return 0
    except (OSError,ValueError,UnicodeError) as e:
        print("LEXICAL_CANDIDATE_BLOCKED:"+str(e),file=sys.stderr)
        print("Any ZIP without BOTH verified receipts is NOT approved.",file=sys.stderr)
        return 2
if __name__=="__main__":raise SystemExit(main())
