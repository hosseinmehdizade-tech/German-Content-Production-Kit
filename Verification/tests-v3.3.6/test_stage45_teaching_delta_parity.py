"""OP-02 Stage4→Stage5 typed didactic parity: synthetic-only negative QA."""
import copy
import csv
import importlib.util
import io
import json
from pathlib import Path

import pytest

FILE = Path(__file__).resolve().parents[1] / "validate_stage45_teaching_delta_parity.py"
spec = importlib.util.spec_from_file_location("op02_stage45", FILE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")


def import_tsv(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=["id", "front", "back", "card_type", "category", "custom_fields"],
        delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def card_item(item_id="i1"):
    return {"item_id": item_id, "de": "eine klare Entscheidung treffen",
            "fa": "تصمیم روشنی گرفتن", "en": "make a clear decision",
            "kind": "noun_verb", "provenance": "CURATED_PEDAGOGICAL",
            "teaching_delta": {"kind": "noun_verb", "reason": "Teaches a support-verb pattern"}}


def fixture():
    card = {"id": "synthetic-a", "category": "noun",
            "combination_disposition": "PRESENT", "kombinationen": [card_item()]}
    empty = {"id": "synthetic-b", "category": "verb",
             "combination_disposition": "CLOSED_NO_FORCE",
             "combination_close_reason": "No distinct learner benefit",
             "kombinationen": []}
    stage4 = {"source_authority_sha256": "d" * 64, "cards": [card, empty]}
    review = {
        "status": "PASS_AI_LINGUISTIC_QA_AND_TECHNICAL_GATES",
        "scope": "WHOLE_EXACT_STAGE4_CONTENT",
        "review_kind": "AI_INDEPENDENT_ADVERSARIAL",
        "reviewed_stage4_sha256": m.sha(encoded(stage4)),
        "source_authority_sha256": "d" * 64,
        "authoring_method": "SYNTHETIC_AUTHORING", "independent_method": "SYNTHETIC_SECOND_PASS",
        "adversarial_method_evidence": "synthetic fixture, never real linguistic QA",
        "risk_queue_open": 0, "deterministic_scanned_cards": 2,
        "item_dispositions": [
            {"card_id": "synthetic-a", "item_id": "i1",
             "disposition": "KEEP_WITH_REASON",
             "stage4_item_sha256": m.sha(m.canonical(card["kombinationen"][0])),
             "reason": "Synthetic justified pattern"}
        ],
    }
    rows = []
    for c in stage4["cards"]:
        rows.append({"id": c["id"], "front": "front", "back": "back",
                     "card_type": "de-vocabulary", "category": c["category"],
                     "custom_fields": json.dumps({
                         "presentation_contract": "gfp-vocabulary-neutral@1",
                         "kombinationen": copy.deepcopy(c["kombinationen"])
                     }, ensure_ascii=False)})
    return stage4, review, rows


def verify_fixture(stage4, review, rows, *, altered=None):
    b4, bq, b5 = encoded(stage4), encoded(review), import_tsv(rows)
    sidecar = {"schema": m.SCHEMA, "status": m.STATUS,
               "source_authority_sha256": "d" * 64,
               "stage4_sha256": m.sha(b4), "stage4_review_sha256": m.sha(bq),
               "stage5_tsv_sha256": m.sha(b5)}
    if altered:
        sidecar.update(altered)
    return m.verify(sidecar, b4, bq, b5)


def assert_rejected(mutation, error):
    a, b, c = fixture()
    mutation(a, b, c)
    result = verify_fixture(a, b, c)
    assert result["status"] == "BLOCKED", result
    assert any(error in e for e in result["errors"]), result


def change_projected_first(rows, edit):
    obj = json.loads(rows[0]["custom_fields"])
    edit(obj)
    rows[0]["custom_fields"] = json.dumps(obj, ensure_ascii=False)


def test_exact_parity_and_reasonable_zero_combinations():
    result = verify_fixture(*fixture())
    assert result["status"] == "PASS_SCOPED_DETERMINISTIC_PARITY_ONLY"
    assert result["counts"] == {"cards": 2, "items": 1, "closed_no_force": 1}
    assert "Stage6" in str(result["not_proven"])


def test_proposed_status_cannot_promote_active_writer():
    a, b, c = fixture()
    assert "NONACTIVE_CONTRACT_REQUIRED" in verify_fixture(
        a, b, c, altered={"status": "PRODUCTION_ACTIVE"})["errors"]


@pytest.mark.parametrize("field", ["stage4_sha256", "stage4_review_sha256", "stage5_tsv_sha256"])
def test_sidecar_wrong_exact_byte_digest_blocks(field):
    a, b, c = fixture()
    result = verify_fixture(a, b, c, altered={field: "0" * 64})
    assert "EXACT_INPUT_SHA_MISMATCH:" + field in result["errors"]


@pytest.mark.parametrize("field,value", [
    ("status", "PASS_SCOPED_AI_REVIEW"),
    ("scope", "SAMPLE_ONLY"),
    ("review_kind", "HUMAN_APPROVAL"),
    ("reviewed_stage4_sha256", "0" * 64),
    ("independent_method", "SYNTHETIC_AUTHORING"),
    ("adversarial_method_evidence", ""),
    ("risk_queue_open", 1),
    ("deterministic_scanned_cards", 1),
])
def test_stage4_scoped_or_stale_review_never_satisfies_full_gate(field, value):
    assert_rejected(lambda a, b, c: b.update({field: value}),
                    "STAGE4_INDEPENDENT_EXACT_REVIEW_RECEIPT_NOT_PROVEN")


def test_source_authority_mismatch():
    assert_rejected(lambda a, b, c: a.update(source_authority_sha256="a"*64),
                    "STAGE4_SOURCE_AUTHORITY_DRIFT")


@pytest.mark.parametrize("operation", [
    lambda c: c.pop(),
    lambda c: c.reverse(),
    lambda c: c.append(copy.deepcopy(c[0])),
])
def test_import_ids_exact_card_universe_and_order(operation):
    assert_rejected(lambda a, b, c: operation(c),
                    "STAGE4_STAGE5_CARD_ORDER_OR_ID_DRIFT")


@pytest.mark.parametrize("operation", [
    lambda f: f.update(kombinationen=[]),
    lambda f: f["kombinationen"][0].update(fa="ترجمه متفاوت"),
    lambda f: f["kombinationen"][0].pop("kind"),
    lambda f: f["kombinationen"][0].pop("provenance"),
    lambda f: f["kombinationen"][0].pop("teaching_delta"),
])
def test_stage5_cannot_drop_or_change_combo_content_or_metadata(operation):
    assert_rejected(lambda a, b, c: change_projected_first(c, operation),
                    "STAGE45_COMBINATION_OR_METADATA_DRIFT")


def test_zero_combinations_without_justification_rejected():
    assert_rejected(lambda a, b, c: a["cards"][1].update(combination_close_reason=""),
                    "EMPTY_COMBINATIONS_UNJUSTIFIED")


def test_zero_combinations_justified_without_quota_passes():
    a, b, c = fixture()
    a["cards"][0]["kombinationen"] = []
    a["cards"][0]["combination_disposition"] = "CLOSED_NO_FORCE"
    a["cards"][0]["combination_close_reason"] = "No nonredundant pattern"
    b["item_dispositions"] = []
    b["reviewed_stage4_sha256"] = m.sha(encoded(a))
    change_projected_first(c, lambda obj: obj.update(kombinationen=[]))
    assert verify_fixture(a, b, c)["status"].startswith("PASS_SCOPED")


@pytest.mark.parametrize("mutation", [
    lambda x: x.pop("teaching_delta"),
    lambda x: x["teaching_delta"].update(kind="unknown"),
    lambda x: x["teaching_delta"].update(reason=""),
])
def test_stage4_item_requires_concrete_delta_and_reason(mutation):
    assert_rejected(lambda a, b, c: mutation(a["cards"][0]["kombinationen"][0]),
                    "MISSING_OR_UNJUSTIFIED_TEACHING_DELTA")


def test_stage4_item_review_hash_frozen():
    assert_rejected(lambda a, b, c: b["item_dispositions"][0].update(
        stage4_item_sha256="0"*64), "MISSING_OR_STALE_ITEM_LEVEL_STAGE4_REVIEW")


def test_stage4_unreviewed_item_stays_blocked():
    assert_rejected(lambda a, b, c: b.update(item_dispositions=[]),
                    "STAGE4_REVIEW_ITEM_UNIVERSE_MISMATCH")


def test_stage4_ghost_review_stays_blocked():
    assert_rejected(lambda a, b, c: b["item_dispositions"].append(
        {"card_id": "ghost", "item_id": "phantom", "disposition": "KEEP_WITH_REASON",
         "stage4_item_sha256": "a"*64, "reason": "fake"}),
        "STAGE4_REVIEW_ITEM_UNIVERSE_MISMATCH")


def test_duplicate_stage4_item_id_rejected():
    assert_rejected(lambda a, b, c: a["cards"][0]["kombinationen"].append(
        copy.deepcopy(a["cards"][0]["kombinationen"][0])),
        "DUPLICATE_STAGE4_COMBINATION_ID")


def test_generated_example_cannot_claim_source_authority():
    assert_rejected(lambda a, b, c: a["cards"][0]["kombinationen"][0].update(
        provenance="PARENT_GENERATED_EXAMPLE", source_ref={"source_id":"fake"}),
        "GENERATED_EXAMPLE_FALSE_SOURCE_CLAIM")


def test_registered_source_without_locator_rejected():
    assert_rejected(lambda a, b, c: a["cards"][0]["kombinationen"][0].update(
        provenance="REGISTERED_SOURCE"), "SOURCE_PROVENANCE_WITHOUT_EXACT_LOCATOR")


def test_unrecognized_provenance_rejected():
    assert_rejected(lambda a, b, c: a["cards"][0]["kombinationen"][0].update(
        provenance="HUMAN_CERTIFIED"), "MISSING_OR_UNRECOGNIZED_PROVENANCE")


def test_neutral_vocabulary_card_envelope_required():
    assert_rejected(lambda a, b, c: c[0].update(card_type="special-vocabulary-ui"),
                    "NON_NEUTRAL_ENVELOPE_OR_CATEGORY_DRIFT")


def test_neutral_presentation_contract_required():
    assert_rejected(lambda a, b, c: change_projected_first(
        c, lambda f: f.update(presentation_contract="custom-different-ui")),
        "NON_NEUTRAL_PRESENTATION_CONTRACT")


def test_malformed_json_is_fail_closed():
    assert_rejected(lambda a, b, c: c[0].update(custom_fields="{invalid"),
                    "INVALID_STAGE5_CUSTOM_FIELDS")


def test_duplicate_json_keys_fail_closed():
    a, b, c = fixture()
    c[0]["custom_fields"] = c[0]["custom_fields"].replace(
        '"presentation_contract":', '"presentation_contract": "untrusted", "presentation_contract":', 1)
    assert any("INVALID_STAGE5_CUSTOM_FIELDS" in e for e in verify_fixture(a,b,c)["errors"])
    with pytest.raises(ValueError, match="DUPLICATE_JSON_OBJECT_KEY"):
        m.read_json(c[0]["custom_fields"].encode("utf-8"))


def test_stage4_empty_card_cannot_appear_with_unrequested_combo():
    a, b, c = fixture()
    c[1]["custom_fields"] = json.dumps({"presentation_contract": "gfp-vocabulary-neutral@1",
                                         "kombinationen":[card_item("invented")]})
    assert any("STAGE45_COMBINATION_OR_METADATA_DRIFT" in e
               for e in verify_fixture(a,b,c)["errors"])


def test_unhashable_card_id_fails_closed():
    a,b,c = fixture()
    a["cards"][0]["id"] = ["not-a-valid-id"]
    assert "STAGE4_DUPLICATE_OR_MISSING_CARD" in verify_fixture(a,b,c)["errors"]


def test_unhashable_provenance_fails_closed():
    a,b,c = fixture()
    a["cards"][0]["kombinationen"][0]["provenance"] = {"fake": "source"}
    assert "MISSING_OR_UNRECOGNIZED_PROVENANCE" in verify_fixture(a,b,c)["errors"]


def test_unhashable_delta_kind_fails_closed():
    a,b,c = fixture()
    a["cards"][0]["kombinationen"][0]["teaching_delta"]["kind"] = ["noun_verb"]
    assert "MISSING_OR_UNJUSTIFIED_TEACHING_DELTA" in verify_fixture(a,b,c)["errors"]


def test_review_receipt_without_real_independent_method_evidence_rejected():
    a,b,c = fixture()
    b["adversarial_method_evidence"] = ""
    assert "STAGE4_INDEPENDENT_EXACT_REVIEW_RECEIPT_NOT_PROVEN" in verify_fixture(a,b,c)["errors"]
