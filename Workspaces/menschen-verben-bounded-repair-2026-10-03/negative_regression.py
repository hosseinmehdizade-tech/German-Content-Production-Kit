"""Challenge the new gates with actual defective immutable parents."""
import json, pathlib, sys, collections
O=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(O.parent/'German-Content-Production-Kit/Verification'))
from prevention_preflight import projection_errors
from bounded_content_preflight import source_errors
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
results={}
for level,expected in [('A1',5),('A2',0),('B1',397)]:
    errors=projection_errors(load(O/(level+'-parent-rows.json')))
    assert len(errors)==expected,(level,errors)
    results[level]={'parent_rejections':len(errors),'error_classes':dict(collections.Counter(e.split(': ',1)[-1] for e in errors))}
    assert projection_errors(load(O/(level+'-rows.json')))==[]
occ=load(next((O/'parents/A2/GFP-v451-R85/02-Source').rglob('*SOURCE-OCCURRENCES*.json')))
binding=load(O/'staging/A2/SOURCE-RAW-BINDING.json')
errors=source_errors(occ,binding)
assert len(errors)==2 and all('SOURCE_RAW_TEXT_BINDING_MISMATCH' in e for e in errors)
results['A2']['source_raw_parent_rejections']=errors
results['status']='PASS_ACTUAL_DEFECTIVE_PARENTS_REJECTED_SUCCESSORS_ACCEPTED'
for p in [O/'REGRESSION-NEGATIVE-RESULTS.json',O.parent/'German-Content-Production-Kit/Workspaces/menschen-verben-bounded-repair-2026-10-03/REGRESSION-NEGATIVE-RESULTS.json']:
    p.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({l:v['parent_rejections'] for l,v in results.items() if isinstance(v,dict)}))
