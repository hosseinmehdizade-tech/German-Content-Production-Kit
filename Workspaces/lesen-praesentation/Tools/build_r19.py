#!/usr/bin/env python3
"""R19 scoped, source-grounded p06-s02 edits; no UI, user progress or CURRENT mutation."""
from pathlib import Path
import json, copy, hashlib, re, collections
ROOT=Path('/mnt/data/lesen_r19_20261108')
PARENT=Path('/mnt/data/lesen_r18_20261107')
SRC=PARENT/'Lesen-Production-Master-v1.3.0-R18-26CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
RUN=PARENT/'Lesen-R18-v505-26CONCLUSIONS-RUNTIME-PREENTRY-CANDIDATE.json'
OUT=ROOT/'Lesen-Production-Master-v1.3.0-R19-10P06-TRILINGUAL-CANDIDATE.json'
ROUT=ROOT/'Lesen-R19-v505-10P06-RUNTIME-PREENTRY-CANDIDATE.json'
LEDGER=ROOT/'LESEN-R19-10P06-EDITORIAL-GRAMMAR-LEDGER.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
write=lambda path,obj:path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old_de='Wichtig ist, dass die Entscheidung nachvollziehbar begründet wird und nicht allein auf Gewohnheit, Idealvorstellungen oder kurzfristigen Eindrücken beruht.'
# Full DE conclusion and exact target grammar feature (category / trigger span).
CHANGES={
11:{'de':'Damit auch Menschen mit wenig Geld studieren können, müssen Hochschulen solide finanziert werden, ohne dass der Zugang vom Einkommen abhängt.',
'fa_old':'مهم است که تصمیم نهایی با استدلالی قابل‌فهم توجیه شود و فقط بر عادت، تصورهای آرمانی یا برداشت‌های کوتاه‌مدت تکیه نکند.',
'fa':'برای اینکه افراد کم‌درآمد هم بتوانند تحصیل کنند، دانشگاه‌ها باید بودجهٔ پایداری داشته باشند، بی‌آنکه دسترسی به تحصیل به درآمد وابسته شود.',
'en_old':'What matters is that the decision is justified transparently and is not based only on habit, idealized assumptions, or short-term impressions.',
'en':'To ensure that people with little money can also study, universities need stable funding without access depending on income.',
'key':'subordinate_clauses_all','label':'Finalsatz mit damit','target':'Damit auch Menschen mit wenig Geld studieren können','rule':'damit leitet einen Finalsatz ein und bezeichnet das Ziel; das finite Verb steht am Ende.','fa_rule':'«damit» جملهٔ هدف را می‌سازد و فعل صرف‌شده در پایان جملهٔ وابسته می‌آید.'},
12:{'de':'Die Bewertung im Sport sollte sich stärker an persönlichen Fortschritten orientieren, damit auch weniger sportliche Kinder Erfolgserlebnisse haben.',
'fa_old':'مهم است که این تصمیم با استدلال روشن پشتیبانی شود، نه فقط با عادت یا تصویرهای ایده‌آل.',
'fa':'ارزیابی در ورزش بهتر است بیشتر بر پیشرفت فردی تکیه کند تا کودکانی که توانایی ورزشی کمتری دارند نیز تجربهٔ موفقیت داشته باشند.',
'en_old':'The decision should be supported by clear reasoning rather than habit or idealized assumptions.',
'en':'Assessment in physical education should focus more on individual progress so that less athletic children can also experience success.',
'key':'subordinate_clauses_all','label':'Finalsatz mit damit','target':'damit auch weniger sportliche Kinder Erfolgserlebnisse haben','rule':'damit markiert die beabsichtigte Folge einer Handlung; das finite Verb steht am Ende.','fa_rule':'«damit» هدفِ یک اقدام را بیان می‌کند و فعل صرف‌شده در پایان جملهٔ وابسته قرار می‌گیرد.'},
13:{'de':'Begegnungen fördern das Verständnis vor allem dann, wenn Reisende lokale Regeln respektieren und mit Menschen vor Ort ins Gespräch kommen.',
'fa_old':'مهم است که تصمیم‌گیری با استدلالی قابل‌فهم انجام شود و فقط بر عادت یا برداشت کوتاه‌مدت تکیه نکند.',
'fa':'دیدارها به‌ویژه زمانی به درک متقابل کمک می‌کنند که گردشگران به قواعد محلی احترام بگذارند و با مردم آنجا وارد گفت‌وگو شوند.',
'en_old':'The position should be justified transparently rather than based only on habit or short-term impressions.',
'en':'Encounters especially promote understanding when travelers respect local rules and engage in conversation with local people.',
'key':'subordinate_clauses_all','label':'Bedingungssatz mit wenn','target':'wenn Reisende lokale Regeln respektieren und mit Menschen vor Ort ins Gespräch kommen','rule':'wenn führt hier einen Bedingungssatz ein und beschreibt, unter welchen Umständen Begegnungen das Verständnis fördern.','fa_rule':'«wenn» در اینجا شرطِ شکل‌گیری درک متقابل را بیان می‌کند.'},
14:{'de':'Die Lektüre sollte deshalb zur Lerngruppe passen, damit Diskussionen über Sprache, Figuren und gesellschaftliche Fragen entstehen können.',
'fa_old':'مهم است که انتخاب‌ها با استدلال روشن توجیه شوند و فقط بر عادت یا تصویرهای آرمانی تکیه نکنند.',
'fa':'بنابراین متن ادبی باید متناسب با گروه یادگیرندگان انتخاب شود تا گفت‌وگو دربارهٔ زبان، شخصیت‌ها و مسائل اجتماعی ممکن شود.',
'en_old':'Choices should be justified transparently rather than based only on habit or idealized assumptions.',
'en':'Reading selections should therefore suit the learner group so that discussions about language, characters, and social issues can develop.',
'key':'subordinate_clauses_all','label':'Finalsatz mit damit','target':'damit Diskussionen über Sprache, Figuren und gesellschaftliche Fragen entstehen können','rule':'Der Finalsatz mit damit erläutert das pädagogische Ziel der passenden Textauswahl.','fa_rule':'جملهٔ وابسته با «damit» هدف آموزشیِ انتخاب متن مناسب را توضیح می‌دهد.'},
15:{'de':'Vor der Studienwahl sollte geprüft werden, ob Interessen, Studieninhalte und berufliche Aussichten zusammenpassen.',
'fa_old':'تصمیم باید با استدلالی قابل‌فهم توجیه شود، نه فقط بر اساس عادت، تصور ایده‌آل یا برداشت کوتاه‌مدت.',
'fa':'پیش از انتخاب رشته باید بررسی شود که آیا علایق فرد، محتوای رشته و چشم‌انداز شغلی با یکدیگر سازگارند یا نه.',
'en_old':'The decision should be justified transparently rather than based only on habit, idealized assumptions, or short-term impressions.',
'en':'Before choosing a degree program, one should check whether personal interests, course content, and career prospects fit together.',
'key':'subordinate_clauses_all','label':'Indirekter Fragesatz mit ob','target':'ob Interessen, Studieninhalte und berufliche Aussichten zusammenpassen','rule':'ob leitet eine indirekte Ja-Nein-Frage ein; das finite Verb steht am Ende.','fa_rule':'«ob» یک پرسش غیرمستقیم بله/خیر می‌سازد و فعل صرف‌شده به پایان جمله می‌رود.'},
16:{'de':'Weil Plattformen Aufmerksamkeit belohnen, brauchen Nutzerinnen und Nutzer klare Grenzen für ihre Onlinezeit und einen kritischen Blick auf geteilte Inhalte.',
'fa_old':'مهم است که موضع ما با استدلال روشن شکل بگیرد و فقط بر عادت یا برداشت‌های کوتاه‌مدت تکیه نکند.',
'fa':'چون پلتفرم‌ها جلب توجه را تشویق می‌کنند، کاربران به مرزهای روشنی برای زمان آنلاین خود و نگاه انتقادی به محتوای به‌اشتراک‌گذاشته‌شده نیاز دارند.',
'en_old':'Our position should be based on clear reasoning rather than habit or short-term impressions.',
'en':'Because platforms reward attention, users need clear limits on their time online and a critical approach to shared content.',
'key':'subordinate_clauses_all','label':'Kausalsatz mit weil','target':'Weil Plattformen Aufmerksamkeit belohnen','rule':'weil nennt den Grund; steht der Nebensatz voran, folgt das finite Verb direkt nach dem Komma im Hauptsatz.','fa_rule':'«weil» دلیل را بیان می‌کند؛ اگر جملهٔ وابسته اول بیاید، فعل صرف‌شدهٔ جملهٔ اصلی بلافاصله پس از ویرگول قرار می‌گیرد.'},
17:{'de':'Wenn Experimente offen gestaltet werden, können Kinder verschiedene Interessen entdecken, ohne vorschnell auf eine Begabung festgelegt zu werden.',
'fa_old':'تصمیم‌ها باید با استدلال روشن و نه صرفاً از روی مد یا تصور ایده‌آل گرفته شوند.',
'fa':'اگر آزمایش‌ها باز و انعطاف‌پذیر طراحی شوند، کودکان می‌توانند علایق گوناگون خود را کشف کنند، بی‌آنکه خیلی زود به یک استعداد مشخص محدود شوند.',
'en_old':'Decisions should be based on clear reasoning rather than fashion or idealized assumptions.',
'en':'When experiments are designed openly, children can discover different interests without being prematurely limited to a single aptitude.',
'key':'subordinate_clauses_all','label':'Konditionalsatz mit wenn','target':'Wenn Experimente offen gestaltet werden','rule':'wenn markiert eine Bedingung, unter der Kinder unterschiedliche Interessen entdecken können.','fa_rule':'«wenn» شرطی را بیان می‌کند که در آن کودکان فرصت کشف علایق مختلف را پیدا می‌کنند.'},
18:{'de':'Deshalb sollten sowohl Lob als auch Kritik ehrlich, konkret und auf die Entwicklung des Kindes ausgerichtet sein.',
'fa_old':'مهم این است که تحسین و نقد هر دو صادقانه، مشخص و با هدف کمک به رشد کودک باشند.',
'fa':None,
'en_old':'Both praise and criticism should be sincere, specific, and aimed at helping the child grow.',
'en':None,
'key':'konjunktiv_ii','label':'Konjunktiv II als Empfehlung','target':'sollten','rule':'sollten formuliert eine vorsichtige Empfehlung, wie Lob und Kritik gestaltet sein sollten.','fa_rule':'«sollten» در اینجا توصیه‌ای سنجیده دربارهٔ شیوهٔ تشویق و انتقاد بیان می‌کند.'},
19:{'de':'Um den Wert einer Erfindung einzuschätzen, muss man ihren langfristigen Nutzen ebenso wie mögliche Risiken und ungleichen Zugang berücksichtigen.',
'fa_old':'ارزیابی باید بر استدلال روشن و پیامدهای واقعی تکیه کند.',
'fa':'برای ارزیابی ارزش یک اختراع باید هم سود بلندمدت آن و هم خطرهای احتمالی و دسترسی نابرابر به آن را در نظر گرفت.',
'en_old':'Evaluation should be based on clear reasoning and real consequences.',
'en':'To assess the value of an invention, one must consider its long-term benefits as well as potential risks and unequal access.',
'key':'infinitive_with_zu','label':'Finale Infinitivgruppe mit um … zu','target':'Um den Wert einer Erfindung einzuschätzen','rule':'um … zu mit Infinitiv bezeichnet das Ziel der Handlung.','fa_rule':'ساختار «um … zu» هدفِ انجام عمل را بیان می‌کند.'},
20:{'de':'Die Wahl sollte sich deshalb an den tatsächlichen Bedürfnissen der Studierenden und an der Qualität des Studienangebots orientieren.',
'fa_old':'انتخاب باید بر نیاز واقعی فرد و کیفیت برنامه تکیه کند.',
'fa':None,
'en_old':'The choice should depend on real individual needs and the quality of the program.',
'en':None,
'key':'konjunktiv_ii','label':'Konjunktiv II als Empfehlung','target':'sollte','rule':'sollte formuliert eine Empfehlung und bewertet die Wahlkriterien zurückhaltend.','fa_rule':'«sollte» توصیه‌ای محتاطانه دربارهٔ معیارهای انتخاب بیان می‌کند.'}
}

