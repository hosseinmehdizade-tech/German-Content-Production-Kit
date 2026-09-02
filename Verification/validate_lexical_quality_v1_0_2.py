#!/usr/bin/env python3
from __future__ import annotations
import argparse,importlib.util,json,re
from pathlib import Path

HERE=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location('lexq101',HERE/'validate_lexical_quality_v1_0_1.py')
base=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(base)

def issue(code,uid,path,message):return {'severity':'error','code':code,'id':uid,'path':path,'message':message}
def nonempty(v):return isinstance(v,str) and bool(v.strip())

def validate_dataset(ds):
    report=base.validate_dataset(ds)
    # v1.0.0 assumed every German example must carry both FA and EN. Rich-card
    # production instead keeps the reviewed primary example bilingual and allows
    # additional externally attested German examples without invented translations.
    report['issues']=[x for x in report.get('issues',[]) if x.get('code')!='EXAMPLE_TRANSLATION_MISSING']
    for i,u in enumerate(ds.get('learning_units',[]) if isinstance(ds,dict) else []):
        if not isinstance(u,dict):continue
        uid=str(u.get('id') or f'index-{i}');exs=u.get('examples') if isinstance(u.get('examples'),list) else []
        if not exs:continue
        first=exs[0] if isinstance(exs[0],dict) else {};trs=first.get('translations') if isinstance(first.get('translations'),list) else []
        langs={t.get('lang') for t in trs if isinstance(t,dict) and nonempty(t.get('text'))}
        if not {'fa-IR','en-US'}.issubset(langs):
            report['issues'].append(issue('PRIMARY_EXAMPLE_TRANSLATION_MISSING',uid,'examples[0].translations','Primary curated example must retain reviewed FA and EN translations.'))
        if len(exs)>1:
            srcs=(u.get('provenance') or {}).get('sources') or []
            ok=any(isinstance(s,dict) and s.get('verification_status')=='verified' and s.get('source_id') not in {'assistant_pedagogical_example','assistant_translation_review'} and 'example_attestation' in (s.get('what_was_verified') or []) for s in srcs)
            if not ok:report['issues'].append(issue('ADDITIONAL_EXAMPLE_EVIDENCE_MISSING',uid,'provenance','Additional rich-card examples require verified external/source example-attestation evidence.'))
        seen=set()
        for j,e in enumerate(exs):
            if not isinstance(e,dict):continue
            text=str(e.get('text') or '').strip();key=text.casefold()
            if key in seen:report['issues'].append(issue('EXAMPLE_DUPLICATE',uid,f'examples[{j}].text','Duplicate example text.'))
            seen.add(key)
    report['validator_version']='1.0.2'
    report['errors']=sum(x.get('severity')=='error' for x in report.get('issues',[]));report['status']='FAIL' if report['errors'] else 'PASS'
    return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument('dataset');ap.add_argument('--tsv');ap.add_argument('--output');ns=ap.parse_args()
    ds=json.loads(Path(ns.dataset).read_text(encoding='utf-8'));quality=validate_dataset(ds);report={'quality':quality}
    if ns.tsv:report['transport']=base.validate_tsv(ns.tsv,ds)
    report['status']='PASS' if quality['status']=='PASS' and report.get('transport',{'status':'PASS'})['status']=='PASS' else 'FAIL'
    text=json.dumps(report,ensure_ascii=False,indent=2)+'\n';print(text,end='')
    if ns.output:Path(ns.output).write_text(text,encoding='utf-8')
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
