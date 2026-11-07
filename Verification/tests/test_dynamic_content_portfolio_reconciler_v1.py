#!/usr/bin/env python3
"""Synthetic positives/negatives for the read-only dynamic content reconciler."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

MOD_PATH = Path(__file__).resolve().parents[2] / "Tools" / "reconcile_dynamic_content_portfolio_v1.py"
spec = importlib.util.spec_from_file_location("portfolio_reconciler", MOD_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SHA_A = "a" * 64
SHA_B = "b" * 64


class ReconcilerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        self.catalog = {"families": []}
        self.registry = {
            "schema": "gfp-opt-dynamic-content-portfolio-registry@1.0.0",
            "registry_state": "INITIAL_OBSERVED_BASELINE__READ_ONLY_METADATA__NO_AUTO_PROMOTION",
            "total_cards_including_cross_family_overlap": 55,
            "items": [],
        }
        for n in range(10):
            fid = "family:fixture-" + str(n)
            p = "Workspaces/fixture" + str(n) + "/LATEST.json"
            self.catalog["families"].append({"id": fid})
            sha = self.write_json(p, {"release": {"sha256": SHA_A}})
            self.registry["items"].append({
                "id": fid, "metrics": {"cards": n + 1},
                "owner_locator": {
                    "path": p, "git_blob_observed": sha,
                    "artifact_sha_json_pointer": "/release/sha256",
                },
                "active_baseline": {"artifact_sha256": SHA_A},
            })
        self.flush()

    def write_json(self, p, obj):
        dst = self.root / p
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = (json.dumps(obj, sort_keys=True) + "\n").encode()
        dst.write_bytes(data)
        return module.git_blob_sha(data)

    def flush(self):
        self.write_json(module.REGISTRY, self.registry)
        self.write_json(module.CATALOG, self.catalog)

    def test_all_exact_reference_matches_without_artifact_finality(self):
        before = (self.root / module.REGISTRY).read_bytes()
        report = module.reconcile(self.root)
        self.assertEqual(report["counts"]["matching_git_pointers"], 10)
        self.assertIn("ARTIFACT_BYTES_UNCHECKED", report["status"])
        self.assertEqual(report["items"][0]["library_drive_artifact_bytes"], "NOT_CHECKED")
        self.assertEqual((self.root / module.REGISTRY).read_bytes(), before)

    def test_selected_owner_artifact_changed_is_review_not_promotion(self):
        self.write_json("Workspaces/fixture0/LATEST.json", {"release": {"sha256": SHA_B}})
        report = module.reconcile(self.root)
        self.assertEqual(report["counts"]["owner_artifact_pointer_changed"], 1)
        self.assertEqual(report["items"][0]["recorded_artifact_sha256"], SHA_A)
        self.assertEqual(report["status"], "REVIEW_REQUIRED")

    def test_unrelated_owner_metadata_change_is_review(self):
        self.write_json("Workspaces/fixture0/LATEST.json",
                        {"release": {"sha256": SHA_A}, "note": "new"})
        report = module.reconcile(self.root)
        self.assertEqual(report["counts"]["owner_metadata_changed"], 1)
        self.assertEqual(report["counts"]["owner_artifact_pointer_changed"], 0)

    def test_missing_owner_file_is_hold(self):
        (self.root / "Workspaces/fixture0/LATEST.json").unlink()
        self.assertEqual(module.reconcile(self.root)["status"], "HOLD_OWNER_UNRESOLVED")

    def test_invalid_owner_json_is_hold(self):
        (self.root / "Workspaces/fixture0/LATEST.json").write_text("{broken")
        self.assertEqual(module.reconcile(self.root)["counts"]["unresolved"], 1)

    def test_missing_release_field_is_hold(self):
        self.write_json("Workspaces/fixture0/LATEST.json", {"other": {}})
        self.assertEqual(module.reconcile(self.root)["counts"]["unresolved"], 1)

    def test_bad_selected_release_sha_is_hold(self):
        self.write_json("Workspaces/fixture0/LATEST.json", {"release": {"sha256": "not-a-hash"}})
        self.assertEqual(module.reconcile(self.root)["counts"]["unresolved"], 1)

    def test_duplicate_family_rejected(self):
        self.registry["items"][1]["id"] = self.registry["items"][0]["id"]
        self.flush()
        with self.assertRaises(ValueError):
            module.reconcile(self.root)

    def test_unmapped_family_rejected(self):
        self.registry["items"][0]["id"] = "family:made-up"
        self.flush()
        with self.assertRaises(ValueError):
            module.reconcile(self.root)

    def test_invalid_card_total_rejected(self):
        self.registry["total_cards_including_cross_family_overlap"] = 54
        self.flush()
        with self.assertRaises(ValueError):
            module.reconcile(self.root)

    def test_parent_directory_escape_rejected(self):
        self.registry["items"][0]["owner_locator"]["path"] = "Workspaces/../../etc/passwd"
        self.flush()
        self.assertEqual(module.reconcile(self.root)["counts"]["unresolved"], 1)

    def test_path_escape_symlink_rejected(self):
        outside = self.base / "outside.json"
        outside.write_text('{"release":{"sha256":"' + SHA_B + '"}}')
        link = self.root / "Workspaces" / "fixture0" / "LATEST.json"
        link.unlink()
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("symlinks unavailable on this platform")
        self.assertEqual(module.reconcile(self.root)["counts"]["unresolved"], 1)

    def test_output_refuses_writes_inside_repo(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = module.main(["--repo-root", str(self.root), "--out-dir", str(self.root / "reports")])
        self.assertEqual(code, 2)
        self.assertFalse((self.root / "reports").exists())

    def test_external_output_is_derived_only(self):
        target = self.base / "derived-report"
        with contextlib.redirect_stdout(io.StringIO()):
            code = module.main(["--repo-root", str(self.root), "--out-dir", str(target)])
        self.assertEqual(code, 0)
        report = json.loads((target / "RECONCILIATION.json").read_text(encoding="utf8"))
        self.assertEqual(report["counts"]["matching_git_pointers"], 10)
        self.assertIn("NOT_CHECKED", (target / "RECONCILIATION.json").read_text())
        self.assertTrue((target / "RECONCILIATION.md").is_file())

    def test_strict_exit_opt_in_only(self):
        self.write_json("Workspaces/fixture0/LATEST.json", {"release": {"sha256": SHA_B}})
        with contextlib.redirect_stdout(io.StringIO()):
            normal = module.main(["--repo-root", str(self.root)])
            strict = module.main(["--repo-root", str(self.root), "--fail-on-review"])
        self.assertEqual(normal, 0)
        self.assertEqual(strict, 2)

    def test_git_blob_nul_format(self):
        self.assertEqual(module.git_blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")


if __name__ == "__main__":
    unittest.main()
