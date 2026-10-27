"""Non-destructive packaging regressions for the active content builder."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Tools" / "build_clean_delivery.py"


def test_micro_batch_zip_is_refused_before_any_source_conversion(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    out = tmp_path / "Menschen-A2-WIP27.zip"
    result = subprocess.run([sys.executable, str(BUILDER), str(src), str(out)],
                            text=True, capture_output=True)
    assert result.returncode != 0
    assert "routine WIP/batch/micro-edit" in result.stderr
    assert not out.exists()


def test_immutable_archive_is_not_deleted_by_builder(tmp_path):
    src = tmp_path / "source"
    src.mkdir()
    out = tmp_path / "STAGE5-ORIGINAL.zip"
    out.write_bytes(b"protected historical bytes")
    result = subprocess.run([sys.executable, str(BUILDER), str(src), str(out)],
                            text=True, capture_output=True)
    assert result.returncode != 0
    assert out.read_bytes() == b"protected historical bytes"


def test_archive_index_guard_is_present():
    script = BUILDER.read_text(encoding="utf-8")
    assert 'identical content and QA already delivered' in script
    assert 'with zipfile.ZipFile(out,"x"' in script
    assert 'out.unlink()' not in script
