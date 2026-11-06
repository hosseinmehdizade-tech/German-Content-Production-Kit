#!/usr/bin/env python3
"""GFP-OPT P1 governed entrypoint for the existing immutable Stage5 builder.

At the safe, explicitly chosen Stage5 publication boundary:
- Resolve the exact central policy/validator and original pinned builder.
- Check the producer's REAL TSV before making a ZIP.
- Invoke unchanged existing official clean builder.
- Re-read the packaged TSV via the SAME active policy and verify exact bytes.
- Persist a write-once, scoped evidence receipt separate from the clean ZIP.

This is opt-in for future eligible Stage5 jobs. It never runs source authoring,
semantic Stage4 review, app/browser imports or workstream CURRENT promotion.
"""
from __future__ import annotations
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Verification"))
from check_active_stage5_policy_v1 import (check_path,check_bytes,sha256,
                                           matches_git_text,Stage5PolicyFailure)
from check_mem009_native_stage5_v1 import audit_tsv_bytes as audit_mem009_native_tsv
BUILDER="Tools/build_clean_delivery.py"
REGISTRY="Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
PURPOSES=("stage5_acceptance",)  # This route must never issue a FINAL certificate.

class GovernedBuildError(ValueError):
    pass

def require(cond,code):
    if not cond: raise GovernedBuildError(code)

def pick(source:Path,patterns:list[str],role:str)->Path:
    hits=[]
    for p in source.iterdir():
        if any(fnmatch.fnmatch(p.name.lower(),pat.lower()) for pat in patterns):
            require(p.is_file() and not p.is_symlink(),
                    "STAGE5_UNSAFE_INPUT_ROLE:"+role)
            hits.append(p)
    require(len(hits)==1,"STAGE5_MISSING_OR_AMBIGUOUS_ROLE:"+role)
    return hits[0]

def select_roles(source:Path)->dict[str,Path]:
    require(source.is_dir() and not source.is_symlink(),"SOURCE_DIR_NOT_REGULAR")
    roles={
        "direct-import-tsv":pick(source,["*Universal*.tsv","*import*.tsv","*cards*.tsv"],"direct-import-tsv"),
        "canonical-json":pick(source,["*canonical*.json"],"canonical-json"),
        "source-output-map-tsv":pick(source,["*source-output-map*.tsv"],"source-output-map-tsv"),
        "qa-report":pick(source,["*verification*.json","*QA*.json","*qa*.json"],"qa-report")
    }
    require("source-inventory" not in roles["direct-import-tsv"].name.lower()
            and "source_inventory" not in roles["direct-import-tsv"].name.lower(),
            "SOURCE_INVENTORY_CANNOT_SATISFY_IMPORT")
    require(len({p.resolve() for p in roles.values()})==4,
            "REUSED_FILE_FOR_MULTIPLE_ROLES")
    return roles

def pinned_builder(root=ROOT):
    registry=json.loads((root/REGISTRY).read_text(encoding="utf-8"))
    b=registry.get("policy_bindings",{}).get("stage5_clean_builder",{})
    require(b.get("path")==BUILDER and
            b.get("scope")=="NEUTRAL_VOCABULARY_PROJECTION" and
            b.get("stages")==[5] and
            re.fullmatch(r"[a-f0-9]{40}",b.get("blob_sha","")) is not None,
            "GOVERNED_BUILDER_REGISTRY_BINDING_INVALID")
    path=root/BUILDER
    require(path.is_file() and not path.is_symlink(),
            "GOVERNED_BUILDER_NOT_REGULAR")
    require(matches_git_text(path.read_bytes(),b["blob_sha"]),
            "GOVERNED_BUILDER_GIT_BLOB_DRIFT")
    return path,b["blob_sha"]

