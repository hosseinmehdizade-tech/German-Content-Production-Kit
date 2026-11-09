#!/usr/bin/env python3
"""Aspekte B1+ L08 Phase3: scoped Duden-backed corrections, all-157-card QA, strict fail-closed release gate.
Reads exact Phase2 pinned owner, never reimports publisher CSV. Does not claim external human or full semantic signoff.
"""
import collections,copy,csv,hashlib,html,importlib.util,io,json,re,zipfile
from pathlib import Path
P=Path('/mnt/data/aspekte_b1plus_l08_phase2/Aspekte-B1plus-L08-PHASE2-WHOLE-157-CARDS-CURATED-NONIMPORT-20261109.zip')
OUTDIR=Path('/mnt/data/aspekte_b1plus_l08_phase3')
OUT=OUTDIR/'Aspekte-B1plus-L08-PHASE3-157-CARD-QUALITY-GATE-RELEASE-BLOCKED-NONIMPORT-20261109.zip'
EXPECTED='10eb382da2a246ada7cdbac31dc15ea4ec1cc75dbcf7d3102f9f450ecfeac5f5'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAPPING='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
EXPECTED_MAIN='689dda1db5ef43e1f0174ad65643393cfe535fa67b35e3dacbcb3cfaad26028c'
EXPECTED_MAP='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
DATE='2026-11-09'
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(o):return (json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
def norm(s):return ' '.join(str(s).casefold().split())
def es(c):
 b=c['back'];return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
def mod(name):
 p=Path('/mnt/data/aspekte_b1plus_l08_phase2')/(name+'.py')
 s=importlib.util.spec_from_file_location(name,p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v);return v
strict=mod('qa_combinationen_strict_v2');finite=mod('qa_combinationen_finite_clause_v4');htmlmod=mod('qa_front_back_sense_examples_v4')
# Exact original front display guard prevents rewriting unanticipated collaborator changes.
CORRECTIONS={
1000: {'expected_front':'der Eiskasten, -kästen (österr.: Kühlschrank)',
       'new_front':'der Eiskasten, die Eiskästen (südd., österr., veraltend: Kühlschrank)',
       'expected_fa':'یخچال (کاربرد رایج در اتریش)',
       'new_fa':'یخچال (کاربرد قدیمی‌شونده در اتریش و جنوب آلمان)',
       'url':'https://www.duden.de/rechtschreibung/Eiskasten','scope':'regional_usage_and_definition_NOT_PLURAL_ATTESTATION'},
1007: {'expected_front':'etw. entfernen; entfernte, hat entfernt',
       'new_front':'entfernen – entfernt – entfernte – hat entfernt; etw. entfernen',
       'url':'https://www.duden.de/rechtschreibung/entfernen','scope':'THIRD_PERSON_PRETERITE_PERFEKT'},
1008: {'expected_front':'ertönen; ertönte; Partizip II: ertönt',
       'new_front':'ertönen – ertönt – ertönte – ist ertönt',
       'url':'https://www.duden.de/rechtschreibung/ertoenen','scope':'THIRD_PERSON_PRETERITE_AUXILIARY_PARTICIPLE'},
1040: {'expected_front':'beurteilen, beurteilte, beurteilt',
       'new_front':'beurteilen – beurteilt – beurteilte – hat beurteilt; jdn./etw. beurteilen',
       'url':'https://www.duden.de/konjugation/beurteilen','scope':'THIRD_PERSON_PRETERITE_PERFEKT'},
1091: {'expected_front':'servieren, servierte, serviert',
       'new_front':'servieren – serviert – servierte – hat serviert',
       'url':'https://www.duden.de/rechtschreibung/servieren','scope':'THIRD_PERSON_PRETERITE_PERFEKT'},
1145: {'expected_front':'subventionieren, subventionierte, subventioniert',
       'new_front':'subventionieren – subventioniert – subventionierte – hat subventioniert',
       'url':'https://www.duden.de/rechtschreibung/subventionieren','scope':'THIRD_PERSON_PRETERITE_PERFEKT'},
1153: {'expected_front':'wehen, wehte, geweht',
       'new_front':'wehen – weht – wehte – hat/ist geweht (bedeutungs- und gebrauchsabhängig)',
       'url':'https://www.duden.de/konjugation/wehen','scope':'THIRD_PERSON_PRETERITE_PARTICIPLE_TWO_AUXILIARIES_WITH_USAGE_SCOPE'}
}

def case_qa(c):
 b=c['back'];f=c['front'];examples=es(c);nets=b.get('semantic_network_sense_anchored_pending_qa') or []
 ids=[n.get('sense_id') for n in nets];idset=set(ids)
 errors=[];risks=[];flags=[]
 if not isinstance(f.get('base_headword_de'),str) or not f['base_headword_de'].strip():errors.append('EMPTY_HEADWORD')
 if not f.get('display_de_provisional'):errors.append('EMPTY_FRONT')
 if b.get('Formen_section') is not None:errors.append('DUPLICATED_FORMEN_BACK')
 if not b.get('meanings_fa_provisional','').strip():errors.append('EMPTY_PERSIAN_MEANING')
 if not examples:errors.append('NO_EXAMPLE')
 if any(not isinstance(e.get('de'),str) or not e['de'].strip() or not isinstance(e.get('fa'),str) or not e['fa'].strip() for e in examples):errors.append('EMPTY_BILINGUAL_EXAMPLE')
 if any(not e.get('status') for e in examples):errors.append('MISSING_EXAMPLE_STATUS')
 if len(ids)!=len(idset):errors.append('DUPLICATED_SENSE_IDS')
 if nets and any(e.get('sense_id') not in idset for e in examples):errors.append('UNLINKED_EXAMPLE_TO_SENSE')
 if any(not n.get('sense_de') or not n.get('sense_fa') for n in nets):errors.append('EMPTY_SENSE_PAIR')
 if any(not co.get('de') or not co.get('fa') for n in nets for co in (n.get('Kombinationen_DE_FA') or [])):errors.append('EMPTY_COMBINATION_PAIR')
 if any(v for v in (b.get('Formen_section'),) if v):errors.append('REDUNDANT_FORMS_IN_BACK')
 if c.get('formal_release_approved') or c.get('import_ready'):errors.append('PREMATURE_RELEASE_FLAG')
 dups={norm(e['de']) for e in examples if sum(norm(z['de'])==norm(e['de']) for z in examples)>1}
 if dups:errors.append('SAME_CARD_EXACT_DE_EXAMPLE_DUPLICATES')
 if c.get('curated_HOLD_content_disposition_exists'):risks.append('INHERITED_CONTENT_HOLD')
 if not f.get('morphology_independently_validated'):risks.append('FORM_SCOPE_NOT_ATTESTED_IN_CURRENT_CARD')
 if any('PENDING' in str(e.get('status','')) for e in examples):risks.append('BILINGUAL_EXAMPLES_PENDING_FINAL_MEANING_REVIEW')
 if any('PENDING' in str(n.get('status','')) for n in nets):risks.append('SENSE_RELATION_MEANING_PENDING_FINAL_REVIEW')
 if len(nets)>1:flags.append('POLYSEMY_MEANINGS_ONE_CARD')
 if len(set(c['linked_original_source_ordinals']))!=len(c['linked_original_source_ordinals']):errors.append('DUPLICATE_SOURCE_LINKS')
 # Check meaningful semantics only when explicit scoped dictionary proof exists; never infer correctness from validator success.
 return {'card_id':c['preview_card_id'],'source_ordinal':c['source_ordinal'],'lemma':f['base_headword_de'],
         'linked_original_source_ordinals':c['linked_original_source_ordinals'],'examples':len(examples),'senses':len(nets),
         'combinations':sum(len(n.get('Kombinationen_DE_FA') or []) for n in nets),
         'critical_structural_errors':errors,'remaining_release_risks':risks,'special_flags':flags,
         'scoped_duden_attestation':f.get('L08_phase3_scoped_Duden_evidence'),
         'verified_now':'CASE_LEVEL_STRUCTURE_AND_REPLAYABLE_REGRESSION',
         'not_verified_now':'COMPLETE_BILINGUAL_GRAMMAR_COLLOCATION_IDIOMATICITY_AND_LIVE_APP_RUNTIME',
         'phase3_release_gate':'RELEASE_BLOCKED_NONIMPORT', 'full_card_language_approved':False}

def validate_card_error_tests(l08):
 c=copy.deepcopy(l08[0]);c['back']['Formen_section']='DUPLICATE';assert 'DUPLICATED_FORMEN_BACK' in case_qa(c)['critical_structural_errors']
 c=copy.deepcopy(l08[0]);c['back']['existing_examples_de_fa_pending_qa'][0]['fa']='';assert 'EMPTY_BILINGUAL_EXAMPLE' in case_qa(c)['critical_structural_errors']
 c=copy.deepcopy(l08[0]);c['import_ready']=True;assert 'PREMATURE_RELEASE_FLAG' in case_qa(c)['critical_structural_errors']
 c=copy.deepcopy(l08[0]);c['back']['existing_examples_de_fa_pending_qa'].append(copy.deepcopy(c['back']['existing_examples_de_fa_pending_qa'][0]));assert 'SAME_CARD_EXACT_DE_EXAMPLE_DUPLICATES' in case_qa(c)['critical_structural_errors']
 c=copy.deepcopy(next(a for a in l08 if a['back'].get('semantic_network_sense_anchored_pending_qa')));es(c)[0]['sense_id']='INVALID_SENSE_ID';assert 'UNLINKED_EXAMPLE_TO_SENSE' in case_qa(c)['critical_structural_errors']
 c=copy.deepcopy(l08[0]);es(c)[0]['status']='';assert 'MISSING_EXAMPLE_STATUS' in case_qa(c)['critical_structural_errors']
 return {'negative_tests':6,'all_expected_rejections':True,'scope':'SCOPED_STRUCTURAL_GUARDS_ONLY'}

def build():
 assert sha(P.read_bytes())==EXPECTED,'Incorrect parent owner'
 with zipfile.ZipFile(P) as z:
  assert z.testzip() is None
  original={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
  for line in z.read('SHA256SUMS.txt').decode('utf8').splitlines():
   digest,name=line.split('  ',1);assert sha(z.read(name))==digest,name
 assert sha(original[MAIN])==EXPECTED_MAIN and sha(original[MAPPING])==EXPECTED_MAP
 before=[json.loads(x) for x in original[MAIN].splitlines()]
 cards=copy.deepcopy(before);l08=[c for c in cards if c['lesson']=='L08'];assert len(l08)==157
 assert sum(1 for c in l08 if c.get('curated_HOLD_content_disposition_exists'))==38
 before_byid={c['preview_card_id']:c for c in before}
 diff={};attestation=[]
 for c in l08:
  o=c['source_ordinal'];fix=CORRECTIONS.get(o)
  if fix:
   assert c['front']['display_de_provisional']==fix['expected_front'],(o,c['front']['display_de_provisional'])
   c['front']['display_de_provisional']=fix['new_front']
   if 'new_fa' in fix:
    assert c['back']['meanings_fa_provisional']==fix['expected_fa']
    c['back']['meanings_fa_provisional']=fix['new_fa']
   # This attests ONLY listed grammatical/usage scope, never the entire bilingual card or all senses.
   c['front']['L08_phase3_scoped_Duden_evidence']={'source_url':fix['url'],'verified_scope':fix['scope'],'date':DATE,
                                                     'full_card_approved':False}
   if o!=1000:
    c['front']['morphology_independently_validated']=True
    c['front']['morphology_origin']='L08_PHASE3_SCOPED_DUDEN_FORMS__NOT_FULL_CARD'
   diff[c['preview_card_id']]={'ordinal':o,'lemma':c['front']['base_headword_de'],
                             'front_before':before_byid[c['preview_card_id']]['front'], 'front_after':copy.deepcopy(c['front']),
                             'meanings_before':before_byid[c['preview_card_id']]['back']['meanings_fa_provisional'],
                             'meanings_after':c['back']['meanings_fa_provisional'],'scope':fix['scope'],'source_url':fix['url']}
   attestation.append({'ordinal':o,'lemma':c['front']['base_headword_de'],'scope':fix['scope'],'url':fix['url']})
 assert len(diff)==7
 case_rows=[case_qa(c) for c in l08]
 assert len(case_rows)==157 and len({r['card_id'] for r in case_rows})==157
 structural_issues=[r for r in case_rows if r['critical_structural_errors']]
 assert not structural_issues,structural_issues[:3]
 neg=validate_card_error_tests(l08)
 assert len(cards)==1571 and len({c['preview_card_id'] for c in cards})==1571
 assert all(before_byid[c['preview_card_id']]==c for c in cards if c['lesson']!='L08')
 actual={c['preview_card_id'] for c in cards if c!=before_byid[c['preview_card_id']]}
 assert actual==set(diff),actual.symmetric_difference(diff)
 assert all(c['linked_original_source_ordinals']==before_byid[c['preview_card_id']]['linked_original_source_ordinals'] for c in cards)
 # Original 1085+1086 merge and 1142 split never modified.
 assert len({c['source_ordinal'] for c in l08})==156
 assert len([c for c in l08 if c['source_ordinal']==1142])==2
 assert any(c['linked_original_source_ordinals']==[1085,1086] for c in l08)
 combos=strict.audit(cards);finite_report=finite.audit(cards)
 assert combos['structural_gate_passed'] and combos['combinations_scanned']==870,combos
 assert finite_report['possible_full_sentence_collocations']==3
 assert not [x for x in finite_report['issues'] if x['lesson']=='L08']
 assert sum(len(es(c)) for c in l08)==357
 assert all(c['formal_release_approved'] is False and c['import_ready'] is False for c in l08)
 htmlreport,htmlcards=htmlmod.qa(l08,lesson='L08')
 assert htmlreport['pass'] and htmlreport['counts']['examples']==357 and len(htmlcards)==157,htmlreport
 doc='<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Aspekte B1+ Lektion 08 Phase 3 QA-only</title><style>body{font:15px system-ui;max-width:1160px;margin:20px auto;line-height:1.45}.card{border:1px solid #ccd;padding:12px;margin:10px 0}.front{background:#eee;padding:6px}.fa{display:block;direction:rtl;text-align:right;color:#456}li{margin:8px}.sense{border-top:1px solid #bbc;margin-top:12px}</style></head><body><h1>Aspekte B1+ · Lektion 08 · Phase 3 (QA ONLY)</h1><p>157 cards; zero full-card releases; never real app rendering.</p>'+''.join(a for c,a in htmlcards)+'</body></html>'
 # Serialize only seven real data edits, with bit-exact preservation of the 1564 other primary JSONL lines.
 all_lines=original[MAIN].splitlines();outlines=[]
 for prior,updated,old_line in zip(before,cards,all_lines):
  outlines.append(json.dumps(updated,ensure_ascii=False,sort_keys=True).encode('utf8') if prior!=updated else old_line)
 main_bytes=b'\n'.join(outlines)+b'\n'
 assert sha(main_bytes)!=EXPECTED_MAIN and len(main_bytes.splitlines())==1571
 total_ex=sum(len(es(c)) for c in cards)
 riskcounts=collections.Counter(r for row in case_rows for r in row['remaining_release_risks'])
 report={'schema':'aspekte-b1plus-L08-phase3-strict-case-level-quality-gate@1','date':DATE,
  'status':'PHASE3_EVALUATED_RELEASE_BLOCKED_NONIMPORT','lesson':'L08','phase':3,'phases_total':3,
  'coverage':{'case_level_card_ledger':len(case_rows),'L08_examples':357,'L08_combinations':68,'global_combinations':870,
     'primary_card_objects_changed':7,'other_lesson_objects_unchanged':1414,'unchanged_L08_objects':150,
     'all_1571_ids_preserved':True,'all_1548_source_map_rows_preserved':True,
     'L08_statusless_examples':0,'L08_unrouted_network_examples':0,'L08_duplicate_example_groups':0,
     'inherited_L08_HOLDs':38,'case_level_critical_structural_errors':len(structural_issues),
     'case_level_release_risk_counts':dict(riskcounts),'scope_attestations':len(attestation),
     'negative_regression_tests':neg,'html_offline_example_routing_qa':'PASS_157_CARDS_357_EXAMPLES',
     'full_card_linguistically_signed_off':0,'actual_app_runtime_imports':0},
  'provenance':{'parent_zip_sha256':EXPECTED,'parent_main_sha256':EXPECTED_MAIN,'new_main_sha256':sha(main_bytes),
      'source_map_sha256':EXPECTED_MAP,'reused_external_textbook':False},
  'global_regression':{'strict_v2':'PASS', 'finite_clause_v4':'FAIL_3_EXISTING_OUTSIDE_L08',
                       'global_finite_clause_candidates':finite_report['issues'],
                       'exact_same_card_example_duplicates_other_lessons':'L09_1157_STILL_OPEN'},
  'release':{'status':'RELEASE_BLOCKED_NONIMPORT','reason':['38_INHERITED_L08_CURATED_HOLDS','CASE_LEVEL_FULL_BILINGUAL_SEMANTIC_SIGNOFF_UNPROVEN',
       'REAL_GERMAN_FLASHCARDS_PRO_IMPORT_RENDER_NOT_RUN','3_GLOBAL_FINITE_CLAUSE_V4_CANDIDATES_OUTSIDE_L08',
       '1_GLOBAL_DUPLICATE_EXAMPLE_GROUP_OUTSIDE_L08'],
       'app_import_tested':False,'actual_app_runtime_access':'NOT_AVAILABLE_IN_THIS_SESSION',
       'formal_approved_cards':0,'approved_release':False},
  'next':'L09_PHASE1_WHOLE_LESSON__PRESERVE_GLOBAL_BLOCKER_BACKLOG_AND_FAIL_CLOSED_RELEASE',
  'limitations':['Structured per-card checking is not proof that all DE/FA examples or collocations are idiomatic and correct',
      'No external human review is required or claimed','No historical QA projection is evidence of real app imports']}
 # Insert QA results into owner archive; explicit basename leaves older historical artifacts intact but non-authoritative.
 updated={MAIN:main_bytes,
          'Lessons/L08/L08-PHASE3-157-CARD-CASE-QA-RELEASE-BLOCKERS.jsonl':b''.join((json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n').encode('utf8') for r in case_rows),
          'Lessons/L08/L08-PHASE3-7-SCOPED-DUDEN-EDIT-EVIDENCE.json':enc(diff),
          'Lessons/L08/L08-PHASE3-SCOPED-DUDEN-CHECKS.json':enc(attestation),
          'Lessons/L08/L08-PHASE3-157-CARD-QUALITY-REPORT.json':enc(report),
          'Lessons/L08/L08-PHASE3-GLOBAL-FINITE-V4.json':enc(finite_report),
          'Lessons/L08/L08-PHASE3-STRICT-COMBOS-V2.json':enc(combos),
          'Lessons/L08/L08-PHASE3-HTML-OFFLINE-QA-ONLY.html':doc.encode('utf8'),
          'README-L08-PHASE3-NONIMPORT.md':(f'# Aspekte B1+ L08 Phase 3 — RELEASE BLOCKED / NONIMPORT\n\nSource owner SHA256 {EXPECTED}. 157 card QA ledgers, seven real scoped Duden-backed edits, 38 HOLDs remain. Case-level structural and bounded dictionary checks only; not 157 full bilingual approvals. No real app import. Next: L09 Phase1 whole lesson.\n').encode()}
 for key,v in updated.items():original[key]=v
 OUTDIR.mkdir(exist_ok=True)
 with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for key,v in sorted(original.items()):z.writestr(key,v)
  sums=''.join(sha(v)+'  '+key+'\n' for key,v in sorted(original.items())).encode()
  z.writestr('SHA256SUMS.txt',sums)
 with zipfile.ZipFile(OUT) as z:
  assert z.testzip() is None
  lines=z.read('SHA256SUMS.txt').decode().splitlines();assert len(lines)==len(z.namelist())-1
  for line in lines:
   digest,name=line.split('  ',1);assert digest==sha(z.read(name)),name
  actual_cards=[json.loads(x) for x in z.read(MAIN).splitlines()]
  assert len(actual_cards)==1571 and sha(z.read(MAPPING))==EXPECTED_MAP
  assert {c['preview_card_id'] for c in actual_cards}=={c['preview_card_id'] for c in before}
  assert {c['preview_card_id'] for c in actual_cards if c!=before_byid[c['preview_card_id']]}==set(diff)
  r=json.loads(z.read('Lessons/L08/L08-PHASE3-157-CARD-QUALITY-REPORT.json'))
  assert r['release']['status']=='RELEASE_BLOCKED_NONIMPORT'
 receipt={'schema':'aspekte-b1plus-L08-phase3-archive-verified@1','date':DATE,'status':'PHASE3_COMPLETE_RELEASE_BLOCKED_NONIMPORT',
          'owner_archive_sha256':sha(OUT.read_bytes()),'size_bytes':OUT.stat().st_size,
          'zip_members':len(original)+1,'manifest_verified_members':len(original),
          'primary_main_sha256':sha(main_bytes),'source_map_sha256':EXPECTED_MAP,
          'parent_owner_sha256':EXPECTED,'case_cards':157,'changed_saved_primary_card_objects':7,
          'unchanged_outside_L08':1414,'new_release_approvals':0,'app_runtime_tested':False,
          'global_v4_finite_clause_fail_count':3,'next':'L09_PHASE1_WHOLE_LESSON'}
 (OUTDIR/'L08-PHASE3-VERIFICATION.json').write_bytes(enc(receipt))
 (OUTDIR/'L08-PHASE3-REPORT.json').write_bytes(enc(report))
 (OUTDIR/'L08-PHASE3-7-EDITS.json').write_bytes(enc(diff))
 (OUTDIR/'L08-PHASE3-157-CASES.jsonl').write_bytes(updated['Lessons/L08/L08-PHASE3-157-CARD-CASE-QA-RELEASE-BLOCKERS.jsonl'])
 print(json.dumps({'receipt':receipt,'report':report},ensure_ascii=False,indent=2))
if __name__=='__main__':build()