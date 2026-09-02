#!/usr/bin/env python3
from __future__ import annotations
import re,time
from urllib.parse import quote
from bs4 import BeautifulSoup,Tag
import enrich_rich_card_v2 as base

# Never depend on hash-randomized set order for sense/search anchors.
base.PREPS=('an','auf','aus','bei','durch','für','gegen','in','mit','nach','über','um','unter','von','vor','zu','zwischen')


def _label_dl(soup,pattern):
    rx=re.compile(r'^\s*(?:'+pattern+r')\s*:?\s*$',re.I)
    for text in soup.find_all(string=rx):
        parent=text.parent
        for sib in parent.next_siblings:
            if isinstance(sib,Tag):
                if sib.name=='dl': return sib
                # A new bold label means this section has no dl payload.
                if sib.name=='p' and 'font-weight:bold' in str(sib.get('style','')).replace(' ',''): break
    return None

def _marked_dd(dl,maxlen=320):
    out=[]; seen=set()
    if not dl: return out
    for dd in dl.find_all('dd'):
        text=base.norm(dd.get_text(' ',strip=True))
        m=re.match(r'^\[([^\]]+)\]\s*(.*)$',text)
        sense=m.group(1).strip() if m else ''
        body=m.group(2).strip() if m else text
        # Strip trailing numeric reference decorations rendered by Wiktionary.
        body=re.sub(r'\s*\[\s*\d+\s*\]\s*$','',body).strip()
        if not body or len(body)>maxlen: continue
        key=(sense,body.casefold())
        if key not in seen:
            seen.add(key); out.append({'sense':sense,'text':body})
    return out

def _atomic_relations(dl,max_items=80):
    out=[]; seen=set()
    if not dl: return out
    for dd in dl.find_all('dd'):
        raw=base.norm(dd.get_text(' ',strip=True))
        m=re.match(r'^\[([^\]]+)\]\s*(.*)$',raw)
        sense=m.group(1).strip() if m else ''
        body=m.group(2).strip() if m else raw
        body=re.sub(r'^(?:mit\s+(?:Substantiv|Verb|Adjektiv|Adverb|Präposition)|ohne\s+nähere\s+Bestimmung)\s*:\s*','',body,flags=re.I)
        # Comma/semicolon-separated Wiktionary relations are atomic. Slash-expanded
        # compressed paradigms are skipped unless the resulting fragment is already
        # a complete phrase; this avoids inventing combinations.
        for part in re.split(r'\s*[,;]\s*',body):
            part=base.norm(part).strip(' ,;:')
            if not part or len(part)>150: continue
            if ' / ' in part: continue
            key=(sense,part.casefold())
            if key not in seen:
                seen.add(key); out.append({'sense':sense,'text':part})
                if len(out)>=max_items: return out
    return out

def wiki_fetch_current(session,lemma):
    url='https://de.wiktionary.org/wiki/'+quote(lemma.replace(' ','_'),safe='')
    r=session.get(url,headers=base.UA,timeout=25); r.raise_for_status(); soup=BeautifulSoup(r.text,'html.parser')
    return {
      'url':url,
      'definitions':_marked_dd(_label_dl(soup,r'Bedeutungen'),320),
      'examples':_marked_dd(_label_dl(soup,r'Beispiele'),240),
      'collocations':_atomic_relations(_label_dl(soup,r'Charakteristische Wortkombinationen')),
      'synonyms':_atomic_relations(_label_dl(soup,r'Synonyme|Sinnverwandte Wörter')),
      'antonyms':_atomic_relations(_label_dl(soup,r'Gegenwörter|Antonyme')),
    }

def source_preps_explicit(unit):
    # Only an explicit learner headword/construction may constrain the sense.
    # Incidental prepositions in source example sentences are not Rektion evidence.
    return base.headword_preps(unit.get('headword',''))

