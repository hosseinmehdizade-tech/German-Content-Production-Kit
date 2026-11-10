#!/usr/bin/env python3
"""Independent structural regression checker for Aspekte B1+ scoped P1 follow-up.
It checks real primary changes, stable identity, example routes and release safety,
not the truth of every German/Persian translation.
"""
import collections,copy,hashlib,json,pathlib,re,zipfile
P=pathlib.Path(__file__).parent
A=P/'Aspekte-B1plus-P1-SCOPED-131-HOLD-RESOLUTION-CURATED-NONIMPORT-20261110.zip'
B=P/'Aspekte-B1plus-P1-REMAINING83-SCOPED-CONTENT-REPAIRS-NONIMPORT-20261110.zip'
PRIMARY='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
EXPECTED_PARENT='d7550a83387b41d3f1efa61297b926c24fdca692ea8a8d5b5288743ef20d563d'
EXPECTED_MAP='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
SH=lambda b:hashlib.sha256(b).hexdigest()
loadl=lambda b:[json.loads(r) for r in b.decode('utf8').splitlines() if r.strip()]
assert SH(A.read_bytes())==EXPECTED_PARENT
with zipfile.ZipFile(A) as z:
 assert z.testzip() is None
 old=loadl(z.read(PRIMARY));orig_map=z.read(MAP)
with zipfile.ZipFile(B) as z:
 assert z.testzip() is None
 sha_lines=z.read('SHA256SUMS.txt').decode().splitlines()
 assert len(sha_lines)==len(z.namelist())-1
 assert len(z.namelist())==342
 for row in sha_lines:
  s,n=row.split('  ',1)
  assert SH(z.read(n))==s,(n,s)
 new=loadl(z.read(PRIMARY));actual_map=z.read(MAP)
 ledger=loadl(z.read('Global-Backlog/P1-REMAINING83/P1-83-CASE-DECISION-LEDGER.jsonl'))
 ledger359=loadl(z.read('Global-Backlog/P1-REMAINING83/P1-ALL-359-CURRENT-STATUS-LEDGER.jsonl'))
 closures=json.loads(z.read('Global-Backlog/P1-REMAINING83/P1-CASE-SCOPED-CLOSURES.json'))
 diffs=json.loads(z.read('Global-Backlog/P1-REMAINING83/P1-SUBSTANTIVE-EDIT-BEFORE-AFTER.json'))
 examples_new=json.loads(z.read('Global-Backlog/P1-REMAINING83/P1-NEW-DE-FA-EXAMPLES.json'))
 report=json.loads(z.read('Global-Backlog/P1-REMAINING83/P1-CONTENT-AND-RELEASE-REPORT.json'))

old_by={c['preview_card_id']:c for c in old}; new_by={c['preview_card_id']:c for c in new}
changeids={d['card_id'] for d in diffs};closureids={c['card_id'] for c in closures}
finite=re.compile(r'\b(?:Pflanzen|die|der|das|ein|eine)\s+(?:gehen|geht|laufen|läuft|wird|werden|steht|stehen|schreibt|schreiben)\b',re.I)

def collect_example(c):
 b=c['back'];return b.get('existing_examples_de_fa_pending_qa',[])+b.get('additional_examples_de_fa_pending_qa',[])

