"""Atomic accepted-owner publication: positive and fail-closed regression tests."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Tools"))
import publish_accepted_content_v1 as pub


class AcceptedPublicationTests(unittest.TestCase):
    def setUp(self):
        self.family = "family:fixture-0"
        self.owner = "Workspaces/fixture0/LATEST.json"
        self.receipt_path = "Workspaces/fixture0/ACCEPTANCE.json"
        self.old = "a" * 64
        self.files = {}
        self.items = []
        self.routes = []
        self.catalog = {"families": []}
        for n in range(10):
            fid = "family:fixture-" + str(n)
            workspace = "Workspaces/fixture" + str(n)
            path = workspace + "/LATEST.json"
            raw = pub.encode({"release": {"sha256": self.old}, "status": "USER_ACCEPTED"})
            self.files[path] = raw
            self.catalog["families"].append({"id": fid})
            self.items.append({"id": fid, "owner_locator": {
                "path": path, "git_blob_observed": pub.git_blob_sha(raw),
                "artifact_sha_json_pointer": "/release/sha256"},
                "active_baseline": {"artifact_name": "old.zip", "artifact_sha256": self.old,
                                    "artifact_size_bytes": 100},
                "metrics": {"cards": 10}})
            self.routes.append({"family_id": fid, "canonical_git_workspace": workspace,
                                "canonical_source_owner_document": path,
                                "active_content_sha256": self.old})
        self.files[pub.REGISTRY] = pub.encode({
            "schema": "gfp-opt-dynamic-content-portfolio-registry@1.0.0",
            "registry_state": "FIXTURE", "items": self.items,
            "total_cards_including_cross_family_overlap": 100,
            "byte_evidence_bridge": {"receipt": "historical.json"}})
        self.files[pub.CATALOG] = pub.encode(self.catalog)
        self.files[pub.ROUTING] = pub.encode({"families": self.routes})
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("Content/test.tsv", "one\ttwo\n")
        self.archive = buf.getvalue()
        self.sha = hashlib.sha256(self.archive).hexdigest()
        self.receipt = {"status": "USER_ACCEPTED_SCOPED_CONTENT",
                        "release": {"zip_sha256": self.sha, "name": "new.zip"},
                        "counts": {"cards": 12}}
        self.kw = dict(family=self.family, expected_parent=self.old,
                       expected_owner_blob=pub.git_blob_sha(self.files[self.owner]),
                       new_owner=pub.encode({"release": {"sha256": self.sha}}),
                       receipt_path=self.receipt_path, receipt_bytes=pub.encode(self.receipt),
                       archive=self.archive, sha_pointer="/release/zip_sha256",
                       name_pointer="/release/name", cards_pointer="/counts/cards",
                       location="Library fixture")

    def plan(self, **kw):
        return pub.build_plan(self.files.get, **(self.kw | kw))

    def test_one_plan_updates_owner_receipt_two_mirrors(self):
        snapshot = copy.deepcopy(self.files)
        plan = self.plan()
        result = {f["path"]: f["content"].encode() for f in plan["files"]}
        self.assertEqual(set(result), {self.owner, self.receipt_path, pub.REGISTRY, pub.ROUTING})
        self.assertEqual(self.files, snapshot)
        r = pub.obj(result[pub.REGISTRY])
        t = pub.obj(result[pub.ROUTING])
        self.assertEqual(r["items"][0]["active_baseline"]["artifact_sha256"], self.sha)
        self.assertEqual(r["items"][0]["owner_locator"]["git_blob_observed"],
                         pub.git_blob_sha(result[self.owner]))
        self.assertEqual(t["families"][0]["active_content_sha256"], self.sha)
        self.assertEqual(r["items"][1:], self.items[1:])
        self.assertEqual(t["families"][1:], self.routes[1:])
        self.assertEqual(r["total_cards_including_cross_family_overlap"], 102)
        self.assertEqual(r["items"][0]["previous_accepted_baseline"]["artifact_sha256"], self.old)
        self.assertEqual(r["items"][0]["active_baseline"]["historical_asof_observation"]["artifact_sha256"],
                         self.old)
        self.assertEqual(r["items"][0]["runtime_stage"], "NO_NEW_INDEPENDENT_RUNTIME_OR_SRS_ATTESTATION")

    def test_stale_blob_and_parent_rejected(self):
        for overrides in ({"expected_owner_blob": "f"*40}, {"expected_parent": "f"*64}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                self.plan(**overrides)

    def test_unaccepted_status_rejected(self):
        for status in ("CANDIDATE_ONLY", "FINAL", "NOT_USER_ACCEPTED", "PENDING_USER_ACCEPTANCE",
                       "USER_ACCEPTED_FALSE"):
            with self.subTest(status=status), self.assertRaises(ValueError):
                self.plan(receipt_bytes=pub.encode(self.receipt | {"status": status}))

    def test_wrong_archive_rejected(self):
        with self.assertRaises((ValueError, zipfile.BadZipFile)):
            self.plan(archive=b"not the approved zip")

    def test_wrong_receipt_sha_rejected(self):
        r = copy.deepcopy(self.receipt)
        r["release"]["zip_sha256"] = "b" * 64
        with self.assertRaises(ValueError):
            self.plan(receipt_bytes=pub.encode(r))

    def test_cross_family_and_immutable_receipt_rejected(self):
        with self.assertRaises(ValueError):
            self.plan(receipt_path="Workspaces/fixture1/ACCEPTANCE.json")
        self.files[self.receipt_path] = b"previous immutable receipt"
        with self.assertRaises(ValueError):
            self.plan()

    def test_missing_family_rejected(self):
        with self.assertRaises(ValueError):
            self.plan(family="family:unknown")

    def test_existing_receipt_not_written_again(self):
        self.files[self.receipt_path] = self.kw["receipt_bytes"]
        self.assertNotIn(self.receipt_path, [f["path"] for f in self.plan()["files"]])

    def test_metadata_only_preserves_selected_baseline(self):
        p = self.plan(new_owner=pub.encode({"release": {"sha256": self.old}, "note": "metadata"}),
                      receipt_path=None, receipt_bytes=None, archive=None, metadata_only=True)
        self.assertEqual({f["path"] for f in p["files"]}, {self.owner, pub.REGISTRY})
        r = pub.obj(next(f["content"] for f in p["files"] if f["path"] == pub.REGISTRY))
        self.assertEqual(r["items"][0]["active_baseline"], self.items[0]["active_baseline"])
        with self.assertRaises(ValueError):
            self.plan(receipt_path=None, receipt_bytes=None, archive=None, metadata_only=True)

    def test_noop_rejected(self):
        with self.assertRaises(ValueError):
            self.plan(new_owner=self.files[self.owner])

    def test_real_git_atomic_commit_and_branch_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", "-C", str(root), *args])
            git("init", "-q")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "user.name", "Fixture")
            for name, raw in self.files.items():
                dst = root / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(raw)
            git("add", ".")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD").decode().strip()
            plan = pub.build_plan(pub.base_reader(root, base), **self.kw)
            commit = pub.publish_branch(root, base, plan, "content/fixture-release")
            self.assertEqual(git("rev-parse", "HEAD").decode().strip(), base)
            self.assertEqual(git("status", "--porcelain"), b"")
            self.assertEqual(git("rev-parse", "content/fixture-release").decode().strip(), commit)
            self.assertEqual(set(git("diff", "--name-only", base, commit).decode().splitlines()),
                             {self.owner, self.receipt_path, pub.REGISTRY, pub.ROUTING})
            for f in plan["files"]:
                self.assertEqual(git("show", commit + ":" + f["path"]), f["content"].encode())
            with self.assertRaises(subprocess.CalledProcessError):
                pub.publish_branch(root, base, plan, "content/fixture-release")
            with self.assertRaises(ValueError):
                pub.publish_branch(root, base, plan, "main")


if __name__ == "__main__":
    unittest.main()
