#!/usr/bin/env python3
"""COP all-family currentness visibility and selected-authority CAS guard.

Read-only: compares the 21-family catalog, 10 selected Git owner pointers and
dated source observations. It NEVER browses Library/Drive, promotes a ZIP,
changes a source, or infers current provider availability from old evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import sys

CATALOG = "Optimization-Program/Control-Center/MASTER-PROJECT-CATALOG-v1.json"
PORTFOLIO = "Optimization-Program/Control-Center/DYNAMIC-CONTENT-PORTFOLIO-REGISTRY-v1.json"
ROUTING = "Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"
OBSERVATIONS = "Optimization-Program/Control-Center/COP-CURRENTNESS-OBSERVATIONS-v1.json"
SCHEMA = "gcpk-cop-currentness-observations@1.0.0"
OUTPUT_SCHEMA = "gcpk-cop-21-family-currentness-report@1.0.0"
SHA = re.compile(r"^[0-9a-f]{64}$")
BLOB = re.compile(r"^[0-9a-f]{40}$")
PROVIDERS = {"conversation", "library", "google_drive"}
KINDS = {"working", "accepted_successor"}


def source_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("Unsafe source path")
    p = Path(relative)
    if p.is_absolute() or any(x in ("", ".", "..") for x in p.parts):
        raise ValueError("Unsafe source path")
    base = root.resolve()
    target = (base / p).resolve()
    if not target.is_relative_to(base):
        raise ValueError("Path escapes repository")
    return target


def read_json(root: Path, relative: str) -> dict:
    obj = json.loads(source_path(root, relative).read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("Expected JSON object: " + relative)
    return obj


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def pointer(obj: dict, route: str):
    if not isinstance(route, str) or not route.startswith("/") or route == "/":
        raise ValueError("Invalid JSON pointer")
    out = obj
    for token in route.split("/")[1:]:
        name = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(out, dict):
            raise ValueError("Missing JSON pointer: " + route)
        out = out[name]
    return out


def inspect(root: Path, observations: str = OBSERVATIONS) -> dict:
    root = root.resolve()
    catalog = read_json(root, CATALOG)
    portfolio = read_json(root, PORTFOLIO)
    routing = read_json(root, ROUTING)
    evidence = read_json(root, observations)
    families = catalog.get("families")
    items = portfolio.get("items")
    routes = routing.get("families")
    if not isinstance(families, list) or len(families) != 21:
        raise ValueError("21-family identity catalog expected")
    if not isinstance(items, list) or len(items) != 10:
        raise ValueError("10 curated accepted baselines expected")
    if not isinstance(routes, list) or len(routes) != 21:
        raise ValueError("21 canonical family routes expected")
    by_id = {x["id"]: x for x in families}
    selected = {x["id"]: x for x in items}
    routed = {x["family_id"]: x for x in routes}
    if len(by_id) != 21 or len(selected) != 10 or len(routed) != 21:
        raise ValueError("Duplicate catalog, portfolio or route identities")
    if not set(selected).issubset(by_id) or set(routed) != set(by_id):
        raise ValueError("Portfolio or routing identity outside catalog")
    if evidence.get("schema") != SCHEMA or evidence.get("data_edit_authorized") is not False:
        raise ValueError("Source observations are not read-only")
    observed = evidence.get("items")
    if not isinstance(observed, list):
        raise ValueError("Missing evidence list")
    obs_by_id = {}
    for item in observed:
        fid = item.get("family_id")
        if fid not in by_id or fid in obs_by_id:
            raise ValueError("Unknown or duplicate family evidence")
        if item.get("kind") not in KINDS or item.get("provider") not in PROVIDERS:
            raise ValueError("Invalid source kind/provider")
        if (not isinstance(item.get("observed_as_of"), str)
                or not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", item["observed_as_of"])):
            raise ValueError("Evidence observation must be date-scoped")
        if not SHA.fullmatch(str(item.get("sha256", ""))):
            raise ValueError("Invalid observed SHA")
        if not item.get("locator") or not item.get("name"):
            raise ValueError("Source observation has no locator/name")
        if item["kind"] == "accepted_successor":
            if item.get("accepted_successor_decision") is not True or not item.get("approval_receipt"):
                raise ValueError("Accepted successor requires explicit decision receipt")
        elif item.get("accepted_successor_decision") is not False:
            raise ValueError("Working observation must not claim accepted promotion")
        obs_by_id[fid] = item

    rows = []
    for fid in sorted(by_id):
        family, route = by_id[fid], routed[fid]
        chosen = selected.get(fid)
        accepted = None
        git_sync = "NO_SELECTED_BASELINE"
        failures = []
        if route.get("canonical_library_root") != family.get("library_path"):
            failures.append("CANONICAL_LIBRARY_ROOT_DRIFT")
        if chosen is not None:
            owner = chosen["owner_locator"]
            accepted = chosen["active_baseline"]["artifact_sha256"]
            if not SHA.fullmatch(str(accepted)):
                failures.append("ACCEPTED_SHA_INVALID")
            if route.get("active_content_sha256") != accepted:
                failures.append("CANONICAL_ARTIFACT_PIN_DRIFT")
            relative = owner.get("path")
            canonical = route.get("canonical_git_workspace")
            if (not isinstance(canonical, str) or not isinstance(relative, str)
                    or not relative.startswith(canonical + "/")):
                failures.append("CANONICAL_OWNER_ROUTE_DRIFT")
            try:
                raw = source_path(root, relative).read_bytes()
                owner_doc = json.loads(raw)
                owner_sha = pointer(owner_doc, owner["artifact_sha_json_pointer"])
                if owner_sha != accepted:
                    failures.append("SELECTED_OWNER_SHA_DRIFT")
                if git_blob(raw) != owner.get("git_blob_observed"):
                    failures.append("SELECTED_OWNER_BLOB_DRIFT")
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                failures.append("SELECTED_OWNER_UNRESOLVED")
            git_sync = "GIT_MATCH" if not failures else "GIT_DRIFT"
        elif route.get("canonical_source_owner_document") or route.get("active_content_sha256"):
            failures.append("UNREGISTERED_FAMILY_CLAIMS_ACCEPTED")
            git_sync = "GIT_DRIFT"

        obs = obs_by_id.get(fid)
        working = None
        if obs is None:
            working_status = "CURRENT_NOT_VERIFIED"
            provenance = "NO_LIVE_OR_RECORDED_WORKING_EVIDENCE"
        else:
            working = obs["sha256"]
            provenance = "AS_OF_" + obs["observed_as_of"] + "__NOT_LIVE_DISCOVERY_IN_CI"
            try:
                source = read_json(root, obs["evidence_path"])
                proof_sha = pointer(source, obs["evidence_json_pointer"])
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                proof_sha = None
            if proof_sha != working:
                working_status = "EVIDENCE_UNRESOLVED_HOLD"
                failures.append("WORKING_SOURCE_RECEIPT_MISMATCH")
            elif accepted is None:
                working_status = "WORKING_OBSERVED_NO_ACCEPTED_BASELINE"
            elif working == accepted:
                working_status = "WORKING_EQUALS_ACCEPTED_AS_OF"
            elif obs["kind"] == "accepted_successor":
                working_status = "ACCEPTED_SUCCESSOR_NOT_SYNCED_HOLD"
                failures.append("ACCEPTED_SUCCESSOR_PIN_STALE")
            else:
                working_status = "WORKING_DIFFERS_ACCEPTED__NO_AUTO_PROMOTION"
        rows.append({
            "family_id": fid, "canonical_library_root": family.get("library_path"),
            "canonical_workspace": route.get("canonical_git_workspace"),
            "accepted_baseline_sha256": accepted, "working_observed_sha256": working,
            "working_status": working_status, "git_sync": git_sync,
            "provider_evidence": provenance, "findings": failures,
            "source_owner": chosen["owner_locator"]["path"] if chosen else None,
        })
    counts = Counter()
    for row in rows:
        counts[row["git_sync"]] += 1
        counts[row["working_status"]] += 1
    blocking = [row["family_id"] for row in rows if row["findings"]]
    status = ("CURRENTNESS_HOLD_GIT_OR_RECORDED_ACCEPTANCE_DRIFT" if blocking
              else "GIT_POINTERS_MATCH__LIVE_PROVIDER_CURRENTNESS_INCOMPLETE")
    return {
        "schema": OUTPUT_SCHEMA, "status": status, "total_catalog_families": len(rows),
        "selected_accepted_baselines": len(selected), "recorded_as_of_families": len(obs_by_id),
        "live_provider_enumeration_in_ci": False, "all_21_live_current_verified": False,
        "counts": dict(sorted(counts.items())), "blocking_families": blocking,
        "families": rows, "source_observations_path": observations,
        "not_proof_of": ["newest unobserved Google Drive/Library files",
                         "automatic acceptance or promotion", "semantic Stage4 correctness",
                         "native app Stage6, SRS or FSRS", "absence of newer unlisted artifacts"],
    }


def markdown(report: dict) -> str:
    lines = ["# COP — 21-family currentness visibility", "",
             "Status: " + report["status"], "",
             "| Family | Accepted (SHA prefix) | Recorded working | Git sync |",
             "|---|---|---|---|"]
    for row in report["families"]:
        accepted = (row["accepted_baseline_sha256"] or "NONE")[:12]
        lines.append("| " + row["family_id"] + " | " + accepted +
                     " | " + row["working_status"] + " | " + row["git_sync"] + " |")
    lines += ["", "GitHub CI does not read private Drive/Library. Missing provider evidence means CURRENT_NOT_VERIFIED, not PASS.",
              "A working source that differs from an accepted baseline does NOT automatically replace that baseline.",
              "No content, app, user study state or accepted release is modified.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--observations", default=OBSERVATIONS)
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--github-summary", action="store_true")
    ap.add_argument("--fail-on-drift", action="store_true")
    args = ap.parse_args(argv)
    try:
        root = args.repo_root.resolve()
        result = inspect(root, args.observations)
        if args.out_dir:
            dest = args.out_dir.resolve()
            if dest.is_relative_to(root):
                raise ValueError("Reports may not be written into the source repository")
            dest.mkdir(parents=True, exist_ok=True)
            (dest / "COP-CURRENTNESS-21-FAMILY.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (dest / "COP-CURRENTNESS-21-FAMILY.md").write_text(markdown(result), encoding="utf-8")
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fp:
                fp.write(markdown(result))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if args.fail_on_drift and result["blocking_families"] else 0
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "CURRENTNESS_INPUT_HOLD",
                          "reason": type(exc).__name__ + ": " + str(exc)[:380]}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
