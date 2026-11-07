#!/usr/bin/env python3
"""Exact R9->R10 bounded source-aware runtime delta; no installed-user data."""
import hashlib,json,copy,pathlib,importlib.util,collections
P=pathlib.Path('/mnt/data/lesen_r10_20261107')
R9M=pathlib.Path('/mnt/data/lesen_r9_20261107/Lesen-Production-Master-v1.3.0-R9-10P04-TRILINGUAL-CANDIDATE.json')
R9R=pathlib.Path('/mnt/data/lesen_r9_20261107/Lesen-R9-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json')
R10M=P/'Lesen-Production-Master-v1.3.0-R10-10P04-TRILINGUAL-CANDIDATE.json'
OUT=P/'Lesen-R10-v505-10P04-RUNTIME-PREENTRY-CANDIDATE.json'
RECORD=P/'LESEN-R10-RUNTIME-TRANSPORT-EVIDENCE.json'
M_PIN='52667254d47987e5f4c4146078fd2c8204e80152de3268cd0eb599fc0c2f8171'
R_PIN='115a988c339f6fa392091727a7aab10f4456d6b7e04e7678492867e785e5aa59'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(R9M.read_bytes())==M_PIN and sha(R9R.read_bytes())==R_PIN
modspec=importlib.util.spec_from_file_location('reading_mapper','/mnt/data/lesen_r4_workspace/build_lesen_r3_runtime_candidate.py')
mapper=importlib.util.module_from_spec(modspec);modspec.loader.exec_module(mapper)
a=json.loads(R9M.read_text());b=json.loads(R9R.read_text());c=json.loads(R10M.read_text());d=copy.deepcopy(b)
assert sha(canon(b['entries']))==b['integrity']['entries_sha256']
assert sha(canon({k:v for k,v in b.items() if k!='integrity'}))==b['integrity']['payload_sha256']
assert len(a['items'])==len(b['entries'])==len(c['items'])==68
changed=[]
for i,(old,new,entry) in enumerate(zip(a['items'],c['items'],b['entries'])):
    assert old['id']==new['id']==entry['source_item_id']
    mapper.verify_section_mapping(old,entry)
    diffs={k for k in old if old[k]!=new[k]}
    if 21<=i+1<=30:
        assert diffs=={'reading','grammar','quality'},(i,diffs)
        assert old['reading']['sections'][:3]==new['reading']['sections'][:3]
        assert old['reading']['sections'][4:]==new['reading']['sections'][4:]
        assert old['reading']['sections'][3]['sentences'][1]==new['reading']['sections'][3]['sentences'][1]
        assert old['questions']==new['questions']
        d['entries'][i]=mapper.apply_fields(old,new,entry)
        changed.append(old['id'])
    else:
        assert diffs==set(),(i,diffs)
        assert d['entries'][i]==entry
    mapper.verify_section_mapping(new,d['entries'][i])
assert changed==[f'LES-PRES-{i:03d}' for i in range(21,31)]
counts={'entries':68,'reading_units':68,
        'passages':sum(len(x['unit']['passages']) for x in d['entries']),
        'exercises':sum(len(x['exercises']) for x in d['entries']),
        'vocabulary_entries':sum(len(x['unit']['r38']['vocabulary']) for x in d['entries']),
        'curated_grammar':sum(len(x['unit']['r38']['grammar']['curated_annotations']) for x in d['entries']),
        'full_text_grammar':sum(len(x['unit']['r38']['grammar']['full_text_occurrences']) for x in d['entries'])}
assert counts=={'entries':68,'reading_units':68,'passages':478,'exercises':340,'vocabulary_entries':350,'curated_grammar':669,'full_text_grammar':4520},counts
d['counts']=counts
d['compiled_from']={'schema_version':c['schema_version'],'pack_id':c['pack_id'],'content_version':c['content_version'],'sha256':sha(R10M.read_bytes())}
d['compiler']={'id':'lesen-r10-10p04-trilingual-bounded-delta-v1','deterministic':True,'runtime_analysis_required':False,
               'contract':'R9 verified preentry runtime + 10 edited p04 source sections, translations and scoped grammar',
               'note':'Deterministic source-specific projection, not original nine-lens producer nor native browser import.'}
d['candidate_review']={'status':'R10_PREENTRY_ONLY_STAGE4_6_7_HOLD','changed_unit_ids':changed,
                        'changed_section_ids':['p04'],'changed_sentences_per_unit':['p04-s01','p04-s03'],
                        'unchanged_p04_s02_all_ten':True,'independent_stage4':'HOLD',
                        'grammar_source_engine_rerun':False,'browser_indexeddb_stage6':'NOT_RUN',
                        'fulltext_grammar_count_after':counts['full_text_grammar'],
                        'parent_r9_runtime_sha256':R_PIN,'curated_current':'UNCHANGED'}
d['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(d['entries']))}
d['integrity']['payload_sha256']=sha(canon({k:v for k,v in d.items() if k!='integrity'}))
write(OUT,d)
evidence={'schema':'lesen-r10-v505-runtime-transport@1.0.0','date':'2026-11-07','r9_content_sha256':M_PIN,
          'r9_runtime_sha256':R_PIN,'r10_content_sha256':sha(R10M.read_bytes()),
          'r10_runtime_sha256':sha(OUT.read_bytes()),'runtime_bytes':OUT.stat().st_size,'counts':counts,
          'unchanged_exact_entries':58,'changed_unit_ids':changed,
          'integrity_entries':d['integrity']['entries_sha256'],'integrity_payload':d['integrity']['payload_sha256'],
          'native_v505_validator':'SEPARATE_REQUIRED','browser_stage6':'NOT_RUN',
          'full_nine_lens_grammar_source':'NOT_RERUN','independent_stage4':'HOLD',
          'curated_current':'UNCHANGED','no_user_srs_fsrs_or_app_change':True}
write(RECORD,evidence)
print(json.dumps(evidence,ensure_ascii=False,indent=2))