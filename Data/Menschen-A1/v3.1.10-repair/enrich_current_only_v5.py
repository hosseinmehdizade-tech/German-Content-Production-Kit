#!/usr/bin/env python3
from __future__ import annotations

from urllib.parse import quote
from bs4 import BeautifulSoup
import enrich_current_only_v2 as base
import enrich_current_only_v4 as v4


def wiki_data(session,headword):
    lemma=v4.lemma_from_headword(headword)
    if not lemma:
        raise RuntimeError('no_lemma')
    url='https://de.wiktionary.org/wiki/'+quote(lemma.replace(' ','_'),safe='')
    r=session.get(url,headers=base.HEADERS,timeout=8)
    r.raise_for_status()
    soup=BeautifulSoup(r.text,'html.parser')
    lines=[base.clean_wiki_text(x) for x in soup.get_text('\n',strip=True).splitlines()]
    lines=[x for x in lines if x]
    combo_lines=v4.between(lines,[r'Charakteristische Wortkombinationen:?'],[r'Wortbildungen:?',r'Übersetzungen:?',r'Referenzen und weiterführende Informationen:?'])
    syn_lines=v4.between(lines,[r'Synonyme:?'],[r'Sinnverwandte Wörter:?',r'Gegenwörter:?',r'Oberbegriffe:?',r'Unterbegriffe:?',r'Beispiele:?',r'Charakteristische Wortkombinationen:?'])
    if not syn_lines:
        syn_lines=v4.between(lines,[r'Sinnverwandte Wörter:?'],[r'Gegenwörter:?',r'Oberbegriffe:?',r'Unterbegriffe:?',r'Beispiele:?',r'Charakteristische Wortkombinationen:?'])
    ant_lines=v4.between(lines,[r'Gegenwörter:?',r'Antonyme:?'],[r'Oberbegriffe:?',r'Unterbegriffe:?',r'Beispiele:?',r'Charakteristische Wortkombinationen:?',r'Wortbildungen:?'])
    combos=base.split_combinations(combo_lines,lemma)
    syns=base.extract_terms(syn_lines)
    ants=base.extract_terms(ant_lines)
    text=base.norm(soup.get_text(' ',strip=True))
    return {'lemma':lemma,'url':url,'collocations':combos,'synonyms':syns,'antonyms':ants,'text':text}

base.wiki_data=wiki_data

if __name__=='__main__':
    base.main()
