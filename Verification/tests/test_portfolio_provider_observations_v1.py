#!/usr/bin/env python3
"""Metadata-only, no-promotion safety tests for connected-provider snapshot."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "Tools" / "reconcile_portfolio_provider_observations_v1.py"
spec = importlib.util.spec_from_file_location("provider_check", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ProviderSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.registry = {"items": []}
        self.snap = {
            "schema": m.SCHEMA,
            "observed_date": "2026-11-07",
            "read_only": True, "auto_release_promotion": False,
            "evidence_scope": "PROVIDER_METADATA_ONLY__NO_FRESH_BINARY_SHA256__NO_PROVIDER_ACCESS_INSIDE_GITHUB_CI",
            "entries": []
        }
        for i in range(10):
            fid = "family:test" + str(i)
            name = "release-" + str(i) + ".zip"
            self.registry["items"].append(
                {"id": fid, "active_baseline": {"artifact_name": name,
                                               "artifact_size_bytes": 100 + i}})
            for prov in ("google_drive", "library"):
                self.snap["entries"].append({
                    "family_id": fid, "provider": prov,
                    "observation": m.OBSERVED[prov],
                    "provider_item_id": "id-" + str(i) + "-" + prov,
                    "name": name, "size_bytes": 100 + i,
                    "sha256_of_bytes": "NOT_REMEASURED"})

    def observed(self, family=0, provider="library"):
        return next(x for x in self.snap["entries"]
                    if x["family_id"] == "family:test" + str(family)
                    and x["provider"] == provider)

    def save(self):
        paths = [(self.root / m.REGISTRY, self.registry),
                 (self.root / m.SNAPSHOT, self.snap)]
        for p, val in paths:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(val), encoding="utf8")

    def test_all_observed_name_and_size_match_is_only_metadata(self):
        before = copy.deepcopy(self.snap)
        rows, counts = m.check_observations(self.registry, self.snap)
        self.assertEqual(counts.get("METADATA_NAME_SIZE_MATCH__BYTES_UNCHECKED"), 20)
        self.assertTrue(all(x["content_sha256_remeasured"] is False for x in rows))
        self.assertEqual(self.snap, before)

    def test_changed_provider_name_is_review(self):
        self.observed()["name"] = "different.zip"
        self.assertEqual(m.check_observations(self.registry, self.snap)[1].get("METADATA_MISMATCH_REVIEW"), 1)

    def test_changed_size_is_review(self):
        self.observed(provider="google_drive")["size_bytes"] += 1
        self.assertEqual(m.check_observations(self.registry, self.snap)[1].get("METADATA_MISMATCH_REVIEW"), 1)

    def test_missing_in_scanned_folder_is_not_deletion(self):
        x = self.observed()
        x.clear()
        x.update({"family_id": "family:test0", "provider": "library",
                  "observation": "NOT_OBSERVED_IN_SCANNED_FOLDERS",
                  "scanned_relative_folders": ["Sample/Current"]})
        classes = [z["classification"] for z in m.check_observations(self.registry, self.snap)[0]]
        self.assertIn("NOT_SEEN_IN_SCOPED_FOLDER__NOT_PROOF_OF_DELETION", classes)

    def test_retirement_needs_receipt(self):
        x = self.observed()
        x.clear()
        x.update({"family_id": "family:test0", "provider": "library",
                  "observation": "RETIRED_WITH_PRIOR_OWNER_AUTHORIZATION"})
        with self.assertRaises(ValueError):
            m.check_observations(self.registry, self.snap)
        x["owner_cleanup_receipt_path"] = "Workspaces/source/receipt.json"
        classes = [z["classification"] for z in m.check_observations(self.registry, self.snap)[0]]
        self.assertIn("OWNER_AUTHORIZED_LIBRARY_RETIREMENT__DRIVE_BACKUP_SEPARATE", classes)

    def test_unchecked_is_neutral(self):
        x = self.observed(provider="google_drive")
        x.clear()
        x.update({"family_id": "family:test0", "provider": "google_drive",
                  "observation": "NOT_CHECKED"})
        self.assertIn("NOT_CHECKED", m.check_observations(self.registry, self.snap)[1])

    def test_duplicate_provider_pair_rejected(self):
        self.snap["entries"][1] = dict(self.snap["entries"][0])
        with self.assertRaises(ValueError):
            m.check_observations(self.registry, self.snap)

    def test_unknown_family_rejected(self):
        self.snap["entries"][0]["family_id"] = "family:malicious"
        with self.assertRaises(ValueError):
            m.check_observations(self.registry, self.snap)

    def test_wrong_provider_observation_pair_rejected(self):
        self.observed(provider="library")["observation"] = "EXACT_FILE_METADATA_OBSERVED"
        with self.assertRaises(ValueError):
            m.check_observations(self.registry, self.snap)

    def test_claimed_binary_hash_must_be_rejected(self):
        self.observed()["sha256_of_bytes"] = "a" * 64
        with self.assertRaises(ValueError):
            m.check_observations(self.registry, self.snap)

    def test_auto_promotion_must_be_off(self):
        self.snap["auto_release_promotion"] = True
        with self.assertRaises(ValueError):
            m.check_observations(self.registry, self.snap)

    def test_metadata_scope_cannot_be_upgraded(self):
        self.snap["evidence_scope"] = "BYTE_SHA256_PASS"
        with self.assertRaises(ValueError):
            m.check_observations(self.registry, self.snap)

    def test_output_never_written_inside_repo(self):
        self.save()
        target = self.root / "artifact"
        with contextlib.redirect_stdout(io.StringIO()):
            code = m.main(["--repo-root", str(self.root), "--out-dir", str(target)])
        self.assertEqual(code, 2)
        self.assertFalse(target.exists())

    def test_external_report_readonly_and_nonpromoting(self):
        self.save()
        before = (self.root / m.REGISTRY).read_bytes()
        out = self.root.parent / "derived"
        with contextlib.redirect_stdout(io.StringIO()):
            code = m.main(["--repo-root", str(self.root), "--out-dir", str(out)])
        self.assertEqual(code, 0)
        j = json.loads((out / "PROVIDER-RECONCILIATION.json").read_text())
        self.assertFalse(j["provider_access_in_ci"])
        self.assertEqual(j["counts"]["METADATA_NAME_SIZE_MATCH__BYTES_UNCHECKED"], 20)
        self.assertEqual(before, (self.root / m.REGISTRY).read_bytes())
        self.assertIn("not live Library/Drive", (out / "PROVIDER-RECONCILIATION.md").read_text())

    def test_review_raises_only_in_explicit_strict_mode(self):
        self.save()
        self.observed()["name"] = "changed.zip"
        self.save()
        with contextlib.redirect_stdout(io.StringIO()):
            default = m.main(["--repo-root", str(self.root)])
            strict = m.main(["--repo-root", str(self.root), "--fail-on-mismatch"])
        self.assertEqual(default, 0)
        self.assertEqual(strict, 2)


if __name__ == "__main__":
    unittest.main()