def verify_stage_zip(path:Path,source_pins:dict[str,str],roles:dict[str,Path],
                     include_mem009:bool=False):
    require(path.is_file() and not path.is_symlink(),"NO_STAGE5_ZIP_AFTER_BUILD")
    bytes_before=path.read_bytes()
    with zipfile.ZipFile(path,"r") as z:
        infos=z.infolist()
        names=[x.filename for x in infos]
        require(len(names)==len(set(names)),"DUPLICATE_DELIVERY_ZIP_MEMBERS")
        require(z.testzip() is None,"DELIVERY_ZIP_CRC_MISMATCH")
        require(all(x.startswith("CONTENT-DELIVERY/") and
                    not x.endswith("/") and
                    ".." not in x.split("/") and "\\" not in x
                    for x in names), "DELIVERY_ZIP_LAYOUT_UNSAFE")
        required={f"CONTENT-DELIVERY/{p.name}" for p in roles.values()}
        required|={"CONTENT-DELIVERY/DELIVERY-MANIFEST.json",
                   "CONTENT-DELIVERY/SHA256SUMS.txt"}
        require(set(names)==required,"DELIVERY_ZIP_ROLE_INVENTORY_INVALID")
        manifest=json.loads(z.read("CONTENT-DELIVERY/DELIVERY-MANIFEST.json"))
        require(manifest.get("unified_vocabulary_validation")=="PASS_EMBEDDED_BUILDER_GATE",
                "DELIVERY_BUILDER_POLICY_STATUS_NOT_PASS")
        require(manifest.get("roles")=={k:v.name for k,v in roles.items()},
                "DELIVERY_ROLE_MANIFEST_CHANGED")
        raw=z.read("CONTENT-DELIVERY/SHA256SUMS.txt").decode("utf-8")
        pairs={}
        for line in raw.splitlines():
            match=re.fullmatch(r"([a-f0-9]{64})  ([^/\\]+)",line)
            require(match is not None,"BAD_DELIVERY_SHA256SUMS_RECORD")
            digest,name=match.groups()
            require(name not in pairs,"DUPLICATE_DELIVERY_SHA256_ENTRY")
            pairs[name]=digest
        expected_members={name.removeprefix("CONTENT-DELIVERY/")
                          for name in required if not name.endswith("SHA256SUMS.txt")}
        require(set(pairs)==expected_members,
                "DELIVERY_MANIFEST_HASH_COVERAGE_INVALID")
        for name,digest in pairs.items():
            require(sha256(z.read("CONTENT-DELIVERY/"+name))==digest,
                    "DELIVERY_MEMBER_HASH_MISMATCH:"+name)
        for role,p in roles.items():
            data=z.read(f"CONTENT-DELIVERY/{p.name}")
            require(sha256(data)==source_pins[role],
                    "STAGED_SOURCE_BYTES_CHANGED:"+role)
        import_data=z.read(f"CONTENT-DELIVERY/{roles['direct-import-tsv'].name}")
        governed_output=check_bytes(import_data)
        require(governed_output["input_tsv_sha256"]==
                source_pins["direct-import-tsv"],
                "GOVERNED_STAGED_IMPORT_SHA_MISMATCH")
        mem009_output=audit_mem009_native_tsv(import_data)
        require(mem009_output["status"]=="PASS_MEM009_NATIVE_STRUCTURE_ONLY",
                "MEM009_STAGED_STRUCTURAL_FAIL:"+str(mem009_output.get("errors",[])[:3]))
        require(mem009_output["input_tsv_sha256"]==
                source_pins["direct-import-tsv"],
                "MEM009_STAGED_IMPORT_SHA_MISMATCH")
    require(path.is_file() and not path.is_symlink() and
            path.read_bytes()==bytes_before,"OUTPUT_ZIP_CHANGED_ON_READBACK")
    # Keep the historical two-value API for existing source-owner and remote
    # verifier callers; only the updated governed run opts into three values.
    return ((governed_output,mem009_output,sha256(bytes_before)) if include_mem009
            else (governed_output,sha256(bytes_before)))

