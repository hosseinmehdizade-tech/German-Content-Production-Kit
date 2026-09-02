#!/usr/bin/env python3
from __future__ import annotations
from urllib.parse import quote
from bs4 import BeautifulSoup
import enrich_rich_card_v2 as base


def wiki_fetch_legacy(session,lemma):
    # Wiktionary's Parsoid HTML flattens Bedeutungen/Beispiele/Wortkombinationen
    # into labels rather than section headings. The legacy parser preserves the
    # h-level section structure expected by the audited extractor.
    url='https://de.wiktionary.org/w/index.php?title='+quote(lemma.replace(' ','_'),safe='')+'&useparsoid=0'
    r=session.get(url,headers=base.UA,timeout=25); r.raise_for_status(); soup=BeautifulSoup(r.text,'html.parser')
    return {
      'url':url,
      'definitions':base.parse_marked(base.raw_lines(base.section_nodes(soup,r'^Bedeutungen'))),
      'collocations':base.parse_marked(base.raw_lines(base.section_nodes(soup,r'Charakteristische Wortkombinationen')),180),
      'synonyms':base.parse_marked(base.raw_lines(base.section_nodes(soup,r'^(Synonyme|Sinnverwandte Wörter)')),100),
      'antonyms':base.parse_marked(base.raw_lines(base.section_nodes(soup,r'^(Gegenwörter|Antonyme)')),100),
    }

base.wiki_fetch=wiki_fetch_legacy

if __name__=='__main__':
    base.main()
