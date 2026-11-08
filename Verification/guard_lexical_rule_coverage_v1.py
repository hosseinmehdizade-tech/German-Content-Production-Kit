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
def exact_surface(s):return " ".join(unicodedata.normalize("NFC",str(s)).split()) # machine-exact: no ß/ss or case folding
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

def split_lexical_bilingual_surface(item):
    """Keep German internal en dashes; split only real DE/FA display delimiters.

    An en dash inside a German pattern (e.g. 'wohin? – wo?') is not a
    translation separator. A spaced em dash remains the legacy fallback.
    """
    for match in re.finditer(r"\s+[—–]\s+",item):
        following=item[match.end():].lstrip()
        if following and re.match(r"[\u0600-\u06ff\u0750-\u077f]",following):
            return item[:match.start()].strip()
    return item.split(" — ",1)[0].strip()


def _lexical_de(item, source):
    """German surface only; do not mistake FA/EN metadata for a new phrase."""
    if isinstance(item,str):
        value=split_lexical_bilingual_surface(item)
    elif isinstance(item,dict):
        value=item.get("de",item.get("text_de",item.get("text","")))
    else:
        raise ValueError("INVALID_COMBINATION_ITEM:"+source)
    if not isinstance(value,str) or not value.strip():
        raise ValueError("EMPTY_COMBO:"+source)
    return value.strip()


def _combination_sources(row, details):
    """Scan learner-visible and supported structured native combinations.

    A synchronized backend mirror is one learner phrase, not a second visible
    tile. Duplicates *within* one actual source remain reviewable HIGH risks.
    No backend item is invented or projected into the original TSV.
    """
    visible=[]
    for section in details:
        if not isinstance(section,dict):raise ValueError("INVALID_DETAIL_SECTION")
        if norm(section.get("title","")) not in ("kombinationen","kollokationen"):
            continue
        items=section.get("items",[])
        if not isinstance(items,list):raise ValueError("INVALID_COMBO_ITEMS")
        visible.extend(_lexical_de(item,"details") for item in items)
    result=[("details",visible)]

    raw_fields=[row.get(key) for key in ("custom_fields","customFields")
                if row.get(key) not in (None,"")]
    fields=[]
    for raw in raw_fields:
        try:parsed=json.loads(raw,object_pairs_hook=unique) if isinstance(raw,str) else raw
        except (ValueError,TypeError) as exc:raise ValueError("INVALID_NATIVE_CUSTOM_FIELDS_JSON") from exc
        if not isinstance(parsed,dict):raise ValueError("INVALID_NATIVE_CUSTOM_FIELDS_OBJECT")
        fields.append(parsed)
    if len(fields)==2 and fields[0] and fields[1] and fields[0]!=fields[1]:
        raise ValueError("CONFLICTING_CUSTOM_FIELDS_ALIASES")
    custom=next((f for f in fields if f),{})
    for key in ("kombinationen_v1","kombinationen_v336"):
        payload=custom.get(key,[])
        if payload is None:payload=[]
        if isinstance(payload,dict):
            if not isinstance(payload.get("items"),list):
                raise ValueError("INVALID_BACKEND_COMBINATION_ITEMS:"+key)
            payload=payload["items"]
        if not isinstance(payload,list):
            raise ValueError("INVALID_BACKEND_COMBINATION_LIST:"+key)
        result.append((key,[_lexical_de(item,key) for item in payload]))
    return result


