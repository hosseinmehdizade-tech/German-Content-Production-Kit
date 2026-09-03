#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'Workspaces/menschen-a2/tools/apply_residual_external_examples_v1.py'
SPEC=importlib.util.spec_from_file_location('residual',TOOL);m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)
RES=json.loads((ROOT/'Workspaces/menschen-a2/tools/RESIDUAL-EXTERNAL-EXAMPLES-v1.json').read_text(encoding='utf-8'))
PRI=json.loads((ROOT/'Workspaces/menschen-a2/tools/GENERATED-PRIMARY-REPLACEMENTS-v1.json').read_text(encoding='utf-8'))

residual_ids={'ma2-lu-0080','ma2-lu-0082','ma2-lu-0090','ma2-lu-0161','ma2-lu-0176','ma2-lu-0182','ma2-lu-0187','ma2-lu-0234','ma2-lu-0245','ma2-lu-0248','ma2-lu-0249'}
primary_ids={'ma2-lu-0048','ma2-lu-0192','ma2-lu-0216','ma2-lu-0239','ma2-lu-0242'}
assert set(RES['items'])==residual_ids
assert set(PRI['items'])==primary_ids
assert not residual_ids & primary_ids
assert RES['policy']['reject_generated_fallback'] is True and PRI['policy']['no_fabrication'] is True
for cfg in (RES,PRI):
    for uid,spec in cfg['items'].items():
        assert spec['candidates'],uid
        for c in spec['candidates']:
            assert c['verification_status']=='verified' and c['source_kind']!='generated' and c['url'].startswith('https://'),(uid,c)
for uid,spec in PRI['items'].items():
    assert spec.get('replace_generated_primary') is True,uid
    assert any(any(t.get('lang')=='en-US' and str(t.get('text') or '').strip() for t in c.get('translations',[])) for c in spec['candidates']),uid

# 1) Residual v8 filler: remove only the known generated fourth example while
# preserving the reviewed primary translation record, then repair vorstellen
# to the source-bound interpersonal sense and add attested evidence.
fallback_text='Darf ich dir meine Kollegin vorstellen?'
with tempfile.TemporaryDirectory() as td:
    fixture=Path(td)/'generated.json'
    fixture.write_text(json.dumps({'items':{'ma2-lu-0187':[{'text':fallback_text}]}},ensure_ascii=False),encoding='utf-8')
    bad=m.generated_texts(fixture)
u={'id':'ma2-lu-0187','type':'verb','headword':'vorstellen','definition_de':'etwas nach vorne stellen','examples':[
 {'id':'ma2-lu-0187-ex-001','lang':'de-DE','text':'Ich stelle dir ihn vor.','order':1,'translations':[{'lang':'en-US','text':'I introduce him to you.'}]},
 {'id':'ma2-lu-0187-ex-002','lang':'de-DE','text':'Vorhandenes externes Beispiel A.','order':2,'translations':[]},
 {'id':'ma2-lu-0187-ex-003','lang':'de-DE','text':'Vorhandenes externes Beispiel B.','order':3,'translations':[]},
 {'id':'ma2-lu-0187-ex-004','lang':'de-DE','text':fallback_text,'order':4,'translations':[]}
], 'connections':[{'kind':'collocation','text':'etwas vor die Tür stellen'}], 'details':{'synonyms':['voranstellen'],'rection':['Akkusativ']}, 'provenance':{'sources':[
 {'source_id':'assistant_translation_review','source_kind':'other','verification_status':'verified'},
 {'source_id':'assistant_pedagogical_example','source_kind':'generated','locator':'generated://menschen-a2/ma2-lu-0187/product-floor-residual-v1'}
]}}
removed,had=m.remove_generated(u,bad,replace_primary=False)
assert had and [x['text'] for x in removed]==[fallback_text]
assert len(u['examples'])==3
assert any(s.get('source_id')=='assistant_translation_review' for s in u['provenance']['sources'])
assert not m.generated_sources(u)
assert m.repair_vorstellen(u) is True
assert u['definition_de']=='jemanden einem anderen, der ihn nicht kennt, bekannt machen'
assert u['connections']==[] and 'synonyms' not in u['details'] and u['details']['rection']==['Akkusativ']
cand=RES['items']['ma2-lu-0187']['candidates'][0]
m.add_provenance(u,cand)
u['examples'].append({'id':m.next_example_id(u),'lang':'de-DE','text':cand['text'],'order':4,'translations':[]})
assert len(u['examples'])==4 and any(s.get('source_id')==cand['source_id'] for s in u['provenance']['sources'])

# 2) Original generated primary: only a unit explicitly listed in the primary
# replacement authority may drop position 0. Its stale translation-review
# provenance is removed, and the attested replacement brings a newly reviewed
# English translation.
ptext='Wir reisen morgen früh nach Berlin ab.'
p={'id':'ma2-lu-0192','type':'verb','headword':'abreisen','examples':[
 {'id':'ma2-lu-0192-ex-001','lang':'de-DE','text':ptext,'order':1,'translations':[{'lang':'en-US','text':'We leave for Berlin early tomorrow.'}]},
 {'id':'ma2-lu-0192-ex-002','lang':'de-DE','text':'Extern A.','order':2,'translations':[]},
 {'id':'ma2-lu-0192-ex-003','lang':'de-DE','text':'Extern B.','order':3,'translations':[]},
 {'id':'ma2-lu-0192-ex-004','lang':'de-DE','text':'Extern C.','order':4,'translations':[]}
], 'provenance':{'sources':[
 {'source_id':'assistant_pedagogical_example','source_kind':'generated','verification_status':'unverified'},
 {'source_id':'assistant_translation_review','source_kind':'other','verification_status':'verified'}
]}}
removed,had=m.remove_generated(p,set(),replace_primary=True)
assert had and [x['text'] for x in removed]==[ptext]
assert len(p['examples'])==3 and not m.generated_sources(p)
assert not any(s.get('source_id')=='assistant_translation_review' for s in p['provenance']['sources'])
pc=PRI['items']['ma2-lu-0192']['candidates'][0]
m.add_provenance(p,pc)
p['examples'].append({'id':m.next_example_id(p),'lang':'de-DE','text':pc['text'],'order':4,'translations':pc['translations']})
assert len(p['examples'])==4
assert any(t.get('lang')=='en-US' for t in p['examples'][-1]['translations'])
assert any(s.get('source_id')=='assistant_translation_review' for s in p['provenance']['sources'])
assert not m.generated_sources(p)

print('PASS A2 attested residual + generated-primary replacement + strict vorstellen sense regressions')
