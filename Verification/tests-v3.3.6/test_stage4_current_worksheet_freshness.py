"""Synthetic OP02 Stage4 freshness contract; no user-card edits or Stage4 approval."""
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from audit_stage4_current_worksheet_freshness import audit,projected,sha256,REVIEW_FIELDS,FROZEN

def fixture():
    unit={
      "id":"ahl-lu-test1","headword":"antworten","type":"verb",
      "definition_de":"reagieren","persian_meaning":"پاسخ دادن",
      "english_gloss":"answer","core":{"auxiliary":"haben"},
      "examples":[{"text":"Ich antworte dir.","translations":[{"lang":"fa-IR","text":"پاسخ می‌دهم."},
          {"lang":"en-US","text":"I answer you."}]}],
      "details":{"rection":["jdm. antworten"],
                 "kombinationen":[{"text_de":"auf Fragen antworten"}],
                 "lexical_relations":[{"kind":"synonym","term_de":"erwidern"}]}
    }
    can=json.dumps({"learning_units":[unit]},ensure_ascii=False).encode("utf-8")
    fields=["id",*FROZEN,*REVIEW_FIELDS]
    output=io.StringIO(newline="")
    w=csv.DictWriter(output,fieldnames=fields)
    w.writeheader()
    data=projected(unit)
    row={"id":unit["id"],**{k:json.dumps(v,ensure_ascii=False) if k.endswith("_json") else v
                              for k,v in data.items()}}
    row.update({k:"" for k in REVIEW_FIELDS})
    w.writerow(row)
    return can,output.getvalue().encode("utf-8"),unit

def run(can,ws):
    return audit(can,ws,expected_units=1)

def test_exact_sheet_never_certifies_stage4():
    c,w,_=fixture()
    r=run(c,w)
    assert r["status"]=="CURRENT_WORKSHEET_ONLY_STAGE4_REVIEW_NOT_CERTIFIED"
    assert r["stage4_semantic_pass"] is False and r["decisions_blank"]==1

@pytest.mark.parametrize("field",["definition_de","meaning_fa","gloss_en",
                                    "rection_json","examples_en_json",
                                    "kombinationen_json","relations_json"])
def test_stale_frozen_field_blocks(field):
    c,w,u=fixture()
    doc=json.loads(c)
    target=doc["learning_units"][0]
    if field=="definition_de":target["definition_de"]="new sense"
    elif field=="meaning_fa":target["persian_meaning"]="پاسخ گفتن"
    elif field=="gloss_en":target["english_gloss"]="reply"
    elif field=="rection_json":target["details"]["rection"]=["auf + Akkusativ antworten"]
    elif field=="examples_en_json":target["examples"][0]["translations"][-1]["text"]="I replied."
    elif field=="kombinationen_json":target["details"]["kombinationen"].append({"text_de":"jdm. antworten"})
    elif field=="relations_json":target["details"]["lexical_relations"].append({"term_de":"die Antwort"})
    c=json.dumps(doc,ensure_ascii=False).encode("utf-8")
    r=run(c,w)
    assert r["status"]=="STALE_WORKSHEET_BLOCKS_STAGE4"
    assert r["affected_units"]==1 and r["drifts_by_field"][field]==1
    assert not r["stage4_semantic_pass"]

def test_external_byte_pin_mismatch_blocks():
    c,w,_=fixture()
    r=audit(c,w,expected_units=1,expected_canonical_sha256="f"*64)
    assert "CANONICAL_EXTERNAL_PIN_MISMATCH" in r["errors"]

def test_duplicate_worksheet_header_blocks():
    c,w,_=fixture()
    w=w.replace(b"definition_de,",b"definition_de,definition_de,",1)
    assert run(c,w)["status"]=="BLOCKED_INVALID_REVIEW_SNAPSHOT"

def test_malformed_json_blocks():
    _,w,_=fixture()
    assert run(b'{"learning_units":',w)["status"]=="BLOCKED_INVALID_REVIEW_SNAPSHOT"

def test_no_reviewer_signature_not_an_approval():
    c,w,_=fixture()
    w=w.replace(b"\r\n",b"\n")
    r=run(c,w)
    assert r["production_authorized"] is False

def test_injected_reviewer_formula_is_blocked():
    c,w,_=fixture()
    text=w.decode("utf-8")
    text=text.rstrip("\r\n")+",=2+2\n"
    assert run(c,text.encode("utf-8"))["status"]=="BLOCKED_INVALID_REVIEW_SNAPSHOT"
