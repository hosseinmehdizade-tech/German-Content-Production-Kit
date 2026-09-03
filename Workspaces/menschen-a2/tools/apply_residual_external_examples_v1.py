#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path

GENERATED_SOURCE_ID='assistant_pedagogical_example'
TRANSLATION_REVIEW_SOURCE_ID='assistant_translation_review'
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

def generated_sources(unit):
    out=[]
    for src in (unit.get('provenance') or {}).get('sources',[]) if isinstance(unit,dict) else []:
        if not isinstance(src,dict): continue
        if src.get('source_id')==GENERATED_SOURCE_ID or str(src.get('locator') or '').startswith(GENERATED_LOCATOR_PREFIX): out.append(src)
    return out

def strip_generated_provenance(unit,*,also_translation_review=False):
    prov=unit.get('provenance') if isinstance(unit.get('provenance'),dict) else {'sources':[]}
    kept=[]
    for src in prov.get('sources') or []:
        if not isinstance(src,dict): continue
        sid=str(src.get('source_id') or '');loc=str(src.get('locator') or '')
        if sid==GENERATED_SOURCE_ID or loc.startswith(GENERATED_LOCATOR_PREFIX): continue
        if also_translation_review and sid==TRANSLATION_REVIEW_SOURCE_ID: continue
        kept.append(src)
    prov['sources']=kept;unit['provenance']=prov

def remove_generated(unit,bad_texts,*,replace_primary=False):
    exs=list(unit.get('examples') or []);had_generated=bool(generated_sources(unit));removed=[]
    # Five explicitly configured Stage-3 units were born without a usable
    # source example. The pipeline inserted a generated primary example and
    # recorded assistant_pedagogical_example provenance. Only those named units
    # may remove position 0 by provenance; never infer this globally.
    if replace_primary and had_generated and exs:
        removed.append(exs.pop(0))
    kept=[]
    for ex in exs:
        if isinstance(ex,dict) and norm(ex.get('text')) in bad_texts:
            removed.append(ex);continue
        kept.append(ex)
    unit['examples']=kept
    if removed and had_generated:
        # The old translation-review record belonged to the removed generated
        # primary only in the explicit replacement case. Residual v8 filler has
        # no reviewed translation and must not delete a valid source-primary
        # translation record.
        strip_generated_provenance(unit,also_translation_review=replace_primary)
    return removed,had_generated

def add_provenance(unit,cand):
    prov=unit.setdefault('provenance',{});sources=prov.setdefault('sources',[])
    sid=cand['source_id'];url=cand['url']
    if not any(isinstance(x,dict) and x.get('source_id')==sid and x.get('locator')==url for x in sources):
        sources.append({
          'source_id':sid,
          'source_kind':cand.get('source_kind','website'),
          'what_was_verified':['example_attestation','sense_alignment'],
          'verification_status':cand.get('verification_status','verified'),
          'locator':url,
          'accessed_at':'2026-09-03',
          'evidence_note':cand.get('evidence_note','Externally attested residual example used after source/corpus enrichment remained below the product floor.')
        })
    translations=[t for t in cand.get('translations',[]) if isinstance(t,dict) and str(t.get('text') or '').strip()]
    if translations and not any(isinstance(x,dict) and x.get('source_id')==TRANSLATION_REVIEW_SOURCE_ID for x in sources):
        sources.append({
          'source_id':TRANSLATION_REVIEW_SOURCE_ID,
          'source_kind':'other',
          'what_was_verified':['english_example_translation'],
          'verification_status':'verified',
          'accessed_at':'2026-09-03',
          'evidence_note':'English translation for the externally attested replacement example was production-reviewed for sense alignment; the German example itself remains externally attested.'
        })

def repair_vorstellen(unit):
    if unit.get('id')!='ma2-lu-0187': return False
    unit['definition_de']='jemanden einem anderen, der ihn nicht kennt, bekannt machen'
    details=unit.get('details') if isinstance(unit.get('details'),dict) else {}
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

