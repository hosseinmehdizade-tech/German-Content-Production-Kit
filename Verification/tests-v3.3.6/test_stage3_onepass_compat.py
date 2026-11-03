"""One-pass Stage3 adapter regression: no fabricated semantic pass or source writes."""
import copy,hashlib,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"Verification/emit_stage3_onepass_compat.py"
spec=importlib.util.spec_from_file_location("onepass",SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
RAW=b"unchanged-authority"
H=hashlib.sha256(RAW).hexdigest()
EXAMPLE={"schema":"gcpk-stage3-onepass@1.0","workstream":"demo",
    "working_sha256":H,"registered_source_sha256":"1"*64,
    "cards":[{"id":"c1","baseline":{"examples":4,"kombinationen":1},
    "changes":[],"decisions":{"kombinationen":{"decision":"VERIFIED_PRESENT"}}},
    {"id":"c2","baseline":{"examples":4,"kombinationen":0},
    "changes":[],"decisions":{"kombinationen":{"decision":"CLOSED_NO_FORCE",
                 "reason":"NO_ADDITIONAL_TEACHING_VALUE"}}}]}
class TestLeanOnePassStage3Compatibility(unittest.TestCase):
    def test_views_cover_exact_source_and_ids(self):
        v=m.project(copy.deepcopy(EXAMPLE),RAW)
        self.assertEqual(set(v),{"3A","3B","3C"})
        self.assertEqual([x["id"] for x in v["3A"]["items"]],["c1","c2"])
        self.assertEqual(v["3A"]["working_sha256"],H)
        self.assertEqual(v["3C"]["open_holds"],0)
    def test_no_new_work_is_fabricated(self):
        v=m.project(copy.deepcopy(EXAMPLE),RAW)
        self.assertEqual(v["3B"]["items"][0]["changes"],[])
        self.assertEqual(v["3B"]["items"][1]["changes"],[])
    def test_views_not_old_official_pass(self):
        v=m.project(copy.deepcopy(EXAMPLE),RAW)
        for view in v.values():self.assertIn("NOT_OFFICIAL_STAGE_PASS",view["status"])
    def test_detect_materialized_source_drift(self):
        with self.assertRaisesRegex(ValueError,"WORKING_BYTES_SHA_MISMATCH"):
            m.project(copy.deepcopy(EXAMPLE),RAW+b"changed")
    def test_detect_changed_declared_pin(self):
        e=copy.deepcopy(EXAMPLE);e["working_sha256"]="0"*64
        with self.assertRaises(ValueError):m.project(e,RAW)
    def test_detect_unpinned_original(self):
        e=copy.deepcopy(EXAMPLE);e["registered_source_sha256"]=None
        with self.assertRaises(ValueError):m.project(e,RAW)
    def test_reject_duplicate_card_id(self):
        e=copy.deepcopy(EXAMPLE);e["cards"][1]["id"]="c1"
        with self.assertRaises(ValueError):m.project(e,RAW)
    def test_reject_missing_facet_decision(self):
        e=copy.deepcopy(EXAMPLE);e["cards"][0]["decisions"]={}
        with self.assertRaises(ValueError):m.project(e,RAW)
    def test_no_force_requires_reason(self):
        e=copy.deepcopy(EXAMPLE);e["cards"][1]["decisions"]["kombinationen"]["reason"]=""
        with self.assertRaises(ValueError):m.project(e,RAW)
    def test_unverified_hold_is_visible(self):
        e=copy.deepcopy(EXAMPLE);e["cards"][0]["decisions"]["kombinationen"]={"decision":"HOLD","reason":"missing source"}
        v=m.project(e,RAW)
        self.assertEqual(v["3C"]["open_holds"],1)
    def test_invalid_changes_fail(self):
        e=copy.deepcopy(EXAMPLE);e["cards"][1]["changes"]=[{"field":"meaning"}]
        with self.assertRaises(ValueError):m.project(e,RAW)
    def test_existing_content_auto_reused_not_reauthored(self):
        v=m.project(copy.deepcopy(EXAMPLE),RAW)
        self.assertEqual(v["3A"]["items"][0]["baseline"]["kombinationen"],1)
        self.assertEqual(v["3C"]["items"][0]["decisions"]["kombinationen"]["decision"],"VERIFIED_PRESENT")
if __name__=="__main__":unittest.main()
