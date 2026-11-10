#!/usr/bin/env python3
"""Separate structural verifier for B1+ L10 Phase2; no publisher reset and no release signoff.
Run: python verify_L10_phase2_v1.py PARENT.zip NEW.zip [OUT.json]
"""
import collections,copy,hashlib,json,re,sys,zipfile
from pathlib import Path
PARENT='0ac34c8178984511d28d4400ff5efe56036d8c8f31aca0d85c1e70f4661a0054'
SOURCE='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
def sha(d):return hashlib.sha256(d).hexdigest()
def norm(x):return re.sub(r'\W+','',str(x).casefold(),flags=re.U)
def ex(c):
 b=c['back'];return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
def nets(c):return c['back'].get('semantic_network_sense_anchored_pending_qa') or []
def combos(c):return [p for n in nets(c) for p in n.get('Kombinationen_DE_FA') or []]
def files(p):
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None,'ZIP_CRC_INVALID'
  manifest={k:d for d,k in (line.split('  ',1) for line in z.read('SHA256SUMS.txt').decode().splitlines())}
  assert len(manifest)==len(z.namelist())-1,'ZIP_MANIFEST_INCOMPLETE'
  assert all(sha(z.read(k))==d for k,d in manifest.items()),'ZIP_MANIFEST_HASH_FAILED'
  return {k:z.read(k) for k in z.namelist() if k!='SHA256SUMS.txt'}
def check(before,after):
 assert len(before)==len(after)==1571,'CARD_COUNT'
 assert [c['preview_card_id'] for c in before]==[c['preview_card_id'] for c in after],'CARD_ID_OR_ORDER'
 assert len({c['preview_card_id'] for c in after})==1571,'DUPLICATE_CARD_ID'
 non=[(b,a) for b,a in zip(before,after) if b['lesson']!='L10']
 lesson=[c for c in after if c['lesson']=='L10']
 assert len(non)==1363 and len(lesson)==208,'LESSON_BOUNDARY'
 assert all(b==a for b,a in non),'NON_L10_EDIT'
 assert sum(b!=a for b,a in zip(before,after) if b['lesson']=='L10')==208,'NO_ACTUAL_PRIMARY_EDIT'
 assert all(not c.get('formal_release_approved') and not c.get('import_ready') for c in lesson),'PREMATURE_RELEASE'
 assert sum(c.get('curated_HOLD_content_disposition_exists') is True for c in lesson)==46,'HOLD_LOST'
 assert all(not c['back'].get('Formen_section') for c in lesson),'FORMS_DUPLICATED_BACK'
 assert all(c['front'].get('forms_rendered_on_front_only') for c in lesson),'FORMS_NOT_FRONT_ONLY'
 assert all(len(nets(c))>0 for c in lesson),'WORTNETZ_MISSING'
 assert sum(len(nets(c)) for c in lesson)==253,'SENSE_BLOCK_COUNT'
 assert sum(len(combos(c)) for c in lesson)==288,'COMBINATIONS_COUNT'
 assert sum(len(ex(c)) for c in lesson)==457,'BILINGUAL_EXAMPLE_COUNT'
 finite={'veröffentlicht','bewertet','begrüßt','trocknet','entscheidet','läuft','arbeitet','reicht','zeigt'}
 determ={'der','die','das','eine','ein','einen','einem','einer'}
 for c in lesson:
  ids=[n['sense_id'] for n in nets(c)]
  assert len(ids)==len(set(ids)) and all(ids),'SENSE_ID_DUPLICATES'
  de_seen=set()
  for e in ex(c):
   assert str(e.get('de','')).strip() and str(e.get('fa','')).strip(),'EMPTY_DE_FA'
   assert e.get('status') and e.get('status')!='PASS','STATUSLESS_OR_AUTO_APPROVED'
   assert e.get('sense_id') in ids,'EXAMPLE_SENSE_NOT_IN_NETWORK'
   n=norm(e['de']);assert n not in de_seen,'DUPLICATE_DE_EXAMPLE';de_seen.add(n)
  for n in nets(c):
   assert n.get('sense_de') and n.get('sense_fa'),'MISSING_DE_FA_SENSE'
   for p in n.get('Kombinationen_DE_FA') or []:
    assert str(p.get('de','')).strip() and str(p.get('fa','')).strip(),'EMPTY_DE_FA_COLLOCATION'
    assert not p['de'].endswith(('.','?','!')),'COLLOCATION_PUNCTUATION'
    w=re.findall(r'\w+',p['de'])
    assert not (len(w)>=4 and w[0].casefold() in determ and w[1][0].isupper() and w[2] in finite),'FINITE_CLAUSE_IN_L10_COMBINATIONS'
 return True

