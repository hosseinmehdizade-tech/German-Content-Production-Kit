from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import json
import unittest

FILE = Path(__file__).resolve().parents[1] / "audit_kombinationen_source_first_v1_2.py"
spec = spec_from_file_location("source_first_audit", FILE)
m = module_from_spec(spec)
spec.loader.exec_module(m)


def item(de="auf halbem Weg", **kwargs):
    return {"de": de, "fa": "در نیمهٔ راه", "en": "halfway", "kind": "prepositional_phrase",
            "teaching_delta": "PATTERN", "origin": "CURATED_PEDAGOGICAL", **kwargs}


class ContractTests(unittest.TestCase):
    def codes(self, data):
        return [it["code"] for it in m.diagnostic(data)["issues"]]

    def test_clean_unicode_whitespace(self):
        self.assertEqual(m.clean("   Auf   HALBEM Weg.  "), "auf halbem weg")

    def test_good_curated_candidate(self):
        c = {"card_id": "demo", "examples": [{"de": "Ich kenne den Weg zum Bahnhof."}], "combinations": [item()], "rection": []}
        self.assertEqual(self.codes(c), [])

    def test_overlap_is_advisory_not_error(self):
        c = {"examples": ["Wir sind auf halbem Weg nach Hause."], "combinations": [item()], "rection": []}
        x = m.diagnostic(c)
        self.assertIn("EXAMPLE_FRAGMENT_OVERLAP", [k["code"] for k in x["issues"]])
        self.assertTrue(x["diagnostic_only_not_stage4_acceptance"])

    def test_exact_example_cloning(self):
        self.assertIn("EXACT_EXAMPLE_CLONE", self.codes({"examples": ["auf halbem Weg"], "combinations": [item()], "rection": []}))

    def test_cross_tile_exact_duplicate(self):
        self.assertIn("EXACT_REKTION_DUPLICATE", self.codes({"examples": [], "combinations": [item()], "rection": ["auf halbem Weg"]}))

    def test_not_cross_tile_partial_overlap(self):
        self.assertNotIn("EXACT_REKTION_DUPLICATE", self.codes({"examples": [], "combinations": [item("auf den Bus warten")], "rection": ["warten auf + Akkusativ"]}))

    def test_duplicate_combinations(self):
        self.assertIn("DUPLICATE_COMBINATION", self.codes({"combinations": [item(), item()], "examples": [], "rection": []}))

    def test_source_without_evidence(self):
        it=item();it["origin"]="REGISTERED_SOURCE"
        self.assertIn("MISSING_REGISTERED_SOURCE_EVIDENCE", self.codes({"combinations": [it]}))

    def test_unknown_source(self):
        it=item();it["origin"]="REGISTERED_SOURCE";it["evidence"]=[{"source_id":"fake","locator":"https://example.com/foo","access_status":"VERIFIED_EXACT_ENTRY"}]
        self.assertIn("UNKNOWN_REGISTERED_SOURCE",[x["code"] for x in m.diagnostic({"combinations":[it]}, {"duden_online"})["issues"]])

    def test_unverified_source_claim(self):
        it=item();it["origin"]="REGISTERED_SOURCE";it["evidence"]=[{"source_id":"dict_cc_de_en","locator":"https://www.dict.cc/","access_status":"UNVERIFIED"}]
        self.assertIn("UNVERIFIED_SOURCE_CLAIM",[x["code"] for x in m.diagnostic({"combinations":[it]}, {"dict_cc_de_en"})["issues"]])

    def test_translation_required(self):
        it=item();it["fa"]="";it["en"]=""
        cs=self.codes({"combinations":[it]});self.assertIn("MISSING_FA", cs);self.assertIn("MISSING_EN",cs)

    def test_en_optional_profile(self):
        it=item();it["en"]="";cs=self.codes({"require_en":False,"combinations":[it]});self.assertNotIn("MISSING_EN",cs)

    def test_no_forced_combination_count(self):
        r=m.diagnostic({"combinations":[],"rection":[]});self.assertEqual(r["issues"],[])

    def test_variety_only_advisory(self):
        cs=[item("ein mühsamer Weg"),item("ein langer Weg"),item("ein kurzer Weg")]
        self.assertIn("SINGLE_PATTERN_FAMILY",self.codes({"combinations":cs}))

    def test_varied_kinds_no_density_warning(self):
        cs=[item("ein mühsamer Weg"),item("auf halbem Weg"),item("den Weg versperren")]
        cs[0]["kind"]="adjective_noun";cs[2]["kind"]="verb_object"
        self.assertNotIn("SINGLE_PATTERN_FAMILY",self.codes({"combinations":cs}))

    def test_filled_technical_label_leaks(self):
        self.assertIn("TECHNICAL_KIND_LEAK",self.codes({"combinations":[item("context")]}))

    def test_does_not_mutate_input(self):
        x={"examples":["auf halbem Weg"],"combinations":[item()]}
        before=json.dumps(x,ensure_ascii=False,sort_keys=True)
        m.diagnostic(x)
        self.assertEqual(before,json.dumps(x,ensure_ascii=False,sort_keys=True))

    def test_rektion_abstract_teaching_delta(self):
        self.assertIn("REKTION_NO_INDEPENDENT_TEACHING_DELTA",self.codes({"rection":[{"de":"warten auf + Akkusativ"}]}))

    def test_structured_item_required(self):
        self.assertIn("STRUCTURED_ITEM_REQUIRED",self.codes({"combinations":["auf halbem Weg"]}))


if __name__ == "__main__":
    unittest.main()