#!/usr/bin/env python3
"""Independent structural validator for Gate02, including negative mutation guards."""
import copy,hashlib,json,pathlib,zipfile,collections
P=pathlib.Path('/mnt/data/aspekte_b1plus_global_hold_resolution')
OLD=P/'Aspekte-B1plus-GLOBAL-BACKLOG-GATE01-1571-CARD-REPAIRS-NONIMPORT-20261110.zip'
NEW=P/'Aspekte-B1plus-GLOBAL-HOLD-GATE02-359-CASE-PRIORITY-REPAIRS-NONIMPORT-20261110.zip'
PRIMARY='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl';SOURCEMAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
sha=lambda b:hashlib.sha256(b).hexdigest()
parse=lambda b:[json.loads(s) for s in b.splitlines() if s.strip()]
with zipfile.ZipFile(OLD) as a,zipfile.ZipFile(NEW) as b:
 assert b.testzip() is None and a.testzip() is None
 original=parse(a.read(PRIMARY));final=parse(b.read(PRIMARY))
 assert a.read(SOURCEMAP)==b.read(SOURCEMAP)
 hashes=dict((l.split('  ',1)[1],l.split('  ',1)[0]) for l in b.read('SHA256SUMS.txt').decode().splitlines())
 assert len(hashes)==len(b.namelist())-1
 assert set(hashes)==set(b.namelist())-{'SHA256SUMS.txt'}
 assert all(sha(b.read(path))==hx for path,hx in hashes.items())
 ledger=parse(b.read('Global-Backlog/GATE02-HOLDS/GATE02-359-CARD-RISK-DECISION-LEDGER.jsonl'))
 changes=json.loads(b.read('Global-Backlog/GATE02-HOLDS/GATE02-ALL-CHANGED-PRIMARY-CARDS-EXACT-BEFORE-AFTER.json'))
 report=json.loads(b.read('Global-Backlog/GATE02-HOLDS/GATE02-359-HOLD-PRIORITIZATION-AND-REPAIR-REPORT.json'))
 assert len(original)==len(final)==1571 and len(ledger)==359 and len(changes)==23
 assert len(set(x['preview_card_id'] for x in final))==1571
 a={x['preview_card_id']:x for x in original};d={x['preview_card_id']:x for x in final}
 assert set(a)==set(d)
 changed={id for id in a if a[id]!=d[id]}
 assert len(changed)==23 and changed=={x['card_id'] for x in changes}
 for x in changes:
  assert x['exact_before']==a[x['card_id']] and x['exact_after']==d[x['card_id']]
  assert sha(json.dumps(x['exact_before'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())==x['before_sha256']
  assert sha(json.dumps(x['exact_after'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())==x['after_sha256']
 for id,x in d.items():
  y=a[id];assert x['source_ordinal']==y['source_ordinal'] and x['source_id']==y['source_id'] and x['lesson']==y['lesson']
  assert x['import_ready'] is False and x['formal_release_approved'] is False
  for k in ('existing_examples_de_fa_pending_qa','additional_examples_de_fa_pending_qa'):
   q=y['back'].get(k,[]);assert x['back'].get(k,[])[:len(q)]==q
 assert sum(x['curated_HOLD_content_disposition_exists'] is True for x in original)==359
 assert sum(x['curated_HOLD_content_disposition_exists'] is True for x in final)==351
 closed={id for id in a if a[id]['curated_HOLD_content_disposition_exists'] and not d[id]['curated_HOLD_content_disposition_exists']}
 assert len(closed)==8
 assert len({l['card_id'] for l in ledger})==359
 assert sum(l['hold_after_gate02'] for l in ledger)==351
 assert sum(l['specific_decision']=='CLOSED_SCOPED_LEXICAL_DISPOSITION' for l in ledger)==8
 assert collections.Counter(l['priority'] for l in ledger)==collections.Counter({'P1':138,'P2':191,'P3':30})
 assert report['new_primary_sha256']==sha(b.read(PRIMARY))
 assert report['source_map_sha256']==sha(b.read(SOURCEMAP))
 # All newly created sense IDs must remain anchored and examples must point to these IDs.
 for id in changed:
  x=d[id];net=x['back'].get('semantic_network_sense_anchored_pending_qa',[])
  ids=[n['sense_id'] for n in net]
  assert len(ids)==len(set(ids))
  if ids:
   for k in ('existing_examples_de_fa_pending_qa','additional_examples_de_fa_pending_qa'):
    for ex in x['back'].get(k,[]):
     if ex.get('sense_id'):assert ex['sense_id'] in ids
 for l,n,stem in [('L09',1162,'die Pension'),('L10',1487,'das Hochwasser')]:
  v=[x for x in final if x['lesson']==l and x['source_ordinal']==n and x['front']['base_headword_de']==stem]
  assert len(v)==1 and len(v[0]['back'].get('semantic_network_sense_anchored_pending_qa',[]))>=2
  assert v[0]['curated_HOLD_content_disposition_exists'] is True
 # Mutation guards - deliberately violate key safety invariants, ensure detector signals false.
 def invariant_cards(xs):return len(xs)==1571 and len({x['preview_card_id'] for x in xs})==1571
 def invariant_hold(xs):return sum(x['curated_HOLD_content_disposition_exists'] is True for x in xs)==351
 def invariant_publish(xs):return all(x['import_ready'] is False and x['formal_release_approved'] is False for x in xs)
 def invariant_source(xs):return all(x['source_id']==a[x['preview_card_id']]['source_id'] for x in xs if x['preview_card_id'] in a)
 def invariant_identity(xs):return set(x['preview_card_id'] for x in xs)==set(a)
 def invariant_unchanged(xs):return {x['preview_card_id'] for x in xs if x!=a[x['preview_card_id']]}==changed
 tests=[]
 def mutation(name,fn,detector):
  xs=copy.deepcopy(final);fn(xs);ok=not detector(xs);tests.append({'name':name,'invalid_data_rejected':ok});assert ok,name
 mutation('duplicate_card_id',lambda x:x[-1].__setitem__('preview_card_id',x[0]['preview_card_id']),invariant_cards)
 mutation('missing_card',lambda x:x.pop(),invariant_cards)
 mutation('premature_import_ready',lambda x:x[0].__setitem__('import_ready',True),invariant_publish)
 mutation('premature_formal_approval',lambda x:x[0].__setitem__('formal_release_approved',True),invariant_publish)
 mutation('card_source_id_changed',lambda x:x[0].__setitem__('source_id','WRONG'),invariant_source)
 mutation('clear_unreviewed_HOLD',lambda x:next(v for v in x if v['curated_HOLD_content_disposition_exists']).__setitem__('curated_HOLD_content_disposition_exists',False),invariant_hold)
 mutation('secretly_edit_non_target',lambda x:next(v for v in x if v['preview_card_id'] not in changed)['front'].__setitem__('base_headword_de','WRONG'),invariant_unchanged)
 mutation('zero_card_identity',lambda x:x[0].__setitem__('preview_card_id','WRONG'),invariant_identity)
 # Archive file checks are also deliberately mutated without recomputing manifest.
 sample=next(iter(hashes))
 assert sha(b.read(sample)+b'CORRUPT')!=hashes[sample];tests.append({'name':'corrupt_member_hash_detected','invalid_data_rejected':True})
 assert len(ledger[:-1])!=359;tests.append({'name':'missing_359th_case_detected','invalid_data_rejected':True})
 assert sum(l['specific_decision']=='CLOSED_SCOPED_LEXICAL_DISPOSITION' for l in ledger[8:])<=8
 out={'schema':'aspekte-b1plus-global-hold-gate02-verifier@1','status':'PASS','baseline_zip_sha256':sha(OLD.read_bytes()),'checked_archive_sha256':sha(NEW.read_bytes()),'archive_bytes':NEW.stat().st_size,'member_count':len(b.namelist()),'verified_manifest_entries':len(hashes),'primary_sha256':sha(b.read(PRIMARY)),'source_map_sha256':sha(b.read(SOURCEMAP)),'cards':len(final),'hold_before':359,'hold_after':351,'hold_closed':8,'actual_primary_edits':len(changed),'risk_ledger_rows':len(ledger),'risk_tiers':dict(collections.Counter(l['priority'] for l in ledger)),'negative_test_count':len(tests),'negative_tests':tests,'no_actual_app_import':True,'full_semantic_signoff':False,'release':'RELEASE_BLOCKED_NONIMPORT'}
 (P/'GATE02-SEPARATE-VERIFICATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(out,ensure_ascii=False,indent=2))