def derive_rection_precise(unit):
    h=base.norm(unit.get('headword',''))
    raw=' '.join(base.norm(s.get('evidence_note')) for s in (unit.get('provenance') or {}).get('sources',[]) if isinstance(s,dict))
    preps=base.headword_preps(h); vals=[]
    explicit_case=''
    if re.search(r'\((?:Dat)\.?\)|\[\+D\]|\bjdm\.?\b|\bjmdm\.?\b',h+' '+raw,re.I): explicit_case='Dativ'
    elif re.search(r'\((?:Akk)\.?\)|\[\+A\]|\bjdn\.?\b|\bjmdn\.?\b',h+' '+raw,re.I): explicit_case='Akkusativ'
    for p in preps:
        c=explicit_case or base.FIXED_CASE.get(p)
        if c: vals.append(f'{p} + {c}')
    if not vals:
        if re.search(r'\bjdn\.?\b|\bjmdn\.?\b',h,re.I): vals.append('jemanden + Akkusativ')
        if re.search(r'\bjdm\.?\b|\bjmdm\.?\b',h,re.I): vals.append('jemandem + Dativ')
    return list(dict.fromkeys(vals))

def tatoeba_fetch_broader(session,query,pages=3):
    # First query the exact construction; if the result pool is small, broaden to
    # the lemma and let the downstream explicit-anchor filter keep the sense.
    def fetch(q,n):
        rows=[]
        for page in range(1,n+1):
            url='https://tatoeba.org/en/api_v0/search?from=deu&query='+quote(q)+'&page='+str(page)
            r=session.get(url,headers=base.UA,timeout=25); r.raise_for_status(); data=r.json(); batch=data.get('results') or []
            rows.extend(batch)
            if len(batch)<10: break
            time.sleep(.04)
        return rows
    rows=fetch(query,5)
    if ' ' in query and len(rows)<50:
        rows+=fetch(query.split()[0],5)
    out=[]; seen=set()
    for x in rows:
        key=x.get('id') or base.norm(x.get('text')).casefold()
        if key not in seen: seen.add(key); out.append(x)
    return out

base.wiki_fetch=wiki_fetch_current
base.source_preps=source_preps_explicit
base.derive_rection=derive_rection_precise
base.tatoeba_fetch=tatoeba_fetch_broader

# Patch the base enrichment loop only at the point needed to reuse sense-matched
# Wiktionary examples. It first runs the audited base flow, then tops up German
# examples from the exact same cached Wiktionary record without fabricating text.
_orig_enrich=base.enrich

def enrich_with_wiki_examples(ds,seed,cache,max_units=None,delay=.12):
    out,attempts,failures,counts,cache=_orig_enrich(ds,seed,cache,max_units,delay)
    wiki_cache=cache.get('wiktionary',{})
    added=0
    for u in out.get('learning_units',[]):
        lemma=base.lookup_lemma(u.get('headword','')); wd=wiki_cache.get(lemma) or {}
        if wd.get('error') or not wd.get('examples'): continue
        anchors=source_preps_explicit(u)
        selected=base.sense_match(wd.get('definitions',[]),anchors)
        sense=selected.get('sense','') if selected else ''
        candidates=base.same_sense(wd.get('examples',[]),sense,lemma,anchors,8)
        existing={base.norm(x.get('text')).casefold() for x in u.get('examples',[]) if isinstance(x,dict)}
        ids=[]
        for text in candidates:
            if len(u.get('examples',[]))>=5: break
            if text.casefold() in existing: continue
            n=len(u.get('examples',[]))+1
            u.setdefault('examples',[]).append({'id':f"{u['id']}-ex-{n:03d}",'lang':'de-DE','text':text,'order':n,'translations':[]})
            existing.add(text.casefold()); ids.append(str(n)); added+=1
        if ids:
            base.add_source(u,'de_wiktionary_live',['example_attestation'],wd.get('url',''),'Sense-filtered examples from the explicit Wiktionary Beispiele section; no example-derived text is relabeled as a collocation.')
    counts['wiktionary_examples_added']=added
    return out,attempts,failures,counts,cache

base.enrich=enrich_with_wiki_examples

if __name__=='__main__': base.main()
