import json
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[2]


def load(relative):
    return json.loads((PACKAGE / relative).read_text(encoding="utf-8"))


class SchemaInvariantTests(unittest.TestCase):
    def test_all_json_artifacts_parse(self):
        for path in PACKAGE.rglob("*.json"):
            with self.subTest(path=path.relative_to(PACKAGE)):
                json.loads(path.read_text(encoding="utf-8"))

    def test_canonical_schema_has_no_example_count(self):
        schema = load("02-SCHEMAS/LEARNING-UNIT-SCHEMA.json")
        examples = schema["$defs"]["learningUnit"]["properties"]["examples"]
        self.assertNotIn("minItems", examples)
        self.assertNotIn("maxItems", examples)

    def test_connection_kinds_are_semantic(self):
        schema = load("02-SCHEMAS/CONNECTION-SCHEMA.json")
        kinds = set(schema["properties"]["kind"]["enum"])
        self.assertIn("nvv", kinds)
        self.assertIn("collocation", kinds)
        self.assertNotIn("left_column", kinds)
        self.assertNotIn("visual_box", kinds)

    def test_type_rules_contain_typed_field_specs(self):
        for path in (PACKAGE / "04-TYPE-RULES").glob("*.json"):
            rule = json.loads(path.read_text(encoding="utf-8"))
            for scope in ("core_fields", "detail_fields"):
                for name, spec in rule[scope].items():
                    with self.subTest(rule=path.name, scope=scope, field=name):
                        self.assertIn(spec["type"], {"string", "boolean", "integer", "number", "array", "object"})
                        self.assertIsInstance(spec["required"], bool)
                        self.assertIsInstance(spec["nullable"], bool)

    def test_count_policy_lives_in_profiles(self):
        targets = {
            load("03-PROFILES/ARCHITECTURE-PROOF.json")["examples"]["default"]["target"],
            load("03-PROFILES/MENSCHEN-A1.json")["examples"]["default"]["target"],
            load("03-PROFILES/INDEPENDENT-B1.json")["examples"]["default"]["target"],
        }
        self.assertEqual({2, 4, 5}, targets)
        for path in (PACKAGE / "04-TYPE-RULES").glob("*.json"):
            rendered = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("count_policy", rendered)
            self.assertNotIn("target_examples", rendered)

    def test_gloss_and_sentence_translation_are_separate(self):
        dataset = load("05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json")
        for unit in dataset["learning_units"]:
            self.assertIn("english_gloss", unit)
            for example in unit["examples"]:
                self.assertNotIn("english_gloss", example)
                self.assertEqual(1, sum(item["lang"] == "en-US" for item in example["translations"]))

    def test_sample_has_distinct_nvv_and_collocation_connections(self):
        dataset = load("05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json")
        decision = next(unit for unit in dataset["learning_units"] if unit["headword"] == "Entscheidung")
        kinds = {item["kind"] for item in decision["connections"]}
        self.assertIn("nvv", kinds)
        self.assertIn("collocation", kinds)


    def test_translation_requiredness_is_profile_driven_not_global(self):
        contract=(PACKAGE / "01-CORE/GERMAN-LANGUAGE-CONTENT-CONTRACT-v3.1.3.md").read_text(encoding="utf-8")
        self.assertIn("زبان‌های required را Profile تعیین می‌کند", contract)
        prompt=(PACKAGE / "01-CORE/CONTENT-GENERATION-MASTER-PROMPT-v3.1.5.md").read_text(encoding="utf-8")
        self.assertIn("رابطه ثابت است، اجبار زبان ثابت نیست", prompt)

if __name__ == "__main__":
    unittest.main()
