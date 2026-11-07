#!/usr/bin/env python3
"""R3: explicit AI-scoped, source-exact grammar annotations for three edited Lesen units.

This is NOT a rerun of the missing original `reading_fulltext_grammar_v1` generator.
Do not edit historical v1.3.0 or previous R2; do not infer full 9-lens coverage.
"""
import copy,hashlib,json,re
from pathlib import Path
from collections import Counter
ROOT=Path('/mnt/data/lesen_r2_20261107')
OUT=Path('/mnt/data/lesen_r3_20261107');OUT.mkdir(exist_ok=True)
INPUT=ROOT/'Lesen-Production-Master-v1.3.0-R2-3UNIT-EDITORIAL-CANDIDATE.json'
OUTPUT=OUT/'Lesen-Production-Master-v1.3.0-R3-3UNIT-GRAMMAR-CANDIDATE.json'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert SHA(INPUT)=='bbeec4c3823879b5037c3669edbc41f2a441662312887f84a8f0ee9bb2e61549'
base=json.loads(INPUT.read_text())
next_data=copy.deepcopy(base)
# Declarative review decisions are about exact literal text in the already curated R2
# sentences, not claims about old textbook source fidelity.
# (unit number, sentence id, grammar lens, exact target, German explanation, Persian explanation)
T=[
(35,'p02-s03','connectors','So','So führt hier eine Folge der zuvor beschriebenen Möglichkeiten ein.','«So» در اینجا نتیجهٔ امکانات مطرح‌شده را معرفی می‌کند.'),
(35,'p02-s03','relative_clauses_all','die mit rein analogen Materialien schwerer zugänglich wären','Der Relativsatz bezieht sich auf „Lernmöglichkeiten“; das finite Verb „wären“ steht am Ende.','جملهٔ موصولی به «Lernmöglichkeiten» برمی‌گردد و فعل صرف‌شدهٔ «wären» در انتها می‌آید.'),
(35,'p02-s03','adjective_declension_all','analogen','„analogen“ ist ein attributives Adjektiv zu „Materialien“ im Dativ Plural nach „mit“.','«analogen» صفت وابسته به «Materialien» در داتیو جمع پس از «mit» است.'),
(35,'p02-s03','konjunktiv_ii','wären','„wären“ ist Konjunktiv II von „sein“ und formuliert hier eine hypothetische Bewertung.','«wären» حالت Konjunktiv II فعل «sein» است و در این جمله ارزیابی فرضی را می‌رساند.'),
(35,'p02-s03','verb_position','wären','Im Relativsatz steht das finite Verb „wären“ am Ende.','در جملهٔ موصولی، فعل صرف‌شدهٔ «wären» در انتها قرار می‌گیرد.'),
(35,'p03-s03','subordinate_clauses_all','Wenn Schulen voraussetzen, dass alle Lernenden über geeignete eigene Geräte verfügen','Der Bedingungssatz mit „wenn“ enthält einen eingebetteten dass-Satz; der Hauptsatz beginnt mit „kann“.','جملهٔ شرطی با «wenn» یک جملهٔ وابستهٔ «dass» را در خود دارد؛ جملهٔ اصلی با «kann» شروع می‌شود.'),
(35,'p03-s03','subordinate_clauses_all','dass alle Lernenden über geeignete eigene Geräte verfügen','Der dass-Satz ist die Ergänzung zu „voraussetzen“; das finite Verb „verfügen“ steht am Ende.','جملهٔ «dass» متمم فعل «voraussetzen» است و «verfügen» در پایان قرار دارد.'),
(35,'p03-s03','verb_position','verfügen','„verfügen“ steht am Ende des eingebetteten dass-Satzes.','«verfügen» در انتهای جملهٔ وابستهٔ «dass» قرار گرفته است.'),
(35,'p03-s03','verbs_with_prepositions','über geeignete eigene Geräte verfügen','„über etwas verfügen“ regiert die Präposition „über“ mit Akkusativ.','ساختار «über etwas verfügen» حرف اضافهٔ «über» با حالت آکوزاتیو می‌گیرد.'),
(35,'p03-s03','adjective_declension_all','geeignete','Attributives Adjektiv vor „Geräte“; nach „über“ steht hier Akkusativ Plural.','صفت وابسته به «Geräte» است؛ پس از «über» در این عبارت آکوزاتیو جمع داریم.'),
(35,'p03-s03','adjective_declension_all','eigene','Attributives Adjektiv zu „Geräte“ im Akkusativ Plural.','صفت «eigene» برای «Geräte» در آکوزاتیو جمع آمده است.'),
(35,'p03-s03','adjective_declension_all','bestehende','„bestehende“ bestimmt „Unterschiede“ im Akkusativ Plural.','«bestehende» صفت «Unterschiede» در آکوزاتیو جمع است.'),
(35,'p04-s01','adjective_declension_all','faire','„faire“ steht attributiv vor dem pluralischen Nomen „Zugangsbedingungen“.','«faire» صفت وابسته به اسم جمع «Zugangsbedingungen» است.'),
(35,'p04-s01','adjective_declension_all','sinnvoller','„sinnvoller“ steht attributiv nach „ein“ bei „Einsatz“ (Nominativ Maskulinum).','«sinnvoller» پس از «ein» برای «Einsatz» در حالت فاعلی مذکر آمده است.'),
(35,'p04-s03','subordinate_clauses_all','welche Geräte welche Lernziele unterstützen','Der mit „welche“ eingeleitete indirekte Fragesatz steht als Ergänzung zu „prüfen“.','پرسش غیرمستقیم با «welche» به‌عنوان متمم «prüfen» آمده است.'),
(35,'p04-s03','verb_position','unterstützen','Das finite Verb „unterstützen“ steht am Ende der indirekten Frage.','فعل صرف‌شدهٔ «unterstützen» در انتهای پرسش غیرمستقیم قرار دارد.'),
(35,'p04-s03','infinitive_with_zu','statt sich pauschal für oder gegen Digitalisierung zu entscheiden','„statt ... zu“ bezeichnet eine Alternative; „entscheiden“ steht im zu-Infinitiv.','ساختار «statt ... zu» یک جایگزین را بیان می‌کند و «entscheiden» به‌شکل مصدر با «zu» آمده است.'),
(51,'p02-s03','connectors','deshalb','„deshalb“ signalisiert eine Folgerung aus den zuvor genannten Einflüssen.','«deshalb» نتیجه‌ای از عوامل مطرح‌شدهٔ قبلی را نشان می‌دهد.'),
(51,'p02-s03','adjective_declension_all','individuelle','Attributives Adjektiv zu „Vorlieben“ im Nominativ Plural.','«individuelle» صفت وابسته به «Vorlieben» در حالت فاعلی جمع است.'),
(51,'p02-s03','adjective_declension_all','soziale','„soziale“ steht nach dem bestimmten Artikel „das“ vor „Umfeld“.','«soziale» پس از آرتیکل معین «das» و پیش از «Umfeld» آمده است.'),
(51,'p02-s03','passive','werden auch durch das soziale Umfeld beeinflusst','Vorgangspassiv mit „werden“ und Partizip II „beeinflusst“; das Agens steht mit „durch“.','مجهول فرایندی با «werden» و قسمت سوم «beeinflusst» ساخته شده و عامل با «durch» آمده است.'),
(51,'p03-s01','connectors','Allerdings','„allerdings“ leitet eine Einschränkung des vorherigen Arguments ein.','«allerdings» محدودیتی بر استدلال پیشین وارد می‌کند.'),
(51,'p03-s03','connectors','Deshalb','„deshalb“ kennzeichnet hier eine Schlussfolgerung.','«deshalb» در اینجا نتیجه‌گیری را نشان می‌دهد.'),
(51,'p03-s03','konjunktiv_ii','sollte','„sollte“ drückt hier eine vorsichtige Empfehlung aus, kein vergangenes Ereignis.','«sollte» در اینجا توصیه‌ای محتاطانه است، نه رویداد گذشته.'),
(51,'p03-s03','adjective_declension_all','einzelne','„einzelne“ steht nach „keine“ vor „Ursache“ (Nominativ Femininum).','«einzelne» پس از «keine» پیش از «Ursache» در نومیناتیو مؤنث آمده است.'),
(51,'p03-s03','adjective_declension_all','vollständige','„vollständige“ steht nach „als“ attributiv vor „Erklärung“.','«vollständige» پس از «als» صفت وابسته به «Erklärung» است.'),
(51,'p04-s01','connectors','daher','„daher“ macht eine Folgerung aus dem vorherigen Abschnitt deutlich.','«daher» نتیجه‌گیری از بخش قبلی را نشان می‌دهد.'),
(51,'p04-s01','subordinate_clauses_all','ob junge Menschen vielfältige Erfahrungen sammeln und sich über Studienwege informieren können','Der ob-Satz ist eine indirekte Ja/Nein-Frage; „können“ schließt den Verbkomplex ab.','جملهٔ «ob» پرسش غیرمستقیم بله/خیر است و «können» گروه فعلی را در انتها می‌بندد.'),
(51,'p04-s01','adjective_declension_all','junge','„junge“ steht attributiv vor dem Nomen „Menschen“.','«junge» به‌صورت صفت وابسته پیش از «Menschen» آمده است.'),
(51,'p04-s01','adjective_declension_all','vielfältige','„vielfältige“ steht attributiv vor „Erfahrungen“.','«vielfältige» صفت وابسته به «Erfahrungen» است.'),
(51,'p04-s01','verbs_with_prepositions','sich über Studienwege informieren','„sich über etwas informieren“ verbindet das Verb mit „über“ + Akkusativ.','ساختار «sich über etwas informieren» با «über» و آکوزاتیو همراه است.'),
(51,'p04-s01','verb_position','können','Das Modalverb „können“ steht am Ende des indirekten ob-Satzes.','فعل وجهی «können» در انتهای جملهٔ غیرمستقیم «ob» قرار دارد.'),
(51,'p04-s03','subordinate_clauses_all','ob solche Angebote die freie Studienwahl fördern','Der ob-Satz nennt die Frage, die geprüft werden soll.','جملهٔ «ob» پرسشی را بیان می‌کند که باید بررسی شود.'),
(51,'p04-s03','infinitive_with_zu','ohne neue Rollenerwartungen zu schaffen','„ohne ... zu“ nennt eine Handlung, die vermieden werden soll.','ساختار «ohne ... zu» کاری را نشان می‌دهد که باید از آن پرهیز شود.'),
(51,'p04-s03','adjective_declension_all','neue','„neue“ steht attributiv vor „Rollenerwartungen“.','«neue» صفت وابسته به «Rollenerwartungen» است.'),
(59,'p02-s03','infinitive_with_zu','ein Studium mit anderen Verpflichtungen zu verbinden','„zu verbinden“ ist ein zu-Infinitiv nach „erleichtert es“.','«zu verbinden» مصدر با «zu» پس از «erleichtert es» است.'),
(59,'p02-s03','adjective_declension_all','anderen','„anderen“ bestimmt „Verpflichtungen“ nach „mit“ im Dativ Plural.','«anderen» به «Verpflichtungen» در داتیو جمع پس از «mit» مربوط است.'),
(59,'p03-s01','connectors','jedoch','„jedoch“ leitet hier eine Einschränkung beziehungsweise einen Gegensatz ein.','«jedoch» در اینجا محدودیت یا تقابل را بیان می‌کند.'),
(59,'p03-s01','subordinate_clauses_all','während Fernstudiengänge unterschiedlich intensiv betreut werden','„während“ verbindet hier zwei kontrastierende Aussagen, nicht zwei Zeitpunkte.','«während» در اینجا دو گزاره را در تقابل قرار می‌دهد، نه دو زمان را.'),
(59,'p03-s03','connectors','Deshalb','„deshalb“ leitet die Schlussfolgerung aus dem Vergleich ein.','«deshalb» نتیجهٔ مقایسه را معرفی می‌کند.'),
(59,'p03-s03','adjective_declension_all','nötige','„nötige“ ist ein attributives Adjektiv nach dem bestimmten Artikel „der“.','«nötige» صفت وابسته پس از آرتیکل معین «der» است.'),
(59,'p04-s01','connectors','daher','„daher“ markiert hier eine Folgerung.','«daher» در اینجا نتیجه‌گیری را مشخص می‌کند.'),
(59,'p04-s03','connectors','Deshalb','„deshalb“ verbindet die Empfehlung mit dem vorherigen Argument.','«deshalb» توصیه را به استدلال قبلی پیوند می‌دهد.'),
(59,'p04-s03','adjective_declension_all','verfügbarer','„verfügbarer“ steht attributiv zu „Zeit“ nach „von“ (Dativ Femininum).','«verfügbarer» صفت وابسته به «Zeit» پس از «von» در داتیو مؤنث است.'),
(59,'p04-s03','verbs_with_prepositions','von Lernzielen, verfügbarer Zeit und der Qualität der Betreuung abhängen','„abhängen von“ verlangt Dativ. Die von-Phrase ist die Ergänzung zu „abhängen“.','ساختار «abhängen von» داتیو می‌گیرد و گروه «von» متمم فعل است.')
]
LABELS={
 'adjective_declension_all':'Adjektivdeklination','subordinate_clauses_all':'Nebensatz',
 'relative_clauses_all':'Relativsatz','verb_position':'Verbposition im Nebensatz',
 'konjunktiv_ii':'Konjunktiv II','passive':'Vorgangspassiv',
 'infinitive_with_zu':'Infinitiv mit zu','connectors':'Konnektoren','verbs_with_prepositions':'Verben mit Präpositionen'}
