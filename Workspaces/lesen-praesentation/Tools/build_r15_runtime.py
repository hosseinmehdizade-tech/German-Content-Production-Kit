#!/usr/bin/env python3
"""Exact R14 v505 transport + 14 changed source lesson mappings, not native Stage6."""
import json,copy,hashlib,pathlib,importlib.util
P=pathlib.Path('/mnt/data/lesen_r15_20261107');OLDM=pathlib.Path('/mnt/data/lesen_r14_20261107/Lesen-Production-Master-v1.3.0-R14-14P03-TRILINGUAL-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r14_20261107/Lesen-R14-v505-14P03-RUNTIME-PREENTRY-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R15-25CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
OUT=P/'Lesen-R15-v505-25CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json'
EVD=P/'LESEN-R15-RUNTIME-TRANSPORT-EVIDENCE.json'
SHA_M='40f4eee25d4ea541d33f91f327bc88243ec5e2971419927ae43c2f0035af2568';SHA_R='84b4e1aa8ad6f9299545eb52b2a730474dfc91e635be5cbd843d8e2bca4ea4f3'
sha=lambda b:hashlib.sha256(b).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(OLDM.read_bytes())==SHA_M and sha(OLDR.read_bytes())==SHA_R
spec=importlib.util.spec_from_file_location('source_v505_transport','/mnt/data/lesen_r4_workspace/build_lesen_r3_runtime_candidate.py')
mapper=importlib.util.module_from_spec(spec);spec.loader.exec_module(mapper)
a=json.loads(OLDM.read_text());b=json.loads(OLDR.read_text());c=json.loads(NEWM.read_text());d=copy.deepcopy(b)
assert sha(canon(b['entries']))==b['integrity']['entries_sha256'] and sha(canon({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
changed=[]
for i,(old,new,ent) in enumerate(zip(a['items'],c['items'],b['entries'])):
 n=i+1
 assert old['id']==new['id']==ent['source_item_id']
 mapper.verify_section_mapping(old,ent)
 diff={key for key in old if old[key]!=new[key]}
 if 11<=n<=24:
  assert diff=={'reading','grammar','quality'},(n,diff)
  assert old['questions']==new['questions'] and old['vocabulary']==new['vocabulary']
  assert old['grammar']['grammar_tasks']==new['grammar']['grammar_tasks']
  assert old['grammar']['auto_lens_targets']==new['grammar']['auto_lens_targets']
  assert [s['id'] for s in old['reading']['sections']]==[s['id'] for s in new['reading']['sections']]
  d['entries'][i]=mapper.apply_fields(old,new,ent)
  changed.append(new['id'])
 else:
  assert not diff,(n,diff)
  assert d['entries'][i]==ent
 mapper.verify_section_mapping(new,d['entries'][i])
assert len(changed)==14
counts={'entries':len(d['entries']),'reading_units':len(d['entries']),'passages':sum(len(e['unit']['passages']) for e in d['entries']),
 'exercises':sum(len(e['exercises']) for e in d['entries']),'vocabulary_entries':sum(len(e['unit']['r38']['vocabulary']) for e in d['entries']),
 'curated_grammar':sum(len(e['unit']['r38']['grammar']['curated_annotations']) for e in d['entries']),
 'full_text_grammar':sum(len(e['unit']['r38']['grammar']['full_text_occurrences']) for e in d['entries'])}
assert counts=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4220},counts
d['counts']=counts
d['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(NEWM.read_bytes())}
d['compiler']={'id':'lesen-r15-p02-p03-conclusion-scoped-v505-delta-v1','deterministic':True,'runtime_analysis_required':False,
 'contract':'Exact current R14 v505 preentry runtime plus fourteen source-mapped lesson updates for 25 revised concluding sentences.',
 'note':'Not historical full compiler, native full grammar extraction, browser IndexedDB Stage6 or release.'}
d['candidate_review']={'status':'R15_CANDIDATE_STAGE4_6_7_HOLD','changed_unit_ids':changed,'changed_section_ids':['p02','p03'],
 'changed_sentence_ids':['p02-s03','p03-s03'],'old_generic_grammar_spans_retired':78,'retargeted_existing_curated_relative_examples':9,
 'native_nine_lens_rerun':False,'full_semantic_stage4':'HOLD','browser_stage6':'NOT_RUN','curated_current':'UNCHANGED',
 'grammar_total':4220,'remaining_exact_generic_p02_s03':41,'remaining_exact_generic_p03_s03':30}
d['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(d['entries']))};d['integrity']['payload_sha256']=sha(canon({k:v for k,v in d.items() if k!='integrity'}))
write(OUT,d)
evidence={'schema':'lesen-r15-v505-scoped-conclusions-delta-transport@1.0.0','date':'2026-11-07',
 'parent_r14_master_sha256':SHA_M,'parent_r14_runtime_sha256':SHA_R,'r15_master_sha256':sha(NEWM.read_bytes()),
 'r15_runtime_sha256':sha(OUT.read_bytes()),'runtime_bytes':OUT.stat().st_size,'counts':counts,
 'changed_unit_ids':changed,'unchanged_entries':54,'changed_conclusion_sections':25,
 'compiled_from_sha256':d['compiled_from']['sha256'],'integrity_entries_sha256':d['integrity']['entries_sha256'],
 'integrity_payload_sha256':d['integrity']['payload_sha256'],'source_mapper_verified_68_of_68':True,
 'native_v505_import_validator':'PENDING_SEPARATE_RUN','formal_independent_stage4':'HOLD','full_grammar_engine_rerun':False,
 'browser_indexeddb_stage6':'NOT_RUN','final_stage7':'NOT_RELEASED'}
write(EVD,evidence);print(json.dumps(evidence,ensure_ascii=False,indent=2))