#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,sys
from collections import Counter
from pathlib import Path

HEADER=['id','card_type','domain','category','source','level','lesson','deck','front','back','front_label','back_label','front_lang','back_lang','typing_target','examples','related','opposites','details','custom_fields','tags','notes','order']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    out=Path(sys.argv[1]); canp=out/'MENSCHEN-A1-CANONICAL-CONTENT-VALIDATED.json'; tsvp=out/'MENSCHEN-A1-UNIVERSAL-v2.tsv'; gatep=out/'PRODUCT-CONTENT-COMPLETENESS.json'
    data=json.loads(canp.read_text(encoding='utf-8')); gate=json.loads(gatep.read_text(encoding='utf-8')); units=data.get('learning_units',[])
    errs=[]; warns=[]; ids=[u.get('id') for u in units]; types=Counter(u.get('type') for u in units)
    if len(units)!=276: errs.append(f'unit count {len(units)} != 276')
    if len(set(ids))!=len(ids): errs.append('duplicate canonical ids')
    if types.get('verb')!=275 or types.get('redemittel')!=1: errs.append(f'type coverage {dict(types)}')
    if gate.get('status')!='PASS' or gate.get('errors')!=0: errs.append(f'product completeness not PASS: {gate.get("status")}, errors={gate.get("errors")}')
    missing=[]
    for u in units:
        if u.get('type')=='verb':
            n=sum(1 for c in u.get('connections',[]) if isinstance(c,dict) and c.get('kind')=='collocation' and str(c.get('text','')).strip())
            if n<3: missing.append((u.get('id'),n))
    if missing: errs.append(f'verbs below 3 collocations: {missing[:20]}')
    # Input-policy check: source identifiers/locators must not reference forbidden historical enrichment mechanisms.
    banned=[]
    for u in units:
        for s in (u.get('provenance') or {}).get('sources',[]):
            ident=(str(s.get('source_id',''))+' '+str(s.get('locator',''))).casefold()
            if any(x in ident for x in ['angereichert','legacy-nvv','legacy_enrichment','legacy-enrichment','old-mapping']): banned.append((u.get('id'),s.get('source_id'),s.get('locator')))
    if banned: errs.append(f'forbidden legacy provenance references: {banned[:20]}')
    full={'validator':'current-only-final-structural','status':'PASS' if not errs else 'FAIL','errors':len(errs),'warnings':len(warns),'learning_units':len(units),'coverage_by_type':dict(types),'unique_ids':len(set(ids)),'verbs_with_3plus_collocations':275-len(missing),'product_content_complete':gate.get('status'),'legacy_enrichment_inputs_detected':bool(banned),'canonical_sha256':sha(canp),'issues':errs,'notes':warns}
    write(out/'FULL-GATE-VALIDATION.json',full)

    derr=[]
    with tsvp.open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
    actual=list(rows[0].keys()) if rows else []
    if actual!=HEADER: derr.append(f'header mismatch: {actual}')
    if len(rows)!=276: derr.append(f'row count {len(rows)} != 276')
    if [r.get('id') for r in rows]!=ids: derr.append('canonical/TSV id or order parity mismatch')
    deep=0; expar=0
    for r,u in zip(rows,units):
        try: cf=json.loads(r['custom_fields']); ex=json.loads(r['examples'])
        except Exception as e: derr.append(f'{r.get("id")}: JSON parse error {e}'); continue
        if cf.get('canonical_unit')!=u: derr.append(f'{u.get("id")}: canonical_unit deep parity mismatch')
        else: deep+=1
        de=[x.get('text') for x in ex if x.get('lang')=='de-DE']; en=[x.get('text') for x in ex if x.get('lang')=='en-US']
        ude=[x.get('text') for x in u.get('examples',[])]; uen=[]
        for x in u.get('examples',[]):
            tr=next((t.get('text') for t in x.get('translations',[]) if t.get('lang')=='en-US'),None); uen.append(tr)
        if de!=ude or en!=uen: derr.append(f'{u.get("id")}: example projection parity mismatch')
        else: expar+=1
    delivery={'validator':'current-only-final-delivery','status':'PASS' if not derr else 'FAIL','errors':len(derr),'rows':len(rows),'columns':len(actual),'header_exact':actual==HEADER,'id_order_parity':not any('id or order' in x for x in derr),'deep_canonical_parity_rows':deep,'example_parity_rows':expar,'canonical_sha256':sha(canp),'tsv_sha256':sha(tsvp),'issues':derr[:100]}
    write(out/'DELIVERY-VALIDATION.json',delivery)
    print(json.dumps({'full':full,'delivery':delivery},ensure_ascii=False,indent=2))
    return 0 if full['status']=='PASS' and delivery['status']=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
