#!/usr/bin/env python3
from __future__ import annotations
import re,time
from urllib.parse import quote

from bs4 import BeautifulSoup
import enrich_rich_card_v5 as v5

base=v5.base


def verbformen_fetch(session,lemma):
    url='https://www.verbformen.de/konjugation/beispiele/'+quote(lemma,safe='')+'.htm'
    r=session.get(url,headers=base.UA,timeout=25);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
    out=[];seen=set()
    for li in soup.find_all('li'):
        if not li.find('q'):continue
        # Verbformen marks the inflected verb with <q> pieces. Collapse those pieces
        # before reading the bilingual list item, otherwise "kuschel te" would leak.
        tmp=BeautifulSoup(str(li),'html.parser')
        for q in tmp.find_all('q'):
            q.replace_with(re.sub(r'\s+','',q.get_text('',strip=True)))
        text=base.norm(tmp.get_text(' ',strip=True))
        text=re.sub(r'\s+([,.!?;:])',r'\1',text)
        m=re.match(r'^(.+?[.!?])(?:\s+(.+))?$',text)
        if not m:continue
        de=base.norm(m.group(1));en=base.norm(m.group(2))
        if not de or len(de)<8 or len(de)>220:continue
        key=de.casefold()
        if key in seen:continue
        seen.add(key);out.append({'text':de,'en':en})
    return {'url':url,'examples':out}


def _looks_like_fragmentary_intransitive_collocation(unit,text,lemma):
    # Conservative parser-health guard for compressed Wiktionary lists such as
    # "im Freien, Hotel, Motel, Wohnwagen, Zelt übernachten" where splitting the
    # list can leave a false learner-facing fragment "Zelt übernachten".
    definition=base.norm(unit.get('definition_de')).casefold()
    if 'intransitiv' not in definition:return False
    tokens=base.norm(text).split()
    return len(tokens)==2 and tokens[-1].casefold()==lemma.casefold() and bool(re.match(r'^[A-ZÄÖÜ]',tokens[0]))

_orig_enrich=base.enrich

def enrich_with_phrase_fallback(ds,seed,cache,max_units=None,delay=.12):
    out,attempts,failures,counts,cache=_orig_enrich(ds,seed,cache,max_units,delay)
    vf_cache=cache.setdefault('verbformen_examples',{});added=0;attempted=0
    processed=out.get('learning_units',[])[:max_units] if max_units else out.get('learning_units',[])
    for u in processed:
        if u.get('type')!='phrase' or len(u.get('examples',[]))>=5:continue
        # Only use this fallback where the phrase itself gives a structural anchor.
        # This avoids broad lemma examples drifting across senses.
        anchors=base.headword_preps(u.get('headword',''))
        reflexive=base.norm(u.get('headword')).casefold().startswith('sich ')
        if not anchors and not reflexive:continue
        lemma=v5.lookup_lemma(u.get('headword',''))
        if not lemma:continue
        attempted+=1;vf=vf_cache.get(lemma)
        if vf is None:
            try:vf=verbformen_fetch(base.requests.Session() if hasattr(base,'requests') else __import__('requests').Session(),lemma);vf_cache[lemma]=vf;time.sleep(delay)
            except Exception as e:vf={'url':'https://www.verbformen.de/konjugation/beispiele/'+quote(lemma,safe='')+'.htm','error':type(e).__name__+': '+str(e),'examples':[]};vf_cache[lemma]=vf
        existing={base.norm(x.get('text')).casefold() for x in u.get('examples',[]) if isinstance(x,dict)};picked=[]
        for item in vf.get('examples',[]):
            if len(u.get('examples',[]))>=5:break
            text=item['text']
            if text.casefold() in existing or not v5.structural_example_ok(u,text):continue
            n=len(u.get('examples',[]))+1
            u.setdefault('examples',[]).append({'id':f"{u['id']}-ex-{n:03d}",'lang':'de-DE','text':text,'order':n,'translations':[]})
            existing.add(text.casefold());picked.append(text);added+=1
        if picked:
            base.add_source(u,'verbformen_examples',['example_attestation'],vf.get('url',''),'External conjugation/example corpus fallback. Only German examples matching the explicit phrase preposition/reflexive structure are retained; English text on the source page is not projected as learner content because extra-example translation quality is not a product requirement.')
    # Learner-facing English is intentionally the reviewed primary example only.
    # Corpus English pairs can be noisy (including gender mismatches) and must not
    # be retained merely because a corpus API returned them. Keep the external
    # German attestations, which are the evidence needed for the rich-card floor.
    extra_en_removed=0;fragment_collocations_removed=0
    for u in processed:
        exs=u.get('examples') if isinstance(u.get('examples'),list) else []
        for ex in exs[1:]:
            trs=ex.get('translations') if isinstance(ex.get('translations'),list) else []
            if any(isinstance(t,dict) and t.get('lang')=='en-US' for t in trs):extra_en_removed+=1
            ex['translations']=[t for t in trs if isinstance(t,dict) and t.get('lang')!='en-US']
        if u.get('definition_de'):
            u['definition_de']=re.sub(r'\s+([,;:.!?])',r'\1',base.norm(u['definition_de']))
        lemma=v5.lookup_lemma(u.get('headword',''))
        if lemma and isinstance(u.get('connections'),list):
            kept=[]
            for c in u['connections']:
                if isinstance(c,dict) and c.get('kind')=='collocation' and _looks_like_fragmentary_intransitive_collocation(u,c.get('text',''),lemma):
                    fragment_collocations_removed+=1;continue
                kept.append(c)
            if kept:u['connections']=kept
            else:u.pop('connections',None)
    counts['verbformen_phrase_examples_added']=added
    counts['verbformen_phrase_units_attempted']=attempted
    counts['extra_corpus_english_removed_for_quality']=extra_en_removed
    counts['fragmentary_collocations_removed']=fragment_collocations_removed
    counts['processed_units_below_4_after_all_filters']=sum(len(u.get('examples',[]))<4 for u in processed)
    return out,attempts,failures,counts,cache

base.enrich=enrich_with_phrase_fallback

if __name__=='__main__':base.main()
