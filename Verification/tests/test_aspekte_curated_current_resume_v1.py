"""Regression: real current Aspekte owner pointers outrank historical raw source and stale summaries.

This is a read-only checkpoint/metadata contract. It is NOT private Library
byte re-download, German/Persian semantic approval, Stage5 acceptance or Stage6.
The real Library byte checks are recorded in B2 R43's scoped evidence receipt.
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
    check("Stage 4" in b1_readme and "raw source" in b1_readme,
          "B1+_BOUNDED_PROVENANCE_NOT_EXPLAINED")

    scope=b2.get("latest_scoped_audit",{})
    check(str(scope.get("label","")).startswith("L01_R43_"),
          "B2_L01_R43_SCOPE_MISSING")
    check(scope.get("source_rows")==160 and
          scope.get("provisional_new_bilingual_card_units")==158 and
          scope.get("noncard_full_content_objects")==2,
          "B2_R43_COVERAGE_OR_PREVIEW_COUNT")
    check(scope.get("importable") is False and scope.get("final_cards_created")==0
          and scope.get("stage2_approved") is False,
          "B2_R43_FALSE_RELEASE")
    check(str(scope.get("library_preview_sha256","")) in b2_readme and
          str(scope.get("parent_R42_canonical_sha256","")) in b2_readme,
          "B2_VERIFIED_CURATED_WORKING_NOT_IN_RESUME")
    check("R43" in b2_readme and "R25" in b2_readme and
          "LATEST.json.latest_scoped_audit" in b2_readme,
          "B2_SEPARATE_SCOPED_AND_GLOBAL_AUTHORITY_MISSING")
    check(receipt.get("status")==
          "PASS_READONLY_LIBRARY_BYTES_AND_SOURCE_TO_DRAFT_UNIT_COVERAGE__NOT_SEMANTIC_OR_RELEASE",
          "B2_READBACK_RECEIPT_SCOPE_CHANGED")
    ev=receipt.get("evidence_checks",{})
    check(ev.get("distinct_immutable_source_ordinals")==160
          and ev.get("distinct_preview_unit_ids")==158
          and ev.get("noncard_supplementary_objects_preserved")==2,
          "B2_READBACK_RECEIPT_COUNTS_CHANGED")
    for flag in ("every_coverage_source_changed_false",
                 "every_coverage_imported_false",
                 "every_preview_export_importable_false",
                 "every_preview_linguistic_release_approved_false"):
        check(ev.get(flag) is True, "B2_IMPORT_SAFETY_LOST:"+flag)
    checks={x.get("name"):x for x in receipt.get("verified_library_artifacts",[])}
    check(len(checks)==6 and
          checks.get("L01-158-UNIT-CARD-PREVIEW-NONIMPORT.csv",{}).get("sha256")==
          scope.get("library_preview_sha256") and
          checks.get("L01-CANONICAL-WORKING-NONIMPORT.csv",{}).get("sha256")==
          scope.get("parent_R42_canonical_sha256"),
          "B2_SOURCE_TO_CURATED_BYTE_PIN_MISMATCH")
    check(receipt.get("no_content_edits") is True and
          receipt.get("no_original_source_reimport") is True and
          receipt.get("no_app_or_srs_changes") is True,
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
          "original Menschen 9,109-row" not in c1_readme,
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
        self.assertIn("B2_R43_FALSE_RELEASE",self.inspect(b2=b2))

    def test_B2_missing_curated_byte_reference_detected(self):
        b2=copy.deepcopy(self.b2)
        b2["latest_scoped_audit"]["parent_R42_canonical_sha256"]="0"*64
        self.assertIn("B2_VERIFIED_CURATED_WORKING_NOT_IN_RESUME",self.inspect(b2=b2))

    def test_B2_source_mutation_or_import_flag_is_detected(self):
        r=copy.deepcopy(self.receipt)
        r["evidence_checks"]["every_coverage_source_changed_false"]=False
        self.assertIn("B2_IMPORT_SAFETY_LOST:every_coverage_source_changed_false",
                      self.inspect(receipt=r))

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
