#!/usr/bin/env python3
"""GFP-OPT P1: read-only branch-qualified recovery for five root CHECKPOINT HOLDs.

Read exact source files from live GitHub at immutable main/owner branch commits.
Branch presence and matching Git blobs prove a safe NAVIGATION TARGET only.
Never copy checkpoints to main, claim CURRENT, reissue Stage QA or mark ADOPTED.
"""
from __future__ import annotations
import argparse
import base64
import binascii
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
REPO="hosseinmehdizade-tech/German-Content-Production-Kit"
API="https://api.github.com/repos/"+REPO
CATALOG="Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
ROUTES="Optimization-Program/RESUME-ROUTES.json"
CANDIDATES="Optimization-Program/Control-Center/ROOT-CHECKPOINT-BRANCH-CANDIDATES-v1.json"
SCHEMA="gfp-opt-p1-branch-checkpoint-live-navigation@1.0.0"
EXPECTED_ISSUES={
 "250_verben_mit_praepositionen_deutschweb",
 "250_verben_mit_praepositionen_kombinationen",
 "grammar_aktiv_a1_c1",
 "nomen_verb_verbindungen",
 "unregelmaessige_verben_kombinationen",
}
BRANCH=re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,110}$")
BLOB=re.compile(r"^[a-f0-9]{40}$")
OWNER_FIELDS={"workstream","workspace","dataset_id"}

def require(ok,code):
    if not ok:
        raise ValueError(code)

def strict_json(raw):
    def pairs(seq):
        out={}
        for k,v in seq:
            require(k not in out,"DUPLICATE_JSON_FIELD:"+str(k))
            out[k]=v
        return out
    val=json.loads(raw.decode("utf-8-sig"),object_pairs_hook=pairs)
    require(isinstance(val,dict),"JSON_NOT_OBJECT")
    return val

def git_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()

def indexed_json(path):
    raw=subprocess.check_output(["git","ls-files","--stage","--",path],
                                cwd=ROOT).decode("utf-8")
    lines=raw.strip().splitlines()
    require(len(lines)==1,"UNTRACKED_CONFIG:"+path)
    match=re.fullmatch("100644 ([a-f0-9]{40}) 0\t"+re.escape(path),lines[0])
    require(match is not None,"UNMERGED_OR_UNSAFE_INDEX_CONFIG:"+path)
    data=subprocess.check_output(["git","cat-file","blob",match.group(1)],cwd=ROOT)
    require(git_blob(data)==match.group(1),"CORRUPT_GIT_CONFIG:"+path)
    return strict_json(data),match.group(1)

def fetch_json(url):
    require(url.startswith(API+"/") and "@" not in url,"UNTRUSTED_API_TARGET")
    header={"Accept":"application/vnd.github+json",
            "User-Agent":"GFP-OPT-branch-readback-v1",
            "X-GitHub-Api-Version":"2022-11-28"}
    token=os.environ.get("GITHUB_TOKEN")
    if token:
        header["Authorization"]="Bearer "+token
    req=Request(url,headers=header)
    try:
        with urlopen(req,timeout=25) as response:
            require(response.status==200,"GITHUB_RESPONSE_NOT_200")
            data=response.read(3_000_000)
    except HTTPError as error:
        if error.code==404:
            return None
        raise
    require(len(data)<3_000_000,"GITHUB_RESPONSE_TOO_LARGE")
    return strict_json(data)

def head(branch,fetch=fetch_json):
    require(BRANCH.fullmatch(branch) is not None,"INVALID_BRANCH_NAME")
    obj=fetch(API+"/git/ref/heads/"+quote(branch,safe=""))
    require(isinstance(obj,dict)
            and isinstance(obj.get("object"),dict)
            and obj["object"].get("type")=="commit"
            and BLOB.fullmatch(str(obj["object"].get("sha",""))) is not None,
            "GITHUB_BRANCH_HEAD_UNAVAILABLE:"+branch)
    return obj["object"]["sha"]

