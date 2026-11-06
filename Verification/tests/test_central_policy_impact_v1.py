"""P1 central impact routing: no syntax-only global adoption, no fake stage PASS."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Tools/plan_central_policy_impact_v1.py"
spec = importlib.util.spec_from_file_location("gfp_opt_p1_impact", SCRIPT)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class CentralPolicyImpactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile,cls.catalog,cls.registry,cls.old,cls.pilot,cls.receipt = p.authority()

    def validate(self, profile=None, catalog=None, previous=None,
                 pilot=None, receipt=None):
        p.verify_catalog_and_profiles(
            copy.deepcopy(self.profile if profile is None else profile),
            copy.deepcopy(self.catalog if catalog is None else catalog),
            copy.deepcopy(self.old if previous is None else previous),
            copy.deepcopy(self.pilot if pilot is None else pilot),
            copy.deepcopy(self.receipt if receipt is None else receipt))

    def impact(self, binding=None):
        return p.build_impact(
            self.profile,self.catalog,self.registry,self.old,
            bindings=None if binding is None else {binding})

    def test_authoritative_all_pins_verified(self):
        self.validate()
        self.assertEqual(self.registry["schema"],"gcpk-global-policy-registry@1.0.0")

    def test_all_live_bindings_have_complete_21_35_17_coverage(self):
        out=self.impact()
        n=len(self.registry["policy_bindings"])
        self.assertGreaterEqual(n,22)
        self.assertEqual(len(out["selected_policy_bindings"]),n)
        self.assertEqual(len(out["family_impacts"]),21*n)
        self.assertEqual(len(out["workspace_impacts"]),35*n)
        self.assertEqual(len(out["root_workstream_impacts"]),17*n)
        self.assertEqual(out["catalog_baseline"]["qa_workspaces_not_direct_producers"],3)

    def test_no_undocumented_stage_or_adoption_pass_in_any_cell(self):
        out=self.impact()
        self.assertTrue(all(
            r["impact_status"] in p.ACCEPTED_STATES and
            r["stage4_semantic_certification"]=="NOT_CERTIFIED" and
            r["actual_currentness"]=="NOT_RESOLVED" and
            r["native_runtime_stage6"]=="NOT_RUN"
            for r in out["family_impacts"]))
        self.assertTrue(all(x["workspace_specific_execution_verified"] is False
                            and x["workspace_specific_real_output_verified"] is False
                            for x in out["workspace_impacts"]))
        self.assertTrue(all(x["root_stage_or_currentness_certified"] is False
                            for x in out["root_workstream_impacts"]))
        self.assertTrue(all(out["truth_boundary"].values()))

    def test_every_workspace_qa_scope_is_not_a_direct_producer(self):
        out=self.impact("stage5_neutral_validator")
        qa=[x for x in out["workspace_impacts"]
            if x["workspace_kind"]=="QA_ONLY_NOT_DIRECT_PRODUCER"]
        self.assertEqual(len(qa),3)
        self.assertTrue(all(x["impact_status"]=="QA_WORKSPACE_NOT_DIRECT_PRODUCER" for x in qa))
        self.assertEqual(len(out["workspace_impacts"]),35)

    def test_qa_workspace_has_resume_only_even_when_policy_is_global(self):
        out=self.impact("currentness")
        qa=[x for x in out["workspace_impacts"]
            if x["workspace_kind"]=="QA_ONLY_NOT_DIRECT_PRODUCER"]
        self.assertEqual(len(qa),3)
        self.assertTrue(all(x["impact_status"]==
                            "QA_WORKSPACE_ROUTED_AT_RESUME_NOT_DIRECT_PRODUCER" for x in qa))

    def test_historical_602_row_witnesses_have_no_global_adoption(self):
        out=self.impact("stage5_neutral_validator")
        witnesses=[r for r in out["family_impacts"]
                   if r["impact_status"]=="HISTORICAL_FORMAT_WITNESS_NOT_CURRENT_OR_ADOPTED"]
        self.assertEqual(
            {r["family_id"] for r in witnesses},
            {"family:250-verben-mit-praepositionen","family:menschen-a1-verben"})
        self.assertEqual(len(witnesses),2)
        self.assertFalse(out["per_policy"]["stage5_neutral_validator"]
                         ["policy_became_executable_in_every_producer"])

    def test_grammar_not_forced_through_lexical_stage5(self):
        out=self.impact("stage5_neutral_validator")
        grammar=[r for r in out["family_impacts"] if "grammatik-aktiv" in r["family_id"]]
        self.assertEqual(len(grammar),3)
        self.assertTrue(all(r["impact_status"]==
                            "DOMAIN_ADAPTER_REQUIRED_NO_FORCED_LEXICAL_SCHEMA" for r in grammar))

    def test_reading_and_writing_require_source_profile(self):
        out=self.impact("stage5_neutral_validator")
        targets=[r for r in out["family_impacts"] if r["family_id"] in
                 {"family:lesen","family:schreiben"}]
        self.assertEqual(len(targets),2)
        self.assertTrue(all(r["impact_status"]==
                            "DOMAIN_ADAPTER_REQUIRED_NO_FORCED_LEXICAL_SCHEMA" for r in targets))

    def test_mixed_source_refuses_automatic_neutral_conformance(self):
        out=self.impact("kombinationen_source_first")
        targets=[r for r in out["family_impacts"] if r["family_id"] in
                 {"family:aber-hallo-listen-tabellen","family:menschen-portfolio"}]
        self.assertEqual(len(targets),2)
        self.assertTrue(all(r["impact_status"]=="SPLIT_SOURCE_PROFILE_REQUIRED"
                            for r in targets))

    def test_generic_vocab_has_no_native_output_proof(self):
        out=self.impact("stage5_clean_builder")
        row=next(x for x in out["family_impacts"]
                 if x["family_id"]=="family:vocabulary-sonstige")
        self.assertEqual(row["impact_status"],"NATIVE_GENERIC_OUTPUT_MISSING")

    def test_all_root_workstreams_have_real_family_parent(self):
        out=self.impact("seven_stages")
        family_ids={x["id"] for x in self.catalog["families"]}
        self.assertTrue(all(x["parent_family_id"] in family_ids
                            and x["root_stage_or_currentness_certified"] is False
                            for x in out["root_workstream_impacts"]))

    def test_added_family_without_profile_fails_closed(self):
        bad=copy.deepcopy(self.catalog)
        bad["families"].append({"id":"family:phantom"})
        with self.assertRaisesRegex(ValueError,"CATALOG_COUNT_DRIFT_STOP_FOR_REVIEW"):
            self.validate(catalog=bad)

    def test_removed_family_profile_fails_closed(self):
        bad=copy.deepcopy(self.profile)
        bad["families"].pop()
        with self.assertRaisesRegex(ValueError,"FAMILY_PROFILE_COVERAGE_OR_DOMAIN_MISMATCH"):
            self.validate(profile=bad)

    def test_fake_real_producer_adoption_fails_closed(self):
        bad=copy.deepcopy(self.profile)
        bad["families"][0]["native_builder_status"]="FULLY_ADOPTED"
        with self.assertRaisesRegex(ValueError,"FORGED_SOURCE_ADOPTION_OR_RELEASE"):
            self.validate(profile=bad)

    def test_forged_stage6_claim_fails_closed(self):
        bad=copy.deepcopy(self.profile)
        bad["families"][0]["stage6_native_app"]="PASS"
        with self.assertRaisesRegex(ValueError,"FORGED_SOURCE_ADOPTION_OR_RELEASE"):
            self.validate(profile=bad)

    def test_unknown_family_domain_fails_closed(self):
        bad=copy.deepcopy(self.profile)
        bad["families"][0]["declared_domain"]="FAKE_EVERYTHING_APPLICABLE"
        with self.assertRaisesRegex(ValueError,"FAMILY_PROFILE_COVERAGE_OR_DOMAIN_MISMATCH"):
            self.validate(profile=bad)

    def test_fake_qa_owner_as_native_producer_fails_closed(self):
        bad=copy.deepcopy(self.profile)
        bad["qa_only_workspace_paths"]=[]
        with self.assertRaisesRegex(ValueError,"QA_ONLY_WORKSPACES_MISMATCH"):
            self.validate(profile=bad)

    def test_registry_new_scope_requires_explicit_engineering_review(self):
        bad=copy.deepcopy(self.registry)
        bad["policy_bindings"]["stage5_neutral_validator"]["scope"]="AUTO_DELETE_HISTORY"
        bad_profile=copy.deepcopy(self.profile)
        # Tampering the bytes of registry is caught before the scope is interpreted.
        with tempfile.TemporaryDirectory() as td:
            tmp=Path(td)
            for location in (p.PROFILE,p.CATALOG,p.REGISTRY,p.PREVIOUS,
                             p.PILOT_PROFILE,p.PILOT_RECEIPT):
                target=tmp/location
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/location,target)
            (tmp/p.REGISTRY).write_text(json.dumps(bad),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"LIVE_GIT_SNAPSHOT_UNAVAILABLE"):
                p.authority(tmp)
        self.assertEqual(bad_profile["program_id"],"GFP-OPT-2026")

    def test_curated_current_router_reaches_35_workspace_candidates_only(self):
        out=self.impact("curated_current_delta_qa")
        self.assertEqual(len(out["workspace_impacts"]),35)
        self.assertEqual(len(out["family_impacts"]),21)
        self.assertTrue(all(x["workspace_specific_execution_verified"] is False
                            and x["workspace_specific_real_output_verified"] is False
                            for x in out["workspace_impacts"]))
        self.assertTrue(all(x["actual_currentness"] == "NOT_RESOLVED"
                            for x in out["family_impacts"]))

    def test_unknown_binding_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_POLICY_BINDING"):
            self.impact("unknown-binding-that-does-not-exist")

    def test_deactivated_protection_flag_rejected(self):
        bad=copy.deepcopy(self.profile)
        bad["protected_boundaries"]["no_auto_migration_on_policy_change"]=False
        with self.assertRaisesRegex(ValueError,"PROTECTED_BOUNDARY_DISABLED"):
            self.validate(profile=bad)

    def test_faked_historical_witness_count_rejected(self):
        bad=copy.deepcopy(self.profile)
        bad["families"][0]["historical_neutral_format_witnesses"][0]["rows"]=9999
        with self.assertRaisesRegex(ValueError,"HISTORICAL_FORMAT_WITNESS_MISMATCH"):
            self.validate(profile=bad)

    def test_fake_historical_receipt_global_pass_rejected(self):
        bad=copy.deepcopy(self.receipt)
        bad["boundaries"]["complete_34_workspace_adoption"]="PASS"
        with self.assertRaisesRegex(ValueError,"REAL_OUTPUT_NOT_GLOBAL"):
            self.validate(receipt=bad)

    def test_profile_inputs_not_written_by_router(self):
        before={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest()
                for x in (p.PROFILE,p.CATALOG,p.REGISTRY,p.PREVIOUS,p.PILOT_PROFILE,p.PILOT_RECEIPT)}
        self.impact()
        after={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in before}
        self.assertEqual(before,after)

    def test_cli_summary_all_policy_bindings(self):
        result=subprocess.run([sys.executable,str(SCRIPT),"--summary"],
                              cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
        self.assertEqual(result.returncode,0,result.stderr)
        d=json.loads(result.stdout)
        self.assertEqual(len(d["per_policy"]),len(self.registry["policy_bindings"]))
        self.assertNotIn("workspace_impacts",d)
        self.assertEqual(d["selected_impact_rows"]["family"],21*len(self.registry["policy_bindings"]))
        self.assertEqual(d["selected_impact_rows"]["workspace"],35*len(self.registry["policy_bindings"]))

    def test_cli_select_policy_and_named_family(self):
        result=subprocess.run([
            sys.executable,str(SCRIPT),"--binding","stage5_neutral_validator",
            "--family","family:250-verben-mit-praepositionen"
        ],cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
        self.assertEqual(result.returncode,0,result.stderr)
        d=json.loads(result.stdout)
        self.assertEqual(len(d["family_impacts"]),1)
        self.assertEqual(d["family_impacts"][0]["impact_status"],
                         "HISTORICAL_FORMAT_WITNESS_NOT_CURRENT_OR_ADOPTED")
        self.assertTrue(d["filtered_view_only"])

    def test_cli_unknown_policy_fails(self):
        result=subprocess.run([sys.executable,str(SCRIPT),"--binding","bogus"],
                              cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
        self.assertEqual(result.returncode,2)
        self.assertIn("UNKNOWN_POLICY_BINDING",result.stderr)

    def test_cli_report_is_write_once(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"report.json"
            command=[sys.executable,str(SCRIPT),"--summary",
                     "--write-once-report",str(target)]
            a=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,
                             encoding="utf-8")
            self.assertEqual(a.returncode,0,a.stderr)
            first=target.read_bytes()
            b=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,
                             encoding="utf-8")
            self.assertEqual(b.returncode,2)
            self.assertEqual(first,target.read_bytes())


if __name__=="__main__":
    unittest.main()
