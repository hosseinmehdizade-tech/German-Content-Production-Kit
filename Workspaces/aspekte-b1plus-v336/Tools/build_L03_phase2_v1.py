#!/usr/bin/env python3
"""L03 one-lesson data curation from SHA-pinned previous owner; no original-source rebuild.

Each S tuple = semantic distinction DE, FA, list of original example indices,
manual bilingual collocations. No automatic sense inference from Persian punctuation.
All new G4 content is provisional, with explicit fail-closed release markers.
"""
import hashlib,json,re,zipfile,collections,copy,os,html,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).parent
PARENT=ROOT/'Aspekte-B1plus-L02-PHASE3-FINAL-91-CARD-GATE-8-FORM-ATTESTATIONS-2-SENSES-NONIMPORT-20261108.zip'
OUTPUT=ROOT/'Aspekte-B1plus-L03-PHASE2-WHOLE-194-CARDS-EDITORIAL-NONIMPORT-20261108.zip'
PRE='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
SHA_PARENT='39caaa7bab3b32b9e220a9c39ac2854942a12e4735cd584d52fd8b695c86f5a3'

def S(de,fa,idx,coll=()):return {'sense_de':de,'sense_fa':fa,'indices':idx,'collocations':coll}
def C(de,fa):return (de,fa)
# The following meaning routes were authored with case-specific checking of EVERY listed existing example.
SPEC={
165:[S('sich ausruhen','استراحت‌کردن و آرام‌گرفتن',[0],[C('nach der Arbeit ruhen','پس از کار استراحت‌کردن')]),S('vorübergehend stillstehen','موقتاً متوقف‌بودن',[1],[C('während der Reparatur ruhen','در زمان تعمیرات موقتاً متوقف‌بودن')]),S('begraben sein (gehoben)','آرمیدن در گور (ادبی)',[2],[C('auf einem Friedhof ruhen','در گورستان آرمیدن')]),S('auf etwas lasten oder gestützt sein','بر چیزی استوار یا متکی بودن',[3],[C('auf jemandes Schultern ruhen','بر دوش کسی بودن')])],
168:[S('eine Handlung oder gute Tat','عمل، کار یا اقدام',[0],[C('eine gute Tat vollbringen','کار نیکی انجام‌دادن')]),S('eine Straftat oder Tat im Polizeikontext','عمل مجرمانه، جرم',[1],[C('eine Tat aufklären','جرمی را روشن‌کردن')])],
177:[S('mit Pfeffer gewürzt','فلفل‌زده، دارای فلفل زیاد',[0],[C('stark gepfeffertes Essen','غذای پرفلفل')]),S('umgangssprachlich: sehr teuer','محاوره‌ای: بسیار گران',[1],[C('ein gepfefferter Preis','قیمتی بسیار بالا')]),S('scharf, direkt oder verletzend','تند و کوبنده (سخن یا پاسخ)',[2,3],[C('eine gepfefferte Antwort','پاسخی تند و کوبنده')])],
179:[S('geschmacklich bitter/herb','در مزه: گس یا اندکی تلخ',[0],[C('herber Geschmack','مزه‌ای گس و تلخ')]),S('übertragen: schmerzlich oder hart','در معنای مجازی: سخت و تلخ',[1],[C('ein herber Rückschlag','ضربه‌ای سخت')])],
180:[S('besonders wohlschmeckend','بسیار خوشمزه',[0,1],[C('köstliches Essen','غذای بسیار لذیذ')]),S('humorvoll und amüsant','بامزه و سرگرم‌کننده',[2,3],[C('eine köstliche Geschichte','داستانی بسیار بامزه')])],
182:[S('leicht sauer im Geschmack','اندکی ترش از نظر مزه',[0,1],[C('säuerlicher Geschmack','مزه‌ای کمی ترش')]),S('missmutig im Gesichtsausdruck','ناراضی یا تلخ از نظر حالت چهره',[2,3],[C('ein säuerliches Lächeln','لبخندی تلخ و ناخشنود')])],
183:[S('unangenehm süß im Geruch/Geschmack','بوی یا طعم شیرینِ زننده',[0,1],[C('ein süßlicher Geruch','بوی شیرین و زننده')]),S('übertrieben gefühlsbetont oder aufgesetzt','احساساتی یا مهربانانهٔ تصنعی',[2,3],[C('süßliche Freundlichkeit','مهربانی تصنعی')])],
190:[S('klein oder sehr fein gemahlen','ریز یا بسیار نرم',[0],[C('fein gemahlene Mandeln','بادام نرم‌آسیاب‌شده')]),S('zart im Geschmack','لطیف و ملایم در طعم',[1],[C('feiner Geschmack','مزه‌ای ظریف و ملایم')]),S('feinfühlig oder differenziert','نکته‌سنج و حساس',[2],[C('ein feines Gespür für etwas','درک ظریفی از چیزی داشتن')])],
191:[S('Behälter für Flüssigkeiten oder Gegenstände','ظرف یا محفظه',[0],[C('ein sauberes Gefäß','ظرفی تمیز')]),S('in der Medizin: Blutgefäß','در پزشکی: رگ',[1],[C('ein verletztes Gefäß','رگ آسیب‌دیده')])],
196:[S('transitiv: jemanden oder etwas gesund machen','درمان‌کردنِ کسی یا چیزی',[0],[C('eine Wunde heilen','زخمی را التیام‌دادن')]),S('intransitiv: gesund werden','خوب‌شدن و التیام‌یافتن',[1],[C('langsam heilen','به‌آرامی التیام‌یافتن')])],
203:[S('etwas besonders Schmackhaftes (meist Plural)','خوراکی لذیذ (اغلب جمع)',[0,1],[C('regionale Köstlichkeiten','خوشمزه‌های محلی')]),S('abstrakte Qualität: köstlicher Geschmack','خوشمزگی و کیفیت بسیار لذیذ',[2],[C('die Köstlichkeit eines Gerichts','خوشمزگی یک غذا')])],
205:[S('auf den Menschen bezogen','مربوط به انسان؛ انسانی',[0],[C('ein menschlicher Fehler','خطای انسانی')]),S('warmherzig und mitfühlend','انسان‌دوستانه و همدلانه',[1],[C('menschlich reagieren','انسان‌دوستانه واکنش نشان‌دادن')])],
210:[S('jemand ist an der Reihe','نوبت کسی‌بودن',[0],[C('an der Reihe sein','نوبتِ کسی بودن')]),S('eine Anzahl oder Folge','مجموعه یا سلسله‌ای از چیزها',[1],[C('eine ganze Reihe von Möglichkeiten','مجموعهٔ بزرگی از گزینه‌ها')]),S('räumlich: in einer Linie','در یک ردیف یا خط (مکانی)',[2],[C('in einer Reihe sitzen','در یک ردیف نشستن')])],
218:[S('ein Geheimnis oder Information preisgeben','فاش یا لو کردن راز و اطلاعات',[0,1],[C('jemandem ein Geheimnis verraten','رازی را برای کسی فاش‌کردن')]),S('jemanden oder dessen Vertrauen verraten','خیانت به کسی یا اعتماد او',[2,3],[C('einen Freund verraten','به دوستی خیانت‌کردن')])],
219:[S('etwas weiter verbessern/entwickeln','بیشتر بهبوددادن و توسعه‌دادن چیزی',[0],[C('ein Produkt weiterentwickeln','محصولی را توسعه‌دادن')]),S('sich persönlich oder beruflich weiterentwickeln','شخصاً یا حرفه‌ای پیشرفت‌کردن',[1,2],[C('sich beruflich weiterentwickeln','از نظر شغلی پیشرفت‌کردن')])],
224:[S('etwas als Geschenk hergeben','چیزی را هدیه یا رایگان بخشیدن',[0,1],[C('etwas an Freunde verschenken','چیزی را به دوستان هدیه‌دادن')]),S('eine Chance oder einen Sieg unnötig verlieren','فرصتی یا پیروزی را بیهوده ازدست‌دادن',[2,3],[C('den Sieg verschenken','پیروزی را بیهوده ازدست‌دادن')])],
239:[S('für eine Ware, Dienstleistung oder Idee werben','برای کالا یا ایده تبلیغ‌کردن',[0],[C('für ein Produkt werben','برای محصولی تبلیغ‌کردن')]),S('um jemanden werben: gewinnen wollen','برای جلب یا جذب کسی تلاش‌کردن',[1],[C('um neue Mitglieder werben','برای جذب اعضای جدید تلاش‌کردن')])],
241:[S('Flugzeug: auf der Erde aufsetzen','فرودآمدن هواپیما',[0],[C('pünktlich landen','به‌موقع فرودآمدن')]),S('übertragen: irgendwo oder in einer Lage enden','سر از جایی درآوردن',[1],[C('im Krankenhaus landen','سر از بیمارستان درآوردن')])],
242:[S('Maßeinheit: 1000 Kilogramm','تُن: واحد وزن برابر با هزار کیلوگرم',[0],[C('mehrere Tonnen Lebensmittel','چندین تن مواد غذایی')]),S('großer Abfallbehälter','سطل بزرگ زباله',[1],[C('die blaue Tonne','سطل آبی زباله')])],
253:[S('trennbar: mit jemandem/etwas umgehen','با فرد یا چیزی رفتار یا برخوردکردن',[0,1],[C('mit Lebensmitteln sorgfältig umgehen','با مواد غذایی با دقت برخوردکردن')]),S('trennbar: ein Gerücht geht um','رواج یا پخش‌شدن خبر یا شایعه',[2,4],[]),S('untrennbar: eine Regel/ein Hindernis umgehen','دورزدنِ مقررات یا مانع',[3,5],[C('Vorschriften umgehen','مقررات را دورزدن')])],
259:[S('kräftig und aus vollem Herzen lachen','از ته دل یا با تمام وجود خندیدن',[0],[C('herzhaft lachen','از ته دل خندیدن')]),S('Speisen: würzig, nicht süß','خوراکی شور یا پرمزه، نه شیرین',[1],[C('ein herzhaftes Frühstück','صبحانه‌ای شور و پرمزه')])],
263:[S('zu etwas motivieren oder zum Denken bringen','ترغیب یا به فکر واداشتن',[0],[C('zum Nachdenken anregen','به فکر واداشتن')]),S('einen Vorschlag machen oder eine Debatte initiieren','پیشنهاددادن یا بحثی را آغازکردن',[1],[C('eine Diskussion anregen','بحثی را پیشنهاد و آغازکردن')])],
270:[S('übertragene Ebene: Betrachtungsaspekt','سطح یا جنبهٔ بررسی (مجازی)',[0,1],[C('auf körperlicher Ebene','در سطح جسمی')]),S('geografisch: flaches Land','دشت یا زمین هموار',[2],[C('eine weite Ebene','دشتی پهناور')])],
274:[S('in einen bestimmten Zustand geraten','دچار وضعیت یا شرایطی شدن',[0,1],[C('unter Druck geraten','تحت فشار قرارگرفتن')]),S('bei einer Herstellung: gut oder schlecht ausfallen','خوب یا بد از آب درآمدن',[2],[C('gut geraten','خوب از آب درآمدن')])],
280:[S('Zusammenstellung konkreter Bestandteile','ترکیب چند جزء یا عنصر',[0,1],[C('eine Kombination von Farben','ترکیب رنگ‌ها')]),S('Zusammenführung von Hinweisen/Gedanken','ترکیب و پیوندزدن سرنخ‌ها و اطلاعات',[2,3],[C('durch geschickte Kombination','با ترکیب هوشمندانه')])],
286:[S('eine Methode oder Technik ausüben','به‌کاربستنِ شیوه یا تمرینی',[0],[C('Yoga praktizieren','یوگا تمرین‌کردن')]),S('einen medizinischen Beruf ausüben','طبابت یا کار حرفه‌ای پزشکی‌کردن',[1],[C('als Arzt praktizieren','به‌عنوان پزشک طبابت‌کردن')])],
291:[S('trennbar: in eine andere Form oder einen Zustand übergehen','به وضعیت یا شکل دیگر تبدیل‌شدن',[0,1],[C('in Lachen übergehen','به خنده تبدیل‌شدن')]),S('untrennbar: jemanden oder etwas nicht beachten','کسی یا چیزی را نادیده‌گرفتن',[2],[C('Einwände übergehen','اعتراض‌ها را نادیده‌گرفتن')])],
293:[S('eine Wirkung haben','اثرکردن یا تأثیر داشتن',[0],[C('gegen Schmerzen wirken','برای درد مؤثربودن')]),S('einen Eindruck machen','به نظررسیدن؛ جلوه‌کردن',[1],[C('müde wirken','خسته به‌نظررسیدن')])],
296:[S('mit einer Aufgabe oder Tätigkeit beschäftigt sein','سرگرم یا مشغول کاری بودن',[0,1],[C('mit einer Aufgabe beschäftigt sein','مشغول انجام کاری بودن')]),S('bei einer Firma beschäftigt sein','در شرکت یا سازمانی استخدام و مشغول به کار بودن',[2,3],[C('bei einer Bank beschäftigt sein','در بانکی شاغل بودن')])],
305:[S('technische Neuerung, Erfindung','اختراع واقعی یا دستاورد نو',[0],[C('eine bedeutende Erfindung','اختراعی مهم')]),S('ausgedachte Geschichte, Unwahrheit','داستان یا ادعای ساختگی',[1],[C('reine Erfindung','کاملاً ساختگی')])],
310:[S('Einstellung oder Position verändern','تنظیم یا جابه‌جاکردن',[0,1],[C('die Höhe des Stuhls verstellen','ارتفاع صندلی را تنظیم‌کردن')]),S('einen Weg oder Zugang blockieren','مسدودکردن مسیر یا دسترسی',[2],[C('den Zugang verstellen','راه دسترسی را بستن')])],
312:[S('Rat und Empfehlung','توصیه و پیشنهاد',[0,1],[C('eine klare Empfehlung geben','توصیهٔ روشنی ارائه‌دادن')]),S('schriftliche Empfehlung/Referenz','توصیه‌نامهٔ مکتوب',[2,3],[C('eine schriftliche Empfehlung','توصیه‌نامهٔ کتبی')])],
315:[S('Methode oder Hilfsmittel','روش، ابزار یا وسیله',[0],[C('ein wirksames Mittel gegen etwas','راهکاری مؤثر علیه چیزی')]),S('Geldmittel oder Budget','پول، بودجه یا منابع مالی',[1],[C('finanzielle Mittel','منابع مالی')]),S('Medikament oder Wirkstoff','دارو یا مادهٔ مؤثر',[2],[C('ein Mittel gegen Beschwerden','دارویی برای کاهش علائم')])],
323:[S('Beginn eines Projekts oder Zeitraums','شروع پروژه یا دوره',[0],[C('der Start ins Semester','شروع ترم')]),S('Abheben eines Flugzeugs','بلندشدن هواپیما',[1,2],[C('der Start eines Flugzeugs','برخاستن هواپیما')])],
324:[S('wirtschaftlicher Absatz: verkaufte Menge','میزان فروشِ محصول',[0],[C('steigender Absatz','افزایش میزان فروش')]),S('Abschnitt eines Textes','بند متن',[1],[C('ein Absatz im Text','بندی در متن')]),S('Teil des Schuhs: Ferse','پاشنهٔ کفش',[2],[C('ein hoher Absatz','پاشنهٔ بلند')]),S('Treppenabsatz','پاگردِ راه‌پله',[3],[C('auf dem Treppenabsatz','روی پاگرد')])],
328:[S('aus einem Unternehmen/Wettbewerb ausscheiden','از شرکت بیرون‌آمدن یا از مسابقه حذف‌شدن (لازم)',[0,1],[C('im Halbfinale ausscheiden','در نیمه‌نهایی حذف‌شدن')]),S('Stoffe aus dem Körper ausscheiden','موادی را از بدن دفع‌کردن (متعدی)',[2],[C('Stoffe ausscheiden','موادی را دفع‌کردن')])],
330:[S('Marktplatz für Wertpapiere','بورس و بازار سهام',[0,1],[C('an der Börse notiert sein','در بورس پذیرفته و ثبت‌شده بودن')]),S('kleiner Geldbeutel (weniger üblich)','کیف پول کوچک (کاربرد محدود)',[2],[C('eine kleine Börse','کیف پول کوچک')])],
334:[S('kaufen oder als Besitz erlangen','خریدن یا به تملک درآوردن',[0],[C('ein Haus erwerben','خانه‌ای خریدن')]),S('Wissen, Fähigkeiten erlangen','دانش یا مهارتی کسب‌کردن',[1],[C('Kenntnisse erwerben','دانش کسب‌کردن')])],
343:[S('Handelsname oder Marke eines Produkts','برند یا نشان تجاری',[0,1],[C('eine bekannte Marke','برندی شناخته‌شده')]),S('Briefmarke','تمبر پستی',[2],[C('eine Marke auf einen Brief kleben','تمبر روی نامه چسباندن')])],
348:[S('aktueller Zustand oder Fortschrittsstand','وضعیت یا سطح پیشرفت',[0],[C('auf dem neuesten Stand sein','به‌روز بودن')]),S('Verkaufsstand auf einem Markt','غرفه یا دکهٔ فروش',[1,2],[C('an einem Stand verkaufen','در غرفه‌ای فروختن')]),S('gesellschaftlicher Stand, Schicht (historisch)','طبقهٔ اجتماعی (معمولاً تاریخی)',[3],[C('einem gesellschaftlichen Stand angehören','به طبقهٔ اجتماعی خاصی تعلق داشتن')])],
353:[S('vorausschauend und klug handeln','دوراندیش و آینده‌نگر بودن',[0,1],[C('weitsichtig handeln','دوراندیشانه عمل‌کردن')]),S('Hyperopie: in der Nähe schlecht sehen','دوربین‌بودن از نظر چشم',[2],[C('weitsichtig sein','دوربینی داشتن')])],
356:[S('jemandem Mut oder Trost zusprechen','به کسی دلگرمی یا تسلی‌دادن',[0],[C('jemandem Mut zusprechen','به کسی دلگرمی‌دادن')]),S('gerichtlich etwas zuerkennen','بر اساس حکم چیزی به کسی اعطا کردن',[1],[C('jemandem eine Entschädigung zusprechen','برای کسی غرامت تعیین‌کردن')])],
357:[S('positive Resonanz, Beliebtheit','استقبال یا محبوبیت',[0],[C('großen Zuspruch finden','با استقبال زیاد روبه‌روشدن')]),S('Ermutigung oder Unterstützung','دلگرمی و حمایت',[1],[C('jemandem Zuspruch geben','به کسی دلگرمی‌دادن')])],
}
# ORIGINAL example indices for the existing word-net cards. No model guessed mapping.
EXISTING={167:[0,0,1],185:[0,1],230:[0,0],232:[0,0],287:[0,0],295:[0,0],303:[0,0],304:[1,0],307:[0,0],309:[0,0],326:[0,2,3],338:[0,0],344:[0,0]}
# Only add pairs for unattested senses that have distinctive pedagogical value.
ADDED_EXAMPLES={
 210:[('Die Kinder sitzen in einer Reihe.','بچه‌ها در یک ردیف نشسته‌اند.')],
 270:[('Die Ebene erstreckt sich bis zum Horizont.','این دشت تا افق امتداد دارد.')],
 348:[('Im Mittelalter spielte der gesellschaftliche Stand eine wichtige Rolle.','در قرون وسطی، طبقهٔ اجتماعی نقش مهمی داشت.')],
 351:[('Die Behörde verfügte die Schließung des Betriebs.','آن اداره دستور تعطیلی واحد را صادر کرد.')],
}
# Form scoped evidence: Duden source directly inspected; do not infer FULL card signoff.
ATTEST={
165:('ruhen – ruht – ruhte – hat geruht',['https://www.duden.de/rechtschreibung/ruhen']),
218:('verraten – verrät – verriet – hat verraten',['https://www.duden.de/rechtschreibung/verraten']),
224:('verschenken – verschenkt – verschenkte – hat verschenkt',['https://www.duden.de/rechtschreibung/verschenken']),
274:('geraten – gerät – geriet – ist geraten',['https://www.duden.de/rechtschreibung/geraten_gelingen_hingelangen']),
291:('trennbar: geht über – ging über – ist übergegangen (in + Akk.) | untrennbar: übergeht – überging – hat übergangen (jemanden/etwas)', ['https://www.duden.de/rechtschreibung/uebergehen_uebergegangen','https://www.duden.de/rechtschreibung/uebergehen_uebergangen']),
328:('ausscheiden: scheidet aus – schied aus – ist ausgeschieden (intransitiv); hat ausgeschieden (transitiv)', ['https://www.duden.de/rechtschreibung/ausscheiden']),
351:('verfügen – verfügt – verfügte – hat verfügt; über + Akk. / etwas verfügen (amtlich)', ['https://www.duden.de/rechtschreibung/verfuegen']),
353:('weitsichtig – weitsichtiger – am weitsichtigsten', ['https://www.duden.de/rechtschreibung/weitsichtig']),
356:('zusprechen – spricht zu – sprach zu – hat zugesprochen; jdm. Mut/etw. zusprechen',['https://www.duden.de/rechtschreibung/zusprechen']),
}
PHRASE_ORIGINAL={258:'feste Redewendung / Sprichwort: „Lachen ist die beste Medizin.“',301:'feste umgangssprachliche Äußerung: „Bloß kein Stress!“',321:'Satzmuster mit Nebensatz: „Es ist ganz natürlich, dass …“'}

