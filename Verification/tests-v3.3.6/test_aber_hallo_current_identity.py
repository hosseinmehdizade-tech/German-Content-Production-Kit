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

def current_wip52():
    """FROZEN HISTORICAL synthetic reconstruction using real WIP52 receipt.

    WIP52 is NOT CURRENT. Never substitute its portable for the live LATEST.
    This fixture preserves prior WIP52 schema negative tests across later WIPs.
    """
    live = json.loads((ROOT / LATEST).read_bytes())
    path = ("Workspaces/aber-hallo-listen-tabellen/"
            "48-wip52-evidence-bounded-rektion/"
            "WIP52-15-EXACT-DUDEN-397-HOLDS-2026-10-30.json")
    receipt_bytes = (ROOT / path).read_bytes()
    receipt = json.loads(receipt_bytes)
    p, counts = receipt["portable"], receipt["counts"]
    current = {**p, "stage4": "OPEN",
               "canonical_sha256": "b" * 64,
               "import_sha256": "c" * 64}
    latest = {
        "schema": "gcpk-workstream-latest@1.0.0",
        "workstream": "aber-hallo-listen-tabellen",
        "status": "CURRENT_WIP52_STAGE4_OPEN_HISTORICAL_ONLY",
        "latest_milestone": "WIP52_15_HISTORICAL_SCOPED_DUDEN",
        "latest_receipt_path": path,
        "latest_receipt_commit_sha": "a" * 40,  # synthetic, NOT Git-authorized
        "authority": {"current_portable": current},
        "complete_working_content_package": {
            "name": p["filename"], "sha256": p["sha256"],
            "bytes": p["size_bytes"], "library_path": p["library_path"],
            "library_file_id": p["library_file_id"],
            "stage4": "OPEN", "stage5_6_7": "NOT_RUN",
            "source_parent_wip51_sha256": receipt["parent"]["sha256"],
        },
        "wip52_evidence_bounded_rektion": live["wip52_evidence_bounded_rektion"],
        "progress": {
            "wip52_new_exact_duden": counts["new_exact_duden_confirmed"],
            "rektion_external_attested_total": counts["cumulative_external_confirmed"],
            "rektion_evidence_holds": counts["remaining_external_holds"],
            "pending_independent_expert_stage4": True,
            "independent_expert_unreviewed_units": 788,
        },
    }
    return [json.dumps(latest, ensure_ascii=False).encode("utf-8"),
            receipt_bytes, (ROOT / SOURCES).read_bytes(), path]


def current_direct_duden():
    """WIP56 HISTORICAL fixture reconstructed from its tracked receipt.

    Preserves full adversarial direct-Duden schema coverage after WIP57+ moves
    CURRENT. Synthetic LATEST is not issuer authorization or content CURRENT.
    """
    live = json.loads((ROOT / LATEST).read_bytes())
    path = ("Workspaces/aber-hallo-listen-tabellen/52-wip56-direct-duden/"
            "WIP56-16-DIRECT-DUDEN-664-ATTESTED-317-HOLDS-2026-10-30.json")
    receipt_bytes = (ROOT / path).read_bytes()
    rec = json.loads(receipt_bytes)
    port = rec["portable"]
    counts = rec["counts"]
    latest = {
        "schema": "gcpk-workstream-latest@1.0.0",
        "workstream": "aber-hallo-listen-tabellen",
        "status": "CURRENT_WIP56_SYNTHETIC_HISTORICAL_ONLY",
        "latest_milestone": "WIP56_16_DIRECT_DUDEN_LEMMA_CASE_SENSE_CONFIRMATIONS_APPLIED_317_ACTIVE_HOLDS",
        "latest_receipt_path": path,
        "latest_receipt_commit_sha": "a" * 40,
        "authority": {"current_portable": {**port, "stage4": "OPEN"}},
        "complete_working_content_package": {
            "name": port["filename"], "sha256": port["sha256"],
            "bytes": port["size_bytes"],
            "member_count": rec["validation"]["zip_members"],
            "library_file_id": port["library_file_id"],
            "library_path": port["library_path"],
            "stage4": "OPEN", "stage5_6_7": "NOT_RUN",
            "parent_sha256": rec["parent"]["sha256"],
        },
        "previous_wip56_source_current": live["previous_wip56_source_current"],
        "progress": {
            "rektion_independent_external_attested_cumulative": counts["cumulative_external_attested"],
            "rektion_external_holds_remaining": counts["remaining_external_holds"],
            "rektion_wip56_new_duden": counts["new_duden_exact"],
            "pending_independent_expert_stage4": True,
            "independent_expert_unreviewed_units": 788,
        },
    }
    return [json.dumps(latest, ensure_ascii=False).encode("utf-8"),
            receipt_bytes, (ROOT / SOURCES).read_bytes(), path]