def current_check(cs,map_content,declared_changed=changeids,declared_closed=closureids,prior=old,check_example_preservation=True):
 assert SH(map_content)==EXPECTED_MAP
 assert len(cs)==len(prior)==1571
 assert len(set(c['preview_card_id'] for c in cs))==1571
 assert [(c['preview_card_id'],c['source_ordinal'],c['lesson'],c['source_id']) for c in cs]==[(c['preview_card_id'],c['source_ordinal'],c['lesson'],c['source_id']) for c in prior]
 current={c['preview_card_id']:c for c in cs}
 assert {c['preview_card_id'] for i,c in enumerate(cs) if c!=prior[i]}==declared_changed
 assert sum(c['curated_HOLD_content_disposition_exists'] for c in cs)==262
 assert sum(c['curated_HOLD_content_disposition_exists'] for c in prior)==303
 assert all(prior[i]['curated_HOLD_content_disposition_exists'] and not c['curated_HOLD_content_disposition_exists'] for i,c in enumerate(cs) if c['preview_card_id'] in declared_closed)
 assert {c['preview_card_id'] for c in cs if c['curated_HOLD_content_disposition_exists'] != prior[cs.index(c)]['curated_HOLD_content_disposition_exists']}==declared_closed
 assert all(not c['import_ready'] and not c['formal_release_approved'] and not c['back'].get('Formen_section') for c in cs)
 for c in cs:
  if c['preview_card_id'] not in declared_changed:continue
  ex=collect_example(c);nets=c['back'].get('semantic_network_sense_anchored_pending_qa') or []
  ids={n['sense_id'] for n in nets}
  assert len(ex)==len(set(e['de'].strip().lower() for e in ex))
  for e in ex:
   assert e.get('de','').strip() and e.get('fa','').strip()
   assert 'PENDING' in e.get('status','')
   if nets:
    assert e.get('sense_id') in ids
    assert all(s in ids for s in e.get('sense_ids',[]))
  for n in nets:
   for phrase in n.get('Kombinationen_DE_FA') or []:
    assert phrase.get('de') and phrase.get('fa')
    assert not finite.search(phrase['de']),phrase
 assert set(i for c in cs for i in c.get('linked_original_source_ordinals',[]) if isinstance(i,int))==set(range(1,1549))
 if check_example_preservation:
  for a,b in zip(prior,cs):
   before=collections.Counter((e['de'],e['fa']) for e in collect_example(a))
   after=collections.Counter((e['de'],e['fa']) for e in collect_example(b))
   removed=before-after
   assert (not removed) or (a['source_ordinal']==886 and len(removed)==1 and list(removed.keys())[0][0]=='Die Besucher schrieben einen Gruß ins Gästebuch.')
 assert sum(len(collect_example(c)) for c in cs)==3553

