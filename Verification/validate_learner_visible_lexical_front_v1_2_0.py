#!/usr/bin/env python3
"""HF2 v1.2.0: additive, explicit, pinned governed-construction subtype.
Ordinary noun/verb/adjective/expression rules delegate unchanged to HF2 v1.1.0.
This is a CONTENT/PROJECTION contract test; not real-runtime Stage6 acceptance.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, re, sys
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

SUBTYPE='governed_verb_construction@1'
VERSION='hf2-governed-structure@1.2.0'
PATTERN=re.compile(r'^(.+?)\s+([a-zäöüß]+(?:/[a-zäöüß]+)?)\s*\+\s*([ADNG])$')
FORM_KEYS=('present_3sg','preterite','perfect')

def digest(b):return hashlib.sha256(b).hexdigest()
def norm(s):return ' '.join(str(s or '').split())
def parse(rows_bytes):return list(csv.DictReader(io.StringIO(rows_bytes.decode('utf-8-sig')),delimiter='\t'))
def load_legacy(path):
    spec=spec_from_file_location('hf2_legacy_1_1_0',str(path));mod=module_from_spec(spec);spec.loader.exec_module(mod);return mod

def validate(rows, registry, legacy):
    errors=[]; opted=[]; ordinary=[]; observed=set(); seen=set()
    source=registry.get('source_cards',{}); permitted=registry.get('approved_governed_ids',[])
    approved=set(permitted)
    if len(set(permitted))!=len(permitted):errors.append({'error':'REGISTRY_APPROVAL_DUPLICATES'})
    if registry.get('subtype')!=SUBTYPE:errors.append({'error':'REGISTRY_SUBTYPE_MISMATCH'})
    for position,row in enumerate(rows,1):
        cid=norm(row.get('id'))
        if not cid or cid in seen:errors.append({'id':cid,'error':'CARD_ID_EMPTY_OR_DUPLICATE'})
        seen.add(cid)
        try:cf=json.loads(row.get('custom_fields','{}'))
        except Exception:errors.append({'id':cid,'error':'CUSTOM_FIELDS_MALFORMED'});continue
        if not isinstance(cf,dict):errors.append({'id':cid,'error':'CUSTOM_FIELDS_NOT_OBJECT'});continue
        contract=cf.get('hf2_governed_construction_v1')
        if not contract:
            ordinary.append(row)
            if cid in approved:errors.append({'id':cid,'error':'APPROVED_CONSTRUCTION_SUBTYPE_MISSING'})
            continue
        opted.append(row);observed.add(cid)
        if cid not in approved:errors.append({'id':cid,'error':'UNAPPROVED_CONSTRUCTION_OPT_IN'});continue
        if not isinstance(contract,dict):errors.append({'id':cid,'error':'GOVERNED_CONTRACT_NOT_OBJECT'});continue
        reg=source.get(cid,{})
        if not reg or position!=reg.get('order'):errors.append({'id':cid,'error':'REGISTRY_ID_OR_ORDER_MISMATCH'})
        for field in ['front','typing_target','category','card_type','id']:
            if row.get(field)!=reg.get(field):errors.append({'id':cid,'error':'SOURCE_FIELD_MODIFIED','field':field})
        if row.get('category','').lower()!='verb' or row.get('card_type')!='de-vocabulary':errors.append({'id':cid,'error':'INVALID_CARD_FAMILY'})
        if cf.get('presentation_contract')!='gfp-vocabulary-neutral@1':errors.append({'id':cid,'error':'NEUTRAL_CONTRACT_NOT_PRESERVED'})
        front=norm(row.get('front'));match=PATTERN.fullmatch(front)
        if not match:errors.append({'id':cid,'error':'GOVERNED_PATTERN_MALFORMED','front':front});continue
        lemma,prep,case=match.groups()
        morphology=cf.get('vnext_morphology',{})
        if not isinstance(morphology,dict):morphology={}
        if any(not norm(morphology.get(k)) for k in FORM_KEYS):errors.append({'id':cid,'error':'PRINCIPAL_FORMS_MISSING'})
        display=front+' — '+', '.join([lemma]+[norm(morphology.get(k)) for k in FORM_KEYS])
        expected={'subtype':SUBTYPE,'lemma':lemma,'source_pattern':front,'preposition':prep,'case':case,
                  'typing_core':front,'generic_display':display,'study_display':display,'quick_display':display,
                  'present_3sg':norm(morphology.get('present_3sg')),'preterite':norm(morphology.get('preterite')),
                  'perfect':norm(morphology.get('perfect'))}
        for key,ref in expected.items():
            if contract.get(key)!=ref:errors.append({'id':cid,'error':'GOVERNED_CONTRACT_VALUE_MISMATCH','key':key})
        if cf.get('typingCore')!=front:errors.append({'id':cid,'error':'SOURCE_GOVERNED_TYPING_MODIFIED'})
        if cf.get('vnext_target_type')!=reg.get('vnext_target_type'):errors.append({'id':cid,'error':'SOURCE_TARGET_TYPE_MODIFIED'})
        if norm(cf.get('canonical_unit',{}).get('sense_qualifier'))!=front:errors.append({'id':cid,'error':'CANONICAL_SOURCE_PATTERN_LOST'})
        for key in FORM_KEYS:
            if norm(morphology.get(key))!=norm(reg.get('morphology',{}).get(key)):
                errors.append({'id':cid,'error':'PINNED_PRINCIPAL_FORM_CHANGED','key':key})
        if norm(lemma)!=norm(reg.get('lemma')):errors.append({'id':cid,'error':'PINNED_CLEAN_LEMMA_CHANGED'})
        if norm(cf.get('typingCore'))!=norm(reg.get('typingCore')):errors.append({'id':cid,'error':'PINNED_TYPING_CORE_CHANGED'})
        if contract.get('lemma','').startswith(('etw.','jdn.','jdm.')):errors.append({'id':cid,'error':'DIRTY_LEMMA'})
    if observed != approved:errors.append({'error':'APPROVED_COVERAGE_NOT_EXACT','missing':sorted(approved-observed),'extra':sorted(observed-approved)})
    if len(rows)!=len(source):errors.append({'error':'REGISTERED_CARD_COUNT_MISMATCH'})
    if set(seen)!=set(source):errors.append({'error':'CARD_ID_SET_CHANGED'})
    legacy_result=legacy.validate(ordinary)
    if legacy_result['status']!='PASS':
        errors.append({'error':'UNSCOPED_OFFICIAL_HF2_V1_1_0_FAILED','details':legacy_result['errors'][:30],'all_errors':len(legacy_result['errors'])})
    return {'schema':'hf2-front-audit@1.2.0','status':'PASS' if not errors else 'FAIL',
            'cards':len(rows),'approved_governed_cards':len(opted),'ordinary_cards':len(ordinary),
            'legacy_ordinary_status':legacy_result['status'],'errors':errors,
            'stage6_actual_app_acceptance':'NOT_EVALUATED'}

def main():
    p=argparse.ArgumentParser();p.add_argument('projection');p.add_argument('--registry',required=True);
    p.add_argument('--legacy',required=True);p.add_argument('--require-sha');a=p.parse_args()
    b=Path(a.projection).read_bytes()
    if a.require_sha and digest(b)!=a.require_sha:
        print(json.dumps({'status':'FAIL','error':'INPUT_SHA_MISMATCH'}));sys.exit(2)
    out=validate(parse(b),json.loads(Path(a.registry).read_text(encoding='utf-8')),load_legacy(a.legacy))
    print(json.dumps(out,ensure_ascii=False,indent=2));sys.exit(0 if out['status']=='PASS' else 1)
if __name__=='__main__':main()