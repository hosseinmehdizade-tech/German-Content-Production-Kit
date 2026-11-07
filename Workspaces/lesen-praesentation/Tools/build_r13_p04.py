#!/usr/bin/env python3
"""R12->R13 content: 16 individually drafted, source-bound p04 trilingual revisions.
No original text source rewind, no native nine-lens rebuild, no browser/user-state changes.
"""
import json,copy,hashlib,pathlib,collections
P=pathlib.Path('/mnt/data/lesen_r13_20261107');P.mkdir(exist_ok=True)
SRC=pathlib.Path('/mnt/data/lesen_r12_20261107/Lesen-Production-Master-v1.3.0-R12-10P04-TRILINGUAL-CANDIDATE.json')
OUT=P/'Lesen-Production-Master-v1.3.0-R13-16P04-TRILINGUAL-CANDIDATE.json'
LEDGER=P/'LESEN-R13-16P04-TRILINGUAL-GRAMMAR-LEDGER.json'
SOURCE_SHA='a41224ae7a054a959c942afb0b13fcb7d686c76fc27131ec813a9272dad6e7d2'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Each field is individually authored against R12 p02, p03, p04-s02 and p05.
# FA/EN reflect all three DE sentences, including the unchanged source p04-s02.
EDITS={
52:{'s01':'KI kann Routinearbeiten erleichtern, doch fehlerhafte oder voreingenommene Ergebnisse bleiben ein Risiko.',
    's03':'Beschäftigte sollten KI-Vorschläge deshalb prüfen und Entscheidungen nicht ungeprüft an Systeme abgeben.', 'k2':'sollten',
    'fa':'هوش مصنوعی می‌تواند کارهای تکراری را آسان کند، اما نتیجه‌های اشتباه یا جانبدارانه همچنان خطر به شمار می‌روند. اگر شفافیت، کنترل انسانی و مسئولیت‌های روشن به‌شکل الزام‌آور تنظیم شوند، می‌توان بخشی از این تعارض را کاهش داد. بنابراین کارکنان بهتر است پیشنهادهای هوش مصنوعی را بررسی کنند و تصمیم‌ها را بدون بررسی به سیستم‌ها نسپارند.',
    'en':'AI can make routine tasks easier, but incorrect or biased results remain a risk. If transparency, human oversight and clear responsibilities are made binding requirements, part of the conflict can be eased. Employees should therefore review AI suggestions and should not hand over decisions to systems without checking them.'},
53:{'s01':'Gute Bildung vermittelt nicht nur Fachwissen, sondern stärkt auch die Fähigkeit, Argumente zu prüfen und mit anderen zu arbeiten.',
    's03':'Schulen müssten dafür Lernziele klar gewichten, statt jede gesellschaftliche Erwartung zu einer neuen Pflichtaufgabe zu machen.', 'k2':'müssten',
    'fa':'آموزش خوب فقط دانش تخصصی منتقل نمی‌کند، بلکه توانایی سنجش استدلال‌ها و همکاری با دیگران را نیز تقویت می‌کند. اگر مبانی تخصصی به‌صورت منظم با مهارت‌های فراتر از یک رشته پیوند داده شوند، می‌توان بخشی از این تعارض را کاهش داد. برای این کار مدارس باید هدف‌های آموزشی را روشن اولویت‌بندی کنند، نه اینکه هر انتظار اجتماعی را به وظیفه‌ای اجباری تبدیل کنند.',
    'en':'Good education does more than convey subject knowledge: it strengthens the ability to assess arguments and work with others. If subject foundations are systematically combined with transferable skills, part of the conflict can be eased. Schools would need to set clear priorities for learning goals rather than turn every social expectation into a new compulsory task.'},
54:{'s01':'Eine zufällige Begegnung kann einen Berufsweg verändern, ersetzt aber weder Können noch Vorbereitung.',
    's03':'Wer neue Möglichkeiten entdeckt, könnte sie mit den eigenen Zielen abgleichen, bevor er einen eingeschlagenen Weg verlässt.', 'k2':'könnte',
    'fa':'یک دیدار اتفاقی می‌تواند مسیر شغلی را تغییر دهد، اما جای مهارت و آمادگی را نمی‌گیرد. اگر افراد هدف‌هایشان را دنبال کنند و هم‌زمان برای فرصت‌های برنامه‌ریزی‌نشده باز بمانند، می‌توان بخشی از این تعارض را کاهش داد. کسی که امکان تازه‌ای پیدا می‌کند، می‌تواند پیش از کنار گذاشتن مسیر قبلی آن را با هدف‌های خود بسنجد.',
    'en':'A chance encounter can change a career path, but it cannot replace skill or preparation. If people pursue their goals while remaining open to unplanned opportunities, part of the conflict can be eased. Someone who discovers a new possibility could compare it with their own goals before abandoning an established path.'},
55:{'s01':'Beim Lernen kann kurzfristige Anspannung aktivieren; dauerhafter Druck beeinträchtigt dagegen Schlaf, Konzentration und Gedächtnis.',
    's03':'Lehrende sollten Leistungsanforderungen so planen, dass Pausen als Teil erfolgreichen Lernens gelten.', 'k2':'sollten',
    'fa':'هنگام یادگیری، تنش کوتاه‌مدت می‌تواند فرد را فعال‌تر کند؛ در مقابل، فشار دائمی به خواب، تمرکز و حافظه آسیب می‌زند. اگر خواسته‌ها واقع‌بینانه باشند و زمان‌های استراحت در برنامه قرار بگیرند، می‌توان بخشی از این تعارض را کاهش داد. مدرسان بهتر است تکلیف‌ها و انتظارهای عملکردی را طوری برنامه‌ریزی کنند که استراحت بخشی از یادگیری موفق به حساب آید.',
    'en':'Short-term tension can stimulate learning, whereas lasting pressure harms sleep, concentration and memory. If demands are realistic and recovery periods are included in the schedule, part of the conflict can be eased. Teachers should plan performance requirements so that breaks count as part of successful learning.'},
56:{'s01':'Digitale Informationen machen Wissen schneller zugänglich, ersetzen jedoch weder ruhige Lernorte noch persönliche Beratung.',
    's03':'Bibliotheken könnten weiterhin offenen Zugang zu Datenbanken, Arbeitsplätzen und Hilfe bei der Quellenbewertung anbieten.', 'k2':'könnten',
    'fa':'اطلاعات دیجیتال دسترسی به دانش را سریع‌تر می‌کنند، اما نه جای محیط آرام مطالعه را می‌گیرند و نه جای مشاورهٔ حضوری را. اگر کتابخانه‌ها خدمات دیجیتال و فیزیکی را ترکیب کنند، می‌توان بخشی از این تعارض را کاهش داد. کتابخانه‌ها می‌توانند همچنان دسترسی آزاد به پایگاه‌های اطلاعاتی، فضای مطالعه و کمک برای ارزیابی اعتبار منابع فراهم کنند.',
    'en':'Digital information makes knowledge more accessible, but it replaces neither quiet places to study nor personal advice. If libraries combine digital and physical services, part of the conflict can be eased. Libraries could continue to provide open access to databases, workspaces and help with assessing sources.'},
57:{'s01':'Ein Teilzeitstudium ist erst dann eine echte Alternative, wenn Prüfungen, Fristen und Veranstaltungen mit anderen Verpflichtungen vereinbar sind.',
    's03':'Hochschulen müssten ihre Studienmodelle auch bei veränderten Lebensumständen flexibel anpassbar machen.', 'k2':'müssten',
    'fa':'تحصیل پاره‌وقت تنها زمانی گزینه‌ای واقعی است که امتحان‌ها، مهلت‌ها و کلاس‌ها با مسئولیت‌های دیگر سازگار باشند. اگر جابه‌جایی میان شیوه‌های تحصیل آسان باشد و استانداردهای حداقلی یکسان بمانند، می‌توان بخشی از این تعارض را کاهش داد. دانشگاه‌ها باید مدل‌های تحصیلی را طوری انعطاف‌پذیر طراحی کنند که با تغییر شرایط زندگی هم قابل تنظیم باشند.',
    'en':'Part-time study is a genuine alternative only when exams, deadlines and classes are compatible with other responsibilities. If switching between study models is easy and minimum standards remain the same, part of the conflict can be eased. Universities would need to make their study models adaptable when students’ circumstances change.'},
58:{'s01':'Internate verbinden Unterricht und Alltag, doch derselbe enge Rahmen kann soziale Konflikte und Heimweh verstärken.',
    's03':'Eltern und Jugendliche sollten vor der Entscheidung prüfen, ob Betreuung, Privatsphäre und Rückzugsmöglichkeiten zu ihren Bedürfnissen passen.', 'k2':'sollten',
    'fa':'مدارس شبانه‌روزی آموزش و زندگی روزمره را به هم پیوند می‌دهند، اما همین محیط نزدیک ممکن است اختلاف‌های اجتماعی و دلتنگی برای خانه را تشدید کند. اگر مراقبت و همراهی حرفه‌ای باشد و تماس منظم با خانواده امکان‌پذیر بماند، می‌توان بخشی از این تعارض را کاهش داد. والدین و نوجوانان بهتر است پیش از تصمیم‌گیری بررسی کنند که نظارت، حریم خصوصی و فضای خلوت با نیازهایشان سازگار است یا نه.',
    'en':'Boarding schools combine classes and daily life, but that same close environment can intensify social conflicts and homesickness. If care is professional and regular contact with family remains possible, part of the conflict can be eased. Parents and young people should check whether supervision, privacy and opportunities to withdraw fit their needs before deciding.'},
60:{'s01':'Private Kontakte zwischen Lehrenden und Studierenden können Nähe schaffen, während Prüfungsbewertungen ein Machtgefälle aufrechterhalten.',
    's03':'Lehrende sollten während laufender Prüfungsverhältnisse offizielle Kommunikationskanäle bevorzugen und private Nachrichten klar abgrenzen.', 'k2':'sollten',
    'fa':'ارتباط خصوصی میان استادان و دانشجویان می‌تواند احساس نزدیکی ایجاد کند، درحالی‌که ارزیابی امتحان‌ها همچنان نابرابری قدرت را حفظ می‌کند. اگر از پلتفرم‌های حرفه‌ای یا حساب‌های کاملاً جداگانه استفاده شود، می‌توان بخشی از این تعارض را کاهش داد. استادان بهتر است تا زمانی که مسئول ارزیابی هستند، کانال‌های رسمی ارتباطی را ترجیح دهند و پیام‌های خصوصی را به‌وضوح از رابطهٔ آموزشی جدا کنند.',
    'en':'Private contacts between teachers and students can create closeness, while examination decisions maintain an imbalance of power. If professional platforms or clearly separate accounts are used, part of the conflict can be eased. Teachers should favour official communication channels while they still assess students and clearly separate private messages from teaching matters.'},
61:{'s01':'Fantasy kann in erfundenen Welten Fragen nach Macht, Vorurteilen und Verantwortung zeigen, ohne fertige Antworten vorzugeben.',
    's03':'Lernende könnten solche Konflikte mit historischen oder gegenwärtigen Beispielen vergleichen und die Grenzen dieser Vergleiche diskutieren.', 'k2':'könnten',
    'fa':'داستان‌های فانتزی می‌توانند در جهان‌های خیالی پرسش‌هایی دربارهٔ قدرت، پیش‌داوری و مسئولیت مطرح کنند، بی‌آنکه پاسخ آماده‌ای بدهند. اگر داستان‌ها در کلاس با پرسش‌ها، مقایسه‌ها و اطلاعات زمینه‌ای پیوند بخورند، می‌توان بخشی از این تعارض را کاهش داد. یادگیرندگان می‌توانند چنین تعارض‌هایی را با نمونه‌های تاریخی یا امروزی مقایسه کنند و دربارهٔ محدودیت‌های این مقایسه‌ها گفت‌وگو کنند.',
    'en':'Fantasy can explore questions of power, prejudice and responsibility in imaginary worlds without supplying ready-made answers. If stories are linked to questions, comparisons and background knowledge in class, part of the conflict can be eased. Learners could compare such conflicts with historical or present-day examples and discuss the limits of those comparisons.'},
62:{'s01':'Kulturförderung kann auch Angebote ermöglichen, die gesellschaftlich wertvoll sind, sich aber nicht allein durch Eintrittsgelder tragen.',
    's03':'Die Vergabe müsste öffentlich begründet werden, damit kleine und experimentelle Projekte faire Chancen haben.', 'k2':'müsste',
    'fa':'حمایت مالی از فرهنگ می‌تواند برنامه‌هایی را امکان‌پذیر کند که برای جامعه ارزشمندند اما تنها با درآمد بلیت تأمین مالی نمی‌شوند. اگر معیارهای روشن، هیئت‌های مستقل و بودجه‌های قابل‌پیگیری وجود داشته باشند، می‌توان بخشی از این تعارض را کاهش داد. تخصیص این بودجه‌ها باید به‌صورت عمومی توضیح داده شود تا پروژه‌های کوچک و آزمایشی نیز فرصت منصفانه داشته باشند.',
    'en':'Cultural funding can also make activities possible that benefit society but cannot support themselves through ticket sales alone. If clear criteria, independent committees and transparent budgets are in place, part of the conflict can be eased. Funding decisions would need to be publicly justified so that small and experimental projects have fair opportunities.'},
63:{'s01':'Bei einem Vertrag steht Genauigkeit im Vordergrund, während in einem Gedicht Rhythmus und Mehrdeutigkeit Teil der Bedeutung sein können.',
    's03':'Übersetzende müssten deshalb erläutern, welche Nuancen sie bewahren und welche sie zugunsten der Lesbarkeit verändern.', 'k2':'müssten',
    'fa':'در قرارداد، دقت محتوایی در اولویت است، درحالی‌که در شعر، آهنگ کلام و چندمعنایی می‌توانند بخشی از معنا باشند. اگر مترجمان بسته به نوع متن اولویت‌های متفاوتی تعیین کنند و تصمیم‌هایشان را شفاف سازند، می‌توان بخشی از این تعارض را کاهش داد. بنابراین مترجمان باید توضیح دهند کدام ظرافت‌ها را حفظ می‌کنند و کدام‌ها را برای روان‌بودن متن تغییر می‌دهند.',
    'en':'Accuracy takes priority in a contract, whereas rhythm and ambiguity may be part of the meaning of a poem. If translators set different priorities depending on text type and make their decisions transparent, part of the conflict can be eased. Translators would therefore need to explain which nuances they preserve and which they change for readability.'},
64:{'s01':'Sympathie erleichtert Fragen und Feedback, ist aber kein verlässliches Maß für fachlich guten Unterricht.',
    's03':'Lernende sollten Erklärungen nach Verständlichkeit und sachlicher Qualität beurteilen, nicht nur nach persönlicher Nähe.', 'k2':'sollten',
    'fa':'صمیمیت و دوست‌داشتنی‌بودن پرسیدن سؤال و دریافت بازخورد را آسان می‌کند، اما معیار مطمئنی برای کیفیت تخصصی تدریس نیست. اگر مدرسان مستقل از میزان نزدیکی شخصی، محترمانه و حرفه‌ای عمل کنند، می‌توان بخشی از این تعارض را کاهش داد. یادگیرندگان بهتر است توضیح‌ها را بر پایهٔ قابل‌فهم‌بودن و درستی محتوا ارزیابی کنند، نه فقط احساس نزدیکی شخصی.',
    'en':'Sympathy makes it easier to ask questions and receive feedback, but it is not a reliable measure of teaching quality. If teachers behave respectfully and professionally regardless of personal closeness, part of the conflict can be eased. Learners should judge explanations by clarity and factual quality, not only by personal closeness.'},
65:{'s01':'Regelmäßiges Vorlesen erweitert Wortschatz und Sprachgefühl, besonders wenn Kinder selbst über die Geschichte nachdenken.',
    's03':'Erwachsene könnten unbekannte Wörter aufgreifen und Kinder ermutigen, eigene Vermutungen über den weiteren Verlauf auszusprechen.', 'k2':'könnten',
    'fa':'بلندخوانی منظم واژگان و درک زبانی کودکان را گسترش می‌دهد، به‌ویژه وقتی خودشان دربارهٔ داستان فکر می‌کنند. اگر بلندخوانی گفت‌وگومحور باشد و کودکان سؤال بپرسند، تصاویر را توصیف کنند یا داستان را ادامه دهند، می‌توان بخشی از این تعارض را کاهش داد. بزرگسالان می‌توانند واژه‌های ناآشنا را توضیح دهند و کودکان را تشویق کنند حدس‌های خود را دربارهٔ ادامهٔ داستان بیان کنند.',
    'en':'Regular reading aloud expands children’s vocabulary and feel for language, especially when they think about the story themselves. If reading is interactive and children ask questions, describe pictures or continue stories, part of the conflict can be eased. Adults could explain unfamiliar words and encourage children to voice their own predictions about what happens next.'},
66:{'s01':'Eltern kennen die Bedürfnisse ihres Kindes, doch die Planung und Bewertung des Unterrichts bleiben Aufgaben der Lehrkräfte.',
    's03':'Schulen sollten Rückmeldungen ernst nehmen und fachliche Entscheidungen nachvollziehbar von individuellen Elternwünschen abgrenzen.', 'k2':'sollten',
    'fa':'والدین نیازهای فرزندشان را می‌شناسند، اما برنامه‌ریزی و ارزیابی آموزش همچنان وظیفهٔ معلمان است. اگر راه‌های ارتباطی روشن، جلسه‌های والدین و روندهای رسیدگی به شکایت وجود داشته باشد، می‌توان بخشی از این تعارض را کاهش داد. مدارس بهتر است بازخوردها را جدی بگیرند و تصمیم‌های تخصصی را با توضیح روشن از خواسته‌های شخصی والدین جدا کنند.',
    'en':'Parents know their child’s needs, but planning and assessing lessons remain the teachers’ responsibilities. If clear communication channels, parent meetings and complaint procedures exist, part of the conflict can be eased. Schools should take feedback seriously and clearly distinguish professional decisions from individual parental wishes.'},
67:{'s01':'Frühe Medienkompetenz beginnt nicht mit möglichst langer Bildschirmzeit, sondern mit einer bewussten gemeinsamen Nutzung.',
    's03':'Erwachsene müssten darauf achten, dass digitale Angebote Bewegung, Spiel und persönliche Begegnungen nicht verdrängen.', 'k2':'müssten',
    'fa':'سواد رسانه‌ای در سنین پایین با بیشترین زمانِ استفاده از صفحه‌نمایش شروع نمی‌شود، بلکه با استفادهٔ آگاهانه و مشترک شکل می‌گیرد. اگر استفاده از رسانه‌های دیجیتال کوتاه، همراهی‌شده و متناسب با سن باقی بماند، می‌توان بخشی از این تعارض را کاهش داد. بزرگسالان باید مراقب باشند فعالیت‌های دیجیتال جای حرکت، بازی و ارتباط‌های رو‌در‌رو را نگیرند.',
    'en':'Early media literacy does not begin with the longest possible screen time but with conscious shared use. If digital use remains brief, supervised and appropriate to the child’s age, part of the conflict can be eased. Adults would need to ensure that digital activities do not displace movement, play and face-to-face interaction.'},
68:{'s01':'Eltern zu unterstützen ist sinnvoll; eine staatliche Erlaubnispflicht würde jedoch tief in persönliche Freiheitsrechte eingreifen.',
    's03':'Kostenlose freiwillige Angebote könnten Wissen vermitteln, ohne Familien von einer Prüfung abhängig zu machen.', 'k2':'könnten',
    'fa':'حمایت از والدین سودمند است، اما الزام به گرفتن مجوز دولتی دخالتی عمیق در آزادی‌های فردی خواهد بود. اگر دوره‌های داوطلبانه یا آسان‌دسترس به‌رایگان ارائه شوند و در صورت نیاز حمایت هدفمند وجود داشته باشد، می‌توان بخشی از این تعارض را کاهش داد. برنامه‌های رایگان و اختیاری می‌توانند دانش لازم را منتقل کنند، بی‌آنکه خانواده‌ها را به گذراندن یک آزمون وابسته کنند.',
    'en':'Supporting parents is useful, but a requirement for a state permit would intrude deeply into personal freedoms. If voluntary or easily accessible courses are offered free of charge and targeted support is available where needed, part of the conflict can be eased. Free voluntary programmes could provide useful knowledge without making families dependent on passing an exam.'},
}

