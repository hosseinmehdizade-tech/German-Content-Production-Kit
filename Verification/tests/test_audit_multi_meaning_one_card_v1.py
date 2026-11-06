#!/usr/bin/env python3
"""Negative controls for MEM-009; no user source bytes or card mutation."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "Verification" / "audit_multi_meaning_one_card_v1.py"
spec = importlib.util.spec_from_file_location("mem009_audit", TOOL)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def meaning(sid, fa):
    return {"sense_id": sid, "fa": fa}


def example(sid, de="Das ist ein deutsches Beispiel.", fa="این یک نمونهٔ آلمانی است."):
    return {"sense_id": sid, "de": de, "fa": fa}


def card(card_id="unit-1", with_examples=True):
    return {
        "card_id": card_id, "lexical_target_id": "lexical-stelle-1",
        "front": "die Stelle",
        "meanings": [
            meaning("s1", "محل / نقطه"),
            meaning("s2", "شغل"),
            meaning("s3", "قسمتی از متن"),
        ],
        "examples": [example("s1"), example("s2")] if with_examples else [],
        "synonyms": [{"sense_id": "s2", "de": "die Arbeitsstelle"}],
    }


def codes(result):
    return {obj["code"] for obj in result["errors"]}


class Mem009Tests(unittest.TestCase):
    def test_one_card_three_meanings_two_examples_is_valid(self):
        result = audit.audit_cards([card()], "structured_json", 1)
        self.assertEqual(result["status"], "STRUCTURAL_PASS_NOT_STAGE4_5_6_7")
        self.assertEqual(result["cards_seen"], 1)
        self.assertEqual(result["unique_card_ids"], 1)
        self.assertEqual(result["per_sense_example_missing_info_only"], 1)
        self.assertNotIn("PER_SENSE_EXAMPLE_MISSING", codes(result))

    def test_no_examples_per_sense_is_not_a_blocker(self):
        result = audit.audit_cards([card(with_examples=False)], "structured_json")
        self.assertEqual(result["status"], "STRUCTURAL_PASS_NOT_STAGE4_5_6_7")
        self.assertEqual(result["per_sense_example_missing_info_only"], 3)
        self.assertEqual(result["errors"], [])

    def test_missing_persian_example_is_blocker(self):
        item = card()
        item["examples"][0]["fa"] = ""
        result = audit.audit_cards([item], "structured_json")
        self.assertIn("EXAMPLE_BILINGUAL_PAIR_BROKEN", codes(result))

    def test_wrong_example_sense_is_blocker(self):
        item = card()
        item["examples"][0]["sense_id"] = "not-a-sense"
        result = audit.audit_cards([item], "structured_json")
        self.assertIn("EXAMPLE_UNKNOWN_SENSE", codes(result))

    def test_wrong_synonym_sense_is_blocker(self):
        item = card()
        item["synonyms"][0]["sense_id"] = "not-a-sense"
        result = audit.audit_cards([item], "structured_json")
        self.assertIn("RELATION_UNKNOWN_SENSE", codes(result))

    def test_duplicate_card_id_is_blocker(self):
        result = audit.audit_cards([card(), card()], "structured_json")
        self.assertIn("CARD_ID_DUPLICATE", codes(result))

    def test_same_explicit_lexical_target_split_is_blocker(self):
        result = audit.audit_cards([card("unit-1"), card("unit-2")], "structured_json")
        self.assertIn("LEXICAL_TARGET_SPLIT", codes(result))

    def test_same_written_front_not_auto_merged(self):
        left, right = card("unit-1"), card("unit-2")
        right["lexical_target_id"] = "different-homograph-identity"
        result = audit.audit_cards([left, right], "structured_json")
        self.assertEqual(result["status"], "STRUCTURAL_PASS_NOT_STAGE4_5_6_7")

    def test_no_fabricated_senses_from_farsi_delimiters(self):
        preview = {
            "unit_id": "ab2-l01-u-1552",
            "front_de_preview": "auflösen; löst auf, löste auf, hat aufgelöst",
            "back_fa_preview": "منحل کردن؛ بستن حساب؛ حل کردن در مایع",
            "example_1_de": "Die Polizei löste die Versammlung auf.",
            "example_1_fa": "پلیس تجمع را متفرق کرد.",
            "example_2_de": "Sie löste die Wohnung auf.",
            "example_2_fa": "او خانه را تخلیه کرد.",
            "export_importable": "FALSE",
        }
        result = audit.audit_cards([preview], "flat_csv")
        self.assertEqual(result["status"], "STRUCTURAL_PASS_NOT_STAGE4_5_6_7")
        self.assertEqual(result["structured_sense_cards"], 0)
        self.assertEqual(result["untyped_sense_cards"], 1)
        self.assertEqual(result["per_sense_example_missing_info_only"], 0)
        self.assertEqual(result["examples_paired"], 2)

    def test_missing_typed_meaning_translation_fails(self):
        item = card()
        item["meanings"][1]["fa"] = ""
        self.assertIn("SENSE_FA_MISSING",
                      codes(audit.audit_cards([item], "structured_json")))

    def test_missing_typed_sense_identifier_fails(self):
        item = card()
        item["meanings"][1]["sense_id"] = ""
        self.assertIn("SENSE_ID_MISSING",
                      codes(audit.audit_cards([item], "structured_json")))

    def test_expected_card_count_guards_against_loss(self):
        self.assertIn("COUNT_MISMATCH",
                      codes(audit.audit_cards([card()], "structured_json", 2)))

    def test_flat_csv_source_is_read_only(self):
        row = {
            "unit_id": "ab2-l01-u-1552",
            "back_fa_preview": "منحل کردن؛ بستن حساب",
            "example_1_de": "Das gilt.",
            "example_1_fa": "این معتبر است.",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "native-b2-preview.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=row.keys())
                writer.writeheader()
                writer.writerow(row)
            before = path.read_bytes()
            cards, profile = audit.load_cards(path)
            result = audit.audit_cards(cards, profile, 1)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(result["status"], "STRUCTURAL_PASS_NOT_STAGE4_5_6_7")
            self.assertFalse(result["content_mutated"])

    def test_typed_json_load_does_not_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cards.json"
            path.write_text(json.dumps({"cards": [card()]}), encoding="utf-8")
            before = path.read_bytes()
            rows, profile = audit.load_cards(path)
            result = audit.audit_cards(rows, profile, 1)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(result["status"], "STRUCTURAL_PASS_NOT_STAGE4_5_6_7")

    def test_missing_example_sense_metadata_not_misrepresented_as_bad(self):
        item = card()
        for e in item["examples"]:
            del e["sense_id"]
        result = audit.audit_cards([item], "structured_json")
        self.assertEqual(result["status"], "STRUCTURAL_PASS_NOT_STAGE4_5_6_7")
        self.assertEqual(result["per_sense_example_missing_info_only"], 3)


if __name__ == "__main__":
    unittest.main()
