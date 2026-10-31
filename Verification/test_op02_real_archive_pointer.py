"""OP-02 nonactive real-archive gate: synthetic ZIP regressions without source PDFs."""
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Verification"))
from audit_op02_real_archive_pointer import (
    audit, h, IMPORT, CANONICAL, POINTER, WORKING, MANIFEST, SOURCES, SUMS, LINES)

def body(n=67, pointer_n=None, pointer_hash=None, manifest_entry_drop=False,
         bad_member_sum=False, bad_pdf_hash=False, pointer_working_hash=None,
         working_status_n=None, working_main_hash=None, working_alias_hash=None):
    pdfs = [b"%PDF-1.4\nsynthetic a\n", b"%PDF-1.5\nsynthetic b\n"]
    paths = ["03-Source-Provenance/User-Supplied-Original-PDFs/A.pdf",
             "03-Source-Provenance/User-Supplied-Original-PDFs/B.pdf"]
    imp = b"id\tcard_type\ncard-1\tvocab\n"
    canonical = json.dumps({"learning_units":[{"id":"unit-1"},{"id":"unit-2"}]}).encode()
    pointer = {
        "workstream":"aber-hallo-listen-tabellen",
        "current":f"WIP{n if pointer_n is None else pointer_n}_SYNTHETIC",
        "canonical_sha256":pointer_hash or h(canonical),
        "import_sha256":h(imp),
        "working_canonical_sha256":pointer_working_hash or h(canonical),
        "working_import_sha256":h(imp),
    }
    working = {
        "status":f"WORKING_WIP{n if working_status_n is None else working_status_n}_SCOPED",
        "canonical_sha256":working_main_hash or h(canonical),
        "import_sha256":h(imp),
        "working_canonical_sha256":working_alias_hash or h(canonical),
        "working_import_sha256":h(imp),
    }
    src = {"sources":[{"archive_file":paths[i],
                       "sha256":h(pdfs[i]) if not bad_pdf_hash or i else "f"*64}
                      for i in range(2)]}
    files = {
        IMPORT:imp,CANONICAL:canonical,
        POINTER:json.dumps(pointer).encode(),
        WORKING:json.dumps(working).encode(),
        SOURCES:json.dumps(src).encode(),
        "01-Final-Import/IMPORT.WORKING.tsv.sha256":
            (h(imp)+"  IMPORT.WORKING.tsv\n").encode(),
        **dict(zip(paths,pdfs)),
        LINES["examples"]:b'{"a":1}\n',
        LINES["kombinationen"]:b'{"a":1}\n',
        LINES["relations"]:b'{"a":1}\n',
    }
    sumfiles = [{"path":p,"size_bytes":len(d),"sha256":h(d)}
                for p,d in files.items()]
    if manifest_entry_drop: sumfiles.pop()
    files[MANIFEST] = json.dumps({
        "summary":{"status":f"CURRENT_WIP{n}_SYNTHETIC",
                   "canonical_sha256":h(canonical),
                   "import_sha256":h(imp)},
        "file_count_excluding_manifest_and_checksums":len(files),
        "files":sumfiles,
    }).encode()
    checks = [(p,h(d)) for p,d in files.items()]
    if bad_member_sum: checks[0]=(checks[0][0],"f"*64)
    files[SUMS] = ("".join(f"{digest}  {p}\n" for p,digest in checks)).encode()
    by=io.BytesIO()
    with ZipFile(by,"w",compression=ZIP_DEFLATED) as z:
        for name,content in files.items():
            z.writestr(name,content)
    data=by.getvalue()
    expected={
        "workstream":"aber-hallo-listen-tabellen",
        "milestone":f"WIP{n}_SYNTHETIC",
        "zip_sha256":h(data),"zip_size_bytes":len(data),
        "member_count":len(files),"canonical_sha256":h(canonical),
        "import_sha256":h(imp),"source_sha256":list(map(h,pdfs)),
        "canonical_units":2,"import_cards":1,
        "examples":1,"kombinationen":1,"relations":1,
    }
    return data,expected

def run_test(**kwargs):
    data,expected=body(**kwargs)
    with tempfile.TemporaryDirectory() as root:
        p=Path(root)/"synthetic.zip"
        p.write_bytes(data)
        return audit(p, expected)

