#!/usr/bin/env python3
"""OP-02 NONACTIVE Stage5 transport→CURRENT v486-R120 visible combination bridge.

Companion to validate_stage45_teaching_delta_parity.py, never an active
builder/runtime adapter or a replacement for true Stage6 browser acceptance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_stage45_teaching_delta_parity import (
    SCHEMA as STAGE45_SCHEMA, STATUS, load_tsv, read_json, canonical,
    verify as verify_stage45, sha, hexsha,
)

SCHEMA = "gcpk-stage45-v486-consumer-bridge@1"
RUNTIME = "v486-R120"
RUNTIME_SHA = "d00c111743eea695e2f5e7a847b0330a0eb74479fd6733396fa062ac222bdeff"
VIEW_FUNCTION = "presentationProjectedDetailsV459"
READ_FUNCTION = "universalRawFromRow"


def german_kombination_detail(title: Any) -> bool:
    if not isinstance(title, str):
        return False
    return "kombination" in title.strip().casefold()


def expected_v486_visible(items: list[dict]) -> list[str]:
    out = []
    for item in items:
        de = item.get("de", "").strip()
        fa = item.get("fa", "").strip()
        if not de:
            continue
        out.append((de + " — " + fa) if fa else de)
    return out


def validate(stage45_contract: dict, bridge_contract: dict,
             stage4_bytes: bytes, review_bytes: bytes, stage5_bytes: bytes):
    problems: list[str] = []
    if (not isinstance(bridge_contract, dict)
            or bridge_contract.get("schema") != SCHEMA
            or bridge_contract.get("status") != STATUS
            or bridge_contract.get("runtime_version") != RUNTIME
            or bridge_contract.get("runtime_sha256") != RUNTIME_SHA
            or bridge_contract.get("presentation_function") != VIEW_FUNCTION
            or bridge_contract.get("tsv_parser_function") != READ_FUNCTION
            or not hexsha(bridge_contract.get("stage5_tsv_sha256"))
            or bridge_contract["stage5_tsv_sha256"] != sha(stage5_bytes)):
        return {"status": "BLOCKED", "errors": ["EXACT_NONACTIVE_V486_PROFILE_OR_INPUT_NOT_PINNED"]}
    source_gate = verify_stage45(stage45_contract, stage4_bytes,
                                 review_bytes, stage5_bytes)
    if source_gate.get("status") != "PASS_SCOPED_DETERMINISTIC_PARITY_ONLY":
        return {"status": "BLOCKED", "errors": [
            "UNDERLYING_STAGE45_CONTENT_INTEGRITY_BLOCKED", *source_gate.get("errors", [])]}
    try:
        rows = load_tsv(stage5_bytes)
        stage4 = read_json(stage4_bytes)
    except (ValueError, UnicodeError, TypeError) as exc:
        return {"status": "BLOCKED", "errors": ["INVALID_BRIDGE_INPUT:" + str(exc)]}
    count=0
    closed=0
    for row, card in zip(rows, stage4["cards"]):
        cid = row["id"]
        items = card["kombinationen"]
        if not isinstance(items, list):
            problems.append("INVALID_STAGE4_COMBINATIONS:" + cid)
            continue
        try:
            cf = read_json(row["custom_fields"].encode("utf-8"))
            if not isinstance(cf, dict):
                raise ValueError("custom_fields must be object")
        except (ValueError, UnicodeError, TypeError) as exc:
            problems.append("MALFORMED_STAGE5_FIELDS:" + cid + ":" + str(exc))
            continue
        if "kombinationenV1" in cf:
            problems.append("DUAL_CAMEL_AND_SNAKE_BRIDGE_ALIAS_FORBIDDEN:" + cid)
        if "kombinationen_v1" not in cf:
            if items:
                problems.append("MISSING_V486_VISIBLE_COMBINATION_BRIDGE:" + cid)
            else:
                closed+=1
            continue
        view = cf["kombinationen_v1"]
        if not isinstance(view, dict):
            problems.append("V486_BRIDGE_NOT_OBJECT:" + cid)
            continue
        visible = view.get("visible_section") or view.get("visibleSection")
        if visible != "Kombinationen":
            problems.append("V486_VISIBLE_SECTION_SELECTOR_MISMATCH:" + cid)
        presented = view.get("items")
        if not isinstance(presented, list) or canonical(presented) != canonical(items):
            problems.append("V486_BRIDGE_ITEMS_LOSS_OR_MUTATION:" + cid)
        expected=expected_v486_visible(items)
        if len(expected) != len(items):
            problems.append("V486_VISIBLE_DE_TEXT_MISSING:" + cid)
        count+=len(items)
        if not items:
            closed+=1
        if "details" not in row or not row.get("details"):
            continue
        try:
            details=read_json(row["details"].encode("utf-8"))
        except (ValueError, UnicodeError, TypeError):
            problems.append("UNPARSEABLE_EXISTING_DETAILS_FOR_V486:" + cid)
            continue
        if not isinstance(details, list):
            problems.append("EXISTING_DETAILS_NOT_ARRAY:" + cid)
            continue
        existing = [x for x in details if isinstance(x, dict)
                    and german_kombination_detail(x.get("title"))]
        if len(existing)>1:
            problems.append("MULTIPLE_PREEXISTING_COMBINATION_SECTIONS:" + cid)
        elif existing:
            prior=existing[0].get("items")
            if prior and prior != expected:
                problems.append("STALE_DETAILS_OVERRIDE_V486_BRIDGE:" + cid)
        # Additional legacy Kollokationen sections can create competing
        # learner-visible families. Report for review, never auto-delete.
        coll=[x for x in details if isinstance(x,dict) and
              any(t in str(x.get("title","")).casefold()
                  for t in ("kollok", "colloc", "nvv")) and x.get("items")]
        if coll and items:
            problems.append("DUPLICATE_VISIBLE_COLLLOCATION_FAMILY_RISK:" + cid)
    return {
        "schema": "gcpk-stage45-v486-consumer-bridge-result@1",
        "status": "PASS_SCOPED_DETERMINISTIC_CONSUMER_PROFILE_ONLY" if not problems else "BLOCKED",
        "errors": sorted(set(problems)),
        "counts": {"visible_stage4_items": count, "closed_no_force_cards": closed,
                   "cards": len(stage4["cards"])},
        "not_proven": [
            "Current v486 importer/storage/IndexedDB end-to-end round trip",
            "Live browser DOM verification in Study/Quick modes or mobile",
            "Independent AI linguistic Stage4 review or original source correctness",
            "Official Stage5/6/7 acceptance, active-schema adoption or new UI",
        ],
    }


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    for arg in ("stage45-contract", "bridge-contract", "stage4",
                "stage4-review", "stage5-tsv"):
        ap.add_argument("--"+arg, required=True, type=Path)
    args=ap.parse_args()
    try:
        a=json.loads(args.stage45_contract.read_text(encoding="utf-8"))
        b=json.loads(args.bridge_contract.read_text(encoding="utf-8"))
        result=validate(a,b,args.stage4.read_bytes(),args.stage4_review.read_bytes(),
                        args.stage5_tsv.read_bytes())
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        result={"status": "BLOCKED", "errors":["INPUT_UNREADABLE:"+str(exc)]}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result.get("status")=="PASS_SCOPED_DETERMINISTIC_CONSUMER_PROFILE_ONLY" else 2


if __name__=="__main__":
    raise SystemExit(main())
