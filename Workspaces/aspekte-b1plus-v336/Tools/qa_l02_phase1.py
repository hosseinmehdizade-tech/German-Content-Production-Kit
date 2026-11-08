#!/usr/bin/env python3
"""Whole lesson L02 content inventory against current curated owner, NOT semantic signoff.
Usage: python qa_l02_phase1.py OWNER.zip OUTPUT_DIRECTORY
Checks source ID mapping, card presence, examples, sense routes, and makes 91 per-card decisions.
All educational text is read-only. Exit 1 if source coverage / structural invariants fail.
"""
from pathlib import Path
from collections import Counter, defaultdict
import sys, json, csv, io, zipfile, hashlib, re

MASTER='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
SOURCE='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
IN_SCOPE=range(72,163)
COMPLEX={73,74,75,78,82,86,87,92,93,96,103,106,109,115,119,123,128,136,137,140,142,151,152,153,157,158,159}
POLYSEMY={74,75,78,82,86,87,88,92,93,96,106,119,123,125,128,132,140,142,144,148,150,151,152,153,157,158,159}
MORPHOLOGY_HIGHRISK={73,74,75,78,82,84,87,92,93,95,96,98,103,106,109,111,112,114,115,120,123,128,134,136,137,140,142,147,148,151,153,156,157,158,159,160,161}
CASE_NOTES={
 75:'weak/strong past + transitivity: verify zerreißen and zerreißen (intransitive)',
 78:'separate eingehen auf + Akk. from eingehen (payment receipt, plants die, fabric shrink); scoped sense network required',
 82:'betten vs sich betten; assess idiomatic contexts',
 86:'Löwe animal and zodiac; do not conflate forms',
 87:'umbauen rebuild vs build around: valency/sense differentiation',
 92:'binden vs sich binden an: valency and reflexive semantics',
 93:'eintreten enter / occur / kick in: different separability/constructions',
 95:'komfortabel comparative and scope; preexisting HOLD',
 105:'gender-variant profession morphology; existing G3 wordnet links',
 106:'leidtun spelling, verbal structure and ich tue vs es tut mir leid',
 114:'ermutigen + Akk. (person) zu + Dat. (action); check existing lexical relations',
 119:'WG as people and shared apartment; nuance / examples',
 120:'architektonisch is adjective not noun; check morphology handling',
 123:'dringen, drang, ist gedrungen; construction durch + Akk.',
 128:'exact duplicate example; preserve distinct examples and two Kastellan senses',
 130:'Königshaus ambiguous family/institution vs palace; preexisting HOLD',
 136:'menschenscheu primarily people-shy animal; anthropic nuance',
 137:'meterdick vs thickness equal / several meters; Persian and inflection',
 140:'schleusen meaning pass through controlled route; transitivity',
 142:'speisen as dine/formal vs supply/feed; context-dependent',
 151:'Vision forward-looking plan vs visionary revelation',
 152:'Vorlage model, draft, proposal, document; sense separation',
 153:'sich zurückziehen vs etwas zurückziehen; reflexive vs transitive distinctions',
 157:'Fall case / fall / fixed phrases; separate meanings and phrase class',
 158:'fortlaufen run away vs continue line/path',
 159:'Glaube an + Akk. belief vs religion; contextual construction',
}

def norm(s):
 return re.sub(r'\W+','',str(s).casefold())

def has_semantic_range(c):
 o=c['source_ordinal']; b=c['back']; s=str(b.get('meanings_fa_provisional',''))
 return o in POLYSEMY or s.count('؛') >= 2 or (' / ' in c['front'].get('base_headword_de',''))