def real_current():
    """Read current tracked LATEST+receipt. Changes independently with the producer."""
    raw = (ROOT / LATEST).read_bytes()
    path = json.loads(raw)["latest_receipt_path"]
    return [raw, (ROOT / path).read_bytes(), (ROOT / SOURCES).read_bytes(), path]


def current_live():
    """Historical WIP57-only fixture; NEVER resolve it as production CURRENT."""
    live = json.loads((ROOT / LATEST).read_bytes())
    prior = live["previous_wip58_source_current"]
    port = prior["portable"]
    receipt_path = prior["receipt"]
    receipt = json.loads((ROOT / receipt_path).read_bytes())
    simulated = {
        "schema": "gcpk-workstream-latest@1.0.0",
        "workstream": "aber-hallo-listen-tabellen",
        "status": "HISTORICAL_WIP57_SIMULATED_ONLY_STAGE4_OPEN",
        "latest_milestone": prior["latest_milestone"],
        "latest_receipt_path": receipt_path,
        "latest_receipt_commit_sha": "a"*40,
        "authority": {"current_portable": port},
        "complete_working_content_package": {
            "name": port["filename"], "sha256": port["sha256"],
            "bytes": port["size_bytes"], "member_count": receipt["zip_members"],
            "library_file_id": port["library_file_id"], "library_path": port["library_path"],
            "stage4": "OPEN", "stage5_6_7": "NOT_RUN",
            "parent_sha256": receipt["parent_sha256"],
        },
        "previous_wip57_source_current": live["previous_wip57_source_current"],
        "progress": {
            "rektion_independent_external_attested_cumulative": receipt["cumulative_attested"],
            "rektion_external_holds_remaining": receipt["hold_count"],
            "pending_independent_expert_stage4": True,
            "independent_expert_unreviewed_units": 788,
        },
    }
    return [json.dumps(simulated, ensure_ascii=False).encode(),
            (ROOT / receipt_path).read_bytes(),
            (ROOT / SOURCES).read_bytes(), receipt_path]


def original():
    """Frozen WIP50 shape using tracked historical identity, NOT live CURRENT."""
    live = json.loads((ROOT / LATEST).read_bytes())
    old = live["previous_wip52_source_current"]
    prior = old["current_portable"]
    latest = {
        "schema": "gcpk-workstream-latest@1.0.0",
        "workstream": "aber-hallo-listen-tabellen",
        "latest_milestone": old["latest_milestone"],
        "latest_receipt_path": old["receipt"],
        "latest_receipt_commit_sha": "a" * 40,  # synthetic only
        "authority": {"current_portable": prior},
        "wip50_master_files": live["wip50_master_files"],
    }
    artifacts = {
        "zip": {**{key: prior[key] for key in ("filename", "sha256", "drive_id")},
                "bytes": 1},
    }
    for key in ("canonical", "import"):
        data = live["wip50_master_files"][key]
        artifacts[key] = {**{field: data[field] for field in
                            ("filename", "sha256", "drive_id")}, "bytes": 1}
    receipt = {
        "schema": "flashcards-work-outcome-receipt@1.0.0",
        "workstream": "aber-hallo-listen-tabellen",
        "artifacts": artifacts,
        "verification": {"stage5": "NOT_RUN"},
        "milestone": {"state": "IN_PROGRESS", "quality": "PASS_SCOPED_ONLY_NOT_GLOBAL_STAGE4"},
    }
    encoded = lambda obj: json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return [encoded(latest), encoded(receipt), (ROOT / SOURCES).read_bytes(),
            old["receipt"]]

def update(index,fn):
    f=original()
    j=json.loads(f[index])
    fn(j)
    f[index]=json.dumps(j,ensure_ascii=False).encode("utf-8")
    return f

def evaluate(f):
    return verify(f[0],f[1],f[2],receipt_relative_path=f[3])

