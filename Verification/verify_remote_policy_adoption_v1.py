#!/usr/bin/env python3
"""P1 independent GitHub-main + supplied Library-copy readback, fail-closed.

GitHub is queried LIVE at immutable HEAD commit and rechecked for ref movement.
Library content is supplied as separate bytes materialized by an authenticated
connector/operator; this script itself CANNOT authenticate the Library provider.
Even complete matching bytes never grant ADOPTED, CURRENT, Stage4/5/6/7 or FINAL.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import quote
from urllib.request import Request, urlopen
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Verification"))
import verify_governed_source_adoption_v1 as local

REPO="hosseinmehdizade-tech/German-Content-Production-Kit"
API="https://api.github.com/repos/"+REPO
BRANCH="main"
MAX_POINTER=2_000_000
MAX_LIBRARY_ZIP=250_000_000
HEX40=re.compile(r"^[a-f0-9]{40}$")
HEX64=re.compile(r"^[a-f0-9]{64}$")
LIBID=re.compile(r"^libfile_[a-zA-Z0-9]+$")
FILEID=re.compile(r"^file_[a-zA-Z0-9]+$")

class RemoteEvidenceError(ValueError):
    pass

def require(check: bool, name: str) -> None:
    if not check:
        raise RemoteEvidenceError(name)

def api_get(url: str) -> dict:
    require(url.startswith(API+"/") and "#" not in url, "API_URL_UNTRUSTED")
    token=os.environ.get("GITHUB_TOKEN")
    headers={
      "Accept":"application/vnd.github+json",
      "User-Agent":"GFP-OPT-readonly-source-adoption-v1",
      "X-GitHub-Api-Version":"2022-11-28"
    }
    if token:
        headers["Authorization"]="Bearer "+token
    req=Request(url,headers=headers)
    with urlopen(req,timeout=20) as response:
        require(response.status==200, "GITHUB_HTTP_NOT_200")
        data=response.read(MAX_POINTER*2)
    obj=json.loads(data.decode("utf-8"))
    require(isinstance(obj,dict),"GITHUB_NOT_OBJECT")
    return obj

def ref_head(fetch=api_get) -> str:
    result=fetch(API+"/git/ref/heads/"+BRANCH)
    ident=result.get("object",{})
    sha=ident.get("sha")
    require(ident.get("type")=="commit" and isinstance(sha,str)
            and HEX40.fullmatch(sha) is not None,"GITHUB_MAIN_HEAD_INVALID")
    return sha

def github_pointer(workspace_dir: str, fetch=api_get) -> tuple[bytes,str,str]:
    require(workspace_dir.startswith("Workspaces/") and
            workspace_dir.count("/")==1 and ".." not in workspace_dir
            and "\\" not in workspace_dir, "UNSAFE_GITHUB_WORKSPACE")
    head=ref_head(fetch)
    filename=workspace_dir+"/LATEST.json"
    endpoint=API+"/contents/"+quote(filename,safe="/")+"?ref="+head
    obj=fetch(endpoint)
    require(obj.get("type")=="file" and obj.get("path")==filename
            and obj.get("encoding")=="base64"
            and isinstance(obj.get("content"),str)
            and isinstance(obj.get("sha"),str)
            and HEX40.fullmatch(obj["sha"]) is not None,
            "GITHUB_CONTENTS_NOT_EXACT_MAIN_FILE")
    try:
        body=base64.b64decode("".join(obj["content"].split()),validate=True)
    except (ValueError,base64.binascii.Error) as error:
        raise RemoteEvidenceError("GITHUB_CONTENT_BASE64_CORRUPT") from error
    require(0<len(body)<=MAX_POINTER and obj.get("size")==len(body),
            "GITHUB_POINTER_SIZE_MISMATCH")
    require(local.governed.matches_git_text(body,obj["sha"]),
            "GITHUB_POINTER_BLOB_MISMATCH")
    return body,head,obj["sha"]

def checked_library_copy(path: Path, *, remote_pointer: dict, library_id: str,
                         file_id: str, library_path: str, expected_sha: str,
                         local_archive: Path) -> dict:
    require(LIBID.fullmatch(library_id or "") is not None
            and FILEID.fullmatch(file_id or "") is not None
            and isinstance(library_path,str)
            and library_path.startswith("/Flasch kart/")
            and ".." not in library_path.split("/"),
            "LIBRARY_REF_OR_PATH_INVALID")
    artifact=remote_pointer.get("artifact",{})
    require(artifact.get("library_file_id")==library_id
            and artifact.get("library_path")==library_path,
            "REMOTE_GITHUB_LIBRARY_ID_OR_PATH_MISMATCH")
    require(path.is_file() and not path.is_symlink()
            and local_archive.is_file() and not local_archive.is_symlink(),
            "LIBRARY_OR_SOURCE_COPY_NOT_REGULAR")
    require(path.resolve()!=local_archive.resolve(),
            "LIBRARY_COPY_NOT_INDEPENDENT_FILE")
    require(path.name==local_archive.name==artifact.get("filename"),
            "LIBRARY_FILENAME_OR_SOURCE_MISMATCH")
    size=path.stat().st_size
    require(0<size<=MAX_LIBRARY_ZIP
            and size==local_archive.stat().st_size
            and size==artifact.get("bytes"),
            "LIBRARY_BYTE_LENGTH_MISMATCH")
    data=path.read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    require(HEX64.fullmatch(expected_sha) is not None
            and digest==expected_sha==artifact.get("sha256"),
            "LIBRARY_CONTENT_DIGEST_MISMATCH")
    with zipfile.ZipFile(path) as zip_file:
        require(zip_file.testzip() is None,"LIBRARY_ARCHIVE_ZIP_CRC_FAIL")
    require(hashlib.sha256(local_archive.read_bytes()).hexdigest()==digest,
            "LIBRARY_BYTES_NOT_LOCAL_GOVERNED_ARCHIVE")
    return {
      "materialized_library_filename":path.name,
      "library_file_id_as_provided_by_operator":file_id,
      "library_record_id_as_provided_by_operator":library_id,
      "library_path_from_remote_git_and_operator":library_path,
      "library_materialized_copy_sha256":digest,
      "library_materialized_copy_bytes":size,
      "library_zip_crc":"PASS",
      "library_provider_authentication_by_this_script":"NOT_AVAILABLE__COPY_AND_IDS_OPERATOR_SUPPLIED",
      "independent_authenticated_library_fetch_required_for_adoption":True
    }

def verify(*, family_id: str, workspace_id: str, source_dir: Path,
           archive: Path, native_receipt: Path, library_copy: Path,
           library_file_id: str, library_record_id: str,
           library_path: str, root: Path=ROOT, fetch=api_get) -> dict:
    owner=local.resolve_owner(family_id,workspace_id,root)
    require(native_receipt.is_file() and not native_receipt.is_symlink(),
            "NO_NEW_GOVERNED_RECEIPT__LEGACY_ARCHIVE_NOT_ADOPTED")
    body,head,blob=github_pointer(owner,fetch)
    pointer=json.loads(body.decode("utf-8-sig"))
    require(isinstance(pointer,dict) and pointer.get("artifact",{}).get("sha256"),
            "GITHUB_LATEST_MISSING_ARTIFACT")
    with tempfile.TemporaryDirectory(prefix="gfp-opt-remote-readback-") as td:
        checkout=Path(td)
        target=checkout/owner/"LATEST.json"
        target.parent.mkdir(parents=True)
        target.write_bytes(body)
        local_proof=local.verify(family_id=family_id,workspace_id=workspace_id,
            latest_blob=blob,workspace_root=checkout,
            source=source_dir,archive=archive,native_receipt=native_receipt,root=root)
    library=checked_library_copy(Path(library_copy),remote_pointer=pointer,
        library_id=library_record_id,file_id=library_file_id,
        library_path=library_path,expected_sha=local_proof["actual_zip_sha256"],
        local_archive=Path(archive))
    require(ref_head(fetch)==head,"GITHUB_MAIN_MOVED_DURING_READBACK__RETRY")
    require(local_proof["workspace_latest_git_blob"]==blob,
            "REMOTE_LOCAL_LATEST_BLOB_MISMATCH")
    return {
      "schema":"gfp-opt-p1-independent-remote-source-adoption-readback@1.0.0",
      "program_id":"GFP-OPT-2026",
      "status":"PASS_LIVE_GITHUB_MAIN_AND_SEPARATE_LIBRARY_COPY_BYTE_PARITY__ADOPTION_HELD",
      "source_family_id":family_id,
      "source_workspace_id":workspace_id,
      "policy_binding_id":"stage5_neutral_validator",
      "github_main_commit_sha":head,
      "github_main_latest_git_blob":blob,
      "github_main_latest_path":owner+"/LATEST.json",
      "governed_native_source_receipt_sha256":local_proof["native_receipt_sha256"],
      "actual_governed_zip_sha256":local_proof["actual_zip_sha256"],
      "actual_governed_zip_bytes":library["library_materialized_copy_bytes"],
      "actual_native_cards":local_proof["verified_cards"],
      "library_copy_proof":library,
      "original_local_candidate_status":local_proof["status"],
      "remote_main_checked_twice_without_movement":True,
      "formal_source_level_policy_adoption":"HELD_PENDING_AUTHENTICATED_LIBRARY_PROVENANCE_SOURCE_OWNER_AND_STAGE_QA",
      "remote_github_currentness":"AT_TIME_OF_TWO_STABLE_MAIN_READS__NOT_FUTURE_GUARANTEE",
      "more_recent_explicit_user_artifact":"MUST_BE_CHECKED_SEPARATELY_BEFORE_CURRENT_CLAIM",
      "linguistic_stage4":"NOT_CERTIFIED_BY_THIS_TOOL",
      "stage5_formal_source_acceptance":"NOT_CERTIFIED_BY_THIS_TOOL",
      "stage6_browser":"NOT_RUN",
      "stage7_final":"NOT_RUN",
      "all_21_families_adopted":False,
      "app_runtime_ui_fsrs_srs_or_locked_mutated":False
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--family-id",required=True)
    p.add_argument("--workspace-id",required=True)
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--governed-zip",type=Path,required=True)
    p.add_argument("--native-receipt",type=Path,required=True)
    p.add_argument("--library-copy",type=Path,required=True)
    p.add_argument("--library-file-id",required=True)
    p.add_argument("--library-record-id",required=True)
    p.add_argument("--library-path",required=True)
    p.add_argument("--new-report",type=Path,required=True)
    args=p.parse_args()
    try:
        require(args.new_report.suffix==".json" and args.new_report.parent.is_dir()
                and not args.new_report.is_symlink()
                and not args.new_report.exists()
                and all(folder.resolve() not in args.new_report.resolve().parents
                        for folder in (args.source_dir,ROOT)),
                "REPORT_PATH_MUST_BE_NEW_OUTSIDE_SOURCE_AND_REPO")
        result=verify(family_id=args.family_id,workspace_id=args.workspace_id,
             source_dir=args.source_dir,archive=args.governed_zip,
             native_receipt=args.native_receipt,library_copy=args.library_copy,
             library_file_id=args.library_file_id,library_record_id=args.library_record_id,
             library_path=args.library_path)
        with args.new_report.open("x",encoding="utf-8") as file:
            json.dump(result,file,ensure_ascii=False,indent=2,sort_keys=True)
            file.write("\n")
    except (OSError,ValueError,UnicodeError,zipfile.BadZipFile) as error:
        print("GFP_OPT_REMOTE_READBACK_FAIL:"+str(error),file=sys.stderr)
        return 2
    print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
