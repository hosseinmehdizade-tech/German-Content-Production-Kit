"""Fail-closed archive-to-governed-wrapper tests. Only synthetic CI fixtures."""
from __future__ import annotations
import csv,hashlib,importlib.util,io,json
from pathlib import Path
import tempfile,unittest,zipfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/"Tools/rehearse_existing_stage5_archive_v1.py"
spec=importlib.util.spec_from_file_location("gfp_p1_archive_rehearsal",FILE)
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

ROLES={"direct-import-tsv":"TEST-IMPORT.tsv",
       "canonical-json":"TEST-CANONICAL.json",
       "source-output-map-tsv":"TEST-SOURCE-OUTPUT-MAP.tsv",
       "qa-report":"TEST-VERIFICATION.json"}

def make_archive(path,*,tamper=False,duplicate=False,traversal=False):
    text=io.StringIO(newline="")
    columns=("id","front","back","card_type","category","details","custom_fields","source")
    writer=csv.DictWriter(text,fieldnames=columns,delimiter="\t",lineterminator="\n")
    writer.writeheader()
    for i in range(2):
        writer.writerow({"id":f"c-{i+1:03d}","front":"gehen","back":"رفتن",
            "card_type":"de-vocabulary","category":"Verb",
            "details":json.dumps([{"title":"Bedeutung","items":["gehen"]}]),
            "custom_fields":json.dumps({"presentation_contract":"gfp-vocabulary-neutral@1"}),
            "source":"Synthetic CI"})
    data={
      ROLES["direct-import-tsv"]:text.getvalue().encode(),
      ROLES["canonical-json"]:b'{"cards":[]}\n',
      ROLES["source-output-map-tsv"]:b"id\tsource\n",
      ROLES["qa-report"]:b'{"status":"synthetic-format-only"}\n'
    }
    prefix="CONTENT-DELIVERY/"
    sums="".join((("0"*64 if tamper and name.endswith(".tsv") else hashlib.sha256(raw).hexdigest())
                   + "  " + name + "\n") for name,raw in data.items())
    with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for name,raw in data.items(): z.writestr(prefix+name,raw)
        z.writestr(prefix+"DELIVERY-MANIFEST.json",json.dumps({"roles":ROLES}))
        z.writestr(prefix+"SHA256SUMS.txt",sums)
        if traversal: z.writestr("../escape.txt","evil")
        if duplicate: z.writestr(prefix+ROLES["qa-report"],data[ROLES["qa-report"]])
    return hashlib.sha256(path.read_bytes()).hexdigest(),prefix

class RealByteEnvelopeTests(unittest.TestCase):
    def fixture(self,**kw):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup)
        path=Path(td.name)/"source.zip";sha,prefix=make_archive(path,**kw)
        return path,sha,prefix
    def test_valid_archive_is_read_only_and_nonadopted(self):
        a,s,p=self.fixture(); result=runner.rehearse(a,s,p)
        self.assertEqual(result["real_input_rows"],2)
        self.assertEqual(len(result["roles_sha256"]),4)
        self.assertFalse(result["adopted"])
        self.assertFalse(result["release_published"])
        self.assertFalse(result["source_owner_new_stage5_authorized"])
    def test_pinned_sha_must_match_exact(self):
        a,s,p=self.fixture()
        with self.assertRaisesRegex(runner.RehearsalError,"ARCHIVE_SHA256_DRIFT"):
            runner.rehearse(a,"f"*64,p)
    def test_malformed_sha_denied(self):
        a,s,p=self.fixture()
        with self.assertRaisesRegex(runner.RehearsalError,"EXPECTED_SHA256_REQUIRED"):
            runner.rehearse(a,"not-sha",p)
    def test_unknown_prefix_denied(self):
        a,s,p=self.fixture()
        with self.assertRaisesRegex(runner.RehearsalError,"DELIVERY_PREFIX_NOT_ALLOWED"):
            runner.rehearse(a,s,"other/")
    def test_archive_internal_sha_mismatch_denied(self):
        a,s,p=self.fixture(tamper=True)
        with self.assertRaisesRegex(runner.RehearsalError,"ROLE_SHA256_MISMATCH"):
            runner.rehearse(a,s,p)
    def test_zip_traversal_denied(self):
        a,s,p=self.fixture(traversal=True)
        with self.assertRaisesRegex(runner.RehearsalError,"UNSAFE_ZIP_MEMBER"):
            runner.rehearse(a,s,p)
    def test_duplicate_member_denied(self):
        a,s,p=self.fixture(duplicate=True)
        with self.assertRaisesRegex(runner.RehearsalError,"ZIP_DUPLICATE_OR_EXCESSIVE_ENTRIES"):
            runner.rehearse(a,s,p)
    def test_exact_governed_wrapper_runs_and_two_mutations_fail_without_output(self):
        a,s,p=self.fixture()
        result=runner.rehearse(a,s,p,repo=ROOT,execute=True)
        self.assertEqual(result["status"],"PASS_DISPOSABLE_GOVERNED_WRAPPER_REHEARSAL__NOT_ADOPTED")
        self.assertTrue(result["wrapper_executed_on_existing_bytes"])
        self.assertEqual(set(result["negative_mutations_rejected_without_zip"]),
                         {"invalid-type","invalid-details"})
        self.assertTrue(result["all_generated_zips_and_receipts_removed"])
        self.assertFalse(result["adopted"])
        self.assertFalse(result["current_or_final_certified"])
    def test_missing_actual_repo_wrapper_denied_not_substituted(self):
        a,s,p=self.fixture()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(runner.RehearsalError,"ACTUAL_REPO_WRAPPER_REQUIRED"):
                runner.rehearse(a,s,p,repo=Path(td),execute=True)

if __name__=="__main__": unittest.main()
