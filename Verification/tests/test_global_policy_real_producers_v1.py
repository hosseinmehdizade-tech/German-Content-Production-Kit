"""P1 real-producer policy gate: positive and adversarial synthetic regression tests.

The two PRIVATE genuine archives are not checked by GitHub CI: this suite uses
minimal synthetic zips, while the separate read-only local full-byte run has
an exact source-specific report and cannot be counted as CI archive readback.
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

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / "Verification/verify_global_policy_real_producers_v1.py"
spec = importlib.util.spec_from_file_location("gfp_opt_real_producer", FILE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

HEADER = ("id", "front", "back", "card_type", "category", "details",
          "custom_fields", "source")

def make_tsv(source: str, details: object = None, second_id: str = "c-02") -> bytes:
    if details is None:
        details = [{"title": "Definition Deutsch", "items": ["gültig"]}]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=HEADER, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for card_id in ("c-01", second_id):
        writer.writerow({
            "id": card_id, "front": "gehen", "back": "رفتن",
            "card_type": "de-vocabulary", "category": "Verb",
            "details": json.dumps(details, ensure_ascii=False),
            "custom_fields": json.dumps(
                {"presentation_contract": "gfp-vocabulary-neutral@1"},
                ensure_ascii=False), "source": source
        })
    return output.getvalue().encode("utf-8")

def synth(profile: dict, directory: Path, source: str | None = None,
          details: object = None, second_id: str = "c-02"):
    p = copy.deepcopy(profile)
    if source is None:
        source = p["source_value"]
    data = make_tsv(source, details=details, second_id=second_id)
    path = directory / p["zip_name"]
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as z:
        z.writestr(p["import_tsv_member"], data)
        z.writestr("NOTICE.txt", b"synthetic fixture only")
    p["zip_sha256"] = m.sha256(path.read_bytes())
    p["import_tsv_sha256"] = m.sha256(data)
    p["expected_rows"] = 2
    return p, path

class CrossProducerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = m.read_json(ROOT, m.PROFILE)

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.work = Path(self.td.name)

    def fixture(self, source=None, details=None, second_id="c-02"):
        p = copy.deepcopy(self.profile)
        first = p["profiles"][0]
        fake, zip_path = synth(first, self.work, source=source,
                               details=details, second_id=second_id)
        p["profiles"][0] = fake
        return p, zip_path, fake["id"]

    def test_actual_git_registry_and_upstream_validator_pins(self):
        sha, validator = m.policy_authority(ROOT, self.profile)
        self.assertEqual(sha, "b6d27c0b98f44cd8b0ffad325710f24f76da95e1")
        self.assertTrue(validator.is_file())

    def test_cli_cannot_use_an_unregistered_source_profile(self):
        with self.assertRaisesRegex(ValueError, "UNAUTHORIZED_PROFILE_OVERRIDE"):
            m.load_authoritative_profile(ROOT, "../my-unregistered-profile.json")

    def test_cli_profile_git_blob_pin_exact(self):
        original = m.load_authoritative_profile(ROOT, m.PROFILE)
        self.assertEqual(original["profiles"][0]["expected_rows"], 292)
        root = self.work / "repo"
        dest = root / m.PROFILE
        dest.parent.mkdir(parents=True)
        dest.write_bytes((ROOT / m.PROFILE).read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "PROFILE_GIT_BLOB_DRIFT"):
            m.load_authoritative_profile(root, m.PROFILE)

    def test_windows_crlf_is_allowed_only_for_exact_canonical_blob(self):
        p = ROOT / m.VALIDATOR
        data = p.read_bytes()
        sha = m.blob_sha(data.replace(b"\r\n", b"\n"))
        windows = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        self.assertTrue(m.git_blob_text_matches(windows, sha))
        self.assertFalse(m.git_blob_text_matches(windows + b"\n# tampered", sha))

    def test_real_profiles_have_two_distinct_source_owners(self):
        m.verify_profile(self.profile)
        self.assertEqual(len({x["family_id"] for x in self.profile["profiles"]}),2)
        self.assertEqual(
            sum(p["expected_rows"] for p in self.profile["profiles"]), 602)

    def test_positive_real_adapter_interface_with_synthetic_zip(self):
        p,z,ident = self.fixture()
        result = m.audit(p,{ident:z},allow_partial=True)
        self.assertEqual(result["status"],"PASS_READONLY_EXACT_HISTORICAL_REAL_ARCHIVE_FORMAT_ONLY")
        self.assertEqual(result["verified_real_rows"],2)
        self.assertEqual(result["verified_producers"],1)
        self.assertFalse(result["all_34_git_workspaces_adopted"])
        self.assertFalse(result["github_ci_rehashed_private_archives"])

    def test_full_two_producer_synthetic_contract(self):
        p,z,ident = self.fixture()
        other = copy.deepcopy(p["profiles"][1])
        q,y = synth(other,self.work)
        p["profiles"][1]=q
        r = m.audit(p,{ident:z,q["id"]:y})
        self.assertEqual(r["verified_producers"],2)
        self.assertEqual(r["verified_real_rows"],4)
        self.assertEqual(r["omitted_producers"],[])

    def test_missing_second_producer_refused_without_partial_flag(self):
        p,z,ident=self.fixture()
        with self.assertRaisesRegex(ValueError,"MISSING_REQUIRED_PRODUCER"):
            m.audit(p,{ident:z})

    def test_wrong_zip_sha_fails_before_schema(self):
        p,z,ident=self.fixture()
        p["profiles"][0]["zip_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"ARCHIVE_SHA_MISMATCH"):
            m.audit(p,{ident:z},allow_partial=True)

    def test_wrong_import_member_digest_fails(self):
        p,z,ident=self.fixture()
        p["profiles"][0]["import_tsv_sha256"]="e"*64
        with self.assertRaisesRegex(ValueError,"IMPORT_TSV_SHA_MISMATCH"):
            m.audit(p,{ident:z},allow_partial=True)

    def test_wrong_source_role_fails(self):
        p,z,ident=self.fixture(source="wrong producer")
        with self.assertRaisesRegex(ValueError,"TSV_ROW_OR_SOURCE_MISMATCH"):
            m.audit(p,{ident:z},allow_partial=True)

    def test_duplicate_card_id_fails(self):
        p,z,ident=self.fixture(second_id="c-01")
        with self.assertRaisesRegex(ValueError,"DUPLICATE_CARD_ID"):
            m.audit(p,{ident:z},allow_partial=True)

    def test_structurally_invalid_details_rejected_by_central_policy(self):
        p,z,ident=self.fixture(details="nonsense German prose")
        with self.assertRaisesRegex(ValueError,"REAL_PRODUCER_NEUTRAL_POLICY_FAIL"):
            m.audit(p,{ident:z},allow_partial=True)

    def test_duplicate_archive_member_fails_closed(self):
        p,z,ident=self.fixture()
        data=z.read_bytes()
        with zipfile.ZipFile(z,"a") as archive:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                archive.writestr(p["profiles"][0]["import_tsv_member"],b"bad")
        p["profiles"][0]["zip_sha256"]=m.sha256(z.read_bytes())
        with self.assertRaisesRegex(ValueError,"DUPLICATE_ZIP_MEMBER"):
            m.audit(p,{ident:z},allow_partial=True)

    def test_incorrect_stage_or_global_adoption_claim_rejected(self):
        p,z,ident=self.fixture()
        p["nonclaims"]["all_producers_verified"] = True
        with self.assertRaisesRegex(ValueError,"FALSE_STAGE_OR_CURRENT_PASS"):
            m.audit(p,{ident:z},allow_partial=True)

    def test_unauthorized_linguistic_stage4_claim_rejected(self):
        p,z,ident=self.fixture()
        p["profiles"][0]["stage4_reverified"]=True
        with self.assertRaisesRegex(ValueError,"FALSE_RELEASE_SCOPE"):
            m.audit(p,{ident:z},allow_partial=True)

    def test_altered_registry_bytes_block_adoption(self):
        p,z,ident=self.fixture()
        root=self.work/"root"
        (root/"Prompt").mkdir(parents=True)
        target=root/m.POLICY_REGISTRY
        target.write_bytes((ROOT/m.POLICY_REGISTRY).read_bytes()+b"\n")
        (root/"Verification").mkdir(parents=True)
        shutil.copyfile(ROOT/m.VALIDATOR,root/m.VALIDATOR)
        with self.assertRaisesRegex(ValueError,"REGISTRY_BLOB_NOT_EXACT"):
            m.audit(p,{ident:z},root=root,allow_partial=True)

    def test_altered_validator_bytes_block_adoption(self):
        p,z,ident=self.fixture()
        root=self.work/"root"
        (root/"Prompt").mkdir(parents=True)
        shutil.copyfile(ROOT/m.POLICY_REGISTRY,root/m.POLICY_REGISTRY)
        (root/"Verification").mkdir(parents=True)
        target=root/m.VALIDATOR
        target.write_bytes((ROOT/m.VALIDATOR).read_bytes()+b"\n")
        with self.assertRaisesRegex(ValueError,"POLICY_VALIDATOR_BLOB_DRIFT"):
            m.audit(p,{ident:z},root=root,allow_partial=True)

    def test_unapproved_zip_source_path_fails(self):
        p,z,ident=self.fixture()
        p["profiles"][0]["import_tsv_member"]="../secret.tsv"
        with self.assertRaisesRegex(ValueError,"UNSAFE_IMPORT_MEMBER"):
            m.audit(p,{ident:z},allow_partial=True)

    def test_unpinned_new_producer_fails(self):
        p,z,ident=self.fixture()
        with self.assertRaisesRegex(ValueError,"UNKNOWN_PRODUCER"):
            m.audit(p,{"producer:unknown":z},allow_partial=True)

    def test_source_not_written_when_audited(self):
        p,z,ident=self.fixture()
        before=m.sha256(z.read_bytes())
        m.audit(p,{ident:z},allow_partial=True)
        self.assertEqual(m.sha256(z.read_bytes()),before)

    def test_bad_actual_archive_is_not_replaceable_by_similar_name(self):
        p,z,ident=self.fixture()
        wrong=self.work/"similar-archive.zip"
        shutil.copyfile(z,wrong)
        with self.assertRaisesRegex(ValueError,"ARCHIVE_FILENAME_WRONG_PRODUCER"):
            m.audit(p,{ident:wrong},allow_partial=True)

    def test_source_type_compulsory_exact_policy(self):
        p,z,ident=self.fixture()
        p["policy_scope"]="ALL_SOURCES_SEMANTICALLY_APPROVED"
        with self.assertRaisesRegex(ValueError,"HISTORICAL_SCOPE_PROMOTED"):
            m.audit(p,{ident:z},allow_partial=True)

if __name__ == "__main__":
    unittest.main()