def run(source:Path,out:Path,receipt:Path,purpose:str="stage5_acceptance",
        milestone_evidence:Path|None=None,user_request:str|None=None,
        applied_edit_proof:Path|None=None,root:Path=ROOT):
    source=Path(source)
    out=Path(out)
    receipt=Path(receipt)
    require(purpose in PURPOSES,"INVALID_PURPOSE")
    require(not out.exists() and not out.is_symlink(),"OUTPUT_ALREADY_EXISTS")
    require(not receipt.exists() and not receipt.is_symlink(),"RECEIPT_ALREADY_EXISTS")
    require(receipt.suffix.lower()==".json" and receipt.parent.is_dir()
            and not receipt.parent.is_symlink(),"RECEIPT_LOCATION_INVALID")
    require(out.resolve()!=receipt.resolve() and
            source.resolve() not in receipt.resolve().parents and
            source.resolve() not in out.resolve().parents,
            "RECEIPT_OR_OUTPUT_INSIDE_SOURCE_DIR")
    builder,actual_builder_blob=pinned_builder(root)
    roles=select_roles(source)
    pins={k:sha256(v.read_bytes()) for k,v in roles.items()}
    before=check_path(roles["direct-import-tsv"],root)
    require(before["input_tsv_sha256"]==pins["direct-import-tsv"],
            "INPUT_NOT_THE_PINNED_SNAPSHOT")
    mem009_before=audit_mem009_native_tsv(roles["direct-import-tsv"].read_bytes())
    require(mem009_before["status"]=="PASS_MEM009_NATIVE_STRUCTURE_ONLY",
            "MEM009_SOURCE_STRUCTURAL_FAIL:"+str(mem009_before.get("errors",[])[:3]))
    require(mem009_before["input_tsv_sha256"]==pins["direct-import-tsv"],
            "MEM009_SOURCE_SHA_MISMATCH")
    args=[sys.executable,"-B",str(builder),str(source),str(out),
          "--purpose",purpose]
    if milestone_evidence is not None:
        args+=["--milestone-evidence",str(milestone_evidence)]
    if user_request is not None: args+=["--user-request",user_request]
    if applied_edit_proof is not None:
        args+=["--applied-edit-proof",str(applied_edit_proof)]
    completed=subprocess.run(args,cwd=root,capture_output=True,text=True,
                             encoding="utf-8",errors="replace")
    require(completed.returncode==0,
            "ORIGINAL_OFFICIAL_BUILDER_REFUSED_INPUT:"+completed.stderr[-1400:]+completed.stdout[-400:])
    for role,path in roles.items():
        require(path.is_file() and not path.is_symlink() and
                sha256(path.read_bytes())==pins[role],
                "SOURCE_CHANGED_AFTER_BUILDER:"+role)
    after,mem009_after,output_sha=verify_stage_zip(out,pins,roles,include_mem009=True)
    require(mem009_before["input_tsv_sha256"]==mem009_after["input_tsv_sha256"] and
            mem009_before["cards_seen"]==mem009_after["cards_seen"] and
            mem009_before["structured_sense_cards"]==mem009_after["structured_sense_cards"] and
            mem009_before["per_sense_example_missing_info_only"]==
            mem009_after["per_sense_example_missing_info_only"],
            "MEM009_SOURCE_STAGED_PARITY_MISMATCH")
    require(before["registry_git_blob"]==after["registry_git_blob"] and
            before["validator_git_blob"]==after["validator_git_blob"] and
            before["input_tsv_sha256"]==after["input_tsv_sha256"],
            "PRODUCER_POLICY_CHANGED_DURING_BUILD")
    pinned_builder(root)
    evidence={
      "schema":"gfp-opt-p1-governed-stage5-producer-invocation@1.0.0",
      "status":"PASS_GOVERNED_STAGE5_FORMAT_AND_BYTE_PARITY_ONLY",
      "program_id":"GFP-OPT-2026",
      "purpose":purpose,
      "active_policy":before,
      "official_builder_git_blob":actual_builder_blob,
      "source_role_sha256":pins,
      "output_zip_name":out.name,
      "output_zip_sha256":output_sha,
      "staged_policy":after,
      "mem009_structural_gate":{
          "status":mem009_before["status"],
          "source_import_tsv_sha256":mem009_before["input_tsv_sha256"],
          "packaged_import_tsv_sha256":mem009_after["input_tsv_sha256"],
          "cards_seen":mem009_before["cards_seen"],
          "structured_sense_cards":mem009_before["structured_sense_cards"],
          "untyped_sense_cards":mem009_before["untyped_sense_cards"],
          "per_sense_example_missing_info_only":
              mem009_before["per_sense_example_missing_info_only"],
          "no_mandatory_per_sense_example_quota":True,
          "full_meaning_retention_verified":False,
          "native_producer_scope":"THIS_GOVERNED_STAGE5_ROUTE_ONLY",
          "semantic_stage4_or_runtime6_certified":False
      },
      "independent_zip_sha256sums_and_crc":"PASS",
      "original_source_files_unchanged":True,
      "linguistic_stage4":"NOT_CERTIFIED",
      "stage5_content_acceptance":"NOT_CERTIFIED",
      "stage6_browser":"NOT_RUN",
      "stage7_final":"NOT_RUN",
      "global_adoption":"NOT_PROVEN",
      "workstream_current_authority":"NOT_RESOLVED",
      "source_or_locked_or_card_edited":False,
      "app_runtime_ui_srs_fsrs_edited":False
    }
    # Atomic exclusive-create: never replace a prior receipt or selected source.
    with receipt.open("x",encoding="utf-8") as handle:
        json.dump(evidence,handle,ensure_ascii=False,sort_keys=True,indent=2)
        handle.write("\n")
    require(sha256(out.read_bytes())==output_sha,"OUTPUT_ZIP_CHANGED_AFTER_RECEIPT")
    return evidence

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir",type=Path)
    parser.add_argument("output_zip",type=Path)
    parser.add_argument("--receipt",type=Path,required=True)
    parser.add_argument("--purpose",choices=PURPOSES,default="stage5_acceptance")
    parser.add_argument("--milestone-evidence",type=Path)
    parser.add_argument("--user-request")
    parser.add_argument("--applied-edit-proof",type=Path)
    args=parser.parse_args()
    try:
        r=run(args.source_dir,args.output_zip,args.receipt,args.purpose,
              args.milestone_evidence,args.user_request,args.applied_edit_proof)
    except (OSError,ValueError,UnicodeError,zipfile.BadZipFile) as e:
        print("GFP_OPT_GOVERNED_STAGE5_FAIL:"+str(e),file=sys.stderr)
        print("If a ZIP exists without a verified receipt, treat it as unaccepted; "
              "never promote it as CURRENT/FINAL.",file=sys.stderr)
        return 2
    print(json.dumps({"status":r["status"],"zip_sha256":r["output_zip_sha256"],
                      "receipt":str(args.receipt),"policy_binding":r["active_policy"]["policy_binding"]},
                     ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
