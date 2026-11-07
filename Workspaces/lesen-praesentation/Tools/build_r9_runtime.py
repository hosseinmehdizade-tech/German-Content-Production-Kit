#!/usr/bin/env python3
"""R8 v505 preentry JSON + strict ten-unit R9 text/grammar delta.

No native browser write, historical compiler rerun, or CURRENT promotion.
"""
import hashlib, json, copy, pathlib, importlib.util, collections
P=pathlib.Path('/mnt/data/lesen_r9_20261107')
PARENT_MASTER=pathlib.Path('/mnt/data/lesen_r8_20261107/Lesen-Production-Master-v1.3.0-R8-18UNIT-Q123-CANDIDATE.json')
PARENT_RUNTIME=pathlib.Path('/mnt/data/lesen_r8_20261107/Lesen-R8-v505-18UNIT-Q123-RUNTIME-CANDIDATE.json')
R9_MASTER=P/'Lesen-Production-Master-v1.3.0-R9-10P04-TRILINGUAL-CANDIDATE.json'
OUT=P/'Lesen-R9-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json'
EVIDENCE=P/'LESEN-R9-V505-TRANSPORT-VERIFICATION.json'
SHA_R8M='f3e22d1f62aa78590f44ccfe358a9240319a99c9d8a1f39fc8a1ee81ac6d4cf2'
SHA_R8R='da770588aee670e60cf985dbfdcfd4fe0715847b43822f214ce90ba27bba4608'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(PARENT_MASTER.read_bytes())==SHA_R8M
assert sha(PARENT_RUNTIME.read_bytes())==SHA_R8R
spec=importlib.util.spec_from_file_location('srcverified','/mnt/data/lesen_r4_workspace/build_lesen_r3_runtime_candidate.py')
mapmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mapmod)
a=json.loads(PARENT_MASTER.read_text(encoding='utf8')); b=json.loads(PARENT_RUNTIME.read_text(encoding='utf8'))
c=json.loads(R9_MASTER.read_text(encoding='utf8'));out=copy.deepcopy(b)
assert len(a['items'])==len(c['items'])==len(b['entries'])==68
assert sha(canonical(b['entries']))==b['integrity']['entries_sha256']
assert sha(canonical({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
changed=[]
for i,(prev,new,entry) in enumerate(zip(a['items'],c['items'],b['entries'])):
    assert prev['id']==new['id']==entry['source_item_id']
    mapmod.verify_section_mapping(prev,entry)
    diffs={key for key in prev if prev[key]!=new[key]}
    if i+1 in range(11,21):
        assert diffs=={'reading','grammar','quality'},(i,diffs)
        assert prev['reading']['sections'][:3]==new['reading']['sections'][:3]
        assert prev['reading']['sections'][4:]==new['reading']['sections'][4:]
        assert prev['reading']['sections'][3]['sentences'][1]==new['reading']['sections'][3]['sentences'][1]
        assert prev['questions']==new['questions']
        out['entries'][i]=mapmod.apply_fields(prev,new,entry)
        changed.append(prev['id'])
    else:
        assert diffs==set(),(i,diffs)
        assert out['entries'][i]==entry
    mapmod.verify_section_mapping(new,out['entries'][i])
assert changed==[f'LES-PRES-{k:03d}' for k in range(11,21)]
counts={'entries':len(out['entries']),'reading_units':len(out['entries']),
 'passages':sum(len(x['unit']['passages']) for x in out['entries']),
 'exercises':sum(len(x['exercises']) for x in out['entries']),
 'vocabulary_entries':sum(len(x['unit']['r38']['vocabulary']) for x in out['entries']),
 'curated_grammar':sum(len(x['unit']['r38']['grammar']['curated_annotations']) for x in out['entries']),
 'full_text_grammar':sum(len(x['unit']['r38']['grammar']['full_text_occurrences']) for x in out['entries'])}
assert counts=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4570},counts
out['counts']=counts
out['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(R9_MASTER.read_bytes())}
out['compiler']={'id':'lesen-r9-10p04-trilingual-bounded-delta-v1','deterministic':True,'runtime_analysis_required':False,
    'contract':'R8 preentry runtime + precisely 10 edited reading sections, translations and scoped grammar offsets',
    'note':'This is deterministic source-aware transport, not the full native Lesen grammar engine or official app compiler.'}
out['candidate_review']={'status':'PREENTRY_CANDIDATE_NOT_STAGE4_6_7','changed_unit_ids':changed,'changed_section_ids':['p04'],
    'changed_sentences_per_unit':['p04-s01','p04-s03'],'unchanged_p04_s02_all_ten':True,'independent_semantic_stage4':'HOLD',
    'grammar_source_engine_rerun':False,'browser_indexeddb_stage6':'NOT_RUN',
    'fulltext_grammar_count_after_exact_scoped_reanchor':counts['full_text_grammar'],
    'parent_r8_runtime_sha256':SHA_R8R,'original_current':'UNCHANGED'}
out['integrity']={'algorithm':'sha256','entries_sha256':sha(canonical(out['entries']))}
out['integrity']['payload_sha256']=sha(canonical({k:v for k,v in out.items() if k!='integrity'}))
write(OUT,out)
record={'schema':'lesen-r9-v505-transport-evidence@1.0.0','date':'2026-11-07','source_r8_sha256':SHA_R8M,
'parent_runtime_r8_sha256':SHA_R8R,'r9_content_sha256':sha(R9_MASTER.read_bytes()),
'r9_runtime_sha256':sha(OUT.read_bytes()),'runtime_bytes':OUT.stat().st_size,'counts':counts,
'preserved_exact_runtime_entries':58,'changed_units':changed,'full_68_to_68_source_mapping':'PASS',
'integrity_entry_hash':out['integrity']['entries_sha256'],'integrity_payload_hash':out['integrity']['payload_sha256'],
'native_v505_validator':'SEPARATE_REQUIRED','native_browser_indexeddb':'NOT_RUN',
'full_source_nine_lens_grammar_engine':'NOT_RERUN','stage4':'HOLD','stage7':'NOT_RELEASED',
'no_installed_app_or_user_data_mutation':True}
write(EVIDENCE,record)
print(json.dumps(record,ensure_ascii=False,indent=2))