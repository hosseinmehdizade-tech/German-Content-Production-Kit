#!/usr/bin/env python3
"""Validate a substantial-work outcome receipt (not language or runtime quality)."""
from __future__ import annotations
import json
import pathlib
import sys

SCHEMA = "flashcards-work-outcome-receipt@1.0.0"
STATES = {"PASS", "CLOSED", "BLOCKED", "IN_PROGRESS"}

def valid_nonnegative_int(value):
    return type(value) is int and value >= 0

def validate(document):
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    if not isinstance(document, dict):
        return ["root must be a JSON object"]
    check(document.get("schema") == SCHEMA, "schema must match " + SCHEMA)
    check(isinstance(document.get("workstream"), str) and bool(document.get("workstream", "").strip()), "workstream must identify a named stream")
    milestone = document.get("milestone", {})
    scope = document.get("scope", {})
    progress = document.get("progress", {})
    quality = document.get("quality", {})
    persistence = document.get("persistence", {})
    for name, obj in [("milestone", milestone), ("scope", scope), ("progress", progress), ("quality", quality), ("persistence", persistence)]:
        check(isinstance(obj, dict), name + " must be an object")
    if errors:
        return errors
    state = milestone.get("state")
    check(state in STATES, "milestone.state must be PASS/CLOSED/BLOCKED/IN_PROGRESS")
    check(isinstance(milestone.get("name"), str) and bool(milestone.get("name", "").strip()), "milestone.name required")
    check(milestone.get("level") in ("major", "substep"), "milestone.level must be major or substep")
    total = scope.get("total_units")
    reviewed = progress.get("reviewed_unique")
    unreviewed = progress.get("unreviewed")
    dispositions = progress.get("dispositions")
    check(isinstance(scope.get("unit"), str) and bool(scope.get("unit", "").strip()), "scope.unit required")
    check(valid_nonnegative_int(total), "scope.total_units must be nonnegative integer")
    check(valid_nonnegative_int(reviewed), "progress.reviewed_unique must be nonnegative integer")
    check(valid_nonnegative_int(unreviewed), "progress.unreviewed must be nonnegative integer")
    check(isinstance(dispositions, dict) and bool(dispositions), "progress.dispositions must be a nonempty status:count map")
    if isinstance(dispositions, dict):
        check(all(isinstance(k, str) and bool(k.strip()) and valid_nonnegative_int(v) for k,v in dispositions.items()), "disposition counts must be nonnegative integers")
    if valid_nonnegative_int(total) and valid_nonnegative_int(reviewed) and valid_nonnegative_int(unreviewed):
        check(reviewed + unreviewed == total, "accounting mismatch: reviewed_unique + unreviewed != total_units")
    if isinstance(dispositions, dict) and valid_nonnegative_int(reviewed) and all(valid_nonnegative_int(v) for v in dispositions.values()):
        check(sum(dispositions.values()) == reviewed, "accounting mismatch: disposition counts != reviewed_unique")
    stage_complete = quality.get("stage_complete")
    check(type(stage_complete) is bool, "quality.stage_complete must be boolean")
    check(isinstance(quality.get("verification_evidence"), list), "quality.verification_evidence must be array")
    check(persistence.get("git") in ("IN_SYNC", "PENDING", "FAILED", "NOT_REQUIRED"), "persistence.git must have a declared status")
    if state in ("PASS", "CLOSED"):
        check(milestone.get("level") == "major", "substep or small edit batch cannot be declared full PASS/CLOSED")
        check(stage_complete is True, "PASS/CLOSED requires explicit stage_complete=true")
        check(unreviewed == 0, "PASS/CLOSED requires all bounded work units dispositioned")
        check(bool(quality.get("verification_evidence")), "PASS/CLOSED requires verification evidence")
    if state == "IN_PROGRESS":
        check(stage_complete is False, "IN_PROGRESS cannot claim stage_complete")
        check(isinstance(persistence.get("resume_pointer"), str) and bool(persistence.get("resume_pointer", "").strip()), "IN_PROGRESS requires exact resume_pointer")
    if state == "BLOCKED":
        check(isinstance(milestone.get("blocker"), str) and bool(milestone.get("blocker", "").strip()), "BLOCKED requires actionable blocker")
        check(isinstance(persistence.get("resume_pointer"), str) and bool(persistence.get("resume_pointer", "").strip()), "BLOCKED requires resume_pointer")
    return errors

def main(argv):
    if len(argv) != 2:
        print("usage: validate_execution_outcome_receipt.py <outcome-receipt.json>", file=sys.stderr)
        return 2
    try:
        doc = json.loads(pathlib.Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        print("FAIL cannot read valid JSON: " + str(exc), file=sys.stderr)
        return 2
    errs = validate(doc)
    if errs:
        for err in errs:
            print("FAIL " + err, file=sys.stderr)
        return 1
    print("PASS outcome-accounting/major-milestone guard only; official content/runtime QA remains separate")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
