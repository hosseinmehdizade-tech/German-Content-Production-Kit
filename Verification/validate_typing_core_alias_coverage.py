#!/usr/bin/env python3
"""Read-only QA: acceptedAnswers overrides may not exclude the authoritative typingCore."""
from __future__ import annotations
import argparse,csv,json,re,sys
from pathlib import Path
def norm(v): return re.sub(r'\s+',' ',str(v or '')).strip()
def validate(rows):
    errors=[];overrides=0;covered=0
    for n,row in enumerate(rows,1):
        cid=row.get('id') or f'row:{n}'
        cf=row.get('custom_fields',row.get('customFields',{}))
        try:
            if isinstance(cf,str):cf=json.loads(cf)
            if not isinstance(cf,dict):raise ValueError('not an object')
        except (TypeError,ValueError) as e:
            errors.append({'id':cid,'code':'INVALID_CUSTOM_FIELDS','detail':str(e)})
            continue
        keys=[k for k in ('acceptedAnswersFull','acceptedAnswersStandard') if k in cf and cf[k] is not None]
        if not keys:continue
        overrides+=1;core=norm(cf.get('typingCore'))
        if not core:
            errors.append({'id':cid,'code':'TYPING_CORE_MISSING'})
            continue
        valid=True
        for key in keys:
            aliases=cf[key]
            if not isinstance(aliases,list) or not aliases or any(not isinstance(a,str) or not norm(a) for a in aliases):
                errors.append({'id':cid,'code':'INVALID_ACCEPTED_ANSWERS','field':key});valid=False
            elif core not in {norm(a) for a in aliases}:
                errors.append({'id':cid,'code':'TYPING_CORE_EXCLUDED','field':key,'typingCore':core});valid=False
        if valid:covered+=1
    return {'schema':'typing-core-accepted-answer-coverage@1.0.0','status':'PASS' if not errors else 'FAIL',
            'cards':len(rows),'override_cards':overrides,'covered_override_cards':covered,
            'error_count':len(errors),'error_ids':sorted({e['id'] for e in errors}),'errors':errors}
def main():
    p=argparse.ArgumentParser();p.add_argument('tsv');a=p.parse_args()
    with Path(a.tsv).open(encoding='utf-8-sig',newline='') as f:r=list(csv.DictReader(f,delimiter='\t'))
    report=validate(r);print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