def review_signals(rows):
    findings=[];tot_ex=tot_co=0
    for row in rows:
        try:
            ds=json.loads(row["details"],object_pairs_hook=unique)
            es=json.loads(row["examples"],object_pairs_hook=unique)
        except (ValueError,TypeError) as exc:raise ValueError("INVALID_LEXICAL_TILES_JSON") from exc
        if not isinstance(ds,list) or not isinstance(es,list):
            raise ValueError("INVALID_LEXICAL_TILES")
        sources=_combination_sources(row,ds)
        # Exact German surfaces are compared once across *mirrored* backends.
        # A real duplicate *within* a source is still a defect.
        combos=[];all_seen=set()
        for source,items in sources:
            local_seen=set()
            for c in items:
                n=exact_surface(c)
                if n in local_seen:
                    findings.append([row["id"],"EXACT_COMBO_DUPLICATE",c,"","HIGH"])
                local_seen.add(n)
                if n not in all_seen:
                    combos.append(c)
                    all_seen.add(n)
        # Distinct authorized backend and learner-visible projections can differ.
        # Report that tension for semantic Stage4 review; no automatic rewrite
        # or unconditional HIGH, because a shorter view may be deliberate.
        visible_items=sources[0][1]
        backend_items=[item for _,items in sources[1:] for item in items]
        if visible_items and backend_items:
            exact=lambda x:" ".join(unicodedata.normalize("NFC",x).split())
            a_set={exact(x) for x in visible_items}
            b_set={exact(x) for x in backend_items}
            if a_set!=b_set:
                candidate=sorted(b_set-a_set) or sorted(a_set-b_set)
                findings.append([row["id"],"BACKEND_VISIBLE_SURFACE_DIVERGENCE_REVIEW",
                                 candidate[0],"","MEDIUM"])
        ex=[]
        for e in es:
            if not isinstance(e,dict):raise ValueError("UNKNOWN_EXAMPLE_FORMAT")
            if str(e.get("lang","de")).lower().startswith("de"):
                t=e.get("text",e.get("text_de",e.get("de","")))
                if not isinstance(t,str) or not t.strip():
                    raise ValueError("EMPTY_GERMAN_EXAMPLE")
                ex.append(t)
        tot_ex+=len(ex);tot_co+=len(combos)
        for c in combos:
            n=exact_surface(c)
            ct={stem(x) for x in words(c) if x not in STOP and len(x)>=4}
            for e in ex:
                et={stem(x) for x in words(e) if x not in STOP and len(x)>=4}
                common={x for x in ct if any(related_stem(x,y) for y in et)}
                exact=n==exact_surface(e)
                if exact or (len(common)>=2 and len(common)>=len(ct)-1):
                    findings.append([row["id"],"EXACT_EXAMPLE_CLONE" if exact else "EXAMPLE_REUSE_REVIEW",c,e,"HIGH" if exact else "MEDIUM"])
                    break
    output=[]
    for cid,code,c,e,severity in findings:
        fp=sha(("\0".join([cid,code,c,e])).encode())
        output.append({"id":fp,"card_id":cid,"code":code,"combination":c,
                       "example":e,"severity":severity})
    return {"examples":tot_ex,"combinations":tot_co,"issues":output}


def high_taxonomy_signals(taxonomy, source_sha):
    """Turn exact-source right-side HIGH diagnostics into stable review obligations."""
    if not isinstance(taxonomy, dict) or taxonomy.get("schema")!="gcpk-related-taxonomy-audit@1.1.0":
        raise ValueError("INVALID_RELATED_TAXONOMY_RESULT")
    if taxonomy.get("source_sha256")!=source_sha or not isinstance(taxonomy.get("findings"), list):
        raise ValueError("RELATED_TAXONOMY_NOT_BOUND_TO_EXACT_SOURCE")
    found={}
    for item in taxonomy["findings"]:
        if not isinstance(item,dict):raise ValueError("INVALID_TAXONOMY_FINDING")
        if item.get("severity")!="HIGH":continue
        cid,code,section,value=(item.get(k) for k in ("card_id","code","section","value"))
        if not all(isinstance(x,str) and x for x in (cid,code,section,value)):
            raise ValueError("INVALID_HIGH_TAXONOMY_IDENTITY")
        fingerprint=sha(("\0".join(("TAXONOMY",cid,code,section,value))).encode("utf-8"))
        found[fingerprint]={"id":fingerprint,"card_id":cid,"code":code,
                            "section":section,"value":value,"severity":"HIGH"}
    return [found[k] for k in sorted(found)]


