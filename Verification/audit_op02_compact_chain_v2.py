#!/usr/bin/env python3
"""OP02 read-only exact three-ZIP WIP74/WIP73/WIP72 provenance; NEVER final release."""
from __future__ import annotations
import csv, hashlib, io, json, re, stat
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, BadZipFile

CANON="02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json"
IMPORT="01-Final-Import/IMPORT.WORKING.tsv"
MANIFEST="MANIFEST.json"; SUMS="SHA256SUMS"
SOURCE="03-Source-Provenance/ORIGINAL-SOURCE-HASHES.json"
CHECK74="06-Checkpoint-State/WIP74-WORKING-CHECKPOINT.json"
CHECK73="06-Checkpoint-State/WIP73-WORKING-CHECKPOINT.json"
QA74="05-Reports/WIP74-SCOPED-QA.json"
QA73="05-Reports/WIP73-SCOPED-QA.json"
PARENT_PDFS=("03-Source-Provenance/User-Supplied-Original-PDFs/A1-A2-listen-tabellen.pdf",
             "03-Source-Provenance/User-Supplied-Original-PDFs/B1-C2-listen-tabellen.pdf")
REQUIRED_PINS={"wip74_sha","wip73_sha","wip72_sha","wip74_canonical_sha",
               "wip74_import_sha","wip73_canonical_sha","wip73_import_sha",
               "pdf_sha","changed_cards","rektion_cards","translation_cards",
               "translations","new_attested","attested","holds"}
HEX=re.compile(r"[0-9a-f]{64}\Z")
def digest(raw):return hashlib.sha256(raw).hexdigest()
def strict_json(raw):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError("DUPLICATE_JSON_KEY")
            d[k]=v
        return d
    def no_constant(x):raise ValueError("NONFINITE_JSON_NUMBER")
    return json.loads(raw.decode("utf-8"),object_pairs_hook=unique,parse_constant=no_constant)
def raw_zip(path,sha,label,errors):
    p=Path(path)
    if type(sha) is not str or not HEX.fullmatch(sha) or sha=="0"*64:
        errors.append(label+"_UNTRUSTED_SHA_FORMAT");return None
    if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=256_000_000:
        errors.append(label+"_INVALID_OR_MISSING_FILE");return None
    binary=p.read_bytes()
    if digest(binary)!=sha:
        errors.append(label+"_OUTER_SHA_DRIFT");return None
    try:
        with ZipFile(io.BytesIO(binary)) as z:
            infos=z.infolist()
            if (not infos or len(infos)>2000 or
                    sum(i.file_size for i in infos)>512_000_000):
                errors.append(label+"_UNSAFE_SIZE");return None
            names=[i.filename for i in infos]
            if len(names)!=len(set(names)):
                errors.append(label+"_DUPLICATE_MEMBER");return None
            for i in infos:
                bits=PurePosixPath(i.filename).parts
                if (not bits or i.filename.startswith(("/", "\\")) or
                    "\\" in i.filename or ".." in bits or ":" in bits[0] or
                    stat.S_ISLNK((i.external_attr>>16)&0xffff) or i.flag_bits&1):
                    errors.append(label+"_UNSAFE_PATH");return None
            return {n:z.read(n) for n in names}
    except (BadZipFile,OSError,ValueError,RuntimeError) as e:
        errors.append(label+"_ZIP_OR_CRC_FAILURE_"+type(e).__name__);return None
def checksum_manifest(files,label,errors):
    if not {SUMS,MANIFEST}.issubset(files):
        errors.append(label+"_MISSING_DIGEST_MANIFEST");return None
    man=strict_json(files[MANIFEST])
    sums={}
    for line in files[SUMS].decode("utf-8").splitlines():
        m=re.fullmatch(r"([0-9a-f]{64})  (.+)",line)
        if m is None or m[2] in sums:
            errors.append(label+"_SUMS_MALFORMED_OR_DUPLICATE")
        else:sums[m[2]]=m[1]
    if set(sums)!=set(files)-{SUMS} or any(sums.get(n)!=digest(v)
                                               for n,v in files.items() if n!=SUMS):
        errors.append(label+"_SUMS_BYTES_OR_COVERAGE")
    entries=man.get("files") if type(man) is dict else None
    if type(entries) is not list:
        errors.append(label+"_MANIFEST_NOT_LIST");return man
    listing={x.get("path"):x for x in entries if type(x) is dict and
             type(x.get("path")) is str}
    if len(listing)!=len(entries) or set(listing)!=set(files)-{MANIFEST,SUMS}:
        errors.append(label+"_MANIFEST_COVERAGE")
    else:
        for n,x in listing.items():
            if x.get("sha256")!=digest(files[n]) or x.get("size_bytes")!=len(files[n]):
                errors.append(label+"_MANIFEST_HASH_OR_LENGTH_DRIFT")
    if ("file_count_excluding_manifest_and_checksums" in man and
            man["file_count_excluding_manifest_and_checksums"]!=len(files)-2):
        errors.append(label+"_MANIFEST_MEMBER_COUNT")
    return man
