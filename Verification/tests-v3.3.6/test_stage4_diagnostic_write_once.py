"""Synthetic-only OP-02 CLI report safety: no overwrite of user/source/LOCKED bytes."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

HERE = Path(__file__).resolve().parent
VERIFY = HERE.parent
sys.path.insert(0, str(VERIFY))
from write_once_diagnostic import write_once_json_report, DiagnosticOutputBlocked
from test_stage4_current_worksheet_freshness import fixture


def sha(data):
    return hashlib.sha256(data).hexdigest()


def test_new_diagnostic_only_created_once(tmp_path):
    target = tmp_path / "report.json"
    raw = '{"stage4_semantic_pass": false}\n'
    write_once_json_report(target, raw)
    assert target.read_text(encoding="utf-8") == raw
    with pytest.raises(DiagnosticOutputBlocked, match="OUTPUT_EXISTS_NO_CLOBBER"):
        write_once_json_report(target, '{"status":"FORGED_FINAL"}')
    assert target.read_text(encoding="utf-8") == raw


@pytest.mark.parametrize("filename", [
    "LATEST.json", "CHECKPOINT.json", "PROJECT-STATE.json",
    "WRITER-SCOPES.json", "SOURCE-MANIFEST.json",
    "FINAL-VERIFICATION-STATUS.json", "report.csv", "report.tsv",
    "report.zip", "report.pdf",
])
def test_authority_names_and_nonjson_denied(tmp_path, filename):
    with pytest.raises(DiagnosticOutputBlocked, match="OUTPUT_MUST_BE_NEW_NONAUTHORITY_JSON"):
        write_once_json_report(tmp_path / filename, "{}")
    assert not (tmp_path / filename).exists()


@pytest.mark.parametrize("directory", [
    "Workspaces", "02-Source", "01-App", "LOCKED", "original",
    ".git", ".github", "Verification", "Optimization-Program",
])
def test_reject_protected_parent_even_if_new_report(tmp_path, directory):
    folder = tmp_path / directory
    folder.mkdir()
    target = folder / "preview.json"
    with pytest.raises(DiagnosticOutputBlocked, match="OUTPUT_IN_WORKSPACE_SOURCE_OR_LOCKED_PATH"):
        write_once_json_report(target, "{}")
    assert not target.exists()


def test_symlink_to_existing_authority_never_touched(tmp_path):
    authority = tmp_path / "existing.json"
    authority.write_bytes(b"ORIGINAL USER BYTES")
    link = tmp_path / "report.json"
    try:
        link.symlink_to(authority)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink permission not available on this platform")
    with pytest.raises(DiagnosticOutputBlocked, match="OUTPUT_SYMLINK_PATH_REFUSED"):
        write_once_json_report(link, "{}")
    assert authority.read_bytes() == b"ORIGINAL USER BYTES"


def test_symlink_parent_never_followed(tmp_path):
    protected = tmp_path / "protected"
    protected.mkdir()
    linkdir = tmp_path / "reports"
    try:
        linkdir.symlink_to(protected, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink permission not available on this platform")
    with pytest.raises(DiagnosticOutputBlocked, match="OUTPUT_SYMLINK_PATH_REFUSED"):
        write_once_json_report(linkdir / "new.json", "{}")
    assert not (protected / "new.json").exists()


def test_relative_parent_traversal_rejected(tmp_path):
    (tmp_path / "reports").mkdir()
    with pytest.raises(DiagnosticOutputBlocked, match="OUTPUT_PARENT_TRAVERSAL"):
        write_once_json_report(tmp_path / "reports" / ".." / "fake.json", "{}")
    assert not (tmp_path / "fake.json").exists()


def test_missing_parent_never_created(tmp_path):
    with pytest.raises(DiagnosticOutputBlocked, match="OUTPUT_PARENT_NOT_A_DIRECTORY"):
        write_once_json_report(tmp_path / "missing" / "evidence.json", "{}")


def test_preexisting_file_never_overwritten(tmp_path):
    target = tmp_path / "report.json"
    target.write_bytes(b"KEEP EXISTING")
    with pytest.raises(DiagnosticOutputBlocked, match="OUTPUT_EXISTS_NO_CLOBBER"):
        write_once_json_report(target, "REPLACE")
    assert target.read_bytes() == b"KEEP EXISTING"


def test_no_report_written_on_nonjson_output(tmp_path):
    with pytest.raises(DiagnosticOutputBlocked):
        write_once_json_report(tmp_path / "learner.csv", "INJECTED")
    assert list(tmp_path.iterdir()) == []


def command(script, *args, cwd):
    return subprocess.run([sys.executable, "-B", str(VERIFY / script), *map(str, args)],
                          cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=False)


def test_rebaseline_cli_writes_new_diagnostic_only_not_source(tmp_path):
    canonical, worksheet, _ = fixture()
    can = tmp_path / "input-canonical.json"
    old = tmp_path / "old-reviewer.csv"
    can.write_bytes(canonical)
    old.write_bytes(worksheet)
    report = tmp_path / "stage4-preview.json"
    cmd = [
        "--canonical", can, "--old-worksheet", old,
        "--expected-canonical-sha256", sha(canonical),
        "--expected-worksheet-sha256", sha(worksheet),
        "--expected-units", "1",
    ]
    first = command("plan_stage4_worksheet_rebaseline.py", *cmd,
                    "--report", report, cwd=tmp_path)
    assert first.returncode == 0, first.stdout + first.stderr
    result = json.loads(report.read_text(encoding="utf-8"))
    assert result["status"] == "ALREADY_FRESH_PREVIEW_ONLY_NOT_STAGE4"
    assert result["candidate_persisted"] is False
    evidence = report.read_bytes()
    second = command("plan_stage4_worksheet_rebaseline.py", *cmd,
                     "--report", report, cwd=tmp_path)
    assert second.returncode == 2
    assert "BLOCKED_DIAGNOSTIC_OUTPUT" in second.stdout
    assert report.read_bytes() == evidence
    assert can.read_bytes() == canonical and old.read_bytes() == worksheet


def test_rebaseline_cli_refuses_source_as_report(tmp_path):
    canonical, worksheet, _ = fixture()
    can = tmp_path / "canonical.json"
    old = tmp_path / "reviewer.csv"
    can.write_bytes(canonical)
    old.write_bytes(worksheet)
    cmd = ["--canonical", can, "--old-worksheet", old,
           "--expected-canonical-sha256", sha(canonical),
           "--expected-worksheet-sha256", sha(worksheet),
           "--expected-units", "1", "--report", can]
    p = command("plan_stage4_worksheet_rebaseline.py", *cmd, cwd=tmp_path)
    assert p.returncode == 2
    assert "BLOCKED_DIAGNOSTIC_OUTPUT" in p.stdout
    assert can.read_bytes() == canonical


def test_corrected_application_cli_does_not_replace_anchor(tmp_path):
    inputs = ["anchor", "before", "import_tsv", "worksheet",
              "source_a1_a2", "source_b1_c2", "receipt", "after", "readback"]
    arguments = []
    sources = {}
    for name in inputs:
        path = tmp_path / (name + ".json")
        content = b"{}" if name == "anchor" else b"synthetic malformed input"
        path.write_bytes(content)
        arguments.extend(["--" + name.replace("_", "-"), path])
        sources[name] = (path, content)
    args = [*arguments, "--expected-after-sha256", "f" * 64]
    dst = tmp_path / "corrected-report.json"
    first = command("verify_stage4_corrected_application.py", *args,
                    "--output", dst, cwd=tmp_path)
    assert first.returncode == 2  # expected invalid content, safe report creation
    assert dst.exists()
    initial = dst.read_bytes()
    assert json.loads(initial)["status"] == "BLOCKED_CORRECTED_APPLICATION_BYTES"
    second = command("verify_stage4_corrected_application.py", *args,
                     "--output", dst, cwd=tmp_path)
    assert second.returncode == 2
    assert "BLOCKED_DIAGNOSTIC_OUTPUT" in second.stdout
    assert dst.read_bytes() == initial
    assert all(path.read_bytes() == content for path, content in sources.values())


def test_freshness_zip_cli_never_overwrites_zip(tmp_path):
    canonical, worksheet, _ = fixture()
    src = tmp_path / "source.zip"
    with zipfile.ZipFile(src, "w") as archive:
        archive.writestr("02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json",
                         canonical)
        archive.writestr("05-QA-Tests/STAGE4-REVIEWER-WORKSHEET-CURRENT-UNSIGNED.csv",
                         worksheet)
    original = src.read_bytes()
    report = tmp_path / "freshness-report.json"
    args = ["--zip", src, "--expected-canonical-sha256", sha(canonical)]
    first = command("audit_stage4_current_worksheet_freshness.py", *args,
                    "--output", report, cwd=tmp_path)
    assert first.returncode == 2  # uses default 788, synthetic fixture has 1
    assert json.loads(report.read_text())["status"] == "BLOCKED_INVALID_REVIEW_SNAPSHOT"
    first_bytes = report.read_bytes()
    second = command("audit_stage4_current_worksheet_freshness.py", *args,
                     "--output", report, cwd=tmp_path)
    assert second.returncode == 2
    assert "BLOCKED_DIAGNOSTIC_OUTPUT" in second.stdout
    assert report.read_bytes() == first_bytes
    assert src.read_bytes() == original


def test_freshness_cli_reports_stdout_without_output_file(tmp_path):
    canonical, worksheet, _ = fixture()
    src = tmp_path / "source.zip"
    with zipfile.ZipFile(src, "w") as archive:
        archive.writestr("02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json",
                         canonical)
        archive.writestr("05-QA-Tests/STAGE4-REVIEWER-WORKSHEET-CURRENT-UNSIGNED.csv",
                         worksheet)
    p = command("audit_stage4_current_worksheet_freshness.py",
                "--zip", src, "--expected-canonical-sha256", sha(canonical),
                cwd=tmp_path)
    assert p.returncode == 2
    assert json.loads(p.stdout)["stage4_semantic_pass"] is False
    assert set(x.name for x in tmp_path.iterdir()) == {"source.zip"}
