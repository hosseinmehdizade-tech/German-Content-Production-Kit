#!/usr/bin/env python3
"""Synthetic committed Git checks: distinguish code-callsite leads from provenance."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

TOOL=Path(__file__).resolve().parents[2]/"Tools"/"triage_legacy_p0_operational_references_v1.py"
spec=importlib.util.spec_from_file_location("p0_legacy_triage",TOOL)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TriageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/"repo"
        self.root.mkdir()
        self.cmd("init","-q")
        self.cmd("config","user.email","test@example.invalid")
        self.cmd("config","user.name","Example")
        self.legacy=[f"Workspaces/hist-{i}" for i in range(20)]
        self.canonical="Workspaces/owner"
        mapping={"workspaces":[{"git_dir":self.canonical,"role":"CANONICAL","family_id":"family:a"}]+
            [{"git_dir":w,"role":"COMPATIBILITY_LEGACY","family_id":"family:a",
              "future_accepted_current_pointer_location":self.canonical} for w in self.legacy]}
        snapshot={"schema":"gcpk-legacy-git-reference-baseline@1.0.0",
                  "rows":[{"workspace_id":"workspace:hist-"+str(i),"family_id":"family:a",
                    "priority":"P0_REVIEW_CODE_OR_CANONICAL_INBOUND" if i<10 else "P1_OTHER",
                    "literal_inbound_reference_file_count":1} for i in range(20)]}
        self.write(m.ROUTING,json.dumps(mapping))
        self.write(m.HISTORIC,json.dumps(snapshot))
        for w in self.legacy:
            self.write(w+"/CHECKPOINT.json",json.dumps({"self":w+"/CHECKPOINT.json"}))
        self.write(self.canonical+"/LATEST.json","\"archive\":\"Workspaces/hist-0/LATEST.json\"")
        self.write("Tools/use_path.py","file = Path('Workspaces/hist-1/CHECKPOINT.json').read_text()")
        self.write("Tools/notes.py","# old reference: Workspaces/hist-2/CHECKPOINT.json")
        self.write("Verification/tests/test_a.py","assert 'Workspaces/hist-3/CHECKPOINT.json'")
        self.write(".github/workflows/test.yml","on: push # Workspaces/hist-4/CHECKPOINT.json")
        self.write("README.md","Historical record: Workspaces/hist-5/CHECKPOINT.json")
        self.write("Tools/overlap.py","v = Path('Workspaces/hist-6-longer/CHECKPOINT.json')")
        self.commit()

    def cmd(self,*args):
        return subprocess.run(["git",*args],cwd=self.root,check=True,capture_output=True).stdout

    def write(self,p,v):
        f=self.root/p
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(v,encoding="utf8")

    def commit(self):
        self.cmd("add",".")
        self.cmd("commit","-qm","fixture")

    def test_only_exact_10_p0_identity(self):
        targets=m.relevant(self.root)
        self.assertEqual(len(targets),10)
        self.assertEqual(targets[0][0],"Workspaces/hist-0")

    def test_line_evidence_and_runtime_proof_are_separate(self):
        data=m.analyze(self.root)
        self.assertEqual(data["counters"]["p0_workspaces"],10)
        self.assertEqual(data["counters"]["p0_workspaces_with_execution_candidate"],2)
        self.assertEqual(data["status"],"P0_EVIDENCE_TRIAGE_COMPLETE__EXECUTION_NOT_ATTESTED")
        self.assertTrue(all(not x["runtime_or_active_import_proven"] for x in data["workspaces"]))
        ws={x["legacy_workspace"]:x for x in data["workspaces"]}
        self.assertEqual(ws[self.legacy[6]]["execution_candidate_source_files"],0)
        src=ws[self.legacy[1]]["inbound_referencers"]
        self.assertEqual(src[0]["samples"][0]["line"],1)
        self.assertEqual(src[0]["samples"][0]["kind"],"EXECUTABLE_PATH_OPERAND_CANDIDATE__VERIFY_CALLSITE")
        self.assertEqual(ws[self.legacy[2]]["execution_candidate_source_files"],0)
        self.assertEqual(ws[self.legacy[3]]["execution_candidate_source_files"],0)
        self.assertEqual(ws[self.legacy[5]]["execution_candidate_source_files"],0)
        self.assertTrue(ws[self.legacy[0]]["inbound_referencers"])
        self.assertTrue(all(x["decision"].startswith("PRESERVE") for x in data["workspaces"]))

    def test_already_committed_git_evidence_not_mutable_worktree(self):
        self.write("Tools/use_path.py","no longer referring to old paths")
        data=m.analyze(self.root)
        self.assertEqual(data["counters"]["p0_workspaces_with_execution_candidate"],2)

    def test_short_path_rejects_sibling_prefix(self):
        q=m.path_boundary("Workspaces/hist-6")
        self.assertIsNone(q.search(b"Workspaces/hist-6-longer/checkpoint.json"))
        self.assertIsNotNone(q.search(b"Workspaces/hist-6/LATEST.json"))

    def test_known_document_is_not_executable(self):
        self.assertEqual(m.source_bucket("Workspaces/current/LATEST.json","file = Path('foo')"),
                         "WORKSPACE_CHECKPOINT_OR_LINEAGE_REFERENCE")
        self.assertEqual(m.source_bucket("Optimization-Program/report.json","open('foo')"),
                         "GOVERNANCE_OR_REPORT_REFERENCE")
        self.assertEqual(m.source_bucket("Verification/tests/test_a.py","x=open('foo')"),
                         "TEST_OR_REGRESSION_EVIDENCE_NOT_RUNTIME_PROOF")

    def test_disallow_reporting_inside_checkout(self):
        dest=self.root/"output"
        with contextlib.redirect_stdout(io.StringIO()):
            code=m.main(["--repo-root",str(self.root),"--out-dir",str(dest)])
        self.assertEqual(code,2)
        self.assertFalse(dest.exists())

    def test_report_external_and_no_source_write(self):
        initial=(self.root/m.ROUTING).read_bytes()
        dest=Path(self.tmp.name)/"evidence"
        with contextlib.redirect_stdout(io.StringIO()):
            code=m.main(["--repo-root",str(self.root),"--out-dir",str(dest)])
        self.assertEqual(code,0)
        self.assertTrue((dest/"P0-LEGACY-REFERENCE-EVIDENCE.json").exists())
        self.assertEqual(initial,(self.root/m.ROUTING).read_bytes())

    def test_fail_closed_if_vetted_p0_set_drifted(self):
        d=json.loads((self.root/m.HISTORIC).read_text())
        d["rows"][0]["priority"]="P1_CHANGED"
        self.write(m.HISTORIC,json.dumps(d))
        with self.assertRaises(ValueError):
            m.relevant(self.root)

if __name__=="__main__":
    unittest.main()
