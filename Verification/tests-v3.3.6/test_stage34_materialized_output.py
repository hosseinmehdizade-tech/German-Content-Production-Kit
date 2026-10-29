"""OP-01: materialized raw byte and unit identity proof, synthetic only."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DIR))
from verify_stage34_materialized_output import digest, unit_digest, verify

spec = importlib.util.spec_from_file_location(
    "stage34_test_fixture",
    DIR / "tests-v3.3.6" / "test_stage3_stage4_unification.py")
fixture_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_mod)


def fixture():
    s3, s4 = fixture_mod.sample_candidate()
    units = [
        {"id": "unit-1", "headword": "antworten", "meaning_fa": "پاسخ دادن",
         "examples": [{"de": "Ich antworte dir.", "en": "I answer you."}]},
        {"id": "unit-2", "headword": "helfen", "meaning_fa": "کمک کردن",
         "examples": [{"de": "Ich helfe dir.", "en": "I help you."}]},
    ]
    raw = json.dumps(
        {"learning_units": units, "source": "synthetic test only"},
        ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    pins = {u["id"]: unit_digest(u) for u in units}
    s3["unit_sha256_by_id"] = pins
    s3["output_sha256"] = digest(raw)
    s4["reviewed_output_sha256"] = digest(raw)
    for row in s4["unit_dispositions"]:
        row["unit_sha256"] = pins[row["unit_id"]]
    return s3, s4, raw, digest(raw)


def check(f):
    return verify(*f)


def test_actual_bytes_and_each_unit_sha_structurally_match_not_stage4():
    r = check(fixture())
    assert r["status"] == "PASS_SCOPED_OUTPUT_BYTES_UNIT_IDENTITY_ONLY", r
    assert r["materialized_units"] == 2
    assert r["stage4_semantic_pass"] is False
    assert r["issuer_authenticated"] is False
    assert r["production_authorized"] is False


def test_harmonized_false_metadata_pins_do_not_prove_raw_bytes():
    f = list(fixture())
    f[0]["unit_sha256_by_id"]["unit-1"] = "f"*64
    f[1]["unit_dispositions"][0]["unit_sha256"] = "f"*64
    # Prior metadata check sees the same fake unit hash in both reports.
    assert fixture_mod.m.validate_candidate(f[0], f[1]) == []
    r = check(f)
    assert "DECLARED_PER_UNIT_DIGESTS_DO_NOT_MATCH_MATERIALIZED_OUTPUT" in r["errors"]


@pytest.mark.parametrize("which", ["raw", "stage3_file", "stage4_file", "external"])
def test_single_byte_or_one_whole_file_pin_change_blocks(which):
    f = list(fixture())
    if which == "raw":
        f[2] += b" "
    elif which == "stage3_file":
        f[0]["output_sha256"] = "f"*64
    elif which == "stage4_file":
        f[1]["reviewed_output_sha256"] = "f"*64
    else:
        f[3] = "f"*64
    assert check(f)["status"] == "BLOCKED_UNBOUND_OUTPUT"


def test_missing_external_independently_pinned_hash_blocks():
    f = list(fixture())
    f[3] = ""
    assert "INDEPENDENT_EXTERNAL_OUTPUT_PIN_MISSING_OR_INVALID" in check(f)["errors"]


def test_real_unit_mutated_and_reviewer_hash_stale_blocks_even_with_new_file_hash():
    f = list(fixture())
    doc = json.loads(f[2])
    doc["learning_units"][0]["meaning_fa"] = "جواب دادن"
    f[2] = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    f[3] = digest(f[2])
    f[0]["output_sha256"] = f[3]
    f[1]["reviewed_output_sha256"] = f[3]
    r = check(f)
    assert "DECLARED_PER_UNIT_DIGESTS_DO_NOT_MATCH_MATERIALIZED_OUTPUT" in r["errors"]
    assert any(e.startswith("REVIEW_SHA_DIFFERS_FROM_REAL_UNIT_BYTES:") for e in r["errors"])


def test_duplicate_unit_ids_rejected_from_actual_bytes():
    f = list(fixture())
    doc = json.loads(f[2])
    doc["learning_units"][1]["id"] = "unit-1"
    f[2] = json.dumps(doc, ensure_ascii=False).encode("utf-8")
    f[3] = digest(f[2])
    assert any("DUPLICATE_UNIT_ID" in e for e in check(f)["errors"])


def test_hidden_extra_unit_not_counted_as_two():
    f = list(fixture())
    doc = json.loads(f[2])
    doc["learning_units"].append({"id": "unit-3", "meaning_fa": "دیگر"})
    f[2] = json.dumps(doc, ensure_ascii=False).encode("utf-8")
    f[3] = digest(f[2])
    r = check(f)
    assert r["materialized_units"] == 3
    assert "STAGE3_DECLARED_COUNT_DIFFERS_FROM_REAL_OUTPUT" in r["errors"]
    assert "DECLARED_PER_UNIT_DIGESTS_DO_NOT_MATCH_MATERIALIZED_OUTPUT" in r["errors"]


def test_duplicate_json_keys_and_nan_fail_closed():
    f = list(fixture())
    for body in (b'{"learning_units":[],"learning_units":[]}',
                 b'{"learning_units":[{"id":"unit-1","score":NaN}]}'):
        g = [copy.deepcopy(f[0]), copy.deepcopy(f[1]), body, digest(body)]
        assert any("UNREADABLE_MATERIALIZED_OUTPUT" in e for e in check(g)["errors"])


def test_unsupported_snapshot_format_fails_closed():
    f = list(fixture())
    f[2] = b'{"cards":[{"id":"unit-1"}]}'
    f[3] = digest(f[2])
    assert any("UNSUPPORTED_OUTPUT_SCHEMA" in e for e in check(f)["errors"])


def test_incomplete_or_malformed_review_metadata_blocks_despite_raw_digest():
    f = list(fixture())
    f[1]["unit_dispositions"].pop()
    assert check(f)["status"] == "BLOCKED_UNBOUND_OUTPUT"
    f = list(fixture())
    f[1]["unit_dispositions"][0]["unit_sha256"] = None
    assert any("REVIEW_SHA_DIFFERS_FROM_REAL_UNIT_BYTES" in e for e in check(f)["errors"])


def test_arbitrary_caller_selected_matching_pin_is_not_issuer_authentication():
    r = check(fixture())
    assert r["source_fidelity_verified"] is False
    assert r["issuer_authenticated"] is False
    assert "Caller must authenticate" in r["note"]
