"""Every new mutable lexical release must identify its canonical owner first.

Tests never mutate a real owner or accepted content, import collection, app or SRS.
"""
from __future__ import annotations
import json,sys,tempfile,unittest,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Verification"))
from verify_lexical_family_release_route_v1 import verify_family,ROUTE

class CanonicalFamilyReleaseTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.d=Path(tmp.name)
        self.registry=json.loads((ROOT/ROUTE).read_text(encoding="utf-8"))
    def review(self,fid,owner=None,parent=None):
        fam=next(f for f in self.registry["families"] if f["family_id"]==fid)
        path=self.d/"review.json"
        path.write_text(json.dumps({"workstream":owner if owner is not None else fam["canonical_git_workspace"],
            "curated_current_parent_sha256":parent if parent is not None else fam.get("active_content_sha256"),
            "schema":"gcpk-lexical-cross-tile-acceptance@1.0.0"}),encoding="utf-8")
        return path
    def test_all_user_accepted_lexical_owners_routed(self):
        allowed=[f for f in self.registry["families"] if f["route_state"].startswith("CANONICAL_ROUTED__USER_ACCEPTED_CURATED_OWNER_PIN")]
        self.assertGreaterEqual(len(allowed),9)
        for family in allowed:
            with self.subTest(family=family["family_id"]):
                got=verify_family(family["family_id"],self.review(family["family_id"]))
                self.assertEqual(got["canonical_git_workspace"],family["canonical_git_workspace"])
                self.assertEqual(got["parent_sha256"],family["active_content_sha256"])
    def test_workstream_basename_also_accepted(self):
        fid="family:menschen-a1-verben"
        f=next(x for x in self.registry["families"] if x["family_id"]==fid)
        out=verify_family(fid,self.review(fid,owner=f["canonical_git_workspace"].removeprefix("Workspaces/")))
        self.assertEqual(out["family_id"],fid)
    def test_aspekte_unattested_owner_blocks_all_levels(self):
        for fid in ("family:aspekte-b1plus","family:aspekte-b2","family:aspekte-c1"):
            with self.subTest(fid=fid),self.assertRaisesRegex(ValueError,"CURATED_CURRENT_UNATTESTED"):
                verify_family(fid,self.review(fid))
    def test_library_only_vocabulary_requires_producer_registration(self):
        with self.assertRaisesRegex(ValueError,"NO_ATTESTED_GIT_OWNER"):
            verify_family("family:vocabulary-sonstige",self.review("family:vocabulary-sonstige"))
    def test_nonlexical_grammar_refused(self):
        with self.assertRaisesRegex(ValueError,"NOT_STANDARD_LEXICAL_FAMILY"):
            verify_family("family:grammatik-aktiv-a1-b1",self.review("family:grammatik-aktiv-a1-b1"))
    def test_nonlexical_bildkarten_refused(self):
        with self.assertRaisesRegex(ValueError,"NOT_STANDARD_LEXICAL_FAMILY"):
            verify_family("family:bildkarten-piloten",self.review("family:bildkarten-piloten"))
    def test_parent_hash_mismatch_blocks(self):
        fid="family:menschen-a1-verben"
        with self.assertRaisesRegex(ValueError,"PARENT_IS_NOT_ATTESTED_CURRENT"):
            verify_family(fid,self.review(fid,parent="f"*64))
    def test_wrong_family_workspace_blocks(self):
        fid="family:menschen-a1-verben"
        with self.assertRaisesRegex(ValueError,"WRONG_CANONICAL_OWNER"):
            verify_family(fid,self.review(fid,owner="Workspaces/aspekte-b2-v336"))
    def test_unknown_family_fail_closed(self):
        path=self.d/"arbitrary.json";path.write_text("{}")
        with self.assertRaisesRegex(ValueError,"UNKNOWN_OR_DUPLICATED_FAMILY"):
            verify_family("family:not-real",path)
    def test_malformed_family_id_fail_closed(self):
        path=self.d/"arbitrary.json";path.write_text("{}")
        with self.assertRaisesRegex(ValueError,"INVALID_FAMILY_ID"):
            verify_family("../Workspaces/menschen-a1-verben",path)
    def test_required_review_absent_blocks(self):
        with self.assertRaisesRegex(ValueError,"CROSS_TILE_REVIEW_MISSING_FOR_FAMILY"):
            verify_family("family:menschen-a1-verben",self.d/"absent.json")
    def test_publisher_family_id_is_mandatory_before_output(self):
        src=self.d/"four-role";src.mkdir()
        (src/"SYNTHETIC-cards.tsv").write_text("id\tfront\tdetails\texamples\nx\tTest\t[]\t[]\n")
        (src/"SYNTHETIC-CANONICAL.json").write_text('{"cards":[]}')
        (src/"SYNTHETIC-SOURCE-OUTPUT-MAP.tsv").write_text("id\tsource\n")
        (src/"SYNTHETIC-QA.json").write_text("{}")
        output=self.d/"output.zip"
        args=[sys.executable,"-B",str(ROOT/"Tools/build_quality_gated_lexical_candidate_v1.py"),
            str(src),str(output),"--receipt",str(self.d/"stage5.json"),
            "--policy-report",str(self.d/"policy.json"),
            "--stage4-receipt",str(self.d/"stage4.json"),
            "--cross-tile-review",str(self.d/"review.json")]
        proc=subprocess.run(args,capture_output=True,text=True,encoding="utf-8",timeout=30)
        self.assertNotEqual(proc.returncode,0)
        self.assertIn("family-id",proc.stderr)
        self.assertFalse(output.exists())
    def test_front_wrapper_native_stage5_uses_quality_launcher(self):
        text=(ROOT/"Tools/build_front_gated_clean_delivery_v1.py").read_text(encoding="utf-8")
        self.assertIn("build_quality_gated_lexical_candidate_v1.py",text)
        self.assertIn("LEXICAL_QUALITY_EVIDENCE_REQUIRED_BEFORE_STAGE5",text)
        self.assertIn("'stage5_acceptance'",text)
        self.assertIn("FRONT_GATE_BLOCKED",text)

if __name__=="__main__":unittest.main()
