#!/usr/bin/env python3
"""Generate a scoped R19 report and immutable candidate checkpoint from on-disk verified artifacts."""
from pathlib import Path
import json,hashlib
D=Path('/mnt/data/lesen_r19_20261108')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={
'master':D/'Lesen-Production-Master-v1.3.0-R19-10P06-TRILINGUAL-CANDIDATE.json',
'runtime':D/'Lesen-R19-v505-10P06-RUNTIME-PREENTRY-CANDIDATE.json',
'ledger':D/'LESEN-R19-10P06-EDITORIAL-GRAMMAR-LEDGER.json',
'qa':D/'LESEN-R19-INDEPENDENT-SOURCE-QA.json',
'native':D/'LESEN-R19-v505-NATIVE-PREENTRY.json'}
ids={'master':'libfile_74cb63a2ec84819191908243c70bcd16','runtime':'libfile_8e980e361f14819180b059014e63e3d5','ledger':'libfile_85ca87421b048191b2887b34631f7592','qa':'libfile_d6771f0a8b5881918df67f660f2446c2','native':'libfile_466600c2eb1881919a9175f6bc032784'}
qa=json.loads(P['qa'].read_text());native=json.loads(P['native'].read_text());led=json.loads(P['ledger'].read_text());assert not qa['failures'] and qa['structural_checks']==15569
assert all(q['rejected'] for q in qa['negative_probes']) and all(q['rejected'] for q in native['negative_probes'])
assert native['validation']['status']=='PASS' and not native['validation']['warnings']
assert H(P['master'])=='1a1fa9be4f61dd34a04264050cf12531168cd75920517f3d9315780b11acf4ff'
assert H(P['runtime'])=='365b774d8478bd98f6e111cafa66677abc1688cad76674102f6061109825254f'
root='/Flasch kart/German-Content-Production-Kit/Content/Lesen'
cp={
 'schema':'lesen-quality-review-checkpoint-r19@1.0.0','date':'2026-11-08','family_id':'family:lesen','owner':'Workspaces/lesen-praesentation',
 'state':'R19_TEN_TOPIC_SPECIFIC_P06_S02_SCOPED_STRUCTURAL_PASS__NATIVE_V505_PREENTRY_PASS__CURRENT_UNCHANGED_STAGE4_6_7_HOLD',
 'current_immutable':{'filename':'Lesen-Praesentation-B2-C1-v1.3.0-CONTENT-PRODUCTION-DELIVERY.zip','sha256':'558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565','library_file_id':'libfile_9b768265ff3c8191aca371baa38551d7','promoted':False},
 'parent_r18':{'content_sha256':'bfd469d4027f59d97cb25baabbefd79b0576f47f13acdc965f82850fc8a63c37','runtime_sha256':'a4d9669ff3db155380a69c74dcad5006d307e68718abdf8fa8a24fe83c64fe9f','library_content_id':'libfile_77fc5e6f6ea481919c978db6ca82fd80','library_runtime_id':'libfile_def17ad65c2081919225eeeb7f16aa05'},
 'candidate_content':{'name':P['master'].name,'sha256':H(P['master']),'bytes':P['master'].stat().st_size,'library_file_id':ids['master'],'library_path':root+'/Candidates/'+P['master'].name,'postupload_readback':'PASS_SHA256_AND_EXACT_BYTE_CMP_20261108','status':'CANDIDATE_NOT_CURRENT'},
 'candidate_runtime':{'name':P['runtime'].name,'sha256':H(P['runtime']),'bytes':P['runtime'].stat().st_size,'library_file_id':ids['runtime'],'library_path':root+'/Candidates/'+P['runtime'].name,'postupload_readback':'PASS_SHA256_AND_EXACT_BYTE_CMP_20261108','status':'PREENTRY_ONLY_NO_BROWSER_STAGE6'},
 'change_scope':{'lesson_numbers':list(range(11,21)),'source_sections_changed':10,'updated_german_sentences':10,'changed_fa_en_translation_pairs':8,'preserved_approved_fa_en_translation_pairs':2,'unmodified_lesson_objects':58,'unmodified_runtime_entries':58,'total_reading_units':68,'total_passages':478,'question_count_unchanged':340,'vocabulary_count_unchanged':350,'curated_grammar_count_unchanged':669,'fulltext_grammar_previous':4041,'retired_old_p06_s02_spans':40,'new_explicit_real_grammar_annotations':10,'fulltext_grammar_current':4011,'identical_original_p06_s02_remaining':48},
 'qa':{'structural_checks':qa['structural_checks'],'structural_errors':len(qa['failures']),'negative_input_mutations_rejected':sum(x['rejected'] for x in qa['negative_probes']),'exact_native_v505_source_sha256':native['current_v505_source_sha256'],'native_source_validator':'PASS_ZERO_WARNINGS','native_negative_inputs_rejected':sum(x['rejected'] for x in native['negative_probes']),'native_in_memory_projection':{'units':68,'questions':340},'full_independent_semantic_stage4':'HOLD','original_native_nine_lens_grammar_engine':'NOT_RERUN','actual_native_browser_indexeddb_stage6':'NOT_RUN','stage7_final':'NOT_RELEASED'},
 'evidence':{'grammar_and_translation_before_after':{'filename':P['ledger'].name,'sha256':H(P['ledger']),'library_file_id':ids['ledger']},'independent_qa':{'filename':P['qa'].name,'sha256':H(P['qa']),'library_file_id':ids['qa']},'native_v505_preentry':{'filename':P['native'].name,'sha256':H(P['native']),'library_file_id':ids['native']},'report':'Workspaces/lesen-praesentation/Reports/LESEN-R19-EDITORIAL-AND-V505-REPORT-20261108.md'},
 'next_step':'Review p06-s02 in lessons 021–030 selectively, then wholepack semantic checks (p01/p07/p06) and independent full trilingual Stage4 before promotion.',
 'no_change':['Original curated CURRENT pointer','German Flashcards app UI','User SRS/FSRS/progress','Other content workstreams','Existing R18 recovery files']}
