#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path

GENERATED_SOURCE_ID='assistant_pedagogical_example'
GENERATED_LOCATOR_PREFIX='generated://menschen-a2/'
MINIMUM=4
MAXIMUM=6


def load(p:Path): return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p:Path,obj): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def norm(s): return re.sub(r'\s+',' ',str(s or '').strip()).casefold().rstrip('.!?')

def next_example_id(unit):
    highest=0
    for ex in unit.get('examples') or []:
        m=re.search(r'-ex-(\d+)$',str(ex.get('id') or '')) if isinstance(ex,dict) else None
        if m: highest=max(highest,int(m.group(1)))
    return f"{unit['id']}-ex-{highest+1:03d}"

def generated_texts(path:Path|None):
    if not path or not path.exists(): return set()
    d=load(path);out=set()
    for rows in (d.get('items') or {}).values():
        for row in rows if isinstance(rows,list) else []:
            if isinstance(row,dict) and row.get('text'): out.add(norm(row['text']))
    return out

def remove_generated(unit,bad_texts):
    before=len(unit.get('examples') or [])
    unit['examples']=[ex for ex in (unit.get('examples') or []) if not (isinstance(ex,dict) and norm(ex.get('text')) in bad_texts)]
    prov=unit.get('provenance') if isinstance(unit.get('provenance'),dict) else {'sources':[]}
    sources=[]
    for src in prov.get('sources') or []:
        if not isinstance(src,dict): continue
        sid=str(src.get('source_id') or '')
        loc=str(src.get('locator') or '')
        if sid==GENERATED_SOURCE_ID or loc.startswith(GENERATED_LOCATOR_PREFIX): continue
        sources.append(src)
    prov['sources']=sources;unit['provenance']=prov
    return before-len(unit['examples'])

def add_provenance(unit,cand):
    prov=unit.setdefault('provenance',{});sources=prov.setdefault('sources',[])
    sid=cand['source_id'];url=cand['url']
    if any(isinstance(x,dict) and x.get('source_id')==sid and x.get('locator')==url for x in sources): return
    sources.append({
      'source_id':sid,
      'source_kind':cand.get('source_kind','website'),
      'what_was_verified':['example_attestation','sense_alignment'],
      'verification_status':cand.get('verification_status','verified'),
      'locator':url,
      'accessed_at':'2026-09-03',
      'evidence_note':cand.get('evidence_note','Externally attested residual example used after source/corpus enrichment remained below the product floor.')
    })

def repair_vorstellen(unit):
    if unit.get('id')!='ma2-lu-0187': return False
    # Source row/example is the interpersonal introduction sense. Bind the
    # learner definition to Wiktionary [3b], not the spatial first sense.
    unit['definition_de']='jemanden einem anderen, der ihn nicht kennt, bekannt machen'
    details=unit.get('details') if isinstance(unit.get('details'),dict) else {}
    # v5/v7 may have harvested relations from a wrong first sense before the
    # source-aware override existed. Remove only sense-risky lexical relations;
    # keep source grammar/rection/variants if present.
    details.pop('synonyms',None);details.pop('antonyms',None)
    if details: unit['details']=details
    elif 'details' in unit: unit.pop('details',None)
    unit['connections']=[]
    prov=unit.setdefault('provenance',{});sources=prov.setdefault('sources',[])
    sid='de_wiktionary_vorstellen_sense_3b'
    if not any(isinstance(x,dict) and x.get('source_id')==sid for x in sources):
        sources.append({
          'source_id':sid,'source_kind':'lexicon',
          'what_was_verified':['definition','sense_alignment'],
          'verification_status':'verified',
          'locator':'https://de.wiktionary.org/wiki/vorstellen#Deutsch',
          'accessed_at':'2026-09-03',
          'evidence_note':'Source example introduces one person to another; bound explicitly to Wiktionary sense [3b], excluding spatial and reflexive-imagination senses.'
        })
    return True

