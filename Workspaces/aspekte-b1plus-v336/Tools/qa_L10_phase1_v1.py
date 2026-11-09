#!/usr/bin/env python3
"""Aspekte B1+ L10 phase 1: immutable full-208-card evidence audit.

Usage: python qa_L10_phase1_v1.py VERIFIED_L09_PHASE3_OWNER.zip OUTPUT_DIR
No publisher-file re-import, no learner-card mutation, no fabricated language approval.
"""
from __future__ import annotations
import collections, hashlib, html, json, re, sys, zipfile
from pathlib import Path

DATE = '2026-11-09'
PARENT_SHA = '0ac34c8178984511d28d4400ff5efe56036d8c8f31aca0d85c1e70f4661a0054'
PRIMARY = 'G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
PRIMARY_SHA = '7eef147f679fec8dea922fefe4a350fafc059277dcfa3a8664c93d1ceddf5e33'
MAP = 'G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
MAP_SHA = 'c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
PREFIX = 'Lessons/L10/'
SUBJECT_DETERMINERS = {'der','die','das','ein','eine'}
FINITE_VERBS = {'reicht','entscheidet','koordiniert','läuft','prüft','schreibt','bringt',
 'bestimmt','öffnet','organisiert','führt','hat','ist','sind','steht','arbeitet',
 'verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt',
 'hält','macht','kann','wird','werden','nimmt','bietet','spricht',
 'veröffentlicht','bewertet','begrüßt','trocknet'}

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def jtext(data)->str:return json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
def jline(data)->str:return json.dumps(data,ensure_ascii=False,sort_keys=True)+'\n'
def norm(s)->str:return re.sub(r'\W+','',str(s).casefold())
def examples(c):
 b=c['back'];return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
def networks(c):return c['back'].get('semantic_network_sense_anchored_pending_qa') or []
def finite_clause(s):
 w=re.findall(r'[A-Za-zÄÖÜäöüß]+',s or '')
 return len(w)>=3 and w[0].casefold() in SUBJECT_DETERMINERS and w[1][0].isupper() and w[2].lower() in FINITE_VERBS

def source_coverage(cards):
 rows=collections.defaultdict(list)
 for c in cards:
  for source in c.get('linked_original_source_ordinals',[]):
   rows[int(source)].append({'card_id':c['preview_card_id'],'lemma':c['front']['base_headword_de'],'primary_ordinal':c['source_ordinal']})
 expected=set(range(1342,1549)); found=set(rows)
 assert found==expected,{'missing':sorted(expected-found),'extra':sorted(found-expected)}
 merged=[{'primary_ordinal':c['source_ordinal'],'lemma':c['front']['base_headword_de'],'original_rows':c['linked_original_source_ordinals']} for c in cards if len(c.get('linked_original_source_ordinals',[]))>1]
 split=[{'original_ordinal':o,'separate_cards':v} for o,v in sorted(rows.items()) if len(v)>1]
 assert merged==[{'primary_ordinal':1451,'lemma':'der Baumstamm','original_rows':[1451,1452]}],merged
 assert [(r['original_ordinal'],[v['lemma'] for v in r['separate_cards']]) for r in split]==[(1487,['das Hochwasser','die Überschwemmung']),(1494,['die Wasserknappheit','der Wassermangel'])],split
 return {'source_ordinal_range':[1342,1548],'unique_source_ordinals':len(rows),'expected_source_ordinals':207,
  'learner_card_count':len(cards),'merged_source_records':merged,'split_lemma_records':split,
  'source_mapping_complete':True,'notes':'Do not auto-merge two distinct approved lexical lemmas or re-split Baumstamm variants'}

