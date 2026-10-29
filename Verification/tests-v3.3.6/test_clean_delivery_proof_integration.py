"""OP-01: real clean Stage5 builder opt-in edit-proof smoke/negative tests.

Only synthetic cards and isolated tmp_path outputs. No workstream input,
current lesson, remote Library, user data, or app/runtime is modified.
"""
from __future__ import annotations

import csv
import hashlib
import io
import os
import json
import subprocess
import sys
import pytest
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
    assert output.read_bytes() == b"protected, not a ZIP"


@pytest.mark.parametrize("role,second_name,copy_name", [
    ("direct-import-tsv", "second-IMPORT.tsv", "a-UNIVERSAL.tsv"),
    ("direct-import-tsv", "second-Cards.tsv", "a-UNIVERSAL.tsv"),
    ("canonical-json", "second-canonical.json", "canonical.json"),
    ("source-output-map-tsv", "backup-source-output-map.tsv", "source-output-map.tsv"),
    ("qa-report", "second-QA.json", "verification.json"),
])
def test_active_builder_rejects_ambiguous_role_before_writing(
        tmp_path, role, second_name, copy_name):
    source, _, _ = _setup(tmp_path)
    (source / second_name).write_bytes((source / copy_name).read_bytes())
    output = tmp_path / "candidate.zip"
    result = _run(source, output, None)
    assert result.returncode != 0
    assert f"ambiguous required delivery role: {role}" in result.stderr + result.stdout
    assert not output.exists()


def test_active_builder_rejects_one_file_for_two_roles(tmp_path):
    source, _, _ = _setup(tmp_path)
    (source / "canonical.json").unlink()
    (source / "verification.json").unlink()
    (source / "canonical-QA.json").write_text("{}\\n", encoding="utf-8")
    output = tmp_path / "candidate.zip"
    result = _run(source, output, None)
    assert result.returncode != 0
    assert "role file reused for multiple roles" in result.stderr + result.stdout
    assert not output.exists()


def test_active_builder_rejects_matching_symlink_without_packaging(tmp_path):
    source, _, _ = _setup(tmp_path)
    (source / "canonical.json").unlink()
    link = source / "canonical-link.json"
    try:
        link.symlink_to(source / "verification.json")
    except (OSError, NotImplementedError):
        pytest.skip("this runner does not permit test symlinks")
    output = tmp_path / "candidate.zip"
    result = _run(source, output, None)
    assert result.returncode != 0
    assert "unsafe required delivery role candidate: canonical-json" in result.stderr + result.stdout
    assert not output.exists()


def _run_with_tamper_hook(source, output, tmp_path, hook):
    """Launch the REAL active builder with a synthetic in-process race hook.

    The hook lives only in this pytest temp directory. No learner file,
    original source or checked-in production tool is modified by the test.
    """
    hooks = tmp_path / "hook-dir"
    hooks.mkdir()
    (hooks / "sitecustomize.py").write_text(hook, encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(hooks) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, str(BUILDER), str(source), str(output)],
        text=True, capture_output=True, env=env, timeout=90,
    )


@pytest.mark.parametrize("target", ["after_original_validator", "during_copy_source",
                                     "during_copy_stage", "before_staged_validation"])
def test_stage5_midprocess_source_or_copy_tamper_blocks(tmp_path, target):
    source, _, _ = _setup(tmp_path)
    output = tmp_path / "candidate.zip"

    if target == "after_original_validator":
        hook = """
import subprocess
from pathlib import Path
_orig = subprocess.run
def _tamper(*args, **kwargs):
    command = args[0] if args else kwargs.get("args", [])
    result = _orig(*args, **kwargs)
    if (isinstance(command, (list, tuple))
            and any("validate_unified_vocabulary_projection_v1_1_0.py" in str(x)
                    for x in command)
            and Path(command[-1]).parent.name != "CONTENT-DELIVERY"):
        candidate = Path(command[-1])
        candidate.write_bytes(candidate.read_bytes() + b"\\n")
    return result
subprocess.run = _tamper
"""
    elif target in {"during_copy_source", "during_copy_stage"}:
        hook = """
import shutil
from pathlib import Path
_orig = shutil.copy2
def _tamper(src, dst, *args, **kwargs):
    if Path(src).name == "canonical.json":
        if MODE == "during_copy_source":
            p = Path(src)
            p.write_bytes(p.read_bytes() + b"\\n")
        result = _orig(src, dst, *args, **kwargs)
        if MODE == "during_copy_stage":
            p = Path(dst)
            p.write_bytes(p.read_bytes() + b"\\n")
        return result
    return _orig(src, dst, *args, **kwargs)
MODE = """ + repr(target) + """
shutil.copy2 = _tamper
"""
    else:
        hook = """
import subprocess
from pathlib import Path
_orig = subprocess.run
def _tamper(*args, **kwargs):
    command = args[0] if args else kwargs.get("args", [])
    if (isinstance(command, (list, tuple))
            and any("validate_unified_vocabulary_projection_v1_1_0.py" in str(x)
                    for x in command)
            and Path(command[-1]).parent.name == "CONTENT-DELIVERY"):
        candidate = Path(command[-1])
        payload = candidate.read_bytes().replace(b"de-vocabulary", b"de-not-valid")
        candidate.write_bytes(payload)
    return _orig(*args, **kwargs)
subprocess.run = _tamper
"""
    result = _run_with_tamper_hook(source, output, tmp_path, hook)
    assert result.returncode != 0, result.stdout + result.stderr
    assert not output.exists()
    combined = result.stderr + result.stdout
    assert ("Stage5 selected input changed" in combined
            or "Stage5 staged direct import failed" in combined)


def test_stage5_manifest_copy_equals_original_when_no_race(tmp_path):
    source, _, _ = _setup(tmp_path)
    output = tmp_path / "candidate.zip"
    run = _run(source, output, None)
    assert run.returncode == 0, run.stdout + run.stderr
    with zipfile.ZipFile(output) as archive:
        for filename in ("a-UNIVERSAL.tsv", "canonical.json",
                         "source-output-map.tsv", "verification.json"):
            assert archive.read("CONTENT-DELIVERY/" + filename) == (
                source / filename).read_bytes()
