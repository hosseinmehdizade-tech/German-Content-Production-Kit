"""Synthetic race-condition tests for the real central lexical Stage5 launcher.

These tests never publish cards, user releases, or accepted content.
"""
from __future__ import annotations
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Tools"))
from build_quality_gated_lexical_candidate_v1 import (
    frozen_source_proofs, require_frozen_proofs, verify_governed_build,
)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class SourceProofFreezeTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir=Path(temp.name)
        self.roles={}
        for name in ("direct-import-tsv","canonical-json",
                     "source-output-map-tsv","qa-report"):
            f=self.dir/(name+".txt")
            f.write_bytes(("signed input "+name).encode())
            self.roles[name]=f
        self.stage4=self.dir/"stage4.json"
        self.stage4.write_bytes(b'{"status":"PASS_SYNTHETIC"}')
        self.review=self.dir/"review.json"
        self.review.write_bytes(b'{"role":"cross-tile"}')
        self.router=self.dir/"canonical-route.json"
        self.router.write_bytes(b'{"owner":"synthetic"}')
        self.zip=self.dir/"stage5-candidate.zip"
        self.zip.write_bytes(b"synthetic-only-zipped-bytes")
        self.pins=self.snapshot()
        self.built={
            "status":"PASS_GOVERNED_STAGE5_FORMAT_AND_BYTE_PARITY_ONLY",
            "source_role_sha256":{k:sha(v) for k,v in self.roles.items()},
            "output_zip_sha256":sha(self.zip),
        }
        self.quality={"source_tsv_sha256":sha(self.roles["direct-import-tsv"])}
        self.family={"route_file_sha256":sha(self.router)}
    def snapshot(self):
        return frozen_source_proofs(self.roles,self.stage4,self.review,self.router)
    def verify(self):
        return verify_governed_build(self.zip,self.built,self.pins,
                                     self.quality,self.family)
    def test_exact_stable_roles_and_published_bytes_pass(self):
        require_frozen_proofs(self.pins)
        self.assertEqual(self.verify(),sha(self.zip))
    def test_stage4_mutated_after_review_rejected(self):
        self.stage4.write_bytes(b'{"status":"FORGED_AFTER_REVIEW"}')
        with self.assertRaisesRegex(ValueError,"SOURCE_OR_PROOF_CHANGED_DURING_STAGE5:stage4-receipt"):
            require_frozen_proofs(self.pins)
    def test_cross_tile_mutated_during_build_rejected(self):
        self.review.write_bytes(b'{"status":"changed-after-quality"}')
        with self.assertRaisesRegex(ValueError,"SOURCE_OR_PROOF_CHANGED_DURING_STAGE5:cross-tile-review"):
            require_frozen_proofs(self.pins)
    def test_canonical_router_mutated_during_build_rejected(self):
        self.router.write_bytes(b'{"parent":"different"}')
        with self.assertRaisesRegex(ValueError,"SOURCE_OR_PROOF_CHANGED_DURING_STAGE5:canonical-router"):
            require_frozen_proofs(self.pins)
    def test_all_four_roles_are_frozen(self):
        for name,file in self.roles.items():
            with self.subTest(role=name):
                before=file.read_bytes()
                file.write_bytes(before+b" changed")
                with self.assertRaisesRegex(ValueError,"SOURCE_OR_PROOF_CHANGED_DURING_STAGE5:"+name):
                    require_frozen_proofs(self.pins)
                file.write_bytes(before)
    def test_missing_stage4_is_refused_before_builder(self):
        self.stage4.unlink()
        with self.assertRaisesRegex(ValueError,"MISSING_OR_UNSAFE_STAGE5_PROOF_ROLE:stage4-receipt"):
            self.snapshot()
    def test_missing_output_zip_not_treated_as_published(self):
        self.zip.unlink()
        with self.assertRaisesRegex(ValueError,"GOVERNED_STAGE5_OUTPUT_NOT_REGULAR"):
            self.verify()
    def test_builder_report_with_wrong_role_digest_fails(self):
        self.built["source_role_sha256"]["qa-report"]="0"*64
        with self.assertRaisesRegex(ValueError,"GOVERNED_STAGE5_ROLE_HASH_MISMATCH"):
            self.verify()
    def test_builder_report_with_wrong_zip_digest_fails(self):
        self.built["output_zip_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"GOVERNED_STAGE5_OUTPUT_BYTES_MISMATCH"):
            self.verify()
    def test_build_returning_no_status_cannot_claim_stage5(self):
        self.built["status"]="DRAFT"
        with self.assertRaisesRegex(ValueError,"GOVERNED_FORMAT_BUILD_NOT_PASS"):
            self.verify()
    def test_quality_gate_source_not_exact_snapshot_fails(self):
        self.quality["source_tsv_sha256"]="c"*64
        with self.assertRaisesRegex(ValueError,"QUALITY_GATE_TSV_NOT_FROZEN_SOURCE"):
            self.verify()
    def test_family_authority_route_not_exact_snapshot_fails(self):
        self.family["route_file_sha256"]="a"*64
        with self.assertRaisesRegex(ValueError,"FAMILY_ROUTER_CHANGED_BEFORE_BUILD"):
            self.verify()
    def test_no_input_symlinks_as_release_proofs(self):
        alias=self.dir/"proof-link.json"
        try:
            alias.symlink_to(self.stage4)
        except (OSError,NotImplementedError) as e:
            self.skipTest("Symlink creation unavailable on this OS: "+str(e))
        with self.assertRaisesRegex(ValueError,"MISSING_OR_UNSAFE_STAGE5_PROOF_ROLE:stage4-receipt"):
            frozen_source_proofs(self.roles,alias,self.review,self.router)

if __name__=="__main__":
    unittest.main()
