#!/usr/bin/env python3
"""Synthetic tests for the central nonmutating morphology title gate."""
import importlib.util
import json
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "audit_visible_morphology_details_v1.py"
spec = importlib.util.spec_from_file_location("morph_gate", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MorphologyVisibleGate(unittest.TestCase):
    def row(self, name="Formen"):
        return {"id": "x1", "front": "der Hund, die Hunde",
                "details": json.dumps([{"title": name, "items": ["Genitiv: des Hundes"]}]),
                "custom_fields": json.dumps({"canonical_unit": {"morphology": {"plural": "Hunde"}}})}

    def test_internal_metadata_is_not_visible_tile(self):
        r = m.audit([self.row()])
        self.assertEqual(r["visible_morphologie_sections"], 0)
        self.assertEqual(r["internal_morphology_metadata_cards"], 1)

    def test_legacy_german_tile_flagged(self):
        self.assertEqual(m.audit([self.row("Morphologie")])["visible_morphologie_sections"], 1)

    def test_english_tile_flagged(self):
        self.assertEqual(m.audit([self.row("MORPHOLOGY")])["visible_morphologie_sections"], 1)

    def test_approved_formen_title(self):
        self.assertEqual(m.audit([self.row("Formen")])["standard_formen_sections"], 1)

    def test_invalid_details(self):
        row = self.row()
        row["details"] = "not-json"
        self.assertEqual(m.audit([row])["invalid_details_ids"], ["x1"])

    def test_duplicate_id_fail_closed(self):
        with self.assertRaises(ValueError):
            m.audit([self.row(), self.row()])

    def test_inexact_information_is_not_deleted(self):
        r = self.row()
        r["details"] = json.dumps([{"title": "Formen", "items": ["Dativ Plural: den Hunden"]}])
        self.assertEqual(m.audit([r])["full_front_formen_exact_duplicate_advisories"], [])


if __name__ == "__main__":
    unittest.main()
