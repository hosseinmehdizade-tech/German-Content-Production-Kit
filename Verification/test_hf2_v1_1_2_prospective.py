#!/usr/bin/env python3
"""Prospective HF2 regression tests; never write source artifacts."""
import argparse,copy,json
from pathlib import Path
import validate_learner_visible_lexical_front_v1_1_2 as candidate
import validate_learner_visible_lexical_front_v1_1_0 as base

def run(a2,b1):
    rows=base.rows(Path(a2)); good=candidate.validate(rows)
    assert good['status']=='PASS',good['errors']
    byid={r['id']:r for r in rows}; count=0
    def negative(r,front):
        nonlocal count
        m=copy.deepcopy(r);m['front']=front
        assert candidate.validate([m])['status']=='FAIL',(r['id'],front)
        count+=1
    for e in good['resolved_shape_mismatches']:
        r=byid[e['id']];negative(r,e['expected'])
        if e['shape'].startswith('GENDERED'):
            negative(r,r['front'].split(';')[0].split(' / ')[0])
            negative(r,r['front'].replace('die ','das ',1))
        elif e['shape']=='PLURAL_SURFACE':
            negative(r,r['front'].removeprefix('die '))
        elif e['shape']=='EXPLICIT_INFLECTED_FORMS':
            negative(r,r['front'].split(' / ')[0])
    n=next(r for r in rows if base.unit_and_type(r,base.custom(r))[1]=='noun' and candidate.explicit_model(r)[0] is None and ', ' in r['front'])
    negative(n,n['front'].split(', ')[0])
    v=next(r for r in rows if base.unit_and_type(r,base.custom(r))[1]=='verb')
    negative(v,v['front'].split(', ')[0])
    assert count==38,count
    rows=base.rows(Path(b1)); byid={r['id']:r for r in rows}
    for cid in ('mb1m-lu-0754','mb1m-lu-1105','mb1m-lu-2624'):
        r=byid[cid]; assert candidate.validate([r])['status']=='PASS'
        negative(r,r['front'].removeprefix('die '))
        negative(r,'das '+r['front'].removeprefix('die '))
        negative(r,r['front']+', '+base.custom(r)['canonical_unit']['headword'])
    assert count==47,count
    assert candidate.validate([byid['mb1m-lu-3098']])['status']=='FAIL'
    return {'status':'PASS','negative_controls':count,'contradictory_plural_metadata_rejected':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('a2');p.add_argument('b1');a=p.parse_args();print(json.dumps(run(a.a2,a.b1)))
