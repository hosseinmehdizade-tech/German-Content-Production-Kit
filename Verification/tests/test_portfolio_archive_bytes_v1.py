#!/usr/bin/env python3
"""Tests for source-pinned exact ZIP byte verification and dated evidence proof."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

FILE=Path(__file__).resolve().parents[2]/"Tools"/"verify_portfolio_archive_bytes_v1.py"
spec=importlib.util.spec_from_file_location("exact_zip_portfolio",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ExactZipTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.zip=self.root/"fixture.zip"
        with zipfile.ZipFile(self.zip,"w",compression=zipfile.ZIP_STORED) as z:
            z.writestr("sample.tsv","a\tb\n1\t2\n")
        self.sha=hashlib.sha256(self.zip.read_bytes()).hexdigest()
        self.size=self.zip.stat().st_size

    def test_valid_file_passes_real_zip_crc_and_sha(self):
        r=m.verify_file(self.zip,self.sha,self.size)
        self.assertEqual(r["status"],"PASS_EXACT_SHA256_AND_ZIP_CRC")
        self.assertEqual(r["zip_entries"],1)
        self.assertTrue(r["zip_crc_pass"])

    def test_wrong_sha_fails(self):
        r=m.verify_file(self.zip,"a"*64,self.size)
        self.assertEqual(r["status"],"FAIL_BYTES_OR_ZIP_CRC")

    def test_wrong_size_fails(self):
        r=m.verify_file(self.zip,self.sha,self.size+1)
        self.assertEqual(r["status"],"FAIL_BYTES_OR_ZIP_CRC")

    def test_corrupted_crc_fails_even_with_matching_measured_sha(self):
        data=bytearray(self.zip.read_bytes())
        with zipfile.ZipFile(self.zip) as z:
            info=z.getinfo("sample.tsv")
            start=info.header_offset+30+len(info.filename.encode("utf-8"))+len(info.extra)
        data[start]^=0x01
        self.zip.write_bytes(data)
        h=hashlib.sha256(data).hexdigest()
        r=m.verify_file(self.zip,h,len(data))
        self.assertEqual(r["status"],"FAIL_BYTES_OR_ZIP_CRC")
        self.assertFalse(r["zip_crc_pass"])

    def test_plain_text_named_zip_is_not_zip(self):
        self.zip.write_bytes(b"not-zip")
        self.assertEqual(m.verify_file(self.zip,hashlib.sha256(b"not-zip").hexdigest(),7)["status"],"FAIL_INVALID_ZIP")

    def test_missing_file_rejected(self):
        with self.assertRaises(FileNotFoundError):
            m.verify_file(self.root/"absent.zip",self.sha,self.size)

    def fixture_report(self):
        ids=["family:menschen-a1-verben"]+[f"family:test-{i}" for i in range(9)]
        reg={"items":[]}
        items=[]
        for fid in ids:
            reg["items"].append({"id":fid,"active_baseline":{"artifact_name":"fixture.zip",
                                     "artifact_sha256":self.sha,
                                     "artifact_size_bytes":self.size}})
            if fid=="family:menschen-a1-verben":
                continue
            providers=["google_drive","library"] if fid in ("family:test-1","family:test-4") else ["google_drive"]
            for prov in providers:
                items.append({"family_id":fid,"provider":prov,"artifact_name":"fixture.zip",
                  "expected_sha256":self.sha,"measured_sha256":self.sha,
                  "measured_size_bytes":self.size,"comparison":"PASS_EXACT_SOURCE_ACCEPTED_SHA256",
                  "zip_entries":1,"zip_crc_test":"PASS_ALL_MEMBERS"})
        # Need exact provider cross-family accounting expected by the production receipt.
        # Rebuild with the real ten IDs to test the static historical contract.
        ids=["family:menschen-a1","family:menschen-a1-verben","family:menschen-a2",
             "family:menschen-a2-verben","family:menschen-b1","family:menschen-b1-verben",
             "family:aber-hallo-listen-tabellen","family:nomen-verb-verbindungen",
             "family:250-verben-mit-praepositionen","family:unregelmaessige-verben"]
        library={"family:menschen-a2","family:menschen-a2-verben",
                 "family:nomen-verb-verbindungen","family:unregelmaessige-verben"}
        drive={"family:menschen-a1","family:menschen-a2-verben","family:menschen-b1",
               "family:menschen-b1-verben","family:aber-hallo-listen-tabellen",
               "family:nomen-verb-verbindungen","family:250-verben-mit-praepositionen"}
        reg={"items":[{"id":fid,"active_baseline":{"artifact_name":"fixture.zip",
                "artifact_sha256":self.sha,"artifact_size_bytes":self.size}} for fid in ids]}
        entries=[{"family_id":fid,"provider":prov,"artifact_name":"fixture.zip",
                  "expected_sha256":self.sha,"measured_sha256":self.sha,
                  "measured_size_bytes":self.size,"comparison":"PASS_EXACT_SOURCE_ACCEPTED_SHA256",
                  "zip_entries":1,"zip_crc_test":"PASS_ALL_MEMBERS"}
                 for fid in ids for prov,allowed in (("google_drive",drive),("library",library)) if fid in allowed]
        evidence={"schema":"gfp-opt-curated-portfolio-exact-byte-evidence@1.0.0",
                  "distinct_families_reverified":9,
                  "all_measured_sha256_and_zip_crc_pass":True,
                  "unresolved_families":[{"family_id":"family:menschen-a1-verben"}],
                  "evidence":entries}
        return reg,evidence

    def save_report(self,reg,report):
        for name,obj in ((m.REGISTRY,reg),(m.EVIDENCE,report)):
            f=self.root/name
            f.parent.mkdir(parents=True,exist_ok=True)
            f.write_text(json.dumps(obj),encoding="utf8")

    def test_as_of_receipt_checks_without_claiming_current_binary_rehash(self):
        r,j=self.fixture_report()
        self.save_report(r,j)
        x=m.verify_recorded_as_of(self.root)
        self.assertIn("NO_LIVE_BINARY_REHASH",x["status"])
        self.assertFalse(x["current_source_bytes_rehashed_now"])

    def test_modified_recorded_hash_rejected(self):
        r,j=self.fixture_report()
        j["evidence"][0]["measured_sha256"]="b"*64
        self.save_report(r,j)
        with self.assertRaises(ValueError):
            m.verify_recorded_as_of(self.root)

    def test_cross_provider_repeat_missing_rejected(self):
        r,j=self.fixture_report()
        j["evidence"]=[x for x in j["evidence"] if not
                       (x["family_id"]=="family:nomen-verb-verbindungen" and x["provider"]=="library")]
        self.save_report(r,j)
        with self.assertRaises(ValueError):
            m.verify_recorded_as_of(self.root)

    def test_duplicate_family_rejected(self):
        r,j=self.fixture_report()
        r["items"][1]["id"]=r["items"][0]["id"]
        self.save_report(r,j)
        with self.assertRaises(ValueError):
            m.verify_recorded_as_of(self.root)

    def test_cli_exact_file_pass_and_tamper_fails(self):
        r,j=self.fixture_report()
        self.save_report(r,j)
        with contextlib.redirect_stdout(io.StringIO()):
            ok=m.main(["--repo-root",str(self.root),"--family","family:menschen-a1","--file",str(self.zip)])
        self.assertEqual(ok,0)
        self.zip.write_bytes(b"broken")
        with contextlib.redirect_stdout(io.StringIO()):
            fail=m.main(["--repo-root",str(self.root),"--family","family:menschen-a1","--file",str(self.zip)])
        self.assertEqual(fail,2)

if __name__=="__main__":
    unittest.main()
