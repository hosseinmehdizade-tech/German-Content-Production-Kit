import copy
import importlib.util
import json
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("validate_content_sources", PACKAGE / "06-VALIDATION" / "validate_content.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)

def load(relative): return json.loads((PACKAGE / relative).read_text(encoding="utf-8"))
RULES = VALIDATOR.load_type_rules(PACKAGE / "04-TYPE-RULES")
REGISTRY = load("03-SOURCES/SOURCE-REGISTRY.json")

class SourcePolicyTests(unittest.TestCase):
    def setUp(self):
        self.dataset = load("05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json")
        self.profile = load("03-PROFILES/ARCHITECTURE-PROOF.json")

    def report(self, data=None, profile=None, registry=None):
        return VALIDATOR.validate_dataset(data or self.dataset, profile or self.profile, RULES, None, registry or REGISTRY)

    def codes(self, report): return {x["code"] for x in report["issues"]}

    def test_unknown_source_fails(self):
        d=copy.deepcopy(self.dataset); d["learning_units"][0]["provenance"]["sources"][0]["source_id"]="unknown_source"
        self.assertIn("SOURCE_UNKNOWN", self.codes(self.report(d)))

    def test_approved_but_unverified_does_not_count_as_verified(self):
        d=copy.deepcopy(self.dataset); p=copy.deepcopy(self.profile)
        p["source_policy"]["require_verified_source"]=True; p["source_policy"]["minimum_verified_sources"]=1
        src=d["learning_units"][0]["provenance"]["sources"][0]; src.update({"source_id":"duden_online","source_kind":"lexicon","what_was_verified":["german_sense"],"verification_status":"unverified"})
        self.assertIn("VERIFIED_SOURCE_REQUIRED", self.codes(self.report(d,p)))

    def test_persian_source_cannot_claim_grammar(self):
        d=copy.deepcopy(self.dataset); src=d["learning_units"][0]["provenance"]["sources"][0]
        src.update({"source_id":"wort_ir","source_kind":"lexicon","what_was_verified":["grammar"],"verification_status":"verified"})
        self.assertIn("SOURCE_CLAIM_NOT_ALLOWED", self.codes(self.report(d)))

    def test_german_grammar_authority_can_claim_grammar(self):
        d=copy.deepcopy(self.dataset); src=d["learning_units"][0]["provenance"]["sources"][0]
        src.update({"source_id":"grammis","source_kind":"website","what_was_verified":["grammar"],"verification_status":"verified"})
        dprof=copy.deepcopy(self.profile); dprof["source_policy"]["allowed_kinds"].append("website")
        self.assertNotIn("SOURCE_CLAIM_NOT_ALLOWED", self.codes(self.report(d,dprof)))

    def test_production_claim_requirements_pass_with_three_authorities(self):
        d=copy.deepcopy(self.dataset); p=load("03-PROFILES/MENSCHEN-A1.json")
        # adapt IDs/profile/schema constraints only for first unit test by changing full fixture metadata/profile ID and count remains compatible (4 default does not fit proof), so use advisory 3/2 sample-compatible policy
        p["profile_id"]=self.dataset["profile_id"]; p["dataset"]["id"]="architecture-proof"; p["id_policy"]=copy.deepcopy(self.profile["id_policy"]); p["examples"]=copy.deepcopy(self.profile["examples"]); p["allowed_types"]=copy.deepcopy(self.profile["allowed_types"]); p["type_requirements"]=copy.deepcopy(self.profile["type_requirements"]); p["allow_generic_type_rule"]=True
        for u in d["learning_units"]:
            u["provenance"]={"risk_flags":[],"sources":[
              {"source_id":"duden_online","source_kind":"lexicon","what_was_verified":["german_sense","rection"],"verification_status":"verified"},
              {"source_id":"langenscheidt_de_fa","source_kind":"lexicon","what_was_verified":["persian_gloss"],"verification_status":"verified"},
              {"source_id":"pons_de_en","source_kind":"lexicon","what_was_verified":["english_gloss"],"verification_status":"verified"}
            ]}
        r=self.report(d,p); self.assertNotIn("SOURCE_CLAIM_MIN", self.codes(r),r["issues"])

    def test_risky_claim_requires_independent_groups(self):
        d=copy.deepcopy(self.dataset); p=copy.deepcopy(self.profile)
        p["source_policy"]["claim_requirements"]={"english_gloss":{"minimum_verified_sources":1,"minimum_independent_sources_when_risky":2,"required_roles":["german_english_bilingual"]}}
        u=d["learning_units"][0]; u["provenance"]={"risk_flags":["ambiguous_sense"],"sources":[
          {"source_id":"langenscheidt_de_en","source_kind":"lexicon","what_was_verified":["english_gloss"],"verification_status":"verified"},
          {"source_id":"collins_de_en","source_kind":"lexicon","what_was_verified":["english_gloss"],"verification_status":"verified"}
        ]}
        self.assertIn("SOURCE_CLAIM_INDEPENDENCE", self.codes(self.report(d,p)))
        u["provenance"]["sources"][1]={"source_id":"pons_de_en","source_kind":"lexicon","what_was_verified":["english_gloss"],"verification_status":"verified"}
        self.assertNotIn("SOURCE_CLAIM_INDEPENDENCE", self.codes(self.report(d,p)))

    def test_rection_field_requires_dedicated_verified_claim(self):
        d=copy.deepcopy(self.dataset); p=load("03-PROFILES/MENSCHEN-A1.json")
        p["profile_id"]=self.dataset["profile_id"]; p["dataset"]["id"]="architecture-proof"; p["id_policy"]=copy.deepcopy(self.profile["id_policy"]); p["examples"]=copy.deepcopy(self.profile["examples"]); p["allowed_types"]=copy.deepcopy(self.profile["allowed_types"]); p["type_requirements"]=copy.deepcopy(self.profile["type_requirements"]); p["allow_generic_type_rule"]=True
        # Keep only first verb and provide all baseline production claims, but no rection claim.
        d["learning_units"]=[copy.deepcopy(d["learning_units"][0])]
        u=d["learning_units"][0]
        u["provenance"]={"risk_flags":[],"sources":[
          {"source_id":"duden_online","source_kind":"lexicon","what_was_verified":["german_sense","grammar"],"verification_status":"verified"},
          {"source_id":"langenscheidt_de_fa","source_kind":"lexicon","what_was_verified":["persian_gloss"],"verification_status":"verified"},
          {"source_id":"pons_de_en","source_kind":"lexicon","what_was_verified":["english_gloss"],"verification_status":"verified"}
        ]}
        self.assertIn("SOURCE_FIELD_CLAIM_MIN", self.codes(self.report(d,p)))
        u["provenance"]["sources"].append({"source_id":"grammis","source_kind":"website","what_was_verified":["rection"],"verification_status":"verified"})
        self.assertNotIn("SOURCE_FIELD_CLAIM_MIN", self.codes(self.report(d,p)))

    def test_duden_can_verify_rection_only_when_explicitly_claimed(self):
        d=copy.deepcopy(self.dataset); p=load("03-PROFILES/MENSCHEN-A1.json")
        p["profile_id"]=self.dataset["profile_id"]; p["dataset"]["id"]="architecture-proof"; p["id_policy"]=copy.deepcopy(self.profile["id_policy"]); p["examples"]=copy.deepcopy(self.profile["examples"]); p["allowed_types"]=copy.deepcopy(self.profile["allowed_types"]); p["type_requirements"]=copy.deepcopy(self.profile["type_requirements"]); p["allow_generic_type_rule"]=True
        d["learning_units"]=[copy.deepcopy(d["learning_units"][0])]
        u=d["learning_units"][0]
        u["provenance"]={"risk_flags":[],"sources":[
          {"source_id":"duden_online","source_kind":"lexicon","what_was_verified":["german_sense","rection"],"verification_status":"verified"},
          {"source_id":"langenscheidt_de_fa","source_kind":"lexicon","what_was_verified":["persian_gloss"],"verification_status":"verified"},
          {"source_id":"pons_de_en","source_kind":"lexicon","what_was_verified":["english_gloss"],"verification_status":"verified"}
        ]}
        codes=self.codes(self.report(d,p))
        self.assertNotIn("SOURCE_CLAIM_NOT_ALLOWED", codes)
        self.assertNotIn("SOURCE_FIELD_CLAIM_MIN", codes)

if __name__ == "__main__": unittest.main()
