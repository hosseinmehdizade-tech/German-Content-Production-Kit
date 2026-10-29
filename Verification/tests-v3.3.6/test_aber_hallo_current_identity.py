"""OP-02 actual native Aber Hallo tracked metadata read-only plus hostile mutations."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import pytest
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from audit_aber_hallo_current_identity import verify,ROOT,LATEST,SOURCES

def original():
    latest=(ROOT/LATEST).read_bytes()
    j=json.loads(latest)
    receipt=j["latest_receipt_path"]
    return [latest,(ROOT/receipt).read_bytes(),(ROOT/SOURCES).read_bytes(),receipt]

def update(index,fn):
    f=original()
    j=json.loads(f[index])
    fn(j)
    f[index]=json.dumps(j,ensure_ascii=False).encode("utf-8")
    return f

def evaluate(f):
    return verify(f[0],f[1],f[2],receipt_relative_path=f[3])

def test_real_tracked_latest_receipt_source_metadata_consistent_without_production_approval():
    result=evaluate(original())
    assert result["status"]=="PASS_SCOPED_NATIVE_METADATA_CONSISTENCY_ONLY",result
    assert result["production_stage5_allowed"] is False
    assert result["real_current_issuer_authenticated"] is False
    assert result["source_pdf_or_portable_bytes_verified"] is False

@pytest.mark.parametrize("key",["zip","canonical","import"])
def test_mutated_receipt_artifact_hash_blocks(key):
    f=update(1,lambda r:r["artifacts"][key].update(sha256="f"*64))
    assert "ARTIFACT_IDENTITY_DRIFT:"+key+":sha256" in evaluate(f)["errors"]

@pytest.mark.parametrize("key",["zip","canonical","import"])
def test_mutated_receipt_drive_identity_blocks(key):
    f=update(1,lambda r:r["artifacts"][key].update(drive_id="different"))
    assert "ARTIFACT_IDENTITY_DRIFT:"+key+":drive_id" in evaluate(f)["errors"]

@pytest.mark.parametrize("key",["canonical","import"])
def test_mutated_current_master_bridge_blocks(key):
    f=update(0,lambda r:r["authority"]["current_portable"].update({key+"_sha256":"f"*64}))
    assert "NATIVE_CURRENT_MASTER_DRIFT:"+key in evaluate(f)["errors"]

def test_stale_receipt_path_blocks():
    f=original();f[3]="Workspaces/aber-hallo-listen-tabellen/stale.json"
    assert "LATEST_RECEIPT_PATH_DRIFT" in evaluate(f)["errors"]

def test_latest_wrong_workstream_blocks():
    f=update(0,lambda r:r.update(workstream="other"))
    assert "LATEST_WRONG_SCHEMA_OR_WORKSTREAM" in evaluate(f)["errors"]

def test_source_manifest_identity_blocks():
    f=update(2,lambda r:r["source_set"][0].update(sha256="bad"))
    assert "SOURCE_MANIFEST_SET_INVALID" in evaluate(f)["errors"]

def test_stage4_unapproved_gate_never_promotes():
    f=update(0,lambda r:r["authority"]["current_portable"].update(stage4="PASS"))
    assert "STAGE4_OR_STAGE5_BOUNDARY_UNEXPECTED" in evaluate(f)["errors"]

def test_stage5_unauthorized_claim_blocks():
    f=update(1,lambda r:r["verification"].update(stage5="PASS"))
    assert "STAGE4_OR_STAGE5_BOUNDARY_UNEXPECTED" in evaluate(f)["errors"]

def test_receipt_wrong_scope_claim_blocks():
    f=update(1,lambda r:r["milestone"].update(quality="PASS_GLOBAL_STAGE4"))
    assert "RECEIPT_SCOPED_QUALITY_BOUNDARY_UNEXPECTED" in evaluate(f)["errors"]

def test_nested_json_duplicate_key_rejected():
    f=original()
    f[2]=f[2].replace(b'"schema":',b'"schema":"forged","schema":',1)
    assert "UNTRUSTED_JSON_OR_DUPLICATE_KEYS" in evaluate(f)["errors"]

def test_malformed_source_manifest_blocks():
    f=original();f[2]=b"[]"
    assert "DOCUMENT_NOT_AN_OBJECT" in evaluate(f)["errors"]
