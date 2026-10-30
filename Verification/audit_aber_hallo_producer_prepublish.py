"""OP-02 NONACTIVE producer prepublish read-only role check, never release proof."""
import argparse
import json
import re
from pathlib import Path
from audit_aber_hallo_receipt_families import SCHEMAS

WIP=re.compile(r"^WIP([0-9]{2,4})_")
KNOWN={**{k:v["version"] for k,v in SCHEMAS.items()},
       "gcpk-aber-hallo-rektion-checkpoint@1.0.0":57,
       "gcpk-aber-hallo-direct-duden-scoped-checkpoint@1.0.0":56}
BASE="Workspaces/aber-hallo-listen-tabellen/"

def _sha(x):
    return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x) and x!="0"*64

def _pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise ValueError("DUPLICATE_JSON_KEY")
        d[k]=v
    return d

def parse(b):
    return json.loads(b.decode("utf-8"),object_pairs_hook=_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))

def assess(latest,receipt,sources,receipt_path):
    e=[]
    r={"schema":"gcpk-op02-producer-prepublish-role-gate@1",
       "status":"BLOCKED_PREPUBLISH","blockers":e,
       "check_scope":"TRACKED_METADATA_ONLY",
       "authenticated_current_source":False,
       "authenticated_issuer":False,
       "original_zip_bytes_verified":False,
       "source_pdf_binary_verified":False,
       "stage4_semantic_pass":False,"stage5_allowed":False,
       "stage6_pass":False,"stage7_release_final":False,
       "writer_granted":False,"performed_writes":False}
    if not all(isinstance(x,dict) for x in (latest,receipt,sources)):
        e.append("DOCUMENT_NOT_OBJECT")
        return r
    if latest.get("schema")!="gcpk-workstream-latest@1.0.0" or latest.get("workstream")!="aber-hallo-listen-tabellen":
        e.append("LATEST_IDENTITY_INVALID")
    if sources.get("schema")!="gcpk-source-manifest@1.1.0" or sources.get("dataset")!="aber-hallo-listen-tabellen":
        e.append("SOURCE_IDENTITY_INVALID")
    src=sources.get("source_set")
    if not isinstance(src,list) or len(src)!=2 or any(
        not isinstance(x,dict) or not isinstance(x.get("source_id"),str)
        or x.get("source_type")!="pdf" or not _sha(x.get("sha256")) for x in src):
        e.append("SOURCE_SET_MALFORMED")
    label=latest.get("latest_milestone")
    m=WIP.match(label) if isinstance(label,str) else None
    version=int(m.group(1)) if m else None
    if version is None:e.append("CURRENT_WIP_VERSION_INVALID")
    ptr=latest.get("latest_receipt_path")
    if not isinstance(ptr,str) or ptr!=receipt_path or not ptr.startswith(BASE) or ".." in ptr.split("/") or version is None or f"WIP{version}" not in ptr:
        e.append("CURRENT_RECEIPT_PATH_DRIFT")
    if receipt.get("status") not in ("PASS_SCOPED_STAGE4_OPEN",):
        e.append("RECEIPT_NOT_SCOPED_PASS")
    schema=receipt.get("schema")
    if schema not in KNOWN:e.append("UNREGISTERED_RECEIPT_SCHEMA")
    elif KNOWN[schema]!=version:e.append("RECEIPT_SCHEMA_VERSION_DRIFT")
    a=latest.get("authority")
    cur=a.get("current_portable") if isinstance(a,dict) else None
    pkg=latest.get("complete_working_content_package")
    if not isinstance(cur,dict) or not isinstance(pkg,dict):
        e.append("CURRENT_PACKAGE_ROLE_MISSING")
    else:
        for left,right in (("filename","name"),("sha256","sha256"),("size_bytes","bytes"),
                           ("library_file_id","library_file_id"),("library_path","library_path")):
            if not cur.get(left) or cur.get(left)!=pkg.get(right):
                e.append("CURRENT_PACKAGE_ROLE_DRIFT:"+left)
        for key in ("sha256","canonical_sha256","import_sha256"):
            if not _sha(cur.get(key)):e.append("CURRENT_HASH_INVALID:"+key)
        if type(cur.get("size_bytes")) is not int or cur["size_bytes"]<=0:
            e.append("INVALID_CURRENT_BYTE_SIZE")
        if cur.get("stage4")!="OPEN" or pkg.get("stage4")!="OPEN" or pkg.get("stage5_6_7")!="NOT_RUN":
            e.append("STAGE4_7_BOUNDARY_INVALID")
        if version is None or not isinstance(cur.get("filename"),str) or f"WIP{version}-" not in cur["filename"]:
            e.append("PORTABLE_VERSION_DRIFT")
        old=latest.get(f"previous_wip{version}_source_current") if version else None
        oldp=old.get("portable") if isinstance(old,dict) else None
        parent=oldp.get("sha256") if isinstance(oldp,dict) else None
        if not _sha(parent) or pkg.get("parent_sha256")!=parent:
            e.append("PACKAGE_PREDECESSOR_PARENT_DRIFT")
        if receipt.get("parent_sha256") is not None and receipt.get("parent_sha256")!=parent:
            e.append("RECEIPT_PREDECESSOR_PARENT_DRIFT")
        for key,left in (("zip","filename"),("zip_sha256","sha256"),
                         ("library_file_id","library_file_id"),
                         ("canonical_sha256","canonical_sha256"),
                         ("import_sha256","import_sha256")):
            if key in receipt and receipt[key]!=cur.get(left):
                e.append("RECEIPT_CURRENT_ROLE_DRIFT:"+key)
        if "zip_members" in receipt and receipt["zip_members"]!=pkg.get("member_count"):
            e.append("RECEIPT_PACKAGE_MEMBER_DRIFT")
    prog=latest.get("progress")
    if not isinstance(prog,dict) or prog.get("pending_independent_expert_stage4") is not True or prog.get("independent_expert_unreviewed_units")!=788:
        e.append("STAGE4_REVIEW_NOT_OPEN")
    else:
        total=prog.get("rektion_independent_external_attested_cumulative")
        holds=prog.get("rektion_external_holds_remaining")
        if type(total) is not int or type(holds) is not int or total<0 or holds<0 or total+holds!=981:
            e.append("GOVERNED_981_ACCOUNTING_DRIFT")
        for key,correct in (("cumulative_attested",total),("remaining_holds",holds),
                            ("external_holds",holds)):
            if key in receipt and receipt[key]!=correct:
                e.append("RECEIPT_REKTION_COUNT_DRIFT:"+key)
    for key in ("learning_units","units"):
        if key in receipt and (type(receipt[key]) is not int or receipt[key]!=788):
            e.append("LEARNING_UNIT_COUNT_INVALID")
    for key in ("lexical_cards","import_cards"):
        if key in receipt and (type(receipt[key]) is not int or receipt[key]!=787):
            e.append("LEXICAL_CARD_COUNT_INVALID")
    for key in ("full_stage4","global_stage4"):
        if key in receipt and receipt[key]!="OPEN":e.append("FALSE_STAGE4_CLAIM")
    if "stage5_to_7" in receipt and receipt["stage5_to_7"]!="NOT_RUN":
        e.append("FALSE_STAGE5_7_CLAIM")
    r["blockers"]=sorted(set(e))
    if not e:r["status"]="PASS_SCOPED_PREPUBLISH_METADATA_ONLY_NOT_AUTHORIZED"
    return r

def main():
    p=argparse.ArgumentParser()
    for name in ("latest","receipt","sources"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--receipt-relative-path",required=True)
    p.add_argument("--strict",action="store_true")
    a=p.parse_args()
    try:
        out=assess(parse(a.latest.read_bytes()),parse(a.receipt.read_bytes()),
                   parse(a.sources.read_bytes()),a.receipt_relative_path)
    except (ValueError,TypeError,OSError,UnicodeError,RecursionError) as err:
        out=assess(None,None,None,a.receipt_relative_path)
        out["blockers"].append("INPUT_READ_FAILURE:"+type(err).__name__)
    print(json.dumps(out,indent=2,sort_keys=True))
    return 2 if a.strict and out["status"].startswith("BLOCKED") else 0

if __name__=="__main__":raise SystemExit(main())
