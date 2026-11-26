#!/usr/bin/env python3
"""Reject NEW lexical Stage5 acceptance claims without exact quality-gated proof.

One read-only repository boundary (PR/commit), not a builder or Stage4 judge.
Historical receipts remain unchanged; a Stage3/4 draft doesn't trigger this.
"""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROUTE="Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"
QUALITY_SCHEMA="gcpk-lexical-quality-gated-stage5-candidate@1.0.0"
QUALITY_STATUS="PASS_STAGE5_CANDIDATE_WITH_EXACT_SOURCE_STAGE4_AND_RULE_COVERAGE"

def sha(b):return hashlib.sha256(b).hexdigest()
def json_obj(raw):
    def unique(pairs):
        obj={}
        for key,val in pairs:
            if key in obj:raise ValueError("DUPLICATE_JSON_KEY")
            obj[key]=val
        return obj
    data=json.loads(raw,object_pairs_hook=unique)
    if not isinstance(data,dict):raise ValueError("RELEASE_OR_PROOF_NOT_OBJECT")
    return data
def claimed_status(value):
    if isinstance(value,dict):value=value.get("status")
    if not isinstance(value,str):return False
    upper=value.upper()
    return bool(("PASS" in upper or "ACCEPTED" in upper or "APPROVED" in upper)
                and not any(x in upper for x in ("NOT_STAGE5","NOT_IMPORT_READY","NONIMPORT","BLOCKED","REJECTED","DRAFT_ONLY")))
def promoted(new,old,path):
    filename=Path(path).name.upper()
    if not filename.endswith(".JSON"):return False
    if filename.startswith("STAGE5") or ("STAGE5" in filename and "CHECKPOINT" in filename):
        n=claimed_status(new.get("status",new.get("stage5")))
        o=claimed_status(old.get("status",old.get("stage5"))) if old else False
        return n and (not o or new.get("artifact")!=old.get("artifact") or new.get("source_sha256")!=old.get("source_sha256"))
    if filename in ("LATEST.JSON","CHECKPOINT.JSON","STAGE7-LATEST.JSON"):
        def content_release_claim(d):
            if not isinstance(d,dict):return False
            st=d.get("status","")
            approved_in_status=(isinstance(st,str) and "STAGE5" in st.upper()
                                and claimed_status(st))
            return d.get("import_ready") is True or claimed_status(d.get("stage5")) or approved_in_status
        if not content_release_claim(new):return False
        if not content_release_claim(old):return True
        # An already-approved pointer can be updated cosmetically without a new
        # release. Any newly pointed source/content/ZIP is a *new* claim.
        identity=("source_sha256","artifact","latest_archive_sha256",
                  "latest_archive","stage5","release_quality_receipt","source_tsv_sha256","current_import_sha256")
        return any(new.get(k)!=old.get(k) for k in identity) or (new.get("content_release") or {}).get("sha256")!=(old.get("content_release") or {}).get("sha256")
    return False
def require_exact_release_zip_pins(pointer, governed_zip_sha):
    """Fail closed on an unbound or contradictory new Stage5 publication pointer.

    A filename and a PASS receipt do not establish that the referenced ZIP is
    the same binary built by the quality gate. The standard owner shape is
    artifact.sha256; support only explicit SHA256 aliases, never a bare name.
    """
    if not isinstance(governed_zip_sha,str) or not re.fullmatch(r"[0-9a-f]{64}",governed_zip_sha):
        raise ValueError("QUALITY_GATE_OUTPUT_SHA256_MISSING")
    observed=[]
    def add(name,value):
        if value is None:return
        if not isinstance(value,str) or not re.fullmatch(r"[0-9a-f]{64}",value):
            raise ValueError("RELEASE_ARTIFACT_SHA256_MALFORMED:"+name)
        observed.append((name,value))
    def named_artifact(name,value):
        if isinstance(value,dict):
            # A separately declared artifact is another release lead: all
            # claimed archive objects must bind to the SAME exact ZIP bytes.
            if "sha256" not in value or value["sha256"] is None:
                raise ValueError("RELEASE_ARTIFACT_SHA256_REQUIRED:"+name)
            add(name+".sha256",value["sha256"])
    named_artifact("artifact",pointer.get("artifact"))
    add("latest_archive_sha256",pointer.get("latest_archive_sha256"))
    named_artifact("latest_archive",pointer.get("latest_archive"))
    stage=pointer.get("stage5")
    if isinstance(stage,dict):
        for k in ("output_zip_sha256","artifact_sha256","zip_sha256"):
            add("stage5."+k,stage.get(k))
        named_artifact("stage5.artifact",stage.get("artifact"))
    if not observed:raise ValueError("RELEASE_ARTIFACT_SHA256_REQUIRED")
    if any(value!=governed_zip_sha for _,value in observed):
        raise ValueError("RELEASE_ARTIFACT_NOT_QUALITY_GATED_ZIP")
    return {"bound_paths":[name for name,_ in observed],"zip_sha256":governed_zip_sha}