def test_historical_wip50_synthetic_receipt_schema_remains_covered_not_current():
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


def test_real_tracked_wip52_current_receipt_is_scoped_only():
    result = evaluate(current_wip52())
    assert result["status"] == "PASS_SCOPED_NATIVE_METADATA_CONSISTENCY_ONLY", result
    assert result["evaluated_contract"] == "WIP52_CURRENT_TRACKED_METADATA_ONLY"
    assert result["historical_wip50_not_current"] is True
    for key in ("production_stage5_allowed", "real_current_issuer_authenticated",
                "stage4_independent_semantic_review_completed",
                "source_pdf_or_portable_bytes_verified"):
        assert result[key] is False, key


def change_wip52(index, fn):
    files = current_wip52()
    doc = json.loads(files[index])
    fn(doc)
    files[index] = json.dumps(doc, ensure_ascii=False).encode("utf-8")
    return files


def test_wip50_receipt_cannot_be_replayed_as_current_wip52():
    files = original()
    current = json.loads(current_wip52()[0])
    files[0] = json.dumps(current, ensure_ascii=False).encode("utf-8")
    files[3] = current["latest_receipt_path"]
    assert "HISTORICAL_WIP50_RECEIPT_CANNOT_CERTIFY_NEWER_CURRENT" in evaluate(files)["errors"]


@pytest.mark.parametrize("key", ["sha256", "filename", "library_file_id", "size_bytes"])
def test_wip52_portable_receipt_identity_tamper_blocks(key):
    def tamper(doc):
        doc["portable"][key] = "f" * 64 if key == "sha256" else 999 if key == "size_bytes" else "forged"
    f = change_wip52(1, tamper)
    assert "WIP52_PORTABLE_RECEIPT_DRIFT:" + key in evaluate(f)["errors"]


@pytest.mark.parametrize("key", ["sha256", "name", "bytes"])
def test_wip52_complete_working_content_package_drift_blocks(key):
    f = change_wip52(0, lambda d: d["complete_working_content_package"].update(
        {key: "f" * 64 if key == "sha256" else "forged" if key == "name" else 7}))
    field = {"sha256": "sha256", "name": "filename", "bytes": "size_bytes"}[key]
    assert "WIP52_CURRENT_PACKAGE_DRIFT:" + field in evaluate(f)["errors"]


@pytest.mark.parametrize("key", ["canonical_sha256", "import_sha256"])
def test_wip52_invalid_internal_master_hash_blocks(key):
    f = change_wip52(0, lambda d: d["authority"]["current_portable"].update({key: "bad"}))
    assert "WIP52_INTERNAL_MASTER_HASH_UNVERIFIED:" + key in evaluate(f)["errors"]


def test_wip52_receipt_path_drift_blocks():
    f = current_wip52()
    f[3] = "Workspaces/aber-hallo-listen-tabellen/stale.json"
    assert "LATEST_RECEIPT_PATH_DRIFT" in evaluate(f)["errors"]


def test_wip52_wrong_scope_receipt_blocks():
    f = change_wip52(1, lambda d: d.update(scope="OTHER_WORKSTREAM"))
    assert "WIP52_RECEIPT_IDENTITY_UNEXPECTED" in evaluate(f)["errors"]


def test_wip52_stage4_claim_must_remain_open():
    f = change_wip52(0, lambda d: d["authority"]["current_portable"].update(stage4="PASS"))
    assert "WIP52_STAGE4_7_BOUNDARY_UNEXPECTED" in evaluate(f)["errors"]


def test_wip52_receipt_scope_false_final_blocks():
    f = change_wip52(1, lambda d: d["validation"].update(no_formal_stage4_claim=False))
    assert "WIP52_SCOPED_NOT_STAGE4_BOUNDARY_MISSING" in evaluate(f)["errors"]


def test_wip52_fake_stage7_completion_blocks():
    f = change_wip52(0, lambda d: d["complete_working_content_package"].update(stage5_6_7="PASS"))
    assert "WIP52_STAGE4_7_BOUNDARY_UNEXPECTED" in evaluate(f)["errors"]


@pytest.mark.parametrize("key", ["remaining_external_holds", "cumulative_external_confirmed"])
def test_wip52_counter_drift_blocks(key):
    f = change_wip52(1, lambda d: d["counts"].update({key: 1234}))
    assert "WIP52_SCOPE_COUNTER_DRIFT" in " ".join(evaluate(f)["errors"])


