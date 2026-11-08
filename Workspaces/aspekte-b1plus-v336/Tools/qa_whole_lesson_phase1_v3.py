#!/usr/bin/env python3
"""Audit ALL cards in one curated Aspekte B1+ lesson, without modifying owner data.

Usage: python qa_whole_lesson_phase1_v3.py OWNER.zip L04 OUTPUT_DIR
Result: whole-lesson status + per-card editorial queue + searchable HTML + plan;
all outputs NONIMPORT. This is risk/structure QA, NOT full independent DE/FA QA.
"""
import collections, hashlib, html, json, re, sys, zipfile
from pathlib import Path

CARD_FILE='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
SOURCE_MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
SOURCE_EXPECTED='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
OWNER_EXPECTED='ea0bde4b38aebca9973f9b8d90e201f627edd8c1c491d752006792991b2a34e6'
LESSON_RANGES={'L01':(1,71),'L02':(72,162),'L03':(163,357),'L04':(358,515),'L05':(516,671),'L06':(672,846),'L07':(847,999),'L08':(1000,1156),'L09':(1157,1341),'L10':(1342,1548)}

def sha(data): return hashlib.sha256(data).hexdigest()
def exs(c):
 b=c.get('back') or {}
 return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
def norm(s): return re.sub(r'\s+',' ',str(s).strip()).casefold()
def dump(path,obj): Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def evaluate(src,lesson,out):
 src=Path(src);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 if lesson not in LESSON_RANGES: raise ValueError('unknown lesson')
 if sha(src.read_bytes())!=OWNER_EXPECTED: raise ValueError('Current owner has changed; audit must be re-baselined against new SHA')
 with zipfile.ZipFile(src) as z:
  if z.testzip() is not None: raise ValueError('Corrupt ZIP member')
  names=z.namelist();manifest=z.read('SHA256SUMS.txt').decode('utf-8').splitlines()
  manifest_pairs=[line.split('  ',1) for line in manifest if line.strip()]
  if len(manifest_pairs)!=len(names)-1 or {n for _,n in manifest_pairs}!={n for n in names if n!='SHA256SUMS.txt'}:raise ValueError('Manifest files mismatch')
  for h,n in manifest_pairs:
   if sha(z.read(n))!=h:raise ValueError('ZIP member sha mismatch: '+n)
  source_bytes=z.read(SOURCE_MAP)
  if sha(source_bytes)!=SOURCE_EXPECTED:raise ValueError('source map changed')
  cards=[json.loads(s) for s in z.read(CARD_FILE).decode('utf-8').splitlines() if s.strip()]
  if len(cards)!=1571 or len(set(c.get('preview_card_id') for c in cards))!=1571:raise ValueError('Global card identity regression')
  if len(source_bytes.decode('utf-8-sig').splitlines())-1!=1548:raise ValueError('Original source rows changed')
  all_originals={int(o) for c in cards for o in c.get('linked_original_source_ordinals',[])}
  if all_originals!=set(range(1,1549)):raise ValueError('Source ordinals coverage regression')
 selected=[c for c in cards if c.get('lesson')==lesson]
 start,end=LESSON_RANGES[lesson];wanted=set(range(start,end+1))
 covered={int(o) for c in selected for o in c.get('linked_original_source_ordinals',[])}
 if not wanted.issubset(covered):raise ValueError('Missing lesson original sources: '+str(sorted(wanted-covered)))
 if not selected: raise ValueError('No cards')
 primary_misses=sorted(wanted-{int(c['source_ordinal']) for c in selected})
 consolidated={str(o):[{'source_ordinal':c['source_ordinal'],'lemma':c['front']['base_headword_de'],'preview_card_id':c['preview_card_id']} for c in selected if o in c.get('linked_original_source_ordinals',[])] for o in primary_misses}
 if any(not holders for holders in consolidated.values()):raise ValueError('Unlinked merged source row')
 if any(c.get('import_ready') or c.get('formal_release_approved') for c in selected):raise ValueError('Audit expects non-import owner only')
 stats=collections.Counter();status=collections.Counter();priority=collections.Counter();duplicates=[];missing_routes=[];case_queue=[]
 for c in selected:
  f=c.get('front') or {};b=c.get('back') or {};source=c.get('source_ordinal');word=f.get('base_headword_de') or ''
  e=exs(c);nets=b.get('semantic_network_sense_anchored_pending_qa') or []
  sense_ids={s.get('sense_id') for s in nets};unrouted=[{'index':i,'de':v.get('de',''),'fa':v.get('fa',''),'sense_id':v.get('sense_id')} for i,v in enumerate(e) if nets and v.get('sense_id') not in sense_ids]
  missingstat=[{'index':i,'de':v.get('de',''),'fa':v.get('fa','')} for i,v in enumerate(e) if not v.get('status')]
  seen=collections.defaultdict(list)
  for i,v in enumerate(e):
   if not v.get('de','').strip() or not v.get('fa','').strip():raise ValueError(f'Empty example at {source}:{i}')
   seen[norm(v['de'])].append({'index':i,'de':v['de'],'fa':v['fa']})
   status[str(v.get('status') or 'MISSING')]+=1
  dupe=[{'normalized_de':k,'pairs':vv} for k,vv in seen.items() if len(vv)>1]
  if dupe:duplicates.append({'source_ordinal':source,'lemma':word,'groups':dupe})
  if unrouted:missing_routes.append({'source_ordinal':source,'lemma':word,'missing_count':len(unrouted),'pairs':unrouted})
  has_hold=bool(c.get('curated_HOLD_content_disposition_exists'))
  attested=bool(f.get('morphology_independently_validated'))
  phrase_candidate=bool((word.endswith(('.', '!', '?')) and len(word.split())>=3) or '...' in word or '…' in word)
  split_source=len([q for q in selected if q.get('source_ordinal')==source])>1
  semantic_candidate=(';' in str(b.get('meanings_fa_provisional','')) or len(nets)>1 or any(x in word.lower() for x in ['(für +','+ dat','+ akk','(mit +']))
  flags=[]
  if has_hold:flags.append('INHERITED_CURATED_HOLD_MUST_BE_DECIDED')
  if not attested:flags.append('FORM_NOT_INDIVIDUALLY_ATTESTED_NOT_NECESSARILY_WRONG')
  if missingstat:flags.append('EXAMPLE_QA_STATUS_MISSING')
  if unrouted:flags.append('EXAMPLES_NOT_LINKED_TO_EXISTING_SENSE')
  if dupe:flags.append('EXACT_GERMAN_EXAMPLE_REPEATED_IN_SAME_CARD')
  if split_source:flags.append('VALID_SHARED_SOURCE_LEXEME_SPLIT_PRESERVE')
  if phrase_candidate:flags.append('PHRASE_OR_SENTENCE_FRONT_VERIFY_TYPE')
  if semantic_candidate:flags.append('SENSE_VALENCY_REGISTER_JUDGMENT_CANDIDATE_NOT_AUTO_SPLIT')
  if b.get('Formen_section') is not None:flags.append('BACK_FORMEN_DUPLICATION_REQUIRES_FIX')
  if not e:flags.append('NO_EXAMPLES')
  if dupe or has_hold or unrouted or missingstat or (len(nets)>1 and any(y.get('sense_id') not in sense_ids for y in e)):
   pri='P1'
  elif (not attested and (phrase_candidate or semantic_candidate)) or split_source or len(nets)>1:
   pri='P2'
  else:pri='P3'
  todo=['REVIEW_DE_FA_MEANINGS_AND_ALL_EXAMPLES_IN_CONTEXT_NO_AUTO_SIGNOFF','CHECK_FRONT_INFLECTION_AND_POS_USING_RULES_OR_DICTIONARY_AS_APPROPRIATE','CHECK_SENSE_SPECIFIC_SYNONYMS_ANTONYMS_KOMBINATIONEN','MARK_ALL_DECISIONS_EXPLICITLY_HOLD_OR_EDITED_OR_NO_CHANGE']
  if dupe:todo.insert(0,'REVIEW_DUPLICATE_DE_EXAMPLE_AND_PRESERVE_UNIQUE_FA_DISTINCTION')
  if unrouted:todo.insert(0,'MAP_EXISTING_DE_FA_EXAMPLES_TO_CORRECT_SENSE_IDS_WITHOUT_FORCING_AMBIGUOUS')
  if missingstat:todo.insert(0,'SET_EXPLICIT_EXAMPLE_QA_STATUS_PENDING_UNLESS_ACTUALLY_APPROVED')
  if has_hold:todo.insert(0,'RESOLVE_OR_PRESERVE_CURATED_HOLD_WITH_CASE_SPECIFIC_REASON')
  if split_source:todo.insert(0,'KEEP_EXISTING_SPLIT_CARDS_AND_EXACT_SOURCE_LINKS_INTACT')
  if phrase_candidate:todo.insert(0,'CHECK_SENTENCE_OR_PHRASE_FRONT_TYPED_AS_WENDUNG_NOT_IMAGINED_NOUN_VERB')
  q={'lesson':lesson,'source_ordinal':source,'preview_card_id':c.get('preview_card_id'),
    'lemma_de':word,'front_display_de':f.get('display_de_provisional'),'front_morphology_independently_attested':attested,
    'linked_original_source_ordinals':c.get('linked_original_source_ordinals'),
    'meanings_fa':b.get('meanings_fa_provisional'),'priority':pri,'flags':flags,
    'curated_HOLD':has_hold,'number_of_examples':len(e),'number_of_senses':len(nets),
    'number_of_unrouted_existing_network_examples':len(unrouted),'number_of_missing_QA_statuses':len(missingstat),
    'examples_DE_FA':[{'de':x.get('de'),'fa':x.get('fa'),'status':x.get('status'),'sense_id':x.get('sense_id')} for x in e],
    'sense_networks':[{'sense_id':x.get('sense_id'),'sense_de':x.get('sense_de'),'sense_fa':x.get('sense_fa'),'Kombinationen_DE_FA':x.get('Kombinationen_DE_FA',[]),'Synonyme':x.get('Synonyme',[]),'Antonyme':x.get('Antonyme',[])} for x in nets],
    'duplicate_examples':dupe,'pending_actions_for_phase2':todo,
    'phase1_review_scope':'STRUCTURE_AND_PRIORITIZATION_NOT_INDEPENDENT_LINGUISTIC_SIGNOFF','formal_release_approved':False,'import_ready':False}
  case_queue.append(q);priority[pri]+=1
  stats.update({'example_pairs':len(e),'sense_network_blocks':len(nets),'examples_in_networked_cards':len(e) if nets else 0,'unrouted_networked_examples':len(unrouted),'examples_missing_QA_status':len(missingstat),'missing_example_cards':not bool(e),'independently_attested_forms':attested,'forms_without_independent_evidence':not attested,'curated_HOLD_cards':has_hold,'cards_with_wordnet':bool(nets),'sense_linked_examples':sum(x.get('sense_id') in sense_ids for x in e) if nets else 0,'phrase_candidates':phrase_candidate,'semantic_review_candidates':semantic_candidate,'split_source_cards':split_source,'cards_with_statusless_examples':bool(missingstat)})
 if len(case_queue)!=160 or len({q['preview_card_id'] for q in case_queue})!=160:raise ValueError('Expected 160 distinct L04 cards')
 case_queue.sort(key=lambda c:({'P1':0,'P2':1,'P3':2}[c['priority']],c['source_ordinal'],c['lemma_de']))
 qpath=out/f'{lesson}-PHASE1-160-CARD-DECISION-QUEUE.jsonl'
 qpath.write_text(''.join(json.dumps(q,ensure_ascii=False,sort_keys=True)+'\n' for q in case_queue),encoding='utf-8')
 report={'schema':'aspekte-b1plus-complete-lesson-structural-audit@3','date':'2026-11-08','lesson':lesson,'phase':1,'phases_total':3,'status':'PHASE1_WHOLE_LESSON_AUDIT_DONE_NO_CARD_TEXT_MUTATION_NONIMPORT',
  'source_owner_sha256':sha(src.read_bytes()),'source_owner_bytes':src.stat().st_size,
  'source_map_sha256':sha(source_bytes),'global_source_rows':1548,'global_preview_cards':1571,'global_source_ordinal_coverage':'PASS_1_TO_1548',
  'input_zip_member_count':len(names),'input_manifest_entries_verified':len(manifest_pairs),'input_crc':'PASS',
  'lesson_cards':len(selected),'lesson_primary_source_ordinal_range':[start,end], 'lesson_source_rows_in_primary_range':len(wanted),
  'all_original_lesson_sources_mapped':True,'external_source_links':sorted(covered-wanted),
  'split_source_ordinals':{str(k):v for k,v in collections.Counter(c['source_ordinal'] for c in selected).items() if v>1},
  'merged_source_ordinals_without_independent_primary_card':primary_misses,'merged_source_evidence':consolidated,
  'counts':dict(stats),'example_status_distribution':dict(status),'priority_distribution':dict(priority),
  'local_exact_duplicate_example_groups':len(duplicates),'local_exact_duplicate_examples_detail':duplicates,
  'networked_cards_with_unrouted_examples_count':len(missing_routes),'unrouted_example_links_detail':missing_routes,
  'queue_card_count':len(case_queue),'queue_all_card_ids_unique':True,'all_cards_unreleased':True,'content_changes_this_phase':0,
  'import_ready':False,'formal_cards_approved_this_phase':0,
  'release_gates_pending':['INDEPENDENT_DE_FA_LANGUAGE_REVIEW','G2_FORM_EVIDENCE_CASE_DECISIONS','CURATED_HOLD_CASE_DISPOSITIONS','ACTUAL_GERMAN_FLASHCARDS_PRO_IMPORT_RENDER'],
  'limitations':['This is a deterministic structural/risk inventory, not a human or independently signed-off German-Persian semantic review.','A missing form-attestation flag is not evidence of an incorrect form.','A Persian semicolon can join synonyms; do not split into artificial senses.','No learner card content has been edited and no application importer exercised.']}
 dump(out/f'{lesson}-PHASE1-FULL-LESSON-AUDIT.json',report)
 plan=f'''# Aspekte B1+ {lesson} — Drei-Phasen-Plan\n\n**Stand:** 2026-11-08 — Phase 1/3 vollständige 160-Karten-Gesamtinventur **DONE**; Phase 2 NEXT; **NONIMPORT**.\n\n## Quelle und Grenzen\n\n- Nur der letzte SHA-verifizierte **kuratierte** Library-Owner wird für Lernkartendaten verwendet, SHA256 `{report['source_owner_sha256']}`; keine Rückkehr zur Lehrbuch-CSV. Original-Source-Map: 1548 Zeilen, SHA256 `{report['source_map_sha256']}`. Gesamtkorpus 1571 Karten. Owner **in Phase1 nicht verändert**.\n- L04 **160 Karten / 158 Originalzeilen (358–515)**: bestehende Aufteilungen in Originalzeilen 358 (3 Karten: Freizeitbeschäftigung/Freizeitaktivität/Freizeitgestaltung) und 436 (2 Karten: plaudern/schwatzen), **bereits korrekt integrierte Quellzeile 443 in der bestehenden Karte 442 `schätzen`**, plus Cross-Lesson-Quellverbindung **44 → 405 `Wohlstand`** erhalten. Alle 158 L04-Originalzeilen vorhanden; kein Duplikat wegen Split automatisch löschen.\n- 365 originale DE–FA-Paare, alle Texte vorhanden, **0 Karten ohne Beispiel**. Scoped Duden G2 bereits für **106** Karten, **54** ohne unabhängige Form-Einzelnachweise. **32** kuratierte Karten-HOLDs bewusst nicht entfernt. 31 Netzwerk-Karten mit 45 Sinnblöcken; **67 der 69** Beispiele in diesen Karten fehlen derzeit die eindeutige Verbindung zu einem Sinn (2 sind bereits verbunden), keine Zwangszuordnung, wenn mehrdeutig. **32** Beispiele ohne QA-Status; alle 365 brauchen vollständige sprachliche Freigabe.\n- **Eine exakte deutschsprachige Wiederholung in `schätzen` (Ordinal 442)**: `Ich schätze, dass wir noch zehn Minuten brauchen.` kommt mit zwei unterschiedlichen, sehr ähnlichen persischen Übersetzungen vor. Nicht ohne Prüfung einer Übersetzungsnuance einfach beide löschen.\n\n## Phase 2 — gesamte Lektion redaktionell korrigieren, nicht 10-Wort-Reviews\n\n1. Vollständige 160-Karten-Queue in einer einzigen Lektionseinheit abarbeiten: Risikofälle **P1 {priority['P1']}**, **P2 {priority['P2']}**, **P3 {priority['P3']}**, ohne P3 als automatisch freigegeben zu betrachten.\n2. Mit Priorität die `schätzen`-Dublette, 67 Beispiel-Sinn-Zuordnungen bei 31 Netzwerk-Karten, 32 Beispiele ohne QA-Status, 32 ererbte HOLDs und falsche Wortarten/Mehrdeutigkeiten bearbeiten. Den aktuell vorhandenen Sinn- und Kombinationen-Inhalt erhalten.\n3. Für alle 160 Einzelkarten Ergebnis festhalten: **wirklich geändert / geprüft ohne Textänderung / HOLD samt Grund**. Nur belegte Korrekturen eintragen; DE–FA-Beispiele, Artikel/Plural, Verben und Mehrdeutigkeiten ausdrücklich prüfen, ohne künstliche Sinn-Splits.\n4. Nach Änderung aktuelle 1571 Karten, 1548 Originalzeilen und alle Nicht-L04-Karten mit Parent bitweise/objektweise abgleichen; strenge Kollokations-, Duplikations- und Morphologie-Gates laufen lassen. L04-Releases bleiben gesperrt.\n\n## Phase 3 — separate Endprüfung\n\n- Echte Sinn-/Übersetzungs-QA und zielgenaue Grammatikevidenz, 32 erhaltene HOLDs einzeln bestimmen. Tatsächlichen App-TSV-Importer/Renderer prüfen. Fehlt der Nachweis, Endstatus **RELEASE_BLOCKED**, nicht künstlich alle Karten bestätigen.\n- Keine erneuten 10-Karten-Mikrobatches und keine Rückkehr zum Lehrbuch-Original als Source of Truth.\n'''
 (out/f'{lesson}-THREE-PHASE-PLAN.md').write_text(plan,encoding='utf-8')
 def fmt(q):
  lines=[f'<div class="item" id="c{q["source_ordinal"]}"><h3>{html.escape(q["lemma_de"])} <small>#{q["source_ordinal"]} · {q["priority"]} · {html.escape(q["preview_card_id"] or "")}</small></h3>',
   '<div class="fa"><strong>فارسی:</strong> '+html.escape(str(q.get('meanings_fa') or ''))+'</div>',
   '<p><strong>Front:</strong> '+html.escape(str(q.get('front_display_de') or ''))+'</p>',
   '<p><strong>Prüfflags:</strong> '+html.escape(', '.join(q['flags']) or 'Keine automatischen Flags')+'</p>',
   '<details><summary>Beispiele / Sinnverbindungen / Folgeschritte</summary>']
  for e in q['examples_DE_FA']:
   lines.append('<p><b>'+html.escape(str(e['de']))+'</b> — '+html.escape(str(e['fa']))+'<br><small>status: '+html.escape(str(e['status']))+' · sense: '+html.escape(str(e['sense_id']))+'</small></p>')
  for n in q['sense_networks']:lines.append('<p><b>Sinn:</b> '+html.escape(str(n['sense_de']))+' / '+html.escape(str(n['sense_fa']))+' <small>['+html.escape(str(n['sense_id']))+']</small></p>')
  lines.append('<p><b>Phase2:</b> '+html.escape(', '.join(q['pending_actions_for_phase2']))+'</p></details></div>')
  return '\n'.join(lines)
 ordered='\n'.join(fmt(q) for q in case_queue)
 page='''<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Aspekte B1+ L04 · 160-Karten-Phase1</title><style>body{font-family:system-ui,sans-serif;max-width:1040px;margin:2rem auto;padding:0 1rem;background:#f7f8fc;color:#17202d}input{width:100%;padding:1rem;border:1px solid #b7c7d7;border-radius:10px;font-size:1rem;box-sizing:border-box}.item{background:white;padding:1rem 1.2rem;border:1px solid #d6dce6;border-radius:10px;margin:12px 0}h3{margin:.2rem 0 .7rem}small{font-size:.74rem;color:#586373;font-weight:normal}p{line-height:1.5}.fa{direction:rtl;text-align:left}.meta{margin:1rem 0;color:#444}details{margin-top:.7rem}details p{padding:.45rem;border-top:1px solid #eee}</style></head><body><h1>Aspekte B1+ · L04 — Vollständige strukturelle Bestandsaufnahme</h1><p>160 Karten, alle 158 Originalquellen und 365 zweisprachige Beispiele. NONIMPORT; ausschließlich QA-Vorschau, keine App-Laufzeit und keine sprachliche Freigabe.</p><input id="filter" placeholder="Suche Lemma / Quellnummer / Flag / Deutsch / فارسی"><div class="meta">Risikopriorität: P1 zuerst, dann P2, dann P3. Kein P3 ist automatisch genehmigt.</div><div id="cards">'''+ordered+'''</div><script>document.getElementById('filter').addEventListener('input',e=>{const s=e.target.value.trim().toLocaleLowerCase();document.querySelectorAll('.item').forEach(x=>x.hidden=!x.textContent.toLocaleLowerCase().includes(s))});</script></body></html>'''
 (out/f'{lesson}-PHASE1-160-CARD-REVIEW-QA-ONLY.html').write_text(page,encoding='utf-8')
 summary={'cards':len(selected),'example_pairs':stats['example_pairs'],'unrouted':stats['unrouted_networked_examples'],'routed':stats['sense_linked_examples'],'morph_attested':stats['independently_attested_forms'],'holds':stats['curated_HOLD_cards'],'duplicates':len(duplicates),'priority':dict(priority),'status':dict(status),'report_file':str(out/f'{lesson}-PHASE1-FULL-LESSON-AUDIT.json'),'queue_file':str(qpath)}
 print(json.dumps(summary,ensure_ascii=False,indent=2))
 return report
if __name__=='__main__':
 if len(sys.argv)!=4: raise SystemExit('Usage: python qa_whole_lesson_phase1_v3.py OWNER.zip L04 output_dir')
 evaluate(*sys.argv[1:])