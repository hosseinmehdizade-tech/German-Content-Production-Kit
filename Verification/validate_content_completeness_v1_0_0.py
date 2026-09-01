#!/usr/bin/env python3
"""Product-content completeness gate for GFP German canonical datasets.
Exit 0 PASS, 1 hard completeness FAIL, 2 input/configuration error.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path

ABSENT = (None, "", [], {})

def load_json(path):
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def as_list(v): return v if isinstance(v, list) else []

def verified_claims(unit):
    out=set()
    for src in as_list((unit.get("provenance") or {}).get("sources")):
        if not isinstance(src,dict) or src.get("verification_status") != "verified": continue
        for claim in as_list(src.get("what_was_verified")):
            if isinstance(claim,str) and claim.strip(): out.add(claim.strip().lower())
    return out

def claim_satisfied(claims, accepted): return any(str(x).lower() in claims for x in accepted)
def issue(severity,code,path,message): return {"severity":severity,"code":code,"path":path,"message":message}
def count_nonempty_strings(v): return sum(1 for x in as_list(v) if isinstance(x,str) and x.strip())

def connections_by_kind(unit):
    c=Counter()
    for x in as_list(unit.get("connections")):
        if isinstance(x,dict) and isinstance(x.get("kind"),str) and str(x.get("text","")).strip(): c[x["kind"]]+=1
    return c

def validate_unit(unit,idx,rule):
    import re
    issues=[]; uid=unit.get("id",f"index-{idx}"); root=f"learning_units[{idx}]({uid})"
    core=unit.get("core") if isinstance(unit.get("core"),dict) else {}
    details=unit.get("details") if isinstance(unit.get("details"),dict) else {}
    claims=verified_claims(unit)
    for f in rule.get("required_core_fields",[]):
        if f not in core or core.get(f) in ABSENT:
            issues.append(issue("error","COMPLETENESS_REQUIRED_FIELD",f"{root}.core.{f}","Required learner content is absent."))
    for cond in rule.get("conditional_requirements",[]):
        if re.search(cond["if_headword_regex"],str(unit.get("headword","")),flags=re.I):
            field=cond["detail_field"]
            if count_nonempty_strings(details.get(field)) < int(cond.get("minimum",1)):
                issues.append(issue("error","COMPLETENESS_CONDITIONAL_MINIMUM",f"{root}.details.{field}",cond.get("message") or "Conditional content requirement is not met."))
    counts=connections_by_kind(unit)
    for spec in rule.get("connections",[]):
        kind=spec["kind"]; found=counts.get(kind,0); minimum=int(spec.get("minimum",0)); preferred=int(spec.get("preferred_minimum",0)); maximum=spec.get("maximum")
        if found < minimum: issues.append(issue("error","COMPLETENESS_MINIMUM",f"{root}.connections.{kind}",f"Required minimum is {minimum}; found {found}."))
        elif found < preferred: issues.append(issue("warning","COMPLETENESS_PREFERRED_MISSING",f"{root}.connections.{kind}",f"Preferred minimum is {preferred}; found {found}. Do not fabricate content; enrich when evidence supports it."))
        if maximum is not None and found > int(maximum): issues.append(issue("warning","COMPLETENESS_MAXIMUM_EXCEEDED",f"{root}.connections.{kind}",f"Preferred maximum is {maximum}; found {found}."))
        if found and spec.get("evidence_claims") and not claim_satisfied(claims,spec["evidence_claims"]):
            issues.append(issue("error","COMPLETENESS_EVIDENCE_MISSING",f"{root}.connections.{kind}",f"Content is present but no verified provenance source claims one of: {', '.join(spec['evidence_claims'])}."))
    for spec in rule.get("details",[]):
        field=spec["field"]; found=count_nonempty_strings(details.get(field)); minimum=int(spec.get("minimum",0)); preferred=int(spec.get("preferred_minimum",0))
        if found < minimum: issues.append(issue("error","COMPLETENESS_MINIMUM",f"{root}.details.{field}",f"Required minimum is {minimum}; found {found}."))
        elif found < preferred: issues.append(issue("warning","COMPLETENESS_PREFERRED_MISSING",f"{root}.details.{field}",f"Preferred minimum is {preferred}; found {found}. Do not fabricate content; enrich when evidence supports it."))
        if found and spec.get("evidence_claims") and not claim_satisfied(claims,spec["evidence_claims"]):
            issues.append(issue("error","COMPLETENESS_EVIDENCE_MISSING",f"{root}.details.{field}",f"Content is present but no verified provenance source claims one of: {', '.join(spec['evidence_claims'])}."))
    rection=count_nonempty_strings(details.get("rection")); rc=rule.get("rection_evidence_claims",[])
    if rection and rc and not claim_satisfied(claims,rc):
        issues.append(issue("error","COMPLETENESS_EVIDENCE_MISSING",f"{root}.details.rection",f"Rektion is present but no verified provenance source claims one of: {', '.join(rc)}."))
    return issues

def validate(dataset,profile):
    if not isinstance(dataset,dict) or not isinstance(dataset.get("learning_units"),list): raise ValueError("Canonical dataset must be an object with learning_units[].")
    issues=[]; coverage=Counter(); by_type=profile.get("by_type",{})
    for i,unit in enumerate(dataset["learning_units"]):
        if not isinstance(unit,dict):
            issues.append(issue("error","COMPLETENESS_UNIT_INVALID",f"learning_units[{i}]","Learning unit is not an object.")); continue
        typ=unit.get("type"); coverage[typ or "<missing>"]+=1; rule=by_type.get(typ)
        if rule: issues.extend(validate_unit(unit,i,rule))
    errors=sum(x["severity"]=="error" for x in issues); warnings=sum(x["severity"]=="warning" for x in issues)
    return {"validator":"gfp-content-completeness","validator_version":"1.0.0","status":"FAIL" if errors else "PASS","errors":errors,"warnings":warnings,"target":profile.get("target"),"completeness_profile_id":profile.get("profile_id"),"coverage_by_type":dict(coverage),"issues":issues}

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument("dataset"); ap.add_argument("profile"); ap.add_argument("--output"); ns=ap.parse_args(argv)
    try: report=validate(load_json(ns.dataset),load_json(ns.profile))
    except Exception as e:
        print(json.dumps({"status":"CONFIGURATION_ERROR","error":str(e)},ensure_ascii=False,indent=2)); return 2
    text=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if ns.output: Path(ns.output).write_text(text,encoding="utf-8")
    print(text,end=""); return 1 if report["status"]=="FAIL" else 0

if __name__=="__main__": raise SystemExit(main())
