#!/usr/bin/env python3
from __future__ import annotations

import re
from urllib.parse import quote

from bs4 import BeautifulSoup
import enrich_current_only_v2 as base

API="https://de.wiktionary.org/w/api.php"
STOP={"sich","jdn","jdm","jemanden","jemandem","etw","etwas","an","auf","aus","bei","durch","für","gegen","in","mit","nach","über","um","unter","von","vor","zu","zwischen","akk","dat","gen"}


def lemma_from_headword(headword):
    h=base.norm(headword).casefold()
    h=re.sub(r"\+\s*(akk|dat|gen)\.?\b.*$","",h,flags=re.I)
    toks=re.findall(r"[a-zäöüß]+",h,flags=re.I)
    useful=[t for t in toks if t.casefold() not in STOP]
    return useful[-1] if useful else (toks[-1] if toks else "")


def parse_live(session,lemma):
    params={"action":"parse","page":lemma,"prop":"text","format":"json","formatversion":"2","redirects":"1"}
    r=session.get(API,params=params,headers=base.HEADERS,timeout=25)
    r.raise_for_status(); data=r.json()
    if "error" in data: raise RuntimeError(data["error"].get("code","mediawiki_error"))
    html=data["parse"].get("text","")
    soup=BeautifulSoup(html,"html.parser")
    raw=soup.get_text("\n",strip=True)
    lines=[base.clean_wiki_text(x) for x in raw.splitlines()]
    lines=[x for x in lines if x]
    return html,lines


def between(lines,start_patterns,end_patterns):
    start=None
    for i,x in enumerate(lines):
        if any(re.fullmatch(p,x,re.I) or re.search(p,x,re.I) for p in start_patterns):
            start=i+1; break
    if start is None: return []
    out=[]
    for x in lines[start:]:
        if any(re.fullmatch(p,x,re.I) for p in end_patterns): break
        if x.lower() in {"bearbeiten"}: continue
        out.append(x)
    return out

END_LABELS=[r"Wortbildungen:?",r"Übersetzungen:?",r"Referenzen und weiterführende Informationen:?",r"Beispiele:?",r"Gegenwörter:?",r"Sinnverwandte Wörter:?",r"Synonyme:?",r"Unterbegriffe:?",r"Oberbegriffe:?",r"Redewendungen:?",r"Sprichwörter:?",r"Charakteristische Wortkombinationen:?"]


def section(lines,label):
    return between(lines,[rf"{re.escape(label)}:?"],[p for p in END_LABELS if not re.fullmatch(p,label+":",re.I)])


def wiki_data(session,headword):
    lemma=lemma_from_headword(headword)
    if not lemma: raise RuntimeError("no_lemma")
    html,lines=parse_live(session,lemma)
    combo_lines=between(lines,[r"Charakteristische Wortkombinationen:?"],[r"Wortbildungen:?",r"Übersetzungen:?",r"Referenzen und weiterführende Informationen:?"])
    syn_lines=between(lines,[r"Synonyme:?"],[r"Sinnverwandte Wörter:?",r"Gegenwörter:?",r"Oberbegriffe:?",r"Unterbegriffe:?",r"Beispiele:?",r"Charakteristische Wortkombinationen:?"])
    if not syn_lines:
        syn_lines=between(lines,[r"Sinnverwandte Wörter:?"],[r"Gegenwörter:?",r"Oberbegriffe:?",r"Unterbegriffe:?",r"Beispiele:?",r"Charakteristische Wortkombinationen:?"])
    ant_lines=between(lines,[r"Gegenwörter:?",r"Antonyme:?"],[r"Oberbegriffe:?",r"Unterbegriffe:?",r"Beispiele:?",r"Charakteristische Wortkombinationen:?",r"Wortbildungen:?"])
    combos=base.split_combinations(combo_lines,lemma)
    syns=base.extract_terms(syn_lines)
    ants=base.extract_terms(ant_lines)
    text=base.norm(BeautifulSoup(html,"html.parser").get_text(" ",strip=True))
    url="https://de.wiktionary.org/wiki/"+quote(lemma.replace(" ","_"),safe="")
    return {"lemma":lemma,"url":url,"collocations":combos,"synonyms":syns,"antonyms":ants,"text":text}

base.wiki_data=wiki_data

if __name__=="__main__":
    base.main()