class RealArchiveBoundary(unittest.TestCase):
    def never_release(self,r):
        for f in ("issuer_authenticated","git_current_authorized",
                  "stage4_semantic_pass","stage5_7_pass",
                  "writer_granted","performed_writes"):
            self.assertIs(r[f],False,f)

    def test_synthetic_strict_complete_zip_accepts_only_scoped(self):
        r=run_test()
        self.assertEqual(r["binary_integrity"],"PASS",r)
        self.assertEqual(r["embedded_current_consistency"],"PASS",r)
        self.assertEqual(r["status"],"PASS_SCOPED_ARCHIVE_AND_POINTER_NOT_RELEASE",r)
        self.never_release(r)

    def test_future_wip_version_not_hardcoded(self):
        r=run_test(n=69)
        self.assertEqual(r["status"],"PASS_SCOPED_ARCHIVE_AND_POINTER_NOT_RELEASE",r)
        self.never_release(r)

    def test_stale_wip66_pointer_in_fully_rehashed_wip67_zip_blocks(self):
        r=run_test(n=67,pointer_n=66)
        self.assertEqual(r["binary_integrity"],"PASS",r)
        self.assertEqual(r["status"],"BLOCKED",r)
        self.assertIn("EMBEDDED_CURRENT_WIP_VERSION_STALE",r["pointer_errors"])
        self.never_release(r)

    def test_stale_canonical_pointer_in_fully_rehashed_zip_blocks(self):
        r=run_test(pointer_hash="e"*64)
        self.assertEqual(r["binary_integrity"],"PASS",r)
        self.assertIn("EMBEDDED_CURRENT_POINTER_HASH_STALE:canonical_sha256",r["pointer_errors"])
        self.never_release(r)

    def test_wip72_main_pointer_hashes_fresh_but_working_alias_stale(self):
        r=run_test(n=72,pointer_working_hash="f"*64)
        self.assertEqual(r["binary_integrity"],"PASS",r)
        self.assertEqual(r["status"],"BLOCKED",r)
        self.assertIn("EMBEDDED_CURRENT_POINTER_HASH_STALE:working_canonical_sha256",r["pointer_errors"])
        self.never_release(r)

    def test_wip72_working_state_status_stale_wip65(self):
        r=run_test(n=72,working_status_n=65)
        self.assertEqual(r["binary_integrity"],"PASS",r)
        self.assertIn("WORKING_STATE_ACTIVE_STATUS_STALE",r["pointer_errors"])
        self.never_release(r)

    def test_wip72_working_state_main_sha_stale(self):
        r=run_test(n=72,working_main_hash="f"*64)
        self.assertEqual(r["binary_integrity"],"PASS",r)
        self.assertIn("WORKING_STATE_ACTIVE_HASH_STALE:canonical_sha256",r["pointer_errors"])
        self.never_release(r)

    def test_wip72_working_state_alias_sha_stale(self):
        r=run_test(n=72,working_alias_hash="f"*64)
        self.assertEqual(r["binary_integrity"],"PASS",r)
        self.assertIn("WORKING_STATE_ACTIVE_HASH_STALE:working_canonical_sha256",r["pointer_errors"])
        self.never_release(r)

    def test_concurrent_old_aliases_and_old_status_are_not_hidden_by_integrity(self):
        r=run_test(n=72,pointer_working_hash="f"*64,
                   working_status_n=65,working_main_hash="f"*64)
        self.assertEqual(r["binary_integrity"],"PASS",r)
        self.assertEqual(r["status"],"BLOCKED",r)
        self.assertGreaterEqual(len(r["pointer_errors"]),3)
        self.never_release(r)

    def test_missing_manifest_member_blocks(self):
        r=run_test(manifest_entry_drop=True)
        self.assertIn("MANIFEST_MEMBER_COUNT_DRIFT",r["errors"])
        self.never_release(r)

    def test_checksum_spoof_blocks(self):
        r=run_test(bad_member_sum=True)
        self.assertIn("SHA256SUMS_MEMBER_BYTE_DRIFT",r["errors"])
        self.never_release(r)

    def test_source_pdf_sha_mismatch_blocks(self):
        r=run_test(bad_pdf_hash=True)
        self.assertIn("SOURCE_PDF_BYTE_MISMATCH",r["errors"])
        self.never_release(r)

    def test_wrong_external_source_pin_blocks(self):
        data,ex=body()
        ex["source_sha256"].reverse()
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"synthetic.zip";p.write_bytes(data)
            r=audit(p,ex)
        self.assertIn("ORIGINAL_PDF_SOURCE_ORDER_OR_HASH_DRIFT",r["errors"])
        self.never_release(r)

    def test_external_sha_mismatch_blocks_before_extracting(self):
        data,ex=body()
        ex["zip_sha256"]="f"*64
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"synthetic.zip";p.write_bytes(data)
            r=audit(p,ex)
        self.assertIn("EXTERNAL_ZIP_SHA_SIZE_DRIFT",r["errors"])
        self.never_release(r)

    def test_size_mismatch_blocks(self):
        data,ex=body()
        ex["zip_size_bytes"]+=1
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"synthetic.zip";p.write_bytes(data)
            r=audit(p,ex)
        self.assertIn("EXTERNAL_ZIP_SHA_SIZE_DRIFT",r["errors"])
        self.never_release(r)

    def test_bool_member_count_invalid(self):
        data,ex=body()
        ex["member_count"]=True
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"synthetic.zip";p.write_bytes(data)
            r=audit(p,ex)
        self.assertIn("EXPECTED_AUTHORITY_SHAPE_INVALID",r["errors"])
        self.never_release(r)

    def test_bad_zip_rejected(self):
        data,ex=body()
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"synthetic.zip";p.write_bytes(b"garbage")
            r=audit(p,ex)
        self.assertEqual(r["status"],"BLOCKED")
        self.never_release(r)

    def test_absent_zip_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            r=audit(Path(root)/"missing.zip",body()[1])
        self.assertEqual(r["status"],"BLOCKED")
        self.never_release(r)

    def test_untrusted_authority_extra_field_rejected(self):
        data,ex=body()
        ex["issuer_approved"]=True
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"synthetic.zip";p.write_bytes(data)
            r=audit(p,ex)
        self.assertIn("EXPECTED_AUTHORITY_SHAPE_INVALID",r["errors"])
        self.never_release(r)

    def test_wrong_workstream_rejected(self):
        data,ex=body()
        ex["workstream"]="menschen-b1"
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"synthetic.zip";p.write_bytes(data)
            r=audit(p,ex)
        self.assertIn("EXPECTED_AUTHORITY_SHAPE_INVALID",r["errors"])
        self.never_release(r)

if __name__ == "__main__":
    unittest.main()