def content(path,at_sha,fetch=fetch_json):
    require(path.startswith("Workspaces/") and
            path.endswith("/CHECKPOINT.json")
            and ".." not in path and "\\" not in path
            and BLOB.fullmatch(at_sha) is not None,
            "UNSAFE_CHECKPOINT_PATH_OR_REF")
    url=API+"/contents/"+quote(path,safe="/")+"?ref="+at_sha
    obj=fetch(url)
    if obj is None:
        return None
    require(obj.get("type")=="file" and obj.get("path")==path
            and obj.get("encoding")=="base64"
            and isinstance(obj.get("content"),str)
            and BLOB.fullmatch(str(obj.get("sha",""))) is not None,
            "GITHUB_UNEXPECTED_CHECKPOINT_CONTENTS")
    try:
        raw=base64.b64decode("".join(obj["content"].split()),validate=True)
    except (ValueError,binascii.Error) as exc:
        raise ValueError("CORRUPT_GITHUB_BASE64") from exc
    require(0<len(raw)<3_000_000 and obj.get("size")==len(raw)
            and git_blob(raw)==obj["sha"],"GITHUB_CHECKPOINT_GIT_BLOB_INVALID")
    return {"blob":obj["sha"],"document":strict_json(raw),"bytes":len(raw)}

def checkpoint_status(document,candidate):
    """Only the pinned native Grammar schema may use a nested Stage7 status."""
    selector=candidate.get("status_selector")
    if selector is None:
        return document.get("status")
    if selector=="stages.7_release_post_package_verification.state":
        stages=document.get("stages")
        if not isinstance(stages,dict):
            return None
        final=stages.get("7_release_post_package_verification")
        return final.get("state") if isinstance(final,dict) else None
    return None

def validate_sources(candidates,catalog,routes,cat_blob,route_blob):
    require(candidates.get("schema")==
            "gfp-opt-p1-branch-qualified-root-checkpoint-evidence@1.0.0"
            and candidates.get("authority")==
            "SCOPED_GITHUB_BRANCH_FILE_EXISTENCE_WITNESS__NEVER_CONTENT_CURRENT_OR_STAGE_ADOPTION",
            "ROOT_RECOVERY_AUTHORITY_INVALID")
    for field,name,actual in (
        ("catalog_authority",CATALOG,cat_blob),
        ("root_route_authority",ROUTES,route_blob)
    ):
        value=candidates.get(field,{})
        require(value.get("path")==name and value.get("git_blob")==actual,
                "ROOT_RECOVERY_BASELINE_PIN_DRIFT:"+field)
    safeguards=candidates.get("safety",{})
    require(len(safeguards)==9 and all(v is True for v in safeguards.values()),
            "ROOT_RECOVERY_SAFETY_DISABLED")
    slots=candidates.get("checkpoint_slots",[])
    require(len(slots)==5 and {x.get("root_key") for x in slots}==EXPECTED_ISSUES,
            "ROOT_CHECKPOINT_CANDIDATE_COVERAGE_INVALID")
    owned={x["key"]:x["parent_family_id"] for x in catalog.get("root_workstreams",[])}
    located={x["key"]:x for x in routes.get("routes",[])}
    candidate_count=0
    seen_branches=set()
    for x in slots:
        key=x["root_key"]
        require(key in owned and key in located and
                x.get("family_id")==owned[key]
                and x.get("main_declared_checkpoint")==
                    (located[key].get("checkpoint") or {}).get("path")
                and located[key]["checkpoint"].get("tracked") is False,
                "ROOT_ROUTE_OWNER_OR_MISSING_MAIN_PATH_CONTRADICTION:"+key)
        cand=x.get("branch_candidate")
        if cand is not None:
            candidate_count+=1
            branch=cand.get("branch")
            require(isinstance(branch,str) and BRANCH.fullmatch(branch) is not None
                    and BLOB.fullmatch(str(cand.get("checkpoint_blob",""))) is not None
                    and cand.get("owner_field") in OWNER_FIELDS
                    and isinstance(cand.get("owner_value"),str)
                    and cand["owner_value"]
                    and isinstance(cand.get("observed_source_checkpoint_status"),str)
                    and cand["observed_source_checkpoint_status"],
                    "MALFORMED_BRANCH_EVIDENCE:"+key)
            require(branch not in seen_branches,"BRANCH_CANDIDATE_REUSED_FOR_ANOTHER_ROOT")
            seen_branches.add(branch)
            if key=="grammar_aktiv_a1_c1":
                require(cand["owner_field"]=="dataset_id"
                        and cand["owner_value"]=="grammatik-aktiv-a1-c1"
                        and cand.get("status_selector")==
                            "stages.7_release_post_package_verification.state",
                        "GRAMMAR_NATIVE_CHECKPOINT_SELECTOR_REQUIRED")
            else:
                require(cand["owner_field"] in {"workstream","workspace"}
                        and "status_selector" not in cand,
                        "NON_GRAMMAR_CHECKPOINT_SELECTOR_NOT_ALLOWED")
        else:
            require(False,"MISSING_BRANCH_CANDIDATE_NEEDS_REVIEW:"+key)
    require(candidate_count==5,"NOT_FIVE_BRANCH_WITNESSES")
    nvv=next(x for x in slots if x["root_key"]=="nomen_verb_verbindungen")
    newer=nvv.get("library_newer_candidate_observation",{})
    require(newer.get("record_id")=="libfile_a8efd55b225c81918b304349f475e92e"
            and newer.get("sha256")=="UNKNOWN__NOT_DOWNLOADED"
            and newer.get("is_current_or_accepted")=="NOT_PROVEN",
            "NVV_LIBRARY_METADATA_FALSIFIED_AS_CURRENT")

