"""OP-02 synthetic-only consumer bridge checks pinned to exact v486 source semantics."""
from __future__ import annotations

import copy
import csv
import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))  # allow real companion module's normal Python imports

def load(name):
    spec=importlib.util.spec_from_file_location(name.replace("-","_"),ROOT/name)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

base=load("validate_stage45_teaching_delta_parity.py")
bridge=load("validate_stage45_v486_consumer_bridge.py")


def source():
    card = {"id": "case-1", "category":"noun",
        "combination_disposition":"PRESENT", "kombinationen": [
            {"item_id":"item-1","de":"eine Entscheidung treffen",
             "fa":"تصمیم گرفتن","en":"make a decision","kind":"noun_verb",
             "provenance":"CURATED_PEDAGOGICAL",
             "teaching_delta":{"kind":"noun_verb","reason":"Learns the support verb"}},
            {"item_id":"item-2","de":"eine wichtige Entscheidung",
             "fa":"تصمیم مهم","en":"an important decision","kind":"adjective_noun",
             "provenance":"CURATED_PEDAGOGICAL",
             "teaching_delta":{"kind":"collocation","reason":"Adjective agreement"}}
        ]}
    empty={"id":"case-2","category":"verb",
           "kombinationen":[],"combination_disposition":"CLOSED_NO_FORCE",
           "combination_close_reason":"No incremental learning value"}
    s4={"source_authority_sha256":"e"*64,"cards":[card,empty]}
    review={
        "status":"PASS_AI_LINGUISTIC_QA_AND_TECHNICAL_GATES",
        "scope":"WHOLE_EXACT_STAGE4_CONTENT",
        "review_kind":"AI_INDEPENDENT_ADVERSARIAL",
        "reviewed_stage4_sha256":base.sha(json_bytes(s4)),
        "source_authority_sha256":"e"*64,
        "authoring_method":"SYNTHETIC_CREATION",
        "independent_method":"SYNTHETIC_ADVERSARIAL",
        "adversarial_method_evidence":"machine fixture, not real AI evaluation",
        "risk_queue_open":0,
        "deterministic_scanned_cards":2,
        "item_dispositions":[{
            "card_id":card["id"],"item_id":item["item_id"],
            "disposition":"KEEP_WITH_REASON",
            "stage4_item_sha256":base.sha(base.canonical(item)),
            "reason":"Synthetic fixture teaching check"
        } for item in card["kombinationen"]]
    }
    rows=[]
    for card in s4["cards"]:
        rich=copy.deepcopy(card["kombinationen"])
        row={"id":card["id"],"front":"synthetic DE","back":"معنی ساختگی",
             "card_type":"de-vocabulary","category":card["category"],
             "custom_fields":json.dumps({
                 "presentation_contract":"gfp-vocabulary-neutral@1",
                 "kombinationen":rich,
                 "kombinationen_v1":{
                     "visible_section":"Kombinationen",
                     "items":copy.deepcopy(rich)}
             },ensure_ascii=False)}
        rows.append(row)
    return s4,review,rows


def json_bytes(data):
    return json.dumps(data,ensure_ascii=False,indent=2).encode("utf-8")


def tsv_bytes(rows,with_details=False):
    fields=["id","front","back","card_type","category","custom_fields"]
    if with_details:
        fields.append("details")
    out=io.StringIO(newline="")
    w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n")
    w.writeheader()
    for row in rows:w.writerow(row)
    return out.getvalue().encode("utf-8")


def validate(s4,review,rows,sidecar_patch=None,include_details=False):
    a,b,c=json_bytes(s4),json_bytes(review),tsv_bytes(rows,include_details)
    base_proof={"schema":base.SCHEMA,"status":base.STATUS,
                "source_authority_sha256":"e"*64,
                "stage4_sha256":base.sha(a),
                "stage4_review_sha256":base.sha(b),
                "stage5_tsv_sha256":base.sha(c)}
    view_proof={"schema":bridge.SCHEMA,"status":base.STATUS,
                "runtime_version":bridge.RUNTIME,
                "runtime_sha256":bridge.RUNTIME_SHA,
                "presentation_function":bridge.VIEW_FUNCTION,
                "tsv_parser_function":bridge.READ_FUNCTION,
                "stage5_tsv_sha256":base.sha(c)}
    view_proof.update(sidecar_patch or {})
    return bridge.validate(base_proof,view_proof,a,b,c)


def update_view(rows,index,do):
    data=json.loads(rows[index]["custom_fields"])
    do(data)
    rows[index]["custom_fields"]=json.dumps(data,ensure_ascii=False)


def blocked(do,reason,include_details=False):
    a,b,c=source()
    do(a,b,c)
    output=validate(a,b,c,include_details=include_details)
    assert output["status"]=="BLOCKED",output
    assert any(reason in problem for problem in output["errors"]),output


def test_full_two_item_dual_projection_passes():
    result=validate(*source())
    assert result["status"]=="PASS_SCOPED_DETERMINISTIC_CONSUMER_PROFILE_ONLY"
    assert result["counts"]=={"visible_stage4_items":2,"closed_no_force_cards":1,"cards":2}


def test_bare_kombinationen_array_without_app_bridge_is_blocked():
    blocked(lambda a,b,c:update_view(c,0,lambda f:f.pop("kombinationen_v1")),
            "MISSING_V486_VISIBLE_COMBINATION_BRIDGE")


