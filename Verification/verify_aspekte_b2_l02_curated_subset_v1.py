#!/usr/bin/env python3
"""Native read-only B2 L02 draft subset guard using the accepted R14 curated overlay.

Never reimports original textbook CSV. Verifies parent SHA, stable source IDs,
R15 partial projection, complete bilingual examples and hard NONIMPORT flags.
No claim about independent lexical QA, final cards, native app or SRS.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys

MAX_BYTES=25_000_000
FIELDS={"unit_id","source_ordinal","source_id","front_de_preview",
        "back_fa_preview","example_1_de","example_1_fa",
        "example_2_de","example_2_fa",
        "export_importable","linguistic_release_approved",
        "editorial_parent_overlay","qa_status"}


class B2L02Failure(ValueError):
    pass


def need(ok,msg):
    if not ok: raise B2L02Failure(msg)


def pinned(path,expected):
    path=Path(path)
    need(path.is_file() and not path.is_symlink() and
         0<path.stat().st_size<=MAX_BYTES,"CURRENT_OR_PARENT_MISSING_OR_UNSAFE")
    need(re.fullmatch("[a-f0-9]{64}",str(expected)) is not None,
         "MISSING_EXACT_SHA_PIN")
    raw=path.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==expected,"CURATED_SHA256_MISMATCH")
    return raw


def scope(latest):
    s=latest.get("latest_l02_scoped_audit")
    need(isinstance(s,dict) and
         re.fullmatch(r"L02_R[1-9][0-9]*_.*_NONIMPORT",str(s.get("label","")))
         is not None, "L02_CURATED_LATEST_UNAVAILABLE")
    need(s.get("lesson")==2 and s.get("project_id")=="aspekte-b2"
         and s.get("source_rows")==108 and s.get("source_ordinal_range")==[1709,1816],
         "L02_OWNER_OR_PARENT_SCOPE_MISMATCH")
    need(s.get("importable") is False and s.get("stage2_approved") is False
         and s.get("formal_stage4_qa_approved") is False
         and s.get("stage3_to_stage7")=="NOT_STARTED",
         "FALSE_STAGE_APPROVAL_OR_IMPORT")
    need(s.get("source_rows_unchanged") is True and
         s.get("original_source_membership_reaudited") is False
         and s.get("prior_user_cards_modified") is False,
         "ORIGINAL_SOURCE_REAUDIT_OR_USER_CARD_MUTATION")
    for key,ext in (("parent_overlay_path",".jsonl"),("current_draft_path",".csv")):
        path=str(s.get(key,""))
        need(path.startswith("/Flasch kart/German-Content-Production-Kit/"
                             "Content/Aspekte-B2/Current/")
             and path.endswith(ext) and (key!="current_draft_path" or
                                          path.endswith("-NONIMPORT.csv")),
             "NONOWNER_OR_OLD_RAW_SOURCE_PATH")
    need(s.get("accepted_editorial_parent")=="R14_108_SOURCE_BOUND_OVERLAY",
         "NOT_THE_ACCEPTED_EDITORIAL_PARENT")
    need(isinstance(s.get("current_draft_rows"),int)
         and 0<s["current_draft_rows"]<=s["source_rows"],
         "INVALID_SCOPED_DRAFT_COUNT")
    return s


def audit(latest,parent,draft):
    s=scope(latest)
    need(Path(parent).name==Path(s["parent_overlay_path"]).name and
         Path(draft).name==Path(s["current_draft_path"]).name,
         "ARTIFACT_NOT_THE_CURRENT_PROJECT_POINTER")
    raw_parent=pinned(parent,s["parent_overlay_sha256"])
    raw_draft=pinned(draft,s["current_draft_sha256"])
    try:
        parents=[json.loads(line) for line in
                 raw_parent.decode("utf-8-sig").splitlines() if line.strip()]
        reader=csv.DictReader(io.StringIO(raw_draft.decode("utf-8-sig"),newline=""),
                              strict=True)
        headers=reader.fieldnames or []
        need(len(headers)==len(set(headers)) and FIELDS<=set(headers),
             "DRAFT_REQUIRED_FIELDS_MISSING_OR_DUPLICATE")
        projected=list(reader)
    except (UnicodeError,csv.Error,json.JSONDecodeError) as e:
        raise B2L02Failure("CURATED_PARENT_OR_DRAFT_DECODE_FAILED") from e
    need(len(parents)==108 and len(projected)==s["current_draft_rows"],
         "SCOPED_PARENT_OR_DRAFT_ROW_COUNT_CHANGED")
    ordered={}
    for row in parents:
        ordinal=row.get("source_csv_ordinal")
        need(isinstance(ordinal,int) and ordinal not in ordered
             and row.get("source_row_id"),"PARENT_IDENTITY_INVALID")
        ordered[ordinal]=row
    need(set(ordered)==set(range(1709,1817)),
         "PARENT_CURATED_SOURCE_ORDINAL_COVERAGE_CHANGED")
    ids=set()
    selected=set()
    for row in projected:
        need(None not in row and None not in row.values(),
             "MALFORMED_CURATED_CARD_ROW")
        ident=row.get("unit_id","")
        ordstr=row.get("source_ordinal","")
        need(bool(ident) and ident not in ids and
             re.fullmatch("[0-9]+",ordstr or "") is not None,
             "DUPLICATE_OR_UNSTABLE_DRAFT_ID")
        ids.add(ident)
        ordval=int(ordstr)
        need(ordval in ordered and ordval not in selected and
             row.get("source_id")==ordered[ordval]["source_row_id"],
             "PROPOSED_CARD_NOT_IN_CURATED_PARENT")
        selected.add(ordval)
        need(row["export_importable"]=="FALSE" and
             row["linguistic_release_approved"]=="FALSE"
             and "NOT_INDEPENDENT" in row["qa_status"],
             "UNAPPROVED_DRAFT_MARKED_FINAL")
        need(row["editorial_parent_overlay"]=="L02_R14",
             "MISMATCHED_PUBLISHED_EDITORIAL_PARENT")
        for key in ("front_de_preview","back_fa_preview","example_1_de",
                    "example_1_fa","example_2_de","example_2_fa"):
            need(bool(row.get(key,"").strip()),"MISSING_BILINGUAL_CONTENT:"+key)
    remaining=sorted(set(ordered)-selected)
    need(len(remaining)==s["remaining_parent_records_not_yet_curated_to_units"]
         and len(selected)==s["current_draft_rows"]
         and len(selected)*2==s["bilingual_example_pairs"],
         "CHAPTER_2_DELTA_ACCOUNTING_OR_EXAMPLE_COUNT_INVALID")
    need(s.get("next_ordinal_to_curate")==remaining[0] if remaining else
         s.get("next_ordinal_to_curate") is None,
         "NEXT_CURATED_LESSON_ORDINAL_MISMATCH")
    return {
        "status":"PASS_L02_R14_TO_SCOPED_CURATED_DRAFT_SUBSET_NOT_STAGE_APPROVAL",
        "source_compared":"NONE__CURATED_PARENT_R14_ONLY",
        "project":"aspekte-b2","lesson":2,
        "parent_rows":len(parents),"projected_draft_units":len(projected),
        "unprojected_parent_units":len(remaining),
        "next_ordinal":remaining[0] if remaining else None,
        "paired_bilingual_examples":len(selected)*2,
        "parent_sha256":hashlib.sha256(raw_parent).hexdigest(),
        "draft_sha256":hashlib.sha256(raw_draft).hexdigest(),
        "source_rows_deleted":0,"app_import":"NOT_AUTHORIZED",
        "semantic_approval":"NOT_CHECKED","stage2":"NOT_APPROVED",
        "stage6":"NOT_RUN","stage7":"NOT_RUN",
    }


def main(argv=None):
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--latest",required=True,type=Path)
    cli.add_argument("--parent-curated",required=True,type=Path)
    cli.add_argument("--draft",required=True,type=Path)
    args=cli.parse_args(argv)
    try:
        latest=json.loads(args.latest.read_text(encoding="utf-8"))
        out=audit(latest,args.parent_curated,args.draft)
        print(json.dumps(out,ensure_ascii=False,sort_keys=True))
        return 0
    except (ValueError,OSError) as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc)},
                         ensure_ascii=False))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
