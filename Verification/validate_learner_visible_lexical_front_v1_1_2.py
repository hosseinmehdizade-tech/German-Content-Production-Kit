#!/usr/bin/env python3
"""HF2 v1.1.2: explicit canonical number and gender shapes.

The v1.1.0 pinned validator remains the baseline.  No card-ID allowlist,
no copying the learner front into the expected value, and no global promotion.
"""
import argparse,json,re
from pathlib import Path
import validate_learner_visible_lexical_front_v1_1_0 as base


def explicit_model(row):
    cf=base.custom(row); u,typ=base.unit_and_type(row,cf)
    core,m=base.core_of(cf,u)
    h=base.headword(row,cf,u)
    if typ=='noun':
        g=core.get('gendered_forms_source_verified')
        if isinstance(g,dict):
            vals=[base.norm(g.get(k)) for k in ('masculine_singular','masculine_plural','feminine_singular','feminine_plural')]
            if not (all(vals) and vals[0].startswith('der ') and vals[2].startswith('die ') and vals[1].startswith('die ') and vals[3].startswith('die ')):
                return 'INVALID_GENDERED_FORMS',None
            return 'GENDERED_EXPLICIT',f'{vals[0]}, {vals[1]}; {vals[2]}, {vals[3]}'
        sf=core.get('singular_forms')
        if isinstance(sf,list) and len(sf)==2 and all(isinstance(m.get(k),str) and ', ' in m[k] for k in ('masculine','feminine')):
            masc,fem=[base.norm(m[k]) for k in ('masculine','feminine')]
            pairs=[x.split(', ',1) for x in (masc,fem)]
            if any(len(x)!=2 or not x[1] for x in pairs) or [x[0] for x in pairs]!=sf or not sf[0].startswith('der ') or not sf[1].startswith('die '):
                return 'INVALID_GENDERED_FORMS',None
            return 'GENDERED_PAIRED',masc+' / '+fem
        if core.get('plural_only') is True or core.get('plural_only_display') is True or m.get('number') in ('plural_only','Pluralwort'):
            a=base.field(cf,u,'article')
            p=base.field(cf,u,'plural')
            if not h or (a not in ('die','die (Plural)') and not (not a and base.closure(core,m,'article') and base.closure(core,m,'plural') and (core.get('number')=='plural_only' or m.get('number')=='plural_only'))): return 'INVALID_PLURAL_ONLY',None
            if core.get('plural_only_display') is True and not base.article_bearing(m.get('singular')):
                return 'INVALID_PLURAL_SOURCE_SURFACE',None
            if p and p not in (h,'die '+h): return 'INVALID_PLURAL_SURFACE',None
            if not p and not (base.closure(core,m,'plural') or m.get('number') in ('plural_only','Pluralwort')):
                return 'INVALID_PLURAL_SURFACE',None
            # Preserve a reviewed plural-only label, derived from canonical evidence, not the front.
            surface='die '+h
            for source in (core,m,u):
                reviewed=base.norm(source.get('reviewed_form'))
                if reviewed in (surface+' (Plural)',surface+' (nur Plural)'):
                    surface=reviewed;break
            return 'PLURAL_SURFACE',surface
        if base.field(cf,u,'plural') in ('—','-','?') and base.closure(core,m,'plural'):
            model=base.noun_model(row,cf,u)
            if not model['forms']:return 'INVALID_CLOSED_PLURAL',None
            return 'CLOSED_NO_PLURAL',' / '.join(model['forms'])
    if typ=='adjective' and base.closure(core,m,'comparison') and isinstance(m.get('forms'),str):
        forms=[base.norm(x) for x in m['forms'].split(',')]
        if len(forms)>=3 and forms[0]==h+'-' and all(re.fullmatch(re.escape(h)+r'\w+',x) for x in forms[1:]):
            return 'EXPLICIT_INFLECTED_FORMS',' / '.join(forms[1:])
    return None,None


def validate(rows):
    old=base.validate(rows); models={}; extra=[]
    for r in rows:
        kind,expected=explicit_model(r)
        if kind is None:continue
        cid=r['id'];front=base.norm(r.get('front'))
        models[cid]=(kind,expected,front)
        if expected is None or expected!=front:
            extra.append({'id':cid,'error':'EXPLICIT_CANONICAL_FRONT_MISMATCH','shape':kind,'expected':expected,'front':front})
    errors=[];resolved=[]
    for e in old['errors']:
        model=models.get(e['id'])
        if model and model[1] is not None and model[1]==model[2] and e['error'] in ('NOUN_FRONT_NOT_CANONICAL_DISPLAY','ADJECTIVE_FRONT_NOT_CANONICAL_DISPLAY'):
            resolved.append(dict(e,shape=model[0],derived_expected=model[1]))
        else:errors.append(e)
    errors.extend(extra)
    return {'schema':'learner-visible-front-audit@1.1.2','status':'PASS' if not errors else 'FAIL','cards':len(rows),'checked':old['checked'],'legacy_status':old['status'],'legacy_error_count':len(old['errors']),'resolved_shape_mismatches':resolved,'explicit_model_count':len(models),'errors':errors,'central_policy_promotion':False}


def main():
    p=argparse.ArgumentParser();p.add_argument('projection');a=p.parse_args();v=validate(base.rows(Path(a.projection)));print(json.dumps(v,ensure_ascii=False,indent=2));raise SystemExit(0 if v['status']=='PASS' else 1)
if __name__=='__main__':main()