def replace_tail(text,old,new):
 assert text.endswith(old),(text[-220:],old)
 return text[:-len(old)]+(new if new is not None else old)

master=json.loads(SRC.read_text(encoding='utf-8'))
runtime=json.loads(RUN.read_text(encoding='utf-8'))
assert sha(SRC.read_bytes())=='bfd469d4027f59d97cb25baabbefd79b0576f47f13acdc965f82850fc8a63c37'
assert sha(RUN.read_bytes())=='a4d9669ff3db155380a69c74dcad5006d307e68718abdf8fa8a24fe83c64fe9f'
ledger=[];total_old=0;total_new=0
for n, spec in CHANGES.items():
    item=master['items'][n-1];entry=runtime['entries'][n-1]
    assert item['id']==entry['source_item_id']==f'LES-PRES-{n:03d}'
    section=next(s for s in item['reading']['sections'] if s['id']=='p06')
    passage=next(p for p in entry['unit']['passages'] if p['r38']['source_section_id']=='p06')
    s1,s2=section['sentences'];assert s2['text']==old_de
    assert section['text']==s1['text']+' '+old_de
    prev=copy.deepcopy(section)
    kept=[g for g in item['grammar']['full_text_occurrences'] if not(g['section_id']=='p06' and g['sentence_id']=='p06-s02')]
    removed=[g for g in item['grammar']['full_text_occurrences'] if g['section_id']=='p06' and g['sentence_id']=='p06-s02']
    assert len(removed)==4,(n,len(removed))
    total_old+=len(removed)
    newtxt=spec['de'];assert newtxt.endswith('.'),(n,newtxt)
    s2['text']=newtxt;section['text']=s1['text']+' '+newtxt
    section['translations']['fa']=replace_tail(section['translations']['fa'],spec['fa_old'],spec['fa'])
    section['translations']['en']=replace_tail(section['translations']['en'],spec['en_old'],spec['en'])
    assert len(section['sentences'])==2
    newspan=spec['target'];start=section['text'].find(newspan,len(s1['text'])+1)
    assert start>=len(s1['text'])+1 and section['text'].count(newspan)==1,(n,newspan)
    occ={'id':f'ftg-r19-p06-s02-{n:03d}','grammar_key':spec['key'],'label_de':spec['label'],
         'section_id':'p06','sentence_id':'p06-s02','start':start,'end':start+len(newspan),
         'target_text':newspan,'explanation_de':spec['rule'],'explanation_fa':spec['fa_rule'],
         'details':{'origin':'R19 authored exact observed grammar, not native nine-lens extraction'},
         'confidence':'high','annotation_source':'R19_MANUAL_SCOPED_EDITORIAL','derivation_method':'exact_new_sentence_span'}
    item['grammar']['full_text_occurrences']=kept+[occ]
    item['grammar']['full_text_occurrences'].sort(key=lambda g:(g['section_id'],g['start'],g['end'],g['id']))
    summ=item['grammar']['full_text_lens_summary'];summ['occurrences']=len(item['grammar']['full_text_occurrences']);summ['counts']=dict(collections.Counter(g['grammar_key'] for g in item['grammar']['full_text_occurrences']))
    summ['scope_note_de']='R19: p06-s02 gesondert redaktionell erneuert; alte Marker der ersetzten Aussage entfernt und nur belegter Satzbau genau annotiert. Kein vollständiger Neun-Linsen-Lauf.'
    summ['scope_note_fa']='در R19 فقط جملهٔ دومِ بخش ششم و گرامر مربوط به همان جمله بازبینی شده است؛ استخراج کامل نه‌گانه انجام نشده است.'
    passage['text_de']=section['text'];passage['translations']=copy.deepcopy(section['translations'])
    entry['unit']['r38']['grammar']=copy.deepcopy(item['grammar'])
    # Archived declared source word counts remain intact; these were already approximate/inherited in R18.
    assert entry['unit']['r38']['word_count_de']==item['reading']['word_count_de']
    ids=[g['id'] for g in item['grammar']['full_text_occurrences']];assert len(ids)==len(set(ids))
    assert all(item['reading']['sections'][int(g['section_id'][1:])-1]['text'][g['start']:g['end']]==g['target_text'] for g in item['grammar']['full_text_occurrences'])
    total_new+=1
    ledger.append({'lesson':n,'source_item_id':item['id'],'title_de':item['title_de'],'section':'p06','sentence':'p06-s02',
        'before':{'de':prev['sentences'][1]['text'],'fa':prev['translations']['fa'],'en':prev['translations']['en']},
        'after':{'de':newtxt,'fa':section['translations']['fa'],'en':section['translations']['en']},
        'changed_translation_pair':spec['fa'] is not None,
        'retired_grammar':removed,'added_grammar':occ,'prior_p06_s01_identical':True,
        'editorial_rationale':'Replaces generic decision justification with a topic-specific implication grounded in the source position.'})
