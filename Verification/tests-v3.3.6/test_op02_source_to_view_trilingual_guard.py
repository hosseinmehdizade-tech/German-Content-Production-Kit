#!/usr/bin/env python3
"""Synthetic nonactive OP02 source-to-view guard tests; no learner data writes."""
import csv
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import op02_source_to_view_trilingual_guard as guard


def card(items, physical, card_id="a"):
    return {
        "id": card_id,
        "custom_fields": json.dumps({"kombinationen_v1": {
            "visible_section": "Kombinationen", "items": items
        }}, ensure_ascii=False),
        "details": json.dumps([{"title":"Kombinationen","items":physical}], ensure_ascii=False)
    }


ITEM = {"de": "eine Frage stellen", "fa":"سؤال پرسیدن", "en":"to ask a question"}


class PhysicalCoverage(unittest.TestCase):
    def test_full_trilingual(self):
        report=guard.audit([card([ITEM],["eine Frage stellen — سؤال پرسیدن — to ask a question"])])
        self.assertEqual(report["counts"], {"PHYSICAL_DE_FA_EN_STRING":1})
        self.assertEqual(report["unresolved_or_unproven"],0)
        self.assertFalse(report["stage6_pass"])

    def test_bilingual_english_gap(self):
        report=guard.audit([card([ITEM],["eine Frage stellen — سؤال پرسیدن"])])
        self.assertEqual(report["counts"], {"PHYSICAL_DE_FA_ONLY":1})
        self.assertEqual(report["status"],"BLOCKED_SOURCE_TO_VIEW_EVIDENCE")

    def test_structured_object_not_automatic_dom_pass(self):
        report=guard.audit([card([ITEM],[dict(ITEM,kind="collocation")])])
        self.assertEqual(report["counts"], {"PHYSICAL_OBJECT_RENDER_PAIRING_UNPROVEN":1})

    def test_partial_section_preempts_projection(self):
        report=guard.audit([card([ITEM],["another phrase"])])
        self.assertEqual(report["counts"], {"PARTIAL_SECTION_PREEMPTED":1})

    def test_empty_section_only_bridge_candidate(self):
        report=guard.audit([card([ITEM],[])])
        self.assertEqual(report["counts"], {"BRIDGE_DE_FA_ONLY_DOM_UNPROVEN":1})

    def test_duplicate_representation_fails_closed(self):
        with self.assertRaises(ValueError):
            guard.classify(ITEM, ["eine Frage stellen — سؤال پرسیدن",
                                  "eine Frage stellen — سؤال پرسیدن — to ask a question"],{})

    def test_repeated_identical_physical_line_rejected(self):
        full = "eine Frage stellen — سؤال پرسیدن — to ask a question"
        self.assertRaises(ValueError, guard.classify, ITEM, [full, full], {})

    def test_missing_fa_rejected(self):
        with self.assertRaises(ValueError):
            guard.classify({"de":"eine Frage stellen","fa":"","en":"ask"},[],{})

    def test_duplicate_card_rejected(self):
        x=card([ITEM],[]);self.assertRaises(ValueError,guard.audit,[x,x])

    def test_duplicate_combination_sections_rejected(self):
        x=card([ITEM],[])
        x["details"]=json.dumps([{"title":"Kombinationen","items":["a"]},
                                  {"title":"Kombinationen","items":["b"]}])
        self.assertRaises(ValueError,guard.audit,[x])

    def test_bad_json_duplicate_key_rejected(self):
        self.assertRaises(ValueError,guard.strict_json,'{"a":1,"a":2}')

    def test_object_values_not_physical_pairing_proof(self):
        report=guard.audit([card([ITEM],[{"de":ITEM["de"],"fa":ITEM["fa"],"en":ITEM["en"]}])])
        self.assertFalse(report["stage7_pass"])

    def test_empty_universe_is_not_stage6_pass(self):
        report=guard.audit([card([],[])])
        self.assertFalse(report["stage6_pass"])
        self.assertFalse(report["stage7_pass"])


if __name__=="__main__":
    unittest.main()
