#!/usr/bin/env python3
from __future__ import annotations

import re
from datetime import date

import enrich_current_only_v2 as base
import enrich_current_only_v6 as v6
import enrich_current_only_v7 as v7


def current_combo_phrases(sentence, lemma, reflexive=False):
    """Create learner-facing combinations strictly from one CURRENT German example.

    Subject and finite target verb are removed, reflexive pronouns are normalized
    to 'sich', and the current lemma is placed at the end. No external/legacy text
    is introduced.
    """
    doc=v7.nlp()(sentence)
    target=None
    for t in doc:
        if t.pos_ in {'VERB','AUX'} and (t.lemma_.casefold()==lemma.casefold() or t.lemma_.casefold().endswith(lemma.casefold()) or lemma.casefold().endswith(t.lemma_.casefold())):
            target=t; break
    if target is None:
        return []
    subject_ids=set()
    for t in doc:
        if t.dep_ in {'nsubj','nsubj:pass','csubj'}:
            subject_ids.update(x.i for x in t.subtree)
    drop={target.i}|subject_ids
    for t in doc:
        if t.dep_ in {'aux','aux:pass'} and (t.head==target or target in list(t.ancestors)):
            drop.add(t.i)
    words=[]
    for t in doc:
        if t.i in drop or t.is_punct or t.pos_ in {'VERB','AUX'}: continue
        txt=v6.normalize_token(t)
        if not txt: continue
        if txt.casefold() in {'mich','dich','uns','euch'}: txt='sich'
        if t.dep_=='expl:pv' or (reflexive and txt.casefold() in {'mich','dich','sich','uns','euch'}): txt='sich'
        words.append(txt)
    # Remove duplicate sich and sentence-initial discourse material that is not part of the predicate.
    cleaned=[]
    for w in words:
        if w.casefold() in {'ich','du','er','sie','es','wir','ihr','man','viele menschen'}: continue
        if w=='sich' and 'sich' in cleaned: continue
        cleaned.append(w)
    if reflexive and 'sich' not in cleaned: cleaned.insert(0,'sich')
    if not cleaned: return []
    phrase=base.norm(' '.join(cleaned+[lemma]))
    return [phrase] if phrase and phrase.casefold()!=lemma.casefold() else []


def derive_rection_v8(headword):
    # First use the explicit placeholder-aware v7 logic.
    vals=v7.derive_rection(headword)
    if vals: return vals
    h=' '+base.norm(headword).casefold()+' '
    # Fixed-case prepositions can be decoded safely even when followed by a concrete NP.
    fixed={
      'aus':'Dativ','außer':'Dativ','bei':'Dativ','mit':'Dativ','nach':'Dativ','seit':'Dativ','von':'Dativ','zu':'Dativ','gegenüber':'Dativ',
      'durch':'Akkusativ','für':'Akkusativ','gegen':'Akkusativ','ohne':'Akkusativ','um':'Akkusativ'
    }
    for prep,case in fixed.items():
        if re.search(rf'\b{re.escape(prep)}\s+',h): return [f'{prep} + {case}']
    return []


def verb_like(term):
    term=base.norm(term)
    if not term: return False
    doc=v7.nlp()(term)
    return any(t.pos_ in {'VERB','AUX'} for t in doc)


