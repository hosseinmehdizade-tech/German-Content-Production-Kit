"""Negative and positive tests for global policy routing. No card data touched."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Verification/audit_global_policy_sync_v1.py"
spec = importlib.util.spec_from_file_location("global_policy_sync_audit", SCRIPT)
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)


class TestGlobalPolicyIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_registry, cls.base_matrix, cls.base_dirs, cls.base_files = auditor.load_snapshot()

    def check_snapshot(self, reg=None, matrix=None, dirs=None, files=None):
        return auditor.audit_snapshot(
            copy.deepcopy(self.base_registry) if reg is None else reg,
            copy.deepcopy(self.base_matrix) if matrix is None else matrix,
            list(self.base_dirs) if dirs is None else dirs,
            dict(self.base_files) if files is None else files,
        )

    def test_actual_complete_registered_snapshot_passes(self):
        self.assertEqual(self.check_snapshot(), [])

    def test_git_blob_sha_has_standard_git_object_encoding(self):
        self.assertEqual(auditor.git_blob_sha(b"test content\n"),
                         "d670460b4b4aece5915caf5c68d12f560a9fe3e4")

    def test_windows_crlf_checkout_does_not_spuriously_break_pin(self):
        path = self.base_registry["policy_bindings"]["currentness"]["path"]
        pin = self.base_registry["policy_bindings"]["currentness"]["blob_sha"]
        original = self.base_files[path]
        crlf = original.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        self.assertTrue(auditor.matches_git_blob_across_checkout_line_endings(crlf, pin))
        files = dict(self.base_files)
        files[path] = crlf
        self.assertEqual(self.check_snapshot(files=files), [])

    def test_crlf_normalization_does_not_hide_actual_policy_mutation(self):
        path = self.base_registry["policy_bindings"]["currentness"]["path"]
        pin = self.base_registry["policy_bindings"]["currentness"]["blob_sha"]
        original = self.base_files[path].replace(b"\r\n", b"\n")
        changed = (original + b"\nUNAUTHORIZED CHANGE\n").replace(b"\n", b"\r\n")
        self.assertFalse(auditor.matches_git_blob_across_checkout_line_endings(changed, pin))
        files = dict(self.base_files)
        files[path] = changed
        self.assertIn("STALE_POLICY_BLOB_PIN:currentness", self.check_snapshot(files=files))

    def test_every_policy_is_version_pinned(self):
        self.assertEqual(len(self.base_registry["policy_bindings"]), len(auditor.REQUIRED_POLICIES))
        self.assertTrue(all(x["path"] in self.base_files for x in
                            self.base_registry["policy_bindings"].values()))

    def test_front_back_policy_mandatory_and_pinned(self):
        reg = copy.deepcopy(self.base_registry)
        key = "global_flashcard_front_back_presentation"
        binding = reg["policy_bindings"][key]
        self.assertEqual(binding["stages"], [5, 6])
        self.assertIn("GLOBAL-FLASHCARD-FRONT-BACK", binding["path"])
        del reg["policy_bindings"][key]
        self.assertIn("MANDATORY_POLICY_BINDINGS_CHANGED", self.check_snapshot(reg=reg))
        files = dict(self.base_files)
        files[binding["path"]] += b"\\nUNAUTHORIZED_POLICY_REWRITE\\n"
        self.assertIn("STALE_POLICY_BLOB_PIN:" + key, self.check_snapshot(files=files))

    def test_front_back_cannot_be_hidden_from_startup(self):
        files = dict(self.base_files)
        files[auditor.START] = files[auditor.START].replace(
            b"Prompt/GLOBAL-FLASHCARD-FRONT-BACK-PRESENTATION-CONTRACT-v1.0.0.md",
            b"Prompt/WRONG-FRONT-BACK-CONTRACT.md", 1)
        self.assertIn("FRONT_BACK_ACTIVE_STARTUP_POINTER_MISSING",
                      self.check_snapshot(files=files))

    def test_registry_pin_mutation_fails(self):
        data = copy.deepcopy(self.base_registry)
        data["policy_bindings"]["related_taxonomy"]["blob_sha"] = "0" * 40
        self.assertIn("STALE_POLICY_BLOB_PIN:related_taxonomy", self.check_snapshot(reg=data))

    def test_policy_bytes_change_without_registry_update_fails(self):
        files = dict(self.base_files)
        path = self.base_registry["policy_bindings"]["stage3_onepass"]["path"]
        files[path] += b"\nUNAUTHORIZED EDIT"
        self.assertIn("STALE_POLICY_BLOB_PIN:stage3_onepass", self.check_snapshot(files=files))

    def test_missing_policy_raises_blocker(self):
        files = dict(self.base_files)
        files.pop(self.base_registry["policy_bindings"]["lexical_relation_display"]["path"])
        self.assertIn("MISSING_ACTIVE_POLICY:lexical_relation_display", self.check_snapshot(files=files))

    def test_missing_expected_binding_fails(self):
        reg = copy.deepcopy(self.base_registry)
        del reg["policy_bindings"]["related_taxonomy"]
        self.assertIn("MANDATORY_POLICY_BINDINGS_CHANGED", self.check_snapshot(reg=reg))

    def test_repo_posix_path_is_valid_on_both_operating_systems(self):
        self.assertTrue(auditor.safe_path("Prompt/RELATED-SECTIONS-TAXONOMY-POLICY-v1.1.0.md"))
        self.assertFalse(auditor.safe_path("C:/outside.md"))
        self.assertFalse(auditor.safe_path("../outside.md"))
        self.assertFalse(auditor.safe_path("Prompt\\\\outside.md"))
        self.assertFalse(auditor.safe_path("Prompt//ambiguous.md"))

    def test_unsafe_parent_reference_fails(self):
        reg = copy.deepcopy(self.base_registry)
        reg["policy_bindings"]["related_taxonomy"]["path"] = "../OTHER.md"
        self.assertIn("UNSAFE_POLICY_PATH:related_taxonomy", self.check_snapshot(reg=reg))

    def test_stage_scope_invalid_fails(self):
        reg = copy.deepcopy(self.base_registry)
        reg["policy_bindings"]["stage5_clean_builder"]["stages"] = [5, 10]
        self.assertIn("INVALID_POLICY_STAGE:stage5_clean_builder", self.check_snapshot(reg=reg))

    def test_safety_invariant_false_fails(self):
        reg = copy.deepcopy(self.base_registry)
        reg["protected_invariants"]["immutable_raw_and_locked"] = False
        self.assertIn("PROTECTED_SAFETY_INVARIANT_MISSING_OR_DISABLED", self.check_snapshot(reg=reg))

    def test_wrong_active_prompt_pointer_fails(self):
        files = dict(self.base_files)
        files[auditor.ENTRY] = b"START-PROMPT-v3.3.4.md\n"
        self.assertIn("WRONG_ACTIVE_PROMPT_POINTER", self.check_snapshot(files=files))

    def test_root_readme_registry_pointer_missing_fails(self):
        files = dict(self.base_files)
        files[auditor.README] = b"Old README only"
        self.assertIn("MISSING_ENTRYPOINT_ROUTER:README.md", self.check_snapshot(files=files))

    def test_new_anti_churn_preamble_before_router_does_not_false_fail(self):
        files = dict(self.base_files)
        # The mandatory pointer remains in the first 4KiB even after
        # legitimate additional metadata and anti-churn instructions.
        files[auditor.START] = b"ANOTHER VALID STARTUP NOTE\\n\\n" + files[auditor.START]
        self.assertNotIn("MISSING_ENTRYPOINT_ROUTER:" + auditor.START,
                         self.check_snapshot(files=files))

    def test_router_buried_beyond_four_kibibytes_still_fails_closed(self):
        files = dict(self.base_files)
        files[auditor.START] = (b"X" * 4500) + files[auditor.START]
        self.assertIn("MISSING_ENTRYPOINT_ROUTER:" + auditor.START,
                      self.check_snapshot(files=files))

    def test_registry_not_in_bootstrap_fails(self):
        files = dict(self.base_files)
        files[auditor.BOOTSTRAP] = b"Not routed"
        self.assertIn("MISSING_ENTRYPOINT_ROUTER:PROJECT-BOOTSTRAP.md", self.check_snapshot(files=files))

    def test_old_active_taxonomy_description_fails(self):
        files = dict(self.base_files)
        files[auditor.README] = files[auditor.README].replace(
            b"Historical 2026-11-04 A1 V25 replay", b"Active v1.0 only")
        self.assertIn("OLD_RELATED_V1_ACTIVE_DESCRIPTION_NOT_RELABELED",
                      self.check_snapshot(files=files))

    def test_misleading_adapter_ci_line_fails(self):
        files = dict(self.base_files)
        files[auditor.START] += b"\nExact per-workstream adapter/CI parity remains unverified"
        self.assertIn("STALE_ADAPTER_CI_CLAIM", self.check_snapshot(files=files))

    def test_new_nvv_workspace_only_routed_not_governed_or_stage_accepted(self):
        path="Workspaces/nomen-verb-verbindungen"
        rows=[w for w in self.base_matrix["git_workspaces"] if w["path"]==path]
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["native_adapter_verified"],"NO_WORKSPACE_SPECIFIC_PROOF")
        self.assertEqual(rows[0]["real_output_verified"],"NO_WORKSPACE_WIDE_PROOF")
        self.assertEqual(rows[0]["semantic_stage4"],"NOT_ATTESTED_BY_SYNC")
        self.assertEqual(rows[0]["stage6_runtime"],"NOT_ATTESTED_BY_SYNC")
        self.assertEqual(self.check_snapshot(),[])

    def test_new_unregistered_workspace_fails(self):
        dirs = list(self.base_dirs) + ["Workspaces/new-future-course"]
        self.assertIn("WORKSPACE_INVENTORY_DRIFT", self.check_snapshot(dirs=dirs))

    def test_lost_registered_workspace_fails(self):
        dirs = list(self.base_dirs[:-1])
        self.assertIn("WORKSPACE_INVENTORY_DRIFT", self.check_snapshot(dirs=dirs))

    def test_duplicate_workspace_fails(self):
        mat = copy.deepcopy(self.base_matrix)
        mat["git_workspaces"].append(copy.deepcopy(mat["git_workspaces"][0]))
        errors = self.check_snapshot(matrix=mat)
        self.assertIn("WORKSPACE_DUPLICATE", errors)

    def test_false_full_stage4_pass_fails(self):
        mat = copy.deepcopy(self.base_matrix)
        mat["git_workspaces"][0]["semantic_stage4"] = "PASS"
        errors = self.check_snapshot(matrix=mat)
        self.assertTrue(any(x.startswith("UNSUPPORTED_ADOPTION_PROMOTION:") for x in errors))

    def test_false_native_adapter_pass_fails(self):
        mat = copy.deepcopy(self.base_matrix)
        mat["git_workspaces"][0]["native_adapter_verified"] = "PASS_34_OF_34"
        self.assertTrue(any("UNSUPPORTED_ADOPTION_PROMOTION" in x for x in
                            self.check_snapshot(matrix=mat)))

    def test_false_global_certificate_fails(self):
        mat = copy.deepcopy(self.base_matrix)
        mat["no_blanket_certification"] = False
        self.assertIn("FALSE_BULK_ACCEPTANCE", self.check_snapshot(matrix=mat))

    def test_disappearing_b1_hold_fails(self):
        mat = copy.deepcopy(self.base_matrix)
        mat["scoped_observations"] = [x for x in mat["scoped_observations"]
                                       if "B1" not in x.get("source", "")]
        self.assertIn("B1_145_REAL_BLOCKER_HIDDEN", self.check_snapshot(matrix=mat))

    def test_disappearing_vocabulary_gap_fails(self):
        mat = copy.deepcopy(self.base_matrix)
        mat["open_gaps"] = [x for x in mat["open_gaps"] if "Vocabulary" not in x]
        self.assertIn("REAL_PARITY_GAPS_NOT_RECORDED", self.check_snapshot(matrix=mat))

    def test_synthetic_adoption_does_not_mutate_inputs(self):
        reg = copy.deepcopy(self.base_registry)
        mat = copy.deepcopy(self.base_matrix)
        files = dict(self.base_files)
        rr, mm, ff = copy.deepcopy(reg), copy.deepcopy(mat), dict(files)
        auditor.audit_snapshot(reg, mat, list(self.base_dirs), files)
        self.assertEqual((reg, mat, files), (rr, mm, ff))


if __name__ == "__main__":
    unittest.main()