def run(parent_path,new_path):
 assert sha(parent_path.read_bytes())==PARENT
 a=files(parent_path);b=files(new_path)
 assert a[MAP]==b[MAP] and sha(b[MAP])==SOURCE,'SOURCE_MAPPING_MODIFIED'
 original=[json.loads(x) for x in a[MAIN].splitlines()]
 updated=[json.loads(x) for x in b[MAIN].splitlines()]
 check(original,updated)
 ledger=[json.loads(x) for x in b['Lessons/L10/L10-PHASE2-ALL-208-CARD-DISPOSITIONS.jsonl'].splitlines()]
 changes=json.loads(b['Lessons/L10/L10-PHASE2-ALL-208-CARD-BEFORE-AFTER.json'])
 routes=[json.loads(x) for x in b['Lessons/L10/L10-PHASE2-ALL-457-EXAMPLE-SENSE-ROUTES.jsonl'].splitlines()]
 assert len(ledger)==len(changes)==208 and len(routes)==457,'EVIDENCE_LEDGER_COVERAGE'
 cmap={c['preview_card_id']:c for c in updated if c['lesson']=='L10'}
 pmap={c['preview_card_id']:c for c in original if c['lesson']=='L10'}
 for r in changes:
  cid=r['preview_card_id'];assert r['before']==pmap[cid] and r['after']==cmap[cid],'EVIDENCE_BEFORE_AFTER_NOT_PRIMARY'
  assert sha(json.dumps(r['before'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())==r['before_sha256']
  assert sha(json.dumps(r['after'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())==r['after_sha256']
 for v in routes:
  c=cmap[v['preview_card_id']];assert any(e['de']==v['de'] and e['fa']==v['fa'] and e['sense_id']==v['assigned_sense_id'] for e in ex(c))
 tests={}
 def should_reject(name,mutation):
  q=copy.deepcopy(updated)
  mutation(q)
  try:check(original,q)
  except AssertionError:tests[name]='PASS_REJECTED'
  else:tests[name]='FAIL_ACCEPTED_INVALID'
 # Multiple intentionally invalid cases, each checked against the same unmodified valid baseline.
 should_reject('duplicate_card_ID',lambda q:q[-1].update(preview_card_id=q[-2]['preview_card_id']))
 should_reject('different_other_lesson',lambda q:q[0].update(import_ready=True))
 should_reject('premature_release',lambda q:next(c for c in q if c['lesson']=='L10').update(formal_release_approved=True))
 should_reject('missing_L10_card',lambda q:q.pop(-1))
 should_reject('statusless_DE_FA',lambda q:next(c for c in q if c['lesson']=='L10')['back']['existing_examples_de_fa_pending_qa'][0].pop('status'))
 should_reject('empty_FA',lambda q:next(c for c in q if c['lesson']=='L10')['back']['existing_examples_de_fa_pending_qa'][0].update(fa=''))
 should_reject('unknown_sense_ID',lambda q:next(c for c in q if c['lesson']=='L10')['back']['existing_examples_de_fa_pending_qa'][0].update(sense_id='INVALID'))
 should_reject('duplicate_example',lambda q:next(c for c in q if c['lesson']=='L10')['back']['existing_examples_de_fa_pending_qa'].append(copy.deepcopy(next(c for c in q if c['lesson']=='L10')['back']['existing_examples_de_fa_pending_qa'][0])))
 should_reject('finite_clause_collocation',lambda q:next(c for c in q if c['lesson']=='L10')['back']['semantic_network_sense_anchored_pending_qa'][0]['Kombinationen_DE_FA'].append({'de':'die Forscherin veröffentlicht Ergebnisse','fa':'پژوهشگر نتایج را منتشر می‌کند'}))
 should_reject('forms_back_reintroduced',lambda q:next(c for c in q if c['lesson']=='L10')['back'].update(Formen_section='Wiederholte Formen'))
 should_reject('HOLD_removed',lambda q:next(c for c in q if c['lesson']=='L10' and c['curated_HOLD_content_disposition_exists']).update(curated_HOLD_content_disposition_exists=False))
 assert all(v=='PASS_REJECTED' for v in tests.values()),('REGRESSION_NEGATIVE_FAIL',tests)
 return {'schema':'aspekte-b1plus-l10-phase2-separate-verifier@1','status':'STRUCTURAL_PASS_RELEASE_BLOCKED_NONIMPORT','valid_parent_sha256':sha(parent_path.read_bytes()),'verified_new_owner_sha256':sha(new_path.read_bytes()),'verified_primary_sha256':sha(b[MAIN]),'verified_member_hash_count':len(b),'zip_CRC':'PASS','primary_card_diff_count':208,'non_L10_objects_unchanged':1363,'all_1548_source_map_bytes_identical':True,'negative_mutation_test_count':len(tests),'negative_mutation_tests':tests,'example_routes':457,'before_after_full_objects':208,'future_phase3_full_semantic_QA':'PENDING','actual_live_app_import':'NOT_TESTED','current_release':'BLOCKED_NONIMPORT'}
if __name__=='__main__':
 p=Path(sys.argv[1]);n=Path(sys.argv[2]);result=run(p,n)
 t=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 if len(sys.argv)>3:Path(sys.argv[3]).write_text(t,encoding='utf-8')
 print(t)
