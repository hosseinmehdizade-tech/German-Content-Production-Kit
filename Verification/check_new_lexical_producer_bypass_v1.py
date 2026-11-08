#!/usr/bin/env python3
"""Prevent NEW executable producer bypasses of the source-owned lexical gate.

Historical scripts are preserved; only ADDED executable lines in the compared
commit range can introduce a new bypass. Format-only regression tests live in
Verification and remain valid. Does not prove branch protection or semantic QA.
"""
from __future__ import annotations
import argparse,json,re,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
# Deliberately exact filenames, not arbitrary "stage5" substrings.
UNGUARDED=(
    re.compile(r"\bbuild_clean_delivery\.py\b",re.I),
    re.compile(r"\bbuild_front_gated_clean_delivery_v1\.py\b",re.I),
    re.compile(r"\bbuild_governed_clean_delivery_v1\.py\b",re.I),
    re.compile(r"\bpackage_release(?:_corrective)?\.py\b",re.I),
    re.compile(r"\bguarded_zip\s*\(",re.I),
)
EXTS={".py",".sh",".bash",".yml",".yaml"}

def git(root,*args):
    p=subprocess.run(["git",*args],cwd=root,capture_output=True,text=True,encoding="utf-8")
    if p.returncode:raise ValueError("GIT_DIFF_FAILED:"+p.stderr[-250:])
    return p.stdout

def scope(path):
    p=Path(path)
    return (p.suffix.lower() in EXTS and
            (path.startswith("Tools/") or path.startswith("Workspaces/") or
             path.startswith(".github/workflows/")) and
            "/tests/" not in path and not p.name.startswith("test_"))

def added_lines(root,base,head,path):
    # Any edit to a legacy script is allowed if it doesn't add an invocation.
    # A new/updated "source" selector with no legacy reference is also allowed.
    diff=git(root,"diff","--unified=0","--no-ext-diff",base,head,"--",path)
    return [line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]

def inspect(root,base,head):
    changes=git(root,"diff","--name-only","--diff-filter=AMR",base,head,"--",
                "Tools","Workspaces",".github/workflows").splitlines()
    hits=[]
    for path in changes:
        if not scope(path):continue
        for line in added_lines(root,base,head,path):
            if not line.strip() or line.lstrip().startswith(("#","//","*")):continue
            for old in UNGUARDED:
                if old.search(line):
                    hits.append({"path":path,"legacy_entrypoint":old.pattern,
                                 "added_line":line.strip()[:220]})
    if hits:
        raise ValueError("NEW_UNGATED_LEXICAL_PRODUCER_REFERENCE:"+json.dumps(hits[:12],ensure_ascii=False))
    return {"schema":"gcpk-prospective-no-new-legacy-producer-bypass@1.0.0",
            "status":"PASS_NO_NEW_UNGATED_PRODUCTION_ENTRYPOINT_REFERENCES",
            "code_files_compared":len([p for p in changes if scope(p)]),
            "scope":"ADDED_EXECUTABLE_LINES_ONLY__HISTORICAL_WRAPPERS_PRESERVED"}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base",required=True)
    parser.add_argument("--head",default="HEAD")
    args=parser.parse_args()
    try:print(json.dumps(inspect(ROOT,args.base,args.head),ensure_ascii=False))
    except (ValueError,OSError) as exc:
        print("PROSPECTIVE_PRODUCER_BYPASS_BLOCKED:"+str(exc),file=sys.stderr)
        return 2
    return 0
if __name__=="__main__":raise SystemExit(main())
