#!/usr/bin/env python3
"""Regression tests for read-only exact Git dependency graph of legacy Workspaces."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

TOOL=Path(__file__).resolve().parents[2]/"Tools"/"audit_legacy_workspace_dependencies_v1.py"
spec=importlib.util.spec_from_file_location("legacy_dep_audit",TOOL)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class AuditLegacyDependenciesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)/"git_repo"
        self.home.mkdir()
        self.git("init", "-q")
        self.git("config","user.email","test@example.invalid")
        self.git("config","user.name","Test Only")
        self.legacy_a="Workspaces/old-a"
        self.legacy_b="Workspaces/old-b"
        self.canonical="Workspaces/live"
        self.routing={"schema":m.EXPECTED_ROUTING,"workspaces":[
            {"role":"CANONICAL","git_dir":self.canonical,
             "family_id":"family:f"},
            {"role":"COMPATIBILITY_LEGACY","git_dir":self.legacy_a,
             "family_id":"family:f","future_accepted_current_pointer_location":self.canonical},
            {"role":"COMPATIBILITY_LEGACY","git_dir":self.legacy_b,
             "family_id":"family:f","future_accepted_current_pointer_location":self.canonical},
        ]}
        self.write(m.ROUTING,json.dumps(self.routing))
        self.write(self.legacy_a+"/CHECKPOINT.json",
                   '{"self_path":"Workspaces/old-a/CHECKPOINT.json","status":"historical"}')
        self.write(self.legacy_b+"/LATEST.json",
                   '{"note":"old evidence"}')
        self.write(self.canonical+"/CHECKPOINT.json",
                   '{"old_lineage":"Workspaces/old-a/CHECKPOINT.json"}')
        self.write("Tools/import_records.py",
                   '# legacy path: Workspaces/old-a/CHECKPOINT.json')
        self.write("README.md",
                   'Canonical owner uses earlier Workspaces/old-b/LATEST.json for provenance')
        self.commit()

    def git(self,*args):
        return subprocess.run(["git",*args],cwd=self.home,check=True,
             capture_output=True).stdout

    def write(self,path,data):
        target=self.home/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(data,encoding="utf8")

    def commit(self):
        self.git("add",".")
        self.git("commit","-qm","fixture")

    def test_real_git_tracking_and_inbound_counts(self):
        r=m.analyze(self.home)
        self.assertEqual(r["counts"]["legacy_workspaces"],2)
        self.assertEqual(r["counts"]["legacy_tracked_files"],2)
        self.assertEqual(r["counts"]["legacy_with_any_text_inbound"],2)
        self.assertEqual(r["counts"]["legacy_with_code_or_canonical_inbound"],1)
        by={x["legacy_workspace"]:x for x in r["workspaces"]}
        self.assertEqual(by[self.legacy_a]["textual_inbound_reference_files"],2)
        self.assertEqual(by[self.legacy_b]["textual_inbound_reference_files"],1)
        self.assertIn("CODE_OR_CI",by[self.legacy_a]["ref_sources_by_class"])
        self.assertIn("CANONICAL_WORKSPACE",by[self.legacy_a]["ref_sources_by_class"])
        self.assertEqual(by[self.legacy_b]["priority"],"P1_REVIEW_OTHER_INBOUND")
        self.assertTrue(all(x["delete_decision"].startswith("PROHIBITED") for x in r["workspaces"]))

    def test_internal_self_path_not_counted_as_external(self):
        r=m.analyze(self.home)
        x=next(x for x in r["workspaces"] if x["legacy_workspace"]==self.legacy_a)
        self.assertNotIn(self.legacy_a+"/CHECKPOINT.json",
                         sum(x["reference_examples"].values(), []))

    def test_no_reference_does_not_authorize_delete(self):
        self.write("README.md","nothing")
        self.write("Tools/import_records.py","# safe")
        self.write(self.canonical+"/CHECKPOINT.json",'{"status":"none"}')
        self.commit()
        r=m.analyze(self.home)
        for x in r["workspaces"]:
            self.assertEqual(x["textual_inbound_reference_files"],0)
            self.assertIn("NOT_DELETION_SAFE",x["priority"])
            self.assertTrue(x["delete_decision"].startswith("PROHIBITED"))

    def test_binary_git_blobs_do_not_create_false_exact_text(self):
        raw=(self.home/"Tools/blob.bin")
        raw.write_bytes(b"\x00Workspaces/old-a/legacy\xff\x00")
        self.commit()
        r=m.analyze(self.home)
        x=next(x for x in r["workspaces"] if x["legacy_workspace"]==self.legacy_a)
        self.assertEqual(x["textual_inbound_reference_files"],2)

    def test_changed_worktree_not_counted_until_git_commit(self):
        self.write("README.md","Workspaces/old-a/new_uncommitted")
        before=m.analyze(self.home)
        self.assertEqual(before["counts"]["legacy_with_code_or_canonical_inbound"],1)
        self.assertEqual(next(x for x in before["workspaces"] if x["legacy_workspace"]==self.legacy_b)["textual_inbound_reference_files"],1)

    def test_missing_grandfathered_tracked_dir_holds(self):
        self.git("rm","-r","-q",self.legacy_a)
        self.commit()
        with self.assertRaises(ValueError):
            m.analyze(self.home)

    def test_new_unregistered_dir_not_in_known_manifest_is_not_silently_invented(self):
        self.write("Workspaces/sibling-unregistered/LATEST.json",'{"foo":"bar"}')
        self.commit()
        r=m.analyze(self.home)
        self.assertEqual(r["counts"]["legacy_workspaces"],2)
        self.assertNotIn("Workspaces/sibling-unregistered",[x["legacy_workspace"] for x in r["workspaces"]])

    def test_bad_routing_mapping_rejected(self):
        self.routing["workspaces"][1]["future_accepted_current_pointer_location"]="Workspaces/unknown"
        self.write(m.ROUTING,json.dumps(self.routing))
        with self.assertRaises(ValueError):
            m.analyze(self.home)

    def test_path_traversal_is_rejected(self):
        for term in ("Workspaces/../evil","Workspaces//","Workspaces/old/x","Workspaces/..\\evil","../Workspaces/old"):
            with self.subTest(term=term), self.assertRaises(ValueError):
                m.route_path(term)

    def test_cli_generates_external_report_only(self):
        dest=Path(self.tmp.name)/"reports"
        before=(self.home/m.ROUTING).read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            ok=m.main(["--repo-root",str(self.home),"--out-dir",str(dest),"--expect-legacy","2"])
        self.assertEqual(ok,0)
        self.assertTrue((dest/"LEGACY-WORKSPACE-DEPENDENCIES.md").exists())
        j=json.loads((dest/"LEGACY-WORKSPACE-DEPENDENCIES.json").read_text(encoding="utf8"))
        self.assertEqual(j["counts"]["legacy_workspaces"],2)
        self.assertEqual(before,(self.home/m.ROUTING).read_bytes())

    def test_cli_cannot_write_into_git_checkout(self):
        dest=self.home/"unsafe"
        with contextlib.redirect_stdout(io.StringIO()):
            status=m.main(["--repo-root",str(self.home),"--out-dir",str(dest),"--expect-legacy","2"])
        self.assertEqual(status,2)
        self.assertFalse(dest.exists())

    def test_fixture_cannot_pretend_to_have_twenty(self):
        with contextlib.redirect_stdout(io.StringIO()):
            status=m.main(["--repo-root",str(self.home)])
        self.assertEqual(status,2)

if __name__=="__main__":
    unittest.main()
