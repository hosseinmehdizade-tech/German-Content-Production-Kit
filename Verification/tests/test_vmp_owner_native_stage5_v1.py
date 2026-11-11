"""Non-publishing VMP owner adapter regressions: no private cards, app or releases."""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Workspaces/250-verben-mit-praepositionen-lexical-enrichment-v1/publish_new_stage5_v1.py"
spec = importlib.util.spec_from_file_location("vmp_owner_stage5", SCRIPT)
vmp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vmp)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class VMPSourceOwnedAdapterTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)
        self.src = self.dir / "source"
        self.src.mkdir()
        (self.src / "SYNTHETIC-import.tsv").write_text(
            "id\tfront\tdetails\texamples\nx\tTest\t[]\t[]\n", encoding="utf-8")
        (self.src / "SYNTHETIC-canonical.json").write_text('{"cards":[]}', encoding="utf-8")
        (self.src / "SYNTHETIC-source-output-map.tsv").write_text("id\tsource\nx\ttest\n", encoding="utf-8")
        (self.src / "SYNTHETIC-QA.json").write_text('{"status":"DRAFT"}', encoding="utf-8")
        self.stage4 = self.dir / "stage4.json"
        self.stage4.write_text('{"status":"SYNTHETIC_TEST_ONLY"}', encoding="utf-8")
        latest = json.loads((ROOT / vmp.OWNER / "LATEST.json").read_text(encoding="utf-8"))
        self.review = self.dir / "review.json"
        self.evidence = {
            "schema": "gcpk-lexical-cross-tile-acceptance@1.0.0",
            "workstream": vmp.OWNER,
            "curated_current_parent_sha256": latest["final_content_only_v18"]["sha256"],
            "source_tsv_sha256": sha(self.src / "SYNTHETIC-import.tsv"),
            "stage4_receipt_sha256": sha(self.stage4)
        }
        self.output = self.dir / "candidate.zip"
        self.receipt = self.dir / "format.json"
        self.policy = self.dir / "quality.json"
        self.save_review()

    def save_review(self):
        self.review.write_text(json.dumps(self.evidence), encoding="utf-8")

    def check(self, **changes):
        config = {
            "root": ROOT, "source": self.src, "output": self.output,
            "receipt": self.receipt, "policy_report": self.policy,
            "stage4": self.stage4, "review_path": self.review}
        config.update(changes)
        return vmp.preflight(**config)

    def test_real_owner_current_pins_allow_preflight_only(self):
        result = self.check()
        self.assertEqual(result["family_id"], vmp.FAMILY)
        self.assertEqual(result["candidate_tsv_sha256"], self.evidence["source_tsv_sha256"])
        self.assertEqual(result["status"],
                         "OWNER_AND_SOURCE_PREFLIGHT_PASS_NOT_STAGE5_OR_ADOPTED")
        self.assertFalse(self.output.exists())
        self.assertFalse(self.receipt.exists())

    def test_same_accepted_current_import_tsv_cannot_be_repackaged(self):
        accepted = json.loads((ROOT / vmp.OWNER / "LATEST.json").read_text(
            encoding="utf-8"))["final_content_only_v18"]["source_tsv_sha256"]
        self.assertEqual(len(accepted), 64)
        actual_digest = vmp.digest
        def simulate_unchanged_current(path):
            if Path(path).name == "SYNTHETIC-import.tsv":
                return accepted
            return actual_digest(path)
        # Synthetic exact-current identity, never copy/edit private user cards.
        with patch.object(vmp, "digest", side_effect=simulate_unchanged_current):
            with self.assertRaisesRegex(ValueError,
                    "NO_NEW_IMPORT_TSV_DELTA_FROM_ACCEPTED_CURRENT"):
                self.check()
        self.assertFalse(self.output.exists())
        self.assertFalse(self.receipt.exists())
        self.assertFalse(self.policy.exists())

    def test_real_accepted_import_sha_is_present_and_distinct_from_candidate(self):
        latest = json.loads((ROOT / vmp.OWNER / "LATEST.json").read_text(
            encoding="utf-8"))
        accepted = latest["final_content_only_v18"]["source_tsv_sha256"]
        self.assertEqual(accepted,
            "d23a5b9865d9e35b7ec24fa4f94fe8d94ee9f65fb990f8da7ffed41c75435191")
        self.assertNotEqual(accepted, sha(self.src / "SYNTHETIC-import.tsv"))
        self.assertEqual(self.check()["status"],
                         "OWNER_AND_SOURCE_PREFLIGHT_PASS_NOT_STAGE5_OR_ADOPTED")

    def test_stale_current_parent_fails_closed(self):
        self.evidence["curated_current_parent_sha256"] = "f" * 64
        self.save_review()
        with self.assertRaisesRegex(ValueError, "CROSS_TILE_REVIEW_NOT_FOR_CURRENT_OWNER"):
            self.check()

    def test_wrong_canonical_source_owner_fails_closed(self):
        self.evidence["workstream"] = "Workspaces/aspekte-b2-v336"
        self.save_review()
        with self.assertRaisesRegex(ValueError, "CROSS_TILE_REVIEW_NOT_FOR_CURRENT_OWNER"):
            self.check()

    def test_stage4_receipt_missing_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "MISSING_OR_UNSAFE_STAGE4_RECEIPT"):
            self.check(stage4=self.dir / "absent-stage4.json")

    def test_stage4_receipt_directory_fails_closed(self):
        directory=self.dir / "fake-stage4.json"
        directory.mkdir()
        with self.assertRaisesRegex(ValueError, "MISSING_OR_UNSAFE_STAGE4_RECEIPT"):
            self.check(stage4=directory)

    def test_stage4_receipt_bytes_tampering_fails_closed(self):
        self.stage4.write_text('{"status":"CHANGED"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "STAGE4_RECEIPT_BYTES_NOT_REVIEWED"):
            self.check()

    def test_exact_source_mutation_fails_closed(self):
        with (self.src / "SYNTHETIC-import.tsv").open("a", encoding="utf-8") as f:
            f.write("y\tChanged\t[]\t[]\n")
        with self.assertRaisesRegex(ValueError, "DIRECT_IMPORT_TSV_NOT_EXACT_REVIEWED_SOURCE"):
            self.check()

    def test_existing_output_never_overwritten(self):
        self.output.write_bytes(b"keep immutable")
        with self.assertRaisesRegex(ValueError, "EXISTING_OUTPUT_OR_RECEIPT"):
            self.check()
        self.assertEqual(self.output.read_bytes(), b"keep immutable")

    def test_output_inside_source_forbidden(self):
        with self.assertRaisesRegex(ValueError, "PUBLIC_GIT_OR_SOURCE_OUTPUT_FORBIDDEN"):
            self.check(output=self.src / "candidate.zip")

    def test_public_git_output_forbidden(self):
        with self.assertRaisesRegex(ValueError, "PUBLIC_GIT_OR_SOURCE_OUTPUT_FORBIDDEN"):
            self.check(output=ROOT / "unsafe_candidate.zip")

    def test_no_old_launcher_or_unapproved_stage_claim(self):
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("build_quality_gated_lexical_candidate_v1.py", script)
        self.assertIn('"--family-id", FAMILY', script)
        self.assertNotIn("subprocess.run(command, shell=True)", script)
        self.assertIn("OWNER_NATIVE_STAGE5_CANDIDATE_PASS_NOT_ADOPTED", script)
        self.assertIn("STAGE4_RECEIPT_BYTES_NOT_REVIEWED", script)

if __name__ == "__main__":
    unittest.main()
