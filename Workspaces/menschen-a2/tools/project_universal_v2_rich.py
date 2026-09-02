#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from copy import deepcopy
from pathlib import Path

HEADERS=['id','card_type','domain','category','source','level','lesson','deck','front','back','front_label','back_label','front_lang','back_lang','typing_target','examples','related','opposites','details','custom_fields','tags','notes','order']

def jd(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
def clean(v):return str(v or '').replace('\t',' ').replace('\r',' ').replace('\n',' ').strip()
def arr(d,k):return d.get(k) if isinstance(d,dict) and isinstance(d.get(k),list) else []

def details_projection(u):
    out=[];core=u.get('core') if isinstance(u.get('core'),dict) else {};d=u.get('details') if isinstance(u.get('details'),dict) else {}
    if u.get('type')=='verb':
        forms=[]
        for label,key in [('Präsens (3. Sg.)','present_3sg'),('Präteritum','preterite_3sg'),('Perfekt','perfect'),('Hilfsverb','auxiliary')]:
            if clean(core.get(key)):forms.append(f'{label}: {clean(core[key])}')
        if forms:out.append({'title':'Formen','items':forms})
    if arr(d,'rection'):out.append({'title':'Rektion','items':[clean(x) for x in arr(d,'rection') if clean(x)]})
    coll=[clean(c.get('text')) for c in u.get('connections',[]) if isinstance(c,dict) and c.get('kind')=='collocation' and clean(c.get('text'))]
    if coll:out.append({'title':'Kollokationen','items':coll})
    variants=[clean(x) for x in arr(d,'variants') if clean(x)]
    if variants:out.append({'title':'Varianten','items':variants})
    notes=[clean(x) for x in arr(d,'grammar_notes') if clean(x)]
    if notes:out.append({'title':'Grammatik','items':notes})
    other=[clean(c.get('text')) for c in u.get('connections',[]) if isinstance(c,dict) and c.get('kind') not in {'collocation'} and clean(c.get('text'))]
    if other:out.append({'title':'Verbindungen','items':other})
    return out

def examples_projection(u):
    exs=[x for x in u.get('examples',[]) if isinstance(x,dict) and clean(x.get('text'))]
    out=[]
    for i,e in enumerate(exs,1):
        out.append({'text':clean(e.get('text')),'lang':'de-DE','role':'example','label':e.get('id') or f"{u['id']}-ex-{i:03d}",'order':i})
    n=len(out)
    for e in exs:
        for t in e.get('translations',[]) if isinstance(e.get('translations'),list) else []:
            if isinstance(t,dict) and t.get('lang')=='en-US' and clean(t.get('text')):
                n+=1;out.append({'text':clean(t['text']),'lang':'en-US','role':'example','label':'translation:'+(e.get('id') or ''),'order':n})
                break
    return out

def custom_fields(u,profile_id):
    typ=u.get('type');core=u.get('core') if isinstance(u.get('core'),dict) else {};d=u.get('details') if isinstance(u.get('details'),dict) else {}
    cf={'entry_type':'verb' if typ=='verb' else 'phrase' if typ=='phrase' else typ,'canonical_entry_type':typ,'learning_unit_id':u['id'],'semantic_identity':u['id'],'german_learning_contract':'gfp-german-learning-content@1.0.0','semantic_contract':'gfp-german-language-content@3.1.3','source_profile_id':profile_id,'german_definition':clean(u.get('definition_de')),'english':'','direction_policy':'language-pair','canonical_unit':deepcopy(u)}
    if typ=='verb':
        sep=core.get('separability')
        cf.update({'present':clean(core.get('present_3sg')),'preterite':clean(core.get('preterite_3sg')),'perfect':clean(core.get('perfect')),'participle_ii':clean(core.get('participle_ii')),'auxiliary':clean(core.get('auxiliary')),'reflexive':bool(core.get('reflexive')),'is_reflexive':bool(core.get('reflexive')),'is_separable':sep=='separable','rection':' · '.join(clean(x) for x in arr(d,'rection') if clean(x))})
    cf.update({'typingCore':clean(u.get('headword')),'typingStandard':clean(u.get('headword')),'typingTargetLang':'de-DE','typingTargetDir':'ltr','typingTargetLabel':'Wort'})
    return cf

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--canonical',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ns=ap.parse_args()
    ds=json.loads(ns.canonical.read_text(encoding='utf-8'));units=ds.get('learning_units') or [];rows=[];profile_id=ds.get('profile_id','menschen-a2@2.1.0')
    for u in units:
        d=u.get('details') if isinstance(u.get('details'),dict) else {};tags=(u.get('metadata') or {}).get('tags') or []
        row={'id':u['id'],'card_type':'de-vocabulary','domain':'German','category':u.get('type',''),'source':'Menschen A2','level':'A2','lesson':'','deck':'','front':clean(u.get('headword')),'back':clean(u.get('persian_meaning')),'front_label':'Deutsch','back_label':'فارسی','front_lang':'de-DE','back_lang':'fa-IR','typing_target':'front-core','examples':jd(examples_projection(u)),'related':jd([clean(x) for x in arr(d,'synonyms') if clean(x)]),'opposites':jd([clean(x) for x in arr(d,'antonyms') if clean(x)]),'details':jd(details_projection(u)),'custom_fields':jd(custom_fields(u,profile_id)),'tags':'; '.join(clean(x) for x in tags if clean(x)),'notes':'','order':str((u.get('metadata') or {}).get('unit_order',''))}
        vals=[clean(row[h]) if h not in {'examples','related','opposites','details','custom_fields'} else row[h] for h in HEADERS]
        if any('\t' in v or '\n' in v or '\r' in v for v in vals):raise SystemExit(f'unsafe TSV cell in {u["id"]}')
        rows.append('\t'.join(vals))
    ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text('\ufeff'+'\t'.join(HEADERS)+'\n'+'\n'.join(rows)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','rows':len(rows),'output':str(ns.output)},ensure_ascii=False))
if __name__=='__main__':main()
