#!/usr/bin/env python3
"""OP-02 historical Menschen A2-L24: read-only proof SHA and combo crosswalk.

No learner text/registered-source bytes are sent to Git. The JSON report stores
stable card IDs, exact SHA-256 and risk labels, not verbatim source sentences.
A risk flag is NOT an error/deletion decision, nor Stage4/Stage5/Stage6 PASS.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

REFERENCE_SHA = "9aa0f362de767b5e4046b81952a3d01e6aaa74305a5bb8d93930dabe7ee3a595"
REFERENCE_MEMBER = "20-Stage3C/REVIEWED-EDITORIAL-155.json"
STAGE4_MEMBER = "27-Stage4/REVIEWED-EDITORIAL-155.json"
STAGE4_REPAIR_LEDGER = "27-Stage4/EXACT-REPAIR-LEDGER.json"
PROOF_MEMBER = "20-Stage3C/ENRICHMENT-COMPLETENESS-STAGE3C.json"
STAGE3B_EDITORIAL = "14-Stage3B/ENRICHED-CANONICAL-EDITORIAL-155.json"
SCHEMA = "gcpk-op02-a2-l24-shadow-evidence-crosswalk@1"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def jbytes(data) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def inspect_archive(path: Path, expected_sha: str) -> tuple[dict[str, bytes], str]:
    if not HEX64.fullmatch(expected_sha):
        raise ValueError("EXPECTED_SHA256_REQUIRED")
    if sha(path.read_bytes()) != expected_sha:
        raise ValueError("ARCHIVE_AUTHORITY_MISMATCH")
    with zipfile.ZipFile(path) as z:
        inf = z.infolist()
        names = [i.filename for i in inf]
        if (len(inf) > 400 or len(names) != len(set(names)) or
                sum(i.file_size for i in inf) > 60_000_000 or
                any(i.file_size > 8_000_000 or i.is_dir() or
                    n.startswith("/") or "\\" in n or
                    any(v in (".", "..") for v in PurePosixPath(n).parts)
                    for i, n in zip(inf, names))):
            raise ValueError("UNSAFE_OR_DUPLICATE_ARCHIVE")
        if z.testzip() is not None:
            raise ValueError("ARCHIVE_CRC_FAILURE")
        payloads = {i.filename: z.read(i.filename) for i in inf}
    return payloads, expected_sha


def resolve_reference(archives: dict[str, dict[str, bytes]],
                      reference: str, expected_path: str) -> dict:
    if not HEX64.fullmatch(reference):
        raise ValueError("MALFORMED_REFERENCE_SHA")
    matches = []
    paths = {}
    for stage, contents in archives.items():
        paths[stage] = sha(contents[expected_path]) if expected_path in contents else None
        for path, data in contents.items():
            if sha(data) == reference:
                matches.append({"stage": stage, "path": path})
    resolved = bool(matches)
    return {
        "status": "RESOLVED_BY_EXACT_ARCHIVED_BYTES" if resolved
                  else "UNRESOLVED_ACROSS_AVAILABLE_ARCHIVES",
        "reference_sha256": reference,
        "referenced_path": expected_path,
        "exact_sha_at_referenced_path_by_archive": paths,
        "matches": matches,
        "not_a_content_error_proof": True,
    }


def normalize(s: str) -> str:
    return " ".join(re.findall(r"[\w]+", s.casefold(), flags=re.UNICODE))


def audit_combinations(stage3: dict, stage4: dict, repairs: list[dict]) -> dict:
    p3 = stage3.get("authored_targets", [])
    p4 = stage4.get("authored_targets", [])
    if not isinstance(p3, list) or not isinstance(p4, list):
        raise ValueError("MALFORMED_AUTHORED_TARGETS")
    ids3 = [x.get("id") for x in p3]
    ids4 = [x.get("id") for x in p4]
    if (len(ids3) != len(set(ids3)) or len(ids4) != len(set(ids4))
            or set(ids3) != set(ids4)):
        raise ValueError("STAGE3C_STAGE4_CARD_ID_DRIFT")
    lookup = {c["id"]: c for c in p3}
    repaired = {(x.get("id"), x.get("field")) for x in repairs
                if isinstance(x, dict) and
                str(x.get("field", "")).startswith("kombinationen[")}
    crosswalk, errors = [], []
    risk_counts = Counter()
    stage4_count = 0
    for card in p4:
        before = lookup[card["id"]]
        prev = before.get("kombinationen", [])
        curr = card.get("kombinationen", [])
        if not isinstance(prev, list) or not isinstance(curr, list):
            raise ValueError("MALFORMED_COMBINATIONS")
        if len(curr) != len(prev):
            errors.append("COUNT_CHANGED_SINCE_STAGE3C: " + card["id"])
        examples = [normalize(e.get("de", "")) for e in card.get("examples", [])]
        for index, item in enumerate(curr):
            if not isinstance(item, dict):
                errors.append("NON_OBJECT_ITEM: " + card["id"])
                continue
            stage4_count += 1
            predecessor = prev[index] if index < len(prev) else None
            phrase = normalize(item.get("de", ""))
            if not phrase or not all(isinstance(item.get(f), str) and
                                    item[f].strip() for f in ("de", "fa", "en")):
                errors.append("INCOMPLETE_TRILINGUAL_COMBO: " + card["id"])
            provenance = item.get("provenance")
            missing_provenance = not isinstance(provenance, str) or not provenance.strip()
            delta = item.get("teaching_delta")
            delta_present = ((isinstance(delta, dict) and bool(delta)) or
                             (isinstance(delta, str) and bool(delta.strip())) or
                             item.get("teaching_delta_verified") is True)
            exact = any(phrase == e for e in examples if phrase)
            phrase_in_example = any(phrase in e for e in examples if phrase)
            normalized_dup = sum(normalize(x.get("de", "")) == phrase
                                 for x in curr if isinstance(x, dict)) > 1
            tracked = (card["id"], f"kombinationen[{index}]") in repaired
            changed = predecessor is None or jbytes(predecessor) != jbytes(item)
            risks = []
            if missing_provenance:
                risks.append("MISSING_ITEM_PROVENANCE")
            if not delta_present:
                risks.append("NO_ITEM_LEVEL_TEACHING_DELTA")
            if exact:
                risks.append("EXACT_WHOLE_EXAMPLE")
            elif phrase_in_example:
                risks.append("COMPLETE_PHRASE_IN_EXAMPLE")
            if normalized_dup:
                risks.append("DUPLICATE_SAME_CARD")
            if changed and not tracked:
                risks.append("UNTRACKED_STAGE4_ITEM_CHANGE")
            risk_counts.update(risks)
            crosswalk.append({
                "card_id": card["id"], "index": index,
                "source_row": card.get("source_row"),
                "source_registered_hash": card.get("registered_source_hash"),
                "stage3c_item_sha256": sha(jbytes(predecessor)) if predecessor is not None else None,
                "stage4_item_sha256": sha(jbytes(item)),
                "provenance_kind": provenance if provenance else "MISSING",
                "item_provenance_present": not missing_provenance,
                "item_teaching_delta_evidence_present": delta_present,
                "same_card_example_match": (
                    "EXACT_WHOLE_EXAMPLE" if exact else
                    "COMPLETE_PHRASE_IN_EXAMPLE" if phrase_in_example else "NONE"
                ),
                "changed_since_stage3c": changed,
                "matching_stage4_repair_record": tracked,
                "risk_codes": risks,
                "pedagogical_adjudication": "NOT_INDEPENDENTLY_REVIEWED_IN_THIS_AUDIT",
            })
    return {
        "source_card_count": len(p4),
        "stage3c_combo_count": sum(len(x.get("kombinationen", [])) for x in p3),
        "stage4_combo_count": stage4_count,
        "comparison_errors": errors,
        "flag_counts": dict(sorted(risk_counts.items())),
        "provenance_count": sum(c["item_provenance_present"] for c in crosswalk),
        "teaching_delta_documented_count": sum(
            c["item_teaching_delta_evidence_present"] for c in crosswalk),
        "crosswalk": crosswalk,
        "scope_note": "Risk codes demand bounded independent pedagogical review; no automatic DROP or FIX.",
    }


def audit(stage3b: dict[str, bytes], stage3c: dict[str, bytes],
          stage4: dict[str, bytes]) -> dict:
    archives = {"Stage3B": stage3b, "Stage3C": stage3c, "Stage4": stage4}
    required = (REFERENCE_MEMBER, PROOF_MEMBER)
    if any(name not in stage3c or name not in stage4 for name in required):
        raise ValueError("STAGE3C_HISTORICAL_MEMBERS_MISSING")
    if STAGE4_MEMBER not in stage4 or STAGE4_REPAIR_LEDGER not in stage4:
        raise ValueError("STAGE4_MEMBERS_MISSING")
    completeness = json.loads(stage3c[PROOF_MEMBER])
    claimed = completeness["summary"]["stage3c_editorial_sha256"]
    if not HEX64.fullmatch(claimed):
        raise ValueError("INVALID_STAGE3C_CLAIMED_SHA")
    refs = []
    for target in completeness["targets"]:
        for cell in target["dimensions"].values():
            refs.extend(x for x in cell.get("basis_refs", [])
                        if isinstance(x, dict) and
                        x.get("path") == REFERENCE_MEMBER and x.get("artifact_sha256"))
    references = Counter(x["artifact_sha256"] for x in refs)
    digests = resolve_reference(archives, claimed, REFERENCE_MEMBER)
    matches = [x for x in refs if x["artifact_sha256"] !=
               sha(stage3c[REFERENCE_MEMBER])]
    stage3_cards = json.loads(stage3c[REFERENCE_MEMBER])
    stage4_cards = json.loads(stage4[STAGE4_MEMBER])
    repairs = json.loads(stage4[STAGE4_REPAIR_LEDGER])
    combos = audit_combinations(stage3_cards, stage4_cards, repairs)
    identical_inherited = {n: sha(stage3c[n]) == sha(stage4[n])
                           for n in stage3c.keys() & stage4.keys()}
    return {
        "schema": SCHEMA,
        "scope": "HISTORICAL_A2_L24_2026_10_18_ONLY__READ_ONLY",
        "reference_resolution": digests,
        "stage3c_summary_claimed_sha": claimed,
        "stage3c_summary_reference_count": sum(references.values()),
        "stage3c_reference_sha_counts": dict(references),
        "stage3c_basis_refs_not_matching_own_member": len(matches),
        "stage3c_member_hash_identical_in_stage4": identical_inherited[REFERENCE_MEMBER],
        "unchanged_inherited_stage3c_files": sum(identical_inherited.values()),
        "total_inherited_stage3c_files": len(identical_inherited),
        "combinations": combos,
        "outcome": "PROVENANCE_AND_DIDACTIC_EVIDENCE_UNRESOLVED",
        "limits": [
            "Verified archive member hashes do not establish historical authoring intent.",
            "No source text or learner phrase is serialized in report; only stable IDs/hash evidence.",
            "No SHA reference was rewritten or backfilled automatically.",
            "No independent linguistic Stage4 or learner teaching_delta approval.",
            "Stage5/6/7 and runtime/UI remain separate and unchanged.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    for stage in ("stage3b", "stage3c", "stage4"):
        parser.add_argument("--" + stage, required=True, type=Path)
        parser.add_argument("--" + stage + "-sha256", required=True)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    try:
        archives = {}
        for stage in ("stage3b", "stage3c", "stage4"):
            archives[stage], _ = inspect_archive(
                getattr(args, stage), getattr(args, stage + "_sha256"))
        result = audit(archives["stage3b"], archives["stage3c"], archives["stage4"])
        result["archives"] = {key: {"sha256": getattr(args, key + "_sha256"),
                                     "members": len(contents)}
                              for key, contents in archives.items()}
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        with args.report.open("x", encoding="utf-8") as handle:
            handle.write(payload)
        print(json.dumps({"outcome": result["outcome"], "report": str(args.report),
                          "items": result["combinations"]["stage4_combo_count"],
                          "reference": result["reference_resolution"]["status"]}))
        return 0
    except (KeyError, ValueError, OSError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"outcome": "BLOCKED", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
