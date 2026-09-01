import copy
import importlib.util
import json
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("validate_content_v312", PACKAGE / "06-VALIDATION" / "validate_content.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


def load(relative):
    return json.loads((PACKAGE / relative).read_text(encoding="utf-8"))


RULES = VALIDATOR.load_type_rules(PACKAGE / "04-TYPE-RULES")
REGISTRY = load("03-SOURCES/SOURCE-REGISTRY.json")


class V312PatchTests(unittest.TestCase):
    def setUp(self):
        self.dataset = load("05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json")
        self.proof_profile = load("03-PROFILES/ARCHITECTURE-PROOF.json")

    def validate(self, dataset=None, profile=None):
        return VALIDATOR.validate_dataset(dataset or self.dataset, profile or self.proof_profile, RULES, None, REGISTRY)

    def noun(self, dataset, headword="Entscheidung"):
        return next(unit for unit in dataset["learning_units"] if unit["headword"] == headword)

    def test_plural_only_nomen_without_singular_is_valid(self):
        data = copy.deepcopy(self.dataset)
        noun = self.noun(data)
        noun["headword"] = "Eltern"
        noun["core"] = {
            "article": "die",
            "plural": "Eltern",
            "plural_only": True,
        }
        report = self.validate(data)
        self.assertEqual("PASS", report["structural_typed_status"], report["issues"])

    def test_normal_singular_nomen_is_valid(self):
        noun = self.noun(self.dataset)
        self.assertIs(noun["core"]["plural_only"], False)
        self.assertTrue(noun["core"]["singular"])
        report = self.validate()
        self.assertEqual("PASS", report["structural_typed_status"], report["issues"])

    def test_nomen_without_useful_plural_is_valid(self):
        data = copy.deepcopy(self.dataset)
        profile = copy.deepcopy(self.proof_profile)
        profile["type_requirements"]["nomen"]["required_core_fields"] = ["article"]
        noun = self.noun(data)
        noun["core"].pop("plural")
        noun["core"]["plural_only"] = False
        report = self.validate(data, profile)
        self.assertEqual("PASS", report["structural_typed_status"], report["issues"])

    def test_plural_only_nomen_without_plural_is_rejected(self):
        data = copy.deepcopy(self.dataset)
        noun = self.noun(data)
        noun["core"].pop("singular")
        noun["core"].pop("plural")
        noun["core"]["plural_only"] = True
        report = self.validate(data)
        self.assertEqual("FAIL", report["structural_typed_status"])
        self.assertIn("TYPED_FIELD_CONDITIONAL", {issue["code"] for issue in report["issues"]})

    def test_plural_only_discriminator_is_typed(self):
        data = copy.deepcopy(self.dataset)
        self.noun(data)["core"]["plural_only"] = "false"
        report = self.validate(data)
        self.assertEqual("FAIL", report["structural_typed_status"])
        self.assertIn("VALUE_TYPE", {issue["code"] for issue in report["issues"]})

    def test_menschen_a1_uses_default_count_and_does_not_force_plural(self):
        profile = load("03-PROFILES/MENSCHEN-A1.json")
        issues = []
        VALIDATOR.validate_configuration(profile, RULES, issues, REGISTRY)
        self.assertEqual([], issues)
        self.assertEqual({}, profile["examples"]["by_type"])
        self.assertNotIn("plural", profile["type_requirements"]["nomen"]["required_core_fields"])
        for unit_type in ("nomen", "verb", "satz", "satzmuster"):
            self.assertEqual(4, VALIDATOR.resolve_count_policy(profile, unit_type)["target"])

    def test_architecture_proof_keeps_example_override_capability(self):
        self.assertIn("verb", self.proof_profile["examples"]["by_type"])
        self.assertEqual(3, VALIDATOR.resolve_count_policy(self.proof_profile, "verb")["target"])
        self.assertEqual(2, VALIDATOR.resolve_count_policy(self.proof_profile, "nomen")["target"])

    def test_phrase_family_does_not_require_artificial_function(self):
        data = copy.deepcopy(self.dataset)
        phrase_types = {"redemittel", "phrase", "idiom", "redewendung", "kollokation", "nomen_verb_verbindung"}
        for unit in data["learning_units"]:
            if unit["type"] in phrase_types:
                unit["core"].pop("function", None)
        report = self.validate(data)
        self.assertEqual("PASS", report["structural_typed_status"], report["issues"])


if __name__ == "__main__":
    unittest.main()
