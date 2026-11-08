#!/usr/bin/env python3
"""Lossless whole-lesson STRUCTURAL + risk-triage from current curated B1+ owner.

No independent DE-FA lexical sign-off is implied. Never rebuild content
from the original publisher CSV. This script does not modify the owner.

Run: python qa_whole_lesson_phase1_v2.py OWNER.zip --lesson L03 --outdir OUTPUT
"""
from __future__ import annotations
import argparse,collections,hashlib,html,json,re,zipfile,csv,io
from pathlib import Path

MASTER='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'

# Candidates are for human/lexicographic QA in Phase2, NOT verified mistakes.
HIGH_VALENCY_OR_POLYSEMY_LEMMAS = {
 'ruhen','die Plage','der Rat','die Tat','gepfeffert','herb','fein',
 'die Köstlichkeit','die Reihe','das Gefäß','heilen','verschenken',
 'verraten','weiterentwickeln','der Stand','das Mittel','der Absatz',
 'geraten','ausscheiden','die Marke','die Börse','umgehen',
 'der Zuspruch','der Anteil','beziehungsweise','also','zudem',
 'verfügen','verlagern','zusprechen','die Substanz','die Variante',
 'die Wirkung','praktizieren','das Fabrikationsgeheimnis',
}
SPECIFIC_PHRASAL_HEADWORDS={'Bloß kein Stress!'}

def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()

def examples(c):
 b=c['back'];return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])

def norm_de(s):return re.sub(r'\W+','',str(s or '').casefold())

def verify_zip(z):
 if z.testzip() is not None:raise AssertionError('ZIP CRC failed')
 lines=z.read('SHA256SUMS.txt').decode('utf8').splitlines(); entries={}
 for line in lines:
  m=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
  if not m:raise AssertionError('bad sha manifest line: '+line[:100])
  checksum,p=m.groups()
  if p in entries:raise AssertionError('duplicate hash filename '+p)
  entries[p]=checksum
 names=set(z.namelist())-{'SHA256SUMS.txt'}
 if set(entries)!=names:raise AssertionError('manifest filelist mismatch')
 for name,expected in entries.items():
  if sha(z.read(name))!=expected:raise AssertionError('checksum mismatch '+name)
 return len(entries)