def workspace_for(path):
    parts=Path(path).parts
    if len(parts)<3 or parts[0]!="Workspaces" or ".." in parts:
        raise ValueError("INVALID_RELEASE_WORKSPACE_PATH")
    return "/".join(parts[:2])

MAINT_STATUS="PASS_CONTENT_ONLY_DISPLAY_DELTA"
MAINT_ACCEPTED="CONTENT_ONLY_ACCEPTED_DISPLAY_DELTA"

def git_blob_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def maintenance_check(path,new,old,loader,router,base_loader,base_router):
    """Validate an already-reviewed maintenance receipt, never a fresh Stage5 PASS.

    Proof must already exist on the protected base, byte-identical at head.
    CI checks its binding, not private archive contents or linguistic truth.
    """
    def need(ok,code):
        if not ok: raise ValueError("DISPLAY_MAINTENANCE_"+code+":"+path)
    owner=workspace_for(path)
    need(base_loader is not None and base_router is not None,"BASE_PROOF_REQUIRED")
    current=[x for x in router["families"] if x.get("canonical_git_workspace")==owner]
    prior=[x for x in base_router["families"] if x.get("canonical_git_workspace")==owner]
    need(len(current)==len(prior)==1 and current[0]["family_id"]==prior[0]["family_id"],"CANONICAL_OWNER")
    family=current[0]; parent=prior[0]["active_content_sha256"]
    release=new.get("content_release") or {}; stage=new.get("stage5") or {}
    decision=new.get("display_maintenance_acceptance") or {}
    previous=(old or {}).get("content_release") or {}
    digest=release.get("sha256"); tsv=new.get("current_import_sha256")
    need(all(isinstance(x,str) and re.fullmatch(r"[a-f0-9]{64}",x) for x in (parent,digest,tsv)) and parent!=digest,"HASH_FORMAT")
    need(previous.get("sha256")==parent and family.get("active_content_sha256")==digest,"PARENT_OR_SELECTED_SHA")
    need(new.get("family_id")==family["family_id"] and new.get("status","").endswith(MAINT_ACCEPTED)
         and stage.get("status")==MAINT_STATUS and release.get("acceptance")==MAINT_ACCEPTED
         and release.get("scope")=="LEARNER_VISIBLE_EXPLANATORY_NOTES_ONLY"
         and release.get("parent_accepted_content_sha256")==parent
         and new.get("stage4")=="INHERITED_UNCHANGED_SCOPE_ONLY__DISPLAY_DELTA_REVIEW_PASS"
         and new.get("source_tsv_sha256")==tsv and new.get("user_import")=="PASS_USER_REPORTED"
         and new.get("stage6_native")=="NOT_ATTESTED" and new.get("stage7_integrated")=="NOT_ATTESTED"
         and "release_quality_receipt" not in new,"SCOPE_OR_FALSE_STAGE_CLAIM")
    need(decision.get("status")==MAINT_ACCEPTED and decision.get("prior_release_sha256")==parent
         and decision.get("accepted_release_sha256")==digest and decision.get("accepted_import_sha256")==tsv
         and decision.get("user_import")=="PASS_USER_REPORTED"
         and decision.get("new_full_stage4_stage5")=="NOT_CLAIMED"
         and decision.get("native_stage6_stage7")=="NOT_CLAIMED","DECISION_BINDING")
    receipt=stage.get("receipt_path")
    need(isinstance(receipt,str) and receipt.startswith(owner+"/") and receipt.endswith(".json")
         and ".." not in Path(receipt).parts and receipt==decision.get("maintenance_receipt"),"RECEIPT_OWNER")
    raw=base_loader(receipt)
    need(raw is not None and loader(receipt)==raw,"PREMERGED_RECEIPT_REQUIRED")
    need(git_blob_sha(raw)==stage.get("receipt_git_blob")==decision.get("maintenance_receipt_git_blob"),"RECEIPT_BLOB")
    q=json_obj(raw.decode("utf-8-sig"))
    need(q.get("schema")=="gcpk-display-delta-maintenance@1" and q.get("status")==MAINT_STATUS
         and q.get("family_id")==family["family_id"] and q.get("parent_zip_sha256")==parent
         and q.get("candidate_zip_sha256")==digest and q.get("candidate_import_sha256")==tsv
         and q.get("parent_import_sha256")==old.get("current_import_sha256")
         and q.get("user_import")=="PASS_USER_REPORTED" and q.get("new_full_stage4_stage5")=="NOT_CLAIMED"
         and q.get("prior_stage4_stage5")=="INHERITED_UNCHANGED_SCOPE_ONLY"
         and q.get("native_stage6_stage7")=="NOT_CLAIMED","RECEIPT_BINDING")
    tool=base_loader("Verification/verify_display_delta.py")
    need(tool is not None and git_blob_sha(tool)==q.get("tool_git_blob") and sha(tool)==q.get("tool_sha256"),"REVIEW_TOOL_PIN")
    review=q.get("review_input") or {}
    need(all(review.get(k)==q.get(k) for k in ("parent_zip_sha256","candidate_zip_sha256","parent_import_sha256","candidate_import_sha256","user_import"))
         and review.get("user_import_sha256")==tsv,"REVIEW_BINDING")
    need(all(type(q.get(k)) is int and q[k]>0 for k in ("cards","changed_cards","changed_items","parent_manifest_checks","candidate_manifest_checks","example_sets"))
         and type(q.get("unchanged_cards")) is int and q["unchanged_cards"]>=0
         and q["changed_cards"]+q["unchanged_cards"]==q["cards"]
         and type(q.get("manual_note_reviews")) is int and 0<=q["manual_note_reviews"]<=q["changed_items"]
         and isinstance(review.get("manual_decisions"),dict) and len(review["manual_decisions"])==q["manual_note_reviews"]
         and all(isinstance(v,str) and v.strip() for v in review["manual_decisions"].values()),"REVIEW_COUNTS")
    tests=q.get("negative_tests") or {}
    required={"id_change","meaning_change","example_change","metadata_change","unrecorded_details","missing_manual_review","wrong_owner_hash","wrong_user_import"}
    need(required.issubset(tests) and all(isinstance(tests[k],str) and tests[k].startswith("PASS_REJECTED:") for k in required),"NEGATIVE_TESTS")
    checkpoint=q.get("source_owner_user_import_receipt")
    need(isinstance(checkpoint,str) and checkpoint.startswith(owner+"/") and ".." not in Path(checkpoint).parts
         and checkpoint==new.get("checkpoint"),"USER_RECEIPT_OWNER")
    b=base_loader(checkpoint); h=loader(checkpoint)
    need(b is not None and h is not None,"USER_RECEIPT_MISSING")
    a=json_obj(b.decode("utf-8-sig")); z=json_obj(h.decode("utf-8-sig"))
    user=a.get("user_field_acceptance") or {}; working=a.get("working_candidate") or {}
    need(user.get("status")=="PASS_USER_REPORTED" and user.get("delivered_zip_sha256")==digest
         and user.get("delivered_import_sha256")==tsv and bool(user.get("reported_text_fa"))
         and working.get("zip_sha256")==digest and working.get("import_sha256")==tsv
         and working.get("library_id")==release.get("library_id") and working.get("filename")==release.get("filename")
         and working.get("bytes")==release.get("bytes")
         and z.get("user_field_acceptance")==user and z.get("working_candidate")==working
         and z.get("accepted_maintenance_successor")==decision,"USER_OR_PACKAGE_BINDING")
    return {"path":path,"status":"PASS_DISPLAY_MAINTENANCE_RECEIPT_BOUND","family":family["family_id"],"release_zip_sha256":digest}

