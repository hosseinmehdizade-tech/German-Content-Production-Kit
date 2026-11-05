#!/usr/bin/env python3
"""GFP-OPT P1: source-grounded NONACTIVE domain adapter and root-pointer triage.

Reads the actual Git index and existing OP02 shadow contract. Does not create
missing CHECKPOINT files, copy other sources, run native producers or grant QA.
"""
from __future__ import annotations
import argparse
import importlib.util
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
PROFILE="Optimization-Program/Control-Center/Profiles/P1-CROSS-DOMAIN-ADAPTER-PREFLIGHT-v1.json"
SCHEMA="gfp-opt-p1-cross-domain-native-adapter-readiness@1.0.0"

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    if spec is None or spec.loader is None:
        raise ValueError("MODULE_NOT_ACCESSIBLE:"+name)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

phase=module("gfp_opt_native_index","Tools/build_project_control_center_v1.py")
graph=module("gfp_opt_native_graph","Tools/build_project_dependency_evidence_v1.py")

def require(ok,code):
    if not ok: raise ValueError(code)

def extra_index_path(path,root=ROOT):
    raw=phase.git("ls-files","--stage","--",path,root=root).decode("utf-8").strip()
    require(raw and "\n" not in raw and "\t" in raw,"UNTRACKED_EXTRA_SOURCE_AUTHORITY:"+path)
    head,name=raw.split("\t",1)
    mode,sha,stage=head.split(" ")
    require(name==path and mode=="100644" and stage=="0"
            and re.fullmatch("[a-f0-9]{40}",sha) is not None,
            "EXTRA_INDEX_NOT_CANONICAL:"+path)
    return sha

def matches_exact_git_text(data:bytes,git_blob:str)->bool:
    def blob(value:bytes)->str:
        return hashlib.sha1(
            b"blob "+str(len(value)).encode("ascii")+b"\0"+value
        ).hexdigest()
    return (blob(data)==git_blob or
            (b"\r\n" in data and blob(data.replace(b"\r\n",b"\n"))==git_blob))

def current_git_json(index,path,root=ROOT):
    require(path in index,"SOURCE_AUTHORITY_NOT_TRACKED:"+path)
    obj=phase.load_json_from_index(path,index,root)
    require(isinstance(obj,dict),"SOURCE_AUTHORITY_INVALID_JSON:"+path)
    return obj

