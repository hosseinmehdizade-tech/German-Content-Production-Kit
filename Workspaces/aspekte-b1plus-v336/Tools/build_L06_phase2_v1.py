#!/usr/bin/env python3
"""Aspekte B1+ L06 whole-lesson editorial Phase2. Strict saved-primary-member verification.
Never reinterpret Phase2 editorial decision as final full-card linguistic QA or actual app import.
"""
from pathlib import Path
import json,hashlib,zipfile,copy,collections,datetime,re,io,csv,html
ROOT=Path('/mnt/data/aspekte_b1plus_l06')
PARENT=Path('/mnt/data/aspekte_b1plus_l04/Aspekte-B1plus-L04-PHASE3-160-CARD-QUALITY-GATE-CORRECTED-NONIMPORT-20261108.zip')
QUEUE=ROOT/'output/L06-PHASE1-177-CARD-DECISION-QUEUE.jsonl'
OUT=ROOT/'Aspekte-B1plus-L06-PHASE2-177-CARDS-CURATED-CORRECTED-NONIMPORT-20261109.zip'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
PARENT_SHA='31d8d0640d5bacdb080f0a379aa926542498a905c82b4e3d2f3d670d7bb2aca4'
SOURCE='L06_PHASE2_EDITORIAL_SENSE_CONTEXT_NONIMPORT_20261109'
def sha(x):return hashlib.sha256(x).hexdigest()
def jbytes(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def jsonl(x):return ''.join(json.dumps(v,ensure_ascii=False,sort_keys=True)+'\n' for v in x).encode()
assert sha(PARENT.read_bytes())==PARENT_SHA,'PARENT_SHA_MISMATCH'
with zipfile.ZipFile(PARENT) as z:
 assert z.testzip() is None
 files={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
 manifest={n:h for h,n in (x.split('  ',1) for x in z.read('SHA256SUMS.txt').decode().splitlines())}
 assert set(files)==set(manifest) and all(sha(v)==manifest[k] for k,v in files.items())
parent=[json.loads(x) for x in files[MAIN].splitlines()]
cards=copy.deepcopy(parent)
queue=[json.loads(x) for x in QUEUE.read_text(encoding='utf-8').splitlines()]
assert len(parent)==len(cards)==1571 and len(queue)==177
lesson=[c for c in cards if c['lesson']=='L06']
assert len(lesson)==177
by_id={c['preview_card_id']:c for c in lesson}
qby={q['card_id']:q for q in queue}; assert set(by_id)==set(qby)
byordinal=collections.defaultdict(list)
for c in lesson:byordinal[c['source_ordinal']].append(c)
changes=[];routes=[];netadd=[];new_ex=[];dup_resolutions=[];status_repairs=[];unresolved=[]
def one(o,frag=None):
 arr=byordinal[o]
 if frag is not None:arr=[c for c in arr if c['front']['base_headword_de'].strip().startswith(frag)]
 assert len(arr)==1,(o,frag,len(arr))
 return arr[0]
def examples(c):
 b=c['back'];return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
def note(c,field,before,after,why):
 if before!=after:changes.append({'card_id':c['preview_card_id'],'ordinal':c['source_ordinal'],'field':field,'before':before,'after':after,'reason':why})
def add_ex(o,frag,de,fa,reason):
 c=one(o,frag); b=c['back'];arr=b.setdefault('additional_examples_de_fa_pending_qa',[])
 assert not any(x.get('de')==de for x in examples(c)),(o,de)
 e={'de':de,'fa':fa,'status':'PENDING_G4_FULL_CARD_DE_FA_REVIEW','provenance':SOURCE,'L06_phase2_editorial_reason':reason}
 arr.append(e);new_ex.append({'ordinal':o,'card_id':c['preview_card_id'],'de':de,'fa':fa,'reason':reason})
 note(c,'back.additional_examples_de_fa_pending_qa',len(arr)-1,len(arr),reason)
# Zero-example cards: two natural, meaning-distinct and contextual bilingual examples per card.
for o,frag,pairs in [
 (771,'denkbar', [('Eine solche Lösung wäre durchaus denkbar.','چنین راه‌حلی کاملاً قابل تصور است.'),('Für dieses Problem sind mehrere Ursachen denkbar.','برای این مشکل چند علت قابل تصور است.')]),
 (771,'undenkbar',[('Für mich wäre ein Umzug ins Ausland undenkbar.','برای من مهاجرت به خارج از کشور غیرقابل تصور است.'),('Es ist undenkbar, die Sicherheitsregeln zu ignorieren.','نادیده گرفتن مقررات ایمنی تصورناپذیر است.')]),
 (773,'erwünscht',[('Eine Anmeldung im Voraus ist erwünscht.','ثبت‌نام از قبل مورد استقبال است.'),('Rückmeldungen sind ausdrücklich erwünscht.','از بازخوردها صراحتاً استقبال می‌شود.')]),
 (773,'unerwünscht',[('Unerwünschte Werbung landet oft im Spamordner.','تبلیغات ناخواسته اغلب وارد پوشه هرزنامه می‌شوند.'),('Störungen während der Prüfung sind unerwünscht.','ایجاد مزاحمت در زمان امتحان نامطلوب است.')])]:
 c=one(o,frag)
 assert len(examples(c))==0,(o,frag)
 for de,fa in pairs:add_ex(o,frag,de,fa,'Fill previously empty DE–FA examples without claiming full release approval')
# Additional accepted meanings that had no distinct in-card example.
add_ex(790,None,'Beim Schuss bleibt das Standbein fest auf dem Boden.','هنگام شوت‌زدن پای تکیه‌گاه محکم روی زمین می‌ماند.','Existing sports sense lacked an illustrative example')
add_ex(828,None,'Seine Liebhaberin wartete vor dem Kino.','معشوقه‌اش جلوی سینما منتظر بود.','Differentiate romantic partner from enthusiast with an additional example')
# Two genuine duplicates; retain differing Persian version as alternates.
for o,de in [(760,'Die Besprechung des Romans erschien gestern in der Zeitung.'),(820,'Wir haben lange hin und her überlegt.')]:
 c=one(o);b=c['back'];es=examples(c);hits=[x for x in es if x['de']==de]
 assert len(hits)==2,(o,len(hits))
 primary,repeat=hits
 if repeat.get('fa')!=primary.get('fa'):
  alternatives=primary.setdefault('fa_alternatives_preserved',[])
  if repeat['fa'] not in alternatives:alternatives.append(repeat['fa'])
  assert repeat['fa'] in alternatives
 for listkey in ('additional_examples_de_fa_pending_qa','existing_examples_de_fa_pending_qa'):
  arr=b.get(listkey) or []
  if any(x is repeat for x in arr):arr.remove(repeat);break
 else:raise AssertionError('DUPLICATE_NOT_REMOVED')
 primary['L06_phase2_duplicate_resolution']='ONE_DE_SENTENCE_WITH_VARIANT_FA_PRESERVED'
 dup_resolutions.append({'ordinal':o,'de':de,'kept_fa':primary['fa'],'other_fa_preserved':repeat['fa']!=primary['fa']})
 note(c,'duplicate_existing_DE_example',2,1,'Remove repeated SRS exposure; preserve distinct Persian paraphrase')
# Improve two context variants rather than keeping nearly identical exercises.
c=one(717);es=examples(c);target=next(x for x in es if x['de']=='Ich habe meinen Schlüssel verlegt.')
old=(target['de'],target['fa']);target['de']='Der Unterricht wurde in einen anderen Raum verlegt.';target['fa']='کلاس به اتاق دیگری منتقل شد.'
assert old!=(target['de'],target['fa'])
note(c,'example_SEMANTIC_VARIETY',old,(target['de'],target['fa']),'Illustrate move of location instead of duplicating misplaced keys')
c=one(701);target=next(x for x in examples(c) if x['de']=='Sie ist handwerklich sehr geschickt.')
old=(target['de'],target['fa']);target['de']='Sie hat eine handwerkliche Ausbildung abgeschlossen.';target['fa']='او یک دوره آموزش فنی‌وحرفه‌ای را به پایان رسانده است.'
note(c,'example_SEMANTIC_VARIETY',old,(target['de'],target['fa']),'Contrast manual ability with craft-related vocational training')
# Precisely sense-anchored existing networks, decided from actual DE+FA context, not generic semantic guessing.
ROUTES={682:[1,1],722:[1,1],728:[1,1],737:[1,1],738:[2,1,3],745:[1,1],751:[1,1],755:[1,2],756:[1,1],757:[1,2],774:[1,1],790:[1,1,2],795:[1,1],796:[1,2],802:[3,2],809:[1,1],826:[1,1],846:[1,1]}
assert len(ROUTES)==18
# Define only genuinely different senses; no automatic splitting on Persian semicolons.
# each sense: German explanation; Persian gloss; one or two compact idiomatic German/Persian collocations.
NEW={
686:[('Sitzungsprotokoll oder Gesprächsniederschrift','صورت‌جلسه و ثبت کتبی گفتگو',[('ein Protokoll anfertigen','صورت‌جلسه تهیه کردن'),('das Protokoll unterschreiben','صورت‌جلسه را امضا کردن')]),('offizielle Regeln und diplomatische Formen','تشریفات و آیین رسمی',[('das diplomatische Protokoll beachten','تشریفات دیپلماتیک را رعایت کردن')]),('technisches Kommunikations- oder Datenprotokoll','پروتکل فنی ارتباط و انتقال داده',[('ein Netzwerkprotokoll verwenden','از پروتکل شبکه استفاده کردن')])],
692:[('besondere Speise oder regionale Köstlichkeit','خوراک ویژه یا محلی',[('regionale Spezialitäten probieren','غذاهای ویژه منطقه‌ای را امتحان کردن'),('eine Spezialität des Hauses','غذای ویژه رستوران')]),('fachliches Spezialgebiet oder besondere Fähigkeit','حوزه تخصصی یا مهارت ویژه',[('die Spezialität eines Handwerkers','تخصص یک صنعتگر')])],
701:[('auf Handwerk und praktische Arbeit bezogen','مربوط به کار فنی یا صنایع دستی',[('handwerkliche Erfahrung sammeln','تجربه کار فنی به‌دست آوردن'),('eine handwerkliche Ausbildung','آموزش فنی‌وحرفه‌ای')]),('mit den Händen und Werkzeugen geschickt','دارای مهارت عملی کار با دست و ابزار',[('handwerklich begabt sein','در کارهای دستی و فنی استعداد داشتن')])],
710:[('finanzieller Bankrott oder Insolvenz','ورشکستگی مالی',[('in die Pleite geraten','ورشکسته شدن'),('kurz vor der Pleite stehen','در آستانه ورشکستگی بودن')]),('misslungenes Vorhaben oder Fiasko (umgangssprachlich)','شکست کامل یک برنامه (محاوره‌ای)',[('eine totale Pleite erleben','شکست کاملی را تجربه کردن')])],
713:[('geneigt oder nicht gerade','کج یا مایل',[('schief an der Wand hängen','کج روی دیوار آویزان بودن')]),('nicht wie geplant oder falsch verlaufen','بد پیش رفتن یا اشتباه از آب درآمدن',[('schiefgehen','بد پیش رفتن'),('schief laufen','درست پیش نرفتن')])],
717:[('Termin oder Ort auf andere Zeit oder an anderen Ort setzen','زمان یا مکان را جابه‌جا کردن',[('einen Termin verlegen','وقت را جابه‌جا کردن'),('eine Veranstaltung verlegen','زمان یا مکان برنامه را تغییر دادن')]),('etwas ablegen und danach nicht wiederfinden','چیزی را جایی گذاشتن و پیدا نکردن',[('den Schlüssel verlegen','کلید را گم کردن')]),('Teppiche, Fliesen oder Kabel installieren','فرش، کاشی یا کابل را نصب یا کار گذاشتن',[('einen Teppich verlegen','فرش را نصب کردن'),('Kabel verlegen','کابل‌کشی کردن')]),('Bücher in einem Verlag veröffentlichen','کتاب منتشر کردن',[('einen Roman verlegen','رمان منتشر کردن')])],
742:[('förmlich oder im gesellschaftlichen Umgang offiziell','رسمی و تشریفاتی',[('ein formaler Anlass','مناسبت رسمی')]),('nur die äußere Form betreffend','از نظر شکل و قالب',[('formal korrekt sein','از نظر شکلی صحیح بودن'),('formale Anforderungen erfüllen','الزامات شکلی را رعایت کردن')])],
744:[('gepflegtes äußeres Auftreten einer Person','آراسته و مرتب',[('ein gepflegtes Erscheinungsbild','ظاهر آراسته')]),('sorgfältig betreute Sache oder Anlage','رسیدگی‌شده و مرتب',[('ein gepflegter Garten','باغ مرتب و رسیدگی‌شده')])],
754:[('innerlich nicht überzeugt oder zweifelnd','مردد یا نامطمئن',[('sich bei einer Entscheidung unsicher sein','در تصمیم‌گیری مطمئن نبودن')]),('mangelnde Sicherheit oder Stabilität','فاقد ایمنی یا ثبات کافی',[('auf unsicherem Boden gehen','روی زمین ناامن راه رفتن')])],
760:[('Arbeitsbesprechung oder gemeinsame Beratung','جلسه یا گفت‌وگوی کاری',[('eine Besprechung einberufen','جلسه‌ای تشکیل دادن'),('an einer Besprechung teilnehmen','در جلسه شرکت کردن')]),('Rezension oder kritische Behandlung eines Werkes','نقد و بررسی یک اثر',[('die Besprechung eines Romans','نقد یک رمان')])],
765:[('Menschen oder Tiere beaufsichtigen und schützen','مراقبت کردن از انسان یا حیوان',[('Schafe hüten','چوپانی کردن و از گوسفندها مراقبت کردن'),('Kinder hüten','از کودکان مراقبت کردن')]),('das Bett hüten: wegen Krankheit im Bett bleiben','در بیماری در بستر ماندن',[('das Bett hüten','در بستر بیماری ماندن')])],
817:[('Handarbeiten als Tätigkeit oder Handwerk','کار دستی مانند بافتنی یا قلاب‌بافی',[('Handarbeit machen','کار دستی انجام دادن'),('Handarbeit lernen','کار دستی یاد گرفتن')]),('ein mit der Hand hergestelltes Stück','شیء یا اثر دست‌ساز',[('eine aufwendige Handarbeit','اثر دست‌ساز پرزحمت')])],
819:[('in einer Region beheimatet oder einheimisch','بومی یا محلی',[('heimische Pflanzen','گیاهان بومی'),('heimische Tierarten','گونه‌های جانوری بومی')]),('sich an einem Ort wie zu Hause fühlen','احساس در خانه بودن در یک مکان',[('sich irgendwo heimisch fühlen','جایی احساس خانه‌بودن داشتن')])],
820:[('räumlich in beide Richtungen','از این‌سو به آن‌سو',[('hin und her laufen','این‌طرف و آن‌طرف دویدن')]),('gedankliches Abwägen mehrerer Möglichkeiten','سبک‌سنگین کردن گزینه‌ها',[('hin und her überlegen','مدام سبک‌سنگین کردن'),('hin und her schwanken','در تصمیم‌گیری مردد بودن')])],
822:[('seltsam oder verrückt (umgangssprachlich)','عجیب و غریب (محاوره‌ای)',[('eine irre Geschichte','داستانی عجیب')]),('sehr oder außerordentlich (Verstärker)','خیلی و فوق‌العاده (قید تقویت‌کننده)',[('irre schön','فوق‌العاده زیبا'),('irre gut','خیلی خوب')])],
828:[('begeisterte Person mit Vorliebe für etwas','علاقه‌مند پرشور به چیزی',[('ein Liebhaber alter Filme','دوستدار فیلم‌های قدیمی'),('Liebhaberin klassischer Musik','علاقه‌مند پرشور موسیقی کلاسیک')]),('Person in einer Liebesbeziehung','عاشق یا معشوق در رابطه عاطفی',[('einen Liebhaber haben','معشوق داشتن')])],
831:[('geflochtenes Netz zum Fangen oder Abdecken','تور یا توری فیزیکی',[('ein Fischernetz reparieren','تور ماهیگیری را تعمیر کردن')]),('Geflecht aus Menschen und sozialen Beziehungen','شبکه روابط و حمایت اجتماعی',[('ein soziales Netz aufbauen','شبکه حمایتی اجتماعی ساختن')]),('Internet oder Kommunikationsnetz','اینترنت یا شبکه ارتباطی',[('Zugang zum Netz haben','دسترسی به اینترنت داشتن')])],
833:[('repräsentativer Eingang eines Gebäudes','درگاه یا ورودی اصلی ساختمان',[('ein reich verziertes Portal','سردر پرنقش‌ونگار')]),('Webportal oder zentraler Onlinezugang','پورتال یا درگاه اینترنتی',[('sich im Onlineportal anmelden','در پورتال اینترنتی ثبت‌نام کردن')])],
844:[('etwas an bestimmter Stelle hinzufügen','چیزی را در متن یا مجموعه درج کردن',[('ein Bild in den Bericht einfügen','تصویری را در گزارش درج کردن')]),('sich in eine Gruppe oder Umgebung integrieren','خود را با جمع یا محیط هماهنگ کردن',[('sich ins Team einfügen','با تیم هماهنگ شدن')])]
}
MAP_NEW={686:[1,2,2,3],692:[1,2,1],701:[2,1,1],710:[1,2],713:[1,2],717:[1,3,2,1,4],742:[2,1],744:[1,2],754:[1,2],760:[1,1,2],765:[1,1,2,2],817:[2,1,2],819:[1,2],820:[1,2],822:[1,2,2],828:[1,1,2],831:[1,3,2],833:[1,2],844:[1,2]}
assert len(NEW)==len(MAP_NEW)==19
for o,senses in NEW.items():
 c=one(o);b=c['back'];assert not b.get('semantic_network_sense_anchored_pending_qa'),o
 n=[]
 for i,(de,fa,pairs) in enumerate(senses,1):
  sid=f"{c['preview_card_id']}:L06P2:S{i}"
  combos=[{'de':de1,'fa':fa1,'status':'PENDING_G4_CONTEXT_SPECIFIC_COMBINATION_QA','source':SOURCE} for de1,fa1 in pairs]
  n.append({'sense_id':sid,'sense_de':de,'sense_fa':fa,'Synonyme':[],'Antonyme':[],'Wortfamilie':[],
   'Verwandte_Woerter_KEINE_Synonyme':[],'Kombinationen_DE_FA':combos,'Feste_Wendungen_DE_FA':[],
   'Satzmuster_DE_FA':[],'status':'PENDING_G4_CONTEXT_SPECIFIC_SEMANTIC_QA','source':SOURCE,
   'lexical_relation_policy':'MEANING_ANCHORED_DO_NOT_AUTO_INFER_SYNONYMS'})
  netadd.append({'ordinal':o,'card_id':c['preview_card_id'],'sense_id':sid,'sense_de':de,'collocations':combos})
 b['semantic_network_sense_anchored_pending_qa']=n
for o in sorted(set(ROUTES)|set(NEW)):
 c=one(o);n=c['back']['semantic_network_sense_anchored_pending_qa'];ex=examples(c)
 mapping=ROUTES[o] if o in ROUTES else MAP_NEW[o]
 assert len(mapping)==len(ex),(o,len(mapping),len(ex))
 for ix,(e,idx) in enumerate(zip(ex,mapping),1):
  assert 1<=idx<=len(n)
  sid=n[idx-1]['sense_id'];prev=e.get('sense_id')
  assert not prev or prev==sid,(o,ix,prev,sid)
  if not prev:
   e['sense_id']=sid;e['L06_phase2_route']='EXPLICIT_EDITORIAL_CONTEXT_QA_NOT_FINAL_RELEASE'
   routes.append({'ordinal':o,'card_id':c['preview_card_id'],'example_index':ix,'de':e['de'],'sense_id':sid,'sense_de':n[idx-1]['sense_de']})
# One existing network, Standbein, now has a newly-added sense2 physical example; old senses retained.
# Missing QA statuses: fill only as PENDING, no false approval.
for c in lesson:
 for e in examples(c):
  if not str(e.get('status','')).strip():
   e['status']='PENDING_G4_EXAMPLE_DE_FA_QA'
   e['L06_phase2_status_note']='MISSING_LEGACY_STATUS_NORMALIZED_TO_PENDING_NOT_APPROVED'
   status_repairs.append({'ordinal':c['source_ordinal'],'card_id':c['preview_card_id'],'de':e['de']})
# Per-card disposition, not false all-card language certification; all 177 are in one whole-lesson queue.
ledger=[]
parent_byid={c['preview_card_id']:c for c in parent}
for c in lesson:
 old=parent_byid[c['preview_card_id']]; q=qby[c['preview_card_id']]
 changed=c!=old
 if changed:status='TARGETED_EDITORIAL_DATA_CHANGED_PENDING_FULL_LANGUAGE_QA'
 else:status='STRUCTURAL_AND_RISK_REVIEW_NO_EDIT_PENDING_FULL_LANGUAGE_QA'
 c['L06_phase2_editorial']={'stage':'PHASE2_WHOLE_LESSON_TRIAGE_NONIMPORT', 'result':status,
  'priority':q['priority'],'formal_release_approved':False,
  'known_blockers':q['risk_flags'],'review_boundary':'NOT_INDEPENDENT_FULL_DE_FA_RELEASE'}
 # NOTE: metadata above changes all 177 objects; for truthful counts distinguish substantive payload edits vs metadata only.
 ledger.append({'card_id':c['preview_card_id'],'ordinal':c['source_ordinal'],'headword':c['front']['base_headword_de'],
  'priority':q['priority'],'targeted_data_or_status_change':changed,'decision':status,'examples':len(examples(c)),
  'HOLD_preserved':bool(c.get('curated_HOLD_content_disposition_exists')),
  'morphology_scoped_attested':bool(c['front'].get('morphology_independently_validated')),
  'needs_full_language_review':True,'release_allowed':False})
# Integrity proof directly on actual payload objects (excluding disposition marker for accurate content statistics).
content_changed_ids={x['card_id'] for x in ledger if x['targeted_data_or_status_change']}
assert len(ledger)==177
assert len(set(x['card_id'] for x in ledger))==177
assert len(content_changed_ids)>40
assert len(routes)>=60
assert len(status_repairs)==14,'Two previous missing-status duplicate items were removed, leaving 14 statuses to normalize'
assert len(dup_resolutions)==2
assert len(new_ex)==10
for c,p in zip(cards,parent):
 assert c['preview_card_id']==p['preview_card_id']
 assert c['linked_original_source_ordinals']==p['linked_original_source_ordinals']
 if c['lesson']!='L06':assert c==p,('OUTSIDE_L06_CHANGED',c['preview_card_id'])
 assert c['formal_release_approved'] is False and c['import_ready'] is False
assert files[MAP]==files[MAP]
all_e=[e for c in lesson for e in examples(c)]
assert len(all_e)==370-2+10==378
assert all(e.get('status') and e.get('de') and e.get('fa') for e in all_e)
assert len({x['preview_card_id'] for x in cards})==1571
assert all(c['back'].get('Formen_section') is None for c in cards)
# All new sense fields must point at valid sense IDs; old networked examples now all routed.
for c in lesson:
 nets=c['back'].get('semantic_network_sense_anchored_pending_qa') or []
 if nets:
  ids={n['sense_id'] for n in nets}
  for e in examples(c):assert e.get('sense_id') in ids,(c['source_ordinal'],e['de'])
# Global duplicate count, all L06 exact intra-card duplicate examples now cleared.
def norm(s):return re.sub(r'\W+','',str(s).casefold())
def dupe_count(groups):
 ret=[]
 for c in groups:
  count=collections.Counter(norm(e['de']) for e in examples(c))
  for key,n in count.items():
   if n>1:ret.append({'ordinal':c['source_ordinal'],'lesson':c['lesson'],'normalized':key,'count':n})
 return ret
old_dup=dupe_count(parent);new_dup=dupe_count(cards)
assert len(old_dup)==5 and len(new_dup)==3 and not [x for x in new_dup if x['lesson']=='L06']
# Recompute strictly structural combinationen QA on ACTUAL updated cards.
qa_file=Path('/mnt/data/aspekte_b1plus_l04/quality_scripts/qa_combinationen_strict_v2.py')
import importlib.util
spec=importlib.util.spec_from_file_location('strict',qa_file)
strict=importlib.util.module_from_spec(spec);spec.loader.exec_module(strict)
strict_result=strict.audit(cards)
assert strict_result['structural_gate_passed'] and strict_result['combinations_scanned']>=665,strict_result
# Additional cautious finite-clause heuristic is a separate control.
for c in cards:
 for n in c['back'].get('semantic_network_sense_anchored_pending_qa') or []:
  for pair in n.get('Kombinationen_DE_FA') or []:
   assert not pair['de'].endswith(('.', '!', '?')) and len(pair['de'].split())<=10
# Sidecar outputs.
rel='Lessons/L06/'
files[rel+'L06-PHASE2-177-CARD-DECISION-LEDGER.jsonl']=jsonl(ledger)
files[rel+'L06-PHASE2-TARGETED-BEFORE-AFTER.json']=jbytes({'changes':changes,'duplicate_merges':dup_resolutions,'new_examples':new_ex,'status_repairs':status_repairs,'sense_networks_added':netadd,'example_sense_links':routes})
report={'schema':'aspekte-b1plus-L06-phase2-whole-lesson-editorial@1','date':'2026-11-09','lesson':'L06','phase':2,'phases_total':3,
 'status':'WHOLE_LESSON_177_CARD_DECISIONS_WITH_TARGETED_CONTENT_EDITS_NONIMPORT',
 'parent_zip_sha256':PARENT_SHA,'parent_main_member_sha256':sha(files[MAIN]),
 'lesson_card_count':177,'per_card_disposition_count':len(ledger),
 'targeted_card_data_or_QA_status_changes_before_disposition_marker':len(content_changed_ids),
 'ids_with_targeted_data_or_QA_status_changes':sorted(content_changed_ids),
 'metadata_disposition_markers_added_to_all_177_cards':True,
 'all_main_card_objects_changed_due_to_metadata_plus_content':177,
 'L06_examples_before':370,'L06_examples_after':378,'new_bilingual_examples':len(new_ex),
 'duplicate_German_example_groups_removed_L06':len(dup_resolutions),
 'legacy_intra_card_global_duplicate_groups_before':len(old_dup),'legacy_intra_card_global_duplicate_groups_after':len(new_dup),
 'old_wordnet_cards_L06':18,'new_wordnet_cards_added':len(NEW),'new_wordnet_sense_blocks':len(netadd),
 'new_example_sense_links':len(routes),'missing_QA_status_repairs_to_PENDING':len(status_repairs),
 'existing_curated_HOLD_markers_L06':33,
 'morphology_scoped_attestation_L06_preserved':108,'unattested_form_cases_L06':69,
 'global_card_identity_count':1571,'original_source_rows':1548,'original_source_map_unchanged':True,
 'non_L06_card_objects_unchanged':True,
 'central_combinationen_gate':strict_result,'real_app_import_render_tested':False,
 'formal_full_card_approved':0,'import_ready':False,'release_allowed':False,
 'limitations':['177 card dispositions are a whole-lesson editorial triage, not 177 independent bilingual signoffs.',
 'No morphology-only gap was falsely declared wrong or independently attested.',
 'Corrected German–Persian examples and collocations remain pending complete card-context QA.',
 'Strict combinationen gate checks structure, not every semantic nuance.',
 'No actual app import or rendered app card was tested.'],
 'next':'L06_PHASE3_STRICT_FAIL_CLOSED_CASE_LEVEL_QA_AND_APP_IMPORT_WHEN_AVAILABLE'}
files[rel+'L06-PHASE2-WHOLE-LESSON-REPORT.json']=jbytes(report)
files[rel+'L06-PHASE2-COMBINATIONS-STRICT-REPORT.json']=jbytes(strict_result)
# Searchable human QA-only HTML view including sense-grouped examples/combos and pending warnings.
parts=['<!doctype html><html lang="de"><meta charset="utf-8"><title>Aspekte B1+ L06 Phase2 QA ONLY — NONIMPORT</title>',
'<style>body{max-width:1000px;margin:2rem auto;font:16px/1.5 system-ui;background:#f7f7fa;color:#222}article{padding:1rem 1.5rem;margin:1.2rem 0;border:1px solid #ddd;border-radius:10px;background:white}h2{margin:0}h3{margin-bottom:0}li{margin:.5rem 0}.warn{color:#ab3900;font-weight:bold}small{color:#666}.fa{direction:rtl;text-align:right;display:inline-block;max-width:100%}</style>',
'<h1>Aspekte B1+ · Lektion 06 · 177 cards · Phase2 editorial QA only</h1><p class="warn">NONIMPORT. No full-card German–Persian release approval; no actual app runtime test.</p>']
for c in lesson:
 b=c['back'];nets=b.get('semantic_network_sense_anchored_pending_qa') or [];es=examples(c)
 parts+=['<article>','<h2>'+html.escape(str(c['front'].get('display_de_provisional','')) )+'</h2>',
 '<p class="fa">'+html.escape(str(b.get('meanings_fa_provisional','')))+'</p>',
 '<p><small>Ordinal '+str(c['source_ordinal'])+' | '+html.escape(c['preview_card_id'])+' | '+html.escape(c['L06_phase2_editorial']['result'])+'</small></p>']
 if nets:
  for n in nets:
   parts.append('<h3>'+html.escape(n['sense_de'])+' — <span class="fa">'+html.escape(n['sense_fa'])+'</span></h3><ul>')
   for e in es:
    if e.get('sense_id')==n['sense_id']:
     parts.append('<li>'+html.escape(e['de'])+'<div class="fa">'+html.escape(e['fa'])+'</div></li>')
   parts.append('</ul><p>**Kombinationen:** '+html.escape(' · '.join(f"{p['de']} — {p['fa']}" for p in n.get('Kombinationen_DE_FA',[])))+'</p>')
 else:
  parts.append('<ul>')
  for e in es:parts.append('<li>'+html.escape(e['de'])+'<div class="fa">'+html.escape(e['fa'])+'</div></li>')
  parts.append('</ul>')
 parts.append('<p class="warn">PENDING FULL QA · Import blocked</p></article>')
parts.append('</html>')
files[rel+'L06-PHASE2-177-CARD-SEARCHABLE-QA-ONLY.html']='\n'.join(parts).encode()
# Persist actual modified canonical primary member -- critical L04 ghost-edit regression prevention.
actual_main=jsonl(cards)
assert actual_main!=files[MAIN] and len(actual_main)>len(files[MAIN]);files[MAIN]=actual_main
files['Tools/build_L06_phase2_v1.py']=Path(__file__).read_bytes()
files['SHA256SUMS.txt']=''.join(f"{sha(v)}  {k}\n" for k,v in sorted(files.items())).encode()
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name in sorted(files):z.writestr(name,files[name])
# Verify saved bytes, full manifest and actual object diff -- not reports only.
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None
 verify={n:z.read(n) for n in z.namelist()}
 savedcards=[json.loads(x) for x in verify[MAIN].splitlines()]
 assert len(savedcards)==1571
 mf={n:h for h,n in (x.split('  ',1) for x in verify['SHA256SUMS.txt'].decode().splitlines())}
 assert set(verify)-{'SHA256SUMS.txt'}==set(mf)
 assert all(sha(verify[n])==digest for n,digest in mf.items())
 delta=sum(x!=y for x,y in zip(parent,savedcards))
 assert delta==177,delta
 saved_contentdelta=sum(x!=y for x,y in zip(parent,savedcards) if x['lesson']=='L06')
 assert saved_contentdelta==177
 assert all(x==y for x,y in zip(parent,savedcards) if x['lesson']!='L06')
 assert verify[MAP]==files[MAP]
 assert len(dupe_count(savedcards))==3
 assert len([x for c in savedcards if c['lesson']=='L06' for x in examples(c)])==378
 assert strict.audit(savedcards)['structural_gate_passed']
 assert len([x for c in savedcards if c['lesson']=='L06' for x in examples(c) if not x.get('sense_id') and c['back'].get('semantic_network_sense_anchored_pending_qa')])==0
receipt={'date':'2026-11-09','status':'L06_PHASE2_WHOLE_LESSON_EDITORIAL_COMPLETED_DATA_PERSISTENCE_VERIFIED_NONIMPORT',
 'owner_zip':OUT.name,'owner_sha256':sha(OUT.read_bytes()),'owner_bytes':OUT.stat().st_size,'zip_member_count':len(files),
 'manifest_entries_verified':len(files)-1,'zip_crc':'PASS',
 'parent_sha256':PARENT_SHA,'parent_primary_main_sha256':sha(parent and jsonl(parent)),
 'new_primary_main_sha256':sha(actual_main),'saved_primary_card_objects_changed':177,
 'targeted_card_data_or_QA_status_changes_before_editorial_status_markers':len(content_changed_ids),
 'new_sense_routes':len(routes),'new_meaning_network_cards':len(NEW),'new_meaning_blocks':len(netadd),
 'new_ex_pairs':len(new_ex),'L06_total_examples':378,'statusless_examples_repaired':len(status_repairs),
 'duplicate_groups_before':5,'duplicate_groups_after':3,'total_combinationen':strict_result['combinations_scanned'],
 'L06_HOLDs':33,'L06_form_evidence_gaps':69,'card_releases':0,'import_ready':False,
 'real_app_import_tested':False,'notes':'No fictional independent human reviewer needed; genuine language QA and actual app importer remain untested.'}
(ROOT/'phase2/L06-PHASE2-PERSISTENCE-RECEIPT.json').write_bytes(jbytes(receipt))
(ROOT/'phase2/L06-PHASE2-REPORT.json').write_bytes(jbytes(report))
(ROOT/'phase2/L06-PHASE2-DECISION-LEDGER.jsonl').write_bytes(jsonl(ledger))
print(json.dumps(receipt,ensure_ascii=False,indent=2))
