"""Control Center identity and read-only metadata contracts, including negative cases."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Tools/build_project_control_center_v1.py"
spec = importlib.util.spec_from_file_location("project_control_center_v1", SCRIPT)
pcc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pcc)


class TestProjectControlCenter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = pcc.git_index()
        cls.cat = pcc.load_json_from_index(pcc.CATALOG, cls.index)
        cls.state = pcc.load_json_from_index(pcc.STATE, cls.index)
        cls.pointers = {}
        for d in pcc.tracked_dirs(cls.index):
            for name in ("LATEST.json", "CHECKPOINT.json"):
                p = d + "/" + name
                if p in cls.index:
                    cls.pointers[p] = pcc.load_json_from_index(p, cls.index)

    def build(self, cat=None, index=None, state=None, pointers=None):
        return pcc.build(copy.deepcopy(self.cat) if cat is None else cat,
                         dict(self.index) if index is None else index,
                         copy.deepcopy(self.state) if state is None else state,
                         copy.deepcopy(self.pointers) if pointers is None else pointers)

    def test_real_catalog_has_distinct_family_workspace_and_root_identity(self):
        self.assertEqual(len(self.cat["families"]), 21)
        self.assertEqual(len(self.cat["workspaces"]), 34)
        self.assertEqual(len(self.cat["root_workstreams"]), 17)
        self.assertEqual(pcc.catalog_errors(self.cat), [])

    def test_root_workspaces_are_not_counted_as_new_families(self):
        snapshot = self.build()
        self.assertEqual(snapshot["counts"]["families"], 21)
        self.assertEqual(snapshot["counts"]["git_workspaces"], len(pcc.tracked_dirs(self.index)))
        self.assertEqual(snapshot["counts"]["root_workstreams"], len(self.state["workstreams"]))

    def test_34_original_workspaces_map_to_exactly_one_family(self):
        self.assertEqual(len(pcc.tracked_dirs(self.index)), 34)
        snap = self.build()
        self.assertEqual(snap["counts"]["mapped_workspaces"], 34)
        self.assertEqual(len(snap["families"]), len({x["id"] for x in snap["families"]}))

    def test_canonical_a1_verben_is_not_general_menschen_a1(self):
        ws = next(x for x in self.cat["workspaces"] if
                  x["git_dir"] == "Workspaces/menschen-a1-verben-wortfamilie-v336")
        family = next(x for x in self.cat["families"] if x["id"] == ws["parent_family_id"])
        self.assertEqual(family["name"], "Menschen-A1-Verben")

    def test_cross_source_review_uses_portfolio_parent(self):
        ws = next(x for x in self.cat["workspaces"] if
                  x["git_dir"].startswith("Workspaces/menschen-verben-aud006"))
        family = next(x for x in self.cat["families"] if x["id"] == ws["parent_family_id"])
        self.assertEqual(family["name"], "Menschen-Portfolio")
        self.assertEqual(ws["kind"], "CROSS_SOURCE_QA_OR_RUNTIME_WORKSPACE")

    def test_missing_direct_git_directory_does_not_invalidate_library_family(self):
        rows = self.build()["families"]
        nv = next(x for x in rows if x["name"] == "Nomen-Verb-Verbindungen")
        self.assertEqual(nv["git_workspace_count"], 0)
        self.assertEqual(nv["root_summary_entries"], 1)
        self.assertEqual(nv["independent_semantic_stage_proof"], "NOT_VERIFIED_BY_THIS_TOOL")

    def test_untracked_root_checkpoint_is_navigation_gap_not_missing_source(self):
        snap = self.build()
        self.assertTrue(any(x["type"] == "ROOT_CHECKPOINT_UNTRACKED" for x in snap["issues"]))
        self.assertEqual(snap["counts"]["stage4_stage5_stage6_stage7_certificates_generated"], 0)

    def test_root_summary_does_not_override_workstream_latest(self):
        snap = self.build()
        w = next(x for x in snap["workspaces"] if
                 x["git_dir"] == "Workspaces/menschen-b1-24-lessons-v336")
        self.assertTrue(w["authority"].startswith("LATEST_INDEX_HINT"))
        self.assertFalse(w["stage_pass_or_release_attested_by_control_center"])

    def test_invalid_workspace_parent_blocks_catalog(self):
        cat = copy.deepcopy(self.cat)
        cat["workspaces"][0]["parent_family_id"] = "family:does-not-exist"
        self.assertIn("DANGLING_WORKSPACE_PARENT", pcc.catalog_errors(cat))

    def test_duplicate_workspace_identity_blocks_catalog(self):
        cat = copy.deepcopy(self.cat)
        cat["workspaces"].append(copy.deepcopy(cat["workspaces"][0]))
        self.assertIn("DUPLICATE_WORKSPACE_ID_OR_PATH", pcc.catalog_errors(cat))

    def test_duplicate_family_identity_blocks_catalog(self):
        cat = copy.deepcopy(self.cat)
        cat["families"][1]["id"] = cat["families"][0]["id"]
        self.assertIn("FAMILY_IDENTITY_COLLISION", pcc.catalog_errors(cat))

    def test_unapproved_acceptance_field_blocks_catalog(self):
        cat = copy.deepcopy(self.cat)
        cat["workspaces"][0]["stage4_pass"] = True
        self.assertIn("VOLATILE_PROGRESS_STORED_IN_IDENTITY_CATALOG", pcc.catalog_errors(cat))

    def test_workstream_newly_tracked_without_catalog_is_visible_not_invented(self):
        idx = dict(self.index)
        idx["Workspaces/future-new-source/LATEST.json"] = "a" * 40
        snap = self.build(index=idx)
        self.assertTrue(any(x["type"] == "UNMAPPED_NEW_WORKSPACE" and
                            x["path"] == "Workspaces/future-new-source"
                            for x in snap["issues"]))
        w = next(x for x in snap["workspaces"] if
                 x["git_dir"] == "Workspaces/future-new-source")
        self.assertIsNone(w["id"])
        self.assertIsNone(w["parent_family_id"])

    def test_removed_tracked_workspace_not_silently_deleted_from_catalog(self):
        idx = {k: v for k, v in self.index.items()
               if not k.startswith("Workspaces/unregelmaessige-verben/")}
        snap = self.build(index=idx)
        self.assertTrue(any(x["type"] == "CATALOGED_WORKSPACE_NOT_TRACKED"
                            for x in snap["issues"]))

    def test_bad_latest_falls_back_to_checkpoint_and_reports_issue(self):
        d = "Workspaces/menschen-b1-24-lessons-v336"
        inp = copy.deepcopy(self.pointers)
        inp[d + "/LATEST.json"] = None
        snap = self.build(pointers=inp)
        w = next(x for x in snap["workspaces"] if x["git_dir"] == d)
        self.assertEqual(w["display_pointer"], d + "/CHECKPOINT.json")
        self.assertTrue(any(x["type"] == "INVALID_LATEST_JSON" for x in snap["issues"]))

    def test_both_pointers_invalid_produces_no_fake_status(self):
        d = "Workspaces/menschen-b1-24-lessons-v336"
        inp = copy.deepcopy(self.pointers)
        inp[d + "/LATEST.json"] = None
        inp[d + "/CHECKPOINT.json"] = None
        snap = self.build(pointers=inp)
        w = next(x for x in snap["workspaces"] if x["git_dir"] == d)
        self.assertIsNone(w["reported_status_hint"])
        self.assertEqual(w["authority"], "NO_PARSEABLE_POINTER_NO_PROGRESS_CLAIM")

    def test_root_workstreams_not_an_object_is_refused(self):
        state = copy.deepcopy(self.state)
        state["workstreams"] = []
        with self.assertRaisesRegex(ValueError, "ROOT_WORKSTREAMS_NOT_OBJECT"):
            self.build(state=state)

    def test_dashboard_generation_does_not_mutate_snapshot(self):
        data = self.build()
        before = copy.deepcopy(data)
        out = pcc.dashboard_md(data)
        self.assertEqual(data, before)
        self.assertIn("not content/Stage4", out)
        self.assertIn("Workspaces/menschen-b1-24-lessons-v336", out)

    def test_generated_snapshot_deterministic_for_identical_git_index(self):
        a = self.build()
        b = self.build()
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_source_inputs_remain_byte_identical_after_real_cli_build(self):
        with tempfile.TemporaryDirectory(prefix="pcc-readonly-tests-") as directory:
            inputs = [ROOT / pcc.CATALOG, ROOT / pcc.STATE,
                      ROOT / "Workspaces/menschen-b1-24-lessons-v336/LATEST.json"]
            original = {str(x): x.read_bytes() for x in inputs}
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--check", "--output-dir", directory],
                cwd=ROOT, capture_output=True, text=True, timeout=120)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((Path(directory) / "CONTROL-CENTER.json").is_file())
            self.assertTrue((Path(directory) / "CONTROL-CENTER.md").is_file())
            self.assertTrue(all(x.read_bytes() == original[str(x)] for x in inputs))

    def test_output_source_tree_rejected(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--output-dir",
             str(ROOT / "Workspaces" / "reserved-test-output")],
            cwd=ROOT, capture_output=True, text=True, timeout=120)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("UNSAFE_OUTPUT_ALIASES_CONTENT_OR_SOURCE", proc.stderr)
        self.assertFalse((ROOT / "Workspaces" / "reserved-test-output").exists())


if __name__ == "__main__":
    unittest.main()