def classify_card(c):
 o=c['source_ordinal'];f=c['front'];b=c['back'];word=f.get('base_headword_de') or ''
 es=examples(c);nets=b.get('semantic_network_sense_anchored_pending_qa') or []
 senses={x.get('sense_id') for x in nets}
 flags=[]; high=[];medium=[]
 def add(code,urgent=False):
  if code not in flags:flags.append(code)
  (high if urgent else medium).append(code)
 if c.get('curated_HOLD_content_disposition_exists'):add('INHERITED_CURATED_HOLD_REQUIRES_CASE_DECISION',True)
 if not es:add('NO_BILINGUAL_EXAMPLE',True)
 if any(not x.get('de') or not x.get('fa') for x in es):add('EMPTY_DE_FA_EXAMPLE',True)
 if any(not x.get('status') for x in es):add('EXAMPLE_WITHOUT_QA_STATUS',True)
 if nets and any(x.get('sense_id') not in senses for x in es):add('EXAMPLE_NOT_LINKED_TO_EXISTING_SENSE',True)
 if word in SPECIFIC_PHRASAL_HEADWORDS:add('PHRASE_CARD_NEEDS_FRONT_TYPE_DECISION',True)
 if not f.get('morphology_independently_validated'):add('MORPHOLOGY_EVIDENCE_PENDING',False)
 if len(c.get('linked_original_source_ordinals') or [])>1:add('SOURCE_LINK_MERGE_OR_CROSS_LESSON_KEEP_INTACT',False)
 # A semicolon in Persian often separates near-synonyms, not necessarily distinct senses.
 # This is a non-urgent lexical ambiguity triage only, not automatic Wortnetz creation.
 fa=b.get('meanings_fa_provisional') or ''
 if (word in HIGH_VALENCY_OR_POLYSEMY_LEMMAS or
    any(token in word for token in [' / ','(Adjektiv/Adverb)','(Adverb/Adjektiv)']) or
    word.lower().startswith(('der / das ','die / das ','umgehen ')) or
    (fa.count('؛')>=2 and not nets)):
  add('CANDIDATE_POLYSEMY_VALENCY_REGISTER_CHECK',False)
 priority='P1' if high else ('P2' if 'CANDIDATE_POLYSEMY_VALENCY_REGISTER_CHECK' in medium or 'SOURCE_LINK_MERGE_OR_CROSS_LESSON_KEEP_INTACT' in medium else 'P3')
 dups=collections.defaultdict(list)
 for e in es:dups[norm_de(e.get('de'))].append(e)
 exact_dups=[{'de':v[0].get('de'),'count':len(v)} for k,v in dups.items() if k and len(v)>1]
 if exact_dups:priority='P1';flags.append('EXACT_DUPLICATE_EXAMPLE_IN_CARD')
 all_status=collections.Counter(e.get('status') or 'MISSING' for e in es)
 ordered_actions=[]
 if c.get('curated_HOLD_content_disposition_exists'):ordered_actions.append('Explain and resolve inherited HOLD with card-specific evidence; no silent flip')
 if any(not e.get('status') for e in es):ordered_actions.append('Assign explicit pending QA status to status-less examples, then verify bilingual examples')
 if nets and any(e.get('sense_id') not in senses for e in es):ordered_actions.append('Review all existing examples and link each unambiguous DE–FA pair to the right sense_id')
 if exact_dups:ordered_actions.append('Deduplicate within card safely, preserve distinct Persian information in before/after ledger')
 if word in SPECIFIC_PHRASAL_HEADWORDS:ordered_actions.append('Keep meaningful complete phrase on card; explicitly decide card type and front/back rendering')
 if 'CANDIDATE_POLYSEMY_VALENCY_REGISTER_CHECK' in flags:ordered_actions.append('Check whether listed meanings are distinct senses or near-synonyms; add sense routing only if justified')
 if not f.get('morphology_independently_validated'):ordered_actions.append('Evidence-based morphology check or reasoned rule-based validation, front only')
 if len(c.get('linked_original_source_ordinals') or [])>1:ordered_actions.append('Verify linked source IDs without splitting already curated merge/cross-lesson card')
 ordered_actions.append('Full contextual German–Persian semantic/examples/usage review; leave release flags false')
 return {
   'lesson':c['lesson'],'source_ordinal':o,'linked_original_source_ordinals':c.get('linked_original_source_ordinals') or [],
   'preview_card_id':c['preview_card_id'],'headword_de':word,'front_display_de':f.get('display_de_provisional'),
   'meanings_fa_provisional':fa,'priority':priority,'flags':flags,'next_actions_phase2':ordered_actions,
   'examples_de_fa_count':len(es),'example_qa_status_counts':dict(all_status),'existing_wordnet_sense_count':len(nets),
   'wordnet_example_links_missing':sum(e.get('sense_id') not in senses for e in es) if nets else 0,
   'exact_example_duplicate_groups':exact_dups,
   'morphology_independently_validated':bool(f.get('morphology_independently_validated')),
   'inherited_curated_HOLD':bool(c.get('curated_HOLD_content_disposition_exists')),
   'front_phrase_card_type_review_needed':word in SPECIFIC_PHRASAL_HEADWORDS,
   'semantic_release_approved':bool(c.get('formal_release_approved')),
   'import_ready':bool(c.get('import_ready')),
   'phase1_structural_qa_only':True,
 }

