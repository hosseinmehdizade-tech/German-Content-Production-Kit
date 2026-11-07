#!/usr/bin/env python3
"""Read-only, metadata-only replay of authenticated Library/Drive observations.

The observation JSON is collected by an authorized external client (e.g. ChatGPT
connectors). GitHub CI cannot query a user's private Library or Drive. Never
promote current content, infer a file was deleted, or claim a ZIP SHA proof.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys

REGISTRY = "Optimization-Program/Control-Center/DYNAMIC-CONTENT-PORTFOLIO-REGISTRY-v1.json"
SNAPSHOT = "Optimization-Program/Control-Center/Provider-Observations/2026-11-07.json"
SCHEMA = "gfp-opt-portfolio-provider-observations@1.0.0"
PROVIDERS = ("google_drive", "library")
OBSERVED = {"google_drive": "EXACT_FILE_METADATA_OBSERVED",
            "library": "EXACT_FOLDER_METADATA_OBSERVED"}
OTHER = {"NOT_CHECKED", "NOT_OBSERVED_IN_SCANNED_FOLDERS",
         "RETIRED_WITH_PRIOR_OWNER_AUTHORIZATION"}


def read_object(path: Path) -> dict:
    j = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(j, dict):
        raise ValueError("JSON root must be an object")
    return j


def check_observations(registry: dict, snapshot: dict) -> tuple[list[dict], dict]:
    if snapshot.get("schema") != SCHEMA or snapshot.get("read_only") is not True:
        raise ValueError("bad observation schema or read-only indicator")
    if snapshot.get("auto_release_promotion") is not False:
        raise ValueError("auto release promotion must be false")
    if snapshot.get("evidence_scope") != "PROVIDER_METADATA_ONLY__NO_FRESH_BINARY_SHA256__NO_PROVIDER_ACCESS_INSIDE_GITHUB_CI":
        raise ValueError("must clearly mark metadata-only evidence scope")
    if not isinstance(snapshot.get("observed_date"), str) or len(snapshot["observed_date"]) != 10:
        raise ValueError("date-scoped observation required")
    registered = registry.get("items")
    if not isinstance(registered, list) or len(registered) != 10:
        raise ValueError("registry must contain exactly ten families")
    expected = {}
    for row in registered:
        fid = row["id"]
        base = row["active_baseline"]
        if fid in expected or not isinstance(base.get("artifact_size_bytes"), int):
            raise ValueError("duplicate family or missing selected artifact size")
        expected[fid] = (base["artifact_name"], base["artifact_size_bytes"])
    entries = snapshot.get("entries")
    if not isinstance(entries, list) or len(entries) != len(expected) * len(PROVIDERS):
        raise ValueError("expected two provider observations per family")
    seen = set()
    rows = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("entry must be an object")
        fid, provider, obs = entry.get("family_id"), entry.get("provider"), entry.get("observation")
        key = (fid, provider)
        if fid not in expected or provider not in PROVIDERS or key in seen:
            raise ValueError("unknown, missing or duplicate provider/family")
        seen.add(key)
        if obs not in set(OBSERVED.values()) | OTHER:
            raise ValueError("unsupported observation status: " + str(obs))
        if "sha256_of_bytes" in entry and entry["sha256_of_bytes"] not in ("NOT_REMEASURED", None):
            raise ValueError("metadata-only observation cannot claim a binary checksum")
        expected_name, expected_size = expected[fid]
        classification = "NOT_CHECKED"
        if obs == OBSERVED.get(provider):
            if not isinstance(entry.get("provider_item_id"), str) or not entry["provider_item_id"]:
                raise ValueError("provider locator needed for observed metadata")
            if (entry.get("name") != expected_name
                    or type(entry.get("size_bytes")) is not int
                    or entry["size_bytes"] != expected_size):
                classification = "METADATA_MISMATCH_REVIEW"
            else:
                classification = "METADATA_NAME_SIZE_MATCH__BYTES_UNCHECKED"
        elif obs in OBSERVED.values():
            raise ValueError("provider and observation kind mismatch")
        elif obs == "NOT_OBSERVED_IN_SCANNED_FOLDERS":
            if provider != "library" or not entry.get("scanned_relative_folders"):
                raise ValueError("scoped folder non-observation requires Library + scan scope")
            classification = "NOT_SEEN_IN_SCOPED_FOLDER__NOT_PROOF_OF_DELETION"
        elif obs == "RETIRED_WITH_PRIOR_OWNER_AUTHORIZATION":
            if provider != "library" or not entry.get("owner_cleanup_receipt_path"):
                raise ValueError("retired item must have owner cleanup receipt")
            classification = "OWNER_AUTHORIZED_LIBRARY_RETIREMENT__DRIVE_BACKUP_SEPARATE"
        rows.append({"family_id": fid, "provider": provider,
                     "classification": classification,
                     "expected_name": expected_name, "expected_size_bytes": expected_size,
                     "observed_name": entry.get("name"),
                     "observed_size_bytes": entry.get("size_bytes"),
                     "observation": obs, "observed_date": snapshot["observed_date"],
                     "content_sha256_remeasured": False})
    if seen != {(fid, prov) for fid in expected for prov in PROVIDERS}:
        raise ValueError("missing family/provider pair")
    counts = Counter(x["classification"] for x in rows)
    return rows, dict(sorted(counts.items()))


def reconcile(root: Path, observation_path: Path | None = None) -> dict:
    root = root.resolve()
    registry = read_object(root / REGISTRY)
    snapshot = read_object(observation_path or root / SNAPSHOT)
    rows, counts = check_observations(registry, snapshot)
    status = "METADATA_MISMATCH_REVIEW" if counts.get("METADATA_MISMATCH_REVIEW") else "METADATA_ONLY_PARTIAL_PROVIDER_VISIBILITY"
    return {"schema": "gfp-opt-portfolio-provider-reconciliation@1.0.0",
            "observed_date": snapshot["observed_date"], "report_generated_from": "RECORDED_CONNECTOR_OBSERVATIONS",
            "status": status, "provider_access_in_ci": False,
            "not_evidence_of": ["current provider live status at later execution",
                                "SHA256 or ZIP byte validation",
                                "global file deletion or full Library crawl",
                                "new owner-user acceptance or release promotion",
                                "native Stage6, app UI, SRS or FSRS correctness"],
            "counts": counts, "items": rows}


def markdown(report: dict) -> str:
    result = ["# Portfolio providers — historical metadata replay", "",
              "**Observation date:** " + report["observed_date"],
              "**Status:** " + report["status"], "",
              "| Family | Provider | Classification |",
              "|---|---|---|"]
    for item in report["items"]:
        result.append("| " + item["family_id"] + " | " + item["provider"]
                      + " | " + item["classification"] + " |")
    result.extend(["", "A GitHub CI PASS on this snapshot is **not live Library/Drive access**.",
                   "Name+size metadata is **not** independent file SHA256/CRC proof.",
                   "Not found in a scanned folder is **not proof of deletion**.",
                   "No candidate or release is promoted by this script.", ""])
    return "\n".join(result)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--observations", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--github-summary", action="store_true")
    parser.add_argument("--fail-on-mismatch", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = reconcile(args.repo_root, args.observations)
        if args.out_dir:
            root, out = args.repo_root.resolve(), args.out_dir.resolve()
            if out.is_relative_to(root):
                raise ValueError("reports inside source repository are forbidden")
            out.mkdir(parents=True, exist_ok=True)
            (out / "PROVIDER-RECONCILIATION.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (out / "PROVIDER-RECONCILIATION.md").write_text(markdown(report), encoding="utf-8")
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fp:
                fp.write(markdown(report))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2 if args.fail_on_mismatch and report["status"] == "METADATA_MISMATCH_REVIEW" else 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID_PROVIDER_SNAPSHOT_HOLD",
                          "reason": type(exc).__name__ + ": " + str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
