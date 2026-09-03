#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'Workspaces/menschen-a2/tools/apply_residual_external_examples_v1.py'
SPEC=importlib.util.spec_from_file_location('residual',TOOL);m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)
CFG=json.loads((ROOT/'Workspaces/menschen-a2/tools/RESIDUAL-EXTERNAL-EXAMPLES-v1.json').read_text(encoding='utf-8'))

assert set(CFG['items'])=={'ma2-lu-0080','ma2-lu-0082','ma2-lu-0090','ma2-lu-0161','ma2-lu-0176','ma2-lu-0182','ma2-lu-0187','ma2-lu-0234','ma2-lu-0245','ma2-lu-0248','ma2-lu-0249'}
assert CFG['policy']['reject_generated_fallback'] is True
for uid,spec in CFG['items'].items():
    assert spec['candidates'],uid
    for c in spec['candidates']:
        assert c['verification_status']=='verified' and c['source_kind']!='generated' and c['url'].startswith('https://'),(uid,c)

# Self-contained generated-fallback fixture. The production v8 branch owns the
# real draft-fallback file; downstream QA must not depend on that branch merely
# to prove that generated learner examples are stripped before PASS.
generated_text='Darf ich dir meine Kollegin vorstellen?'
with tempfile.TemporaryDirectory() as td:
    fixture=Path(td)/'generated.json'
    fixture.write_text(json.dumps({'items':{'ma2-lu-0187':[{'text':generated_text}]}},ensure_ascii=False),encoding='utf-8')
    bad=m.generated_texts(fixture)

# Unit-level helpers: generated fallback must be removed, exact external evidence
# appended, and the known vorstellen polysemy repaired to sense [3b].
u={'id':'ma2-lu-0187','type':'verb','headword':'vorstellen','definition_de':'etwas nach vorne stellen','examples':[
 {'id':'ma2-lu-0187-ex-001','lang':'de-DE','text':'Ich stelle dir ihn vor.','order':1,'translations':[{'lang':'en-US','text':'I introduce him to you.'}]},
 {'id':'ma2-lu-0187-ex-002','lang':'de-DE','text':'Vorhandenes externes Beispiel A.','order':2,'translations':[]},
 {'id':'ma2-lu-0187-ex-003','lang':'de-DE','text':'Vorhandenes externes Beispiel B.','order':3,'translations':[]},
 {'id':'ma2-lu-0187-ex-004','lang':'de-DE','text':generated_text,'order':4,'translations':[]}
], 'connections':[{'kind':'collocation','text':'etwas vor die Tür stellen'}], 'details':{'synonyms':['voranstellen'],'rection':['Akkusativ']}, 'provenance':{'sources':[{'source_id':'assistant_pedagogical_example','source_kind':'generated','locator':'generated://menschen-a2/ma2-lu-0187/product-floor-residual-v1'}]}}
assert m.remove_generated(u,bad)==1
assert len(u['examples'])==3
assert m.repair_vorstellen(u) is True
assert u['definition_de']=='jemanden einem anderen, der ihn nicht kennt, bekannt machen'
assert u['connections']==[] and 'synonyms' not in u['details'] and u['details']['rection']==['Akkusativ']
assert not any(s.get('source_id')=='assistant_pedagogical_example' for s in u['provenance']['sources'])

cand=CFG['items']['ma2-lu-0187']['candidates'][0]
m.add_provenance(u,cand)
u['examples'].append({'id':m.next_example_id(u),'lang':'de-DE','text':cand['text'],'order':4,'translations':[]})
assert len(u['examples'])==4
assert any(s.get('source_id')==cand['source_id'] for s in u['provenance']['sources'])
assert all(s.get('source_kind')!='generated' for s in u['provenance']['sources'])
print('PASS Menschen A2 residual external-evidence + generated-fallback rejection + vorstellen sense override regression')
