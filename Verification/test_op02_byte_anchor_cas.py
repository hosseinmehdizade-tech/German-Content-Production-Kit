"""OP02 exact-byte & rollback preflight adversarial regressions: no network/writes."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_op02_byte_anchor_cas import (
    source_bytes, git_control_blob, rollback_preflight, sha256,
    git_blob_sha1, read_regular_file)

PDF1=b"%PDF-1.7\nthis is synthetic source a\n"
PDF2=b"%PDF-1.6\nthis is synthetic source b\n"

def source_fixture():
    spec=[{"source_id":"a","modality":"pdf","sha256":sha256(PDF1),
           "size_bytes":len(PDF1)},
          {"source_id":"b","modality":"pdf","sha256":sha256(PDF2),
           "size_bytes":len(PDF2)}]
    return spec, {"a":PDF1,"b":PDF2}, {"a":sha256(PDF1),"b":sha256(PDF2)}

def git_fixture():
    data=b'{"schema":"test"}\n'
    a={"repository":"hosseinmehdizade-tech/German-Content-Production-Kit",
       "path":"Workspaces/aber-hallo-listen-tabellen/LATEST.json",
       "commit_sha":"a"*40,"blob_sha":git_blob_sha1(data),
       "sha256":sha256(data)}
    return data,a,copy.deepcopy(a)

class BytesCas(unittest.TestCase):
    def deny(self,r):
        for field in ("authenticated_trust_root","authenticated_issuer",
                      "stage4_semantic_pass","stage5_7_authorized",
                      "writer_granted","performed_writes"):
            self.assertIs(r[field],False)

    def source_fail(self,mutate,code):
        a=list(copy.deepcopy(source_fixture()))
        mutate(a)
        r=source_bytes(*a)
        self.assertEqual(r["status"],"BLOCKED",r)
        self.assertIn(code,r["errors"],r)
        self.deny(r)

    def git_fail(self,mutate,code):
        a=list(copy.deepcopy(git_fixture()))
        mutate(a)
        r=git_control_blob(*a)
        self.assertEqual(r["status"],"BLOCKED",r)
        self.assertIn(code,r["errors"],r)
        self.deny(r)

    def test_two_synthetic_pdf_bytes_pass_only_scoped(self):
        r=source_bytes(*source_fixture())
        self.assertEqual(r["status"],"PASS_SCOPED_BYTES_ONLY_NOT_RELEASE",r)
        self.assertTrue(r["byte_matches"])
        self.assertEqual(len(r["items"]),2)
        self.deny(r)

    def test_git_object_sha1_known_vector(self):
        self.assertEqual(git_blob_sha1(b"test\n"),
                         "9daeafb9864cf43055ae93beb0afd6c7d144bfa4")

    def test_git_bytes_match_only_scoped(self):
        r=git_control_blob(*git_fixture())
        self.assertEqual(r["status"],"PASS_SCOPED_BYTES_ONLY_NOT_RELEASE",r)
        self.assertTrue(r["byte_matches"])
        self.deny(r)

    def test_two_self_attested_pins_cannot_grant_issuer(self):
        d,a,p=git_fixture()
        a["commit_sha"]=p["commit_sha"]="f"*40
        r=git_control_blob(d,a,p)
        self.assertEqual(r["status"],"PASS_SCOPED_BYTES_ONLY_NOT_RELEASE",r)
        self.deny(r)

    def test_source_one_byte_mutation(self):
        self.source_fail(lambda a:a[1].update(a=PDF1[:-1]+b"!"),
                         "BYTE_HASH_SIZE_OR_MAGIC_DRIFT:a")

    def test_source_raw_bytes_swapped(self):
        self.source_fail(lambda a:a[1].update(a=PDF2,b=PDF1),
                         "BYTE_HASH_SIZE_OR_MAGIC_DRIFT:a")

    def test_manifest_coordinated_with_forged_raw_but_external_pin(self):
        def mutate(a):
            forged=b"%PDF-1.7\nforged"
            a[1]["a"]=forged
            a[0][0].update(sha256=sha256(forged),size_bytes=len(forged))
        self.source_fail(mutate,"PIN_OR_MANIFEST_DRIFT:a")

    def test_manifest_and_external_pin_disagree(self):
        self.source_fail(lambda a:a[2].update(a="f"*64),"PIN_OR_MANIFEST_DRIFT:a")

    def test_source_missing(self):
        self.source_fail(lambda a:a[1].pop("b"),"SOURCE_UNIVERSE_DRIFT")

    def test_source_extra_unregistered(self):
        self.source_fail(lambda a:a[1].update(extra=b"data"),"SOURCE_UNIVERSE_DRIFT")

    def test_duplicate_source_id(self):
        self.source_fail(lambda a:a[0][1].update(source_id="a"),"SOURCE_UNIVERSE_DRIFT")

    def test_source_pin_missing(self):
        self.source_fail(lambda a:a[2].pop("b"),"SOURCE_UNIVERSE_DRIFT")

    def test_source_boolean_size_rejected(self):
        self.source_fail(lambda a:a[0][0].update(size_bytes=True),"SOURCE_SPEC_INVALID")

    def test_source_pdf_header_spoof(self):
        def mutate(a):
            d=b"not a pdf"
            a[1]["a"]=d
            a[0][0].update(sha256=sha256(d),size_bytes=len(d))
            a[2]["a"]=sha256(d)
        self.source_fail(mutate,"BYTE_HASH_SIZE_OR_MAGIC_DRIFT:a")

    def test_source_wrong_modality(self):
        self.source_fail(lambda a:a[0][0].update(modality="executable"),"SOURCE_SPEC_INVALID")

    def test_source_wrong_size(self):
        self.source_fail(lambda a:a[0][0].update(size_bytes=2),"BYTE_HASH_SIZE_OR_MAGIC_DRIFT:a")

    def test_source_extra_field(self):
        self.source_fail(lambda a:a[0][0].update(approved=True),"SOURCE_SPEC_INVALID")

    def test_git_bytes_mutated(self):
        self.git_fail(lambda a:a.__setitem__(0,a[0]+b"!"),"GIT_BLOB_BYTE_HASH_DRIFT")

    def test_git_blob_pin_mismatch(self):
        self.git_fail(lambda a:a[1].update(blob_sha="f"*40),
                      "ANCHOR_NOT_BOUND_TO_INDEPENDENT_PIN")

    def test_git_sha256_pin_mismatch(self):
        self.git_fail(lambda a:a[1].update(sha256="f"*64),
                      "ANCHOR_NOT_BOUND_TO_INDEPENDENT_PIN")

    def test_git_traversal_rejected(self):
        def mutate(a):
            a[1]["path"]=a[2]["path"]="Workspaces/../LATEST.json"
        self.git_fail(mutate,"ANCHOR_PATH_OR_IDENTITY_INVALID")

    def test_git_wrong_repo_rejected(self):
        def mutate(a):
            a[1]["repository"]=a[2]["repository"]="../../outside"
        self.git_fail(mutate,"ANCHOR_PATH_OR_IDENTITY_INVALID")

    def test_git_malformed_commit_rejected(self):
        def mutate(a):
            a[1]["commit_sha"]=a[2]["commit_sha"]="bad"
        self.git_fail(mutate,"ANCHOR_PATH_OR_IDENTITY_INVALID")

    def test_git_raw_missing(self):
        self.git_fail(lambda a:a.__setitem__(0,None),"GIT_BLOB_RAW_BYTES_MISSING")

    def test_git_extra_authority_claim_rejected(self):
        self.git_fail(lambda a:a[1].update(issuer=True),"ANCHOR_SHAPE")

    def rollback(self,head="a"*40,pin="a"*40,post=b"after",postpin=None,
                 parent=b"before",parentpin=None,issuer=None):
        return rollback_preflight(head,pin,post,postpin or sha256(b"after"),
                                  parent,parentpin or sha256(b"before"),
                                  issuer_claim=issuer)

    def test_cas_good_hashes_still_no_writer(self):
        r=self.rollback()
        self.assertEqual(r["status"],"BLOCKED_NO_ROLLBACK_WRITER",r)
        self.assertTrue(r["preconditions_consistent"])
        self.assertFalse(r["rollback_authorized"])
        self.deny(r)

    def test_cas_remote_race_rejected(self):
        r=self.rollback(head="b"*40)
        self.assertIn("REMOTE_HEAD_CHANGED",r["errors"])
        self.deny(r)

    def test_cas_postimage_hash_drift(self):
        r=self.rollback(postpin="f"*64)
        self.assertIn("POSTIMAGE_BYTES_DRIFT",r["errors"])

    def test_cas_parent_hash_drift(self):
        r=self.rollback(parentpin="f"*64)
        self.assertIn("IMMUTABLE_PARENT_BYTES_DRIFT",r["errors"])

    def test_cas_parent_missing(self):
        r=self.rollback(parent=None)
        self.assertIn("POST_OR_PARENT_BYTES_MISSING",r["errors"])

    def test_cas_self_attested_issuer_rejected(self):
        r=self.rollback(issuer={"approved":True})
        self.assertIn("SELF_ATTESTED_ISSUER_IS_NOT_AUTHENTICATION",r["errors"])
        self.deny(r)

    def test_cas_no_change_rejected(self):
        r=self.rollback(post=b"before",postpin=sha256(b"before"))
        self.assertIn("SAME_PARENT_NOT_ROLLBACK",r["errors"])

    def test_local_regular_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"file.pdf";p.write_bytes(PDF1)
            self.assertEqual(read_regular_file(p),PDF1)

    def test_local_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"file.pdf";p.write_bytes(PDF1)
            q=Path(d)/"link.pdf";q.symlink_to(p)
            with self.assertRaises((OSError,ValueError)):
                read_regular_file(q)

    def test_local_empty_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"empty.pdf";p.write_bytes(b"")
            with self.assertRaises(ValueError):read_regular_file(p)

    def test_local_oversize_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"large.pdf";p.write_bytes(PDF1)
            with self.assertRaises(ValueError):
                read_regular_file(p,max_bytes=3)

if __name__=="__main__":
    unittest.main()
