#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,json,re,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import enrich_rich_card_v7 as v7

REFL=re.compile(r'\b(?:sich|mich|dich|uns|euch)\b',re.I)
GENERATED_SOURCE='assistant_pedagogical_example'

def norm(s): return v7.base.norm(s)

def refl_unit(u): return bool((u.get('core') or {}).get('reflexive')) or norm(u.get('headword')).casefold().startswith('sich ')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--cache',type=Path,required=True);ap.add_argument('--generated-spec',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);ns=ap.parse_args()
    src=json.loads(ns.input.read_text(encoding='utf-8'));out=copy.deepcopy(src);cache=json.loads(ns.cache.read_text(encoding='utf-8'));gen=json.loads(ns.generated_spec.read_text(encoding='utf-8')).get('items',{})
    generated_texts={uid:{norm(x).casefold() for x in vals} for uid,vals in gen.items()}
    removed_examples=[];removed_collocations=[];removed_generated=[];refilled=[]
    vf_cache=cache.get('verbformen_examples') or {}
    for u in out.get('learning_units',[]):
        if not isinstance(u,dict):continue
        uid=u.get('id');isrefl=refl_unit(u);exs=u.get('examples') if isinstance(u.get('examples'),list) else []
        kept=[]
        for j,e in enumerate(exs):
            if not isinstance(e,dict):continue
            text=norm(e.get('text'));key=text.casefold();reason=None
            if j>0 and key in generated_texts.get(uid,set()): reason='generated_product_floor_fallback'
            elif j>0 and isrefl and text and not REFL.search(text): reason='reflexive_surface_mismatch'
            if reason:
                rec={'id':uid,'headword':u.get('headword'),'example_id':e.get('id'),'text':text,'reason':reason};removed_examples.append(rec)
                if reason.startswith('generated_'): removed_generated.append(rec)
            else: kept.append(e)
        u['examples']=kept
        srcs=(u.get('provenance') or {}).get('sources')
        if isinstance(srcs,list):
            u['provenance']['sources']=[s for s in srcs if not (isinstance(s,dict) and s.get('source_id')==GENERATED_SOURCE)]
        conns=u.get('connections') if isinstance(u.get('connections'),list) else []
        kc=[]
        for c in conns:
            if isinstance(c,dict) and c.get('kind')=='collocation' and isrefl:
                text=norm(c.get('text'))
                if text and not REFL.search(text):
                    removed_collocations.append({'id':uid,'headword':u.get('headword'),'text':text,'reason':'reflexive_surface_mismatch'});continue
            kc.append(c)
        u['connections']=kc

    # Refill only cards made thin by the semantic cleanup, using the already-durable
    # Verbformen cache. No network requests and no generated learner content.
    for u in out.get('learning_units',[]):
        exs=u.get('examples') if isinstance(u.get('examples'),list) else []
        if len(exs)>=4: continue
        lemma=v7.v5.lookup_lemma(u.get('headword',''))
        vf=vf_cache.get(lemma) if lemma else None
        existing={norm(e.get('text')).casefold() for e in exs if isinstance(e,dict) and norm(e.get('text'))}
        added=[]
        for item in ((vf or {}).get('examples') or []):
            if len(exs)>=4: break
            text=norm(item.get('text') if isinstance(item,dict) else item)
            if not text or text.casefold() in existing: continue
            if not v7.residual_example_ok(u,text,lemma): continue
            exs.append({'id':'TEMP','lang':'de-DE','text':text,'order':0,'translations':[]});existing.add(text.casefold());added.append(text)
        if added:
            srcs=u.setdefault('provenance',{}).setdefault('sources',[])
            url=(vf or {}).get('url') or ('https://www.verbformen.de/konjugation/beispiele/'+str(lemma)+'.htm')
            if not any(isinstance(s,dict) and s.get('source_id')=='verbformen_examples' and s.get('locator')==url for s in srcs):
                srcs.append({'source_id':'verbformen_examples','source_kind':'other','what_was_verified':['example_attestation'],'verification_status':'verified','locator':url,'accessed_at':'2026-09-03','evidence_note':'Stage 4 semantic cleanup refill from the already-durable Stage 3 Verbformen cache. Accepted only after exact unit-type/reflexive/anchor filtering; no network refetch and no generated example.'})
            refilled.append({'id':u.get('id'),'headword':u.get('headword'),'lemma':lemma,'added':added,'source':url})
        u['examples']=exs

    # Re-number after removals/refills while keeping the authoritative primary at #001.
    for u in out.get('learning_units',[]):
        for i,e in enumerate(u.get('examples') or [],1):
            if isinstance(e,dict):e['id']=f"{u.get('id')}-ex-{i:03d}";e['order']=i

    below=[{'id':u.get('id'),'headword':u.get('headword'),'examples':len(u.get('examples') or [])} for u in out.get('learning_units',[]) if len(u.get('examples') or [])<4]
    generated_remaining=[];reflexive_example_remaining=[];reflexive_collocation_remaining=[]
    for u in out.get('learning_units',[]):
        uid=u.get('id');srcs=(u.get('provenance') or {}).get('sources') or []
        if any(isinstance(s,dict) and s.get('source_id')==GENERATED_SOURCE for s in srcs):generated_remaining.append(uid)
        if refl_unit(u):
            for e in (u.get('examples') or [])[1:]:
                if isinstance(e,dict) and norm(e.get('text')) and not REFL.search(norm(e.get('text'))):reflexive_example_remaining.append({'id':uid,'text':norm(e.get('text'))})
            for c in u.get('connections') or []:
                if isinstance(c,dict) and c.get('kind')=='collocation' and norm(c.get('text')) and not REFL.search(norm(c.get('text'))):reflexive_collocation_remaining.append({'id':uid,'text':norm(c.get('text'))})
    report={'status':'PASS' if not (below or generated_remaining or reflexive_example_remaining or reflexive_collocation_remaining) else 'FAIL','repair':'menschen-a2-stage4-semantic-alignment-v1','input':'02-canonical/CANONICAL-ENRICHED.json','output':'04-qa/CANONICAL-QA-REPAIRED.json','network_refetch':False,'generated_content_added':False,'removed_examples':removed_examples,'removed_generated_examples':removed_generated,'removed_collocations':removed_collocations,'cache_refills':refilled,'below4_after_cache_refill':below,'generated_provenance_remaining':generated_remaining,'reflexive_example_mismatches_remaining':reflexive_example_remaining,'reflexive_collocation_mismatches_remaining':reflexive_collocation_remaining}
    ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');ns.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v if not isinstance(v,list) else len(v) for k,v in report.items()},ensure_ascii=False,indent=2));raise SystemExit(0 if report['status']=='PASS' else 2)
if __name__=='__main__':main()
