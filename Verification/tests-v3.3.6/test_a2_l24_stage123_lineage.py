"""OP-02 synthetic-only adversarial checks; no user content in Git or CI."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import zipfile

MODULE = Path(__file__).resolve().parents[1] / "audit_a2_l24_stage123_lineage.py"
spec = importlib.util.spec_from_file_location("op02_actual_lineage", MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")


def synthetic():
    source = {"occurrence_id": "row-1", "locator": {"row": 1},
              "raw_text": "das Haus", "raw_definition_fa": "خانه",
              "raw_example_de": "Das Haus steht dort.",
              "source_row_payload_sha256": "a"*64, "media_refs": []}
    stub = {"id": "card-1", "source_row": 1, "source_hash": "a"*64,
            "source_occurrence_id": "row-1", "source_immutable_raw_learnable": "das Haus",
            "source_seed_fa": "خانه", "source_example_de": "Das Haus steht dort.",
            "source_audio_refs": []}
    edge = {"source_row": 1, "target_id": "card-1", "binding_kind": "NEW_TARGET",
            "source_hash": "a"*64, "source_occurrence_id": "row-1", "source_audio_tags": []}
    decision = {"source_row": 1, "source_hash": "a"*64,
                "source_text_unchanged": "das Haus",
                "source_fa_seed_unchanged": "خانه",
                "target_dispositions": [{"target_id": "card-1"}]}
    card = {"id": "card-1", "source_row": 1,
            "registered_source_hash": "a"*64,
            "registered_source_label_exact": "das Haus",
            "registered_source_fa_gloss_exact": "خانه",
            "registered_source_example_de_exact": "Das Haus steht dort.",
            "audio_file_references": [],
            "examples": [{"de": "Das Haus ist groß.", "fa": "خانه بزرگ است.",
                          "en": "The house is large.",
                          "provenance": "MODEL_EDITORIAL_AUTHORSHIP_NOT_SOURCE_VERBATIM"}]*4,
            "kombinationen": [{"de": "ein altes Haus", "fa": "خانه قدیمی",
                               "en": "an old house", "provenance": "CURATED_PEDAGOGICAL",
                               "teaching_delta": {"new_learner_value": "age adjective"}}]}
    values = {
        "source": {"occurrences": [source]},
        "stubs": [stub],
        "edges": [edge],
        "decisions": [decision],
        "reuse": [],
        "stage3": {"authored_targets": [copy.deepcopy(card)]},
        "stage4": {"authored_targets": [copy.deepcopy(card)]},
        "ledger": [{"target_id": "card-1", "dimension": "examples_de",
                    "status": "VERIFIED_PRESENT"}],
    }
    stage3_bytes = encode(values["stage3"])
    values["completeness"] = {
        "canonical_sha256": m.digest(encode(values["stubs"])),
        "targets": [{"id": "card-1", "source_ordinals": [1],
                     "dimensions": {"examples_de": {
                         "status": "VERIFIED_PRESENT",
                         "basis_refs": [{"path": m.FILES["stage3"],
                                         "artifact_sha256": m.digest(stage3_bytes)}]}}}],
        "summary": {"targets": 1, "dimension_cells": 1, "unresolved_cells": 0,
                    "status_counts": {"VERIFIED_PRESENT": 1},
                    "stage3c_editorial_sha256": m.digest(stage3_bytes)},
    }
    return values


def payload(values):
    return {m.FILES[label]: encode(values[label]) for label in m.FILES}


def report(values):
    return m.audit_payloads(payload(values), strict_legacy=False)


def archive_bytes(content):
    manifest = {"files": {name: {"sha256": m.digest(data), "bytes": len(data)}
                          for name, data in content.items()}}
    files = dict(content)
    files["MANIFEST.json"] = encode(manifest)
    files["SHA256SUMS"] = "".join(f"{m.digest(data)}  {name}\n"
                                for name, data in sorted(files.items())).encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    return buf.getvalue()


def test_synthetic_complete_source_and_proof_scoped_pass():
    a = report(synthetic())
    assert a["source_errors"] == []
    assert a["evidence_errors"] == []
    assert a["counts"]["canonical_targets"] == 1
    assert a["semantic_evidence_result"] == "PASS_RECORD_PROOF_ONLY"


def test_changed_raw_persian_is_source_error():
    v = synthetic()
    v["stage4"]["authored_targets"][0]["registered_source_fa_gloss_exact"] = "not original"
    assert any("Stage4" in e and "raw_fa" in e for e in report(v)["source_errors"])


def test_source_edge_relinked_is_source_error():
    v = synthetic()
    v["edges"][0]["source_occurrence_id"] = "row-99"
    assert any("source_occurrence_id" in e for e in report(v)["source_errors"])


def test_missing_target_decision_disposition_rejected():
    v = synthetic()
    v["decisions"][0]["target_dispositions"] = []
    assert any("decision/edge" in e for e in report(v)["source_errors"])


def test_duplicate_source_target_rejected():
    v = synthetic()
    v["stubs"].append(copy.deepcopy(v["stubs"][0]))
    assert any("duplicate/missing" in e for e in report(v)["source_errors"])


def test_stage4_dropped_card_rejected():
    v = synthetic()
    v["stage4"]["authored_targets"] = []
    assert any("Stage4 lost" in e for e in report(v)["source_errors"])


def test_stage3_ledger_missing_target_cell_rejected():
    v = synthetic()
    v["ledger"] = []
    assert any("ledger/completeness" in e for e in report(v)["source_errors"])


def test_stage3_inflated_dim_count_rejected():
    v = synthetic()
    v["completeness"]["summary"]["dimension_cells"] = 2
    assert any("completion counters" in e for e in report(v)["source_errors"])


def test_stage3_false_present_source_hash_rejected():
    v = synthetic()
    v["stubs"][0]["source_hash"] = "0" * 64
    assert any("canonical_hash" in e for e in report(v)["source_errors"])


def test_stale_stage3_editorial_reference_is_evidence_block():
    v = synthetic()
    v["completeness"]["targets"][0]["dimensions"]["examples_de"]["basis_refs"][0][
        "artifact_sha256"] = "0" * 64
    x = report(v)
    assert x["source_errors"] == []
    assert "STAGE3C_BASIS_REFS_NOT_BOUND_TO_ARCHIVED_BYTES" in x["evidence_errors"]


def test_stale_stage3_summary_sha_is_evidence_block():
    v = synthetic()
    v["completeness"]["summary"]["stage3c_editorial_sha256"] = "0" * 64
    assert "STAGE3C_SUMMARY_EDITORIAL_SHA_NOT_PRESENT_MEMBER" in report(v)["evidence_errors"]


def test_missing_teaching_delta_is_not_silent_pass():
    v = synthetic()
    v["stage4"]["authored_targets"][0]["kombinationen"][0].pop("teaching_delta")
    assert "COMBINATION_ITEM_LEVEL_TEACHING_DELTA_NOT_DOCUMENTED" in report(v)["evidence_errors"]


def test_missing_combo_provenance_is_not_silent_pass():
    v = synthetic()
    v["stage4"]["authored_targets"][0]["kombinationen"][0].pop("provenance")
    assert "COMBINATION_ITEM_LEVEL_PROVENANCE_ABSENT" in report(v)["evidence_errors"]


def test_reported_source_counts_do_not_replace_original_ids():
    v = synthetic()
    v["source"]["occurrences"].append(copy.deepcopy(v["source"]["occurrences"][0]))
    assert any("duplicate/missing" in e for e in report(v)["source_errors"])


def test_archive_manifests_and_crc_verified(tmp_path):
    p = tmp_path / "synthetic.zip"
    raw = archive_bytes(payload(synthetic()))
    p.write_bytes(raw)
    accepted = m.inspect_zip(p, m.digest(raw))
    assert len(accepted) == len(m.FILES) + 2
    assert report(synthetic())["source_identity_result"] == "PASS_SCOPED"


def test_archive_expected_sha_not_optional(tmp_path):
    p = tmp_path / "synthetic.zip"
    p.write_bytes(archive_bytes(payload(synthetic())))
    try:
        m.inspect_zip(p, "0"*64)
    except ValueError as exc:
        assert "ARCHIVE_SHA256_NOT_EXPECTED" in str(exc)
    else:
        raise AssertionError("unexpected archive authority acceptance")


def test_archive_manifest_tamper_rejected(tmp_path):
    content = payload(synthetic())
    raw = archive_bytes(content)
    p = tmp_path / "synthetic.zip"
    p.write_bytes(raw)
    altered = dict(content)
    altered[m.FILES["stubs"]] += b" "
    # Repackage with old manifest/sha: must not accept valid CRC alone.
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        originals = {name: z.read(name) for name in z.namelist()}
    originals[m.FILES["stubs"]] = altered[m.FILES["stubs"]]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, value in originals.items():
            z.writestr(name, value)
    p.write_bytes(buf.getvalue())
    try:
        m.inspect_zip(p, m.digest(p.read_bytes()))
    except ValueError as exc:
        assert "MANIFEST_SHA_OR_SIZE_DRIFT" in str(exc)
    else:
        raise AssertionError("manifest tamper not blocked")


def test_historical_163_target_count_is_explicit_not_synthetic_promotion():
    v = synthetic()
    a = m.audit_payloads(payload(v), strict_legacy=True)
    assert any("historical expected count drift" in e for e in a["source_errors"])