def review_high_findings(cross_tile, taxonomy_high, evidence):
    """One existing independent review, never a new per-flag editorial phase.

    A claimed CORRECTED_IN_EXACT_SOURCE is invalid while that exact finding
    remains detectable. Historical content is not edited by this function.
    """
    blockers=[]
    issues=cross_tile["issues"]
    flagged={x["card_id"] for x in issues}|{x["card_id"] for x in taxonomy_high}
    supplied=evidence.get("flagged_card_ids")
    if not isinstance(supplied,list) or any(not isinstance(x,str) for x in supplied) or \
        len(supplied)!=len(set(supplied)) or set(supplied)!=flagged:
        blockers.append("CROSS_TILE_SCOPE_MISSING_CARDS")
    if evidence.get("risk_based_independent_review") is not True:
        blockers.append("NO_INDEPENDENT_CROSS_TILE_REVIEW")
    raw=evidence.get("high_decisions",[])
    if not isinstance(raw,list):
        return blockers+["INVALID_HIGH_DECISION_LIST"]
    decisions={}
    for item in raw:
        if not isinstance(item,dict) or not isinstance(item.get("id"),str):
            blockers.append("INVALID_HIGH_DECISION_RECORD")
            continue
        if item["id"] in decisions:
            blockers.append("DUPLICATE_HIGH_DECISION:"+item["id"][:12])
        decisions[item["id"]]=item
    current={x["id"] for x in issues if x["severity"]=="HIGH"}|{x["id"] for x in taxonomy_high}
    for fp in decisions:
        if fp not in current:
            blockers.append("STALE_OR_UNKNOWN_HIGH_DECISION:"+fp[:12])
    for item in issues+taxonomy_high:
        if item["severity"]!="HIGH":continue
        fingerprint=item["id"]
        code=item["code"]
        if code=="EXACT_COMBO_DUPLICATE":
            blockers.append("DUPLICATE_COMBO_REQUIRES_SOURCE_CORRECTION:"+fingerprint[:12])
            continue
        if code in ("OPAQUE_TARGET_ID_IN_RELATED","INVISIBLE_FORMAT_CONTROL",
                    "DUPLICATE_WITHIN_RELATED","CONFLICTING_TYPED_TARGET"):
            blockers.append("RELATED_STRUCTURAL_HIGH_REQUIRES_CORRECTION:"+fingerprint[:12])
            continue
        decision=decisions.get(fingerprint,{})
        if decision.get("decision")=="CORRECTED_IN_EXACT_SOURCE":
            blockers.append("CORRECTION_STILL_PRESENT_IN_EXACT_SOURCE:"+fingerprint[:12])
        elif decision.get("decision")!="KEEP_WITH_SPECIFIC_TEACHING_DELTA" or \
            not isinstance(decision.get("reason"),str) or not decision["reason"].strip():
            blockers.append("HIGH_UNRESOLVED:"+fingerprint[:12])
    return blockers


def evaluate(tsv,stage4=None,review=None,root=ROOT,policy_checks=True):
    if not tsv.is_file() or tsv.is_symlink():raise ValueError("INVALID_CURRENT_TSV")
    original=tsv.read_bytes();rows=native_rows(original);sc=review_signals(rows)
    blockers=[];extra={};taxonomy_high=[]
    authority=pinned(root) if policy_checks else {"mode":"SYNTHETIC_UNIT_TEST_ONLY"}
    if policy_checks:
        sys.path.insert(0,str(root/"Verification"))
        from audit_lexical_relation_fields_v1 import audit as lexical
        from audit_related_sections_taxonomy_v1_1 import audit as related,load_cards
        from audit_kombinationen_lean_v1_1 import analyze_rows
        from check_mem009_native_stage5_v1 import audit_tsv_bytes
        from check_active_stage5_policy_v1 import check_bytes
        rel=lexical(tsv);tax=related(load_cards(original,".tsv"),sha(original))
        taxonomy_high=high_taxonomy_signals(tax,sha(original))
        did=analyze_rows(rows,tsv.name,sha(original));mem=audit_tsv_bytes(original)
        neutral=check_bytes(original,root)
        extra={"lexical_relation":rel["status"],
          "related_taxonomy_high":len(taxonomy_high),
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
            blockers.extend(review_high_findings(sc,taxonomy_high,ev))
    if tsv.read_bytes()!=original:raise ValueError("SOURCE_CHANGED_DURING_AUDIT")
    return {"schema":"gcpk-mandatory-lexical-release-coverage@1.0.0",
        "status":"BLOCKED" if blockers else "PASS_FOR_GOVERNED_STAGE5_CANDIDATE_ONLY",
        "source_tsv_sha256":sha(original),"cards":len(rows),
        "policy_authority":authority,"executed_scanners":extra,
        "cross_tile":{"examples":sc["examples"],"combinations":sc["combinations"],
             "issues":len(sc["issues"]),"by_code":{c:sum(x["code"]==c for x in sc["issues"]) for c in sorted({x["code"] for x in sc["issues"]})},
             "affected_cards":len({x["card_id"] for x in sc["issues"]}|{x["card_id"] for x in taxonomy_high}),
             "first_12":sc["issues"][:12],
             "related_taxonomy_high":len(taxonomy_high),
             "related_taxonomy_first_12":taxonomy_high[:12]},
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