counts=Counter();seen=set();delta=[]
for n,sid,key,match,de,fa in T:
 assert key in LABELS and de and fa
 unit=next_data['items'][n-1]
 secid=sid.split('-')[0]
 section=next(s for s in unit['reading']['sections'] if s['id']==secid)
 sent=next(s for s in section['sentences'] if s['id']==sid)
 assert sent['text'].count(match)==1,(n,sid,key,match,'ambiguous/missing')
 assert section['text'].count(sent['text'])==1
 offset=section['text'].index(sent['text'])+sent['text'].index(match)
 assert section['text'][offset:offset+len(match)]==match
 identity=(n,sid,key,match)
 assert identity not in seen;seen.add(identity)
 existing=[x for x in unit['grammar']['full_text_occurrences'] if x['sentence_id']==sid and x['grammar_key']==key and x['target_text']==match]
 if existing:raise AssertionError(('duplicates existing',identity))
 # ID is stable for all existing and uses a separate namespace for curated AI additions.
 counts[n]+=1;gid=f'ftg-r3-{n:03d}-{counts[n]:03d}'
 obj={'id':gid,'grammar_key':key,'label_de':LABELS[key],
      'section_id':secid,'sentence_id':sid,'start':offset,'end':offset+len(match),
      'target_text':match,'explanation_de':de,'explanation_fa':fa,
      'details':{'evidence':'R2 sentence text; exact section character offsets', 'context_review':'explicit_narrow_scope'},
      'confidence':'high','annotation_source':'ai_scoped_exact_r3',
      'derivation_method':'explicit_reviewed_target_in_R2_sentence'}
 unit['grammar']['full_text_occurrences'].append(obj)
 delta.append({'unit_id':unit['id'],'sentence_id':sid,'annotation_id':gid,'grammar_key':key,'target_text':match,'start':offset,'end':offset+len(match)})
