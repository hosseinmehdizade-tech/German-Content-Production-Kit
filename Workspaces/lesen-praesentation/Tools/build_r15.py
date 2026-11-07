#!/usr/bin/env python3
"""R14 -> R15: 25 topic-specific concluding sentences in p02/p03, 14 lessons.
The user's latest curated R14 candidate is authority. No source-book rewind.
Preserve all unchanged first two sentences DE/FA/EN; retire stale s03 grammar,
retarget existing legitimate relative-clause curated samples only.
Not the native nine-lens grammar generator and not Stage4 language certification.
"""
import pathlib,json,hashlib,copy,re,collections
P=pathlib.Path('/mnt/data/lesen_r15_20261107');P.mkdir(exist_ok=True)
BASE=pathlib.Path('/mnt/data/lesen_r14_20261107/Lesen-Production-Master-v1.3.0-R14-14P03-TRILINGUAL-CANDIDATE.json')
OUT=P/'Lesen-Production-Master-v1.3.0-R15-25CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
LED=P/'LESEN-R15-25CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json'
PARENT='40f4eee25d4ea541d33f91f327bc88243ec5e2971419927ae43c2f0035af2568'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda obj:json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Explicit individually authored last sentences, grounded in source p02/p03 first two
# and supported by the user's existing lesson. Tuple: German, Persian, English.
E={
11:{
'p02':('Zusätzliche Einnahmen könnten vor allem dann die Studienbedingungen verbessern, wenn sie tatsächlich in Lehre und Ausstattung fließen.','درآمدهای اضافی به‌ویژه زمانی می‌توانند شرایط تحصیل را بهتر کنند که واقعاً صرف آموزش و امکانات دانشگاه شوند.','Additional income could improve study conditions particularly if it is actually invested in teaching and facilities.'),
'p03':('Wenn Gebühren den Hochschulzugang vom Geldbeutel abhängig machen, widerspricht das dem Anspruch auf faire Bildungschancen.','اگر شهریه دسترسی به دانشگاه را به توان مالی وابسته کند، این موضوع با اصل فرصت‌های آموزشی عادلانه در تضاد است.','If fees make access to university dependent on financial means, that conflicts with the goal of fair educational opportunities.')},
12:{
'p02':('Beim gemeinsamen Sport üben Kinder Formen des Miteinanders, die auch außerhalb der Turnhalle wichtig sind.','کودکان هنگام ورزش گروهی شیوه‌های تعامل با دیگران را تمرین می‌کنند که بیرون از سالن ورزش هم اهمیت دارند.','Through sport together, children practise ways of interacting that also matter outside the gym.'),
'p03':('Eine Bewertung, die nur sportliche Leistung belohnt, kann dagegen ausgerechnet die Freude an Bewegung verringern.','در مقابل، ارزیابی‌ای که فقط عملکرد ورزشی را تشویق کند، ممکن است اتفاقاً لذت حرکت و ورزش را کاهش دهد.','An assessment that rewards only athletic performance can, by contrast, diminish enjoyment of physical activity.')},
13:{'p02':('Von diesem Austausch können auch örtliche Betriebe profitieren, die Reisenden Dienstleistungen anbieten.','کسب‌وکارهای محلی که به مسافران خدمات ارائه می‌کنند نیز می‌توانند از این تبادل سود ببرند.','Local businesses that provide services to travellers can also benefit from this exchange.')},
14:{
'p02':('Literarische Gespräche eröffnen damit Perspektiven, die im gewöhnlichen Schulalltag oft wenig Raum erhalten.','گفت‌وگوهای ادبی به این ترتیب دیدگاه‌هایی را مطرح می‌کنند که در زندگی عادی مدرسه اغلب فرصت کمی برای مطرح‌شدن دارند.','Literary discussions thus open up perspectives that often receive little attention in everyday school life.'),
'p03':('Ohne Wahlmöglichkeiten kann die Pflichtlektüre gerade jene Jugendlichen abschrecken, die noch einen Zugang zu Büchern suchen.','بدون امکان انتخاب، مطالعهٔ اجباری ممکن است دقیقاً نوجوانانی را دلسرد کند که هنوز در جست‌وجوی راهی برای ارتباط با کتاب‌اند.','Without any choice, compulsory reading can discourage precisely those young people who are still finding their way into books.')},
15:{
'p02':('Arbeitsmarktdaten liefern dabei eine Orientierung, die eine bewusste Studienentscheidung erleichtern kann.','داده‌های بازار کار در این زمینه راهنمایی فراهم می‌کنند که می‌تواند تصمیم‌گیری آگاهانه دربارهٔ رشتهٔ تحصیلی را آسان‌تر کند.','Labour-market data provide guidance that can make an informed choice of degree easier.'),
'p03':('Wer sich ausschließlich nach heutigen Jobprognosen richtet, übersieht womöglich sowohl eigene Interessen als auch spätere Veränderungen.','کسی که فقط به پیش‌بینی‌های شغلی امروز تکیه کند، ممکن است هم علاقه‌های خود و هم تغییرات آینده را نادیده بگیرد.','Anyone who relies solely on today’s job forecasts may overlook both personal interests and future changes.')},
16:{
'p02':('So können Gemeinschaften entstehen, die Erfahrungen austauschen und sich gegenseitig unterstützen.','به این ترتیب گروه‌هایی شکل می‌گیرند که تجربه‌هایشان را به اشتراک می‌گذارند و از یکدیگر حمایت می‌کنند.','Communities can thus develop in which people share experiences and support one another.'),
'p03':('Wer ständig erreichbar sein soll, kann trotz vieler Nachrichten das Gefühl echter Nähe vermissen.','کسی که انتظار می‌رود همیشه در دسترس باشد، ممکن است با وجود پیام‌های فراوان احساس نزدیکی واقعی نداشته باشد.','Someone expected to be constantly available may still miss a sense of genuine closeness despite receiving many messages.')},
17:{'p02':('Solche Erfahrungen können Interesse wecken, das Kinder auch in späteren Schuljahren zum Forschen motiviert.','چنین تجربه‌هایی می‌توانند علاقه‌ای ایجاد کنند که کودکان را در سال‌های بعد مدرسه نیز به پژوهش و کشف تشویق کند.','Such experiences can spark an interest that motivates children to explore science in later school years as well.')},
18:{
'p02':('Konkretes Lob macht Anstrengung und Fortschritt sichtbar, sodass Kinder ihren eigenen Lernweg besser verstehen.','تشویق مشخص تلاش و پیشرفت را قابل‌مشاهده می‌کند تا کودکان مسیر یادگیری خود را بهتر بفهمند.','Specific praise makes effort and progress visible, helping children understand their own learning process better.'),
'p03':('Ständige pauschale Bewunderung kann dagegen dazu führen, dass Kinder selbst bei kleinen Fehlern Bestätigung suchen.','در مقابل، تحسین دائمی و کلی ممکن است باعث شود کودکان حتی هنگام اشتباه‌های کوچک هم دنبال تأیید دیگران باشند.','Constant, indiscriminate admiration can instead make children seek approval even when they make small mistakes.')},
19:{
'p02':('Aus einer bahnbrechenden Erfindung können weitere Anwendungen entstehen, die anfangs niemand vorausgesehen hat.','یک اختراع تحول‌آفرین ممکن است به کاربردهای دیگری منجر شود که در آغاز هیچ‌کس پیش‌بینی نکرده بود.','A groundbreaking invention can lead to further applications that no one anticipated at first.'),
'p03':('Eine verantwortliche Bewertung technischer Neuerungen sollte deshalb auch mögliche Abhängigkeiten und Nebenwirkungen berücksichtigen.','بنابراین ارزیابی مسئولانهٔ نوآوری‌های فنی باید وابستگی‌ها و پیامدهای جانبی احتمالی را نیز در نظر بگیرد.','A responsible assessment of technological innovations should therefore consider possible dependencies and side effects.')},
20:{
'p02':('Das eröffnet Bildungschancen für Menschen, die wegen Beruf, Familie oder Wohnort nicht täglich auf den Campus fahren können.','این موضوع فرصت‌های تحصیلی را برای کسانی فراهم می‌کند که به دلیل شغل، خانواده یا محل زندگی نمی‌توانند هر روز به دانشگاه رفت‌وآمد کنند.','This opens educational opportunities for people who cannot travel to campus daily because of work, family or where they live.'),
'p03':('Die größere Freiheit verlangt daher feste Lernroutinen und Unterstützung, die bei Schwierigkeiten erreichbar bleibt.','بنابراین آزادی بیشتر به برنامهٔ منظم یادگیری و حمایتی نیاز دارد که هنگام دشواری‌ها در دسترس باشد.','Greater freedom therefore requires regular study routines and support that remains accessible when difficulties arise.')},
21:{'p02':('Ein Alumni-Netzwerk schafft damit Kontakte, die Studierende und Hochschulen auch nach dem Abschluss nutzen können.','شبکهٔ فارغ‌التحصیلان به این ترتیب ارتباط‌هایی ایجاد می‌کند که دانشجویان و دانشگاه‌ها حتی پس از فارغ‌التحصیلی می‌توانند از آن بهره ببرند.','An alumni network thus creates contacts that students and universities can use even after graduation.')},
22:{
'p02':('Kinder sammeln dabei Erfahrungen, die ihnen auch bei neuen praktischen Aufgaben zugutekommen können.','کودکان در این فعالیت‌ها تجربه‌هایی به دست می‌آورند که هنگام انجام کارهای عملی تازه نیز به آن‌ها کمک می‌کنند.','Children gain experiences that can also help them with new practical tasks.'),
'p03':('Schulen müssen deshalb abwägen, ob Zeit, Ausstattung und Fachpersonal für ein solches Angebot ausreichen.','بنابراین مدارس باید بسنجند که آیا زمان، امکانات و نیروی متخصص برای چنین برنامه‌ای کافی است یا نه.','Schools therefore need to consider whether time, equipment and specialist staff are sufficient for such a programme.')},
23:{
'p02':('Gezielte Fortbildung hilft Beschäftigten, neue Anforderungen zu erkennen und ihre Kenntnisse daran anzupassen.','آموزش تکمیلیِ هدفمند به کارکنان کمک می‌کند نیازهای جدید را بشناسند و دانش خود را با آن‌ها هماهنگ کنند.','Targeted further training helps employees recognise new requirements and adapt their skills accordingly.'),
'p03':('Weiterbildung sollte deshalb an echten beruflichen Bedürfnissen ansetzen, statt nur weitere Zertifikate zu produzieren.','بنابراین آموزش تکمیلی باید از نیازهای واقعی شغلی آغاز شود، نه اینکه فقط گواهی‌های بیشتری تولید کند.','Further training should therefore address genuine professional needs instead of merely producing more certificates.')},
24:{
'p02':('Eine solche Lernumgebung kann besonders denen helfen, die zu Hause nur schwer eine feste Arbeitsroutine finden.','چنین محیط یادگیری‌ای به‌ویژه به کسانی کمک می‌کند که در خانه به‌سختی می‌توانند برنامهٔ ثابت مطالعه داشته باشند.','Such a learning environment can particularly help those who struggle to establish a regular study routine at home.'),
'p03':('Für manche Lernende überwiegen deshalb die Vorteile eines ruhigen Arbeitsplatzes zu Hause ohne lange Anfahrtswege.','بنابراین برای بعضی یادگیرندگان، مزایای محیط آرام مطالعه در خانه بدون رفت‌وآمد طولانی بیشتر است.','For some learners, the advantages of a quiet workspace at home without long journeys therefore outweigh those of the library.')}
}
assert sorted(E)==list(range(11,25))
A=json.loads(BASE.read_text());B=copy.deepcopy(A)
assert sha(BASE.read_bytes())==PARENT and len(A['items'])==68
GENERIC={'p02':'Dadurch kann ein Nutzen entstehen, der über den unmittelbaren Einzelfall hinausgeht.','p03':'Ein Vorteil auf der einen Seite kann also durchaus neue Probleme auf der anderen Seite erzeugen.'}
ledger=[];retired=0;curated_retarget=0
for n,edits in E.items():
 u=B['items'][n-1];old=A['items'][n-1];assert u['id']==f'LES-PRES-{n:03d}'
 for sid,(de,fa,en) in edits.items():
  sec=next(s for s in u['reading']['sections'] if s['id']==sid);before=next(s for s in old['reading']['sections'] if s['id']==sid)
  assert len(sec['sentences'])==3 and sec['sentences'][-1]['id']==sid+'-s03'
  assert before['sentences'][-1]['text']==GENERIC[sid],(n,sid)
  assert de.endswith('.') and not de==GENERIC[sid]
  translation_prefix={}
  for lang,new_last in [('fa',fa),('en',en)]:
   original=before['translations'][lang]
   parts=re.split(r'(?<=[.!?؟])\s+',original)
   assert len(parts)==3,(n,sid,lang,len(parts),parts)
   assert new_last.endswith('.')
   translation_prefix[lang]=' '.join(parts[:-1])
   sec['translations'][lang]=translation_prefix[lang]+' '+new_last
  sec['sentences'][-1]['text']=de
  sec['text']=' '.join(s['text'] for s in sec['sentences'])
  for c in u['grammar']['curated_annotations']:
   if c['section_id']==sid and c['sentence_id']==sid+'-s03':
    assert c['grammar_key']=='relative_clause' and sid=='p02' and ', die ' in de or c['grammar_key']=='relative_clause' and sid=='p02' and (', der ' in de or ', denen ' in de or ', das ' in de or ', in denen ' in de),(n,c,de)
    c['target_text']=de
    c['annotation_source']='editorial_verified_relative_clause_r15'
    c['derivation_method']='retarget_existing_curated_sample_to_topic_specific_relative_clause_not_native_engine'
    curated_retarget+=1
  old_occ=[z for z in old['grammar']['full_text_occurrences'] if z['section_id']==sid and z['sentence_id']==sid+'-s03']
  assert len(old_occ)==(4 if sid=='p02' else 2),(n,sid,len(old_occ))
  old_ids={z['id'] for z in old_occ}
  u['grammar']['full_text_occurrences']=[z for z in u['grammar']['full_text_occurrences'] if z['id'] not in old_ids]
  retired+=len(old_occ)
  ledger.append({'unit_id':u['id'],'title_de':u['title_de'],'section_id':sid,
                 'sentence_id':sid+'-s03','before_de':before['sentences'][-1]['text'],'after_de':de,
                 'before_fa':before['translations']['fa'],'after_fa':sec['translations']['fa'],
                 'before_en':before['translations']['en'],'after_en':sec['translations']['en'],
                 'old_first_two_de_preserved':before['sentences'][:2]==sec['sentences'][:2],
                 'old_first_two_fa_en_prefix_preserved':translation_prefix,
                 'invalidated_fulltext_occurrences':old_occ})
 u['reading']['word_count_de']=len(' '.join(s['text'] for s in u['reading']['sections']).split())
 u['quality']['content_hash']=sha(' '.join(s['text'] for s in u['reading']['sections']).encode())[:16]
 u['quality']['app_mapping_status']='r15_scoped_p02_p03_conclusion_candidate_preentry_only'
 u['grammar']['full_text_lens_summary']['occurrences']=len(u['grammar']['full_text_occurrences'])
 u['grammar']['full_text_lens_summary']['counts']=dict(collections.Counter(z['grammar_key'] for z in u['grammar']['full_text_occurrences']))
 u['grammar']['full_text_lens_summary']['scope_note_de']='R15: nur veraltete Marker der ersetzten Schlussätze p02/p03 entfernt; alle übrigen Originalmarker auf Position und Zielsatz exakt geprüft. Keine native Neun-Linsen-Neuaufbereitung.'
 u['grammar']['full_text_lens_summary']['scope_note_fa']='در R15 فقط نشانگرهای جمله‌های پایانیِ جایگزین‌شده حذف و دیگر موارد دقیقاً بررسی شده‌اند؛ استخراج کامل گرامر انجام نشده است.'
 for c in u['grammar']['curated_annotations']:
  s=next(x for x in u['reading']['sections'] if x['id']==c['section_id'])
  t=next(x for x in s['sentences'] if x['id']==c['sentence_id'])
  assert c['target_text'] in t['text'],(n,c['id'])
