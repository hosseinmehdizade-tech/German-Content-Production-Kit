#!/usr/bin/env python3
"""R10 -> R11 editorial p04 DE/FA/EN 031-040, with previously accepted 035 preserved.
Curated R10 content is authority. Source-bound human-authored, not generated from original PDF.
No native full 9-lens producer, no Stage4/6 claim, no mutation of CURRENT or the app.
"""
import copy, hashlib, json, pathlib, collections
DIR=pathlib.Path('/mnt/data/lesen_r11_20261107')
SRC=pathlib.Path('/mnt/data/lesen_r10_20261107/Lesen-Production-Master-v1.3.0-R10-10P04-TRILINGUAL-CANDIDATE.json')
OUT=DIR/'Lesen-Production-Master-v1.3.0-R11-9P04-TRILINGUAL-CANDIDATE.json'
LEDGER=DIR/'LESEN-R11-9P04-TRILINGUAL-GRAMMAR-LEDGER.json'
PIN='4be5bf368b23a1a46bae2d28686b3d4f9336ac01d98c2c1449ab19df81b9509a'
sha=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Each FA/EN paragraph is a faithful translation of new DE sentence 1 + existing DE sentence 2 + new DE sentence 3.
EDITS={
31:{'s01':'Im Unterricht ist nicht das Smartphone selbst die Lernmethode, sondern der Auftrag, für den es eingesetzt wird.',
's03':'Lehrkräfte könnten die Geräte für gezielte Recherchen freigeben und sie während längerer Konzentrationsphasen weglegen lassen.', 'k2':'könnten',
'fa':'در کلاس، خودِ گوشی هوشمند روش یادگیری نیست، بلکه تکلیفی مهم است که برای آن از گوشی استفاده می‌شود. اگر قوانین روشن، بازه‌های زمانی محدود و تکلیف‌های مشخص آموزشی تعیین شوند، می‌توان بخشی از این تعارض را کاهش داد. معلمان می‌توانند استفاده از دستگاه‌ها را برای پژوهش‌های هدفمند مجاز کنند و بخواهند در فعالیت‌هایی که به تمرکز طولانی نیاز دارند، گوشی‌ها کنار گذاشته شوند.',
'en':'In the classroom, the smartphone itself is not a teaching method; what matters is the task for which it is used. If clear rules, limited periods of use and specific learning tasks are agreed upon, part of the conflict can be eased. Teachers could allow the devices for focused research and have them put away during longer periods requiring concentration.'},
32:{'s01':'Roboter sind vor allem dort sinnvoll, wo sie gefährliche Aufgaben übernehmen, ohne menschliche Nähe ersetzen zu müssen.',
's03':'In der Pflege könnten sie beim Heben helfen, während Entscheidungen über Betreuung und Verantwortung bei Menschen bleiben.', 'k2':'könnten',
'fa':'ربات‌ها به‌ویژه جایی مفیدند که کارهای خطرناک را انجام می‌دهند، بی‌آنکه مجبور باشند جای نزدیکی و ارتباط انسانی را بگیرند. اگر قواعد ایمنی، مسئولیت حقوقی و نظارت انسان به‌روشنی تعیین شوند، می‌توان بخشی از این تعارض را کاهش داد. در مراقبت از بیماران، ربات‌ها می‌توانند برای بلندکردن افراد کمک کنند، درحالی‌که تصمیم‌ها دربارهٔ مراقبت و مسئولیت همچنان بر عهدهٔ انسان‌ها می‌ماند.',
'en':'Robots are most useful where they take over dangerous tasks without having to replace human contact. If safety rules, liability and human oversight are clearly regulated, part of the conflict can be eased. In care settings, they could help with lifting while decisions about care and responsibility remain with people.'},
33:{'s01':'Musikunterricht entfaltet seinen Wert nicht nur auf der Bühne, sondern auch beim gemeinsamen Zuhören und Ausprobieren.',
's03':'Schulen könnten Singen, Rhythmusprojekte und unterschiedliche Musiktraditionen einbeziehen, statt ausschließlich Instrumentaltechnik zu benoten.', 'k2':'könnten',
'fa':'ارزش درس موسیقی تنها روی صحنه آشکار نمی‌شود، بلکه در گوش‌دادن و تجربه‌کردنِ مشترک نیز شکل می‌گیرد. اگر آموزش موسیقی متنوع طراحی شود و تنها مهارت نوازندگی ارزیابی نشود، می‌توان بخشی از این تعارض را کاهش داد. مدارس می‌توانند آوازخوانی، پروژه‌های ریتم و سنت‌های گوناگون موسیقی را وارد برنامه کنند، به‌جای آنکه فقط مهارت نوازندگی را نمره بدهند.',
'en':'Music lessons show their value not only on stage but also through listening and experimenting together. If music teaching is varied and assessment does not focus solely on instrumental performance, part of the conflict can be eased. Schools could include singing, rhythm projects and different musical traditions instead of grading only instrumental technique.'},
34:{'s01':'Ein professionelles Online-Profil kann berufliche Kontakte eröffnen, doch permanente Sichtbarkeit setzt viele Menschen unter Druck.',
's03':'Für eine Bewerbung wäre ein Profil mit nachvollziehbaren Projekten hilfreicher als die ständige Inszenierung des Privatlebens.', 'k2':'wäre',
'fa':'یک پروفایل حرفه‌ای آنلاین می‌تواند زمینهٔ ارتباط‌های کاری را فراهم کند، اما دیده‌شدن دائمی برای بسیاری از افراد فشار ایجاد می‌کند. اگر کاربران حریم خصوصی، مخاطبان و محتوای خود را آگاهانه مدیریت کنند، می‌توان بخشی از این تعارض را کاهش داد. برای درخواست شغل، پروفایلی که پروژه‌های قابل‌بررسی را نشان می‌دهد سودمندتر از نمایش همیشگی زندگی خصوصی خواهد بود.',
'en':'A professional online profile can open up career contacts, but constant visibility puts pressure on many people. If users consciously manage their privacy, audience and content, part of the conflict can be eased. For a job application, a profile showing verifiable projects would be more useful than constantly staging one’s private life.'},
36:{'s01':'Ernährungsbildung soll Kinder zu eigenen Entscheidungen befähigen, statt Lebensmittel oder Familien moralisch zu bewerten.',
's03':'Praktisches Kochen und das Lesen von Zutatenlisten könnten Wissen greifbar machen, ohne einzelne Kinder wegen ihrer Essgewohnheiten bloßzustellen.', 'k2':'könnten',
'fa':'آموزش تغذیه باید کودکان را برای تصمیم‌گیری مستقل توانمند کند، نه اینکه دربارهٔ خوراکی‌ها یا خانواده‌ها قضاوت اخلاقی کند. اگر آموزش واقع‌بینانه، عملی و بدون شرمنده‌کردن طراحی شود، می‌توان بخشی از این تعارض را کاهش داد. آشپزی عملی و خواندن فهرست مواد تشکیل‌دهنده می‌توانند دانش را ملموس کنند، بدون اینکه کودکی به‌خاطر عادت‌های غذایی‌اش تحقیر شود.',
'en':'Nutrition education should enable children to make their own decisions instead of passing moral judgments on foods or families. If lessons are factual, practical and free of shaming, part of the conflict can be eased. Cooking activities and reading ingredient lists could make knowledge tangible without embarrassing individual children about their eating habits.'},
37:{'s01':'Fachwissen allein macht eine Vorlesung noch nicht verständlich; dafür braucht es auch eine didaktische Struktur.',
's03':'Hochschulen sollten klare Lernziele und hilfreiches Feedback fördern, ohne Studierenden die Verantwortung für ihr Lernen abzunehmen.', 'k2':'sollten',
'fa':'دانش تخصصی به‌تنهایی یک سخنرانی دانشگاهی را قابل‌فهم نمی‌کند؛ برای این کار به ساختار آموزشی مناسب نیز نیاز است. اگر استادان دانشگاه مهارت‌های پایهٔ تدریس را توسعه دهند و دانشجویان نیز مسئولیت خود را بپذیرند، می‌توان بخشی از این تعارض را کاهش داد. دانشگاه‌ها بهتر است هدف‌های یادگیری روشن و بازخورد مفید را تقویت کنند، بی‌آنکه مسئولیت یادگیری را از دانشجویان بگیرند.',
'en':'Subject expertise alone does not make a lecture understandable; it also needs a sound teaching structure. If university teachers develop basic didactic skills and students take responsibility, part of the conflict can be eased. Universities should encourage clear learning objectives and useful feedback without taking responsibility for learning away from students.'},
38:{'s01':'Mehr Studienplätze sind erst dann ein Fortschritt, wenn Betreuung und Räume mit der Nachfrage Schritt halten.',
's03':'Statt nur Zulassungszahlen zu erhöhen, müssten Hochschulen Seminarkapazitäten, Beratung und Ausstattung gemeinsam planen.', 'k2':'müssten',
'fa':'افزایش ظرفیت پذیرش دانشگاه تنها زمانی پیشرفت محسوب می‌شود که پشتیبانی آموزشی و فضاها هم‌پای تقاضا گسترش پیدا کنند. اگر نیروی انسانی، فضاها و سامانه‌های دیجیتال متناسب با نیاز توسعه یابند، می‌توان بخشی از این تعارض را کاهش داد. دانشگاه‌ها به‌جای بالا بردن صرفِ تعداد پذیرش، باید ظرفیت کلاس‌ها، مشاوره و تجهیزات را هماهنگ با هم برنامه‌ریزی کنند.',
'en':'More university places are progress only when academic support and facilities keep pace with demand. If staff, spaces and digital systems are expanded accordingly, part of the conflict can be eased. Instead of simply increasing admissions, universities would need to plan seminar capacity, guidance and equipment together.'},
39:{'s01':'Ein einheitlicher Kostenbeitrag wäre ungerecht, weil Einkommen und Zukunftspläne junger Erwachsener stark auseinandergehen.',
's03':'Familien sollten offen über Haushaltskosten und Sparziele sprechen, damit ein Beitrag nicht den späteren Auszug erschwert.', 'k2':'sollten',
'fa':'دریافت مبلغ یکسان از همه ناعادلانه خواهد بود، زیرا درآمد و برنامه‌های آیندهٔ جوانان بزرگسال تفاوت زیادی دارد. اگر سهم پرداختی با توجه به درآمد، مرحلهٔ زندگی و هزینه‌های واقعی تعیین شود، می‌توان بخشی از این تعارض را کاهش داد. خانواده‌ها بهتر است دربارهٔ هزینه‌های خانه و هدف‌های پس‌انداز صریح صحبت کنند تا این کمک مالی، مستقل‌شدن و نقل‌مکان بعدی را دشوار نکند.',
'en':'A uniform contribution would be unfair because young adults differ greatly in income and plans for the future. If contributions are agreed according to income, life stage and actual costs, part of the conflict can be eased. Families should discuss household costs and saving goals openly so that a contribution does not make moving out later more difficult.'},
40:{'s01':'Fachliche Autorität entsteht durch Kompetenz und Fairness, nicht durch die Erwartung bedingungslosen Gehorsams.',
's03':'Lehrende könnten Regeln klar vertreten und zugleich Widerspruch zulassen, damit Studierende eigenständig urteilen lernen.', 'k2':'könnten',
'fa':'اقتدار علمی از تخصص و انصاف به وجود می‌آید، نه از انتظار اطاعت بی‌چون‌وچرا. اگر اقتدار بر تخصص، انصاف و مسئولیت استوار باشد و نه بر ترساندن، می‌توان بخشی از این تعارض را کاهش داد. استادان می‌توانند بر قواعد روشن پافشاری کنند و هم‌زمان اجازهٔ مخالفت بدهند تا دانشجویان یاد بگیرند مستقل قضاوت کنند.',
'en':'Academic authority comes from competence and fairness, not from the expectation of unquestioning obedience. If authority is based on competence, fairness and responsibility rather than intimidation, part of the conflict can be eased. Teachers could uphold clear rules while also allowing disagreement so that students learn to form independent judgments.'},
}

