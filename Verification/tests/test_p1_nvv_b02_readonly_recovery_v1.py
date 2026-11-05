"""Negative tests: NVV B02 parent recovery must never become Stage3/4 or P1 ADOPTED."""
from __future__ import annotations
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
script=ROOT/"Verification/verify_p1_nvv_b02_readonly_recovery_v1.py"
spec=importlib.util.spec_from_file_location("gfp_opt_nvv_b02_recovery",script)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
class NVVB02RecoveryReadOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((ROOT/gate.REPORT).read_text(encoding="utf8"))
    def test_exact_owner_snapshot_still_stage3_unrecovered(self):
        x=gate.verify()
        self.assertEqual(x["baseline_cards"],100)
        self.assertEqual(x["examples_trilingual"],400)
        self.assertEqual(x["editorial_proposals_pending"],13)
        self.assertEqual(x["original_lost_stage3_working"],"NOT_RECOVERED")
        self.assertFalse(x["P1_ADOPTED"])
    def deny(self,expected,modifier):
        x=copy.deepcopy(self.original)
        modifier(x)
        with self.assertRaisesRegex(gate.VerificationError,expected):
            gate.verify(receipt=x)
    def test_forged_B02_stage4_approval_denied(self):
        self.deny("FALSE_STAGE4_OR_RELEASE_PROMOTION",lambda d:d["nonclaims"].__setitem__("stage4_B02_accepted",True))
    def test_forged_original_stage3_recovered_denied(self):
        self.deny("FALSE_STAGE4_OR_RELEASE_PROMOTION",lambda d:d["nonclaims"].__setitem__("original_f604_working_file_recovered",True))
    def test_original_working_sha_forged_denied(self):
        self.deny("FALSIFIED_ORIGINAL_STAGE3_BYTES",lambda d:d["recovered_baseline"].__setitem__("sha256",d["source_owner"]["lost_original_working_expected_sha256"]))
    def test_wrong_source_parent_denied(self):
        self.deny("ORIGINAL_SOURCE_PINS_MISMATCH",lambda d:d["authenticated_parents"].__setitem__("parent_stage4_zip_sha256","0"*64))
    def test_false_lesson_count_denied(self):
        self.deny("RECOVERED_PARENT_BASELINE_SCOPE_INVALID",lambda d:d["recovered_baseline"].__setitem__("positions",[1,100]))
    def test_provider_readback_not_optional(self):
        self.deny("SCOPE_OR_PROVIDER_RECEIPT_INVALID",lambda d:d["recovery_tool"].__setitem__("provider_readback_byte_identical",False))
    def test_negative_control_inflation_denied(self):
        self.deny("QA_NEGATIVE_CONTROLS_INVALID",lambda d:d["recovery_qa"]["negative_controls_rejected"].append("made-up-pass"))
    def test_fake_proposals_promoted_denied(self):
        self.deny("RECOVERED_PARENT_BASELINE_SCOPE_INVALID",lambda d:d["recovered_baseline"].__setitem__("no_proposals_applied",False))
    def test_owner_pin_not_replaced(self):
        self.deny("OWNER_RECOVERY_PIN_INVALID",lambda d:d["source_owner"].__setitem__("git_blob","0"*40))
    def test_no_app_or_learner_srs_claim(self):
        self.deny("FALSE_STAGE4_OR_RELEASE_PROMOTION",lambda d:d["nonclaims"].__setitem__("source_LOCKED_app_SRS_FSRS_modified",True))
if __name__=="__main__":unittest.main()
