#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from collections import Counter
from pathlib import Path

ABSENT=(None,"",[],{})
FIXED_CASE_PREPS={'aus','außer','bei','mit','nach','seit','von','zu','gegenüber','durch','für','gegen','ohne','um'}

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def issue(severity,code,path,message): return {'severity':severity,'code':code,'path':path,'message':message}

def get_path(unit,path):
    cur=unit
    for part in path.split('.'):
        if not isinstance(cur,dict): return None
        cur=cur.get(part)
    return cur

def detail_count(unit,spec):
    if spec=='connections.collocation':
        return sum(1 for x in unit.get('connections',[]) if isinstance(x,dict) and x.get('kind')=='collocation' and str(x.get('text','')).strip())
    v=get_path(unit,spec)
    if isinstance(v,list): return len([x for x in v if (isinstance(x,str) and x.strip()) or isinstance(x,dict)])
    return 1 if v not in ABSENT else 0

def translation_count(examples,lang):
    n=0
    for ex in examples:
        if any(isinstance(t,dict) and t.get('lang')==lang and str(t.get('text','')).strip() for t in ex.get('translations',[])):
            n+=1
    return n

def explicit_rection_required(unit):
    text=' '.join(str(x or '') for x in [unit.get('headword'),(unit.get('core') or {}).get('structure')])
    low=text.casefold()
    if re.search(r'\[(?:\+)?[ad]\]|\((?:dat|akk)\.?\)|\b(?:jdn|jmdn|jdm|jmdm)\.?\b',low): return True
    return any(re.search(rf'\b{re.escape(p)}\b',low) for p in FIXED_CASE_PREPS)

