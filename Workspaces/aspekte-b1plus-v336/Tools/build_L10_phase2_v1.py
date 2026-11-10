#!/usr/bin/env python3
"""Aspekte B1+ L10 Phase2: all 208 current learner cards; true primary editing.
Reproducible, SHA-pinned input only. German/Persian pair proposals remain pending case QA.
Run: python build_L10_phase2_v1.py OWNER.zip MANUAL_TSV OUTPUT_DIR
"""
from __future__ import annotations
import collections, copy, csv, hashlib, html, io, json, re, sys, zipfile
from pathlib import Path

DATE='2026-11-10'
OWNER_SHA='0ac34c8178984511d28d4400ff5efe56036d8c8f31aca0d85c1e70f4661a0054'
OWNER_PRIMARY_SHA='7eef147f679fec8dea922fefe4a350fafc059277dcfa3a8664c93d1ceddf5e33'
SOURCE_MAP_SHA='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
ROOT='Lessons/L10/'
STATUS='PENDING_L10_PHASE3_CASE_LEVEL_DE_FA_QA'
SENSE_STATUS='PENDING_L10_PHASE3_SENSE_SPECIFIC_SEMANTIC_QA'

# All multi-meaning routes are explicit, based on actual examples in the SHA-pinned source.
# Key is current source_ordinal; values are 1-based net order, in existing+additional example order.
ROUTES={
 1347:[1,2,2],1352:[1,2,2],1353:[1,2,1],1360:[2,1],1364:[2,1,2],
 1377:[1,2,1,1,1],1408:[2,2,2],1417:[1,2,2],1422:[1,1],1430:[1,1,3,2],
 1424:[1,1],1433:[1,2],1435:[1,1,1],1443:[1,2,1,2,2],1444:[1,2],1445:[2,3,4,4],1448:[3,1,3],
 1449:[3,1,3],1471:[1,2,1],1477:[1,2],1481:[2,2],1484:[1,1,1],
 1485:[2,1],1510:[1,1],1512:[1,2],1515:[1,1,1],1518:[1,2],
 1520:[1,1,1],1523:[2,1],1527:[1,1,2,2],1533:[1,1,2],1535:[1,1,2,2],
 1542:[1,1,2,2],1543:[1,2],1548:[2,1]
}
# The rest of the legacy multiple-net cards have two example-level routes, established below.
ROUTES.update({1521:[1,1],1539:[1,1]})

# Existing structural false friends: FULL CLAUSES must not appear as 'Kombinationen'.
FINITE_FIXES={
 (1387,'eine Forscherin veröffentlicht Ergebnisse'):("Forschungsergebnisse veröffentlichen","نتایج پژوهش را منتشر کردن"),
 (1398,'die Umweltexpertin bewertet die Folgen'):("die Folgen fachlich bewerten","پیامدها را به‌صورت کارشناسی ارزیابی کردن"),
 (1439,'der Talkmaster begrüßt seine Gäste'):("Gäste begrüßen","به مهمانان خوشامد گفتن"),
 (1485,'die Haut trocknet aus'):("die Haut austrocknen","پوست را خشک کردن"),
 (1485,'ein Gewässer trocknet aus'):("ohne Regen austrocknen","بدون باران خشک شدن"),
}
# Distinct, genuinely useful finite-clause examples moved into the Beispiele zone.
EXTRA_EXAMPLES={
 1387:[('Eine Forscherin veröffentlicht ihre Forschungsergebnisse.','یک پژوهشگر زن نتایج پژوهش خود را منتشر می‌کند.',1)],
 1398:[('Die Umweltexpertin bewertet die Folgen der Dürre.','کارشناس زن محیط زیست پیامدهای خشکسالی را ارزیابی می‌کند.',1)],
 1485:[('Bei großer Hitze trocknet die Haut schnell aus.','در گرمای شدید پوست به‌سرعت خشک می‌شود.',1),
       ('In langen Dürreperioden trocknen Gewässer aus.','در دوره‌های طولانی خشکسالی پهنه‌های آبی خشک می‌شوند.',1)],
}
# Reference forms are checked in Duden for these *scoped* entries; no full-card signoff.
FORM_EVIDENCE={
 1352:{'scope':'trennbar, lässt an / ließ an / hat angelassen; meanings of Motor, Kleidung, eingeschaltet lassen','url':'https://www.duden.de/rechtschreibung/anlassen'},
 1377:{'scope':'intr. ist verbrannt, trans. hat verbrannt, reflexive hat; meaning-specific auxiliary','url':'https://www.duden.de/rechtschreibung/verbrennen'},
 1443:{'scope':'trennbar, redet aus / redete aus / hat ausgeredet; jemanden ausreden lassen; jemandem etwas ausreden','url':'https://www.duden.de/rechtschreibung/ausreden'},
 1424:{'scope':'fügt zu / fügte zu / hat zugefügt; both harm and addition senses are recorded','url':'https://www.duden.de/rechtschreibung/zufuegen'},
 1435:{'scope':'Kleider is plural of das Kleid and also generic clothing; sense distinction','url':'https://www.duden.de/rechtschreibung/Kleid'},
 1445:{'scope':'ergreift / ergriff / hat ergriffen; hand, Wort, initiative and emotional sense','url':'https://www.duden.de/rechtschreibung/ergreifen'},
 1448:{'scope':'hält an / hielt an / hat angehalten; car stop, continuation and jemanden zu etwas anhalten','url':'https://www.duden.de/rechtschreibung/anhalten'},
 1485:{'scope':'trennbar, trocknet aus / trocknete aus; intr. ist / trans. hat ausgetrocknet','url':'https://www.duden.de/rechtschreibung/austrocknen'},
}


