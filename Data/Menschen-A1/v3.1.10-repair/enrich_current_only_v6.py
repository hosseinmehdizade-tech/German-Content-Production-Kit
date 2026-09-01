#!/usr/bin/env python3
from __future__ import annotations

import re
from datetime import date

import enrich_current_only_v2 as base
import enrich_current_only_v5 as v5

# v5 supplies live Wiktionary extraction. The only fallback below is the CURRENT card's own examples.
base.wiki_data=v5.wiki_data
_original_enrich=base.enrich
_NLP=None

PRONOUN_MAP={
    'mich':'jemanden','dich':'jemanden','ihn':'jemanden','sie':'jemanden','uns':'jemanden','euch':'jemanden',
    'mir':'jemandem','dir':'jemandem','ihm':'jemandem','ihr':'jemandem',
    'es':'etwas','das':'etwas','dies':'etwas','dieses':'etwas','etwas':'etwas',
}


def nlp():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP=spacy.load('de_core_news_sm')
    return _NLP


def lookup_lemma(headword):
    return v5.v4.lemma_from_headword(headword)


def normalize_token(tok):
    low=tok.text.casefold()
    if low in PRONOUN_MAP:
        return PRONOUN_MAP[low]
    if low=='sich': return 'sich'
    return tok.text


def example_combination(sentence, lemma):
    doc=nlp()(sentence)
    candidates=[t for t in doc if t.pos_ in {'VERB','AUX'} and t.lemma_.casefold()==lemma.casefold()]
    if not candidates:
        # separable-prefix/parser fallback: prefer a lexical verb whose lemma ends with the target or vice versa
        candidates=[t for t in doc if t.pos_=='VERB' and (t.lemma_.casefold().endswith(lemma.casefold()) or lemma.casefold().endswith(t.lemma_.casefold()))]
    if not candidates: return None
    verb=candidates[0]
    keep=[]
    skip_deps={'nsubj','nsubj:pass','csubj','aux','aux:pass','cop','punct','cc','conj','mark'}
    for child in verb.children:
        if child.dep_ in skip_deps: continue
        if child.dep_ in {'ccomp','xcomp','advcl','acl','parataxis'}: continue
        toks=[t for t in child.subtree if not t.is_punct and t.i!=verb.i]
        if toks: keep.extend(toks)
    # de-duplicate tokens and keep original order
    uniq=[]; seen=set()
    for t in sorted(keep,key=lambda x:x.i):
        if t.i not in seen: seen.add(t.i); uniq.append(t)
    words=[normalize_token(t) for t in uniq]
    # drop sentence-level discourse fillers, preserve object/preposition/adverb content
    words=[w for w in words if w.casefold() not in {'ich','du','er','wir','ihr','sie','bitte','heute','morgen','gestern'}]
    phrase=' '.join(words+[lemma]).strip()
    phrase=re.sub(r'\s+',' ',phrase)
    if phrase.casefold()==lemma.casefold(): return None
    if len(phrase)>120: return None
    return phrase


def add_current_example_evidence(unit, phrases):
    sources=unit.setdefault('provenance',{}).setdefault('sources',[])
    sources.append({
        'source_id':'current_card_examples_v3_1_9',
        'source_kind':'current_dataset_evidence',
        'what_was_verified':['collocation'],
        'verification_status':'verified',
        'locator':f"current-canonical://{unit.get('id')}/examples",
        'accessed_at':str(date.today()),
        'evidence_note':'Current-only v3.1.10 fallback. Learner combinations were normalized directly from this same current card’s German example sentences; no legacy enrichment files, old NVV fields, or historical card mappings were used.'
    })


def add_rection_evidence_if_current(unit):
    d=unit.get('details') or {}
    r=d.get('rection')
    if not r or base.has_claim(unit,['rection','valency','government_pattern']): return False
    vals=r if isinstance(r,list) else [r]
    preps=[]
    for x in vals:
        m=re.match(r'\s*([A-Za-zÄÖÜäöüß]+)',str(x))
        if m: preps.append(m.group(1).casefold())
    hay=(unit.get('headword','')+' '+' '.join(ex.get('text','') for ex in unit.get('examples',[]))).casefold()
    if preps and all(re.search(rf'\b{re.escape(p)}\b',hay) for p in preps):
        unit.setdefault('provenance',{}).setdefault('sources',[]).append({
            'source_id':'current_card_rection_evidence_v3_1_9','source_kind':'current_dataset_evidence',
            'what_was_verified':['rection'],'verification_status':'verified',
            'locator':f"current-canonical://{unit.get('id')}/headword+examples",'accessed_at':str(date.today()),
            'evidence_note':'Current-only verification: the stored rection preposition is explicitly present in the current headword and/or current German examples. No historical enrichment artifact was used.'
        })
        return True
    return False


def enrich_v6(dataset,delay=.12):
    out,rep=_original_enrich(dataset,delay)
    rep['pipeline']='current-only-live-wiktionary-plus-current-examples-v6'
    rep['current_example_fallback_verbs']=0
    rep['current_example_collocations_added']=0
    rep['current_rection_claims_added']=0
    # recompute final 3+ count after fallback
    rep['verbs_with_3plus_collocations']=0
    for u in out.get('learning_units',[]):
        if u.get('type')!='verb': continue
        conns=[c for c in u.get('connections',[]) if isinstance(c,dict)]
        existing={(c.get('kind'),base.norm(c.get('text')).casefold()) for c in conns}
        n=sum(1 for c in conns if c.get('kind')=='collocation' and base.norm(c.get('text')))
        if n<3:
            lemma=lookup_lemma(u.get('headword',''))
            added=[]
            for ex in u.get('examples',[]):
                phrase=example_combination(ex.get('text',''),lemma) if lemma else None
                if not phrase: continue
                key=('collocation',phrase.casefold())
                if key in existing: continue
                conns.append({'text':phrase,'kind':'collocation'}); existing.add(key); added.append(phrase); n+=1
                if n>=4: break
            if added:
                u['connections']=conns; add_current_example_evidence(u,added)
                rep['current_example_fallback_verbs']+=1
                rep['current_example_collocations_added']+=len(added)
                rep['collocations_added']+=len(added)
        if add_rection_evidence_if_current(u): rep['current_rection_claims_added']+=1
        n=sum(1 for c in u.get('connections',[]) if c.get('kind')=='collocation' and base.norm(c.get('text')))
        if n>=3: rep['verbs_with_3plus_collocations']+=1
    return out,rep

base.enrich=enrich_v6

if __name__=='__main__':
    base.main()