assert total_old==40 and total_new==10
master['content_version']='1.3.0-R19-CANDIDATE'
master['status']='R19_TEN_P06_TOPIC_SPECIFIC_CONCLUSIONS_SCOPED_CANDIDATE__STAGE4_6_7_HOLD'
master['qa_summary']['r19_scope']='TEN_P06_S02_LESSONS_011_TO_020__S01_PRESERVED__8_FA_EN_PAIRS_REVISED_2_PRESERVED__NOT_FULL_SEMANTIC_STAGE4'
master['translation_qa']['r19_review_status']='TEN_SCOPED_SOURCE_BOUND_P06_S02_TRANSLATIONS__NOT_INDEPENDENT_WHOLEPACK_STAGE4'
q=master['full_text_grammar_qa']; allg=[g for it in master['items'] for g in it['grammar']['full_text_occurrences']]
q['occurrences']=len(allg);q['offset_exact_matches']=len(allg);q['counts']=dict(collections.Counter(g['grammar_key'] for g in allg));q['result']='R19_SCOPED_P06_CONCLUSIONS_10_UNITS_EXACT_OFFSETS__NOT_FULL_NATIVE'
q['r19_scope']={'changed_p06_sections':10,'retired_old_generic_p06_s02_spans':40,'new_scoped_real_grammar':10,'fulltext_grammar_before':4041,'fulltext_grammar_after':len(allg),'native_full_nine_lens_rerun':False,'independent_stage4':'HOLD'}
write(OUT,master)
for i in range(68):
    if i+1 in CHANGES:continue
    assert master['items'][i]==json.loads(SRC.read_text(encoding='utf-8'))['items'][i]
