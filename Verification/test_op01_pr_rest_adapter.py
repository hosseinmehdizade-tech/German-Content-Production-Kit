"""OP-01 synthetic real-REST-shape compatibility; no token, no network, no writes."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import audit_op01_pr_rest_adapter as adapter
import test_op01_pr_staging_simulation as legacy


class GitHubRESTStagedPRShape(unittest.TestCase):
    def setUp(self):
        source = legacy.StagedPRTransportSimulation()
        source.setUp()
        self.model = source
        self.plan = copy.deepcopy(source.plan)
        self.observed = copy.deepcopy(source.observed)
        self.observed.pop("pull_request")
        self.observed.pop("changed_files")
        self.observed.pop("changed_files_paginated_complete")
        self.rest = {
            "number": 999,
            "state": "open",
            "merged": False,
            "draft": True,
            "changed_files": 1,
            "base": {
                "ref": "main", "sha": source.main_sha,
                "repo": {"full_name": adapter.REPOSITORY}
            },
            "head": {
                "ref": source.branch, "sha": source.head,
                "repo": {"full_name": adapter.REPOSITORY}
            },
        }
        self.files = [{
            "sha": adapter.git_blob_sha(source.candidate),
            "filename": source.path,
            "status": "modified",
            "additions": 2,
            "deletions": 2,
            "changes": 4,
            "blob_url": "https://github.com/...",
            "raw_url": "https://raw.githubusercontent.com/...",
        }]

    def evaluate(self, update=None, **kwargs):
        p = copy.deepcopy(self.plan)
        o = copy.deepcopy(self.observed)
        pr = copy.deepcopy(self.rest)
        files = copy.deepcopy(self.files)
        if update:
            update(p, o, pr, files)
        return adapter.assess_rest(
            p, o, rest_pr=pr, rest_files=files,
            parent=self.model.parent,
            candidate=self.model.candidate,
            staged=kwargs.pop("staged", self.model.candidate),
            **kwargs,
        )

    def no_authority(self, outcome):
        for flag in (
            "observations_are_authenticated",
            "rest_api_identity_authenticated",
            "rest_pagination_independently_authenticated",
            "main_branch_protection_independently_verified",
            "independent_current_issuer_authenticated",
            "required_status_source_authenticated",
            "op01_writer_granted",
            "production_write_allowed",
            "pr_merge_allowed",
            "stage4_semantic_pass",
            "stage5_allowed",
            "stage6_pass",
            "stage7_release_final",
            "performed_writes",
            "github_settings_changed",
            "github_network_requests_performed",
        ):
            self.assertIs(outcome[flag], False, flag)

    def blocked(self, update, code, **kwargs):
        result = self.evaluate(update, **kwargs)
        self.assertEqual(result["status"], "BLOCKED_PR_TRANSPORT_SIMULATION", result)
        self.assertIn(code, " | ".join(result["blockers"]), result)
        self.no_authority(result)

    def test_actual_nested_rest_shape_passes_only_a_simulation(self):
        outcome = self.evaluate()
        self.assertEqual(outcome["status"],
                         "PASS_SIMULATED_ONE_FILE_PR_SHAPE_ONLY_NOT_AUTHORIZED", outcome)
        self.assertTrue(outcome["exact_one_file_modified"])
        self.no_authority(outcome)

    def test_real_github_rest_files_have_extra_metadata(self):
        normalized = adapter.normalize(
            self.rest, self.files, page_size=100, page_number=1,
            next_page_present=False,
        )
        self.assertEqual(normalized["changed_files_normalized"], [{
            "filename": self.model.path,
            "status": "modified",
            "git_blob_sha": adapter.git_blob_sha(self.model.candidate),
        }])

    def test_real_closed_pr50_shape_is_rejected_not_promoted(self):
        # Shapes/count verified with public GitHub REST /pulls/50 and /files;
        # reduced fixture, not authenticated runtime or a live source.
        def mutate(p, o, pr, files):
            pr.update({
                "number": 50, "state": "closed",
                "merged": True, "draft": False, "changed_files": 3
            })
            pr["head"]["ref"] = "audit/op01-pr-staging-contract-nonactive-20261030"
            files.extend([
                {**files[0], "filename": "Verification/audit_op01_pr_staging_simulation.py", "status": "added"},
                {**files[0], "filename": "Verification/test_op01_pr_staging_simulation.py", "status": "added"},
            ])
        self.blocked(mutate, "REST_PR_MUST_CHANGE_EXACTLY_ONE_FILE")

    def test_pr_rest_head_from_fork_is_rejected(self):
        self.blocked(
            lambda p,o,pr,f: pr["head"]["repo"].update(full_name="attacker/fork"),
            "REST_BASE_OR_HEAD_REPO_NOT_EXPECTED")

    def test_pr_rest_base_repo_crossed_is_rejected(self):
        self.blocked(
            lambda p,o,pr,f: pr["base"]["repo"].update(full_name="attacker/other"),
            "REST_BASE_OR_HEAD_REPO_NOT_EXPECTED")

    def test_rest_base_wrong_main_sha_fails_exact_parent_gate(self):
        self.blocked(lambda p,o,pr,f: pr["base"].update(sha="f"*40),
                     "PR_BASE_OR_HEAD_PIN_MISMATCH")

    def test_rest_head_wrong_sha_fails_race_gate(self):
        self.blocked(lambda p,o,pr,f: pr["head"].update(sha="f"*40),
                     "PR_HEAD_MOVED_OR_UNPINNED")

    def test_main_head_race_cannot_be_hidden_by_rest_parse(self):
        self.blocked(lambda p,o,pr,f: o.update(main_commit_after="f"*40),
                     "MAIN_HEAD_CHANGED_OR_STALE_BASE")

    def test_rest_file_sha_must_match_candidate_exact_git_blob(self):
        self.blocked(lambda p,o,pr,f: f[0].update(sha="f"*40),
                     "REST_FILE_GIT_BLOB_DIFFERS_FROM_STAGING_BYTES")

    def test_actual_staged_readback_diff_blocks_even_if_rest_sha_matches_old(self):
        self.blocked(None, "REST_FILE_GIT_BLOB_DIFFERS_FROM_STAGING_BYTES",
                     staged=b"wrong staged readback")

    def test_original_parent_sha_still_enforced(self):
        self.blocked(
            lambda p,o,pr,f: o.update(parent_git_blob_sha_at_main="f"*40),
            "REMOTE_PARENT_BLOB_STALE_OR_UNVERIFIED")

    def test_rest_changed_files_count_forged_blocks(self):
        self.blocked(lambda p,o,pr,f: pr.update(changed_files=2),
                     "REST_PR_FILE_COUNT_OR_PAGINATION_DRIFT")

    def test_rest_extra_file_list_blocks(self):
        self.blocked(lambda p,o,pr,f: f.append(dict(f[0],filename="other.tsv")),
                     "REST_PR_FILE_COUNT_OR_PAGINATION_DRIFT")

    def test_rest_duplicate_file_paths_block(self):
        self.blocked(lambda p,o,pr,f: (
            pr.update(changed_files=2),
            f.append(dict(f[0])),
        ), "REST_FILE_DUPLICATE_OR_MISSING_PATH")

    def test_rest_renamed_file_cannot_be_canonicalized(self):
        self.blocked(lambda p,o,pr,f: f[0].update(
            status="renamed", previous_filename="Workspaces/a/old.tsv"),
            "REST_RENAMED_FILE_FORBIDDEN")

    def test_rest_source_file_is_out_of_scope(self):
        path = "Workspaces/synthetic-op01/02-Source/canonical.json"
        self.blocked(lambda p,o,pr,f: (
            p.update(target_path=path),
            f[0].update(filename=path),
        ), "EDIT_PATH_OUTSIDE_MUTABLE_WORKSPACE")

    def test_actual_pr_files_first_page_is_required(self):
        self.blocked(None, "REST_FILES_PAGE_NOT_EXHAUSTIVELY_READ", page_number=2)

    def test_short_page_size_is_not_accepted(self):
        self.blocked(None, "REST_FILES_PAGE_NOT_EXHAUSTIVELY_READ", page_size=30)

    def test_false_pagination_assurance_with_next_link_blocks(self):
        self.blocked(None, "REST_FILES_PAGE_NOT_EXHAUSTIVELY_READ",
                     next_page_present=True)

    def test_open_merged_impossible_response_blocks(self):
        self.blocked(lambda p,o,pr,f: pr.update(merged=True),
                     "REST_PR_IMPOSSIBLE_MERGED_OPEN")

    def test_nonboolean_rest_fields_block(self):
        self.blocked(lambda p,o,pr,f: pr.update(merged=0),
                     "REST_PR_STATUS_INVALID")

    def test_unknown_rest_file_status_blocks(self):
        self.blocked(lambda p,o,pr,f: f[0].update(status="magic"),
                     "REST_FILE_STATUS_UNRECOGNIZED")

    def test_missing_rest_repo_is_not_silently_assumed(self):
        self.blocked(lambda p,o,pr,f: pr["head"].pop("repo"),
                     "REST_PR_REF_REPO_MISSING")

    def test_real_closed_single_file_pr_rejected_as_candidate(self):
        self.blocked(lambda p,o,pr,f: pr.update(state="closed", merged=True),
                     "PR_IDENTITY_OR_REVIEW_STATE_MISMATCH")

    def test_unprotected_branch_still_blocks(self):
        self.blocked(lambda p,o,pr,f: o.update(main_protected=False),
                     "PROTECTED_MAIN_NOT_SHOWN_IN_SUPPLIED_SNAPSHOT")

    def test_fake_owner_signature_cannot_activate_result(self):
        def mutate(p,o,pr,f):
            pr["approved"] = True
            pr["owner_signature"] = "self-issued"
            o["trusted_checks"] = "green"
        out = self.evaluate(mutate)
        self.assertEqual(out["status"],
                         "PASS_SIMULATED_ONE_FILE_PR_SHAPE_ONLY_NOT_AUTHORIZED")
        self.no_authority(out)

    def test_no_network_and_no_github_write_helpers_exposed(self):
        self.assertFalse(hasattr(adapter, "github_api"))
        self.assertFalse(hasattr(adapter, "merge_pull_request"))
        self.assertFalse(hasattr(adapter, "create_pull_request"))


if __name__ == "__main__":
    unittest.main()
