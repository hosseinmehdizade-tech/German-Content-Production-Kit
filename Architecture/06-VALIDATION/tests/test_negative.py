import copy
import importlib.util
import json
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("validate_content_negative", PACKAGE / "06-VALIDATION" / "validate_content.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


def load(relative):
    return json.loads((PACKAGE / relative).read_text(encoding="utf-8"))


RULES = VALIDATOR.load_type_rules(PACKAGE / "04-TYPE-RULES")
REGISTRY = load("03-SOURCES/SOURCE-REGISTRY.json")


class NegativeValidationTests(unittest.TestCase):
    def setUp(self):
        self.dataset = load("05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json")
        self.profile = load("03-PROFILES/ARCHITECTURE-PROOF.json")

    def assert_fails_with(self, dataset, code, profile=None):
        report = VALIDATOR.validate_dataset(dataset, profile or self.profile, RULES, None, REGISTRY)
        self.assertEqual("FAIL", report["structural_typed_status"])
        codes = {item["code"] for item in report["issues"]}
        self.assertIn(code, codes, report["issues"])

    def test_boolean_as_string_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][0]["core"]["reflexive"] = "sometimes"
        self.assert_fails_with(data, "VALUE_TYPE")

    def test_array_instead_of_string_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][0]["core"]["present_3sg"] = ["hängt ab"]
        self.assert_fails_with(data, "VALUE_TYPE")

    def test_object_instead_of_string_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][0]["core"]["perfect"] = {"value": True}
        self.assert_fails_with(data, "VALUE_TYPE")

    def test_invalid_enum_value_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][0]["core"]["auxiliary"] = "sometimes"
        self.assert_fails_with(data, "VALUE_ENUM")

    def test_invalid_nested_object_property_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][1]["core"]["imperative"]["wir"] = "Melden wir uns an!"
        self.assert_fails_with(data, "VALUE_OBJECT_UNKNOWN")

    def test_invalid_connection_kind_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][2]["connections"][0]["kind"] = "visual_box"
        self.assert_fails_with(data, "CONNECTION_KIND_INVALID")

    def test_connections_scalar_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][0]["connections"] = "von etwas abhängen"
        self.assert_fails_with(data, "CONNECTIONS_TYPE")

    def test_duplicate_example_id_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][1]["examples"][0]["id"] = data["learning_units"][0]["examples"][0]["id"]
        self.assert_fails_with(data, "EXAMPLE_ID_DUPLICATE")

    def test_missing_fa_translation_fails(self):
        data = copy.deepcopy(self.dataset)
        example = data["learning_units"][0]["examples"][0]
        example["translations"] = [item for item in example["translations"] if item["lang"] != "fa-IR"]
        self.assert_fails_with(data, "TRANSLATION_REQUIRED")

    def test_missing_en_translation_fails(self):
        data = copy.deepcopy(self.dataset)
        example = data["learning_units"][0]["examples"][0]
        example["translations"] = [item for item in example["translations"] if item["lang"] != "en-US"]
        self.assert_fails_with(data, "TRANSLATION_REQUIRED")

    def test_invalid_sense_reference_fails(self):
        data = copy.deepcopy(self.dataset)
        castle = next(unit for unit in data["learning_units"] if unit["headword"] == "Schloss")
        castle["examples"][0]["sense_id"] = "sense-99"
        self.assert_fails_with(data, "EXAMPLE_SENSE_UNKNOWN")

    def test_too_few_default_examples_fails(self):
        data = copy.deepcopy(self.dataset)
        noun = next(unit for unit in data["learning_units"] if unit["type"] == "nomen")
        noun["examples"].pop()
        self.assert_fails_with(data, "EXAMPLE_COUNT_EXACT")

    def test_too_few_per_type_override_examples_fails(self):
        data = copy.deepcopy(self.dataset)
        verb = next(unit for unit in data["learning_units"] if unit["type"] == "verb")
        verb["examples"].pop()
        self.assert_fails_with(data, "EXAMPLE_COUNT_EXACT")

    def test_too_many_examples_fails(self):
        data = copy.deepcopy(self.dataset)
        noun = next(unit for unit in data["learning_units"] if unit["type"] == "nomen")
        extra = copy.deepcopy(noun["examples"][-1])
        extra["id"] = f"{noun['id']}-ex-003"
        extra["order"] = 3
        noun["examples"].append(extra)
        self.assert_fails_with(data, "EXAMPLE_COUNT_EXACT")

    def test_invalid_language_tag_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][0]["examples"][0]["translations"][0]["lang"] = "not a tag"
        self.assert_fails_with(data, "LANGUAGE_TAG_INVALID")

    def test_duplicate_order_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][0]["examples"][1]["order"] = 1
        self.assert_fails_with(data, "ORDER_DUPLICATE")

    def test_english_gloss_inside_example_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][0]["examples"][0]["english_gloss"] = "depend"
        self.assert_fails_with(data, "EXAMPLE_FIELD_UNKNOWN")

    def test_unknown_core_field_fails(self):
        data = copy.deepcopy(self.dataset)
        data["learning_units"][0]["core"]["a1_only_badge"] = True
        self.assert_fails_with(data, "TYPED_FIELD_UNKNOWN")

    def test_active_retired_id_fails(self):
        data = copy.deepcopy(self.dataset)
        unit = data["learning_units"][0]
        unit["metadata"]["retired_example_ids"] = [unit["examples"][0]["id"]]
        self.assert_fails_with(data, "RETIRED_ID_ACTIVE")

    def test_profile_cannot_require_undeclared_field(self):
        profile = copy.deepcopy(self.profile)
        profile["type_requirements"]["verb"] = {"required_core_fields": ["future_magic"], "required_detail_fields": []}
        self.assert_fails_with(copy.deepcopy(self.dataset), "PROFILE_CORE_REQUIREMENT_UNKNOWN", profile)


if __name__ == "__main__":
    unittest.main()