def release_check(path,new,old,loader,router,base_loader=None,base_router=None):
    if not promoted(new,old,path):return {"path":path,"status":"NOT_A_NEW_LEXICAL_STAGE5_PROMOTION"}
    if isinstance(new.get("stage5"),dict) and new["stage5"].get("status")==MAINT_STATUS:
        return maintenance_check(path,new,old,loader,router,base_loader,base_router)
    owner=workspace_for(path)
    eligible={f["canonical_git_workspace"]:f for f in router["families"]
              if f.get("canonical_git_workspace")}
    if owner not in eligible:raise ValueError("NEW_STAGE5_CLAIM_OUTSIDE_CANONICAL_FAMILY:"+owner)
    family=eligible[owner]
    ref=new.get("release_quality_receipt")
    if not isinstance(ref,dict):raise ValueError("RELEASE_QUALITY_RECEIPT_REQUIRED:"+path)
    receipt_path=ref.get("path");pin=ref.get("sha256")
    if not isinstance(receipt_path,str) or not receipt_path.startswith(owner+"/") or \
        not receipt_path.endswith(".json") or ".." in Path(receipt_path).parts:
        raise ValueError("RELEASE_QUALITY_RECEIPT_WRONG_OWNER")
    if not isinstance(pin,str) or not re.fullmatch("[0-9a-f]{64}",pin):
        raise ValueError("RELEASE_QUALITY_RECEIPT_UNPINNED")
    contents=loader(receipt_path)
    if contents is None or sha(contents)!=pin:raise ValueError("RELEASE_QUALITY_RECEIPT_BYTES_MISMATCH")
    q=json_obj(contents.decode("utf-8-sig"))
    if q.get("schema")!=QUALITY_SCHEMA or q.get("status")!=QUALITY_STATUS:
        raise ValueError("QUALITY_GATE_NOT_ACCEPTED")
    owner_proof=q.get("family_authority",{})
    if owner_proof.get("family_id")!=family.get("family_id") or \
       owner_proof.get("canonical_git_workspace")!=owner or \
       owner_proof.get("parent_sha256")!=family.get("active_content_sha256"):
        raise ValueError("RELEASE_FAMILY_CURRENTNESS_MISMATCH")
    qq=q.get("quality_gate",{})
    native=q.get("governed_format_build",{})
    if qq.get("status")!="PASS_FOR_GOVERNED_STAGE5_CANDIDATE_ONLY" or \
       qq.get("blockers")!=[] or \
       native.get("status")!="PASS_GOVERNED_STAGE5_FORMAT_AND_BYTE_PARITY_ONLY":
        raise ValueError("CONTENT_QA_OR_NATIVE_FORMAT_GATE_NOT_PASS")
    digest=qq.get("source_tsv_sha256")
    if not isinstance(digest,str) or not re.fullmatch(r"[0-9a-f]{64}",digest):
        raise ValueError("RELEASE_SOURCE_TSV_SHA256_INVALID")
    if digest!=native.get("source_role_sha256",{}).get("direct-import-tsv"):
        raise ValueError("RELEASE_SOURCE_TSV_HASH_MISMATCH")
    for name in ("source_tsv_sha256","content_tsv_sha256"):
        if name in new and new[name]!=digest:
            raise ValueError("RELEASE_POINTER_TSV_HASH_MISMATCH:"+name)
    if not re.fullmatch("[0-9a-f]{64}",str(q.get("exact_stage4_receipt_sha256",""))) or \
       not re.fullmatch("[0-9a-f]{64}",str(q.get("exact_cross_tile_review_sha256",""))):
        raise ValueError("EXACT_STAGE4_OR_CROSS_TILE_PROOF_MISSING")
    if native.get("linguistic_stage4")!="NOT_CERTIFIED":
        raise ValueError("FORMAT_WRAPPER_FAKES_STAGE4")
    archive=require_exact_release_zip_pins(new,native.get("output_zip_sha256"))
    return {"path":path,"status":"PASS_EXACT_SOURCE_LEXICAL_STAGE5_CLAIM_RECEIPT_BOUND",
        "family":family["family_id"],"receipt_sha256":pin,
        "release_zip_sha256":archive["zip_sha256"],
        "bound_artifact_pointers":archive["bound_paths"]}
