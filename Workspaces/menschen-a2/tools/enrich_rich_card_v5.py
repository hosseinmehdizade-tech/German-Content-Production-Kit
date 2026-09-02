#!/usr/bin/env python3
from __future__ import annotations
import re
from collections import Counter

import enrich_rich_card_v4 as v4

base=v4.base
base.PREPS=('an','auf','aus','bei','durch','für','gegen','in','mit','nach','über','um','unter','von','vor','zu','zwischen','ohne','seit','außer','gegenüber')
CASE_RE=re.compile(r'(?:\((?:Dat|Akk|Nom|Gen)\.?\)|\[(?:\+)?[ADNG]\])',re.I)
DA_FORMS={
 'an':('daran','woran'),'auf':('darauf','worauf'),'aus':('daraus','woraus'),'bei':('dabei','wobei'),
 'für':('dafür','wofür'),'gegen':('dagegen','wogegen'),'in':('darin','worin'),'mit':('damit','womit'),
 'nach':('danach','wonach'),'über':('darüber','worüber'),'um':('darum','worum'),'unter':('darunter','worunter'),
 'von':('davon','wovon'),'vor':('davor','wovor'),'zu':('dazu','wozu')
}
REFL_RE=re.compile(r'\b(mich|dich|sich|uns|euch)\b',re.I)
REGISTER_PREFIX_RE=re.compile(r'^(?:Präpositionalgruppe|Adverbialbestimmung|umgangssprachlich|ugs\.?|gehoben|selten|veraltet|regional|landschaftlich|fachsprachlich|übertragen|Sport)\s*:\s*',re.I)


def lookup_lemma(headword):
    h=base.norm(headword)
    h=CASE_RE.sub(' ',h)
    h=re.sub(r'^sich\s+','',h,flags=re.I)
    h=re.sub(r'\b(?:jdn\.?|jdm\.?|jmdn\.?|jmdm\.?|jemanden|jemandem|etw\.?|etwas)\b',' ',h,flags=re.I)
    toks=[]
    for raw in re.split(r'\s+',h):
        t=raw.strip('.,;:()[]{}')
        if not t or t.casefold() in base.PREPS or t.startswith('+'):
            continue
        if t.casefold() in {'dat','akk','nom','gen','dativ','akkusativ','nominativ','genitiv'}:
            continue
        toks.append(t)
    return toks[-1] if toks else ''


def contains_anchor(text,prep):
    low=base.norm(text).casefold()
    if re.search(rf'\b{re.escape(prep)}\b',low):
        return True
    return any(re.search(rf'\b{re.escape(x)}\b',low) for x in DA_FORMS.get(prep,()))


def sense_anchors(unit):
    explicit=base.headword_preps(unit.get('headword',''))
    if explicit:
        return explicit
    ex=base.source_example(unit)
    return [p for p in base.PREPS if contains_anchor(ex,p)][:2]


def tatoeba_examples(items,anchors,reflexive,limit=5):
    out=[];seen=set()
    for item in items:
        text=base.norm(item.get('text'))
        if not text or len(text)<12 or len(text)>180:
            continue
        if anchors and not all(contains_anchor(text,a) for a in anchors[:1]):
            continue
        if reflexive and not REFL_RE.search(text):
            continue
        en=''
        for grp in item.get('translations') or []:
            for tr in grp or []:
                if tr.get('lang')=='eng' and base.norm(tr.get('text')):
                    en=base.norm(tr.get('text'));break
            if en:break
        if not en:continue
        key=text.casefold()
        if key in seen:continue
        seen.add(key);out.append({'sentence_id':item.get('id'),'text':text,'en':en})
        if len(out)>=limit:break
    return out


def clean_relation(text):
    return base.norm(REGISTER_PREFIX_RE.sub('',base.norm(text))).strip(' ,;:')

_orig_wiki=v4.wiki_fetch_current

def wiki_fetch_quality(session,lemma):
    wd=_orig_wiki(session,lemma)
    for field in ('collocations','synonyms','antonyms'):
        cleaned=[];seen=set()
        for e in wd.get(field) or []:
            t=clean_relation(e.get('text'))
            if not t or len(t)>100 or any(ch in t for ch in ':,;/'):
                continue
            if field=='collocations' and not re.search(rf'\b{re.escape(lemma)}\b',t,re.I):
                continue
            key=(e.get('sense',''),t.casefold())
            if key in seen:continue
            seen.add(key);cleaned.append({'sense':e.get('sense',''),'text':t})
        if field=='antonyms':
            counts=Counter(e.get('sense','') for e in cleaned)
            cleaned=[e for e in cleaned if counts[e.get('sense','')]<=2 and not e['text'].startswith('-')]
        wd[field]=cleaned
    return wd


def structural_example_ok(unit,text):
    if unit.get('type')!='phrase':
        return True
    explicit=base.headword_preps(unit.get('headword',''))
    if explicit and not all(contains_anchor(text,a) for a in explicit[:1]):
        return False
    if base.norm(unit.get('headword')).casefold().startswith('sich ') and not REFL_RE.search(text):
        return False
    return True

base.lookup_lemma=lookup_lemma
base.source_preps=sense_anchors
v4.source_preps_explicit=sense_anchors
base.tatoeba_examples=tatoeba_examples
base.wiki_fetch=wiki_fetch_quality
_orig_enrich=base.enrich


def enrich_quality(ds,seed,cache,max_units=None,delay=.12):
    out,attempts,failures,counts,cache=_orig_enrich(ds,seed,cache,max_units,delay)
    for u in out.get('learning_units',[]):
        exs=u.get('examples') if isinstance(u.get('examples'),list) else []
        if not exs:continue
        kept=[exs[0]]
        for ex in exs[1:]:
            if isinstance(ex,dict) and structural_example_ok(u,ex.get('text','')):
                kept.append(ex)
        for i,ex in enumerate(kept,1):
            ex['id']=f"{u['id']}-ex-{i:03d}";ex['order']=i
        u['examples']=kept
    cache_w=cache.get('wiktionary',{})
    byid={a.get('id'):a for a in attempts if isinstance(a,dict)}
    for u in out.get('learning_units',[]):
        a=byid.get(u.get('id'))
        if not a:continue
        lemma=lookup_lemma(u.get('headword',''));wd=cache_w.get(lemma) or {}
        sel=base.sense_match(wd.get('definitions',[]),sense_anchors(u)) if not wd.get('error') else None
        a['selected_wiktionary_sense']=sel.get('sense','') if isinstance(sel,dict) else ''
        a['examples_after_quality_filter']=len(u.get('examples',[]))
    counts['units_below_4_after_quality_filter']=sum(len(u.get('examples',[]))<4 for u in out.get('learning_units',[]))
    return out,attempts,failures,counts,cache

base.enrich=enrich_quality

if __name__=='__main__':
    base.main()
