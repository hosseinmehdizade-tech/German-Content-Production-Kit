#!/usr/bin/env python3
"""Exact current-v505 R16 pre-entry payload plus 13 source-aware R17 deltas."""
import pathlib,json,copy,hashlib,importlib.util
P=pathlib.Path('/mnt/data/lesen_r17_20261107')
oldm=pathlib.Path('/mnt/data/lesen_r16_20261107/Lesen-Production-Master-v1.3.0-R16-22CONCLUSIONS-TRILINGUAL-CANDIDATE.json')
oldr=pathlib.Path('/mnt/data/lesen_r16_20261107/Lesen-R16-v505-22CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json')
newm=P/'Lesen-Production-Master-v1.3.0-R17-23CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
out=P/'Lesen-R17-v505-23CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json'
evd=P/'LESEN-R17-V505-TRANSPORT-EVIDENCE.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(oldm.read_bytes())=='0b31f21ed6cd65b2562d3806e58269294196d161b05ba87cc7af35e3ab87ffa5'
assert sha(oldr.read_bytes())=='afec137c5868eb26051c913e3dedefcc848a4a932d5e4cf23e5e21409516f641'
mpath='/mnt/data/lesen_r4_workspace/build_lesen_r3_runtime_candidate.py'
spec=importlib.util.spec_from_file_location('v505_exact_map_r17',mpath)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
a=json.loads(oldm.read_text());b=json.loads(oldr.read_text());c=json.loads(newm.read_text());d=copy.deepcopy(b)
assert sha(canon(b['entries']))==b['integrity']['entries_sha256']
assert sha(canon({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
changed=[]
for i,(old,new,e) in enumerate(zip(a['items'],c['items'],b['entries'])):
 assert old['id']==new['id']==e['source_item_id']
 mod.verify_section_mapping(old,e)
 if old!=new:
  diff={k for k in old if old[k]!=new[k]};assert 39<=i+1<=52 and i+1!=51 and diff=={'reading','grammar','quality'},(old['id'],diff)
  assert old['questions']==new['questions'] and old['vocabulary']==new['vocabulary']
  assert old['grammar']['auto_lens_targets']==new['grammar']['auto_lens_targets']
  assert old['grammar']['grammar_tasks']==new['grammar']['grammar_tasks']
  d['entries'][i]=mod.apply_fields(old,new,e);changed.append(old['id'])
 else:assert d['entries'][i]==e
 mod.verify_section_mapping(new,d['entries'][i])
assert len(changed)==13
counts={'entries':68,'reading_units':68,
 'passages':sum(len(e['unit']['passages']) for e in d['entries']),
 'exercises':sum(len(e['exercises']) for e in d['entries']),
 'vocabulary_entries':sum(len(e['unit']['r38']['vocabulary']) for e in d['entries']),
 'curated_grammar':sum(len(e['unit']['r38']['grammar']['curated_annotations']) for e in d['entries']),
 'full_text_grammar':sum(len(e['unit']['r38']['grammar']['full_text_occurrences']) for e in d['entries'])}
assert counts=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4097},counts
d['counts']=counts
d['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(newm.read_bytes())}
d['compiler']={'id':'lesen-r17-source-aligned-conclusions-v505-delta-v1','deterministic':True,'runtime_analysis_required':False,
'contract':'Exact source-aware R16 runtime plus 13 changed R17 entries with 23 targeted conclusions, four translation tails.',
'note':'NOT historical compiler, grammar nine-lens rerun, browser Stage6 import or released content.'}
d['candidate_review']={'status':'R17_23_CONCLUSIONS_STAGE4_6_7_HOLD','changed_unit_ids':changed,
'changed_section_ids':['p02','p03'],'changed_sentence_ids':['p02-s03','p03-s03'],
'old_fulltext_spans_retired':72,'new_manual_relative_grammar':9,'curated_relative_retargets':9,
'four_specific_translation_tail_pairs_revised':True,'full_semantic_stage4':'HOLD','browser_indexeddb_stage6':'NOT_RUN',
'original_current':'UNCHANGED','grammar_total':4097,'remaining_generic_p02_s03':15,'remaining_generic_p03_s03':11}
d['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(d['entries']))};d['integrity']['payload_sha256']=sha(canon({k:v for k,v in d.items() if k!='integrity'}))
write(out,d)
ev={'schema':'lesen-r17-source-aware-v505-preentry-transport@1','date':'2026-11-07','parent_master_sha256':sha(oldm.read_bytes()),
'parent_runtime_sha256':sha(oldr.read_bytes()),'candidate_master_sha256':sha(newm.read_bytes()),'candidate_runtime_sha256':sha(out.read_bytes()),
'candidate_runtime_bytes':out.stat().st_size,'counts':counts,'changed_units':changed,'unchanged_entries':55,
'changed_conclusion_sections':23,'entries_integrity_verified_before_and_after':True,'new_integrity':d['integrity'],
'section_mapping_verified':68,'independent_stage4':'HOLD','browser_stage6':'NOT_RUN','stage7':'NOT_RELEASED'}
write(evd,ev);print(json.dumps(ev,ensure_ascii=False,indent=2))