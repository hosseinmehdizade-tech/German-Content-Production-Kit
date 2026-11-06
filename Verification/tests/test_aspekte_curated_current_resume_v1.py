"""Regression: real current Aspekte owner pointers outrank historical raw source and stale summaries.

This is a read-only checkpoint/metadata contract. It is NOT private Library
byte re-download, German/Persian semantic approval, Stage5 acceptance or Stage6.
The R43 receipt is historical and cannot be a live B2 L01 current-source pin.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
BASE="Workspaces/"
POLICY="Prompt/CURATED-CURRENT-AUTHORITY-AND-DELTA-QA-POLICY-v1.0.0.md"


def read_json(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))


def read_md(path):
    return (ROOT/path).read_text(encoding="utf-8")


def issues(b1, b1_readme, b2, b2_readme, c1, c1_readme, receipt):
    """Fail closed on curated resume regression or false FINAL/importable promotion."""
    errors=[]
    def check(ok, code):
        if not ok: errors.append(code)
    for name,doc in (("B1+",b1_readme),("B2",b2_readme),("C1",c1_readme)):
        check(POLICY in doc, name+"_MISSING_CURATED_CURRENT_ROUTE")
    base=b1.get("baseline") or b1.get("current_library_baseline") or {}
    check(bool(base.get("sha256")) and base["sha256"] in b1_readme,
          "B1+_VERIFIED_CURRENT_BASELINE_NOT_IN_RESUME")
    check("NONIMPORT" in str(base.get("name","")) and "340" in b1_readme,
          "B1+_NONIMPORT_OR_HOLDS_MISSING")
    check("Stage 4" in b1_readme and "bounded exact-attribution" in b1_readme,
          "B1+_BOUNDED_PROVENANCE_NOT_EXPLAINED")

    # Never freeze the active B2 lesson at R43. LATEST can advance to R48+;
    # old R43 evidence continues to attest R43 only, not currentness.
    import re
    scope=b2.get("latest_scoped_audit",{})
    match=re.match(r"^L01_R([1-9][0-9]*)_",str(scope.get("label","")))
    check(match is not None, "B2_L01_CURRENT_SCOPED_LABEL_INVALID")
    revision=int(match.group(1)) if match else None
    check(scope.get("source_rows_coverage")==160 and
          scope.get("draft_unique_ids")==158,
          "B2_L01_CURATED_SCOPE_COUNTS_INVALID")
    check(scope.get("importable") is False and
          scope.get("stage2_approved") is False and
          scope.get("imported_cards")==0 and
          scope.get("stage3_to_stage7")=="NOT_STARTED",
          "B2_CURRENT_FALSE_RELEASE")
    parents=[(int(m.group(1)),val) for key,val in scope.items()
             if (m:=re.fullmatch(r"parent_R([1-9][0-9]*)_158_current_sha256",key))]
    check(len(parents)==1 and revision is not None
          and parents[0][0]==revision-1
          and re.fullmatch(r"[0-9a-f]{64}",str(parents[0][1])) is not None
          and parents[0][1] != "0"*64,
          "B2_IMMEDIATE_CURATED_PARENT_INVALID")
    curr_sha=scope.get("current_158_draft_preview_sha256","")
    curr_path=scope.get("current_158_draft_preview_path","")
    check(re.fullmatch(r"[0-9a-f]{64}",str(curr_sha)) is not None
          and curr_sha != "0"*64
          and str(curr_path).endswith(f"-R{revision}-NONIMPORT.csv")
          and "/Aspekte-B2/Current/" in curr_path,
          "B2_CURRENT_BYTE_PIN_INVALID")
    check(re.fullmatch(r"[0-9a-f]{64}",
                       str(scope.get("noncard_2_current_sha256",""))) is not None
          and str(scope.get("noncard_2_current_path","")).endswith("-NONIMPORT.csv"),
          "B2_NONCARD_CURRENT_PIN_INVALID")
    check(scope.get("R44_legacy_HOLDs",0)>=17 and
          len(scope.get("identity_or_target_HOLDs",[]))>=4,
          "B2_RELEASE_HOLDS_NOT_CARRIED")
    check("LATEST.json#latest_scoped_audit" in b2_readme
          and "verification/verify_aspekte_b2_curated_unit_delta_v1.py" in b2_readme.lower()
          and "R25" in b2_readme
          and "do not pin lesson progress" in b2_readme.lower(),
          "B2_DYNAMIC_CURRENT_STARTUP_MISSING")
    check("is the **newer L01 R43 scoped work**" not in b2_readme,
          "B2_STALE_R43_AS_CURRENT_REINTRODUCED")

    # The 2026-11-06 R43 evidence receipt remains historically immutable.
    check(receipt.get("status")==
          "PASS_READONLY_LIBRARY_BYTES_AND_SOURCE_TO_DRAFT_UNIT_COVERAGE__NOT_SEMANTIC_OR_RELEASE",
          "B2_HISTORIC_R43_READBACK_RECEIPT_CHANGED")
    ev=receipt.get("evidence_checks",{})
    check(ev.get("distinct_immutable_source_ordinals")==160
          and ev.get("distinct_preview_unit_ids")==158
          and ev.get("noncard_supplementary_objects_preserved")==2,
          "B2_HISTORIC_R43_COUNTS_CHANGED")
    for flag in ("every_coverage_source_changed_false",
                 "every_coverage_imported_false",
                 "every_preview_export_importable_false",
                 "every_preview_linguistic_release_approved_false"):
        check(ev.get(flag) is True,"B2_HISTORIC_R43_IMPORT_SAFETY_LOST:"+flag)
    checks={x.get("name"):x for x in receipt.get("verified_library_artifacts",[])}
    check(len(checks)==6 and
          checks.get("L01-158-UNIT-CARD-PREVIEW-NONIMPORT.csv",{}).get("sha256")==
          "720154fe304c990aeec4dc7b69c70bc36fa22784f8e769d7f208d2724b0b50c3"
          and checks.get("L01-CANONICAL-WORKING-NONIMPORT.csv",{}).get("sha256")==
          "9da4568db9edc592429d35d2ddac4a91fb5369cfff1a5782ce1ce5ef74b88d0b",
          "B2_HISTORIC_R43_BLOB_PINS_CHANGED")
    check(receipt.get("no_content_edits") is True
          and receipt.get("no_original_source_reimport") is True
          and receipt.get("no_app_or_srs_changes") is True,
          "B2_NONDESTRUCTIVE_BOUNDARY_LOST")

    check(c1.get("stage1")=="IN_PROGRESS" and c1.get("approved_cards")==0,
          "C1_FALSE_STAGE_OR_APPROVAL")
    check(str(c1.get("portable_sha256","")) in c1_readme and
          str(c1.get("portable_file","")) in c1_readme,
          "C1_CURRENT_CURATED_COMPARATOR_NOT_IN_RESUME")
    check("Stage1 IN_PROGRESS" in c1_readme and
          "3,088" in c1_readme and "7,863" in c1_readme and
          "79" in c1_readme,
          "C1_CURATED_LOWER_BASELINE_OR_GATE_MISSING")
    check("NO PRODUCTION START" not in c1_readme and
          "**Read-only lower references:** Menschen original" not in c1_readme,
          "C1_STALE_RAW_SOURCE_AUTHORITY_REINTRODUCED")
    return errors


class AspekteCuratedResume(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b1=read_json(BASE+"aspekte-b1plus-v336/LATEST.json")
        cls.b2=read_json(BASE+"aspekte-b2-v336/LATEST.json")
        cls.c1=read_json(BASE+"aspekte-c1-v336/LATEST.json")
        cls.b1_md=read_md(BASE+"aspekte-b1plus-v336/README.md")
        cls.b2_md=read_md(BASE+"aspekte-b2-v336/README.md")
        cls.c1_md=read_md(BASE+"aspekte-c1-v336/README.md")
        cls.receipt=read_json(BASE+"aspekte-b2-v336/Reports/R43-CURATED-CURRENT-RESUME-READBACK-20261106.json")

    def inspect(self, b1=None, b1_md=None, b2=None, b2_md=None,
                c1=None, c1_md=None, receipt=None):
        return issues(
            self.b1 if b1 is None else b1,
            self.b1_md if b1_md is None else b1_md,
            self.b2 if b2 is None else b2,
            self.b2_md if b2_md is None else b2_md,
            self.c1 if c1 is None else c1,
            self.c1_md if c1_md is None else c1_md,
            self.receipt if receipt is None else receipt)

    def test_real_git_owner_current_pointers_and_readmes_are_consistent(self):
        self.assertEqual(self.inspect(), [])

    def test_B2_no_automatic_card_publication(self):
        b2=copy.deepcopy(self.b2)
        b2["latest_scoped_audit"]["importable"]=True
        self.assertIn("B2_CURRENT_FALSE_RELEASE",self.inspect(b2=b2))

    def test_B2_missing_curated_byte_reference_detected(self):
        b2=copy.deepcopy(self.b2)
        b2["latest_scoped_audit"]["current_158_draft_preview_sha256"]="0"*64
        self.assertIn("B2_CURRENT_BYTE_PIN_INVALID",self.inspect(b2=b2))

    def test_B2_source_mutation_or_import_flag_is_detected(self):
        r=copy.deepcopy(self.receipt)
        r["evidence_checks"]["every_coverage_source_changed_false"]=False
        self.assertIn("B2_HISTORIC_R43_IMPORT_SAFETY_LOST:every_coverage_source_changed_false",
                      self.inspect(receipt=r))

    def test_B2_immediate_parent_cannot_be_skipped(self):
        b2=copy.deepcopy(self.b2)
        orig=[k for k in b2["latest_scoped_audit"]
              if k.startswith("parent_R") and k.endswith("_158_current_sha256")]
        self.assertEqual(len(orig),1)
        b2["latest_scoped_audit"]["parent_R44_158_current_sha256"]=(
            b2["latest_scoped_audit"].pop(orig[0]))
        self.assertIn("B2_IMMEDIATE_CURATED_PARENT_INVALID",self.inspect(b2=b2))

    def test_B2_future_revision_must_not_be_blocked_by_R43_receipt(self):
        b2=copy.deepcopy(self.b2)
        scope=b2["latest_scoped_audit"]
        old_key=[k for k in scope if k.startswith("parent_R") and
                 k.endswith("_158_current_sha256")][0]
        old_rev=int(old_key.split("_")[1][1:])
        new_rev=old_rev+2
        scope[f"parent_R{old_rev+1}_158_current_sha256"]=scope.pop(old_key)
        scope["label"]=f"L01_R{new_rev}_SAFE_NEXT_SCOPED_DRAFT"
        scope["current_158_draft_preview_path"]=scope[
            "current_158_draft_preview_path"].replace(
            f"-R{old_rev+1}-NONIMPORT.csv",f"-R{new_rev}-NONIMPORT.csv")
        self.assertEqual(self.inspect(b2=b2),[])

    def test_C1_does_not_fall_back_to_raw_Menschen(self):
        c1_md=self.c1_md.replace("3,088","3,089").replace("Stage1 IN_PROGRESS","NO PRODUCTION START")
        res=self.inspect(c1_md=c1_md)
        self.assertIn("C1_CURATED_LOWER_BASELINE_OR_GATE_MISSING",res)
        self.assertIn("C1_STALE_RAW_SOURCE_AUTHORITY_REINTRODUCED",res)

    def test_B1_current_baseline_change_requires_readme_rebind(self):
        b1=copy.deepcopy(self.b1)
        b1["baseline"]["sha256"]="0"*64
        self.assertIn("B1+_VERIFIED_CURRENT_BASELINE_NOT_IN_RESUME",self.inspect(b1=b1))

    def test_read_only_no_source_rewriting(self):
        sample=(ROOT/(BASE+"aspekte-b2-v336/LATEST.json")).read_bytes()
        self.assertEqual(self.inspect(),[])
        self.assertEqual(sample,(ROOT/(BASE+"aspekte-b2-v336/LATEST.json")).read_bytes())


if __name__=="__main__":
    unittest.main()
