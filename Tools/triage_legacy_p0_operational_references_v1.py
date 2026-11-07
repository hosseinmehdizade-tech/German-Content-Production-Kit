#!/usr/bin/env python3
"""Evidence-level triage of P0 legacy inbound references; no edits or auto-deletion.

Only a live, direct runtime test can establish whether a reference is executed.
This enumerates exact Git HEAD match locations (line/snippet) and distinguishes
executable-looking references, QA/test examples, and immutable provenance.
"""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
BASE=HERE/"audit_legacy_workspace_dependencies_v1.py"
spec=importlib.util.spec_from_file_location("legacy_git_audit_base",BASE)
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

ROUTING=base.ROUTING
HISTORIC="Optimization-Program/Control-Center/Legacy-Dependencies/2026-11-07-PR146-GIT-REFERENCE-SNAPSHOT.json"
SCHEMA="gcpk-legacy-p0-reference-evidence@1.0.0"
SOURCE_EXT={".py",".js",".mjs",".cjs",".ts",".tsx",".jsx",".sh",".ps1",".bat",".cmd",".rb"}
CI_EXT={".yml",".yaml"}
DOC_EXT={".md",".rst",".txt",".json",".jsonl",".tsv",".csv",".html"}
OPERAND_RE=re.compile(r"\b(?:Path\s*\(|open\s*\(|read_text\s*\(|read_bytes\s*\(|write_text\s*\(|"
    r"load\s*\(|exists\s*\(|is_file\s*\(|glob\s*\(|subprocess|git\s+(?:show|grep)|"
    r"source\s+|import\s+|cp\s+|mv\s+|rm\s+|--(?:input|source|path|root|file))",re.I)

def path_boundary(pattern: str) -> re.Pattern[bytes]:
    return re.compile(re.escape(pattern.encode("utf-8"))+rb"(?![A-Za-z0-9_.-])")

def source_bucket(source: str, text_line: str) -> str:
    p=Path(source)
    line=text_line.strip()
    if source.startswith(("Verification/tests/","Tests/")):
        return "TEST_OR_REGRESSION_EVIDENCE_NOT_RUNTIME_PROOF"
    if p.suffix in CI_EXT and source.startswith(".github/workflows/"):
        return "CI_DECLARATION_REVIEW_REQUIRED"
    if p.suffix in SOURCE_EXT and source.startswith((".github/","Tools/","Verification/")):
        if line.startswith(("#","//","*")):
            return "CODE_COMMENT_OR_DOCUMENTARY_STRING"
        if OPERAND_RE.search(line):
            return "EXECUTABLE_PATH_OPERAND_CANDIDATE__VERIFY_CALLSITE"
        return "SOURCE_CODE_TEXT_REFERENCE__VERIFY_CALLSITE"
    if source.startswith("Workspaces/") and p.suffix in SOURCE_EXT:
        if OPERAND_RE.search(line):
            return "CANONICAL_OR_LEGACY_SCRIPT_PATH_OPERAND__VERIFY_CALLSITE"
        return "WORKSPACE_SOURCE_CODE_REFERENCE__VERIFY_CALLSITE"
    if source.startswith("Workspaces/"):
        return "WORKSPACE_CHECKPOINT_OR_LINEAGE_REFERENCE"
    if source.startswith("Optimization-Program/"):
        return "GOVERNANCE_OR_REPORT_REFERENCE"
    if source.endswith(".md") or p.suffix in DOC_EXT:
        return "DOCUMENT_OR_HISTORICAL_PROVENANCE_REFERENCE"
    return "UNCLASSIFIED_REFERENCE_REVIEW_REQUIRED"

def relevant(root: Path):
    raw=json.loads((root/HISTORIC).read_text(encoding="utf8"))
    if raw.get("schema")!="gcpk-legacy-git-reference-baseline@1.0.0":
        raise ValueError("Wrong vetted legacy dependency snapshot")
    rows=raw.get("rows",[])
    p0=[x for x in rows if x.get("priority","").startswith("P0_")]
    if len(rows)!=20 or len(p0)!=10:
        raise ValueError("Unexpected P0 baseline count; rebaseline explicitly, not silently")
    mapping=json.loads((root/ROUTING).read_text(encoding="utf8"))
    legacy={x["git_dir"]:x for x in mapping["workspaces"] if x["role"]=="COMPATIBILITY_LEGACY"}
    targets=[]
    for row in p0:
        key="Workspaces/"+row["workspace_id"].split("workspace:",1)[-1]
        if key not in legacy or legacy[key]["family_id"]!=row["family_id"]:
            raise ValueError("P0 baseline no longer matches canonical family/role")
        targets.append((key,legacy[key]["future_accepted_current_pointer_location"],row))
    return targets

