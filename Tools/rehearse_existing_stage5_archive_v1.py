#!/usr/bin/env python3
"""Nonpublishing P1 replay of the exact governed wrapper on existing source ZIPs.

An old archive is a source-byte donor, NOT authorization for a new Stage5
publication. All generated ZIPs and receipts live inside TemporaryDirectory.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,sys,tempfile,zipfile
from pathlib import Path

ROLES={"direct-import-tsv","canonical-json","source-output-map-tsv","qa-report"}
PREFIXES=("CONTENT-DELIVERY/","02-Content/CLEAN-DELIVERY/")
class RehearsalError(ValueError): pass
def require(ok,msg):
    if not ok: raise RehearsalError(msg)
def sha(b): return hashlib.sha256(b).hexdigest()

def read_roles(archive,expected,prefix):
    require(re.fullmatch(r"[a-f0-9]{64}",expected or "") is not None,"EXPECTED_SHA256_REQUIRED")
    require(prefix in PREFIXES,"DELIVERY_PREFIX_NOT_ALLOWED")
    require(archive.is_file() and not archive.is_symlink(),"ARCHIVE_NOT_REGULAR")
    require(0<archive.stat().st_size<=50_000_000,"ARCHIVE_BYTES_EXCESSIVE")
    before=archive.read_bytes()
    require(sha(before)==expected,"ARCHIVE_SHA256_DRIFT")
    with zipfile.ZipFile(io.BytesIO(before)) as z:
        infos=z.infolist()
        names=[x.filename for x in infos]
        require(len(names)==len(set(names)) and len(names)<=500,"ZIP_DUPLICATE_OR_EXCESSIVE_ENTRIES")
        require(all(n and not n.startswith(("/","\\")) and "\\" not in n
                    and "\x00" not in n and all(p not in (".","..") for p in n.split("/"))
                    for n in names),"UNSAFE_ZIP_MEMBER")
        require(sum(i.file_size for i in infos)<=130_000_000,"ZIP_UNCOMPRESSED_BYTES_EXCESSIVE")
        require(z.testzip() is None,"ZIP_CRC_FAIL")
        require(prefix+"DELIVERY-MANIFEST.json" in names and
                prefix+"SHA256SUMS.txt" in names,"CLEAN_DELIVERY_METADATA_MISSING")
        manifest=json.loads(z.read(prefix+"DELIVERY-MANIFEST.json"))
        roles=manifest.get("roles")
        require(isinstance(roles,dict) and set(roles)==ROLES,"FOUR_SOURCE_ROLES_REQUIRED")
        require(all(isinstance(n,str) and re.fullmatch(r"[A-Za-z0-9_.-]+",n) and
                    n not in (".","..") for n in roles.values()) and
                len(set(roles.values()))==4,"UNSAFE_OR_DUPLICATE_ROLE_NAME")
        sums={}
        for line in z.read(prefix+"SHA256SUMS.txt").decode("utf-8").splitlines():
            match=re.fullmatch(r"([a-f0-9]{64})  ([A-Za-z0-9_.-]+)",line)
            require(match is not None,"INVALID_SHA256SUMS")
            digest,name=match.groups()
            require(name not in sums,"DUPLICATE_SHA256SUMS")
            sums[name]=digest
        inputs={}
        for role,name in roles.items():
            require(prefix+name in names,"MISSING_ROLE:"+role)
            raw=z.read(prefix+name)
            require(sums.get(name)==sha(raw),"ROLE_SHA256_MISMATCH:"+role)
            inputs[name]=raw
    require(sha(archive.read_bytes())==expected,"SOURCE_ZIP_CHANGED_DURING_READ")
    reader=csv.DictReader(io.StringIO(inputs[roles["direct-import-tsv"]].decode("utf-8-sig"),newline=""),delimiter="\t",strict=True)
    rows=list(reader)
    require(rows and "details" in rows[0] and "card_type" in rows[0],"TSV_ROLE_NOT_ELIGIBLE")
    return roles,inputs,len(rows)

def bad_import(original,change):
    reader=csv.DictReader(io.StringIO(original.decode("utf-8-sig"),newline=""),delimiter="\t",strict=True)
    rows=list(reader)
    require(bool(rows),"EMPTY_NEGATIVE_FIXTURE")
    if change=="invalid-type": rows[0]["card_type"]="invalid-layout-card"
    elif change=="invalid-details": rows[0]["details"]="unstructured-prose"
    else: raise RehearsalError("BAD_NEGATIVE_MODE")
    out=io.StringIO(newline="")
    writer=csv.DictWriter(out,fieldnames=reader.fieldnames,delimiter="\t",lineterminator="\n")
    writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode("utf-8")

def rehearse(archive,expected,prefix,*,repo=None,execute=False):
    roles,inputs,nrows=read_roles(archive,expected,prefix)
    summary={
      "schema":"gfp-opt-p1-existing-source-disposable-governed-rehearsal@1.0.0",
      "status":"PASS_EXISTING_LIBRARY_SOURCE_BYTES_ONLY__WRAPPER_NOT_EXECUTED",
      "archive_sha256":expected,"real_input_rows":nrows,
      "roles_sha256":{role:sha(inputs[name]) for role,name in roles.items()},
      "adopted":False,"source_owner_new_stage5_authorized":False,
      "release_published":False,"current_or_final_certified":False
    }
    if not execute: return summary
    require(repo is not None and (repo/"Tools/build_governed_clean_delivery_v1.py").is_file(),
            "ACTUAL_REPO_WRAPPER_REQUIRED")
    require((repo/"Verification/check_active_stage5_policy_v1.py").is_file(),
            "ACTIVE_POLICY_GATE_REQUIRED")
    sys.path.insert(0,str(repo/"Tools"))
    import build_governed_clean_delivery_v1 as governed
    with tempfile.TemporaryDirectory(prefix="gfp-opt-nonpublishing-") as tmp:
        base=Path(tmp);source=base/"source";source.mkdir()
        for name,raw in inputs.items(): (source/name).write_bytes(raw)
        out=base/"REHEARSAL-NOT-RELEASE.zip"
        receipt=base/"REHEARSAL-NOT-ADOPTION.json"
        proof=governed.run(source,out,receipt,root=repo)
        require(proof.get("status")=="PASS_GOVERNED_STAGE5_FORMAT_AND_BYTE_PARITY_ONLY" and
                proof.get("global_adoption")=="NOT_PROVEN","GOVERNED_PROOF_WRONG_SCOPE")
        require(proof.get("source_role_sha256")==summary["roles_sha256"],
                "GOVERNED_SOURCE_ROLES_CHANGED")
        require(out.is_file() and receipt.is_file(),"TEMP_PRODUCER_RESULT_MISSING")
        temporary_digest=sha(out.read_bytes())
        negative_codes={}
        for mode in ("invalid-type","invalid-details"):
            bad=base/mode;bad.mkdir()
            for name,raw in inputs.items(): (bad/name).write_bytes(raw)
            tsv=bad/roles["direct-import-tsv"]
            tsv.write_bytes(bad_import(tsv.read_bytes(),mode))
            denied_zip=base/(mode+".zip")
            denied_receipt=base/(mode+".json")
            try:
                governed.run(bad,denied_zip,denied_receipt,root=repo)
            except (ValueError,OSError) as e:
                negative_codes[mode]=type(e).__name__
            else:
                raise RehearsalError("MUTATED_SOURCE_ACCEPTED:"+mode)
            require(not denied_zip.exists() and not denied_receipt.exists(),
                    "FAILED_SOURCE_PRODUCED_ARTIFACT:"+mode)
        require(all(sha((source/name).read_bytes())==sha(raw)
                    for name,raw in inputs.items()),"SOURCE_ROLE_CHANGED")
    require(sha(archive.read_bytes())==expected,"ORIGINAL_ARCHIVE_CHANGED")
    return {**summary,
      "status":"PASS_DISPOSABLE_GOVERNED_WRAPPER_REHEARSAL__NOT_ADOPTED",
      "wrapper_executed_on_existing_bytes":True,
      "temporary_archive_sha256_nonrelease":temporary_digest,
      "negative_mutations_rejected_without_zip":negative_codes,
      "all_generated_zips_and_receipts_removed":True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive",required=True,type=Path)
    p.add_argument("--sha256",required=True)
    p.add_argument("--prefix",required=True)
    p.add_argument("--run-governed",action="store_true")
    a=p.parse_args()
    try:
        result=rehearse(a.archive,a.sha256,a.prefix,
                        repo=Path(__file__).resolve().parents[1],
                        execute=a.run_governed)
    except (OSError,ValueError,UnicodeError,zipfile.BadZipFile,csv.Error) as e:
        print("P1_DISPOSABLE_REHEARSAL_DENIED:"+str(e),file=sys.stderr)
        return 2
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
