"""P1 next source-owner milestone intake: no silent ADOPTED from legacy Stage5."""
from __future__ import annotations
import copy, importlib.util, json, shutil, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"Verification/verify_p1_next_native_owner_intake_v1.py"
spec=importlib.util.spec_from_file_location("gfp_p1_owner_intake",SCRIPT)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class SevenSourceOwnerIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((ROOT/gate.INTAKE).read_text(encoding="utf-8"))
        cls.actual=gate.verify()
    def test_real_exact_owner_blobs_seven_without_adoption(self):
        a=self.actual
        self.assertEqual(a["counts"]["source_owner_witnesses"],7)
        self.assertEqual(a["counts"]["ready_producers"],0)
        self.assertEqual(a["counts"]["adopted_producers"],0)
        self.assertGreaterEqual(a["counts"]["source_owner_predicates"],15)
        self.assertTrue(all(r["source_owner_git_blob_verified"] and
                            not r["formal_adopted"] for r in a["candidates"]))
    def mutate(self,modify):
        d=copy.deepcopy(self.manifest)
        modify(d)
        return d
    def fails(self,code,mutator):
        with self.assertRaisesRegex(gate.IntakeError,code):
            gate.verify(intake=self.mutate(mutator))
    def test_claim_new_adoption_without_native_receipt_rejected(self):
        self.fails("UNSUPPORTED_NEW_ADOPTION_OR_AUTHORIZATION",
                   lambda d:d["candidates"][0]["governed_new_production_evidence"].__setitem__("formal_new_p1_adoption",True))
    def test_claim_governed_native_receipt_without_any_remote_proof_rejected(self):
        self.fails("UNSUPPORTED_NEW_ADOPTION_OR_AUTHORIZATION",
                   lambda d:d["candidates"][1]["governed_new_production_evidence"].__setitem__("new_production_governed_receipt",True))
    def test_claim_user_source_authorization_without_owner_file_rejected(self):
        self.fails("UNSUPPORTED_NEW_ADOPTION_OR_AUTHORIZATION",
                   lambda d:d["candidates"][1]["governed_new_production_evidence"].__setitem__("new_source_owner_stage5_authorization",True))
    def test_owner_sha_swapped_to_old_content_refused(self):
        self.fails("OWNER_BLOB_PIN_DRIFT",
                   lambda d:d["candidates"][0].__setitem__("owner_git_blob","0"*40))
    def test_global_registry_pin_drift_refused(self):
        self.fails("OWNER_BLOB_PIN_DRIFT",
                   lambda d:d["authority"].__setitem__("registry_git_blob","0"*40))
    def test_catalog_pin_drift_refused(self):
        self.fails("OWNER_BLOB_PIN_DRIFT",
                   lambda d:d["authority"].__setitem__("catalog_git_blob","0"*40))
    def test_wrong_workspace_parent_refused(self):
        self.fails("OWNER_WORKSPACE_FAMILY_ROUTING_DRIFT",
                   lambda d:d["candidates"][0].__setitem__("family_id","family:aspekte-b2"))
    def test_status_changed_without_review_refused(self):
        self.fails("OWNER_STAGE_STATUS_CHANGED_REVIEW_REQUIRED",
                   lambda d:d["candidates"][2]["observed_assertions"].__setitem__("independent_stage4_qa_completed",True))
    def test_synthetic_ready_status_does_not_promise_producer(self):
        self.fails("FALSE_READY_STATUS",
                   lambda d:d["candidates"][2].__setitem__("status","ADOPTED"))
    def test_duplicate_source_candidate_refused(self):
        self.fails("DUPLICATE_CANDIDATE_ID",
                   lambda d:d["candidates"][1].__setitem__("id",d["candidates"][0]["id"]))
    def test_fake_nonzero_status_count_refused(self):
        self.fails("UNSUPPORTED_SUCCESSFUL_ADOPTION_COUNTS",
                   lambda d:d["counts"].__setitem__("formally_adopted_new_p1_producers",1))
    def test_unlisted_source_field_refused(self):
        self.fails("OWNER_FIELD_MISSING",
                   lambda d:d["candidates"][4]["observed_assertions"].__setitem__("stage4.certified",True))
    def test_modified_owner_file_with_original_sha_refused(self):
        with tempfile.TemporaryDirectory() as td:
            temp=Path(td)
            paths={gate.INTAKE,gate.CATALOG,gate.REGISTRY,
                   "Tools/build_governed_clean_delivery_v1.py"}
            paths.update(r["owner_evidence"] for r in self.manifest["candidates"])
            for name in paths:
                target=temp/name
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/name,target)
            owner=temp/self.manifest["candidates"][0]["owner_evidence"]
            owner.write_bytes(owner.read_bytes()+b"\n")
            with self.assertRaisesRegex(gate.IntakeError,"OWNER_BLOB_PIN_DRIFT"):
                gate.verify(root=temp)
    def test_unreadable_source_namespace_refused(self):
        self.fails("OWNER_WORKSPACE_FAMILY_ROUTING_DRIFT",
                   lambda d:d["candidates"][0].__setitem__("owner_evidence","Other/BOGUS.json"))
    def test_unknown_gate_not_silently_added(self):
        self.fails("UNSUPPORTED_NEW_ADOPTION_OR_AUTHORIZATION",
                   lambda d:d["candidates"][2]["governed_new_production_evidence"].__setitem__("fake_receipt",False))

if __name__=="__main__":unittest.main()
