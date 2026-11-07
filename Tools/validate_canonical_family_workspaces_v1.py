#!/usr/bin/env python3
"""Fail-closed canonical family Workspace routing guard (no file mutations).

Validates exactly one intended Git owner per represented family, checks selected
curated source owner remains inside that canonical Workspace, and blocks
unregistered sibling directories. Existing 36 directories are grandfathered,
NOT deleted or considered all inactive. A future directory requires a genuinely
explicit recorded migration/initialization approval; the guard never creates it.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

SCHEMA="gcpk-canonical-family-workspace-routing@1.0.0"
ROUTING="Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"
CATALOG="Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
PORTFOLIO="Optimization-Program/Control-Center/DYNAMIC-CONTENT-PORTFOLIO-REGISTRY-v1.json"
WORKSPACE_ROLES={"CANONICAL","COMPATIBILITY_LEGACY"}
NEW_AUTHORIZATION_SCHEMA="gcpk-workspace-new-canonical-approval@1.0.0"


def read_json(file:Path)->dict:
    data=json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data,dict):
        raise ValueError("Expected JSON object")
    return data


def safe_dir(root:Path,rel:str)->Path:
    if not isinstance(rel,str) or not rel.startswith("Workspaces/"):
        raise ValueError("Workspace must be a top-level Workspaces/ folder")
    parts=rel.split("/")
    if len(parts)!=2 or any(x in ("",".","..") for x in parts) or "\\" in rel:
        raise ValueError("Unsafe workspace path")
    home=root.resolve()
    full=(home/rel).resolve()
    if not full.is_relative_to(home):
        raise ValueError("Workspace escapes Git checkout")
    return full


def authority_approval(root:Path,authorization:dict,required_family:str,required_new_path:str,previous_path:str|None):
    if not isinstance(authorization,dict):
        raise ValueError("Invalid creation/migration authorization")
    if authorization.get("family_id")!=required_family or authorization.get("new_git_workspace")!=required_new_path:
        raise ValueError("Wrong family or path in approval")
    if authorization.get("previous_git_workspace")!=previous_path:
        raise ValueError("Previous canonical route not matched")
    route=authorization.get("approval_receipt")
    if not isinstance(route,str) or not route.startswith("Optimization-Program/Control-Center/Approvals/"):
        raise ValueError("Approval must be a dedicated Control Center receipt")
    if "\\" in route or ".." in route.split("/"):
        raise ValueError("Unsafe approval receipt")
    home=root.resolve()
    p=(home/route).resolve()
    if not p.is_relative_to(home) or not p.is_file():
        raise ValueError("Missing dedicated approval receipt")
    signed=read_json(p)
    if (signed.get("schema")!=NEW_AUTHORIZATION_SCHEMA
        or signed.get("user_explicit_approval") is not True
        or signed.get("family_id")!=required_family
        or signed.get("new_git_workspace")!=required_new_path
        or signed.get("previous_git_workspace")!=previous_path
        or signed.get("approval_scope")!="CANONICAL_WORKSPACE_ROUTE_ONLY_NO_DATA_DELETION"):
        raise ValueError("Approval evidence does not match exact family, old/new paths and scope")
    # A receipt is an input claimed as approval, not independent evidence of a
    # live user action; reviewers must check real user-authorized provenance.


def inspect(root:Path)->dict:
    home=root.resolve()
    catalog=read_json(home/CATALOG)
    routing=read_json(home/ROUTING)
    portfolio=read_json(home/PORTFOLIO)
    if routing.get("schema")!=SCHEMA:
        raise ValueError("Unrecognized canonical routing schema")
    if routing.get("change_type")!="ADDITIVE_ROUTING_AND_NEW_WORKSPACE_CREATION_GUARD__NO_PHYSICAL_MIGRATION":
        raise ValueError("Routing cannot silently imply a folder migration")
    guard=routing.get("prohibition",{})
    if not all(guard.get(k) is False for k in ("auto_folder_move","auto_delete","auto_new_workspaces","auto_accept_content","auto_stage6_final","auto_release_promotion")):
        raise ValueError("Unsafe auto operation setting in routing")
    fams=catalog.get("families")
    dirs=catalog.get("workspaces")
    rfams=routing.get("families")
    roles=routing.get("workspaces")
    baseline=routing.get("grandfathered_workspace_directories")
    if not all(isinstance(x,list) for x in (fams,dirs,rfams,roles,baseline)):
        raise ValueError("Missing catalog/routing arrays")
    if len(fams)!=21 or len(rfams)!=21 or len(baseline)!=36 or len(roles)<36 or len(dirs)<36:
        raise ValueError("Required reviewed 21-family/36-directory baseline missing")
    family_by_id={x["id"]:x for x in fams}
    route_by_id={x["family_id"]:x for x in rfams}
    if len(family_by_id)!=len(fams) or len(route_by_id)!=len(rfams) or set(route_by_id)!=set(family_by_id):
        raise ValueError("Family mapping must be unique and complete")
    catalog_by_dir={x["git_dir"]:x for x in dirs}
    role_by_dir={x["git_dir"]:x for x in roles}
    if len(catalog_by_dir)!=len(dirs) or len(role_by_dir)!=len(roles) or set(role_by_dir)!=set(catalog_by_dir):
        raise ValueError("Workspace catalog and role map must match 1:1")
    baseline_set=set(baseline)
    if len(baseline_set)!=36 or any(not isinstance(w,str) for w in baseline):
        raise ValueError("Grandfathered baseline malformed")
    for path in baseline_set|set(catalog_by_dir):
        safe_dir(home,path)
    if not baseline_set.issubset(catalog_by_dir):
        raise ValueError("Original workspace directory removed or renamed")
    new_paths=set(catalog_by_dir)-baseline_set
    migrations={r["family_id"]:r for r in rfams if r.get("initial_canonical_git_workspace")!=r.get("canonical_git_workspace")}
    if not new_paths.issubset({r["canonical_git_workspace"] for r in migrations.values()}):
        raise ValueError("New top-level workspace is not an approved canonical route change")
    for route in rfams:
        fid=route["family_id"]
        if route.get("canonical_library_root")!=family_by_id[fid].get("library_path"):
            raise ValueError("Canonical Library family root altered "+fid)
        selected=route.get("canonical_git_workspace")
        mapped=[p for p,w in catalog_by_dir.items() if w["parent_family_id"]==fid]
        role_canonical=[x for x in roles if x["family_id"]==fid and x["role"]=="CANONICAL"]
        if selected is None:
            if mapped or role_canonical or route.get("active_content_sha256"):
                raise ValueError("No-Git family must not silently have workspace/current "+fid)
        elif selected not in mapped or len(role_canonical)!=1 or role_canonical[0]["git_dir"]!=selected:
            raise ValueError("Family must have exactly one catalogued canonical Git workspace "+fid)
        if route.get("no_new_git_workspace_created") is not (selected not in new_paths):
            raise ValueError("Workspace creation flag contradicts the actual approved new path")
    for path,role in role_by_dir.items():
        original=catalog_by_dir[path]
        if role.get("workspace_id")!=original.get("id") or role.get("family_id")!=original.get("parent_family_id"):
            raise ValueError("Workspace identity collision "+path)
        if role.get("role") not in WORKSPACE_ROLES:
            raise ValueError("Unknown workspace role "+path)
        if role.get("archive_or_move_status")!="NOT_MOVED_NOT_DELETED":
            raise ValueError("No old folders may be implicitly archived/deleted")
        selected=route_by_id[role["family_id"]]["canonical_git_workspace"]
        if ((role["role"]=="CANONICAL") != (path==selected)):
            raise ValueError("Duplicate/noncanonical owner: "+path)
        if role.get("future_accepted_current_pointer_location")!=selected:
            raise ValueError("Legacy workspace cannot be its own future CURRENT authority")
    curated=portfolio.get("items")
    if not isinstance(curated,list) or len(curated)!=10:
        raise ValueError("Ten current curated content authorities required")
    seen=set()
    for item in curated:
        fid=item["id"]
        if fid in seen or fid not in route_by_id:
            raise ValueError("Unmapped or duplicated curated family")
        seen.add(fid)
        path=item["owner_locator"]["path"]
        canonical=route_by_id[fid]["canonical_git_workspace"]
        if not path.startswith(canonical+"/"):
            raise ValueError("Curated selected source-owner is not inside canonical Workspace "+fid)
        if route_by_id[fid].get("canonical_source_owner_document")!=path or (
            route_by_id[fid].get("active_content_sha256")!=item["active_baseline"]["artifact_sha256"]):
            raise ValueError("Canonical routing stale vs curated current SHA "+fid)
    for route in rfams:
        if route["family_id"] not in seen and (route.get("canonical_source_owner_document") or route.get("active_content_sha256")):
            raise ValueError("Noncurated family cannot assert a current accepted artifact")
    authorizations=routing.get("migration_authorizations",[])
    if not isinstance(authorizations,list) or len(authorizations)!=len(migrations):
        raise ValueError("Every changed canonical route requires its own explicit approval receipt")
    registered=set()
    for authorization in authorizations:
        fid=authorization.get("family_id")
        if fid not in migrations or fid in registered:
            raise ValueError("Unknown/duplicate canonical migration family")
        registered.add(fid)
        target=migrations[fid]["canonical_git_workspace"]
        former=migrations[fid]["initial_canonical_git_workspace"]
        if authorization.get("new_git_workspace")!=target or authorization.get("previous_git_workspace")!=former:
            raise ValueError("Canonical migration cannot silently replace the original route")
        if role_by_dir[target]["role"]!="CANONICAL":
            raise ValueError("Only an explicitly reviewed canonical replacement is permitted")
        if former is not None and (former not in baseline_set or role_by_dir[former]["family_id"]!=fid):
            raise ValueError("Historical canonical predecessor must remain in the same family")
        authority_approval(home,authorization,fid,target,former)
    work=root/"Workspaces"
    observed={("Workspaces/"+p.name) for p in work.iterdir() if p.is_dir()} if work.is_dir() else set()
    if observed!=set(catalog_by_dir):
        raise ValueError("Workspace directory mismatch (unregistered or missing): "+
                         str(sorted(observed-set(catalog_by_dir)))+"; "+
                         str(sorted(set(catalog_by_dir)-observed)))
    counts={"families":len(rfams),"canonical_git":sum(x["canonical_git_workspace"] is not None for x in rfams),
            "library_only":sum(x["canonical_git_workspace"] is None for x in rfams),
            "preserved_legacy":sum(x["role"]=="COMPATIBILITY_LEGACY" for x in roles),
            "grandfathered_dirs":len(baseline_set),"approved_new_dirs":len(new_paths),
            "source_owner_pins_aligned":len(curated)}
    if not new_paths and counts!={"families":21,"canonical_git":16,"library_only":5,
        "preserved_legacy":20,"grandfathered_dirs":36,
        "approved_new_dirs":0,"source_owner_pins_aligned":10}:
        raise ValueError("Initial reviewed canonical migration baseline changed unexpectedly")
    if routing.get("counts")!={k:counts[v] for k,v in (
        ("families","families"),("canonical_git_workspaces","canonical_git"),
        ("library_only_families","library_only"),("prior_workspace_directories","grandfathered_dirs"),
        ("legacy_compatibility_directories","preserved_legacy"))}:
        raise ValueError("Published routing summary counters drifted")
    return {"schema":"gcpk-canonical-family-routing-gate@1.0.0",
        "status":("PASS_ROUTING_ONE_CANONICAL_PER_FAMILY__APPROVED_CHANGES_CHECKED" if migrations
                  else "PASS_ROUTING_ONE_CANONICAL_PER_FAMILY__ZERO_PHYSICAL_CHANGES"),
        "counts":counts,"new_git_workspace_creation":"BLOCKED_UNLESS_EXPLICIT_REVIEWED_APPROVAL",
        "runtime_or_content_final_claims":"NONE",
        "live_library_or_drive_scanned":False,"automatic_source_content_or_srs_changes":False}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out-dir",type=Path)
    ap.add_argument("--github-summary",action="store_true")
    args=ap.parse_args(argv)
    try:
        report=inspect(args.repo_root)
        if args.out_dir:
            dest=args.out_dir.resolve()
            if dest.is_relative_to(args.repo_root.resolve()):
                raise ValueError("Cannot write generated reports into Git checkout")
            dest.mkdir(parents=True,exist_ok=True)
            (dest/"CANONICAL-WORKSPACE-GATE.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as out:
                out.write("### Canonical Workspace Routing\n\n"+
                    report["status"]+"\n\n"+json.dumps(report["counts"],ensure_ascii=False)+"\n")
        print(json.dumps(report,indent=2))
        return 0
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as err:
        print(json.dumps({"status":"HOLD_CANONICAL_WORKSPACE_ROUTING", "reason":type(err).__name__+": "+str(err)[:480]}))
        return 2


if __name__=="__main__":
    sys.exit(main())
