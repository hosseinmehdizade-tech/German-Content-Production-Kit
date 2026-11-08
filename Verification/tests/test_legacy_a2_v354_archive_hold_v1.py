"""Ensure pre-current A2 v354 workflows cannot re-publish legacy content.

Workflow byte bodies are kept as exact historical reproducibility witnesses;
the only supported edits are one archive comment, contents:read and an
unconditionally skipped release job. New A2 work belongs to the current owner.
"""
from __future__ import annotations
import hashlib,sys,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ARCHIVE_HEADER=(
    "# Archived v354 workflow: source retained for reproducibility, execution disabled.\n"
    "# The current A2 owner is Workspaces/menschen-a2-24-lessons-v336.\n"
    "# To reactivate legacy release requires a dedicated, reviewed PR and source-exact Stage4+5+6+7.\n")
CONTRACT={
 ".github/workflows/menschen-a2-e2e.yml":{
    "job":"produce-verify-release",
    "old_blob":"83f97f0279354e3fb10efdac8d12bf785b0a8944"},
 ".github/workflows/menschen-a2-stage7-corrective.yml":{
    "job":"release-and-verify",
    "old_blob":"5674ff7316cdec935131a28800bebaf1ddcf9edc"}}
DEFUSE_LINE="    if: false  # Immutable historical v354 release; do not produce or push to main\n"

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()

def assert_defused(text,job,old_blob):
    if not text.startswith(ARCHIVE_HEADER):
        raise ValueError("ARCHIVAL_SCOPE_HEADER_MISSING")
    if "permissions:\n  contents: read\n" not in text:
        raise ValueError("LEGACY_WRITABLE_TOKEN_NOT_REMOVED")
    target="  "+job+":\n"+DEFUSE_LINE
    if text.count(target)!=1:
        raise ValueError("LEGACY_RELEASE_JOB_NOT_UNCONDITIONALLY_DISABLED")
    if text.count("  contents: write")!=0:
        raise ValueError("LEGACY_RELEASE_WRITE_PERMISSION_RETAINED")
    restored=text.removeprefix(ARCHIVE_HEADER).replace(target,"  "+job+":\n",1)
    restored=restored.replace("permissions:\n  contents: read\n",
                              "permissions:\n  contents: write\n",1)
    if git_blob(restored.encode("utf-8"))!=old_blob:
        raise ValueError("HISTORIC_WORKFLOW_WAS_ALTERED_BEYOND_DEFUSING")
    return True

class ArchivedLegacyA2WorkflowTests(unittest.TestCase):
    def test_both_v354_jobs_skip_and_history_is_exactly_preserved(self):
        for path,record in CONTRACT.items():
            with self.subTest(path=path):
                actual=(ROOT/path).read_text(encoding="utf-8").replace("\r\n","\n")
                self.assertTrue(assert_defused(actual,record["job"],record["old_blob"]))
    def test_unskipping_legacy_job_is_rejected(self):
        for path,record in CONTRACT.items():
            actual=(ROOT/path).read_text(encoding="utf-8").replace("\r\n","\n")
            with self.subTest(path=path), self.assertRaisesRegex(ValueError,"NOT_UNCONDITIONALLY_DISABLED"):
                assert_defused(actual.replace(DEFUSE_LINE,"",1),record["job"],record["old_blob"])
    def test_write_permission_reintroduction_rejected(self):
        for path,record in CONTRACT.items():
            actual=(ROOT/path).read_text(encoding="utf-8").replace("\r\n","\n")
            with self.subTest(path=path), self.assertRaisesRegex(ValueError,"WRITABLE_TOKEN_NOT_REMOVED"):
                assert_defused(actual.replace("  contents: read","  contents: write",1),record["job"],record["old_blob"])
    def test_new_legacy_republishing_step_rejected_even_while_job_skipped(self):
        for path,record in CONTRACT.items():
            actual=(ROOT/path).read_text(encoding="utf-8").replace("\r\n","\n")
            altered=actual.replace("    steps:\n","    steps:\n      - run: echo unsanctioned\n",1)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError,"HISTORIC_WORKFLOW_WAS_ALTERED"):
                assert_defused(altered,record["job"],record["old_blob"])

if __name__=="__main__":unittest.main()