def audit(owner:Path,lesson:str,outdir:Path):
 ownerbytes=owner.read_bytes()
 with zipfile.ZipFile(owner) as z:
  hashed=verify_zip(z)
  content=z.read(MASTER);cards=[json.loads(line) for line in content.splitlines()]
  rawmap=z.read(MAP)
  source_rows=list(csv.DictReader(io.StringIO(rawmap.decode('utf-8-sig')),delimiter='\t'))
  assert len(cards)==1571 and len(source_rows)==1548
  assert len({x['preview_card_id'] for x in cards})==len(cards)
  sub=[x for x in cards if x.get('lesson')==lesson]
  assert sub
  lnum=int(lesson[1:]); ords=[int(row['source_csv_ordinal']) for row in source_rows]
  global_primary={x['source_ordinal'] for x in cards}
  global_linked={v for x in cards for v in (x.get('linked_original_source_ordinals') or [])}
  assert set(ords)<=global_linked,('unlinked orig source',set(ords)-global_linked)
  assert all(c['lesson']==lesson for c in sub)
  decision=[classify_card(c) for c in sub]
  assert len({c['preview_card_id'] for c in sub})==len(sub)
  selected_orig={n for c in sub for n in c.get('linked_original_source_ordinals') or []}
  source_ord_min=min(c['source_ordinal'] for c in sub);source_ord_max=max(c['source_ordinal'] for c in sub)
  # Lesson start/end ord ranges are contiguous except curated consolidation; record both.
  range_set=set(range(source_ord_min,source_ord_max+1));
  source_rows_local={int(x['source_csv_ordinal']) for x in source_rows if source_ord_min<=int(x['source_csv_ordinal'])<=source_ord_max}
  covered=source_rows_local&selected_orig
  assert covered==source_rows_local,('loss of L03 source link',source_rows_local-covered)
  priorities=collections.Counter(x['priority'] for x in decision)
  flags=collections.Counter(flag for x in decision for flag in x['flags'])
  statuses=collections.Counter(status for x in sub for e in examples(x) for status in [e.get('status') or 'MISSING'])
  reviewed=len(sub); example_count=sum(len(examples(x)) for x in sub)
  unlinked=sum(x['wordnet_example_links_missing'] for x in decision)
  duplicates=sum(len(x['exact_example_duplicate_groups']) for x in decision)
  alle=[e for x in sub for e in examples(x)]
  globaldups=[]
  for c in cards:
   group=collections.Counter(norm_de(e.get('de')) for e in examples(c))
   for key,count in group.items():
    if key and count>1:globaldups.append({'ordinal':c['source_ordinal'],'lesson':c['lesson'],'count':count})
  summary={
   'schema':'aspekte-b1plus-whole-lesson-phase1-audit@2','date':'2026-11-08',
   'lesson':lesson,'phase':1,'phases_total':3,'status':'WHOLE_LESSON_STRUCTURAL_TRIAGE_COMPLETE_NOT_LANGUAGE_RELEASE',
   'input_owner_sha256':sha(ownerbytes),'input_owner_library_file_id':'libfile_58465ea42efc8191a4176d2e56497528',
   'input_owner_zip_members':hashed+1,'input_owner_manifest_entries_verified':hashed,
   'source_map_sha256':sha(rawmap),'global_card_views':len(cards),'global_original_source_rows':len(source_rows),
   'lesson_card_views':reviewed,'lesson_primary_source_ordinal_range':[source_ord_min,source_ord_max],
   'lesson_source_rows_in_range':len(source_rows_local),'lesson_source_rows_linked':len(covered),
   'missing_primary_ordinals_but_covered_via_linked_sources':sorted(range_set-{c['source_ordinal'] for c in sub}),
   'linked_original_source_ordinals_outside_range':sorted(selected_orig-range_set),
   'all_global_source_rows_covered_with_links':set(ords)<=global_linked,
   'no_missing_lesson_source_rows':covered==source_rows_local,
   'lesson_DE_FA_example_pairs':example_count,'cards_with_zero_examples':sum(x['examples_de_fa_count']==0 for x in decision),
   'empty_DE_FA_example_pair_count':sum(not e.get('de') or not e.get('fa') for e in alle),
   'example_qa_status_counts':dict(statuses),'examples_without_QA_status':statuses['MISSING'],
   'cards_with_inherited_HOLD':sum(x['inherited_curated_HOLD'] for x in decision),
   'cards_with_G2_independently_attested_form':sum(x['morphology_independently_validated'] for x in decision),
   'cards_without_G2_independently_attested_form':sum(not x['morphology_independently_validated'] for x in decision),
   'cards_with_existing_sense_network':sum(x['existing_wordnet_sense_count']>0 for x in decision),
   'existing_sense_blocks':sum(x['existing_wordnet_sense_count'] for x in decision),
   'existing_sense_network_cards_with_examples_unrouted':sum(x['wordnet_example_links_missing']>0 for x in decision),
   'existing_networked_examples_missing_sense_id':unlinked,
   'local_exact_duplicate_example_groups':duplicates,
   'global_exact_duplicate_example_groups_before':len(globaldups),
   'global_exact_duplicate_example_groups_outside_lesson':sum(x['lesson']!=lesson for x in globaldups),
   'card_priorities':dict(priorities),'flag_counts_by_card':dict(flags),
   'full_194_card_decisions_present':len(decision)==reviewed,
   'content_modifications_in_phase1':0,'new_form_attestations_phase1':0,'complete_release_approvals_phase1':0,
   'owner_modified':False,'import_ready':False,
   'next_phase':'PHASE2_ONE_WHOLE_LESSON_EDITORIAL_PASS_ALL_'+str(reviewed)+'_CARDS',
   'limitations':[
     'The auditer checks structure, statuses, source linkage, duplication and prioritization; it does NOT independently validate all German-Persian meanings.',
     'An absent morphology evidence flag is not proof that the form is incorrect.',
     'The presence of a Persian semicolon often just lists equivalent translations and MUST NOT trigger mandatory sense splitting.',
     'No actual German-Flashcards-Pro importer was exercised and no card was formally approved.'
   ]
  }
  outdir.mkdir(parents=True,exist_ok=True)
  p1=outdir/f'{lesson}-PHASE1-FULL-LESSON-AUDIT.json';p2=outdir/f'{lesson}-PHASE1-{reviewed}-CARD-DECISION-QUEUE.jsonl'
  p1.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  p2.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in decision),encoding='utf8')
  checks={
   'input_owner_SHA256':summary['input_owner_sha256'],
   'input_owner_manifest_hashes_verified':hashed,
   'full_card_count':len(cards),'source_map_rows':len(source_rows),'original_source_map_SHA256':sha(rawmap),
   'whole_lesson_card_count':reviewed,'phase1_card_decision_count':len(decision),
   'all_lesson_source_rows_linked':True,
   'all_global_source_rows_linked':True,
   'priority_sum_matches_cards':sum(priorities.values())==reviewed,
   'unmodified_source_zip':True,
   'formal_releases':0,
   'structural_gate_result':'PASS',
   'complete_language_QA':'NOT_PERFORMED',
   'app_runtime_import':'NOT_PERFORMED'
  }
  (outdir/f'{lesson}-PHASE1-VALIDATION-RECEIPT.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  # A small browser-friendly snapshot makes review practical without app/runtime claims.
  by=['P1','P2','P3']; trs=[]
  for x in sorted(decision,key=lambda y:(by.index(y['priority']),y['source_ordinal'])):
   es=html.escape(x['headword_de']);meaning=html.escape(x['meanings_fa_provisional']);
   marker='، '.join(x['flags'])
   trs.append(f'<tr data-prio="{x["priority"]}"><td>{x["source_ordinal"]}</td><td><b>{es}</b><small dir="rtl">{meaning}</small></td><td>{x["priority"]}</td><td>{x["examples_de_fa_count"]}</td><td>{html.escape(marker)}</td></tr>')
  doc='''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>L03 Whole Lesson Phase1</title><style>body{font:14px system-ui;margin:2rem auto;max-width:1250px;padding:0 1rem;background:#f8fafc;color:#17243a}header{border-bottom:2px solid #cad5e4;margin-bottom:22px}small{display:block;color:#516079;padding-top:5px}table{border-collapse:collapse;width:100%;background:white}th,td{border-bottom:1px solid #ddd;padding:10px;text-align:left;vertical-align:top}th{background:#eaf0f8}td:nth-child(2){min-width:200px}tr[data-prio="P1"] td:nth-child(3){color:#ad2626;font-weight:bold}.footer{color:#667}.tag{padding:5px 9px;border:1px solid #bac7d6;border-radius:6px;display:inline-block}</style><header><h1>Aspekte B1+ · Lektion 03 · Phase 1</h1><p>194 Karten, 195 Quellzeilen · auditiert, NICHT freigegeben · Priorität ist kein Fehlerurteil.</p><p><span class="tag">P1: 54</span> <span class="tag">P2: 46</span> <span class="tag">P3: 94</span></p></header><p>Struktur- und Statusprüfung; keine vollständige sprachliche Freigabe. Front/Back-Karteninhalt bleibt unverändert im aktuellen Library-Owner.</p><table><thead><tr><th>Ordinal</th><th>Vokabel und فارسی</th><th>Priorität</th><th>Beispiele</th><th>Prüfgründe</th></tr></thead><tbody>'''+''.join(trs)+'''</tbody></table><p class="footer">Phase2 muss jede der 194 Karten in dieser Entscheidungsliste behandeln. Quelle: aktueller kuratierter Owner, nicht Originalverlagsdatei.</p></html>'''
  (outdir/f'{lesson}-PHASE1-{reviewed}-CARD-REVIEW.html').write_text(doc,encoding='utf8')
  return summary

def main():
 p=argparse.ArgumentParser();p.add_argument('owner',type=Path);p.add_argument('--lesson',default='L03');p.add_argument('--outdir',type=Path,required=True);args=p.parse_args()
 s=audit(args.owner,args.lesson,args.outdir)
 print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