report=f'''# Lesen R19 — zehn begründete eigene Positionen (p06-s02, Lektionen 011–020)

**Stand 08.11.2026:** scoped editorial + structural QA **PASS**; **R19 CANDIDATE**, nicht CURRENT, nicht FINAL.

## Autorität und Änderungen

- Parent ist das nutzerkuratierte **R18**, nicht ein älteres Lehrbuch. Master SHA `bfd469d4027f59d97cb25baabbefd79b0576f47f13acdc965f82850fc8a63c37`.
- 10 identische, sehr generische Schluss-Sätze der eigenen Position (`p06-s02`) in **LES-PRES-011–020** durch konkret zum Unterrichtsthema passende DE-Sätze ersetzt; jeweilige `p06-s01` und alle anderen Abschnitte unverändert.
- **8 FA/EN-Absatzpaare** im genauen Schlussteil angepasst; die in 018 (ehrliches, konkretes Lob/Kritik) und 020 (Bedürfnisse und Studienqualität) bereits sinnvollen Übersetzungen **unverändert** übernommen.
- 58 von 68 Master-Einträgen und exakt dieselben 58 Runtime-Einträge unberührt. 340 Fragen, 350 Vokabeleinträge, 669 kuratierte Grammatikreferenzen erhalten.
- 48 identische ursprüngliche `p06-s02` verbleiben. Andere wiederholte Muster in p01/p07 noch nicht ganzheitlich verbessert.

## Belegbares Beispiel

**Lektion 018 — Wie viel Lob brauchen Kinder?**

- **Vorher DE:** Wichtig ist, dass die Entscheidung nachvollziehbar begründet wird und nicht allein auf Gewohnheit, Idealvorstellungen oder kurzfristigen Eindrücken beruht.
- **Jetzt DE:** Deshalb sollten sowohl Lob als auch Kritik ehrlich, konkret und auf die Entwicklung des Kindes ausgerichtet sein.
- **FA bereits passend, unverändert:** مهم این است که تحسین و نقد هر دو صادقانه، مشخص و با هدف کمک به رشد کودک باشند.
- **EN bereits passend, unverändert:** Both praise and criticism should be sincere, specific, and aimed at helping the child grow.

Alle 10 vorher/nachher DE/FA/EN-Paare stehen im JSON-Ledger `LESEN-R19-10P06-EDITORIAL-GRAMMAR-LEDGER.json`, SHA `{H(P['ledger'])}`.

## Grammatik — ehrliche Scope-Abgrenzung

- Vorher 4041 gültige Fulltext-Vorkommen. 40 ursprüngliche Marker an den ersetzten generischen `p06-s02`-Sätzen entfernt; 10 neue am real vorliegenden Satzbau kontrolliert annotiert (u.a. **damit, wenn, ob, weil, um … zu, sollte/sollten**).
- **Jetzt 4011 exakt positionierte Vorkommen** im Master **und** im abgeleiteten v505-Runtime. Die übrigen Marker und alle 669 kuratierten Grammatik-IDs unverändert.
- Neuannotationen tragen klar `R19_MANUAL_SCOPED_EDITORIAL`; **der ursprüngliche 9-Linsen-Generator wurde NICHT neu ausgeführt**. Geerbte historische Wortzählungsmetadaten wurden nicht pauschal überschrieben. Master 001 hat unverändert neun statt sieben Abschnitte; die unabhängige QA akzeptiert das nach Parent-Abgleich.

## Read-only und v505-Prüfung

- Unabhängige lesende Quell-/Runtimeprüfung: **{qa['structural_checks']:,} / {qa['structural_checks']:,} PASS**, {len(qa['failures'])} Fehler; **9/9 mutierte Testfälle abgewiesen**.
- Exakt dieselbe Datei `reading-content-import-v38.js` wie im gepinnten v505-App-ZIP, SHA `{native['current_v505_source_sha256']}`: **PASS, null Warnungen**, **10/10 gezielt defekte Runtime-Payloads abgelehnt**.
- Isolierte In-Memory-Projektion **68 Lerneinheiten / 340 Aufgaben** erfolgreich, 478 Textabschnitte in DE/FA/EN. **Keine echte Browser-IndexedDB-Transaktion:** Stage6 ist weiterhin **NOT_RUN**.
- Vollständige unabhängige semantische DE/FA/EN Stage4 **HOLD**; Release Stage7 **NOT_RELEASED**.

## Kandidaten, SHA-256 und Ablage

- Content: `{P['master'].name}`, `{H(P['master'])}`, {P['master'].stat().st_size:,} Bytes; Library `{ids['master']}`. **Post-upload SHA256 und Byte-CMP PASS.**
- Runtime: `{P['runtime'].name}`, `{H(P['runtime'])}`, {P['runtime'].stat().st_size:,} Bytes; Library `{ids['runtime']}`. **Post-upload SHA256 und Byte-CMP PASS.**
- Unverändertes CURATED CURRENT ZIP v1.3.0 SHA `558c165df7603c26b775781f9c9bbd508c456b4b24f68979ebe0edecf3b46565`.

## Weiter

Die **48** verbleibenden `p06-s02` nach Qualität und Sinn, nicht bloß automatischer Variation, in begrenzten Gruppen bearbeiten. Weitere Qualitätsrisiken in Einleitungen/Synthesen (p01/p07) und vollständige Sprachprüfung pro 68 Lerneinheiten separat priorisieren. Keine UI-, FSRS-, Fortschritts- oder andere Familienänderung.
'''
(D/'LESEN-R19-EDITORIAL-AND-V505-REPORT-20261108.md').write_text(report,encoding='utf-8')
(D/'QUALITY-REVIEW-CHECKPOINT-R19-20261108.json').write_text(json.dumps(cp,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('checkpoint_sha',H(D/'QUALITY-REVIEW-CHECKPOINT-R19-20261108.json'))
print('report_sha',H(D/'LESEN-R19-EDITORIAL-AND-V505-REPORT-20261108.md'))