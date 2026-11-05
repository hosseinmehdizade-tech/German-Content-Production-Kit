"""B02 editorial sidecar proves source owner alignment but NEVER Stage4/ADOPTED."""
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"Verification/verify_p1_nvv_b02_13_editorial_review_v1.py"
sp=importlib.util.spec_from_file_location("verify_p1_nvv_b02_13_editorial_review_v1",SCRIPT)
v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
class EditorialOwnerGateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=json.loads((ROOT/v.REVIEW).read_text(encoding="utf8"))
  cls.qa=json.loads((ROOT/v.QA).read_text(encoding="utf8"))
 def deny(self,label,mutator):
  r,q=copy.deepcopy(self.report),copy.deepcopy(self.qa)
  mutator(r,q)
  with self.assertRaisesRegex(v.VerifyError,label):v.verify(report=r,qa=q)
 def test_live_pin_and_nonimport(self):
  result=v.verify()
  self.assertEqual((result["sources"],result["cards_approved"],result["P1_ADOPTED"]),(13,0,0))
 def test_fake_stage4(self):
  self.deny("FALSE_COUNTS_OR_ADOPTION",lambda r,q:r["counts"].__setitem__("stage4_acceptance",1))
 def test_fake_adopted(self):
  self.deny("FALSE_COUNTS_OR_ADOPTION",lambda r,q:r["counts"].__setitem__("adopted_producers",1))
 def test_misleading_original_pdf_source(self):
  self.deny("SOURCE_SCOPE_OR_LEXICAL_REFERENCE_FALSE",lambda r,q:r["candidates"][0].__setitem__("evidence_scope","ORIGINAL_NVVPDF_VERIFIED"))
 def test_invalid_owner_pos(self):
  self.deny("EDITORIAL_OWNER_PROPOSAL_MISMATCH",lambda r,q:r["candidates"][0].__setitem__("position",199))
 def test_duplicate_existing_target_as_new(self):
  self.deny("DUPLICATE_CANONICAL_TARGET_CARD",lambda r,q:r["candidates"][1].__setitem__("editorial_assessment","EXTERNAL_LEXEME_EDITORIAL_CANDIDATE"))
 def test_make_new_edit_without_owner_stage4(self):
  self.deny("FORGED_EDITORIAL_PROMOTION",lambda r,q:r["candidates"][0].__setitem__("card_write_authorized",True))
 def test_collapsing_two_senses(self):
  self.deny("BEANSPRUCHEN_SENSE_COLLAPSE",lambda r,q:q["lexical_distinct_senses"].__setitem__("beanspruchen_144","rights_claim"))
 def test_rename_target_term(self):
  self.deny("EDITORIAL_OWNER_PROPOSAL_MISMATCH",lambda r,q:r["candidates"][1].__setitem__("term_de","fake"))
 def test_closing_phrase_hold_without_approval(self):
  self.deny("EXTERNAL_ATTESTATION_FALSE_STAGE4",lambda r,q:next(x for x in r["dispositions"] if x["position"]==163)["new_external_attestation"].__setitem__("original_hold_remains",False))
 def test_forge_owner_decision(self):
  self.deny("OWNER_DISPOSITION_MUTATED",lambda r,q:r["dispositions"][0].__setitem__("source_owner_decision_unchanged","APPROVED"))
 def test_unjustified_new_count(self):
  self.deny("FALSE_COUNTS_OR_ADOPTION",lambda r,q:r["counts"].__setitem__("new_cards_approved",1))
 def test_orphan_links(self):
  self.deny("DUPLICATE_CANONICAL_TARGET_CARD",lambda r,q:r["candidates"][1].__setitem__("relationship_target_id","nonexistent-id"))
 def test_no_invented_example_approval(self):
  self.deny("FORGED_EDITORIAL_PROMOTION",lambda r,q:r["candidates"][0].__setitem__("formal_stage3_content_acceptance",True))
if __name__=="__main__":unittest.main()