def assessment(profile,catalog,domains,sources,routes,index,op02,issues):
    require(profile.get("schema")=="gfp-opt-p1-cross-domain-adapter-preflight@1.0.0"
            and profile.get("authority")==
             "SHADOW_METADATA_ONLY__NO_NATIVE_ADOPTION_OR_STAGE_PASS",
            "DOMAIN_PREFLIGHT_NOT_SHADOW")
    require(catalog.get("schema")=="gcpk-master-project-catalog@1.0.0"
            and domains.get("schema")==
            "gfp-opt-p1-source-domain-applicability-profiles@1.0.0"
            and sources.get("schema")=="gcpk-source-registry@1.1.0"
            and routes.get("schema")=="gfp-optimization-resume-routes@1"
            and op02.get("workstreams") is not None,
            "DOMAIN_SOURCE_AUTHORITY_SCHEMA_CHANGED")
    for key,val in profile.get("anti_promotion",{}).items():
        require(val is True,"PREFLIGHT_ANTI_PROMOTION_DISABLED:"+key)
    require(len(profile.get("anti_promotion",{}))==8,
            "MISSING_PRESERVATION_BOUNDARIES")
    allfamilies={f["id"]:f for f in catalog["families"]}
    domain_index={d["id"]:d["declared_domain"] for d in domains["families"]}
    require(set(allfamilies)==set(domain_index) and len(allfamilies)==21,
            "SOURCE_DOMAIN_PROFILE_COVERAGE_DRIFT")
    reg={x["source_id"]:x for x in sources["sources"]}
    require(len(reg)==len(sources["sources"]), "SOURCE_REGISTRY_DUPLICATE_ID")
    resumer={x["key"]:x for x in routes["routes"]}
    require(len(resumer)==len(routes["routes"]), "DUPLICATE_RESUME_ROUTE")
    family_profiles=profile["profiles"]
    expected={f for f,d in domain_index.items() if d in {
       "GRAMMAR_NEEDS_PROFILE","READING_SKILLS_NEEDS_PROFILE",
       "WRITING_SKILLS_NEEDS_PROFILE","VISUAL_MEDIA_NEEDS_PROFILE",
       "MIXED_SOURCE_NEEDS_OUTPUT_SPLIT"}}
    require(len(family_profiles)==len(expected)==8 and
            {p["family_id"] for p in family_profiles}==expected,
            "MISSING_OR_DUPLICATED_NONLEXICAL_FAMILY")
    results=[]
    for row in family_profiles:
        fid=row["family_id"]
        owner=row.get("native_owner")
        ids=row.get("registered_sources")
        require(type(ids) is list and len(ids)==len(set(ids))
                and all(isinstance(k,str) and k in reg for k in ids),
                "SOURCE_ID_NOT_REGISTERED:"+fid)
        if owner:
            require(all(reg[x]["workstream"]==owner for x in ids),
                    "SOURCE_OWNER_MISMATCH:"+fid)
        else:
            require(not ids,"UNREGISTERED_DOMAIN_CANNOT_ASSERT_SOURCE")
        found=[{"source_id":k,"domain":reg[k]["domain"],
                "source_sha256":reg[k]["sha256"],"native_workstream":reg[k]["workstream"]}
               for k in ids]
        domain=domain_index[fid]
        if domain=="READING_SKILLS_NEEDS_PROFILE":
            require([x["domain"] for x in found]==["reading"],
                    "READING_SOURCE_MUST_BE_NATIVE")
        if domain=="GRAMMAR_NEEDS_PROFILE":
            require(all(x["domain"]=="grammar" for x in found),
                    "GRAMMAR_SOURCE_MUST_BE_NATIVE")
        op02_name=row.get("op02_shadow_owner")
        shadow=op02["workstreams"].get(op02_name) if op02_name else None
        if op02_name:
            require(shadow is not None and
                    shadow["domain"] in ("reading","grammar") and
                    {k:v for k,v in
                     ((x[0],x[2]) for x in shadow["sources"])}==
                    {x["source_id"]:x["source_sha256"] for x in found},
                    "OP02_SHADOW_NOT_EXACT_SOURCE_BINDING:"+fid)
        checkpoint=None
        tracked=False
        checkpoint_hint=None
        if owner and ids:
            ck={reg[x].get("checkpoint") for x in ids}
            require(len(ck)==1,"CONFLICTING_NATIVE_SOURCE_CHECKPOINTS:"+fid)
            checkpoint=next(iter(ck))
            require(isinstance(checkpoint,str) and
                    checkpoint.startswith("Workspaces/"+owner+"/") and
                    ".." not in checkpoint and "\\" not in checkpoint,
                    "UNSAFE_NATIVE_SOURCE_CHECKPOINT:"+fid)
            tracked=checkpoint in index
            if tracked and checkpoint=="Workspaces/lesen-praesentation/CHECKPOINT.json":
                source_ck=phase.load_json_from_index(checkpoint,index)
                require(isinstance(source_ck,dict)
                        and source_ck.get("dataset",{}).get("domain")=="reading",
                        "READING_CHECKPOINT_WRONG_DOMAIN")
                stages=source_ck.get("stages",[])
                require(len(stages)==7 and
                        [x["stage"] for x in stages]==list(range(1,8)),
                        "READING_STAGE_STRUCTURE_CHANGED")
                checkpoint_hint={
                    "stage1_declared_from_git_checkpoint":stages[0]["state"],
                    "remaining_stages_declared_from_git_checkpoint":
                        {str(x["stage"]):x["state"] for x in stages[1:]},
                    "this_preflight_independently_reexecuted_source_qa":False
                }
        if not ids:
            status="BLOCKED_UNREGISTERED_SOURCE_AND_NATIVE_CONTRACT"
        elif not tracked:
            status="BLOCKED_NATIVE_CHECKPOINT_UNTRACKED__DO_NOT_INVENT"
        elif domain=="READING_SKILLS_NEEDS_PROFILE" and shadow:
            status="SHADOW_READING_STAGE1_METADATA_ONLY__STAGE2_TO_7_NOT_ACCEPTED"
        elif domain=="MIXED_SOURCE_NEEDS_OUTPUT_SPLIT":
            status="MIXED_OUTPUTS_REQUIRE_SOURCE_TYPED_SPLIT__NOT_ADOPTED"
        elif shadow:
            status="SHADOW_DOMAIN_ENVELOPE_ONLY__NOT_ACTIVE_ADAPTER"
        else:
            status="NATIVE_SOURCE_TRACKED__NO_VERIFIED_DOMAIN_ADAPTER"
        results.append({
            "family_id":fid,"declared_domain":domain,
            "registered_source_ids":ids,"registered_sources":found,
            "native_workstream":owner,"native_checkpoint_path":checkpoint,
            "native_checkpoint_tracked_in_git_index":tracked,
            "native_checkpoint_hint":checkpoint_hint,
            "op02_shadow_contract":shadow["contract"] if shadow else None,
            "shadow_is_active_producer":False,
            "status":status,
            "next_action":row["action"],
            "real_native_adapter_adopted":False,
            "semantic_stage4_acceptance":False,
            "source_stage5_7_or_final_acceptance":False
        })
    # Diagnose root workstream pointers WITHOUT repairing or inventing files.
    root_catalog={x["key"]:x["parent_family_id"]
                  for x in catalog["root_workstreams"]}
    triage=[]
    for issue in issues:
        kind=issue.get("type")
        path=issue.get("path")
        if kind!="ROOT_CHECKPOINT_UNTRACKED":
            triage.append({"issue_type":kind,"reported_path":path,
                           "status":"OTHER_NAVIGATION_ISSUE_REVIEW_SEPARATELY",
                           "auto_repair":False})
            continue
        candidates=[k for k,r in resumer.items() if
                    (r.get("checkpoint") or {}).get("path")==path]
        if len(candidates)==1 and candidates[0] in root_catalog:
            key=candidates[0]
            declared=resumer[key]["checkpoint"]
            require(declared["tracked"] is False and path not in index,
                    "ROOT_POINTER_TRIAGE_CONTRADICTS_GIT_INDEX")
            triage.append({"issue_type":kind,"reported_path":path,
                           "root_key":key,"parent_family_id":root_catalog[key],
                           "resume_route_declares_tracked":False,
                           "status":"CONFIRMED_STALE_OR_UNMATERIALIZED_ROOT_CHECKPOINT_REFERENCE",
                           "auto_repair":False,
                           "action":"RESOLVE_EXACT_SOURCE_OWNER_AND_NEWEST_VALID_PORTABLE_BEFORE_UPDATING_ROOT_POINTER"})
        else:
            triage.append({"issue_type":kind,"reported_path":path,
                           "status":"UNMAPPED_ROOT_CHECKPOINT_REFERENCE_HOLD",
                           "auto_repair":False})
    summary={
      "nonlexical_family_profiles":len(results),
      "native_grammar_source_families":sum(x["declared_domain"]=="GRAMMAR_NEEDS_PROFILE" for x in results),
      "native_reading_source_families":sum(x["declared_domain"]=="READING_SKILLS_NEEDS_PROFILE" for x in results),
      "writing_source_registered":any(x["declared_domain"]=="WRITING_SKILLS_NEEDS_PROFILE" and x["registered_sources"] for x in results),
      "actual_domain_adapters_adopted":0,
      "observed_navigation_issues":len(triage),
      "untracked_root_checkpoints":sum(x["issue_type"]=="ROOT_CHECKPOINT_UNTRACKED" for x in triage),
      "classified_existing_root_checkpoint_issues":
          sum(x["status"]=="CONFIRMED_STALE_OR_UNMATERIALIZED_ROOT_CHECKPOINT_REFERENCE" for x in triage),
      "source_stage_passes_certified_by_preflight":0
    }
    return {
       "schema":SCHEMA,"program_id":"GFP-OPT-2026",
       "status":"PASS_DOMAIN_AND_METADATA_ROUTING_ONLY__ALL_NATIVE_ADOPTIONS_HELD",
       "counts":summary,
       "source_families":results,
       "root_checkpoint_issue_triage":triage,
       "policy_conformance_adopted":False,
       "source_original_locked_cards_or_runtime_edited":False,
       "source_currentness_verified":False,
       "github_pointer_hints_not_source_pass":True,
       "next":"Source owners must resolve five untracked pointers from their latest authoritative source without inventing checkpoint files. Grammar, Lesen and Schreiben require separate producer-specific QA; OP02 remains SHADOW ONLY."
    }

