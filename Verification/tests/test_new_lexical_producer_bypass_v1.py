"""Reject new executable production paths that bypass lexical quality evidence."""
from __future__ import annotations
import hashlib,subprocess,sys,tempfile,unittest
from unittest.mock import patch
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Verification"))
from check_new_lexical_producer_bypass_v1 import inspect,scope,PINNED_NONIMPORT_GUARDED_CHECKPOINTS

class ProducerBypassTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.g("init","-q")
        self.g("config","user.name","Synthetic CI")
        self.g("config","user.email","ci@example.invalid")
        (self.root/"README.md").write_text("baseline")
        self.g("add",".");self.g("commit","-qm","base")
        self.base=self.g("rev-parse","HEAD").strip()
    def g(self,*args):
        return subprocess.run(["git",*args],cwd=self.root,check=True,
            capture_output=True,text=True,encoding="utf-8").stdout
    def write_commit(self,path,content):
        f=self.root/path
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(content,encoding="utf-8")
        self.g("add",path);self.g("commit","-qm","change")
        return self.g("rev-parse","HEAD").strip()
    def test_new_lexical_python_legacy_builder_refused(self):
        h=self.write_commit("Workspaces/menschen-a1-verben-wortfamilie-v336/build.py",
            'subprocess.run(["python", "Tools/build_clean_delivery.py", source, output])\n')
        with self.assertRaisesRegex(ValueError,"NEW_UNGATED_LEXICAL_PRODUCER_REFERENCE"):
            inspect(self.root,self.base,h)
    def test_new_workflow_direct_legacy_wrapper_refused(self):
        h=self.write_commit(".github/workflows/new-lexical.yml",
          "jobs:\n  release:\n    steps:\n      - run: python Tools/build_front_gated_clean_delivery_v1.py x out.zip\n")
        with self.assertRaisesRegex(ValueError,"NEW_UNGATED_LEXICAL_PRODUCER_REFERENCE"):
            inspect(self.root,self.base,h)
    def test_new_direct_guarded_zip_refused(self):
        h=self.write_commit("Tools/producer.py",
             "with guarded_zip('CONTENT-NEW.zip',purpose='stage5_acceptance') as z:\n    pass\n")
        with self.assertRaisesRegex(ValueError,"NEW_UNGATED_LEXICAL_PRODUCER_REFERENCE"):
            inspect(self.root,self.base,h)
    def test_new_dotted_python_m_legacy_builder_refused(self):
        h=self.write_commit(".github/workflows/new-module-producer.yml",
            "jobs:\n  release:\n    steps:\n      - run: python -m Tools.build_governed_clean_delivery_v1 source output\n")
        with self.assertRaisesRegex(ValueError,"NEW_UNGATED_LEXICAL_PRODUCER_REFERENCE"):
            inspect(self.root,self.base,h)

    def test_new_direct_import_of_legacy_builder_refused(self):
        h=self.write_commit("Workspaces/menschen-b1-verben-kombinationen-v336/build.py",
            "from Tools.build_governed_clean_delivery_v1 import run as publish\npublish(source,output,receipt)\n")
        with self.assertRaisesRegex(ValueError,"NEW_UNGATED_LEXICAL_PRODUCER_REFERENCE"):
            inspect(self.root,self.base,h)

    def test_new_importlib_legacy_builder_refused(self):
        h=self.write_commit("Tools/alternate_lexical_producer.py",
            "import importlib\npublisher=importlib.import_module('Tools.build_clean_delivery')\n")
        with self.assertRaisesRegex(ValueError,"NEW_UNGATED_LEXICAL_PRODUCER_REFERENCE"):
            inspect(self.root,self.base,h)

    def test_new_bare_import_of_historical_builder_refused(self):
        h=self.write_commit("Tools/adapt_content.py",
            "import build_front_gated_clean_delivery_v1 as bare_builder\n")
        with self.assertRaisesRegex(ValueError,"NEW_UNGATED_LEXICAL_PRODUCER_REFERENCE"):
            inspect(self.root,self.base,h)

    def test_historical_unchanged_wrapper_not_retroactively_blocked(self):
        p="Workspaces/menschen-a2/tools/package_release.py"
        self.write_commit(p,"with guarded_zip(out,purpose='final_delivery') as z: pass\n")
        parent=self.g("rev-parse","HEAD").strip()
        head=self.write_commit("Workspaces/menschen-a1-verben-wortfamilie-v336/notes.txt",
            "unrelated content note")
        self.assertEqual(inspect(self.root,parent,head)["status"],
            "PASS_NO_NEW_UNGATED_PRODUCTION_ENTRYPOINT_REFERENCES")
    def test_strict_quality_launcher_accepted(self):
        head=self.write_commit("Tools/new_producer.py",
            'subprocess.run(["python","Tools/build_quality_gated_lexical_candidate_v1.py",*arguments])\n')
        self.assertEqual(inspect(self.root,self.base,head)["status"],
            "PASS_NO_NEW_UNGATED_PRODUCTION_ENTRYPOINT_REFERENCES")
    def test_bypass_in_first_of_multiple_commits_still_blocked(self):
        self.write_commit("Tools/misroute.py",
            'subprocess.run(["python","Tools/build_governed_clean_delivery_v1.py",source,zip_path])\n')
        previous=self.g("rev-parse","HEAD").strip()
        head=self.write_commit("Tools/legit.py","print('non publishing build')\n")
        self.assertEqual(inspect(self.root,previous,head)["code_files_compared"],1)
        with self.assertRaisesRegex(ValueError,"NEW_UNGATED_LEXICAL_PRODUCER_REFERENCE"):
            inspect(self.root,self.base,head)
    def test_documentation_and_regression_tests_are_not_producer_calls(self):
        head=self.write_commit("Verification/tests/test_legacy_format.py",
            'assert "build_clean_delivery.py" in historical_note\n')
        self.assertEqual(inspect(self.root,self.base,head)["code_files_compared"],0)
    def test_code_comment_is_not_an_invocation(self):
        head=self.write_commit("Tools/nonrelease.py",
            '# Old builder build_clean_delivery.py is historical only\nprint("not a release")\n')
        self.assertEqual(inspect(self.root,self.base,head)["status"],
            "PASS_NO_NEW_UNGATED_PRODUCTION_ENTRYPOINT_REFERENCES")
    def test_real_nonimport_writer_is_exact_sha_pinned(self):
        path="Workspaces/aspekte-b1plus-v336/Tools/build_P1_remaining83_v1.py"
        raw=(ROOT/path).read_bytes().replace(b"\r\n",b"\n")
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        self.assertEqual(blob,PINNED_NONIMPORT_GUARDED_CHECKPOINTS[path])
        self.assertIn(b"with guarded_zip(OUT,purpose='validated_major_checkpoint',",raw)
        self.assertIn(b"'formal_release_approvals':0",raw)
        self.assertIn(b"'stage5_import_ready':False",raw)

    def test_exact_pinned_nonimport_guard_passes_scoped_synthetic(self):
        path="Workspaces/aspekte-b1plus-v336/Tools/build_P1_remaining83_v1.py"
        head=self.write_commit(path,
            "with guarded_zip(out,purpose='validated_major_checkpoint',evidence=proof) as z:\n    pass\n")
        blob=self.g("rev-parse",f"HEAD:{path}").strip()
        with patch.dict(PINNED_NONIMPORT_GUARDED_CHECKPOINTS,{path:blob}):
            self.assertEqual(inspect(self.root,self.base,head)["status"],
                "PASS_NO_NEW_UNGATED_PRODUCTION_ENTRYPOINT_REFERENCES")

    def test_changed_pinned_nonimport_writer_fails_closed(self):
        path="Workspaces/aspekte-b1plus-v336/Tools/build_P1_remaining83_v1.py"
        head=self.write_commit(path,
            "with guarded_zip(out,purpose='final_delivery') as z:\n    pass\n")
        with self.assertRaisesRegex(ValueError,
              "FROZEN_NONIMPORT_GUARDED_CHECKPOINT_BLOB_DRIFT"):
            inspect(self.root,self.base,head)

    def test_unpinned_nonimport_guarded_zip_still_refused(self):
        path="Workspaces/aspekte-b1plus-v336/Tools/new_checkpoint.py"
        head=self.write_commit(path,
            "with guarded_zip(out,purpose='validated_major_checkpoint',evidence=proof) as z:\n    pass\n")
        with self.assertRaisesRegex(ValueError,"NEW_UNGATED_LEXICAL_PRODUCER_REFERENCE"):
            inspect(self.root,self.base,head)

    def test_scopes_only_code_and_producer_workflow(self):
        self.assertTrue(scope("Tools/build_more.py"))
        self.assertTrue(scope(".github/workflows/publish.yml"))
        self.assertTrue(scope("Workspaces/project/producer.sh"))
        self.assertFalse(scope("Verification/tests/test_release.py"))
        self.assertFalse(scope("Workspaces/project/LATEST.json"))
        self.assertFalse(scope("Docs/README.md"))

if __name__=="__main__":unittest.main()
