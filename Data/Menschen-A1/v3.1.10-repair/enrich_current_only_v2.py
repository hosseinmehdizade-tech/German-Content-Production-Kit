#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, hashlib, json, re, time
from copy import deepcopy
from datetime import date
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup, Tag

HEADERS={"User-Agent":"Mozilla/5.0 (compatible; German-Content-Production-Kit/3.1.10; +https://github.com/hosseinmehdizade-tech/German-Content-Production-Kit)"}
BASE_HEADER=["id","card_type","domain","category","source","level","lesson","deck","front","back","front_label","back_label","front_lang","back_lang","typing_target","examples","related","opposites","details","custom_fields","tags","notes","order"]


def read_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def write_json(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def norm(s): return re.sub(r"\s+"," ",(str(s) if s is not None else "").replace("\u00ad","").strip())

def lookup_lemma(headword):
    h=norm(headword)
    h=re.sub(r"^sich\s+","",h,flags=re.I)
    h=re.sub(r"\s+(?:an|auf|aus|bei|durch|für|gegen|in|mit|nach|über|um|unter|von|vor|zu|zwischen)\b.*$","",h,flags=re.I)
    h=re.sub(r"\s*\+\s*(?:Akk\.?|Dat\.?|Gen\.?).*$","",h,flags=re.I)
    return h.split()[0] if h else ""

def fetch(session,url):
    r=session.get(url,headers=HEADERS,timeout=25); r.raise_for_status(); return r.text

def heading_level(tag):
    if not isinstance(tag,Tag) or not tag.name or not re.fullmatch(r"h[1-6]",tag.name): return None
    return int(tag.name[1])

def section_nodes(soup, pattern):
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        title=norm(h.get_text(" ",strip=True))
        if re.search(pattern,title,re.I):
            lvl=heading_level(h); out=[]
            for sib in h.next_siblings:
                sl=heading_level(sib)
                if sl is not None and sl<=lvl: break
                out.append(sib)
            return out
    return []

def clean_wiki_text(s):
    s=norm(s)
    s=re.sub(r"^\[[^\]]+\]\s*","",s)
    s=re.sub(r"\s*\(Audio\s*\(Info\)\)\s*"," ",s,flags=re.I)
    s=re.sub(r"\s*Audio\s*\(Info\)\s*"," ",s,flags=re.I)
    s=re.sub(r"\s+"," ",s).strip(" ,;:")
    return s

def node_lines(nodes):
    lines=[]
    for n in nodes:
        if not isinstance(n,Tag): continue
        lis=n.find_all("li") if n.name!="li" else [n]
        if lis:
            for li in lis:
                t=clean_wiki_text(li.get_text(" ",strip=True))
                if t: lines.append(t)
        else:
            t=clean_wiki_text(n.get_text(" ",strip=True))
            if t: lines.append(t)
    return lines

def split_combinations(lines,lemma):
    out=[]; seen=set(); lowlemma=lemma.casefold()
    for line in lines:
        for semi in re.split(r"\s*;\s*",line):
            semi=clean_wiki_text(semi)
            if not semi: continue
            parts=[clean_wiki_text(x) for x in re.split(r"\s*,\s*",semi) if clean_wiki_text(x)]
            if len(parts)>1 and all(lowlemma in p.casefold() for p in parts): candidates=parts
            else: candidates=[semi]
            for c in candidates:
                if lowlemma not in c.casefold(): continue
                if len(c)>120: continue
                key=c.casefold()
                if key not in seen:
                    seen.add(key); out.append(c)
    return out

def extract_terms(lines):
    out=[]; seen=set()
    for line in lines:
        for part in re.split(r"\s*[,;]\s*",line):
            p=clean_wiki_text(part)
            p=re.sub(r"^\[[^\]]+\]\s*","",p)
            if not p or len(p)>64: continue
            k=p.casefold()
            if k not in seen: seen.add(k); out.append(p)
    return out

def wiki_data(session,headword):
    lemma=lookup_lemma(headword)
    if not lemma: return None
    url="https://de.wiktionary.org/wiki/"+quote(lemma.replace(" ","_"),safe="")
    html=fetch(session,url); soup=BeautifulSoup(html,"html.parser")
    combos=split_combinations(node_lines(section_nodes(soup,r"Charakteristische Wortkombinationen")),lemma)
    syns=extract_terms(node_lines(section_nodes(soup,r"^(Synonyme|Sinnverwandte Wörter)")))
    ants=extract_terms(node_lines(section_nodes(soup,r"^(Gegenwörter|Antonyme)")))
    return {"lemma":lemma,"url":url,"collocations":combos,"synonyms":syns,"antonyms":ants,"text":norm(soup.get_text(" ",strip=True))}

def has_claim(unit,claims):
    want=set(claims)
    for s in (unit.get("provenance") or {}).get("sources",[]):
        if s.get("verification_status")=="verified" and want.intersection(s.get("what_was_verified") or []): return True
    return False

def wiki_source(unit,data,claims):
    sources=unit.setdefault("provenance",{}).setdefault("sources",[])
    src={"source_id":"de_wiktionary_live","source_kind":"lexicon","what_was_verified":sorted(set(claims)),"verification_status":"verified","locator":data["url"],"accessed_at":str(date.today()),"evidence_note":"Current-only v3.1.10 enrichment from the live German Wiktionary entry. Collocations are copied only from the explicit 'Charakteristische Wortkombinationen' section. No legacy enrichment artifact is used."}
    sources.append(src)

def rection_supported(text,rection):
    vals=rection if isinstance(rection,list) else [rection]
    preps=[]
    for x in vals:
        m=re.match(r"\s*([A-Za-zÄÖÜäöüß]+)",str(x))
        if m: preps.append(m.group(1).casefold())
    low=text.casefold()
    return bool(preps) and all(re.search(rf"\b{re.escape(p)}\b",low) for p in preps)

def enrich(dataset,delay):
    out=deepcopy(dataset); s=requests.Session()
    rep={"pipeline":"current-only-live-wiktionary-v2","accessed_at":str(date.today()),"legacy_inputs_used":False,"units_total":len(out.get("learning_units",[])),"verbs":0,"wiktionary_pages_ok":0,"wiktionary_pages_failed":0,"verbs_with_3plus_collocations":0,"collocations_added":0,"synonyms_verified_or_added":0,"antonyms_verified_or_added":0,"rection_claims_added":0,"failures":[]}
    for u in out.get("learning_units",[]):
        if u.get("type")!="verb": continue
        rep["verbs"]+=1
        try:
            wd=wiki_data(s,u.get("headword","")); rep["wiktionary_pages_ok"]+=1
        except Exception as e:
            rep["wiktionary_pages_failed"]+=1; rep["failures"].append({"id":u.get("id"),"headword":u.get("headword"),"reason":type(e).__name__}); time.sleep(delay); continue
        claims=[]
        conns=[x for x in u.get("connections",[]) if isinstance(x,dict)]
        existing={(x.get("kind"),norm(x.get("text")).casefold()) for x in conns}
        for phrase in wd["collocations"][:4]:
            key=("collocation",phrase.casefold())
            if key not in existing: conns.append({"text":phrase,"kind":"collocation"}); existing.add(key); rep["collocations_added"]+=1
        if wd["collocations"]: claims.append("collocation")
        if conns: u["connections"]=conns
        d=u.setdefault("details",{})
        if wd["synonyms"]:
            vals=[]; seen=set()
            for x in list(d.get("synonyms",[]) or [])+wd["synonyms"]:
                x=norm(x); k=x.casefold()
                if x and k!=wd["lemma"].casefold() and k not in seen: seen.add(k); vals.append(x)
                if len(vals)>=2: break
            if vals: d["synonyms"]=vals; claims.append("synonymy"); rep["synonyms_verified_or_added"]+=1
        elif d.get("synonyms") and not has_claim(u,["synonymy","synonyms"]):
            d.pop("synonyms",None)
        if wd["antonyms"]:
            vals=[]; seen=set()
            for x in list(d.get("antonyms",[]) or [])+wd["antonyms"]:
                x=norm(x); k=x.casefold()
                if x and k!=wd["lemma"].casefold() and k not in seen: seen.add(k); vals.append(x)
                if len(vals)>=2: break
            if vals: d["antonyms"]=vals; claims.append("antonymy"); rep["antonyms_verified_or_added"]+=1
        elif d.get("antonyms") and not has_claim(u,["antonymy","antonyms"]):
            d.pop("antonyms",None)
        if d.get("rection") and not has_claim(u,["rection","valency","government_pattern"]) and rection_supported(wd["text"],d.get("rection")):
            claims.append("rection"); rep["rection_claims_added"]+=1
        if claims: wiki_source(u,wd,claims)
        n=sum(1 for c in u.get("connections",[]) if c.get("kind")=="collocation" and norm(c.get("text")))
        if n>=3: rep["verbs_with_3plus_collocations"]+=1
        time.sleep(delay)
    return out,rep

def type_alias(t):
    return {"verb":"verb","nomen":"noun","adjektiv":"adjective","adverb":"adverb","praeposition":"preposition","konnektor":"conjunction","konjunktion":"conjunction","pronomen":"pronoun","artikelwort":"artikelwort","partikel":"particle","interjektion":"interjection","redemittel":"phrase","phrase":"phrase","idiom":"idiom","redewendung":"idiom","kollokation":"collocation","nomen_verb_verbindung":"nvv","satzmuster":"sentence_pattern","satz":"sentence","frage_antwort":"qa","grammatische_struktur":"grammar_structure","numeral":"numeral","abkuerzung":"abbreviation","generic":"custom"}.get(t,t or "custom")
def delivery_examples(u):
    out=[]
    for ex in u.get("examples",[]):
        out.append({"lang":"de-DE","text":ex.get("text","")})
        for tr in ex.get("translations",[]):
            if tr.get("lang")=="en-US": out.append({"lang":"en-US","text":tr.get("text","")}); break
    return out

def build_tsv(ds,profile,path):
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=BASE_HEADER,delimiter="\t",lineterminator="\n"); w.writeheader()
        for u in ds.get("learning_units",[]):
            d=u.get("details") or {}; core=u.get("core") or {}; conns=u.get("connections") or []
            cf={"entry_type":type_alias(u.get("type")),"canonical_entry_type":u.get("type"),"learning_unit_id":u.get("id"),"semantic_identity":u.get("id"),"german_learning_contract":"gfp-german-learning-content@1.0.0","semantic_contract":"gfp-german-language-content@3.1.3","source_profile_id":ds.get("profile_id"),"german_definition":u.get("definition_de",""),"english":u.get("english_gloss",""),"canonical_unit":u}
            if u.get("type")=="verb": cf.update({"present":core.get("present_3sg"),"preterite":core.get("preterite_3sg"),"perfect":core.get("perfect"),"participle_ii":core.get("participle_ii"),"auxiliary":core.get("auxiliary"),"reflexive":core.get("reflexive"),"is_reflexive":core.get("reflexive"),"is_separable":core.get("separability")=="separable","rection":"; ".join(d.get("rection",[])) if isinstance(d.get("rection"),list) else d.get("rection","")})
            w.writerow({"id":u.get("id",""),"card_type":"de-vocabulary","domain":"German","category":u.get("type",""),"source":profile.get("dataset",{}).get("title") or profile.get("dataset",{}).get("id",""),"level":profile.get("cefr",""),"lesson":"","deck":"","front":u.get("headword",""),"back":u.get("persian_meaning",""),"front_label":"Deutsch","back_label":"فارسی","front_lang":"de-DE","back_lang":"fa-IR","typing_target":"front-core","examples":json.dumps(delivery_examples(u),ensure_ascii=False,separators=(",",":")),"related":"; ".join(d.get("synonyms",[]) or []),"opposites":"; ".join(d.get("antonyms",[]) or []),"details":json.dumps({"core":core,"details":d,"connections":conns},ensure_ascii=False,separators=(",",":")),"custom_fields":json.dumps(cf,ensure_ascii=False,separators=(",",":")),"tags":";".join(u.get("metadata",{}).get("tags",[]) or []),"notes":"","order":u.get("metadata",{}).get("unit_order","")})
def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--baseline",required=True); ap.add_argument("--profile",required=True); ap.add_argument("--outdir",required=True); ap.add_argument("--delay",type=float,default=.08); a=ap.parse_args()
    ds=read_json(a.baseline); profile=read_json(a.profile); repaired,rep=enrich(ds,a.delay); out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    canon=out/"MENSCHEN-A1-CANONICAL-CONTENT-VALIDATED.json"; tsv=out/"MENSCHEN-A1-UNIVERSAL-v2.tsv"; write_json(canon,repaired); write_json(out/"CURRENT-ONLY-ENRICHMENT-REPORT.json",rep); build_tsv(repaired,profile,tsv)
    write_json(out/"BUILD-METADATA.json",{"artifact_type":"gfp-data-build-metadata","metadata_version":"1.0","prompt_version":"v3.1.10","data_build_id":"menschen-a1-v3.1.10-current-only","schema_profile":"universal-v2","data_file":tsv.name,"data_sha256":sha256(tsv),"canonical_file":canon.name,"canonical_sha256":sha256(canon),"legacy_inputs_used":False,"enrichment_sources":["current v3.1.9 canonical baseline","live German Wiktionary pages"]})
    print(json.dumps(rep,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
