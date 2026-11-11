"""P1 source-owner preflight tests over the real current Aspekte B1+ checkout.

Negative controls change only in-memory objects; never mutate cards or checkpoints.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Tools/p1_aspekte_b1plus_real_owner_gate_v1.py"
spec = importlib.util.spec_from_file_location("p1_b1plus_gate", SOURCE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class SourceOwnerGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.latest, cls.latest_blob = gate.read_json(ROOT, gate.OWNER + "/LATEST.json")
        cls.checkpoint, cls.checkpoint_blob = gate.read_json(ROOT, gate.OWNER + "/CHECKPOINT.json")
        cls.registry, cls.registry_blob = gate.read_json(ROOT, gate.REGISTRY)
        cls.catalog, cls.catalog_blob = gate.read_json(ROOT, gate.CATALOG)
        cls.domains, cls.domain_blob = gate.read_json(ROOT, gate.DOMAINS)

    def check(self, **changes):
        return gate.evaluate(ROOT, **changes)

    def test_real_policy_bytes_and_source_owner_are_verified_without_release(self):
        output = self.check()
        self.assertEqual(output["report_status"],
                         "PASS_REAL_OWNER_AND_ALL_POLICY_BYTES__NO_STAGE5_ADOPTION")
        self.assertEqual(output["owner"]["source_rows"], 1548)
        self.assertEqual(output["owner"]["project_id"], "aspekte-b1plus")
        self.assertEqual(output["owner"]["current_stage"], gate.GATE08_NONIMPORT)
        self.assertEqual(output["owner"]["reported_stage4_holds_from_checkpoint"], 340)
        self.assertNotIn("274 remaining G2", output["next"])
        self.assertEqual(output["policy"]["registered_bindings"],
                         len(self.registry["policy_bindings"]))
        self.assertEqual(output["policy"]["byte_pinned_bindings_verified"],
                         len(self.registry["policy_bindings"]))
        self.assertTrue({"risk_based_stage4", "linguistic_qa",
                         "curated_current_delta_qa", "seven_stages"}.issubset(
                            output["policy"]["stage4_routed_binding_ids"]))
        self.assertEqual(output["owner_git_blobs"]["latest"], self.latest_blob)
        self.assertEqual(output["owner_git_blobs"]["checkpoint"], self.checkpoint_blob)
        self.assertEqual(output["stage5"],
                         "BLOCKED_NO_NEW_SOURCE_OWNER_STAGE4_APPROVAL")
        self.assertEqual(output["new_formal_policy_adoptions"], 0)

    def test_checkpoint_and_latest_stage_must_agree(self):
        tampered = copy.deepcopy(self.checkpoint)
        tampered["current_stage"] = "STAGE4_G2_274_REMAIN_NONIMPORT"
        with self.assertRaisesRegex(gate.P1GateError,
                                    "OWNER_LATEST_CHECKPOINT_STAGE_OR_STATUS_DRIFT"):
            self.check(checkpoint=tampered)

    def test_gate08_without_explicit_stage4_holds_is_not_approved(self):
        tampered = copy.deepcopy(self.checkpoint)
        tampered["stage4"] = "STAGE4_ALL_APPROVED"
        with self.assertRaisesRegex(gate.P1GateError,
                                    "UNEXPECTED_SOURCE_STAGE_REVIEW_REQUIRED"):
            self.check(checkpoint=tampered)

    def test_gate08_ambiguous_blocked_name_is_rejected(self):
        tampered = copy.deepcopy(self.latest)
        tampered["current_stage"] = "APP_GATE08_MAYBE_OK_NONIMPORT"
        companion = copy.deepcopy(self.checkpoint)
        companion["current_stage"] = tampered["current_stage"]
        with self.assertRaisesRegex(gate.P1GateError,
                                    "UNEXPECTED_SOURCE_STAGE_REVIEW_REQUIRED"):
            self.check(latest=tampered, checkpoint=companion)

    def test_gate08_fake_checkpoint_import_ready_is_rejected(self):
        tampered = copy.deepcopy(self.checkpoint)
        tampered["import_ready"] = True
        with self.assertRaisesRegex(gate.P1GateError,
                                    "FALSE_STAGE4_5_6_7_OR_IMPORT_PROMOTION"):
            self.check(checkpoint=tampered)

    def test_gate08_fake_stage6_pass_is_rejected(self):
        tampered = copy.deepcopy(self.checkpoint)
        tampered["stage6"] = "PASS_WITHOUT_REAL_IMPORT"
        with self.assertRaisesRegex(gate.P1GateError,
                                    "FALSE_STAGE4_5_6_7_OR_IMPORT_PROMOTION"):
            self.check(checkpoint=tampered)

    def test_fake_formal_stage4_approval_is_rejected(self):
        tampered = copy.deepcopy(self.latest)
        tampered["stage4_formal_acceptance"] = True
        with self.assertRaisesRegex(gate.P1GateError,
                                    "FALSE_STAGE4_5_6_7_OR_IMPORT_PROMOTION"):
            self.check(latest=tampered)

    def test_fake_import_ready_is_rejected(self):
        tampered = copy.deepcopy(self.latest)
        tampered["import_ready"] = True
        with self.assertRaisesRegex(gate.P1GateError, "FALSE_STAGE4_5_6_7_OR_IMPORT"):
            self.check(latest=tampered)

    def test_stage5_promotion_without_a_new_owner_decision_is_rejected(self):
        tampered = copy.deepcopy(self.checkpoint)
        tampered["stage5"] = "PASS_UNAUTHORIZED"
        with self.assertRaisesRegex(gate.P1GateError,
                                    "FALSE_STAGE4_5_6_7_OR_IMPORT"):
            self.check(checkpoint=tampered)

    def test_mismatched_curated_source_identity_is_rejected(self):
        tampered = copy.deepcopy(self.latest)
        tampered["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(gate.P1GateError,
                                    "CURATED_OWNER_SOURCE_IDENTITY_DRIFT"):
            self.check(latest=tampered)

    def test_wrong_family_workspace_pair_is_rejected(self):
        tampered = copy.deepcopy(self.catalog)
        target = next(x for x in tampered["workspaces"] if x["id"] == gate.WORKSPACE)
        target["parent_family_id"] = "family:aspekte-b2"
        with self.assertRaisesRegex(gate.P1GateError,
                                    "WRONG_FAMILY_WORKSPACE_OR_DOMAIN"):
            self.check(catalog=tampered)

    def test_policy_blob_pin_drift_is_rejected(self):
        tampered = copy.deepcopy(self.registry)
        tampered["policy_bindings"]["risk_based_stage4"]["blob_sha"] = "f" * 40
        with self.assertRaisesRegex(gate.P1GateError,
                                    "POLICY_GIT_BLOB_DRIFT:risk_based_stage4"):
            self.check(registry=tampered)

    def test_missing_central_policy_is_rejected(self):
        tampered = copy.deepcopy(self.registry)
        del tampered["policy_bindings"]["curated_current_delta_qa"]
        with self.assertRaisesRegex(gate.P1GateError,
                                    "MANDATORY_STAGE4_POLICY_MISSING"):
            self.check(registry=tampered)

    def test_wrong_owner_domain_never_forced_to_lexical(self):
        tampered = copy.deepcopy(self.domains)
        target = next(x for x in tampered["families"] if x["id"] == gate.FAMILY)
        target["declared_domain"] = "GRAMMAR"
        with self.assertRaisesRegex(gate.P1GateError,
                                    "WRONG_FAMILY_WORKSPACE_OR_DOMAIN"):
            self.check(domains=tampered)

    def test_nonimport_boundary_required(self):
        tampered = copy.deepcopy(self.latest)
        tampered["current_stage"] = "STAGE5_RELEASED"
        companion = copy.deepcopy(self.checkpoint)
        companion["current_stage"] = tampered["current_stage"]
        with self.assertRaisesRegex(gate.P1GateError,
                                    "UNEXPECTED_SOURCE_STAGE_REVIEW_REQUIRED"):
            self.check(latest=tampered, checkpoint=companion)


if __name__ == "__main__":
    unittest.main()