def test_wip52_ledger_disposition_accounting_tamper_blocks():
    f = change_wip52(0, lambda d: d["wip52_evidence_bounded_rektion"].update(holds_legacy=319))
    assert "WIP52_HOLDS_DISPOSITION_ACCOUNTING_INVALID" in evaluate(f)["errors"]


def test_wip52_cumulative_rektion_accounting_invalid_blocks():
    f = change_wip52(0, lambda d: d["wip52_evidence_bounded_rektion"].update(confirmed_cumulative=588))
    assert "WIP52_REKTION_TOTAL_ACCOUNTING_INVALID" in evaluate(f)["errors"]


def test_wip52_ledger_parent_sha_mismatch_blocks():
    f = change_wip52(1, lambda d: d["parent"].update(sha256="f"*64))
    assert "WIP52_PARENT_REFERENCE_DRIFT" in evaluate(f)["errors"]


def test_wip52_missing_source_set_blocks():
    f = change_wip52(2, lambda d: d.update(source_set=[]))
    assert "SOURCE_MANIFEST_SET_INVALID" in evaluate(f)["errors"]


def test_wip52_unauthorized_latest_workstream_name_blocks():
    f = change_wip52(0, lambda d: d.update(workstream="other"))
    assert "LATEST_WRONG_SCHEMA_OR_WORKSTREAM" in evaluate(f)["errors"]


def test_wip52_untrusted_duplicate_receipt_schema_key_blocks():
    f = current_wip52()
    f[1] = f[1].replace(b'"schema":', b'"schema":"fake","schema":', 1)
    assert "UNTRUSTED_JSON_OR_DUPLICATE_KEYS" in evaluate(f)["errors"]


def test_future_unsupported_receipt_schema_must_block_rather_than_coerce_wip50():
    f = change_wip52(1, lambda d: d.update(schema="gcpk-aber-hallo-wip53-milestone@1.0.0"))
    assert "UNSUPPORTED_OR_FUTURE_RECEIPT_SCHEMA" in evaluate(f)["errors"]



def test_current_live_direct_duden_schema_parity_not_semantics():
    r = evaluate(current_live())
    assert r["status"] == "PASS_SCOPED_NATIVE_METADATA_CONSISTENCY_ONLY", r
    assert r["evaluated_contract"] == "REKTION_FLAT_SCOPED_TRACKED_METADATA_ONLY"
    assert r["historical_wip52_not_current"] is True
    for flag in ("production_stage5_allowed", "stage4_independent_semantic_review_completed",
                 "source_pdf_or_portable_bytes_verified", "real_current_issuer_authenticated"):
        assert r[flag] is False


def modify_current(index, fn):
    files = current_direct_duden()
    obj = json.loads(files[index])
    fn(obj)
    files[index] = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return files


@pytest.mark.parametrize("field", [
    "filename", "sha256", "size_bytes", "library_file_id",
    "library_path", "canonical_sha256", "import_sha256",
])
def test_direct_duden_portable_receipt_tamper_blocks(field):
    r = modify_current(1, lambda obj: obj["portable"].update({
        field: "f" * 64 if "sha256" in field else -99 if field == "size_bytes" else "forged"}))
    assert ("DIRECT_DUDEN_CURRENT_RECEIPT_DRIFT:" + field) in evaluate(r)["errors"]


@pytest.mark.parametrize("field", [
    ("name", "filename"), ("sha256", "sha256"), ("bytes", "size_bytes"),
    ("library_file_id", "library_file_id"),
])
def test_direct_duden_package_role_tamper_blocks(field):
    left, right = field
    r = modify_current(0, lambda obj: obj["complete_working_content_package"].update(
        {left: -1 if left == "bytes" else "f" * 64}))
    assert ("DIRECT_DUDEN_CURRENT_PACKAGE_DRIFT:" + right) in evaluate(r)["errors"]


def test_direct_duden_parent_sha_drift_rejected():
    r = modify_current(1, lambda obj: obj["parent"].update(sha256="f" * 64))
    assert "DIRECT_DUDEN_PARENT_SHA_DRIFT" in evaluate(r)["errors"]


