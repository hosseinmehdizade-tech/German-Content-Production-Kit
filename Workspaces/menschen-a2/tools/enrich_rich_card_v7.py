#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,time
from datetime import date
from pathlib import Path

import enrich_rich_card_v6 as v6

base=v6.base
v5=v6.v5

# Patch the deterministic grammar decoder before the inherited enrichment chain
# enters the v2 base loop. Direct complement-bound case notation such as
# "sich etw. (Dat.) verschließen" is learner-facing evidence; bare source [+A]/[+D]
# shorthand was normalized out at Stage 2 and is never reconstructed here.
_orig_rection=base.derive_rection

def derive_rection_v7(unit):
    vals=list(_orig_rection(unit) or [])
    h=base.norm(unit.get('headword',''))
    if not base.headword_preps(h):
        m=re.search(r'\betw(?:as)?\.?\s*\((Dat|Akk)\.?\)',h,re.I)
        if m:
            vals.append('etwas + '+('Dativ' if m.group(1).lower().startswith('dat') else 'Akkusativ'))
    return list(dict.fromkeys(vals))

base.derive_rection=derive_rection_v7


def _reflexive_unit(unit):
    return bool((unit.get('core') or {}).get('reflexive')) or base.norm(unit.get('headword')).casefold().startswith('sich ')


def _has_reflexive(text):
    return bool(v5.REFL_RE.search(base.norm(text)))


def _single_lexical_phrase(unit,lemma):
    h=base.norm(unit.get('headword'))
    return bool(re.fullmatch(r'[A-Za-zÄÖÜäöüß-]+',h)) and h.casefold()==base.norm(lemma).casefold()


def _source_authorizes_nonreflexive_surface(unit):
    # Some source constructions explicitly pair a reflexive construction with a
    # non-reflexive/passive paraphrase (e.g. "sich auf etw. einrichten" and
    # "darauf eingerichtet sein"). We only relax the reflexive-surface filter when
    # the authoritative primary source example itself demonstrates that alternate
    # surface while preserving the explicit prepositional anchor.
    if not base.norm(unit.get('headword')).casefold().startswith('sich '): return False
    anchors=base.headword_preps(unit.get('headword',''))
    src=base.source_example(unit)
    if not anchors or not src or _has_reflexive(src): return False
    return all(v5.contains_anchor(src,a) for a in anchors[:1])


def residual_example_ok(unit,text,lemma=None):
    text=base.norm(text); lemma=lemma or v5.lookup_lemma(unit.get('headword',''))
    if not text or len(text)<8 or len(text)>220 or not lemma: return False
    typ=unit.get('type')
    if typ=='verb':
        expected_refl=_reflexive_unit(unit); actual_refl=_has_reflexive(text)
        if expected_refl != actual_refl: return False
        anchors=base.headword_preps(unit.get('headword',''))
        if anchors and not all(v5.contains_anchor(text,a) for a in anchors[:1]): return False
        return True
    if typ=='phrase':
        if _single_lexical_phrase(unit,lemma): return True
        anchors=base.headword_preps(unit.get('headword',''))
        if anchors and not all(v5.contains_anchor(text,a) for a in anchors[:1]): return False
        if base.norm(unit.get('headword')).casefold().startswith('sich ') and not _has_reflexive(text):
            if not _source_authorizes_nonreflexive_surface(unit): return False
        # An unanchored multiword phrase is not broadened to generic lemma examples.
        if not anchors and not base.norm(unit.get('headword')).casefold().startswith('sich '): return False
        return True
    return False


_orig_enrich=base.enrich

