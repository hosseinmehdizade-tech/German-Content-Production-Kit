"""Synthetic-only exact snapshot + independent-method receipt contract tests."""
import copy
import csv
import io
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from audit_stage4_current_worksheet_freshness import projected,FROZEN,REVIEW_FIELDS
from audit_stage4_snapshot_review_receipt import (
    ANCHOR_SCHEMA,RECEIPT_SCHEMA,WORKSTREAM,DISPOSITIONS,
    digest,unit_hash,verify
)

def encoded(v):
    return json.dumps(v,ensure_ascii=False,sort_keys=True).encode("utf-8")

def fixtures():
    units=[]
    for n in range(2):
        units.append({
            "id":f"ahl-lu-synthetic-{n}",
            "headword":f"antworten-{n}","type":"verb",
            "definition_de":"reagieren","persian_meaning":"پاسخ دادن",
            "english_gloss":"answer",
            "core":{"auxiliary":"haben"},
            "details":{"rection":["jdm. antworten"],
                       "kombinationen":[{"text_de":"auf Fragen antworten"}],
                       "lexical_relations":[{"kind":"synonym","term_de":"erwidern"}]},
            "examples":[{"text":"Ich antworte dir.","translations":[
                {"lang":"fa-IR","text":"پاسخ می‌دهم."},
                {"lang":"en-US","text":"I answer you."}]}]
        })
    canonical=encoded({"learning_units":units})
    import_bytes=b"synthetic-import\tvalue\n"
    sources={"a1-a2":b"synthetic a1 original PDF","b1-c2":b"synthetic b1 original PDF"}
    out=io.StringIO(newline="")
    writer=csv.DictWriter(out,fieldnames=["id",*FROZEN,*REVIEW_FIELDS])
    writer.writeheader()
    for unit in units:
        p=projected(unit)
        row={"id":unit["id"],**{k:json.dumps(v,ensure_ascii=False) if k.endswith("_json") else v
                                  for k,v in p.items()}}
        row.update({k:"" for k in REVIEW_FIELDS})
        writer.writerow(row)
    worksheet=out.getvalue().encode("utf-8")
    anchor={
        "schema":ANCHOR_SCHEMA,"workstream":WORKSTREAM,"expected_units":2,
        "canonical_sha256":digest(canonical),
        "import_sha256":digest(import_bytes),
        "worksheet_sha256":digest(worksheet),
        "portable_zip_sha256":digest(b"synthetic expected ZIP"),
        "source_pdfs":{
            "a1-a2":{"sha256":digest(sources["a1-a2"]),"pages":10},
            "b1-c2":{"sha256":digest(sources["b1-c2"]),"pages":35}
        }
    }
    reviews=[]
    for n,u in enumerate(units):
        reviews.append({
            "unit_id":u["id"],"unit_sha256":unit_hash(u),
            "reviewer_id":"separate-reviewer","method":"independent_ai_second_pass",
            "evidence_ref":f"source-and-output-check-{n}",
            "source_locator":{"source_id":"a1-a2","page":n+1},
            "disposition":"verified_keep","applied_change_sha256":None
        })
    receipt={
        "schema":RECEIPT_SCHEMA,"workstream":WORKSTREAM,
        "snapshot":{k:anchor[k] for k in ("canonical_sha256","import_sha256",
             "worksheet_sha256","portable_zip_sha256","source_pdfs")},
        "producer_id":"first-pass-producer",
        "reviewed_unique":2,"unreviewed":0,
        "disposition_counts":{k:2 if k=="verified_keep" else 0 for k in DISPOSITIONS},
        "reviews":reviews
    }
    return [anchor,canonical,import_bytes,worksheet,sources,receipt]

def audit(f):
    return verify(f[0],f[1],f[2],f[3],f[4],encoded(f[5]))

def test_complete_coherent_receipt_is_not_approval():
    o=audit(fixtures())
    assert o["status"]=="COMPLETE_RECEIPT_STRUCTURE_ONLY_NOT_SIGNED_OFF",o
    assert o["reviewed_unique"]==2 and o["unreviewed"]==0
    assert not o["stage4_semantic_pass"] and not o["issuer_authenticated"]
    assert not o["production_authorized"] and not o["stage5_allowed"]
    assert not o["performed_writes"]

def test_partial_receipt_stays_open():
    f=fixtures()
    f[5]["reviews"].pop()
    f[5]["reviewed_unique"]=1
    f[5]["unreviewed"]=1
    f[5]["disposition_counts"]["verified_keep"]=1
    r=audit(f)
    assert r["status"]=="OPEN_PARTIAL_REVIEW_NOT_SIGNED_OFF"
    assert r["reviewed_unique"]==1 and r["unreviewed"]==1

@pytest.mark.parametrize("part",["canonical","import","worksheet","a1-a2","b1-c2"])
def test_changed_bytes_without_external_pin_block(part):
    f=fixtures()
    if part=="canonical":f[1]+=b" "
    elif part=="import":f[2]+=b" "
    elif part=="worksheet":f[3]+=b" "
    else:f[4][part]+=b" "
    r=audit(f)
    assert r["status"]=="BLOCKED_REVIEW_RECEIPT_BINDING"