def main():
    assert sha(SRC.read_bytes())==PIN,'R10 SOURCE NOT EXACT'; DIR.mkdir(exist_ok=True,parents=True)
    old=json.loads(SRC.read_text(encoding='utf8'));cand=copy.deepcopy(old)
    ledger=[]; removed=[]; shifted=0; retained=0; new_a=[]; retargeted=[]
    assert set(EDITS)==set(range(31,41))-{35}
    assert not old['items'][34]['reading']['sections'][3]['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.')
    for n,edit in EDITS.items():
        a=old['items'][n-1];b=cand['items'][n-1]
        assert a['id']==b['id']==f'LES-PRES-{n:03d}'
        old_s=a['reading']['sections'][3];new_s=b['reading']['sections'][3]
        assert len(old_s['sentences'])==3 and old_s['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.')
        assert old_s['sentences'][1]==new_s['sentences'][1]
        assert len(edit['fa'])>=140 and len(edit['en'])>=170
        new_s['sentences'][0]['text']=edit['s01'];new_s['sentences'][2]['text']=edit['s03']
        new_s['text']=' '.join(x['text'] for x in new_s['sentences'])
        new_s['translations']={'fa':edit['fa'],'en':edit['en']}
        assert new_s['text'] != old_s['text']
        old_occ=a['grammar']['full_text_occurrences'];g=[];drop=[];middle_reanchors=[]
        old_middle_start=len(old_s['sentences'][0]['text'])+1
        new_middle_start=len(new_s['sentences'][0]['text'])+1
        for occ in old_occ:
            if occ['section_id']!='p04':g.append(copy.deepcopy(occ));continue
            assert old_s['text'][occ['start']:occ['end']]==occ['target_text']
            if occ['sentence_id']!='p04-s02':
                removed.append((a['id'],occ['id']));drop.append({'id':occ['id'],'grammar_key':occ['grammar_key'],'target':occ['target_text'],'old_sentence':occ['sentence_id']})
                continue
            o=copy.deepcopy(occ)
            old_relative=o['start']-old_middle_start
            assert old_relative>=0 and old_s['sentences'][1]['text'][old_relative:old_relative+len(o['target_text'])]==o['target_text']
            o['start']=new_middle_start+old_relative;o['end']=o['start']+len(o['target_text'])
            assert new_s['text'][o['start']:o['end']]==o['target_text']
            shifted+=int(o['start']!=occ['start']);retained+=1
            middle_reanchors.append({'id':o['id'],'before':occ['start'],'after':o['start']});g.append(o)
        marker=edit['k2'];s3=edit['s03'];assert s3.count(marker)==1,(n,marker)
        mpos=len(new_s['sentences'][0]['text'])+1+len(new_s['sentences'][1]['text'])+1+s3.index(marker)
        ann={'id':f'ftg-r11-{n:03d}-p04-k2','grammar_key':'konjunktiv_ii','label_de':'Konjunktiv II für eine mögliche Handlung oder Empfehlung',
             'section_id':'p04','sentence_id':'p04-s03','start':mpos,'end':mpos+len(marker),'target_text':marker,
             'explanation_de':f'„{marker}“ steht hier im Konjunktiv II und drückt einen Vorschlag, eine Möglichkeit oder eine vorsichtig formulierte Anforderung aus.',
             'explanation_fa':f'«{marker}» در این جمله ساخت Konjunktiv II است و برای بیان پیشنهاد، امکان یا درخواست سنجیده به کار می‌رود.',
             'details':{'scope':'manual_scoped_r11_p04_s03','form':marker},'confidence':'high','annotation_source':'editorial_scoped_r11',
             'derivation_method':'manually_attested_specific_german_form_not_full_engine'}
        assert new_s['text'][mpos:mpos+len(marker)]==marker and ann['id'] not in {q['id'] for q in g}
        g.append(ann);new_a.append((b['id'],ann['id'],marker))
        b['grammar']['full_text_occurrences']=g
        summary=b['grammar']['full_text_lens_summary'];summary['occurrences']=len(g);summary['counts']=dict(collections.Counter(x['grammar_key'] for x in g))
        summary['scope_note_de']='R11: Ersetzte p04-s01/s03-Sätze erfordern Entfernung alter Kontextmarker; p04-s02-Marker exakt neu positioniert; genau eine neue geprüfte Konjunktiv-II-Form ergänzt. Native Neun-Linsen-Analyse nicht neu ausgeführt.'
        summary['scope_note_fa']='در R11 ارجاع‌های مربوط به جمله‌های تغییرکرده حذف و ارجاع‌های جملهٔ دوم با دقت جابه‌جا شدند؛ یک نمونهٔ مشخص Konjunktiv II افزوده شد. موتور کامل گرامر اجرا نشده است.'
        rets=[]
        for cur in b['grammar']['curated_annotations']:
            if cur['section_id']=='p04' and cur['sentence_id']=='p04-s03':
                assert cur['grammar_key']=='konjunktiv_ii' and cur['id']=='g07'
                cur['target_text']=s3;cur['annotation_source']='editorial_retarget_r11'
                rets.append(cur['id']);retargeted.append((b['id'],cur['id']))
        for cur in b['grammar']['curated_annotations']:
            sec=next(s for s in b['reading']['sections'] if s['id']==cur['section_id'])
            sent=next(s for s in sec['sentences'] if s['id']==cur['sentence_id'])
            assert cur['target_text'] in sent['text'],(b['id'],cur['id'])
        b['reading']['word_count_de']=len(' '.join(sec['text'] for sec in b['reading']['sections']).split())
        b['quality']['content_hash']=sha(' '.join(sec['text'] for sec in b['reading']['sections']).encode())[:16]
        b['quality']['app_mapping_status']='r11_scoped_p04_candidate_preentry_only'
        ledger.append({'unit_id':b['id'],'title_de':b['title_de'],'before_p04':old_s,'after_p04':new_s,'source_evidence_sections':['p02','p03','p05'],
                       'old_grammar_p04_removed':drop,'s02_reanchors':middle_reanchors,'new_manual_grammar':ann,'curated_s03_retargeted':rets,
                       'parent_item_sha256':sha(canonical(a)),'r11_item_sha256':sha(canonical(b))})
    assert old['items'][34]==cand['items'][34], 'PREVIOUSLY ACCEPTED LESSON 035 MUST NOT CHANGE'
    assert sum(a!=b for a,b in zip(old['items'],cand['items']))==9
    allocc=[x for unit in cand['items'] for x in unit['grammar']['full_text_occurrences']]
    qa=cand['full_text_grammar_qa'];qa['occurrences']=len(allocc);qa['counts']=dict(collections.Counter(x['grammar_key'] for x in allocc));qa['offset_exact_matches']=len(allocc)
    qa['result']='R11_SCOPED_EXACT_SPANS__NOT_COMPLETE_NATIVE_GRAMMAR_OR_STAGE4';qa['r11_scope']={'changed_units':9,'preserved_lesson_035':True,'removed_prior_spans':len(removed),'s02_shifted_exact':shifted,'new_explicit_k2_spans':len(new_a),'native_9_lens_rerun':False,'stage4':'HOLD'}
    wc=[u['reading']['word_count_de'] for u in cand['items']]
    cand['qa_summary']['word_count_de']={'min':min(wc),'mean':round(sum(wc)/68,1),'max':max(wc)}
    cand['qa_summary']['r11_scope']='NINE_P04_TRILINGUAL_SECTIONS_031_TO_040_EXCEPT_PREVIOUSLY_REVISED_035'
    cand['translation_qa']['r11_review_status']='SCOPED_AI_EDITORIAL_TRILINGUAL_NOT_INDEPENDENT_STAGE4'
    cand['translation_qa']['result']='R11_9_P04_SECTIONS_REVIEWED_STILL_STAGE4_HOLD'
    cand['content_version']='1.3.0-R11-CANDIDATE';cand['status']='R11_9_P04_TRILINGUAL_GRAMMAR_CANDIDATE__STAGE4_6_7_HOLD'
    for a,b in zip(old['items'],cand['items']):
        assert a['id']==b['id'] and a['questions']==b['questions'] and a['vocabulary']==b['vocabulary']
        for occ in b['grammar']['full_text_occurrences']:
            sec=next(s for s in b['reading']['sections'] if s['id']==occ['section_id'])
            assert sec['text'][occ['start']:occ['end']]==occ['target_text'],(b['id'],occ['id'])
    write(OUT,cand)
    rec={'schema':'lesen-r11-9p04-multilingual-ledger@1.0.0','date':'2026-11-07','parent_content_sha256':PIN,
         'candidate_content_sha256':sha(OUT.read_bytes()),'candidate_bytes':OUT.stat().st_size,
         'changed_unit_ids':[x['unit_id'] for x in ledger],'preserved_previously_edited':['LES-PRES-035'],'changed_p04_sections':9,
         'changed_de_sentences':18,'unchanged_p04_middle_sentences':9,'unchanged_master_units':59,
         'grammar_before':sum(len(x['grammar']['full_text_occurrences']) for x in old['items']),'grammar_after':len(allocc),
         'invalidated_old_occurrences':len(removed),'middle_anchors_repositioned':shifted,'middle_anchors_retained':retained,
         'new_scoped_occurrences':len(new_a),'curated_annotations_retargeted':len(retargeted),
         'native_9_lens_engine_rerun':False,'independent_semantic_stage4':'HOLD','browser_stage6':'NOT_RUN','stage7':'NOT_FINAL',
         'all_questions_unchanged':340,'vocabulary_unchanged':350,'immutable_current_modified':False,
         'before_after':ledger}
    write(LEDGER,rec)
    print(json.dumps({k:v for k,v in rec.items() if k!='before_after'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()