def analyze(root: Path) -> dict:
    root=root.resolve()
    targets=relevant(root)
    paths=[x[0] for x in targets]
    candidate_sources=base.paths_with_literal_refs(root,paths)
    by_source={}
    edges=[]
    for source in candidate_sources:
        if source==ROUTING:
            continue
        # Read the Git object, not CRLF-normalized checkout files.
        raw=base.git(root,["show","HEAD:"+source])
        if b"\0" in raw:
            continue  # Binary refs are outside this text-only audit.
        lines=raw.splitlines()
        by_source[source]=lines
    for legacy,canonical,row in targets:
        regex=path_boundary(legacy)
        recs=[]
        for source, lines in sorted(by_source.items()):
            if source.startswith(legacy+"/"):
                continue # Self-reference is not an inbound dependency.
            hits=[]
            for n,raw_line in enumerate(lines,1):
                match=regex.search(raw_line)
                if not match:
                    continue
                txt=raw_line.decode("utf8","replace")
                # Truncate around exact matched term, not randomly at start of
                # a huge one-line JSON source record.
                center=len(raw_line[:match.start()].decode("utf8","replace"))
                clip=txt[max(0,center-100):min(len(txt),center+len(legacy)+120)].strip()
                kind=source_bucket(source,txt)
                hits.append({"line":n,"kind":kind,"excerpt":clip[:350]})
            if hits:
                recs.append({
                    "referencer":source,
                    "reference_class":base.classify(source,set(x[1] for x in targets),set(x[0] for x in targets)),
                    "occurrences":len(hits),
                    "samples":hits[:8],
                    "truncated_at_eight_samples":len(hits)>8,
                    "runtime_execution_proven":False,
                })
        raw_types=Counter(hit["kind"] for referer in recs for hit in referer["samples"])
        code_candidates=[x for x in recs if any(h["kind"] in (
            "EXECUTABLE_PATH_OPERAND_CANDIDATE__VERIFY_CALLSITE",
            "SOURCE_CODE_TEXT_REFERENCE__VERIFY_CALLSITE",
            "CI_DECLARATION_REVIEW_REQUIRED",
            "CANONICAL_OR_LEGACY_SCRIPT_PATH_OPERAND__VERIFY_CALLSITE",
            "WORKSPACE_SOURCE_CODE_REFERENCE__VERIFY_CALLSITE")
            for h in x["samples"])]
        edges.append({
            "family_id":row["family_id"],"legacy_workspace":legacy,
            "canonical_future_task_target":canonical,
            "baseline_exact_inbound_file_count":row["literal_inbound_reference_file_count"],
            "observed_source_file_count":len(recs),
            "source_file_count_changed_since_baseline":len(recs)!=row["literal_inbound_reference_file_count"],
            "runtime_or_active_import_proven":False,
            "execution_candidate_source_files":len(code_candidates),
            "execution_candidate_paths":[x["referencer"] for x in code_candidates],
            "sampled_line_types":dict(sorted(raw_types.items())),
            "inbound_referencers":recs,
            "decision":"PRESERVE_LEGACY__REVIEW_EXECUTION_CANDIDATES__NO_LINK_REWRITE",
        })
    return {
        "schema":SCHEMA,
        "status":"P0_EVIDENCE_TRIAGE_COMPLETE__EXECUTION_NOT_ATTESTED",
        "git_head":base.git(root,["rev-parse","HEAD"]).decode("ascii").strip(),
        "scope":"TEN_P0_LEGACY_WORKSPACES__EXACT_COMMITTED_GIT_TEXT_PATHS",
        "counters":{
            "p0_workspaces":len(edges),
            "p0_inbound_source_file_edges":sum(x["observed_source_file_count"] for x in edges),
            "p0_execution_candidate_referencer_files":sum(x["execution_candidate_source_files"] for x in edges),
            "p0_workspaces_with_execution_candidate":sum(x["execution_candidate_source_files"]>0 for x in edges),
            "p0_baseline_changed":sum(x["source_file_count_changed_since_baseline"] for x in edges),
        },
        "limits":[
            "Code syntax evidence is only a callsite candidate; runtime execution cannot be proved by textual Git grep.",
            "Git HEAD files only. Private Library/Drive ZIPs, user app runtime, untracked files, indirect imports and binary contents excluded.",
            "Line snippets may be partial; all old paths and SHA-bound source-owner receipts must be preserved.",
            "No source pointer promotion, physical relocation, deletion, FSRS or app/UI change.",
        ],
        "workspaces":edges,
    }

def markdown(report: dict) -> str:
    ls=["# P0 Legacy Workspace — callsite evidence triage","",
        "**No active execution is attested by these text matches.**", "",
        "| Preserved legacy | Inbound tracked files | Executable/CI code-file leads |",
        "| --- | ---: | ---: |"]
    for row in report["workspaces"]:
        ls.append("| `"+row["legacy_workspace"]+"` | "+str(row["observed_source_file_count"])+" | "+str(row["execution_candidate_source_files"])+" |")
    ls+=["","Any executable/CI lead needs source-level review plus native run evidence before rewriting a reference.",
           "No archive deletion, no reference rewriting, no automatic content change.",""]
    return "\n".join(ls)

def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out-dir",type=Path)
    ap.add_argument("--github-summary",action="store_true")
    args=ap.parse_args(argv)
    try:
        report=analyze(args.repo_root)
        if args.out_dir:
            out=args.out_dir.resolve()
            if out.is_relative_to(args.repo_root.resolve()):
                raise ValueError("Cannot write derived evidence into source checkout")
            out.mkdir(parents=True,exist_ok=True)
            (out/"P0-LEGACY-REFERENCE-EVIDENCE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
            (out/"P0-LEGACY-REFERENCE-EVIDENCE.md").write_text(markdown(report),encoding="utf8")
        if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
                f.write(markdown(report))
        print(json.dumps({
            "status":report["status"],"git_head":report["git_head"],"counters":report["counters"],
            "workspaces":[{"workspace":w["legacy_workspace"],"inbound":w["observed_source_file_count"],
                "candidate_code_paths":w["execution_candidate_paths"],
                "candidate_count":w["execution_candidate_source_files"]} for w in report["workspaces"]]
        },ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError,UnicodeError) as e:
        print(json.dumps({"status":"HOLD_P0_REFERENCE_EVIDENCE","reason":type(e).__name__+": "+str(e)[:350]}))
        return 2

if __name__=="__main__":
    sys.exit(main())