def examples(c):return (c['back'].get('existing_examples_de_fa_pending_qa') or [])+(c['back'].get('additional_examples_de_fa_pending_qa') or [])
def count(cards):
 l=[c for c in cards if c['lesson']=='L03'];net=[c for c in l if c['back'].get('semantic_network_sense_anchored_pending_qa')]
 return dict(cards=len(l),examples=sum(len(examples(c)) for c in l),network_cards=len(net),sense_blocks=sum(len(c['back']['semantic_network_sense_anchored_pending_qa']) for c in net),links=sum(e.get('sense_id') is not None for c in l for e in examples(c)),morphology=sum(bool(c['front'].get('morphology_independently_validated')) for c in l),holds=sum(bool(c.get('curated_HOLD_content_disposition_exists')) for c in l))

def build():
 assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==SHA_PARENT,'WRONG PARENT'
 with zipfile.ZipFile(PARENT) as z:
  assert z.testzip() is None
  manifest=dict(l.strip().split('  ',1)[::-1] for l in z.read('SHA256SUMS.txt').decode().splitlines() if l.strip())
  assert len(manifest)==len(z.namelist())-1
  assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in manifest.items())
  oldparts={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
 current=[json.loads(s) for s in oldparts[PRE].splitlines()]
 pre=copy.deepcopy(current)
 original_map=next(n for n in oldparts if 'SOURCE-MAP' in n and n.endswith('.tsv') and n.startswith('G2-'))
 lesson={c['source_ordinal']:c for c in current if c['lesson']=='L03'}
 assert len(lesson)==194 and set(SPEC).issubset(lesson) and set(EXISTING).issubset(lesson)
 print('Original source map',original_map)
 original_cnt=count(pre)
 ledger=[];per_card=[];altered=set();links_added=0;meaning_nodes_added=0;collocations_added=0;new_pairs=0;status_fixes=0
 for ord,c in lesson.items():
  orig=copy.deepcopy(c);f=c['front'];b=c['back'];e=examples(c)
  # Explicit provisional status for missing QA metadata, not approval.
  for x in e:
   if not x.get('status'):
    x['status']='PENDING_INDEPENDENT_DE_FA_SEMANTIC_QA'
    x['status_origin_L03_phase2']='STRUCTURAL_MISSING_STATUS_FIXED_NOT_APPROVED'
    status_fixes+=1
  if ord in ADDED_EXAMPLES:
   for de,fa in ADDED_EXAMPLES[ord]:
    assert de not in [x['de'] for x in e]
    b['additional_examples_de_fa_pending_qa'].append({'de':de,'fa':fa,'status':'PENDING_INDEPENDENT_DE_FA_SEMANTIC_QA','provenance':'L03_PHASE2_EDITORIAL_ORIGINAL_BILINGUAL_EXAMPLE_NOT_LEXICON_QUOTE'})
    new_pairs+=1
  e=examples(c)
  if ord in EXISTING:
   nets=b['semantic_network_sense_anchored_pending_qa'];routes=EXISTING[ord]
   assert len(routes)==len(e),(ord,'route len mismatch',len(routes),len(e))
   for x,idx in zip(e,routes):
    assert idx<len(nets)
    sid=nets[idx]['sense_id']
    if x.get('sense_id') is None: x['sense_id']=sid;links_added+=1
    else: assert x['sense_id']==sid,(ord,'conflicting preexisting route')
  if ord in SPEC:
   assert not b.get('semantic_network_sense_anchored_pending_qa'),(ord,'existing network must not overwrite')
   entries=SPEC[ord]
   mapped=[i for s in entries for i in s['indices']]
   assert sorted(mapped)==list(range(len(e))),(ord,'indices mismatch',sorted(mapped),len(e))
   nets=[]
   for i,s in enumerate(entries):
    sid=f"{c['preview_card_id']}:L03P2:S{i+1}"
    combos=[{'de':de,'fa':fa,'status':'PENDING_G4_DE_FA_COLLOCATION_QA','source':'L03_PHASE2_CASE_BY_CASE_EDITORIAL'} for de,fa in s['collocations']]
    # Phrase examples are NOT source of collocations: distinctive short lexical pairs only.
    nets.append({'sense_id':sid,'sense_de':s['sense_de'],'sense_fa':s['sense_fa'],
      'Synonyme':[],'Antonyme':[],'Wortfamilie':[],'Verwandte_Woerter_KEINE_Synonyme':[],
      'Kombinationen_DE_FA':combos,'Feste_Wendungen_DE_FA':[],'Satzmuster_DE_FA':([{'de':'Ein Gerücht geht um.','fa':'شایعه‌ای پخش شده است.','source':'L03_PHASE2_SENTENCE_PATTERN_NOT_KOMBINATION','status':'PENDING_G4_INDEPENDENT_DE_FA_QA'}] if ord==253 and i==1 else []),
      'usage_distinction_de':'Bedeutungsbezogene DE–FA-Bindung; Beispiele einzeln geprüft, keine automatische Teilung aufgrund persischer Semikolons.',
      'dictionary_evidence_urls':ATTEST[ord][1] if ord in ATTEST else [],
      'status':'PENDING_INDEPENDENT_G4_SEMANTIC_QA',
      'source':'L03_PHASE2_CASE_BY_CASE_EDITORIAL_WITH_REAL_EXAMPLE_ROUTES'})
    for j in s['indices']:
     assert 'sense_id' not in e[j],(ord,'unexpected preexisting link')
     e[j]['sense_id']=sid;links_added+=1
    meaning_nodes_added+=1;collocations_added+=len(combos)
   b['semantic_network_sense_anchored_pending_qa']=nets
  if ord in PHRASE_ORIGINAL:
   b['L03_phase2_card_classification']={'type':'FULL_PHRASE_OR_SENTENCE_PATTERN','front_label':PHRASE_ORIGINAL[ord], 'keep_existing_one_card':True,'status':'EDITORIAL_CLASSIFIED_NOT_FULL_G4_QA'}
  if ord in ATTEST:
   assert not f['morphology_independently_validated'],(ord,'already attested')
   f['display_de_provisional']=ATTEST[ord][0]
   f['morphology_independently_validated']=True
   f['morphology_origin']='DUDEN_SCOPED_LEXICOGRAPHIC_FORM_CHECK_L03_PHASE2_NOT_FULL_CARD_RELEASE'
   f['morphology_lexicographic_check_scope']='SPECIFIC_FORM_AND_CONSTRUCTION_ONLY_FULL_G4_DE_FA_QA_PENDING'
   f['lexicographic_evidence_urls']=ATTEST[ord][1]
  # case-by-case signoff of curated old HOLD is NOT conducted by script; preserve all original flags.
  assert c['curated_HOLD_content_disposition_exists']==orig['curated_HOLD_content_disposition_exists']
  assert c['back'].get('meanings_fa_provisional')==orig['back'].get('meanings_fa_provisional')
  assert c['linked_original_source_ordinals']==orig['linked_original_source_ordinals']
  assert c.get('import_ready') is False and c.get('formal_release_approved') is False
  changes={}
  for section in ('front','back'):
   for key in sorted(set(orig[section])|set(c[section])):
    if orig[section].get(key)!=c[section].get(key):changes[section+'.'+key]={'before':orig[section].get(key),'after':c[section].get(key)}
  if changes:
   altered.add(ord)
   ledger.append({'source_ordinal':ord,'card_id':c['preview_card_id'],'headword':f['base_headword_de'],'changed_fields':changes})
  per_card.append({'source_ordinal':ord,'id':c['preview_card_id'],'lemma':f['base_headword_de'],
   'editorial_disposition':'CONTENT_UPDATED' if changes else 'STRUCTURAL_SCREENED_NO_CONTENT_CHANGE',
   'field_change_count':len(changes),
   'G2_form_status':'SCOPE_ATTESTED' if f.get('morphology_independently_validated') else 'NOT_INDEPENDENTLY_ATTESTED',
   'example_pairs':len(e),'all_examples_explicit_pending_or_scoped':all(bool(x.get('status')) for x in e),
   'sense_blocks':len(b.get('semantic_network_sense_anchored_pending_qa') or []),
   'missing_sense_routes':sum('sense_id' not in x for x in e) if b.get('semantic_network_sense_anchored_pending_qa') else None,
   'curated_HOLD_preserved':bool(c.get('curated_HOLD_content_disposition_exists')),
   'formal_release_approved':False,'import_ready':False,
   'next_required':'INDEPENDENT_FULL_G4_DE_FA_AND_REAL_APP_RUNTIME_IN_PHASE3'})
 assert len(per_card)==194
 assert all(a==b for a,b in zip(pre,current) if a['lesson']!='L03')
 assert len(current)==1571
 assert all(a['preview_card_id']==b['preview_card_id'] for a,b in zip(pre,current))
 assert all(a['linked_original_source_ordinals']==b['linked_original_source_ordinals'] for a,b in zip(pre,current))
 updated=count(current)
 report={'schema':'aspekte-b1plus-L03-phase2-whole-lesson-content-report@1','date':'2026-11-08','lesson':'L03','status':'ALL_194_CARDS_EDITORIAL_STRUCTURAL_SCREEN_AND_TARGETED_CONTENT_REVISIONS_NONIMPORT',
   'parent_sha256':SHA_PARENT,'cards_reviewed_via_structural_decision_queue':194,'cards_with_actual_edits':len(altered), 'cards_structurally_screened_no_edits':194-len(altered),
   'source_rows_lesson':195,'card_views_lesson':194, 'pre':original_cnt,'after':updated,'example_pairs_added':new_pairs,'examples_without_QA_status_fixed_to_explicit_pending':status_fixes,
   'examples_routed_to_specific_senses_new':links_added,'existing_wordnets_routed':len(EXISTING),'new_wordnet_cards':len(SPEC),'new_sense_blocks':meaning_nodes_added,
   'new_sense_bound_bilingual_collocations':collocations_added,'new_external_Duden_scoped_form_attestations':len(ATTEST),
   'morphology_attested_ordinals':list(ATTEST),'old_curated_HOLDs_preserved':original_cnt['holds'],
   'original_1548_row_source_map_byte_identical':True,'other_lessons_cards_unchanged':True,
   'semantic_review_scope':'TARGETED_SENSE_AND_EXAMPLE_EDITORIAL_JUDGMENT_ONLY_NO_FULL_INDEPENDENT_LANGUAGE_SIGNOFF',
   'hard_release_blockers':['Full DE/FA card signoff missing','Real app import/render not executed','Remaining G2 forms without scoped evidence','Existing curated HOLDs not adjudicated'],
   'import_ready':False,'formal_release_approved':False}
 newparts={**oldparts}
 newparts[PRE]=(''.join(json.dumps(c,ensure_ascii=False,sort_keys=True)+'\n' for c in current)).encode('utf8')
 report_file='Lessons/L03/L03-PHASE2-194-CARDS-CONTENT-REPORT.json'
 ledger_file='Lessons/L03/L03-PHASE2-BEFORE-AFTER-EDITS.json'
 decisions_file='Lessons/L03/L03-PHASE2-194-CARD-DISPOSITIONS.jsonl'
 newparts[report_file]=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode()
 newparts[ledger_file]=(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n').encode()
 newparts[decisions_file]=(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in per_card)).encode()
 # QA-only static HTML that groups examples under their corresponding meaning.
 CSS="""body{font:15px system-ui, sans-serif;background:#f4f7fa;color:#193044;max-width:1120px;margin:20px auto;padding:10px}h1{font-size:24px}.meta{color:#8f3a36}article{background:#fff;border:1px solid #d8e1e8;border-radius:13px;padding:20px;margin:16px 0}.two{display:grid;grid-template-columns:30% 68%;gap:2%}.s{padding:10px;border-top:1px solid #cbd5df}h2{font-size:18px}.de{font-weight:600}.fa{direction:rtl;text-align:right;color:#3c4c63}.unmapped{background:#fff0d8;padding:8px}@media(max-width:720px){.two{display:block}}"""
 body=[]
 for c in current:
  if c['lesson']!='L03':continue
  ex=examples(c);nets=c['back'].get('semantic_network_sense_anchored_pending_qa') or []
  b=[]
  if nets:
   for net in nets:
    attached=[x for x in ex if x.get('sense_id')==net['sense_id']]
    b.append('<section class="s"><h3>'+html.escape(net['sense_de'])+'</h3><p class="fa">'+html.escape(net['sense_fa'])+'</p>')
    for x in attached:b.append('<p class="de">'+html.escape(x['de'])+'</p><p class="fa">'+html.escape(x['fa'])+'</p>')
    if net.get('Kombinationen_DE_FA'):
     b.append('<h4>Kombinationen</h4>')
     for k in net['Kombinationen_DE_FA']:
      b.append('<p class="de">'+html.escape(k['de'])+'</p><p class="fa">'+html.escape(k['fa'])+'</p>')
    b.append('</section>')
   unmatched=[x for x in ex if not x.get('sense_id')]
   if unmatched:
    b.append('<section class="unmapped">Nicht zugeordnet — QA HOLD')
    for x in unmatched:b.append('<p>'+html.escape(x['de'])+'<span class="fa">'+html.escape(x['fa'])+'</span></p>')
    b.append('</section>')
  else:
   for x in ex:b.append('<p class="de">'+html.escape(x['de'])+'</p><p class="fa">'+html.escape(x['fa'])+'</p>')
  body.append('<article><div class="two"><div><h2>'+html.escape(c['front']['base_headword_de'])+'</h2><p>'+html.escape(c['front']['display_de_provisional'])+'</p><small>#'+str(c['source_ordinal'])+'</small></div><div><p class="fa">'+html.escape(c['back'].get('meanings_fa_provisional',''))+'</p>'+''.join(b)+'</div></div></article>')
 htmlout='<!doctype html><html lang="de"><meta charset="utf-8"><title>L03 — 194 QA cards</title><style>'+CSS+'</style><body><h1>Aspekte B1+ — Lektion 03 (194 Karten)</h1><p class="meta">QA ONLY / NONIMPORT. Keine formale Kartenfreigabe. Keine echte App-Laufzeit.</p>'+''.join(body)+'</body></html>'
 newparts['Lessons/L03/L03-PHASE2-194-CARDS-QA-FRONT-BACK.html']=htmlout.encode('utf8')
 # Portable minimal validation for exact content and source links.
 checker='''#!/usr/bin/env python3
import json,zipfile,hashlib,sys
PRE="G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl"
p,base=sys.argv[1:3]
with zipfile.ZipFile(p) as a,zipfile.ZipFile(base) as b:
 assert a.testzip() is None
 A=[json.loads(x) for x in a.read(PRE).splitlines()]
 B=[json.loads(x) for x in b.read(PRE).splitlines()]
 assert len(A)==len(B)==1571
 assert all(x==y for x,y in zip(A,B) if x["lesson"]!="L03")
 assert all(x["preview_card_id"]==y["preview_card_id"] for x,y in zip(A,B))
 assert all(x["linked_original_source_ordinals"]==y["linked_original_source_ordinals"] for x,y in zip(A,B))
 assert a.read("G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv")==b.read("G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv")
 L=[c for c in A if c["lesson"]=="L03"]
 assert len(L)==194
 for c in L:
  nets=c["back"].get("semantic_network_sense_anchored_pending_qa") or []
  ex=(c["back"].get("existing_examples_de_fa_pending_qa") or [])+(c["back"].get("additional_examples_de_fa_pending_qa") or [])
  assert all(x.get("de") and x.get("fa") and x.get("status") for x in ex)
  if nets:assert all(x.get("sense_id") in {n["sense_id"] for n in nets} for x in ex)
  assert c["back"].get("Formen_section") is None and not c.get("formal_release_approved") and not c.get("import_ready")
  assert c.get("curated_HOLD_content_disposition_exists")==next(y for y in B if y["preview_card_id"]==c["preview_card_id"]).get("curated_HOLD_content_disposition_exists")
 print(json.dumps({"pass":True,"L03_cards":194,"total_cards":1571,"other_lessons_identical":True,"source_map_identical":True,"import_ready":False},indent=2))
'''
 newparts['Tools/qa_L03_phase2_parent_diff_v1.py']=checker.encode()
 # TSV preview is intentionally NONIMPORT, with reversible human-readable fields.
 import csv,io
 sv=io.StringIO();w=csv.writer(sv,delimiter='\t',lineterminator='\n')
 w.writerow(['card_id','lesson','front_de','meanings_fa','examples_de_fa_json','semantic_network_json','release'])
 for c in current:
  if c['lesson']=='L03':w.writerow([c['preview_card_id'],'L03',c['front']['display_de_provisional'],c['back']['meanings_fa_provisional'],json.dumps(examples(c),ensure_ascii=False),json.dumps(c['back'].get('semantic_network_sense_anchored_pending_qa',[]),ensure_ascii=False),'NONIMPORT'])
 newparts['Lessons/L03/L03-PHASE2-194-CARD-TSV-CANDIDATE-NONIMPORT.tsv']=sv.getvalue().encode('utf8')
 # Content policy/regression metrics independently calculated before any release.
 allcomb=[k for c in current for n in c['back'].get('semantic_network_sense_anchored_pending_qa',[]) or [] for k in n.get('Kombinationen_DE_FA',[]) or []]
 norm=lambda s:re.sub(r'\W+','',str(s).casefold())
 dup=[];badcomb=[];unrouted=[]
 for c in current:
  ex=examples(c);countg=collections.Counter(norm(x['de']) for x in ex)
  dup.extend([{'ordinal':c['source_ordinal'],'de':next(x['de'] for x in ex if norm(x['de'])==key)} for key,num in countg.items() if key and num>1])
  nets=c['back'].get('semantic_network_sense_anchored_pending_qa',[]) or []
  ids={n['sense_id'] for n in nets}
  if nets:
   unrouted.extend([{'ordinal':c['source_ordinal'],'de':x['de']} for x in ex if x.get('sense_id') not in ids])
  for n in nets:
   for k in n.get('Kombinationen_DE_FA',[]) or []:
    form=k.get('de','');kn=norm(form)
    if form.strip().endswith(('.', '?','!')) or len(form.split())>10 or kn in {norm(e['de']) for e in ex}:
     badcomb.append({'ordinal':c['source_ordinal'],'de':form,'reason':'FULL_SENTENCE_OR_COPY'})
     continue
    # Additional conservative finite-clause check: sentence contains a person pronoun plus finite predicate.
    if re.search(r'\b(ich|du|er|sie|es|wir|ihr|man)\s+(bin|bist|ist|sind|hat|habe|haben|geht|ging|macht|kann|können|muss|müssen|war|waren|wurde)\b',form,re.I):badcomb.append({'ordinal':c['source_ordinal'],'de':form,'reason':'POSSIBLE_FINITE_CLAUSE'})
 metrics={'schema':'aspekte-b1plus-L03-phase2-regression@1','all_cards':len(current),'original_source_rows':1548,'lesson_cards':194,'lesson_example_pairs':updated['examples'],'whole_corpus_example_pairs':sum(len(examples(c)) for c in current),
  'all_network_cards':sum(bool(c['back'].get('semantic_network_sense_anchored_pending_qa')) for c in current),'all_sense_blocks':sum(len(c['back'].get('semantic_network_sense_anchored_pending_qa') or []) for c in current),
  'all_collocations':len(allcomb),'new_L03_example_to_sense_links':links_added,'unrouted_all_corpus':len(unrouted),'unrouted_L03':[x for x in unrouted if 163<=x['ordinal']<=357],
  'bad_collocation_noncopy_or_finite_clause':badcomb,'duplicate_example_groups':dup,'global_legacy_duplicate_groups_expected':6,
  'G2_attested_global':sum(bool(c['front'].get('morphology_independently_validated')) for c in current),
  'release_ready':False,'actual_app_runtime_tested':False}
 assert not metrics['unrouted_L03'],metrics['unrouted_L03']
 assert not badcomb,badcomb
 assert len(dup)==6,(len(dup),dup)
 assert updated['morphology']==original_cnt['morphology']+len(ATTEST)
 assert updated['network_cards']==original_cnt['network_cards']+len(SPEC)
 assert updated['examples']==original_cnt['examples']+len(ADDED_EXAMPLES)
 newparts['Lessons/L03/L03-PHASE2-STRUCTURAL-REGRESSION.json']=(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n').encode('utf8')
 report['all_corpus']= {key:metrics[key] for key in ['all_cards','whole_corpus_example_pairs','all_network_cards','all_sense_blocks','all_collocations','G2_attested_global','global_legacy_duplicate_groups_expected']}
 newparts[report_file]=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode()
 sha_line=''.join(hashlib.sha256(newparts[n]).hexdigest()+'  '+n+'\n' for n in sorted(newparts))
 with zipfile.ZipFile(OUTPUT,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for n in sorted(newparts):z.writestr(n,newparts[n])
  z.writestr('SHA256SUMS.txt',sha_line.encode())
 with zipfile.ZipFile(OUTPUT) as z:
  assert z.testzip() is None
  hashes=dict(line.split('  ',1)[::-1] for line in z.read('SHA256SUMS.txt').decode().splitlines())
  assert len(hashes)==len(z.namelist())-1
  assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in hashes.items())
  assert z.read(original_map)==oldparts[original_map]
 d=ROOT/'output';d.mkdir(exist_ok=True)
 (d/'L03-PHASE2-194-CARD-EDITORIAL-REPORT.json').write_bytes(newparts[report_file])
 (d/'L03-PHASE2-194-CARD-DISPOSITIONS.jsonl').write_bytes(newparts[decisions_file])
 (d/'L03-PHASE2-194-CARD-FRONT-BACK-QA-ONLY.html').write_bytes(newparts['Lessons/L03/L03-PHASE2-194-CARDS-QA-FRONT-BACK.html'])
 (d/'L03-PHASE2-STRUCTURAL-REGRESSION.json').write_bytes(newparts['Lessons/L03/L03-PHASE2-STRUCTURAL-REGRESSION.json'])
 (d/'L03-PHASE2-194-CARD-CANDIDATE-NONIMPORT.tsv').write_bytes(newparts['Lessons/L03/L03-PHASE2-194-CARD-TSV-CANDIDATE-NONIMPORT.tsv'])
 (d/'L03-PHASE2-BEFORE-AFTER-EDITS.json').write_bytes(newparts[ledger_file])
 (d/'qa_L03_phase2_parent_diff_v1.py').write_bytes(newparts['Tools/qa_L03_phase2_parent_diff_v1.py'])
 print(json.dumps({'result':'BUILT','owner_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'zip_path':str(OUTPUT),'zip_bytes':OUTPUT.stat().st_size,'zip_entries':len(newparts)+1,'manifest_entries':len(newparts),'edited_cards':len(altered),'new_network_cards':len(SPEC),'new_sense_blocks':meaning_nodes_added,'new_collocations':collocations_added,'new_links':links_added,'new_examples':new_pairs,'morphology_attested_new':len(ATTEST),'QA_status_fixed':status_fixes,'before':original_cnt,'after':updated,'global':report['all_corpus'],'duplicate_count':len(dup)},ensure_ascii=False,indent=2))

if __name__=='__main__':build()
