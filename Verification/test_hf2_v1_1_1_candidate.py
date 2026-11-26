#!/usr/bin/env python3
"""Regression checks against real A2 projection, no mutation of source files."""
import argparse,copy,json
from pathlib import Path
import validate_learner_visible_lexical_front_v1_1_1 as candidate
import validate_learner_visible_lexical_front_v1_1_0 as base

def run(path):
    rows=base.rows(Path(path)); good=candidate.validate(rows); assert good['status']=='PASS',good['errors']
    results=[]; byid={r['id']:r for r in rows}
    def negative(r,front,label):
        m=copy.deepcopy(r);m['front']=front
        assert candidate.validate([m])['status']=='FAIL',label
        results.append({'id':r['id'],'mutation':label,'status':'REJECTED'})
    for e in good['resolved_shape_mismatches']:
        r=byid[e['id']]; negative(r,e['expected'],'legacy_incorrect_expected')
        if e['shape'].startswith('GENDERED'):
            negative(r,r['front'].split(';')[0].split(' / ')[0],'missing_feminine_and_plural')
            negative(r,r['front'].replace('die ', 'das ',1),'wrong_article')
        elif e['shape']=='PLURAL_SURFACE':
            negative(r,r['front'].removeprefix('die '),'missing_plural_article')
        elif e['shape']=='EXPLICIT_INFLECTED_FORMS':
            negative(r,r['front'].split(' / ')[0],'missing_reviewed_inflected_forms')
    # Retain base validator rejection of ordinary missing forms and verb placeholders.
    n=next(r for r in rows if base.unit_and_type(r,base.custom(r))[1]=='noun' and candidate.explicit_model(r)[0] is None and ', ' in r['front'])
    negative(n,n['front'].split(', ')[0],'ordinary_missing_plural')
    v=next(r for r in rows if base.unit_and_type(r,base.custom(r))[1]=='verb')
    negative(v,v['front'].split(', ')[0],'ordinary_missing_verb_forms_on_front')
    return {'status':'PASS','source_cards':len(rows),'original_legacy_mismatches':good['legacy_error_count'],'resolved_shape_mismatches':len(good['resolved_shape_mismatches']),'negative_controls':len(results),'results':results,'central_policy_promotion':False}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('projection');print(json.dumps(run(a.parse_args().projection),ensure_ascii=False,indent=2))
