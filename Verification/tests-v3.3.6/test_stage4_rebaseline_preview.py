"""OP-02 synthetic/no-write Stage4 reviewer worksheet rebaseline preview."""
import csv
import io
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from audit_stage4_current_worksheet_freshness import audit, FROZEN, REVIEW_FIELDS, sha256
from plan_stage4_worksheet_rebaseline import plan, FIELDS
from test_stage4_current_worksheet_freshness import fixture


def baseline(stale=True):
    canonical, old, unit = fixture()
    if stale:
        obj = json.loads(canonical)
        obj["learning_units"][0]["persian_meaning"] = "جواب دادن"
        canonical = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return canonical, old


def run(canonical, old, **kwargs):
    return plan(canonical, old,
                expected_canonical_sha256=kwargs.get("canonical_sha", sha256(canonical)),
                expected_worksheet_sha256=kwargs.get("worksheet_sha", sha256(old)),
                expected_units=kwargs.get("expected_units", 1))


def blocked(result, marker):
    assert result["status"] == "BLOCKED_REBASELINE_PREVIEW", result
    assert any(marker in e for e in result["errors"]), result
    assert result["preview_worksheet_sha256"] is None
    assert result["candidate_persisted"] is False
    assert result["stage4_semantic_pass"] is False
    assert result["production_authorized"] is False


def test_stale_one_unit_previews_exact_fresh_baseline_not_stage4():
    c, old = baseline()
    r, preview = run(c, old)
    assert r["status"] == "PASS_SCOPED_REBASELINE_PREVIEW_ONLY_NOT_STAGE4", r
    assert r["stale_affected_units"] == 1
    assert r["stale_fields"] == {"meaning_fa": 1}
    assert r["preview_worksheet_sha256"] == sha256(preview)
    assert audit(c, preview, expected_units=1)["status"] == "CURRENT_WORKSHEET_ONLY_STAGE4_REVIEW_NOT_CERTIFIED"
    assert r["proposed_reviewer_cells_populated"] == 0
    assert r["issuer_authenticated"] is False
    assert r["stage5_allowed"] is False
    assert r["candidate_persisted"] is False


def test_generated_preview_is_deterministic_for_same_exact_bytes():
    c, w = baseline()
    first, a = run(c, w)
    second, b = run(c, w)
    assert a == b and first == second


def test_no_change_is_not_claimed_as_new_rebaseline():
    c, w = baseline(stale=False)
    r, preview = run(c, w)
    assert r["status"] == "ALREADY_FRESH_PREVIEW_ONLY_NOT_STAGE4"
    assert r["stale_affected_units"] == 0
    assert preview is not None and r["stage4_semantic_pass"] is False


def test_raw_original_worksheet_bytes_remain_unchanged():
    c, old = baseline()
    snapshot = old[:]
    _, preview = run(c, old)
    assert old == snapshot
    assert preview != old


def test_existing_reviewer_decision_is_not_overwritten():
    c, old = baseline()
    rows = old.decode().splitlines()
    # Exact header and one row; insert review value through csv parser/writer.
    read = csv.DictReader(io.StringIO(old.decode()))
    raw = next(read)
    raw["expert_decision"] = "verified_keep"
    output = io.StringIO(newline="")
    w = csv.DictWriter(output, fieldnames=read.fieldnames)
    w.writeheader()
    w.writerow(raw)
    r, preview = run(c, output.getvalue().encode())
    blocked(r, "EXISTING_REVIEWER_CELLS_MUST_BE_PRESERVED")
    assert r["prior_reviewer_cells_populated"] == 1 and preview is None


@pytest.mark.parametrize("field", REVIEW_FIELDS[1:])
def test_even_nondecision_reviewer_evidence_is_never_dropped(field):
    c, old = baseline()
    read = csv.DictReader(io.StringIO(old.decode()))
    row = next(read)
    row[field] = "prior reviewer metadata"
    output = io.StringIO(newline="")
    w = csv.DictWriter(output, fieldnames=read.fieldnames)
    w.writeheader()
    w.writerow(row)
    r, _ = run(c, output.getvalue().encode())
    blocked(r, "EXISTING_REVIEWER_CELLS_MUST_BE_PRESERVED")


def test_forged_original_canonical_sha_is_rejected():
    c, old = baseline()
    r, _ = run(c, old, canonical_sha="f"*64)
    blocked(r, "CANONICAL_EXTERNAL_PIN_MISMATCH")


def test_forged_original_worksheet_sha_is_rejected():
    c, old = baseline()
    r, _ = run(c, old, worksheet_sha="f"*64)
    blocked(r, "WORKSHEET_EXTERNAL_PIN_MISMATCH")


