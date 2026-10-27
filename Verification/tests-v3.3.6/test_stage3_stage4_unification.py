"""Stage3/4 design compatibility dry-run tests. No content or stage promotion."""
import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "validate_stage3_stage4_unification.py"
spec = importlib.util.spec_from_file_location("stage34preflight", MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sample_candidate():
    facets = {x: {"decision": "DONE"} for x in m.FACETS}
    facets["combinations"] = {"decision": "DONE", "visible_items": 0,
                              "close": "CLOSED_NO_FORCE",
                              "reason": "No incremental teaching value"}
    s3 = {
        "input_sha256": "a"*64, "output_sha256": "b"*64,
        "source_authority": "source-exact:test", "stage3_method": "PRODUCTION_METHOD_A",
        "mutable_bytes_applied": True, "locked_source_mutated": False,
        "facets": facets, "unresolved_holds": 0,
    }
    s4 = {
        "reviewed_output_sha256": "b"*64,
        "independent_method": "ADVERSARIAL_METHOD_B",
        "review_kind": "AI_INDEPENDENT_ADVERSARIAL",
        "deterministic_coverage": "FULL",
        "semantic_scope": "WHOLE_DATASET_RISK_TARGETED_WITH_ADVERSARIAL_SAMPLING",
        "risk_queue_open": 0, "source_challenge": True,
        "stage4_result": "PASS", "downstream_stage5_6_7_unmodified": True,
    }
    return s3, s4


def test_versioned_matrix_and_actual_checkpoint_formats():
    assert m.validate_matrix(m.BASE) == []
    assert m.legacy_compatibility(m.BASE) == []


def test_compatible_complete_candidate_only_metadata():
    a, b = sample_candidate()
    assert m.validate_candidate(a, b) == []


def test_missing_any_stage3_facet_blocked():
    a, b = sample_candidate()
    del a["facets"]["relations"]
    assert any("nine facets" in x for x in m.validate_candidate(a, b))


def test_card_with_no_combinations_is_valid_if_explained():
    a, b = sample_candidate()
    assert m.validate_candidate(a, b) == []
    a["facets"]["combinations"]["reason"] = ""
    assert any("pedagogical reason" in x for x in m.validate_candidate(a, b))


def test_forced_combo_without_teaching_value_blocked():
    a, b = sample_candidate()
    a["facets"]["combinations"] = {"decision": "DONE", "visible_items": 5,
                                     "teaching_delta_verified": False}
    assert any("teaching_delta" in x for x in m.validate_candidate(a, b))


def test_unresolved_holds_and_unapplied_editorial_reports_blocked():
    a, b = sample_candidate()
    a["facets"]["sense"] = {"decision": "HELD"}
    a["unresolved_holds"] = 1
    a["mutable_bytes_applied"] = False
    out = m.validate_candidate(a, b)
    assert any("HOLD" in x for x in out)
    assert any("not applied" in x for x in out)


def test_stage4_is_stale_after_content_edit():
    a, b = sample_candidate()
    a["output_sha256"] = "c"*64
    assert any("stale" in x for x in m.validate_candidate(a, b))


def test_stage4_self_review_cannot_pass():
    a, b = sample_candidate()
    b["independent_method"] = a["stage3_method"]
    assert any("independently" in x for x in m.validate_candidate(a, b))


def test_stage4_partial_semantic_scope_cannot_pass():
    a, b = sample_candidate()
    b["semantic_scope"] = "SCOPED"
    b["deterministic_coverage"] = "SCOPED"
    out = m.validate_candidate(a, b)
    assert any("deterministic" in x for x in out)
    assert any("semantic" in x for x in out)


def test_stage4_risks_and_downstream_bypass_blocked():
    a, b = sample_candidate()
    b["risk_queue_open"] = 3
    b["downstream_stage5_6_7_unmodified"] = False
    out = m.validate_candidate(a, b)
    assert any("unresolved" in x for x in out)
    assert any("Stage5-7" in x for x in out)


def test_no_false_human_review_claim():
    a, b = sample_candidate()
    b["review_kind"] = "HUMAN_SIGNED"
    assert any("label AI" in x for x in m.validate_candidate(a, b))


def test_not_applicable_facet_requires_reason():
    a, b = sample_candidate()
    a["facets"]["morphosyntax"] = {"decision": "NA_WITH_REASON"}
    assert any("not-applicable" in x for x in m.validate_candidate(a, b))
