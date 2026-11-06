#!/usr/bin/env python3
"""P1 producer-neutral real Stage5 input gate: active registry -> exact validator.

Only checks deterministic projection structure and policy binding. No semantic
Stage4, currentness, browser import or release authority is inferred.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import re
import subprocess
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
REGISTRY="Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
BINDING="stage5_neutral_validator"
VALIDATOR="Verification/validate_unified_vocabulary_projection_v1_1_0.py"
MAX_TSV=35_000_000

class Stage5PolicyFailure(ValueError):
    pass

def require(cond, code):
    if not cond: raise Stage5PolicyFailure(code)

def sha256(blob):
    return hashlib.sha256(blob).hexdigest()

def git_blob(blob):
    return hashlib.sha1(b"blob "+str(len(blob)).encode("ascii")+b"\0"+blob).hexdigest()

def matches_git_text(blob, digest):
    """Allow the only checkout normalization Git applies: CRLF <-> LF."""
    return git_blob(blob)==digest or (
        b"\r\n" in blob and git_blob(blob.replace(b"\r\n",b"\n"))==digest)

def active_registry_blob_from_checkout():
    """Resolve the **actual checked-out Git commit**'s approved registry bytes.

    This avoids invalidating every native Stage5 run whenever a new central
    policy is merged; fail-closed on non-Git/uncommitted tampering. The central
    registry audit still validates every binding, path, safety invariant and
    stage scope independently. Never infer source CURRENT or Stage4/6 here.
    """
    proc=subprocess.run(["git","rev-parse","--verify","HEAD:"+REGISTRY],
                        cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
    require(proc.returncode==0, "ACTIVE_GIT_REGISTRY_UNAVAILABLE")
    sha=proc.stdout.strip()
    require(re.fullmatch(r"[0-9a-f]{40}",sha) is not None,
            "ACTIVE_GIT_REGISTRY_BLOB_INVALID")
    return sha


def load_authority(root=ROOT):
    file=root/REGISTRY
    require(file.is_file() and not file.is_symlink(), "MISSING_REGISTRY_FILE")
    blob=file.read_bytes()
    require(matches_git_text(blob,active_registry_blob_from_checkout()),
            "REGISTRY_GIT_BLOB_MISMATCH")
    reg=json.loads(blob.decode("utf-8-sig"))
    require(reg.get("schema")=="gcpk-global-policy-registry@1.0.0" and
            reg.get("status")=="ACTIVE_PROSPECTIVE_POLICY_ROUTER_NOT_BULK_CONTENT_MIGRATION",
            "REGISTRY_NOT_ACTIVE")
    binding=reg.get("policy_bindings",{}).get(BINDING,{})
    require(binding.get("path")==VALIDATOR and
            binding.get("scope")=="NEUTRAL_VOCABULARY_PROJECTION" and
            binding.get("stages")==[5], "BINDING_SCOPE_OR_PATH_CHANGED")
    file=root/VALIDATOR
    require(file.is_file() and not file.is_symlink(),"VALIDATOR_MISSING_OR_SYMLINK")
    require(matches_git_text(file.read_bytes(),binding.get("blob_sha","")),
            "VALIDATOR_GIT_BLOB_MISMATCH")
    spec=importlib.util.spec_from_file_location("gfp_active_neutral_policy_v1",file)
    require(spec is not None and spec.loader is not None,"VALIDATOR_IMPORT_UNAVAILABLE")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(callable(getattr(module,"validate",None)),"VALIDATOR_API_NOT_AVAILABLE")
    return module,binding

def check_bytes(data:bytes, root=ROOT):
    require(isinstance(data,bytes) and 0<len(data)<=MAX_TSV,"EMPTY_OR_OVERSIZE_TSV")
    module,binding=load_authority(root)
    try:
        decoded=data.decode("utf-8-sig")
        reader=csv.DictReader(io.StringIO(decoded,newline=""),delimiter="\t",strict=True)
        header=reader.fieldnames or []
        require(len(header)==len(set(header)) and
                {"id","front","back","card_type","category","custom_fields"}<=set(header),
                "INVALID_TSV_COLUMNS")
        rows=list(reader)
    except (UnicodeDecodeError,csv.Error) as exc:
        raise Stage5PolicyFailure("TSV_DECODE_OR_STRUCTURE_FAIL") from exc
    require(bool(rows) and len(rows)<=200_000,"EMPTY_OR_EXCESSIVE_ROWS")
    require(all(None not in row and row.get("id") and row["id"].strip() for row in rows),
            "MALFORMED_ROWS_OR_ID")
    ids=[r["id"] for r in rows]
    require(len(set(ids))==len(ids),"DUPLICATE_CARD_ID")
    result=module.validate(rows)
    require(result.get("status")=="PASS",
            "ACTIVE_NEUTRAL_STAGE5_POLICY_FAILED: "+
            ",".join(e.get("error","UNKNOWN") for e in result.get("errors",[])[:6]))
    return {
      "schema":"gfp-opt-p1-stage5-active-policy-input-gate@1.0.0",
      "status":"PASS_EXACT_ACTIVE_STAGE5_NEUTRAL_FORMAT_ONLY",
      "registry_git_blob":active_registry_blob_from_checkout(),
      "policy_binding":BINDING,
      "validator_git_blob":binding["blob_sha"],
      "input_tsv_sha256":sha256(data),
      "cards_validated":len(rows),
      "details_evidence":"VALIDATED_IF_PRESENT",
      "linguistic_stage4":"NOT_CHECKED",
      "stage5_release":"NOT_CERTIFIED",
      "stage6_browser":"NOT_RUN",
      "stage7_final":"NOT_RUN",
      "all_producers_adopted":False,
      "active_workstream_currentness":"NOT_DETERMINED"
    }

def check_path(path:Path, root=ROOT):
    require(path.is_file() and not path.is_symlink(),"INPUT_NOT_REGULAR_FILE")
    before=path.read_bytes()
    result=check_bytes(before,root)
    require(path.is_file() and not path.is_symlink() and path.read_bytes()==before,
            "INPUT_CHANGED_DURING_POLICY_CHECK")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("tsv",type=Path)
    args=p.parse_args()
    try:
        outcome=check_path(args.tsv)
    except (OSError,ValueError,UnicodeError) as exc:
        print("P1_ACTIVE_POLICY_FAIL: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps(outcome,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
