#!/usr/bin/env python3
"""Canonical routing regression tests: preservation, no sibling CURRENT, no silent new dir."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[2]/"Tools"/"validate_canonical_family_workspaces_v1.py"
spec=importlib.util.spec_from_file_location("canonical_workspace_guard",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CanonicalWorkspaceGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)/"repo"
        self.home.mkdir()
        self.catalog={"families":[],"workspaces":[]}
        self.portfolio={"items":[]}
        self.routing={"schema":m.SCHEMA,
            "change_type":"ADDITIVE_ROUTING_AND_NEW_WORKSPACE_CREATION_GUARD__NO_PHYSICAL_MIGRATION",
            "prohibition":{k:False for k in ("auto_folder_move","auto_delete","auto_new_workspaces",
                                            "auto_accept_content","auto_stage6_final","auto_release_promotion")},
            "families":[],"workspaces":[],"migration_authorizations":[]}
        for i in range(21):
            fid=f"family:demo-{i}"
            library=f"/Flasch kart/German-Content-Production-Kit/Content/Demo-{i}"
            active=f"Workspaces/family-demo-{i}" if i<16 else None
            self.catalog["families"].append({"id":fid,"library_path":library})
            selected=(("b"*63)+str(i%10)) if i<10 else None
            self.routing["families"].append({"family_id":fid,"canonical_library_root":library,
                "canonical_git_workspace":active,"initial_canonical_git_workspace":active,"active_content_sha256":selected,
                "canonical_source_owner_document":active+"/LATEST.json" if i<10 else None,
                "no_new_git_workspace_created":True})
            if active:
                self.add_workdir(fid,active,canonical=True)
            if i<10:
                self.portfolio["items"].append({"id":fid,"owner_locator":{"path":active+"/LATEST.json"},
                    "active_baseline":{"artifact_sha256":selected}})
        for k in range(20):
            self.add_workdir("family:demo-0",f"Workspaces/legacy-demo-{k}",canonical=False,
                             future="Workspaces/family-demo-0")
        self.routing["grandfathered_workspace_directories"]=sorted(x["git_dir"] for x in self.catalog["workspaces"])
        self.routing["counts"]={"families":21,"canonical_git_workspaces":16,
            "library_only_families":5,"prior_workspace_directories":36,
            "legacy_compatibility_directories":20}
        self.persist()

    def add_workdir(self,fid,rel,canonical=False,future=None):
        w={"id":"workspace:"+rel.split("/")[-1],"git_dir":rel,"parent_family_id":fid}
        self.catalog["workspaces"].append(w)
        role="CANONICAL" if canonical else "COMPATIBILITY_LEGACY"
        self.routing["workspaces"].append({"workspace_id":w["id"],"family_id":fid,"git_dir":rel,
            "role":role,"archive_or_move_status":"NOT_MOVED_NOT_DELETED",
            "future_accepted_current_pointer_location":future or rel})
        (self.home/rel).mkdir(parents=True,exist_ok=True)

    def persist(self):
        for rel,obj in ((m.CATALOG,self.catalog),(m.ROUTING,self.routing),(m.PORTFOLIO,self.portfolio)):
            path=self.home/rel
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf8")

    def route(self,n):
        return self.routing["families"][n]

    def expect_hold(self):
        self.persist()
        with self.assertRaises(ValueError):
            m.inspect(self.home)

    def test_good_baseline_one_canonical_per_family(self):
        r=m.inspect(self.home)
        self.assertIn("PASS_ROUTING",r["status"])
        self.assertEqual(r["counts"]["canonical_git"],16)
        self.assertEqual(r["counts"]["preserved_legacy"],20)

    def test_auditing_does_not_edit_any_source(self):
        raw=(self.home/m.ROUTING).read_bytes()
        m.inspect(self.home)
        self.assertEqual(raw,(self.home/m.ROUTING).read_bytes())

    def test_two_canonical_roles_block(self):
        self.routing["workspaces"][-1]["role"]="CANONICAL"
        self.expect_hold()

    def test_wrong_family_owner_role_block(self):
        self.routing["workspaces"][1]["family_id"]="family:demo-0"
        self.expect_hold()

    def test_unregistered_new_sibling_dir_block(self):
        (self.home/"Workspaces"/"rogue-branch").mkdir()
        self.expect_hold()

    def test_catalog_and_role_new_noncanonical_still_block(self):
        self.add_workdir("family:demo-0","Workspaces/sibling-unapproved",
                         canonical=False,future="Workspaces/family-demo-0")
        self.expect_hold()

    def test_fake_canonical_move_without_receipt_block(self):
        r=self.route(0)
        r["canonical_git_workspace"]="Workspaces/new-owner-0"
        r["canonical_source_owner_document"]="Workspaces/new-owner-0/LATEST.json"
        self.portfolio["items"][0]["owner_locator"]["path"]="Workspaces/new-owner-0/LATEST.json"
        self.routing["workspaces"][0]["role"]="COMPATIBILITY_LEGACY"
        self.routing["workspaces"][0]["future_accepted_current_pointer_location"]="Workspaces/new-owner-0"
        for w in self.routing["workspaces"][16:]:
            w["future_accepted_current_pointer_location"]="Workspaces/new-owner-0"
        self.add_workdir("family:demo-0","Workspaces/new-owner-0",canonical=True)
        self.expect_hold()

    def test_deleted_existing_directory_block(self):
        (self.home/"Workspaces/family-demo-1").rmdir()
        self.expect_hold()

    def test_current_accepted_sha_drift_block(self):
        self.portfolio["items"][0]["active_baseline"]["artifact_sha256"]="c"*64
        self.expect_hold()

    def test_curated_source_owner_must_be_in_canonical_dir(self):
        self.portfolio["items"][0]["owner_locator"]["path"]="Workspaces/legacy-demo-0/LATEST.json"
        self.route(0)["canonical_source_owner_document"]="Workspaces/legacy-demo-0/LATEST.json"
        self.expect_hold()

    def test_family_without_git_cannot_claim_fake_current(self):
        self.route(20)["active_content_sha256"]="c"*64
        self.expect_hold()

    def test_library_root_mismatch_block(self):
        self.route(9)["canonical_library_root"]="/Flasch kart/wrong-place"
        self.expect_hold()

    def test_modified_grandfathered_baseline_block(self):
        self.routing["grandfathered_workspace_directories"].pop()
        self.expect_hold()

    def test_changed_auto_promotion_flag_block(self):
        self.routing["prohibition"]["auto_release_promotion"]=True
        self.expect_hold()

    def test_unsafe_directory_path_rejected(self):
        for s in ("Workspaces/../oops","Workspaces/x/deeper","Workspaces/..\\secret","/etc"):
            with self.subTest(path=s),self.assertRaises(ValueError):
                m.safe_dir(self.home,s)

    def test_symlink_outside_checkout_rejected(self):
        link=self.home/"Workspaces"/"outside"
        target=Path(self.tmp.name)/"outside"
        target.mkdir()
        try:
            link.symlink_to(target,target_is_directory=True)
        except OSError:
            self.skipTest("Symlinks unavailable")
        with self.assertRaises(ValueError):
            m.safe_dir(self.home,"Workspaces/outside")

    def test_approval_missing_from_valid_path_must_block(self):
        auth={"family_id":"family:demo-20","new_git_workspace":"Workspaces/first",
              "previous_git_workspace":None,
              "approval_receipt":"Optimization-Program/Control-Center/Approvals/first.json"}
        with self.assertRaises(ValueError):
            m.authority_approval(self.home,auth,"family:demo-20","Workspaces/first",None)

    def test_approval_must_identify_exact_scope(self):
        path=self.home/"Optimization-Program/Control-Center/Approvals/test.json"
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({"schema":m.NEW_AUTHORIZATION_SCHEMA,
            "user_explicit_approval":True,"family_id":"family:demo-20",
            "new_git_workspace":"Workspaces/first","previous_git_workspace":None,
            "approval_scope":"DELETE_OLD"}))
        auth={"family_id":"family:demo-20","new_git_workspace":"Workspaces/first",
              "previous_git_workspace":None,"approval_receipt":
              "Optimization-Program/Control-Center/Approvals/test.json"}
        with self.assertRaises(ValueError):
            m.authority_approval(self.home,auth,"family:demo-20","Workspaces/first",None)

    def test_cli_external_derived_report_passes_and_stays_read_only(self):
        dest=Path(self.tmp.name)/"output"
        with contextlib.redirect_stdout(io.StringIO()):
            result=m.main(["--repo-root",str(self.home),"--out-dir",str(dest)])
        self.assertEqual(result,0)
        self.assertTrue((dest/"CANONICAL-WORKSPACE-GATE.json").exists())
        self.assertEqual(json.loads((dest/"CANONICAL-WORKSPACE-GATE.json").read_text())["counts"]["families"],21)

    def approve(self,fid,new,former,short):
        path=f"Optimization-Program/Control-Center/Approvals/{short}.json"
        receipt={"schema":m.NEW_AUTHORIZATION_SCHEMA,
            "user_explicit_approval":True,"family_id":fid,
            "new_git_workspace":new,"previous_git_workspace":former,
            "approval_scope":"CANONICAL_WORKSPACE_ROUTE_ONLY_NO_DATA_DELETION"}
        dest=self.home/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(receipt))
        self.routing["migration_authorizations"].append({
            "family_id":fid,"new_git_workspace":new,
            "previous_git_workspace":former,"approval_receipt":path})

    def test_approved_first_git_workspace_for_library_only_family_passes(self):
        fid="family:demo-20"
        new="Workspaces/family-demo-20"
        self.add_workdir(fid,new,canonical=True)
        self.route(20)["canonical_git_workspace"]=new
        self.route(20)["no_new_git_workspace_created"]=False
        self.routing["counts"]["canonical_git_workspaces"]=17
        self.routing["counts"]["library_only_families"]=4
        self.approve(fid,new,None,"first")
        self.persist()
        x=m.inspect(self.home)
        self.assertEqual(x["counts"]["approved_new_dirs"],1)
        self.assertEqual(x["counts"]["canonical_git"],17)
        self.assertIn("APPROVED_CHANGES_CHECKED",x["status"])

    def test_approved_canonical_reassignment_to_existing_legacy_dir_passes(self):
        fid="family:demo-0"
        former="Workspaces/family-demo-0"
        replacement="Workspaces/legacy-demo-0"
        self.route(0)["canonical_git_workspace"]=replacement
        self.route(0)["canonical_source_owner_document"]=replacement+"/LATEST.json"
        self.portfolio["items"][0]["owner_locator"]["path"]=replacement+"/LATEST.json"
        for w in self.routing["workspaces"]:
            if w["family_id"]==fid:
                w["future_accepted_current_pointer_location"]=replacement
                w["role"]="CANONICAL" if w["git_dir"]==replacement else "COMPATIBILITY_LEGACY"
        self.approve(fid,replacement,former,"existing-reassign")
        self.persist()
        r=m.inspect(self.home)
        self.assertEqual(r["counts"]["approved_new_dirs"],0)
        self.assertIn("APPROVED_CHANGES_CHECKED",r["status"])

    def test_existing_legacy_reassignment_without_approval_rejected(self):
        fid="family:demo-0"
        former="Workspaces/family-demo-0"
        replacement="Workspaces/legacy-demo-0"
        self.route(0)["canonical_git_workspace"]=replacement
        self.route(0)["canonical_source_owner_document"]=replacement+"/LATEST.json"
        self.portfolio["items"][0]["owner_locator"]["path"]=replacement+"/LATEST.json"
        for w in self.routing["workspaces"]:
            if w["family_id"]==fid:
                w["future_accepted_current_pointer_location"]=replacement
                w["role"]="CANONICAL" if w["git_dir"]==replacement else "COMPATIBILITY_LEGACY"
        self.expect_hold()

    def test_no_report_written_into_checkout(self):
        dest=self.home/"output"
        with contextlib.redirect_stdout(io.StringIO()):
            status=m.main(["--repo-root",str(self.home),"--out-dir",str(dest)])
        self.assertEqual(status,2)
        self.assertFalse(dest.exists())

    def test_duplicate_family_identity_rejected(self):
        self.routing["families"][0]["family_id"]="family:demo-1"
        self.expect_hold()

if __name__=="__main__":
    unittest.main()