def merged_specs(residual_cfg,primary_cfg):
    a=dict(residual_cfg.get('items') or {});b=dict(primary_cfg.get('items') or {}) if primary_cfg else {}
    dup=set(a)&set(b)
    if dup: raise ValueError('duplicate unit IDs across residual and primary replacement configs: '+','.join(sorted(dup)))
    a.update(b);return a

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dataset',required=True,type=Path)
    ap.add_argument('--evidence',required=True,type=Path)
    ap.add_argument('--residuals',required=True,type=Path)
    ap.add_argument('--primary-replacements',type=Path)
    ap.add_argument('--generated-fallback',type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--evidence-output',required=True,type=Path)
    ap.add_argument('--report',required=True,type=Path)
    ns=ap.parse_args()
    ds=load(ns.dataset);ev=load(ns.evidence);rcfg=load(ns.residuals);pcfg=load(ns.primary_replacements) if ns.primary_replacements else None
    specs=merged_specs(rcfg,pcfg);bad=generated_texts(ns.generated_fallback);primary_ids={uid for uid,s in (pcfg.get('items') or {}).items() if s.get('replace_generated_primary')} if pcfg else set()
    units=ds.get('learning_units') or [];byid={u.get('id'):u for u in units if isinstance(u,dict)}
    report={'status':'PASS','tool':'apply_residual_external_examples_v1','tool_version':'1.1.0','dataset':'menschen-a2','removed_generated_examples':{},'replaced_generated_primary':[],'added_external_examples':{},'sense_overrides':[],'below_minimum':[],'problems':[]}

    # Remove only known generated content: exact v8 residual texts and the five
    # explicitly configured generated-primary units. Unknown generated content
    # is deliberately left visible and becomes a hard failure below.
    for u in units:
        if not isinstance(u,dict): continue
        removed,had_generated=remove_generated(u,bad,replace_primary=u.get('id') in primary_ids)
        if removed:
            report['removed_generated_examples'][u['id']]=[str(x.get('text') or '') for x in removed if isinstance(x,dict)]
            if u.get('id') in primary_ids: report['replaced_generated_primary'].append(u['id'])
        elif u.get('id') in primary_ids and had_generated:
            report['problems'].append(f"{u.get('id')} was configured for generated-primary replacement but no example was removed")

    for uid,spec in specs.items():
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
            translations=[{'lang':str(t['lang']),'text':str(t['text'])} for t in cand.get('translations',[]) if isinstance(t,dict) and t.get('lang') and str(t.get('text') or '').strip()]
            ex={'id':next_example_id(u),'lang':'de-DE','text':text,'order':len(u.get('examples') or [])+1,'translations':translations}
            u.setdefault('examples',[]).append(ex);seen.add(key);used.append(cand);add_provenance(u,cand)
        if used:
            report['added_external_examples'][uid]=[c['text'] for c in used];update_evidence(ev,u,used)

    for u in units:
        if not isinstance(u,dict): continue
        for i,ex in enumerate(u.get('examples') or [],1):
            if isinstance(ex,dict): ex['order']=i
        if len(u.get('examples') or [])<MINIMUM: report['below_minimum'].append({'id':u.get('id'),'count':len(u.get('examples') or [])})
        if len(u.get('examples') or [])>MAXIMUM: report['problems'].append(f"{u.get('id')} exceeds maximum {MAXIMUM}")
        if generated_sources(u): report['problems'].append(f"{u.get('id')} retains generated learner-example provenance")
        if any(isinstance(ex,dict) and norm(ex.get('text')) in bad for ex in u.get('examples') or []): report['problems'].append(f"{u.get('id')} retains a known v8 generated fallback example")
    for uid in primary_ids:
        if uid not in report['replaced_generated_primary'] and generated_sources(byid.get(uid,{})):
            report['problems'].append(f'{uid} generated primary was not durably replaced')
    if report['below_minimum'] or report['problems']: report['status']='FAIL'
    dump(ns.output,ds);dump(ns.evidence_output,ev);dump(ns.report,report)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
