#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path


def load(p:Path): return json.loads(p.read_text(encoding='utf-8'))
def norm(s): return ' '.join(str(s or '').split()).strip()
def h(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--spec',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);ns=ap.parse_args()
    ds=load(ns.input);spec=load(ns.spec);units=ds.get('learning_units') or [];byid={u.get('id'):u for u in units if isinstance(u,dict)}
    before=h(ns.input);removed=[];inserted=[]
    for uid,texts in (spec.get('remove_exact') or {}).items():
        u=byid.get(uid)
        if not u: raise SystemExit('missing remove unit '+uid)
        rm={norm(x).casefold() for x in texts};kept=[]
        for ex in u.get('examples') or []:
            if isinstance(ex,dict) and norm(ex.get('text')).casefold() in rm:
                removed.append({'id':uid,'example_id':ex.get('id'),'text':norm(ex.get('text'))});continue
            kept.append(ex)
        u['examples']=kept
    for uid,item in (spec.get('items') or {}).items():
        u=byid.get(uid)
        if not u: raise SystemExit('missing patch unit '+uid)
        if norm(u.get('headword'))!=norm(item.get('headword')): raise SystemExit(f'headword mismatch {uid}: {u.get("headword")}')
        exs=u.setdefault('examples',[]);existing={norm(x.get('text')).casefold() for x in exs if isinstance(x,dict)}
        for e in item.get('examples') or []:
            if len(exs)>=4: break
            text=norm(e.get('text'))
            if not text or text.casefold() in existing: continue
            exs.append({'id':'TEMP','lang':'de-DE','text':text,'order':0,'translations':[]});existing.add(text.casefold())
            inserted.append({'id':uid,'text':text,'source_id':e['source_id'],'locator':e['locator']})
            srcs=u.setdefault('provenance',{}).setdefault('sources',[])
            rec={'source_id':e['source_id'],'source_kind':e.get('source_kind','website'),'what_was_verified':['example_attestation'],'verification_status':'verified','locator':e['locator'],'accessed_at':spec.get('accessed_at','2026-09-03'),'evidence_note':'Targeted Stage 4 semantic repair using an externally attested example after removal of a generated or sense-mismatched learner example. No full-source refetch and no generated learner content.'}
            if not any(isinstance(s,dict) and s.get('source_id')==rec['source_id'] and s.get('locator')==rec['locator'] for s in srcs): srcs.append(rec)
        u['examples']=exs
    for u in units:
        for i,ex in enumerate(u.get('examples') or [],1):
            if isinstance(ex,dict): ex['id']=f"{u.get('id')}-ex-{i:03d}";ex['order']=i
    below=[{'id':u.get('id'),'headword':u.get('headword'),'examples':len(u.get('examples') or [])} for u in units if len(u.get('examples') or [])<4]
    over=[{'id':u.get('id'),'headword':u.get('headword'),'examples':len(u.get('examples') or [])} for u in units if len(u.get('examples') or [])>6]
    generated=[]
    for u in units:
        for s in ((u.get('provenance') or {}).get('sources') or []):
            if isinstance(s,dict) and s.get('source_id')=='assistant_pedagogical_example': generated.append(u.get('id'));break
    ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(ds,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report={'status':'PASS' if not (below or over or generated) else 'FAIL','repair':'menschen-a2-stage4-attested-residual-v2','input_sha256':before,'output_sha256':h(ns.output),'network_full_refetch':False,'generated_content_added':False,'removed_exact':removed,'inserted_attested':inserted,'below4':below,'over6':over,'generated_provenance_remaining':sorted(set(generated))}
    ns.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['status']=='PASS' else 2)

if __name__=='__main__':main()
