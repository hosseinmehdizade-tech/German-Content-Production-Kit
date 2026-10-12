#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path
ARTICLES=('der','die','das')
GENDER_ARTICLE={'masculine':'der','maskulin':'der','m':'der','feminine':'die','feminin':'die','f':'die','neuter':'das','neutral':'das','neutrum':'das','n':'das'}
CLOSURES={'NOT_APPLICABLE','CLOSED_NO_FORCE'}
PLACEHOLDER_RE=re.compile(r'(?<!\w)(?:etw\.|jdn\.|jdm\.|jemanden|jemandem|jemand|etwas)(?!\w)',re.I)
CASE_RE=re.compile(r'(?<!\w)(?:akk\.?|akkusativ|dat\.?|dativ|gen\.?|genitiv|nom\.?|nominativ)(?!\w)',re.I)

def norm(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def rows(path:Path):
    if path.suffix.lower()=='.json':
        v=json.loads(path.read_text(encoding='utf-8-sig'))
        return v.get('cards',[]) if isinstance(v,dict) else v
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def custom(row):
    v=row.get('customFields',row.get('custom_fields',{}))
    if isinstance(v,dict):return v
    return json.loads(v) if v else {}
def unit_and_type(row,cf):
    u=cf.get('canonical_unit') or cf.get('canonicalUnit') or {}
    typ=norm(u.get('type') or cf.get('vnext_pos') or cf.get('entry_type') or row.get('category')).lower()
    aliases={'nomen':'noun','substantiv':'noun','adjektiv':'adjective'}
    return u,aliases.get(typ,typ)
def core_of(cf,u):
    core=u.get('core') if isinstance(u,dict) and isinstance(u.get('core'),dict) else {}
    morph=cf.get('vnext_morphology') if isinstance(cf.get('vnext_morphology'),dict) else {}
    return core,morph
def field(cf,u,key,*alts):
    core,morph=core_of(cf,u)
    for src in (core,morph,cf):
        for k in (key,*alts):
            v=src.get(k) if isinstance(src,dict) else None
            if v not in (None,''):return norm(v)
    return ''
def headword(row,cf,u):
    return norm((u.get('headword') if isinstance(u,dict) else '') or cf.get('lemma') or cf.get('infinitiveDisplay'))
def article_bearing(s):
    s=norm(s); return any(s.casefold().startswith(a+' ') for a in ARTICLES)
def unique(seq):
    out=[]; seen=set()
    for x in seq:
        x=norm(x)
        if x and x.casefold() not in seen: seen.add(x.casefold()); out.append(x)
    return out
def closure(core,morph,key):
    for src in (core,morph):
        v=norm(src.get(key+'_status') if isinstance(src,dict) else '').upper()
        if v in CLOSURES:return v
    return ''
def noun_model(row,cf,u):
    core,morph=core_of(cf,u); head=headword(row,cf,u); forms=[]
    for src in (core,morph):
        vals=src.get('singular_forms') if isinstance(src,dict) else None
        if isinstance(vals,list): forms += [v for v in vals if article_bearing(v)]
        pf=src.get('person_forms') if isinstance(src,dict) else None
        if isinstance(pf,dict) and isinstance(pf.get('singular_forms'),list): forms += [v for v in pf['singular_forms'] if article_bearing(v)]
        tf=src.get('thing_forms') if isinstance(src,dict) else None
        if isinstance(tf,dict):
            if isinstance(tf.get('forms'),list): forms += [v for v in tf['forms'] if article_bearing(v)]
            if tf.get('article') and head: forms.append(f"{norm(tf['article'])} {head}")
    if not forms:
        article=field(cf,u,'article') or norm(cf.get('vnext_gender'))
        article=GENDER_ARTICLE.get(article.casefold(),article)
        if article in ARTICLES and head: forms=[f'{article} {head}']
    forms=unique(forms); plurals=[]
    for src in (core,morph):
        if not isinstance(src,dict):continue
        if src.get('plural'): plurals.append(src['plural'])
        pf=src.get('person_forms')
        if isinstance(pf,dict) and pf.get('plural'): plurals.append(pf['plural'])
        tf=src.get('thing_forms')
        if isinstance(tf,dict) and tf.get('plural'): plurals.append(tf['plural'])
    plurals=unique(plurals)
    return {'forms':forms,'plurals':plurals,'article_closure':closure(core,morph,'article'),'plural_closure':closure(core,morph,'plural')}
def noun_expected(row,cf,u):
    m=noun_model(row,cf,u)
    if not m['forms']:return '',m
    out=' / '.join(m['forms'])
    if m['plurals']:out += ', ' + ' / '.join(m['plurals'])
    return out,m
def adjective_expected(row,cf,u):
    h=headword(row,cf,u); vals=[h] if h else []
    for k in ('comparative','superlative'):
        v=field(cf,u,k)
        if v: vals.append(v)
    return ', '.join(vals)
def verb_expected(row,cf,u):
    h=headword(row,cf,u); vals=[h] if h else []
    for key,alts in [('present_3sg',('present',)),('preterite',('preterite_3sg',)),('perfect',())]:
        v=field(cf,u,key,*alts)
        if v: vals.append(v)
    return ', '.join(vals)
def validate(rs):
    errors=[]; checked={'noun':0,'verb':0,'adjective':0,'expression':0,'other':0}
    for i,row in enumerate(rs,1):
        cid=norm(row.get('id') or f'row:{i}'); front=norm(row.get('front')); cf=custom(row);u,typ=unit_and_type(row,cf)
        if typ=='noun':
            checked['noun']+=1; exp,m=noun_expected(row,cf,u)
            if not m['forms'] and not m['article_closure']: errors.append({'id':cid,'error':'NOUN_ARTICLE_METADATA_MISSING','front':front})
            if not m['plurals'] and not m['plural_closure']: errors.append({'id':cid,'error':'NOUN_PLURAL_METADATA_MISSING','front':front})
            if exp and front!=exp: errors.append({'id':cid,'error':'NOUN_FRONT_NOT_CANONICAL_DISPLAY','expected':exp,'front':front})
        elif typ=='verb':
            checked['verb']+=1; h=headword(row,cf,u); exp=verb_expected(row,cf,u)
            if PLACEHOLDER_RE.search(h) or CASE_RE.search(h): errors.append({'id':cid,'error':'VERB_LEMMA_CONTAINS_ARGUMENT_PLACEHOLDER','lemma':h})
            missing=[]
            for key,alts in [('present_3sg',('present',)),('preterite',('preterite_3sg',)),('perfect',())]:
                if not field(cf,u,key,*alts): missing.append(key)
            if missing: errors.append({'id':cid,'error':'VERB_PRINCIPAL_FORMS_MISSING','slots':missing})
            if exp and front!=exp: errors.append({'id':cid,'error':'VERB_FRONT_NOT_CANONICAL_DISPLAY','expected':exp,'front':front})
        elif typ=='adjective':
            checked['adjective']+=1; exp=adjective_expected(row,cf,u)
            if exp and front!=exp: errors.append({'id':cid,'error':'ADJECTIVE_FRONT_NOT_CANONICAL_DISPLAY','expected':exp,'front':front})
        elif typ=='expression': checked['expression']+=1
        else: checked['other']+=1
    return {'schema':'learner-visible-front-audit@1.1.0','status':'PASS' if not errors else 'FAIL','cards':len(rs),'checked':checked,'errors':errors}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('projection');a=ap.parse_args();r=validate(rows(Path(a.projection)));print(json.dumps(r,ensure_ascii=False,indent=2));raise SystemExit(0 if r['status']=='PASS' else 1)
if __name__=='__main__':main()
