#!/usr/bin/env python3
"""OP-02 NONACTIVE current Stage4 worksheet freshness diagnostic (read-only).

Compares every frozen reviewer cell against exact Canonical unit values.
This NEVER approves linguistic Stage4: a perfectly fresh sheet is still only
a review input, and an unsigned/external review cannot be auto-certified.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

SCHEMA="gcpk-op02-stage4-current-worksheet-freshness@1"
REVIEW_FIELDS=("expert_decision","expert_reviewer_identity","expert_review_date",
               "expert_evidence","expert_comments")
FROZEN=("headword","type","definition_de","meaning_fa","gloss_en",
        "core_json","rection_json","source_book_locators_json","senses_json",
        "examples_de_json","examples_fa_json","examples_en_json",
        "kombinationen_json","relations_json")

def sha256(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def translation(example:dict,lang:str)->str:
    return next((t["text"] for t in example.get("translations",[])
                 if t.get("lang")==lang),"")

def projected(unit:dict)->dict:
    detail=unit.get("details") or {}
    ex=unit.get("examples") or []
    return {
      "headword":unit.get("headword",""),"type":unit.get("type",""),
      "definition_de":unit.get("definition_de",""),
      "meaning_fa":unit.get("persian_meaning",""),
      "gloss_en":unit.get("english_gloss",""),
      "core_json":unit.get("core",{}),
      "rection_json":detail.get("rection",[]),
      "source_book_locators_json":[s.get("locator","") for s in
           (unit.get("provenance") or {}).get("sources",[])
           if s.get("source_kind")=="book"],
      "senses_json":unit.get("senses",[]),
      "examples_de_json":[e.get("text","") for e in ex],
      "examples_fa_json":[translation(e,"fa-IR") for e in ex],
      "examples_en_json":[translation(e,"en-US") for e in ex],
      "kombinationen_json":detail.get("kombinationen",[]),
      "relations_json":detail.get("lexical_relations",[]),
    }

def result(status,errors,canonical,worksheet,drifts,ids,decisions,expected_units):
    return {
      "schema":SCHEMA,"status":status,"errors":sorted(set(errors)),
      "expected_units":expected_units,"worksheet_rows":decisions["rows"],
      "decisions_entered":decisions["entered"],"decisions_blank":decisions["blank"],
      "affected_units":len(ids),"drifts_by_field":dict(sorted(drifts.items())),
      "affected_id_sample":sorted(ids)[:12],
      "canonical_sha256":sha256(canonical),"worksheet_sha256":sha256(worksheet),
      "stage4_semantic_pass":False,"production_authorized":False,
      "original_content_modified":False,
      "boundary":"Only byte-pinned row freshness against current Canonical. Not independent reviewer identity, language accuracy, source proof, signature or Stage4 signoff."
    }

def audit(canonical_bytes:bytes,worksheet_bytes:bytes, *,
          expected_units:int=788, expected_canonical_sha256:str|None=None,
          expected_worksheet_sha256:str|None=None)->dict:
    errors=[]; drift=collections.Counter();ids=set()
    decisions={"rows":0,"entered":0,"blank":0}
    if (expected_canonical_sha256 is not None and
        sha256(canonical_bytes)!=expected_canonical_sha256):
        errors.append("CANONICAL_EXTERNAL_PIN_MISMATCH")
    if (expected_worksheet_sha256 is not None and
        sha256(worksheet_bytes)!=expected_worksheet_sha256):
        errors.append("WORKSHEET_EXTERNAL_PIN_MISMATCH")
    try:
        doc=json.loads(canonical_bytes.decode("utf-8"))
        units=doc["learning_units"]
        if not isinstance(units,list) or len(units)!=expected_units:
            raise ValueError("CANONICAL_UNIT_COUNT")
        unit_map={u["id"]:u for u in units}
        if len(unit_map)!=len(units):
            raise ValueError("DUPLICATE_CANONICAL_ID")
        csvtext=worksheet_bytes.decode("utf-8-sig")
        reader=csv.DictReader(io.StringIO(csvtext,newline=""),restkey="__EXTRA__")
        fields=reader.fieldnames or []
        if (len(fields)!=len(set(fields)) or
            not set(("id",)+FROZEN+REVIEW_FIELDS).issubset(fields)):
            raise ValueError("WORKSHEET_HEADER_INVALID")
        rows=list(reader)
        decisions["rows"]=len(rows)
        if len(rows)!=expected_units:
            errors.append("WORKSHEET_ROW_COUNT_MISMATCH")
        worksheet_ids=[r.get("id") for r in rows]
        if len(set(worksheet_ids))!=len(worksheet_ids) or set(worksheet_ids)!=set(unit_map):
            errors.append("WORKSHEET_UNIT_ID_SET_MISMATCH")
        if worksheet_ids != [u["id"] for u in units]:
            errors.append("WORKSHEET_UNIT_ORDER_MISMATCH")
        for row in rows:
            uid=row.get("id","")
            if row.get("__EXTRA__"):
                errors.append("WORKSHEET_EXTRA_COLUMNS:"+str(uid))
            if row.get("expert_decision","").strip():
                decisions["entered"]+=1
            else:
                decisions["blank"]+=1
            for field in REVIEW_FIELDS:
                value=(row.get(field) or "").lstrip()
                if value.startswith(("=","+","-","@","\t","\r")):
                    errors.append("UNSAFE_REVIEWER_CELL:"+str(uid)+":"+field)
            if uid not in unit_map:
                continue
            baseline=projected(unit_map[uid])
            for field in FROZEN:
                old=row.get(field)
                if field.endswith("_json"):
                    try:old=json.loads(old)
                    except (ValueError,TypeError):
                        errors.append("UNPARSEABLE_WORKSHEET_JSON:"+uid+":"+field)
                        continue
                if old!=baseline[field]:
                    drift[field]+=1
                    ids.add(uid)
    except (UnicodeError,ValueError,TypeError,KeyError,IndexError,RecursionError,AttributeError) as exc:
        errors.append("MALFORMED_INPUT:"+type(exc).__name__)
    if errors:
        status="BLOCKED_INVALID_REVIEW_SNAPSHOT"
    elif ids:
        status="STALE_WORKSHEET_BLOCKS_STAGE4"
    else:
        status="CURRENT_WORKSHEET_ONLY_STAGE4_REVIEW_NOT_CERTIFIED"
    return result(status,errors,canonical_bytes,worksheet_bytes,drift,ids,decisions,expected_units)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip",type=Path,required=True)
    parser.add_argument("--expected-canonical-sha256",required=True)
    parser.add_argument("--expected-worksheet-sha256")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        with zipfile.ZipFile(args.zip) as archive:
            names=archive.namelist()
            if len(names)!=len(set(names)):
                raise ValueError("DUPLICATE_ZIP_MEMBERS")
            canonical=archive.read("02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json")
            worksheet=archive.read("05-QA-Tests/STAGE4-REVIEWER-WORKSHEET-CURRENT-UNSIGNED.csv")
        report=audit(canonical,worksheet,
              expected_canonical_sha256=args.expected_canonical_sha256,
              expected_worksheet_sha256=args.expected_worksheet_sha256)
    except (OSError,KeyError,ValueError,zipfile.BadZipFile,RuntimeError) as exc:
        print(json.dumps({"schema":SCHEMA,"status":"BLOCKED_UNREADABLE_INPUT",
              "error_type":type(exc).__name__,"stage4_semantic_pass":False}))
        return 2
    data=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        args.output.write_text(data,encoding="utf-8")
    else:
        print(data)
    return 2 if report["status"].startswith("BLOCKED") or report["status"].startswith("STALE") else 0

if __name__=="__main__":
    raise SystemExit(main())
