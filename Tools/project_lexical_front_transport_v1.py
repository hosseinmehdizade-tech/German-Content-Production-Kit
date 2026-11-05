#!/usr/bin/env python3
"""Transport only: source-backed noun/verb/adjective morphology -> consumer type/core.

DO NOT change card IDs, original front, meanings, examples, other canonical fields or SRS.
Importing the output still needs real CURRENT app Stage6 and backup verification.
"""
import argparse,csv,hashlib,json,re
from pathlib import Path

TYPES={'Noun':'noun','Verb':'verb','Adjective':'adjective'}
ALIASES={'noun':{'article':['article','artikel'],'plural':['plural']},
         'verb':{'present_3sg':['present_3sg','present'],
                 'preterite':['preterite','past_3sg','preterite_3sg'],
                 'perfect':['perfect','perfect_3sg']},
         'adjective':{'comparative':['comparative'],'superlative':['superlative']}}

def valid(x):return isinstance(x,str) and x.strip() not in ('','—','-','?')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def front_facts(row,typ):
    p=[v.strip() for v in row['front'].split(',')]
    if typ=='verb' and len(p)==4 and p[-1].startswith(('hat ','ist ')):
        return dict(zip(('present_3sg','preterite','perfect'),p[1:]))
    if typ=='noun' and len(p)==2 and re.match(r'^(der|die|das)\s+',p[0],re.I):
        return {'article':p[0].split()[0],**({} if re.match(r'^(der|die|das)\s+',p[1],re.I) else {'plural':p[1]})}
    if typ=='adjective' and len(p)==3 and p[-1].startswith('am '):
        return dict(zip(('comparative','superlative'),p[1:]))
    return {}

def project(row):
    typ=TYPES.get(row.get('category'))
    if not typ:return row,False
    cf=json.loads(row['custom_fields']);u=cf.get('canonical_unit')
    if not isinstance(u,dict):return row,False
    oldtype=u.get('type')
    if oldtype not in (None,'','sense',typ):raise ValueError(f'Conflicting canonical type on {row["id"]}: {oldtype}')
    morph=u.get('morphology') if isinstance(u.get('morphology'),dict) else {}
    core=u.get('core') if isinstance(u.get('core'),dict) else {}
    additions={};front=front_facts(row,typ)
    for key,aliases in ALIASES[typ].items():
        if valid(core.get(key)):continue
        val=next((morph[k] for k in aliases if valid(morph.get(k))),None)
        if not valid(val):val=front.get(key)
        if not valid(val) or key=='article' and val not in ('der','die','das'):continue
        additions[key]=val.strip()
    if typ=='noun' and morph.get('article')=='der/die':
        h=str(u.get('headword') or '')
        if h.startswith('der/die ') and not core.get('singular_forms'):
            tail=h[len('der/die '):]
            additions['singular_forms']=['der '+tail,'die '+tail]
    if typ=='noun' and morph.get('article')=='die (Plural)' and morph.get('number')=='Pluralwort' and row['front'].startswith('die (Plural) '):
        if not core.get('article'):additions['article']='die'
        if not core.get('plural_only'):additions['plural_only']=True
    if oldtype==typ and not additions:return row,False
    if oldtype!=typ:u['type']=typ
    if additions:u.setdefault('core',{}).update(additions)
    result=dict(row)
    result['custom_fields']=json.dumps(cf,ensure_ascii=False,separators=(',',':'),sort_keys=True)
    return result,True

def main(src,dst,source_sha=None):
    if source_sha and sha(src)!=source_sha:raise SystemExit('SOURCE_SHA_NOT_PINNED')
    with open(src,encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f,delimiter='\t');fields=reader.fieldnames;rows=list(reader)
    out=[];count=0
    for r in rows:
        x,changed=project(r);out.append(x);count+=changed
        if any(r[k]!=x[k] for k in fields if k!='custom_fields'):raise RuntimeError('Protected columns changed')
    with open(dst,'w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(out)
    print(json.dumps({'status':'PROJECTION_ONLY_NOT_STAGE6','cards':len(out),'metadata_only_changed':count,'source_sha':sha(src),'output_sha':sha(dst)},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');p.add_argument('--source-sha');a=p.parse_args();main(a.source,a.output,a.source_sha)
