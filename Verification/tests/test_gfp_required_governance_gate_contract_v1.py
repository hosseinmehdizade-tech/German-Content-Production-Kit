"""Stable required CI job contract; no source content, ZIP or release writes."""
from __future__ import annotations
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/gfp-required-governance-gate.yml"

REQUIRED_COMMANDS = (
    "Verification/audit_global_policy_sync_v1.py --check",
    "Verification/check_new_lexical_stage5_claims_v1.py --base",
    "Verification/check_new_lexical_producer_bypass_v1.py --base",
    "Verification/tests-v3.3.6/test_content_zip_guard.py",
    "Tools/validate_canonical_family_workspaces_v1.py --repo-root",
    "Tools/discover_parallel_accepted_sources_v1.py --repo-root",
)
EXPECTED_JOB = "GFP-Required-Governance-Gate"

def problems(source: str) -> list[str]:
    errors: list[str] = []
    if not re.search(r"(?m)^on:\s*$", source):
        errors.append("NO_EVENT_DECLARATION")
    if not re.search(r"(?m)^  pull_request:\s*$", source):
        errors.append("NOT_ON_EVERY_PR")
    if not re.search(r"(?m)^  push:\s*$", source):
        errors.append("NOT_ON_MAIN_PUSH")
    if not re.search(r"(?m)^    branches: \[main\]\s*$", source):
        errors.append("NO_MAIN_TARGET")
    if re.search(r"(?m)^\s+(?:paths|paths-ignore):", source):
        errors.append("PATH_FILTER_CAN_LEAVE_REQUIRED_CHECK_PENDING")
    if "workflow_dispatch:" in source or "pull_request_target:" in source:
        errors.append("UNSAFE_OR_UNRELATED_TRIGGER")
    if not re.search(r"(?m)^    name: GFP-Required-Governance-Gate\s*$", source):
        errors.append("REQUIRED_CHECK_CONTEXT_CHANGED")
    if not re.search(r"(?m)^permissions:\s*\n  contents: read\s*$", source):
        errors.append("NOT_READ_ONLY_TOKEN")
    if "fetch-depth: 0" not in source or "persist-credentials: false" not in source:
        errors.append("EXACT_BASE_OR_TOKEN_HARDENING_MISSING")
    if "github.event.pull_request.base.sha" not in source or "github.event.before" not in source:
        errors.append("FULL_COMPARISON_RANGE_MISSING")
    if ('BASE="${PARENTS[1]}"' not in source or '"${PARENTS[2]}" != "$PR_HEAD"' not in source
            or 'git merge-base --is-ancestor "$PR_BASE" "$BASE"' not in source):
        errors.append("ACTUAL_TESTED_MERGE_BASE_NOT_PROVEN")
    if 'git cat-file -e "$BASE^{commit}"' not in source:
        errors.append("MISSING_BASE_OBJECT_NOT_REJECTED")
    if "continue-on-error:" in source:
        errors.append("MUST_NOT_IGNORE_FAILED_STEP")
    if re.search(r"(?m)^\s+if:\s*", source):
        errors.append("REQUIRED_STEP_MUST_NOT_BE_CONDITIONAL")
    for command in REQUIRED_COMMANDS:
        if command not in source:
            errors.append("MISSING_REQUIRED_CONTROL:" + command.split()[0])
    return errors

class RequiredGovernanceGateContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WORKFLOW.read_text(encoding="utf-8")
    def test_real_workflow_contract(self):
        self.assertEqual(problems(self.source), [])
    def test_filtering_just_one_pr_path_is_refused(self):
        text = self.source.replace("  pull_request:\n    branches: [main]",
                    "  pull_request:\n    branches: [main]\n    paths:\n      - Tools/**")
        self.assertIn("PATH_FILTER_CAN_LEAVE_REQUIRED_CHECK_PENDING", problems(text))
    def test_silently_skipping_a_failed_guard_is_refused(self):
        text = self.source.replace("    timeout-minutes: 25",
                    "    timeout-minutes: 25\n    continue-on-error: true")
        self.assertIn("MUST_NOT_IGNORE_FAILED_STEP", problems(text))
    def test_removing_content_guard_is_refused(self):
        text = self.source.replace(
            "Verification/tests-v3.3.6/test_content_zip_guard.py","DISABLED_TEST.py")
        self.assertTrue(any(x.startswith("MISSING_REQUIRED_CONTROL") for x in problems(text)))
    def test_checkout_without_exact_base_history_is_refused(self):
        text = self.source.replace("fetch-depth: 0","fetch-depth: 1")
        self.assertIn("EXACT_BASE_OR_TOKEN_HARDENING_MISSING",problems(text))
    def test_unrelated_manual_event_cannot_satisfy_required_job(self):
        text = self.source.replace("  push:", "  workflow_dispatch:\n  push:")
        self.assertIn("UNSAFE_OR_UNRELATED_TRIGGER",problems(text))
    def test_required_job_name_is_fixed(self):
        text = self.source.replace("name: GFP-Required-Governance-Gate",
                                   "name: Optional-Preview-Only")
        self.assertIn("REQUIRED_CHECK_CONTEXT_CHANGED",problems(text))
    def test_duplicate_status_test_can_run_only_on_merge_range(self):
        text = self.source.replace("github.event.pull_request.base.sha","github.sha")
        self.assertIn("FULL_COMPARISON_RANGE_MISSING",problems(text))

    @unittest.skipUnless(shutil.which("git") and shutil.which("bash"), "Git and Bash required")
    def test_stale_event_base_does_not_replay_unrelated_family(self):
        """Execute both workflow PR base selectors against a real synthetic merge."""
        workflows = [WORKFLOW, ROOT / ".github/workflows/gfp-lexical-stage5-claim-guard.yml"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", "-C", directory, *args], text=True, stderr=subprocess.STDOUT).strip()
            git("init", "-b", "main")
            git("config", "user.name", "Regression")
            git("config", "user.email", "regression@example.invalid")
            (root / "initial").write_text("initial")
            git("add", ".")
            git("commit", "-m", "original base")
            old_base = git("rev-parse", "HEAD")
            git("checkout", "-b", "a1")
            (root / "A1.json").write_text("{}")
            git("add", ".")
            git("commit", "-m", "A1 change")
            head = git("rev-parse", "HEAD")
            git("checkout", "main")
            (root / "A2.json").write_text("{}")
            git("add", ".")
            git("commit", "-m", "unrelated A2 maintenance")
            actual_base = git("rev-parse", "HEAD")
            git("merge", "--no-ff", "a1", "-m", "GitHub synthetic merge")
            self.assertEqual(git("diff", "--name-only", old_base, "HEAD").splitlines(), ["A1.json", "A2.json"])
            for workflow in workflows:
                with self.subTest(workflow=workflow.name):
                    source = workflow.read_text(encoding="utf-8")
                    match = re.search(r'(?ms)^          if \[ "\$EVENT_NAME" = "pull_request" \]; then\n(.*?)(?=^          (?:elif|else)\b)', source)
                    self.assertIsNotNone(match)
                    script = match.group(1) + '\nprintf "%s\\n" "$BASE"\n'
                    env = dict(os.environ, PR_BASE=old_base, PR_HEAD=head)
                    run = subprocess.run(["bash", "-e", "-c", script], cwd=root, env=env, text=True, capture_output=True)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    self.assertEqual(run.stdout.strip(), actual_base)
                    self.assertEqual(git("diff", "--name-only", run.stdout.strip(), "HEAD"), "A1.json")
                    env["PR_HEAD"] = old_base
                    rejected = subprocess.run(["bash", "-e", "-c", script], cwd=root, env=env, text=True, capture_output=True)
                    self.assertNotEqual(rejected.returncode, 0)

if __name__ == "__main__":
    unittest.main()