def test_direct_duden_previous_current_parent_drift_rejected():
    live = json.loads(current_direct_duden()[0])
    match = __import__("re").match(r"WIP([0-9]+)_", live["latest_milestone"])
    key = f"previous_wip{match.group(1)}_source_current"
    r = modify_current(0, lambda obj: obj[key]["portable"].update(sha256="f" * 64))
    assert "DIRECT_DUDEN_PREVIOUS_CURRENT_LINEAGE_DRIFT" in evaluate(r)["errors"]


def test_direct_duden_receipt_path_mismatch_rejected():
    r = current_direct_duden()
    r[3] = "Workspaces/aber-hallo-listen-tabellen/old-stale.json"
    assert "LATEST_RECEIPT_PATH_DRIFT" in evaluate(r)["errors"]


def test_direct_duden_wrong_new_schema_rejected_without_downgrade():
    r = modify_current(1, lambda obj: obj.update(
        schema="gcpk-aber-hallo-unrecognized-checkpoint@1.0.0"))
    assert "UNSUPPORTED_OR_FUTURE_RECEIPT_SCHEMA" in evaluate(r)["errors"]


@pytest.mark.parametrize("field", ["remaining_external_holds", "governed_patterns",
                                    "non_governed_optional_adjuncts"])
def test_direct_duden_rektion_conservation_tamper_blocks(field):
    r = modify_current(1, lambda obj: obj["counts"].update({field: 999}))
    errors = evaluate(r)["errors"]
    assert any("DIRECT_DUDEN_GOVERNED_PATTERN_TOTAL_INVALID" in e
               or "DIRECT_DUDEN_ORIGINAL_UNIVERSE_TOTAL_INVALID" in e for e in errors)


def test_direct_duden_progress_attestation_drift_rejected():
    r = modify_current(0, lambda obj: obj["progress"].update(
        rektion_independent_external_attested_cumulative=111))
    assert "DIRECT_DUDEN_PROGRESS_COUNTER_DRIFT" in evaluate(r)["errors"]


def test_direct_duden_open_stage4_downgrade_blocked():
    r = modify_current(0, lambda obj: obj["authority"]["current_portable"].update(
        stage4="VERIFIED"))
    assert "DIRECT_DUDEN_STAGE4_7_BOUNDARY_UNEXPECTED" in evaluate(r)["errors"]


def test_direct_duden_false_stage5_release_blocked():
    r = modify_current(1, lambda obj: obj["validation"].update(
        stages_5_6_7="PASS"))
    assert "DIRECT_DUDEN_SCOPE_VALIDATION_DRIFT:stages_5_6_7" in evaluate(r)["errors"]


def test_direct_duden_pdf_immutability_claim_must_be_present():
    r = modify_current(1, lambda obj: obj["validation"].update(
        original_source_PDFs="REPLACED"))
    assert "DIRECT_DUDEN_SCOPE_VALIDATION_DRIFT:original_source_PDFs" in evaluate(r)["errors"]


def test_direct_duden_zip_member_count_mismatch_rejected():
    r = modify_current(1, lambda obj: obj["validation"].update(zip_members=1))
    assert "DIRECT_DUDEN_ZIP_MEMBER_COUNT_DRIFT" in evaluate(r)["errors"]


def test_direct_duden_reviewer_stage4_must_remain_open():
    r = modify_current(0, lambda obj: obj["progress"].update(
        independent_expert_unreviewed_units=0))
    assert "DIRECT_DUDEN_INDEPENDENT_REVIEW_OPEN_NOT_PROVEN" in evaluate(r)["errors"]


def test_direct_duden_source_manifest_hash_mutation_detected():
    r = modify_current(2, lambda obj: obj["source_set"][0].update(sha256="bad"))
    assert "SOURCE_MANIFEST_SET_INVALID" in evaluate(r)["errors"]


def test_direct_duden_duplicate_json_keys_fail_closed():
    r = current_direct_duden()
    r[1] = r[1].replace(b'"schema":', b'"schema":"fake","schema":', 1)
    assert "UNTRUSTED_JSON_OR_DUPLICATE_KEYS" in evaluate(r)["errors"]


def test_direct_duden_malformed_validation_does_not_throw():
    r = modify_current(1, lambda obj: obj.update(validation=[]))
    assert evaluate(r)["status"] == "BLOCKED"