def test_wrong_visible_section_selector_blocked():
    blocked(lambda a,b,c:update_view(c,0,lambda f:f["kombinationen_v1"].update(
        visible_section="Kollokationen")),"V486_VISIBLE_SECTION_SELECTOR_MISMATCH")


@pytest.mark.parametrize("mutation",[
    lambda value:value.pop(),
    lambda value:value.reverse(),
    lambda value:value[0].update(fa="دیگر"),
    lambda value:value[0].pop("teaching_delta"),
    lambda value:value[1].update(provenance="OTHER"),
    lambda value:value[0].update(de="wrong German"),
    lambda value:value[0].update(en="different English"),
])
def test_bridge_cannot_drop_reorder_or_change_any_rich_item(mutation):
    blocked(lambda a,b,c:update_view(c,0,lambda f:mutation(
        f["kombinationen_v1"]["items"])),"V486_BRIDGE_ITEMS_LOSS_OR_MUTATION")


def test_unknown_camel_case_alias_conflict_is_blocked():
    blocked(lambda a,b,c:update_view(c,0,lambda f:f.update(
        kombinationenV1={"visible_section":"Kombinationen","items":[]})),
        "DUAL_CAMEL_AND_SNAKE_BRIDGE_ALIAS_FORBIDDEN")


def test_empty_closed_card_may_omit_view_bridge_without_false_quota():
    a,b,c=source()
    update_view(c,1,lambda f:f.pop("kombinationen_v1"))
    result=validate(a,b,c)
    assert result["status"].startswith("PASS_SCOPED")
    assert result["counts"]["closed_no_force_cards"]==1


def test_empty_closed_card_with_explicit_empty_bridge_passes():
    result=validate(*source())
    assert result["status"].startswith("PASS_SCOPED")


def test_invalid_view_object_blocks():
    blocked(lambda a,b,c:update_view(c,0,lambda f:f.update(kombinationen_v1=[])),
            "V486_BRIDGE_NOT_OBJECT")


def test_prior_details_stale_override_detected():
    def mutate(a,b,c):
        c[0]["details"]=json.dumps([{"title":"Kombinationen","items":["stale text"]}])
        c[1]["details"]="[]"
    blocked(mutate,"STALE_DETAILS_OVERRIDE_V486_BRIDGE",include_details=True)


def test_prior_details_same_exact_view_items_accepted():
    a,b,c=source()
    shown=bridge.expected_v486_visible(a["cards"][0]["kombinationen"])
    c[0]["details"]=json.dumps([{"title":"Kombinationen","items":shown}])
    c[1]["details"]="[]"
    assert validate(a,b,c,include_details=True)["status"].startswith("PASS_SCOPED")


def test_duplicate_preexisting_kombinationen_sections_detected():
    a,b,c=source()
    s={"title":"Kombinationen","items":["old"]}
    c[0]["details"]=json.dumps([s,s])
    c[1]["details"]="[]"
    result=validate(a,b,c,include_details=True)
    assert "MULTIPLE_PREEXISTING_COMBINATION_SECTIONS:case-1" in result["errors"]


def test_duplicate_legacy_collocation_category_detected():
    a,b,c=source()
    c[0]["details"]=json.dumps([{"title":"Kollokationen","items":["old"]}])
    c[1]["details"]="[]"
    result=validate(a,b,c,include_details=True)
    assert "DUPLICATE_VISIBLE_COLLLOCATION_FAMILY_RISK:case-1" in result["errors"]


def test_malformed_existing_details_fail_closed():
    a,b,c=source()
    c[0]["details"]="{broken"
    c[1]["details"]="[]"
    result=validate(a,b,c,include_details=True)
    assert "UNPARSEABLE_EXISTING_DETAILS_FOR_V486:case-1" in result["errors"]


@pytest.mark.parametrize("key,value",[
    ("runtime_sha256","0"*64),
    ("runtime_version","v999"),
    ("presentation_function","different"),
    ("tsv_parser_function","different"),
    ("stage5_tsv_sha256","0"*64),
    ("status","ACTIVE"),
])
def test_stale_runtime_or_attempted_promotion_blocks(key,value):
    a,b,c=source()
    result=validate(a,b,c,sidecar_patch={key:value})
    assert "EXACT_NONACTIVE_V486_PROFILE_OR_INPUT_NOT_PINNED" in result["errors"]


def test_changed_stage4_review_is_not_waved_through_by_correct_v486_view():
    a,b,c=source()
    b["risk_queue_open"]=1
    result=validate(a,b,c)
    assert "UNDERLYING_STAGE45_CONTENT_INTEGRITY_BLOCKED" in result["errors"]


def test_changed_full_source_item_translation_blocks_even_if_bridge_matches_previous():
    a,b,c=source()
    a["cards"][0]["kombinationen"][0]["fa"]="تغییر یافته"
    result=validate(a,b,c)
    assert "UNDERLYING_STAGE45_CONTENT_INTEGRITY_BLOCKED" in result["errors"]


def test_english_and_teaching_delta_preserved_only_as_metadata_not_visible_text():
    a,b,c=source()
    data=json.loads(c[0]["custom_fields"])
    raw=a["cards"][0]["kombinationen"]
    assert data["kombinationen_v1"]["items"]==raw
    assert bridge.expected_v486_visible(raw)==[
        "eine Entscheidung treffen — تصمیم گرفتن",
        "eine wichtige Entscheidung — تصمیم مهم"
    ]
    assert "make a decision" not in " ".join(bridge.expected_v486_visible(raw))
    assert "Learns the support verb" not in " ".join(bridge.expected_v486_visible(raw))
