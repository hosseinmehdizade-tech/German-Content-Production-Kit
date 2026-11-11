"""Nonpublishing OP01 base-source path guard regressions; no network, cards, or ZIP."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Verification/check_op01_trusted_base_pr_paths_v1.py"
spec = importlib.util.spec_from_file_location("op01_base_paths", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

REPO = "hosseinmehdizade-tech/German-Content-Production-Kit"
HEAD = "a" * 40


def snapshot(paths):
    files = [{"filename": path, "status": "modified"} for path in paths]
    pr = {
        "number": 178, "base": {"ref": "main", "repo": {"full_name": REPO}},
        "head": {"sha": HEAD}, "changed_files": len(files),
    }
    return pr, files


class TrustedBasePathGuardTests(unittest.TestCase):
    def check(self, paths, **changes):
        pr, files = snapshot(paths)
        pr.update(changes)
        return guard.assess(pr, files, REPO, 178, HEAD)

    def test_regular_docs_change_passes(self):
        result = self.check(["Optimization-Program/README.md"])
        self.assertEqual(result["status"],
                         "PASS_BASE_DEFINED_CONTROL_PATHS_UNCHANGED")
        self.assertEqual(result["head_sha"], HEAD)

    def test_current_required_workflow_edit_denied(self):
        with self.assertRaisesRegex(ValueError,
                                    "TRUSTED_GOVERNANCE_CONTROL_PATH_EDIT"):
            self.check([".github/workflows/gfp-required-governance-gate.yml"])

    def test_future_trusted_workflow_edit_denied(self):
        with self.assertRaisesRegex(ValueError,
                                    "TRUSTED_GOVERNANCE_CONTROL_PATH_EDIT"):
            self.check([".github/workflows/gfp-op01-trusted-base-guard.yml"])

    def test_fresh_workflow_can_not_spoof_a_required_job_name(self):
        # A NEW filename can claim an old check context with GitHub Actions as
        # its source; protecting only the original workflow name is unsound.
        with self.assertRaisesRegex(ValueError,
                                    "TRUSTED_GOVERNANCE_CONTROL_PATH_EDIT"):
            self.check([".github/workflows/new-fake-required-status.yml"])

    def test_renamed_filename_into_workflows_is_also_denied(self):
        pr, files = snapshot([".github/workflows/fake-from-docs.yaml"])
        files[0]["status"] = "renamed"
        files[0]["previous_filename"] = "docs/notes.yaml"
        with self.assertRaisesRegex(ValueError,
                                    "TRUSTED_GOVERNANCE_CONTROL_PATH_EDIT"):
            guard.assess(pr, files, REPO, 178, HEAD)

    def test_self_verifier_edit_denied(self):
        with self.assertRaisesRegex(ValueError,
                                    "TRUSTED_GOVERNANCE_CONTROL_PATH_EDIT"):
            self.check(["Verification/check_op01_trusted_base_pr_paths_v1.py"])

    def test_writer_permission_registry_edit_denied(self):
        with self.assertRaisesRegex(ValueError,
                                    "TRUSTED_GOVERNANCE_CONTROL_PATH_EDIT"):
            self.check(["Optimization-Program/WRITER-SCOPES.json"])

    def test_renamed_protected_previous_name_denied(self):
        pr, files = snapshot(["docs/safe-name.yml"])
        files[0]["status"] = "renamed"
        files[0]["previous_filename"] = ".github/workflows/gfp-required-governance-gate.yml"
        with self.assertRaisesRegex(ValueError,
                                    "TRUSTED_GOVERNANCE_CONTROL_PATH_EDIT"):
            guard.assess(pr, files, REPO, 178, HEAD)

    def test_contradictory_event_head_sha_denied(self):
        with self.assertRaisesRegex(ValueError, "PR_HEAD_SHA_MOVED"):
            self.check(["docs/a.md"], head={"sha": "b" * 40})

    def test_nonmain_target_denied(self):
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_TARGET_BRANCH"):
            self.check(["docs/a.md"], base={"ref": "other", "repo": {"full_name": REPO}})

    def test_changed_file_count_must_match(self):
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_OR_OVERSIZED"):
            self.check(["docs/a.md"], changed_files=2)

    def test_path_traversal_denied(self):
        with self.assertRaisesRegex(ValueError, "UNSAFE_CHANGED_PATH"):
            self.check(["docs/../Verification/check_op01_trusted_base_pr_paths_v1.py"])

    def test_empty_pr_or_oversized_pr_denied(self):
        pr, _ = snapshot([])
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_OR_OVERSIZED"):
            guard.assess(pr, [], REPO, 178, HEAD)
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_OR_OVERSIZED"):
            self.check(["docs/a.md"], changed_files=3001)

    def test_real_workflow_is_readonly_base_defined_and_nonrequired(self):
        wf = (ROOT / ".github/workflows/gfp-op01-trusted-base-guard.yml").read_text()
        self.assertIn("  pull_request_target:", wf)
        self.assertIn("  contents: read", wf)
        self.assertIn("  pull-requests: read", wf)
        self.assertIn("GFP-Trusted-Base-Workflow-Guard", wf)
        self.assertNotIn("allow-unsafe-pr-checkout", wf)
        self.assertNotIn("ref: ${{ github.event.pull_request.head", wf)
        self.assertNotIn("run: make", wf)

    def test_provider_pagination_and_head_recheck(self):
        pr, files = snapshot([f"docs/file-{i:03}.md" for i in range(101)])
        calls = []
        def fake(url, token):
            calls.append(url)
            if "/files?" not in url:
                return pr
            return files[:100] if url.endswith("page=1") else files[100:]
        result = guard.run({
            "GITHUB_EVENT_NAME": "pull_request_target",
            "GITHUB_REPOSITORY": REPO,
            "PR_NUMBER": "178",
            "PR_HEAD_SHA": HEAD,
            "GITHUB_TOKEN": "synthetic",
        }, fetch=fake)
        self.assertEqual(result["changed_files_checked"], 101)
        self.assertEqual(len(calls), 4)

    def test_provider_change_after_pagination_denied(self):
        pr, files = snapshot(["docs/safe.md"])
        reads = 0
        def fake(url, token):
            nonlocal reads
            if "/files?" in url:
                return files
            reads += 1
            if reads == 2:
                return dict(pr, head={"sha": "b" * 40})
            return pr
        with self.assertRaisesRegex(ValueError, "PR_HEAD_OR_FILE_SET_MOVED"):
            guard.run({
                "GITHUB_EVENT_NAME": "pull_request_target",
                "GITHUB_REPOSITORY": REPO,
                "PR_NUMBER": "178",
                "PR_HEAD_SHA": HEAD,
                "GITHUB_TOKEN": "synthetic",
            }, fetch=fake)

    def test_wrong_event_denied_before_network(self):
        with self.assertRaisesRegex(ValueError, "BASE_DEFINED_PR_EVENT_REQUIRED"):
            guard.run({"GITHUB_EVENT_NAME": "pull_request"})

if __name__ == "__main__":
    unittest.main()
