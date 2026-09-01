import copy
import importlib.util
import json
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("validate_content", PACKAGE / "06-VALIDATION" / "validate_content.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


def load(relative):
    return json.loads((PACKAGE / relative).read_text(encoding="utf-8"))


RULES = VALIDATOR.load_type_rules(PACKAGE / "04-TYPE-RULES")
REGISTRY = load("03-SOURCES/SOURCE-REGISTRY.json")


class PositiveValidationTests(unittest.TestCase):
    def setUp(self):
        self.dataset = load("05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json")
        self.profile = load("03-PROFILES/ARCHITECTURE-PROOF.json")

    def validate(self, dataset=None, profile=None, previous=None):
        return VALIDATOR.validate_dataset(dataset or self.dataset, profile or self.profile, RULES, previous, REGISTRY)

    def test_multi_type_sample_passes_typed_validation(self):
        report = self.validate()
        self.assertEqual("PASS", report["structural_typed_status"], report["issues"])
        self.assertEqual(10, report["counts"]["learning_units"])
        self.assertEqual(22, report["counts"]["examples"])
        self.assertEqual(22, report["counts"]["translations_by_language"]["fa-IR"])
        self.assertEqual(22, report["counts"]["translations_by_language"]["en-US"])
        self.assertEqual("NOT_RUN", report["linguistic_status"])

    def test_per_type_count_override_is_resolved(self):
        self.assertEqual(2, VALIDATOR.resolve_count_policy(self.profile, "nomen")["target"])
        self.assertEqual(3, VALIDATOR.resolve_count_policy(self.profile, "verb")["target"])
        verbs = [unit for unit in self.dataset["learning_units"] if unit["type"] == "verb"]
        nouns = [unit for unit in self.dataset["learning_units"] if unit["type"] == "nomen"]
        self.assertTrue(all(len(unit["examples"]) == 3 for unit in verbs))
        self.assertTrue(all(len(unit["examples"]) == 2 for unit in nouns))

    def test_optional_english_profile_does_not_require_english(self):
        dataset = copy.deepcopy(self.dataset)
        profile = copy.deepcopy(self.profile)
        next(item for item in profile["languages"]["translations"] if item["lang"] == "en-US")["required"] = False
        for unit in dataset["learning_units"]:
            for example in unit["examples"]:
                example["translations"] = [item for item in example["translations"] if item["lang"] != "en-US"]
        report = self.validate(dataset, profile)
        self.assertEqual("PASS", report["structural_typed_status"], report["issues"])
        self.assertNotIn("en-US", report["counts"]["translations_by_language"])

    def test_text_edit_and_reorder_preserve_identity(self):
        previous = copy.deepcopy(self.dataset)
        current = copy.deepcopy(self.dataset)
        examples = current["learning_units"][0]["examples"]
        examples[0]["text"] = "Das hängt heute vom Wetter ab."
        examples.reverse()
        for index, example in enumerate(examples, start=1):
            example["order"] = index
        report = self.validate(current, previous=previous)
        self.assertEqual("PASS", report["structural_typed_status"], report["issues"])

    def test_all_requested_type_families_resolve(self):
        profile = load("03-PROFILES/MENSCHEN-A1.json")
        unresolved = [unit_type for unit_type in profile["allowed_types"] if VALIDATOR.find_rule(unit_type, profile, RULES) is None]
        self.assertEqual([], unresolved)

    def test_primary_unit_type_and_related_connection_are_distinct(self):
        decision = next(unit for unit in self.dataset["learning_units"] if unit["headword"] == "Entscheidung")
        nvv = next(unit for unit in self.dataset["learning_units"] if unit["type"] == "nomen_verb_verbindung")
        self.assertTrue(any(item["kind"] == "nvv" and item["text"] == nvv["headword"] for item in decision["connections"]))
        self.assertEqual("nomen", decision["type"])

    def test_advanced_verb_capabilities_are_typed_and_accepted(self):
        register = next(unit for unit in self.dataset["learning_units"] if unit["headword"] == "sich anmelden")
        self.assertIsInstance(register["core"]["imperative"], dict)
        self.assertIs(register["core"]["reflexive"], True)
        report = self.validate()
        self.assertEqual("PASS", report["structural_typed_status"], report["issues"])


if __name__ == "__main__":
    unittest.main()