# Correct concrete pre-existing annotations whose explanations make misleading claims.
# These are in the 3 affected lessons, and are reversible by comparison to immutable R2.
fixes=[]
for n,oldid in [(35,'ftg-0005'),(51,'ftg-0005'),(59,'ftg-0002')]:
 unit=next_data['items'][n-1];occ=next(x for x in unit['grammar']['full_text_occurrences'] if x['id']==oldid)
 assert occ['target_text']=='als es zunächst scheint' and occ['grammar_key']=='subordinate_clauses_all'
 before={'label_de':occ['label_de'],'explanation_de':occ['explanation_de'],'explanation_fa':occ['explanation_fa'],'details':copy.deepcopy(occ['details'])}
 occ['label_de']='Vergleichssatz mit als'
 occ['explanation_de']='„als“ leitet hier einen Vergleich mit „weniger ... als“ ein; es bezeichnet keinen vergangenen Zeitpunkt.'
 occ['explanation_fa']='«als» در ساختار مقایسه‌ای «weniger ... als» به کار رفته و در اینجا زمان گذشته را بیان نمی‌کند.'
 occ['details']={'trigger':'als','function':'comparison_weniger_als'}
 occ['annotation_source']='ai_scoped_corrective_review_r3'
 fixes.append({'unit_id':unit['id'],'old_annotation_id':oldid,'reason':'old explanation falsely described temporal past for comparative als','before':before,'after':{'label_de':occ['label_de'],'explanation_de':occ['explanation_de'],'explanation_fa':occ['explanation_fa'],'details':occ['details']}})
