"""Adversarial byte-bound attestation fixture tests. Never mutate real source."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Tools/attest_source_package_bytes_v1.py"
spec = importlib.util.spec_from_file_location("package_attestation", SCRIPT)
att = importlib.util.module_from_spec(spec)
spec.loader.exec_module(att)


class TestRealSourcePackageByteContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="gcpk-byte-attest-test-")
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.source = root / "source.pdf"
        self.source.write_bytes(b"%PDF-1.4\nSYNTHETIC ORIGINAL FIXTURE\n")
        self.archive = root / "synthetic-r7.zip"
        self.profile = {
            "schema": att.PROFILE_SCHEMA,
            "workstream": "synthetic-fixture-never-release",
            "artifact_filename": self.archive.name,
            "artifact_sha256": "0" * 64,
            "artifact_size_bytes": 1,
            "original_source_sha256": att.sha256_file(self.source),
            "original_source_member": "03-Source/original.pdf",
            "content_member": "02-Content/cards.tsv",
            "content_sha256": att.sha256_bytes(b"id\tfront\n1\tgehen\n"),
        }
        self.members = {
            self.profile["original_source_member"]: self.source.read_bytes(),
            self.profile["content_member"]: b"id\tfront\n1\tgehen\n",
            "05-Reports/QA.json": b'{"status":"NOT_A_REAL_QA_RECEIPT"}\n',
        }
        self.repack()

    def repack(self, *, manifest=True, corrupt_manifest=False):
        manifest_records = {
            name: att.sha256_bytes(blob) for name, blob in self.members.items()
        }
        if corrupt_manifest:
            manifest_records[self.profile["content_member"]] = "0" * 64
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as z:
            for name, blob in self.members.items():
                z.writestr(name, blob)
            if manifest:
                m = "".join(f"{h}  {name}\n" for name, h in manifest_records.items())
                z.writestr("SHA256SUMS.txt", m)
        self.profile["artifact_sha256"] = att.sha256_file(self.archive)
        self.profile["artifact_size_bytes"] = self.archive.stat().st_size

    def attest(self):
        return att.attest(self.profile, self.archive, self.source)

    def test_nondefault_root_manifest_member_requires_explicit_profile(self):
        self.profile["manifest_member"] = "SHA256SUMS"
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as z:
            for n, data in self.members.items():
                z.writestr(n, data)
            text = "".join(f"{att.sha256_bytes(data)}  {name}\n"
                           for name, data in self.members.items())
            z.writestr("SHA256SUMS", text)
        self.profile["artifact_sha256"] = att.sha256_file(self.archive)
        self.profile["artifact_size_bytes"] = self.archive.stat().st_size
        result = self.attest()
        self.assertEqual(result["manifest_entries_verified"], len(self.members))
        self.profile.pop("manifest_member")
        with self.assertRaisesRegex(att.AttestationBlocked, "MISSING_SHA256_MANIFEST"):
            self.attest()

    def test_unsafe_manifest_member_selector_rejected(self):
        self.profile["manifest_member"] = "../SHA256SUMS"
        with self.assertRaisesRegex(att.AttestationBlocked, "UNSAFE_PROFILE_MANIFEST_MEMBER"):
            self.attest()

    def test_valid_synthetic_fixture_is_byte_sound_but_not_stage4(self):
        r = self.attest()
        self.assertEqual(r["status"], "PASS_EXACT_SOURCE_PACKAGE_BYTES_AND_MANIFEST__SCOPED_NOT_FINAL")
        self.assertTrue(r["embedded_source_identical_to_external"])
        self.assertEqual(r["manifest_entries_verified"], 3)
        self.assertEqual(r["stage4_gate"]["status"], "NOT_RERUN")
        self.assertEqual(r["stage6_real_browser"], "NOT_ATTESTED")

    def test_fixture_does_not_claim_linguistic_quality(self):
        self.assertEqual(self.attest()["stage7_release"], "NOT_ATTESTED")

    def test_wrong_archive_byte_detected_before_unpack(self):
        with self.archive.open("ab") as f:
            f.write(b"unapproved mutation")
        with self.assertRaisesRegex(att.AttestationBlocked, "ARTIFACT_SIZE_MISMATCH"):
            self.attest()

    def test_wrong_zip_expected_hash_fails(self):
        self.profile["artifact_sha256"] = "f" * 64
        with self.assertRaisesRegex(att.AttestationBlocked, "ARTIFACT_SHA256_MISMATCH"):
            self.attest()

    def test_wrong_source_pdf_hash_fails(self):
        self.source.write_bytes(b"%PDF-1.4\nCHANGED SOURCE\n")
        with self.assertRaisesRegex(att.AttestationBlocked, "ORIGINAL_SOURCE_SHA256_MISMATCH"):
            self.attest()

    def test_fake_profile_content_sha_fails(self):
        self.profile["content_sha256"] = "f" * 64
        with self.assertRaisesRegex(att.AttestationBlocked, "CONTENT_SHA256_MISMATCH"):
            self.attest()

    def test_valid_new_zip_with_manipulated_manifest_fails(self):
        self.repack(corrupt_manifest=True)
        with self.assertRaisesRegex(att.AttestationBlocked, "MEMBER_SHA256_MISMATCH"):
            self.attest()

    def test_manifest_missing_fails(self):
        self.repack(manifest=False)
        with self.assertRaisesRegex(att.AttestationBlocked, "MISSING_SHA256_MANIFEST"):
            self.attest()

    def test_manifest_missing_source_member_fails_exact_coverage(self):
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as z:
            for name, blob in self.members.items():
                z.writestr(name, blob)
            z.writestr("SHA256SUMS.txt", "0" * 64 + "  02-Content/cards.tsv\n")
        self.profile["artifact_sha256"] = att.sha256_file(self.archive)
        self.profile["artifact_size_bytes"] = self.archive.stat().st_size
        with self.assertRaisesRegex(att.AttestationBlocked, "MANIFEST_NOT_EXACT_COVERAGE"):
            self.attest()

    def test_traversal_path_refused_even_if_self_consistent(self):
        self.members["../evil.txt"] = b"evil"
        self.repack()
        with self.assertRaisesRegex(att.AttestationBlocked, "UNSAFE_ZIP_MEMBER_PATH"):
            self.attest()

    def test_windows_backslash_archive_member_rejected(self):
        self.members["..\\windows.txt"] = b"evil"
        self.repack()
        with self.assertRaisesRegex(att.AttestationBlocked, "UNSAFE_ZIP_MEMBER_PATH"):
            self.attest()

    def test_zip_symlink_refused(self):
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as z:
            for name, blob in self.members.items():
                if name == self.profile["content_member"]:
                    info = zipfile.ZipInfo(name)
                    info.create_system = 3
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                    z.writestr(info, blob)
                else:
                    z.writestr(name, blob)
            manifest = "".join(f"{att.sha256_bytes(b)}  {n}\n"
                               for n, b in self.members.items())
            z.writestr("SHA256SUMS.txt", manifest)
        self.profile["artifact_sha256"] = att.sha256_file(self.archive)
        self.profile["artifact_size_bytes"] = self.archive.stat().st_size
        with self.assertRaisesRegex(att.AttestationBlocked, "ZIP_SYMLINK_FORBIDDEN"):
            self.attest()

    def test_manifest_duplicate_entry_refused(self):
        text = "".join(f"{att.sha256_bytes(b)}  {n}\n"
                       for n, b in self.members.items())
        first = next(iter(self.members))
        text += f"{att.sha256_bytes(self.members[first])}  {first}\n"
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_DEFLATED) as z:
            for n, b in self.members.items():
                z.writestr(n, b)
            z.writestr("SHA256SUMS.txt", text)
        self.profile["artifact_sha256"] = att.sha256_file(self.archive)
        self.profile["artifact_size_bytes"] = self.archive.stat().st_size
        with self.assertRaisesRegex(att.AttestationBlocked, "MANIFEST_DUPLICATE_ENTRY"):
            self.attest()

    def test_stage4_unpinned_arbitrary_script_never_runs(self):
        self.profile["pinned_stage4_gate"] = {
            "script_member": "04-Tests/gate.py",
            "script_git_blob_sha": "0" * 40,
            "policy_member": "04-Tests/policy.json",
            "policy_git_blob_sha": "0" * 40,
            "risk_receipt_member": "05-Reports/receipt.json",
        }
        self.members.update({
            "04-Tests/gate.py": b"raise Exception('DO NOT RUN')\n",
            "04-Tests/policy.json": b"{}\n",
            "05-Reports/receipt.json": b"{}\n",
        })
        self.repack()
        with self.assertRaisesRegex(att.AttestationBlocked, "STAGE4_GATE_SCRIPT_PIN_MISMATCH"):
            self.attest()

    def test_invalid_policy_git_pin_refused(self):
        self.profile["pinned_stage4_gate"] = {
            "script_member": "04-Tests/gate.py", "script_git_blob_sha": "garbage",
            "policy_member": "04-Tests/policy.json", "policy_git_blob_sha": "0" * 40,
            "risk_receipt_member": "05-Reports/receipt.json",
        }
        with self.assertRaisesRegex(att.AttestationBlocked, "INVALID_STAGE4_GATE_GIT_PIN"):
            self.attest()

    def test_embedded_source_must_match_real_original_bytes(self):
        self.members[self.profile["original_source_member"]] = b"%PDF-1.4\nSOME OTHER PDF\n"
        self.repack()
        with self.assertRaisesRegex(att.AttestationBlocked, "EMBEDDED_SOURCE_SHA256_MISMATCH"):
            self.attest()

    def test_missing_original_member_fails(self):
        del self.members[self.profile["original_source_member"]]
        self.repack()
        with self.assertRaisesRegex(att.AttestationBlocked, "PACKAGE_ORIGINAL_SOURCE_MEMBER_MISSING"):
            self.attest()

    def test_source_and_zip_remain_unchanged_after_attestation(self):
        a, b = self.source.read_bytes(), self.archive.read_bytes()
        self.attest()
        self.assertEqual(self.source.read_bytes(), a)
        self.assertEqual(self.archive.read_bytes(), b)

    def test_cli_report_path_cannot_overwrite_original_pdf(self):
        profile_path = Path(self.tmp.name) / "profile.json"
        profile_path.write_text(json.dumps(self.profile), encoding="utf-8")
        before = self.source.read_bytes()
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "--profile", str(profile_path),
             "--archive", str(self.archive), "--original-source", str(self.source),
             "--output", str(self.source)], capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 2)
        self.assertIn("OUTPUT_ALIASES_INPUT_BYTES", run.stderr)
        self.assertEqual(self.source.read_bytes(), before)

    def test_cli_report_path_cannot_overwrite_zip(self):
        profile_path = Path(self.tmp.name) / "profile.json"
        profile_path.write_text(json.dumps(self.profile), encoding="utf-8")
        before = self.archive.read_bytes()
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "--profile", str(profile_path),
             "--archive", str(self.archive), "--original-source", str(self.source),
             "--output", str(self.archive)], capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 2)
        self.assertIn("OUTPUT_ALIASES_INPUT_BYTES", run.stderr)
        self.assertEqual(self.archive.read_bytes(), before)

    def test_cli_report_path_cannot_write_inside_git_checkout(self):
        profile_path = Path(self.tmp.name) / "profile.json"
        profile_path.write_text(json.dumps(self.profile), encoding="utf-8")
        target = ROOT / "Workspaces" / "forbidden-attestation-output.json"
        run = subprocess.run(
            [sys.executable, str(SCRIPT), "--profile", str(profile_path),
             "--archive", str(self.archive), "--original-source", str(self.source),
             "--output", str(target)], capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 2)
        self.assertIn("OUTPUT_INSIDE_REPOSITORY_FORBIDDEN", run.stderr)
        self.assertFalse(target.exists())

    def test_cli_real_fixture_status_and_no_false_final(self):
        profile_path = Path(self.tmp.name) / "profile.json"
        profile_path.write_text(json.dumps(self.profile), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), "--profile", str(profile_path),
                            "--archive", str(self.archive), "--original-source",
                            str(self.source)], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        result = json.loads(r.stdout)
        self.assertEqual(result["stage5_final"], "NOT_ATTESTED")
        self.assertEqual(result["status"],
                         "PASS_EXACT_SOURCE_PACKAGE_BYTES_AND_MANIFEST__SCOPED_NOT_FINAL")


if __name__ == "__main__":
    unittest.main()