def test_direct_duden_malformed_source_id_does_not_throw():
    r = modify_current(2, lambda obj: obj["source_set"][0].update(source_id=[]))
    assert "SOURCE_MANIFEST_SET_INVALID" in evaluate(r)["errors"]


def test_direct_duden_label_disagrees_with_portable_version():
    r = modify_current(0, lambda obj: obj.update(
        latest_milestone="WIP57_FUTURE_SYNTHETIC_NONCURRENT"))
    assert "DIRECT_DUDEN_MILESTONE_PORTABLE_VERSION_DRIFT" in evaluate(r)["errors"]


def test_wip52_receipt_cannot_replay_as_wip56_current():
    r = current_direct_duden()
    past = current_wip52()
    r[1] = past[1]
    result = evaluate(r)
    assert result["status"] == "BLOCKED"
    assert any("WIP52" in error for error in result["errors"])



def mutate_flat(index, fn):
    f = current_live()
    doc = json.loads(f[index])
    fn(doc)
    f[index] = json.dumps(doc, ensure_ascii=False).encode("utf-8")
    return f


@pytest.mark.parametrize("key", ["zip","zip_sha256","size_bytes","library_file_id",
                                    "library_path","canonical_sha256","import_sha256"])
def test_flat_current_receipt_artifact_tamper_blocks(key):
    f = mutate_flat(1, lambda d: d.update({
        key: "f"*64 if key.endswith("sha256") else -1 if key=="size_bytes" else "forged"}))
    field = {"zip": "filename", "zip_sha256": "sha256"}.get(key,key)
    assert "REKTION_RECEIPT_PORTABLE_DRIFT:" + field in evaluate(f)["errors"]


@pytest.mark.parametrize("key", ["sha256","bytes","parent_sha256"])
def test_flat_current_package_tamper_blocks(key):
    f = mutate_flat(0, lambda d: d["complete_working_content_package"].update({
        key: -1 if key=="bytes" else "f"*64}))
    assert evaluate(f)["status"] == "BLOCKED"


@pytest.mark.parametrize("field", ["hold_count","cumulative_attested",
                                    "original_governed_count","non_governed_reclassified"])
def test_flat_rektion_conservation_invalid_tamper_blocks(field):
    f = mutate_flat(1, lambda d: d.update({field: 123456}))
    assert any(e.startswith("REKTION_GOVERNED_TOTAL_NOT_CONSERVED") or
               e.startswith("REKTION_984_ORIGINAL_PATTERNS_NOT_CONSERVED")
               for e in evaluate(f)["errors"])


def test_flat_current_parent_lineage_uses_resolved_wip_version():
    live = json.loads(current_live()[0])
    import re
    match = re.match(r"^WIP([0-9]{2,4})_", live["latest_milestone"])
    assert match is not None
    key = f"previous_wip{match.group(1)}_source_current"
    f = mutate_flat(0, lambda d: d[key]["portable"].update(sha256="f"*64))
    assert "REKTION_PARENT_LINEAGE_INVALID" in evaluate(f)["errors"]


def test_flat_real_wip57_receipt_path_not_source_authority():
    f = current_live()
    f[3] = "Workspaces/aber-hallo-listen-tabellen/stale.json"
    assert "LATEST_RECEIPT_PATH_DRIFT" in evaluate(f)["errors"]


def test_flat_stage4_must_stay_open_in_current_receipt():
    f = mutate_flat(1, lambda d: d.update(full_stage4="PASS"))
    assert "REKTION_SCOPE_BOUNDARY_INVALID:full_stage4" in evaluate(f)["errors"]


def test_flat_stage5_7_must_remain_not_run():
    f = mutate_flat(1, lambda d: d.update(stage5_6_7="PASS"))
    assert "REKTION_SCOPE_BOUNDARY_INVALID:stage5_6_7" in evaluate(f)["errors"]


def test_flat_pdf_source_immutability_metadata_must_hold():
    f = mutate_flat(1, lambda d: d.update(source_pdfs="REPLACED"))
    assert "REKTION_SCOPE_BOUNDARY_INVALID:source_pdfs" in evaluate(f)["errors"]


def test_flat_malformed_boolean_counter_never_counts_as_integer():
    f = mutate_flat(1, lambda d: d.update(hold_count=True))
    assert "REKTION_INTEGER_COUNTERS_INVALID" in evaluate(f)["errors"]


