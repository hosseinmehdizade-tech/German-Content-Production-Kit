#!/usr/bin/env python3
"""GFP-OPT P1: executable global-policy impact router across source families.

It answers "which sources should consider this rule?" using the exact active
registry, existing project catalog and a conservative source-domain profile.
This read-only router is NOT a producer adapter, semantic QA or release gate.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import re
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "Optimization-Program/Control-Center/Profiles/P1-ALL-FAMILY-APPLICABILITY-v1.json"
CATALOG = "Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
REGISTRY = "Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
PREVIOUS = "Optimization-Program/Verification/GLOBAL-POLICY-ADOPTION-MATRIX-20261105.json"
PILOT_PROFILE = "Optimization-Program/Control-Center/Profiles/P1-NEUTRAL-STAGE5-REAL-PRODUCERS-v1.json"
PILOT_RECEIPT = "Optimization-Program/Verification/OP01-OP02-P1-TWO-REAL-PRODUCER-FORMAT-20261105.json"

ALLOWED_DOMAINS = {
    "LEXICAL_SOURCE_CANDIDATE", "MIXED_SOURCE_NEEDS_OUTPUT_SPLIT",
    "VISUAL_MEDIA_NEEDS_PROFILE", "GRAMMAR_NEEDS_PROFILE",
    "READING_SKILLS_NEEDS_PROFILE", "WRITING_SKILLS_NEEDS_PROFILE",
    "GENERIC_IMPORT_NATIVE_OUTPUT_UNRESOLVED"
}
LEXICAL_DOMAINS = {"LEXICAL_SOURCE_CANDIDATE"}
MIXED_DOMAINS = {"MIXED_SOURCE_NEEDS_OUTPUT_SPLIT"}
ACCEPTED_SCOPES = {
    "ALL_WORKSTREAM_STARTUP", "ALL_PRODUCERS", "LEXICAL_MUTABLE",
    "LINGUISTIC_REVIEW", "LEXICAL_MUTABLE_AND_VISIBLE_PROJECTION",
    "NEUTRAL_VOCABULARY_PROJECTION", "USER_FACING_LEXICAL_DELIVERY",
    "CLEAN_DELIVERY", "LEXICAL_QA_ADVISORY",
    "NEW_OR_MUTABLE_GERMAN_NOUN_VERB_ADJECTIVE_LEARNER_VISIBLE_PROJECTIONS",
    "SOURCE_ATTESTED_LEXICAL_FRONT_SEMANTIC_QA",
    "MUTABLE_NEUTRAL_VOCABULARY_NOUN_VERB_ADJECTIVE_WITH_CANONICAL_UNIT",
    "SOURCE_PINNED_MUTABLE_NEUTRAL_LEXICAL_PROJECTIONS",
    "OPT_IN_NATIVE_STAGE5_BUILDER_WITH_READABLE_CANONICAL_MORPHOLOGY"
}
QA_ONLY_SCOPE = "QA_WORKSPACE_NOT_DIRECT_PRODUCER"
ROUTER_SCOPE = "INHERITS_NORMATIVE_GLOBAL_ENTRYPOINT_FOR_FUTURE_AUTHORIZED_WORK"
ACCEPTED_STATES = {
    "ROUTED_PROSPECTIVE_NO_EXECUTION_PROOF",
    "PRODUCER_CONTRACT_CANDIDATE_NEEDS_NATIVE_ADAPTER",
    "LINGUISTIC_REVIEW_CANDIDATE_NOT_STAGE4",
    "LEXICAL_CANDIDATE_FIELD_LEVEL_PROOF_REQUIRED",
    "SPLIT_SOURCE_PROFILE_REQUIRED",
    "DOMAIN_ADAPTER_REQUIRED_NO_FORCED_LEXICAL_SCHEMA",
    "NATIVE_GENERIC_OUTPUT_MISSING",
    "HISTORICAL_FORMAT_WITNESS_NOT_CURRENT_OR_ADOPTED",
    "POSSIBLE_NEUTRAL_OUTPUT_NEEDS_REAL_FOUR_ROLE_PROOF",
    "LEXICAL_DELIVERY_CANDIDATE_NEEDS_CURRENT_BYTES",
    "QA_WORKSPACE_ROUTED_AT_RESUME_NOT_DIRECT_PRODUCER",
    "QA_WORKSPACE_NOT_DIRECT_PRODUCER"
}

class ImpactError(ValueError):
    pass

def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ImpactError(reason)

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def git_blob_text_matches(data: bytes, expected: str) -> bool:
    # GitHub's canonical LF blob is authoritative; Windows CRLF checkout is
    # accepted only if canonical bytes give the SAME pinned Git blob identity.
    return git_blob_sha(data) == expected or (
        b"\r\n" in data and
        git_blob_sha(data.replace(b"\r\n", b"\n")) == expected
    )

def active_git_blob(root: Path, path: str) -> str:
    """Resolve the **live** policy/accepted-current matrix from the checked out commit.

    Historical profile records retain their old SHA and should NOT be edited
    whenever the user approves another rule. Working-tree tampering is rejected.
    """
    proc = subprocess.run(["git","rev-parse","--verify","HEAD:" + path],
                          cwd=root, text=True, capture_output=True, encoding="utf-8")
    require(proc.returncode == 0, "LIVE_GIT_SNAPSHOT_UNAVAILABLE:" + path)
    sha=proc.stdout.strip()
    require(re.fullmatch(r"[0-9a-f]{40}", sha) is not None,
            "LIVE_GIT_SNAPSHOT_INVALID:" + path)
    return sha


def load_json(root: Path, path: str, expected_blob: str | None = None) -> dict:
    f = root / path
    require(f.is_file() and not f.is_symlink(), "MISSING_OR_UNSAFE_EVIDENCE:" + path)
    raw = f.read_bytes()
    if expected_blob is not None:
        require(git_blob_text_matches(raw, expected_blob),
                "GIT_BLOB_MISMATCH:" + path)
    doc = json.loads(raw.decode("utf-8-sig"))
    require(isinstance(doc, dict), "JSON_EXPECTED_OBJECT:" + path)
    return doc

def authority(root: Path = ROOT) -> tuple[dict, dict, dict, dict, dict, dict]:
    profiles = load_json(root, PROFILE)
    require(profiles.get("schema") ==
            "gfp-opt-p1-source-domain-applicability-profiles@1.0.0"
            and profiles.get("program_id") == "GFP-OPT-2026"
            and profiles.get("status") ==
            "CANDIDATE_SCOPES_AND_HISTORICAL_FORMAT_WITNESSES_ONLY__NOT_PRODUCER_ADOPTION",
            "FALSE_PROFILE_AUTHORITY")
    paths = {
        "catalog": CATALOG, "policy_registry": REGISTRY,
        "previous_routing_snapshot": PREVIOUS,
        "historical_real_output_profiles": PILOT_PROFILE,
        "historical_real_output_mirror_receipt": PILOT_RECEIPT
    }
    pins = profiles.get("authority", {})
    docs = []
    for key, path in paths.items():
        item = pins.get(key, {})
        require(item.get("path") == path and
                isinstance(item.get("git_blob"), str) and
                len(item["git_blob"]) == 40, "MISSING_AUTHORITY_BLOB_PIN:" + key)
        # The 2026-11-05 profile pins are historical **snapshots**, not live
        # assertions about the continuously versioned policy and adoption matrix.
        # Verify live bytes against Git HEAD for mutable control-plane pointers.
        expected=(active_git_blob(root,path)
                  if key in {"policy_registry","previous_routing_snapshot"}
                  else item["git_blob"])
        docs.append(load_json(root, path, expected))
    catalog, registry, previous, pilot, pilot_receipt = docs
    require(catalog.get("schema") == "gcpk-master-project-catalog@1.0.0",
            "CATALOG_SCHEMA_CHANGED")
    require(registry.get("schema") == "gcpk-global-policy-registry@1.0.0"
            and registry.get("status") ==
            "ACTIVE_PROSPECTIVE_POLICY_ROUTER_NOT_BULK_CONTENT_MIGRATION",
            "REGISTRY_NOT_ACTIVE")
    require(previous.get("no_blanket_certification") is True,
            "FALSE_GLOBAL_BASELINE_ADOPTION")
    require(registry.get("policy_bindings") and
            all(b.get("scope") in ACCEPTED_SCOPES and
                isinstance(b.get("stages"), list) and
                b.get("stages") for b in registry["policy_bindings"].values()),
            "UNKNOWN_OR_UNSAFE_BINDING_SCOPE")
    return profiles, catalog, registry, previous, pilot, pilot_receipt

def verify_catalog_and_profiles(profile: dict, catalog: dict, previous: dict,
                                pilot: dict, receipt: dict) -> None:
    families = catalog.get("families", [])
    workspaces = catalog.get("workspaces", [])
    roots = catalog.get("root_workstreams", [])
    require(len(families) == 21 and len(workspaces) == 36
            and len(roots) == 17, "CATALOG_COUNT_DRIFT_STOP_FOR_REVIEW")
    family_ids = [x.get("id") for x in families]
    require(len(family_ids) == len(set(family_ids)) and
            all(isinstance(x, str) and x.startswith("family:") for x in family_ids),
            "INVALID_CATALOG_FAMILY_ID")
    entities = profile.get("families", [])
    profiled_ids = [x.get("id") for x in entities]
    require(profiled_ids == family_ids and
            all(x.get("declared_domain") in ALLOWED_DOMAINS for x in entities),
            "FAMILY_PROFILE_COVERAGE_OR_DOMAIN_MISMATCH")
    work_ids = [x.get("id") for x in workspaces]
    root_keys = [x.get("key") for x in roots]
    require(len(work_ids) == len(set(work_ids))
            and len(root_keys) == len(set(root_keys))
            and all(x.get("parent_family_id") in family_ids for x in workspaces + roots),
            "WORKSPACE_OR_ROOT_PARENT_UNKNOWN")
    prev_ws = previous.get("git_workspaces", [])
    by_path = {x.get("path"): x for x in prev_ws}
    require(len(by_path) == len(prev_ws) == len(workspaces)
            and set(by_path) == {w["git_dir"] for w in workspaces},
            "WORKSPACE_ROUTING_BASELINE_CHANGED")
    qa = {x["path"] for x in prev_ws
          if x.get("scope") == QA_ONLY_SCOPE}
    require(set(profile.get("qa_only_workspace_paths", [])) == qa
            and len(qa) == 3, "QA_ONLY_WORKSPACES_MISMATCH")
    require(all(row.get("global_policy_routing") == ROUTER_SCOPE
                and row.get("native_adapter_verified") == "NO_WORKSPACE_SPECIFIC_PROOF"
                for row in prev_ws), "PREVIOUS_ROUTER_CLAIMS_CHANGED")
    assert_guards = profile.get("protected_boundaries", {})
    require(assert_guards and all(v is True for v in assert_guards.values())
            and len(assert_guards) >= 7, "PROTECTED_BOUNDARY_DISABLED")
    for row in entities:
        require(row.get("routing_status") ==
                "CENTRAL_POLICY_ROUTED_FOR_FUTURE_APPLICABLE_WORK_ONLY"
                and row.get("native_builder_status") ==
                "NOT_CONNECTED_FOR_THIS_FAMILY__GOVERNED_ENTRYPOINT_EXISTS_CENTRALLY"
                and row.get("latest_authoritative_artifact_status") ==
                "NOT_RESOLVED_BY_THIS_CATALOG"
                and row.get("independent_semantic_stage4") ==
                "NOT_VERIFIED_BY_THIS_PROFILE"
                and row.get("stage5_release_status") == "NOT_PROMOTED"
                and row.get("stage6_native_app") == "NOT_RUN"
                and row.get("stage7_final") == "NOT_RUN"
                and row.get("applicable_policies_must_be_resolved_by_family_and_fields") is True,
                "FORGED_SOURCE_ADOPTION_OR_RELEASE:" + row["id"])
    witnesses = {}
    require(pilot.get("schema") ==
            "gfp-opt-policy-real-producer-conformance-profiles@1.0.0"
            and pilot.get("snapshot_type") ==
            "EXACT_HISTORICAL_LIBRARY_ZIPS__NOT_CURRENTNESS",
            "PILOT_HISTORICAL_SCOPE_CHANGED")
    require(receipt.get("status") ==
            "PASS_TWO_HISTORICAL_REAL_SOURCE_FORMAT_WITNESSES__GLOBAL_ADOPTION_OPEN"
            and receipt.get("boundaries", {}).get("complete_34_workspace_adoption") ==
            "NOT_PROVEN", "REAL_OUTPUT_NOT_GLOBAL")
    for example in pilot.get("profiles", []):
        actual = next((x for x in receipt.get("local_byte_evidence", [])
                       if x["id"] == example["id"]), None)
        require(actual and actual.get("rows") == example["expected_rows"]
                and actual.get("archive_sha256") == example["zip_sha256"]
                and actual.get("import_member_sha256") ==
                example["import_tsv_sha256"], "PILOT_BYTES_OR_ROWS_NOT_PINNED")
        witness = {
            "historical_profile_id": example["id"],
            "historical_zip_sha256": example["zip_sha256"],
            "import_tsv_sha256": example["import_tsv_sha256"],
            "rows": example["expected_rows"],
            "format_evidence_only":
            "HISTORICAL_LOCAL_BYTE_SHAPE_MIRROR_NOT_CURRENT_OR_BUILDER_INVOCATION"
        }
        witnesses.setdefault(example["family_id"], []).append(witness)
    require(sum(map(len, witnesses.values())) == 2
            and sum(x["rows"] for v in witnesses.values() for x in v) == 602,
            "PILOT_WITNESS_COUNTS_CHANGED")
    for row in entities:
        require(row.get("historical_neutral_format_witnesses", []) ==
                witnesses.get(row["id"], []), "HISTORICAL_FORMAT_WITNESS_MISMATCH:" + row["id"])

def family_decision(row: dict, binding: dict) -> str:
    domain = row["declared_domain"]
    scope = binding["scope"]
    if scope == "ALL_WORKSTREAM_STARTUP":
        return "ROUTED_PROSPECTIVE_NO_EXECUTION_PROOF"
    if scope == "ALL_PRODUCERS":
        return "PRODUCER_CONTRACT_CANDIDATE_NEEDS_NATIVE_ADAPTER"
    if domain in MIXED_DOMAINS:
        return "SPLIT_SOURCE_PROFILE_REQUIRED"
    if domain == "GENERIC_IMPORT_NATIVE_OUTPUT_UNRESOLVED":
        return "NATIVE_GENERIC_OUTPUT_MISSING"
    if scope == "LINGUISTIC_REVIEW":
        return ("LINGUISTIC_REVIEW_CANDIDATE_NOT_STAGE4"
                if domain in LEXICAL_DOMAINS or domain in {
                    "GRAMMAR_NEEDS_PROFILE", "READING_SKILLS_NEEDS_PROFILE",
                    "WRITING_SKILLS_NEEDS_PROFILE"}
                else "DOMAIN_ADAPTER_REQUIRED_NO_FORCED_LEXICAL_SCHEMA")
    if scope in {"NEUTRAL_VOCABULARY_PROJECTION", "CLEAN_DELIVERY"}:
        if row["historical_neutral_format_witnesses"]:
            return "HISTORICAL_FORMAT_WITNESS_NOT_CURRENT_OR_ADOPTED"
        if domain in LEXICAL_DOMAINS:
            return "POSSIBLE_NEUTRAL_OUTPUT_NEEDS_REAL_FOUR_ROLE_PROOF"
        return "DOMAIN_ADAPTER_REQUIRED_NO_FORCED_LEXICAL_SCHEMA"
    if domain not in LEXICAL_DOMAINS:
        return "DOMAIN_ADAPTER_REQUIRED_NO_FORCED_LEXICAL_SCHEMA"
    if scope == "USER_FACING_LEXICAL_DELIVERY":
        return "LEXICAL_DELIVERY_CANDIDATE_NEEDS_CURRENT_BYTES"
    return "LEXICAL_CANDIDATE_FIELD_LEVEL_PROOF_REQUIRED"

def build_impact(profiles: dict, catalog: dict, registry: dict, previous: dict,
                 bindings: set[str] | None = None) -> dict:
    all_bindings = registry["policy_bindings"]
    if bindings is not None:
        require(bool(bindings) and bindings <= set(all_bindings),
                "UNKNOWN_POLICY_BINDING")
    chosen = sorted(bindings or set(all_bindings))
    family_by_id = {row["id"]: row for row in profiles["families"]}
    prev_by_path = {w["path"]: w for w in previous["git_workspaces"]}
    family_rows, workspace_rows, root_rows = [], [], []
    per_policy = {}
    for key in chosen:
        b = all_bindings[key]
        fam_status = {}
        for source in catalog["families"]:
            f = family_by_id[source["id"]]
            state = family_decision(f, b)
            require(state in ACCEPTED_STATES, "UNSAFE_RULE_DECISION")
            fam_status[f["id"]] = state
            family_rows.append({
                "policy_binding_id": key,
                "policy_path": b["path"],
                "policy_git_blob": b["blob_sha"],
                "scope": b["scope"],
                "stage_numbers": b["stages"],
                "family_id": f["id"],
                "domain": f["declared_domain"],
                "impact_status": state,
                "producer_implementation_status": f["native_builder_status"],
                "actual_currentness": "NOT_RESOLVED",
                "native_runtime_stage6": "NOT_RUN",
                "stage4_semantic_certification": "NOT_CERTIFIED",
                "historical_format_witness_count":
                    len(f["historical_neutral_format_witnesses"]),
                "next_action": ("RESOLVE_NATIVE_CURRENT_AND_FOUR_ROLE_OUTPUT"
                               if state in {"POSSIBLE_NEUTRAL_OUTPUT_NEEDS_REAL_FOUR_ROLE_PROOF",
                                            "HISTORICAL_FORMAT_WITNESS_NOT_CURRENT_OR_ADOPTED"}
                               else "RESOLVE_FIELD_SCOPE_AND_SOURCE_SPECIFIC_ADAPTER")
            })
        for w in catalog["workspaces"]:
            old = prev_by_path[w["git_dir"]]
            qa_only = old["scope"] == QA_ONLY_SCOPE
            state = (
                "QA_WORKSPACE_ROUTED_AT_RESUME_NOT_DIRECT_PRODUCER"
                if qa_only and b["scope"] == "ALL_WORKSTREAM_STARTUP" else
                "QA_WORKSPACE_NOT_DIRECT_PRODUCER"
                if qa_only else fam_status[w["parent_family_id"]]
            )
            workspace_rows.append({
                "policy_binding_id": key,
                "workspace_id": w["id"],
                "git_dir": w["git_dir"],
                "parent_family_id": w["parent_family_id"],
                "workspace_kind": "QA_ONLY_NOT_DIRECT_PRODUCER" if qa_only
                                  else "CATALOG_WORKSPACE_NATIVE_PRODUCER_UNVERIFIED",
                "impact_status": state,
                "workspace_specific_execution_verified": False,
                "workspace_specific_real_output_verified": False,
                "not_independent_family": True
            })
        for r in catalog["root_workstreams"]:
            root_rows.append({
                "policy_binding_id": key,
                "root_key": r["key"],
                "parent_family_id": r["parent_family_id"],
                "impact_status": fam_status[r["parent_family_id"]],
                "root_stage_or_currentness_certified": False,
                "not_independent_family": True
            })
        per_policy[key] = {
            "scope": b["scope"],
            "stages": b["stages"],
            "family_impacts": dict(sorted(Counter(fam_status.values()).items())),
            "workspace_count": len(catalog["workspaces"]),
            "qa_only_workspaces": 3,
            "root_workstreams": len(catalog["root_workstreams"]),
            "real_producer_adoption_verified_from_this_impact_planner": 0,
            "policy_became_executable_in_every_producer": False
        }
    return {
        "schema":"gfp-opt-p1-central-policy-impact-and-adoption-plan@1.0.0",
        "program_id":"GFP-OPT-2026",
        "status":"PASS_CONSERVATIVE_IMPACT_ROUTING_ONLY__ACTUAL_ADOPTION_OPEN",
        "catalog_baseline": {
            "families":len(catalog["families"]),
            "git_workspaces":len(catalog["workspaces"]),
            "root_workstreams":len(catalog["root_workstreams"]),
            "qa_workspaces_not_direct_producers":len(profiles["qa_only_workspace_paths"]),
            "policy_registry_bindings":len(all_bindings)
        },
        "selected_policy_bindings":chosen,
        "per_policy":per_policy,
        "family_impacts":family_rows,
        "workspace_impacts":workspace_rows,
        "root_workstream_impacts":root_rows,
        "truth_boundary":{
            "family_impacts_are_candidates_only":True,
            "workspace_count_is_not_producer_adoption_count":True,
            "historical_witnesses_are_not_new_currentness_or_stage_approval":True,
            "synthetic_tests_do_not_prove_real_producer_adoption":True,
            "no_automatic_rewrite_of_locked_sources_or_cards":True,
            "no_app_runtime_ui_srs_fsrs_modification":True,
            "no_stage4_5_6_7_or_final_certification":True
        },
        "next":"P1: source-owning workstreams must resolve actual mutable field scope, authorized current source and active native producer invocation. Collect a separate governed-builder receipt and independently verified source/output bytes before granting producer-level adoption."
    }

def execute(root: Path = ROOT, bindings: set[str] | None = None) -> dict:
    p, c, r, old, pilot, proof = authority(root)
    verify_catalog_and_profiles(p,c,old,pilot,proof)
    return build_impact(p,c,r,old,bindings)

def main() -> int:
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--binding",action="append",help="Exact policy binding ID; omit to inspect all currently registered rules")
    cli.add_argument("--family",help="Filter a family's candidate rows (or use --binding)")
    cli.add_argument("--summary",action="store_true",
                     help="Compact summary instead of all family/workspace/root rows")
    cli.add_argument("--write-once-report",type=Path,
                     help="Create a new JSON report; never overwrite an old receipt")
    args=cli.parse_args()
    try:
        result=execute(bindings=set(args.binding) if args.binding else None)
        if args.family:
            require(any(x["family_id"]==args.family
                        for x in result["family_impacts"]), "UNKNOWN_FAMILY")
            result["family_impacts"]=[
                x for x in result["family_impacts"] if x["family_id"]==args.family]
            result["workspace_impacts"]=[
                x for x in result["workspace_impacts"] if x["parent_family_id"]==args.family]
            result["root_workstream_impacts"]=[
                x for x in result["root_workstream_impacts"] if x["parent_family_id"]==args.family]
            result["filtered_view_only"]=True
        result["selected_impact_rows"]={
            "family":len(result["family_impacts"]),
            "workspace":len(result["workspace_impacts"]),
            "root":len(result["root_workstream_impacts"])
        }
        if args.write_once_report:
            target=args.write_once_report
            require(target.suffix==".json" and not target.exists()
                    and not target.is_symlink() and target.parent.is_dir()
                    and target.resolve() not in [ROOT / PROFILE, ROOT / CATALOG, ROOT / REGISTRY],
                    "OUTPUT_REPORT_NOT_A_NEW_SAFE_PATH")
            with target.open("x",encoding="utf-8") as stream:
                json.dump(result,stream,ensure_ascii=False,sort_keys=True,indent=2)
                stream.write("\n")
        if args.summary:
            result={k:v for k,v in result.items()
                    if k not in {"family_impacts","workspace_impacts","root_workstream_impacts"}}
        print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
    except (ImpactError,OSError,ValueError,UnicodeError) as error:
        print("GFP_OPT_IMPACT_FAIL: "+str(error),file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
