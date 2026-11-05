#!/usr/bin/env python3
"""Replay the REAL Git-index Lesen/Präsentation Stage1 inventory deterministically.

This validates derived native reading inventory/ID-map bytes and their relation
to source registry, manifest, QA and checkpoint. No source PDF bytes are here;
it is NOT semantic Stage4, native text production, Stage2+, CURRENT or ADOPTED.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
BASE="Workspaces/lesen-praesentation"
FILES={
    "registry":"SOURCE-REGISTRY.json",
    "manifest":BASE+"/00-source/SOURCE-MANIFEST.json",
    "inventory":BASE+"/01-inventory/SOURCE-INVENTORY.json",
    "ids":BASE+"/01-inventory/STABLE-ID-MAP.json",
    "qa":BASE+"/01-inventory/INVENTORY-QA.json",
    "checkpoint":BASE+"/CHECKPOINT.json",
}
SOURCE_ID="presentation-topics-b2-c1"
DATASET="lesen-praesentation"
SCHEMA="gfp-opt-p1-lesen-native-stage1-replay@1.0.0"
TOPIC_FIELDS=("stable_id","source_order","page_start","page_end",
              "label_text_nfc","source_number_token","heading_kind")
TOPIC_ID=re.compile(r"^lesen-praes-[0-9]{4}$")

def require(ok,code):
    if not ok: raise ValueError(code)

def sha256(raw):
    return hashlib.sha256(raw).hexdigest()

def strict_json(data):
    def pairs(source):
        out={}
        for key,value in source:
            require(key not in out,"DUPLICATE_JSON_KEY:"+key)
            out[key]=value
        return out
    def nonfinite(value):
        raise ValueError("NONFINITE_JSON:"+value)
    doc=json.loads(data.decode("utf-8-sig"),object_pairs_hook=pairs,
                   parse_constant=nonfinite)
    require(isinstance(doc,dict),"ROOT_JSON_NOT_OBJECT")
    return doc

def git_index_bytes(root=ROOT):
    require(root.resolve()==ROOT.resolve(),"CANNOT_REBASE_TRUST_ROOT")
    output={}
    for alias,path in FILES.items():
        raw=subprocess.check_output(
            ["git","ls-files","--stage","--",path],cwd=root).decode("utf-8")
        lines=raw.strip().splitlines()
        require(len(lines)==1,"NOT_ONE_TRACKED_FILE:"+alias)
        match=re.fullmatch(r"100644 ([0-9a-f]{40}) 0\t"+re.escape(path),
                           lines[0])
        require(match is not None,"UNMERGED_SYMLINK_OR_WRONG_INDEX_PATH:"+alias)
        blob=match.group(1)
        data=subprocess.check_output(["git","cat-file","blob",blob],cwd=root)
        require(0<len(data)<3_000_000,"SOURCE_EVIDENCE_BYTES_OUTSIDE_LIMIT:"+alias)
        canonical=(b"blob "+str(len(data)).encode("ascii")+b"\0"+data)
        require(hashlib.sha1(canonical).hexdigest()==blob,
                "CORRUPT_GIT_INDEX_BLOB:"+alias)
        output[alias]={"path":path,"blob":blob,"sha256":sha256(data),
                       "bytes":len(data),"document":strict_json(data)}
    return output

def check(documents,byte_hashes,blobs):
    require(set(documents)==set(FILES) and
            set(byte_hashes)==set(FILES) and set(blobs)==set(FILES),
            "MISSING_NATIVE_READING_ROLE")
    reg=documents["registry"]
    man=documents["manifest"]
    inv=documents["inventory"]
    ids=documents["ids"]
    qa=documents["qa"]
    checkpoint=documents["checkpoint"]
    require(reg.get("schema")=="gcpk-source-registry@1.1.0"
            and man.get("schema_version")=="1.0.0"
            and inv.get("schema_version")=="gcpk.source-inventory.v1"
            and ids.get("schema_version")=="gcpk.stable-id-map.v1"
            and qa.get("schema_version")=="gcpk.inventory-qa.v1"
            and checkpoint.get("checkpoint_schema_version")=="2.0.0",
            "READING_NATIVE_SCHEMAS_CHANGED")
    candidates=[x for x in reg.get("sources",[])
                if x.get("source_id")==SOURCE_ID]
    require(len(candidates)==1 and candidates[0].get("domain")=="reading"
            and candidates[0].get("workstream")==DATASET,
            "REGISTERED_NATIVE_SOURCE_OWNER_MISMATCH")
    entry=candidates[0]
    source_sha=entry["sha256"]
    require(re.fullmatch("[0-9a-f]{64}",source_sha) is not None
            and entry.get("checkpoint")==FILES["checkpoint"]
            and all(d.get("source_id")==SOURCE_ID and
                    d.get("source_sha256",d.get("sha256"))==source_sha
                    for d in (man,inv,ids,qa))
            and checkpoint.get("source_access",{}).get("source_id")==SOURCE_ID
            and checkpoint["source_access"].get("sha256")==source_sha,
            "CROSS_ROLE_READING_SOURCE_ID_OR_HASH_DRIFT")
    require(man.get("dataset")==inv.get("dataset")==ids.get("dataset")==
            qa.get("dataset")==checkpoint.get("dataset",{}).get("id")==DATASET
            and man.get("domain")=="reading"
            and man.get("canonical_filename")==inv.get("canonical_filename")
            and man.get("source_kind")=="user-provided-pdf"
            and man.get("production_policy",{}).get("runtime_reproduction")==
            "rewritten_learning_content_not_verbatim_reproduction",
            "READING_SOURCE_DOMAIN_OR_DELIVERY_BOUNDARY_CHANGED")
    require(qa.get("status")=="PASS"
            and isinstance(qa.get("checks"),dict)
            and qa["checks"] and all(v is True for v in qa["checks"].values()),
            "SOURCE_RECORDED_QA_IS_NOT_PASS")
    evidence=qa.get("evidence",{})
    require(evidence.get("source_inventory")==FILES["inventory"].removeprefix(BASE+"/")
            and evidence.get("stable_id_map")==FILES["ids"].removeprefix(BASE+"/")
            and evidence.get("source_inventory_sha256")==byte_hashes["inventory"]
            and evidence.get("stable_id_map_sha256")==byte_hashes["ids"],
            "ACTUAL_NATIVE_INVENTORY_ID_BYTES_NOT_QA_PINNED")
    stages=checkpoint.get("stages",[])
    require(len(stages)==7
            and [x.get("stage") for x in stages]==list(range(1,8))
            and stages[0].get("state")=="PASS"
            and all(x.get("state")=="NOT_STARTED" and
                    x.get("pass_commit") is None for x in stages[1:]),
            "READING_STAGE_BOUNDS_CHANGED")
    require(set(stages[0].get("authoritative_outputs",[]))==
            {"00-source/SOURCE-MANIFEST.json",
             "01-inventory/SOURCE-INVENTORY.json",
             "01-inventory/STABLE-ID-MAP.json"}
            and stages[0].get("gate_evidence")==["01-inventory/INVENTORY-QA.json"],
            "STAGE1_OUTPUT_ROLES_DRIFT")
    topics=inv.get("topics",[])
    mapping=ids.get("mappings",[])
    pages=inv.get("page_accounting",[])
    counts=inv.get("counts",{})
    require(isinstance(topics,list) and isinstance(mapping,list)
            and len(topics)==len(mapping)==ids.get("count")==68
            and len(pages)==76,
            "READING_TOPIC_OR_PAGE_COUNT_CHANGED")
    require([x.get("page") for x in pages]==list(range(1,77)),
            "MISSING_DUPLICATE_OR_OUT_OF_ORDER_PDF_PAGE")
    require([x.get("source_order") for x in topics]==list(range(1,69))
            and [x.get("stable_id") for x in topics]==[
                "lesen-praes-"+str(i).zfill(4) for i in range(1,69)],
            "READING_STABLE_ID_ORDER_INVALID")
    require(all(a.get("stable_id")==b.get("stable_id")
                and all(a.get(k)==b.get(k) for k in TOPIC_FIELDS)
                for a,b in zip(topics,mapping)),
            "ACTUAL_NATIVE_ID_MAP_NOT_SAME_SOURCE_ORDER")
    byid={x["stable_id"]:x for x in topics}
    require(len(byid)==68 and all(TOPIC_ID.fullmatch(x) for x in byid),
            "DUPLICATE_OR_INVALID_READING_TOPIC_ID")
    classes=Counter(p.get("classification") for p in pages)
    require(classes==Counter({"topic_start":68,"continuation":6,
                              "blank":1,"duplicate_occurrence":1}),
            "PAGE_CLASSIFICATION_CONSERVATION_FAILED")
    require(counts=={"pdf_pages":76,"topics":68,"topic_start_pages":68,
                     "continuation_pages":6,"blank_pages":1,
                     "duplicate_occurrence_pages":1}
            and qa.get("summary",{}).get("pdf_pages")==76
            and qa["summary"].get("topics")==68
            and all(qa["summary"].get(k)==v for k,v in counts.items()),
            "SOURCE_COUNT_OR_RECORDED_QA_SUMMARY_DRIFT")
    idx={p["page"]:p for p in pages}
    require(all((p.get("topic_id") in byid if p["classification"]!="blank"
                 else p.get("topic_id") is None) for p in pages),
            "PAGE_REFERENCES_UNKNOWN_TOPIC")
    for topic in topics:
        start=topic["page_start"]
        cont=topic.get("continuation_pages")
        dup=topic.get("duplicate_occurrence_pages")
        require(type(start) is int and 1<=start<=76
                and isinstance(cont,list) and isinstance(dup,list)
                and all(type(p) is int and 1<=p<=76 for p in cont+dup),
                "INVALID_TOPIC_PAGE_RANGE")
        require(topic["page_end"]==max([start]+cont)
                and idx[start]["classification"]=="topic_start"
                and idx[start]["topic_id"]==topic["stable_id"]
                and [p["page"] for p in pages
                     if p["classification"]=="topic_start"
                     and p["topic_id"]==topic["stable_id"]]==[start],
                "TOPIC_START_OR_END_PAGE_DRIFT")
        require(cont==[p["page"] for p in pages
                       if p["classification"]=="continuation"
                       and p["topic_id"]==topic["stable_id"]]
                and dup==[p["page"] for p in pages
                          if p["classification"]=="duplicate_occurrence"
                          and p["topic_id"]==topic["stable_id"]],
                "TOPIC_SPECIAL_PAGE_MEMBERSHIP_DRIFT")
        require(all(idx[n].get("continues_page")==start for n in cont)
                and all(idx[n].get("duplicates_topic_start_page")==start
                        for n in dup),
                "PAGE_SPECIAL_ORIGIN_DRIFT")
        label=topic.get("label_text_nfc")
        heading=topic.get("source_heading_nfc")
        require(isinstance(label,str) and bool(label.strip())
                and unicodedata.normalize("NFC",label)==label
                and isinstance(heading,str)
                and unicodedata.normalize("NFC",heading)==heading
                and unicodedata.normalize("NFC",
                     topic.get("source_heading_extracted",""))==heading,
                "HEADING_OR_LABEL_NFC_DRIFT")
        require(topic.get("heading_kind") in
                ("source_heading","prompt_without_short_heading"),
                "UNKNOWN_SOURCE_HEADING_KIND")
    special=inv.get("special_cases",{})
    blank=special.get("blank_pages")
    continuation=special.get("continuation_pages")
    dupcases=special.get("duplicate_occurrences")
    unnumbered=special.get("unnumbered_topic_start_pages")
    require(blank==[p["page"] for p in pages if p["classification"]=="blank"]
            and isinstance(continuation,list) and isinstance(dupcases,list)
            and [x.get("page") for x in continuation]==[
                p["page"] for p in pages if p["classification"]=="continuation"]
            and [x.get("page") for x in dupcases]==[
                p["page"] for p in pages if p["classification"]=="duplicate_occurrence"],
            "SPECIAL_PAGES_NOT_RECONCILED")
    for x in continuation:
        orig=idx[x["page"]]
        require(x["topic_id"]==orig["topic_id"]
                and x["continues_topic_start_page"]==orig["continues_page"],
                "CONTINUATION_ORIGIN_NOT_RECONCILED")
    for x in dupcases:
        orig=idx[x["page"]]
        require(x["topic_id"]==orig["topic_id"]
                and x["duplicates_topic_start_page"]==
                    orig["duplicates_topic_start_page"],
                "DUPLICATE_ORIGIN_NOT_RECONCILED")
    require(unnumbered==[t["page_start"] for t in topics
                         if t["heading_kind"]=="prompt_without_short_heading"]
            and all(byid[p["topic_id"]]["source_number_token"] is None
                    for p in pages if p["page"] in unnumbered)
            and qa["summary"]["unnumbered_topic_start_pages"]==unnumbered,
            "UNNUMBERED_READING_PROMPT_NOT_RECONCILED")
    inventory_counts=man.get("inventory",{})
    require(inventory_counts.get("pdf_pages")==76
            and inventory_counts.get("topics")==68
            and inventory_counts.get("continuation_pages")==[
                p["page"] for p in pages if p["classification"]=="continuation"]
            and inventory_counts.get("blank_pages")==blank
            and inventory_counts.get("duplicate_occurrence_pages")==[
                p["page"] for p in pages if p["classification"]=="duplicate_occurrence"]
            and inventory_counts.get("unnumbered_topic_start_pages")==unnumbered,
            "SOURCE_MANIFEST_DERIVED_INVENTORY_MISMATCH")
    return {
       "schema":SCHEMA,
       "status":"PASS_ACTUAL_GIT_READING_STAGE1_DERIVED_BYTES_AND_STRUCTURE_REPLAY_ONLY",
       "family_id":"family:lesen",
       "native_workstream":DATASET,
       "registered_source_id":SOURCE_ID,
       "registered_source_sha256_from_registry_not_reread_pdf":source_sha,
       "actual_git_derived_evidence":{
           name:{"path":FILES[name],"git_blob":blobs[name],
                 "sha256":byte_hashes[name]}
           for name in ("manifest","inventory","ids","qa","checkpoint")
       },
       "replayed_counts":{"topics":68,"pages":76,"continuations":6,
                          "blanks":1,"duplicate_occurrences":1,
                          "unnumbered_topics":len(unnumbered)},
       "recorded_checkpoint_stage1":"PASS_IN_PREEXISTING_SOURCE_CHECKPOINT",
       "actual_independent_stage1_source_pdf_bytes_revalidated":False,
       "linguistic_stage4":"NOT_RUN",
       "stage2_to_7":"NOT_APPROVED",
       "new_native_producer_invocation":"NOT_RUN",
       "new_policy_adoption":"NOT_ADOPTED",
       "live_github_main_or_library_currentness":"NOT_CHECKED_BY_GIT_INDEX_REPLAY",
       "user_newer_source_override":"NOT_EXCLUDED",
       "any_card_source_locked_or_app_mutation":False,
    }

def execute():
    roles=git_index_bytes()
    return check({k:v["document"] for k,v in roles.items()},
                 {k:v["sha256"] for k,v in roles.items()},
                 {k:v["blob"] for k,v in roles.items()})

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--new-report",type=Path,required=True)
    a.add_argument("--summary",action="store_true")
    opts=a.parse_args()
    try:
        report=execute()
        target=opts.new_report.resolve()
        require(target.suffix==".json" and target.parent.is_dir()
                and not target.exists() and not target.is_symlink()
                and ROOT.resolve() not in target.parents,
                "REPORT_NOT_EXCLUSIVE_OR_OUTSIDE_GIT_REPOSITORY")
        with target.open("x",encoding="utf-8") as f:
            json.dump(report,f,ensure_ascii=False,sort_keys=True,indent=2)
            f.write("\n")
        if opts.summary:
            print(json.dumps({k:v for k,v in report.items()
                              if k not in ("actual_git_derived_evidence",)},
                             ensure_ascii=False,indent=2))
        else:
            print(json.dumps(report,ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,subprocess.CalledProcessError,UnicodeError) as e:
        print("GFP_OPT_READING_NATIVE_REPLAY_BLOCKED:"+str(e),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