def update_evidence(evidence,unit,candidates_used):
    residual=evidence.setdefault('residual_external_evidence',[])
    for c in candidates_used:
        key=(unit['id'],c['source_id'],c['text'])
        if any((x.get('id'),x.get('source_id'),x.get('text'))==key for x in residual if isinstance(x,dict)): continue
        residual.append({'id':unit['id'],'type':unit.get('type'),'source_id':c['source_id'],'source_kind':c.get('source_kind','website'),'locator':c['url'],'status':'success','text':c['text'],'accessed_at':'2026-09-03','sense_note':c.get('evidence_note','')})
    if unit.get('type')=='verb' and candidates_used:
        for a in evidence.get('external_evidence_attempts') or []:
            if isinstance(a,dict) and a.get('id')==unit['id']:
                srcs=a.setdefault('sources',[])
                for c in candidates_used:
                    if c['source_id'] not in srcs: srcs.append(c['source_id'])
                if a.get('status') in {None,'failed','no_evidence'}: a['status']='success'
                break

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dataset',required=True,type=Path)
    ap.add_argument('--evidence',required=True,type=Path)
    ap.add_argument('--residuals',required=True,type=Path)
    ap.add_argument('--generated-fallback',type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--evidence-output',required=True,type=Path)
    ap.add_argument('--report',required=True,type=Path)
    ns=ap.parse_args()
    ds=load(ns.dataset);ev=load(ns.evidence);cfg=load(ns.residuals);bad=generated_texts(ns.generated_fallback)
    units=ds.get('learning_units') or [];byid={u.get('id'):u for u in units if isinstance(u,dict)}
    report={'status':'PASS','tool':'apply_residual_external_examples_v1','dataset':'menschen-a2','removed_generated_examples':{},'added_external_examples':{},'sense_overrides':[],'below_minimum':[],'problems':[]}
    # First remove the now-prohibited v8 draft filler everywhere.
    for u in units:
        if not isinstance(u,dict): continue
        n=remove_generated(u,bad)
        if n: report['removed_generated_examples'][u['id']]=n
    for uid,spec in (cfg.get('items') or {}).items():
        u=byid.get(uid)
        if not u:
            report['problems'].append(f'missing unit {uid}');continue
        if u.get('headword')!=spec.get('expected_headword'):
            report['problems'].append(f"{uid} headword mismatch: {u.get('headword')!r} != {spec.get('expected_headword')!r}")
            continue
        if repair_vorstellen(u): report['sense_overrides'].append(uid)
        seen={norm(x.get('text')) for x in u.get('examples') or [] if isinstance(x,dict)}
        used=[]
        for cand in spec.get('candidates') or []:
            if len(u.get('examples') or [])>=MINIMUM: break
            text=str(cand.get('text') or '').strip();key=norm(text)
            if not text or key in seen: continue
            ex={'id':next_example_id(u),'lang':'de-DE','text':text,'order':len(u.get('examples') or [])+1,'translations':[]}
            u.setdefault('examples',[]).append(ex);seen.add(key);used.append(cand);add_provenance(u,cand)
        if used:
            report['added_external_examples'][uid]=[c['text'] for c in used];update_evidence(ev,u,used)
    # Normalize order and enforce hard bounds; do not invent content if evidence is insufficient.
    for u in units:
        if not isinstance(u,dict): continue
        for i,ex in enumerate(u.get('examples') or [],1):
            if isinstance(ex,dict): ex['order']=i
        if len(u.get('examples') or [])<MINIMUM: report['below_minimum'].append({'id':u.get('id'),'count':len(u.get('examples') or [])})
        if len(u.get('examples') or [])>MAXIMUM: report['problems'].append(f"{u.get('id')} exceeds maximum {MAXIMUM}")
        # Final safety: generated learner example provenance is forbidden.
        for src in (u.get('provenance') or {}).get('sources',[]):
            if isinstance(src,dict) and (src.get('source_id')==GENERATED_SOURCE_ID or str(src.get('locator') or '').startswith(GENERATED_LOCATOR_PREFIX)):
                report['problems'].append(f"{u.get('id')} retains generated learner-example provenance")
    if report['below_minimum'] or report['problems']: report['status']='FAIL'
    dump(ns.output,ds);dump(ns.evidence_output,ev);dump(ns.report,report)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
