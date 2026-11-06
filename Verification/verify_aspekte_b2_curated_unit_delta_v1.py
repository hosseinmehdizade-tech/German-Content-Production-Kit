#!/usr/bin/env python3
"""Read-only native B2 lesson-1 curated-current successor gate.

Use the CURRENT working CSV and its immediate curated parent from B2 Library,
NEVER the user's original publisher/source vocabulary as an output-equality test.
This verifies exact bytes, card identity, scoped deltas, draft safety and source
ordinal *coverage* only. It cannot certify DE/FA semantics, Stage2, Stage4–7
or the installed app, and never writes or promotes a card.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys

MAX_BYTES = 25_000_000
REQUIRED = {
    "unit_id", "source_ordinals", "source_ids", "front_de_preview",
    "back_fa_preview", "example_1_de", "example_1_fa",
    "example_2_de", "example_2_fa", "export_importable",
    "linguistic_release_approved", "qa_status", "POS_or_unit_type",
    "unit_policy", "prior_card_link"
}
IDENTITY = {
    "unit_id", "source_ordinals", "source_ids", "prior_card_link",
    "POS_or_unit_type", "unit_policy", "source_example_count_in_original_R42"
}
LANGUAGE = {"front_de_preview", "back_fa_preview", "example_1_de",
            "example_1_fa", "example_2_de", "example_2_fa"}


class CuratedB2Error(ValueError):
    pass


def demand(ok, code):
    if not ok:
        raise CuratedB2Error(code)


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def read_exact(path, expected_sha):
    path = Path(path)
    demand(path.is_file() and not path.is_symlink(), "CURATED_FILE_MISSING_OR_SYMLINK")
    demand(0 < path.stat().st_size <= MAX_BYTES, "INVALID_CURATED_FILE_SIZE")
    body = path.read_bytes()
    demand(re.fullmatch(r"[0-9a-f]{64}", str(expected_sha or "")) is not None,
           "MISSING_CURATED_SHA_PIN")
    demand(sha(body) == expected_sha, "CURRENT_OR_PARENT_SHA256_MISMATCH")
    return body


def parse_rows(blob, id_field):
    try:
        text = blob.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        names = reader.fieldnames or []
        demand(id_field in names and len(names) == len(set(names))
               and all(names), "MISSING_OR_DUPLICATED_HEADER")
        out = list(reader)
        demand(all(None not in row and None not in row.values()
                   and row.get(id_field) and row[id_field].strip() == row[id_field]
                   for row in out), "MALFORMED_OR_BLANK_CURATED_ROW")
        keys = [x[id_field] for x in out]
        demand(len(keys) == len(set(keys)), "DUPLICATE_UNIT_ID")
        return {x[id_field]: x for x in out}, set(names)
    except (UnicodeError, csv.Error) as e:
        raise CuratedB2Error("INVALID_UTF8_OR_CSV") from e


def scope_contract(latest):
    scope = latest.get("latest_scoped_audit", {})
    demand(isinstance(scope, dict), "B2_LATEST_SCOPE_NOT_OBJECT")
    label = str(scope.get("label", ""))
    match = re.match(r"^L01_R([1-9][0-9]*)_", label)
    demand(match is not None, "NOT_A_L01_CURATED_SCOPED_SUCCESSOR")
    revision = int(match.group(1))
    parents = [(int(m.group(1)), value) for key, value in scope.items()
               if (m := re.fullmatch(r"parent_R([1-9][0-9]*)_158_current_sha256",
                                     key))]
    demand(len(parents) == 1 and parents[0][0] == revision - 1,
           "MISSING_IMMEDIATE_ACCEPTED_CURATED_PARENT_PIN")
    curr_path = str(scope.get("current_158_draft_preview_path", ""))
    demand(curr_path.startswith("/Flasch kart/German-Content-Production-Kit/"
                               "Content/Aspekte-B2/Current/")
           and curr_path.endswith(f"-R{revision}-NONIMPORT.csv"),
           "CURATED_CURRENT_PATH_NOT_OWNER_LOCAL_OR_NONIMPORT")
    demand(scope.get("draft_unique_ids") == 158
           and scope.get("source_rows_coverage") == 160,
           "L01_UNIT_AND_COVERAGE_COUNTER_INVALID")
    demand(scope.get("importable") is False and
           scope.get("stage2_approved") is False and
           scope.get("imported_cards") == 0 and
           scope.get("stage3_to_stage7") == "NOT_STARTED",
           "FALSE_APPROVAL_OR_IMPORT_CLAIM")
    demand(str(scope.get("global_portable_project_checkpoint", "")).startswith("L05_R25_"),
           "SCOPED_L01_CONFUSED_WITH_GLOBAL_L05")
    demand(bool(scope.get("noncard_2_current_path", "")).endswith("-NONIMPORT.csv")
           and "/Aspekte-B2/Current/" in scope["noncard_2_current_path"],
           "NONCARD_OWNER_OR_DRAFT_BOUNDARY_MISSING")
    demand(scope.get("identity_or_target_HOLDs") and
           scope.get("R44_legacy_HOLDs", 0) >= 17,
           "RELEASE_HOLDS_SILENTLY_DROPPED")
    for key in ("current_158_draft_preview_sha256", "noncard_2_current_sha256"):
        demand(re.fullmatch(r"[0-9a-f]{64}", str(scope.get(key, ""))) is not None,
               "UNPINNED_CURRENT_ARTIFACT:"+key)
    return scope, revision, parents[0][1]


def ordinal_tokens(rows):
    result = []
    for row in rows.values():
        val = row.get("source_ordinals", row.get("source_ordinal", ""))
        for part in val.split(";"):
            demand(part.strip().isdigit(), "INVALID_SOURCE_ORDINAL")
            result.append(int(part))
    return result


def audit(latest, parent_file, current_file, noncard_file):
    """Verify only the 158-unit *current vs accepted predecessor*, plus 2 noncards."""
    scope, rev, parent_sha = scope_contract(latest)
    demand(Path(current_file).name == Path(scope["current_158_draft_preview_path"]).name,
           "CURRENT_FILENAME_NOT_LATEST")
    demand(Path(noncard_file).name == Path(scope["noncard_2_current_path"]).name,
           "NONCARD_FILENAME_NOT_LATEST")
    pbytes = read_exact(parent_file, parent_sha)
    cbytes = read_exact(current_file, scope["current_158_draft_preview_sha256"])
    nbytes = read_exact(noncard_file, scope["noncard_2_current_sha256"])
    before, bheader = parse_rows(pbytes, "unit_id")
    current, cheader = parse_rows(cbytes, "unit_id")
    noncard, _ = parse_rows(nbytes, "object_id")
    demand(bheader == cheader and REQUIRED <= cheader,
           "CURATED_SCHEMA_DROPPED_OR_CHANGED")
    demand(set(before) == set(current) and len(current) == 158,
           "PROVISIONAL_UNIT_IDS_OR_CARD_COUNT_CHANGED")
    demand(len(noncard) == 2, "NONCARD_CONTENT_OBJECTS_DROPPED")
    for row in current.values():
        demand(all(row.get(key, "").strip() for key in LANGUAGE),
               "CURATED_BILINGUAL_CONTENT_BLANKED")
        demand(row["export_importable"] == "FALSE"
               and row["linguistic_release_approved"] == "FALSE",
               "UNAPPROVED_CARD_MARKED_IMPORTABLE")
    for row in noncard.values():
        demand(row.get("importable") == "FALSE"
               and row.get("release_approved") == "FALSE",
               "NONCARD_MARKED_IMPORTABLE")
        demand(all(row.get(k, "").strip() for k in
                   ("source_ordinal","source_id","front_de_current","back_fa_current",
                    "example_1_de","example_1_fa","example_2_de","example_2_fa")),
               "NONCARD_SOURCE_OR_BILINGUAL_CONTENT_LOST")
    changed = {}
    field_count = 0
    for ident in sorted(current):
        old, new = before[ident], current[ident]
        delta = sorted(key for key in bheader if old[key] != new[key])
        demand(not (set(delta) & IDENTITY), "CURATED_IDENTITY_OR_PROVENANCE_CHANGED:" + ident)
        demand("export_importable" not in delta and
               "linguistic_release_approved" not in delta,
               "CURATED_RELEASE_BOUNDARY_CHANGED:" + ident)
        demand(all(not old[k].strip() or new[k].strip() for k in bheader),
               "PREVIOUS_ACCEPTED_FIELD_BLANKED:" + ident)
        if delta:
            changed[ident] = delta
            field_count += len(delta)
    demand(len(changed) == scope.get("modified_unit_count") and
           field_count == scope.get("modified_field_count") and
           len(current) - len(changed) == scope.get("unchanged_unit_count"),
           "DELTA_COUNTS_DISAGREE_WITH_CURRENT_POINTER")
    coverage = ordinal_tokens(current) + [
        int(x["source_ordinal"]) for x in noncard.values()]
    demand(set(coverage) == set(range(1549,1709)),
           "SOURCE_TO_CURATED_UNIT_COVERAGE_REGRESSION")
    # Splitting a lexical unit can repeat a source ordinal; this is NOT
    # duplicate card membership. A source ordinal must not disappear.
    return {
        "status": "PASS_SCOPED_CURATED_PARENT_TO_CURRENT_DELTA_ONLY_NOT_SEMANTIC_OR_RELEASE",
        "project": "aspekte-b2", "lesson": 1, "current_revision": rev,
        "source_comparison": "NONE__USER_CURATED_PARENT_ONLY",
        "previous_curated_sha256": sha(pbytes),
        "current_curated_sha256": sha(cbytes),
        "noncard_sha256": sha(nbytes),
        "new_or_deleted_unit_ids": 0, "current_provisional_units": len(current),
        "unchanged_units": len(current) - len(changed),
        "changed_units": len(changed), "changed_fields": field_count,
        "changed_field_names": dict(changed),
        "covered_source_ordinals": len(set(coverage)),
        "noncard_supplementary_objects": len(noncard),
        "legacy_release_holds": scope["R44_legacy_HOLDs"],
        "independent_language_qa": "NOT_PROVEN",
        "formal_stage2_approval": False,
        "stage5_import": "NOT_AUTHORIZED",
        "stage6_runtime": "NOT_RUN", "stage7_final": "NOT_RUN",
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--latest", type=Path, required=True)
    p.add_argument("--previous-curated", type=Path, required=True)
    p.add_argument("--current-curated", type=Path, required=True)
    p.add_argument("--noncard", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        latest=json.loads(args.latest.read_text(encoding="utf-8"))
        result=audit(latest, args.previous_curated, args.current_curated,
                     args.noncard)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status":"BLOCKED", "reason":str(exc)},ensure_ascii=False))
        return 2
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