def validate(dataset,floor,evidence):
    units=dataset.get('learning_units') if isinstance(dataset,dict) else None
    if not isinstance(units,list): raise ValueError('dataset.learning_units must be an array')
    issues=[]; type_counts=Counter(); with_detail=Counter()
    attempts={}
    for a in evidence.get('external_evidence_attempts',[]) if isinstance(evidence,dict) else []:
        if isinstance(a,dict) and a.get('id'): attempts[a['id']]=a
    for i,u in enumerate(units):
        if not isinstance(u,dict):
            issues.append(issue('error','PRODUCT_UNIT_INVALID',f'learning_units[{i}]','Unit is not an object.')); continue
        typ=u.get('type'); type_counts[typ]+=1; rule=(floor.get('by_type') or {}).get(typ)
        if not rule: continue
        root=f"learning_units[{i}]({u.get('id','?')})"
        for f in rule.get('required_unit_fields',[]):
            if u.get(f) in ABSENT: issues.append(issue('error','PRODUCT_REQUIRED_UNIT_FIELD',f'{root}.{f}','Required rich-card learner field is absent.'))
        core=u.get('core') if isinstance(u.get('core'),dict) else {}
        for f in rule.get('required_core_fields',[]):
            if core.get(f) in ABSENT: issues.append(issue('error','PRODUCT_REQUIRED_CORE_FIELD',f'{root}.core.{f}','Required rich-card core field is absent.'))
        exs=[x for x in u.get('examples',[]) if isinstance(x,dict) and str(x.get('text','')).strip()]
        er=rule.get('examples') or {}; mn=int(er.get('minimum',0)); mx=er.get('maximum')
        if len(exs)<mn: issues.append(issue('error','PRODUCT_EXAMPLE_MINIMUM',f'{root}.examples',f'Need at least {mn} usable German examples; found {len(exs)}.'))
        if mx is not None and len(exs)>int(mx): issues.append(issue('warning','PRODUCT_EXAMPLE_MAXIMUM',f'{root}.examples',f'Preferred maximum is {mx}; found {len(exs)}.'))
        for lang in er.get('required_translation_languages',[]):
            for j,ex in enumerate(exs):
                if not any(isinstance(t,dict) and t.get('lang')==lang and str(t.get('text','')).strip() for t in ex.get('translations',[])):
                    issues.append(issue('error','PRODUCT_EXAMPLE_TRANSLATION_MISSING',f'{root}.examples[{j}].translations',f'Missing required {lang} translation.'))
        for lang,minimum in (er.get('minimum_translated_examples') or {}).items():
            found=translation_count(exs,lang)
            if found<int(minimum):
                issues.append(issue('error','PRODUCT_TRANSLATED_EXAMPLE_MINIMUM',f'{root}.examples',f'Need at least {minimum} example(s) with a {lang} translation; found {found}.'))
        cr=rule.get('conditional_rection') or {}
        if cr.get('when_structure_has_explicit_case_or_fixed_case_preposition') and explicit_rection_required(u):
            found=detail_count(u,'details.rection')
            minimum=int(cr.get('minimum',1))
            if found<minimum:
                issues.append(issue('error','PRODUCT_EXPLICIT_RECTION_MISSING',f'{root}.details.rection',f'Explicit learner-facing government/case notation requires at least {minimum} Rektion item; found {found}.'))
        ldr=rule.get('lexical_detail_coverage') or {}
        if ldr:
            total=sum(detail_count(u,p) for p in ldr.get('count_fields',[]))
            if total>0: with_detail[typ]+=1
    eg=floor.get('evidence_gate') or {}
    eligible=set(eg.get('eligible_types',[]))
    for i,u in enumerate(units):
        if isinstance(u,dict) and u.get('type') in eligible:
            uid=u.get('id'); a=attempts.get(uid)
            if not a:
                issues.append(issue('error','PRODUCT_EXTERNAL_EVIDENCE_ATTEMPT_MISSING',f'learning_units[{i}]({uid}).provenance','No external lexical-evidence attempt is recorded for this eligible unit.'))
            elif a.get('status') not in {'success','no_evidence','failed'}:
                issues.append(issue('error','PRODUCT_EXTERNAL_EVIDENCE_ATTEMPT_INVALID',f'evidence.external_evidence_attempts[{uid}]','Attempt status must be success, no_evidence, or failed.'))
    verbs=type_counts.get('verb',0)
    if verbs and floor.get('policy',{}).get('zero_external_lexical_enrichment_is_a_hard_failure_for_nonempty_verb_datasets'):
        success=sum(1 for a in attempts.values() if a.get('type')=='verb' and a.get('status')=='success')
        if success==0: issues.append(issue('error','PRODUCT_ZERO_EXTERNAL_ENRICHMENT','evidence','Non-empty verb dataset has zero successful external lexical enrichment.'))
    for typ,rule in (floor.get('by_type') or {}).items():
        ldr=rule.get('lexical_detail_coverage') or {}
        if ldr and type_counts.get(typ):
            frac=with_detail.get(typ,0)/type_counts[typ]
            minimum=float(ldr.get('minimum_dataset_fraction_with_any_detail',0))
            if frac<minimum:
                issues.append(issue('error','PRODUCT_LEXICAL_DETAIL_SYSTEM_HEALTH',f'coverage.{typ}',f'Only {with_detail.get(typ,0)}/{type_counts[typ]} ({frac:.1%}) units have any evidence-backed lexical detail; systemic floor is {minimum:.0%}. This indicates a broken/disabled enrichment path, not permission to fabricate content.'))
    errors=sum(x['severity']=='error' for x in issues); warnings=sum(x['severity']=='warning' for x in issues)
    return {'validator':'gfp-rich-card-product-floor','validator_version':'1.0.0','product_floor_id':floor.get('profile_id'),'status':'FAIL' if errors else 'PASS','errors':errors,'warnings':warnings,'coverage':{'type_counts':dict(type_counts),'with_any_lexical_detail':dict(with_detail),'external_attempts':len(attempts)},'issues':issues}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('dataset'); ap.add_argument('floor'); ap.add_argument('evidence'); ap.add_argument('--output'); a=ap.parse_args()
    try: r=validate(load(a.dataset),load(a.floor),load(a.evidence))
    except Exception as e:
        print(json.dumps({'status':'CONFIGURATION_ERROR','error':str(e)},ensure_ascii=False,indent=2)); return 2
    text=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if a.output: Path(a.output).write_text(text,encoding='utf-8')
    print(text,end=''); return 1 if r['status']=='FAIL' else 0
if __name__=='__main__': raise SystemExit(main())
