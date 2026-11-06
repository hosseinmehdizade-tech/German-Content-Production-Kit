"""Fast read-only regression: curate current, do not resurrect deleted textbook rows."""
from __future__ import annotations
import importlib.util
import io
import json
from pathlib import Path
import contextlib
import hashlib
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "audit_curated_current_delta_v1.py"
spec = importlib.util.spec_from_file_location("curated_delta", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestCuratedCurrentDelta(unittest.TestCase):
    def test_first_verified_curated_baseline_does_not_require_book(self):
        cards = mod.records(b"id\tfront\tback\nnew-word\tneues Wort\t\xd8\xaa\n", ".tsv")
        result = mod.analyze(cards)
        self.assertEqual(result["status"], "BASELINE_STRUCTURAL_PASS_NOT_SEMANTIC")
        self.assertFalse(result["original_book_row_equality_required"])
        self.assertEqual(result["current_count"], 1)

    def test_addition_not_in_old_book_is_valid_delta_scope(self):
        before = {"a": {"id": "a", "front": "alt"}}
        after = {**before, "b": {"id": "b", "front": "neu"}}
        result = mod.analyze(after, before)
        self.assertEqual(result["status"], "DELTA_STRUCTURAL_PASS_NOT_SEMANTIC")
        self.assertEqual(result["added"], ["b"])
        self.assertEqual(result["review_scope"], ["b"])

    def test_unreviewed_new_deletion_fails_closed(self):
        before = {"a": {"id": "a", "front": "alt"}, "b": {"id": "b", "front": "keep"}}
        after = {"b": before["b"]}
        result = mod.analyze(after, before)
        self.assertEqual(result["status"], "HOLD_REMOVAL_DECISION")
        self.assertEqual(result["decision_holds"], ["a"])

    def test_approved_deletion_is_not_resurrected(self):
        before = {"a": {"id": "a", "front": "alt"}, "b": {"id": "b", "front": "keep"}}
        after = {"b": before["b"]}
        decisions = {"a": {"operation": "REMOVED", "disposition": "USER_APPROVED", "reason": "duplicate"}}
        result = mod.analyze(after, before, decisions)
        self.assertEqual(result["status"], "DELTA_STRUCTURAL_PASS_NOT_SEMANTIC")
        self.assertEqual(result["removed"], ["a"])
        self.assertFalse(result["decision_holds"])

    def test_old_approved_removal_is_not_replayed_for_baseline(self):
        current = {"b": {"id": "b", "front": "keep"}}
        result = mod.analyze(current)
        self.assertEqual(result["status"], "BASELINE_STRUCTURAL_PASS_NOT_SEMANTIC")
        self.assertEqual(result["review_scope"], [])

    def test_modification_scopes_review_not_unchanged(self):
        before = {"a": {"id": "a", "front": "alt"}, "b": {"id": "b", "front": "unchanged"}}
        after = {"a": {"id": "a", "front": "verbessert"}, "b": before["b"]}
        result = mod.analyze(after, before)
        self.assertEqual(result["modified"], ["a"])
        self.assertEqual(result["unchanged"], 1)
        self.assertEqual(result["review_scope"], ["a"])

    def test_duplicate_ids_rejected(self):
        with self.assertRaisesRegex(mod.DeltaError, "DUPLICATE_ID"):
            mod.records(b"id\tfront\na\tone\na\ttwo\n", ".tsv")

    def test_bad_tsv_row_rejected(self):
        with self.assertRaisesRegex(mod.DeltaError, "MALFORMED_TABULAR_ROW"):
            mod.records(b"id\tfront\na\tone\textra\n", ".tsv")

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(mod.DeltaError, "DUPLICATE_JSON_KEY"):
            mod.records(b'[{"id":"a","id":"b"}]', ".json")

    def test_bad_deleted_reason_fails(self):
        d = {"a": {"operation": "REMOVED", "disposition": "REVIEWED_CURATED", "reason": ""}}
        res = mod.analyze({}, {"a": {"id": "a"}}, d)
        self.assertEqual(res["decision_holds"], ["a"])

    def test_cli_hash_pinned_baseline_and_no_file_edit(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "CURRENT.tsv"
            original = b"id\tfront\tback\na\tneu\tnew\n"
            p.write_bytes(original)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = mod.main(["--current", str(p),
                               "--expected-current-sha256", hashlib.sha256(original).hexdigest()])
            self.assertEqual(rc, 0)
            self.assertIn("BASELINE_STRUCTURAL_PASS_NOT_SEMANTIC", out.getvalue())
            self.assertEqual(p.read_bytes(), original)

    def test_cli_wrong_hash_does_not_read_as_current(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "CURRENT.tsv"
            p.write_text("id\tfront\na\ttest\n", encoding="utf8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = mod.main(["--current", str(p), "--expected-current-sha256", "0"*64])
            self.assertEqual(rc, 2)
            self.assertIn("CURRENT_HASH_MISMATCH", out.getvalue())


if __name__ == "__main__":
    unittest.main()
