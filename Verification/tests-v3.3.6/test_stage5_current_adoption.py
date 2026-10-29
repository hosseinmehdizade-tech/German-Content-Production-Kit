"""Synthetic nonactive root consistency and rollback tests; no Git network/real cards."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plan_stage5_current_adoption import (sha,git_blob,verify_readonly,plan_recovery,
  CHECKPOINT_SCHEMA,SIDECAR_SCHEMA,REPO)

def js(o):
    return json.dumps(o,sort_keys=True,ensure_ascii=False).encode("utf-8")

def fixture():
    ws="synthetic-stage5-op02"
    source=sha(b"original synthetic source")
    parent=sha(b"immutable synthetic parent")
    current=sha(b"synthetic current tsv")
    side={
        "schema":SIDECAR_SCHEMA,"status":"NONACTIVE_EXTERNAL_PIN",
        "lock_state":"EDITABLE_CURRENT",
        "workstream_id":ws,"artifact_id":"synthetic-001",
        "registered_source_sha256":source,"parent_artifact_sha256":parent,
        "roles": {name:{"filename":filename,"sha256":current if name=="direct-import-tsv" else sha(name.encode()),"size":2}
                for name,filename in {
                  "direct-import-tsv":"Synthetic-Universal.tsv",
                  "canonical-json":"Synthetic-canonical.json",
                  "source-output-map-tsv":"Synthetic-source-output-map.tsv",
                  "qa-report":"Synthetic-QA.json"}.items()}
    }
    checkpoint={
        "schema":CHECKPOINT_SCHEMA,"lock_state":"EDITABLE_CURRENT",
        "activation_state":"NONACTIVE_ONLY",
        "workstream_id":ws,"artifact_id":"synthetic-001",
        "registered_source_sha256":source,"parent_artifact_sha256":parent,
        "current_tsv_sha256":current,"authority_sidecar_sha256":sha(js(side))
    }
    checkpoint_bytes=js(checkpoint)
    anchor={k:checkpoint[k] for k in (
        "workstream_id","artifact_id","registered_source_sha256",
        "parent_artifact_sha256","current_tsv_sha256","authority_sidecar_sha256")}
    anchor.update(repository=REPO,commit_sha="a"*40,
                  checkpoint_path=f"Workspaces/{ws}/LATEST.json",
                  checkpoint_blob_sha=git_blob(checkpoint_bytes),
                  checkpoint_sha256=sha(checkpoint_bytes))
    rb={"repository":REPO,"commit_sha":anchor["commit_sha"],"path":anchor["checkpoint_path"],
        "blob_sha":anchor["checkpoint_blob_sha"]}
    scopes={"status":"DENY_ALL_PENDING_EXPLICIT_SCOPE_APPROVAL","scopes":[]}
    return anchor,rb,checkpoint_bytes,js(side),scopes

def audit(f):
    return verify_readonly(*f)

def test_exact_synthetic_normalized_root_consistency_pass():
    r=audit(fixture());assert r["status"]=="PASS_NONACTIVE_PIN_CONSISTENCY_ONLY"
    assert r["production_approved"] is False and r["real_latest_resolved"] is False

@pytest.mark.parametrize("part", ["commit_sha","path","blob_sha","repository"])
def test_wrong_authenticated_readback_blocks(part):
    f=list(fixture());f[1][part]="b"*40 if "sha" in part else "other"
    assert "GIT_READBACK_IDENTITY_MISMATCH" in audit(f)["errors"]

def test_wrong_checkpoint_bytes_blocks():
    f=list(fixture());f[2]=f[2]+b" "
    assert "CHECKPOINT_EXACT_BYTES_MISMATCH" in audit(f)["errors"]

def test_wrong_git_blob_even_correct_sha256_blocks():
    f=list(fixture());f[0]["checkpoint_blob_sha"]="b"*40
    assert "CHECKPOINT_EXACT_BYTES_MISMATCH" in audit(f)["errors"]

def test_wrong_scoped_latest_path_blocks():
    f=list(fixture());f[0]["checkpoint_path"]="Workspaces/other/LATEST.json"
    assert "UNSUPPORTED_NATIVE_LATEST_PATH_OR_SCOPE" in audit(f)["errors"]

@pytest.mark.parametrize("key", ["registered_source_sha256","parent_artifact_sha256","current_tsv_sha256","authority_sidecar_sha256"])
def test_forged_external_current_anchor_blocks(key):
    f=list(fixture());f[0][key]=sha(b"forged")
    assert "CHECKPOINT_ANCHOR_DRIFT:"+key in audit(f)["errors"]

def test_sidecar_changed_without_independent_pin_blocks():
    f=list(fixture());f[3]=f[3]+b" "
    assert "SIDECAR_EXACT_BYTES_MISMATCH" in audit(f)["errors"]

def test_lock_state_blocks_even_with_rehashed_checkpoint():
    f=list(fixture());cp=json.loads(f[2]);cp["lock_state"]="LOCKED";f[2]=js(cp)
    f[0]["checkpoint_sha256"]=sha(f[2]);f[0]["checkpoint_blob_sha"]=git_blob(f[2])
    f[1]["blob_sha"]=f[0]["checkpoint_blob_sha"]
    assert "LOCKED_OR_ACTIVATION_STATE_INVALID" in audit(f)["errors"]

def test_writer_scope_activation_never_authorized():
    f=list(fixture());f[4]["status"]="APPROVED";f[4]["scopes"]=[{"path":"workspaces/other.tsv"}]
    assert "WRITER_AUTHORIZATION_NOT_DENY_ALL" in audit(f)["errors"]

@pytest.mark.parametrize("duplicate", ["top","nested"])
def test_duplicate_json_rejected(duplicate):
    f=list(fixture())
    if duplicate=="top":
        f[2]=f[2].replace(b'"schema":',b'"schema":"forged","schema":',1)
    else:
        f[3]=f[3].replace(b'"lock_state":',b'"lock_state":"LOCKED","lock_state":',1)
    assert "STRICT_JSON_OR_BYTES_INVALID" in audit(f)["errors"] or "CHECKPOINT_EXACT_BYTES_MISMATCH" in audit(f)["errors"]

def test_no_write_never_rolls_back():
    r=plan_recovery(write_occurred=False,pinned_preimage_sha="a"*40,
       expected_written_sha="b"*40,observed_remote_sha="a"*40,
       immutable_parent_sha256=sha(b"parent"),verified_parent_sha256=sha(b"parent"))
    assert r["status"]=="ABORT_CANDIDATE_KEEP_CURRENT"

def test_postwrite_equal_allows_only_manual_cas_plan():
    r=plan_recovery(write_occurred=True,pinned_preimage_sha="a"*40,
       expected_written_sha="b"*40,observed_remote_sha="b"*40,
       immutable_parent_sha256=sha(b"parent"),verified_parent_sha256=sha(b"parent"))
    assert r["status"]=="MANUAL_CAS_RECOVERY_ELIGIBILITY_ONLY" and not r["performed_write"]

def test_postwrite_drift_never_forces_overwrite():
    r=plan_recovery(write_occurred=True,pinned_preimage_sha="a"*40,
       expected_written_sha="b"*40,observed_remote_sha="c"*40,
       immutable_parent_sha256=sha(b"parent"),verified_parent_sha256=sha(b"parent"))
    assert r["status"]=="BLOCKED" and r["reason"]=="POSTWRITE_REMOTE_CAS_DRIFT"

def test_unverified_immutable_parent_blocks_recovery():
    r=plan_recovery(write_occurred=True,pinned_preimage_sha="a"*40,
       expected_written_sha="b"*40,observed_remote_sha="b"*40,
       immutable_parent_sha256=sha(b"parent"),verified_parent_sha256=sha(b"wrong"))
    assert r["status"]=="BLOCKED" and r["reason"]=="PARENT_RECOVERY_NOT_VERIFIED"