def live_report(candidates,catalog,routes,cat_blob,route_blob,fetch=fetch_json):
    validate_sources(candidates,catalog,routes,cat_blob,route_blob)
    main=head("main",fetch)
    slots=[]
    for x in candidates["checkpoint_slots"]:
        path=x["main_declared_checkpoint"]
        existing=content(path,main,fetch)
        cand=x.get("branch_candidate")
        item={
          "root_key":x["root_key"],
          "family_id":x["family_id"],
          "declared_main_path":path,
          "main_path_at_checked_main_commit":
             "MISSING" if existing is None else "PRESENT__ROOT_METADATA_REVIEW_REQUIRED",
          "branch_locator":None,
          "source_currentness":"NOT_VERIFIED",
          "source_owner_stage_acceptance":"NOT_REISSUED",
          "policy_adopted":False,
          "automatic_checkpoint_repair_performed":False
        }
        if cand is None:
            item["status"]="NO_BRANCH_CANDIDATE__SOURCE_OWNER_HOLD"
        else:
            branch=cand["branch"]
            first=head(branch,fetch)
            read=content(path,first,fetch)
            second=head(branch,fetch)
            if first!=second:
                state="BRANCH_MOVED_DURING_READBACK__RETRY"
            elif read is None:
                state="BRANCH_CHECKPOINT_DISAPPEARED__SOURCE_OWNER_REVIEW"
            elif read["blob"]!=cand["checkpoint_blob"]:
                state="BRANCH_CHECKPOINT_BLOB_CHANGED__SOURCE_OWNER_REVIEW"
            elif (read["document"].get(cand["owner_field"])!=cand["owner_value"]
                  or checkpoint_status(read["document"],cand)!=
                     cand["observed_source_checkpoint_status"]):
                state="BRANCH_CHECKPOINT_OWNER_OR_STATUS_DRIFT__SOURCE_OWNER_REVIEW"
            else:
                state="PASS_BRANCH_QUALIFIED_CHECKPOINT_BLOB_EXISTS__NOT_CURRENT"
            item["status"]=state
            item["branch_locator"]={
                "branch_name":branch,
                "first_branch_commit":first,
                "second_branch_commit":second,
                "checkpoint_git_blob_observed":read["blob"] if read else None,
                "expected_historical_checkpoint_git_blob":cand["checkpoint_blob"],
                "qualified_path":branch+":"+path,
                "observed_checkpoint_bytes":read["bytes"] if read else None
            }
        if item["main_path_at_checked_main_commit"]!="MISSING":
            item["status"]="MAIN_PATH_NOW_PRESENT__ROOT_ROUTE_TRIAGE_REVIEW_REQUIRED"
        if x["root_key"]=="nomen_verb_verbindungen":
            item["separate_library_newer_candidate"]={
                "record_id":x["library_newer_candidate_observation"]["record_id"],
                "observation_is_provider_listing_metadata_not_content_validation":True,
                "source_currentness_conflict":"OLDER_BRANCH_RECORD_VS_NEWER_LIBRARY_CANDIDATE__HOLD"
            }
        slots.append(item)
    require(head("main",fetch)==main,"MAIN_MOVED_DURING_ROOT_RECOVERY_READBACK")
    passed=sum(x["status"]==
        "PASS_BRANCH_QUALIFIED_CHECKPOINT_BLOB_EXISTS__NOT_CURRENT" for x in slots)
    missing=sum(x["main_path_at_checked_main_commit"]=="MISSING" for x in slots)
    return {
      "schema":SCHEMA,
      "program_id":"GFP-OPT-2026",
      "status":("PASS_FIVE_LIVE_BRANCH_LOCATORS__ZERO_SOURCE_PROMOTION"
                if passed==5 and missing==5 else
                "SOURCE_BRANCH_DRIFT_OR_MAIN_POINTER_CHANGED__REVIEW_REQUIRED"),
      "github_main_commit_observed_twice":main,
      "counts":{
        "missing_root_paths_checked":5,
        "still_missing_on_main":missing,
        "branch_candidates":5,
        "exact_live_branch_blob_locs":passed,
        "source_current_confirmed":0,
        "root_checkpoint_files_created":0,
        "formal_new_policy_adoptions":0
      },
      "roots":slots,
      "authenticated_library_zip_bytes_by_this_tool":False,
      "more_recent_user_confirmed_artifact": "NOT_EXCLUDED",
      "next":"Branch-qualified links are navigational evidence. Source owner must authorize exact latest portable, newer Library candidate and source QA before any main pointer repair."
    }

