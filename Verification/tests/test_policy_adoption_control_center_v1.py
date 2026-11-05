"""Policy-adoption Control Center: real Git-index snapshot + adversarial receipt truth."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"Tools/build_policy_adoption_control_center_v1.py"
spec=importlib.util.spec_from_file_location("gfp_policy_control",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class AdoptionDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=m.graph.index_blobs(ROOT)
        cls.ledger=m.phase.load_json_from_index(m.LEDGER,cls.index,ROOT)
        cls.cat=m.phase.load_json_from_index(m.CATALOG,cls.index,ROOT)
        cls.reg=m.phase.load_json_from_index(m.REGISTRY,cls.index,ROOT)
        cls.domains=m.phase.load_json_from_index(m.DOMAINS,cls.index,ROOT)
        cls.history=m.source_proof(cls.ledger,cls.index,cls.cat,cls.reg)
        cls.output=m.execute()

    def check(self,ledger=None,index=None,cat=None,reg=None):
        return m.source_proof(
            copy.deepcopy(self.ledger if ledger is None else ledger),
            copy.deepcopy(self.index if index is None else index),
            copy.deepcopy(self.cat if cat is None else cat),
            copy.deepcopy(self.reg if reg is None else reg)
        )

    def test_one_verifiable_central_source_of_trust(self):
        self.assertEqual(self.output["schema"],m.SCHEMA)
        self.assertEqual(self.output["status"],
          "PASS_CROSS_PROJECT_POLICY_STATUS_AS_GIT_INDEX_REPORT__ZERO_NEW_ADOPTIONS")
        self.assertEqual(self.output["controller"],"Project Control Center")
        self.assertTrue(self.output["data_authority"]["git_index_not_verified_live_remote_main"])

    def test_all_21_source_families_without_double_counting(self):
        n=self.output["counts"]
        self.assertEqual((n["families"],n["workspaces"],n["roots"]),(21,34,17))
        self.assertEqual((n["central_policy_bindings"],n["policy_family_candidate_impacts"]),(15,315))
        self.assertEqual((n["workspace_pointer_navigation_views"],n["root_pointer_navigation_views"]),(510,255))

    def test_all_source_families_in_same_order_as_catalog(self):
        self.assertEqual(
            [x["family_id"] for x in self.output["source_families"]],
            [x["id"] for x in self.cat["families"]]
        )

    def test_no_synthetic_or_historical_pass_promoted(self):
        self.assertEqual(self.output["counts"]["formally_adopted_producers"],0)
        self.assertEqual(self.output["counts"]["new_governed_policy_adoption_claims"],0)
        self.assertEqual(self.output["counts"]["stage4_5_6_7_certified_by_dashboard"],0)
        self.assertTrue(all(x["formal_policy_adoption"]=="NOT_ADOPTED"
                            and x["source_currentness"]=="NOT_VERIFIED_BY_THIS_LEDGER"
                            and x["new_governed_producer_receipt"]=="NOT_REGISTERED"
                            for x in self.output["source_families"]))
        self.assertTrue(all(self.output["acceptance_boundaries"].values()))

    def test_previous_real_250_verben_bytes_remain_nonadoption(self):
        x=next(r for r in self.output["source_families"]
               if r["family_id"]=="family:250-verben-mit-praepositionen")
        self.assertEqual(x["historical_evidence_state"],
                         "HISTORICAL_REAL_BYTES_MATCH_BUT_NO_NEW_GOVERNED_RECEIPT")
        self.assertEqual(x["real_legacy_details"]["archive_sha256"],
                         "63ae8f2a3a8d2ec5dff94798db3ed060a0b4e43b1cc2699e540beb1393882e5c")
        self.assertFalse(x["real_legacy_details"]["not_new_policy_adoption"] is False)

    def test_second_native_witness_is_format_only(self):
        x=next(r for r in self.output["source_families"]
               if r["family_id"]=="family:menschen-a1-verben")
        self.assertEqual(x["historical_evidence_state"],
                         "HISTORICAL_REAL_FORMAT_ONLY__NO_NEW_GOVERNED_RECEIPT")

    def test_grammar_and_lesen_and_schreiben_not_forced_to_neutral_vocab(self):
        groups={"family:grammatik-aktiv-a1-b1":"DEFINE_GRAMMAR_SPECIFIC_PRODUCER_ADAPTER",
                "family:lesen":"DEFINE_LESEN_SOURCE",
                "family:schreiben":"DEFINE_SCHREIBEN_NATIVE_OUTPUT"}
        for fid,prefix in groups.items():
            x=next(r for r in self.output["source_families"] if r["family_id"]==fid)
            self.assertTrue(x["next_action"].startswith(prefix))
            self.assertEqual(x["key_policies"]["stage5_neutral_validator"],
                             "DOMAIN_ADAPTER_REQUIRED_NO_FORCED_LEXICAL_SCHEMA")

    def test_qa_workspaces_stay_nav_only(self):
        paths=[w["git_dir"] for f in self.output["source_families"]
               for w in f["git_workspaces"] if w["kind"]=="CROSS_SOURCE_QA_OR_RUNTIME_WORKSPACE"]
        self.assertLessEqual(len(paths),34)
        self.assertTrue(all("pointer_adoption_proof" in w for f in self.output["source_families"]
                            for w in f["git_workspaces"]))

    def test_exact_registry_pin_must_match_actual_git_index(self):
        bad=copy.deepcopy(self.ledger)
        bad["baseline"]["policy_registry"]["git_blob"]="f"*40
        with self.assertRaisesRegex(ValueError,"LEDGER_BASELINE_GIT_PIN_DRIFT"):
            self.check(ledger=bad)

    def test_fake_great_global_adoption_refused(self):
        bad=copy.deepcopy(self.ledger)
        bad["adoption_status"]="ALL_21_ADOPTED"
        with self.assertRaisesRegex(ValueError,"FALSE_GLOBAL_OR_SOURCE_PRODUCER_ADOPTION"):
            self.check(ledger=bad)

    def test_spoofed_one_new_adopted_producer_rejected(self):
        bad=copy.deepcopy(self.ledger)
        bad["adoption_claims"]=[{"family_id":"family:250-verben-mit-praepositionen",
                                 "status":"ADOPTED"}]
        with self.assertRaisesRegex(ValueError,"FALSE_GLOBAL_OR_SOURCE_PRODUCER_ADOPTION"):
            self.check(ledger=bad)

    def test_guard_against_auto_migrating_locked(self):
        bad=copy.deepcopy(self.ledger)
        bad["submission_contract"]["no_retroactive_rewrite_of_locked_content"]=False
        with self.assertRaisesRegex(ValueError,"ADOPTION_PROOF_GATE_DISABLED"):
            self.check(ledger=bad)

    def test_guard_against_auto_adoption_from_synthetic_ci(self):
        bad=copy.deepcopy(self.ledger)
        bad["submission_contract"]["no_auto_adoption_from_synthetic_ci"]=False
        with self.assertRaisesRegex(ValueError,"ADOPTION_PROOF_GATE_DISABLED"):
            self.check(ledger=bad)

    def test_forged_real_r8_archive_digest_rejected(self):
        bad=copy.deepcopy(self.ledger)
        bad["historical_scoped_evidence"][0]["historical_archive_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"HISTORICAL_RECEIPT_SHA_OWNER_SIZE_MISMATCH"):
            self.check(ledger=bad)

    def test_historical_receipt_is_git_blob_pinned(self):
        bad=copy.deepcopy(self.ledger)
        bad["historical_scoped_evidence"][0]["report_git_blob"]="a"*40
        with self.assertRaisesRegex(ValueError,"HISTORICAL_CONNECTOR_REPORT_NOT_PINNED"):
            self.check(ledger=bad)

    def test_wrong_source_owner_of_historical_receipt_refused(self):
        bad=copy.deepcopy(self.ledger)
        bad["historical_scoped_evidence"][0]["family_id"]="family:menschen-a1"
        with self.assertRaisesRegex(ValueError,"HISTORICAL_ANCHOR_WRONG_OWNER"):
            self.check(ledger=bad)

    def test_old_latest_pointer_move_is_not_a_false_current_pass(self):
        changed=copy.deepcopy(self.index)
        key=self.ledger["historical_scoped_evidence"][0]["old_source_latest_path"]
        changed[key]="a"*40
        report=self.check(index=changed)
        self.assertFalse(report["historical_pointer_is_still_in_git_index"])
        self.assertEqual(report["historical_pointer_index_blob_today"],"a"*40)

    def test_injecting_unreviewed_historical_evidence_fails(self):
        bad=copy.deepcopy(self.ledger)
        bad["historical_scoped_evidence"].append(copy.deepcopy(
            bad["historical_scoped_evidence"][0]))
        with self.assertRaisesRegex(ValueError,"UNREVIEWED_HISTORICAL_EVIDENCE_COUNT"):
            self.check(ledger=bad)

    def test_broken_policy_impact_cardinality_is_refused(self):
        cat,registry,prev,pilot,receipt=None,None,None,None,None
        p,c,r,old,pil,proof=m.planner.authority()
        impact=m.planner.build_impact(p,c,r,old)
        impact["family_impacts"]=impact["family_impacts"][:-1]
        index=self.index
        state=m.phase.load_json_from_index(m.ROOT_STATE,index,ROOT)
        pointers={}
        for d in m.phase.tracked_dirs(index):
            for suffix in ("LATEST.json","CHECKPOINT.json"):
                key=d+"/"+suffix
                if key in index:pointers[key]=m.phase.load_json_from_index(key,index,ROOT)
        snapshot=m.phase.build(c,index,state,pointers)
        with self.assertRaisesRegex(ValueError,"POLICY_IMPACT_CARDINALITY_MISMATCH"):
            m.build(self.ledger,index,snapshot,impact,c,self.domains,self.history)

    def test_report_contains_usable_workspace_hints(self):
        arr=[w for f in self.output["source_families"] for w in f["git_workspaces"]]
        self.assertEqual(len(arr),34)
        self.assertTrue(all(w["git_dir"].startswith("Workspaces/") for w in arr))
        self.assertTrue(any(w["selected_pointer"] for w in arr))
        self.assertTrue(all(w["pointer_adoption_proof"]=="NOT_CERTIFIED" for w in arr))

    def test_fresh_markdown_contains_each_family_and_no_fake_pass(self):
        content=m.markdown(self.output)
        self.assertIn("250-Verben-mit-Praepositionen",content)
        self.assertIn("Formal new governed producer adoptions: 0",content)
        self.assertIn("Lesen",content)
        self.assertIn("NOT_ADOPTED",content)

    def test_cli_generates_json_and_markdown_reports(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"dashboard"
            args=[sys.executable,"-B",str(SCRIPT),"--output-dir",str(target)]
            result=subprocess.run(args,cwd=ROOT,capture_output=True,
                                  text=True,encoding="utf-8",timeout=70)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((target/"POLICY-ADOPTION-STATUS.json").exists())
            self.assertTrue((target/"POLICY-ADOPTION-STATUS.md").exists())
            parsed=json.loads((target/"POLICY-ADOPTION-STATUS.json").read_text(encoding="utf-8"))
            self.assertEqual(parsed["counts"]["families"],21)
            self.assertEqual(parsed["counts"]["formally_adopted_producers"],0)

    def test_cli_refuses_overwriting_previous_dashboard(self):
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)/"dashboard"
            command=[sys.executable,"-B",str(SCRIPT),"--output-dir",str(dest)]
            first=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=70)
            self.assertEqual(first.returncode,0,first.stderr)
            initial=(dest/"POLICY-ADOPTION-STATUS.json").read_bytes()
            second=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=70)
            self.assertEqual(second.returncode,2)
            self.assertEqual(initial,(dest/"POLICY-ADOPTION-STATUS.json").read_bytes())

    def test_cli_rejects_unknown_family(self):
        with tempfile.TemporaryDirectory() as td:
            c=[sys.executable,"-B",str(SCRIPT),"--output-dir",td,
               "--family-id","family:nonexistent"]
            a=subprocess.run(c,cwd=ROOT,text=True,capture_output=True,timeout=70)
            self.assertEqual(a.returncode,2)
            self.assertIn("UNKNOWN_FAMILY",a.stderr)

    def test_nonlexical_shadow_preflight_is_joined_not_adopted(self):
        report=self.output["nonlexical_domain_preflight"]
        self.assertEqual(report["counts"]["nonlexical_family_profiles"],8)
        self.assertEqual(self.output["counts"]["nonlexical_source_families_profiled"],8)
        self.assertEqual(report["counts"]["actual_domain_adapters_adopted"],0)
        self.assertTrue(all(x["real_native_adapter_adopted"] is False
                            for x in report["source_families"]))

    def test_unified_dashboard_has_actual_lesen_stage1_derived_byte_replay(self):
        preflight=self.output["nonlexical_domain_preflight"]
        self.assertEqual(preflight["counts"]["real_git_native_reading_stage1_structure_replays"],1)
        self.assertEqual(preflight["counts"]["real_nonlexical_native_policy_adoptions"],0)
        lesen=next(x for x in preflight["source_families"]
                   if x["family_id"]=="family:lesen")
        self.assertEqual(lesen["native_stage1_actual_git_derived_replay"]["replayed_counts"]["topics"],68)
        self.assertFalse(lesen["native_stage1_actual_git_derived_replay"][
                         "actual_independent_stage1_source_pdf_bytes_revalidated"])
        self.assertEqual(self.output["counts"]["formally_adopted_producers"],0)
        self.assertIn("REAL Git inventory + ID map 68 topics / 76 pages",m.markdown(self.output))

    def test_five_root_checkpoint_triages_explain_metadata_issues(self):
        report=self.output["nonlexical_domain_preflight"]
        self.assertEqual(self.output["counts"]["triaged_untracked_root_checkpoints"],5)
        self.assertEqual(len([x for x in report["root_checkpoint_issue_triage"]
                             if x.get("root_key")]),5)
        self.assertTrue(all(x["auto_repair"] is False for x in
                            report["root_checkpoint_issue_triage"]))
        md=m.markdown(self.output)
        self.assertIn("Untracked main checkpoint references",md)

    def test_single_dashboard_shows_branch_qualified_checkpoints_without_current_claim(self):
        preflight=self.output["nonlexical_domain_preflight"]
        self.assertEqual(preflight["counts"]["branch_qualified_checkpoint_candidates"],5)
        self.assertEqual(preflight["counts"]["unresolved_grammar_branch_checkpoint_candidates"],0)
        self.assertTrue(all(r["auto_repair"] is False for r in
                            preflight["root_checkpoint_issue_triage"]))
        self.assertIn("five historical owner-branch locators",m.markdown(self.output))
        self.assertIn("SOURCE OWNER HOLD",m.markdown(self.output))
        self.assertEqual(self.output["counts"]["formally_adopted_producers"],0)

    def test_no_production_files_modified_by_dry_readonly_report(self):
        targets=[m.LEDGER,m.CATALOG,m.DOMAINS,m.REGISTRY,m.SOURCE_RECEIPT]
        before={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in targets}
        self.assertEqual(m.execute()["counts"]["formally_adopted_producers"],0)
        after={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in targets}
        self.assertEqual(before,after)

if __name__=="__main__":
    unittest.main()
