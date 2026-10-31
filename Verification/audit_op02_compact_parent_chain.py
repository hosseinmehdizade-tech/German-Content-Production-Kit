#!/usr/bin/env python3
"""Read-only OP02 compact CURRENT versus immutable full-parent byte lineage.

A scoped PASS is never a publisher signature, Stage4 acceptance or final release.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
from zipfile import ZipFile, BadZipFile

MAX_ZIP=256_000_000
MAX_MEMBERS=2000
CANON="02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json"
IMPORT="01-Final-Import/IMPORT.WORKING.tsv"
CHECKPOINT="06-Checkpoint-State/WIP73-WORKING-CHECKPOINT.json"
SOURCE="03-Source-Provenance/ORIGINAL-SOURCE-HASHES.json"
QA="05-Reports/WIP73-SCOPED-QA.json"
MANIFEST="MANIFEST.json"
SUMS="SHA256SUMS"
PARENT_PDFS=(
    "03-Source-Provenance/User-Supplied-Original-PDFs/A1-A2-listen-tabellen.pdf",
    "03-Source-Provenance/User-Supplied-Original-PDFs/B1-C2-listen-tabellen.pdf",
)
SHA=re.compile(r"[0-9a-f]{64}\Z")
REQUIRED=frozenset((CANON,IMPORT,CHECKPOINT,SOURCE,QA,MANIFEST,SUMS))
EXPECTED_KEYS=frozenset(("compact_sha256","parent_sha256","canonical_sha256",
    "import_sha256","parent_name","source_sha256","member_count",
    "changed_cards","parent_holds","new_attested","current_attested","remaining_holds"))

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def sha_ok(value):
    return type(value) is str and bool(SHA.fullmatch(value)) and value != "0"*64

def parse_json(raw):
    def unique(pairs):
        d={}
        for key,val in pairs:
            if key in d:
                raise ValueError("JSON_DUPLICATE_FIELD")
            d[key]=val
        return d
    def finite(v):
        raise ValueError("JSON_NONFINITE_VALUE")
    return json.loads(raw.decode("utf-8"),object_pairs_hook=unique,parse_constant=finite)

def read_zip(path, expected_sha, *, label, errors):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=MAX_ZIP:
        errors.append(label+"_FILE_MISSING_SYMLINK_OR_TOO_BIG")
        return None
    raw=p.read_bytes()
    if digest(raw)!=expected_sha:
        errors.append(label+"_OUTER_SHA_MISMATCH")
        return None
    try:
        with ZipFile(io.BytesIO(raw)) as z:
            infos=z.infolist()
            names=[info.filename for info in infos]
            if not infos or len(infos)>MAX_MEMBERS or len(names)!=len(set(names)):
                errors.append(label+"_DUPLICATE_OR_TOO_MANY_MEMBERS")
                return None
            if sum(i.file_size for i in infos)>512_000_000:
                errors.append(label+"_EXPANDED_SIZE_LIMIT")
                return None
            for info in infos:
                name=info.filename
                if (not name or name.startswith(("/","\\")) or "\\" in name
                        or any(part in (".","..") for part in PurePosixPath(name).parts)
                        or ":" in PurePosixPath(name).parts[0]
                        or stat.S_ISLNK((info.external_attr>>16)&0xffff)
                        or info.flag_bits&1):
                    errors.append(label+"_UNSAFE_MEMBER")
                    return None
            return {name:z.read(name) for name in names}  # all CRCs checked
    except (BadZipFile, OSError, ValueError, RuntimeError) as exc:
        errors.append(label+"_ZIP_UNREADABLE_"+type(exc).__name__)
        return None

def rows(raw):
    data=list(csv.reader(io.StringIO(raw.decode("utf-8-sig")),delimiter="\t"))
    if (not data or data[0][:2]!=["id","card_type"]
            or len(data[0])!=23 or
            any(len(x)!=len(data[0]) or not x[0] for x in data[1:])
            or len(set(x[0] for x in data[1:]))!=len(data)-1):
        raise ValueError("INVALID_IMPORT_UNIVERSE")
    return data

def audit(compact_path,parent_path,expected):
    errors=[]
    out={"schema":"gcpk-op02-compact-parent-chain@1",
         "status":"BLOCKED","errors":errors,
         "compact_bytes_verified":False,"parent_bytes_verified":False,
         "manifest_checksum_valid":False,"parent_original_pdfs_verified":0,
         "changed_import_rows":None,"changed_canonical_units":None,
         "parent_required":True,"compact_is_final_release":False,
         "issuer_authenticated":False,"protected_git_authority":False,
         "stage4_semantic_pass":False,"stage5_7_authorized":False,
         "writer_granted":False,"performed_writes":False}
    if (type(expected) is not dict or set(expected)!=EXPECTED_KEYS
            or any(not sha_ok(expected.get(k)) for k in
                   ("compact_sha256","parent_sha256","canonical_sha256","import_sha256"))
            or type(expected.get("source_sha256")) is not list
            or len(expected["source_sha256"])!=2
            or not all(sha_ok(x) for x in expected["source_sha256"])
            or type(expected.get("parent_name")) is not str
            or not expected["parent_name"].endswith(".zip")
            or any(type(expected.get(k)) is not int or expected[k]<0 for k in
                   ("member_count","changed_cards","parent_holds","new_attested",
                    "current_attested","remaining_holds"))):
        errors.append("INDEPENDENT_SNAPSHOT_INVALID")
        return out
    compact=read_zip(compact_path,expected["compact_sha256"],label="COMPACT",errors=errors)
    parent=read_zip(parent_path,expected["parent_sha256"],label="PARENT",errors=errors)
    if compact is None or parent is None:
        return out
    out["compact_bytes_verified"]=True
    out["parent_bytes_verified"]=True
    if Path(parent_path).name!=expected["parent_name"]:
        errors.append("PARENT_NAME_DRIFT")
    if len(compact)!=expected["member_count"] or not REQUIRED.issubset(compact):
        errors.append("COMPACT_MEMBER_SET_DRIFT")
        return out
    if CANON not in parent or IMPORT not in parent or not all(n in parent for n in PARENT_PDFS):
        errors.append("FULL_PARENT_SOURCE_OR_DATA_MISSING")
        return out
    try:
        man=parse_json(compact[MANIFEST])
        cp=parse_json(compact[CHECKPOINT])
        src=parse_json(compact[SOURCE])
        qa=parse_json(compact[QA])
        # Full archive checksums: a rehashed stale metadata member still fails semantic tests.
        checks={}
        for line in compact[SUMS].decode("utf-8").splitlines():
            m=re.fullmatch(r"([0-9a-f]{64})  (.+)",line)
            if not m or m[2] in checks:
                errors.append("COMPACT_SHA256SUMS_MALFORMED_OR_DUPLICATE")
                continue
            checks[m[2]]=m[1]
        if set(checks)!=set(compact)-{SUMS} or any(
                digest(compact[n])!=h for n,h in checks.items() if n in compact):
            errors.append("COMPACT_SHA256SUMS_COVERAGE_OR_BYTES")
        files=man.get("files") if type(man) is dict else None
        listed={} if type(files) is not list else {
            x.get("path"):x for x in files if type(x) is dict and type(x.get("path")) is str}
        if (type(files) is not list or len(listed)!=len(files)
                or set(listed)!=set(compact)-{MANIFEST,SUMS}
                or man.get("file_count_excluding_manifest_and_checksums")!=len(compact)-2):
            errors.append("COMPACT_MANIFEST_FILE_SET_DRIFT")
        else:
            for name,entry in listed.items():
                if (entry.get("sha256")!=digest(compact[name])
                        or entry.get("size_bytes")!=len(compact[name])):
                    errors.append("COMPACT_MANIFEST_MEMBER_HASH_DRIFT")
        out["manifest_checksum_valid"]=not errors
        if (type(man) is not dict or
                man.get("schema")!="gcpk-aber-hallo-wip73-compact-current-working@1"
                or man.get("workstream")!="aber-hallo-listen-tabellen"
                or type(cp) is not dict or cp.get("schema")!="gcpk-wip73-compact-working@1"):
            errors.append("COMPACT_CONTRACT_OR_WORKSTREAM_DRIFT")
        if (type(cp) is dict and
                (not str(cp.get("status","")).startswith("CURRENT_WIP73_COMPACT_")
                 or cp.get("stage4")!="OPEN" or cp.get("stage5_6_7")!="NOT_RUN")):
            errors.append("COMPACT_ACTIVE_SCOPE_OR_STAGE_CLAIM_DRIFT")
        for name in (CANON,IMPORT):
            tag="canonical_sha256" if name==CANON else "import_sha256"
            if digest(compact[name])!=expected[tag]:
                errors.append("EXTERNALLY_PINNED_"+tag+"_DRIFT")
            if type(cp) is not dict or cp.get(tag)!=digest(compact[name]):
                errors.append("COMPACT_CHECKPOINT_"+tag+"_DRIFT")
            if type(qa) is not dict or qa.get(tag)!=digest(compact[name]):
                errors.append("COMPACT_QA_"+tag+"_DRIFT")
        for label,obj,field in (
            ("MANIFEST",man.get("parent_full_zip") if type(man) is dict else None,"sha256"),
            ("CHECKPOINT",cp,"parent_sha256"),("SOURCE",src,"parent_sha256"),
            ("QA",qa,"parent_sha256")):
            if type(obj) is not dict or obj.get(field)!=expected["parent_sha256"]:
                errors.append(label+"_PARENT_HASH_DRIFT")
        if (type(man.get("parent_full_zip")) is not dict
                or man["parent_full_zip"].get("name")!=expected["parent_name"]
                or cp.get("full_source_and_history_parent")!=expected["parent_name"]
                or src.get("parent_full_zip")!=expected["parent_name"]):
            errors.append("PARENT_FILENAME_CLAIMS_DRIFT")
        for i,n in enumerate(PARENT_PDFS):
            if (not parent[n].startswith(b"%PDF-")
                    or digest(parent[n])!=expected["source_sha256"][i]):
                errors.append("PARENT_SOURCE_PDF_ORIGINAL_BYTES_MISMATCH")
            else:
                out["parent_original_pdfs_verified"]+=1
        source_entries=[{"id":key,"sha256":value} for key,value in
                        zip(("A1-A2","B1-C2"),expected["source_sha256"])]
        for obj,key in ((man,"original_source_pdf_sha256"),
                        (cp,"source_sha256"),(src,"source_pdf_sha256"),
                        (qa,"source_sha256")):
            if type(obj) is not dict or obj.get(key)!=source_entries:
                errors.append("SOURCE_HASH_DECLARATION_DRIFT:"+key)
        parent_rows=rows(parent[IMPORT])
        compact_rows=rows(compact[IMPORT])
        if ([x[0] for x in parent_rows]!=[x[0] for x in compact_rows]):
            errors.append("IMPORT_STABLE_IDS_OR_ORDER_CHANGED")
        diff=sum(a!=b for a,b in zip(parent_rows[1:],compact_rows[1:]))
        out["changed_import_rows"]=diff
        if len(parent_rows)!=len(compact_rows) or diff!=expected["changed_cards"]:
            errors.append("IMPORT_CHANGED_ROW_COUNT_DRIFT")
        a=parse_json(parent[CANON]);b=parse_json(compact[CANON])
        au=a.get("learning_units") if type(a) is dict else None
        bu=b.get("learning_units") if type(b) is dict else None
        if type(au) is not list or type(bu) is not list:
            errors.append("CANONICAL_LEARNING_UNITS_INVALID")
        else:
            out["changed_canonical_units"]=sum(x!=y for x,y in zip(au,bu))
            if (len(au)!=len(bu) or len(au)!=788
                    or [x.get("id") for x in au]!=[y.get("id") for y in bu]
                    or out["changed_canonical_units"]!=expected["changed_cards"]):
                errors.append("CANONICAL_UNITS_OR_ID_LINEAGE_DRIFT")
        summary=man.get("summary") if type(man) is dict else None
        counts=qa.get("counts") if type(qa) is dict else None
        for field,expect in (
            ("changed_distinct_cards",expected["changed_cards"]),
            ("new_exact_attestations",expected["new_attested"]),
            ("wip72_hold_queue_input",expected["parent_holds"]),
            ("carried_holds",expected["remaining_holds"]),
            ("cumulative_attested",expected["current_attested"])):
            if (type(summary) is not dict or summary.get(field)!=expect
                    or type(counts) is not dict or counts.get(field)!=expect):
                errors.append("COMPACT_QA_COUNT_DRIFT:"+field)
        if (type(summary) is not dict or
                summary.get("portable_kind")!="COMPACT_CURRENT_WORKING_SNAPSHOT_WITH_EXACT_PARENT"
                or summary.get("stage4")!="OPEN" or summary.get("stage5_6_7")!="NOT_RUN"):
            errors.append("COMPACT_NOT_EXPLICITLY_NONFINAL")
        if (cp.get("new_attested")!=expected["new_attested"]
                or cp.get("remaining_holds")!=expected["remaining_holds"]
                or expected["parent_holds"]-expected["new_attested"]!=expected["remaining_holds"]):
            errors.append("COMPACT_CHECKPOINT_PROGRESS_DRIFT")
    except (ValueError,KeyError,TypeError,UnicodeError,AttributeError) as exc:
        errors.append("COMPACT_PARSE_OR_SCHEMA_"+type(exc).__name__)
    out["status"]="PASS_SCOPED_COMPACT_PARENT_RECOVERY_NOT_FINAL" if not errors else "BLOCKED"
    return out
