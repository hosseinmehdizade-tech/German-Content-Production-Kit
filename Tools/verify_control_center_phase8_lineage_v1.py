#!/usr/bin/env python3
"""Fail-closed Git-index metadata-only verifier for dated Aber Hallo Phase8 lineage.

Never rehashes private user PDFs or Library ZIPs in CI. A pinned historical
receipt must not be misinterpreted as a source-content Stage4 or FINAL verdict.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
P7_PATH = ROOT / "Tools/verify_control_center_lineage_evidence_v1.py"
spec = importlib.util.spec_from_file_location("phase7_pinned", P7_PATH)
p7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p7)
INDEX = p7.INDEX
RECEIPT = "Optimization-Program/Verification/CONTROL-CENTER-PHASE8-ABER-HALLO-WIP92-WIP95-LINEAGE-20261105.json"
LATEST = "Workspaces/aber-hallo-listen-tabellen/LATEST.json"
P7_RECEIPT = p7.REC

def check(value, code):
    if not value:
        raise ValueError(code)

def validate(index, receipt, phase7):
    check(index.get("schema")=="gcpk-control-center-additive-lineage-evidence-index@1.0.0",
          "PHASE8_INDEX_SCHEMA")
    check(index.get("role")=="HISTORICAL_REAL_BYTE_LINEAGE_REPORTS__NOT_LIVE_CURRENT_OR_STAGE_VERDICT",
          "PHASE8_INDEX_FALSE_CURRENT")
    evidence=index.get("evidence")
    check(isinstance(evidence,list) and len(evidence)==2, "PHASE8_INDEX_RECORD_COUNT")
    old,new=evidence
    check(old.get("receipt_path")==P7_RECEIPT and old.get("proven_links")==15 and
          old.get("unproven_prior_links")==5, "PHASE7_RECORD_CHANGED")
    check(new.get("receipt_path")==RECEIPT and
          new.get("target_id")=="workspace:aber-hallo-listen-tabellen" and
          new.get("parent_family_id")=="family:aber-hallo-listen-tabellen" and
          new.get("receipt_git_blob_sha") and
          re.fullmatch(r"[a-f0-9]{40}", new["receipt_git_blob_sha"]) and
          new.get("previous_receipt_path")==P7_RECEIPT and
          new.get("previous_receipt_git_blob_sha")==old.get("receipt_git_blob_sha") and
          new.get("historical_source_anchor_registry_id")==
          old.get("historical_source_anchor_registry_id"),
          "PHASE8_TARGET_OR_PIN_MISMATCH")
    check(new.get("evidence_kind")=="ADDITIVE_REAL_BYTE_WIP92_WIP95__NOT_WIP72_TO_WIP77" and
          new.get("proven_new_links")==3 and new.get("prior_proven_links")==15 and
          new.get("cumulative_proven_links_wip77_to_wip95")==18 and
          new.get("unproven_prior_links")==5 and
          new.get("library_status")=="UNSYNCED_CONVERSATION_ARTIFACT__NO_LIBRARY_READBACK_CLAIM",
          "PHASE8_FALSE_COMPLETENESS_OR_LIBRARY_CLAIM")
    for name in ("full_stage4","stage5","stage6","stage7","current_or_final"):
        check(new.get(name) is False, "PHASE8_FALSE_STAGE_PROMOTION:"+name)
    check(receipt.get("schema")==
          "gcpk-control-center-phase8-wip92-wip95-real-byte-lineage-checkpoint@1.0.0" and
          receipt.get("status")==
          "PASS_LOCAL_3_OF_3_REAL_PARENT_CHILD_EDGES_WIP92_TO_WIP95__NOT_FULL_HISTORICAL_CHAIN_OR_STAGE_PASS",
          "PHASE8_RECEIPT_SCHEMA_OR_STATUS")
    check(receipt.get("target_id")==new["target_id"] and
          receipt.get("parent_family_id")==new["parent_family_id"] and
          receipt.get("parent_evidence",{}).get("path")==P7_RECEIPT and
          receipt.get("parent_evidence",{}).get("git_blob_sha")==old["receipt_git_blob_sha"] and
          receipt.get("parent_evidence",{}).get("wip92_zip_sha256")==
          phase7.get("snapshots",[])[-1].get("sha256") and
          receipt.get("parent_evidence",{}).get("prior_verified_links_wip77_to_wip92")==15,
          "PHASE8_PARENT_LINEAGE_BREAK")
    snaps=receipt.get("snapshots",[])
    check(len(snaps)==4 and [s.get("version") for s in snaps]==[92,93,94,95],
          "PHASE8_SNAPSHOT_SEQUENCE")
    check([s.get("zip_members") for s in snaps]==[103,108,112,116] and
          [s.get("sha256sums") for s in snaps]==[102,107,111,115] and
          [s.get("manifest_entries") for s in snaps]==[101,106,110,114],
          "PHASE8_MANIFEST_COUNTS")
    check([s.get("rection_qa_mismatched_ids") for s in snaps]==
          [["ahl-lu-0278"]]*3+[[]],
          "PHASE8_RECTION_MIRROR_CLAIM_CHANGED")
    edges=receipt.get("edges",[])
    check(len(edges)==3 and
          [(e.get("parent"),e.get("child"),e.get("changed_card_count")) for e in edges] ==
          [(92,93,4),(93,94,5),(94,95,18)],
          "PHASE8_MISSING_OR_WRONG_EDGES")
    for i,e in enumerate(edges):
        check(e.get("parent_sha_in_manifest_and_checkpoint")=="PASS_EXACT" and
              e.get("changed_id_declarations")=="EXACT" and
              isinstance(snaps[i].get("zip_sha256"),str) and
              re.fullmatch(r"[a-f0-9]{64}",snaps[i]["zip_sha256"]) and
              isinstance(snaps[i+1].get("zip_sha256"),str) and
              re.fullmatch(r"[a-f0-9]{64}",snaps[i+1]["zip_sha256"]),
              "PHASE8_UNPINNED_EDGE:"+str(i))
    check(edges[0].get("only_metadata_changes") is False and
          edges[0].get("non_metadata_exception",{}).get("id")=="ahl-lu-0684" and
          all(e.get("only_metadata_changes") is True for e in edges[1:]),
          "PHASE8_WIP93_NON_METADATA_EXCEPTION_HIDDEN")
    check(receipt.get("dated_git_latest_at_preflight",{}).get("blob_sha")==
          "ca648c93752b7b03ea4b06dc8ba6eb617dd067c3" and
          receipt.get("dated_git_latest_at_preflight",{}).get("current_portable_sha256")==
          snaps[-1]["zip_sha256"] and
          receipt.get("latest_wip95_workstream_checkpoint",{}).get("blob_sha")==
          "b07a0a54964c3ec8a107f5f32a9d2a536db7b8c2",
          "PHASE8_LATEST_OR_CHECKPOINT_PREIMAGE_MISMATCH")
    check(receipt.get("actual_original_pdf_sha256s",{}).get("a1_a2")==
          phase7.get("source_original_sha256s",{}).get("a1_a2") and
          receipt.get("actual_original_pdf_sha256s",{}).get("b1_c2")==
          phase7.get("source_original_sha256s",{}).get("b1_c2"),
          "PHASE8_ORIGINAL_SOURCE_DRIFT")
    constraints=receipt.get("cross_snapshot_constraints",{})
    check(constraints.get("total_changed_card_operations")==27 and
          constraints.get("total_changed_unique_cards")==25 and
          constraints.get("total_parent_child_links_now_verified_wip77_to_wip95")==18 and
          constraints.get("still_unproven_parent_child_links_wip72_to_wip77")==5 and
          constraints.get("changed_card_id_sets_match_canonical_tsv_manifest_checkpoint")=="3_OF_3" and
          constraints.get("wip95_learner_facing_change_declaration")==0 and
          constraints.get("wip95_browser_render_and_downstream_hidden_field_effects")=="NOT_VERIFIED",
          "PHASE8_COUNTS_OR_DISPLAY_BOUNDARY_CHANGED")
    pkg=receipt.get("locally_verified_package",{})
    check(pkg.get("sha256")=="69ebff9ba87ed7097231bfa376d4805b80b71e199e62b2a24a835e7403de8eb4" and
          pkg.get("report_sha256")=="d167e0146e4c9c99b99759196bc64657622024fab052f05624f05caed8e369bb" and
          pkg.get("local_positive_and_mutation_controls")=="16_OF_16_PASS" and
          pkg.get("library_sync")=="UNAVAILABLE_CONTAINER_SESSION_EXPIRED__NOT_CLAIMED" and
          pkg.get("github_runner_original_zip_pdf_readback")==0,
          "PHASE8_PACKAGE_OR_LIBRARY_ATTESTATION_NOT_GROUNDED")
    limits=receipt.get("explicit_limits",{})
    check(limits.get("wip73_to_wip76_real_archive_bytes_independently_attested") is False and
          limits.get("fully_contiguous_wip72_to_wip95") is False and
          limits.get("linguistic_stage4")=="OPEN" and
          all(limits.get(k)=="NOT_RUN" for k in ("stage5_final","stage6_browser","stage7_release")) and
          limits.get("current_or_final_approval_from_this_receipt") is False and
          limits.get("mutations_to_user_content_source_LOCKED_app_UI_FSRS_SRS")==0,
          "PHASE8_FALSE_STAGE_OR_CONTIGUITY")
    return {"status":"PASS_PINNED_PHASE8_METADATA_ONLY__NO_REAL_BINARY_CI",
            "verified_historical_edges_WIP77_to_WIP95":18,
            "unverified_earlier_edges":5,
            "native_or_release_certificates":0,
            "ci_real_pdf_or_library_zip_rereads":0}

def validate_repo(root=ROOT):
    index=p7.read(INDEX,root)
    item=index["evidence"][1]
    check(p7.git_blob(item["receipt_path"],root)==item["receipt_git_blob_sha"],
          "PHASE8_RECEIPT_GIT_BLOB_DRIFT")
    check(p7.git_blob(item["previous_receipt_path"],root)==
          item["previous_receipt_git_blob_sha"],"PHASE8_PARENT_GIT_BLOB_DRIFT")
    return validate(index,p7.read(RECEIPT,root),p7.read(P7_RECEIPT,root))

if __name__=="__main__":
    print(json.dumps(validate_repo(),sort_keys=True))
