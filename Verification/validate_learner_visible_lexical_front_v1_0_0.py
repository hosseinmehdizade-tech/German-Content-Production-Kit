#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path

PLACEHOLDER_RE=re.compile(r'(^|\\s)(?:etw\\.|jdn\\.|jdm\\.|jemanden|jemandem|jemand|etwas)(?=\\s|$)',re.I)
ARTICLE_SET={'der','die','das','ein','eine'}

def rows(path:Path):
    if path.suffix.lower()=='.json':
        v=json.loads(path.read_text(encoding='utf-8-sig'))
        return v.get('cards',[]) if isinstance(v,dict) else v
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\\t'))

def custom(row):
    v=row.get('customFields',row.get('custom_fields',{}))
    if isinstance(v,dict):return v
    if not v:return {}
    return json.loads(v)

def unit_and_type(row,cf):
    u=cf.get('canonical_unit') or cf.get('canonicalUnit') or {}
    typ=str(u.get('type') or cf.get('vnext_pos') or cf.get('entry_type') or row.get('category') or '').strip().lower()
    aliases={'nomen':'noun','substantiv':'noun','adjektiv':'adjective'}
    return u,aliases.get(typ,typ)

def field(cf,u,key,*alts):
    core=u.get('core') if isinstance(u,dict) and isinstance(u.get('core'),dict) else {}
    for k in (key,*alts):
        v=core.get(k)
        if v not in (None,''):return str(v).strip()
    morph=cf.get('vnext_morphology') if isinstance(cf.get('vnext_morphology'),dict) else {}
    for k in (key,*alts):
        v=morph.get(k)
        if v not in (None,''):return str(v).strip()
    for k in (key,*alts):
        v=cf.get(k)
        if v not in (None,''):return str(v).strip()
    return ''

def headword(row,cf,u):
    return str((u.get('headword') if isinstance(u,dict) else '') or cf.get('lemma') or cf.get('infinitiveDisplay') or '').strip()

def contains(front,value):
    return not value or value.casefold() in front.casefold()

def validate(rs):
    errors=[];checked={'noun':0,'verb':0,'adjective':0,'expression':0}
    for i,row in enumerate(rs,1):
        cid=str(row.get('id') or f'row:{i}'); front=str(row.get('front') or '').strip(); cf=custom(row);u,typ=unit_and_type(row,cf)
        if typ=='noun':
            checked['noun']+=1; lemma=headword(row,cf,u) or front; article=field(cf,u,'article') or str(cf.get('vnext_gender') or '').strip(); plural=field(cf,u,'plural')
            if article and article.lower() in ARTICLE_SET and not contains(front,article):errors.append({'id':cid,'error':'NOUN_ARTICLE_NOT_LEARNER_VISIBLE','article':article,'front':front})
            if lemma and not contains(front,lemma):errors.append({'id':cid,'error':'NOUN_LEMMA_NOT_LEARNER_VISIBLE','lemma':lemma,'front':front})
            if plural and not contains(front,plural):errors.append({'id':cid,'error':'NOUN_PLURAL_NOT_LEARNER_VISIBLE','plural':plural,'front':front})
        elif typ=='verb':
            checked['verb']+=1; lemma=headword(row,cf,u) or front
            if PLACEHOLDER_RE.search(lemma):errors.append({'id':cid,'error':'VERB_LEMMA_CONTAINS_ARGUMENT_PLACEHOLDER','lemma':lemma})
            if lemma and not contains(front,lemma):errors.append({'id':cid,'error':'VERB_LEMMA_NOT_LEARNER_VISIBLE','lemma':lemma,'front':front})
            for key,alts,label in [('present_3sg',('present',),'present'),('preterite',('preterite_3sg',),'preterite'),('perfect',(), 'perfect')]:
                v=field(cf,u,key,*alts)
                if v and not contains(front,v):errors.append({'id':cid,'error':'VERB_FORM_NOT_LEARNER_VISIBLE','slot':label,'value':v,'front':front})
        elif typ=='adjective':
            checked['adjective']+=1; lemma=headword(row,cf,u) or front
            if lemma and not contains(front,lemma):errors.append({'id':cid,'error':'ADJECTIVE_LEMMA_NOT_LEARNER_VISIBLE','lemma':lemma,'front':front})
            for key in ('comparative','superlative'):
                v=field(cf,u,key)
                if v and not contains(front,v):errors.append({'id':cid,'error':'ADJECTIVE_FORM_NOT_LEARNER_VISIBLE','slot':key,'value':v,'front':front})
        else: checked['expression']+=1
    return {'status':'PASS' if not errors else 'FAIL','cards':len(rs),'checked':checked,'errors':errors}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('projection');a=ap.parse_args();r=validate(rows(Path(a.projection)));print(json.dumps(r,ensure_ascii=False,indent=2));raise SystemExit(0 if r['status']=='PASS' else 1)
if __name__=='__main__':main()
