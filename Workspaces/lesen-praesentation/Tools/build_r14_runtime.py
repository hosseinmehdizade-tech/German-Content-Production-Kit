#!/usr/bin/env python3
"""R13 -> R14 exact v505 source-aware p03 delta transport, not native full compiler."""
import json,copy,hashlib,pathlib,importlib.util
P=pathlib.Path('/mnt/data/lesen_r14_20261107')
OLDM=pathlib.Path('/mnt/data/lesen_r13_20261107/Lesen-Production-Master-v1.3.0-R13-16P04-TRILINGUAL-CANDIDATE.json')
OLDR=pathlib.Path('/mnt/data/lesen_r13_20261107/Lesen-R13-v505-16P04-RUNTIME-PREENTRY-CANDIDATE.json')
NEWM=P/'Lesen-Production-Master-v1.3.0-R14-14P03-TRILINGUAL-CANDIDATE.json'
OUT=P/'Lesen-R14-v505-14P03-RUNTIME-PREENTRY-CANDIDATE.json'
EVD=P/'LESEN-R14-RUNTIME-TRANSPORT-EVIDENCE.json'
SHA_M='d619d7d9777849a25a154b52574b66a3dd92fc4f4d045e7b4ceb4e0fbc16b30f'
SHA_R='628f56e6bab608a6ab5f7a8939eea3a8451f1fbc4a8699bcaeb23a56f10d78a7'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
write=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
assert sha(OLDM.read_bytes())==SHA_M and sha(OLDR.read_bytes())==SHA_R
spec=importlib.util.spec_from_file_location('source_v505_transport','/mnt/data/lesen_r4_workspace/build_lesen_r3_runtime_candidate.py')
mapper=importlib.util.module_from_spec(spec);spec.loader.exec_module(mapper)
a=json.loads(OLDM.read_text());b=json.loads(OLDR.read_text());c=json.loads(NEWM.read_text());d=copy.deepcopy(b)
expected={13,17,21,25,29,33,37,41,45,49,53,57,61,65}
assert len(a['items'])==len(b['entries'])==len(c['items'])==68
assert sha(canon(b['entries']))==b['integrity']['entries_sha256']
assert sha(canon({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
changed=[]
for i,(old,new,ent) in enumerate(zip(a['items'],c['items'],b['entries'])):
 n=i+1
 assert old['id']==new['id']==ent['source_item_id']
 mapper.verify_section_mapping(old,ent)
 diff={key for key in old if old[key]!=new[key]}
 if n in expected:
  assert diff=={'reading','grammar','quality'},(n,diff)
  assert old['reading']['sections'][:2]==new['reading']['sections'][:2]
  assert old['reading']['sections'][3:]==new['reading']['sections'][3:]
  assert all(old['reading']['sections'][2]['sentences'][k]==new['reading']['sections'][2]['sentences'][k] for k in [1,2])
  d['entries'][i]=mapper.apply_fields(old,new,ent);changed.append(new['id'])
 else:
  assert not diff,(n,diff)
  assert d['entries'][i]==ent
 mapper.verify_section_mapping(new,d['entries'][i])
assert changed==[f'LES-PRES-{n:03d}' for n in sorted(expected)]
counts={'entries':68,'reading_units':68,'passages':sum(len(e['unit']['passages']) for e in d['entries']),
'exercises':sum(len(e['exercises']) for e in d['entries']),
'vocabulary_entries':sum(len(e['unit']['r38']['vocabulary']) for e in d['entries']),
'curated_grammar':sum(len(e['unit']['r38']['grammar']['curated_annotations']) for e in d['entries']),
'full_text_grammar':sum(len(e['unit']['r38']['grammar']['full_text_occurrences']) for e in d['entries'])}
assert counts=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4298},counts
d['counts']=counts
d['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(NEWM.read_bytes())}
d['compiler']={'id':'lesen-r14-p03-scoped-delta-transport-v1','deterministic':True,'runtime_analysis_required':False,
 'contract':'Exact R13 v505 preentry runtime plus fourteen source-verified p03 trilingual and grammar changes',
 'note':'NOT historical full runtime compiler, native nine-lens grammar derivation, browser IndexedDB Stage6 or release.'}
d['candidate_review']={'status':'R14_CANDIDATE_STAGE4_6_7_HOLD','changed_unit_ids':changed,'changed_section_ids':['p03'],
 'changed_sentence_ids':['p03-s01','p03-s04'],'preserved_middle_sentences':28,
 'native_nine_lens_rerun':False,'full_semantic_stage4':'HOLD','browser_stage6':'NOT_RUN','curated_current':'UNCHANGED','grammar_total':4298}
d['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(d['entries']))}
d['integrity']['payload_sha256']=sha(canon({k:v for k,v in d.items() if k!='integrity'}))
write(OUT,d)
ev={'schema':'lesen-r14-v505-scoped-p03-delta-transport@1.0.0','date':'2026-11-07',
 'parent_r13_master_sha256':SHA_M,'parent_r13_runtime_sha256':SHA_R,
 'r14_master_sha256':sha(NEWM.read_bytes()),'r14_runtime_sha256':sha(OUT.read_bytes()),
 'runtime_bytes':OUT.stat().st_size,'counts':counts,'changed_unit_ids':changed,'untouched_entries':54,
 'compiled_from_sha256':d['compiled_from']['sha256'],'integrity_entries_sha256':d['integrity']['entries_sha256'],
 'integrity_payload_sha256':d['integrity']['payload_sha256'],
 'source_mapper_verified_68_of_68':True,'native_v505_import_validator':'PENDING_SEPARATE_RUN',
 'independent_stage4':'HOLD','nine_lens_engine_rerun':False,'browser_stage6':'NOT_RUN','final_stage7':'NOT_RELEASED'}
write(EVD,ev);print(json.dumps(ev,indent=2,ensure_ascii=False))