"""Phase2 graph correctness and independent evidence negative controls.

All tests use Git-index source metadata. No user file or card is changed.
"""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / "Tools/build_project_dependency_evidence_v1.py"
spec = importlib.util.spec_from_file_location("gcpk_dependency_evidence", FILE)
graph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph)


class TestDependencyEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = graph.index_blobs()
        cls.catalog = graph.source_json(graph.CATALOG, cls.index)
        cls.registry = graph.source_json(graph.REGISTRY, cls.index)
        cls.state = graph.source_json(graph.STATE, cls.index)
        cls.pointers = {}
        for path in graph.phase1.tracked_dirs(cls.index):
            for name in ("LATEST.json", "CHECKPOINT.json"):
                file = path + "/" + name
                if file in cls.index:
                    cls.pointers[file] = graph.source_json(file, cls.index)

    def build(self, cat=None, reg=None, index=None, state=None, pointers=None, changes=None):
        return graph.build_graph(
            copy.deepcopy(self.catalog) if cat is None else cat,
            copy.deepcopy(self.registry) if reg is None else reg,
            dict(self.index) if index is None else index,
            copy.deepcopy(self.state) if state is None else state,
            copy.deepcopy(self.pointers) if pointers is None else pointers,
            changes,
        )

    def test_exact_current_index_pins_match_all_15_policy_files(self):
        self.assertEqual(graph.binding_failures(self.registry, self.index), [])
        self.assertEqual(len(self.registry["policy_bindings"]), 15)

    def test_all_known_families_workspaces_and_root_keys_have_graph_nodes(self):
        r = self.build()
        self.assertEqual(r["counts"]["families"], 21)
        self.assertEqual(r["counts"]["workspaces"], 35)
        self.assertEqual(r["counts"]["root_keys"], 17)
        self.assertEqual(r["counts"]["policies"], 15)
        self.assertEqual(len(r["nodes"]), 21 + 35 + 17 + 15)

    def test_every_workspace_has_exactly_one_family_ownership_edge(self):
        r = self.build()
        ownership = [e for e in r["edges"] if e["kind"] == "WORKSPACE_OWNERSHIP_EXPLICIT"]
        self.assertEqual(len(ownership), 35)
        self.assertEqual(len({x["from"] for x in ownership}), 35)

    def test_policy_edges_label_potential_impact_not_verified_adoption(self):
        r = self.build()
        links = [e for e in r["edges"] if e["kind"] == "POTENTIAL_POLICY_DEPENDENCY_NOT_NATIVE_QA"]
        self.assertTrue(len(links) > 100)
        self.assertTrue(all("NOT_" in e["applicability"] or "CONDITIONAL" in e["applicability"]
                            for e in links))

    def test_currentness_applies_to_all_workspaces(self):
        r = self.build()
        edges = [x for x in r["edges"] if x["from"] == "policy:currentness"]
        self.assertEqual(len(edges), 35)

    def test_lexical_policy_does_not_imply_cross_source_audit_is_content_producer(self):
        r = self.build()
        edges = [x for x in r["edges"] if x["from"] == "policy:related_taxonomy"]
        self.assertEqual(len(edges), 32)
        self.assertFalse(any("menschen-verben-aud006" in x["to"] for x in edges))

    def test_neutral_builder_application_is_conditional_not_34_verified(self):
        r = self.build()
        edges = [x for x in r["edges"] if x["from"] == "policy:stage5_neutral_validator"]
        self.assertTrue(all(x["applicability"].startswith("CONDITIONAL_CONSUMER_SCHEMA") for x in edges))

    def test_pin_changing_without_registry_update_is_blocking(self):
        idx = dict(self.index)
        path = self.registry["policy_bindings"]["related_taxonomy"]["path"]
        idx[path] = "0" * 40
        with self.assertRaisesRegex(ValueError, "POLICY_PIN_DRIFT:related_taxonomy"):
            self.build(index=idx)

    def test_missing_pinned_source_is_blocking(self):
        idx = dict(self.index)
        idx.pop(self.registry["policy_bindings"]["lexical_relation_display"]["path"])
        with self.assertRaisesRegex(ValueError, "PINNED_POLICY_NOT_IN_GIT_INDEX"):
            self.build(index=idx)

    def test_invalid_policy_path_rejected(self):
        reg = copy.deepcopy(self.registry)
        reg["policy_bindings"]["currentness"]["path"] = "../outside.txt"
        with self.assertRaisesRegex(ValueError, "UNSAFE_POLICY_PATH:currentness"):
            self.build(reg=reg)

    def test_declared_artifact_sha_is_not_marked_verified(self):
        e = graph.scan_evidence(
            "Workspaces/test", {"artifact_sha256": "a" * 64},
            {"Workspaces/test/LATEST.json": "b" * 40},
            "Workspaces/test/LATEST.json")
        self.assertEqual(e["artifact_sha256_claim"], "a" * 64)
        self.assertEqual(e["artifact_sha256_readback"], "NOT_PERFORMED__SOURCE_ARTIFACT_NOT_MOUNTED")

    def test_existing_receipt_path_only_proves_path_tracking(self):
        idx = {"Workspaces/test/LATEST.json": "a" * 40,
               "Workspaces/test/receipt.json": "b" * 40}
        e = graph.scan_evidence("Workspaces/test", {"receipt": "receipt.json"},
                                idx, "Workspaces/test/LATEST.json")
        self.assertEqual(e["receipt_refs"][0]["declaration"],
                         "GIT_RECEIPT_PATH_TRACKED__CONTENT_NOT_AUDITED")
        self.assertEqual(e["linguistic_stage4"], "NOT_CERTIFIED_BY_THIS_REPORT")

    def test_unsafe_or_external_receipt_is_never_resolved(self):
        idx = {"Workspaces/test/receipt.json": "b" * 40}
        for path in ("../other.json", "https://example.org/report.json", "/absolute/report.json"):
            r = graph.normalize_receipt_pointer(path, "Workspaces/test", idx)
            self.assertIsNone(r["git_path"])

    def test_missing_receipt_is_a_hold_not_automatic_pass(self):
        r = graph.normalize_receipt_pointer("missing.json", "Workspaces/test", {})
        self.assertEqual(r["declaration"], "DECLARED_RECEIPT_PATH_NOT_TRACKED_HOLD")

    def test_changed_lexical_policy_produces_scoped_possible_impacts(self):
        path = self.registry["policy_bindings"]["related_taxonomy"]["path"]
        impact = self.build(changes=[path])["prospective_impact"][0]
        self.assertEqual(len(impact["possibly_affected_workspace_ids"]), 32)
        self.assertTrue(impact["impact_is_prospective_only"])
        self.assertFalse(impact["locked_sources_reopened"])

    def test_single_workspace_change_does_not_force_whole_repo_rebuild(self):
        path = "Workspaces/aspekte-c1-v336/LATEST.json"
        impact = self.build(changes=[path])["prospective_impact"][0]
        self.assertEqual(impact["possibly_affected_workspace_ids"],
                         ["workspace:aspekte-c1-v336"])

    def test_unknown_workspace_never_auto_assigned(self):
        impact = self.build(changes=["Workspaces/new-future-course/LATEST.json"])["prospective_impact"][0]
        self.assertEqual(impact["classification"], "UNREGISTERED_WORKSPACE_HOLD")
        self.assertEqual(impact["possibly_affected_workspace_ids"], [])

    def test_changing_registry_requires_all_policy_scope_review(self):
        impact = self.build(changes=[graph.REGISTRY])["prospective_impact"][0]
        self.assertEqual(len(impact["possibly_affected_workspace_ids"]), 35)
        self.assertFalse(impact["locked_sources_reopened"])

    def test_change_path_traversal_is_rejected_as_unsafe(self):
        impact = self.build(changes=["../source/secret.csv"])["prospective_impact"][0]
        self.assertEqual(impact["classification"], "UNSAFE_PATH_HOLD")

    def test_snapshot_is_deterministic_and_does_not_mutate_inputs(self):
        catalog = copy.deepcopy(self.catalog)
        before = copy.deepcopy(catalog)
        a = self.build(cat=catalog)
        b = self.build(cat=catalog)
        self.assertEqual(a, b)
        self.assertEqual(catalog, before)
        self.assertEqual(a["counts"]["source_artifact_shas_independently_verified"], 0)

    def test_actual_cli_writes_report_only_to_safe_output_directory(self):
        with tempfile.TemporaryDirectory(prefix="gcpk-graph-phase2-") as directory:
            source = ROOT / "Workspaces/aspekte-c1-v336/LATEST.json"
            before = source.read_bytes()
            run = subprocess.run(
                [sys.executable, str(FILE), "--check",
                 "--changed-path", "Prompt/RELATED-SECTIONS-TAXONOMY-POLICY-v1.1.0.md",
                 "--output-dir", directory],
                cwd=ROOT, capture_output=True, text=True, timeout=120)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertTrue((Path(directory) / "DEPENDENCY-EVIDENCE.json").exists())
            self.assertTrue((Path(directory) / "DEPENDENCY-EVIDENCE.md").exists())
            self.assertEqual(source.read_bytes(), before)

    def test_output_inside_workspaces_is_refused(self):
        dest = ROOT / "Workspaces" / "forbidden-graph-test"
        proc = subprocess.run([sys.executable, str(FILE), "--output-dir", str(dest)],
                              cwd=ROOT, capture_output=True, text=True, timeout=120)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("UNSAFE_OUTPUT_LOCATION", proc.stderr)
        self.assertFalse(dest.exists())


if __name__ == "__main__":
    unittest.main()