def git(root,*parts):
    x=subprocess.run(["git",*parts],cwd=root,capture_output=True)
    if x.returncode!=0:raise ValueError("GIT_COMMAND_FAILED:"+x.stderr.decode(errors="replace")[-300:])
    return x.stdout
def at(root,commit,path):
    try:return git(root,"show",f"{commit}:{path}")
    except ValueError:return None
def run(base,head,root=ROOT):
    reg=json_obj((root/ROUTE).read_bytes())
    base_reg_raw=at(root,base,ROUTE)
    base_reg=json_obj(base_reg_raw) if base_reg_raw is not None else None
    changed=git(root,"diff","--name-only","--diff-filter=AMR",base,head,"--","Workspaces").decode().splitlines()
    records=[]
    for path in changed:
        if not path.endswith(".json") or "/." in path:continue
        name=Path(path).name.upper()
        if not (name.startswith("STAGE5") or
                name in ("LATEST.JSON","CHECKPOINT.JSON","STAGE7-LATEST.JSON")):
            # Other receipts can be lists, tables or model QA artifacts;
            # they must not be misparsed as release pointers.
            continue
        raw=at(root,head,path)
        if raw is None:continue
        new=json_obj(raw)
        old_raw=at(root,base,path)
        old=json_obj(old_raw) if old_raw is not None else None
        records.append(release_check(path,new,old,lambda p:at(root,head,p),reg,lambda p:at(root,base,p),base_reg))
    return {"schema":"gcpk-prospective-stage5-claim-guard@1.0.0",
        "checked_changed_json":len(records),
        "new_claims_verified":sum(r["status"].startswith("PASS_") for r in records),
        "status":"PASS_ALL_NEW_CLAIMS_EVIDENCED_OR_NO_NEW_CLAIM"}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base",required=True)
    p.add_argument("--head",default="HEAD")
    a=p.parse_args()
    try:print(json.dumps(run(a.base,a.head),sort_keys=True,ensure_ascii=False))
    except (ValueError,OSError,UnicodeError) as exc:
        print("PROSPECTIVE_STAGE5_PUBLICATION_BLOCKED:"+str(exc),file=sys.stderr)
        return 2
    return 0
if __name__=="__main__":raise SystemExit(main())
