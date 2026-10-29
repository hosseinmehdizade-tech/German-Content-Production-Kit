#!/usr/bin/env python3
"""OP-02 NONACTIVE read-only Stage4 per-unit receipt binding; NEVER a signoff.

The anchor is externally PROVIDED and must be independently authenticated;
matching hashes, reviewer names or self-asserted approvals prove no authority.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import re
from audit_stage4_current_worksheet_freshness import audit as audit_freshness

SCHEMA = "gcpk-op02-stage4-receipt-binding@1"
RECEIPT_SCHEMA = "gcpk-op02-stage4-independent-review-receipt-PROPOSAL@1"
ANCHOR_SCHEMA = "gcpk-op02-stage4-snapshot-anchor-PROPOSAL@1"
WORKSTREAM = "aber-hallo-listen-tabellen"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
SOURCE_IDS = ("a1-a2", "b1-c2")
DISPOSITIONS = ("verified_keep", "closed_no_force", "evidence_hold",
                "rejected", "corrected")
METHODS = ("independent_ai_second_pass", "independent_review")
ANCHOR_KEYS = {"schema", "workstream", "canonical_sha256", "import_sha256",
               "worksheet_sha256", "portable_zip_sha256", "source_pdfs",
               "expected_units"}
RECEIPT_KEYS = {"schema", "workstream", "snapshot", "producer_id",
                "reviewed_unique", "unreviewed", "disposition_counts", "reviews"}
REVIEW_KEYS = {"unit_id", "unit_sha256", "reviewer_id", "method",
               "evidence_ref", "source_locator", "disposition",
               "applied_change_sha256"}
LOCATOR_KEYS = {"source_id", "page"}
MAX_BYTES = 32_000_000

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def clean_hash(value) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None and value != "0"*64

def _pairs(items):
    obj = {}
    for k, v in items:
        if k in obj:
            raise ValueError("DUPLICATE_JSON_KEY")
        obj[k] = v
    return obj

def _no_constant(value):
    raise ValueError("INVALID_JSON_CONSTANT:"+value)

def parse(raw: bytes):
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError("INVALID_RAW_BYTES")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                      parse_constant=_no_constant)

def unit_hash(unit:dict) -> str:
    stable = json.dumps(unit, ensure_ascii=False, sort_keys=True,
                        separators=(",",":"), allow_nan=False).encode("utf-8")
    return digest(stable)

def report(errors, reviewed, outstanding, corrected_count):
    if errors:
        status="BLOCKED_REVIEW_RECEIPT_BINDING"
    elif outstanding:
        status="OPEN_PARTIAL_REVIEW_NOT_SIGNED_OFF"
    else:
        status="COMPLETE_RECEIPT_STRUCTURE_ONLY_NOT_SIGNED_OFF"
    return {
        "schema":SCHEMA,"status":status,"errors":sorted(set(errors)),
        "reviewed_unique":reviewed,"unreviewed":outstanding,
        "corrected_claims":corrected_count,
        "stage4_semantic_pass":False,"issuer_authenticated":False,
        "production_authorized":False,"stage5_allowed":False,
        "performed_writes":False,
        "limits":[
            "Externally provided anchor is not an authenticated issuer signature",
            "Unit digest binds whole Canonical unit but not independent linguistic correctness",
            "Reviewer identity and methods inside self-authored receipt are not cryptographic proof",
            "Applied corrections need separate verified post-edit bytes and CAS readback",
            "Real Stage4, Stage5, Stage6 and Stage7 remain separate"
        ]
    }

def verify(anchor, canonical_bytes:bytes, import_bytes:bytes,
           worksheet_bytes:bytes, source_pdf_bytes:dict,
           receipt_bytes:bytes) -> dict:
    errors=[]
    reviewed=0
    expected_units=0
    corrected_count=0
    if not isinstance(anchor,dict) or set(anchor)!=ANCHOR_KEYS:
        return report(["ANCHOR_SHAPE_INVALID"],0,0,0)
    if anchor.get("schema")!=ANCHOR_SCHEMA or anchor.get("workstream")!=WORKSTREAM:
        errors.append("ANCHOR_IDENTITY_INVALID")
    if type(anchor.get("expected_units")) is not int or not 1<=anchor["expected_units"]<=100000:
        return report(["EXPECTED_UNITS_INVALID"],0,0,0)
    expected_units=anchor["expected_units"]
    for key in ("canonical_sha256","import_sha256","worksheet_sha256","portable_zip_sha256"):
        if not clean_hash(anchor.get(key)):
            errors.append("ANCHOR_SHA_INVALID:"+key)
    sources=anchor.get("source_pdfs")
    if not isinstance(sources,dict) or set(sources)!=set(SOURCE_IDS):
        errors.append("SOURCE_SET_INVALID")
        sources={}
    for source_id in SOURCE_IDS:
        entry=sources.get(source_id)
        if not isinstance(entry,dict) or set(entry)!={"sha256","pages"} or not clean_hash(entry.get("sha256")) or type(entry.get("pages")) is not int or entry["pages"]<1:
            errors.append("SOURCE_ANCHOR_INVALID:"+source_id)
    if errors:
        return report(errors,0,expected_units,0)
    if not isinstance(source_pdf_bytes,dict) or set(source_pdf_bytes)!=set(SOURCE_IDS):
        errors.append("SOURCE_RAW_SET_INVALID")
    else:
        for source_id in SOURCE_IDS:
            raw=source_pdf_bytes[source_id]
            if not isinstance(raw,bytes) or digest(raw)!=sources[source_id]["sha256"]:
                errors.append("SOURCE_RAW_SHA_MISMATCH:"+source_id)
    for key,raw in (("canonical_sha256",canonical_bytes),
                    ("import_sha256",import_bytes),
                    ("worksheet_sha256",worksheet_bytes)):
        if not isinstance(raw,bytes) or digest(raw)!=anchor[key]:
            errors.append("SNAPSHOT_BYTE_PIN_MISMATCH:"+key)
    if errors:
        return report(errors,0,expected_units,0)
    try:
        canonical=parse(canonical_bytes)
        receipt=parse(receipt_bytes)
        units=canonical["learning_units"]
        if not isinstance(units,list) or len(units)!=expected_units:
            raise ValueError("CANONICAL_UNIT_COUNT")
        unit_ids=[u["id"] for u in units]
        if len(set(unit_ids))!=expected_units or any(not isinstance(i,str) or not i for i in unit_ids):
            raise ValueError("CANONICAL_UNIT_IDS")
        unit_hashes={u["id"]:unit_hash(u) for u in units}
    except (ValueError,UnicodeError,TypeError,KeyError,RecursionError,AttributeError):
        return report(["CANONICAL_OR_RECEIPT_INVALID_JSON"],0,expected_units,0)
    freshness=audit_freshness(canonical_bytes,worksheet_bytes,
             expected_units=expected_units,expected_canonical_sha256=anchor["canonical_sha256"],
             expected_worksheet_sha256=anchor["worksheet_sha256"])
    if freshness["status"]!="CURRENT_WORKSHEET_ONLY_STAGE4_REVIEW_NOT_CERTIFIED":
        errors.append("STALE_OR_MALFORMED_REVIEWER_SNAPSHOT")
    if not isinstance(receipt,dict) or set(receipt)!=RECEIPT_KEYS:
        return report(errors+["RECEIPT_SHAPE_INVALID"],0,expected_units,0)
    if receipt["schema"]!=RECEIPT_SCHEMA or receipt["workstream"]!=WORKSTREAM:
        errors.append("RECEIPT_IDENTITY_INVALID")
    snapshot=receipt["snapshot"]
    if not isinstance(snapshot,dict) or snapshot!= {
            k:anchor[k] for k in ("canonical_sha256","import_sha256",
                                   "worksheet_sha256","portable_zip_sha256","source_pdfs")}:
        errors.append("RECEIPT_SNAPSHOT_DRIFT")
    producer=receipt["producer_id"]
    if not isinstance(producer,str) or len(producer.strip())<3:
        errors.append("PRODUCER_ID_MISSING")
    reviews=receipt["reviews"]
    if not isinstance(reviews,list):
        return report(errors+["REVIEWS_LIST_INVALID"],0,expected_units,0)
    if len(reviews)>expected_units:
        errors.append("REVIEWS_OVERFLOW")
    ids=[]
    counts=Counter()
    for ix,review in enumerate(reviews):
        if not isinstance(review,dict) or set(review)!=REVIEW_KEYS:
            errors.append("REVIEW_SCHEMA_INVALID:"+str(ix))
            continue
        uid=review["unit_id"]
        if not isinstance(uid,str) or uid not in unit_hashes:
            errors.append("UNKNOWN_REVIEWED_UNIT:"+str(ix))
            continue
        ids.append(uid)
        if review["unit_sha256"]!=unit_hashes[uid]:
            errors.append("UNIT_CONTENT_SHA_DRIFT:"+uid)
        reviewer=review["reviewer_id"]
        if not isinstance(reviewer,str) or len(reviewer.strip())<3 or reviewer==producer:
            errors.append("REVIEWER_INDEPENDENCE_NOT_EVIDENCED:"+uid)
        if review["method"] not in METHODS:
            errors.append("REVIEW_METHOD_UNKNOWN:"+uid)
        if not isinstance(review["evidence_ref"],str) or len(review["evidence_ref"].strip())<8:
            errors.append("REVIEW_EVIDENCE_MISSING:"+uid)
        locator=review["source_locator"]
        if not isinstance(locator,dict) or set(locator)!=LOCATOR_KEYS:
            errors.append("SOURCE_LOCATOR_INVALID:"+uid)
        else:
            sid=locator["source_id"]
            page=locator["page"]
            if not isinstance(sid,str) or sid not in sources or type(page) is not int or not 1<=page<=sources[sid]["pages"]:
                errors.append("SOURCE_LOCATOR_INVALID:"+uid)
        disp=review["disposition"]
        if disp not in DISPOSITIONS:
            errors.append("DISPOSITION_INVALID:"+uid)
        else:
            counts[disp]+=1
        if disp=="corrected":
            corrected_count+=1
            # Never auto-certify content application from self-authored receipt.
            errors.append("CORRECTED_REQUIRES_SEPARATE_POSTEDIT_CAS_EVIDENCE:"+uid)
        elif review["applied_change_sha256"] is not None:
            errors.append("UNEXPECTED_APPLIED_CHANGE:"+uid)
    reviewed=len(set(ids))
    outstanding=expected_units-reviewed
    if len(ids)!=reviewed:
        errors.append("DUPLICATE_REVIEW_UNIT")
    if type(receipt["reviewed_unique"]) is not int or receipt["reviewed_unique"]!=reviewed:
        errors.append("REVIEW_COUNT_MISMATCH")
    if type(receipt["unreviewed"]) is not int or receipt["unreviewed"]!=outstanding:
        errors.append("UNREVIEWED_COUNT_MISMATCH")
    declared=receipt["disposition_counts"]
    if not isinstance(declared,dict) or set(declared)!=set(DISPOSITIONS) or any(
            type(declared[k]) is not int or declared[k]<0 for k in DISPOSITIONS):
        errors.append("DISPOSITION_COUNTS_INVALID")
    elif declared!={k:counts[k] for k in DISPOSITIONS}:
        errors.append("DISPOSITION_COUNT_MISMATCH")
    return report(errors,reviewed,outstanding,corrected_count)