def test_unsupported_additional_worksheet_column_not_silently_dropped():
    c, old = baseline()
    old = old.replace(b"expert_comments", b"other_review_col,expert_comments", 1)
    r, _ = run(c, old)
    blocked(r, "UNSUPPORTED_REVIEWER_WORKSHEET_COLUMNS")


def test_duplicate_canonical_json_key_rejected_even_if_rehashed():
    c, old = baseline()
    c = c.replace(b'"learning_units":', b'"learning_units":[],"learning_units":', 1)
    r, _ = run(c, old)
    blocked(r, "DUPLICATE_JSON_KEY")


def test_nonfinite_canonical_json_rejected():
    c, old = baseline()
    c = c.replace(b'"learning_units":', b'"other": NaN, "learning_units":', 1)
    r, _ = run(c, old)
    blocked(r, "INVALID_JSON_CONSTANT")


def test_canonical_duplicate_id_rejected():
    c, old = baseline()
    obj = json.loads(c)
    obj["learning_units"].append(obj["learning_units"][0])
    c = json.dumps(obj, ensure_ascii=False).encode()
    r, _ = run(c, old, expected_units=2)
    blocked(r, "INVALID_UNIQUE_UNIT_IDS")


def test_truncated_canonical_rejected():
    c, old = baseline()
    r, _ = run(c[:-2], old)
    blocked(r, "MALFORMED_INPUT")


def test_malformed_original_csv_rejected():
    c, old = baseline()
    old = old.replace(b"core_json,", b"core_json,core_json,", 1)
    r, _ = run(c, old)
    blocked(r, "UNSUPPORTED_REVIEWER_WORKSHEET_COLUMNS")


def test_original_row_count_mismatch_rejected():
    c, old = baseline()
    old = old + old.splitlines(True)[1]
    r, _ = run(c, old)
    blocked(r, "EXISTING_WORKSHEET_STRUCTURE_INVALID")


def test_original_frozen_json_is_not_ignored():
    c, old = baseline()
    old = old.replace(b'"haben"', b'BROKEN', 1)
    r, _ = run(c, old)
    blocked(r, "EXISTING_WORKSHEET_STRUCTURE_INVALID")


def test_formula_in_proposed_headword_rejected():
    c, old = baseline()
    doc = json.loads(c)
    doc["learning_units"][0]["headword"] = "=IMPORTXML(\"http://bad\", \"x\")"
    c = json.dumps(doc, ensure_ascii=False).encode()
    r, _ = run(c, old)
    blocked(r, "UNSAFE_SPREADSHEET_CELL:headword")


def test_formula_in_proposed_id_rejected():
    c, old = baseline()
    doc = json.loads(c)
    doc["learning_units"][0]["id"] = "+malicious"
    c = json.dumps(doc, ensure_ascii=False).encode()
    # Input audit also rejects the old ID mismatch: never make a positive claim.
    r, _ = run(c, old)
    assert r["status"] == "BLOCKED_REBASELINE_PREVIEW"
    assert r["stage4_semantic_pass"] is False


def test_non_string_frozen_fields_rejected():
    c, old = baseline()
    doc = json.loads(c)
    doc["learning_units"][0]["english_gloss"] = ["list instead of text"]
    c = json.dumps(doc, ensure_ascii=False).encode()
    r, _ = run(c, old)
    blocked(r, "NON_STRING_FROZEN_VALUE:gloss_en")


def test_source_book_locator_reprojection_matches_exact_new_canonical():
    c, old = baseline()
    doc = json.loads(c)
    doc["learning_units"][0]["provenance"]["sources"][0]["locator"] = "ahl-a1a2-p007-001 (PDF p.7)"
    c = json.dumps(doc, ensure_ascii=False).encode()
    r, preview = run(c, old)
    assert r["status"] == "PASS_SCOPED_REBASELINE_PREVIEW_ONLY_NOT_STAGE4", r
    assert r["stale_fields"] == {"meaning_fa":1,"source_book_locators_json":1}
    assert audit(c, preview, expected_units=1)["affected_units"] == 0


def test_invalid_expected_unit_count_fails_closed():
    c, old = baseline()
    r, _ = run(c, old, expected_units=0)
    blocked(r, "INVALID_EXPECTED_UNITS")


def test_unpinned_null_input_fails_closed():
    c, old = baseline()
    r, preview = plan(None, old,
                      expected_canonical_sha256=sha256(c),
                      expected_worksheet_sha256=sha256(old),
                      expected_units=1)
    blocked(r, "INVALID_OR_OVERSIZED_INPUT")
    assert preview is None


def test_reviewer_formula_already_present_is_not_transferred():
    c, old = baseline()
    reader = csv.DictReader(io.StringIO(old.decode()))
    row = next(reader)
    row["expert_comments"] = "=2+2"
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerow(row)
    r, _ = run(c, out.getvalue().encode())
    blocked(r, "EXISTING_WORKSHEET_STRUCTURE_INVALID")
