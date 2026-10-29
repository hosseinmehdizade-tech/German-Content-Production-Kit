"""Synthetic-only mixed Canonical/import scope cases, no learner content writes."""
import csv
import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_wip50_mixed_canonical_import_scope import (
    HEADER, audit, full_unit_sha, sha256
)


def fixture():
    units = [
        {"id": "unit-g", "type": "grammatische_struktur",
         "headword": "Deklination", "examples": [{"de": "Der Mann"}]},
        {"id": "unit-v", "type": "verb", "headword": "helfen"},
        {"id": "unit-a", "type": "adjektiv", "headword": "freundlich"}
    ]
    canonical = json.dumps({"learning_units": units}, ensure_ascii=False,
                           separators=(",", ":")).encode("utf-8")
    out = io.StringIO(newline="")
    w = csv.writer(out, delimiter="\t", lineterminator="\n")
    w.writerow(HEADER)
    for uid, cat in (("unit-v", "Verb"), ("unit-a", "Adjektiv")):
        d = dict.fromkeys(HEADER, "")
        d.update({"id": uid, "card_type": "de-vocabulary", "category": cat})
        w.writerow([d[h] for h in HEADER])
    imported = out.getvalue().encode("utf-8")
    return [canonical, imported, sha256(canonical), sha256(imported)]


def call(f):
    return audit(*f)


def repin(f):
    f[2], f[3] = sha256(f[0]), sha256(f[1])
    return f


def test_realistic_mixed_scope_is_structural_only_not_stage4():
    result = call(fixture())
    assert result["status"] == "PASS_SCOPED_MIXED_ID_AND_BYTE_PARITY_ONLY", result
    assert result["canonical_units"] == 3 and result["lexical_units"] == 2
    assert result["nonlexical_grammar_units"] == 1 and result["import_cards"] == 2
    assert result["canonical_type_counts"] == {
        "adjektiv": 1, "grammatische_struktur": 1, "verb": 1}
    assert result["nonlexical_excluded_unit_proofs"][0]["canonical_unit_sha256"] == full_unit_sha(
        json.loads(fixture()[0])["learning_units"][0])
    assert result["stage4_semantic_pass"] is False
    assert result["issuer_authenticated"] is False
    assert result["production_authorized"] is False
    assert result["performed_writes"] is False


@pytest.mark.parametrize("index", [0, 1])
def test_byte_tamper_detected_without_repin(index):
    f = fixture()
    f[index] += b" "
    assert call(f)["status"] == "BLOCKED_INVALID_MIXED_SCOPE"


def test_mismatched_expected_external_pin_rejected():
    f = fixture()
    f[2] = "f" * 64
    assert "UNTRUSTED_OR_MISMATCHED_PIN:canonical" in call(f)["errors"]


def test_dropped_lexical_tsv_card_fails_despite_both_new_pins():
    f = fixture()
    s = f[1].decode("utf-8").splitlines()
    f[1] = ("\n".join(s[:-1]) + "\n").encode("utf-8")
    r = call(repin(f))
    assert "LEXICAL_ID_ORDER_OR_SET_DIFFERS_FROM_IMPORT" in r["errors"]


def test_grammar_card_smuggled_into_tsv_is_rejected():
    f = fixture()
    s = f[1].decode("utf-8").splitlines()
    s[1] = s[1].replace("unit-v", "unit-g")
    f[1] = ("\n".join(s) + "\n").encode("utf-8")
    r = call(repin(f))
    assert "IMPORT_REFERENCES_NONLEXICAL_OR_UNKNOWN_ID" in r["errors"]


def test_lexical_tsv_reordering_is_detected():
    f = fixture()
    s = f[1].decode("utf-8").splitlines()
    s[1], s[2] = s[2], s[1]
    f[1] = ("\n".join(s) + "\n").encode("utf-8")
    assert "LEXICAL_ID_ORDER_OR_SET_DIFFERS_FROM_IMPORT" in call(repin(f))["errors"]


def test_new_lexical_unit_without_tsv_card_cannot_pass():
    f = fixture()
    doc = json.loads(f[0])
    doc["learning_units"].append({"id": "unit-extra", "type": "verb"})
    f[0] = json.dumps(doc).encode("utf-8")
    assert "LEXICAL_ID_ORDER_OR_SET_DIFFERS_FROM_IMPORT" in call(repin(f))["errors"]


def test_unknown_nonlexical_type_is_blocked():
    f = fixture()
    doc = json.loads(f[0])
    doc["learning_units"][0]["type"] = "custom_other"
    f[0] = json.dumps(doc).encode("utf-8")
    assert any("UNKNOWN_OR_MISSING_CANONICAL_TYPE" in e for e in call(repin(f))["errors"])


def test_grammar_removed_from_full_canonical_is_blocked():
    f = fixture()
    doc = json.loads(f[0])
    doc["learning_units"].pop(0)
    f[0] = json.dumps(doc).encode("utf-8")
    assert "WIP50_EXPECTED_EXPLICIT_NONLEXICAL_UNIT_MISSING" in call(repin(f))["errors"]


def test_card_category_and_type_checked():
    f = fixture()
    s = f[1].decode("utf-8").splitlines()
    s[1] = s[1].replace("de-vocabulary", "de-grammar").replace("Verb", "Adjektiv")
    f[1] = ("\n".join(s) + "\n").encode("utf-8")
    r = call(repin(f))
    assert "NON_VOCABULARY_IMPORT_CARD" in r["errors"]
    assert "IMPORT_LEXICAL_CATEGORY_MISMATCH" in r["errors"]


def test_duplicate_json_keys_and_tsv_header_blocked():
    f = fixture()
    f[0] = b'{"learning_units":[],"learning_units":[]}'
    assert any("DUPLICATE_JSON_KEY" in e for e in call(repin(f))["errors"])
    f = fixture()
    f[1] = f[1].replace(b"typing_target", b"typing_wrong")
    assert any("WIP50_TSV_HEADER_MISMATCH" in e for e in call(repin(f))["errors"])


def test_duplicate_import_id_blocks():
    f = fixture()
    s = f[1].decode("utf-8").splitlines()
    s[2] = s[2].replace("unit-a", "unit-v")
    f[1] = ("\n".join(s) + "\n").encode("utf-8")
    assert "DUPLICATE_IMPORTED_LEXICAL_ID" in call(repin(f))["errors"]


def test_nonfinite_json_fails():
    f = fixture()
    f[0] = b'{"learning_units":[{"id":"unit-g","type":"grammatische_struktur","x":NaN}]}'
    assert any("NONFINITE_JSON" in e for e in call(repin(f))["errors"])