current_check(new,actual_map)
assert len(ledger)==83 and len(ledger359)==359
assert len(closures)==41 and len(diffs)==41 and len(examples_new)==14
assert sum(row['HOLD_after_P1_remaining83'] for row in ledger359)==262
assert sum(row['current_hold'] for row in ledger)==42
assert len(closureids)==41 and len(changeids)==41
assert not any(d['before']==d['after'] for d in diffs)
for d in diffs:
 id=d['card_id']
 assert d['before']==old_by[id] and d['after']==new_by[id]
 assert d['before_sha256']==SH((json.dumps(d['before'],ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode())
 assert d['after_sha256']==SH((json.dumps(d['after'],ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode())
assert SH(orig_map)==EXPECTED_MAP
assert report['new_primary_sha256']==SH(('\n'.join(json.dumps(c,ensure_ascii=False,sort_keys=True) for c in new)+'\n').encode())

def clone():return copy.deepcopy(new)

def reject(fn,label):
 try:
  cs,map_content,declared_changed,declared_closed=fn()
  current_check(cs,map_content,declared_changed,declared_closed)
 except (AssertionError,KeyError,TypeError,ValueError):return {'check':label,'rejected_invalid_mutation':True}
 raise AssertionError('FAIL: mutation escaped gates '+label)

checkcases=[
 ('duplicate_card_id',lambda:(duplicate_id(clone()),actual_map,changeids,closureids)),
 ('card_deleted',lambda:(clone()[:-1],actual_map,changeids,closureids)),
 ('source_ordinal_changed',lambda:(mutate_card(clone(),0,lambda c:c.__setitem__('source_ordinal',0)),actual_map,changeids,closureids)),
 ('outside_scope_card_changed',lambda:(mutate_card(clone(),0,lambda c:c['front'].__setitem__('base_headword_de','CORRUPTED')),actual_map,changeids,closureids)),
 ('hold_count_off',lambda:(mutate_card_id(clone(),next(iter(closureids)),lambda c:c.__setitem__('curated_HOLD_content_disposition_exists',True)),actual_map,changeids,closureids)),
 ('early_formal_release',lambda:(mutate_card(clone(),0,lambda c:c.__setitem__('formal_release_approved',True)),actual_map,changeids,closureids)),
 ('early_import_approval',lambda:(mutate_card(clone(),0,lambda c:c.__setitem__('import_ready',True)),actual_map,changeids,closureids)),
 ('bad_DE_example',lambda:(mutate_card_id(clone(),next(iter(closureids)),lambda c:collect_example(c)[0].__setitem__('de','')),actual_map,changeids,closureids)),
 ('bad_FA_example',lambda:(mutate_card_id(clone(),next(iter(closureids)),lambda c:collect_example(c)[0].__setitem__('fa','')),actual_map,changeids,closureids)),
 ('unknown_sense_route',lambda:(mutate_card_id(clone(),'AB1P-EFFECTIVE-QA-PASS02-0363',lambda c:collect_example(c)[0].__setitem__('sense_id','NOT_AN_ID')),actual_map,changeids,closureids)),
 ('duplicate_DE_in_card',lambda:(mutate_card_id(clone(),'AB1P-EFFECTIVE-QA-PASS02-0363',lambda c:c['back']['additional_examples_de_fa_pending_qa'].append(copy.deepcopy(collect_example(c)[0]))),actual_map,changeids,closureids)),
 ('finite_clause_as_collocation',lambda:(mutate_card_id(clone(),'AB1P-EFFECTIVE-QA-PASS02-0078',lambda c:c['back']['semantic_network_sense_anchored_pending_qa'][2]['Kombinationen_DE_FA'].append({'de':'Pflanzen gehen ein','fa':'گیاهان می‌میرند'})),actual_map,changeids,closureids)),
 ('back_duplicated_forms',lambda:(mutate_card_id(clone(),next(iter(closureids)),lambda c:c['back'].__setitem__('Formen_section','unwanted')),actual_map,changeids,closureids)),
 ('source_map_changed',lambda:(clone(),actual_map+b'corruption',changeids,closureids)),
 ('unaccounted_changed_card',lambda:(mutate_card_id(clone(),'AB1P-EFFECTIVE-QA-PASS02-0081',lambda c:c['front'].__setitem__('display_de_provisional','changed')),actual_map,changeids,closureids)),
 ('pending_to_pass',lambda:(mutate_card_id(clone(),'AB1P-EFFECTIVE-QA-PASS02-0363',lambda c:collect_example(c)[0].__setitem__('status','PASS_FULL_APPROVAL')),actual_map,changeids,closureids)),
]

def mutate_card(cs,index,edit):edit(cs[index]);return cs

def mutate_card_id(cs,cid,edit):
 edit(next(c for c in cs if c['preview_card_id']==cid));return cs

def duplicate_id(cs):cs[1]['preview_card_id']=cs[0]['preview_card_id'];return cs

result=[]
for label,fn in checkcases:result.append(reject(fn,label))
assert len(result)==16
out={'schema':'aspekte-b1plus-P1-remaining83-independent-structural-verification@1','date':'2026-11-10',
 'status':'PASS','parent_sha256':EXPECTED_PARENT,'new_owner_sha256':SH(B.read_bytes()),
 'new_primary_sha256':SH(('\n'.join(json.dumps(c,ensure_ascii=False,sort_keys=True) for c in new)+'\n').encode()),
 'source_map_sha256':SH(actual_map),'total_learner_card_objects':1571,'changed_primary_card_objects':41,
 'untouched_card_objects':1530,'P1_cases_screened':83,'scoped_HOLDs_closed':41,'global_HOLDs_remaining':262,
 'P1_remaining':42,'P2_remaining':190,'P3_remaining':30,'existing_examples_preserved_except_one_FA_translation_correction':True,
 'new_example_pairs':14,'total_example_pairs':3553,
 'manifest_entries_verified':len(sha_lines),'archive_members':len(sha_lines)+1,'ZIP_CRC':'PASS',
 'full_before_after_objects_verified':True,'negative_mutation_tests_passed':len(result),'negative_mutation_tests_total':len(result),
 'mutations':result,'real_app_import_tested':False,'full_language_approval':False,'release':'RELEASE_BLOCKED_NONIMPORT'}
(P/'P1-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k in ['status','new_owner_sha256','new_primary_sha256','total_learner_card_objects','changed_primary_card_objects','untouched_card_objects','scoped_HOLDs_closed','global_HOLDs_remaining','negative_mutation_tests_passed','total_example_pairs']},ensure_ascii=False,indent=2))
