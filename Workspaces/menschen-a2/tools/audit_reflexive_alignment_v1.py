#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path

REFL=re.compile(r'\b(?:sich|mich|dich|uns|euch)\b',re.I)

def reflexive_unit(u):
    return bool((u.get('core') or {}).get('reflexive')) or str(u.get('headword') or '').strip().casefold().startswith('sich ')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('dataset',type=Path);ap.add_argument('--output',type=Path,required=True);ns=ap.parse_args()
    ds=json.loads(ns.dataset.read_text(encoding='utf-8'));bad_examples=[];bad_collocations=[];ref_units=[]
    for u in ds.get('learning_units',[]):
        if not isinstance(u,dict) or not reflexive_unit(u):continue
        uid=u.get('id');ref_units.append(uid)
        for j,e in enumerate((u.get('examples') or [])[1:],start=1):
            if not isinstance(e,dict):continue
            text=str(e.get('text') or '').strip()
            if text and not REFL.search(text):bad_examples.append({'id':uid,'headword':u.get('headword'),'index':j,'example_id':e.get('id'),'text':text})
        ci=0
        for c in u.get('connections') or []:
            if not isinstance(c,dict) or c.get('kind')!='collocation':continue
            text=str(c.get('text') or '').strip()
            if text and not REFL.search(text):bad_collocations.append({'id':uid,'headword':u.get('headword'),'collocation_index':ci,'text':text})
            ci+=1
    report={'status':'FAIL' if bad_examples or bad_collocations else 'PASS','validator':'menschen-a2-reflexive-surface-audit','version':'1.0.0','reflexive_units':len(ref_units),'nonprimary_example_mismatches':len(bad_examples),'collocation_mismatches':len(bad_collocations),'example_issues':bad_examples,'collocation_issues':bad_collocations}
    ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
