#!/usr/bin/env python3
"""One fail-closed content acceptance preflight for future editable lexical releases.

This is NOT a dictionary judge. Machine checks run on the actual TSV bytes;
independent risk-based Stage4 and an exact same-card cross-tile review are
separate mandatory evidence. Historical accepted cards are read-only.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,sys,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY="Prompt/GLOBAL-POLICY-REGISTRY-v1.0.0.json"
REQUIRED={"kombinationen_pointer","kombinationen_source_first",
 "related_taxonomy","lexical_relation_display","linguistic_qa",
 "risk_based_stage4","curated_current_delta_qa","stage5_neutral_validator"}
STOP={"das","der","die","den","dem","des","ein","eine","einen","einem",
 "einer","ich","du","er","sie","es","wir","ihr","man","wird","wurde",
 "wurden","werden","ist","sind","war","haben","hat","möchte","möchten",
 "und","oder","mit","von","an","auf","im","am","in","zum","zur","bei",
 "für","über","etwas","jemanden","jemandem","sich","sein"}

def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def norm(s):return " ".join(unicodedata.normalize("NFC",str(s)).casefold().split())
def words(s):return re.findall(r"[^\W_]+",norm(s),flags=re.UNICODE)
def stem(w):
    if len(w)<6:return w
    for suf in ("erten","ertet","erte","est","ete","ten","tet","te","en","et","er","es","em","e","t","n","s"):
        if w.endswith(suf) and len(w)-len(suf)>=4:return w[:-len(suf)]
    return w
def related_stem(a,b):
    if a==b:return True
    c=len(__import__("os").path.commonprefix([a,b]))
    return c>=6 and len(a)-c<=2 and len(b)-c<=2
def unique(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError("DUPLICATE_JSON_KEY:"+k)
        d[k]=v
    return d
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"),object_pairs_hook=unique)
def pinned(root):
    reg=read(root/REGISTRY);entries=reg.get("policy_bindings",{})
    if not REQUIRED.issubset(entries):raise ValueError("MISSING_CENTRAL_REQUIRED_POLICIES")
    for name,item in entries.items():
        rel=item.get("path");pin=item.get("blob_sha")
        if not isinstance(rel,str) or not re.fullmatch("[a-f0-9]{40}",str(pin)):
            raise ValueError("INVALID_CENTRAL_POLICY_BINDING:"+name)
        p=root/rel
        if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):
            raise ValueError("MISSING_POLICY_FILE:"+name)
        b=p.read_bytes()
        if blob(b)!=pin and (b"\r\n" not in b or blob(b.replace(b"\r\n",b"\n"))!=pin):
            raise ValueError("CENTRAL_POLICY_CONTENT_DRIFT:"+name)
    return {"bindings_checked":len(entries),"registry_sha256":sha((root/REGISTRY).read_bytes()),
            "scope":"BYTE_PINS_ONLY_NOT_SEMANTIC_ADOPTION"}

def native_rows(raw):
    rdr=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline=""),delimiter="\t")
    if not rdr.fieldnames or not {"id","front","details","examples"}.issubset(rdr.fieldnames):
        raise ValueError("UNSUPPORTED_NATIVE_LEXICAL_TSV")
    rows=list(rdr)
    if not rows or any(None in row or any(v is None for v in row.values()) or not row["id"] for row in rows):
        raise ValueError("INVALID_LEXICAL_ROWS")
    ids=[row["id"] for row in rows]
    if len(ids)!=len(set(ids)):raise ValueError("DUPLICATE_CARD_IDS")
    return rows

def review_signals(rows):
    findings=[];tot_ex=tot_co=0
    for row in rows:
        ds=json.loads(row["details"]);es=json.loads(row["examples"])
        if not isinstance(ds,list) or not isinstance(es,list):raise ValueError("INVALID_LEXICAL_TILES")
        combos=[]
        for sec in ds:
            if not isinstance(sec,dict):raise ValueError("INVALID_DETAIL_SECTION")
            if norm(sec.get("title","")) in ("kombinationen","kollokationen"):
                its=sec.get("items",[])
                if not isinstance(its,list):raise ValueError("INVALID_COMBO_ITEMS")
                for item in its:
                    if isinstance(item,str):s=item.split(" — ",1)[0]
                    elif isinstance(item,dict):s=item.get("de",item.get("text_de",item.get("text","")))
                    else:raise ValueError("UNKNOWN_COMBO_FORMAT")
                    if not isinstance(s,str) or not s.strip():raise ValueError("EMPTY_COMBO")
                    combos.append(s.strip())
        ex=[]
        for e in es:
            if not isinstance(e,dict):raise ValueError("UNKNOWN_EXAMPLE_FORMAT")
            if str(e.get("lang","de")).lower().startswith("de"):
                t=e.get("text",e.get("text_de",e.get("de","")))
                if not isinstance(t,str) or not t.strip():raise ValueError("EMPTY_GERMAN_EXAMPLE")
                ex.append(t)
        tot_ex+=len(ex);tot_co+=len(combos)
        seen=set()
        for c in combos:
            n=norm(c)
            if n in seen:findings.append([row["id"],"EXACT_COMBO_DUPLICATE",c,"","HIGH"])
            seen.add(n)
            ct={stem(x) for x in words(c) if x not in STOP and len(x)>=4}
            for e in ex:
                et={stem(x) for x in words(e) if x not in STOP and len(x)>=4}
                common={x for x in ct if any(related_stem(x,y) for y in et)}
                exact=n==norm(e)
                if exact or (len(common)>=2 and len(common)>=len(ct)-1):
                    findings.append([row["id"],"EXACT_EXAMPLE_CLONE" if exact else "EXAMPLE_REUSE_REVIEW",c,e,"HIGH" if exact else "MEDIUM"])
                    break
    output=[]
    for cid,code,c,e,severity in findings:
        fp=sha(("\0".join([cid,code,c,e])).encode())
        output.append({"id":fp,"card_id":cid,"code":code,"combination":c,
                       "example":e,"severity":severity})
    return {"examples":tot_ex,"combinations":tot_co,"issues":output}

def evaluate(tsv,stage4=None,review=None,root=ROOT,policy_checks=True):
    if not tsv.is_file() or tsv.is_symlink():raise ValueError("INVALID_CURRENT_TSV")
    original=tsv.read_bytes();rows=native_rows(original);sc=review_signals(rows)
    blockers=[];extra={}
    authority=pinned(root) if policy_checks else {"mode":"SYNTHETIC_UNIT_TEST_ONLY"}
    if policy_checks:
        sys.path.insert(0,str(root/"Verification"))
        from audit_lexical_relation_fields_v1 import audit as lexical
        from audit_related_sections_taxonomy_v1_1 import audit as related,load_cards
        from audit_kombinationen_lean_v1_1 import analyze_rows
        from check_mem009_native_stage5_v1 import audit_tsv_bytes
        from check_active_stage5_policy_v1 import check_bytes
        rel=lexical(tsv);tax=related(load_cards(original,".tsv"),sha(original))
        did=analyze_rows(rows,tsv.name,sha(original));mem=audit_tsv_bytes(original)
        neutral=check_bytes(original,root)
        extra={"lexical_relation":rel["status"],
          "related_taxonomy_high":tax["severity_counts"].get("HIGH",0),
          "kombinationen_advisory_count":len(did["flags"]),
          "mem009":mem["status"],"neutral_projection":neutral["status"]}
        if rel["issue_counts"]["BLOCKER"]:blockers.append("LEXICAL_RELATION_STRUCTURAL_ERROR")
        if mem["status"]!="PASS_MEM009_NATIVE_STRUCTURE_ONLY":blockers.append("MEM009_STRUCTURAL_ERROR")
        if neutral["status"]!="PASS_EXACT_ACTIVE_STAGE5_NEUTRAL_FORMAT_ONLY":blockers.append("NEUTRAL_FORMAT_ERROR")
    if stage4 is None or not stage4.is_file():
        blockers.append("INDEPENDENT_STAGE4_EVIDENCE_MISSING")
    else:
        sys.path.insert(0,str(root/"Verification"))
        from audit_kombinationen_lean_v1_1 import accept_existing_stage4
        decision=accept_existing_stage4(tsv,stage4)
        if not str(decision["status"]).startswith("PASS") or decision["blockers"]:
            blockers.append("EXACT_SOURCE_OFFICIAL_STAGE4_FAILED")
    if review is None or not review.is_file():
        blockers.append("SAME_CARD_CROSS_TILE_REVIEW_MISSING")
    else:
        ev=read(review)
        if ev.get("schema")!="gcpk-lexical-cross-tile-acceptance@1.0.0" or ev.get("source_tsv_sha256")!=sha(original):
            blockers.append("CROSS_TILE_REVIEW_SOURCE_MISMATCH")
        else:
            if not ev.get("workstream") or not re.fullmatch("[a-f0-9]{64}",str(ev.get("curated_current_parent_sha256",""))):
                blockers.append("CURRENT_OWNER_NOT_BOUND")
            if stage4 and stage4.is_file() and ev.get("stage4_receipt_sha256")!=sha(stage4.read_bytes()):
                blockers.append("CROSS_TILE_REVIEW_STAGE4_MISMATCH")
            flagged={i["card_id"] for i in sc["issues"]}
            if set(ev.get("flagged_card_ids",[]))!=flagged:
                blockers.append("CROSS_TILE_SCOPE_MISSING_CARDS")
            if ev.get("risk_based_independent_review") is not True:
                blockers.append("NO_INDEPENDENT_CROSS_TILE_REVIEW")
            decisions={d.get("id"):d for d in ev.get("high_decisions",[]) if isinstance(d,dict)}
            for i in sc["issues"]:
                if i["code"]=="EXACT_COMBO_DUPLICATE":
                    # An identical second combination is not a new lesson.
                    blockers.append("DUPLICATE_COMBO_REQUIRES_SOURCE_CORRECTION:"+i["id"][:12])
                    continue
                if i["severity"]=="HIGH":
                    d=decisions.get(i["id"],{})
                    if d.get("decision") not in ("KEEP_WITH_SPECIFIC_TEACHING_DELTA","CORRECTED_IN_EXACT_SOURCE") or not str(d.get("reason","")).strip():
                        blockers.append("HIGH_UNRESOLVED:"+i["id"][:12])
    if tsv.read_bytes()!=original:raise ValueError("SOURCE_CHANGED_DURING_AUDIT")
    return {"schema":"gcpk-mandatory-lexical-release-coverage@1.0.0",
        "status":"BLOCKED" if blockers else "PASS_FOR_GOVERNED_STAGE5_CANDIDATE_ONLY",
        "source_tsv_sha256":sha(original),"cards":len(rows),
        "policy_authority":authority,"executed_scanners":extra,
        "cross_tile":{"examples":sc["examples"],"combinations":sc["combinations"],
             "issues":len(sc["issues"]),"by_code":{c:sum(x["code"]==c for x in sc["issues"]) for c in sorted({x["code"] for x in sc["issues"]})},
             "affected_cards":len({x["card_id"] for x in sc["issues"]}),
             "first_12":sc["issues"][:12]},
        "blockers":blockers,"does_not_prove":["ALL_22_LINGUISTIC_POLICIES",
             "TRUE_SEMANTIC_CORRECTNESS","NATIVE_APP_STAGE6","FINAL_STAGE7"]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("tsv",type=Path);p.add_argument("--stage4-receipt",type=Path)
    p.add_argument("--cross-tile-review",type=Path);p.add_argument("--report",type=Path)
    a=p.parse_args()
    try:
        result=evaluate(a.tsv,a.stage4_receipt,a.cross_tile_review)
        if a.report:
            if a.report.exists() or a.report.is_symlink() or a.report.resolve()==a.tsv.resolve():
                raise ValueError("REPORT_NOT_WRITE_ONCE")
            with a.report.open("x",encoding="utf-8") as fh:
                json.dump(result,fh,ensure_ascii=False,indent=2);fh.write("\n")
    except (ValueError,OSError,UnicodeError) as e:
        print("LEXICAL_RELEASE_POLICY_ERROR:"+str(e),file=sys.stderr);return 2
    print(json.dumps({"status":result["status"],"cards":result["cards"],
          "overlap":result["cross_tile"]["issues"],"blockers":result["blockers"][:10]},ensure_ascii=False))
    return 2 if result["blockers"] else 0

if __name__=="__main__":raise SystemExit(main())
