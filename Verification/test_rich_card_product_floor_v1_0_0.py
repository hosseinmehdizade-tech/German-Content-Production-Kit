#!/usr/bin/env python3
import importlib.util,json,tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('gate',HERE/'validate_rich_card_product_floor_v1_0_0.py')
gate=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(gate)
floor=json.loads((HERE.parent/'Prompt/GERMAN-RICH-CARD-PRODUCT-FLOOR-v1.0.0.json').read_text(encoding='utf-8'))

def verb(uid='v1'):
    return {'id':uid,'type':'verb','headword':'klettern','persian_meaning':'بالا رفتن','definition_de':'sich mit Händen und Füßen nach oben bewegen','core':{'present_3sg':'klettert','preterite_3sg':'kletterte','perfect':'ist geklettert','auxiliary':'sein','reflexive':False,'separability':'non_prefixed'},'examples':[{'id':f'{uid}-ex-{i:03d}','lang':'de-DE','text':t,'translations':[{'lang':'en-US','text':e}]} for i,(t,e) in enumerate([('Wir klettern auf einen Baum.','We climb a tree.'),('Die Kinder klettern über den Zaun.','The children climb over the fence.'),('Er klettert gern in den Bergen.','He likes climbing in the mountains.'),('Sie ist bis zum Gipfel geklettert.','She climbed to the summit.')],1)],'connections':[{'kind':'collocation','text':'auf einen Baum klettern'}]}

def run(ds,attempts): return gate.validate({'learning_units':ds},floor,{'external_evidence_attempts':attempts})

thin=verb(); thin.pop('definition_de'); thin['examples']=thin['examples'][:1]; thin['connections']=[]
r=run([thin],[])
assert r['status']=='FAIL'
codes={x['code'] for x in r['issues']}
assert 'PRODUCT_REQUIRED_UNIT_FIELD' in codes
assert 'PRODUCT_EXAMPLE_MINIMUM' in codes
assert 'PRODUCT_EXTERNAL_EVIDENCE_ATTEMPT_MISSING' in codes
assert 'PRODUCT_ZERO_EXTERNAL_ENRICHMENT' in codes
assert 'PRODUCT_LEXICAL_DETAIL_SYSTEM_HEALTH' in codes

good=verb()
r=run([good],[{'id':'v1','type':'verb','status':'success','sources':['de_wiktionary_live']}])
assert r['status']=='PASS', r
print('PASS thin-card regression + healthy rich-card fixture')
