#!/usr/bin/env python3
"""GFP-OPT P1: independently replay a native Stage5 receipt against source owner.

This creates a LOCAL, BYTE-VERIFIED ADOPTION *CANDIDATE* only. It cannot prove
that the pinned LATEST blob is currently main on GitHub, remote Library bytes
are still available, original-source semantics, formal Stage4, or app Stage6.
A full producer ADOPTED/PASS/CURRENT assertion requires independent remote
readback and an authorized source-specific workstream checkpoint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Tools"))
import build_governed_clean_delivery_v1 as governed

CATALOG = "Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
CATALOG_BLOB = "a73e06a3b6ac13425c523851b5d046a360683db3"
FAMILIES = "Optimization-Program/Control-Center/Profiles/P1-ALL-FAMILY-APPLICABILITY-v1.json"
FAMILIES_BLOB = "7e919f5b5a07e12c6f060a6aad59a16906b9fb41"
RECEIPT_SCHEMA = "gfp-opt-p1-governed-stage5-producer-invocation@1.0.0"

class AdoptionError(ValueError):
    pass

def guard(ok: bool, code: str) -> None:
    if not ok:
        raise AdoptionError(code)

def read_json_file(path: Path) -> dict:
    guard(path.is_file() and not path.is_symlink(), "EVIDENCE_MISSING_OR_SYMLINK")
    data=json.loads(path.read_text(encoding="utf-8-sig"))
    guard(isinstance(data,dict), "EVIDENCE_NOT_OBJECT")
    return data

def catalog_authority(root: Path=ROOT):
    cpath=root/CATALOG
    fpath=root/FAMILIES
    guard(cpath.is_file() and fpath.is_file()
          and not cpath.is_symlink() and not fpath.is_symlink(),
          "CATALOG_OR_PROFILE_NOT_LOCAL")
    guard(governed.matches_git_text(cpath.read_bytes(),CATALOG_BLOB),
          "CATALOG_BLOB_MISMATCH")
    guard(governed.matches_git_text(fpath.read_bytes(),FAMILIES_BLOB),
          "FAMILY_PROFILE_BLOB_MISMATCH")
    catalog=read_json_file(cpath)
    profiles=read_json_file(fpath)
    guard(catalog.get("schema")=="gcpk-master-project-catalog@1.0.0"
          and profiles.get("schema")=="gfp-opt-p1-source-domain-applicability-profiles@1.0.0",
          "CATALOG_PROFILE_SCHEMA_NOT_ACTIVE")
    guard(len(catalog.get("families",[]))==21
          and len(catalog.get("workspaces",[]))==36
          and len(profiles.get("families",[]))==21,
          "CATALOG_COVERAGE_DRIFT")
    return catalog,profiles

def resolve_owner(family_id: str, workspace_id: str, root: Path=ROOT):
    catalog, profiles=catalog_authority(root)
    family=next((x for x in catalog["families"] if x["id"]==family_id),None)
    workspace=next((x for x in catalog["workspaces"] if x["id"]==workspace_id),None)
    typed=next((x for x in profiles["families"] if x["id"]==family_id),None)
    guard(family is not None and workspace is not None and typed is not None,
          "UNKNOWN_SOURCE_OWNER")
    guard(workspace.get("parent_family_id")==family_id
          and typed["declared_domain"]=="LEXICAL_SOURCE_CANDIDATE",
          "WORKSPACE_WRONG_FAMILY_OR_NONLEXICAL_ADAPTER")
    guard(typed.get("native_builder_status")==
          "NOT_CONNECTED_FOR_THIS_FAMILY__GOVERNED_ENTRYPOINT_EXISTS_CENTRALLY",
          "EXISTING_ADOPTION_STATUS_CHANGED_REVIEW")
    git_dir=workspace["git_dir"]
    guard(git_dir.startswith("Workspaces/")
          and git_dir.count("/")==1
          and ".." not in git_dir and "\\" not in git_dir,
          "DANGEROUS_WORKSPACE_LOCATOR")
    return git_dir

def check_pointer(*, workspace_root: Path, workspace_dir: str, expected_blob: str,
                  actual_zip: Path, actual_sha: str):
    guard(re.fullmatch(r"[0-9a-f]{40}",expected_blob or "") is not None,
          "LATEST_GIT_BLOB_PIN_REQUIRED")
    locator=workspace_root / workspace_dir / "LATEST.json"
    guard(locator.is_file() and not locator.is_symlink(),
          "SOURCE_LATEST_MISSING_OR_SYMLINK")
    raw=locator.read_bytes()
    guard(governed.matches_git_text(raw,expected_blob),
          "LATEST_GIT_BLOB_CHANGED")
    pointer=json.loads(raw.decode("utf-8-sig"))
    guard(isinstance(pointer,dict)
          and pointer.get("schema")=="gcpk-workstream-latest@1.0.0",
          "UNSUPPORTED_WORKSTREAM_LATEST_SCHEMA")
    guard(pointer.get("workstream")==workspace_dir.split("/")[1],
          "LATEST_REFERENCES_DIFFERENT_WORKSTREAM")
    stage=pointer.get("status","")
    guard(isinstance(stage,str) and stage.startswith(("PASS_STAGE5_", "STAGE5_PASS_"))
          and "NOT_STAGE5" not in stage and "WIP" not in stage,
          "LATEST_NOT_STAGE5_ELIGIBLE")
    artifact=pointer.get("artifact")
    guard(isinstance(artifact,dict)
          and artifact.get("filename")==actual_zip.name
          and artifact.get("sha256")==actual_sha,
          "LATEST_ACTUAL_ZIP_DOES_NOT_MATCH")
    if "bytes" in artifact:
        guard(artifact["bytes"]==actual_zip.stat().st_size,
              "LATEST_ACTUAL_ZIP_SIZE_MISMATCH")
    return {
        "workspace_latest_relative_path":workspace_dir+"/LATEST.json",
        "workspace_latest_git_blob":expected_blob,
        "current_pointer_status_string":stage,
        "pointer_archive_sha256":artifact["sha256"],
        "pointer_archive_bytes":artifact.get("bytes"),
        "remote_main_pointer_readback":"NOT_DONE_IN_OFFLINE_VERIFIER",
        "user_newer_artifact_precedence":"MUST_BE_CHECKED_BEFORE_ADOPTION"
    }

def verify(*, family_id: str, workspace_id: str, latest_blob: str,
           workspace_root: Path, source: Path, archive: Path,
           native_receipt: Path, root: Path=ROOT)->dict:
    workspace_dir=resolve_owner(family_id,workspace_id,root)
    source=Path(source)
    archive=Path(archive)
    native_receipt=Path(native_receipt)
    guard(archive.is_file() and not archive.is_symlink(),
          "REAL_GOVERNED_ARCHIVE_MISSING")
    guard(native_receipt.is_file() and not native_receipt.is_symlink(),
          "NO_ACTUAL_GOVERNED_RECEIPT__LEGACY_ARCHIVE_NOT_ADOPTED")
    original_receipt_bytes=native_receipt.read_bytes()
    evidence=read_json_file(native_receipt)
    guard(evidence.get("schema")==RECEIPT_SCHEMA
          and evidence.get("status")==
          "PASS_GOVERNED_STAGE5_FORMAT_AND_BYTE_PARITY_ONLY"
          and evidence.get("program_id")=="GFP-OPT-2026"
          and evidence.get("purpose")=="stage5_acceptance",
          "NOT_GOVERNED_STAGE5_RECEIPT")
    for key,expected in {
        "linguistic_stage4":"NOT_CERTIFIED",
        "stage5_content_acceptance":"NOT_CERTIFIED",
        "stage6_browser":"NOT_RUN",
        "stage7_final":"NOT_RUN",
        "global_adoption":"NOT_PROVEN",
        "workstream_current_authority":"NOT_RESOLVED",
        "original_source_files_unchanged":True,
        "source_or_locked_or_card_edited":False,
        "app_runtime_ui_srs_fsrs_edited":False,
        "independent_zip_sha256sums_and_crc":"PASS"
    }.items():
        guard(evidence.get(key)==expected,
              "FORGED_NATIVE_RECEIPT_PASS_OR_MUTATION:"+key)
    _,builder_blob=governed.pinned_builder(root)
    guard(evidence.get("official_builder_git_blob")==builder_blob,
          "NATIVE_BUILDER_POLICY_BLOB_MISMATCH")
    roles=governed.select_roles(source)
    pins={key:governed.sha256(path.read_bytes()) for key,path in roles.items()}
    guard(evidence.get("source_role_sha256")==pins,
          "ACTUAL_SOURCE_ROLES_CHANGED_OR_FORGED")
    before=governed.check_path(roles["direct-import-tsv"],root)
    guard(evidence.get("active_policy")==before,
          "CURRENT_PINNED_POLICY_NOT_IN_RECEIPT")
    after,archive_sha=governed.verify_stage_zip(archive,pins,roles)
    guard(evidence.get("staged_policy")==after,
          "PACKAGED_POLICY_AND_RECEIPT_MISMATCH")
    guard(evidence.get("output_zip_sha256")==archive_sha
          and evidence.get("output_zip_name")==archive.name,
          "ACTUAL_GOVERNED_ZIP_NOT_IN_RECEIPT")
    guard(before==after,"PRE_POST_POLICY_REPLAY_CHANGED")
    pointer=check_pointer(
        workspace_root=Path(workspace_root),workspace_dir=workspace_dir,
        expected_blob=latest_blob,actual_zip=archive,actual_sha=archive_sha)
    for name,path in roles.items():
        guard(path.is_file() and not path.is_symlink()
              and governed.sha256(path.read_bytes())==pins[name],
              "INPUT_CHANGED_DURING_RECEIPT_REPLAY:"+name)
    guard(native_receipt.read_bytes()==original_receipt_bytes,
          "NATIVE_RECEIPT_CHANGED_DURING_REPLAY")
    guard(governed.sha256(archive.read_bytes())==archive_sha,
          "OUTPUT_ZIP_CHANGED_DURING_REPLAY")
    return {
        "schema":"gfp-opt-p1-source-owner-governed-adoption-candidate@1.0.0",
        "status":"PASS_SCOPED_LOCAL_CURRENT_POINTER_AND_GOVERNED_ZIP_PARITY__REMOTE_ADOPTION_OPEN",
        "program_id":"GFP-OPT-2026",
        "family_id":family_id,
        "workspace_id":workspace_id,
        "policy_binding":"stage5_neutral_validator",
        "registry_git_blob":before["registry_git_blob"],
        "validator_git_blob":before["validator_git_blob"],
        "native_builder_git_blob":builder_blob,
        "native_receipt_sha256":governed.sha256(original_receipt_bytes),
        "native_receipt_status":evidence["status"],
        "source_input_sha256":pins,
        "verified_cards":before["cards_validated"],
        "actual_zip_sha256":archive_sha,
        "actual_zip_name":archive.name,
        **pointer,
        "formal_real_producer_adoption":"NOT_GRANTED__INDEPENDENT_REMOTE_MAIN_AND_LIBRARY_READBACK_REQUIRED",
        "source_semantic_stage4":"NOT_CERTIFIED_BY_THIS_TOOL",
        "stage5_formal_approval":"NOT_CERTIFIED_BY_THIS_TOOL",
        "app_stage6_browser":"NOT_RUN",
        "stage7_final":"NOT_RUN",
        "automatic_other_source_propagation":False,
        "source_or_locked_or_card_mutation":False,
        "app_ui_importer_srs_fsrs_mutation":False,
        "github_ci_private_source_rehash":False
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--family-id",required=True)
    ap.add_argument("--workspace-id",required=True)
    ap.add_argument("--latest-git-blob",required=True)
    ap.add_argument("--workspace-root",type=Path,default=ROOT)
    ap.add_argument("--source-dir",type=Path,required=True)
    ap.add_argument("--archive",type=Path,required=True)
    ap.add_argument("--native-receipt",type=Path,required=True)
    ap.add_argument("--new-report",type=Path,required=True)
    args=ap.parse_args()
    try:
        guard(args.new_report.suffix.lower()==".json"
              and args.new_report.parent.is_dir()
              and not args.new_report.exists()
              and not args.new_report.is_symlink()
              and args.new_report.resolve() not in {
                  args.native_receipt.resolve(),args.archive.resolve()}
              and args.source_dir.resolve() not in args.new_report.resolve().parents
              and args.workspace_root.resolve() not in args.new_report.resolve().parents,
              "REPORT_PATH_MUST_BE_NEW_OUTSIDE_SOURCE_AND_WORKSPACE")
        result=verify(family_id=args.family_id,workspace_id=args.workspace_id,
                      latest_blob=args.latest_git_blob,
                      workspace_root=args.workspace_root,source=args.source_dir,
                      archive=args.archive,native_receipt=args.native_receipt)
        with args.new_report.open("x",encoding="utf-8") as out:
            json.dump(result,out,ensure_ascii=False,sort_keys=True,indent=2)
            out.write("\n")
        print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
        return 0
    except (OSError,ValueError,UnicodeError,zipfile.BadZipFile) as error:
        print("P1_SOURCE_ADOPTION_REPLAY_FAIL:"+str(error),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
