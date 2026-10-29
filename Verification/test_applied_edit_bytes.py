"""Synthetic-only adversarial tests of OP-01 actual-current edit proof."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import csv
import io
import zipfile
import tempfile
import unittest
from pathlib import Path

MOD = Path(__file__).resolve().with_name("validate_applied_edit_bytes.py")
spec = importlib.util.spec_from_file_location("applied_edit_bytes", MOD)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class AppliedEditByteProofTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.before = {"cards": [
            {"id": "c1", "de": "sich erinnern", "fa": "یادش آمد", "en": "remember"},
            {"id": "c2", "de": "lernen", "fa": "یاد گرفتن", "en": "learn"}]}
        self.after = copy.deepcopy(self.before)
        self.after["cards"][0]["fa"] = "به یاد آوردن"
        self.source = b"immutable original author material"
        self.proof = {
            "schema": v.SCHEMA, "status": "APPLIED_SCOPED",
            "workstream": "synthetic-test-only", "artifact_id": "CURRENT-SYNTHETIC",
            "applied_count": 1,
            "edits": [{"id": "c1", "fields": ["fa"]}],
            "files": {key: key + ".json" for key in v.FILE_KEYS},
            "sha256": {}}
        self.proof["files"]["source_before"] = "source-before.bin"
        self.proof["files"]["source_after"] = "source-after.bin"
        self.save()

    def write_bytes(self, key, data: bytes):
        (self.root / self.proof["files"][key]).write_bytes(data)

    def save(self, *, readback: bytes | None = None, source_after: bytes | None = None,
             pointer_current_sha: str | None = None, qa_current_sha: str | None = None,
             qa_result: str = "PASS", qa_ids: list[str] | None = None):
        before_raw = json.dumps(self.before, ensure_ascii=False, sort_keys=True).encode("utf-8")
        current_raw = json.dumps(self.after, ensure_ascii=False, sort_keys=True).encode("utf-8")
        observed_ids = [a["id"] for b, a in zip(self.before["cards"], self.after["cards"]) if a != b]
        pointer = {"workstream": self.proof["workstream"], "artifact_id": self.proof["artifact_id"],
                   "current_sha256": pointer_current_sha or sha(current_raw)}
        qa = {"result": qa_result, "test_suite": "synthetic-content-scope",
              "assessed_sha256": qa_current_sha or sha(current_raw),
              "changed_ids": sorted(qa_ids if qa_ids is not None else observed_ids)}
        data = {
            "parent": before_raw, "current": current_raw,
            "readback": current_raw if readback is None else readback,
            "source_before": self.source,
            "source_after": self.source if source_after is None else source_after,
            "qa": json.dumps(qa, sort_keys=True).encode(),
            "pointer": json.dumps(pointer, sort_keys=True).encode(),
        }
        for key, content in data.items():
            self.write_bytes(key, content)
        self.proof["sha256"] = {key: sha(data[key]) for key in v.HASH_KEYS}
        self.save_proof()

    def save_proof(self):
        self.proof_path = self.root / "proof.json"
        self.proof_path.write_text(json.dumps(self.proof, ensure_ascii=False), encoding="utf-8")

    def errors(self):
        return v.verify(self.proof_path)

    def assert_rejected(self, fragment: str):
        messages = self.errors()
        self.assertTrue(any(fragment in msg for msg in messages), messages)

    def test_real_mutable_changed_bytes_and_readback_pass_scoped(self):
        self.assertEqual(self.errors(), [])

    def test_report_only_same_current_bytes_rejected_even_with_forged_hashes(self):
        self.after = copy.deepcopy(self.before)
        self.proof["applied_count"] = 0
        self.proof["edits"] = []
        self.save()
        self.assert_rejected("CURRENT bytes unchanged")

    def test_declared_edit_but_no_actual_change_rejected(self):
        self.after = copy.deepcopy(self.before)
        self.save()
        self.assert_rejected("actual changed IDs/fields")

    def test_wrong_current_hash_rejected(self):
        self.proof["sha256"]["current"] = "f" * 64
        self.save_proof()
        self.assert_rejected("SHA256 mismatch: current")

    def test_stale_current_pointer_rejected(self):
        self.save(pointer_current_sha="f" * 64)
        self.assert_rejected("currentness pointer")

    def test_wrong_workstream_pointer_rejected(self):
        pointer = self.root / self.proof["files"]["pointer"]
        data = json.loads(pointer.read_text())
        data["workstream"] = "different-branch"
        pointer.write_text(json.dumps(data))
        self.assert_rejected("currentness pointer identity mismatch")

    def test_qa_claims_stale_parent_rejected(self):
        parent_digest = self.proof["sha256"]["parent"]
        self.save(qa_current_sha=parent_digest)
        self.assert_rejected("post-edit QA assessed wrong")

    def test_qa_failure_rejected(self):
        self.save(qa_result="FAIL")
        self.assert_rejected("post-edit QA not PASS")

    def test_qa_omits_changed_id_rejected(self):
        self.save(qa_ids=[])
        self.assert_rejected("QA changed-ID scope")

    def test_persisted_readback_differs_rejected_even_if_receipt_rehashed(self):
        self.save(readback=b'{"cards":[]}')
        self.assert_rejected("persisted readback differs")

    def test_source_mutation_rejected_even_if_receipt_rehashed(self):
        self.save(source_after=b"tampered original source")
        self.assert_rejected("immutable source bytes mutated")

    def test_unlisted_second_card_change_rejected(self):
        self.after["cards"][1]["en"] = "study"
        self.save()
        self.assert_rejected("actual changed IDs/fields")

    def test_unlisted_field_on_same_card_rejected(self):
        self.after["cards"][0]["de"] = "erinnern"
        self.save()
        self.assert_rejected("actual changed IDs/fields")

    def test_reordered_cards_rejected(self):
        self.after["cards"] = list(reversed(self.after["cards"]))
        self.save()
        self.assert_rejected("card count/order/identity changed")

    def test_duplicate_stable_ids_rejected(self):
        self.after["cards"][1]["id"] = "c1"
        self.save()
        self.assert_rejected("duplicate stable IDs")

    def test_same_path_as_readback_rejected(self):
        self.proof["files"]["readback"] = self.proof["files"]["current"]
        self.save_proof()
        self.assert_rejected("readback must be a separate file")

    def test_path_traversal_rejected(self):
        self.proof["files"]["current"] = "../outside.json"
        self.save_proof()
        self.assert_rejected("unsafe current path")

    def test_missing_readback_rejected(self):
        (self.root / self.proof["files"]["readback"]).unlink()
        self.assert_rejected("unreadable readback")

    def test_reject_silent_missing_source_hash(self):
        del self.proof["sha256"]["source_after"]
        self.save_proof()
        self.assert_rejected("SHA256 mismatch: source_after")

    def test_missing_identity_rejected_without_crashing(self):
        del self.proof["workstream"]
        self.save_proof()
        self.assert_rejected("missing workstream")


class TsvZipProofTests(unittest.TestCase):
    """All bytes are invented local fixtures; no user content or source changes."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cols = ["id", "de", "fa", "en"]
        self.old = [["c1", "sehen", "دیدن", "see"],
                    ["c2", "lernen", "یاد گرفتن", "learn"]]
        self.new = copy.deepcopy(self.old)
        self.new[0][2] = "مشاهده کردن"
        self.mode = "TSV_ITEMS_V1"
        self.extra = b"untouched source metadata"
        self.qa_current = None
        self.qa_ids = None
        self.readback_bytes = None
        self.proof = {
            "schema": v.SCHEMA, "status": "APPLIED_SCOPED",
            "workstream": "synthetic-tsv-only", "artifact_id": "CURRENT-TSV",
            "format": "TSV_ITEMS_V1", "id_column": "id",
            "applied_count": 1, "edits": [{"id": "c1", "fields": ["fa"]}],
            "files": {key: key + ".bin" for key in v.FILE_KEYS},
        }
        self.proof["member"] = "Lessons/L01.tsv"
        self.proof["manifest_member"] = "SHA256SUMS"
        self.save()

    def tsv(self, rows: list[list[str]]) -> bytes:
        target = io.StringIO(newline="")
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(self.cols)
        writer.writerows(rows)
        return target.getvalue().encode("utf-8")

    def archive(self, tsv_bytes: bytes, extra: bytes | None = None,
                *, bad_manifest: bool = False, insert_unrelated: bool = False,
                extra_name: str = "support/source.txt") -> bytes:
        payloads = {
            self.proof["member"]: tsv_bytes,
            extra_name: self.extra if extra is None else extra,
        }
        if insert_unrelated:
            payloads["another/unrelated.txt"] = b"unpermitted new member"
        manifest = "".join(
            f"{'0' * 64 if bad_manifest else sha(data)}  {name}\n"
            for name, data in sorted(payloads.items())
        ).encode("utf-8")
        target = io.BytesIO()
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in payloads.items():
                archive.writestr(name, data)
            archive.writestr("SHA256SUMS", manifest)
        return target.getvalue()

    def save(self, *, corrupt_current_manifest: bool = False,
             zip_extra_current: bytes | None = None, extra_new_member: bool = False,
             raw_readback: bytes | None = None, extra_name: str = "support/source.txt"):
        parent_raw = self.tsv(self.old)
        current_raw = self.tsv(self.new)
        if self.mode == "ZIP_TSV_V1":
            parent_raw = self.archive(parent_raw)
            current_raw = self.archive(
                current_raw, extra=zip_extra_current,
                bad_manifest=corrupt_current_manifest,
                insert_unrelated=extra_new_member, extra_name=extra_name)
        current_sha = sha(current_raw)
        pointer = {"workstream": self.proof["workstream"],
                   "artifact_id": self.proof["artifact_id"],
                   "current_sha256": current_sha}
        qa = {"result": "PASS", "test_suite": "synthetic-postedit-scope",
              "assessed_sha256": self.qa_current or current_sha,
              "changed_ids": sorted(self.qa_ids if self.qa_ids is not None else ["c1"])}
        data = {
            "parent": parent_raw, "current": current_raw,
            "readback": current_raw if raw_readback is None else raw_readback,
            "source_before": b"original-source-frozen",
            "source_after": b"original-source-frozen",
            "qa": json.dumps(qa).encode("utf-8"),
            "pointer": json.dumps(pointer).encode("utf-8"),
        }
        for key, value in data.items():
            (self.root / self.proof["files"][key]).write_bytes(value)
        self.proof["sha256"] = {key: sha(data[key]) for key in v.HASH_KEYS}
        self.proof_file = self.root / "proof.json"
        self.proof_file.write_text(json.dumps(self.proof, ensure_ascii=False), encoding="utf-8")

    def issues(self):
        return v.verify(self.proof_file)

    def expect_reject(self, message):
        found = self.issues()
        self.assertTrue(any(message in issue for issue in found), found)

    def test_tsv_valid_changed_field_and_readback_pass(self):
        self.assertEqual(self.issues(), [])

    def test_tsv_unlisted_field_edit_rejected(self):
        self.new[0][3] = "look"
        self.save()
        self.expect_reject("actual changed IDs/fields")

    def test_tsv_unlisted_card_edit_rejected(self):
        self.new[1][2] = "یادگیری"
        self.save()
        self.expect_reject("actual changed IDs/fields")

    def test_tsv_row_reordering_rejected(self):
        self.new.reverse()
        self.save()
        self.expect_reject("card count/order/identity changed")

    def test_tsv_duplicate_stable_id_rejected(self):
        self.new[1][0] = "c1"
        self.save()
        self.expect_reject("duplicate stable IDs")

    def test_tsv_duplicate_headers_rejected(self):
        self.cols = ["id", "de", "fa", "fa"]
        self.save()
        self.expect_reject("TSV missing/duplicate columns")

    def test_tsv_new_column_rejected_as_disallowed_schema(self):
        self.cols.append("tag")
        for row in self.old + self.new:
            row.append("X")
        self.new[0][-1] = "Y"
        self.save()
        self.expect_reject("actual changed IDs/fields")

    def test_tsv_stale_qa_rejected(self):
        self.qa_current = "f" * 64
        self.save()
        self.expect_reject("post-edit QA assessed wrong")

    def test_tsv_missing_or_ragged_row_rejected(self):
        self.new[0].pop()
        self.save()
        self.expect_reject("TSV empty, ragged")

    def test_zip_valid_single_member_edited_pass(self):
        self.mode = "ZIP_TSV_V1"
        self.proof["format"] = "ZIP_TSV_V1"
        self.save()
        self.assertEqual(self.issues(), [])

    def test_zip_unrelated_payload_mutation_rejected_with_valid_manifest(self):
        self.mode = "ZIP_TSV_V1"
        self.proof["format"] = "ZIP_TSV_V1"
        self.save(zip_extra_current=b"changed but not declared")
        self.expect_reject("unrelated ZIP member payload changed")

    def test_zip_additional_member_rejected(self):
        self.mode = "ZIP_TSV_V1"
        self.proof["format"] = "ZIP_TSV_V1"
        self.save(extra_new_member=True)
        self.expect_reject("ZIP member inventory changed")

    def test_zip_incorrect_manifest_hash_rejected(self):
        self.mode = "ZIP_TSV_V1"
        self.proof["format"] = "ZIP_TSV_V1"
        self.save(corrupt_current_manifest=True)
        self.expect_reject("ZIP member SHA256 mismatch")

    def test_zip_untrusted_member_path_rejected(self):
        self.mode = "ZIP_TSV_V1"
        self.proof["format"] = "ZIP_TSV_V1"
        self.save(extra_name="../escape.txt")
        self.expect_reject("unsafe, oversized or malformed members")

    def test_zip_wrong_target_member_rejected(self):
        self.mode = "ZIP_TSV_V1"
        self.proof["format"] = "ZIP_TSV_V1"
        self.proof["member"] = "Lessons/missing.tsv"
        self.save()
        # A synthetic fixture can be internally self-consistent for any declared
        # member: verify a forged pointer to a non-existent member instead.
        self.proof["member"] = "Lessons/missing-now.tsv"
        self.proof_file.write_text(json.dumps(self.proof), encoding="utf-8")
        self.expect_reject("ZIP missing, duplicate, unsafe")

    def test_zip_no_actual_target_change_rejected(self):
        self.mode = "ZIP_TSV_V1"
        self.proof["format"] = "ZIP_TSV_V1"
        self.new = copy.deepcopy(self.old)
        self.save()
        self.expect_reject("report-only: CURRENT bytes unchanged")

    def test_zip_readback_mismatch_even_if_all_claimed_hashes_match(self):
        self.mode = "ZIP_TSV_V1"
        self.proof["format"] = "ZIP_TSV_V1"
        self.save(raw_readback=b"fake-persisted-other-archive")
        self.expect_reject("persisted readback differs")

    def test_format_not_declared_rejected_when_tsv_input(self):
        del self.proof["format"]
        self.proof_file.write_text(json.dumps(self.proof), encoding="utf-8")
        self.expect_reject("unverified content format/JSON receipt")



if __name__ == "__main__":
    unittest.main()
