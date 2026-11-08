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
        n=bool(new.get("import_ready") is True or claimed_status(new.get("stage5")))
        o=bool(old and (old.get("import_ready") is True or claimed_status(old.get("stage5"))))
        return n and not o
    return False
def workspace_for(path):
    parts=Path(path).parts
    if len(parts)<3 or parts[0]!="Workspaces" or ".." in parts:
        raise ValueError("INVALID_RELEASE_WORKSPACE_PATH")
    return "/".join(parts[:2])
def release_check(path,new,old,loader,router):
    if not promoted(new,old,path):return {"path":path,"status":"NOT_A_NEW_LEXICAL_STAGE5_PROMOTION"}
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
    if digest!=native.get("source_role_sha256",{}).get("direct-import-tsv"):
        raise ValueError("RELEASE_SOURCE_TSV_HASH_MISMATCH")
    if not re.fullmatch("[0-9a-f]{64}",str(q.get("exact_stage4_receipt_sha256",""))) or \
       not re.fullmatch("[0-9a-f]{64}",str(q.get("exact_cross_tile_review_sha256",""))):
        raise ValueError("EXACT_STAGE4_OR_CROSS_TILE_PROOF_MISSING")
    if native.get("linguistic_stage4")!="NOT_CERTIFIED":
        raise ValueError("FORMAT_WRAPPER_FAKES_STAGE4")
    if isinstance(new.get("artifact"),dict) and new["artifact"].get("sha256") and \
       new["artifact"]["sha256"]!=native.get("output_zip_sha256"):
        raise ValueError("RELEASE_ARTIFACT_NOT_QUALITY_GATED_ZIP")
    return {"path":path,"status":"PASS_EXACT_SOURCE_LEXICAL_STAGE5_CLAIM_RECEIPT_BOUND",
        "family":family["family_id"],"receipt_sha256":pin}
def git(root,*parts):
    x=subprocess.run(["git",*parts],cwd=root,capture_output=True)
    if x.returncode!=0:raise ValueError("GIT_COMMAND_FAILED:"+x.stderr.decode(errors="replace")[-300:])
    return x.stdout
def at(root,commit,path):
    try:return git(root,"show",f"{commit}:{path}")
    except ValueError:return None
def run(base,head,root=ROOT):
    reg=json_obj((root/ROUTE).read_bytes())
    changed=git(root,"diff","--name-only","--diff-filter=AMR",base,head,"--","Workspaces").decode().splitlines()
    records=[]
    for path in changed:
        if not path.endswith(".json") or "/." in path:continue
        raw=at(root,head,path)
        if raw is None:continue
        new=json_obj(raw)
        old_raw=at(root,base,path)
        old=json_obj(old_raw) if old_raw is not None else None
        records.append(release_check(path,new,old,lambda p:at(root,head,p),reg))
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
