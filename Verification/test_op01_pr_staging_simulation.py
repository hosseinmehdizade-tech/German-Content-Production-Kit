"""OP01 feature-branch PR protocol preflight: synthetic-only, never authorized."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import persist_verified_git_edit as writer

spec = importlib.util.spec_from_file_location(
    "op01_pr_simulator", HERE / "audit_op01_pr_staging_simulation.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StagedPRTransportSimulation(unittest.TestCase):
    def setUp(self):
        self.parent = b'{"v":1,"review":"unverified"}\n'
        self.candidate = b'{"v":2,"review":"unverified"}\n'
        self.head = "b" * 40
        self.main_sha = "a" * 40
        self.path = "Workspaces/synthetic-op01/review/CURRENT-EDITABLE.json"
        self.branch = "op01-staging/synthetic-one-file"
        self.plan = {
            "repository": module.REPOSITORY,
            "target_branch": "main",
            "staging_branch": self.branch,
            "target_path": self.path,
            "workstream": "synthetic-op01",
            "expected_main_commit_sha": self.main_sha,
            "expected_parent_git_blob_sha": writer.git_blob_sha(self.parent),
            "expected_candidate_sha256": hashlib.sha256(self.candidate).hexdigest(),
        }
        self.observed = {
            "pull_request": {
                "number": 999, "state": "open", "merged": False,
                "base": "main", "base_sha": self.main_sha,
                "head": self.branch, "head_sha": self.head,
                "head_repo_full_name": module.REPOSITORY, "changed_files": 1,
            },
            "changed_files": [{"filename": self.path, "status": "modified"}],
            "changed_files_paginated_complete": True,
            "main_commit_before": self.main_sha,
            "main_commit_after": self.main_sha,
            "pr_head_before": self.head,
            "pr_head_after": self.head,
            "parent_git_blob_sha_at_main": writer.git_blob_sha(self.parent),
            "candidate_git_blob_sha_at_head": writer.git_blob_sha(self.candidate),
            "main_protected": True,  # UNTRUSTED mock; no real Git policy
            "writer_scope_status": "DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL",
        }

    def assess(self, change=None, *, parent=None, candidate=None, staged=None):
        p = copy.deepcopy(self.plan)
        o = copy.deepcopy(self.observed)
        if change:
            change(p, o)
        return module.assess(
            p, o,
            parent=self.parent if parent is None else parent,
            candidate=self.candidate if candidate is None else candidate,
            staged=self.candidate if staged is None else staged,
        )

    def blocked(self, change, code, **kwargs):
        result = self.assess(change, **kwargs)
        self.assertEqual(result["status"], "BLOCKED_PR_TRANSPORT_SIMULATION", result)
        self.assertIn(code, result["blockers"], result)
        self.check_never_authorizes(result)

    def check_never_authorizes(self, result):
        for key in (
            "observations_are_authenticated", "main_branch_protection_independently_verified",
            "required_status_source_authenticated", "independent_current_issuer_authenticated",
            "independent_owner_approval", "workstream_content_approved",
            "op01_writer_granted", "production_write_allowed", "pr_merge_allowed",
            "stage4_semantic_pass", "stage5_allowed", "stage6_pass",
            "stage7_release_final", "performed_writes", "github_settings_changed",
        ):
            self.assertIs(result[key], False, key)

    def test_matching_one_file_PR_shape_passes_simulation_not_authority(self):
        result = self.assess()
        self.assertEqual(result["status"], "PASS_SIMULATED_ONE_FILE_PR_SHAPE_ONLY_NOT_AUTHORIZED", result)
        self.assertTrue(result["base_head_unchanged_within_snapshot"])
        self.assertTrue(result["pr_head_unchanged_within_snapshot"])
        self.assertTrue(result["file_bytes_match_claimed_candidate"])
        self.assertTrue(result["exact_one_file_modified"])
        self.check_never_authorizes(result)

    def test_no_network_or_write_api_is_provided_by_simulator(self):
        self.assertFalse(hasattr(module, "github_api"))
        self.assertFalse(hasattr(module, "persist"))
        self.assertFalse(hasattr(module, "create_pull_request"))
        self.assertFalse(hasattr(module, "merge_pull_request"))

    def test_unchanged_bytes_are_not_an_edit(self):
        self.blocked(None, "NO_EDIT", candidate=self.parent, staged=self.parent)

    def test_candidate_hash_tamper_fails(self):
        self.blocked(lambda p,o: p.update(expected_candidate_sha256="f"*64),
                     "CANDIDATE_SHA256_MISMATCH")

    def test_remote_staged_bytes_mismatch_fails(self):
        self.blocked(None, "STAGING_BRANCH_READBACK_BYTES_DIFFER",
                     staged=b"tampered branch")

    def test_parent_blob_hash_drift_fails(self):
        self.blocked(lambda p,o: p.update(expected_parent_git_blob_sha="f"*40),
                     "LOCAL_PARENT_GIT_BLOB_MISMATCH")

    def test_actual_main_target_blob_changed_fails(self):
        self.blocked(lambda p,o: o.update(parent_git_blob_sha_at_main="f"*40),
                     "REMOTE_PARENT_BLOB_STALE_OR_UNVERIFIED")

    def test_head_candidate_git_blob_changed_fails(self):
        self.blocked(lambda p,o: o.update(candidate_git_blob_sha_at_head="f"*40),
                     "REMOTE_STAGING_BLOB_MISMATCH")

    def test_main_head_race_fails(self):
        self.blocked(lambda p,o: o.update(main_commit_after="c"*40),
                     "MAIN_HEAD_CHANGED_OR_STALE_BASE")

    def test_stale_main_parent_pin_fails(self):
        self.blocked(lambda p,o: p.update(expected_main_commit_sha="c"*40),
                     "MAIN_HEAD_CHANGED_OR_STALE_BASE")

    def test_pr_head_race_fails(self):
        self.blocked(lambda p,o: o.update(pr_head_after="c"*40),
                     "PR_HEAD_MOVED_OR_UNPINNED")

    def test_pr_head_pin_drift_fails(self):
        self.blocked(lambda p,o: o["pull_request"].update(head_sha="c"*40),
                     "PR_HEAD_MOVED_OR_UNPINNED")

    def test_added_extra_file_fails(self):
        def bad(p,o):
            o["pull_request"]["changed_files"] = 2
            o["changed_files"].append({"filename":"Optimization-Program/WRITER-SCOPES.json",
                                        "status":"modified"})
        self.blocked(bad, "PR_FILE_SCOPE_NOT_EXACT_ONE_MODIFIED_WORKING_FILE")

    def test_incomplete_files_pagination_fails(self):
        self.blocked(lambda p,o: o.update(changed_files_paginated_complete=False),
                     "PR_FILES_PAGINATION_NOT_PROVEN_COMPLETE")

    def test_pr_changed_file_count_mismatch_fails(self):
        self.blocked(lambda p,o: o["pull_request"].update(changed_files=2),
                     "PR_CHANGED_FILE_COUNT_MISMATCH")

    def test_rename_or_add_is_not_an_allowed_mutable_edit(self):
        for status in ("added", "removed", "renamed", "copied"):
            with self.subTest(status=status):
                self.blocked(
                    lambda p,o: o["changed_files"][0].update(status=status),
                    "PR_FILE_SCOPE_NOT_EXACT_ONE_MODIFIED_WORKING_FILE"
                )

    def test_wrong_repo_or_fork_fails(self):
        self.blocked(lambda p,o: o["pull_request"].update(
            head_repo_full_name="attacker/fork"),
            "PR_IDENTITY_OR_REVIEW_STATE_MISMATCH")

    def test_pr_already_merged_not_a_proposal(self):
        self.blocked(lambda p,o: o["pull_request"].update(state="closed", merged=True),
                     "PR_IDENTITY_OR_REVIEW_STATE_MISMATCH")

    def test_wrong_target_branch_fails(self):
        self.blocked(lambda p,o: p.update(target_branch="unprotected-dev"),
                     "UNEXPECTED_REPOSITORY_OR_TARGET_BRANCH")

    def test_direct_main_instead_of_staging_branch_fails(self):
        self.blocked(lambda p,o: p.update(staging_branch="main"),
                     "INVALID_DEDICATED_STAGING_BRANCH")

    def test_wip52_LATEST_cannot_be_staged_under_mutable_working_exception(self):
        path = "Workspaces/aber-hallo-listen-tabellen/LATEST.json"
        self.blocked(lambda p,o: (p.update(target_path=path,
                                          workstream="aber-hallo-listen-tabellen"),
                                  o["changed_files"][0].update(filename=path)),
                     "EDIT_PATH_OUTSIDE_MUTABLE_WORKSPACE")

    def test_source_and_locked_paths_remain_immutable(self):
        for path in (
            "Workspaces/synthetic-op01/02-Source/canonical.json",
            "Workspaces/synthetic-op01/LOCKED/archive.json",
            "Workspaces/synthetic-op01/00-source/manifest.json",
        ):
            with self.subTest(path=path):
                self.blocked(lambda p,o: (p.update(target_path=path),
                                          o["changed_files"][0].update(filename=path)),
                             "EDIT_PATH_OUTSIDE_MUTABLE_WORKSPACE")

    def test_unprotected_main_must_not_be_rehearsal_pass(self):
        self.blocked(lambda p,o: o.update(main_protected=False),
                     "PROTECTED_MAIN_NOT_SHOWN_IN_SUPPLIED_SNAPSHOT")

    def test_true_flag_is_only_mock_not_real_branch_protection(self):
        result = self.assess()
        self.assertFalse(result["main_branch_protection_independently_verified"])
        self.assertFalse(result["production_write_allowed"])

    def test_self_claimed_approval_cannot_promote_positive_rehearsal(self):
        def fake(p,o):
            p["approved"] = True
            p["signature"] = "fake"
            o["pull_request"]["approved_by_owner"] = True
            o["trusted_status_green"] = True
        result = self.assess(fake)
        self.assertEqual(result["status"], "PASS_SIMULATED_ONE_FILE_PR_SHAPE_ONLY_NOT_AUTHORIZED")
        self.check_never_authorizes(result)

    def test_writer_grant_activated_in_snapshot_is_not_allowed(self):
        self.blocked(lambda p,o: o.update(writer_scope_status="ACTIVE_SCOPED_GRANTS"),
                     "WRITER_SCOPE_DENY_ALL_NOT_PRESERVED")

    def test_branch_get_error_or_empty_snapshot_fails(self):
        result = module.assess({}, {}, parent=self.parent,
                               candidate=self.candidate, staged=self.candidate)
        self.assertEqual(result["status"], "BLOCKED_PR_TRANSPORT_SIMULATION")
        self.check_never_authorizes(result)


if __name__ == "__main__":
    unittest.main()