def main():
    assert sha(SRC.read_bytes())==SOURCE_SHA
    a=json.loads(SRC.read_text());b=copy.deepcopy(a)
    assert set(EDITS)==set(range(52,59))|set(range(60,69))
    ledger=[];invalid=0;reanchored=0;retained=0;added=0;retargeted=0
    for n,edit in EDITS.items():
        old=a['items'][n-1];new=b['items'][n-1]
        assert old['id']==new['id']==f'LES-PRES-{n:03d}'
        prior=old['reading']['sections'][3];post=new['reading']['sections'][3]
        assert prior['id']=='p04' and len(prior['sentences'])==3
        assert prior['sentences'][0]['text']=='Entscheidend ist deshalb die konkrete Ausgestaltung.'
        assert prior['sentences'][2]['text'].startswith('Statt nur zwischen Zustimmung und Ablehnung zu wählen')
        assert prior['sentences'][1]==post['sentences'][1]
        post['sentences'][0]['text']=edit['s01'];post['sentences'][2]['text']=edit['s03']
        post['text']=' '.join(s['text'] for s in post['sentences'])
        post['translations']={'fa':edit['fa'],'en':edit['en']}
        assert len(edit['fa'])>170 and len(edit['en'])>190,(n,len(edit['fa']),len(edit['en']))
        oStart=len(prior['sentences'][0]['text'])+1; nStart=len(post['sentences'][0]['text'])+1
        full=[];removed=[];kept=[]
        for occ in old['grammar']['full_text_occurrences']:
            if occ['section_id']!='p04':full.append(copy.deepcopy(occ));continue
            assert prior['text'][occ['start']:occ['end']]==occ['target_text']
            if occ['sentence_id']!='p04-s02':
                invalid+=1;removed.append({'id':occ['id'],'sentence_id':occ['sentence_id'],'target_text':occ['target_text'],'grammar_key':occ['grammar_key']});continue
            cc=copy.deepcopy(occ);rel=occ['start']-oStart
            assert rel>=0 and prior['sentences'][1]['text'][rel:rel+len(cc['target_text'])]==cc['target_text']
            cc['start']=nStart+rel;cc['end']=cc['start']+len(cc['target_text'])
            assert post['text'][cc['start']:cc['end']]==cc['target_text']
            retained+=1;reanchored+=int(cc['start']!=occ['start']);full.append(cc)
            kept.append({'id':cc['id'],'old_start':occ['start'],'new_start':cc['start']})
        marker=edit['k2']; s03=edit['s03'];assert s03.count(marker)==1,(n,marker)
        offset=len(post['sentences'][0]['text'])+1+len(post['sentences'][1]['text'])+1+s03.index(marker)
        ann={'id':f'ftg-r13-{n:03d}-p04-k2','grammar_key':'konjunktiv_ii','label_de':'Konjunktiv II: Möglichkeit oder vorsichtige Empfehlung',
             'section_id':'p04','sentence_id':'p04-s03','start':offset,'end':offset+len(marker),'target_text':marker,
             'explanation_de':f'Die Form „{marker}“ steht hier im Konjunktiv II und kennzeichnet eine denkbare Handlung oder vorsichtige Empfehlung, nicht eine feststehende Tatsache.',
             'explanation_fa':f'«{marker}» در این جمله ساخت Konjunktiv II است و یک امکان یا پیشنهاد سنجیده را بیان می‌کند، نه یک واقعیت قطعی.',
             'details':{'scope':'manual_scoped_r13_p04_s03','form':marker},'confidence':'high','annotation_source':'editorial_scoped_r13',
             'derivation_method':'manual_exact_form_attestation_not_full_native_grammar_engine'}
        assert post['text'][ann['start']:ann['end']]==marker and ann['id'] not in {z['id'] for z in full}
        full.append(ann);added+=1
        new['grammar']['full_text_occurrences']=full
        summ=new['grammar']['full_text_lens_summary'];summ['occurrences']=len(full);summ['counts']=dict(collections.Counter(z['grammar_key'] for z in full))
        summ['scope_note_de']='R13: Kontextmarker der geänderten p04-s01/s03 entfernt; Marker der unveränderten p04-s02 exakt verschoben; ein manuell geprüftes Konjunktiv-II-Beispiel ergänzt. Neun-Linsen-Generator nicht neu ausgeführt.'
        summ['scope_note_fa']='R13: نشانگرهای جمله‌های حذف‌شده کنار گذاشته، نشانگرهای جملهٔ میانیِ حفظ‌شده دقیقاً جابه‌جا و یک نمونهٔ دست‌بررسی‌شدهٔ Konjunktiv II اضافه شده است؛ موتور کامل اجرا نشده است.'
        ret=[]
        for cur in new['grammar']['curated_annotations']:
            if cur['section_id']=='p04' and cur['sentence_id']=='p04-s03':
                assert cur['id']=='g07' and cur['grammar_key']=='konjunktiv_ii'
                cur['target_text']=s03;cur['annotation_source']='editorial_retarget_r13';ret.append(cur['id']);retargeted+=1
        for cur in new['grammar']['curated_annotations']:
            sec=next(s for s in new['reading']['sections'] if s['id']==cur['section_id'])
            sent=next(s for s in sec['sentences'] if s['id']==cur['sentence_id'])
            assert cur['target_text'] in sent['text'],(n,cur['id'])
        new['reading']['word_count_de']=len(' '.join(sec['text'] for sec in new['reading']['sections']).split())
        new['quality']['content_hash']=sha(' '.join(sec['text'] for sec in new['reading']['sections']).encode())[:16]
        new['quality']['app_mapping_status']='r13_scoped_p04_candidate_preentry_only'
        ledger.append({'unit_id':new['id'],'title_de':new['title_de'],'source_grounded_sections':['p02','p03','p04-s02','p05'],
                       'before_p04':prior,'after_p04':post,'retired_context_anchors':removed,'middle_anchors_reanchored':kept,
                       'new_grammar':ann,'curated_g07_retargeted':ret,'parent_unit_sha256':sha(canon(old)),'candidate_unit_sha256':sha(canon(new))})
    changed=[n for n,(x,y) in enumerate(zip(a['items'],b['items']),1) if x!=y]
    assert changed==sorted(EDITS)
    assert a['items'][50]==b['items'][50] and a['items'][58]==b['items'][58]
    gr=[x for u in b['items'] for x in u['grammar']['full_text_occurrences']]
    fq=b['full_text_grammar_qa'];fq['occurrences']=len(gr);fq['counts']=dict(collections.Counter(x['grammar_key'] for x in gr));fq['offset_exact_matches']=len(gr)
    fq['result']='R13_SCOPED_GRAMMAR_EXACT_OFFSETS__NATIVE_9_LENS_NOT_RERUN__STAGE4_HOLD'
    fq['r13_scope']={'units':len(EDITS),'retired_old_anchors':invalid,'reanchored_middle':reanchored,'retained_middle':retained,'new_scoped_k2':added,'retargeted_curated':retargeted,'native_engine_rerun':False}
    wc=[u['reading']['word_count_de'] for u in b['items']]
    b['qa_summary']['word_count_de']={'min':min(wc),'mean':round(sum(wc)/len(wc),1),'max':max(wc)}
    b['qa_summary']['r13_scope']='16_SOURCE_GROUNDED_P04_TRILINGUAL_SECTIONS_052_058_AND_060_068__OTHERS_UNCHANGED'
    b['translation_qa']['r13_review_status']='SOURCE_BOUND_AI_SCOPED_REVIEW__NOT_INDEPENDENT_STAGE4'
    b['translation_qa']['result']='R13_16_P04_SECTIONS_REVIEWED_WITH_STAGE4_HOLD'
    b['content_version']='1.3.0-R13-CANDIDATE'
    b['status']='R13_16_P04_TRILINGUAL_SCOPED_GRAMMAR_CANDIDATE_STAGE4_6_7_HOLD'
    for x,y in zip(a['items'],b['items']):
        assert x['id']==y['id'] and x['questions']==y['questions'] and x['vocabulary']==y['vocabulary']
        for occ in y['grammar']['full_text_occurrences']:
            sec=next(s for s in y['reading']['sections'] if s['id']==occ['section_id'])
            assert sec['text'][occ['start']:occ['end']]==occ['target_text'],(y['id'],occ['id'])
    assert sum(x['reading']['sections'][3]['text'].startswith('Entscheidend ist deshalb die konkrete Ausgestaltung.') for x in b['items'])==0
    write(OUT,b)
    result={'schema':'lesen-r13-16-p04-editorial-grammar-ledger@1.0.0','date':'2026-11-07','source_r12_sha256':SOURCE_SHA,
            'candidate_r13_sha256':sha(OUT.read_bytes()),'candidate_bytes':OUT.stat().st_size,'changed_units':[f'LES-PRES-{n:03d}' for n in changed],
            'p04_sections_changed':16,'de_sentences_changed':32,'middle_source_sentences_preserved':16,'unchanged_units':52,
            'previous_accepted_units_preserved':['LES-PRES-051','LES-PRES-059'],
            'grammar_total_before':sum(len(u['grammar']['full_text_occurrences']) for u in a['items']),
            'grammar_total_after':len(gr),'old_context_invalidated':invalid,'original_middle_reanchored':reanchored,'original_middle_retained':retained,
            'new_scoped_k2':added,'curated_retargeted':retargeted,'remaining_original_generic_p04_starts':0,
            'semantic_stage4':'HOLD','native_nine_lens_rerun':False,'browser_stage6':'NOT_RUN','stage7':'NOT_RELEASED',
            'before_after':ledger}
    write(LEDGER,result)
    print(json.dumps({k:v for k,v in result.items() if k!='before_after'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()