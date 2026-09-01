#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from copy import deepcopy
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; German-Content-Production-Kit/3.1.10; +https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit)"
}
BASE_HEADER = [
    "id","card_type","domain","category","source","level","lesson","deck","front","back",
    "front_label","back_label","front_lang","back_lang","typing_target","examples","related",
    "opposites","details","custom_fields","tags","notes","order"
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\u00ad", "").strip())


def duden_source(unit):
    for src in (unit.get("provenance") or {}).get("sources", []):
        if src.get("source_id") == "duden_online" and src.get("locator"):
            return src
    return None


def fetch_page(session, url: str):
    r = session.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return r.text


def section_after_heading(soup: BeautifulSoup, pattern: str):
    heading = None
    for h in soup.find_all(["h2", "h3"]):
        if re.search(pattern, norm(h.get_text(" ", strip=True)), flags=re.I):
            heading = h
            break
    if not heading:
        return []
    nodes = []
    for sib in heading.next_siblings:
        name = getattr(sib, "name", None)
        if name in {"h2", "h3"}:
            break
        nodes.append(sib)
    return nodes


def linked_terms(nodes):
    out=[]
    for node in nodes:
        if not hasattr(node, "find_all"):
            continue
        for a in node.find_all("a"):
            t=norm(a.get_text(" ", strip=True))
            if not t or len(t)>48:
                continue
            if re.fullmatch(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß -]*", t):
                out.append(t)
    return out


def extract_duden(soup: BeautifulSoup, headword: str):
    typical_nodes = section_after_heading(soup, r"Typische Verbindungen")
    typical = linked_terms(typical_nodes)

    syn_nodes = section_after_heading(soup, r"Synonyme zu")
    synonyms = linked_terms(syn_nodes)

    # Duden often has no dedicated antonym section. Only use an explicit one if present.
    ant_nodes = section_after_heading(soup, r"(Gegenwörter|Antonyme)")
    antonyms = linked_terms(ant_nodes)

    text = norm(soup.get_text(" ", strip=True))
    return typical, synonyms, antonyms, text


def make_collocations(headword: str, terms):
    h = norm(headword)
    seen=set(); out=[]
    bad={"anzeigen","übersicht","mehr","erfahren","duden","wort","wörterbuch"}
    for term in terms:
        t=norm(term)
        if not t or t.casefold() in bad or t.casefold()==h.casefold():
            continue
        # Duden's "Typische Verbindungen" lists nouns/adjectives/adverbs linked with the lemma.
        # Preserve Duden term exactly and combine deterministically with the current lemma.
        phrase=f"{t} {h}"
        k=phrase.casefold()
        if k not in seen:
            seen.add(k); out.append(phrase)
        if len(out)>=4:
            break
    return out


def evidence_matches_rection(duden_text: str, rection):
    if not rection:
        return False
    prep_words=[]
    for x in rection if isinstance(rection,list) else [rection]:
        m=re.match(r"\s*([A-Za-zÄÖÜäöüß]+)", str(x))
        if m: prep_words.append(m.group(1).casefold())
    low=duden_text.casefold()
    return bool(prep_words) and all(re.search(rf"\b{re.escape(p)}\b", low) for p in prep_words)


def add_claim(src: dict, claim: str):
    claims=list(src.get("what_was_verified") or [])
    if claim not in claims:
        claims.append(claim)
    src["what_was_verified"]=claims


def enrich(dataset, delay=0.18):
    out=deepcopy(dataset)
    report={
        "pipeline":"current-only-duden-enrichment-v1",
        "accessed_at":str(date.today()),
        "legacy_inputs_used":False,
        "units_total":len(out.get("learning_units",[])),
        "verbs":0,"duden_pages_ok":0,"duden_pages_failed":0,
        "verbs_with_3plus_collocations":0,"collocations_added":0,
        "synonyms_added":0,"antonyms_added":0,"evidence_claims_added":0,
        "failures":[]
    }
    session=requests.Session()
    for unit in out.get("learning_units",[]):
        if unit.get("type")!="verb":
            continue
        report["verbs"]+=1
        src=duden_source(unit)
        if not src:
            report["failures"].append({"id":unit.get("id"),"reason":"NO_CURRENT_DUDEN_SOURCE"})
            continue
        try:
            html=fetch_page(session, src["locator"])
            soup=BeautifulSoup(html,"html.parser")
            terms,syns,ants,dtext=extract_duden(soup, unit.get("headword", ""))
            report["duden_pages_ok"]+=1
        except Exception as e:
            report["duden_pages_failed"]+=1
            report["failures"].append({"id":unit.get("id"),"url":src.get("locator"),"reason":type(e).__name__})
            continue

        conns=[c for c in unit.get("connections",[]) if isinstance(c,dict)]
        existing={(c.get("kind"),norm(c.get("text","" )).casefold()) for c in conns}
        added=0
        for phrase in make_collocations(unit.get("headword",""), terms):
            key=("collocation",phrase.casefold())
            if key not in existing:
                conns.append({"text":phrase,"kind":"collocation"})
                existing.add(key); added+=1
        if conns:
            unit["connections"]=conns
        if added:
            add_claim(src,"collocation")
            src["accessed_at"]=str(date.today())
            src["evidence_note"]=(src.get("evidence_note","") + " Current-only v3.1.10 enrichment: Duden 'Typische Verbindungen' was used for collocational evidence; no legacy enrichment artifacts were used.").strip()
            report["collocations_added"]+=added
            report["evidence_claims_added"]+=1

        details=unit.setdefault("details",{})
        current_syn=[norm(x) for x in details.get("synonyms",[]) if norm(str(x))]
        for s in syns:
            if s.casefold()!=norm(unit.get("headword","")).casefold() and s.casefold() not in {x.casefold() for x in current_syn}:
                current_syn.append(s); report["synonyms_added"]+=1
            if len(current_syn)>=2: break
        if current_syn:
            details["synonyms"]=current_syn
            if syns:
                add_claim(src,"synonymy"); report["evidence_claims_added"]+=1

        current_ant=[norm(x) for x in details.get("antonyms",[]) if norm(str(x))]
        for a in ants:
            if a.casefold()!=norm(unit.get("headword","")).casefold() and a.casefold() not in {x.casefold() for x in current_ant}:
                current_ant.append(a); report["antonyms_added"]+=1
            if len(current_ant)>=2: break
        if current_ant:
            details["antonyms"]=current_ant
            if ants:
                add_claim(src,"antonymy"); report["evidence_claims_added"]+=1

        if details.get("rection") and evidence_matches_rection(dtext, details.get("rection")):
            add_claim(src,"rection"); report["evidence_claims_added"]+=1

        ncoll=sum(1 for c in unit.get("connections",[]) if c.get("kind")=="collocation" and norm(c.get("text","")))
        if ncoll>=3: report["verbs_with_3plus_collocations"]+=1
        time.sleep(delay)
    return out, report


def type_alias(t):
    return {
      "verb":"verb","nomen":"noun","adjektiv":"adjective","adverb":"adverb","praeposition":"preposition",
      "konnektor":"conjunction","konjunktion":"conjunction","pronomen":"pronoun","artikelwort":"artikelwort",
      "partikel":"particle","interjektion":"interjection","redemittel":"phrase","phrase":"phrase","idiom":"idiom",
      "redewendung":"idiom","kollokation":"collocation","nomen_verb_verbindung":"nvv","satzmuster":"sentence_pattern",
      "satz":"sentence","frage_antwort":"qa","grammatische_struktur":"grammar_structure","numeral":"numeral",
      "abkuerzung":"abbreviation","generic":"custom"
    }.get(t,t or "custom")


def delivery_examples(unit):
    de=[]; en=[]
    for ex in unit.get("examples",[]):
        de.append({"lang":"de-DE","text":ex.get("text","")})
        for tr in ex.get("translations",[]):
            if tr.get("lang")=="en-US":
                en.append({"lang":"en-US","text":tr.get("text","")})
                break
    return de+en


def build_tsv(dataset, profile, path: Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=BASE_HEADER,delimiter="\t",lineterminator="\n",quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for u in dataset.get("learning_units",[]):
            details=u.get("details") if isinstance(u.get("details"),dict) else {}
            core=u.get("core") if isinstance(u.get("core"),dict) else {}
            conns=u.get("connections") if isinstance(u.get("connections"),list) else []
            related=details.get("synonyms",[]) if isinstance(details.get("synonyms"),list) else []
            opposites=details.get("antonyms",[]) if isinstance(details.get("antonyms"),list) else []
            cf={
              "entry_type":type_alias(u.get("type")),"canonical_entry_type":u.get("type"),"learning_unit_id":u.get("id"),
              "semantic_identity":u.get("id"),"german_learning_contract":"gfp-german-learning-content@1.0.0",
              "semantic_contract":"gfp-german-language-content@3.1.3","source_profile_id":dataset.get("profile_id"),
              "german_definition":u.get("definition_de", ""),"english":u.get("english_gloss", ""),"canonical_unit":u
            }
            if u.get("type")=="verb":
                cf.update({"present":core.get("present_3sg"),"preterite":core.get("preterite_3sg"),"perfect":core.get("perfect"),
                           "participle_ii":core.get("participle_ii"),"auxiliary":core.get("auxiliary"),"reflexive":core.get("reflexive"),
                           "is_reflexive":core.get("reflexive"),"is_separable":core.get("separability")=="separable",
                           "rection":"; ".join(details.get("rection",[])) if isinstance(details.get("rection"),list) else details.get("rection","")})
            display_details={"core":core,"details":details,"connections":conns}
            row={
              "id":u.get("id",""),"card_type":"de-vocabulary","domain":"German","category":u.get("type",""),
              "source":profile.get("dataset",{}).get("title") or profile.get("dataset",{}).get("id",""),"level":profile.get("cefr",""),
              "lesson":"","deck":"","front":u.get("headword",""),"back":u.get("persian_meaning",""),"front_label":"Deutsch",
              "back_label":"فارسی","front_lang":profile.get("languages",{}).get("source",{}).get("lang","de-DE"),"back_lang":"fa-IR",
              "typing_target":"front-core","examples":json.dumps(delivery_examples(u),ensure_ascii=False,separators=(",",":")),
              "related":"; ".join(related),"opposites":"; ".join(opposites),
              "details":json.dumps(display_details,ensure_ascii=False,separators=(",",":")),
              "custom_fields":json.dumps(cf,ensure_ascii=False,separators=(",",":")),
              "tags":";".join(u.get("metadata",{}).get("tags",[]) or []),"notes":"","order":u.get("metadata",{}).get("unit_order","")
            }
            w.writerow(row)


def sha256(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--baseline",required=True,type=Path)
    ap.add_argument("--profile",required=True,type=Path)
    ap.add_argument("--outdir",required=True,type=Path)
    ap.add_argument("--delay",type=float,default=0.18)
    ns=ap.parse_args()
    dataset=read_json(ns.baseline); profile=read_json(ns.profile)
    repaired,report=enrich(dataset,ns.delay)
    ns.outdir.mkdir(parents=True,exist_ok=True)
    canonical=ns.outdir/"MENSCHEN-A1-CANONICAL-CONTENT-VALIDATED.json"
    tsv=ns.outdir/"MENSCHEN-A1-UNIVERSAL-v2.tsv"
    write_json(canonical,repaired)
    write_json(ns.outdir/"CURRENT-ONLY-ENRICHMENT-REPORT.json",report)
    build_tsv(repaired,profile,tsv)
    write_json(ns.outdir/"BUILD-METADATA.json",{
      "artifact_type":"gfp-data-build-metadata","metadata_version":"1.0","prompt_version":"v3.1.10",
      "validator_version":"v3.1.10","data_build_id":"menschen-a1-v3.1.10-current-only",
      "schema_profile":"universal-v2","data_file":tsv.name,"data_sha256":sha256(tsv),
      "canonical_file":canonical.name,"canonical_sha256":sha256(canonical),"legacy_inputs_used":False,
      "enrichment_sources":["current v3.1.9 canonical baseline","live Duden pages already bound in current provenance"]
    })
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
