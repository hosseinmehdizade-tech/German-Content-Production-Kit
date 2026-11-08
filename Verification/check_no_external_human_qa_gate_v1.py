#!/usr/bin/env python3
"""Read-only central linguistic QA authority guard (MEM-031).

Does not assign Stage4 PASS, import cards, or inspect private learner SRS.
Fail-closed when a mandatory external-human reviewer silently reappears.
"""
import argparse
import json
from pathlib import Path

POLICY = "LINGUISTIC-QA-AUTHORITY-POLICY.json"
REGISTRY = "Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
B2_GATE = "Workspaces/aspekte-b2-v336/QA/B2-CENTRAL-QUALITY-GATE-v1.py"
DECISION = "MEM-031-AI-AND-USER-LINGUISTIC-QA-NO-EXTERNAL-HUMAN-GATE"
FORBIDDEN_B2_GATES = (
    "INDEPENDENT_DEFA_QA_NOT_SIGNED",
    "L01_EDITORIAL_COLLOCATION_INDEPENDENT_SIGNOFF_PENDING",
    "EXTERNAL_HUMAN_REVIEWER_REQUIRED",
    "QUALIFIED_EXTERNAL_APPROVAL_REQUIRED",
)


def check(root: Path) -> list[str]:
    problems = []
    try:
        policy = json.loads((root / POLICY).read_text(encoding="utf-8"))
        reg = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
        checker = (root / B2_GATE).read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        return ["POLICY_OR_CHECKER_MISSING_OR_INVALID: " + str(error)]

    if policy.get("status") != "USER_APPROVED_ACTIVE" or policy.get("decision_id") != DECISION:
        problems.append("CENTRAL_USER_DECISION_NOT_ACTIVE")
    if "Remove mandatory external qualified-human signature" not in policy.get("authority", ""):
        problems.append("CENTRAL_NO_EXTERNAL_HUMAN_INSTRUCTION_MISSING")
    stage4 = policy.get("stage4_method", {})
    roles = stage4.get("roles", {})
    if "ChatGPT" not in roles.get("linguistic_editor", "") or not roles.get("adjudicator", "").startswith("ChatGPT"):
        problems.append("AI_AND_USER_REVIEW_ROLES_MISSING")
    if not any("AI-review, not external human" in rule for rule in stage4.get("mandatory_pass_gates", [])):
        problems.append("HONEST_AI_QA_LABEL_REQUIRED")
    if "Stage5 complete content-production delivery" not in "\n".join(stage4.get("mandatory_pass_gates", [])):
        problems.append("TECHNICAL_RUNTIME_GATES_CANNOT_BE_DROPPED")
    binding = reg.get("policy_bindings", {}).get("linguistic_qa", {})
    if binding.get("path") != POLICY or binding.get("scope") != "LINGUISTIC_REVIEW":
        problems.append("CENTRAL_POLICY_BINDING_CHANGED")
    guard = reg.get("protected_invariants", {}).get("no_mandatory_external_human_linguistic_QA_reviewer")
    if guard is not True:
        problems.append("CENTRAL_ANTI_REGRESSION_INVARIANT_MISSING")
    if reg.get("reviewer_authority_resolution", {}).get("external_human_signature_required") is not False:
        problems.append("CENTRAL_EXPLICIT_EXTERNAL_GATE_WAIVER_MISSING")

    for marker in FORBIDDEN_B2_GATES:
        if marker in checker:
            problems.append("B2_REINTRODUCED_EXTERNAL_HUMAN_GATE:" + marker)
    if '"external_human_reviewer_required":False' not in checker:
        problems.append("B2_MISSING_NO_EXTERNAL_GATE_CONTRACT")
    if "AI_LINGUISTIC_QA_EVIDENCE_PENDING" not in checker:
        problems.append("B2_AI_CONTENT_QUALITY_GATE_LOST")
    if "LIVE_ACCEPTED_SRS_ID_NOT_VERIFIED" not in checker:
        problems.append("B2_SRS_IDENTITY_GATE_LOST")
    if "NATIVE_APP_TEST_NOT_RUN" not in checker:
        problems.append("B2_NATIVE_APP_GATE_LOST")
    return problems


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = cli.parse_args()
    issues = check(args.root)
    result = {"policy": DECISION, "pass": not issues, "issues": issues,
              "scope": "ACTIVE_CENTRAL_QA_AUTHORITY_AND_B2_GENERATOR_ONLY",
              "stage4_semantic_approved": False,
              "native_app_srs_tested": False}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if issues else 0)


if __name__ == "__main__":
    main()
