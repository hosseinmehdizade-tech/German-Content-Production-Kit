#!/usr/bin/env python3
"""Fail-closed lexical front transport gate; no morphology generation, no runtime mutation.

Checks consumer-readable canonical_unit.type/core against already source-attested
canonical_unit.pos/morphology for supported noun/verb/adjective vocabulary rows.
This is an independent Stage5 preflight, never Stage6/browser proof.
"""
import csv,json,sys
from pathlib import Path

TYPES={'Noun':'noun','Verb':'verb','Adjective':'adjective'}
FIELDS={'noun':{'article':('article','artikel'),'plural':('plural',)},
        'verb':{'present_3sg':('present_3sg','present'),
                'preterite':('preterite','past_3sg','preterite_3sg'),
                'perfect':('perfect','perfect_3sg')},
        'adjective':{'comparative':('comparative',),'superlative':('superlative',)}}

def usable(value):
    return isinstance(value,str) and value.strip() not in ('','—','-','?')

def validate(path):
    errors=[];checked=0;source_attested=0
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,delimiter='\t'):
            typ=TYPES.get(r.get('category',''))
            if not typ:continue
            cf=json.loads(r.get('custom_fields','{}'));u=cf.get('canonical_unit')
            if not isinstance(u,dict):continue
            morph=u.get('morphology') if isinstance(u.get('morphology'),dict) else {}
            core=u.get('core') if isinstance(u.get('core'),dict) else {}
            accepted={}
            for key,aliases in FIELDS[typ].items():
                for a in aliases:
                    value=morph.get(a)
                    if usable(value):accepted[key]=value.strip();break
            # No false failure for a source whose morphological facts were never established.
            if not accepted and not (r['category']=='Noun' and r['front'].startswith(('der ','die ','das '))):continue
            checked+=1;id_=r.get('id','?')
            if u.get('type')!=typ:errors.append({'id':id_,'error':'CONSUMER_POS_UNBOUND','expected':typ,'actual':u.get('type')})
            for key,expected in accepted.items():
                source_attested+=1
                actual=core.get(key)
                if key=='article' and expected=='der/die' and u.get('headword','').startswith('der/die '):
                    stem=u['headword'][len('der/die '):]
                    if core.get('singular_forms')!=['der '+stem,'die '+stem]:
                        errors.append({'id':id_,'error':'COMPOUND_GENDER_FORMS_NOT_BOUND'})
                elif key=='article' and expected=='die (Plural)' and morph.get('number')=='Pluralwort':
                    if actual!='die' or core.get('plural_only') is not True:
                        errors.append({'id':id_,'error':'PLURAL_ONLY_NOUN_NOT_BOUND'})
                elif actual!=expected:errors.append({'id':id_,'error':'SOURCE_MORPH_NOT_ON_CONSUMER_FRONT','field':key,'expected':expected,'actual':actual})
    return {'schema':'gcpk-front-transport-gate@1','status':'PASS' if not errors else 'FAIL',
            'checked_source_attested_cards':checked,'source_attested_form_fields':source_attested,
            'issues':len(errors),'samples':errors[:20],'Stage6_real_browser':'NOT_RUN'}

if __name__=='__main__':
    v=validate(sys.argv[1]);print(json.dumps(v,ensure_ascii=False,indent=2));sys.exit(0 if v['status']=='PASS' else 1)
