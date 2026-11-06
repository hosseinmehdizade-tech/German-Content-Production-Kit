"""GFP-OPT P1: real official builder invoked by one centrally pinned format rule.

These tests use SYNTHETIC four-role Stage5 source fixtures, not private content.
They run the REAL production builder and examine the real generated ZIP/receipt.
"""
from __future__ import annotations
import copy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/"Tools/build_governed_clean_delivery_v1.py"
spec=importlib.util.spec_from_file_location("gfp_opt_stage5_launcher",FILE)
build=importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
gate=__import__("check_active_stage5_policy_v1")

HEAD=("id","front","back","card_type","category","details","custom_fields","source")
def tsv_bytes(details=None, duplicate=False, invalid_selector=False,
              drop_category=False):
    if details is None: details=[{"title":"Bedeutung","items":["gehen"]}]
    out=io.StringIO(newline="")
    fields=[x for x in HEAD if not (drop_category and x=="category")]
    writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n")
    writer.writeheader()
    for i in range(2):
        item={"id":"c-001" if duplicate or i==0 else "c-002",
              "front":"gehen","back":"رفتن","card_type":"de-vocabulary",
              "category":"Verb",
              "details":json.dumps(details,ensure_ascii=False),
              "custom_fields":json.dumps({"presentation_contract":"gfp-vocabulary-neutral@1",
                  **({"layout_template":"another UI"} if invalid_selector else {})}),
              "source":"Synthetic Producer"}
        writer.writerow({k:item[k] for k in fields})
    return out.getvalue().encode("utf-8")

def fixture(path:Path,**kwargs):
    path.mkdir()
    files={
      "TEST-IMPORT.tsv":tsv_bytes(**kwargs),
      "TEST-CANONICAL.json":b'{"cards":[]}\n',
      "TEST-SOURCE-OUTPUT-MAP.tsv":b"id\tsource\n",
      "TEST-VERIFICATION.json":b'{"status":"synthetic-not-stage4"}\n'
    }
    for name,content in files.items(): (path/name).write_bytes(content)
    return files

