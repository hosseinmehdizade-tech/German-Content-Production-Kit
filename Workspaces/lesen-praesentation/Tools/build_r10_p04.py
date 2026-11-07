#!/usr/bin/env python3
"""Bounded Lesen R9 -> R10 trilingual p04 editorial candidate, lessons 021–030.
The present curated R9 master is authority. Never regenerate from original publisher PDF.
Manual 2-sentence editorial changes with matching section FA/EN, preserve p04-s02.
Never assert independent Stage4, full native grammar regeneration or browser Stage6.
"""
import json,copy,hashlib,pathlib,collections
DIR=pathlib.Path('/mnt/data/lesen_r10_20261107')
SRC=pathlib.Path('/mnt/data/lesen_r9_20261107/Lesen-Production-Master-v1.3.0-R9-10P04-TRILINGUAL-CANDIDATE.json')
OUT=DIR/'Lesen-Production-Master-v1.3.0-R10-10P04-TRILINGUAL-CANDIDATE.json'
LEDGER=DIR/'LESEN-R10-10P04-TRILINGUAL-GRAMMAR-LEDGER.json'
PIN='52667254d47987e5f4c4146078fd2c8204e80152de3268cd0eb599fc0c2f8171'
sha=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Texts are authored against the R9 lessons' p02/p03/p05 and the verbatim p04-s02.
EDITS={
21:{'s01':'Ein Alumni-Verein hilft beim Berufseinstieg nur dann wirklich, wenn Kontakte nicht zum Privileg gut vernetzter Absolventen werden.',
's03':'Hochschulen sollten deshalb gerade diejenigen aktiv einbeziehen, die bislang wenig Zugang zu beruflichen Netzwerken haben.',
'fa':'انجمن فارغ‌التحصیلان تنها زمانی واقعاً به ورود به بازار کار کمک می‌کند که ارتباط‌های شغلی به امتیاز ویژهٔ فارغ‌التحصیلانِ دارای شبکهٔ قوی تبدیل نشوند. اگر برنامه‌ها باز، شفاف و برای کسانی که تازه وارد بازار کار می‌شوند نیز در دسترس طراحی شوند، بخشی از این تعارض کاهش می‌یابد. بنابراین دانشگاه‌ها بهتر است به‌ویژه کسانی را فعالانه مشارکت دهند که تاکنون دسترسی کمی به شبکه‌های حرفه‌ای داشته‌اند.',
'en':'An alumni association truly helps people enter the workforce only if professional contacts do not become a privilege reserved for well-connected graduates. If its programs are open, transparent, and accessible to people just starting their careers, part of the conflict can be reduced. Universities should therefore actively include those who have so far had little access to professional networks.'},
22:{'s01':'Werken ist mehr als ein Nebenfach, weil Kinder dabei Materialien, Werkzeuge und ihre eigenen Fehler unmittelbar erleben.',
's03':'Schulen sollten Projekte so auswählen, dass sie praktische Fertigkeiten fördern und zugleich Unterrichtszeit sinnvoll nutzen.',
'fa':'کار عملی و کاردستی چیزی بیش از یک درس فرعی است، زیرا کودکان در آن مستقیماً با مواد، ابزارها و خطاهای خود روبه‌رو می‌شوند. اگر پروژه‌های عملی به‌صورت میان‌رشته‌ای با فناوری، هنر یا پایداری پیوند بخورند، بخشی از این تعارض کاهش می‌یابد. بنابراین مدارس بهتر است پروژه‌هایی انتخاب کنند که هم مهارت‌های عملی را پرورش دهند و هم از زمان کلاس به‌شکلی مفید استفاده کنند.',
'en':'Crafts and practical work are more than a minor school subject because children directly encounter materials, tools, and their own mistakes. If practical projects are linked across subjects with technology, art, or sustainability, part of the conflict can be reduced. Schools should therefore choose projects that develop practical skills while also making meaningful use of classroom time.'},
23:{'s01':'Berufliche Weiterbildung nützt wenig, wenn Beschäftigte dafür ständig Freizeit und eigenes Geld opfern müssen.',
's03':'Arbeitgeber sollten Lernziele mit den Aufgaben im Betrieb verbinden und dafür verlässlich Zeit bereitstellen.',
'fa':'آموزش تکمیلی شغلی زمانی فایدهٔ چندانی ندارد که کارکنان مجبور باشند دائماً وقت آزاد و پول شخصی خود را صرف آن کنند. اگر کارفرمایان از نظر زمان، تأمین مالی و مسیرهای روشن رشد شغلی حمایت کنند، بخشی از این تعارض کاهش می‌یابد. بنابراین کارفرمایان بهتر است هدف‌های یادگیری را به وظایف واقعی محل کار پیوند دهند و برای آن زمان مشخص و قابل‌اتکا در نظر بگیرند.',
'en':'Professional development is of little use if employees must constantly sacrifice their free time and personal money for it. If employers support learning through time, funding, and clear development paths, part of the conflict can be reduced. Employers should therefore connect learning goals to actual workplace tasks and reliably provide time for them.'},
24:{'s01':'Nicht jeder ruhige Raum eignet sich gleichermaßen für jede Lernaufgabe.',
's03':'Lernende sollten deshalb ausprobieren, ob sie für konzentriertes Lesen, Gruppenarbeit oder Prüfungsvorbereitung unterschiedliche Orte brauchen.',
'fa':'هر فضای ساکتی برای همهٔ فعالیت‌های یادگیری به یک اندازه مناسب نیست. اگر یادگیرندگان آگاهانه محیط خود را بر اساس نوع کار و شیوهٔ شخصی مطالعه انتخاب کنند، بخشی از این تعارض کاهش می‌یابد. بنابراین بهتر است امتحان کنند که آیا برای مطالعهٔ متمرکز، کار گروهی یا آمادگی امتحان به مکان‌های متفاوت نیاز دارند یا نه.',
'en':'Not every quiet room is equally suitable for every learning task. If learners consciously choose their environment according to the task and their personal way of working, part of the conflict can be reduced. They should therefore try out whether they need different places for focused reading, group work, or exam preparation.'},
25:{'s01':'Ein Lernplan soll Orientierung geben und darf nicht selbst zum zusätzlichen Stressfaktor werden.',
's03':'Studierende sollten ihre Wochenziele regelmäßig überprüfen und Erholung ebenso bewusst einplanen wie Lernphasen.',
'fa':'برنامهٔ مطالعه باید راهنما باشد و نباید خودش به عامل استرس بیشتر تبدیل شود. اگر برنامه‌ها زمان ذخیره داشته باشند و مرتب با شرایط تازه سازگار شوند، بخشی از این تعارض کاهش می‌یابد. بنابراین دانشجویان بهتر است هدف‌های هفتگی خود را به‌طور منظم بررسی کنند و زمان استراحت را نیز به‌اندازهٔ دوره‌های مطالعه آگاهانه برنامه‌ریزی کنند.',
'en':'A study plan should provide guidance and must not itself become an additional source of stress. If plans include buffer time and are adjusted regularly, part of the conflict can be reduced. Students should therefore review their weekly goals regularly and plan recovery time just as deliberately as study sessions.'},
26:{'s01':'Eine Verfilmung kann eine Geschichte anschaulich machen, aber die Erzählweise eines Romans nicht vollständig übernehmen.',
's03':'Beim Vergleich sollten Zuschauer und Leser fragen, was durch Bilder und Musik gewonnen wird und welche inneren Perspektiven verloren gehen.',
'fa':'اقتباس سینمایی می‌تواند داستانی را ملموس و دیدنی کند، اما نمی‌تواند شیوهٔ روایت یک رمان را به‌طور کامل منتقل کند. اگر کتاب و فیلم به‌عنوان دو شکل هنری متفاوت مقایسه شوند، نه دو محصول یکسان، بخشی از این تعارض کاهش می‌یابد. بنابراین تماشاگران و خوانندگان هنگام مقایسه بهتر است بپرسند تصویر و موسیقی چه چیزی به داستان اضافه می‌کنند و کدام دیدگاه‌های درونی از دست می‌روند.',
'en':'A film adaptation can bring a story vividly to life, but it cannot fully reproduce a novel’s way of telling that story. If book and film are compared as different art forms rather than treated as identical products, part of the conflict can be reduced. When comparing them, viewers and readers should ask what images and music add and which inner perspectives are lost.'},
27:{'s01':'Eltern helfen Jugendlichen am meisten, wenn sie Verantwortung schrittweise abgeben, statt den Studienweg vorzugeben.',
's03':'Sie sollten auch über Finanzierung und mögliche Umwege sprechen, damit eine spätere Kurskorrektur nicht als Scheitern erscheint.',
'fa':'والدین زمانی بیشترین کمک را به نوجوانان می‌کنند که مسئولیت را به‌تدریج به خود آنان بسپارند، نه اینکه مسیر تحصیلشان را از پیش تعیین کنند. اگر والدین مشاوره و حمایت ارائه دهند اما تصمیم‌ها را کم‌کم به فرزند واگذار کنند، بخشی از این تعارض کاهش می‌یابد. آنان بهتر است دربارهٔ هزینه‌های تحصیل و مسیرهای جایگزین احتمالی نیز صحبت کنند تا تغییر مسیر در آینده به‌صورت شکست دیده نشود.',
'en':'Parents help young people most when they gradually hand over responsibility instead of prescribing their educational path. If parents offer advice and support but increasingly leave decisions to their child, part of the conflict can be reduced. They should also discuss funding and possible alternative paths so that a later change of direction is not seen as failure.'},
28:{'s01':'Beim Sprachenlernen ist nicht Fehlerfreiheit der wichtigste Maßstab, sondern ob man die Sprache tatsächlich anwendet.',
's03':'Lernende sollten kleine Sprechanlässe suchen und Rückmeldungen nutzen, ohne aus jedem Fehler ein Urteil über ihre Begabung abzuleiten.',
'fa':'در یادگیری زبان، مهم‌ترین معیار بی‌اشتباه‌بودن نیست، بلکه این است که فرد زبان را واقعاً به کار ببرد. اگر یادگیری به هدف‌های کوچک و مشخص تقسیم شود و با موقعیت‌های واقعی ارتباط پیدا کند، بخشی از این تعارض کاهش می‌یابد. بنابراین زبان‌آموزان بهتر است فرصت‌های کوتاه برای صحبت‌کردن پیدا کنند و از بازخورد استفاده کنند، بی‌آنکه از هر اشتباه دربارهٔ استعداد خود قضاوتی کلی بسازند.',
'en':'In language learning, the most important measure is not being error-free but actually using the language. If learning is divided into small, concrete goals and connected to real situations, part of the conflict can be reduced. Learners should therefore seek short opportunities to speak and use feedback without treating every mistake as a judgment on their ability.'},
29:{'s01':'Eine stille sprachliche Modernisierung kann verletzende Ausdrücke entfernen, verwischt aber möglicherweise auch historische Spuren.',
's03':'Verlage sollten Änderungen kenntlich machen und den historischen Kontext erklären, statt bearbeitete Fassungen als unveränderte Originale auszugeben.',
'fa':'نوسازیِ بی‌سروصدای زبان یک متن ممکن است عبارت‌های آزاردهنده را حذف کند، اما در عین حال می‌تواند ردپاهای تاریخی را هم محو کند. اگر متن‌های اصلی حفظ شوند و بخش‌های مسئله‌دار از طریق مقدمه، پانویس یا آموزش در بستر تاریخی‌شان توضیح داده شوند، بخشی از این تعارض کاهش می‌یابد. بنابراین ناشران بهتر است تغییرات را مشخص کنند و زمینهٔ تاریخی را توضیح دهند، نه اینکه نسخه‌های ویرایش‌شده را به‌عنوان متن اصلیِ دست‌نخورده عرضه کنند.',
'en':'Quietly modernizing a text’s language can remove hurtful expressions, but it may also obscure historical traces. If original texts are preserved and problematic passages are contextualized through prefaces, footnotes, or teaching, part of the conflict can be reduced. Publishers should therefore clearly identify changes and explain the historical context instead of presenting edited versions as unchanged originals.'},
30:{'s01':'Der Ruf einer Hochschule ersetzt weder einen passenden Studiengang noch gute Betreuung im Studienalltag.',
's03':'Studieninteressierte sollten deshalb Lehrangebot, Kosten und Praxisbezug prüfen, bevor sie sich von Rankings leiten lassen.',
'fa':'شهرت یک دانشگاه نه جای رشتهٔ مناسب را می‌گیرد و نه جای پشتیبانی خوب در زندگی روزمرهٔ دانشجویی را. اگر دانشجویان محتوای رشته، کیفیت راهنمایی، هزینه‌ها و تناسب شخصی را بیشتر از رتبه‌بندی‌ها در نظر بگیرند، بخشی از این تعارض کاهش می‌یابد. بنابراین متقاضیان تحصیل بهتر است پیش از آنکه رتبه‌بندی‌ها جهت تصمیمشان را تعیین کنند، برنامهٔ آموزشی، هزینه‌ها و پیوند با کار عملی را بررسی کنند.',
'en':'A university’s reputation is no substitute for a suitable program or good support in everyday student life. If students give more weight to program content, supervision, cost, and personal fit than to rankings, part of the conflict can be reduced. Prospective students should therefore check the course offerings, costs, and practical orientation before letting rankings guide their decision.'}
}

