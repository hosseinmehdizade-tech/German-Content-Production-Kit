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
            n=len(u.get('examples',[]))+1;trs=[]
            if item.get('en'):trs=[{'lang':'en-US','text':item['en']}]
            u.setdefault('examples',[]).append({'id':f"{u['id']}-ex-{n:03d}",'lang':'de-DE','text':text,'order':n,'translations':trs})
            existing.add(text.casefold());picked.append(text);added+=1
        if picked:
            base.add_source(u,'verbformen_examples',['example_attestation']+(['english_example_translation'] if any(x.get('en') for x in vf.get('examples',[])) else []),vf.get('url',''),'External conjugation/example corpus fallback. Only examples matching the explicit phrase preposition/reflexive structure are retained; it is not used as broad sense evidence.')
    counts['verbformen_phrase_examples_added']=added
    counts['verbformen_phrase_units_attempted']=attempted
    counts['processed_units_below_4_after_all_filters']=sum(len(u.get('examples',[]))<4 for u in processed)
    return out,attempts,failures,counts,cache

base.enrich=enrich_with_phrase_fallback

if __name__=='__main__':base.main()
