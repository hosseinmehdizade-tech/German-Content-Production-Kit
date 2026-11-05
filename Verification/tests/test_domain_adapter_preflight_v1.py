"""GFP-OPT P1 nonlexical adapter discovery and FIVE root pointer triage checks."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"Tools/build_domain_adapter_preflight_v1.py"
spec=importlib.util.spec_from_file_location("gfp_op_p1_domain_preflight",SCRIPT)
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class NonLexicalDomainPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual=p.execute()
        cls.idx=p.graph.index_blobs(ROOT)
        cls.cfg=p.current_git_json(cls.idx,p.PROFILE)
        for x in cls.cfg["input_pins"].values():
            if x["path"] not in cls.idx:
                cls.idx[x["path"]]=p.extra_index_path(x["path"])
        cls.catalog=p.current_git_json(cls.idx,cls.cfg["input_pins"]["catalog"]["path"])
        cls.domains=p.current_git_json(cls.idx,cls.cfg["input_pins"]["domains"]["path"])
        cls.sources=p.current_git_json(cls.idx,cls.cfg["input_pins"]["source_registry"]["path"])
        cls.routes=p.current_git_json(cls.idx,cls.cfg["input_pins"]["resume_routes"]["path"])
        shadow=p.module("op02_domain_preflight_test","Verification/audit_op02_typed_envelope_v2.py")
        cls.shadow={"workstreams":shadow.DOMAINS}
        state=p.current_git_json(cls.idx,"PROJECT-STATE.json")
        pointers={}
        for directory in p.phase.tracked_dirs(cls.idx):
            for name in ("LATEST.json","CHECKPOINT.json"):
                path=directory+"/"+name
                if path in cls.idx:
                    pointers[path]=p.phase.load_json_from_index(path,cls.idx)
        cls.issues=p.phase.build(cls.catalog,cls.idx,state,pointers)["issues"]

    def rerun(self,profile=None,catalog=None,domains=None,
              sources=None,routes=None,index=None,op02=None,issues=None):
        return p.assessment(
            copy.deepcopy(self.cfg if profile is None else profile),
            copy.deepcopy(self.catalog if catalog is None else catalog),
            copy.deepcopy(self.domains if domains is None else domains),
            copy.deepcopy(self.sources if sources is None else sources),
            copy.deepcopy(self.routes if routes is None else routes),
            copy.deepcopy(self.idx if index is None else index),
            copy.deepcopy(self.shadow if op02 is None else op02),
            copy.deepcopy(self.issues if issues is None else issues)
        )

    def test_actual_21_owner_catalog_nonlexical_8_profiles(self):
        self.assertEqual(self.actual["schema"],p.SCHEMA)
        self.assertEqual(self.actual["counts"]["nonlexical_family_profiles"],8)
        self.assertEqual(self.actual["counts"]["native_grammar_source_families"],3)
        self.assertEqual(self.actual["status"],
              "PASS_DOMAIN_AND_METADATA_ROUTING_ONLY__ALL_NATIVE_ADOPTIONS_HELD")

    def test_five_actual_untracked_roots_not_content_qa_errors(self):
        t=[x for x in self.actual["root_checkpoint_issue_triage"]
           if x.get("issue_type")=="ROOT_CHECKPOINT_UNTRACKED"]
        self.assertEqual(len(t),5)
        self.assertEqual(self.actual["counts"]["untracked_root_checkpoints"],5)
        self.assertEqual(self.actual["counts"]["classified_existing_root_checkpoint_issues"],5)
        self.assertTrue(all(x["status"]==
              "CONFIRMED_STALE_OR_UNMATERIALIZED_ROOT_CHECKPOINT_REFERENCE"
              and x["auto_repair"] is False for x in t))
        self.assertEqual({x["root_key"] for x in t},{
          "250_verben_mit_praepositionen_deutschweb",
          "250_verben_mit_praepositionen_kombinationen",
          "grammar_aktiv_a1_c1",
          "nomen_verb_verbindungen",
          "unregelmaessige_verben_kombinationen"
        })

    def test_five_branch_qualified_checkpoint_locations_are_navigation_not_current(self):
        self.assertEqual(self.actual["counts"]["branch_qualified_checkpoint_candidates"],5)
        self.assertEqual(self.actual["counts"]["unresolved_grammar_branch_checkpoint_candidates"],0)
        self.assertEqual(self.actual["root_branch_evidence_type"],
            "PINNED_HISTORICAL_BRANCH_LOCATION_ONLY__LIVE_REMOTE_WORKFLOW_SEPARATE")
        found=[x for x in self.actual["root_checkpoint_issue_triage"]
               if x.get("branch_checkpoint_historical_observation")]
        self.assertEqual(len(found),5)
        self.assertTrue(all(x["auto_repair"] is False and
            x["branch_checkpoint_historical_observation"]["source_currentness"]==
            "NOT_VERIFIED" for x in found))
        grammar=next(x for x in self.actual["root_checkpoint_issue_triage"]
                     if x.get("root_key")=="grammar_aktiv_a1_c1")
        self.assertEqual(grammar["branch_checkpoint_historical_observation"]["qualified_branch"],
                         "grammar-aktiv-a1-c1-production")
        self.assertEqual(grammar["branch_checkpoint_historical_observation"]["source_currentness"],
                         "NOT_VERIFIED")

    def test_nvv_october_branch_and_november_library_conflict_keeps_hold(self):
        row=next(x for x in self.actual["root_checkpoint_issue_triage"]
                 if x["root_key"]=="nomen_verb_verbindungen")
        self.assertEqual(row["branch_checkpoint_historical_observation"]["qualified_branch"],
                         "nvv-production")
        self.assertTrue(row["newer_library_candidate_is_unverified"]["source_currentness"].startswith(
                        "REVIEW_REQUIRED"))
        self.assertFalse(row["auto_repair"])

    def test_grammar_two_original_registered_hashes_without_checkpoint(self):
        row=next(x for x in self.actual["source_families"]
                 if x["family_id"]=="family:grammatik-aktiv-a1-c1")
        self.assertEqual(len(row["registered_sources"]),2)
        self.assertEqual(row["native_checkpoint_path"],
             "Workspaces/grammatik-aktiv-a1-c1/CHECKPOINT.json")
        self.assertEqual(row["status"],
             "BLOCKED_NATIVE_CHECKPOINT_UNTRACKED__DO_NOT_INVENT")
        self.assertFalse(row["real_native_adapter_adopted"])

    def test_lesen_real_source_and_existing_op02_shadow_only(self):
        row=next(x for x in self.actual["source_families"]
                 if x["family_id"]=="family:lesen")
        self.assertTrue(row["native_checkpoint_tracked_in_git_index"])
        self.assertEqual(row["op02_shadow_contract"],"reading-stage1-inventory@1")
        self.assertEqual(row["native_checkpoint_hint"]["stage1_declared_from_git_checkpoint"],"PASS")
        self.assertTrue(all(v=="NOT_STARTED" for v in
           row["native_checkpoint_hint"]["remaining_stages_declared_from_git_checkpoint"].values()))
        self.assertEqual(row["status"],
              "SHADOW_READING_STAGE1_METADATA_ONLY__STAGE2_TO_7_NOT_ACCEPTED")

    def test_lesen_real_native_stage1_git_bytes_replayed_not_adopted(self):
        row=next(x for x in self.actual["source_families"]
                 if x["family_id"]=="family:lesen")
        proof=row["native_stage1_actual_git_derived_replay"]
        self.assertEqual(proof["status"],
          "PASS_ACTUAL_GIT_READING_STAGE1_DERIVED_BYTES_AND_STRUCTURE_REPLAY_ONLY")
        self.assertEqual(proof["replayed_counts"]["topics"],68)
        self.assertEqual(proof["replayed_counts"]["pages"],76)
        self.assertFalse(proof["actual_independent_stage1_source_pdf_bytes_revalidated"])
        self.assertEqual(proof["new_policy_adoption"],"NOT_ADOPTED")
        self.assertEqual(self.actual["counts"]["real_git_native_reading_stage1_structure_replays"],1)
        self.assertEqual(self.actual["counts"]["real_nonlexical_native_policy_adoptions"],0)

    def test_aber_hallo_existing_op02_shadow_has_exact_pdf_identity(self):
        row=next(x for x in self.actual["source_families"]
                 if x["family_id"]=="family:aber-hallo-listen-tabellen")
        self.assertEqual(row["op02_shadow_contract"],"grammar-wip-open@1")
        self.assertEqual(len(row["registered_sources"]),2)
        self.assertFalse(row["shadow_is_active_producer"])
        self.assertFalse(row["source_stage5_7_or_final_acceptance"])

    def test_schreiben_and_visual_have_no_invented_native_sources(self):
        for family in ("family:schreiben","family:bildkarten-piloten"):
            row=next(x for x in self.actual["source_families"]
                     if x["family_id"]==family)
            self.assertEqual(row["registered_sources"],[])
            self.assertIsNone(row["native_workstream"])
            self.assertEqual(row["status"],"BLOCKED_UNREGISTERED_SOURCE_AND_NATIVE_CONTRACT")

    def test_menschen_portfolio_not_equivalent_to_b1_audio_shadow(self):
        row=next(x for x in self.actual["source_families"]
                 if x["family_id"]=="family:menschen-portfolio")
        self.assertIsNone(row["op02_shadow_contract"])
        self.assertEqual(len(row["registered_sources"]),1)
        self.assertFalse(row["real_native_adapter_adopted"])

    def test_zero_domain_adapter_or_stage_pass(self):
        self.assertEqual(self.actual["counts"]["actual_domain_adapters_adopted"],0)
        self.assertEqual(self.actual["counts"]["source_stage_passes_certified_by_preflight"],0)
        self.assertTrue(all(not x["real_native_adapter_adopted"]
                            and not x["semantic_stage4_acceptance"]
                            and not x["source_stage5_7_or_final_acceptance"]
                            for x in self.actual["source_families"]))
        self.assertFalse(self.actual["policy_conformance_adopted"])

    def test_scope_precedence_no_locked_changes(self):
        self.assertFalse(self.actual["source_original_locked_cards_or_runtime_edited"])
        self.assertFalse(self.actual["source_currentness_verified"])
        self.assertTrue(self.actual["github_pointer_hints_not_source_pass"])

    def test_unknown_nonlexical_family_halts(self):
        changed=copy.deepcopy(self.cfg)
        changed["profiles"].pop()
        with self.assertRaisesRegex(ValueError,"MISSING_OR_DUPLICATED_NONLEXICAL_FAMILY"):
            self.rerun(profile=changed)

    def test_duplicate_source_registry_id_halts(self):
        changed=copy.deepcopy(self.sources)
        changed["sources"].append(copy.deepcopy(changed["sources"][0]))
        with self.assertRaisesRegex(ValueError,"SOURCE_REGISTRY_DUPLICATE_ID"):
            self.rerun(sources=changed)

    def test_forged_source_registry_sha_halts_op02_exact_binding(self):
        changed=copy.deepcopy(self.sources)
        target=next(x for x in changed["sources"]
                    if x["source_id"]=="presentation-topics-b2-c1")
        target["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"OP02_SHADOW_NOT_EXACT_SOURCE_BINDING"):
            self.rerun(sources=changed)

    def test_shadow_contract_name_change_never_silent(self):
        changed=copy.deepcopy(self.shadow)
        changed["workstreams"]["lesen-praesentation"]["domain"]="writing"
        with self.assertRaisesRegex(ValueError,"OP02_SHADOW_NOT_EXACT_SOURCE_BINDING"):
            self.rerun(op02=changed)

    def test_source_owner_mismatch_fails_closed(self):
        changed=copy.deepcopy(self.sources)
        target=next(x for x in changed["sources"]
                    if x["source_id"]=="grammatik-aktiv-a1-b1")
        target["workstream"]="other-workstream"
        with self.assertRaisesRegex(ValueError,"SOURCE_OWNER_MISMATCH"):
            self.rerun(sources=changed)

    def test_profile_disabled_guard_rejected(self):
        changed=copy.deepcopy(self.cfg)
        changed["anti_promotion"]["no_migration_from_shadow_op02"]=False
        with self.assertRaisesRegex(ValueError,"PREFLIGHT_ANTI_PROMOTION_DISABLED"):
            self.rerun(profile=changed)

    def test_moved_root_checkpoint_is_not_fixed_by_invented_source(self):
        changed=copy.deepcopy(self.idx)
        changed["Workspaces/grammatik-aktiv-a1-c1/CHECKPOINT.json"]="a"*40
        with self.assertRaisesRegex(ValueError,"ROOT_POINTER_TRIAGE_CONTRADICTS_GIT_INDEX"):
            self.rerun(index=changed)

    def test_new_other_issue_is_not_misdiagnosed_as_checkpoint_failure(self):
        new=copy.deepcopy(self.issues)
        new.append({"type":"SOME_NEW_WARNING","path":"Workspaces/example"})
        r=self.rerun(issues=new)
        self.assertEqual(r["root_checkpoint_issue_triage"][-1]["status"],
                         "OTHER_NAVIGATION_ISSUE_REVIEW_SEPARATELY")
        self.assertEqual(r["counts"]["untracked_root_checkpoints"],5)

    def test_profile_registry_pins_are_exact_git_index(self):
        for key,x in self.cfg["input_pins"].items():
            self.assertEqual(x["git_blob"],self.idx.get(x["path"]),key)

    def test_executed_op02_shadow_matches_pinned_git_blob_only(self):
        item=self.cfg["input_pins"]["op02_shadow"]
        data=(ROOT/item["path"]).read_bytes()
        self.assertTrue(p.matches_exact_git_text(data,item["git_blob"]))
        self.assertFalse(p.matches_exact_git_text(data+b"# shadow tamper",item["git_blob"]))
        self.assertTrue(p.matches_exact_git_text(
            data.replace(b"\r\n",b"\n").replace(b"\n",b"\r\n"),
            item["git_blob"]))

    def test_cli_writes_report_only_to_new_external_path(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"preflight.json"
            command=[sys.executable,"-B",str(SCRIPT),
                     "--summary","--output",str(target)]
            x=subprocess.run(command,cwd=ROOT,text=True,
                             capture_output=True,timeout=60)
            self.assertEqual(x.returncode,0,x.stderr)
            a=json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(a["counts"]["classified_existing_root_checkpoint_issues"],5)
            before=target.read_bytes()
            y=subprocess.run(command,cwd=ROOT,text=True,
                             capture_output=True,timeout=60)
            self.assertEqual(y.returncode,2)
            self.assertEqual(target.read_bytes(),before)

if __name__=="__main__":
    unittest.main()
