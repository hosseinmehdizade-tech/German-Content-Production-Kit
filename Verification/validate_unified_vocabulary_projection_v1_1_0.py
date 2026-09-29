#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path

NEUTRAL='de-vocabulary'
NEUTRAL_SCHEMA_PROFILE='german-v411-lexical'
NEUTRAL_PRESENTATION_CONTRACT='gfp-vocabulary-neutral@1'

def load_rows(path:Path):
    if path.suffix.lower()=='.json':
        data=json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data,dict) and isinstance(data.get('cards'),list): data=data['cards']
        if not isinstance(data,list): raise ValueError('JSON projection must be a card list or {cards:[...]} object')
        return data
    if path.suffix.lower() in {'.tsv','.txt'}:
        with path.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f,delimiter='\t'))
    raise ValueError('supported projection formats: JSON or TSV')

def parse_custom(row):
    raw=row.get('customFields',row.get('custom_fields',{}))
    if raw is None or raw=='': return {},None
    if isinstance(raw,dict): return raw,None
    if isinstance(raw,str):
        try: value=json.loads(raw)
        except Exception as exc: return {},f'INVALID_CUSTOM_FIELDS_JSON: {exc}'
        if isinstance(value,dict): return value,None
        return {},'CUSTOM_FIELDS_NOT_OBJECT'
    return {},'CUSTOM_FIELDS_NOT_OBJECT'

def card_type(row): return str(row.get('cardType') or row.get('card_type') or '').strip().lower()
def norm_key(key): return re.sub(r'[^a-z0-9]+','',str(key).lower())

SAFE_PRESENTATION_KEYS={'presentationcontract','presentationexamples','sourceschemaprofile'}
EXACT_SELECTOR_KEYS={
    'cardtype','schemaprofile','presentationprofile','presentationtype','presentationid','presentationname',
    'presentationselector','presentationmode','presentationfamily','presentationvariant','presentationstyle',
    'layoutprofile','layouttype','layoutid','layoutname','layoutselector','layoutmode','layoutfamily','layoutvariant','layoutstyle',
    'templateprofile','templatetype','templateid','templatename','templateselector','templatemode','templatefamily','templatevariant','templatestyle',
    'rendererprofile','renderertype','rendererid','renderername','rendererselector','renderermode','rendererfamily','renderervariant','rendererstyle',
    'renderprofile','rendertype','renderid','rendername','renderselector','rendermode','renderfamily','rendervariant','renderstyle',
    'viewprofile','viewtype','viewid','viewname','viewselector','viewmode','viewfamily','viewvariant','viewstyle',
    'cardlayout','cardtemplate','cardprofile','cardpresentation','visualprofile','visualtemplate','visualtype'
}
SELECTOR_STEMS=('layout','template','renderer')

def is_presentation_selector_key(key):
    n=norm_key(key)
    if n in SAFE_PRESENTATION_KEYS: return False
    if n in EXACT_SELECTOR_KEYS: return True
    if any(stem in n for stem in SELECTOR_STEMS): return True
    if 'presentation' in n and n not in SAFE_PRESENTATION_KEYS: return True
    if 'schemaprofile' in n and n!='sourceschemaprofile': return True
    return False

def collect_selector_violations(value,path='custom'):
    found=[]
    if isinstance(value,dict):
        for key,child in value.items():
            nk=norm_key(key); child_path=f'{path}.{key}'
            if nk=='presentationcontract':
                contract=str(child or '').strip()
                if contract!=NEUTRAL_PRESENTATION_CONTRACT:
                    found.append({'selector':child_path,'value':contract,'reason':'INVALID_PRESENTATION_CONTRACT'})
            elif is_presentation_selector_key(key):
                found.append({'selector':child_path,'value':child if isinstance(child,(str,int,float,bool)) or child is None else '<structured>','reason':'NESTED_PRESENTATION_SELECTOR_FORBIDDEN'})
            if isinstance(child,(dict,list)): found.extend(collect_selector_violations(child,child_path))
    elif isinstance(value,list):
        for i,child in enumerate(value):
            if isinstance(child,(dict,list)): found.extend(collect_selector_violations(child,f'{path}[{i}]'))
    return found

def top_level_selector_violations(row):
    found=[]
    for key,value in row.items():
        nk=norm_key(key)
        if nk in {'cardtype','customfields','schemaprofile'}: continue
        if is_presentation_selector_key(key):
            found.append({'selector':f'top.{key}','value':value if isinstance(value,(str,int,float,bool)) or value is None else '<structured>','reason':'TOP_LEVEL_PRESENTATION_SELECTOR_FORBIDDEN'})
    profile=str(row.get('schemaProfile',row.get('schema_profile','')) or '').strip().lower()
    if profile and profile!=NEUTRAL_SCHEMA_PROFILE:
        found.append({'selector':'top.schemaProfile','value':profile,'reason':'NON_NEUTRAL_SCHEMA_PROFILE'})
    return found

def validate(rows):
    errors=[];legacy=[];missing=[];selector_conflicts=[]
    for i,row in enumerate(rows,start=1):
        cid=str(row.get('id') or f'row:{i}'); ct=card_type(row)
        if not ct: missing.append(cid);errors.append({'id':cid,'error':'MISSING_CARD_TYPE'})
        elif ct!=NEUTRAL:
            legacy.append({'id':cid,'card_type':ct});errors.append({'id':cid,'error':'NON_NEUTRAL_VOCABULARY_ENVELOPE','card_type':ct,'expected':NEUTRAL})
        if not str(row.get('category') or '').strip(): errors.append({'id':cid,'error':'MISSING_SEMANTIC_CATEGORY'})
        custom,custom_error=parse_custom(row)
        if custom_error: errors.append({'id':cid,'error':custom_error})
        contract=str(custom.get('presentation_contract') or '').strip() if isinstance(custom,dict) else ''
        if contract!=NEUTRAL_PRESENTATION_CONTRACT:
            errors.append({'id':cid,'error':'MISSING_OR_INVALID_PRESENTATION_CONTRACT','expected':NEUTRAL_PRESENTATION_CONTRACT,'actual':contract})
        conflicts=top_level_selector_violations(row)+collect_selector_violations(custom)
        if conflicts:
            selector_conflicts.append({'id':cid,'conflicts':conflicts});errors.append({'id':cid,'error':'PRESENTATION_SELECTOR_CONFLICT','conflicts':conflicts})
    return {'status':'PASS' if not errors else 'FAIL','cards':len(rows),'neutral_card_type':NEUTRAL,'neutral_schema_profile':NEUTRAL_SCHEMA_PROFILE,'presentation_contract':NEUTRAL_PRESENTATION_CONTRACT,'semantic_morphology_policy':'ALLOWED_AND_PRESENTATION_NEUTRAL','selector_scan':'TOP_LEVEL_PLUS_RECURSIVE_CUSTOM_FIELDS_CASE_INSENSITIVE','legacy_or_non_neutral':legacy,'missing_card_type':missing,'presentation_selector_conflicts':selector_conflicts,'errors':errors}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('projection');a=ap.parse_args();path=Path(a.projection)
    result=validate(load_rows(path));result['input']=str(path);print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
