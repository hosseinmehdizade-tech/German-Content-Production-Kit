#!/usr/bin/env python3
from __future__ import annotations

import re
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

import enrich_current_only_v2 as base

API = "https://de.wiktionary.org/w/api.php"


def _parse_json(session, **params):
    q={"action":"parse","format":"json","formatversion":"2","redirects":"1"}
    q.update(params)
    r=session.get(API,params=q,headers=base.HEADERS,timeout=25)
    r.raise_for_status()
    data=r.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("code","mediawiki_error"))
    return data["parse"]


def _section_index(session, page, patterns):
    parsed=_parse_json(session,page=page,prop="sections")
    for sec in parsed.get("sections",[]):
        line=base.norm(BeautifulSoup(sec.get("line",""),"html.parser").get_text(" ",strip=True))
        if any(re.search(p,line,re.I) for p in patterns):
            return sec.get("index")
    return None


def _section_lines(session,page,patterns):
    idx=_section_index(session,page,patterns)
    if idx is None:
        return []
    parsed=_parse_json(session,page=page,prop="text",section=str(idx))
    html=parsed.get("text","")
    soup=BeautifulSoup(html,"html.parser")
    lines=[]
    for li in soup.find_all("li"):
        t=base.clean_wiki_text(li.get_text(" ",strip=True))
        if t:
            lines.append(t)
    if not lines:
        for p in soup.find_all(["p","dd"]):
            t=base.clean_wiki_text(p.get_text(" ",strip=True))
            if t:
                lines.append(t)
    return lines


def wiki_data(session, headword):
    lemma=base.lookup_lemma(headword)
    if not lemma:
        return None
    # API is used only against the live German Wiktionary. Nothing is read from legacy project artifacts.
    combos=base.split_combinations(_section_lines(session,lemma,[r"Charakteristische Wortkombinationen"]),lemma)
    syns=base.extract_terms(_section_lines(session,lemma,[r"^Synonyme$",r"^Sinnverwandte Wörter$"]))
    ants=base.extract_terms(_section_lines(session,lemma,[r"^Gegenwörter$",r"^Antonyme$"]))
    full=_parse_json(session,page=lemma,prop="text").get("text","")
    text=base.norm(BeautifulSoup(full,"html.parser").get_text(" ",strip=True))
    url="https://de.wiktionary.org/wiki/"+quote(lemma.replace(" ","_"),safe="")
    return {"lemma":lemma,"url":url,"collocations":combos,"synonyms":syns,"antonyms":ants,"text":text}


base.wiki_data=wiki_data

if __name__=="__main__":
    base.main()