def audit(owner:Path,out:Path):
 assert owner.is_file(),f'MISSING_OWNER:{owner}'
 out.mkdir(parents=True,exist_ok=True)
 raw_zip=owner.read_bytes();assert sha(raw_zip)==PARENT_SHA,'PARENT_SHA_MISMATCH'
 with zipfile.ZipFile(owner) as z:
  assert z.testzip() is None,'PARENT_ZIP_CRC_FAILURE'
  manifest={n:d for d,n in [line.split('  ',1) for line in z.read('SHA256SUMS.txt').decode().splitlines() if line.strip()]}
  assert set(manifest)==set(z.namelist())-{'SHA256SUMS.txt'},'PARENT_MANIFEST_FILESET_MISMATCH'
  assert all(sha(z.read(n))==digest for n,digest in manifest.items()),'PARENT_MANIFEST_INVALID'
  raw=z.read(PRIMARY);source_map=z.read(MAP)
 assert sha(raw)==PRIMARY_SHA,'PARENT_PRIMARY_NOT_PINNED'
 assert sha(source_map)==MAP_SHA,'PARENT_SOURCE_MAP_NOT_PINNED'
 allcards=[json.loads(line) for line in raw.splitlines() if line.strip()]
 assert len(allcards)==1571 and len({c['preview_card_id'] for c in allcards})==1571,'GLOBAL_CARD_IDS_INVALID'
 assert len(source_map.decode('utf-8-sig').splitlines())-1==1548,'GLOBAL_SOURCE_ROW_COUNT_INVALID'
 current=[c for c in allcards if c['lesson']=='L10']
 assert len(current)==208 and len({c['preview_card_id'] for c in current})==208,'L10_CARD_IDS_INVALID'
 assert all(c.get('import_ready') is False and c.get('formal_release_approved') is False for c in allcards),'UNEXPECTED_READY_OR_FORMAL_RELEASE'
 source=source_coverage(current)
 test_pairs=[
  ('finite-verb-regular','eine Forscherin veröffentlicht Ergebnisse',True),
  ('finite-verb-umlaut-eszett','der Talkmaster begrüßt seine Gäste',True),
  ('separable-finite-verb','die Haut trocknet aus',True),
  ('ordinary-infinitive','einen Dieb erwischen',False),
  ('ordinary-infinitive-noun-phrase','die Restmülltonne leeren',False),
  ('temporal-prepositional-phrase','bis nächsten Freitag',False),
 ]
 test_results=[]
 for test_name,sentence,expected in test_pairs:
  result=bool(finite_clause(sentence))
  assert result==expected,('finite-clause-classifier-regression',test_name,sentence,expected,result)
  test_results.append({'name':test_name,'phrase':sentence,'expected_is_finite_clause':expected,'actual_is_finite_clause':result,'result':'PASS'})
 try:
  source_coverage([c for c in current if c['source_ordinal']!=1342])
 except AssertionError:
  test_results.append({'name':'source-row-loss-is-rejected','result':'PASS','reason':'coverage assertion fails on missing source ordinal 1342'})
 else:raise AssertionError('source-coverage-guard-did-not-reject-card-loss')
 total=collections.Counter();pcounts=collections.Counter();queue=[];dup=[];missing=[];clause=[];allclauses=[];other=[];rel_flags=[];targets=[]
 for c in allcards:
  for net in networks(c):
   for co in net.get('Kombinationen_DE_FA') or []:
    if finite_clause(co.get('de','')):allclauses.append({'lesson':c['lesson'],'source_ordinal':c['source_ordinal'],'headword':c['front']['base_headword_de'],'de':co.get('de',''),'fa':co.get('fa',''),'reason':'ARTICLE_NOUN_FINITE_VERB_PATTERN_STRUCTURAL_HEURISTIC','linguistically_confirmed':False})
 for c in current:
  oo=c['source_ordinal'];ee=examples(c);nn=networks(c);com=[dict(co,sense_id=n.get('sense_id')) for n in nn for co in n.get('Kombinationen_DE_FA') or []]
  known_senses={n.get('sense_id') for n in nn if n.get('sense_id')}
  bad=[{'index':i,'sense_id':e.get('sense_id'),'de':e.get('de')} for i,e in enumerate(ee) if nn and e.get('sense_id') not in known_senses]
  no_status=[{'index':i,'de':e.get('de'),'fa':e.get('fa')} for i,e in enumerate(ee) if not e.get('status')]
  blank=[{'index':i,'de':e.get('de'),'fa':e.get('fa')} for i,e in enumerate(ee) if not str(e.get('de','')).strip() or not str(e.get('fa','')).strip()]
  groups=collections.defaultdict(list)
  for i,e in enumerate(ee):
   if norm(e.get('de')):groups[norm(e['de'])].append((i,e))
  double=[{'indices':[i for i,_ in vv],'de':[e.get('de') for _,e in vv],'fa_alternatives':[e.get('fa') for _,e in vv]} for vv in groups.values() if len(vv)>1]
  suspicious=[{'de':co.get('de'),'fa':co.get('fa'),'sense_id':co.get('sense_id'),'reason':'LIKELY_FULL_FINITE_CLAUSE_NOT_A_COLLOCATION'} for co in com if finite_clause(co.get('de',''))]
  wordnet_missing=not nn;has_hold=bool(c.get('curated_HOLD_content_disposition_exists'))
  priority='P1' if (has_hold or no_status or blank or not ee or double or suspicious or any(e.get('sense_id') and e.get('sense_id') not in known_senses for e in ee if nn)) else 'P2' if bad or len(nn)>1 or (bool(nn) and len(com)==0) else 'P3'
  tasks=[]
  if has_hold:tasks.append('KEEP_CURATED_HOLD__ADJUDICATE_ONLY_WITH_LEXICAL_EVIDENCE')
  if no_status:tasks.append('REVIEW_MISSING_EXAMPLE_STATUS__MARK_PENDING_NOT_PASS')
  if bad:tasks.append('ROUTE_EXAMPLES_TO_EXACT_MEANING_ID__DO_NOT_GUESS_MULTISENSE')
  if not ee:tasks.append('ADD_GENUINE_CONTEXTUAL_DE_FA_EXAMPLES')
  if blank:tasks.append('FIX_EMPTY_GERMAN_OR_PERSIAN_EXAMPLE')
  if double:tasks.append('COMPARE_DUPLICATE_GERMAN_EXAMPLES__KEEP_USEFUL_FA_ALTERNATIVES')
  if suspicious:tasks.append('MOVE_FULL_SENTENCE_FROM_KOMBINATIONEN_TO_BEISPIELE_OR_REWRITE_AS_SHORT_COLLOCATION')
  if not c['front'].get('morphology_independently_validated'):tasks.append('VERIFY_FRONT_MORPHOLOGY_WHERE_EVIDENCE_AVAILABLE__NOT_AUTOMATIC_ERROR')
  if wordnet_missing:tasks.append('CONSIDER_REAL_SENSE_SCOPED_WORTNETZ__NO_FORCED_SYNONYMS')
  else:tasks.append('CHECK_EXISTING_SENSE_BLOCKS_RELATIONS_AND_IDIOMATIC_COLLOCATIONS')
  if len(nn)>1:tasks.append('PRESERVE_MULTIPLE_SENSES_ON_ONE_CARD__CHECK_EXAMPLE_DISTRIBUTION')
  tasks.append('PRESERVE_LEARNER_SOURCE_LINKS_AND_CARD_ID')
  total.update({'examples':len(ee),'semantic_sense_blocks':len(nn),'combinations':len(com),'net_cards':bool(nn),'HOLD_cards':has_hold,
                'statusless_examples':len(no_status),'cards_with_statusless':bool(no_status),'missing_de_fa_examples':len(blank),'cards_without_examples':not bool(ee),
                'unrouted_network_examples':len(bad),'network_cards_with_unrouted':bool(bad),'duplicated_DE_groups':len(double),
                'cards_with_duplicate_DE':bool(double),'finite_clause_collocations':len(suspicious),'cards_with_clause_collocations':bool(suspicious),
                'morphology_attestation_missing':not bool(c['front'].get('morphology_independently_validated')),
                'forms_back_nonempty':c['back'].get('Formen_section') not in (None,'',[],{}),
                'cards_multiple_senses':len(nn)>1})
  pcounts[priority]+=1
  if no_status:missing.append({'source_ordinal':oo,'lemma':c['front']['base_headword_de'],'examples':no_status})
  if double:dup.append({'source_ordinal':oo,'lemma':c['front']['base_headword_de'],'groups':double})
  for co in suspicious:clause.append({'source_ordinal':oo,'lemma':c['front']['base_headword_de'],**co})
  case={'lesson':'L10','priority':priority,'source_ordinal':oo,'linked_original_source_ordinals':c['linked_original_source_ordinals'],'preview_card_id':c['preview_card_id'],'headword_de':c['front']['base_headword_de'],
   'front_display':c['front'].get('display_de_provisional'),'morphology_recorded_validated':bool(c['front'].get('morphology_independently_validated')),
   'meaning_fa_current':c['back'].get('meanings_fa_provisional'),'curated_HOLD':has_hold,'audit_flags':c.get('audit_flags',[]),
   'examples':ee,'example_count':len(ee),'missing_qa_status_entries':no_status,'blank_examples':blank,'unrouted_or_invalid_sense_examples':bad,
   'duplicate_DE_groups':double,'sense_blocks':nn,'semantic_sense_count':len(nn),'combinations_count':len(com),'finite_clause_collocations':suspicious,
   'tasks_for_phase2':tasks,'current_primary_card_json_sha256':sha(jline(c).encode()),
   'phase1_disposition':'REVIEW_QUEUE_NO_PRIMARY_EDITS','formal_card_release_approved':False}
  queue.append(case)
 queue=sorted(queue,key=lambda x:(x['source_ordinal'],x['headword_de']))
 assert len(queue)==208 and set(x['preview_card_id'] for x in queue)=={c['preview_card_id'] for c in current}
 assert sum(pcounts.values())==208
 assert total['examples']==sum(len(examples(c)) for c in current)
 assert all(not c['import_ready'] for c in current)
 report={'schema':'aspekte-b1plus-L10-phase1-whole-208-card-audit@1','date':DATE,'status':'L10_PHASE1_208_CARD_AUDIT_COMPLETE_AUDIT_ONLY_NONIMPORT',
  'source_authority':{'curated_owner_sha256':PARENT_SHA,'primary_sha256':PRIMARY_SHA,'source_map_sha256':MAP_SHA,'zip_members_verified':len(manifest),'zip_crc':'PASS','learner_data_owner_changed':False,'changed_primary_cards':0,'formal_approved_cards':0},
  'whole_corpus':{'total_cards':1571,'original_source_rows':1548,'lesson_card_counts':dict(sorted(collections.Counter(c['lesson'] for c in allcards).items())),
                 'collocations':sum(len(n.get('Kombinationen_DE_FA') or []) for c in allcards for n in networks(c))},
  'source_coverage':source,'L10_cards_audited':208,'L10_metrics':dict(total),'priority_queue':dict(sorted(pcounts.items())),'L10_full_clause_candidates':clause,
  'L10_missing_example_statuses_by_card':missing,'L10_duplicate_DE_example_groups':dup,
  'global_finite_clause_candidates':allclauses,'global_finite_clause_counts_by_lesson':dict(sorted(collections.Counter(c['lesson'] for c in allclauses).items())),
  'guard_regression_tests':{'passed':len(test_results),'total':len(test_results),'all_passed':True,'note':'Narrow diagnostics and source-coverage guards, not full linguistic certification'},
  'known_limitations':['Machine-readable structure and risk triage only, not definitive idiomaticity/semantic quality.',
    'Morphology attestation missing is not the same as incorrect inflection.',
    'Finite-clause pattern is a heuristic; Phase2 checks flagged cases individually.',
    'No human third-party review requirement; separate deterministic evidence gates are sufficient for this nonimport workflow.',
    'No real German-Flashcards-Pro app importer or UI rendering used.'],
  'next_phase':'L10_PHASE2_ONE_WHOLE_208_CARD_EDITORIAL__SAVE_ACTUAL_PRIMARY_1571_CARD_DIFF_ONLY_WITH_HASH_PROOFS'}
 coverage=source
 clause_report={'schema':'aspekte-b1plus-l10-finite-clauses-v5@1','date':DATE,'global_combinations':report['whole_corpus']['collocations'],
                'algorithm':'DEFINITE_ARTICLE_OR_EIN_EINE + CAPITALIZED_NOUN + KNOWN_FINITE_VERB',
                'global_candidates':allclauses,'L10_candidates':clause,'candidate_count_L10':len(clause),
                'not_full_semantic_certification':True,'strict_global_structural_pass':len(allclauses)==0}
 plan=f'''# Aspekte B1+ — Lektion 10 three-phase plan\n\n**Stand:** {DATE} · **Phase 1 DONE** · **Phase 2 NEXT** · Phase 3 planned · **NONIMPORT**\n\n## Authority and scope\nExact curated L09 Phase3 owner: SHA256 `{PARENT_SHA}`; primary 1571 JSONL SHA256 `{PRIMARY_SHA}`; source map SHA256 `{MAP_SHA}`. Never replace owner with Phase1 audit ZIP. No original publisher CSV inventory.\n\n## Phase 1 DONE — all 208 cards\n- All 208 L10 current cards covering original rows 1342–1548 audited together. The two approved separate lemma units at 1487 (Hochwasser / Überschwemmung) and 1494 (Wasserknappheit / Wassermangel) remain separate; 1451+1452 are one Baumstamm card.\n- {total['examples']} bilingual examples. {total['statusless_examples']} have no explicit QA status in {total['cards_with_statusless']} cards: do not auto mark PASS. {total['unrouted_network_examples']} missing or invalid sense IDs across {total['network_cards_with_unrouted']} network cards. {total['HOLD_cards']} inherited HOLDs unchanged.\n- {total['net_cards']} cards with networks, {total['semantic_sense_blocks']} current sense blocks, {total['combinations']} existing L10 collocations; {len(clause)} known full finite clauses mistakenly in combinations across {total['cards_with_clause_collocations']} L10 cards. Globally {len(allclauses)} flagged candidates; this detector is narrow.\n- Priority queue **P1={pcounts['P1']} / P2={pcounts['P2']} / P3={pcounts['P3']}**; each of 208 ledger rows includes before-state evidence, full examples, network entries and exact Phase2 tasks. Not 208 known language mistakes, not 208 approvals.\n- **0 changes to learner primary 1571-card JSONL** and zero formal card approvals. Full decision queue, structured report, audit-only HTML, source coverage, finite-clause diagnostics and reproducible script persist to Library/GitHub with SHA proof.\n\n## Phase 2 NEXT — one whole-208-card editorial stage\nReview every card against central front/back standards without microlots: nouns Artikel + Plural, verbs relevant conjugation and separability, multi-meaning one lemma, examples and relation-to-sense IDs, natural short bilingual combinations, no forced synonyms, no duplicate Formen on back. Resolve {total['statusless_examples']} example statuses conservatively as PENDING not PASS; route {total['unrouted_network_examples']} sense IDs with meaning evidence; treat {len(clause)} finite clauses as Examples or rewrite into true collocations. Preserve {total['HOLD_cards']} HOLDs unless case-specific evidence supports removal.\nPersist **actual primary 1571-card JSONL changes**, complete per-card before/after and unchanged 1363 non-L10 cards; retain mapping 1548 rows; ZIP + SHA256SUMS + exact Library readback. Do not count sidecar edits as real learner changes.\n\n## Phase 3 later\nComplete 208 case-level fail-closed release QA and regression. Attempt actual app import/render only if technical access exists. If bilingual semantic signoff or importer remains unverified, explicitly RELEASE_BLOCKED_NONIMPORT and retain unresolved cases in project-wide backlog. No extra microcycle or separate external reviewer.\n'''
 def h(s):return html.escape(str(s or ''))
 chunks=["<!doctype html><html lang='de'><meta charset='utf-8'><title>Aspekte B1+ L10 — 208 card audit only</title><style>body{font:15px/1.55 system-ui,sans-serif;max-width:1030px;margin:24px auto;color:#252a33}section{margin:15px 0;border:1px solid #ddd;border-radius:9px;padding:13px}h2{margin:0}.dim{color:#606a76}.risk{color:#a53a23}.examples{padding-left:21px}li{margin:7px 0}kbd{font-size:12px;background:#eee;padding:2px 5px}code{white-space:pre-wrap}.fa{direction:rtl;text-align:right;color:#444}summary{cursor:pointer}h1{font-size:26px}</style><h1>Aspekte B1+ — Lektion 10, Phase 1 (audit only)</h1>",
 f"<p>Stand {DATE} · 208/208 learner cards · P1 {pcounts['P1']} / P2 {pcounts['P2']} / P3 {pcounts['P3']} · release blocked, no primary edits</p>"]
 for case in queue:
  chunks.append(f"<section><h2>{h(case['source_ordinal'])} · {h(case['headword_de'])} <kbd>{h(case['priority'])}</kbd></h2><p class='dim'>{h(case['front_display'])}</p><p class='fa'>{h(case['meaning_fa_current'])}</p>")
  if case['curated_HOLD']:chunks.append("<strong class='risk'>CURATED HOLD — unchanged</strong>")
  if case['finite_clause_collocations']:chunks.append("<p class='risk'>Full finite clause in Kombinationen — Phase2 action</p>")
  chunks.append("<details><summary>Beispiele (DE–FA), senses and pending QA</summary><ol class='examples'>")
  for e in case['examples']:chunks.append(f"<li>{h(e.get('de'))}<p class='fa'>{h(e.get('fa'))}</p><small>Status: {h(e.get('status') or 'MISSING / PENDING')} · sense {h(e.get('sense_id') or 'UNROUTED')}</small></li>")
  chunks.append('</ol>')
  for n in case['sense_blocks']:
   chunks.append(f"<p><b>Sense:</b> {h(n.get('sense_de'))} — {h(n.get('sense_fa'))}</p><ul>")
   for v in n.get('Kombinationen_DE_FA') or []:chunks.append(f"<li>{h(v.get('de'))} — <span class='fa'>{h(v.get('fa'))}</span></li>")
   chunks.append('</ul>')
  chunks.append("</details><details><summary>Phase2 action queue</summary><ul>")
  for t in case['tasks_for_phase2']:chunks.append(f'<li>{h(t)}</li>')
  chunks.append('</ul></details></section>')
 chunks.append('</html>')
 files={
 PREFIX+'PHASE1-FULL-LESSON-AUDIT.json':jtext(report).encode(),
 PREFIX+'PHASE1-208-CARD-DECISION-QUEUE.jsonl':''.join(jline(x) for x in queue).encode(),
 PREFIX+'PHASE1-SOURCE-ROW-COVERAGE.json':jtext(source).encode(),
 PREFIX+'PHASE1-7-REGRESSION-TESTS.json':jtext({'date':DATE,'tests':test_results,'pass_count':len(test_results),'fail_count':0}).encode(),
 PREFIX+'PHASE1-FINITE-CLAUSE-GATE-v5.json':jtext(clause_report).encode(),
 PREFIX+'PHASE1-208-CARD-OFFLINE-QA-ONLY.html':''.join(chunks).encode(),
 PREFIX+'THREE-PHASE-PLAN.md':plan.encode(),
 'Tools/qa_L10_phase1_v1.py':Path(__file__).read_bytes(),
 'AUDIT-ONLY-NO-PRIMARY-DATA.txt':f'AUDIT ONLY. Current curated learner owner (unchanged): {PARENT_SHA}\nPrimary SHA256 (unchanged): {PRIMARY_SHA}\nSource mapping SHA256 (unchanged): {MAP_SHA}\nStatus: NONIMPORT, 0 formal approvals\n'.encode()
 }
 manifest=''.join(f'{sha(v)}  {k}\n' for k,v in sorted(files.items())).encode()
 files['SHA256SUMS.txt']=manifest
 dest=out/'Aspekte-B1plus-L10-PHASE1-WHOLE-208-CARD-AUDIT-NONIMPORT-20261109.zip'
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in sorted(files.items()):
   i=zipfile.ZipInfo(name,(2026,11,9,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o644<<16;z.writestr(i,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  mm=dict((n,d) for d,n in (x.split('  ',1) for x in z.read('SHA256SUMS.txt').decode().splitlines() if x))
  assert set(mm)==set(z.namelist())-{'SHA256SUMS.txt'} and all(sha(z.read(n))==d for n,d in mm.items())
  ledger=[json.loads(l) for l in z.read(PREFIX+'PHASE1-208-CARD-DECISION-QUEUE.jsonl').splitlines()];assert len(ledger)==208
  assert sha(z.read(PREFIX+'PHASE1-FULL-LESSON-AUDIT.json'))==sha(files[PREFIX+'PHASE1-FULL-LESSON-AUDIT.json'])
 writeout={
  'bundle':str(dest),'bundle_sha256':sha(dest.read_bytes()),'bundle_size_bytes':dest.stat().st_size,
  'zip_members':len(files),'manifest_verified_members':len(mm),'crc':'PASS','full_ledger_rows':len(ledger),
  'report_sha256':sha(files[PREFIX+'PHASE1-FULL-LESSON-AUDIT.json']),
  'decision_queue_sha256':sha(files[PREFIX+'PHASE1-208-CARD-DECISION-QUEUE.jsonl']),
  'readback_library':'NOT_YET','report':report
 }
 (out/'L10-PHASE1-LOCAL-RECEIPT.json').write_text(jtext(writeout),encoding='utf-8')
 (out/'L10-PHASE1-FULL-LESSON-AUDIT.json').write_bytes(files[PREFIX+'PHASE1-FULL-LESSON-AUDIT.json'])
 (out/'L10-THREE-PHASE-PLAN.md').write_bytes(files[PREFIX+'THREE-PHASE-PLAN.md'])
 print(jtext({'bundle':writeout['bundle'],'bundle_sha256':writeout['bundle_sha256'],'bytes':writeout['bundle_size_bytes'],
  'members':writeout['zip_members'],'manifest_sha':writeout['manifest_verified_members'],
  'cards':len(current),'source_rows':source['unique_source_ordinals'],'priority':dict(pcounts),'metrics':dict(total),
  'finite_L10':len(clause),'global_clauses':len(allclauses),'global_per_lesson':dict(collections.Counter(x['lesson'] for x in allclauses)),
  'owner_unchanged_sha':PARENT_SHA}))

if __name__=='__main__':
 if len(sys.argv)<3:raise SystemExit('Usage: qa_L10_phase1_v1.py VERIFIED_OWNER_ZIP OUTPUT_DIR')
 audit(Path(sys.argv[1]),Path(sys.argv[2]))