def test_flat_bad_source_manifest_identity_fails():
    f = mutate_flat(2, lambda d: d["source_set"][0].update(sha256="not-a-hash"))
    assert "SOURCE_MANIFEST_SET_INVALID" in evaluate(f)["errors"]


def test_flat_malformed_duplicate_json_key_fails():
    f = current_live()
    f[1] = f[1].replace(b'"schema":', b'"schema":"fake","schema":', 1)
    assert "UNTRUSTED_JSON_OR_DUPLICATE_KEYS" in evaluate(f)["errors"]


def test_flat_future_unknown_receipt_schema_fails_closed():
    f = mutate_flat(1, lambda d: d.update(schema="unknown-future-v58@1"))
    assert "UNSUPPORTED_OR_FUTURE_RECEIPT_SCHEMA" in evaluate(f)["errors"]


def test_historical_wip56_receipt_cannot_claim_wip57_current():
    f = current_live()
    f[1] = current_direct_duden()[1]
    assert evaluate(f)["status"] == "BLOCKED"


def test_flat_real_rektion_receipt_maintains_stage4_issuer_blocks():
    result = evaluate(current_live())
    assert result["evaluated_contract"] == "REKTION_FLAT_SCOPED_TRACKED_METADATA_ONLY"
    assert result["production_stage5_allowed"] is False
    assert result["stage4_independent_semantic_review_completed"] is False
    assert result["real_current_issuer_authenticated"] is False
    assert result["source_pdf_or_portable_bytes_verified"] is False



def latest_family_mutation(index, fn):
    files = real_current()
    obj = json.loads(files[index])
    fn(obj)
    files[index] = json.dumps(obj, ensure_ascii=False).encode()
    return files


def test_actual_latest_supported_family_metadata_still_no_release():
    r = evaluate(real_current())
    assert r["status"] == "PASS_SCOPED_NATIVE_METADATA_CONSISTENCY_ONLY", r
    assert r["evaluated_contract"] == "WIP58_60_EXPLICIT_KNOWN_SCOPED_RECEIPT_METADATA_ONLY"
    for k in ("production_stage5_allowed", "stage4_independent_semantic_review_completed",
              "real_current_issuer_authenticated", "source_pdf_or_portable_bytes_verified"):
        assert r[k] is False


def test_old_wip50_receipt_cannot_fake_current_wip60():
    files = original()
    current = real_current()
    files[0] = current[0]
    files[3] = json.loads(current[0])["latest_receipt_path"]
    assert "HISTORICAL_WIP50_RECEIPT_CANNOT_CERTIFY_NEWER_CURRENT" in evaluate(files)["errors"]


@pytest.mark.parametrize("field", ["zip","zip_sha256","library_file_id",
                                  "canonical_sha256","import_sha256"])
def test_family_latest_receipt_portable_drift_blocks(field):
    f = latest_family_mutation(1, lambda d: d.update({field:"f"*64 if field.endswith("sha256") else "forged"}))
    dest = {"zip":"filename","zip_sha256":"sha256"}.get(field,field)
    assert "KNOWN_RECEIPT_CURRENT_ARTIFACT_DRIFT:"+dest in evaluate(f)["errors"]


@pytest.mark.parametrize("field", ["sha256","bytes","parent_sha256"])
def test_family_package_readback_or_parent_drift_blocks(field):
    f = latest_family_mutation(0, lambda d: d["complete_working_content_package"].update(
        {field: -1 if field=="bytes" else "f"*64}))
    assert evaluate(f)["status"] == "BLOCKED"


@pytest.mark.parametrize("field", ["remaining_holds","cumulative_attested",
                                    "learning_units","lexical_cards"])
def test_family_counts_fail_closed(field):
    f = latest_family_mutation(1, lambda d: d.update({field: 12345}))
    assert evaluate(f)["status"] == "BLOCKED"


def test_family_parent_predecessor_lineage_drifts_blocks():
    f = latest_family_mutation(0, lambda d: d["previous_wip60_source_current"]["portable"].update(
        sha256="f"*64))
    assert "KNOWN_PARENT_PORTABLE_LINEAGE_DRIFT" in evaluate(f)["errors"]


