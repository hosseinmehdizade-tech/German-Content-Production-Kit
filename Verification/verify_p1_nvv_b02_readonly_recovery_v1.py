#!/usr/bin/env python3
"""Fail-closed metadata verification for P1 NVV B02 read-only parent recovery.

CI does not possess the user's private Library files. Authenticated actual ZIP
and rematerialized bytes were compared separately and pinned in the receipt.
This verifies the exact immutable Git source-owner scope only; NEVER ADOPTED.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPORT="Optimization-Program/Verification/P1-NVV-B02-READONLY-PARENT-BASELINE-LIBRARY-RECOVERY-20261105.json"
STAGE5="Workspaces/nomen-verb-verbindungen/B01-STAGE5-NATIVE-CLEAN-DELIVERY-PASS-20261105.json"
STAGE7="Workspaces/nomen-verb-verbindungen/B01-STAGE7-USER-ACCEPTED-CONTENT-RELEASE-20261105.json"
STAGE5_BLOB="c52200ee4b4455d3bec42c59d2410b55e4671593"
STAGE7_BLOB="c8131732ed001a9d115660a3ef2ce3b9198d63b4"

class VerificationError(ValueError): pass
def require(cond,reason):
    if not cond:raise VerificationError(reason)
def git_blob(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def sha64(s):
    return bool(isinstance(s,str) and re.fullmatch("[a-f0-9]{64}",s))
def load_pinned(root:Path,path:str,expected_blob:str):
    require(isinstance(path,str) and not path.startswith("/") and
            ".." not in Path(path).parts,"UNSAFE_GIT_PATH")
    f=root/path
    require(f.is_file() and not f.is_symlink() and
            f.resolve().is_relative_to(root.resolve()),"GIT_SOURCE_MISSING")
    b=f.read_bytes()
    require(git_blob(b)==expected_blob,"GIT_SOURCE_BLOB_DRIFT")
    return json.loads(b)
def verify(root=ROOT,receipt=None):
    root=Path(root)
    d=receipt if receipt is not None else json.loads((root/REPORT).read_text(encoding="utf8"))
    require(d["schema"]=="gfp-opt-p1-nvv-b02-parent-baseline-recovery@1.0.0" and
            d["status"]=="PASS_PROVIDER_READBACK_100_EXACT_PARENT_CARDS__ORIGINAL_STAGE3_WORKING_MISSING__STAGE4_HOLD" and
            d["family"]=="family:nomen-verb-verbindungen" and
            d["workspace"]=="workspace:nomen-verb-verbindungen" and
            d["batch"]=="B02", "RECOVERY_SCOPE_INVALID")
    r=d["source_owner"]
    require(r["path"]=="Workspaces/nomen-verb-verbindungen/B02-SOURCE-FIRST-RECOVERY-20261105.json" and
            r["git_blob"]=="bc50c938ed83486523cf2c96cab9da03b33896dd","OWNER_RECOVERY_PIN_INVALID")
    own=load_pinned(root,r["path"],r["git_blob"])
    require(own["schema"]=="nvv-b02-source-first-github-recovery@1" and
            own["status"]=="STAGE3_EDITABLE_RECOVERY_NOT_STAGE4_ACCEPTED" and
            own["B02_stage4"]=="NOT_RUN" and
            own["stages_5_6_7"]=="NOT_RUN" and
            own["source_verified_positions"]=="101-200" and
            own["single_working_json"]["storage"]=="CURRENT_CHAT_SANDBOX_ONLY_LIBRARY_UPLOAD_FAILED_CONTAINER_SESSION_UNAVAILABLE" and
            own["single_working_json"]["authoritative_promotion"] is False and
            own["single_working_json"]["sha256"]==r["lost_original_working_expected_sha256"],"ORIGINAL_STAGE3_RECOVERY_OVERCLAIM")
    require(len(own["proposed"])==r["source_owner_proposals_pending"]==13 and
            all(p["stage4"]=="PENDING" and p["graph_mutation"] is False
                for p in own["proposed"]) and
            len(own["dispositions"])==r["source_owner_dispositions"]==11 and
            any(x["position"]==r["unresolved_phrase_hold_position"]==163 and
                x["decision"]=="HOLD_DIRECT_PHRASE_EVIDENCE" for x in own["dispositions"]), "EDITORIAL_PROPOSALS_OR_HOLD_DRIFT")
    require(own["exact_parent_zip_sha256"]==d["authenticated_parents"]["parent_stage4_zip_sha256"] and
            own["source_original_pdf_sha256"]==d["authenticated_parents"]["original_pdf_sha256_OWNER_REPORTED_NOT_RECHECKED"],"ORIGINAL_SOURCE_PINS_MISMATCH")
    five=load_pinned(root,STAGE5,STAGE5_BLOB)
    seven=load_pinned(root,STAGE7,STAGE7_BLOB)
    require(five["native_package"]["sha256"]==d["authenticated_parents"]["stage5_native_zip_sha256"] and
            five["authority"]["stage4_accepted_zip_sha256"]==d["authenticated_parents"]["parent_stage4_zip_sha256"] and
            seven["stages"]["stage4"]["cards"]==100 and
            seven["stages"]["stage7"]["full_2492_linguistic_stage4_approved"] is False,
            "B01_SCOPE_OR_NATIVE_PARENT_DRIFT")
    base=d["recovered_baseline"]
    require(base["positions"]==[101,200] and base["unique_ids"]==100 and
            base["first_id"]=="dah-nvv-exp-00099" and
            base["last_id"]=="dah-nvv-exp-00198" and
            base["trilingual_DE_FA_EN_example_triples"]==400 and
            base["no_proposals_applied"] is True and
            base["provider_readback_byte_identical"] is True,
            "RECOVERED_PARENT_BASELINE_SCOPE_INVALID")
    for role in ("recovered_baseline","recovery_qa","recovery_tool"):
        node=d[role]
        require(node["path"].startswith("/Flasch kart/German-Content-Production-Kit/Content/Nomen-Verb-Verbindungen/") and
                node["library_stable_id"].startswith("libfile_") and
                isinstance(node["bytes"],int) and node["bytes"]>0 and
                sha64(node["sha256"]) and
                node["provider_readback_byte_identical"] is True,
                "SCOPE_OR_PROVIDER_RECEIPT_INVALID:"+role)
    require(base["sha256"]!="f604f265ea1483d800590f5a66adef99abbdb574240171db777201eaacaee96e" and
            base["sha256"]!=r["lost_original_working_expected_sha256"],
            "FALSIFIED_ORIGINAL_STAGE3_BYTES")
    qa=d["recovery_qa"]
    require(qa["individual_card_hashes"]==100 and
            sorted(qa["negative_controls_rejected"])==
            sorted(["wrong_initial_id","missing_last_card","missing_persian_example","duplicated_id"]),
            "QA_NEGATIVE_CONTROLS_INVALID")
    require(all(value is False for value in d["nonclaims"].values()) and
            d["authenticated_parents"]["stage4_stage5_canonical_byte_identical"] is True and
            d["authenticated_parents"]["parent_archive_crc_pass"] is True and
            d["authenticated_parents"]["parent_16_member_SHA256SUMS_all_pass"] is True,
            "FALSE_STAGE4_OR_RELEASE_PROMOTION")
    return {"schema":"gfp-opt-p1-nvv-b02-recovery-metadata-verification@1.0.0",
        "status":"PASS_PINNED_SOURCE_OWNER_RECOVERY_SCOPE__NOT_STAGE3_OR_STAGE4_OR_ADOPTED",
        "owner_blob_sha":r["git_blob"],"source_parent_sha256":d["authenticated_parents"]["parent_stage4_zip_sha256"],
        "baseline_sha256":base["sha256"],"baseline_cards":100,"examples_trilingual":400,
        "editorial_proposals_pending":13,"direct_phrase_hold_position":163,
        "provider_readback":"RECORDED_IN_SCOPED_SESSION_NOT_PERFORMED_IN_THIS_CI",
        "original_lost_stage3_working":"NOT_RECOVERED","P1_ADOPTED":False}
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",type=Path,default=ROOT)
    o=ap.parse_args()
    try:out=verify(o.root)
    except (VerificationError,ValueError,KeyError,TypeError,OSError,UnicodeError) as e:
        print("GFP_OPT_NVV_B02_RECOVERY_DENIED:"+str(e),file=sys.stderr);return 2
    print(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2))
    return 0
if __name__=="__main__":raise SystemExit(main())