assert len(ledger)==25 and retired==78 and curated_retarget==9,(len(ledger),retired,curated_retarget)
assert [n+1 for n,(x,y) in enumerate(zip(A['items'],B['items'])) if x!=y]==sorted(E)
allocc=[z for it in B['items'] for z in it['grammar']['full_text_occurrences']]
assert len(allocc)==4220
for it in B['items']:
 for z in it['grammar']['full_text_occurrences']:
  sec=next(s for s in it['reading']['sections'] if s['id']==z['section_id'])
  sent=next(s for s in sec['sentences'] if s['id']==z['sentence_id'])
  assert sec['text'][z['start']:z['end']]==z['target_text'] and z['target_text'] in sent['text'],(it['id'],z['id'])
qa=B['full_text_grammar_qa'];qa['occurrences']=len(allocc);qa['offset_exact_matches']=len(allocc)
qa['counts']=dict(collections.Counter(z['grammar_key'] for z in allocc))
qa['result']='R15_EXACT_SCOPED_CONCLUSION_REWRITE_OFFSETS__NATIVE_FULL_ENGINE_NOT_RERUN__STAGE4_HOLD'
qa['r15_scope']={'units':len(E),'sections':len(ledger),'old_generic_s03_spans_retired':retired,'retargeted_legitimate_curated_relative_clauses':curated_retarget,'other_offsets_preserved_exact':True,'new_manually_invented_fulltext_markers':0,'native_nine_lens_engine_rerun':False}
wc=[u['reading']['word_count_de'] for u in B['items']]
B['qa_summary']['word_count_de']={'min':min(wc),'mean':round(sum(wc)/len(wc),1),'max':max(wc)}
B['qa_summary']['r15_scope']='25_SOURCE_GROUNDED_P02_P03_CONCLUSIONS_ON_14_UNITS__NO_NEW_AUTOMATIC_GRAMMAR'
B['translation_qa']['r15_review_status']='AI_SCOPED_25_SENTENCE_TRILINGUAL_REVIEW_NOT_INDEPENDENT_STAGE4'
B['content_version']='1.3.0-R15-CANDIDATE'
B['status']='R15_14UNIT_25CONCLUSIONS_TRILINGUAL_AND_EXACT_OFFSET_CANDIDATE__STAGE4_6_7_HOLD'
write(OUT,B)
remaining={sid:sum(1 for i in B['items'] if next(x for x in i['reading']['sections'] if x['id']==sid)['sentences'][-1]['text']==GENERIC[sid]) for sid in GENERIC}
record={'schema':'lesen-r15-25-conclusion-editorial-grammar-ledger@1.0.0','date':'2026-11-07',
'parent_r14_content_sha256':PARENT,'r15_content_sha256':sha(OUT.read_bytes()),'size_bytes':OUT.stat().st_size,
'changed_units':[f'LES-PRES-{n:03d}' for n in sorted(E)],'changed_unit_count':len(E),'changed_sections':len(ledger),
'changed_de_fa_en_final_sentences':25,'unchanged_units':54,'unchanged_prior_de_fa_en_first_two_sentences':True,
'fulltext_occurrences_before':4298,'old_context_invalidations':retired,'fulltext_occurrences_after':len(allocc),
'curated_relative_clause_samples_retargeted':curated_retarget,'new_grammar_extractions':0,
'remaining_exact_generic_p02_s03':remaining['p02'],'remaining_exact_generic_p03_s03':remaining['p03'],
'original_native_nine_lens_engine_rerun':False,'full_semantic_stage4':'HOLD','browser_stage6':'NOT_RUN','release_stage7':'NOT_RELEASED',
'preservation_scope':'54 exact unchanged lesson objects; in 14 edited lessons only concluding sentence translations, invalidated grammar, retained curated-relative examples, word counts, hashes and quality status changed',
'before_after':ledger}
write(LED,record)
print(json.dumps({k:v for k,v in record.items() if k!='before_after'},ensure_ascii=False,indent=2))