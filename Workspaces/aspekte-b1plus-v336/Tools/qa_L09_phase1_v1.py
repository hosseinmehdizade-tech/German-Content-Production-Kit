#!/usr/bin/env python3
"""Aspekte B1+ L09 audit of all 185 currently curated cards, without editing the learner owner.

Usage: python qa_L09_phase1_v1.py SOURCE_CURATED_ZIP OUTPUT_DIR
A single whole-lesson NONIMPORT triage, not a semantic release or publisher comparison.
"""
from __future__ import annotations
import collections, hashlib, html, io, json, re, sys, zipfile
from pathlib import Path

DATE='2026-11-09'
OWNER_SHA='577770549cf2a93feb86bc0197079c3580c8b73becaa20d7b65decf0f6d437e0'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAIN_SHA='89171eeea1e5b0aba9182ebe36418265b756ae6caab8fa45b0878579120608e0'
SRC='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
SRC_SHA='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
DETERMINERS={'der','die','das','ein','eine','einen','einem','einer','diese','dieser','dieses','jener','jene'}
FINITE={'reicht','entscheidet','koordiniert','läuft','prüft','schreibt','bringt','bestimmt','öffnet','organisiert','führt','hat','ist','sind','steht','arbeitet','verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt','hält','macht','kann','wird','werden','nimmt','bietet','spricht'}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def jbytes(o)->bytes:return (json.dumps(o,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
def jline(o)->str:return json.dumps(o,ensure_ascii=False,sort_keys=True)+'\n'
def get_examples(c):
 b=c.get('back',{});return list(b.get('existing_examples_de_fa_pending_qa') or [])+list(b.get('additional_examples_de_fa_pending_qa') or [])
def get_networks(c):return list(c.get('back',{}).get('semantic_network_sense_anchored_pending_qa') or [])
def norm(s):return re.sub(r'\W','',str(s).casefold(),flags=re.UNICODE)
def finite(c):
 found=[];total=0
 for network in get_networks(c):
  for co in network.get('Kombinationen_DE_FA') or []:
   total+=1;w=re.findall(r'\w+',co.get('de',''),flags=re.UNICODE)
   if len(w)>=4 and w[0].casefold() in DETERMINERS and w[1][0].isupper() and w[2].casefold() in FINITE:
    found.append({'lesson':c['lesson'],'source_ordinal':c['source_ordinal'],'headword_de':c['front']['base_headword_de'],'de':co['de'],'fa':co.get('fa',''), 'reason':'KNOWN_SIMPLE_NP_PLUS_FINITE_VERB_PATTERN'})
 return total,found

def ensure_static_asserts(cards,raw,sm):
 assert len(cards)==1571,'LOSS_OF_LEARNER_UNITS'
 assert len({c['preview_card_id'] for c in cards})==1571,'DUPLICATE_LEARNER_IDS'
 assert sha(raw)==MAIN_SHA,'PRIMARY_SHA_MISMATCH'
 assert sha(sm)==SRC_SHA,'SOURCE_MAP_SHA_MISMATCH'
 assert len(sm.decode('utf-8-sig').splitlines())-1==1548,'SOURCE_MAP_ROWS_CHANGED'
 assert all(c.get('import_ready') is False and c.get('formal_release_approved') is False for c in cards),'UNEXPECTED_RELEASED_CARD'

def run(owner:Path,out:Path):
 out.mkdir(parents=True,exist_ok=True)
 original=owner.read_bytes();assert sha(original)==OWNER_SHA, 'UNEXPECTED_CURATED_OWNER__FAIL_CLOSED'
 with zipfile.ZipFile(io.BytesIO(original)) as z:
  assert z.testzip() is None,'OWNER_ZIP_CRC_FAIL'
  names=z.namelist();assert len(names)==285,'OWNER_MEMBER_COUNT_CHANGED'
  manifest={n:h for h,n in (x.split('  ',1) for x in z.read('SHA256SUMS.txt').decode().splitlines())}
  assert set(manifest)==(set(names)-{'SHA256SUMS.txt'}),'OWNER_MANIFEST_COVERAGE_FAILED'
  assert all(sha(z.read(n))==h for n,h in manifest.items()),'OWNER_MEMBER_SHA_FAILED'
  raw=z.read(MAIN);sm=z.read(SRC)
  cards=[json.loads(x) for x in raw.splitlines()]
 ensure_static_asserts(cards,raw,sm)
 lesson=[c for c in cards if c['lesson']=='L09'];assert len(lesson)==185,'L09_CARD_COUNT_MISMATCH'
 orig=collections.defaultdict(list)
 for c in lesson:
  for o in c.get('linked_original_source_ordinals',[]):orig[o].append({'id':c['preview_card_id'],'de':c['front']['base_headword_de']})
 assert set(orig)==set(range(1157,1342)),'SOURCE_COVERAGE_MISSING_OR_EXTRA'
 assert len(orig[1302])==2 and {x['de'] for x in orig[1302]}=={'die Kochshow','die Kochsendung'},'1302_LEXEME_SPLIT_LOST'
 assert len(orig[1240])==1 and len(orig[1241])==1 and orig[1240]==orig[1241] and orig[1240][0]['de']=='zurückhaben','1240_1241_MERGE_CORRUPT'

 metrics=collections.Counter(); priorities=collections.Counter(); queue=[]; duplicates=[]; missing_status=[]; zero_example=[]; unrouted=[]; global_finite=[]; violations=[]; all_collocations=collections.Counter(); hold_cards=[]; networks=[]; flagged_forms=[]
 for c in cards:
  co_count,cases=finite(c);all_collocations[c['lesson']]+=co_count;global_finite.extend(cases)
 for c in lesson:
  ordinal=c['source_ordinal'];term=c['front']['base_headword_de'];ex=get_examples(c);net=get_networks(c)
  ids={n.get('sense_id') for n in net if n.get('sense_id')}
  orphan=[{'index':i,'de':e.get('de'),'fa':e.get('fa'),'sense_id':e.get('sense_id')} for i,e in enumerate(ex) if net and e.get('sense_id') not in ids]
  statuses=[{'index':i,'de':e.get('de'),'fa':e.get('fa')} for i,e in enumerate(ex) if not e.get('status')]
  missing=[{'index':i,'de':e.get('de'),'fa':e.get('fa')} for i,e in enumerate(ex) if not str(e.get('de','')).strip() or not str(e.get('fa','')).strip()]
  duplicate=[];groups=collections.defaultdict(list)
  for i,e in enumerate(ex):
   n=norm(e.get('de',''))
   if n: groups[n].append({'index':i,'de':e.get('de'),'fa':e.get('fa'),'status':e.get('status')})
  for entries in groups.values():
   if len(entries)>1:duplicate.append(entries)
  coll=[];forbidden=[]
  for n in net:
   for phrase in n.get('Kombinationen_DE_FA') or []:
    coll.append({'sense_id':n.get('sense_id'),'de':phrase.get('de',''),'fa':phrase.get('fa','')})
    if not phrase.get('de') or not phrase.get('fa'):forbidden.append('EMPTY_DE_FA_COLLOCATION')
    if any(norm(phrase.get('de',''))==norm(e.get('de','')) for e in ex):forbidden.append('COLLOCATION_EQUAL_TO_EXAMPLE')
  v4=[v for v in global_finite if v['lesson']=='L09' and v['source_ordinal']==ordinal and v['headword_de']==term]
  flags=[];actions=[]
  if not ex: flags.append('NO_BILINGUAL_EXAMPLES');actions.append('Create context-accurate paired German–Persian examples, then verify language and sense before publishing')
  if missing:flags.append('EMPTY_DE_FA_EXAMPLE_FIELDS');actions.append('Repair blank DE or FA fields using verified context')
  if statuses:flags.append('EXAMPLE_QA_STATUS_MISSING');actions.append('Set missing statuses to PENDING; do not auto-PASS')
  if duplicate:flags.append('EXACT_SAME_CARD_GERMAN_EXAMPLE_REPEATED');actions.append('Compare translations; merge only redundant German example, preserve helpful Persian alternative')
  if orphan:flags.append('EXAMPLES_UNROUTED_TO_SENSE');actions.append('Explicitly route each existing example to correct sense_id after checking actual contextual meaning')
  if v4:flags.append('FINITE_SENTENCE_INSIDE_KOMBINATIONEN');actions.append('Move full sentence to examples OR replace it with a natural shorter collocation after editorial QA')
  if c.get('curated_HOLD_content_disposition_exists'):flags.append('CURATED_RELEASE_HOLD_OPEN');actions.append('Preserve and resolve exact HOLD cause only when semantic evidence suffices; no automatic release')
  if forbidden:flags.append('COLLOCATION_STRUCTURE_OR_NONCOPY_REVIEW');actions.append('Correct malformed/copy-based collocations if evidence supports a change')
  if len(net)>1:flags.append('MULTIPLE_SENSE_BLOCKS_EDITORIAL_SCOPE');actions.append('Keep one lemma card and attach relations/examples/collocations to each specific sense')
  if c.get('audit_flags'):flags.append('INHERITED_AUDIT_FLAGS_PRESENT');actions.append('Recheck inherited flags against current edited card, distinguish already-fixed from genuine pending cases')
  if not c['front'].get('morphology_independently_validated'):actions.append('Perform risk-proportionate front morphology check; absence of evidence is not proof of an error')
  if not actions:actions=['Conservative whole-card semantic/style pass; preserve accepted content unless a concrete error is found']
  if any(f in flags for f in ['CURATED_RELEASE_HOLD_OPEN','NO_BILINGUAL_EXAMPLES','EXAMPLE_QA_STATUS_MISSING','EXACT_SAME_CARD_GERMAN_EXAMPLE_REPEATED','FINITE_SENTENCE_INSIDE_KOMBINATIONEN','EMPTY_DE_FA_EXAMPLE_FIELDS','COLLOCATION_STRUCTURE_OR_NONCOPY_REVIEW']):p='P1'
  elif any(f in flags for f in ['EXAMPLES_UNROUTED_TO_SENSE','MULTIPLE_SENSE_BLOCKS_EDITORIAL_SCOPE','INHERITED_AUDIT_FLAGS_PRESENT']):p='P2'
  else:p='P3'
  priorities[p]+=1
  metrics.update({'example_total':len(ex),'sense_blocks':len(net),'collocation_total':len(coll),'statusless_examples':len(statuses),'unrouted_network_examples':len(orphan),'cards_without_examples':int(not ex),'blank_bilingual_examples':len(missing),'curated_HOLDs':int(bool(c.get('curated_HOLD_content_disposition_exists'))),'network_cards':int(bool(net)),'morphology_front_attestations_recorded':int(bool(c['front'].get('morphology_independently_validated'))),'duplicate_de_example_groups':len(duplicate),'known_finite_clause_patterns_L09':len(v4),'cards_with_inherited_audit_flags':int(bool(c.get('audit_flags')))})
  if not ex:zero_example.append({'ordinal':ordinal,'headword':term})
  if statuses:missing_status.extend([{'ordinal':ordinal,'headword':term,**x} for x in statuses])
  if orphan:unrouted.extend([{'ordinal':ordinal,'headword':term,**x} for x in orphan])
  if duplicate:duplicates.append({'ordinal':ordinal,'headword':term,'groups':duplicate})
  if net:networks.append({'ordinal':ordinal,'headword':term,'senses':[{'sense_id':n.get('sense_id'),'de':n.get('sense_de'),'fa':n.get('sense_fa'),'combinationen':n.get('Kombinationen_DE_FA')} for n in net]})
  if c.get('curated_HOLD_content_disposition_exists'):hold_cards.append({'ordinal':ordinal,'headword':term})
  if c['front'].get('morphology_independently_validated'):flagged_forms.append({'ordinal':ordinal,'headword':term})
  queue.append({'lesson':'L09','source_ordinal':ordinal,'linked_source_ordinals':c['linked_original_source_ordinals'],'preview_card_id':c['preview_card_id'],'headword_de':term,'front_display_de':c['front']['display_de_provisional'],'meanings_fa':c['back'].get('meanings_fa_provisional'),'priority':p,'risk_flags':flags,'inherited_audit_flags':c.get('audit_flags',[]),'curated_hold':c.get('curated_HOLD_content_disposition_exists'), 'example_count':len(ex),'examples':ex,'network_senses':net,'unrouted_examples':orphan,'missing_example_statuses':statuses,'duplicate_examples':duplicate,'known_finite_clause_cases':v4,'combination_count':len(coll),'morphology_attestation_recorded':c['front'].get('morphology_independently_validated'),'phase2_actions':actions,'release_status':'PROVISIONAL_NONIMPORT','phase1_saved_primary_edits':0})
 assert len(queue)==185 and sum(priorities.values())==185
 assert metrics['example_total']==419 and metrics['statusless_examples']==41 and metrics['curated_HOLDs']==43
 assert metrics['cards_without_examples']==2 and metrics['unrouted_network_examples']==16
 assert metrics['duplicate_de_example_groups']==1 and metrics['collocation_total']==21
 assert metrics['network_cards']==8 and metrics['morphology_front_attestations_recorded']==0
 assert len(duplicates)==1 and duplicates[0]['ordinal']==1157
 assert len([f for f in global_finite if f['lesson']=='L09'])==1 and any(f['source_ordinal']==1266 for f in global_finite),'MISSING_EXPECTED_V4_CASE'
 assert len(global_finite)==3,'EXPECTED_3_GLOBAL_LEGACY_CASES'
 assert len(set(c['preview_card_id'] for c in lesson))==185
 assert sorted(priorities)==['P1','P2','P3']

 report={'schema':'aspekte-b1plus-L09-phase1-whole-lesson-audit@1','date':DATE,'phase':1,'phases_total':3,'status':'L09_185_CARDS_FULL_AUDIT_DONE_AUDIT_ONLY_NONIMPORT','current_curated_learner_data_owner_unchanged':True,'parent_owner':{'sha256':OWNER_SHA,'size_bytes':len(original),'member_count':285,'manifest_members_verified':len(manifest),'zip_crc':'PASS','library_file_id':'libfile_417fe423eb6c8191bb50a3ba7b6f6352','primary_jsonl_sha256':sha(raw),'original_source_map_sha256':sha(sm)},'global':{'card_count':len(cards),'source_map_rows':1548,'collocations_corpus':sum(all_collocations.values()),'combinations_by_lesson':dict(all_collocations),'v4_known_pattern_cases':global_finite,'v4_strict_gate':'FAIL_3_EXISTING_CASES'},'lesson':{'cards':len(lesson),'ordinals':[1157,1341],'original_source_rows_covered':len(orig),'original_1302_split_into':['die Kochshow','die Kochsendung'],'original_1240_and_1241_link_to':'zurückhaben','source_mapping_identity':'PASS','metrics':dict(metrics),'priority_distribution':dict(priorities),'cards_with_missing_status':len({x['ordinal'] for x in missing_status}),'cards_with_unrouted_network_examples':len({x['ordinal'] for x in unrouted}),'duplicate_german_examples':duplicates,'zero_example_cards':zero_example,'morphology_front_flags_recorded':len(flagged_forms),'network_cards':networks},'release':{'formal_cards_approved':0,'learner_data_cards_changed':0,'real_app_import_render_tested':False,'ready_for_import':False,'blocked_legacy_HOLDs_preserved':len(hold_cards)},'limitations':['Priority is a work queue, not proven linguistic error.','A structural pass does not prove idiomaticity or complete DE–FA correctness.','No publisher/source CSV reimport, and source map is not used as a quality reset.','No second human evaluator is required or claimed.','The audit ZIP is not a replacement curated learner-data owner.'],'next':'L09_PHASE2_ALL_185_CARD_EDITORIAL_REAL_PRIMARY_DATA_EDIT_WITH_BEFORE_AFTER_DIFF_AND_SOURCE_MAPPING_GUARDS'}

 plan=f'''# Aspekte B1+ — L09 three-phase plan (LIVE)\n\nStand {DATE} · Phase 1 DONE · Phase 2 NEXT · Phase 3 release gate PLANNED · NONIMPORT\n\n## Owner\nExact current curated L08 Phase3 Library owner: libfile_417fe423eb6c8191bb50a3ba7b6f6352, SHA-256 {OWNER_SHA}. Source map SHA {SRC_SHA}. Audit-only: NO primary card edits and NO owner promotion.\n\n## Phase 1 — full-lesson audit DONE\n- All 185 current L09 learner cards and source ordinals 1157–1341 checked. 1302 is two distinct lemmas (Kochshow, Kochsendung); 1240/1241 both link to one zurückhaben card.\n- {metrics['example_total']} DE–FA examples; {metrics['cards_without_examples']} zero-example cards (both ordinal 1302); {metrics['statusless_examples']} missing explicit example QA statuses on {len({x['ordinal'] for x in missing_status})} cards; no blank bilingual example fields.\n- {metrics['curated_HOLDs']} inherited HOLDs; {metrics['network_cards']} network cards / {metrics['sense_blocks']} sense blocks / {metrics['unrouted_network_examples']} unlinked network examples; {metrics['collocation_total']} L09 combos / {sum(all_collocations.values())} corpus combos.\n- Duplicated DE example in 1157 Andenken: preserve useful Persian alternative, remove only true duplicate in Phase2. Full sentence in Kombinationen 1266 Ozeanriese: move to Beispiele or replace with a natural phrase.\n- Priority queues P1={priorities['P1']}, P2={priorities['P2']}, P3={priorities['P3']}. They are triage, not proof. Missing recorded scoped morphology validation on 185/185 is evidence metadata gap, not 185 wrong forms.\n\n## Phase 2 — NEXT, ONE WHOLE LESSON (185 cards)\n- Address exact 43 HOLDs conservatively and audit all card meanings, front inflections, examples, sense-specific relations and idiomatic combinations. Fix zero-example Kochshow/Kochsendung, 41 missing statuses as PENDING (not auto-PASS), 16 sense routes, Andenken duplicate and Ozeanriese sentence. Keep same-lemma senses together.\n- Persist actual modified PRIMARY 1571-card JSONL and full-card before/after. Assert 1386 cards outside L09 unchanged, 1548 source rows and stable IDs preserved; do not promote a sidecar-only audit as a new owner.\n\n## Phase 3 — after Phase 2\n- Full-case QA and regression on saved edited primary cards and strict importer/render test if technically accessible. If real app or complete bilingual linguistic signoff is lacking, mark RELEASE_BLOCKED_NONIMPORT and proceed to L10 Phase1. No invented human reviewer, no 10-word loops, no textbook reinventory.\n'''

 # Portable full evidence: source mapping coverage, report, per-card full case queue, QA-only readable HTML, plan.
 files={
   'Lessons/L09/L09-PHASE1-WHOLE-185-CARD-AUDIT.json':jbytes(report),
   'Lessons/L09/L09-PHASE1-185-CARD-DECISION-QUEUE.jsonl':''.join(jline(x) for x in queue).encode(),
   'Lessons/L09/L09-PHASE1-SOURCE-MAP-COVERAGE.json':jbytes({'source_ordinals':{str(k):orig[k] for k in sorted(orig)},'all_original_185_rows_covered':True,'source_map_primary_owner_unchanged':True,'source_map_sha256':SRC_SHA}),
   'Lessons/L09/L09-PHASE1-THREE-PHASE-PLAN.md':plan.encode(),
   'Lessons/L09/L09-PHASE1-MISSING-STATUS-AND-SENSE-ROUTES.json':jbytes({'statusless_examples':missing_status,'unrouted_network_examples':unrouted,'no_examples':zero_example,'duplicate_examples':duplicates,'HOLDs':hold_cards}),
   'Lessons/L09/L09-PHASE1-KOMBINATIONEN-V4-GLOBAL.json':jbytes({'scanned':sum(all_collocations.values()),'issues':global_finite,'known_pattern_only':True,'structural_not_semantic_signoff':True}),
  }
 parts=['<!doctype html><html lang="de"><meta charset="utf-8"><title>Aspekte B1+ L09 185 — QA ONLY NONIMPORT</title>', '<style>body{font-family:system-ui,sans-serif;max-width:1100px;margin:25px auto;line-height:1.5;color:#202635}article{border:1px solid #ccc;border-radius:8px;padding:12px 18px;margin-bottom:12px}summary{cursor:pointer}code{background:#eee;padding:2px}.fa{direction:rtl;text-align:right}.risk{color:#a34d22}.meta{color:#667085}</style><body>', f'<h1>Aspekte B1+ L09 · {len(lesson)} cards · Phase 1 AUDIT_ONLY · NONIMPORT</h1><p>{metrics["example_total"]} DE/FA examples. Priority P1={priorities["P1"]} P2={priorities["P2"]} P3={priorities["P3"]}. This report does not approve cards.</p>']
 for q in queue:
  parts.extend(['<article><h2>'+html.escape(q['headword_de'])+' <small>'+q['priority']+' · '+str(q['source_ordinal'])+'</small></h2>', '<div>'+html.escape(str(q['front_display_de']))+'</div>','<p class="fa">'+html.escape(str(q['meanings_fa']))+'</p>', '<p class="risk">'+html.escape(', '.join(q['risk_flags']) or 'No known high-priority structural flags')+'</p>',f'<details><summary>Beispiele ({q["example_count"]})</summary><ol>'])
  for e in q['examples']:
   parts.append('<li>'+html.escape(str(e.get('de','')))+'<div class="fa">'+html.escape(str(e.get('fa','')) )+'</div><small>'+html.escape(str(e.get('status') or 'QA_STATUS_MISSING'))+'</small></li>')
  parts.append('</ol></details><details><summary>Wortnetz / Kombinationen</summary>')
  for n in q['network_senses']:
   parts.append('<p><b>'+html.escape(str(n.get('sense_de','')) )+'</b> — '+html.escape(str(n.get('sense_fa','')) )+'</p>')
   for co in n.get('Kombinationen_DE_FA') or []:parts.append('<p>'+html.escape(str(co.get('de','')) )+' — '+html.escape(str(co.get('fa','')) )+'</p>')
  parts.append('</details><details><summary>Phase2 actions</summary><ul>')
  for a in q['phase2_actions']:parts.append('<li>'+html.escape(a)+'</li>')
  parts.append('</ul></details></article>')
 parts.append('</body></html>');files['Lessons/L09/L09-PHASE1-185-CARD-QA-ONLY.html']='\n'.join(parts).encode()
 files['Tools/qa_L09_phase1_v1.py']=Path(__file__).read_bytes()
 zip_name='Aspekte-B1plus-L09-PHASE1-WHOLE-185-CARD-AUDIT-NONIMPORT-20261109.zip'
 zip_file=out/zip_name
 with zipfile.ZipFile(zip_file,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for name,b in sorted(files.items()):z.writestr(name,b)
  z.writestr('SHA256SUMS.txt',''.join(f'{sha(b)}  {n}\n' for n,b in sorted(files.items())).encode())
 with zipfile.ZipFile(zip_file) as z:
  assert z.testzip() is None
  m={n:h for h,n in (x.split('  ',1) for x in z.read('SHA256SUMS.txt').decode().splitlines())}
  assert set(m)==set(z.namelist())-{'SHA256SUMS.txt'} and all(sha(z.read(n))==h for n,h in m.items())
  q=[json.loads(x) for x in z.read('Lessons/L09/L09-PHASE1-185-CARD-DECISION-QUEUE.jsonl').splitlines()]
  assert len(q)==185 and {x['preview_card_id'] for x in q}=={x['preview_card_id'] for x in lesson}
  assert z.read('Lessons/L09/L09-PHASE1-WHOLE-185-CARD-AUDIT.json')==files['Lessons/L09/L09-PHASE1-WHOLE-185-CARD-AUDIT.json']
 # Source not rewritten, stable owner remains. Audit-only distinct path.
 (out/'L09-PHASE1-WHOLE-185-CARD-AUDIT.json').write_bytes(files['Lessons/L09/L09-PHASE1-WHOLE-185-CARD-AUDIT.json'])
 (out/'L09-PHASE1-185-CARD-DECISION-QUEUE.jsonl').write_bytes(files['Lessons/L09/L09-PHASE1-185-CARD-DECISION-QUEUE.jsonl'])
 (out/'L09-PHASE1-THREE-PHASE-PLAN.md').write_bytes(files['Lessons/L09/L09-PHASE1-THREE-PHASE-PLAN.md'])
 print(json.dumps({'zip_name':zip_name,'zip_sha256':sha(zip_file.read_bytes()),'zip_size_bytes':zip_file.stat().st_size,'members':len(files)+1,'manifest_entries':len(files),'metrics':dict(metrics),'priority_distribution':dict(priorities),'report_sha256':sha(files['Lessons/L09/L09-PHASE1-WHOLE-185-CARD-AUDIT.json']),'decision_queue_sha256':sha(files['Lessons/L09/L09-PHASE1-185-CARD-DECISION-QUEUE.jsonl']),'status':'NONIMPORT_AUDIT_ONLY_OWNER_UNCHANGED'},ensure_ascii=False,indent=2))

if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('Usage: python qa_L09_phase1_v1.py OWNER.zip OUTPUT_DIR')
 run(Path(sys.argv[1]),Path(sys.argv[2]))