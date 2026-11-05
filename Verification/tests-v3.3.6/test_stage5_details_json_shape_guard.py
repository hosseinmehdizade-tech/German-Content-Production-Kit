"""Stage5 central vocabulary validator: details JSON shape fail-closed tests.

No registered learner cards are changed; all fixture builds are disposable.
"""
import copy
import csv
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "Verification" / "validate_unified_vocabulary_projection_v1_1_0.py"
BUILDER = ROOT / "Tools" / "build_clean_delivery.py"
spec = importlib.util.spec_from_file_location("stage5_neutral_validator", VALIDATOR)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def demo(details="[]"):
    return {
        "id": "synthetic-1", "card_type": "de-vocabulary",
        "category": "Verb", "front": "gehen", "back": "رفتن",
        "details": details,
        "custom_fields": json.dumps({"presentation_contract": "gfp-vocabulary-neutral@1"}),
    }


def codes(*rows):
    return [x["error"] for x in validator.validate(list(rows))["errors"]]


def write_tsv(path, cards):
    columns = list(cards[0])
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(cards)


def builder_trial(rows):
    with tempfile.TemporaryDirectory(prefix="gcpk-details-shape-fixture-") as tmp:
        root = Path(tmp)
        source = root / "source"
        source.mkdir()
        dest = root / "output"
        dest.mkdir()
        import_path = source / "Synthetic-Universal.tsv"
        write_tsv(import_path, rows)
        (source / "Synthetic-canonical.json").write_text("{}\n", encoding="utf-8")
        (source / "Synthetic-source-output-map.tsv").write_text("id\tstatus\nsynthetic-1\tfixture\n", encoding="utf-8")
        (source / "Synthetic-QA.json").write_text('{"status":"FIXTURE_NOT_STAGE4"}\n', encoding="utf-8")
        output = dest / "Synthetic-Stage5.zip"
        original = import_path.read_bytes()
        result = subprocess.run(
            [sys.executable, str(BUILDER), str(source), str(output),
             "--purpose", "stage5_acceptance"],
            capture_output=True, text=True, timeout=70,
        )
        assert import_path.read_bytes() == original, "SOURCE_TSV_WAS_MUTATED"
        return result.returncode, (result.stdout + result.stderr), output.exists()


class TestVisibleDetailsCentralGate(unittest.TestCase):
    def test_valid_empty_details(self):
        self.assertEqual(codes(demo()), [])

    def test_legacy_absent_optional_details_still_accepted(self):
        c = demo()
        del c["details"]
        self.assertEqual(codes(c), [])

    def test_valid_full_section_and_persian_metadata(self):
        details = [{"title": "Verwandte Wörter", "items": [
            {"de": "Bewegung", "fa": "حرکت", "en": "movement"}, "die Bewegung"
        ]}]
        self.assertEqual(codes(demo(json.dumps(details, ensure_ascii=False))), [])

    def test_non_json_b1_l19_prose_fails_closed(self):
        self.assertIn("INVALID_DETAILS_JSON", codes(demo("Ein etwas längerer deutscher Beschreibungstext.")))

    def test_plain_json_string_is_not_array(self):
        self.assertIn("DETAILS_NOT_LIST", codes(demo('"Deutscher Fließtext"')))

    def test_object_is_not_array(self):
        self.assertIn("DETAILS_NOT_LIST", codes(demo('{"title":"Verwandte Wörter","items":[]}')))

    def test_json_null_is_not_array(self):
        self.assertIn("DETAILS_NOT_LIST", codes(demo("null")))

    def test_blank_present_cell_is_not_silently_converted(self):
        self.assertIn("INVALID_DETAILS_JSON", codes(demo("")))

    def test_array_element_must_be_object(self):
        self.assertIn("DETAIL_SECTION_NOT_OBJECT", codes(demo('["Verwandte Wörter"]')))

    def test_array_object_requires_title(self):
        self.assertIn("DETAIL_SECTION_TITLE_MISSING", codes(demo('[{"items": []}]')))

    def test_array_object_requires_items_list(self):
        self.assertIn("DETAIL_SECTION_ITEMS_NOT_LIST", codes(demo('[{"title":"Wortfamilie","items":"die Fahrt"}]')))

    def test_json_native_projection_list_allowed(self):
        c = demo([{"title":"Wortfamilie","items":["die Fahrt"]}])
        self.assertEqual(codes(c), [])

    def test_every_b1_l19_row_is_individually_rejected(self):
        rows = []
        for n in range(145):
            c = demo("Deutscher Langtext statt JSON.")
            c["id"] = f"synthetic-b1-l19-{n+1:03d}"
            rows.append(c)
        result = validator.validate(rows)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(len([e for e in result["errors"] if e["error"] == "INVALID_DETAILS_JSON"]), 145)

    def test_validator_does_not_mutate_source_objects(self):
        c = demo('[{"title":"Kombinationen","items":["auf den Bus warten"]}]')
        original = copy.deepcopy(c)
        validator.validate([c])
        self.assertEqual(c, original)

    def test_actual_builder_rejects_prose_before_creating_zip(self):
        returncode, output, produced = builder_trial([demo("B1-L19 Prosa statt JSON")])
        self.assertNotEqual(returncode, 0)
        self.assertFalse(produced)
        self.assertIn("INVALID_DETAILS_JSON", output)

    def test_actual_builder_rejects_invalid_nested_section(self):
        returncode, output, produced = builder_trial([demo('[{"title":"Wortfamilie","items":"nicht-Liste"}]')])
        self.assertNotEqual(returncode, 0)
        self.assertFalse(produced)
        self.assertIn("DETAIL_SECTION_ITEMS_NOT_LIST", output)

    def test_actual_builder_accepts_valid_details(self):
        returncode, output, produced = builder_trial([demo('[{"title":"Wortfamilie","items":["die Fahrt"]}]')])
        self.assertEqual(returncode, 0, output)
        self.assertTrue(produced)

    def test_actual_builder_preserves_legacy_missing_column(self):
        c = demo()
        del c["details"]
        returncode, output, produced = builder_trial([c])
        self.assertEqual(returncode, 0, output)
        self.assertTrue(produced)


if __name__ == "__main__":
    unittest.main()
