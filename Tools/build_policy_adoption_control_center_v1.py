#!/usr/bin/env python3
"""Read-only GFP-OPT Control Center policy-adoption status over live Git INDEX.

Combines the existing 21-family identity dashboard, the current active-policy
candidate impact planner and a typed, exact-Git-pinned admission ledger.
Never turns Git status hints, old ZIP bytes or synthetic tests into ADOPTED.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
LEDGER="Optimization-Program/Control-Center/POLICY-ADOPTION-EVIDENCE-LEDGER-v1.json"
CATALOG="Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
DOMAINS="Optimization-Program/Control-Center/Profiles/P1-ALL-FAMILY-APPLICABILITY-v1.json"
REGISTRY="Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
SOURCE_RECEIPT="Optimization-Program/Verification/P1-REAL-LIVE-CONNECTOR-R8-NONADOPTION-20261105.json"
ROOT_STATE="PROJECT-STATE.json"
ROOT_FOCUS=("currentness","kombinationen_source_first","stage5_neutral_validator")
SCHEMA="gfp-opt-control-center-policy-adoption-status@1.0.0"
EVIDENCE_STATE="HISTORICAL_GIT_AND_LIBRARY_BYTES_MATCHED__NO_NEW_GOVERNED_INVOCATION"
ALLOWED_DOMAIN={
 "LEXICAL_SOURCE_CANDIDATE","MIXED_SOURCE_NEEDS_OUTPUT_SPLIT",
 "VISUAL_MEDIA_NEEDS_PROFILE","GRAMMAR_NEEDS_PROFILE",
 "READING_SKILLS_NEEDS_PROFILE","WRITING_SKILLS_NEEDS_PROFILE",
 "GENERIC_IMPORT_NATIVE_OUTPUT_UNRESOLVED"
}

def load_module(name:str,path:str):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    if spec is None or spec.loader is None:
        raise ValueError("UNAVAILABLE_REQUIRED_MODULE:"+name)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

phase=load_module("gfp_control_center_base","Tools/build_project_control_center_v1.py")
planner=load_module("gfp_p1_impact_for_adoption","Tools/plan_central_policy_impact_v1.py")
graph=load_module("gfp_p1_dependency_graph","Tools/build_project_dependency_evidence_v1.py")
nonlexical=load_module("gfp_p1_source_domain_preflight","Tools/build_domain_adapter_preflight_v1.py")

def require(ok:bool, code:str)->None:
    if not ok:
        raise ValueError(code)

def valid_sha(s:str, length:int=40)->bool:
    return isinstance(s,str) and re.fullmatch("[0-9a-f]{"+str(length)+"}",s) is not None

def source_proof(ledger:dict, index:dict, cat:dict, reg:dict):
    require(ledger.get("schema")=="gfp-opt-policy-adoption-evidence-ledger@1.0.0"
            and ledger.get("program_id")=="GFP-OPT-2026"
            and ledger.get("controller")=="Project Control Center"
            and ledger.get("authority")==
                "SCOPED_POLICY_ADOPTION_EVIDENCE_POINTERS__NEVER_SOURCE_STAGE_OR_CONTENT_CURRENT",
            "LEDGER_IDENTITY_OR_AUTHORITY_INVALID")
    declared={
        "catalog":CATALOG,
        "source_domains":DOMAINS,
        "policy_registry":REGISTRY
    }
    # The adopted ledger is an immutable 2026-11-05 *historical witness*.
    # Its original Registry SHA must agree with the separately stored historical
    # source-family profile, not with today's expanded live Registry SHA.
    # This preserves attribution and prevents yesterday's 15 rules from
    # vetoing today's user-approved curated-current rule.
    historic_profile=phase.load_json_from_index(DOMAINS,index)
    historic_registry=historic_profile.get("authority",{}).get("policy_registry",{})
    for key,path in declared.items():
        target=ledger.get("baseline",{}).get(key,{})
        ok=(target.get("path")==path and valid_sha(target.get("git_blob")))
        if key=="policy_registry":
            ok=ok and (historic_registry.get("path")==path and
                       target["git_blob"]==historic_registry.get("git_blob") and
                       valid_sha(index.get(path)))
        else:
            ok=ok and target["git_blob"]==index.get(path)
        require(ok,"LEDGER_BASELINE_GIT_PIN_DRIFT:"+key)
    require(reg.get("schema")=="gcpk-global-policy-registry@1.0.0"
            and "curated_current_delta_qa" in reg.get("policy_bindings",{}),
            "LIVE_CURATED_CURRENT_REGISTRY_NOT_ACTIVE")
    require(ledger.get("adoption_status")==
            "ZERO_NAMED_NATIVE_PRODUCERS_FORMALLY_ADOPTED__PROSPECTIVE_POLICY_ROUTING_EXISTS"
            and ledger.get("adoption_claims")==[],
            "FALSE_GLOBAL_OR_SOURCE_PRODUCER_ADOPTION")
    contract=ledger.get("submission_contract",{})
    for flag in (
      "write_source_specific_receipt_only_after_governed_native_build",
      "independent_live_main_pointer_and_library_bytes_required",
      "source_owner_and_stage_qa_required","provider_authenticity_required",
      "reject_unversioned_policy_or_unpinned_source",
      "no_auto_adoption_from_structural_format_evidence",
      "no_auto_adoption_from_historical_storage_byte_match",
      "no_auto_adoption_from_synthetic_ci",
      "no_retroactive_rewrite_of_locked_content",
      "no_app_ui_runtime_fsrs_srs_changes"
    ):
        require(contract.get(flag) is True,
                "ADOPTION_PROOF_GATE_DISABLED:"+flag)
    require(contract.get("formally_adopted_v1_allowed") is False,
            "UNAUTHORIZED_V1_ADOPTED_STATUS")
    records=ledger.get("historical_scoped_evidence")
    require(isinstance(records,list) and len(records)==1,
            "UNREVIEWED_HISTORICAL_EVIDENCE_COUNT")
    record=records[0]
    require(record.get("id")=="legacy-r8-250-verben"
            and record.get("kind")==
            "HISTORICAL_REAL_LIBRARY_BYTE_PARITY_WITHOUT_NEW_GOVERNED_PRODUCER_RECEIPT"
            and record.get("policy_binding_id")=="stage5_neutral_validator"
            and "stage5_neutral_validator" in reg.get("policy_bindings",{}),
            "HISTORICAL_ANCHOR_OR_POLICY_INVALID")
    family,workspace=record.get("family_id"),record.get("workspace_id")
    require(any(x.get("id")==family for x in cat["families"])
            and any(x.get("id")==workspace and x.get("parent_family_id")==family
                    for x in cat["workspaces"]),
            "HISTORICAL_ANCHOR_WRONG_OWNER")
    require(record.get("report_path")==SOURCE_RECEIPT
            and record.get("report_git_blob")==index.get(SOURCE_RECEIPT)
            and valid_sha(record.get("report_git_blob")),
            "HISTORICAL_CONNECTOR_REPORT_NOT_PINNED")
    receipt=phase.load_json_from_index(SOURCE_RECEIPT,index)
    require(isinstance(receipt,dict)
            and receipt.get("schema")==
               "gfp-opt-p1-live-github-and-library-connector-readback@1.0.0"
            and receipt.get("status")==
            "PASS_LIVE_GITHUB_MAIN_AND_FRESH_FILES_LIBRARY_RAW_BYTE_MATCH__LEGACY_NOT_NEW_GOVERNED_ADOPTION",
            "HISTORICAL_RECEIPT_NOT_THE_SCOPED_PROOF")
    git=receipt.get("sources",{}).get("github",{})
    lib=receipt.get("sources",{}).get("library",{})
    digest=record.get("historical_archive_sha256")
    pointer=record.get("old_source_latest_path")
    require(valid_sha(digest,64)
            and git.get("selected_artifact_sha256")==digest
            and lib.get("materialized_sha256")==digest
            and record.get("historical_library_record_id")==lib.get("library_record_id")
            and git.get("selected_library_record_id")==lib.get("library_record_id")
            and git.get("selected_artifact_bytes")==lib.get("materialized_actual_bytes")
            and git.get("workspace_latest_path")==pointer
            and pointer=="Workspaces/"+workspace.removeprefix("workspace:")+"/LATEST.json"
            and record.get("old_source_latest_git_blob")==git.get("latest_blob")
            and valid_sha(record.get("old_source_latest_git_blob")),
            "HISTORICAL_RECEIPT_SHA_OWNER_SIZE_MISMATCH")
    limits=receipt.get("important_limits",{})
    for key in ("is_actual_new_governed_build_receipt_present","is_new_policy_source_adopted",
                "source_semantic_stage4_reperformed","source_stage5_reaccepted",
                "native_stage6_browser_performed","stage7_final_performed"):
        require(limits.get(key) is False,"HISTORICAL_RECEIPT_FALSE_PROMOTION:"+key)
    require(record.get("evidence_status")==EVIDENCE_STATE
            and record.get("currentness")=="NOT_PROVEN_BY_HISTORICAL_RECEIPT"
            and record.get("source_semantic_stage4")=="NOT_REPERFORMED"
            and record.get("formal_stage5")=="NOT_REISSUED"
            and record.get("stage6")==record.get("stage7")=="NOT_RUN"
            and record.get("adopted_under_new_policy") is False,
            "HISTORICAL_LEDGER_CLAIMS_FORMAL_ADOPTION")
    return {
      "record":record,
      "historical_pointer_is_still_in_git_index":
          index.get(pointer)==record["old_source_latest_git_blob"],
      "historical_pointer_index_blob_today":index.get(pointer),
      "historical_library_record_id":lib["library_record_id"],
      "archive_sha256":digest,
      "historical_zip_readback_proof":"SCOPED_PAST_REAL_CONNECTOR_READBACK_NOT_RUN_IN_CI"
    }

def next_action(domain:str,stage5:str)->str:
    if domain=="GRAMMAR_NEEDS_PROFILE":
        return "DEFINE_GRAMMAR_SPECIFIC_PRODUCER_ADAPTER_AND_REAL_SEMANTIC_QA"
    if domain=="READING_SKILLS_NEEDS_PROFILE":
        return "DEFINE_LESEN_SOURCE_AND_NATIVE_TEXT_PRODUCER_ADAPTER"
    if domain=="WRITING_SKILLS_NEEDS_PROFILE":
        return "DEFINE_SCHREIBEN_NATIVE_OUTPUT_AND_FEEDBACK_ADAPTER"
    if domain=="VISUAL_MEDIA_NEEDS_PROFILE":
        return "DEFINE_IMAGE_CAPTION_SOURCE_AUTHORITY_AND_MEDIA_ADAPTER"
    if domain=="MIXED_SOURCE_NEEDS_OUTPUT_SPLIT":
        return "SPLIT_MIXED_SOURCE_OUTPUTS_BEFORE_APPLYING_FIELD_RULES"
    if domain=="GENERIC_IMPORT_NATIVE_OUTPUT_UNRESOLVED":
        return "IDENTIFY_GENERIC_VOCABULARY_SOURCE_AUTHORITY_AND_REAL_PRODUCER"
    if stage5=="HISTORICAL_FORMAT_WITNESS_NOT_CURRENT_OR_ADOPTED":
        return "ELIGIBLE_FUTURE_STAGE5_PRODUCER_MUST_GENERATE_NEW_GOVERNED_RECEIPT"
    return "RESOLVE_SOURCE_PROFILE_AND_REAL_NATIVE_PRODUCER_BEFORE_ADOPTION"

def build(ledger:dict,index:dict,snapshot:dict,impact:dict,cat:dict,domains:dict,
          historical:dict)->dict:
    require(snapshot.get("schema")=="gcpk-control-center-snapshot@1.0.0"
            and snapshot.get("authority")=="GIT_INDEX_METADATA_ONLY__NO_PASS_PROMOTION",
            "BASE_SNAPSHOT_NOT_METADATA_ONLY")
    require(impact.get("schema")=="gfp-opt-p1-central-policy-impact-and-adoption-plan@1.0.0"
            and impact.get("status")==
            "PASS_CONSERVATIVE_IMPACT_ROUTING_ONLY__ACTUAL_ADOPTION_OPEN",
            "IMPACT_PLAN_PROMOTED_TO_ADOPTION")
    selected=impact.get("selected_policy_bindings",[])
    active=phase.load_json_from_index(REGISTRY,index).get("policy_bindings",{})
    n=len(active)
    require(n>=22 and isinstance(selected,list) and len(selected)==n
            and len(set(selected))==n and set(selected)==set(active)
            and len(impact.get("family_impacts",[]))==len(cat["families"])*n
            and len(impact.get("workspace_impacts",[]))==len(cat["workspaces"])*n
            and len(impact.get("root_workstream_impacts",[]))==len(cat["root_workstreams"])*n,
            "POLICY_IMPACT_CARDINALITY_MISMATCH")
    fbyid={f["id"]:f for f in snapshot["families"]}
    prof={p["id"]:p for p in domains["families"]}
    impactby={(r["family_id"],r["policy_binding_id"]):r
              for r in impact["family_impacts"]}
    require(len(impactby)==len(cat["families"])*n,"DUPLICATE_FAMILY_POLICY_IMPACT")
    groups=defaultdict(list)
    for w in snapshot["workspaces"]:
        groups[w["parent_family_id"]].append(w)
    roots=defaultdict(list)
    for r in snapshot["root_workstreams"]:
        roots[r["family_id"]].append(r)
    rows=[]
    for family in cat["families"]:
        fid=family["id"]
        base=fbyid.get(fid)
        spec=prof.get(fid)
        require(base is not None and spec is not None and
                spec.get("declared_domain") in ALLOWED_DOMAIN,
                "UNMAPPED_FAMILY_OR_DOMAIN")
        allpolicy=[impactby[(fid,key)] for key in impact["selected_policy_bindings"]]
        stage5=impactby[(fid,"stage5_neutral_validator")]["impact_status"]
        witness=bool(spec.get("historical_neutral_format_witnesses"))
        evidence="NONE__NO_NEW_GOVERNED_PRODUCER_RECEIPT"
        remote=None
        if fid==historical["record"]["family_id"]:
            evidence="HISTORICAL_REAL_BYTES_MATCH_BUT_NO_NEW_GOVERNED_RECEIPT"
            remote={
                "historic_record":"legacy-r8-250-verben",
                "archive_sha256":historical["archive_sha256"],
                "old_library_record_id":historical["historical_library_record_id"],
                "current_index_pointer_matches_old_record":
                    historical["historical_pointer_is_still_in_git_index"],
                "current_pointer_index_blob":historical["historical_pointer_index_blob_today"],
                "historical_report_pinned_in_git":True,
                "not_new_policy_adoption":True
            }
        elif witness:
            evidence="HISTORICAL_REAL_FORMAT_ONLY__NO_NEW_GOVERNED_RECEIPT"
        candidates=Counter(x["impact_status"] for x in allpolicy)
        wsrows=[]
        for w in groups[fid]:
            wsrows.append({
                "workspace_id":w["id"],
                "git_dir":w["git_dir"],
                "kind":w["kind"],
                "reported_status_hint_not_stage_proof":w["reported_status_hint"],
                "next_action_hint_not_authority":w["next_action_hint"],
                "selected_pointer":w["display_pointer"],
                "pointer_git_index_blob":(
                    w["latest_index_blob_sha"] if w["display_pointer"] and
                    w["display_pointer"].endswith("/LATEST.json") else
                    w["checkpoint_index_blob_sha"]),
                "pointer_adoption_proof":"NOT_CERTIFIED",
            })
        rows.append({
          "family_id":fid,
          "family_name":family["name"],
          "source_domain":spec["declared_domain"],
          "candidate_policy_impacts":len(allpolicy),
          "all_policy_impact_states":dict(sorted(candidates.items())),
          "key_policies":{key:impactby[(fid,key)]["impact_status"]
                          for key in ROOT_FOCUS},
          "git_workspaces":wsrows,
          "root_summary_hints":[{"root_key":r["key"],
                                 "reported_status_hint_not_authority":r["summary_status_hint"],
                                 "checkpoint_path_hint":r["checkpoint_path"]}
                                 for r in roots[fid]],
          "historical_evidence_state":evidence,
          "real_legacy_details":remote,
          "new_governed_producer_receipt":"NOT_REGISTERED",
          "formal_policy_adoption":"NOT_ADOPTED",
          "stage4_semantic_signoff_from_this_control_center":"NOT_GRANTED",
          "stage5_source_acceptance_from_this_control_center":"NOT_GRANTED",
          "stage6_native_browser":"NOT_RUN_BY_THIS_TOOL",
          "stage7_final":"NOT_GRANTED",
          "source_currentness":"NOT_VERIFIED_BY_THIS_LEDGER",
          "next_action":next_action(spec["declared_domain"],stage5)
        })
    require(len(rows)==21 and sum(len(f["git_workspaces"]) for f in rows)==35
            and sum(len(f["root_summary_hints"]) for f in rows)==17,
            "DASHBOARD_CATALOG_CARDINALITY_DRIFT")
    return {
      "schema":SCHEMA,
      "program_id":"GFP-OPT-2026",
      "controller":"Project Control Center",
      "status":"PASS_CROSS_PROJECT_POLICY_STATUS_AS_GIT_INDEX_REPORT__ZERO_NEW_ADOPTIONS",
      "data_authority":{
        "ledger_git_index_blob_sha":index.get(LEDGER),
        "catalog_git_index_blob_sha":index.get(CATALOG),
        "policy_registry_git_index_blob_sha":index.get(REGISTRY),
        "root_state_git_index_blob_sha":index.get(ROOT_STATE),
        "git_index_not_verified_live_remote_main":True,
        "private_library_artifacts_not_read_by_ci":True,
        "historical_remote_bytes_are_past_scoped_receipts_only":True,
        "newer_user_artifacts_may_supersede_git":True
      },
      "counts":{
        "families":len(rows),
        "workspaces":35,
        "roots":17,
        "central_policy_bindings":n,
        "policy_family_candidate_impacts":len(cat["families"])*n,
        "workspace_pointer_navigation_views":len(cat["workspaces"])*n,
        "root_pointer_navigation_views":len(cat["root_workstreams"])*n,
        "explicit_historical_remote_byte_witnesses":1,
        "historical_neutral_format_families":
           sum(bool(prof[r["family_id"]]["historical_neutral_format_witnesses"]) for r in rows),
        "new_governed_policy_adoption_claims":0,
        "formally_adopted_producers":0,
        "stage4_5_6_7_certified_by_dashboard":0,
        "metadata_navigation_issues":len(snapshot["issues"])
      },
      "historical_record_pointer_freshness":
         "UNCHANGED_IN_CHECKOUT_INDEX__NOT_LIVE_CURRENT"
         if historical["historical_pointer_is_still_in_git_index"] else
         "POINTER_MOVED_SINCE_HISTORICAL_RECEIPT__RE_REVIEW_SOURCE",
      "source_families":rows,
      "navigation_issues":snapshot["issues"],
      "acceptance_boundaries":{
        "candidate_policy_applicability_is_not_adoption":True,
        "native_builder_exists_is_not_each_producer_invocation":True,
        "historical_byte_match_is_not_governed_receipt":True,
        "synthetic_ci_not_private_real_source_acceptance":True,
        "git_index_hints_not_exact_remote_latest_proof":True,
        "source_owner_stage_qa_and_provider_provenance_pending":True,
        "no_card_original_locked_content_runtime_ui_fsrs_srs_modified":True
      }
    }

def markdown(status:dict)->str:
    c=status["counts"]
    lines=[
      "# GFP-OPT — Central Policy Adoption & Project Status",
      "",
      "**READ-ONLY Git-index snapshot. Candidate impacts are NOT formal adoption, source CURRENT or Stage4–7 approvals.**",
      "",
      f"**{c['families']} source families** · **{c['workspaces']} Git workspaces** · **{c['roots']} root workstreams** · **{c['central_policy_bindings']} central policies**.",
      f"**{c['policy_family_candidate_impacts']} rule–family impact cells**, {c['workspace_pointer_navigation_views']} workspace and {c['root_pointer_navigation_views']} root navigation views; these overlap, not separate producers.",
      f"**Formal new governed producer adoptions: {c['formally_adopted_producers']}**. Historical scoped byte receipts: {c['explicit_historical_remote_byte_witnesses']}; historical neutral-format families: {c['historical_neutral_format_families']}.",
      "",
      "## Family / source-owner adoption truth",
      "",
      "| Source family | Domain | Git workspaces | Evidence type | Rule adoption | Next engineering action |",
      "|---|---|---:|---|---|---|"
    ]
    for f in status["source_families"]:
        esc=lambda v:str(v).replace("|","\\|").replace("\n"," ")
        lines.append("| "+" | ".join(map(esc,[
            f["family_name"],f["source_domain"],len(f["git_workspaces"]),
            f["historical_evidence_state"],f["formal_policy_adoption"],f["next_action"]
        ]))+" |")
    lines.extend([
       "",
       "## Active acceptance blockers",
       "",
       "A binding listed in the Global Policy Registry is **routed**, not automatically executable in all producers.",
       "The governed Stage5 launcher and remote-byte replay are available only for eligible native vocabulary output.",
       "250 Verben R8 was checked via real GitHub/Library bytes, but is an old artifact **without a newly governed launcher receipt**.",
       "The real-source format witness for Menschen A1 Verben is historical, not a source-owner adoption record.",
       "Nonlexical Grammar, Lesen, Schreiben and visual/mixed sources require independent adapters.",
       "Current user-validated source artifacts can supersede Git. Real source-owner approval, provider provenance and semantic/stage QA are not inferred.",
       "",
       "## Workstream Git-index status hints",
       "",
       "| Workspace | Git status hint (unverified) | Pointer | Parent family |",
       "|---|---|---|---|"
    ])
    for f in status["source_families"]:
        for w in f["git_workspaces"]:
            esc=lambda v:str(v or "—").replace("|","\\|").replace("\n"," ")
            lines.append("| "+" | ".join(map(esc,[
                w["git_dir"],w["reported_status_hint_not_stage_proof"],
                w["selected_pointer"],f["family_id"]
            ]))+" |")
    lines.extend(["","## Next priority",
       "",
       "P1: one **new authorized source-owner run** must create a real governed native policy receipt, then pass independent GitHub main and authenticated Library readback plus source semantic/stage review before scoped ADOPTED. Continue non-neutral producer adapter work in parallel.",
       "P3: feed the typed source statuses from this report into a higher-level management dashboard. Do not auto-promote old receipts or rewrite LOCKED files.",
       ""])
    domain=status.get("nonlexical_domain_preflight",{})
    if domain:
        lines.extend(["", "## Nonlexical native source readiness — actual Lesen Stage1 derived replay; other sources shadow only", "",
          "| Source family | Native checkpoint tracked | Real derived QA bytes | Adapter readiness | Next safe action |",
          "|---|---|---|---|---|"])
        for item in domain["source_families"]:
            replay=item.get("native_stage1_actual_git_derived_replay")
            proof=("REAL Git inventory + ID map 68 topics / 76 pages (source PDF NOT reread)"
                   if replay and replay["status"]==
                   "PASS_ACTUAL_GIT_READING_STAGE1_DERIVED_BYTES_AND_STRUCTURE_REPLAY_ONLY"
                   else "NOT PERFORMED")
            lines.append("| " + " | ".join(str(v).replace("|","\\|") for v in (
                item["family_id"],
                "YES" if item["native_checkpoint_tracked_in_git_index"] else "NO",
                proof,item["status"],item["next_action"]))+" |")
        lines.extend(["","## Untracked main checkpoint references — five historical owner-branch locators; no auto-repair","",
          "| Root key | Missing main path | Branch-qualified historical candidate | Diagnosis |",
          "|---|---|---|---|"])
        for item in domain["root_checkpoint_issue_triage"]:
            locator=item.get("branch_checkpoint_historical_observation") or {}
            branch=locator.get("qualified_branch")
            status=("branch "+branch+"; blob "+locator.get("checkpoint_git_blob_observed","")[:12]+
                    " (NOT CURRENT)" if branch else "SOURCE OWNER HOLD")
            lines.append("| " + " | ".join(str(v).replace("|","\\|") for v in (
                item.get("root_key","UNMAPPED"),item["reported_path"],status,item["status"]))+" |")
        lines.extend(["",
          "**Lesen Stage1 derived Git evidence has been independently replayed; original source PDF bytes and new native producer execution have NOT been verified. All source producer policy adoptions remain ZERO.** Root checkpoint references must be resolved by their actual source owners; a missing Git pointer is not evidence of a content QA failure.",
          ""])
    return "\n".join(lines)

def execute(root:Path=ROOT)->dict:
    require(root.resolve()==ROOT.resolve(),"UNSUPPORTED_ROOT_FOR_GIT_INDEX")
    index=graph.index_blobs(root)
    ledger=phase.load_json_from_index(LEDGER,index,root)
    cat=phase.load_json_from_index(CATALOG,index,root)
    domains=phase.load_json_from_index(DOMAINS,index,root)
    reg=phase.load_json_from_index(REGISTRY,index,root)
    state=phase.load_json_from_index(ROOT_STATE,index,root)
    require(all(isinstance(x,dict) for x in (ledger,cat,domains,reg,state)),
            "MISSING_EXACT_GIT_INDEX_AUTHORITIES")
    require(not phase.catalog_errors(cat),"CATALOG_INVALID")
    historical=source_proof(ledger,index,cat,reg)
    impact=planner.execute(root)
    dirs=phase.tracked_dirs(index)
    pointers={}
    for d in dirs:
        for name in ("LATEST.json","CHECKPOINT.json"):
            p=d+"/"+name
            if p in index:
                pointers[p]=phase.load_json_from_index(p,index,root)
    snapshot=phase.build(cat,index,state,pointers)
    report=build(ledger,index,snapshot,impact,cat,domains,historical)
    preflight=nonlexical.execute(root)
    require(preflight["schema"]=="gfp-opt-p1-cross-domain-native-adapter-readiness@1.0.0"
            and preflight["status"]==
            "PASS_DOMAIN_AND_METADATA_ROUTING_ONLY__ALL_NATIVE_ADOPTIONS_HELD"
            and preflight["counts"]["actual_domain_adapters_adopted"]==0
            and preflight["counts"]["source_stage_passes_certified_by_preflight"]==0,
            "NONLEXICAL_PREFLIGHT_NOT_SHADOW")
    report["nonlexical_domain_preflight"]=preflight
    report["counts"]["nonlexical_source_families_profiled"]=preflight["counts"]["nonlexical_family_profiles"]
    report["counts"]["triaged_untracked_root_checkpoints"]=preflight["counts"]["classified_existing_root_checkpoint_issues"]
    return report

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--github-summary",action="store_true")
    p.add_argument("--family-id",help="Optional filtered view of one family; output is labelled filtered")
    args=p.parse_args()
    try:
        report=execute()
        if args.family_id:
            selection=[f for f in report["source_families"]
                       if f["family_id"]==args.family_id]
            require(len(selection)==1,"UNKNOWN_FAMILY")
            report["source_families"]=selection
            report["display_filtered_family_only"]=True
        dest=args.output_dir.resolve()
        protected=[ROOT/"Workspaces",ROOT/"Prompt",
                   ROOT/"Optimization-Program",ROOT/"Verification",
                   ROOT/"Tools",ROOT/"Data",ROOT/"Content",ROOT/"Source"]
        require(dest != ROOT.resolve() and
                not any(folder.resolve()==dest or
                        folder.resolve() in dest.parents for folder in protected)
                and not dest.is_symlink(),
                "UNSAFE_DASHBOARD_DESTINATION")
        dest.mkdir(parents=True,exist_ok=True)
        for filename in ("POLICY-ADOPTION-STATUS.json","POLICY-ADOPTION-STATUS.md"):
            require(not (dest/filename).exists()
                    and not (dest/filename).is_symlink(),
                    "REPORT_EXISTING_MUST_NOT_BE_OVERWRITTEN")
        body=markdown(report)
        with (dest/"POLICY-ADOPTION-STATUS.json").open("x",encoding="utf-8") as file:
            json.dump(report,file,ensure_ascii=False,indent=2,sort_keys=True)
            file.write("\n")
        with (dest/"POLICY-ADOPTION-STATUS.md").open("x",encoding="utf-8") as file:
            file.write(body)
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as file:
                file.write(body)
        print(json.dumps({"status":report["status"],
                          "counts":report["counts"],
                          "output_dir":str(dest),
                          "new_governed_adoptions":0},
                         ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,subprocess.CalledProcessError) as exc:
        print("GFP_OPT_ADOPTION_DASHBOARD_BLOCKED:"+str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
