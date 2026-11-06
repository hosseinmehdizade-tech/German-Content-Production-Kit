#!/usr/bin/env python3
"""Read-only GCPK gate: every producer workspace references one file-lifecycle law."""
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER="FILE_LIFECYCLE_RULE_V1_0_0"
POLICY="Library-Organization/FILE-LIFECYCLE-AND-SAFE-CLEANUP-v1.0.0.md"
SCHEMA="Library-Organization/FILE-LIFECYCLE-REGISTER-SCHEMA-v1.0.0.json"
def main():
    errors=[]
    policy=ROOT/POLICY
    if not policy.is_file():errors.append("MISSING_GLOBAL_POLICY")
    else:
        s=policy.read_text(encoding="utf-8")
        for x in ("Must run without a user reminder","Only after exact provider Library write/readback","Never delete automatically","every existing","future workspaces"):
            if x.lower() not in s.lower():errors.append("POLICY_CLAUSE_MISSING:"+x)
    p=ROOT/SCHEMA
    if not p.is_file():errors.append("NO_ARTIFACT_REGISTRY_SCHEMA")
    else:
        d=json.loads(p.read_text(encoding="utf8"))
        if d.get("policy")!=POLICY or not d.get("deletion_gate",{}).get("user_specific_authorization_required"):
            errors.append("REGISTRY_NOT_SAFE")
    for x in ("Prompt/START-PROMPT-v3.3.6.md","Prompt/NEW-SOURCE-AGENTIC-RUNBOOK-v1.0.0.md","Workspaces/README.md"):
        f=ROOT/x
        if not f.is_file() or MARKER not in f.read_text(encoding="utf8") or POLICY not in f.read_text(encoding="utf8"):
            errors.append("STARTUP_POINTER_MISSING:"+x)
    ws=ROOT/"Workspaces"
    projects=sorted(x for x in ws.iterdir() if x.is_dir() and not x.name.startswith("."))
    if not projects:errors.append("WORKSPACES_NOT_FOUND")
    for folder in projects:
        a=folder/"FILE-LIFECYCLE-RULE.md"
        if not a.is_file():errors.append("LOCAL_RULE_MISSING:"+folder.name);continue
        s=a.read_text(encoding="utf8")
        if MARKER not in s or POLICY not in s or "explicitly user-approved" not in s:
            errors.append("LOCAL_RULE_INCOMPLETE:"+folder.name)
    if errors:
        print(json.dumps({"status":"BLOCKED_MISSING_RULE","errors":errors,"workspace_count":len(projects)},ensure_ascii=False,indent=2))
        return 2
    print(json.dumps({"status":"PASS_ALL_WORKSPACES_REFER_TO_ONE_FILE_LIFECYCLE_POLICY","workspaces":len(projects),"policy":POLICY,"deletion_authorization":"EXPLICIT_USER_APPROVAL_ONLY"}))
    return 0
if __name__=="__main__":sys.exit(main())
