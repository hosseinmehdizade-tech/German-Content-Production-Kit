#!/usr/bin/env python3
"""Regression tests: parallel source discovery never promotes accepted cards."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from types import SimpleNamespace

SCRIPT=Path(__file__).resolve().parents[2]/"Tools"/"discover_parallel_accepted_sources_v1.py"
spec=importlib.util.spec_from_file_location("parallel_accepted_discovery",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
OLD="a"*64
NEW="b"*64


class ParallelDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/"repo"
        self.root.mkdir()
        self.catalog={"workspaces":[]}
        self.registry={"schema":"gfp-opt-dynamic-content-portfolio-registry@1.0.0","items":[]}
        self.preserve={}
        for i in range(10):
            fid="family:test-"+str(i)
            dirname="Workspaces/owner-"+str(i)
            path=dirname+"/LATEST.json"
            data={"date":"2026-11-07","status":"CONTENT_FINAL_USER_ACCEPTED__APP_NOT_FINAL",
                  "artifact":{"sha256":OLD,"name":"accepted-"+str(i)+".zip"}}
            blob=self.store(path,data)
            self.preserve[path]=data
            self.catalog["workspaces"].append({"git_dir":dirname,"parent_family_id":fid})
            self.registry["items"].append({"id":fid,"active_baseline":{"artifact_sha256":OLD},
                "owner_locator":{"repository":m.REPO,"path":path,"git_blob_observed":blob,
                                  "artifact_sha_json_pointer":"/artifact/sha256"}})
        self.store(m.REGISTRY,self.registry)
        self.store(m.CATALOG,self.catalog)

    def store(self,path,data):
        target=self.root/path
        target.parent.mkdir(parents=True,exist_ok=True)
        raw=(json.dumps(data,sort_keys=True)+"\n").encode()
        target.write_bytes(raw)
        return m.blob(raw)

    def add_sibling(self,status="R10_CONTENT_FINAL_USER_ACCEPTED__APP_STAGE7_NOT_FINAL",
                    date="2026-11-08",sha=NEW,name="new.zip",field="artifact"):
        path="Workspaces/parallel-"+str(len(self.catalog["workspaces"]))+"/LATEST.json"
        parent=path.rsplit("/",1)[0]
        self.catalog["workspaces"].append({"git_dir":parent,"parent_family_id":"family:test-0"})
        data={"status":status,"date":date,field:{"sha256":sha,"name":name}}
        self.store(path,data)
        self.store(m.CATALOG,self.catalog)
        return path

    def test_no_sibling_source_is_clean_without_writes(self):
        before=(self.root/m.REGISTRY).read_bytes()
        report=m.investigate(self.root)
        self.assertEqual(report["status"],"NO_QUALIFIED_NEWER_ACCEPTED_SOURCE_OBSERVED")
        self.assertEqual(report["portfolio_families"],10)
        self.assertEqual(before,(self.root/m.REGISTRY).read_bytes())

    def test_regression_stale_repair4_vs_accepted_r10_is_flagged(self):
        self.add_sibling()
        report=m.investigate(self.root)
        row=report["families"][0]
        self.assertEqual(row["status"],"REVIEW_ALTERNATIVE_USER_ACCEPTED_SOURCE")
        self.assertEqual(row["alternatives"][0]["sha256"],NEW)
        self.assertEqual(row["current_sha256"],OLD)
        self.assertFalse(row["alternatives"][0]["date_comparison_is_proof_of_promotion"])
        self.assertEqual(report["status"],"REVIEW_PARALLEL_ACCEPTED_SOURCE")

    def test_older_accepted_sibling_is_documented_not_auto_promoted(self):
        self.add_sibling(date="2026-11-04")
        report=m.investigate(self.root)
        row=report["families"][0]
        self.assertEqual(row["alternatives"][0]["status"],
                         "HISTORICAL_ACCEPTED_SIBLING__NOT_RECOMMENDED_FOR_PROMOTION")
        self.assertEqual(report["status"],"NO_QUALIFIED_NEWER_ACCEPTED_SOURCE_OBSERVED")

    def test_same_date_is_not_automatic_supersession(self):
        self.add_sibling(date="2026-11-07")
        self.assertEqual(m.investigate(self.root)["status"],"REVIEW_PARALLEL_ACCEPTED_SOURCE")

    def test_pending_stage4_is_ignored(self):
        self.add_sibling(status="STAGE4_AI_WIP__NOT_FINAL")
        self.assertEqual(m.investigate(self.root)["status"],"NO_QUALIFIED_NEWER_ACCEPTED_SOURCE_OBSERVED")

    def test_negated_user_acceptance_not_qualified(self):
        self.add_sibling(status="NOT_USER_ACCEPTED__WIP")
        self.assertEqual(m.investigate(self.root)["status"],"NO_QUALIFIED_NEWER_ACCEPTED_SOURCE_OBSERVED")

    def test_draft_zip_even_with_user_accepted_status_is_not_new_release(self):
        self.add_sibling(name="CANDIDATE-WIP-NOT-IMPORT.zip")
        self.assertEqual(m.investigate(self.root)["status"],"NO_QUALIFIED_NEWER_ACCEPTED_SOURCE_OBSERVED")

    def test_no_name_no_release_identity(self):
        path=self.add_sibling()
        self.store(path,{"status":"USER_ACCEPTED_CONTENT_FINAL","date":"2026-11-08",
                         "artifact":{"sha256":NEW}})
        self.assertEqual(m.investigate(self.root)["status"],"NO_QUALIFIED_NEWER_ACCEPTED_SOURCE_OBSERVED")

    def test_different_sha_same_owner_current_file_holds(self):
        self.store("Workspaces/owner-0/LATEST.json",
                   {"status":"USER_ACCEPTED","artifact":{"sha256":NEW,"name":"different.zip"}})
        self.assertEqual(m.investigate(self.root)["status"],"HOLD_SELECTED_OWNER_DRIFT")

    def test_unmapped_directory_is_reported_not_mapped_by_guess(self):
        self.store("Workspaces/totally-new-project/LATEST.json",
                   {"status":"USER_ACCEPTED_CONTENT_FINAL","artifact":{"sha256":NEW,"name":"new.zip"}})
        r=m.investigate(self.root)
        self.assertEqual(r["status"],"REVIEW_UNMAPPED_WORKSPACES")
        self.assertIn("totally-new-project",r["unmapped_workspace_names"])

    def test_invalid_catalog_duplicate_workspace_hold(self):
        self.catalog["workspaces"].append(dict(self.catalog["workspaces"][0]))
        self.store(m.CATALOG,self.catalog)
        with self.assertRaises(ValueError):
            m.investigate(self.root)

    def test_security_parent_escape_rejected(self):
        with self.assertRaises(ValueError):
            m.below(self.root,"Workspaces/a/../../secret")
        with self.assertRaises(ValueError):
            m.below(self.root,"/etc/passwd")

    def test_malicious_symlink_cannot_leave_repo(self):
        target=Path(self.tmp.name)/"private.json"
        target.write_text('{"status":"USER_ACCEPTED"}')
        link=self.root/"Workspaces"/"owner-0"/"LATEST.json"
        link.unlink()
        try:
            link.symlink_to(target)
        except OSError:
            self.skipTest("symlinks unavailable")
        with self.assertRaises(ValueError):
            m.investigate(self.root)

    def test_git_blob_ignores_windows_checkout_crlf_normalization(self):
        owner="Workspaces/owner-0/LATEST.json"
        committed=(self.root/owner).read_bytes()
        (self.root/owner).write_bytes(committed.replace(b"\\n", b"\\r\\n"))
        (self.root/".git").mkdir()
        with mock.patch.object(m.subprocess, "run",
              return_value=SimpleNamespace(returncode=0, stdout=committed, stderr=b"")) as proc:
            self.assertEqual(m.git_owner_bytes(self.root,owner),committed)
            self.assertEqual(m.investigate(self.root)["status"],"NO_QUALIFIED_NEWER_ACCEPTED_SOURCE_OBSERVED")
            self.assertTrue(proc.called)

    def test_same_sha_in_sibling_not_alarm(self):
        self.add_sibling(sha=OLD)
        self.assertEqual(m.investigate(self.root)["status"],"NO_QUALIFIED_NEWER_ACCEPTED_SOURCE_OBSERVED")

    def test_multiple_sibling_sources_same_sha_deduplicated(self):
        self.add_sibling()
        self.add_sibling()
        r=m.investigate(self.root)
        self.assertEqual(len(r["families"][0]["alternatives"]),1)
        self.assertEqual(len(r["families"][0]["alternatives"][0]["evidence"]),2)

    def test_external_report_only_and_strict_exit_optin(self):
        self.add_sibling()
        target=Path(self.tmp.name)/"derived"
        with contextlib.redirect_stdout(io.StringIO()):
            status=m.main(["--repo-root",str(self.root),"--out-dir",str(target)])
            strict=m.main(["--repo-root",str(self.root),"--fail-on-review"])
        self.assertEqual(status,0)
        self.assertEqual(strict,2)
        doc=json.loads((target/"PARALLEL-SOURCES.json").read_text())
        self.assertEqual(doc["status"],"REVIEW_PARALLEL_ACCEPTED_SOURCE")
        self.assertTrue((target/"PARALLEL-SOURCES.md").exists())

    def test_reject_report_inside_source_checkout(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code=m.main(["--repo-root",str(self.root),
                         "--out-dir",str(self.root/"bad-output")])
        self.assertEqual(code,2)
        self.assertFalse((self.root/"bad-output").exists())


if __name__=="__main__":
    unittest.main()
