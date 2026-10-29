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
        "lexical_cards_total": 2, "facet_card_coverage": {x: 2 for x in m.FACETS},
        "source_lineage_receipt": "source:test:sha256-bound",
        "facets": facets, "unresolved_holds": 0,
    }
    s4 = {
        "reviewed_output_sha256": "b"*64,
        "independent_method": "ADVERSARIAL_METHOD_B",
        "review_kind": "AI_INDEPENDENT_ADVERSARIAL",
        "deterministic_coverage": "FULL",
        "semantic_scope": "WHOLE_DATASET_RISK_TARGETED_WITH_ADVERSARIAL_SAMPLING",
        "risk_queue_total": 2, "risk_queue_closed": 2, "risk_queue_open": 0,
        "deterministic_scanned_units": 2,
        "independent_semantic_challenge_units": 2,
        "adversarial_method_evidence": "second-pass:source-challenge:receipt",
        "source_challenge": True, "stage4_result": "PASS", "downstream_stage5_6_7_unmodified": True,
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


def test_incomplete_stage3_card_by_card_facet_is_blocked():
    a, b = sample_candidate()
    a["facet_card_coverage"]["examples"] = 1
    assert any("incomplete card coverage" in x for x in m.validate_candidate(a, b))


def test_stage4_review_receipt_cannot_hide_unscanned_cards():
    a, b = sample_candidate()
    b["deterministic_scanned_units"] = 1
    assert any("deterministic count" in x for x in m.validate_candidate(a, b))


def test_stage4_risk_queue_requires_exact_closed_count():
    a, b = sample_candidate()
    b["risk_queue_total"] = 5
    b["risk_queue_closed"] = 4
    assert any("risk queue needs exact" in x for x in m.validate_candidate(a, b))


def test_stage4_requires_nonempty_independent_semantic_challenge():
    a, b = sample_candidate()
    b["independent_semantic_challenge_units"] = 0
    b["adversarial_method_evidence"] = ""
    out = m.validate_candidate(a, b)
    assert any("independent semantic adversarial" in x for x in out)
    assert any("method evidence" in x for x in out)


# OP-01/OP-02: matrix must encode EVERY requires edge, never only a
# plausible-looking subset. All tests run in-memory; no content mutation.
def test_matrix_exactly_matches_fourteen_required_predecessors():
    matrix = m.load(m.BASE / m.MATRIX)
    expected = {(dep, c["id"]) for c in matrix["conflicts"] for dep in c["requires"]}
    assert len(matrix["conflicts"]) == 12
    assert len(expected) == 14
    assert set(tuple(edge) for edge in matrix["dependencies"]) == expected
    assert m.validate_dependency_edges(matrix) == []
    assert matrix["status"] == "PROPOSED_COMPATIBILITY_ONLY_NOT_ACTIVE"


def test_matrix_rejects_omitted_predecessor():
    matrix = m.load(m.BASE / m.MATRIX)
    matrix["dependencies"].remove(["C10", "C01"])
    assert any("graph omits required dependency" in x for x in m.validate_dependency_edges(matrix))


def test_matrix_rejects_undeclared_predecessor():
    matrix = m.load(m.BASE / m.MATRIX)
    matrix["dependencies"].append(["C04", "C12"])
    assert any("undeclared dependency edge" in x for x in m.validate_dependency_edges(matrix))


def test_matrix_rejects_repeated_predecessor():
    matrix = m.load(m.BASE / m.MATRIX)
    matrix["dependencies"].append(["C09", "C01"])
    assert any("duplicate dependency edge" in x for x in m.validate_dependency_edges(matrix))


def test_matrix_rejects_unknown_or_malformed_predecessor():
    matrix = m.load(m.BASE / m.MATRIX)
    matrix["dependencies"].extend([["C99", "C03"], ["C01"]])
    errors = m.validate_dependency_edges(matrix)
    assert any("unknown graph vertex" in x for x in errors)
    assert any("malformed dependency edge" in x for x in errors)


def test_matrix_rejects_requirements_added_without_graph_update():
    matrix = m.load(m.BASE / m.MATRIX)
    c04 = next(c for c in matrix["conflicts"] if c["id"] == "C04")
    c04["requires"].append("C07")
    assert any("C07->C04" in x for x in m.validate_dependency_edges(matrix))


def test_matrix_rejects_circular_self_requirement():
    matrix = m.load(m.BASE / m.MATRIX)
    c01 = next(c for c in matrix["conflicts"] if c["id"] == "C01")
    c01["requires"].append("C01")
    assert any("invalid required predecessor" in x for x in m.validate_dependency_edges(matrix))


def _precedence_pair():
    return m.load(m.BASE / m.MATRIX), m.load(m.BASE / m.PRECEDENCE)


def test_precedence_opt_in_only_and_currentness_guard():
    matrix, adoption = _precedence_pair()
    assert m.validate_precedence_adoption(matrix, adoption) == []
    assert adoption["status"] == "NONACTIVE_VERSIONED_OPT_IN"
    assert adoption["currentness_resolution"]["never_assume_version_from_draft"]
    assert len(adoption["applicability"]) == 10


def test_precedence_rejects_accidental_promotion():
    matrix, adoption = _precedence_pair()
    adoption["status"] = "ACTIVE"
    adoption["rollout_state"] = "PRODUCTION"
    assert any("promoted" in x for x in m.validate_precedence_adoption(matrix, adoption))


def test_precedence_rejects_unknown_or_missing_conflict():
    matrix, adoption = _precedence_pair()
    adoption["preserved_conflicts"].remove("C12")
    assert any("dropped" in x for x in m.validate_precedence_adoption(matrix, adoption))


def test_precedence_rejects_stage5_6_7_bypass_or_ui_change():
    matrix, adoption = _precedence_pair()
    adoption["compatibility"]["stage5_6_7"] = "OPTIONAL"
    adoption["compatibility"]["ui"] = "REDESIGN"
    assert any("weakens" in x for x in m.validate_precedence_adoption(matrix, adoption))


def test_precedence_rejects_stale_authority_default():
    matrix, adoption = _precedence_pair()
    adoption["currentness_resolution"]["never_assume_version_from_draft"] = False
    assert any("stale authority" in x for x in m.validate_precedence_adoption(matrix, adoption))


def test_precedence_rejects_incomplete_ten_stream_map():
    matrix, adoption = _precedence_pair()
    adoption["applicability"] = adoption["applicability"][:-1]
    assert any("ten scoped" in x for x in m.validate_precedence_adoption(matrix, adoption))


def test_precedence_rejects_unapproved_migration():
    matrix, adoption = _precedence_pair()
    adoption["promotion_requirements"] = ["Stage5/6/7 separate gates"]
    assert any("missing migration approval" in x for x in m.validate_precedence_adoption(matrix, adoption))


def test_precedence_rejects_mismatched_graph_edge_count():
    matrix, adoption = _precedence_pair()
    adoption["dependency_graph_integrity"]["edges"] = 9
    assert any("dependency counts" in x for x in m.validate_precedence_adoption(matrix, adoption))


def _stage56_receipts():
    prefix = "Architecture/Stage3-Stage4-Unification/"
    return tuple(m.load(m.BASE / (prefix + name)) for name in (
        "250-VERBEN-STAGE6-V486-R120-BOUNDARY-v1.7.json",
        "250-VERBEN-STAGE6-USER-CONFIRMED-v1.7-2026-10-29.json",
        "PHASE-2-3-4-READINESS-v0.1.json",
    ))


def test_stage56_exact_user_and_static_evidence_chain():
    a, b, c = _stage56_receipts()
    assert m.validate_stage56_evidence_chain(a, b, c) == []


def test_stage56_false_automated_pass_is_rejected():
    a, b, c = _stage56_receipts()
    b["acceptance"]["independent_browser_automation"] = "PASS"
    assert any("fabricate independent" in x for x in m.validate_stage56_evidence_chain(a, b, c))


def test_stage56_different_app_current_is_rejected():
    a, b, c = _stage56_receipts()
    b["target_identity"]["app_zip_sha256"] = "f" * 64
    assert any("different app CURRENT" in x for x in m.validate_stage56_evidence_chain(a, b, c))


def test_stage56_wrong_import_tsv_is_rejected():
    a, b, c = _stage56_receipts()
    b["target_identity"]["stage4_stage5_approved_content_tsv_sha256"] = "f" * 64
    assert any("dataset identity mismatch" in x for x in m.validate_stage56_evidence_chain(a, b, c))


def test_stage56_user_report_must_not_erase_old_browser_block():
    a, b, c = _stage56_receipts()
    a["real_stage6"]["overall"] = "PASS"
    assert any("automated PASS" in x for x in m.validate_stage56_evidence_chain(a, b, c))


def test_stage56_missing_user_check_rejected():
    a, b, c = _stage56_receipts()
    b["checked_behaviors"].pop()
    assert any("eight distinct user-reported" in x for x in m.validate_stage56_evidence_chain(a, b, c))


def test_stage7_private_does_not_imply_runtime_promotion():
    a, b, c = _stage56_receipts()
    c["overall"] = "STAGE6_USER_CONFIRMED_PASS__STAGE7_PRIVATE_SINGLE_ZIP_PASS"
    assert any("runtime promotion" in x for x in m.validate_stage56_evidence_chain(a, b, c))
