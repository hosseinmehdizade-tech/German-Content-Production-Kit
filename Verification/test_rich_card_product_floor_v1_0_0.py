#!/usr/bin/env python3
import importlib.util,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('gate',HERE/'validate_rich_card_product_floor_v1_0_0.py')
gate=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(gate)
floor=json.loads((HERE.parent/'Prompt/GERMAN-RICH-CARD-PRODUCT-FLOOR-v1.0.0.json').read_text(encoding='utf-8'))

def verb(uid='v1'):
    examples=[]
    rows=[('Wir klettern auf einen Baum.','We climb a tree.'),('Die Kinder klettern über den Zaun.',None),('Er klettert gern in den Bergen.',None),('Sie ist bis zum Gipfel geklettert.',None)]
    for i,(t,e) in enumerate(rows,1):
        ex={'id':f'{uid}-ex-{i:03d}','lang':'de-DE','text':t,'translations':[]}
        if e: ex['translations']=[{'lang':'en-US','text':e}]
        examples.append(ex)
    return {'id':uid,'type':'verb','headword':'klettern','persian_meaning':'بالا رفتن','definition_de':'sich mit Händen und Füßen nach oben bewegen','core':{'present_3sg':'klettert','preterite_3sg':'kletterte','perfect':'ist geklettert','auxiliary':'sein','reflexive':False,'separability':'non_prefixed'},'examples':examples,'connections':[{'kind':'collocation','text':'auf einen Baum klettern'}]}

def phrase(uid='p1',with_rection=True):
    u={'id':uid,'type':'phrase','headword':'auf etw. (Dat.) bestehen','persian_meaning':'بر چیزی اصرار داشتن','core':{'structure':'auf etw. (Dat.) bestehen'},'examples':[
      {'id':f'{uid}-ex-001','lang':'de-DE','text':'Ich bestehe auf meiner Meinung.','translations':[{'lang':'en-US','text':'I insist on my opinion.'}]},
      {'id':f'{uid}-ex-002','lang':'de-DE','text':'Sie besteht auf einer Antwort.','translations':[]},
      {'id':f'{uid}-ex-003','lang':'de-DE','text':'Er besteht auf seinem Recht.','translations':[]},
      {'id':f'{uid}-ex-004','lang':'de-DE','text':'Wir bestehen auf einer Lösung.','translations':[]}
    ]}
    if with_rection: u['details']={'rection':['auf + Dativ']}
    return u

def run(ds,attempts): return gate.validate({'learning_units':ds},floor,{'external_evidence_attempts':attempts})

thin=verb(); thin.pop('definition_de'); thin['examples']=thin['examples'][:1]; thin['examples'][0]['translations']=[]; thin['connections']=[]
r=run([thin],[])
assert r['status']=='FAIL'
codes={x['code'] for x in r['issues']}
for required in ['PRODUCT_REQUIRED_UNIT_FIELD','PRODUCT_EXAMPLE_MINIMUM','PRODUCT_TRANSLATED_EXAMPLE_MINIMUM','PRODUCT_EXTERNAL_EVIDENCE_ATTEMPT_MISSING','PRODUCT_ZERO_EXTERNAL_ENRICHMENT','PRODUCT_LEXICAL_DETAIL_SYSTEM_HEALTH']:
    assert required in codes, (required,codes)

bad_phrase=phrase(with_rection=False)
r=run([bad_phrase],[])
assert r['status']=='FAIL' and 'PRODUCT_EXPLICIT_RECTION_MISSING' in {x['code'] for x in r['issues']}

good=verb(); p=phrase()
r=run([good,p],[{'id':'v1','type':'verb','status':'success','sources':['de_wiktionary_live']}])
assert r['status']=='PASS', r
print('PASS thin-card + English-example + phrase-rection regressions')