def test_family_different_receipt_schema_cannot_autopromote():
    f = latest_family_mutation(1, lambda d: d.update(
        schema="gcpk-aber-hallo-wip61-unknown@1"))
    assert "UNSUPPORTED_OR_FUTURE_RECEIPT_SCHEMA" in evaluate(f)["errors"]


def test_family_previous_historical_wip59_milestone_stale():
    f = latest_family_mutation(0, lambda d: d.update(
        latest_milestone="WIP59_STALE_HISTORICAL_SNAPSHOT"))
    assert "KNOWN_RECEIPT_NOT_CURRENT_MILESTONE" in evaluate(f)["errors"]


def test_family_stage4_issuer_must_stay_open():
    f = latest_family_mutation(1, lambda d: d.update(global_stage4="PASS"))
    assert "KNOWN_STAGE4_CLAIM_DRIFT" in evaluate(f)["errors"]


def test_family_source_pdf_claim_must_remain_provenanced():
    f = latest_family_mutation(1, lambda d: d.update(source_pdfs="REPLACED"))
    assert "KNOWN_SOURCE_IMMUTABILITY_CLAIM_DRIFT" in evaluate(f)["errors"]


def test_family_stages5_to7_must_not_run():
    f = latest_family_mutation(1, lambda d: d.update(stage5_to_7="VERIFIED"))
    assert "KNOWN_STAGE5_7_CLAIM_DRIFT" in evaluate(f)["errors"]


def test_family_duplicate_json_receipt_invalid():
    f = real_current()
    f[1] = f[1].replace(b'"schema":', b'"schema":"fake","schema":',1)
    assert "UNTRUSTED_JSON_OR_DUPLICATE_KEYS" in evaluate(f)["errors"]


def test_family_untrusted_bad_source_manifest_fails():
    f = latest_family_mutation(2, lambda d: d["source_set"][0].update(source_id=[]))
    assert "SOURCE_MANIFEST_SET_INVALID" in evaluate(f)["errors"]


def test_legacy_wip58_wip59_contracts_frozen_historical_not_current():
    import re
    from audit_aber_hallo_receipt_families import audit_family
    live = json.loads(real_current()[0])
    for version,oldkey in ((58,"previous_wip59_source_current"),
                           (59,"previous_wip60_source_current")):
        row = live[oldkey]
        receipt_path = row.get("receipt") or row.get("latest_receipt_path")
        r = json.loads((ROOT / receipt_path).read_bytes())
        port = row["portable"]
        parent = (r.get("parent_wip57_sha256") if version==58 else r["parent"]["sha256"])
        simulated = {
            "schema":"gcpk-workstream-latest@1.0.0",
            "workstream":"aber-hallo-listen-tabellen",
            "latest_milestone":row["latest_milestone"],
            "latest_receipt_path":receipt_path,
            "latest_receipt_commit_sha":"a"*40,
            "authority":{"current_portable":port},
            "complete_working_content_package":{
                "name":port["filename"], "sha256":port["sha256"],
                "bytes":port["size_bytes"], "library_file_id":port["library_file_id"],
                "library_path":port["library_path"], "stage4":"OPEN",
                "stage5_6_7":"NOT_RUN", "parent_sha256":parent,
                "member_count": r["tests"]["zip_members"] if version==58 else r["qa"]["zip_members"],
            },
            f"previous_wip{version}_source_current":live[f"previous_wip{version}_source_current"],
            "progress":{
                "rektion_independent_external_attested_cumulative":708 if version==58 else 731,
                "rektion_external_holds_remaining":273 if version==58 else 250,
                "pending_independent_expert_stage4":True,
                "independent_expert_unreviewed_units":788,
            },
        }
        errors,contract=audit_family(simulated,r,json.loads(real_current()[2]),receipt_path)
        assert errors == [], (version,errors)
        assert contract == "WIP58_60_EXPLICIT_KNOWN_SCOPED_RECEIPT_METADATA_ONLY"


def test_nested_json_duplicate_key_rejected():
    f=original()
    f[2]=f[2].replace(b'"schema":',b'"schema":"forged","schema":',1)
    assert "UNTRUSTED_JSON_OR_DUPLICATE_KEYS" in evaluate(f)["errors"]

def test_malformed_source_manifest_blocks():
    f=original();f[2]=b"[]"
    assert "DOCUMENT_NOT_AN_OBJECT" in evaluate(f)["errors"]
