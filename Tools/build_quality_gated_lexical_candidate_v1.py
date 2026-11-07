#!/usr/bin/env python3
"""Only candidate-release entrypoint for a NEW mutable lexical direct-import TSV.

The old governed launcher remains a format/byte gate, NOT a semantic release
authorization. This entrypoint refuses to build if any applicable QA evidence
is missing or fails; it does not mutate owner sources or learner data.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Verification"))
sys.path.insert(0,str(ROOT/"Tools"))
from guard_lexical_rule_coverage_v1 import evaluate
from build_governed_clean_delivery_v1 import run as format_build,select_roles,sha256

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_dir",type=Path)
    p.add_argument("output_zip",type=Path)
    p.add_argument("--receipt",type=Path,required=True)
    p.add_argument("--policy-report",type=Path,required=True)
    p.add_argument("--stage4-receipt",type=Path,required=True)
    p.add_argument("--cross-tile-review",type=Path,required=True)
    a=p.parse_args()
    try:
        selected=(a.output_zip,a.receipt,a.policy_report)
        if any(x.exists() or x.is_symlink() for x in selected):
            raise ValueError("OUTPUT_OR_RECEIPT_ALREADY_EXISTS")
        if len({x.resolve() for x in selected})!=3:
            raise ValueError("OUTPUT_PATH_ROLE_COLLISION")
        roles=select_roles(a.source_dir)
        tsv=roles["direct-import-tsv"]
        quality=evaluate(tsv,a.stage4_receipt,a.cross_tile_review)
        if quality["status"]!="PASS_FOR_GOVERNED_STAGE5_CANDIDATE_ONLY":
            print(json.dumps({"status":"BLOCKED_BEFORE_PACKAGING",
                "source_sha256":quality["source_tsv_sha256"],
                "cross_tile":quality["cross_tile"],
                "blockers":quality["blockers"][:30]},ensure_ascii=False),file=sys.stderr)
            return 2
        output=format_build(a.source_dir,a.output_zip,a.receipt)
        if sha256(tsv.read_bytes())!=quality["source_tsv_sha256"]:
            raise ValueError("SOURCE_CHANGED_AFTER_POLICY_GATE")
        report={"schema":"gcpk-lexical-quality-gated-stage5-candidate@1.0.0",
                "status":"PASS_STAGE5_CANDIDATE_WITH_EXACT_SOURCE_STAGE4_AND_RULE_COVERAGE",
                "quality_gate":quality,"governed_format_build":output,
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