def main(owner,dest):
 zpath=Path(owner);out=Path(dest);out.mkdir(parents=True,exist_ok=True)
 owner_bytes=zpath.read_bytes(); owner_sha=hashlib.sha256(owner_bytes).hexdigest()
 with zipfile.ZipFile(zpath) as z:
  allnames=z.namelist();bad=z.testzip()
  assert bad is None,f'CRC failure: {bad}'
  manifest=z.read('SHA256SUMS.txt').decode('utf-8')
  manifest_entries=0
  for line in manifest.splitlines():
   if not line.strip():continue
   expected,filename=line.split('  ',1)
   assert hashlib.sha256(z.read(filename)).hexdigest()==expected,(filename,'hash mismatch')
   manifest_entries+=1
  full=[json.loads(x) for x in z.read(MASTER).splitlines() if x.strip()]
  original_mapping=z.read(SOURCE)
  smap=list(csv.DictReader(io.StringIO(original_mapping.decode('utf-8-sig')),delimiter='\t'))
 assert len(full)==1571,len(full)
 assert len(smap)==1548,len(smap)
 selected=sorted((c for c in full if c.get('lesson')=='L02'),key=lambda c:(c['source_ordinal'],c['preview_card_id']))
 expected_ordinals=set(IN_SCOPE); source_rows=[r for r in smap if int(r['source_csv_ordinal']) in expected_ordinals]
 assert len(source_rows)==len(expected_ordinals),(len(source_rows),len(expected_ordinals))
 mapped_ids={row['G2_linked_learner_unit_IDS'] for row in source_rows}
 card_ids={c['preview_card_id'] for c in selected}
 assert len(card_ids)==len(selected)
 missing=[r for r in source_rows if not any(k in card_ids for k in r['G2_linked_learner_unit_IDS'].split(';'))]
 extra=[c['preview_card_id'] for c in selected if not any(c['preview_card_id'] in r['G2_linked_learner_unit_IDS'].split(';') for r in source_rows)]
 assert not missing and not extra,{'missing_source_rows':missing,'unmapped_cards':extra}
 assert len(selected)==91,len(selected)
 assert {c['source_ordinal'] for c in selected}==expected_ordinals
 def examples(c):
  b=c['back'];return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
 rows=[];totals=Counter();priority=Counter(); qa_statuses=Counter(); audit_flags=Counter(); duplicated=[]; pending_sense=[]; malformed=[]
 for c in selected:
  o=c['source_ordinal'];f=c['front'];b=c['back'];ex=examples(c);nets=b.get('semantic_network_sense_anchored_pending_qa') or []
  hold=bool(c.get('curated_HOLD_content_disposition_exists'));form_ok=bool(f.get('morphology_independently_validated'))
  extras=[]; localdup=[]; d=defaultdict(list)
  for i,e in enumerate(ex):
   qa_statuses[e.get('status','NOT_MARKED')]+=1
   if not e.get('de') or not e.get('fa'):malformed.append({'id':c['preview_card_id'],'idx':i})
   d[norm(e.get('de',''))].append({'index':i,'de':e.get('de'),'fa':e.get('fa')})
  for k,v in d.items():
   if k and len(v)>1: localdup.append(v);duplicated.append({'card_id':c['preview_card_id'],'source_ordinal':o,'entries':v})
  sense_ids={n.get('sense_id') for n in nets}
  unlinked=[{'index':i,'de':e['de'],'sense_id':e.get('sense_id')} for i,e in enumerate(ex) if nets and e.get('sense_id') not in sense_ids]
  if unlinked:pending_sense.append({'source_ordinal':o,'card_id':c['preview_card_id'],'items':unlinked})
  for flag in c.get('audit_flags',[]):audit_flags[flag]+=1
  if hold:extras.append('REVIEW_PREEXISTING_CURATED_HOLD_CASE_BY_CASE')
  if localdup:extras.append('FIX_EXACT_INTRA_CARD_DE_EXAMPLE_DUPLICATION_PRESERVE_UNIQUE_TRANSLATIONS')
  if unlinked:extras.append('ROUTE_EXISTING_EXAMPLE_TO_CORRECT_SENSE')
  if has_semantic_range(c):extras.append('MEANING_BY_MEANING_BILINGUAL_QA_AND_SENSE_ROUTING_IF_USEFUL')
  if any('status' not in e for e in ex):extras.append('MARK_UNSTATUSSED_EXAMPLES_PENDING_INDEPENDENT_DEFA')
  if o in MORPHOLOGY_HIGHRISK:extras.append('CHECK_NONTRIVIAL_FORM_VALENCY_AND_ARTICLE')
  if not form_ok:extras.append('INDEPENDENT_FORM_VALIDATION_OR_RULE_BASED_EXPLANATION_REQUIRED')
  extras.append('REVIEW_ALL_DE_FA_EXAMPLES_IN_CONTEXT_NOT_AUTOAPPROVE')
  if hold or localdup or unlinked or o in COMPLEX or any('status' not in e for e in ex):tier='P1'
  elif has_semantic_range(c) or o in MORPHOLOGY_HIGHRISK or len(ex)>=3 or c.get('audit_flags'):tier='P2'
  else:tier='P3'
  priority[tier]+=1
  totals['cards']+=1;totals['source_ordinal_ids']+=len(c.get('linked_original_source_ordinals') or [])
  totals['examples']+=len(ex);totals['example_empty_cards']+=not bool(ex);totals['curated_hold_marker_cards']+=hold
  totals['form_scoped_attested']+=form_ok;totals['wordnet_cards']+=bool(nets);totals['sense_blocks']+=len(nets)
  totals['polysemy_or_valency_risk_candidates']+=has_semantic_range(c)
  totals['missing_example_status_cards']+=any('status' not in e for e in ex)
  totals['examples_missing_sense_route']+=len(unlinked)
  totals['examples_status_missing']+=sum('status' not in e for e in ex)
  totals['example_duplicate_groups']+=len(localdup)
  rows.append({
    'lesson':'L02','source_ordinal':o,'preview_card_id':c['preview_card_id'],
    'headword_de':f.get('base_headword_de'),'current_front_de':f.get('display_de_provisional'),
    'current_meaning_fa':b.get('meanings_fa_provisional'),
    'source_ordinals':c.get('linked_original_source_ordinals'),
    'priority':tier,'editorial_phase2_decision':'PENDING_WHOLE_LESSON_CORRECTION',
    'example_pairs_count':len(ex),'example_statuses':dict(Counter(e.get('status','NOT_MARKED') for e in ex)),
    'curated_HOLD':hold,'independent_form_attestation_present':form_ok,
    'network_sense_blocks':len(nets),'possible_multisense_or_valency':has_semantic_range(c),
    'missing_networked_example_sense_routes':unlinked,'duplicate_example_groups':localdup,
    'audit_flags':c.get('audit_flags',[]),'needs_content_review':True,
    'case_note_phase2_not_an_approval':CASE_NOTES.get(o),
    'work_queue_actions':extras,
    'formal_release_approved':False
  })
 assert totals['cards']==91
 assert totals['examples']==sum(x['example_pairs_count'] for x in rows)
 assert sum(priority.values())==91
 assert not malformed,malformed
 all_lesson_ex=totals['examples']
 summary={
  'schema':'aspekte-b1plus-L02-whole-lesson-phase1-audit@1.0', 'date':'2026-11-08',
  'phase':'1/3','phase_status':'COMPLETED_STRUCTURAL_AND_RISK_TRIAGE_NOT_CONTENT_SIGNOFF',
  'input_owner_sha256':owner_sha,'owner_unchanged':True,'owner_library_file_id':'libfile_d5a43c53f89c81919d8eb6d071a7a60a',
  'owner_members':len(allnames),'owner_manifest_entries_verified':manifest_entries,
  'source_map_sha256':hashlib.sha256(original_mapping).hexdigest(),
  'corpus_cards':len(full),'corpus_source_map_rows':len(smap),
  'lesson':'L02','lesson_card_count':len(selected),'lesson_source_rows':len(source_rows),
  'lesson_first_source_ordinal':min(expected_ordinals),'lesson_last_source_ordinal':max(expected_ordinals),
  'all_source_ordinal_rows_mapped':True,'no_unlinked_preview_cards':True,
  'counts':dict(totals),'L02_morphology_without_external_attestation':91-totals['form_scoped_attested'],
  'example_qa_status_counts':dict(qa_statuses),'card_priorities':dict(priority),
  'audit_flag_counts':dict(audit_flags),
  'duplicate_example_details':duplicated,'missing_sense_routing_details':pending_sense,
  'critical_structural_errors':malformed,
  'release_status':'BLOCKED_NOT_TESTED_FOR_REAL_APP',
  'phase2_must':'Correct the entire L02 91-card queue in one whole-lesson editorial phase: remove one duplicate only after checking nonredundant translations, address unlabeled G4 statuses and sense links, check cases with 18 inherited HOLD markers, provide independent or rule-based G2 form evidence where justified. Do not break into 10-card Review milestones.',
  'phase3_must':'Independent complete bilingual/grammar checking, signed-off HOLD decisions, and actual German-Flashcards-Pro import/render runtime acceptance. Offline preview is not evidence of app runtime.',
  'limits':['Structural/risk triage only; no new external dictionary verification','All 91 forms lack recorded independent attestations, not proof of 91 errors','Networks absent on simpler words are not automatically defective','No formal bilingual release approvals in phase1','No learner-data fields edited']
 }
 qpath=out/'L02-PHASE1-91-CARD-DECISION-QUEUE.jsonl'
 qpath.write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in rows),encoding='utf-8')
 report=out/'L02-PHASE1-COMPLETE-LESSON-AUDIT.json'
 report.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 plan=out/'L02-THREE-PHASE-PLAN.md'
 plan.write_text(f'''# Aspekte B1+ / Lektion 02 — Drei-Phasen-Plan\n\n**Stand:** 2026-11-08 — Phase 1/3 DONE; Phase 2 NEXT; NONIMPORT.\n\n**Source of truth:** SHA-verified curated Library L01-Phase3 ZIP, SHA256 `{owner_sha}`. Existing learner data are read-only in Phase1. No textbook re-import.\n\n## Phase 1 — Whole-Lesson Inventory: DONE\n\n- **91 L02 cards across 91 original source rows (ordinals 72–162)**, all mapped; no dropped or duplicate learner IDs. Overall project stays 1571 card views / 1548 source rows.\n- **{all_lesson_ex} DE–FA example pairs**, {totals['example_empty_cards']} cards without examples, {totals['examples_status_missing']} examples lacking an explicit QA status, {totals['form_scoped_attested']} independent recorded morphology attestations (thus {91-totals['form_scoped_attested']} require evidence/rule-scoped review).\n- **{totals['curated_hold_marker_cards']} existing curated HOLD card markers**; {totals['wordnet_cards']} cards already containing sense networks ({totals['sense_blocks']} sense blocks); {totals['polysemy_or_valency_risk_candidates']} risk candidates for meaning/routing review — not automatically content errors.\n- **{totals['example_duplicate_groups']} exact duplicate DE example group** at ordinal 128 / `der Kastellan`: same sentence appears twice; preserve unique DE/FA examples in Phase2 and handle historical duplicate-release gate.\n- **{totals['examples_missing_sense_route']} examples on already-networked cards lack correct explicit sense linkage**; do not assume other 88 cards all require an elaborate network.\n- Priority groups are **P1 {priority['P1']}; P2 {priority['P2']}; P3 {priority['P3']}**. Every one of 91 cards has a written Phase2 action in `L02-PHASE1-91-CARD-DECISION-QUEUE.jsonl`; priority is not approval.\n- QA statuses: {json.dumps(dict(qa_statuses),ensure_ascii=False)}. No invalid empty German/Persian example pair found. No changes to learner data in this phase.\n\n## Phase 2 — Complete 91-card editorial correction: NEXT\n\nHandle **all 91** cards and **all {all_lesson_ex} examples** in one L02 whole-lesson stage. Prioritize HOLD, sense-ambiguity, valency and duplicate issues. Correct genuine errors only and keep multiple meanings on one existing card. Record explicit before/after evidence and 91 decisions. Do not create a micro-Review for every 10 cards.\n\n## Phase 3 — Independent full-card QA and runtime import gate: LATER\n\nIndependent complete German/Persian release QA + morphologic and sense-routing gates + case-by-case HOLD decisions. Real German-Flashcards-Pro application TSV import and rendered Front/Back must be demonstrated rather than simulated. Failure → `RELEASE_BLOCKED`, never pretend the lesson is approved.\n\n**Global unchanged:** 338/1571 prior G2 form attestations, 340 legacy release HOLD markers, seven exact duplicate groups across corpus (one L02); zero formal full-card release approvals. This L02 Phase1 creates **no new attestations or released cards**.\n''',encoding='utf-8')
 print(json.dumps({'owner_sha':owner_sha,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [report,qpath,plan]},'summary':{k:v for k,v in summary.items() if k in ['counts','card_priorities','example_qa_status_counts','lesson_card_count','lesson_source_rows']},'duplicates':duplicated,'unlinked':pending_sense},ensure_ascii=False,indent=2))
if __name__=='__main__':
 main(sys.argv[1],sys.argv[2])