# A fragment was presented as an entire subordinate clause: replace with the exact full clause.
n=59;unit=next_data['items'][n-1];occ=next(x for x in unit['grammar']['full_text_occurrences'] if x['id']=='ftg-0028')
assert occ['target_text']=='Wenn digitale Betreuung'
new_target='Wenn digitale Betreuung, feste Termine und Lerngruppen verbindlich vorgesehen sind'
sec=next(s for s in unit['reading']['sections'] if s['id']=='p04')
sent=next(s for s in sec['sentences'] if s['id']=='p04-s02')
assert new_target in sent['text'] and sec['text'].count(new_target)==1
before={'target_text':occ['target_text'],'start':occ['start'],'end':occ['end'],'explanation_de':occ['explanation_de'],'explanation_fa':occ['explanation_fa']}
occ['start']=sec['text'].index(new_target);occ['end']=occ['start']+len(new_target);occ['target_text']=new_target
occ['explanation_de']='Der wenn-Satz nennt die Bedingung; das finite Verb „sind“ steht am Ende des Nebensatzes.'
occ['explanation_fa']='جملهٔ «wenn» شرط را بیان می‌کند و فعل صرف‌شدهٔ «sind» در پایان جملهٔ وابسته قرار دارد.'
occ['annotation_source']='ai_scoped_corrective_review_r3';occ['derivation_method']='explicit_exact_clause_repair_r3'
fixes.append({'unit_id':unit['id'],'old_annotation_id':occ['id'],'reason':'fragment expanded to complete conditional clause with exact offsets','before':before,'after':{'target_text':occ['target_text'],'start':occ['start'],'end':occ['end'],'explanation_de':occ['explanation_de'],'explanation_fa':occ['explanation_fa']}})
# Old "wichtiger" is predicative comparative, not an attributive declension; exclude from wrong lens.
u=next_data['items'][34];wrong=next(x for x in u['grammar']['full_text_occurrences'] if x['id']=='ftg-0042')
assert wrong['target_text']=='wichtiger' and wrong['grammar_key']=='adjective_declension_all'
u['grammar']['full_text_occurrences'].remove(wrong)
fixes.append({'unit_id':u['id'],'old_annotation_id':'ftg-0042','reason':'predicative comparative; not adjective declension; no matching accepted lens','removed_annotation':wrong})
# "Damit wird deutlich" is a main clause, not a subordinate clause; eliminate false tag (035,059).
for n,wrongid in ((35,'ftg-0063'),(59,'ftg-0059')):
 u=next_data['items'][n-1];wrong=next(x for x in u['grammar']['full_text_occurrences'] if x['id']==wrongid)
 assert wrong['target_text']=='Damit wird deutlich' and wrong['grammar_key']=='subordinate_clauses_all'
 u['grammar']['full_text_occurrences'].remove(wrong)
 fixes.append({'unit_id':u['id'],'old_annotation_id':wrongid,'reason':'Damit wird deutlich is a main clause, not subordinating clause','removed_annotation':wrong})