def test_forged_repin_canonical_still_rejects_stale_worksheet_and_receipt():
    f=fixtures()
    doc=json.loads(f[1])
    doc["learning_units"][0]["persian_meaning"]="بازنویسی جدید"
    f[1]=encoded(doc)
    f[0]["canonical_sha256"]=digest(f[1])
    r=audit(f)
    assert "STALE_OR_MALFORMED_REVIEWER_SNAPSHOT" in r["errors"]
    assert "RECEIPT_SNAPSHOT_DRIFT" in r["errors"]
    assert any(e.startswith("UNIT_CONTENT_SHA_DRIFT:") for e in r["errors"])

def test_stale_reviewer_baseline_cannot_be_reused_even_if_receipt_rehashed():
    f=fixtures()
    f[3]=f[3].replace(b"reagieren",b"something-else")
    f[0]["worksheet_sha256"]=digest(f[3])
    f[5]["snapshot"]["worksheet_sha256"]=f[0]["worksheet_sha256"]
    assert "STALE_OR_MALFORMED_REVIEWER_SNAPSHOT" in audit(f)["errors"]

@pytest.mark.parametrize("change,error",[
    ("unit_digest","UNIT_CONTENT_SHA_DRIFT:"),
    ("reviewer","REVIEWER_INDEPENDENCE_NOT_EVIDENCED:"),
    ("method","REVIEW_METHOD_UNKNOWN:"),
    ("locator","SOURCE_LOCATOR_INVALID:"),
    ("evidence","REVIEW_EVIDENCE_MISSING:"),
    ("disposition","DISPOSITION_INVALID:"),
])
def test_review_control_failure(change,error):
    f=fixtures()
    obj=f[5]["reviews"][0]
    if change=="unit_digest":obj["unit_sha256"]="f"*64
    elif change=="reviewer":obj["reviewer_id"]=f[5]["producer_id"]
    elif change=="method":obj["method"]="AI-self-certification"
    elif change=="locator":obj["source_locator"]={"source_id":"b1-c2","page":36}
    elif change=="evidence":obj["evidence_ref"]=""
    else:obj["disposition"]="done"
    assert any(s.startswith(error) for s in audit(f)["errors"])

def test_unknown_source_locator_list_type_fails_without_crashing():
    f=fixtures()
    f[5]["reviews"][0]["source_locator"]["source_id"]=["a1-a2"]
    assert any(x.startswith("SOURCE_LOCATOR_INVALID") for x in audit(f)["errors"])

def test_replay_duplicate_unit_does_not_count_as_distinct_review():
    f=fixtures()
    f[5]["reviews"][1]=copy.deepcopy(f[5]["reviews"][0])
    r=audit(f)
    assert "DUPLICATE_REVIEW_UNIT" in r["errors"]
    assert "REVIEW_COUNT_MISMATCH" in r["errors"]
    assert "UNREVIEWED_COUNT_MISMATCH" in r["errors"]

def test_false_disposition_conservation_blocks():
    f=fixtures()
    f[5]["disposition_counts"]["verified_keep"]=1
    assert "DISPOSITION_COUNT_MISMATCH" in audit(f)["errors"]

def test_reviewed_corrected_is_never_proof_of_applied_content():
    f=fixtures()
    f[5]["reviews"][0]["disposition"]="corrected"
    f[5]["reviews"][0]["applied_change_sha256"]="a"*64
    f[5]["disposition_counts"]["verified_keep"]=1
    f[5]["disposition_counts"]["corrected"]=1
    r=audit(f)
    assert any(e.startswith("CORRECTED_REQUIRES_SEPARATE_POSTEDIT_CAS_EVIDENCE:") for e in r["errors"])
    assert r["stage4_semantic_pass"] is False

def test_direct_self_authorizing_issuer_key_fails_closed():
    f=fixtures()
    f[5]["issuer_authorized"]=True
    assert "RECEIPT_SHAPE_INVALID" in audit(f)["errors"]

def test_rejected_duplicate_json_keys():
    f=fixtures()
    raw=encoded(f[5])
    raw=raw.replace(b'"schema":',b'"schema":"older","schema":',1)
    r=verify(f[0],f[1],f[2],f[3],f[4],raw)
    assert r["status"]=="BLOCKED_REVIEW_RECEIPT_BINDING"
    assert "CANONICAL_OR_RECEIPT_INVALID_JSON" in r["errors"]

def test_rejected_nonfinite_json():
    f=fixtures()
    raw=encoded(f[5]).replace(b'"reviewed_unique":2',b'"reviewed_unique":NaN')
    r=verify(f[0],f[1],f[2],f[3],f[4],raw)
    assert "CANONICAL_OR_RECEIPT_INVALID_JSON" in r["errors"]

def test_unpinned_or_incomplete_source_set_blocks():
    f=fixtures()
    f[0]["source_pdfs"].pop("b1-c2")
    assert "SOURCE_SET_INVALID" in audit(f)["errors"]
