#!/usr/bin/env python3
"""Separate deterministic structural and regression test for L09 Phase2 owner; not a human semantic reviewer."""
import copy,hashlib,json,re,zipfile,collections
from pathlib import Path
OUT=Path('/mnt/data/aspekte_b1plus_l09_phase2')
P=OUT/'Aspekte-B1plus-L09-PHASE2-WHOLE-185-CARDS-CURATED-NONIMPORT-20261109.zip'
OLD=Path('/mnt/data/aspekte_b1plus_l09_phase1/Aspekte-B1plus-L08-PHASE3-157-CARD-QUALITY-GATE-RELEASE-BLOCKED-NONIMPORT-20261109.zip')
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
def sha(x):return hashlib.sha256(x).hexdigest()
def ex(c):return c['back'].get('existing_examples_de_fa_pending_qa',[])+c['back'].get('additional_examples_de_fa_pending_qa',[])
def net(c):return c['back'].get('semantic_network_sense_anchored_pending_qa') or []
def check(cs,baseline):
 if len(cs)!=1571 or len(set(c['preview_card_id'] for c in cs))!=1571 or set(c['preview_card_id'] for c in cs)!=set(c['preview_card_id'] for c in baseline):return 'CARD_IDENTITY'
 for a,b in zip(cs,baseline):
  if a['preview_card_id']!=b['preview_card_id']:return 'CARD_ORDER'
  if a['lesson']!='L09' and a!=b:return 'OTHER_LESSON_MUTATION'
 l=[c for c in cs if c['lesson']=='L09']
 if len(l)!=185:return 'L09_CARD_COUNT'
 if sum(bool(c.get('curated_HOLD_content_disposition_exists')) for c in l)!=43:return 'HOLD_LOST'
 for c in l:
  if c['import_ready'] or c['formal_release_approved']:return 'PREMATURE_RELEASE'
  if c['back'].get('Formen_section') is not None:return 'BACK_FORMEN_DUPLICATE'
  ee=ex(c)
  if not ee:return 'MISSING_EXAMPLES'
  if any(not e.get('status') or not e.get('de') or not e.get('fa') for e in ee):return 'EXAMPLE_BLANK_OR_STATUS_MISSING'
  if len({re.sub(r'\W+','',e['de'].casefold()) for e in ee})!=len(ee):return 'DUPLICATE_EXAMPLE'
  nn=net(c)
  if nn and any(e.get('sense_id') not in {n['sense_id'] for n in nn} for e in ee):return 'ORPHAN_EXAMPLE_SENSE_ID'
  for n in nn:
   for k in n.get('Kombinationen_DE_FA',[]):
    de=k.get('de','').strip();fa=k.get('fa','').strip()
    if not de or not fa:return 'BAD_COMBINATION'
    if de.endswith(('.', '!', '?')):return 'FULL_SENTENCE_IN_COMBINATION'
    if re.search(r'\b(?:geht|läuft|kommt|hat|ist|sind|gibt|macht|kann|wird)\b',de,re.I):return 'FINITE_COMBINATION'
 return 'PASS'
with zipfile.ZipFile(P) as z:
 assert z.testzip() is None
 manifest={n:s for s,n in (x.split('  ',1) for x in z.read('SHA256SUMS.txt').decode().splitlines())}
 assert set(manifest)==set(z.namelist())-{'SHA256SUMS.txt'}
 assert all(sha(z.read(n))==s for n,s in manifest.items())
 cards=[json.loads(x) for x in z.read(MAIN).splitlines()]
 source_map=z.read(MAP)
with zipfile.ZipFile(OLD) as z:
 baseline=[json.loads(x) for x in z.read(MAIN).splitlines()]
 assert z.read(MAP)==source_map
assert check(cards,baseline)=='PASS'
assert sum(len(ex(c)) for c in cards if c['lesson']=='L09')==423
assert sum(sum(len(n.get('Kombinationen_DE_FA',[])) for n in net(c)) for c in cards if c['lesson']=='L09')==237
assert sum(len(net(c))>0 for c in cards if c['lesson']=='L09')==182
muts=[]
def run(name,mut,expected):
 a=copy.deepcopy(cards)
 mut(a)
 got=check(a,baseline)
 assert got==expected,(name,got,expected)
 muts.append({'name':name,'expected_detection':expected,'actual_detection':got,'result':'PASS'})
def first(a):return next(c for c in a if c['lesson']=='L09' and c['source_ordinal']==1157)
run('reject_premature_release',lambda a:first(a).__setitem__('import_ready',True),'PREMATURE_RELEASE')
run('reject_back_formen',lambda a:first(a)['back'].__setitem__('Formen_section','x'),'BACK_FORMEN_DUPLICATE')
run('reject_missing_example_status',lambda a:ex(first(a))[0].pop('status'), 'EXAMPLE_BLANK_OR_STATUS_MISSING')
run('reject_intra_card_duplicate',lambda a:first(a)['back']['additional_examples_de_fa_pending_qa'].append(copy.deepcopy(ex(first(a))[0])),'DUPLICATE_EXAMPLE')
run('reject_wrong_sense_link',lambda a:ex(first(a))[0].__setitem__('sense_id','NONEXISTENT'), 'ORPHAN_EXAMPLE_SENSE_ID')
run('reject_full_sentence_combination',lambda a:net(first(a))[0]['Kombinationen_DE_FA'][0].__setitem__('de','Der Tourist ist hier.'),'FULL_SENTENCE_IN_COMBINATION')
run('reject_mutation_other_lesson',lambda a:next(c for c in a if c['lesson']=='L08')['front'].__setitem__('base_headword_de','BROKEN'),'OTHER_LESSON_MUTATION')
run('reject_lost_hold',lambda a:first(a).__setitem__('curated_HOLD_content_disposition_exists',False),'HOLD_LOST')
run('reject_renamed_card_id',lambda a:first(a).__setitem__('preview_card_id','WRONG'),'CARD_IDENTITY')
receipt={'schema':'aspekte-b1plus-l09-phase2-separate-structural-regressions@1','source_archive_sha256':sha(P.read_bytes()),'all_185_card_structural_positive_check':'PASS','negative_synthetic_checks':muts,'negative_pass_count':len(muts),'limitations':'These are structural and identity checks; cannot prove naturalness or exact semantic translations. App importer not exercised.'}
(OUT/'L09-PHASE2-STRICT-REGRESSIONS.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'zipsha':receipt['source_archive_sha256'],'positive':'PASS','negative_pass':len(muts),'checks':[m['name'] for m in muts]},ensure_ascii=False,indent=2))