# Runtime retains exactly the previous entries outside target scope; only content-version and documented compiler metadata change.
runtime['compiled_from']['sha256']=sha(OUT.read_bytes());runtime['compiled_from']['content_version']=master['content_version']
runtime['counts']['full_text_grammar']=len(allg)
runtime['compiler']={'id':'lesen-r19-source-grounded-ten-p06-v505-delta-v1','deterministic':True,'runtime_analysis_required':False,
 'contract':'R18 byte-pinned runtime with ten p06-s02 authored source-mapped updates; 58 untouched entries; semantic Stage4 and browser Stage6 remain HOLD.',
 'note':'Does not represent full grammar extraction, actual browser IndexedDB import, or final release.'}
runtime['candidate_review']={'status':'R19_TEN_P06_CONCLUSIONS_SCOPED_QA_PENDING__STAGE4_6_7_HOLD','changed_unit_ids':[f'LES-PRES-{n:03d}' for n in CHANGES],
 'unchanged_unit_count':58,'retired_obsolete_grammar':40,'new_explicit_attested_grammar':10,'source_master_sha256':sha(OUT.read_bytes())}
runtime['integrity']={'algorithm':'sha256','entries_sha256':sha(canon(runtime['entries']))}
runtime['integrity']['payload_sha256']=sha(canon({k:v for k,v in runtime.items() if k!='integrity'}))
write(ROUT,runtime)
write(LEDGER,{'schema':'lesen-r19-10-p06-scoped-editorial-ledger@1','date':'2026-11-08','original_master_sha256':sha(SRC.read_bytes()),'original_runtime_sha256':sha(RUN.read_bytes()),
 'new_master_sha256':sha(OUT.read_bytes()),'new_runtime_sha256':sha(ROUT.read_bytes()),'changes':ledger,
 'scope':{'lessons':list(CHANGES),'sections':10,'german_sentences':10,'fa_en_pairs_changed':8,'fa_en_pairs_preserved':2,'retired_old_fulltext_anchors':40,'attested_new_annotations':10,'grammar_previous':4041,'grammar_current':len(allg)},
 'limitations':['Independent wholepack semantic QA not completed','Full original nine-lens grammar engine not rerun','Actual browser IndexedDB Stage6 not run','No final release']})
print(json.dumps({'master_sha':sha(OUT.read_bytes()),'master_bytes':OUT.stat().st_size,'runtime_sha':sha(ROUT.read_bytes()),'runtime_bytes':ROUT.stat().st_size,'changed_lessons':list(CHANGES),'old_grammar_removed':total_old,'grammar_new':len(allg),'ledger_sha':sha(LEDGER.read_bytes())},ensure_ascii=False,indent=2))