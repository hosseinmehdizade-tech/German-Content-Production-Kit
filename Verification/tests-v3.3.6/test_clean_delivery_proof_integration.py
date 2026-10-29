"""OP-01: real clean Stage5 builder opt-in edit-proof smoke/negative tests.

Only synthetic cards and isolated tmp_path outputs. No workstream input,
current lesson, remote Library, user data, or app/runtime is modified.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Tools" / "build_clean_delivery.py"
SCHEMA = "gcpk-applied-edit-bytes-proof@1"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tsv(back: str) -> bytes:
    custom = json.dumps({"presentation_contract": "gfp-vocabulary-neutral@1"}, ensure_ascii=False)
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter="\t", lineterminator="\n")
    writer.writerow(("id", "card_type", "category", "front", "back", "custom_fields"))
    writer.writerow(("c1", "de-vocabulary", "Verb", "sehen", back, custom))
    writer.writerow(("c2", "de-vocabulary", "Noun", "Haus", "خانه", custom))
    return buffer.getvalue().encode("utf-8")


def _setup(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    proof_dir = tmp_path / "local-proof"
    proof_dir.mkdir()
    old, current = _tsv("دیدن"), _tsv("مشاهده کردن")
    (source / "a-UNIVERSAL.tsv").write_bytes(current)
    (source / "canonical.json").write_text("{}\n", encoding="utf-8")
    (source / "source-output-map.tsv").write_text("source_row\tstatus\n1\tPASS\n", encoding="utf-8")
    (source / "verification.json").write_text('{"status":"PASS"}\n', encoding="utf-8")
    workstream = "synthetic-clean-delivery"
    artifact_id = "synthetic-CURRENT-001"
    receipt = {
        "schema": SCHEMA,
        "status": "APPLIED_SCOPED",
        "format": "TSV_ITEMS_V1",
        "workstream": workstream,
        "artifact_id": artifact_id,
        "id_column": "id",
        "applied_count": 1,
        "edits": [{"id": "c1", "fields": ["back"]}],
        "files": {
            "parent": "parent.tsv",
            "current": "current.tsv",
            "readback": "readback.tsv",
            "source_before": "source-before.bin",
            "source_after": "source-after.bin",
            "qa": "qa.json",
            "pointer": "pointer.json",
        },
        "sha256": {},
    }
    data = {
        "parent": old,
        "current": current,
        "readback": current,
        "source_before": b"untouched synthetic original",
        "source_after": b"untouched synthetic original",
        "qa": json.dumps({
            "result": "PASS",
            "test_suite": "synthetic-post-edit-qa",
            "assessed_sha256": _sha(current),
            "changed_ids": ["c1"],
        }).encode(),
        "pointer": json.dumps({
            "workstream": workstream,
            "artifact_id": artifact_id,
            "current_sha256": _sha(current),
        }).encode(),
    }
    for key, payload in data.items():
        (proof_dir / receipt["files"][key]).write_bytes(payload)
    receipt["sha256"] = {key: _sha(data[key]) for key in data if key != "pointer"}
    path = proof_dir / "proof.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False), encoding="utf-8")
    return source, path, receipt


def _run(source: Path, output: Path, proof: Path | None):
    args = [sys.executable, str(BUILDER), str(source), str(output)]
    if proof is not None:
        args += ["--applied-edit-proof", str(proof)]
    return subprocess.run(args, text=True, capture_output=True)


def test_valid_local_proof_binds_selected_direct_tsv_into_real_builder(tmp_path):
    source, proof, _ = _setup(tmp_path)
    output = tmp_path / "candidate.zip"
    result = _run(source, output, proof)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    with zipfile.ZipFile(output) as z:
        prefix = "CONTENT-DELIVERY/"
        manifest = json.loads(z.read(prefix + "DELIVERY-MANIFEST.json"))
        gate = manifest["optional_applied_edit_proof"]
        assert gate["status"] == "PASS_SCOPED_LOCAL_BYTE_PROOF_NOT_REMOTE_PERSISTENCE"
        assert gate["current_tsv_sha256"] == _sha((source / "a-UNIVERSAL.tsv").read_bytes())
        assert gate["remote_git_or_library_cas_verified"] is False
        assert gate["linguistic_stage4_certified"] is False
        assert z.read(prefix + "a-UNIVERSAL.tsv") == (source / "a-UNIVERSAL.tsv").read_bytes()


def test_legacy_builder_without_proof_remains_usable(tmp_path):
    source, _, _ = _setup(tmp_path)
    output = tmp_path / "candidate.zip"
    result = _run(source, output, None)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    with zipfile.ZipFile(output) as z:
        manifest = json.loads(z.read("CONTENT-DELIVERY/DELIVERY-MANIFEST.json"))
        assert manifest["optional_applied_edit_proof"] is None


def test_reject_report_only_claim_without_modified_current(tmp_path):
    source, proof, receipt = _setup(tmp_path)
    parent = (proof.parent / "parent.tsv").read_bytes()
    (proof.parent / "current.tsv").write_bytes(parent)
    (proof.parent / "readback.tsv").write_bytes(parent)
    (source / "a-UNIVERSAL.tsv").write_bytes(parent)
    receipt["sha256"]["current"] = _sha(parent)
    receipt["sha256"]["readback"] = _sha(parent)
    proof.write_text(json.dumps(receipt), encoding="utf-8")
    output = tmp_path / "candidate.zip"
    result = _run(source, output, proof)
    assert result.returncode != 0
    assert not output.exists()
    assert "report-only: CURRENT bytes unchanged" in result.stderr + result.stdout


def test_reject_changed_selected_tsv_after_proof_even_with_valid_local_receipt(tmp_path):
    source, proof, _ = _setup(tmp_path)
    (source / "a-UNIVERSAL.tsv").write_bytes(_tsv("دست‌کاری بعد از رسید"))
    output = tmp_path / "candidate.zip"
    result = _run(source, output, proof)
    assert result.returncode != 0 and not output.exists()
    assert "selected Stage5 TSV differs from verified CURRENT" in result.stderr + result.stdout


def test_reject_stale_qa_even_if_proof_hashes_match(tmp_path):
    source, proof, receipt = _setup(tmp_path)
    path = proof.parent / "qa.json"
    q = json.loads(path.read_text())
    q["assessed_sha256"] = "0" * 64
    path.write_text(json.dumps(q), encoding="utf-8")
    receipt["sha256"]["qa"] = _sha(path.read_bytes())
    proof.write_text(json.dumps(receipt), encoding="utf-8")
    output = tmp_path / "candidate.zip"
    result = _run(source, output, proof)
    assert result.returncode != 0 and not output.exists()
    assert "post-edit QA assessed wrong" in result.stderr + result.stdout


def test_reject_zip_proof_at_tsv_only_builder_boundary(tmp_path):
    source, proof, receipt = _setup(tmp_path)
    receipt["format"] = "ZIP_TSV_V1"
    proof.write_text(json.dumps(receipt), encoding="utf-8")
    output = tmp_path / "candidate.zip"
    result = _run(source, output, proof)
    assert result.returncode != 0 and not output.exists()
    assert "accepts TSV_ITEMS_V1 only" in result.stderr + result.stdout


def test_refuse_existing_archive_even_with_valid_proof(tmp_path):
    source, proof, _ = _setup(tmp_path)
    output = tmp_path / "candidate.zip"
    output.write_bytes(b"protected, not a ZIP")
    result = _run(source, output, proof)
    assert result.returncode != 0
    assert output.read_bytes() == b"protected"
