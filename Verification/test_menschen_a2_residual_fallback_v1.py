#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/'Workspaces/menschen-a2/tools'
sys.path.insert(0,str(TOOLS))
import enrich_rich_card_v8 as v8

residual_ids=['ma2-lu-0080','ma2-lu-0082','ma2-lu-0090','ma2-lu-0161','ma2-lu-0176','ma2-lu-0182','ma2-lu-0187','ma2-lu-0234','ma2-lu-0245','ma2-lu-0248','ma2-lu-0249']
headwords={
 'ma2-lu-0080':('verb','sich ausruhen'),
 'ma2-lu-0082':('verb','sich wiegen'),
 'ma2-lu-0090':('verb','sich verlieren'),
 'ma2-lu-0161':('verb','sich lösen'),
 'ma2-lu-0176':('phrase','sich etw. (Dat.) verschließen'),
 'ma2-lu-0182':('phrase','aufzeigen'),
 'ma2-lu-0187':('verb','vorstellen'),
 'ma2-lu-0234':('verb','verfilmen'),
 'ma2-lu-0245':('verb','weglaufen'),
 'ma2-lu-0248':('phrase','zu jdm. aufschließen'),
 'ma2-lu-0249':('verb','absperren')
}
units=[]
for uid in residual_ids:
    typ,h=headwords[uid]
    units.append({'id':uid,'type':typ,'headword':h,'examples':[{'id':uid+'-ex-001','lang':'de-DE','text':'Quelle '+uid,'order':1,'translations':[]}],'provenance':{'sources':[]}})
# A healthy card must not be touched.
units.append({'id':'healthy','type':'verb','headword':'lernen','examples':[{'id':f'healthy-ex-{i:03d}','lang':'de-DE','text':f'Beispiel {i}.','order':i,'translations':[]} for i in range(1,5)],'provenance':{'sources':[]}})
out={'learning_units':units}
added,touched,unresolved=v8._generated_fallback(out)
assert not unresolved,unresolved
assert len(touched)==11,touched
assert added==33,added
for u in out['learning_units'][:-1]:
    assert len(u['examples'])==4,(u['id'],len(u['examples']))
    src=u['provenance']['sources'][-1]
    assert src['source_id']=='assistant_pedagogical_example'
    assert src['source_kind']=='generated'
    assert src['verification_status']=='unverified'
    assert src['what_was_verified']==[]
healthy=out['learning_units'][-1]
assert len(healthy['examples'])==4
assert healthy['provenance']['sources']==[]
print('PASS Menschen A2 targeted residual pedagogical fallback regression')
