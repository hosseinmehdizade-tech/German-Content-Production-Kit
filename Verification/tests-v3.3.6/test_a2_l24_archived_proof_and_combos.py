"""Synthetic-only OP02 multi-archive provenance and didactic shadow QA."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "audit_a2_l24_archived_proof_and_combos.py"
spec = importlib.util.spec_from_file_location("a2_l24_proof_shadow", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def blob(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")


def fixture():
    old = {"authored_targets": [{
        "id": "ma2m-lu-synthetic", "source_row": 7,
        "registered_source_hash": "a"*64,
        "examples": [{"de": "Eine lange Fahrt ist schön.", "fa": "نمونه", "en": "Example"}],
        "kombinationen": [
            {"de": "eine lange Fahrt", "fa": "یک سفر طولانی", "en": "a long trip",
             "provenance": "MODEL_EDITORIAL_CANDIDATE"},
            {"de": "ein Ticket buchen", "fa": "رزرو", "en": "book a ticket",
             "provenance": "MODEL_EDITORIAL_CANDIDATE"},
        ],
    }]}
    new = copy.deepcopy(old)
    new["authored_targets"][0]["kombinationen"][1] = {
        "de": "ein gültiges Ticket", "fa": "بلیتی معتبر",
        "en": "a valid ticket", "provenance": "STAGE4_INTERNAL_EDITORIAL_REPAIR",
    }
    repairs = [{
        "id": "ma2m-lu-synthetic", "field": "kombinationen[1]",
        "reason": "distinct teaching example",
    }]
    stage3 = {m.REFERENCE_MEMBER: blob(old)}
    prior = {"old_work": b"unrelated"}
    refs = [{"path": m.REFERENCE_MEMBER, "artifact_sha256": m.sha(stage3[m.REFERENCE_MEMBER])}]
    completeness = {
        "summary": {"stage3c_editorial_sha256": m.sha(stage3[m.REFERENCE_MEMBER])},
        "targets": [{"dimensions": {"sense": {"basis_refs": refs}}}],
    }
    stage3[m.PROOF_MEMBER] = blob(completeness)
    stage4 = {**stage3, m.STAGE4_MEMBER: blob(new),
              m.STAGE4_REPAIR_LEDGER: blob(repairs)}
    return prior, stage3, stage4


def test_reference_found_exact_member():
    a,b,c = fixture()
    result = m.resolve_reference({"3C": b, "4": c},m.sha(b[m.REFERENCE_MEMBER]),m.REFERENCE_MEMBER)
    assert result["status"] == "RESOLVED_BY_EXACT_ARCHIVED_BYTES"
    assert len(result["matches"]) == 2


def test_reference_unresolved_does_not_autorepair():
    a,b,c = fixture()
    r = m.resolve_reference({"3B": a, "3C": b, "4": c}, "f"*64, m.REFERENCE_MEMBER)
    assert r["status"] == "UNRESOLVED_ACROSS_AVAILABLE_ARCHIVES"
    assert not r["matches"]
    assert r["not_a_content_error_proof"]


def test_reference_malformed_sha_rejected():
    with pytest.raises(ValueError, match="MALFORMED"):
        m.resolve_reference({}, "fake-sha", m.REFERENCE_MEMBER)


def test_combo_overlap_warning_is_not_pedagogical_verdict():
    _, b, c = fixture()
    r = m.audit(b, b, c)
    rows = r["combinations"]["crosswalk"]
    assert len(rows) == 2
    assert rows[0]["same_card_example_match"] == "COMPLETE_PHRASE_IN_EXAMPLE"
    assert rows[0]["pedagogical_adjudication"] == "NOT_INDEPENDENTLY_REVIEWED_IN_THIS_AUDIT"


def test_missing_delta_is_documented_without_deletion():
    _, b, c = fixture()
    r = m.audit(b,b,c)
    assert r["combinations"]["teaching_delta_documented_count"] == 0
    assert r["combinations"]["flag_counts"]["NO_ITEM_LEVEL_TEACHING_DELTA"] == 2
    assert r["combinations"]["stage4_combo_count"] == 2


def test_repaired_combination_is_matched_to_explicit_repair_ledger():
    _, b, c = fixture()
    r = m.audit(b,b,c)["combinations"]["crosswalk"]
    assert r[1]["changed_since_stage3c"] is True
    assert r[1]["matching_stage4_repair_record"] is True
    assert "UNTRACKED_STAGE4_ITEM_CHANGE" not in r[1]["risk_codes"]


def test_changed_combo_without_repair_record_flagged():
    _, b, c = fixture()
    c[m.STAGE4_REPAIR_LEDGER] = blob([])
    row = m.audit(b,b,c)["combinations"]["crosswalk"][1]
    assert "UNTRACKED_STAGE4_ITEM_CHANGE" in row["risk_codes"]


def test_missing_provenance_is_flag_not_an_invented_source():
    _, b, c = fixture()
    current = json.loads(c[m.STAGE4_MEMBER])
    current["authored_targets"][0]["kombinationen"][0].pop("provenance")
    c[m.STAGE4_MEMBER] = blob(current)
    r = m.audit(b,b,c)
    assert r["combinations"]["provenance_count"] == 1
    assert "MISSING_ITEM_PROVENANCE" in r["combinations"]["crosswalk"][0]["risk_codes"]


def test_duplicate_card_ids_rejected():
    _, b, c = fixture()
    cards = json.loads(c[m.STAGE4_MEMBER])
    cards["authored_targets"].append(copy.deepcopy(cards["authored_targets"][0]))
    c[m.STAGE4_MEMBER] = blob(cards)
    with pytest.raises(ValueError, match="CARD_ID_DRIFT"):
        m.audit(b,b,c)


def test_count_change_is_not_a_silent_pass():
    _, b, c = fixture()
    cards = json.loads(c[m.STAGE4_MEMBER])
    cards["authored_targets"][0]["kombinationen"].pop()
    c[m.STAGE4_MEMBER] = blob(cards)
    assert any("COUNT_CHANGED" in x for x in m.audit(b,b,c)["combinations"]["comparison_errors"])


def test_proof_claiming_absent_sha_is_not_resolved_by_same_member_path():
    _, b, c = fixture()
    d = json.loads(b[m.PROOF_MEMBER])
    d["summary"]["stage3c_editorial_sha256"] = "9"*64
    d["targets"][0]["dimensions"]["sense"]["basis_refs"][0]["artifact_sha256"] = "9"*64
    b[m.PROOF_MEMBER] = blob(d)
    c[m.PROOF_MEMBER] = b[m.PROOF_MEMBER]
    r = m.audit(b,b,c)
    assert r["reference_resolution"]["status"] == "UNRESOLVED_ACROSS_AVAILABLE_ARCHIVES"
    assert r["stage3c_basis_refs_not_matching_own_member"] == 1


def test_no_literal_card_text_serialized_in_crosswalk():
    _, b, c = fixture()
    result = m.audit(b,b,c)
    exported = json.dumps(result,ensure_ascii=False)
    assert "eine lange Fahrt" not in exported
    assert "ein gültiges Ticket" not in exported
    assert "ma2m-lu-synthetic" in exported


def test_snapshot_changes_in_archived_stage3c_are_detected():
    _, b, c = fixture()
    c[m.REFERENCE_MEMBER] = b"not original"
    r = m.audit(b,b,c)
    assert r["stage3c_member_hash_identical_in_stage4"] is False


def test_previously_verified_delta_provided_is_not_empty():
    _, b, c = fixture()
    new = json.loads(c[m.STAGE4_MEMBER])
    new["authored_targets"][0]["kombinationen"][0]["teaching_delta"] = {
        "new_learner_value": "case-specific contrast"
    }
    c[m.STAGE4_MEMBER] = blob(new)
    r = m.audit(b,b,c)
    assert r["combinations"]["teaching_delta_documented_count"] == 1
