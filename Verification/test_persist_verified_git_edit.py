"""Synthetic-only OP-01 integration negatives for the opt-in real Git writer.

The API is injected in tests: no learner content, GitHub mutation, or Library access.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("remote_cas_writer", ROOT / "persist_verified_git_edit.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakeGitHub:
    def __init__(self, data: bytes):
        self.data = data
        self.calls = []
        self.conflict = False
        self.corrupt_after_write = False
        self.bad_response = False
        self.bad_encoding = False

    def __call__(self, method, path, branch, token, payload=None):
        self.calls.append(method)
        if method == "GET":
            if self.bad_encoding:
                return {"type": "file", "encoding": "none", "content": "",
                        "size": len(self.data), "sha": m.git_blob_sha(self.data)}
            return {"type": "file", "encoding": "base64",
                    "content": base64.b64encode(self.data).decode("ascii"),
                    "size": len(self.data), "sha": m.git_blob_sha(self.data)}
        if method != "PUT":
            raise AssertionError("unexpected method")
        if self.conflict:
            raise m.PersistenceBlocked("CAS_CONFLICT: simulated remote concurrent writer")
        if payload["sha"] != m.git_blob_sha(self.data):
            raise AssertionError("PUT missing preimage SHA")
        incoming = base64.b64decode(payload["content"])
        self.data = incoming + b"tamper" if self.corrupt_after_write else incoming
        sha_new = m.git_blob_sha(incoming)
        return {"content": {"sha": "0" * 40 if self.bad_response else sha_new},
                "commit": {"sha": "a" * 40}}


class RemoteGitAppliedEditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.before = {"cards": [
            {"id": "c1", "de": "sehen", "fa": "دیدن"},
            {"id": "c2", "de": "lernen", "fa": "یادگرفتن"}]}
        self.after = copy.deepcopy(self.before)
        self.after["cards"][0]["fa"] = "مشاهده کردن"
        self.source = b"immutable source"
        self.proof = {
            "schema": "gcpk-applied-edit-bytes-proof@1",
            "status": "APPLIED_SCOPED", "format": "JSON_ITEMS_V1",
            "workstream": "synthetic-op01", "artifact_id": "CURRENT-SYNTHETIC",
            "applied_count": 1,
            "edits": [{"id": "c1", "fields": ["fa"]}],
            "files": {
                "parent": "parent.json", "current": "current.json",
                "readback": "readback.json", "source_before": "source-before.bin",
                "source_after": "source-after.bin", "qa": "qa.json",
                "pointer": "pointer.json"},
        }
        self.path = "Workspaces/synthetic-op01/editable/cards.json"
        self.save()

    def save(self):
        before = json.dumps(self.before, ensure_ascii=False, sort_keys=True).encode()
        current = json.dumps(self.after, ensure_ascii=False, sort_keys=True).encode()
        files = {
            "parent": before, "current": current, "readback": current,
            "source_before": self.source, "source_after": self.source,
            "qa": json.dumps({"result": "PASS", "test_suite": "synthetic-op01",
                              "assessed_sha256": sha(current),
                              "changed_ids": ["c1"]}).encode(),
            "pointer": json.dumps({"workstream": self.proof["workstream"],
                                   "artifact_id": self.proof["artifact_id"],
                                   "current_sha256": sha(current)}).encode(),
        }
        for key, value in files.items():
            (self.base / self.proof["files"][key]).write_bytes(value)
        self.proof["sha256"] = {
            key: sha(files[key]) for key in (
                "parent", "current", "readback", "source_before", "source_after", "qa")}
        self.proof_file = self.base / "proof.json"
        self.proof_file.write_text(json.dumps(self.proof, ensure_ascii=False), encoding="utf-8")
        self.parent_bytes = before
        self.current_bytes = current

    def run_persist(self, api, **kwargs):
        return m.persist(self.proof_file, kwargs.get("path", self.path),
                         kwargs.get("expected", m.git_blob_sha(self.parent_bytes)),
                         kwargs.get("token", "synthetic-token"),
                         api=api, branch=kwargs.get("branch", "main"))

    def rejects(self, api, fragment, **kwargs):
        with self.assertRaises(m.PersistenceBlocked) as ctx:
            self.run_persist(api, **kwargs)
        self.assertIn(fragment, str(ctx.exception))

    def test_exact_preimage_cas_update_independent_remote_readback(self):
        api = FakeGitHub(self.parent_bytes)
        result = self.run_persist(api)
        self.assertEqual(api.calls, ["GET", "PUT", "GET"])
        self.assertEqual(api.data, self.current_bytes)
        self.assertEqual(result["current_sha256"], result["remote_readback_sha256"])
        self.assertFalse(result["independent_linguistic_stage4"])
        self.assertFalse(result["global_writer_coverage"])
        self.assertFalse(result["library_readback_verified"])

    def test_report_only_rejected_before_network(self):
        self.after = copy.deepcopy(self.before)
        self.save()
        api = FakeGitHub(self.parent_bytes)
        self.rejects(api, "LOCAL_APPLIED_PROOF_FAILED")
        self.assertEqual(api.calls, [])

    def test_bad_qa_scope_rejected_before_network(self):
        qa = self.base / "qa.json"
        value = json.loads(qa.read_text())
        value["changed_ids"] = []
        qa.write_text(json.dumps(value))
        self.proof["sha256"]["qa"] = sha(qa.read_bytes())
        self.proof_file.write_text(json.dumps(self.proof))
        api = FakeGitHub(self.parent_bytes)
        self.rejects(api, "LOCAL_APPLIED_PROOF_FAILED")
        self.assertEqual(api.calls, [])

    def test_stale_remote_changed_parent_rejected(self):
        api = FakeGitHub(b"other mutable writer version")
        self.rejects(api, "STALE_CURRENT")
        self.assertEqual(api.calls, ["GET"])

    def test_stale_expected_blob_rejected(self):
        api = FakeGitHub(self.parent_bytes)
        self.rejects(api, "STALE_CURRENT", expected="0" * 40)
        self.assertEqual(api.calls, ["GET"])

    def test_server_cas_conflict_does_not_claim_success(self):
        api = FakeGitHub(self.parent_bytes)
        api.conflict = True
        self.rejects(api, "CAS_CONFLICT")
        self.assertEqual(api.calls, ["GET", "PUT"])
        self.assertEqual(api.data, self.parent_bytes)

    def test_remote_readback_differs_after_accepted_put(self):
        api = FakeGitHub(self.parent_bytes)
        api.corrupt_after_write = True
        self.rejects(api, "REMOTE_READBACK_MISMATCH")
        self.assertEqual(api.calls, ["GET", "PUT", "GET"])

    def test_unexpected_put_echo_is_uncertain_not_pass(self):
        api = FakeGitHub(self.parent_bytes)
        api.bad_response = True
        self.rejects(api, "WRITE_OUTCOME_UNCERTAIN")
        self.assertEqual(api.calls, ["GET", "PUT"])

    def test_remote_contents_bad_encoding_rejected(self):
        api = FakeGitHub(self.parent_bytes)
        api.bad_encoding = True
        self.rejects(api, "REMOTE_CONTENTS_UNUSABLE")
        self.assertEqual(api.calls, ["GET"])

    def test_immutable_paths_or_wrong_branch_refuse_before_network(self):
        for path in (
            "Workspaces/synthetic-op01/00-source/cards.json",
            "Workspaces/synthetic-op01/LOCKED/release.tsv",
            "Workspaces/synthetic-op01/CHECKPOINT.json",
            "Workspaces/synthetic-op01/LATEST.json",
            "Workspaces/synthetic-op01/../secret.tsv",
            "Optimization-Program/STATE.json",
            "Workspaces/synthetic-op01/archive.zip",
        ):
            with self.subTest(path=path):
                api = FakeGitHub(self.parent_bytes)
                self.rejects(api, "TARGET" if path.startswith("Optimization") or ".." in path or path.endswith(".zip") else "PATH", path=path)
                self.assertEqual(api.calls, [])
        api = FakeGitHub(self.parent_bytes)
        self.rejects(api, "UNAUTHORIZED_TARGET", branch="old-branch")
        self.assertEqual(api.calls, [])

    def test_missing_auth_or_explicit_sha_refuse(self):
        api = FakeGitHub(self.parent_bytes)
        self.rejects(api, "AUTH_REQUIRED", token="")
        self.rejects(api, "EXPECTED_BLOB_SHA_REQUIRED", expected="invalid")
        self.assertEqual(api.calls, [])

    def test_zip_proof_does_not_go_to_git_binary_transport(self):
        self.proof["format"] = "ZIP_TSV_V1"
        self.proof_file.write_text(json.dumps(self.proof))
        api = FakeGitHub(self.parent_bytes)
        with mock.patch.object(m, "verify_local", return_value=[]):
            self.rejects(api, "GIT_TEXT_ONLY")
        self.assertEqual(api.calls, [])

    def test_contents_http409_maps_to_conflict(self):
        err = urllib.error.HTTPError("https://api.github.com", 409, "conflict", None, None)
        with mock.patch.object(m.urllib.request, "urlopen", side_effect=err):
            with self.assertRaises(m.PersistenceBlocked) as ctx:
                m.github_api("PUT", self.path, "main", "synthetic-token", {"sha": "a"})
        self.assertIn("CAS_CONFLICT", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
