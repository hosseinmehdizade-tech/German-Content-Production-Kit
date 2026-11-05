#!/usr/bin/env python3
"""Read-only verifier for the Git-pinned Phase7 lineage declaration.

Important: GitHub CI verifies unchanged report identity and internal consistency,
NOT actual user's PDF/Library ZIP bytes; those were checked outside GitHub and
the reproducible byte-level attestor is contained in the pinned Library package.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
INDEX = "Optimization-Program/Control-Center/LINEAGE-EVIDENCE-v1.json"
REC = "Optimization-Program/Verification/CONTROL-CENTER-PHASE7-ABER-HALLO-WIP77-WIP92-LINEAGE-20261105.json"
REG = "Optimization-Program/Control-Center/EVIDENCE-REGISTRY-v1.json"
EXPECTED_SRC = {
    "a1_a2": "4125ed49efa3c4e72500a9c80b8d39021c8933d9a387fc96a637fd4b457e3cf3",
    "b1_c2": "ebaa3896c3c383808b832241afaf6c38ef4f498eb4dc1b38f26c12087cc97a04",
}
SHA = re.compile(r"[a-f0-9]{64}\\Z")
BLOB = re.compile(r"[a-f0-9]{40}\\Z")

def ensure(expr, code):
    if not expr:
        raise ValueError(code)

def read(path, root=ROOT):
    ensure(isinstance(path, str) and path.startswith("Optimization-Program/") and
           ".." not in Path(path).parts, "UNSAFE_LEDGER_PATH")
    return json.loads((root / path).read_text(encoding="utf-8"))

def git_blob(path, root=ROOT):
    completed = subprocess.run(
        ["git", "ls-files", "--stage", "--", path], cwd=root,
        capture_output=True, text=True, check=True)
    line = completed.stdout.strip()
    ensure(len(line.splitlines()) == 1, "LEDGER_GIT_INDEX_NOT_UNIQUE")
    match = re.fullmatch(r"100644 ([0-9a-f]{40}) 0\\t(.+)", line)
    ensure(match is not None and match.group(2) == path, "LEDGER_GIT_PIN_UNTRACKED")
    return match.group(1)

def validate(index, receipt, historic):
    ensure(index.get("schema") ==
           "gcpk-control-center-additive-lineage-evidence-index@1.0.0",
           "LINEAGE_INDEX_SCHEMA")
    ensure(index.get("role") ==
           "HISTORICAL_REAL_BYTE_LINEAGE_REPORTS__NOT_LIVE_CURRENT_OR_STAGE_VERDICT",
           "FALSE_LEDGER_CURRENTNESS")
    records=index.get("evidence")
    ensure(isinstance(records,list) and len(records)==1,"LINEAGE_INDEX_RECORD_COUNT")
    item=records[0]
    ensure(item.get("target_id") == "workspace:aber-hallo-listen-tabellen" and
           item.get("parent_family_id") == "family:aber-hallo-listen-tabellen" and
           item.get("receipt_path") == REC and
           BLOB.fullmatch(item.get("receipt_git_blob_sha","")) is not None,
           "LINEAGE_INDEX_TARGET_OR_PIN")
    ensure(item.get("evidence_kind") ==
           "CONSECUTIVE_EXACT_BYTE_WIP77_TO_WIP92__NOT_WIP72_TO_WIP77"
           and item.get("proven_links")==15 and item.get("unproven_prior_links")==5
           and item.get("historical_source_anchor_registry_id") ==
           "aber-hallo-wip92-source-anchored-historical-20261105",
           "LINEAGE_KIND_OR_LINK_COUNT")
    for field in ("full_stage4","stage5","stage6","stage7","current_or_final"):
        ensure(item.get(field) is False,"LINEAGE_FAKE_STAGE:"+field)
    ensure(receipt.get("schema") ==
           "gcpk-control-center-phase7-wip77-wip92-direct-byte-lineage@1.0.0"
           and receipt.get("status") ==
           "PASS_15_OF_15_EXACT_PARENT_CHILD_BYTE_EDGES_WIP77_WIP92__FIVE_EARLIER_EDGES_UNATTESTED",
           "RECEIPT_SCOPE_OR_SCHEMA")
    ensure(receipt.get("target_id")==item["target_id"] and
           receipt.get("parent_family_id")==item["parent_family_id"]
           and receipt.get("source_original_sha256s")==EXPECTED_SRC,
           "RECEIPT_OWNER_OR_SOURCE")
    snaps=receipt.get("snapshots"); links=receipt.get("links")
    ensure(isinstance(snaps,list) and len(snaps)==16 and
           isinstance(links,list) and len(links)==15,
           "RECEIPT_MISSING_CONTIGUOUS_SNAPSHOTS")
    ensure([x.get("version") for x in snaps]==list(range(77,93)) and
           all(isinstance(x.get("sha256"),str) and SHA.fullmatch(x["sha256"]) for x in snaps),
           "RECEIPT_VERSION_OR_SHA")
    ensure(snaps[0]["sha256"] ==
           "00c6a6099d91fa22273e7aa598deb738355b2ce404025f1fb2cabac7e8d4c386"
           and snaps[-1]["sha256"] ==
           "3ff0900dbaad87110c3ef72ecd6b035091b4dd30dfe67ab537b28ce37336a4de",
           "RECEIPT_ENDPOINT_SHA")
    counts=[]
    for i,link in enumerate(links):
        ensure(link.get("parent_version")==77+i and
               link.get("child_version")==78+i and
               link.get("actual_parent_sha256")==snaps[i]["sha256"] and
               link.get("actual_child_sha256")==snaps[i+1]["sha256"] and
               link.get("parent_hash_manifest_and_checkpoint")=="PASS_EXACT" and
               link.get("source_provenance_and_examples_unchanged") is True,
               "BROKEN_PARENT_CHILD_LINK:"+str(i))
        k=link.get("changed_canonical_ids_count")
        ensure(isinstance(k,int) and not isinstance(k,bool) and k>=0 and
               link.get("changed_tsv_ids_count")==k and
               link.get("checkpoint_comparison")==(
                  "EXACT_COUNT_ONLY" if i in (4,5) else "EXACT_CHANGED_ID_SET"),
               "CHANGED_CARD_PROJECTION_DISAGREES:"+str(i))
        counts.append(k)
    ensure(counts==[4,25,15,18,27,14,13,12,11,15,11,10,10,3,1],
           "CHANGED_CARD_COUNTS_DIFFER")
    observed=receipt.get("observed",{})
    ensure(observed.get("consecutive_archives_read")==16 and
           observed.get("verified_links")==15 and
           observed.get("canonical_units_per_version")==788 and
           observed.get("lexical_tsv_rows_per_version")==787 and
           observed.get("lexical_tsv_columns_per_version")==23 and
           observed.get("changed_card_operations")==189 and
           observed.get("unique_changed_card_ids")==185 and
           observed.get("all_example_lists_stable") is True and
           observed.get("full_crc_sha256sums_manifest_checked_per_archive") is True,
           "OBSERVED_COUNTS_OR_INTEGRITY_INCONSISTENT")
    boundary=receipt.get("claims_boundary",{})
    ensure(boundary.get("total_parent_child_edges_wip72_to_wip92")==20 and
           boundary.get("verified_wip77_to_wip92_edges")==15 and
           boundary.get("not_verified_wip72_to_wip77_edges")==5 and
           boundary.get("unreadable_intermediate_archives")==[73,74,75,76] and
           boundary.get("full_semantic_source_to_card_fidelity")=="NOT_ATTESTED" and
           boundary.get("stage4")=="OPEN" and boundary.get("stage5")=="NOT_RUN" and
           boundary.get("stage6_native_browser")=="NOT_RUN" and
           boundary.get("stage7")=="NOT_RUN" and
           boundary.get("current_or_final_certificate") is False and
           boundary.get("github_ci_rehashed_actual_pdfs_or_zips") is False and
           boundary.get("source_learner_cards_app_UI_SRS_FSRS_modified") is False,
           "FALSE_STAGE_OR_FULL_CHAIN_PROMOTION")
    pkg=receipt.get("reproducible_package",{})
    ensure(pkg.get("sha256") ==
           "b4ad6b62cc2b33193296e6b5885f0d62cd2406e296451384ae4f385d992f9ab2"
           and pkg.get("library_roundtrip")=="PASS_EXACT_SHA256_AND_BYTES"
           and pkg.get("local_test_count")=="9_OF_9_PASS",
           "REPRODUCIBLE_PACKAGE_PIN_MISMATCH")
    evidence=historic.get("records",[])
    ensure(isinstance(evidence,list) and
           len([r for r in evidence if r.get("evidence_id")==
             item["historical_source_anchor_registry_id"]])==1,
           "PHASE6_ANCHOR_MISSING")
    return {"status":"PASS_GIT_PINNED_LINEAGE_METADATA_ONLY",
            "historical_proven_links":15,
            "historical_unproven_links":5,
            "actual_library_zip_pdf_bytes_rehashed_here":0,
            "Stage4_to_Stage7_or_CURRENT_FINAL_certificates":0}

def validate_repo(root=ROOT):
    index=read(INDEX,root)
    item=index["evidence"][0]
    ensure(git_blob(item["receipt_path"],root)==item["receipt_git_blob_sha"],
           "LINEAGE_RECEIPT_GIT_BLOB_PIN_DRIFT")
    return validate(index,read(REC,root),read(REG,root))

def main():
    print(json.dumps(validate_repo(),sort_keys=True))

if __name__=="__main__":
    main()