def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def pretty(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def norm(x):return re.sub(r'\W+','',str(x).casefold(),flags=re.U)
def examples(c):
 b=c['back'];return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
def nets(c):return c['back'].get('semantic_network_sense_anchored_pending_qa') or []
def all_collocs(c):return [d for n in nets(c) for d in n.get('Kombinationen_DE_FA',[])]

def read_owner(path):
 raw=path.read_bytes();assert sha(raw)==OWNER_SHA,'PARENT_ARCHIVE_SHA_MISMATCH'
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  assert z.testzip() is None,'PARENT_ZIP_CRC_ERROR'
  entries={k:z.read(k) for k in z.namelist() if k!='SHA256SUMS.txt'}
  mani={name:digest for digest,name in (line.split('  ',1) for line in z.read('SHA256SUMS.txt').decode().splitlines() if line)}
  assert set(entries)==set(mani),'PARENT_ZIP_MANIFEST_NAMES_DIFFER'
  assert all(sha(b)==mani[n] for n,b in entries.items()),'PARENT_MANIFEST_HASHES_INVALID'
  assert sha(entries[MAIN])==OWNER_PRIMARY_SHA,'PARENT_PRIMARY_SHA_MISMATCH'
  assert sha(entries[MAP])==SOURCE_MAP_SHA,'PARENT_SOURCE_MAP_SHA_MISMATCH'
  lines=entries[MAIN].splitlines(keepends=True)
  assert len(lines)==1571
  cards=[json.loads(line) for line in lines]
  return entries,lines,cards

def manual_map(path,cards):
 rows=list(csv.DictReader(path.open(encoding='utf-8'),delimiter='|'))
 assert rows and set(rows[0])=={'key','sense_de','sense_fa','collocation_de','collocation_fa'},'MANUAL_TSV_SCHEMA_ERROR'
 out=collections.defaultdict(list)
 for r in rows:
  assert all(v and v.strip() for v in r.values()),('EMPTY_LEXICAL_CELL',r)
  assert not any(r['collocation_de'].rstrip().endswith(x) for x in ('.','!','?')),'SENTENCE_PUNCTUATION_IN_COLLOCATION'
  out[r['key']].append(r)
 no_nets=[c for c in cards if c.get('lesson')=='L10' and not nets(c)]
 def key(c):
  if c['source_ordinal'] in (1487,1494):return f"{c['source_ordinal']}:{c['front']['base_headword_de']}"
  return str(c['source_ordinal'])
 expected={key(c) for c in no_nets}
 assert len(no_nets)==178 and set(out)==expected,('MISSING_OR_UNEXPECTED_LEXICAL_ROWS',sorted(expected-set(out)),sorted(set(out)-expected))
 assert len(rows)==212,('UNEXPECTED_SENSE_BLOCK_COUNT',len(rows))
 return out,key

def new_net(c,r,sense_seq):
 return {
  'sense_id':f"{c['preview_card_id']}:L10P2:S{sense_seq}",
  'sense_de':r['sense_de'], 'sense_fa':r['sense_fa'],
  'Kombinationen_DE_FA':[{'de':r['collocation_de'],'fa':r['collocation_fa'],'status':STATUS,'editorial_origin':'L10_PHASE2_MANUAL_CONTEXT_SPECIFIC_LEXICAL_REWRITE'}],
  'Synonyme':[],'Antonyme':[],'Verwandte_Woerter_KEINE_Synonyme':[],'Wortfamilie':[],
  'lexical_relation_policy':'ONLY_VERIFIED_SENSE_SPECIFIC_RELATIONS__EMPTY_IF_NOT_EVIDENCED',
  'source':'L10_PHASE2_MANUAL_SENSE_SPECIFIC_EDITORIAL_FROM_CURRENT_CURATED_CARD',
  'status':SENSE_STATUS,
 }

def enforce(c):
 b=c['back']; assert c['import_ready'] is False and c['formal_release_approved'] is False
 assert b.get('Formen_section') in (None,[],''),'NEVER_DUPLICATE_FRONT_FORMS_ON_BACK'
 assert c['front'].get('forms_rendered_on_front_only') is True
 assert len(examples(c))>0,'NO_EXAMPLES_IN_LEMMA'
 for e in examples(c):assert isinstance(e.get('de'),str) and e['de'].strip() and isinstance(e.get('fa'),str) and e['fa'].strip(),'EMPTY_DE_FA_PAIR'
 for n in nets(c):
  assert n.get('sense_id') and n.get('sense_fa') and n.get('sense_de'),'INVALID_SENSE_DEFINITION'
  for x in n.get('Kombinationen_DE_FA',[]):assert x.get('de') and x.get('fa'),'EMPTY_COLLOCATION'


def mutate(c,manual,key):
 orig=copy.deepcopy(c);o=c['source_ordinal'];b=c['back']
 ns=b.get('semantic_network_sense_anchored_pending_qa') or []
 if not ns:
  ns=[new_net(c,r,i) for i,r in enumerate(manual[key(c)],1)]
  b['semantic_network_sense_anchored_pending_qa']=ns
  b['L10_phase2_network_editorial_origin']='MANUAL_212_SENSE_SPECIFIC_DEFINITIONS_COLLOCATIONS__NOT_AUTOMATIC_LEMMA_STRING_EXPANSION'
 if o==1485:
  assert len(ns)==1 and len(ns[0].get('Kombinationen_DE_FA',[]))==2
  ns[0]['sense_de']='intransitiv: völlig trocken werden (Perfekt mit ist)'
  ns[0]['sense_fa']='کاملاً خشک شدن (فعل لازم؛ با sein)'
  ns[0]['Kombinationen_DE_FA']=[{'de':'ohne Regen austrocknen','fa':'بدون باران خشک شدن','status':STATUS,'editorial_origin':'L10_PHASE2_CORRECT_FINITE_CLAUSE'}]
  ns[0]['status']=SENSE_STATUS
  ns.append({'sense_id':f"{c['preview_card_id']}:L10P2:S2",'sense_de':'transitiv: etwas völlig trocken machen (Perfekt mit hat)','sense_fa':'چیزی را به‌طور کامل خشک کردن (فعل گذرا؛ با haben)',
   'Kombinationen_DE_FA':[{'de':'den Boden austrocknen','fa':'زمین را خشک کردن','status':STATUS,'editorial_origin':'L10_PHASE2_VERIFIED_TRANSITIVE_USE'}],
   'Synonyme':[],'Antonyme':[],'Verwandte_Woerter_KEINE_Synonyme':[],'Wortfamilie':[],
   'source':'L10_PHASE2_SCOPED_DUDEN_AUXILIARY_EVIDENCE','status':SENSE_STATUS,
   'lexical_relation_policy':'NO_FORCED_SYNONYMS','usage_distinction_de':'Transitiver Gebrauch: die Sonne trocknet den Boden aus.'})
 # Handle exactly the 5 known finite clauses from old L10, not global other-lesson cases.
 for n in ns:
  for pair in n.get('Kombinationen_DE_FA',[]):
   k=(o,pair.get('de'))
   if k in FINITE_FIXES:
    if o==1485:
     # handled explicitly by splitting sense and replacing old clause list, do not duplicate
     raise AssertionError('UNEXPECTED_RETAINED_AUSTROCKNEN_CLAUSE')
    before=copy.deepcopy(pair)
    pair.update(de=FINITE_FIXES[k][0],fa=FINITE_FIXES[k][1],status=STATUS,editorial_origin='L10_PHASE2_FINITE_CLAUSE_TO_LEXICAL_COLLOCATION')
    b.setdefault('L10_phase2_full_sentence_collocation_fixes',[]).append({'before':before,'after':copy.deepcopy(pair),'same_lemma_sense_id':n['sense_id']})
 # All 29 statusless examples explicitly PENDING, NEVER default PASS.
 for e in examples(c):
  if not e.get('status'):
   e['status']='PENDING_L10_PHASE3_DE_FA_MEANING_CHECK'
   e['status_origin']='L10_PHASE2_PREVIOUSLY_STATUSLESS_NOT_AUTOPASSED'
 # Explicit lemma- and sentence-level meaning routes; the 32 ambiguous multisense cards are handwritten below.
 ex=examples(c);route=ROUTES.get(o)
 if len(ns)>1:
  assert route is not None,('MULTISENSE_WITHOUT_EXPLICIT_ROUTE',o,c['front']['base_headword_de'])
  assert len(route)==len(ex),('UNRESOLVED_MULTISENSE_LENGTH',o,len(route),len(ex))
 else:
  route=[1]*len(ex)
 for e,sid in zip(ex,route):
  assert 1<=sid<=len(ns),'INVALID_MANUAL_SENSE_ROUTE'
  e['sense_id']=ns[sid-1]['sense_id']
  e['L10_phase2_sense_route_review']='EDITORIALLY_ASSIGNED_PENDING_PHASE3_SEMANTIC_QA'
 for de,fa,sid in EXTRA_EXAMPLES.get(o,[]):
  assert 1<=sid<=len(ns)
  assert not any(norm(e['de'])==norm(de) for e in examples(c)),'SYNTHETIC_DE_DUPLICATE'
  b.setdefault('additional_examples_de_fa_pending_qa',[]).append({'de':de,'fa':fa,'sense_id':ns[sid-1]['sense_id'],'status':STATUS,'provenance':'L10_PHASE2_EDITORIAL_REVIEWED_CONTEXT_ADDITION__NOT_FROM_PUBLISHER','L10_phase2_sense_route_review':'EDITORIALLY_ASSIGNED_PENDING_PHASE3_SEMANTIC_QA'})
 if o==1448:
  assert c['front']['base_headword_de']=='anhalten (zu + D.)'
  c['front']['base_headword_de']='anhalten'
  c['front']['display_de_provisional']='anhalten – hält an – hielt an – hat angehalten; 1) etw. (Akk.) anhalten; 2) andauern; 3) jdn. (Akk.) zu etw. (Dat.) anhalten'
 if o in FORM_EVIDENCE:
  ev=FORM_EVIDENCE[o]
  c['front']['morphology_independently_validated']=True
  c['front']['morphology_attestation_L10_phase2']={**ev,'scope_status':'VERIFIED_DUDEN_ONLY_FORM_AND_SPECIFIC_VALENCY_NOT_ALL_MEANINGS','date':DATE}
 # No release flag lifted, no HOLD removed, no user source rewrite.
 c['formal_release_approved']=False;c['import_ready']=False
 b['L10_phase2_editorial_gate']='COMPLETE_REVIEW_DISPOSITION_PENDING_FULL_CASE_QA_NONIMPORT'
 # Demonstrate that every changed object carries concrete lexical or meaning-route changes.
 assert c!=orig,'NO_PRIMARY_CHANGE'
 enforce(c)
 return orig,c

def finite_clause_candidates(cards):
 det={'der','die','das','ein','eine','einen','einem','einer','dieser','diese'}
 finite={'veröffentlicht','bewertet','begrüßt','trocknet','wirkt','ist','sind','hat','haben','steht','läuft','arbeitet','verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt','hält','macht','nimmt','bietet','spricht','entscheidet','koordiniert','prüft','bringt','bestimmt','öffnet','organisiert','führt','reicht'}
 hits=[]
 for c in cards:
  for n in nets(c):
   for x in n.get('Kombinationen_DE_FA',[]):
    w=re.findall(r'\w+',x['de'],re.U)
    if len(w)>=4 and w[0].casefold() in det and w[1][0].isupper() and w[2].casefold() in finite:
     hits.append({'lesson':c['lesson'],'source_ordinal':c['source_ordinal'],'lemma':c['front']['base_headword_de'],'de':x['de']})
 return hits

def validate(parent,new,changed,manual,changes,source_map):
 assert len(parent)==len(new)==1571
 pids=[x['preview_card_id'] for x in new]
 assert len(set(pids))==1571,'DUPLICATE_ID'
 assert [x['preview_card_id'] for x in parent]==pids,'ID_ORDER_CHANGED'
 assert sum(c['lesson']=='L10' for c in new)==208
 assert sum(c['lesson']!='L10' for c in new)==1363
 assert set(changed)=={x['preview_card_id'] for x in new if x['lesson']=='L10'},('NOT_ALL_208_PRIMARY_EDITED',len(changed))
 assert all(p==n for p,n in zip(parent,new) if p['lesson']!='L10'),'OUTSIDE_1363_CARD_OBJECT_CHANGED'
 assert sha(source_map)==SOURCE_MAP_SHA
 assert all(x['import_ready'] is False and x['formal_release_approved'] is False for x in new if x['lesson']=='L10')
 oldH=sum(c.get('curated_HOLD_content_disposition_exists') is True for c in parent if c['lesson']=='L10')
 newH=sum(c.get('curated_HOLD_content_disposition_exists') is True for c in new if c['lesson']=='L10')
 assert oldH==newH==46,('HOLD_CHANGED',oldH,newH)
 assert all(p['linked_original_source_ordinals']==n['linked_original_source_ordinals'] for p,n in zip(parent,new))
 assert all(p['source_id']==n['source_id'] and p['source_ordinal']==n['source_ordinal'] for p,n in zip(parent,new))
 cc=[c for c in new if c['lesson']=='L10'];assert len(cc)==208
 ass=[e for c in cc for e in examples(c)]
 assert len(ass)==454,('EXPECTED_454_BILINGUAL_PAIRS',len(ass))
 assert all(e.get('status') and e.get('status')!='PASS' and e.get('sense_id') in {n['sense_id'] for n in nets(c)} for c in cc for e in examples(c))
 assert all(not c['back'].get('Formen_section') for c in cc)
 assert all(len(nets(c))>=1 for c in cc)
 assert all(len({n['sense_id'] for n in nets(c)})==len(nets(c)) for c in cc)
 assert all(len(examples(c))>0 for c in cc)
 assert all(not any(norm(a['de'])==norm(b['de']) for i,a in enumerate(examples(c)) for b in examples(c)[i+1:]) for c in cc),'DUPLICATE_DE_IN_CARD'
 hit=finite_clause_candidates(new)
 assert not [x for x in hit if x['lesson']=='L10'],('NEW_L10_FINITE_CLAUSES',hit)
 assert len(hit)==2,('UNEXPECTED_GLOBAL_FINITE_COUNT',hit)
 assert {x['source_ordinal'] for x in hit}=={158,232}
 assert len(changes)==208
 combo_l10=sum(len(all_collocs(c)) for c in cc)
 assert combo_l10==76+212+0,('UNEXPECTED_COMBINATION_TOTAL',combo_l10)
 sense_total=sum(len(nets(c)) for c in cc)
 assert sense_total==40+212+1,('UNEXPECTED_SENSE_TOTAL',sense_total)
 assert len(manual)==178
 # Explicit all original row links unique as documented: 1342..1548; 1451/1452 merge and 1487/1494 split.
 bysrc=collections.defaultdict(list)
 for c in cc:
  for t in c['linked_original_source_ordinals']:bysrc[t].append(c)
 assert set(bysrc)==set(range(1342,1549)),('LOST_L10_SOURCE_ROW',set(range(1342,1549))-set(bysrc))
 assert len(bysrc[1451])==len(bysrc[1452])==1 and bysrc[1451][0]['preview_card_id']==bysrc[1452][0]['preview_card_id']
 assert len(bysrc[1487])==len(bysrc[1494])==2
 return {'card_total':len(new),'L10_cards':208,'non_L10_unchanged':1363,'changed_primary_objects':len(changed),'source_row_map_sha256':sha(source_map),
 'lesson10_bilingual_examples':len(ass),'zero_example_cards':0,'missing_example_QA_status':0,'unrouted_semantic_example_senses':0,
 'L10_semantic_network_cards':208,'L10_sense_blocks':sense_total,'new_semantic_network_cards':178,'new_semantic_sense_blocks':213,
 'L10_collocations':combo_l10,'new_L10_collocations_net':212,'old_L10_collocations':76,
 'L10_exact_duplicate_de_groups':0,'remaining_known_finite_clauses_globally':hit,'L10_known_finite_clauses':0,
 'curated_HOLDs_L10':newH,'formal_approved_cards_L10':0,'real_app_import_tested':False,
 'source_coverage_rows':207,'canonical_lemma_splits_verified':2,'canonical_merged_rows_verified':1,
 'scoped_Duden_morphology_attestations':len(FORM_EVIDENCE),
 'semantic_language_all_208_fully_signed_off':False,'import_ready':False}

def run(parent:Path,lexical:Path,out:Path):
 out.mkdir(parents=True,exist_ok=True)
 oldfiles,lines,old=read_owner(parent)
 manual,key=manual_map(lexical,old)
 new=copy.deepcopy(old)
 decisions=[];changes=[];routes=[];newlines=[]
 priority={}
 q=out/'L10-PHASE1-208-CARD-DECISION-QUEUE-20261109.jsonl'
 # Queue provided in the identical work directory beside OWNER, read it by exact name.
 if not q.exists():raise FileNotFoundError('REQUIRES_ORIGINAL_PHASE1_208_CARD_QUEUE_FOR_EVERY_DECISION')
 for l in q.read_text(encoding='utf-8').splitlines():
  j=json.loads(l);priority[j['preview_card_id']]=j['priority']
 assert len(priority)==208
 for i,(c,raw) in enumerate(zip(new,lines)):
  if c['lesson']!='L10':newlines.append(raw);continue
  before,after=mutate(c,manual,key)
  assert before==old[i] and after==new[i]
  newlines.append((js(after)+'\n').encode('utf-8'))
  cardid=after['preview_card_id'];before_sha=sha(js(before).encode());after_sha=sha(js(after).encode())
  assert before_sha!=after_sha
  changes.append({'preview_card_id':cardid,'source_ordinal':c['source_ordinal'],'headword':c['front']['base_headword_de'],
   'before_sha256':before_sha,'after_sha256':after_sha,'before':before,'after':copy.deepcopy(after)})
  for e in examples(after):routes.append({'preview_card_id':cardid,'source_ordinal':after['source_ordinal'], 'de':e['de'],'fa':e['fa'],'assigned_sense_id':e['sense_id'],'QA':e['status']})
  decisions.append({'card_id':cardid,'ordinal':after['source_ordinal'],'headword':after['front']['base_headword_de'],
   'priority':priority[cardid], 'actual_primary_learner_object_changed':True,'before_sha256':before_sha,'after_sha256':after_sha,
   'example_pairs_before':len(examples(before)),'example_pairs_after':len(examples(after)),
   'semantic_senses_before':len(nets(before)),'semantic_senses_after':len(nets(after)),
   'collocations_before':len(all_collocs(before)),'collocations_after':len(all_collocs(after)),
   'curated_HOLD_preserved':before['curated_HOLD_content_disposition_exists']==after['curated_HOLD_content_disposition_exists'],
   'semantic_formal_release_approved':False,
   'disposition':'SAVED_PRIMARY_EDITORIAL__PENDING_L10_PHASE3_LINGUISTIC_AND_APP_IMPORT_GATES'})
 primary=b''.join(newlines)
 assert len(primary.splitlines())==1571
 assert all(old[i]==new[i] for i in range(len(new)) if old[i]['lesson']!='L10')
 metrics=validate(old,new,{x['preview_card_id'] for x in changes},manual,changes,oldfiles[MAP])
 assert len(decisions)==208 and len(routes)==454
 report={
  'schema':'aspekte-b1plus-l10-phase2-saved-primary-208-cards@1','date':DATE,
  'stage':'L10_PHASE2_ALL_208_CARDS_SAVED_PRIMARY_EDITED_NONIMPORT',
  'parent_curated_learner_zip_sha256':OWNER_SHA,'parent_primary_sha256':OWNER_PRIMARY_SHA,
  'new_primary_sha256':sha(primary),'source_map_sha256':SOURCE_MAP_SHA,
  'metrics':metrics,
  'editorial_method':'Handwritten per-lemma meaning-specific German/Persian senses and short collocations; no generated full sentence copied into Kombinationen. Existing 30 semantic networks preserved with explicit routes, austrocknen sense split. Every L10 primary card actually changed.',
  'status_policy':'All 29 previously missing example QA statuses were set to PENDING, not PASS; all 454 examples linked to current sense ID, still pending full bilingual semantic QA.',
  'grammar_evidence':FORM_EVIDENCE,
  'release_gate':{'status':'RELEASE_BLOCKED_NONIMPORT','formal_approved_cards':0,'real_app_import_and_front_back_render_tested':False,
                  'unresolved_curated_HOLDs':46,'new_lexical_collocations_need_case_QA':212,'full_bilingual_case_QA':'NOT_COMPLETED_PHASE3_NEXT',
                  'historical_finite_clause_issues_outside_L10':[158,232]},
  'next':'L10_PHASE3_ALL_208_CARD_CASE_LEVEL_QA_AND_RELEASE_GATE_WITH_FAIL_CLOSED_POLICY',
 }
 extras={
  ROOT+'L10-PHASE2-WHOLE-208-CARD-REPORT.json':pretty(report),
  ROOT+'L10-PHASE2-ALL-208-CARD-DISPOSITIONS.jsonl':(''.join(js(x)+'\n' for x in decisions)).encode(),
  ROOT+'L10-PHASE2-ALL-208-CARD-BEFORE-AFTER.json':pretty(changes),
  ROOT+'L10-PHASE2-ALL-454-EXAMPLE-SENSE-ROUTES.jsonl':(''.join(js(x)+'\n' for x in routes)).encode(),
  ROOT+'L10-PHASE2-MANUAL-SENSE-AND-COLLOCATION-EDITS.tsv':lexical.read_bytes(),
  ROOT+'L10-PHASE2-GLOBAL-REGRESSION-AND-IMPORT-GATE.json':pretty({'status':'STRUCTURAL_PASS__RELEASE_BLOCKED_NONIMPORT','metrics':metrics,
   'guards':{'PARENT_FULL_SHA256':'PASS','PARENT_PRIMARY_SHA256':'PASS','SOURCE_MAP_BYTE_IDENTICAL':'PASS','GLOBAL_1571_IDS_unchanged':'PASS','NON_L10_1363_OBJECTS_IDENTICAL':'PASS','ALL_208_PRIMARY_OBJECTS_ACTUALLY_DIFFER':'PASS','L10_454_EXAMPLES_HAVE_VALID_SENSE_IDS':'PASS','L10_29_MISSING_STATUSES_NOT_AUTOPASS':'PASS','L10_5_FINITE_CLAUSES_FIXED':'PASS','L10_46_HOLDS_PRESERVED':'PASS','ALL_FORMEN_ONLY_FRONT':'PASS','L10_NO_DE_DUPLICATES':'PASS'},
   'scope_limitations':['not a native Flashcards-Pro importer test','not all German/Farsi examples linguistically signed off','not all new collocations signed off','historical L02/L03 finite-clause cases still unresolved']}),
 }
 # HTML review is deliberately ONLY an offline QA view, not an app render.
 html_content=['<!doctype html><meta charset="utf-8"><title>Aspekte B1+ L10 Phase2: QA ONLY</title>',
  '<style>body{font:15px/1.5 system-ui;max-width:1150px;margin:24px auto;color:#171a21}article{border-bottom:1px solid #ddd;padding:14px}h2{font-size:20px}li{margin:.35em 0}.fa{direction:rtl;display:inline-block;padding-left:8px}</style>',
  '<h1>L10 Phase2 · 208 cards · OFFLINE QA ONLY · NOT THE LIVE APP · RELEASE BLOCKED</h1>']
 for c in (x for x in new if x['lesson']=='L10'):
  html_content.append(f'<article><h2>{c["source_ordinal"]} · {html.escape(c["front"]["base_headword_de"])} | {html.escape(c["front"]["display_de_provisional"])}</h2>')
  html_content.append(f'<p class="fa">{html.escape(c["back"].get("meanings_fa_provisional") or "")}</p><ul>')
  for n in nets(c):
   html_content.append(f'<li><b>{html.escape(n["sense_de"])}</b> — <span class="fa">{html.escape(n["sense_fa"])}</span><ul>')
   for p in n.get('Kombinationen_DE_FA',[]):html_content.append('<li>'+html.escape(p['de'])+' — <span class="fa">'+html.escape(p['fa'])+'</span></li>')
   for e in examples(c):
    if e.get('sense_id')==n['sense_id']:html_content.append('<li>'+html.escape(e['de'])+' — <span class="fa">'+html.escape(e['fa'])+'</span> ['+html.escape(e['status'])+']</li>')
   html_content.append('</ul></li>')
  html_content.append('</ul></article>')
 extras[ROOT+'L10-PHASE2-208-CARD-OFFLINE-QA-ONLY.html']='\n'.join(html_content).encode()
 # Critical learner-data owner is updated inside the *primary* member, not sidecars only.
 entries=dict(oldfiles);entries[MAIN]=primary;entries.update(extras)
 path=out/'Aspekte-B1plus-L10-PHASE2-WHOLE-208-CARDS-CURATED-NONIMPORT-20261110.zip'
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for k in sorted(entries):z.writestr(k,entries[k])
  z.writestr('SHA256SUMS.txt',''.join(f'{sha(entries[k])}  {k}\n' for k in sorted(entries)).encode())
 zipsha=sha(path.read_bytes())
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None and sha(z.read(MAIN))==sha(primary)
  assert len(z.namelist())==len(entries)+1
  assert len(z.read('SHA256SUMS.txt').splitlines())==len(entries)
  assert all(sha(z.read(k))==sha(entries[k]) for k in entries)
 report['archive']={'name':path.name,'size_bytes':path.stat().st_size,'zip_sha256':zipsha,'members':len(entries)+1,'manifest_entries_verified':len(entries)}
 (out/'L10-PHASE2-WHOLE-208-CARD-REPORT.json').write_bytes(pretty(report))
 (out/'L10-PHASE2-ALL-208-CARD-DISPOSITIONS.jsonl').write_bytes(extras[ROOT+'L10-PHASE2-ALL-208-CARD-DISPOSITIONS.jsonl'])
 (out/'L10-PHASE2-GLOBAL-REGRESSION-AND-IMPORT-GATE.json').write_bytes(extras[ROOT+'L10-PHASE2-GLOBAL-REGRESSION-AND-IMPORT-GATE.json'])
 print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
 if len(sys.argv)!=4:raise SystemExit('USAGE python build_L10_phase2_v1.py OWNER.zip MANUAL_TSV OUTPUT_DIR')
 run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