# The word "während" as contrasting conjunction is already annotated independently in R3.
# Reorder exact section spans in sensible display order and update all derived counts.
for n in (35,51,59):
 u=next_data['items'][n-1]
 sectionrank={s['id']:i for i,s in enumerate(u['reading']['sections'])}
 u['grammar']['full_text_occurrences'].sort(key=lambda x:(sectionrank[x['section_id']],x['start'],x['end'],x['id']))
 g=u['grammar']['full_text_lens_summary'];allg=u['grammar']['full_text_occurrences'];g['occurrences']=len(allg);g['counts']=dict(Counter(x['grammar_key'] for x in allg))
 g['scope_note_de']='R3: neue AI-geprüfte exakte Einzelstellen nach R2-Text und gezielte Korrekturen falscher Altlabels; Original-Engine NICHT erneut ausgeführt, vollständige Neuanalyse NICHT bestätigt.'
 g['scope_note_fa']='در R3 نشانه‌های جدید فقط با متن دقیق R2 بررسی و چند برچسب نادرست قدیمی اصلاح شده‌اند؛ موتور اصلی دوباره اجرا نشده و پوشش کامل تأیید نشده است.'
 u['quality']['app_mapping_status']='not_compiled_editorial_grammar_candidate'
next_data['content_version']='1.3.0-R3-GRAMMAR-SCOPED-CANDIDATE'
next_data['status']='R3_SCOPED_GRAMMAR_CANDIDATE__SOURCE_ENGINE_UNAVAILABLE__STAGE4_STAGE6_HOLD'
next_data['full_text_grammar_qa']['occurrences']=sum(len(u['grammar']['full_text_occurrences']) for u in next_data['items'])
next_data['full_text_grammar_qa']['counts']=dict(Counter(x['grammar_key'] for u in next_data['items'] for x in u['grammar']['full_text_occurrences']))
next_data['full_text_grammar_qa']['offset_exact_matches']=next_data['full_text_grammar_qa']['occurrences']
next_data['full_text_grammar_qa']['result']='INCOMPLETE_R3_SCOPED_EXACT_GRAMMAR_OVERLAY__ORIGINAL_ENGINE_NOT_RERUN'
next_data['full_text_grammar_qa']['r3_review_status']='AI_SCOPED_EXACT_CURATED_OVERLAY_WITH_FALSE_LABEL_REPAIRS__NOT_NATIVE_FULL_ENGINE'
next_data['qa_summary']['r3_quality_gate']='SCOPED_GRAMMAR_ANNOTATIONS_EXACT_AND_GRAMMAR_FALSE_POSITIVES_CORRECTED__STAGE4_AND_NATIVE_STAGE6_HOLD'
next_data['translation_qa']['r3_review_status']='3_R2_EDITED_UNITS_SPOT_CHECKED_WITH_GRAMMAR_EXPLANATION_DE_FA__INDEPENDENT_FULL_STAGE4_PENDING'
OUTPUT.write_text(json.dumps(next_data,ensure_ascii=False,indent=2)+'\n')
ledger={'schema':'lesen-r3-scoped-grammar-ledger@1.0.0','date':'2026-11-07','r2_parent_sha256':SHA(INPUT),'r3_candidate_sha256':SHA(OUTPUT),'additions':len(delta),'additions_by_unit':dict(counts),'added_exact_annotations':delta,'legacy_corrections':fixes,'old_removed_due_to_changed_text':34,'original_fulltext_engine_rerun':False,'no_claim_of_34_for_34_restoration':True,'production_master_or_runtime_promotion':False,'advisory':'This annotates attested grammatical facts in revised sentences, not an exhaustive regeneration of all nine native lenses.'}
(OUT/'LESEN-R3-SCOPED-GRAMMAR-LEDGER-20261107.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'r3':str(OUTPUT),'sha256':SHA(OUTPUT),'added':len(delta),'count_by_unit':dict(counts),'corrected_existing':len(fixes),'total_grammar':next_data['full_text_grammar_qa']['occurrences']},ensure_ascii=False,indent=2))