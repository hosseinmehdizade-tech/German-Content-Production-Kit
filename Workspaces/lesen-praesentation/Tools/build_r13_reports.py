#!/usr/bin/env python3
"""Build transparent source-owner R13 evidence, not semantic Stage4 approval."""
import pathlib,json,hashlib,collections
P=pathlib.Path('/mnt/data/lesen_r13_20261107')
M=P/'Lesen-Production-Master-v1.3.0-R13-16P04-TRILINGUAL-CANDIDATE.json'
R=P/'Lesen-R13-v505-16P04-RUNTIME-PREENTRY-CANDIDATE.json'
a=json.loads(M.read_text());b=json.loads(R.read_text());ledger=json.loads((P/'LESEN-R13-16P04-TRILINGUAL-GRAMMAR-LEDGER.json').read_text());qa=json.loads((P/'LESEN-R13-INDEPENDENT-STRUCTURAL-QA.json').read_text());native=json.loads((P/'LESEN-R13-v505-NATIVE-PREENTRY.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,obj:p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert qa['errors_count']==0 and qa['all_negative_mutations_rejected']
assert native['checks']['candidate_pack_status']=='PASS' and native['checks']['candidate_warnings']==[]
firstlines=collections.Counter(x['reading']['sections'][2]['sentences'][0]['text'] for x in a['items'])
reviews={
52:'KI: Routinegewinne versus Verzerrungen, Datenschutz und Verantwortung; menschliche Kontrolle bleibt sichtbar.',
53:'Bildungsbegriff: verbindliche Fachgrundlagen und überfachliche Fähigkeiten, ohne Schule mit Zielen zu überlasten.',
54:'Karriere: Zufallschance versus Vorbereitung und reflektierte Zielbindung.',
55:'Lernstress: kurzfristige Aktivierung versus anhaltende Belastung; Pausen als Teil der Lernplanung.',
56:'Bibliotheken: Onlinezugriff versus öffentliche Lernorte, Quellenbewertung und Beratung.',
57:'Studienmodelle: tatsächliche Fristen/Prüfungszeiten sowie Wechsel bei familiären und beruflichen Pflichten.',
58:'Internate: Gemeinschaft und intensive Betreuung versus Heimweh, soziale Konflikte und Privatsphäre.',
60:'Lehrende/soziale Netzwerke: Nähe versus Machtgefälle bei laufender Bewertung; offizielle Kanäle.',
61:'Fantasy: erfundene moralische Konflikte als Diskussionsanlass und begrenzte Realitätsvergleiche.',
62:'Kulturförderung: gesellschaftliche Aufgabe versus begrenzte Mittel; unabhängige transparente Vergabe.',
63:'Übersetzung: Genauigkeit bei Verträgen versus Klang/Mehrdeutigkeit bei Lyrik; Textsorten priorisieren.',
64:'Sympathische Lehrende: positive Beziehung versus fachlich begründete Qualität und professionalisierte Betreuung.',
65:'Vorlesen: Spracherwerb, Worterklärung und dialogische Beteiligung statt passiven Zuhörens.',
66:'Elternmitwirkung: berechtigte Rückmeldungen versus fachliche Zuständigkeit der Lehrkräfte.',
67:'Vorschul-Medienkompetenz: kurze begleitete Nutzung versus Bewegung, Spiel und direkten Kontakt.',
68:'Elternführerschein: freiwillige Beratung statt verpflichtender staatlicher Zulassung zur Elternschaft.'}
assert set(reviews)==set([int(x[-3:]) for x in ledger['changed_units']])
scoped=[]
for before_after in ledger['before_after']:
 n=int(before_after['unit_id'][-3:]);p=before_after['after_p04']
 scoped.append({'unit':before_after['unit_id'],'title_de':before_after['title_de'],'evidence':['p02','p03','p04-s02','p05'],
 'editorial_focus_de':reviews[n],'de_first':p['sentences'][0]['text'],'de_middle_unchanged':p['sentences'][1]['text'],
 'de_third':p['sentences'][2]['text'],'translation_fa':p['translations']['fa'],'translation_en':p['translations']['en'],
 'status':'AUTHOR_SCOPED_TRILINGUAL_REVIEW_NOT_INDEPENDENT_SEMANTIC_STAGE4'})
semantic={'schema':'lesen-r13-scoped-trilingual-editorial-review@1.0.0','date':'2026-11-07',
 'material_basis':'R12 curated mutable master, p02/p03/p05 and unchanged p04-s02 (NOT original book)',
 'reviewer_type':'AI editorial, not independent nine-lens/semantic reviewer',
 'scope':'16 p04 three-language sections; source-topic claim alignment, not whole 68-unit linguistic correctness',
 'units':scoped,'known_remaining':'Inherited generic constructions in p02/p03 and p04-s02 remain; complete semantic Stage4 HOLD.',
 'stage4':'HOLD','native_grammar_engine':'NOT_RERUN'}
write(P/'LESEN-R13-TRILINGUAL-SCOPED-REVIEW.json',semantic)
progress={'initial_generic_p04':55,'revised_r9':10,'revised_r10':10,'revised_r11':9,'revised_r12':10,'revised_r13':16,
          'generic_opening_remaining':0,'known_generic_p03_first_sentence_count':firstlines.most_common(1)[0][1],
          'warning':'Template opening removed, not whole-pack qualitative Stage4 approval.'}
checkpoint={'schema':'lesen-quality-review-checkpoint-r13@1.0.0','date':'2026-11-07','owner':'Workspaces/lesen-praesentation','family_id':'family:lesen',
 'status':'R13_16_TRILINGUAL_P04_EDIT_SCOPED_QA_AND_V505_PREENTRY_PASS__CURATED_CURRENT_UNCHANGED_STAGE4_6_7_HOLD',
 'current_immutable':{'sha256':'558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565','library_file_id':'libfile_9b768265ff3c8191aca371baa38551d7','status':'CURRENT_UNCHANGED_NOT_FINAL'},
 'parent_r12':{'content_sha256':ledger['source_r12_sha256'],'runtime_sha256':'e08844a19137a1edece8deb9f39e036df7b4777de2e54db4312e0ab14c3bcd86'},
 'candidate_content':{'name':M.name,'sha256':sha(M),'bytes':M.stat().st_size,'status':'CANDIDATE_NOT_CURRENT','library_file_id':None,'library_byte_readback':'PENDING'},
 'candidate_runtime':{'name':R.name,'sha256':sha(R),'bytes':R.stat().st_size,'status':'PREENTRY_CANDIDATE_NOT_BROWSER_STAGE6','library_file_id':None,'library_byte_readback':'PENDING'},
 'change_scope':{'revised_lessons':ledger['changed_units'],'sections_changed':16,'german_sentences_changed':32,'unaltered_middle_sentences':16,'unchanged_other_units':52,
  'accepted_prior_units_051_059_preserved':True,'stable_questions':340,'stable_vocab':350,'stable_curated_grammar_ids':669},
 'grammar':{'before':4425,'after':4345,'old_context_invalidated':96,'middle_anchors_reanchored':44,'new_scoped_k2':16,'curated_g07_retargeted':8,'native_9_lens_rerun':False,'exact_offsets':True},
 'qa':{'independent_structural_checks':qa['checks_total'],'independent_structural_errors':qa['errors_count'],'negative_mutations_rejected':len(qa['negative_mutations']),
  'actual_v505_source_preentry':'PASS_ZERO_WARNINGS','actual_v505_negative_mutations_rejected':len(native['checks']['negative_cases']),
  'isolated_in_memory_units':native['checks']['in_memory_projection']['units'],'isolated_in_memory_exercises':native['checks']['in_memory_projection']['exercises'],
  'full_independent_trilingual_semantic_stage4':'HOLD','native_browser_indexeddb_stage6':'NOT_RUN','final_stage7':'NOT_RELEASED'},
 'progress':progress,
 'evidence':{'report':'Workspaces/lesen-praesentation/Reports/LESEN-R13-EDITORIAL-AND-V505-REPORT-20261107.md',
  'trilingual_review':'LESEN-R13-TRILINGUAL-SCOPED-REVIEW.json','detailed_ledger':'LESEN-R13-16P04-TRILINGUAL-GRAMMAR-LEDGER.json',
  'structural_qa':'LESEN-R13-INDEPENDENT-STRUCTURAL-QA.json','v505_preentry':'LESEN-R13-v505-NATIVE-PREENTRY.json','runtime_transport':'LESEN-R13-RUNTIME-TRANSPORT-EVIDENCE.json'},
 'next_action':'Review remaining generic p02/p03 sentences and whole-pack trilingual semantic Stage4; do not issue Stage6 or release without browser/IndexedDB.',
 'no_current_promotion':True,'no_runtime_app_code_changes':True,'no_srs_fsrs_mutations':True,'no_library_deletion':True}
write(P/'QUALITY-REVIEW-CHECKPOINT-R13-20261107.json',checkpoint)
report=f'''# Lesen R13 – Abschluss der 16 verbliebenen p04-Vorlagenstarts (7 Nov 2026)

**Familie/Owner:** `family:lesen` / `Workspaces/lesen-praesentation`  
**Status:** R13 CONTENT + v505 PREENTRY RUNTIME **CANDIDATES ONLY**, CURRENT v1.3.0 unverändert.

## Tatsächliche Bearbeitung

- R12 Master SHA256 `{ledger['source_r12_sha256']}` als alleinige inhaltliche Arbeitsgrundlage; keine Rücksetzung auf Quellen-PDF.
- Die 16 vormals generischen p04-Abschnitte der Einheiten 052–058 und 060–068 wurden mit **32 individuell verfassten deutschen Sätzen** (je s01/s03) sowie jeweils synchronisierten FA/EN-Abschnitten aktualisiert.
- Alle 16 vorhandenen p04-s02-Sätze und sämtliche 52 weiteren Einheiten unverändert; besonders **051 und 059** mitsamt allen bisherigen Eingriffen geschützt.
- Der konkrete **wörtlich identische** Abschnittsauftakt „Entscheidend ist deshalb die konkrete Ausgestaltung.“ wurde von 16 auf **0** reduziert. Damit wurden 55/55 ursprünglich identifizierte Starts über R9–R13 bearbeitet. Dies ist **keine** Aussage, dass alle 68 Lektionen sprachlich/gehaltlich fertig sind.
- Q01–Q05 und alle 340 Frage-IDs, 350 Wortschatzeinträge sowie 669 kuratierte Grammatik-IDs identisch zu R12.

## Grammatik und Transport

| Kontrollpunkt | Anzahl |
|---|---:|
| Volltextanker R12 | 4425 |
| Kontextabhängige alte Anker s01/s03 entfernt | 96 |
| Exakt re-anchorte alte s02-Anker | 44 |
| Neue manuell belegte KII-Formen | 16 |
| Retargetete kuratierte g07-Verweise | 8 |
| Volltextanker R13 (exakte Offsets) | 4345 |
| Laufzeit-Einträge R13 geändert | 16 |
| Laufzeit-Einträge byteinhaltlich gleich R12 | 52 |

Die native neun-Linsen-Quellgrammatik wurde **nicht** neu ausgeführt. Alte Anker, deren Text gelöscht wurde, wurden dokumentiert entfernt; eine Verringerung der Ankerzahl ist kein Verlustnachweis oder vollständige linguistische Prüfung.

## Testbefund und Grenzen

- Unabhängiger, nur lesender Struktur-/Quellvergleich: **{qa['checks_total']} Checks, {qa['errors_count']} Fehler**, {len(qa['negative_mutations'])}/{len(qa['negative_mutations'])} Korruptionsproben korrekt erkannt.
- Die echte JavaScript-Quellvalidierung des aktuellen v505-Moduls `reading-content-import-v38.js` meldet **PASS, 0 Warnungen**, {len(native['checks']['negative_cases'])}/{len(native['checks']['negative_cases'])} negative Fälle erkannt, isolierte In-Memory-Projektion 68/340.
- Browser-/IndexedDB-Import, Wiederladen, User-SRS/FSRS und Integration mit UI **nicht** ausgeführt. **Stage6 NOT_RUN; Stage7 NOT_RELEASED**.
- Eigenständige Vollprüfung der DE–FA–EN-Semantik über alle 68 Einheiten **nicht** abgeschlossen; **Stage4 HOLD**. Bei 14 Einheiten beginnt p03 weiterhin wortgleich mit „Dem stehen jedoch gewichtige Einwände gegenüber.“; weitere repetitive Muster bleiben (einschließlich der vorläufig beibehaltenen p04-s02-Sätze).

## Verifizierbare Dateipins

- Content: `{M.name}`, SHA256 `{sha(M)}`, {M.stat().st_size} bytes.
- Runtime: `{R.name}`, SHA256 `{sha(R)}`, {R.stat().st_size} bytes.
- Detailed before/after and grammar: `LESEN-R13-16P04-TRILINGUAL-GRAMMAR-LEDGER.json`.
- Scoped review: `LESEN-R13-TRILINGUAL-SCOPED-REVIEW.json`; QA: `LESEN-R13-INDEPENDENT-STRUCTURAL-QA.json` and `LESEN-R13-v505-NATIVE-PREENTRY.json`.
- Durable candidate registration and Library readback must be checked before GitHub-backed completion is claimed; the source-owner current ZIP has SHA256 `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`.

**Next bounded outcome:** Analyze and repair generic p02/p03 claims without indiscriminately rewriting all sections. Then perform independent trilingual semantic QA and real isolated browser/IndexedDB Stage6 before publication. No UI change and no user review-state modification.
'''
(P/'LESEN-R13-EDITORIAL-AND-V505-REPORT-20261107.md').write_text(report,encoding='utf8')
print(json.dumps({'report':str(P/'LESEN-R13-EDITORIAL-AND-V505-REPORT-20261107.md'),'scoped_review_count':len(scoped),'checkpoint':str(P/'QUALITY-REVIEW-CHECKPOINT-R13-20261107.json'),'p03_repeated_opener':firstlines.most_common(1)},ensure_ascii=False))