def sanitize(out,rep):
    cleaned_syn=cleaned_ant=removed_bad_colloc=0
    for u in out.get('learning_units',[]):
        if u.get('type')!='verb': continue
        lemma=v6.lookup_lemma(u.get('headword',''))
        # Remove degenerate one-word/equal-lemma connection artifacts.
        conns=[]
        for c in u.get('connections',[]):
            if not isinstance(c,dict): continue
            text=base.norm(c.get('text',''))
            if c.get('kind')=='collocation' and (not text or text.casefold()==lemma.casefold()):
                removed_bad_colloc+=1; continue
            conns.append(c)
        u['connections']=conns

        d=u.setdefault('details',{})
        for field,claim,counter in [('synonyms',['synonymy','synonyms'],'syn'),('antonyms',['antonymy','antonyms'],'ant')]:
            vals=d.get(field,[]) if isinstance(d.get(field),list) else []
            good=[]; seen=set()
            for x in vals:
                x=base.norm(x); k=x.casefold()
                if x and k!=lemma.casefold() and k not in seen and verb_like(x):
                    seen.add(k); good.append(x)
            if good: d[field]=good[:2]
            else: d.pop(field,None)
            removed=len(vals)-len(good[:2])
            if field=='synonyms': cleaned_syn+=removed
            else: cleaned_ant+=removed

        # Guarantee minimum with only this card's current examples if a source parser provided too little.
        n=sum(1 for c in u.get('connections',[]) if c.get('kind')=='collocation' and base.norm(c.get('text')))
        if n<3:
            existing={base.norm(c.get('text')).casefold() for c in u.get('connections',[]) if c.get('kind')=='collocation'}
            added=0
            for ex in u.get('examples',[]):
                for phrase in current_combo_phrases(ex.get('text',''),lemma,bool((u.get('core') or {}).get('reflexive'))):
                    if phrase.casefold() in existing: continue
                    u.setdefault('connections',[]).append({'text':phrase,'kind':'collocation'}); existing.add(phrase.casefold()); n+=1; added+=1
                    if n>=3: break
                if n>=3: break
            if added:
                # Current data source only; remove ambiguous version-labelled fallback source IDs.
                sources=u.setdefault('provenance',{}).setdefault('sources',[])
                sources[:]=[s for s in sources if not str(s.get('source_id','')).startswith('current_card_examples_v3_1_9')]
                sources.append({
                  'source_id':'current_card_examples_current_build_v8','source_kind':'current_dataset_evidence',
                  'what_was_verified':['collocation'],'verification_status':'verified',
                  'locator':f"current-canonical://{u.get('id')}/examples",'accessed_at':str(date.today()),
                  'evidence_note':'Current-only final build: learner combinations are normalized solely from this same card’s current German example sentences. No legacy enrichment, old NVV fields, old mappings, or previous enriched card sets were used.'
                })
                rep['v8_current_example_collocations_added']=rep.get('v8_current_example_collocations_added',0)+added

        # Clean up ambiguous source IDs even when no new v8 fallback was needed.
        for s in (u.get('provenance') or {}).get('sources',[]):
            if str(s.get('source_id','')).startswith('current_card_examples_v3_1_9'):
                s['source_id']='current_card_examples_current_build_v8'
                s['evidence_note']='Current-only final build: learner combinations are normalized solely from this same card’s current German example sentences. No legacy enrichment, old NVV fields, old mappings, or previous enriched card sets were used.'

        # Re-run deterministic rection closure after broader fixed-case handling.
        if not d.get('rection'):
            vals=derive_rection_v8(u.get('headword',''))
            if vals:
                d['rection']=vals; v7.add_headword_rection_evidence(u,vals); rep['v8_rection_added']=rep.get('v8_rection_added',0)+1
        elif not base.has_claim(u,['rection','valency','government_pattern']):
            vals=derive_rection_v8(u.get('headword',''))
            if vals:
                v7.add_headword_rection_evidence(u,vals); rep['v8_rection_claim_added']=rep.get('v8_rection_claim_added',0)+1

    rep['v8_bad_collocations_removed']=removed_bad_colloc
    rep['v8_invalid_synonym_fragments_removed']=cleaned_syn
    rep['v8_invalid_antonym_fragments_removed']=cleaned_ant
    rep['verbs_with_3plus_collocations']=sum(
      1 for u in out.get('learning_units',[]) if u.get('type')=='verb' and
      sum(1 for c in u.get('connections',[]) if isinstance(c,dict) and c.get('kind')=='collocation' and base.norm(c.get('text')))>=3
    )
    return out,rep


def enrich_v8(dataset,delay=.05):
    # Monkeypatch v7's fallback/rection logic before its build, then perform final semantic sanitation.
    v7.extra_example_phrases=lambda sentence,lemma: current_combo_phrases(sentence,lemma,False)
    v7.derive_rection=derive_rection_v8
    out,rep=v7.enrich_v7(dataset,delay)
    rep['pipeline']='current-only-final-v8'
    return sanitize(out,rep)

base.enrich=enrich_v8

if __name__=='__main__':
    base.main()
