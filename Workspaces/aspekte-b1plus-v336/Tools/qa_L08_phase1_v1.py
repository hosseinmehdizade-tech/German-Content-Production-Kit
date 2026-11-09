#!/usr/bin/env python3
"""Aspekte B1+ L08: deterministic, non-mutating whole-lesson audit, 157 cards.

Run: python qa_L08_phase1_v1.py OWNER.zip [OUTPUT_DIR]
This is an evidence/triage audit, NOT a full linguistic signoff or owner rewrite.
"""
from __future__ import annotations
import collections, hashlib, html, json, re, sys, zipfile
from pathlib import Path

MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
DATE='2026-11-09'

def sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def write_json(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def norm(s): return re.sub(r'\W+','',str(s).casefold())
def examples(c):
 b=c['back']
 return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
def nets(c): return c['back'].get('semantic_network_sense_anchored_pending_qa') or []
def duplicates(cards):
 found=[]
 for c in cards:
  groups=collections.defaultdict(list)
  for i,e in enumerate(examples(c)):
   if e.get('de'): groups[norm(e['de'])].append((i,e))
  for key,entries in groups.items():
   if key and len(entries)>1:
    found.append({'lesson':c['lesson'],'source_ordinal':c['source_ordinal'],
                  'card_id':c['preview_card_id'],'headword':c['front']['base_headword_de'],
                  'normalized_German':key,'de_variants':[e['de'] for _,e in entries],
                  'fa_variants':[e['fa'] for _,e in entries],
                  'editorial_policy':'Merge DE duplicates only after comparing meanings and retaining useful Persian variants; no change in Phase1'})
 return found

def finite_clause(cards):
 DETERMINERS={'der','die','das','ein','eine','einen','einem','einer','diese','dieser','dieses','jener','jene'}
 FINITE={'reicht','entscheidet','koordiniert','läuft','prüft','schreibt','bringt','bestimmt','öffnet','organisiert','führt','hat','ist','sind','steht','arbeitet','verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt','hält','macht','kann','wird','werden','nimmt','bietet','spricht'}
 issues=[];total=0;per_lesson=collections.Counter()
 for c in cards:
  for n in nets(c):
   for x in n.get('Kombinationen_DE_FA',[]) or []:
    total+=1;per_lesson[c['lesson']]+=1
    w=re.findall(r'\w+',x.get('de',''),re.UNICODE)
    if len(w)>=4 and w[0].casefold() in DETERMINERS and w[1][0].isupper() and w[2].casefold() in FINITE:
     issues.append({'lesson':c['lesson'],'ordinal':c['source_ordinal'],'headword':c['front']['base_headword_de'],
                    'de':x['de'],'reason':'KNOWN_SIMPLE_NP_PLUS_FINITE_VERB_PATTERN',
                    'action':'Replace with a true collocation, or put full sentence in Beispiele after DE–FA editorial review'})
 return {'schema':'aspekte-b1plus-l08-v4-combinations-diagnostic@1','global_cards_scanned':len(cards),
         'combinations_scanned':total,'by_lesson':dict(sorted(per_lesson.items())),
         'issues':issues,'count':len(issues),'strict_corpus_pass':not issues,
         'scope':'Known pattern only; a pass is NOT a full semantic-naturalness certificate'}

def main(owner:Path,out:Path):
 assert owner.exists(),f'NOT_FOUND:{owner}'
 out.mkdir(parents=True,exist_ok=True)
 owner_sha=sha(owner.read_bytes())
 assert owner_sha=='14841de70a121551121c6c1bced5cca987a659e006d0b225d980f302939dac81', 'Unexpected owner; never silently change inputs'
 with zipfile.ZipFile(owner) as z:
  assert z.testzip() is None,'SOURCE_ZIP_CRC_FAIL'
  manifest={name:digest for digest,name in (line.split('  ',1) for line in z.read('SHA256SUMS.txt').decode().splitlines() if line)}
  other={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
  assert set(manifest)==set(other) and all(sha(v)==manifest[k] for k,v in other.items()), 'SOURCE_MANIFEST_INVALID'
  raw=other[MAIN]; source_map=other[MAP].decode('utf-8-sig')
  cards=[json.loads(s) for s in raw.splitlines()]
 assert sha(raw)=='e979959fd3b10885ed8d05266e6c17101fb29302a9d626d606252aa9e684046e','PRIMARY_OWNER_SHA_MISMATCH'
 assert len(cards)==1571 and len({x['preview_card_id'] for x in cards})==1571,'CARD_IDENTITY_INVALID'
 assert len(source_map.splitlines())-1==1548,'SOURCE_ROW_COUNT_INVALID'
 lesson=[c for c in cards if c.get('lesson')=='L08']
 assert len(lesson)==157,'L08_CARD_COUNT_CHANGED'
 assert len({c['preview_card_id'] for c in lesson})==157,'L08_IDS_NOT_UNIQUE'
 assert all(x.get('import_ready') is False and x.get('formal_release_approved') is False for x in lesson),'UNEXPECTED_RELEASED_CARD'
 original_to_cards=collections.defaultdict(list)
 for c in lesson:
  for ordinal in c['linked_original_source_ordinals']:
   original_to_cards[ordinal].append({'card_id':c['preview_card_id'],'headword':c['front']['base_headword_de']})
 expected=set(range(1000,1157))
 assert set(original_to_cards)==expected, f'SOURCE_GAPS:{sorted(expected-set(original_to_cards))}'
 assert len(original_to_cards[1086])==1 and original_to_cards[1086][0]['headword']=='das Panorama'
 assert len(original_to_cards[1142])==2 and {x['headword'] for x in original_to_cards[1142]}=={'die Milliarde','die Billion'}
 assert len({o:c for o,c in original_to_cards.items() if len(c)>1})==1
 assert len({o:c for o,c in original_to_cards.items() if len(c)>0})==157
 original_map_rows={int(row.split('\t')[0]):row for row in source_map.splitlines()[1:]}
 assert all(row in original_map_rows for row in expected)
 assert all(set(x['card_id'] for x in original_to_cards[row])==set(original_map_rows[row].split('\t')[1].split(';')) for row in expected), 'SOURCE_MAPPING_LINK_MISMATCH'

 example_total=sum(len(examples(c)) for c in lesson)
 empty_examples=[c['preview_card_id'] for c in lesson if not examples(c)]
 blank_examples=[{'card_id':c['preview_card_id'],'index':i} for c in lesson for i,e in enumerate(examples(c)) if not e.get('de') or not e.get('fa')]
 missing_status=[{'card_id':c['preview_card_id'],'ordinal':c['source_ordinal'],'headword':c['front']['base_headword_de'], 'example_index':i,
                  'de':e.get('de',''),'fa':e.get('fa','')} for c in lesson for i,e in enumerate(examples(c)) if not e.get('status')]
 holds=[{'card_id':c['preview_card_id'],'ordinal':c['source_ordinal'],'headword':c['front']['base_headword_de']} for c in lesson if c['curated_HOLD_content_disposition_exists']]
 networked=[c for c in lesson if nets(c)]
 unlinked=[{'card_id':c['preview_card_id'],'ordinal':c['source_ordinal'],'headword':c['front']['base_headword_de'],
            'index':i,'de':e.get('de'),'fa':e.get('fa'),'candidate_senses':[{'sense_id':n.get('sense_id'),'de':n.get('sense_de'),'fa':n.get('sense_fa')} for n in nets(c)]}
           for c in networked for i,e in enumerate(examples(c)) if e.get('sense_id') not in {n.get('sense_id') for n in nets(c)}]
 duplicate=duplicates(lesson); global_dup=duplicates(cards)
 form_evidenced=[c['preview_card_id'] for c in lesson if c['front'].get('morphology_independently_validated')]
 independent_form_proposals=[{'ordinal':c['source_ordinal'],'headword':c['front']['base_headword_de'],
                              'evidence_status':c.get('G2_morphology_review',{}).get('status'),'dictionary_reference':c.get('G2_morphology_review',{}).get('dictionary_reference_url')}
                             for c in lesson if c.get('G2_morphology_review')]
 collocation_count=sum(len(n.get('Kombinationen_DE_FA',[]) or []) for c in lesson for n in nets(c))
 global_finite=finite_clause(cards)
 assert len(holds)==38 and len(missing_status)==38 and len(networked)==15 and len(unlinked)==31, 'MILESTONE_METRICS_MISMATCH'
 assert example_total==359 and not empty_examples and not blank_examples,'EXAMPLE_CORPUS_MISMATCH'
 assert len(duplicate)==1 and len(global_dup)==2 and len(form_evidenced)==0, 'BASELINE_REGRESSION'
 assert global_finite['combinations_scanned']==834 and len(global_finite['issues'])==3,'FINITE_GATE_CHANGED'

 # Phase1: assess all 157 cards without editing primary data.
 sensitive_heads={'umschreiben','das Leder','vermitteln','die Beschwerde','die Gutschrift','bestellen','abkaufen','die Milliarde','die Billion'}
 decisions=[]
 for c in lesson:
  e=examples(c); n=nets(c);missing=[i for i,x in enumerate(e) if not x.get('status')]
  ids={item.get('sense_id') for item in n}
  routes=[i for i,x in enumerate(e) if n and x.get('sense_id') not in ids]
  repeated=[g for g in duplicate if g['card_id']==c['preview_card_id']]
  flags=[];actions=[]
  if c.get('curated_HOLD_content_disposition_exists'):
   flags.append('INHERITED_CURATED_HOLD');actions.append('Re-evaluate HOLD with direct German–Persian semantic evidence; never auto-clear')
  if repeated:
   flags.append('EXACT_GERMAN_EXAMPLE_REPEATED');actions.append('Consolidate repeated German sentence after comparing Persian paraphrases; retain informative alternatives')
  if missing:
   flags.append('EXAMPLE_QA_STATUS_MISSING');actions.append('Mark status explicitly PENDING after checking scope; do not auto-approve')
  if routes:
   flags.append('EXAMPLE_TO_SENSE_LINK_MISSING');actions.append('Route examples to correct sense IDs after bilingual context check; never assign by order alone')
  if not c['front'].get('morphology_independently_validated'):
   flags.append('MORPHOLOGY_SCOPED_ATTESTATION_ABSENT');actions.append('Verify article/plural or verb forms only as relevant; absent evidence does not prove incorrect German')
  if c.get('G2_morphology_review'):
   flags.append('G2_FRONT_PROPOSAL_NOT_FINAL_ATTESTATION');actions.append('Adjudicate existing G2 form proposal, preserving distinction between proof of form and approval of whole card')
  if c['front']['base_headword_de'] in sensitive_heads:
   flags.append('SENSE_USAGE_MANUAL_DISAMBIGUATION_PRIORITY');actions.append('Check distinct meanings and grammatical valencies, preserving main then secondary senses in one card')
  if c['source_ordinal']==1085:
   flags.append('TWO_SOURCE_ROWS_CORRECTLY_MERGED');actions.append('Preserve source ordinals 1085 and 1086 in one Panorama card')
  if c['source_ordinal']==1142:
   flags.append('TWO_DIFFERENT_LEMMAS_CORRECTLY_SPLIT');actions.append('Keep Milliarde (10^9) and Billion (10^12) separate; no English billion conflation')
  if n:
   actions.append('Audit synonyms/antonyms/word families and every combination for idiomatic, sense-specific DE–FA usage')
  else:
   actions.append('Evaluate whether multi-sense network is needed; do not invent forced synonyms or antonyms')
  if not e:actions.append('Add at least one contextual bilingual example after independent QA')
  if repeated or missing or c['curated_HOLD_content_disposition_exists']:
   priority='P1'
  elif routes or c.get('G2_morphology_review') or c['front']['base_headword_de'] in sensitive_heads or len(e)>3:
   priority='P2'
  else:priority='P3'
  decisions.append({'card_id':c['preview_card_id'],'ordinal':c['source_ordinal'],'headword_de':c['front']['base_headword_de'],
    'front_display_de':c['front'].get('display_de_provisional'),'meanings_fa':c['back']['meanings_fa_provisional'],
    'priority':priority,'inherited_HOLD':bool(c.get('curated_HOLD_content_disposition_exists')),
    'morphology_independently_attested':bool(c['front'].get('morphology_independently_validated')),
    'example_count':len(e),'examples':e,'example_indices_missing_QA_status':missing,
    'sense_blocks':n,'unrouted_example_indices':routes,'duplicate_DE_example_groups':repeated,
    'linked_original_source_ordinals':c['linked_original_source_ordinals'],'risk_flags':flags,
    'phase2_actions':list(dict.fromkeys(actions)),'phase1_content_changed':False,
    'phase1_approval':'TRIAGED_NOT_LINGUISTICALLY_APPROVED','release_status':'BLOCKED_NONIMPORT'})
 assert len(decisions)==157
 dist=dict(collections.Counter(x['priority'] for x in decisions))

 report={'schema':'aspekte-b1plus-L08-phase1-whole-157-card-audit@1','date':DATE,
  'lesson':'L08','phase':1,'phases_total':3,'status':'WHOLE_LESSON_157_CARD_AUDIT_COMPLETE_NONIMPORT_NO_PRIMARY_DATA_EDITS',
  'source_authority':{'library_file_id':'libfile_4e8d3ac0eac481919bc8627f21f0f2bd','sha256':owner_sha,'bytes':owner.stat().st_size,
                      'primary_main_sha256':sha(raw),'original_1548_source_map_sha256':sha(other[MAP]),'source_archive_members':len(other)+1,'source_manifest_entries_verified':len(manifest),'CRC':'PASS'},
  'lesson_metrics':{'cards':len(lesson),'source_row_range':[1000,1156],'source_rows_covered':len(expected),
    'accepted_1085_1086_one_Panorama_card':True,'accepted_1142_two_Milliarde_Billion_cards':True,
    'examples_total':example_total,'empty_example_cards':len(empty_examples),'blank_DE_FA_example_count':len(blank_examples),
    'example_statuses_missing':len(missing_status),'cards_with_missing_example_status':len(set(x['card_id'] for x in missing_status)),
    'curated_HOLDs':len(holds),'sense_network_cards':len(networked),'sense_blocks':sum(len(nets(c)) for c in networked),
    'network_examples':sum(len(examples(c)) for c in networked),'network_examples_unrouted':len(unlinked),
    'L08_structured_combinations':collocation_count,'independent_morphology_front_flags':len(form_evidenced),
    'pending_G2_morphology_front_proposals':len(independent_form_proposals),'same_card_exact_DE_example_duplicate_groups':len(duplicate),
    'priority_distribution':dist,'all_cards_triaged':len(decisions)},
  'global_QA':{'total_card_ids':len(cards),'original_source_map_rows':1548,'Kombinationen_total':global_finite['combinations_scanned'],
    'finite_clause_v4_global_count':len(global_finite['issues']),'finite_clause_v4_L08_count':sum(x['lesson']=='L08' for x in global_finite['issues']),
    'global_duplicate_groups':len(global_dup),'global_finite_clause_strict_gate':'FAILED_3_IN_OTHER_LESSONS',
    'structural_collocation_gate_scope_limited':True},
  'release':{'real_app_import_render_tested':False,'formally_approved_cards':0,'import_ready':False,
             'L08_content_changed_in_phase1':0,'curated_data_owner_replaced':False},
  'next':'L08_PHASE2_ALL_157_CARD_EDITORIAL_WITH_PERSISTED_PRIMARY_JSONL_DIFF_GUARD',
  'limitations':['Prioritized risks are not verified linguistic errors','No textbook CSV used or reintroduced',
                  'G2 source proposals do not count as independent morphology attestation','No phantom approval based on QA-only HTML or TSV']}
 coverage={'schema':'aspekte-b1plus-L08-source-row-preservation@1','date':DATE,'card_count':len(lesson),
 'original_source_ordinal_range':[1000,1156],'mapped_source_rows':len(original_to_cards),
 'no_original_row_dropped':True,'source_1086_merged_into_1085_Panorama':original_to_cards[1086],
 'source_1142_two_separate_lemmas':original_to_cards[1142],
 'all_ordinal_to_accepted_card_id_map':{str(k):original_to_cards[k] for k in sorted(original_to_cards)},
 'source_mapping_sha256':sha(other[MAP]),'data_owner_cards_unchanged':True}

 plan=f'''# Aspekte B1+ · L08 · Drei-Phasen-Plan (LIVE)\n\n**Stand {DATE} · Phase 1 DONE · Phase 2 NEXT · Phase 3 strict release gate PLANNED · NONIMPORT**\n\n**Authority:** Last SHA-verified curated Library L07 Phase3 owner \\`libfile_4e8d3ac0eac481919bc8627f21f0f2bd\\`, SHA-256 \\`{owner_sha}\\`. Phase1 is AUDIT_ONLY; it does **not** replace the 1571-card learner-data owner or mutate cards.\n\n## Phase 1 · completed whole-lesson audit\n- **157 cards**, source ordinals **1000–1156** fully accounted for. Original **1086** correctly linked in 1085 Panorama; source **1142** correctly splits into Milliarde / Billion. No lost original source row.\n- **{example_total} DE–FA examples**. **{len(missing_status)} statusless QA entries** on {len(set(x['card_id'] for x in missing_status))} cards; 0 cards with no examples; **{len(holds)} inherited HOLDs**; **{len(networked)} sense-network cards**, **{len(unlinked)} sense-unrouted examples**; **{len(duplicate)} duplicate German example group** (7065 der Appell); **{len(form_evidenced)} independently validated morphology flags**, **{len(independent_form_proposals)} unapproved G2 front proposals**, all 157 need proportionate case-level form audit.\n- **{collocation_count} L08 combinations** of {global_finite['combinations_scanned']} current corpus-wide; finite-clause v4 detector found no L08 candidates but still **3 global old cases** in other lessons. Only structural proof, no per-collocation idiomatic signoff.\n- Full 157-row JSONL decision ledger: P1={dist.get('P1',0)}, P2={dist.get('P2',0)}, P3={dist.get('P3',0)}. Priorities are repair order, not proof of quality. No 10-word batches.\n\n## Phase 2 · next, one whole lesson\nReview all 157 real cards, starting with HOLDs, 38 QA-status blanks, 7065 `der Appell` repeated German sentence with two useful Persian translations, 31 unrouted sense-examples and context-sensitive words. Preserve main meanings before subsidiary senses within **one lemma card**. Do not force synonyms or antonyms, and keep meaning-scoped natural Kombinationen genuinely shorter than full sentences. Check proposed forms with actual evidence, no invented review. Persist edited PRIMARY 1571-card JSONL and compare actual per-card diffs before updating any owner checkpoint; reject sidecar-only fake progress.\n\n## Phase 3 · only after Phase2, one whole lesson\nRun strict case-level bilingual/grammar/sense/network and regressions, generate QA-only HTML/TSV, then **actual app import/render** if technically available. If real app runtime or independent content evidence is missing, mark \\`RELEASE_BLOCKED_NONIMPORT\\`; do not make up formal approvals. No forced second person.\n'''.replace('\\`','`').replace('\u00137\u00130\u00136\u00135','1065')
 (out/'Lessons/L08').mkdir(parents=True,exist_ok=True)
 (out/'Tools').mkdir(parents=True,exist_ok=True)
 pr=out/'Lessons/L08/L08-PHASE1-FULL-LESSON-AUDIT.json'; write_json(pr,report)
 q=out/'Lessons/L08/L08-PHASE1-157-CARD-DECISION-QUEUE.jsonl'
 q.write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in decisions),encoding='utf-8')
 write_json(out/'Lessons/L08/L08-PHASE1-SOURCE-MAP-COVERAGE.json',coverage)
 write_json(out/'Lessons/L08/L08-PHASE1-GLOBAL-V4-COMBINATIONS.json',global_finite)
 write_json(out/'Lessons/L08/L08-PHASE1-DUPLICATE-EXAMPLE-CASES.json',{'local':duplicate,'global':global_dup})
 write_json(out/'Lessons/L08/L08-PHASE1-G2-MORPHOLOGY-PROPOSALS.json',independent_form_proposals)
 (out/'Lessons/L08/L08-THREE-PHASE-PLAN.md').write_text(plan,encoding='utf-8')
 # QA-only, human-readable full audit including DE/FA cases and why flagged.
 page=['<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Aspekte B1+ L08 157-card audit - NONIMPORT</title>',
 '<style>body{font-family:system-ui,sans-serif;max-width:1160px;margin:24px auto;color:#172333;line-height:1.5}article{border:1px solid #ccd8e0;padding:14px 20px;border-radius:9px;margin:14px 0}h1{margin:0}h2{margin:0 0 8px}summary{cursor:pointer}.fa{direction:rtl;text-align:right;color:#395477}.meta{color:#667085;font-size:.9em}.risk{color:#ad3f23}.sense{background:#f5f7f9;padding:8px;margin:6px 0;border-radius:6px}li{margin:5px 0}code{background:#f4f6fa;padding:2px 4px}</style></head><body>',
 f'<h1>Aspekte B1+ — Lektion 08</h1><p class="meta">Phase 1, {DATE}. {len(lesson)} cards, {example_total} bilingual examples. NONIMPORT — not a linguistic release proof.</p>']
 for d in decisions:
  page.append('<article><h2>'+html.escape(d['headword_de'])+' <span class="meta">'+html.escape(d['priority'])+' · '+str(d['ordinal'])+'</span></h2>')
  page.append('<p><strong>Vorderseite:</strong> '+html.escape(d['front_display_de'])+'<br><strong>فارسی:</strong> <span dir="rtl">'+html.escape(d['meanings_fa'])+'</span></p>')
  page.append('<p class="risk"><strong>Flags:</strong> '+html.escape(', '.join(d['risk_flags']))+'</p>')
  page.append('<details><summary>Beispiele ('+str(d['example_count'])+')</summary><ol>')
  for e in d['examples']:
   page.append('<li>'+html.escape(e.get('de',''))+'<p class="fa">'+html.escape(e.get('fa',''))+'</p><span class="meta">'+html.escape(str(e.get('status') or 'QA_STATUS_MISSING'))+'</span></li>')
  page.append('</ol></details>')
  if d['sense_blocks']:
   page.append('<details><summary>Wortnetz / Kombinationen ('+str(len(d['sense_blocks']))+')</summary>')
   for n in d['sense_blocks']:
    page.append('<div class="sense"><b>'+html.escape(n.get('sense_de',''))+'</b><p class="fa">'+html.escape(n.get('sense_fa',''))+'</p>')
    for co in n.get('Kombinationen_DE_FA',[]):page.append('<p>'+html.escape(co.get('de',''))+' — <span dir="rtl">'+html.escape(co.get('fa',''))+'</span></p>')
    page.append('</div>')
   page.append('</details>')
  page.append('<details><summary>Phase2 decisions</summary><ul>')
  for a in d['phase2_actions']:page.append('<li>'+html.escape(a)+'</li>')
  page.append('</ul></details></article>')
 page.append('</body></html>')
 (out/'Lessons/L08/L08-PHASE1-157-CARD-QA-ONLY.html').write_text('\n'.join(page),encoding='utf-8')
 src=Path(__file__).read_bytes()
 (out/'Tools/qa_L08_phase1_v1.py').write_bytes(src)
 (out/'README-L08-PHASE1-NONIMPORT.md').write_text(f'# L08 Phase1: 157 learner-card triage — NONIMPORT\n\nInput owner = SHA256 {owner_sha}. Evidence ZIP only, **not** a new learner card version.\n\n157 JSONL decisions (P1 {dist.get("P1",0)}, P2 {dist.get("P2",0)}, P3 {dist.get("P3",0)}), full source mapping, global duplicates, v4 finite-clause check, HTML and fully reproducible script. Primary data in upstream curated ZIP is NOT edited or included in this audit bundle. No approved cards. Next Phase2 entire 157-card lesson.\n',encoding='utf-8')
 bundle=out.parent/f'Aspekte-B1plus-L08-PHASE1-WHOLE-157-CARD-AUDIT-NONIMPORT-{DATE.replace("-","")}.zip'
 files=sorted(x for x in out.rglob('*') if x.is_file())
 with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  hashes=[]
  for f in files:
   name=f.relative_to(out).as_posix();data=f.read_bytes();z.writestr(name,data);hashes.append(f'{sha(data)}  {name}')
  z.writestr('SHA256SUMS.txt','\n'.join(hashes)+'\n')
 with zipfile.ZipFile(bundle) as z:
  assert z.testzip() is None
  m={k:v for v,k in (x.split('  ',1) for x in z.read('SHA256SUMS.txt').decode().splitlines())}
  assert len(m)==len(files) and all(sha(z.read(k))==v for k,v in m.items())
  assert len(z.namelist())==len(files)+1
 print(json.dumps({'status':'PASS','bundle':str(bundle),'zip_bytes':bundle.stat().st_size,
       'zip_sha256':sha(bundle.read_bytes()),'members':len(files)+1,'verified_members':len(files),
       'cards':157,'source_rows':157,'examples':example_total,'holds':len(holds),
       'statusless':len(missing_status),'unrouted':len(unlinked),'network_cards':len(networked),
       'duplicate_in_L08':len(duplicate),'global_duplicate_groups':len(global_dup),
       'global_finite_v4':len(global_finite['issues']),'priority':dist,
       'primary_card_data_modified':False},ensure_ascii=False,indent=2))

if __name__=='__main__':
 if len(sys.argv)<2:raise SystemExit('Usage: python qa_L08_phase1_v1.py ZIP [OUTPUTDIR]')
 main(Path(sys.argv[1]),Path(sys.argv[2]) if len(sys.argv)>2 else Path('l08-phase1-report'))
