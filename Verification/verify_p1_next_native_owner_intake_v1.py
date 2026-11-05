#!/usr/bin/env python3
"""Read-only, fail-closed P1 next Stage5 source-owner intake snapshot.

This intentionally CANNOT issue ADOPTED; later adoption requires new native
receipts plus the separately pinned remote provider readback verifiers.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INTAKE="Optimization-Program/Control-Center/P1-NEXT-NATIVE-STAGE5-OWNER-INTAKE-20261105.json"
REGISTRY="Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
CATALOG="Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
REQUIRED_FLAGS={
 "new_source_owner_stage5_authorization",
 "new_production_governed_receipt",
 "new_production_stage5_owner_qa",
 "new_github_main_latest_pointer_readback",
 "new_provider_authenticated_library_output_readback",
 "formal_new_p1_adoption",
}
class IntakeError(ValueError): pass
def require(yes,message):
    if not yes: raise IntakeError(message)
def git_blob(blob):
    return hashlib.sha1(b"blob "+str(len(blob)).encode("ascii")+b"\0"+blob).hexdigest()
def matches_git(blob,sha):
    return bool(re.fullmatch(r"[a-f0-9]{40}",sha or "")) and (
        git_blob(blob)==sha or
        (b"\r\n" in blob and git_blob(blob.replace(b"\r\n",b"\n"))==sha)
    )
def content(root,name,expected):
    require(name and name==Path(name).as_posix() and
            not Path(name).is_absolute() and
            ".." not in Path(name).parts, "UNSAFE_REPO_EVIDENCE_PATH")
    root=root.resolve()
    file=root/name
    require(file.is_file() and not file.is_symlink() and
            file.resolve().is_relative_to(root), "OWNER_EVIDENCE_NOT_REGULAR:"+name)
    data=file.read_bytes()
    require(matches_git(data,expected),"OWNER_BLOB_PIN_DRIFT:"+name)
    return json.loads(data.decode("utf-8-sig"))
def get_path(d,key):
    cur=d
    for part in key.split("."):
        require(isinstance(cur,dict) and part in cur,
                "OWNER_FIELD_MISSING:"+key)
        cur=cur[part]
    return cur

def verify(root=ROOT,intake=None):
    root=Path(root)
    config=intake if intake is not None else json.loads((root/INTAKE).read_text(encoding="utf-8"))
    require(config.get("schema")=="gfp-opt-p1-native-stage5-next-owner-intake@1.0.0" and
            config.get("program_id")=="GFP-OPT-2026" and
            config.get("snapshot_date")=="2026-11-05",
            "INTAKE_SCHEMA_OR_SCOPE_INVALID")
    auth=config["authority"]
    require(auth["catalog_path"]==CATALOG and
            auth["registry_path"]==REGISTRY,
            "CENTRAL_AUTHORITY_ROUTE_CHANGED")
    cat=content(root,CATALOG,auth["catalog_git_blob"])
    reg=content(root,REGISTRY,auth["registry_git_blob"])
    require(cat.get("schema")=="gcpk-master-project-catalog@1.0.0" and
            reg.get("schema")=="gcpk-global-policy-registry@1.0.0",
            "CENTRAL_AUTHORITY_SCHEMA_UNTRUSTED")
    require(reg["policy_bindings"]["stage5_clean_builder"]["blob_sha"]==
            auth["native_builder_blob"] and
            reg["policy_bindings"]["stage5_neutral_validator"]["stages"]==[5],
            "STAGE5_PIN_DRIFT")
    wrapper=root/"Tools/build_governed_clean_delivery_v1.py"
    require(wrapper.is_file() and not wrapper.is_symlink() and
            wrapper.resolve().is_relative_to(root.resolve()) and
            matches_git(wrapper.read_bytes(),auth["new_governed_wrapper_blob"]),
            "GOVERNED_WRAPPER_GIT_BLOB_DRIFT")
    dirs={w["id"]:(w["git_dir"],w["parent_family_id"])
          for w in cat["workspaces"]}
    families={f["id"] for f in cat["families"]}
    rows=config["candidates"]
    require(isinstance(rows,list) and len(rows)==7,
            "SEVEN_SOURCE_SNAPSHOT_REQUIRED")
    require(len({r["id"] for r in rows})==len(rows),
            "DUPLICATE_CANDIDATE_ID")
    results=[]
    for r in rows:
        require(r["family_id"] in families and
                r["workspace_id"] in dirs and
                dirs[r["workspace_id"]][1]==r["family_id"] and
                dirs[r["workspace_id"]][0] in r["owner_evidence"],
                "OWNER_WORKSPACE_FAMILY_ROUTING_DRIFT:"+r["id"])
        require(r["status"] not in ("ADOPTED","READY_FOR_PUBLICATION") and
                isinstance(r["next_owner_action"],str) and
                len(r["next_owner_action"])>=20,
                "FALSE_READY_STATUS:"+r["id"])
        gates=r["governed_new_production_evidence"]
        require(set(gates)==REQUIRED_FLAGS and
                all(gates[k] is False for k in REQUIRED_FLAGS),
                "UNSUPPORTED_NEW_ADOPTION_OR_AUTHORIZATION:"+r["id"])
        owner=content(root,r["owner_evidence"],r["owner_git_blob"])
        checks=r["observed_assertions"]
        require(isinstance(checks,dict) and checks,
                "NO_CONCRETE_SOURCE_WITNESS:"+r["id"])
        for field,expected in checks.items():
            require(get_path(owner,field)==expected,
                    "OWNER_STAGE_STATUS_CHANGED_REVIEW_REQUIRED:"+r["id"]+":"+field)
        results.append({"candidate_id":r["id"],
                        "workspace_id":r["workspace_id"],
                        "source_owner_git_blob_verified":True,
                        "source_predicates_verified":len(checks),
                        "new_authorized_governed_stage5":False,
                        "formal_adopted":False,
                        "status":r["status"]})
    require(config["counts"]["selected_source_candidates"]==len(results) and
            all(config["counts"][key]==0 for key in
                ("source_owner_new_stage5_authorization_proved",
                 "new_governed_production_receipts",
                 "new_independently_verified_git_main_library_publications",
                 "formally_adopted_new_p1_producers")),
            "UNSUPPORTED_SUCCESSFUL_ADOPTION_COUNTS")
    require(config["rules"]["all_existing_rehearsal_receipts_nonadopting"] is True and
            config["rules"]["updated_source_owner_evidence_requires_new_review_not_silent_progress"] is True,
            "FALSE_SNAPSHOT_PROMOTION_POLICY")
    return {"schema":"gfp-opt-p1-native-adoption-intake-audit@1.0.0",
            "status":"PASS_SEVEN_LIVE_PINNED_OWNER_CANDIDATES__ZERO_NEW_GOVERNED_STAGE5_ADOPTED",
            "counts":{"source_owner_witnesses":len(results),
                      "source_owner_predicates":sum(x["source_predicates_verified"] for x in results),
                      "ready_producers":0,"adopted_producers":0},
            "candidates":results,
            "boundary":"2026-11-05 scoped history; owner blob changes must stop this check and trigger review, never promote by inferred format or historic Stage5"}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    a=p.parse_args()
    try:
        r=verify(root=a.root)
    except (ValueError,KeyError,TypeError,OSError,UnicodeError) as e:
        print("GFP_OPT_P1_OWNER_INTAKE_DENIED:"+str(e),file=sys.stderr)
        return 2
    print(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
