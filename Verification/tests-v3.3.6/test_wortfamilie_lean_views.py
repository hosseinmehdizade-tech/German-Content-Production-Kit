"""Guardrails for optional lean Wortfamilie drift diagnostic; synthetic, non-mutating."""
import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / "audit_wortfamilie_lean_views.py"
spec = importlib.util.spec_from_file_location("wf_audit", HERE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def card(uid="c1", visible=None, canonical=None, vnext=None, related=None):
    sections = [] if visible is None else [{"title": "Wortfamilie", "items": visible}]
    return {"id": uid, "front": "fahren", "details": json.dumps(sections),
            "custom_fields": json.dumps({"canonical_relations": canonical or [],
                                         "vnext_relations": vnext or []}),
            "related": json.dumps(related or [])}
def edge(tid="c2", label="die Fahrt"):
    return {"type": "WORD_FAMILY", "target_id": tid, "label": label}

class TestWortfamilieLeanViews(unittest.TestCase):
    def audit(self, rows):
        return m.audit(rows, "1" * 64)

    def test_both_channels_one_card(self):
        x = self.audit([card(visible=["die Fahrt — سفر"], canonical=[edge()]),
                        card("c2")])
        self.assertEqual(x["counts"]["both_cards"], 1)
        self.assertEqual(x["counts"]["references_in_input"], 1)

    def test_visible_only_is_legal(self):
        x = self.audit([card(visible=["die Fahrt — سفر"])])
        self.assertEqual(x["counts"]["visible_only_cards"], 1)
        self.assertEqual(x["status"], "SCOPED_DIAGNOSTIC_NOT_STAGE_ACCEPTANCE")

    def test_typed_only_is_advisory_not_auto_error(self):
        x = self.audit([card(vnext=[edge("c2")]), card("c2")])
        self.assertEqual(x["counts"]["typed_only_cards"], 1)
        self.assertEqual(x["review_candidates"]["relation_without_visible"][0]["id"], "c1")

    def test_zero_family_is_no_quota(self):
        x = self.audit([card()])
        self.assertEqual(x["counts"]["neither_cards"], 1)
        self.assertFalse(x["new_mandatory_gate"])

    def test_related_word_family_recognized(self):
        x = self.audit([card(related=[{"relation_type": "WORD_FAMILY", "target_id": "c2"}]),
                        card("c2")])
        self.assertEqual(x["counts"]["typed_cards"], 1)

    def test_related_other_types_not_family(self):
        x = self.audit([card(related=[{"relation_type": "RELATED", "target_id": "c2"}])])
        self.assertEqual(x["counts"]["typed_cards"], 0)

    def test_duplicate_canonical_projection_not_new_unique_lexemes(self):
        x = self.audit([card(visible=["die Fahrt"], canonical=[edge()], vnext=[edge()]),
                        card("c2")])
        self.assertEqual(x["counts"]["typed_entries_across_fields"], 2)
        self.assertIn("NOT unique", x["interpretation"]["typed_entries_across_fields"])

    def test_external_target_is_not_automatically_dangling(self):
        x = self.audit([card(canonical=[edge("external-id")])])
        self.assertEqual(x["counts"]["references_outside_input"], 1)
        self.assertEqual(x["status"], "SCOPED_DIAGNOSTIC_NOT_STAGE_ACCEPTANCE")

    def test_duplicate_card_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE_ID"):
            self.audit([card("c1"), card("c1")])

    def test_empty_universe_rejected(self):
        with self.assertRaisesRegex(ValueError, "EMPTY_CARD_UNIVERSE"):
            self.audit([])

    def test_malformed_details_rejected(self):
        r = card()
        r["details"] = "{bad"
        with self.assertRaisesRegex(ValueError, "INVALID_JSON"):
            self.audit([r])

    def test_duplicate_json_key_rejected(self):
        r = card()
        r["custom_fields"] = '{"canonical_relations":[],"canonical_relations":[]}'
        with self.assertRaisesRegex(ValueError, "INVALID_JSON"):
            self.audit([r])

    def test_bad_wortfamilie_item_shape_rejected(self):
        r = card()
        r["details"] = '{"Wortfamilie":["x"]}'
        with self.assertRaisesRegex(ValueError, "INVALID_CARD_STRUCTURE"):
            self.audit([r])

    def test_original_card_data_unmodified(self):
        rows = [card(visible=["die Fahrt"], canonical=[edge()]), card("c2")]
        orig = copy.deepcopy(rows)
        self.audit(rows)
        self.assertEqual(rows, orig)

    def test_tsv_header_rejects_incomplete_data(self):
        with self.assertRaisesRegex(ValueError, "MISSING_TSV_COLUMNS"):
            m.read_tsv(b"id\tfront\nabc\tx\n")

    def test_valid_tsv_input_smoke(self):
        import csv
        import io
        a = card()
        s = io.StringIO()
        w = csv.DictWriter(s, fieldnames=list(a), delimiter="\t")
        w.writeheader()
        w.writerow(a)
        parsed = m.read_tsv(s.getvalue().encode())
        self.assertEqual(self.audit(parsed)["counts"]["cards_total"], 1)

if __name__ == "__main__":
    unittest.main()
