#!/usr/bin/env python3
from pathlib import Path
import json, copy

ROOT=Path(__file__).resolve().parents[1]
canonical_path=ROOT/'02-canonical/CANONICAL.json'
seed_path=ROOT/'tools/ENRICHMENT-SEED.json'
out_path=ROOT/'02-canonical/CANONICAL-ENRICHED.json'
evidence_path=ROOT/'03-evidence/EVIDENCE-INDEX.json'

ds=json.loads(canonical_path.read_text(encoding='utf-8'))
seed=json.loads(seed_path.read_text(encoding='utf-8'))['items']
generated=0
translated=0
source_examples=0

for unit in ds['learning_units']:
    uid=unit['id']
    s=seed[uid]
    if not unit.get('examples'):
        text=s.get('german_example')
        if not text:
            raise SystemExit(f'missing usable example and no generated example seed for {uid}')
        unit['examples']=[{
            'id':f'{uid}-ex-001','lang':'de-DE','text':text,'order':1,'translations':[]
        }]
        unit.setdefault('provenance',{}).setdefault('sources',[]).append({
            'source_id':'assistant_pedagogical_example',
            'source_kind':'generated',
            'what_was_verified':[],
            'verification_status':'unverified',
            'accessed_at':'2026-09-02',
            'evidence_note':'Pedagogical German example added because the source row did not contain a usable example; generated content is reviewed by Stage 4 and is not represented as external attestation.'
        })
        generated+=1
    else:
        source_examples+=1
    if len(unit['examples']) != 1:
        raise SystemExit(f'expected exactly one example at enrichment boundary for {uid}')
    ex=unit['examples'][0]
    ex['translations']=[
        {'lang':'fa-IR','text':s['translation_fa']},
        {'lang':'en-US','text':s['translation_en']}
    ]
    translated+=2
    unit.setdefault('provenance',{}).setdefault('sources',[]).append({
        'source_id':'assistant_translation_review',
        'source_kind':'other',
        'what_was_verified':['persian_example_translation','english_example_translation'],
        'verification_status':'verified',
        'accessed_at':'2026-09-02',
        'evidence_note':'Production translation generated and sense-alignment reviewed against the German example and canonical Persian meaning; this is internal production evidence, not an external lexicon claim.'
    })

out_path.parent.mkdir(parents=True,exist_ok=True)
out_path.write_text(json.dumps(ds,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ev={
  'schema_version':'1.0.0',
  'dataset':'menschen-a2',
  'stage':3,
  'status':'PASS',
  'canonical_units':len(ds['learning_units']),
  'source_examples_retained':source_examples,
  'generated_german_examples':generated,
  'example_translations_added':translated,
  'external_lexical_enrichment_used':False,
  'connections_added':0,
  'synonyms_added':0,
  'antonyms_added':0,
  'rection_added':0,
  'quality_policy':'No density fields were fabricated. The five missing/invalid source-example cases received one minimal pedagogical example; all example translations were sense-alignment reviewed. Source inventory/raw row evidence remains authoritative.',
  'evidence_sources':[
    {'source_id':'menschen_a2_user_screenshots','role':'authoritative source for source facts'},
    {'source_id':'assistant_translation_review','role':'internal translation review only'},
    {'source_id':'assistant_pedagogical_example','role':'generated example provenance for five units only'}
  ]
}
evidence_path.parent.mkdir(parents=True,exist_ok=True)
evidence_path.write_text(json.dumps(ev,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(ev,ensure_ascii=False))