def enrich_residual_floor(ds,seed,cache,max_units=None,delay=.12):
    out,attempts,failures,counts,cache=_orig_enrich(ds,seed,cache,max_units,delay)
    vf_cache=cache.setdefault('verbformen_examples',{})
    processed=out.get('learning_units',[])[:max_units] if max_units else out.get('learning_units',[])
    sess=base.requests.Session() if hasattr(base,'requests') else __import__('requests').Session()
    added=0; attempted=0; by_type={'verb':0,'phrase':0}; added_by_type={'verb':0,'phrase':0}
    for u in processed:
        if u.get('type') not in {'verb','phrase'} or len(u.get('examples') or [])>=5: continue
        lemma=v5.lookup_lemma(u.get('headword',''))
        if not lemma: continue
        # Plain lexical phrases are allowed here because Stage 2 may type a source
        # row as phrase solely because the source omitted a standalone paradigm.
        if u.get('type')=='phrase' and not (_single_lexical_phrase(u,lemma) or base.headword_preps(u.get('headword','')) or _reflexive_unit(u)):
            continue
        attempted+=1; by_type[u['type']]+=1
        vf=vf_cache.get(lemma)
        if vf is None:
            try:
                vf=v6.verbformen_fetch(sess,lemma); vf_cache[lemma]=vf; time.sleep(delay)
            except Exception as e:
                vf={'url':'https://www.verbformen.de/konjugation/beispiele/'+lemma+'.htm','error':type(e).__name__+': '+str(e),'examples':[]}; vf_cache[lemma]=vf
        existing={base.norm(x.get('text')).casefold() for x in (u.get('examples') or []) if isinstance(x,dict)}
        picked=[]
        for item in vf.get('examples',[]):
            if len(u.get('examples') or [])>=5: break
            text=base.norm(item.get('text'))
            if not text or text.casefold() in existing or not residual_example_ok(u,text,lemma): continue
            n=len(u.get('examples') or [])+1
            u.setdefault('examples',[]).append({'id':f"{u['id']}-ex-{n:03d}",'lang':'de-DE','text':text,'order':n,'translations':[]})
            existing.add(text.casefold()); picked.append(text); added+=1; added_by_type[u['type']]+=1
        if picked:
            base.add_source(u,'verbformen_examples',['example_attestation'],vf.get('url',''),'Exact-lemma external German example attestation. Residual examples are accepted only after unit-type, reflexive-surface and explicit-anchor filters; no source-page English is projected as learner content.')
    # Synchronize per-unit attempt records with the final post-fallback artifact.
    byid={a.get('id'):a for a in attempts if isinstance(a,dict)}
    for u in processed:
        a=byid.get(u.get('id'))
        if not a: continue
        src_ids=[s.get('source_id') for s in (u.get('provenance') or {}).get('sources',[]) if isinstance(s,dict)]
        if 'verbformen_examples' in src_ids:
            ss=a.setdefault('sources',[])
            if 'verbformen_examples' not in ss: ss.append('verbformen_examples')
            a['status']='success'
        a['examples_after']=len(u.get('examples') or [])
        a['examples_after_all_filters']=len(u.get('examples') or [])
        a['lexical_detail_count']=sum(1 for c in (u.get('connections') or []) if isinstance(c,dict) and base.norm(c.get('text')))+sum(len((u.get('details') or {}).get(f,[]) or []) for f in ('rection','synonyms','antonyms','variants'))
    counts['verbformen_residual_examples_added']=added
    counts['verbformen_residual_units_attempted']=attempted
    counts['verbformen_residual_attempted_by_type']=by_type
    counts['verbformen_residual_added_by_type']=added_by_type
    counts['processed_units_below_4_after_v7']=sum(len(u.get('examples') or [])<4 for u in processed)
    return out,attempts,failures,counts,cache

base.enrich=enrich_residual_floor


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--canonical',required=True); ap.add_argument('--seed',required=True); ap.add_argument('--out',required=True); ap.add_argument('--evidence',required=True); ap.add_argument('--cache',required=True); ap.add_argument('--max-units',type=int); ap.add_argument('--delay',type=float,default=.12); a=ap.parse_args()
    ds=base.load(a.canonical); seed=base.load(a.seed).get('items',{}); cp=Path(a.cache); cache=base.load(cp) if cp.exists() else {'schema_version':'1.0.0','accessed_at':str(date.today())}
    out,attempts,failures,counts,cache=base.enrich(ds,seed,cache,a.max_units,a.delay)
    if a.max_units: out['learning_units']=out['learning_units'][:a.max_units]
    base.dump(a.out,out); base.dump(a.cache,cache)
    units=out.get('learning_units',[]); verbs=[u for u in units if u.get('type')=='verb']; phrases=[u for u in units if u.get('type')=='phrase']
    source_ids=sorted({s.get('source_id') for u in units for s in (u.get('provenance') or {}).get('sources',[]) if isinstance(s,dict) and s.get('source_id')})
    ev={'schema_version':'2.1.0','dataset':'menschen-a2','stage':3,'status':'RUNNING','canonical_units':len(units),'external_lexical_enrichment_used':any(x.get('status')=='success' for x in attempts if x.get('type')=='verb'),'external_evidence_attempts':attempts,'failures':failures,'counts':counts,'coverage':{'verbs':len(verbs),'phrases':len(phrases),'verbs_with_definition':sum(bool(base.norm(u.get('definition_de'))) for u in verbs),'units_with_4plus_examples':sum(len(u.get('examples') or [])>=4 for u in units),'verbs_with_any_lexical_detail':sum((sum(1 for c in (u.get('connections') or []) if isinstance(c,dict) and base.norm(c.get('text')))+sum(len((u.get('details') or {}).get(f,[]) or []) for f in ('rection','synonyms','antonyms','variants')))>0 for u in verbs)},'evidence_sources':source_ids,'evidence_index_note':'RUNNING until the exact enriched artifact passes the mandatory product-floor preflight and Stage 3 enrichment validation; this file may be durably persisted as WIP without constituting PASS.'}
    base.dump(a.evidence,ev)
    print(json.dumps(ev['coverage']|counts,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