def execute(root=ROOT):
    require(root.resolve()==ROOT.resolve(),"UNSUPPORTED_GIT_INDEX_ROOT")
    index=graph.index_blobs(root)
    profile=current_git_json(index,PROFILE,root)
    for key,item in profile["input_pins"].items():
        path=item["path"]
        actual=index.get(path) if path in index else extra_index_path(path,root)
        require(actual==item["git_blob"],"SOURCE_DOMAIN_AUTHORITY_PIN_DRIFT:"+key)
        index[path]=actual
    cat=current_git_json(index,profile["input_pins"]["catalog"]["path"],root)
    domains=current_git_json(index,profile["input_pins"]["domains"]["path"],root)
    sources=current_git_json(index,profile["input_pins"]["source_registry"]["path"],root)
    routes=current_git_json(index,profile["input_pins"]["resume_routes"]["path"],root)
    rootstate=current_git_json(index,"PROJECT-STATE.json",root)
    dirs=phase.tracked_dirs(index)
    pointers={}
    for d in dirs:
        for name in ("LATEST.json","CHECKPOINT.json"):
            p=d+"/"+name
            if p in index: pointers[p]=phase.load_json_from_index(p,index,root)
    old=phase.build(cat,index,rootstate,pointers)
    path=profile["input_pins"]["op02_shadow"]["path"]
    op02_file=root/path
    require(op02_file.is_file() and not op02_file.is_symlink()
            and matches_exact_git_text(op02_file.read_bytes(),
                                       profile["input_pins"]["op02_shadow"]["git_blob"]),
            "OP02_WORKTREE_NOT_EXACT_PINNED_SHADOW")
    op02=module("gfp_opt_existing_op02_nonactive",path)
    report=assessment(profile,cat,domains,sources,routes,index,
                      {"workstreams":op02.DOMAINS},old["issues"])
    reader=module("gfp_opt_real_lesen_stage1_replay",
                  "Verification/replay_lesen_stage1_native_v1.py")
    proof=reader.execute()
    require(proof["status"]==
            "PASS_ACTUAL_GIT_READING_STAGE1_DERIVED_BYTES_AND_STRUCTURE_REPLAY_ONLY"
            and proof["new_policy_adoption"]=="NOT_ADOPTED"
            and proof["stage2_to_7"]=="NOT_APPROVED"
            and proof["actual_independent_stage1_source_pdf_bytes_revalidated"] is False
            and proof["replayed_counts"]["topics"]==68
            and proof["replayed_counts"]["pages"]==76,
            "READING_NATIVE_REPLAY_SCOPE_OR_SOURCE_CHANGED")
    reading=[row for row in report["source_families"]
             if row["family_id"]=="family:lesen"]
    require(len(reading)==1 and reading[0]["native_checkpoint_tracked_in_git_index"],
            "READING_OWNER_NO_LONGER_ELIGIBLE_FOR_STAGE1_REPLAY")
    reading[0]["native_stage1_actual_git_derived_replay"]=proof
    report["counts"]["real_git_native_reading_stage1_structure_replays"]=1
    report["counts"]["real_nonlexical_native_policy_adoptions"]=0
    locator=module("gfp_opt_p1_branch_root_locator",
                   "Verification/reconcile_live_root_checkpoints_v1.py")
    candidate, _=locator.indexed_json(locator.CANDIDATES)
    catalog_live, catalog_blob=locator.indexed_json(locator.CATALOG)
    route_live, route_blob=locator.indexed_json(locator.ROUTES)
    locator.validate_sources(candidate,catalog_live,route_live,
                             catalog_blob,route_blob)
    candidate_by_key={x["root_key"]:x for x in candidate["checkpoint_slots"]}
    root_rows=[x for x in report["root_checkpoint_issue_triage"]
               if x.get("issue_type")=="ROOT_CHECKPOINT_UNTRACKED"]
    require(len(root_rows)==5
            and {x.get("root_key") for x in root_rows}==set(candidate_by_key),
            "ROOT_LOCATOR_TRIAGE_IDENTITY_DRIFT")
    # Preserve unrelated navigation warnings, but do not mistake them for
    # one of the five tracked root keys or silently discard them.
    for x in root_rows:
        pinned=candidate_by_key[x["root_key"]]
        candidate_branch=pinned.get("branch_candidate")
        x["branch_checkpoint_historical_observation"]=(
          {
            "qualified_branch":candidate_branch["branch"],
            "checkpoint_git_blob_observed":candidate_branch["checkpoint_blob"],
            "status":"EXACT_BRANCH_BLOB_OBSERVED_PREVIOUSLY__NOT_LIVE_VERIFIED_BY_DASHBOARD",
            "source_currentness":"NOT_VERIFIED"
          } if candidate_branch else None)
        if pinned["root_key"]=="nomen_verb_verbindungen":
            x["newer_library_candidate_is_unverified"]={
              "record_id":pinned["library_newer_candidate_observation"]["record_id"],
              "source_currentness":"REVIEW_REQUIRED__DO_NOT_USE_OLDER_BRANCH_AS_CURRENT"
            }
    report["counts"]["branch_qualified_checkpoint_candidates"]=sum(
         x["branch_checkpoint_historical_observation"] is not None
         for x in root_rows)
    report["counts"]["unresolved_grammar_branch_checkpoint_candidates"]=0
    report["root_branch_evidence_type"]="PINNED_HISTORICAL_BRANCH_LOCATION_ONLY__LIVE_REMOTE_WORKFLOW_SEPARATE"
    return report

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--output",type=Path,required=True)
    a.add_argument("--summary",action="store_true")
    args=a.parse_args()
    try:
        result=execute()
        target=args.output.resolve()
        require(target.suffix==".json" and target.parent.is_dir()
                and not target.exists() and not target.is_symlink()
                and ROOT.resolve() not in target.parents,
                "REPORT_NOT_NEW_OR_INSIDE_REPOSITORY")
        with target.open("x",encoding="utf-8") as f:
            json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2)
            f.write("\n")
        short={k:v for k,v in result.items() if k not in
               ("source_families","root_checkpoint_issue_triage")}
        print(json.dumps(short if args.summary else result,ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,subprocess.CalledProcessError) as e:
        print("GFP_OPT_DOMAIN_PREFLIGHT_HOLD:"+str(e),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
