#!/usr/bin/env python3
from __future__ import annotations
import json
from copy import deepcopy
from datetime import date
from pathlib import Path

import enrich_rich_card_v7 as v7

base=v7.base
ROOT=Path(__file__).resolve().parents[1]
FALLBACK_PATH=ROOT/'tools/RESIDUAL-PEDAGOGICAL-EXAMPLES-v1.json'


def _norm(s):
    return base.norm(s)


def _add_generated_source(unit, added_texts):
    if not added_texts:
        return
    srcs=unit.setdefault('provenance',{}).setdefault('sources',[])
    srcs.append({
        'source_id':'assistant_pedagogical_example',
        'source_kind':'generated',
        'what_was_verified':[],
        'verification_status':'unverified',
        'locator':f"generated://menschen-a2/{unit.get('id')}/product-floor-residual-v1",
        'accessed_at':str(date.today()),
        'evidence_note':'Targeted pedagogical German examples generated only after Wiktionary, Tatoeba and Verbformen retrieval still left this unit below the mandatory four-example product floor. They are not represented as corpus attestations. They were constrained to the canonical sense/structure and remain subject to downstream linguistic QA.'
    })


def _generated_fallback(out, max_units=None):
    cfg=json.loads(FALLBACK_PATH.read_text(encoding='utf-8'))
    items=cfg.get('items',{})
    processed=out.get('learning_units',[])[:max_units] if max_units else out.get('learning_units',[])
    added=0; touched=[]; unresolved=[]
    for u in processed:
        exs=u.get('examples') if isinstance(u.get('examples'),list) else []
        if len(exs)>=4:
            continue
        uid=u.get('id'); candidates=items.get(uid,[])
        existing={_norm(x.get('text')).casefold() for x in exs if isinstance(x,dict) and _norm(x.get('text'))}
        added_here=[]
        for text in candidates:
            if len(exs)>=4:
                break
            text=_norm(text)
            if not text or text.casefold() in existing:
                continue
            # Preserve the stronger phrase-structure guard developed in v5/v7.
            if u.get('type')=='phrase' and not v7.v6.v5.structural_example_ok(u,text):
                continue
            n=len(exs)+1
            exs.append({'id':f"{uid}-ex-{n:03d}",'lang':'de-DE','text':text,'order':n,'translations':[]})
            existing.add(text.casefold()); added_here.append(text); added+=1
        u['examples']=exs
        if added_here:
            _add_generated_source(u,added_here)
            touched.append({'id':uid,'added':added_here,'final_example_count':len(exs)})
        if len(exs)<4:
            unresolved.append({'id':uid,'headword':u.get('headword'),'example_count':len(exs)})
    return added,touched,unresolved


_orig_enrich=base.enrich

def enrich_v8(ds,seed,cache,max_units=None,delay=.12):
    out,attempts,failures,counts,cache=_orig_enrich(ds,seed,cache,max_units,delay)
    added,touched,unresolved=_generated_fallback(out,max_units)
    counts['generated_residual_examples_added']=added
    counts['generated_residual_units_touched']=len(touched)
    counts['generated_residual_unresolved_units']=len(unresolved)
    counts['processed_units_below_4_after_v8']=sum(len(u.get('examples',[]))<4 for u in (out.get('learning_units',[])[:max_units] if max_units else out.get('learning_units',[])))
    cache['generated_residual_v1']={'source':str(FALLBACK_PATH.relative_to(ROOT)),'touched':touched,'unresolved':unresolved}
    return out,attempts,failures,counts,cache

base.enrich=enrich_v8

if __name__=='__main__':
    base.main()
