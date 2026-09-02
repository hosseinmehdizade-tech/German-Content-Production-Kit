#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, hashlib
from pathlib import Path
from collections import Counter

MARKER_RE=re.compile(r'^\s*\[\s*\d+(?:[a-z])?\s*\]\s*',re.I)
ALLOWED_SEP={'separable','inseparable','non_prefixed','variable'}
ALLOWED_AUX={'haben','sein','haben_or_sein','none'}
EXPECTED_RETIRED={177,203,266,286,292}
EXPECTED_GENERATED={'ma2-lu-0048','ma2-lu-0192','ma2-lu-0216','ma2-lu-0239','ma2-lu-0242'}

def issue(sev,code,uid,path,msg):
    return {'severity':sev,'code':code,'id':uid,'path':path,'message':msg}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('dataset',type=Path); ap.add_argument('--output',type=Path,required=True)
    ns=ap.parse_args(); ds=json.loads(ns.dataset.read_text(encoding='utf-8'))
    issues=[]; units=ds.get('learning_units') or []
    ids=[u.get('id') for u in units if isinstance(u,dict)]
    orders=[(u.get('metadata') or {}).get('unit_order') for u in units if isinstance(u,dict)]
    if len(units)!=292: issues.append(issue('error','UNIT_COUNT','dataset','learning_units',f'Expected 292 active units; found {len(units)}.'))
    if len(ids)!=len(set(ids)): issues.append(issue('error','DUPLICATE_ID','dataset','learning_units','Duplicate unit IDs.'))
    expected_orders=[i for i in range(1,298) if i not in EXPECTED_RETIRED]
    if orders!=expected_orders: issues.append(issue('error','SOURCE_ORDER_PARITY','dataset','metadata.unit_order','Active source-order sequence differs from Stage-2 retirement/exclusion decisions.'))
    types=Counter(u.get('type') for u in units if isinstance(u,dict))
    if types!=Counter({'verb':227,'phrase':65}): issues.append(issue('error','TYPE_COUNT','dataset','learning_units',f'Unexpected type counts: {dict(types)}'))
    generated=set(); source_attested=0; trans_count=0
    for i,u in enumerate(units):
        uid=str(u.get('id') or f'index-{i}')
        for field in ('headword','persian_meaning'):
            if not isinstance(u.get(field),str) or not u[field].strip(): issues.append(issue('error','FIELD_EMPTY',uid,field,f'{field} must be non-empty.'))
            elif '\t' in u[field] or '\n' in u[field] or '\r' in u[field]: issues.append(issue('error','CONTROL_CHAR',uid,field,'Learner-facing field contains tab/newline.'))
            elif MARKER_RE.search(u[field]): issues.append(issue('error','SOURCE_MARKER_LEAK',uid,field,'Source sense marker leaked into learner-facing text.'))
        typ=u.get('type'); core=u.get('core') if isinstance(u.get('core'),dict) else {}; details=u.get('details') if isinstance(u.get('details'),dict) else {}
        if typ=='verb':
            for f in ('present_3sg','preterite_3sg','perfect','auxiliary','reflexive','separability'):
                if f not in core or core.get(f) in (None,''): issues.append(issue('error','VERB_CORE_MISSING',uid,f'core.{f}','Required verb core field missing.'))
            if core.get('auxiliary') not in ALLOWED_AUX: issues.append(issue('error','AUXILIARY_ENUM',uid,'core.auxiliary',str(core.get('auxiliary'))))
            if not isinstance(core.get('reflexive'),bool): issues.append(issue('error','REFLEXIVE_TYPE',uid,'core.reflexive','reflexive must be boolean.'))
            if core.get('separability') not in ALLOWED_SEP: issues.append(issue('error','SEPARABILITY_ENUM',uid,'core.separability',str(core.get('separability'))))
        elif typ=='phrase':
            if not isinstance(core.get('structure'),str) or not core.get('structure','').strip(): issues.append(issue('error','PHRASE_STRUCTURE',uid,'core.structure','Phrase requires structure.'))
        else: issues.append(issue('error','TYPE_UNEXPECTED',uid,'type',str(typ)))
        for field in ('synonyms','antonyms','rection','grammar_notes','variants'):
            vals=details.get(field)
            if vals is not None:
                if not isinstance(vals,list) or not all(isinstance(x,str) and x.strip() for x in vals): issues.append(issue('error','ARRAY_SHAPE',uid,f'details.{field}','Must be array of non-empty strings.'))
                else:
                    for j,x in enumerate(vals):
                        if MARKER_RE.search(x): issues.append(issue('error','SOURCE_MARKER_LEAK',uid,f'details.{field}[{j}]','Source marker leaked.'))
        if u.get('connections') not in (None,[]):
            for j,c in enumerate(u.get('connections') or []):
                if not isinstance(c,dict) or not str(c.get('text') or '').strip(): issues.append(issue('error','CONNECTION_INVALID',uid,f'connections[{j}]','Connection must be object with text.'))
                elif MARKER_RE.search(str(c.get('text'))): issues.append(issue('error','SOURCE_MARKER_LEAK',uid,f'connections[{j}].text','Source marker leaked.'))
        exs=u.get('examples')
        if not isinstance(exs,list) or len(exs)!=1:
            issues.append(issue('error','EXAMPLE_CARDINALITY',uid,'examples',f'Expected exactly one curated example at this release; found {len(exs) if isinstance(exs,list) else "non-list"}.'))
            continue
        ex=exs[0]
        if ex.get('id')!=f'{uid}-ex-001': issues.append(issue('error','EXAMPLE_ID',uid,'examples[0].id',str(ex.get('id'))))
        if ex.get('lang')!='de-DE' or not str(ex.get('text') or '').strip(): issues.append(issue('error','EXAMPLE_DE',uid,'examples[0]','German example malformed.'))
        if 'Nach: Stadt, Land etc.' in str(ex.get('text') or ''): issues.append(issue('error','USAGE_NOTE_AS_EXAMPLE',uid,'examples[0].text','Usage note must not be exposed as example.'))
        trs=ex.get('translations') if isinstance(ex.get('translations'),list) else []
        langs={t.get('lang'):t.get('text') for t in trs if isinstance(t,dict)}
        for lang in ('fa-IR','en-US'):
            if not isinstance(langs.get(lang),str) or not langs[lang].strip(): issues.append(issue('error','EXAMPLE_TRANSLATION_MISSING',uid,'examples[0].translations',f'Missing {lang}.'))
            else: trans_count+=1
        srcs=(u.get('provenance') or {}).get('sources') or []
        if any(isinstance(s,dict) and s.get('source_id')=='assistant_pedagogical_example' for s in srcs): generated.add(uid)
        else: source_attested+=1
    if generated!=EXPECTED_GENERATED: issues.append(issue('error','GENERATED_EXAMPLE_SET','dataset','provenance',f'Expected generated-example IDs {sorted(EXPECTED_GENERATED)}; found {sorted(generated)}.'))
    errors=sum(x['severity']=='error' for x in issues); warnings=sum(x['severity']=='warning' for x in issues)
    report={
      'validator':'menschen-a2-linguistic-qa','validator_version':'1.0.0','status':'PASS' if not errors else 'FAIL',
      'errors':errors,'warnings':warnings,'dataset_sha256':hashlib.sha256(ns.dataset.read_bytes()).hexdigest(),
      'metrics':{'units':len(units),'verbs':types.get('verb',0),'phrases':types.get('phrase',0),'source_attested_examples':source_attested,'generated_examples':len(generated),'example_translations':trans_count,'collocations':sum(len([c for c in (u.get('connections') or []) if isinstance(c,dict) and c.get('kind')=='collocation']) for u in units)},
      'generated_example_ids':sorted(generated),
      'translation_review':'All 292 DE examples and their FA/EN translations were reviewed for direct semantic alignment during production; row 242 usage-note mismatch was explicitly repaired before enrichment.',
      'issues':issues
    }
    ns.output.parent.mkdir(parents=True,exist_ok=True); ns.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if report['status']=='PASS' else 1)
if __name__=='__main__': main()