def execute(fetch=fetch_json):
    c,cat_blob=indexed_json(CATALOG)
    r,route_blob=indexed_json(ROUTES)
    x,_=indexed_json(CANDIDATES)
    return live_report(x,c,r,cat_blob,route_blob,fetch)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--summary",action="store_true")
    a=p.parse_args()
    try:
        target=a.report.resolve()
        require(target.suffix==".json" and target.parent.is_dir()
                and not target.exists() and not target.is_symlink()
                and ROOT.resolve() not in target.parents,
                "READBACK_REPORT_MUST_BE_NEW_AND_OUTSIDE_GIT_REPO")
        proof=execute()
        with target.open("x",encoding="utf-8") as f:
            json.dump(proof,f,ensure_ascii=False,indent=2,sort_keys=True)
            f.write("\n")
        view={k:v for k,v in proof.items() if k!="roots"} if a.summary else proof
        print(json.dumps(view,ensure_ascii=False,indent=2))
        return 0 if proof["status"]=="PASS_FIVE_LIVE_BRANCH_LOCATORS__ZERO_SOURCE_PROMOTION" else 3
    except (OSError,ValueError,subprocess.CalledProcessError,UnicodeError) as exc:
        print("GFP_OPT_BRANCH_RECOVERY_HOLD:"+str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