def main():
    DIR.mkdir(parents=True,exist_ok=True)
    assert sha(SRC.read_bytes())==PIN,'R9 parent SHA mismatch'
    prev=json.loads(SRC.read_text(encoding='utf8')); cand=copy.deepcopy(prev)
    ledger=[]; removed=[]; added=[]; shifted_total=0; rets=0
    for n,edit in EDITS.items():
        a=prev['items'][n-1];b=cand['items'][n-1]
        assert a['id']==b['id']==f'LES-PRES-{n:03d}'
        po=a['reading']['sections'][3];pn=b['reading']['sections'][3]
        assert po['id']==pn['id']=='p04' and len(po['sentences'])==3
        assert po['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.')
        assert po['sentences'][1]==pn['sentences'][1]
        assert 'Statt nur zwischen Zustimmung und Ablehnung zu wählen' in po['sentences'][2]['text']
        pn['sentences'][0]['text']=edit['s01'];pn['sentences'][2]['text']=edit['s03']
        pn['text']=' '.join(s['text'] for s in pn['sentences'])
        pn['translations']={'fa':edit['fa'],'en':edit['en']}
        assert pn['text']!=po['text'] and len(pn['translations']['fa'])>180 and len(pn['translations']['en'])>170
        # Section-relative offsets: retire all changed-sentence occurrences, preserve and exactly re-anchor s02.
        old_g=b['grammar']['full_text_occurrences'];g=[];drop=[];kept_s02=0;shifted=0
        for x in old_g:
            if x['section_id']!='p04':g.append(copy.deepcopy(x));continue
            assert po['text'][x['start']:x['end']]==x['target_text']
            if x['sentence_id']!='p04-s02':
                drop.append({'id':x['id'],'grammar_key':x['grammar_key'],'sentence_id':x['sentence_id'],'target_text':x['target_text'],'reason':'REVISED_SENTENCE_INVALIDATES_OLD_CONTEXT'})
                removed.append((b['id'],x['id']));continue
            nn=copy.deepcopy(x)
            idx=pn['sentences'][1]['text'].find(nn['target_text'])
            assert idx>=0
            nn['start']=len(pn['sentences'][0]['text'])+1+idx
            nn['end']=nn['start']+len(nn['target_text'])
            assert pn['text'][nn['start']:nn['end']]==nn['target_text']
            shifted+=int(nn['start']!=x['start']);kept_s02+=1
            g.append(nn)
        s03=pn['sentences'][2]['text']; marker='sollten'
        assert s03.count(marker)==1,(n,s03)
        pos=len(pn['sentences'][0]['text'])+1+len(pn['sentences'][1]['text'])+1+s03.index(marker)
        gid=f'ftg-r10-{n:03d}-p04-k2-advice'
        assert gid not in {o['id'] for o in g}
        ann={'id':gid,'grammar_key':'konjunktiv_ii','label_de':'Konjunktiv II als Empfehlung','section_id':'p04','sentence_id':'p04-s03',
             'start':pos,'end':pos+len(marker),'target_text':marker,
             'explanation_de':'Die Form „sollten“ kennzeichnet einen Ratschlag bzw. eine begründete Empfehlung im Konjunktiv II; keine Tatsachenbehauptung.',
             'explanation_fa':'صورت «sollten» در اینجا توصیه یا پیشنهاد سنجیده در وجه Konjunktiv II را بیان می‌کند، نه گزارش یک واقعیت.',
             'details':{'scope':'manual_scoped_r10_p04_s03','form':marker},'confidence':'high',
             'annotation_source':'editorial_scoped_r10','derivation_method':'manual_explicit_lexical_and_semantic_evidence'}
        assert pn['text'][ann['start']:ann['end']]==marker
        g.append(ann);added.append((b['id'],gid));b['grammar']['full_text_occurrences']=g
        summary=b['grammar']['full_text_lens_summary'];summary['occurrences']=len(g);summary['counts']=dict(collections.Counter(x['grammar_key'] for x in g))
        summary['scope_note_de']='R10: p04-s02-Anker nach Prüfung exakt neu positioniert; alte Vorkommen aus umformulierten Sätzen entfernt; eine manuell validierte Konjunktiv-II-Empfehlung ergänzt. Der native Neun-Linsen-Generator wurde nicht neu ausgeführt.'
        summary['scope_note_fa']='در R10 ارجاع‌های گرامری جملهٔ دوم حفظ و با جایگاه جدید تطبیق داده شدند؛ ارجاع‌های جمله‌های تغییرکرده کنار گذاشته شدند و یک کاربرد Konjunktiv II به‌صورت محدود بررسی شد. موتور اصلی گرامر دوباره اجرا نشده است.'
        curated=[]
        for x in b['grammar']['curated_annotations']:
            if x['section_id']=='p04' and x['sentence_id']=='p04-s03':
                assert x['id']=='g07' and x['grammar_key']=='konjunktiv_ii'
                x['target_text']=s03;x['annotation_source']='editorial_retarget_r10'
                curated.append(x['id']);rets+=1
        for x in b['grammar']['curated_annotations']:
            sec=next(s for s in b['reading']['sections'] if s['id']==x['section_id'])
            sent=next(s for s in sec['sentences'] if s['id']==x['sentence_id'])
            assert x['target_text'] in sent['text'],(b['id'],x['id'])
        full=' '.join(s['text'] for s in b['reading']['sections'])
        b['reading']['word_count_de']=len(full.split())
        b['quality']['content_hash']=sha(full.encode())[:16]
        b['quality']['app_mapping_status']='r10_scoped_p04_candidate_preentry_only'
        ledger.append({'unit_id':b['id'],'title_de':b['title_de'],'source_sections':['p02','p03','p05'],
                       'original_p04':po,'revised_p04':pn,'before_grammar':len(a['grammar']['full_text_occurrences']),
                       'after_grammar':len(g),'invalidated_grammar':drop,'retained_p04_s02':kept_s02,
                       'shifted_p04_s02':shifted,'new_scoped_grammar':ann,'retargeted_curated':curated,
                       'before_word_count':a['reading']['word_count_de'],'after_word_count':b['reading']['word_count_de'],
                       'parent_item_sha256':sha(canonical(a)),'revised_item_sha256':sha(canonical(b))})
        shifted_total+=shifted
    assert len(ledger)==10
    assert all(prev['items'][i]==cand['items'][i] for i in list(range(20))+list(range(30,68)))
    occ=[x for b in cand['items'] for x in b['grammar']['full_text_occurrences']]
    qa=cand['full_text_grammar_qa'];qa['occurrences']=len(occ);qa['counts']=dict(collections.Counter(x['grammar_key'] for x in occ));qa['offset_exact_matches']=len(occ)
    qa['result']='R10_SCOPED_EXACT_P04_SPANS__NOT_FULL_NATIVE_GRAMMAR_OR_STAGE4'
    qa['r10_scoped_status']={'changed_units':10,'old_anchors_invalidated':len(removed),
                            'p04_s02_exact_shifted':shifted_total,'new_scoped_k2':len(added),
                            'native_full_nine_lens_engine_rerun':False,'independent_stage4':'HOLD'}
    cand['qa_summary']['word_count_de']={'min':min(u['reading']['word_count_de'] for u in cand['items']),
                                        'mean':round(sum(u['reading']['word_count_de'] for u in cand['items'])/68,1),
                                        'max':max(u['reading']['word_count_de'] for u in cand['items'])}
    cand['qa_summary']['r10_scope']='TEN_P04_MULTILINGUAL_SECTIONS_021_TO_030__NATIVE_FULL_GRAMMAR_NOT_RUN'
    cand['translation_qa']['r10_review_status']='AI_SCOPED_10_P04__INDEPENDENT_STAGE4_HOLD'
    cand['translation_qa']['result']='R10_SCOPED_10_P04_TRILINGUAL_NOT_HOLISTIC_STAGE4'
    cand['content_version']='1.3.0-R10-CANDIDATE'
    cand['status']='R10_SCOPED_10_P04_TRILINGUAL_GRAMMAR_CANDIDATE__STAGE4_6_7_HOLD'
    for a,b in zip(prev['items'],cand['items']):
        assert a['id']==b['id'] and a['questions']==b['questions'] and a['vocabulary']==b['vocabulary']
        for x in b['grammar']['full_text_occurrences']:
            sec=next(t for t in b['reading']['sections'] if t['id']==x['section_id'])
            assert sec['text'][x['start']:x['end']]==x['target_text'],(b['id'],x['id'])
    save(OUT,cand)
    rec={'schema':'lesen-r10-trilingual-scoped-p04@1.0.0','date':'2026-11-07','parent_sha256':PIN,
         'candidate_sha256':sha(OUT.read_bytes()),'candidate_bytes':OUT.stat().st_size,
         'changed_units':[u['unit_id'] for u in ledger],'changed_sections':10,'changed_de_sentences':20,
         'preserved_p04_s02_sentences':10,'unaffected_units':58,
         'fulltext_grammar_before':sum(len(u['grammar']['full_text_occurrences']) for u in prev['items']),
         'fulltext_grammar_after':len(occ),'invalidated_old_grammar':len(removed),
         'p04_s02_reanchored':shifted_total,'new_scoped_grammar':len(added),
         'curated_annotations_retargeted':rets,'native_full_grammar_rerun':False,
         'independent_semantic_stage4':'HOLD','browser_stage6':'NOT_RUN','stage7':'NOT_FINAL',
         'unchanged_q_ids':340,'unchanged_vocabulary':350,'current_zip_unchanged':True,
         'before_after':ledger}
    save(LEDGER,rec)
    print(json.dumps({k:v for k,v in rec.items() if k!='before_after'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()