def import_rows(raw,errors,label):
    rows=list(csv.reader(io.StringIO(raw.decode("utf-8-sig")),delimiter="\t"))
    if (not rows or rows[0][:2]!=["id","card_type"] or len(rows[0])!=23
        or any(len(r)!=23 for r in rows)):
        errors.append(label+"_TSV_SCHEMA_DRIFT");return []
    ids=[r[0] for r in rows[1:]]
    if not all(ids) or len(ids)!=len(set(ids)):
        errors.append(label+"_TSV_STABLE_IDS_DRIFT")
    return rows
def leaf_paths(a,b,path=""):
    if type(a)!=type(b):return [path]
    if isinstance(a,dict):
        out=[]
        for k in set(a)|set(b):
            if k not in a or k not in b:out.append(path+"."+k)
            else:out.extend(leaf_paths(a[k],b[k],path+"."+k))
        return out
    if isinstance(a,list):
        out=[path+".length"] if len(a)!=len(b) else []
        for i,(x,y) in enumerate(zip(a,b)):
            out.extend(leaf_paths(x,y,path+"["+str(i)+"]"))
        return out
    return [] if a==b else [path]

def audit(paths,pins):
    errors=[]
    result={"schema":"gcpk-op02-compact-triple-lineage@1",
            "status":"BLOCKED","errors":errors,
            "verified_archive_count":0,"verified_original_pdfs":0,
            "changed_import_rows":None,"changed_canonical_units":None,
            "rektion_only_units":None,"translation_only_units":None,
            "issuer_authenticated":False,"stage4_semantic_pass":False,
            "stage5_7_authorized":False,"writer_granted":False,
            "is_final_release":False,"performed_writes":False}
    if (type(paths) is not dict or set(paths)!={72,73,74} or type(pins) is not dict or
            set(pins)!=REQUIRED_PINS or
            any(type(pins.get(k)) is not int or pins[k]<0 for k in
                ("changed_cards","rektion_cards","translation_cards","translations",
                 "new_attested","attested","holds")) or
            type(pins.get("pdf_sha")) is not list or len(pins["pdf_sha"])!=2 or
            not all(type(x) is str and HEX.fullmatch(x) for x in pins["pdf_sha"])):
        errors.append("INDEPENDENT_EXPECTATION_INVALID");return result
    members={}
    for v in (72,73,74):
        current=raw_zip(paths[v],pins["wip"+str(v)+"_sha"],"WIP"+str(v),errors)
        if current is None:return result
        members[v]=current;result["verified_archive_count"]+=1
    try:
        z72,z73,z74=(members[v] for v in (72,73,74))
        m73=checksum_manifest(z73,"WIP73",errors)
        m74=checksum_manifest(z74,"WIP74",errors)
        if type(m73) is not dict or type(m74) is not dict:raise ValueError("MISSING_MANIFEST_OBJECT")
        cp73,cp74=(strict_json(members[v][p]) for v,p in ((73,CHECK73),(74,CHECK74)))
        q73,q74=(strict_json(members[v][p]) for v,p in ((73,QA73),(74,QA74)))
        s73,s74=(strict_json(members[v][SOURCE]) for v in (73,74))
        if m73.get("schema")!="gcpk-aber-hallo-wip73-compact-current-working@1" or m74.get("schema")!="gcpk-aber-hallo-wip74-compact@1":
            errors.append("SCHEMA_OR_VERSION_DRIFT")
        if len(z73)!=13 or len(z74)!=14:errors.append("COMPACT_MEMBER_COUNT_DRIFT")
        for obj,key,h,label in (
            (m74,"parent_sha256",pins["wip73_sha"],"WIP74_MANIFEST_PARENT"),
            (m74,"full_source_parent_sha256",pins["wip72_sha"],"WIP74_MANIFEST_FULL_PARENT"),
            (cp74,"parent_sha256",pins["wip73_sha"],"WIP74_CHECKPOINT_PARENT"),
            (cp74,"immutable_source_parent_sha256",pins["wip72_sha"],"WIP74_CHECKPOINT_FULL_PARENT"),
            (s74,"parent_wip73_sha256",pins["wip73_sha"],"WIP74_SOURCE_PARENT"),
            (s74,"full_parent_sha256",pins["wip72_sha"],"WIP74_SOURCE_FULL_PARENT"),
            (q74,"parent_wip73_sha256",pins["wip73_sha"],"WIP74_QA_PARENT"),
            (q74,"immutable_full_parent_wip72_sha256",pins["wip72_sha"],"WIP74_QA_FULL_PARENT"),
            (m73.get("parent_full_zip",{}),"sha256",pins["wip72_sha"],"WIP73_MANIFEST_PARENT"),
            (cp73,"parent_sha256",pins["wip72_sha"],"WIP73_CHECKPOINT_PARENT"),
            (s73,"parent_sha256",pins["wip72_sha"],"WIP73_SOURCE_PARENT"),
            (q73,"parent_sha256",pins["wip72_sha"],"WIP73_QA_PARENT")):
            if type(obj) is not dict or obj.get(key)!=h:errors.append(label+"_HASH_DRIFT")
        fname=Path(paths[72]).name
        if (m73.get("parent_full_zip",{}).get("name")!=fname or
            cp73.get("full_source_and_history_parent")!=fname or
            s73.get("parent_full_zip")!=fname or
            s74.get("immutable_parent_full_zip")!=fname):
            errors.append("FULL_SOURCE_PARENT_NAME_DRIFT")
        for v,z,cp,q in ((73,z73,cp73,q73),(74,z74,cp74,q74)):
            for path,key in ((CANON,"canonical_sha256"),(IMPORT,"import_sha256")):
                if path not in z:
                    errors.append("MISSING_ACTIVE_DATA:"+path);continue
                measured=digest(z[path])
                if measured!=pins["wip"+str(v)+"_"+key.replace("_sha256","_sha")]:
                    errors.append("INDEPENDENT_SHA_DRIFT:WIP"+str(v)+":"+key)
                if cp.get(key)!=measured or q.get(key)!=measured:
                    errors.append("CHECKPOINT_OR_QA_ACTIVE_SHA_DRIFT:WIP"+str(v)+":"+key)
        for i,path in enumerate(PARENT_PDFS):
            if path not in z72 or not z72[path].startswith(b"%PDF-") or digest(z72[path])!=pins["pdf_sha"][i]:
                errors.append("PARENT_PDF_BYTES_DRIFT:"+str(i))
            else:result["verified_original_pdfs"]+=1
        source_declaration=[{"id":n,"sha256":v} for n,v in zip(("A1-A2","B1-C2"),pins["pdf_sha"])]
        for obj,key in ((m73,"original_source_pdf_sha256"),
                         (cp73,"source_sha256"),(s73,"source_pdf_sha256"),
                         (q73,"source_sha256"),(s74,"source_pdf_sha256")):
            if obj.get(key)!=source_declaration:errors.append("SOURCE_DECLARATION_DRIFT:"+key)
        if (cp73.get("stage4")!="OPEN" or cp73.get("stage5_6_7")!="NOT_RUN" or
            not cp73.get("status","").startswith("CURRENT_WIP73_COMPACT_") or
            cp74.get("workstream")!="aber-hallo-listen-tabellen" or
            cp74.get("state")!="CURRENT_WIP74_COMPACT_STAGE4_OPEN" or
            cp74.get("stage4")!="OPEN" or cp74.get("stage5_to_7")!="NOT_RUN" or
            q74.get("scope_boundaries",{}).get("stage4_full_semantic_translation_source_adversarial")!="OPEN" or
            q74.get("scope_boundaries",{}).get("stage5_6_7")!="NOT_RUN"):
            errors.append("NONFINAL_STAGE_DECLARATION_DRIFT")
        a=import_rows(z73[IMPORT],errors,"WIP73")
        b=import_rows(z74[IMPORT],errors,"WIP74")
        if [x[0] for x in a]!=[x[0] for x in b]:
            errors.append("IMPORT_IDS_OR_ORDER_DRIFT")
        modified=[(x[0],[j for j,(u,v) in enumerate(zip(x,y)) if u!=v])
                  for x,y in zip(a[1:],b[1:]) if x!=y]
        result["changed_import_rows"]=len(modified)
        if len(modified)!=pins["changed_cards"] or any(v!=[19] for _,v in modified):
            errors.append("IMPORT_EDITED_ROWS_OR_FIELDS_DRIFT")
        ca=strict_json(z73[CANON]).get("learning_units")
        cb=strict_json(z74[CANON]).get("learning_units")
        if (type(ca) is not list or type(cb) is not list or len(ca)!=788 or
            len(cb)!=788 or [x.get("id") for x in ca]!=[x.get("id") for x in cb]):
            errors.append("CANONICAL_UNIVERSE_DRIFT")
        classes={"rektion":[],"translation":[],"other":[]}
        for prev,cur in zip(ca,cb):
            if prev!=cur:
                changed=leaf_paths(prev,cur)
                if changed and all(x.startswith(".metadata.rection_qa.patterns[") for x in changed):
                    classes["rektion"].append(prev["id"])
                elif set(changed)=={".details.kombinationen[0].text_fa",
                                   ".examples[0].translations[0].text"}:
                    classes["translation"].append(prev["id"])
                else:classes["other"].append(prev["id"])
        result["rektion_only_units"]=len(classes["rektion"])
        result["translation_only_units"]=len(classes["translation"])
        result["changed_canonical_units"]=sum(len(x) for x in classes.values())
        if (classes["other"] or len(classes["rektion"])!=pins["rektion_cards"] or
            len(classes["translation"])!=pins["translation_cards"] or
            result["changed_canonical_units"]!=pins["changed_cards"] or
            {x[0] for x in modified}!=set(classes["rektion"]+classes["translation"])):
            errors.append("CANONICAL_CHANGE_KIND_OR_ID_DRIFT")
        counts=m74.get("counts",{})
        qa_counts=q74.get("counts",{})
        for key,v in (("distinct_cards_changed",pins["changed_cards"]),
                      ("new_independent_exact_rektion",pins["new_attested"]),
                      ("rektion_attested_total",pins["attested"]),
                      ("rektion_remaining_exact_holds",pins["holds"]),
                      ("translation_correction_cards",pins["translation_cards"]),
                      ("learner_translation_corrections",pins["translations"]),
                      ("units",788),("lexical_cards",787),("examples_total",3152)):
            if counts.get(key)!=v or qa_counts.get(key)!=v:
                errors.append("MANIFEST_QA_COUNT_DRIFT:"+key)
        for path,key in (("04-QA-Review/04-LEARNER-TRANSLATION-REPAIRS.jsonl","translations"),
                         ("04-QA-Review/05-NEW-INDEPENDENT-CASE-SENSE-EVIDENCE.jsonl","new_attested"),
                         ("04-QA-Review/41-REMAINING-EXACT-HOLDS.jsonl","holds")):
            lines=z74[path].splitlines()
            if len(lines)!=pins[key]:errors.append("EVIDENCE_LINE_COUNT_DRIFT:"+key)
            for line in lines:strict_json(line)
        if (cp74.get("attested")!=pins["attested"] or cp74.get("held")!=pins["holds"] or
            pins["attested"]+pins["holds"]!=981 or
            cp73.get("new_attested")!=6 or cp73.get("remaining_holds")!=46 or
            pins["attested"]-pins["new_attested"]!=935 or
            pins["holds"]+pins["new_attested"]!=46):
            errors.append("CURRENT_PARENT_PROGRESS_DRIFT")
    except (KeyError,TypeError,ValueError,UnicodeError,AttributeError,OSError) as ex:
        errors.append("PARSE_OR_CONTRACT_"+type(ex).__name__)
    result["status"]="PASS_SCOPED_THREE_ZIP_RECOVERY_NOT_FINAL" if not errors else "BLOCKED"
    return result
