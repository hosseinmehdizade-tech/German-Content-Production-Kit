#!/usr/bin/env python3
"""Regression tests for the bounded 64 MB Stage5 neutral TSV input gate.

This does NOT certify linguistic Stage4, the workstream owner or native Stage6.
An exact 54 MB Menschen A1 source may be provided via GCPK_A1_STAGE5_TSV.
"""
import csv
import io
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_active_stage5_policy_v1 import (
    MAX_TSV, Stage5PolicyFailure, check_bytes, check_path,
)


def fixture(ids=("a",), category="Nomen", contract="gfp-vocabulary-neutral@1"):
    writer_buffer = io.StringIO(newline="")
    writer = csv.writer(writer_buffer, delimiter="\t", lineterminator="\n")
    writer.writerow(["id", "front", "back", "card_type", "category", "custom_fields", "details"])
    for card_id in ids:
        writer.writerow([card_id, "der Tisch", "میز", "de-vocabulary",
                         category, '{"presentation_contract":"' + contract + '"}', "[]"])
    return writer_buffer.getvalue().encode("utf-8")


class CurrentLargeSourceCapTests(unittest.TestCase):
    def test_explicit_bounded_cap(self):
        self.assertEqual(MAX_TSV, 64_000_000)

    def test_valid_neutral_fixture_still_passes(self):
        self.assertEqual(check_bytes(fixture())["status"],
                         "PASS_EXACT_ACTIVE_STAGE5_NEUTRAL_FORMAT_ONLY")

    def test_empty_still_fails(self):
        with self.assertRaisesRegex(Stage5PolicyFailure, "EMPTY_OR_OVERSIZE_TSV"):
            check_bytes(b"")

    def test_oversize_still_fails_before_parsing(self):
        with self.assertRaisesRegex(Stage5PolicyFailure, "EMPTY_OR_OVERSIZE_TSV"):
            check_bytes(b"X" * (MAX_TSV + 1))

    def test_duplicate_stable_id_still_fails(self):
        with self.assertRaisesRegex(Stage5PolicyFailure, "DUPLICATE_CARD_ID"):
            check_bytes(fixture(("same", "same")))

    def test_missing_category_still_fails(self):
        with self.assertRaisesRegex(Stage5PolicyFailure, "ACTIVE_NEUTRAL_STAGE5_POLICY_FAILED"):
            check_bytes(fixture(category=""))

    def test_invalid_presentation_contract_still_fails(self):
        with self.assertRaisesRegex(Stage5PolicyFailure, "ACTIVE_NEUTRAL_STAGE5_POLICY_FAILED"):
            check_bytes(fixture(contract="legacy-layout"))

    @unittest.skipUnless(os.environ.get("GCPK_A1_STAGE5_TSV"),
                         "Optional exact large-content QA fixture not provided")
    def test_exact_large_source_integrity(self):
        path = Path(os.environ["GCPK_A1_STAGE5_TSV"])
        original = path.read_bytes()
        self.assertGreater(len(original), 35_000_000)
        self.assertLessEqual(len(original), MAX_TSV)
        result = check_path(path)
        self.assertEqual(result["status"], "PASS_EXACT_ACTIVE_STAGE5_NEUTRAL_FORMAT_ONLY")
        self.assertEqual(result["cards_validated"], 2997)
        self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
