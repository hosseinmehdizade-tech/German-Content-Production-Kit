#!/usr/bin/env python3
"""OP-02 historical A2 L24 Stage1→Stage2→Stage3 actual-card read-only audit.

No registered source, LOCKED, learner cards, checkpoints or app are modified.
A source/identity PASS is NOT Stage3 didactic PASS, independent Stage4, or Stage5–7.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

ROOT = "gcpk-op02-a2-l24-actual-card-lineage@1"
FILES = {
    "source": "01-Source-Inventory/A2-L24-SOURCE-OCCURRENCES.json",
    "stubs": "02-Canonical-Data/A2-L24-CANONICAL-STUBS.json",
    "edges": "03-Source-to-Canonical/A2-L24-MAPPING-EDGES.json",
    "decisions": "03-Source-to-Canonical/A2-L24-DECISIONS-ALL-SOURCE.json",
    "reuse": "04-Historical-Parent-Audit/A2-L24-EXACT-IMMUTABLE-REUSE-SNAPSHOTS.json",
    "stage3": "20-Stage3C/REVIEWED-EDITORIAL-155.json",
    "ledger": "20-Stage3C/DIMENSION-DISPOSITION-LEDGER.json",
    "completeness": "20-Stage3C/ENRICHMENT-COMPLETENESS-STAGE3C.json",
    "stage4": "27-Stage4/REVIEWED-EDITORIAL-155.json",
}
EXPECTED = {
    "source_rows": 117, "canonical_targets": 163, "new_authored": 155,
    "locked_reuse": 8, "dimension_cells": 2651, "trilingual_examples": 620,
    "trilingual_combinations": 64,
}
HEX = re.compile(r"^[0-9a-f]{64}$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspect_zip(path: Path, expected_sha256: str | None = None) -> dict[str, bytes]:
    if expected_sha256 and digest(path.read_bytes()) != expected_sha256:
        raise ValueError("ARCHIVE_SHA256_NOT_EXPECTED_AUTHORITY")
    payloads: dict[str, bytes] = {}
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [e.filename for e in entries]
        if (len(names) != len(set(names)) or len(names) > 500 or
                any(e.is_dir() or e.file_size > 12_000_000 for e in entries) or
                sum(e.file_size for e in entries) > 75_000_000 or
                any(n.startswith("/") or "\\" in n or
                    any(part in ("..", ".") for part in PurePosixPath(n).parts)
                    for n in names)):
            raise ValueError("UNSAFE_OR_OVERSIZED_ARCHIVE")
        if archive.testzip() is not None:
            raise ValueError("ZIP_CRC_FAILURE")
        payloads = {name: archive.read(name) for name in names}
    if not {"MANIFEST.json", "SHA256SUMS", *FILES.values()} <= payloads.keys():
        raise ValueError("MISSING_ARCHIVE_EVIDENCE")
    try:
        summary = json.loads(payloads["MANIFEST.json"])
        recorded = summary["files"]
        if set(recorded) != set(payloads) - {"MANIFEST.json", "SHA256SUMS"}:
            raise ValueError("MANIFEST_MEMBER_INVENTORY_DRIFT")
        for name, meta in recorded.items():
            if meta["sha256"] != digest(payloads[name]) or meta["bytes"] != len(payloads[name]):
                raise ValueError("MANIFEST_SHA_OR_SIZE_DRIFT: " + name)
        claims: dict[str, str] = {}
        for line in payloads["SHA256SUMS"].decode("utf-8").splitlines():
            m = re.fullmatch(r"([a-f0-9]{64})  (.+)", line)
            if not m or m[2] in claims:
                raise ValueError("SHA256SUMS_MALFORMED_OR_DUPLICATE")
            claims[m[2]] = m[1]
        if claims != {name: digest(data) for name, data in payloads.items()
                      if name != "SHA256SUMS"}:
            raise ValueError("SHA256SUMS_DRIFT")
    except (KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("INVALID_MANIFEST_FORMAT") from exc
    return payloads


def keyed(items: list[dict], key: str, errors: list[str], label: str) -> dict:
    result = {}
    for item in items:
        if not isinstance(item, dict) or item.get(key) in result or not item.get(key):
            errors.append(label + ": duplicate/missing identity")
            continue
        result[item[key]] = item
    return result


def audit_payloads(payloads: dict[str, bytes], strict_legacy: bool = True) -> dict:
    source_errors: list[str] = []
    evidence_errors: list[str] = []
    data = {label: json.loads(payloads[name]) for label, name in FILES.items()}
    src = keyed(data["source"]["occurrences"], "occurrence_id", source_errors, "source")
    rows = keyed(
        [{"row": item["locator"]["row"], **item} for item in src.values()],
        "row", source_errors, "source-row")
    stubs = keyed(data["stubs"], "id", source_errors, "canonical")
    edges = keyed(data["edges"], "target_id", source_errors, "edge")
    decisions = keyed(data["decisions"], "source_row", source_errors, "decision")
    reuse = keyed(data["reuse"], "id", source_errors, "LOCKED")
    authored = keyed(data["stage3"]["authored_targets"], "id", source_errors, "Stage3")
    reviewed = keyed(data["stage4"]["authored_targets"], "id", source_errors, "Stage4")
    completeness = keyed(data["completeness"]["targets"], "id", source_errors, "complete")
    closure = data["completeness"]["summary"]
    d = {}
    ledger = data["ledger"]
    for cell in ledger:
        pair = (cell.get("target_id"), cell.get("dimension"))
        if pair in d or not all(pair):
            source_errors.append("dimension ledger duplicate or orphan key")
        d[pair] = cell
    if set(stubs) != set(edges) or set(stubs) != set(completeness):
        source_errors.append("Stage2/Stage3 identity union mismatch")
    if (set(authored) | set(reuse)) != set(stubs) or set(authored) & set(reuse):
        source_errors.append("new/LOCKED partition mismatch")
    if set(reviewed) != set(authored):
        source_errors.append("Stage4 lost or added authored target")
    row_targets = defaultdict(set)
    for target, edge in edges.items():
        sr = edge["source_row"]
        row_targets[sr].add(target)
        original, stub = rows.get(sr), stubs.get(target)
        if original is None or stub is None:
            source_errors.append("orphan source/canonical target: " + target)
            continue
        comparison = {
            "source_hash": (edge.get("source_hash"), original["source_row_payload_sha256"]),
            "source_occurrence_id": (edge.get("source_occurrence_id"), original["occurrence_id"]),
            "canonical_hash": (stub.get("source_hash"), edge.get("source_hash")),
            "canonical_row": (stub.get("source_row"), sr),
            "canonical_raw_de": (stub.get("source_immutable_raw_learnable"), original["raw_text"]),
            "canonical_raw_fa": (stub.get("source_seed_fa"), original["raw_definition_fa"]),
            "canonical_raw_example": (stub.get("source_example_de"), original["raw_example_de"]),
            "canonical_audio": (stub.get("source_audio_refs"), original["media_refs"]),
            "edge_audio": (edge.get("source_audio_tags"), original["media_refs"]),
        }
        for field, (left, right) in comparison.items():
            if left != right:
                source_errors.append(target + ": " + field + " drift")
        kind = edge.get("binding_kind")
        if (kind == "NEW_TARGET") != (target in authored) or (
                kind == "IMMUTABLE_REUSE") != (target in reuse):
            source_errors.append(target + ": binding kind/LOCKED mismatch")
        if target in authored and target in reviewed:
            for label, card in (("Stage3", authored[target]), ("Stage4", reviewed[target])):
                mapping = {
                    "row": (card.get("source_row"), sr),
                    "hash": (card.get("registered_source_hash"),
                             original["source_row_payload_sha256"]),
                    "raw_de": (card.get("registered_source_label_exact"), original["raw_text"]),
                    "raw_fa": (card.get("registered_source_fa_gloss_exact"),
                               original["raw_definition_fa"]),
                    "raw_example": (card.get("registered_source_example_de_exact"),
                                    original["raw_example_de"]),
                    "audio": (card.get("audio_file_references"), original["media_refs"]),
                }
                for field, (left, right) in mapping.items():
                    if left != right:
                        source_errors.append(label + " " + target + ": " + field + " drift")
    if set(rows) != set(decisions):
        source_errors.append("source decision row inventory mismatch")
    for row, ids in row_targets.items():
        decision = decisions.get(row)
        if not decision:
            continue
        actual = [x["target_id"] for x in decision["target_dispositions"]]
        if len(actual) != len(set(actual)) or set(actual) != ids:
            source_errors.append("decision/edge exact target mismatch: " + str(row))
        original = rows[row]
        if (decision.get("source_hash") != original["source_row_payload_sha256"] or
                decision.get("source_text_unchanged") != original["raw_text"] or
                decision.get("source_fa_seed_unchanged") != original["raw_definition_fa"]):
            source_errors.append("source decision original facts changed: " + str(row))
    observed_status = Counter()
    for target, comp in completeness.items():
        stub = stubs.get(target)
        if not stub:
            continue
        if comp.get("source_ordinals") != [stub["source_row"]]:
            source_errors.append("Stage3 source ordinal drift: " + target)
        for dim, value in comp["dimensions"].items():
            pair = (target, dim)
            observed_status[value.get("status")] += 1
            if pair not in d or d[pair].get("status") != value.get("status"):
                source_errors.append("ledger/completeness cell mismatch: " + str(pair))
    expected_pairs = {(t, dimension) for t, comp in completeness.items()
                      for dimension in comp["dimensions"]}
    if set(d) != expected_pairs:
        source_errors.append("completeness/ledger exact coverage mismatch")
    if (closure.get("targets") != len(completeness) or
            closure.get("dimension_cells") != len(d) or
            closure.get("status_counts") != dict(observed_status) or
            closure.get("unresolved_cells") != 0):
        source_errors.append("Stage3C completion counters/holds mismatch")
    if data["completeness"].get("canonical_sha256") != digest(payloads[FILES["stubs"]]):
        source_errors.append("Stage2 canonical captured bytes mismatch")
    examples = [e for card in reviewed.values() for e in card.get("examples", [])]
    combos = [x for card in reviewed.values() for x in card.get("kombinationen", [])]
    for card in reviewed.values():
        if len(card.get("examples", [])) != 4:
            source_errors.append("Stage4 example count mismatch: " + card["id"])
        for e in card.get("examples", []):
            if not all(isinstance(e.get(k), str) and e[k].strip() for k in ("de", "fa", "en")):
                source_errors.append("incomplete trilingual example: " + card["id"])
            if e.get("provenance") != "MODEL_EDITORIAL_AUTHORSHIP_NOT_SOURCE_VERBATIM":
                source_errors.append("Stage4 example falsely attributed: " + card["id"])
        for item in card.get("kombinationen", []):
            if not all(isinstance(item.get(k), str) and item[k].strip()
                       for k in ("de", "fa", "en")):
                source_errors.append("incomplete trilingual combination: " + card["id"])
    metrics = {
        "source_rows": len(rows), "canonical_targets": len(stubs),
        "new_authored": len(authored), "locked_reuse": len(reuse),
        "dimension_cells": len(ledger), "trilingual_examples": len(examples),
        "trilingual_combinations": len(combos),
        "stage3c_verified_present": observed_status.get("VERIFIED_PRESENT", 0),
        "stage3c_closed_no_force": observed_status.get("CLOSED_NO_FORCE", 0),
    }
    if strict_legacy:
        for name, number in EXPECTED.items():
            if metrics[name] != number:
                source_errors.append(name + ": historical expected count drift")

    # Never infer proof hashes from a self-authored summary. Resolve exact bytes.
    stale_refs = Counter()
    for card in completeness.values():
        for facet in card.get("dimensions", {}).values():
            for ref in facet.get("basis_refs", []):
                if ref.get("artifact_sha256"):
                    referent = ref.get("path")
                    actual = digest(payloads[referent]) if referent in payloads else None
                    if actual != ref["artifact_sha256"]:
                        stale_refs[(referent, ref["artifact_sha256"], actual)] += 1
    editorial_path = FILES["stage3"]
    current_editorial_sha = digest(payloads[editorial_path])
    declared_editorial_sha = closure.get("stage3c_editorial_sha256")
    if current_editorial_sha != declared_editorial_sha:
        evidence_errors.append("STAGE3C_SUMMARY_EDITORIAL_SHA_NOT_PRESENT_MEMBER")
    if stale_refs:
        evidence_errors.append("STAGE3C_BASIS_REFS_NOT_BOUND_TO_ARCHIVED_BYTES")
    teaching_delta = sum(isinstance(x.get("teaching_delta"), dict) or
                         x.get("teaching_delta_verified") is True for x in combos)
    explicit_provenance = sum(isinstance(x.get("provenance"), str) and
                              bool(x["provenance"].strip()) for x in combos)
    if teaching_delta != len(combos):
        evidence_errors.append("COMBINATION_ITEM_LEVEL_TEACHING_DELTA_NOT_DOCUMENTED")
    if explicit_provenance != len(combos):
        evidence_errors.append("COMBINATION_ITEM_LEVEL_PROVENANCE_ABSENT")

    return {
        "schema": ROOT,
        "source_identity_result": "PASS_SCOPED" if not source_errors else "BLOCKED",
        "semantic_evidence_result": "PASS_RECORD_PROOF_ONLY" if not evidence_errors
                                    else "BLOCKED_RECORD_EVIDENCE_ONLY",
        "source_errors": source_errors,
        "evidence_errors": evidence_errors,
        "counts": metrics,
        "evidence": {
            "stage3c_editorial_archived_sha256": current_editorial_sha,
            "stage3c_completeness_claimed_editorial_sha256": declared_editorial_sha,
            "stale_basis_reference_count": sum(stale_refs.values()),
            "distinct_stale_references": len(stale_refs),
            "teaching_delta_item_count": teaching_delta,
            "combination_provenance_item_count": explicit_provenance,
            "combination_total": len(combos),
        },
        "limits": [
            "Only one historical ZIP; not newest mutable A2 authority.",
            "This source check is internal Stage1 slice and checkpoint lineage, not an independent original RAR extraction.",
            "This does not assess pedagogical or linguistic correctness.",
            "Never silently change historical source, LOCKED cards, Stage3C or Stage4 receipts.",
            "No Stage4/5/6/7 promotion, HF2 rendering or CURRENT app acceptance.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        payloads = inspect_zip(args.archive, args.expected_sha256)
        report = audit_payloads(payloads, strict_legacy=True)
        report["archive_sha256"] = digest(args.archive.read_bytes())
        report["zip_member_count"] = len(payloads)
    except (ValueError, KeyError, TypeError, zipfile.BadZipFile, OSError) as exc:
        report = {"schema": ROOT, "source_identity_result": "BLOCKED",
                  "semantic_evidence_result": "BLOCKED", "errors": [str(exc)]}
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.write_text(output, encoding="utf-8")
    print(output)
    return 0 if (report.get("source_identity_result") == "PASS_SCOPED"
                 and report.get("semantic_evidence_result") == "PASS_RECORD_PROOF_ONLY") else 2


if __name__ == "__main__":
    raise SystemExit(main())