class PolicyInputTests(unittest.TestCase):
    def test_active_exact_git_registry_policy_can_load(self):
        module,binding=gate.load_authority()
        self.assertTrue(callable(module.validate))
        self.assertEqual(binding["scope"],"NEUTRAL_VOCABULARY_PROJECTION")

    def test_registry_authority_comes_from_live_checkout_not_20261105_pin(self):
        import subprocess
        resolved = subprocess.check_output(
            ["git", "rev-parse", "--verify", "HEAD:" + gate.REGISTRY],
            cwd=ROOT, text=True).strip()
        self.assertEqual(gate.active_registry_blob_from_checkout(), resolved)
        self.assertEqual(gate.check_bytes(tsv_bytes())["registry_git_blob"], resolved)

    def test_valid_source_projects_with_canonical_same_rule(self):
        result=gate.check_bytes(tsv_bytes())
        self.assertEqual(result["status"],"PASS_EXACT_ACTIVE_STAGE5_NEUTRAL_FORMAT_ONLY")
        self.assertEqual(result["cards_validated"],2)
        self.assertFalse(result["all_producers_adopted"])

    def test_invalid_details_fails(self):
        with self.assertRaisesRegex(ValueError,"ACTIVE_NEUTRAL_STAGE5_POLICY_FAILED"):
            gate.check_bytes(tsv_bytes(details="unstructured prose"))

    def test_invalid_presentation_override_fails(self):
        with self.assertRaisesRegex(ValueError,"ACTIVE_NEUTRAL_STAGE5_POLICY_FAILED"):
            gate.check_bytes(tsv_bytes(invalid_selector=True))

    def test_duplicate_id_fails(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_CARD_ID"):
            gate.check_bytes(tsv_bytes(duplicate=True))

    def test_missing_category_column_fails(self):
        with self.assertRaisesRegex(ValueError,"INVALID_TSV_COLUMNS"):
            gate.check_bytes(tsv_bytes(drop_category=True))

    def test_invalid_utf8_fails(self):
        with self.assertRaisesRegex(gate.Stage5PolicyFailure, "TSV_DECODE_OR_STRUCTURE_FAIL"):
            gate.check_bytes(b"\xff\xff")

    def test_empty_tsv_fails(self):
        with self.assertRaisesRegex(ValueError,"EMPTY_OR_OVERSIZE_TSV"):
            gate.check_bytes(b"")

    def test_registry_modified_versus_git_blob_fails(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); (base/"Prompt").mkdir();(base/"Verification").mkdir()
            (base/gate.REGISTRY).write_bytes((ROOT/gate.REGISTRY).read_bytes()+b"\n")
            (base/gate.VALIDATOR).write_bytes((ROOT/gate.VALIDATOR).read_bytes())
            with self.assertRaisesRegex(ValueError,"REGISTRY_GIT_BLOB_MISMATCH"):
                gate.check_bytes(tsv_bytes(),root=base)

    def test_validator_modified_versus_git_blob_fails(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);(base/"Prompt").mkdir();(base/"Verification").mkdir()
            (base/gate.REGISTRY).write_bytes((ROOT/gate.REGISTRY).read_bytes())
            (base/gate.VALIDATOR).write_bytes((ROOT/gate.VALIDATOR).read_bytes()+b"#tampered\n")
            with self.assertRaisesRegex(ValueError,"VALIDATOR_GIT_BLOB_MISMATCH"):
                gate.check_bytes(tsv_bytes(),root=base)

    def test_only_crlf_checkout_normalization_allowed(self):
        original=(ROOT/gate.VALIDATOR).read_bytes().replace(b"\r\n",b"\n")
        windows=original.replace(b"\n",b"\r\n")
        self.assertTrue(gate.matches_git_text(windows,gate.git_blob(original)))
        self.assertFalse(gate.matches_git_text(windows+b"evil",gate.git_blob(original)))

    def test_read_only_source_no_change(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"producer.tsv";p.write_bytes(tsv_bytes())
            old=p.read_bytes()
            self.assertEqual(gate.check_path(p)["cards_validated"],2)
            self.assertEqual(p.read_bytes(),old)

class GovernedIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)
        self.src=self.path/"source"
        self.files=fixture(self.src)
        self.out=self.path/"ACCEPTED-STAGE5-DELIVERY.zip"
        self.receipt=self.path/"GOVERNED-RECEIPT.json"

    def run_governed(self):
        return build.run(self.src,self.out,self.receipt)

    def test_official_builder_end_to_end_and_receipt(self):
        before={p.name:p.read_bytes() for p in self.src.iterdir()}
        result=self.run_governed()
        self.assertEqual(result["status"],"PASS_GOVERNED_STAGE5_FORMAT_AND_BYTE_PARITY_ONLY")
        self.assertEqual(result["active_policy"]["cards_validated"],2)
        self.assertEqual(result["staged_policy"]["cards_validated"],2)
        self.assertEqual(result["linguistic_stage4"],"NOT_CERTIFIED")
        self.assertEqual(result["stage5_content_acceptance"],"NOT_CERTIFIED")
        self.assertEqual(result["stage6_browser"],"NOT_RUN")
        self.assertEqual(result["global_adoption"],"NOT_PROVEN")
        self.assertEqual(result["source_role_sha256"]["direct-import-tsv"],
                         result["active_policy"]["input_tsv_sha256"])
        self.assertEqual(json.loads(self.receipt.read_text(encoding="utf-8")),
                         result)
        self.assertEqual(result["output_zip_sha256"],
                         hashlib.sha256(self.out.read_bytes()).hexdigest())
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.src.iterdir()})
        with zipfile.ZipFile(self.out) as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(z.read("CONTENT-DELIVERY/TEST-IMPORT.tsv"),
                             self.files["TEST-IMPORT.tsv"])

    def test_existing_output_refused_pre_build(self):
        self.out.write_bytes(b"historic")
        with self.assertRaisesRegex(ValueError,"OUTPUT_ALREADY_EXISTS"):
            self.run_governed()
        self.assertEqual(self.out.read_bytes(),b"historic")
        self.assertFalse(self.receipt.exists())

    def test_existing_receipt_refused_pre_build(self):
        self.receipt.write_text('{"status":"already"}',encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"RECEIPT_ALREADY_EXISTS"):
            self.run_governed()
        self.assertFalse(self.out.exists())

    def test_invalid_policy_cannot_build(self):
        (self.src/"TEST-IMPORT.tsv").write_bytes(
            tsv_bytes(details="German prose not sections"))
        with self.assertRaisesRegex(ValueError,"ACTIVE_NEUTRAL_STAGE5_POLICY_FAILED"):
            self.run_governed()
        self.assertFalse(self.out.exists())
        self.assertFalse(self.receipt.exists())

    def test_two_possible_import_roles_rejected(self):
        (self.src/"EXTRA-CARDS.tsv").write_bytes(tsv_bytes())
        with self.assertRaisesRegex(ValueError,"STAGE5_MISSING_OR_AMBIGUOUS_ROLE"):
            self.run_governed()
        self.assertFalse(self.out.exists())

    def test_archive_cannot_be_placed_inside_sources(self):
        with self.assertRaisesRegex(ValueError,"RECEIPT_OR_OUTPUT_INSIDE_SOURCE_DIR"):
            build.run(self.src,self.src/"NEW-DELIVERY.zip",self.receipt)

    def test_receipt_cannot_be_in_source_dir(self):
        with self.assertRaisesRegex(ValueError,"RECEIPT_OR_OUTPUT_INSIDE_SOURCE_DIR"):
            build.run(self.src,self.out,self.src/"NEW-RECEIPT.json")

    def test_builder_version_modified_fails_before_build(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"Tools").mkdir();(root/"Prompt").mkdir()
            (root/build.REGISTRY).write_bytes((ROOT/build.REGISTRY).read_bytes())
            (root/build.BUILDER).write_bytes(
                (ROOT/build.BUILDER).read_bytes()+b"#malicious mismatch\n")
            with self.assertRaisesRegex(ValueError,"GOVERNED_BUILDER_GIT_BLOB_DRIFT"):
                build.pinned_builder(root)

    def test_checkpoint_purpose_cannot_be_issued_by_stage5_gate(self):
        with self.assertRaisesRegex(ValueError,"INVALID_PURPOSE"):
            build.run(self.src,self.out,self.receipt,purpose="explicit_user_checkpoint")
        self.assertFalse(self.out.exists())
        self.assertFalse(self.receipt.exists())

    def test_final_delivery_cannot_be_issued_by_stage5_gate(self):
        with self.assertRaisesRegex(ValueError,"INVALID_PURPOSE"):
            build.run(self.src,self.out,self.receipt,purpose="final_delivery")
        self.assertFalse(self.out.exists())
        self.assertFalse(self.receipt.exists())

    def test_duplicate_publication_cannot_silently_replace(self):
        self.run_governed()
        with self.assertRaisesRegex(ValueError,"OUTPUT_ALREADY_EXISTS"):
            self.run_governed()

    def test_pinned_builder_production_path(self):
        path,git_sha=build.pinned_builder()
        self.assertEqual(path,ROOT/build.BUILDER)
        self.assertEqual(git_sha,"e12d2224c3321564e279bb5892298c35036bf7e9")

if __name__=="__main__":
    unittest.main()
