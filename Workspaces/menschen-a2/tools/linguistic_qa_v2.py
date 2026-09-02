#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,hashlib
from pathlib import Path
from collections import Counter

MARKER_RE=re.compile(r'^\s*\[\s*\d+(?:[a-z])?\s*\]\s*',re.I)
ALLOWED_SEP={'separable','inseparable','non_prefixed','variable'}
ALLOWED_AUX={'haben','sein','haben_or_sein','none'}
EXPECTED_RETIRED={177,203,266,286,292}
EXPECTED_GENERATED={'ma2-lu-0048','ma2-lu-0192','ma2-lu-0216','ma2-lu-0239','ma2-lu-0242'}

def issue(sev,code,uid,path,msg): return {'severity':sev,'code':code,'id':uid,'path':path,'message':msg}
def nonempty(v): return isinstance(v,str) and bool(v.strip())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('dataset',type=Path);ap.add_argument('--output',type=Path,required=True);ns=ap.parse_args()
    ds=json.loads(ns.dataset.read_text(encoding='utf-8'));issues=[];units=ds.get('learning_units') or []
    ids=[u.get('id') for u in units if isinstance(u,dict)];orders=[(u.get('metadata') or {}).get('unit_order') for u in units if isinstance(u,dict)]
    if len(units)!=292:issues.append(issue('error','UNIT_COUNT','dataset','learning_units',f'Expected 292 active units; found {len(units)}.'))
    if len(ids)!=len(set(ids)):issues.append(issue('error','DUPLICATE_ID','dataset','learning_units','Duplicate unit IDs.'))
    expected_orders=[i for i in range(1,298) if i not in EXPECTED_RETIRED]
    if orders!=expected_orders:issues.append(issue('error','SOURCE_ORDER_PARITY','dataset','metadata.unit_order','Active source-order sequence differs from Stage-2 decisions.'))
    types=Counter(u.get('type') for u in units if isinstance(u,dict))
    if types!=Counter({'verb':227,'phrase':65}):issues.append(issue('error','TYPE_COUNT','dataset','learning_units',f'Unexpected type counts: {dict(types)}'))
    generated=set();source_attested=0;first_fa_en=0;rich_units=0;extra_examples=0
    for i,u in enumerate(units):
        uid=str(u.get('id') or f'index-{i}')
        for field in ('headword','persian_meaning'):
            v=u.get(field)
            if not nonempty(v):issues.append(issue('error','FIELD_EMPTY',uid,field,f'{field} must be non-empty.'))
            elif '\t' in v or '\n' in v or '\r' in v:issues.append(issue('error','CONTROL_CHAR',uid,field,'Learner-facing field contains tab/newline.'))
            elif MARKER_RE.search(v):issues.append(issue('error','SOURCE_MARKER_LEAK',uid,field,'Source sense marker leaked into learner-facing text.'))
        typ=u.get('type');core=u.get('core') if isinstance(u.get('core'),dict) else {};details=u.get('details') if isinstance(u.get('details'),dict) else {}
        if typ=='verb':
            if not nonempty(u.get('definition_de')):issues.append(issue('error','VERB_DEFINITION_MISSING',uid,'definition_de','Rich verb card requires German definition.'))
            for f in ('present_3sg','preterite_3sg','perfect','auxiliary','reflexive','separability'):
                if f not in core or core.get(f) in (None,''):issues.append(issue('error','VERB_CORE_MISSING',uid,f'core.{f}','Required verb core field missing.'))
            if core.get('auxiliary') not in ALLOWED_AUX:issues.append(issue('error','AUXILIARY_ENUM',uid,'core.auxiliary',str(core.get('auxiliary'))))
            if not isinstance(core.get('reflexive'),bool):issues.append(issue('error','REFLEXIVE_TYPE',uid,'core.reflexive','reflexive must be boolean.'))
            if core.get('separability') not in ALLOWED_SEP:issues.append(issue('error','SEPARABILITY_ENUM',uid,'core.separability',str(core.get('separability'))))
        elif typ=='phrase':
            if not nonempty(core.get('structure')):issues.append(issue('error','PHRASE_STRUCTURE',uid,'core.structure','Phrase requires structure.'))
        else:issues.append(issue('error','TYPE_UNEXPECTED',uid,'type',str(typ)))
        for field in ('synonyms','antonyms','rection','grammar_notes','variants'):
            vals=details.get(field)
            if vals is not None:
                if not isinstance(vals,list) or not all(nonempty(x) for x in vals):issues.append(issue('error','ARRAY_SHAPE',uid,f'details.{field}','Must be array of non-empty strings.'))
                else:
                    if len(vals)!=len(dict.fromkeys(x.casefold() for x in vals)):issues.append(issue('error','ARRAY_DUPLICATE',uid,f'details.{field}','Multi-value learner field contains duplicates.'))
                    for j,x in enumerate(vals):
                        if MARKER_RE.search(x):issues.append(issue('error','SOURCE_MARKER_LEAK',uid,f'details.{field}[{j}]','Source marker leaked.'))
        conns=u.get('connections') or []
        if not isinstance(conns,list):issues.append(issue('error','CONNECTIONS_SHAPE',uid,'connections','connections must be an array.'));conns=[]
        for j,c in enumerate(conns):
            if not isinstance(c,dict) or not nonempty(c.get('text')):issues.append(issue('error','CONNECTION_INVALID',uid,f'connections[{j}]','Connection must be object with text.'))
            elif MARKER_RE.search(c['text']):issues.append(issue('error','SOURCE_MARKER_LEAK',uid,f'connections[{j}].text','Source marker leaked.'))
        exs=u.get('examples')
        if not isinstance(exs,list):issues.append(issue('error','EXAMPLES_SHAPE',uid,'examples','Examples must be an array.'));continue
        if len(exs)<4 or len(exs)>6:issues.append(issue('error','EXAMPLE_CARDINALITY',uid,'examples',f'Rich-card floor requires 4-6 German examples; found {len(exs)}.'))
        else:rich_units+=1
        seen_text=set();seen_ids=set()
        for j,ex in enumerate(exs):
            path=f'examples[{j}]'
            if not isinstance(ex,dict):issues.append(issue('error','EXAMPLE_OBJECT',uid,path,'Example must be an object.'));continue
            expected_id=f'{uid}-ex-{j+1:03d}'
            if ex.get('id')!=expected_id:issues.append(issue('error','EXAMPLE_ID',uid,path+'.id',f'Expected {expected_id}; found {ex.get("id")!r}.'))
            if ex.get('id') in seen_ids:issues.append(issue('error','EXAMPLE_ID_DUPLICATE',uid,path+'.id','Duplicate example ID.'))
            seen_ids.add(ex.get('id'))
            text=str(ex.get('text') or '').strip()
            if ex.get('lang')!='de-DE' or not text:issues.append(issue('error','EXAMPLE_DE',uid,path,'German example malformed.'))
            if '\t' in text or '\n' in text or '\r' in text:issues.append(issue('error','EXAMPLE_CONTROL_CHAR',uid,path+'.text','Example contains tab/newline.'))
            if MARKER_RE.search(text):issues.append(issue('error','SOURCE_MARKER_LEAK',uid,path+'.text','Source sense marker leaked into example.'))
            if text.casefold() in seen_text:issues.append(issue('error','EXAMPLE_DUPLICATE',uid,path+'.text','Duplicate German example text.'))
            seen_text.add(text.casefold())
            if 'Nach: Stadt, Land etc.' in text:issues.append(issue('error','USAGE_NOTE_AS_EXAMPLE',uid,path+'.text','Usage note must not be exposed as example.'))
            trs=ex.get('translations') if isinstance(ex.get('translations'),list) else []
            langs={t.get('lang'):t.get('text') for t in trs if isinstance(t,dict) and nonempty(t.get('text'))}
            if j==0:
                if not nonempty(langs.get('fa-IR')):issues.append(issue('error','PRIMARY_FA_MISSING',uid,path+'.translations','Primary source/generated example requires reviewed Persian translation.'))
                if not nonempty(langs.get('en-US')):issues.append(issue('error','PRIMARY_EN_MISSING',uid,path+'.translations','Primary source/generated example requires reviewed English translation.'))
                if nonempty(langs.get('fa-IR')) and nonempty(langs.get('en-US')):first_fa_en+=1
            for t in trs:
                if not isinstance(t,dict) or not nonempty(t.get('lang')) or not nonempty(t.get('text')):issues.append(issue('error','TRANSLATION_SHAPE',uid,path+'.translations','Translation entries require lang + text.'))
        srcs=(u.get('provenance') or {}).get('sources') or []
        if any(isinstance(s,dict) and s.get('source_id')=='assistant_pedagogical_example' for s in srcs):generated.add(uid)
        else:source_attested+=1
        if len(exs)>1:
            extra_examples+=len(exs)-1
            external_attestation=any(isinstance(s,dict) and s.get('verification_status')=='verified' and s.get('source_id') not in {'menschen_a2_user_screenshots','assistant_translation_review','assistant_pedagogical_example'} and 'example_attestation' in (s.get('what_was_verified') or []) for s in srcs)
            if not external_attestation:issues.append(issue('error','EXTRA_EXAMPLE_EVIDENCE_MISSING',uid,'provenance','Additional examples require explicit verified external example-attestation evidence.'))
    if generated!=EXPECTED_GENERATED:issues.append(issue('error','GENERATED_EXAMPLE_SET','dataset','provenance',f'Expected generated-example IDs {sorted(EXPECTED_GENERATED)}; found {sorted(generated)}.'))
    errors=sum(x['severity']=='error' for x in issues);warnings=sum(x['severity']=='warning' for x in issues)
    report={'validator':'menschen-a2-rich-card-linguistic-qa','validator_version':'2.0.0','status':'PASS' if not errors else 'FAIL','errors':errors,'warnings':warnings,'dataset_sha256':hashlib.sha256(ns.dataset.read_bytes()).hexdigest(),'metrics':{'units':len(units),'verbs':types.get('verb',0),'phrases':types.get('phrase',0),'rich_units_4_to_6_examples':rich_units,'source_attested_primary_examples':source_attested,'generated_primary_examples':len(generated),'primary_examples_with_fa_en':first_fa_en,'additional_external_examples':extra_examples,'collocations':sum(len([c for c in (u.get('connections') or []) if isinstance(c,dict) and c.get('kind')=='collocation']) for u in units)},'generated_example_ids':sorted(generated),'issues':issues}
    ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['status']=='PASS' else 1)
if __name__=='__main__':main()
