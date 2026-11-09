#!/usr/bin/env python3
"""Aspekte B1+ L07 whole-lesson targeted Phase2 editorial, no release/old CSV.

Run from current L06 P3 canonical owner. Writes actual primary JSONL, explicit
before/after ledger, all-154 decisions, QA-only preview, manifest/ZIP CRC.
"""
import copy,hashlib,html,json,re,sys,zipfile,collections
from pathlib import Path
BASE=Path('/mnt/data/aspekte_b1plus_l07_phase2')
PARENT=BASE/'Aspekte-B1plus-L06-PHASE3-FINAL-177-CARD-RELEASE-BLOCKED-NONIMPORT-20261109.zip'
AUDIT=BASE/'Aspekte-B1plus-L07-PHASE1-WHOLE-154-CARD-AUDIT-NONIMPORT-20261109.zip'
OUT=BASE/'Aspekte-B1plus-L07-PHASE2-154-CARDS-TARGETED-EDITORIAL-NONIMPORT-20261109.zip'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
STATUS='PENDING_INDEPENDENT_DE_FA_SEMANTIC_QA'

def sha(b):return hashlib.sha256(b).hexdigest()
def pair(de,fa): return {'de':de,'fa':fa}
def sense(de,fa,colls):return {'de':de,'fa':fa,'colls':[pair(*z) for z in colls]}

# Deliberately narrow sense-specific idiomatic collocations, never whole example sentences.
SPECS={
847:[sense('allein in einem Haushalt wohnen','تنها زندگی کردن', [('alleinlebende Menschen','افرادی که تنها زندگی می‌کنند'),('als alleinlebende Person','به‌عنوان فردی که تنها زندگی می‌کند')])],
848:[sense('Liebesbeziehung über räumliche Distanz','رابطه عاطفی از راه دور',[('eine Fernbeziehung führen','رابطه از راه دور داشتن'),('eine Fernbeziehung aufrechterhalten','رابطه از راه دور را حفظ کردن')])],
849:[sense('Familie mit zahlreichen Mitgliedern oder mehreren Generationen','خانواده بزرگ یا گسترده',[('in einer Großfamilie aufwachsen','در خانواده‌ای پرجمعیت بزرگ‌شدن'),('das Leben in einer Großfamilie','زندگی در خانواده‌ای بزرگ')])],
852:[sense('Partnerin oder Partner im gemeinsamen Leben','شریک زندگی، همدم عاطفی',[('mit dem Lebensgefährten zusammenleben','با شریک زندگی مرد زندگی کردن'),('mit der Lebensgefährtin zusammenleben','با شریک زندگی زن زندگی کردن')])],
860:[sense('sich nach Meinungsverschiedenheiten wieder verständigen','پس از اختلاف دوباره به تفاهم رسیدن',[('sich nach einem Streit zusammenraufen','پس از مشاجره به تفاهم رسیدن'),('sich als Team zusammenraufen','به‌عنوان گروه هماهنگ‌شدن')])],
861:[sense('ein Eheversprechen geben','نامزد شدن برای ازدواج',[('sich mit jemandem verloben','با کسی نامزد شدن'),('frisch verlobt sein','تازه نامزد کرده بودن')])],
868:[sense('aufgrund von etwas Förderlichem','به لطف یا در نتیجه کمک چیزی',[('dank guter Vorbereitung','به لطف آمادگی خوب'),('dank deiner Unterstützung','به لطف حمایت تو')])],
870:[sense('Dienstzeit, Arbeitsverpflichtung, Schicht','شیفت یا نوبت کاری',[('Dienst haben','شیفت کاری داشتن'),('den Dienst antreten','شروع به خدمت یا کار کردن')]),sense('Dienstleistung oder organisierter Dienst','خدمات سازمان‌یافته',[('ein ambulanter Pflegedienst','خدمات مراقبت سیار'),('einen Dienst in Anspruch nehmen','از خدماتی استفاده کردن')])],
878:[sense('digitale oder organisatorische Plattform','بستر یا پلتفرم دیجیتال',[('eine digitale Plattform nutzen','استفاده از پلتفرم دیجیتال'),('über eine Plattform kommunizieren','از طریق یک پلتفرم ارتباط برقرار کردن')]),sense('erhöhte Fläche, Podest','سکو یا سطح مرتفع',[('eine erhöhte Plattform','سکویی بلندتر از سطح زمین'),('auf einer Plattform stehen','روی سکو ایستادن')])],
879:[sense('schwierig oder leicht auf dem Arbeitsmarkt vermittelbar','به سختی یا آسانی قابل معرفی برای کار',[('schwer vermittelbare Bewerber','متقاضیان کاری که یافتن کار برایشان دشوار است'),('auf dem Arbeitsmarkt leicht vermittelbar','دارای شانس خوب برای معرفی به کار')]),sense('schwierig oder leicht verständlich erklärbar','به سختی یا آسانی قابل توضیح و انتقال',[('schwer vermittelbare Inhalte','مطالبی که انتقال یا توضیحشان دشوار است'),('leicht vermittelbare Grundkenntnisse','دانسته‌های پایه که انتقالشان آسان است')])],
882:[sense('ein Mehrfaches einer Größe','چند برابر یک مقدار',[('ein Vielfaches des ursprünglichen Preises','چند برابر قیمت اولیه'),('um ein Vielfaches steigen','چندین برابر افزایش یافتن')])],
886:[sense('Sammlung von Einträgen und Grüßen der Gäste','دفتر ثبت پیام یا امضای مهمانان',[('sich ins Gästebuch eintragen','نام خود را در دفتر مهمانان ثبت کردن'),('einen Gruß im Gästebuch hinterlassen','در دفتر مهمانان پیامی گذاشتن')])],
888:[sense('Möglichkeit zwischen Alternativen zu wählen','امکان یا گزینه انتخاب',[('mehrere Auswahlmöglichkeiten haben','چند گزینه برای انتخاب داشتن'),('die Auswahlmöglichkeiten einschränken','گزینه‌های انتخاب را محدودکردن')])],
900:[sense('kulturell geprägte Weise zu leben','شیوه یا فرهنگ زندگی',[('eine entspannte Lebensart','سبک زندگی آرام'),('die regionale Lebensart kennenlernen','با سبک زندگی منطقه آشناشدن')])],
904:[sense('Metall durch Schlagen formen','فلز را با چکش شکل دادن',[('ein Eisen schmieden','آهن را چکش‌کاری کردن'),('Metall in der Schmiede bearbeiten','فلز را در آهنگری پرداختن')]),sense('Pläne oder Vorhaben entwerfen','طرح‌ریزی و نقشه‌کشیدن',[('Pläne für die Zukunft schmieden','برای آینده برنامه ریختن'),('gemeinsam Pläne schmieden','با هم نقشه کشیدن')])],
909:[sense('eine Aussage oder Handlung mit etwas in Bezug setzen','چیزی را به چیز دیگری ربط دادن',[('eine Aussage auf etwas beziehen','اظهارنظری را به موضوعی مرتبط دانستن'),('etwas auf einen konkreten Fall beziehen','چیزی را به موردی مشخص ربط دادن')]),sense('sich auf etwas beziehen; etwas zum Thema haben','به چیزی اشاره یا مربوط‌بودن',[('sich auf den vorherigen Absatz beziehen','به پاراگراف قبلی اشاره‌کردن'),('sich auf ein Beispiel beziehen','به مثالی اشاره‌کردن')])],
910:[sense('loyal zu jemandem stehen','حمایت کردن و طرف کسی را گرفتن',[('auch in Krisen zu jemandem halten','در بحران‌ها هم طرف کسی را گرفتن'),('fest zu seinem Partner halten','محکم از شریک خود حمایت کردن')])],
918:[sense('der Teil: Abschnitt oder Anteil','بخش، قسمت یا سهم',[('ein Teil der Gruppe','بخشی از گروه'),('der erste Teil eines Buches','بخش اول کتاب')]),sense('das Teil: einzelnes Bauteil oder Gegenstand','قطعه یا جزء مستقل',[('ein defektes Teil austauschen','تعویض قطعه معیوب'),('ein Teil der Maschine','قطعه‌ای از دستگاه')])],
919:[sense('gierig und schnell essen','با ولع خوردن و بلعیدن',[('das Essen hastig verschlingen','غذا را باعجله و ولع خوردن'),('eine Mahlzeit verschlingen','غذایی را با ولع خوردن')]),sense('etwas begeistert lesen','با ولع مطالعه کردن',[('einen Roman verschlingen','رمانی را با ولع خواندن'),('ein spannendes Buch verschlingen','کتابی مهیج را با اشتیاق زیاد خواندن')]),sense('sich ineinander verflechten','به هم پیچیدن و در هم تنیدن',[('sich ineinander verschlingen','در هم تنیده شدن'),('ineinander verschlungene Ranken','شاخه‌های پیچیده در هم')])],
927:[sense('einmaliger Anlauf, Bemühung','تلاش یا نوبت امتحان‌کردن',[('beim ersten Versuch','در اولین تلاش'),('ein neuer Versuch','تلاشی جدید')]),sense('wissenschaftliches Experiment','آزمایش علمی',[('einen Versuch durchführen','آزمایشی اجراکردن'),('ein Versuch im Labor','آزمایشی در آزمایشگاه')])],
933:[sense('große Menge oder Mehrzahl','انبوه، اکثریت یا توده جمعیت',[('die Masse der Besucher','اکثر بازدیدکنندگان'),('eine große Masse an Menschen','انبوهی از مردم')]),sense('formbare Substanz','ماده یا خمیر قابل شکل‌دهی',[('eine flüssige Masse','ماده مایع یا خمیر روان'),('die Masse in Formen gießen','ماده را داخل قالب‌ها ریختن')]),sense('physikalische Masse','جرم در فیزیک',[('die Masse eines Körpers','جرم یک جسم'),('eine Masse von zwei Kilogramm','جرمی برابر دو کیلوگرم')])],
934:[sense('technische Funktionsbeeinträchtigung','نقص یا اختلال فنی',[('eine technische Störung','اختلال فنی'),('eine Störung beheben','رفع‌کردن اختلال')]),sense('Unterbrechung oder Belästigung','مزاحمت یا وقفه',[('Entschuldigung für die Störung','ببخشید که مزاحم شدم'),('ohne Störung arbeiten','بدون مزاحمت کارکردن')])],
944:[sense('jemanden beschäftigen, einstellen','استخدام‌کردن',[('neue Mitarbeiter anstellen','کارکنان تازه استخدام‌کردن'),('fest angestellt sein','استخدام ثابت بودن')]),sense('ein Gerät einschalten','روشن‌کردن دستگاه',[('das Radio anstellen','رادیو را روشن‌کردن'),('die Heizung anstellen','گرمایش را روشن‌کردن')]),sense('Überlegungen oder Vermutungen anstellen','فکر و بررسی یا حدس‌زدن',[('Vermutungen anstellen','حدس و گمان مطرح‌کردن'),('Überlegungen anstellen','فکر و بررسی کردن')]),sense('etwas Unkluges tun','دسته‌گل به آب دادن یا خرابکاری کردن',[('etwas Dummes anstellen','کار احمقانه‌ای کردن'),('wieder etwas angestellt haben','باز خرابکاری کرده بودن')])],
948:[sense('grundlegend, wesentlich','اساسی و بنیادین',[('von elementarer Bedeutung','دارای اهمیت بنیادی'),('elementare Bedürfnisse','نیازهای اساسی')]),sense('einfach, auf der ersten Stufe','ابتدایی و مقدماتی',[('elementare Grammatikregeln','قواعد ابتدایی دستور زبان'),('elementare Kenntnisse','دانش پایه‌ای')])],
953:[sense('fröhlich, ungezwungen','سرخوش و شادِ بی‌تکلف',[('eine ausgelassene Stimmung','فضای سرخوش و شاد'),('ausgelassen feiern','با شادی و بی‌قیدی جشن گرفتن')]),sense('Partizip II von auslassen: weggelassen','حذف‌شده یا از قلم افتاده',[('eine ausgelassene Passage','بخشی حذف‌شده از متن'),('einen Absatz auslassen','پاراگرافی را حذف‌کردن')])],
956:[sense('jemals: zu irgendeinem Zeitpunkt','روزی، تا کنون یا در هر زمانی',[('jemals davon gehört haben','تا به حال چیزی درباره آن شنیده بودن'),('jemals Hilfe benötigen','روزی نیاز به کمک داشتن')])],
960:[sense('von Indizien auf eine Folgerung schließen','از نشانه‌ای به نتیجه‌ای رسیدن',[('aus den Daten auf etwas schließen','از داده‌ها چیزی را نتیجه‌گرفتن'),('von Symptomen auf eine Ursache schließen','از نشانه‌ها به علت پی بردن')])],
971:[sense('herzlicher Gruß oder Glückwunsch','آرزوی محبت‌آمیز یا تبریک صمیمانه',[('alles Liebe zum Geburtstag wünschen','برای تولد بهترین آرزوها را داشتن'),('alles Liebe für die Zukunft wünschen','برای آینده بهترین آرزوها را داشتن')])],
972:[sense('äußere Einfassung eines Gegenstands','قاب یا چارچوب یک شیء',[('ein hölzerner Bilderrahmen','قاب چوبی تصویر'),('der Rahmen eines Spiegels','قاب آینه')]),sense('organisatorische oder thematische Begrenzung','چارچوب موضوعی یا سازمانی',[('im Rahmen eines Projekts','در چارچوب پروژه‌ای'),('im vorgegebenen Rahmen bleiben','در محدوده تعیین‌شده ماندن')])],
973:[sense('Handlung des Schutzes oder Sichverteidigens','دفاع و محافظت',[('das Recht auf Verteidigung','حق دفاع'),('die Verteidigung der eigenen Position','دفاع از موضع خود')]),sense('juristische Verteidigerseite','تیم یا وکلای دفاع',[('das Plädoyer der Verteidigung','دفاعیه پایانی وکلای مدافع'),('ein Antrag der Verteidigung','درخواست تیم دفاع')])],
987:[sense('regelmäßig zwischen Wohnort und Arbeitsplatz fahren','به‌طور منظم رفت‌وآمد کردن',[('zwischen zwei Städten pendeln','بین دو شهر رفت‌وآمد کردن'),('täglich zur Arbeit pendeln','هر روز به محل کار رفت‌وآمد کردن')]),sense('hin und her schwingen','پاندول‌وار نوسان‌کردن',[('hin und her pendeln','به این سو و آن سو نوسان‌کردن'),('eine pendelnde Bewegung','حرکتی پاندولی')])],
990:[sense('relativ: abhängig vom Bezugsrahmen','نسبی، وابسته به معیار سنجش',[('ein relativer Vorteil','مزیتی نسبی'),('relative Unterschiede','تفاوت‌های نسبی')]),sense('relativ: in gewissem Maße (Adverb)','نسبتاً، تا حدی',[('relativ günstig','نسبتاً ارزان'),('relativ schwierig','نسبتاً دشوار')])],
999:[sense('etwas bewusst nicht sagen','عمداً چیزی را نگفتن یا پنهان‌کردن',[('jemandem etwas verschweigen','موضوعی را از کسی پنهان‌کردن'),('wichtige Informationen verschweigen','اطلاعات مهمی را نگفتن')])],
}
# Explicit case-level assignments where a card carries several genuinely distinct senses.
# These are substrings of already saved examples (not generated text), in order of senses above.
ROUTE={
870:['Dienst','Pflegedienst'],878:['digital','Aussichtsturm|Redner'],879:['Bewerber|Ausbildung|Fähigkeiten','Grundidee'],
904:['Schmied|heiße Eisen','Pläne'],909:['beziehe diese Bemerkung|beziehen Sie Ihre Antwort','bezieht sich'],
918:['Teil der Gruppe|Teil des Buches','Teil der Maschine'],
919:['Essen|Junge','Roman','Ranken'],927:['zweiten Versuch|Prüfung','Labor'],
933:['Besucher','flüssige Masse','UNMATCHED'],934:['technischen Störung','Entschuldigung'],
944:['Mitarbeiter|Firma','Radio','Vermutungen','was hast du denn wieder angestellt'],948:['elementar|Kommunikation','elementaren Regeln'],
953:['Kinder|Feier|Stimmung','Zusammenfassung'],972:['Rahmen des Bildes|Rahmen des Spiegels','Im Rahmen|im Rahmen'],
973:['Recht auf Verteidigung','Die Verteidigung beantragte'],987:['pendelt|gependelt','UNMATCHED'],
990:['UNMATCHED','relativ günstig|relativ aussagekräftig|relativ einfach']
}

def get_route(r,example,network):
    ordinal=r['source_ordinal']; de=example.get('de','');
    # Respect contrast of paired cards, source ordinal 956 maps to two distinct cards.
    if ordinal==956:return 0
    if ordinal==870:return 1 if 'Pflegedienst' in de else 0
    if ordinal==997:
        return 1 if 'bei dieser Entscheidung' in de else 0
    if ordinal in ROUTE:
        import re
        for ix,terms in enumerate(ROUTE[ordinal]):
            if terms=='UNMATCHED':continue
            if any(k.casefold() in de.casefold() for k in terms.split('|')):return ix
        return None
    return 0 if len(network)==1 else None

def add_pairs(r,de,fa):
    r['back']['existing_examples_de_fa_pending_qa'].append({'de':de,'fa':fa,'provenance':'L07_PHASE2_CONTEXTUAL_EDITORIAL','status':STATUS})

def examples(r):return r['back']['existing_examples_de_fa_pending_qa']+r['back']['additional_examples_de_fa_pending_qa']

with zipfile.ZipFile(PARENT) as z:
    assert z.testzip() is None
    files={x:z.read(x) for x in z.namelist() if x!='SHA256SUMS.txt'}
    sums={n:hashh for hashh,n in (a.split('  ',1) for a in z.read('SHA256SUMS.txt').decode().splitlines() if a)}
    assert set(files)==set(sums)
    assert all(sha(v)==sums[n] for n,v in files.items())
with zipfile.ZipFile(AUDIT) as z:
    assert z.testzip() is None
    queue=[json.loads(q) for q in z.read('Lessons/L07/L07-PHASE1-154-CARD-DECISION-QUEUE.jsonl').splitlines()]
assert len(queue)==154
orig_bytes=files[MAIN]
original=[json.loads(x) for x in orig_bytes.splitlines()]
assert len(original)==1571
cards=copy.deepcopy(original)
L07=[r for r in cards if r['lesson']=='L07']
assert len(L07)==154
assert len([q for q in queue if q['priority']=='P1'])==44
L07ids={r['preview_card_id'] for r in L07}
assert L07ids=={x['card_id'] for x in queue}
# Ensure no earlier revisions slipped in.
assert sha(orig_bytes)=='eaa8205368528e0be128b3eef79c4ce441b8682abdad1fb56cdd300c696b4694'

# Correct cross-lemma example routing while retaining each German/Persian pair on its own card.
misrouted=[]
for r in L07:
    if r['source_ordinal']==956:
        is_ever=r['front']['base_headword_de'].strip()=='jemals'
        additional=r['back']['additional_examples_de_fa_pending_qa']
        removed=[x for x in additional if ('niemals' in x['de'].casefold()) == is_ever]
        assert len(removed)==1,(r['front']['base_headword_de'],additional)
        r['back']['additional_examples_de_fa_pending_qa']=[x for x in additional if x not in removed]
        if is_ever:
            add_pairs(r,'Wenn du jemals Hilfe brauchst, melde dich.','اگر روزی به کمک نیاز داشتی، خبر بده.')
        else:
            add_pairs(r,'So etwas würde ich niemals tun.','من هرگز چنین کاری نمی‌کنم.')
        misrouted.append({'card':r['preview_card_id'],'removed_misrouted_de':removed[0]['de'],'added_de':r['back']['existing_examples_de_fa_pending_qa'][-1]['de']})
assert len(misrouted)==2

# Preserve both Persian paraphrases of one exact German example as alternatives on one example object.
dedup=[]
for r in L07:
    if r['source_ordinal']==971:
        seen={};keep=[]
        for ex in r['back']['existing_examples_de_fa_pending_qa']+r['back']['additional_examples_de_fa_pending_qa']:
            key=ex['de'].strip()
            if key in seen:
                previous=seen[key]
                if ex['fa'].strip()!=previous['fa'].strip():
                    previous.setdefault('fa_alternatives',[]).append(ex['fa'].strip())
                dedup.append({'card':r['preview_card_id'],'de':key,'preserved_Persian_alternatives':[previous['fa']]+previous.get('fa_alternatives',[])})
            else:seen[key]=ex;keep.append(ex)
        r['back']['existing_examples_de_fa_pending_qa']=keep
        r['back']['additional_examples_de_fa_pending_qa']=[]
assert len(dedup)==1

# Restore genuinely missing fourth colloquial sense of anstellen as a bilingual example.
for r in L07:
    if r['source_ordinal']==944:
        add_pairs(r,'Was hast du denn wieder angestellt?','باز چه دسته‌گلی به آب داده‌ای؟')

status_fixes=[]
for r in L07:
    for ex in examples(r):
        if not ex.get('status'):
            ex['status']=STATUS
            status_fixes.append({'card':r['preview_card_id'],'de':ex['de']})
# 41 original missing - 1 duplicate removed, plus two newly-added examples (already status assigned)
assert len(status_fixes)==38, len(status_fixes)

# New explicit sense schema uses original card ID; never changes lemma IDs/source map.
network_additions=[];sense_links=[];ambiguous=[];combination_additions=[]
for r in L07:
    existing=r['back'].get('semantic_network_sense_anchored_pending_qa',[])
    if r['source_ordinal'] in SPECS and not existing:
        specs=SPECS[r['source_ordinal']]
        if r['source_ordinal']==956:
            specs=[sense('niemals: zu keinem Zeitpunkt','هرگز و در هیچ زمانی', [('niemals vergessen','هرگز فراموش نکردن'),('niemals wieder','دیگر هرگز')])] if r['front']['base_headword_de'].strip()=='niemals' else SPECS[956]
        network=[]
        for index,s in enumerate(specs,1):
            sid=r['preview_card_id']+f':L07P2:S{index}'
            node={'sense_id':sid,'sense_de':s['de'],'sense_fa':s['fa'],
             'Kombinationen_DE_FA':s['colls'],'Synonyme':[],'Antonyme':[],
             'Verwandte_Woerter_KEINE_Synonyme':[],'Wortfamilie':[],
             'status':'PENDING_G4_INDEPENDENT_SENSE_AND_RELATION_QA',
             'source':'L07_PHASE2_TARGETED_CONTEXTUAL_EDITORIAL_NOT_EXTERNAL_DICTIONARY_ATTESTED',
             'lexical_relation_policy':'NO_FORCED_SYNONYMS_ANTONYMS_OR_UNGROUNDED_WORD_FAMILY'}
            network.append(node)
            combination_additions.extend([dict(card=r['preview_card_id'],sense_id=sid,**col) for col in s['colls']])
        r['back']['semantic_network_sense_anchored_pending_qa']=network
        network_additions.append({'card':r['preview_card_id'],'ordinal':r['source_ordinal'],'headword':r['front']['base_headword_de'],'senses':len(network)})
    current=r['back'].get('semantic_network_sense_anchored_pending_qa',[])
    if current:
        for ex in examples(r):
            if ex.get('sense_id') and ex['sense_id'] in {s['sense_id'] for s in current}:continue
            idx=get_route(r,ex,current)
            if idx is None:
                ambiguous.append({'card':r['preview_card_id'],'de':ex['de'],'reason':'MIXED_OR_AMBIGUOUS_CONTEXT_NO_GUESS'})
                continue
            assert 0<=idx<len(current),(r['source_ordinal'],idx)
            ex['sense_id']=current[idx]['sense_id']
            sense_links.append({'card':r['preview_card_id'],'de':ex['de'],'sense_id':ex['sense_id']})

# Explicit contextual improvement for a misleading first-card German/Persian meaning;
# no arbitrary front-side morph approvals are manufactured.
meaning_fixes=[]
for r in L07:
    if r['source_ordinal']==971:
        old=r['back']['meanings_fa_provisional']
        new='آرزوی محبت‌آمیز؛ «بهترین آرزوها» در تبریک یا پایان پیام صمیمانه'
        if old!=new:
            r['back']['meanings_fa_provisional']=new
            meaning_fixes.append({'card':r['preview_card_id'],'before':old,'after':new})
    if r['source_ordinal']==879:
        old=r['back']['meanings_fa_provisional']
        new='به‌سختی/به‌آسانی قابل معرفی به کار؛ در کاربرد عمومی: دشوار/آسان برای توضیح یا انتقال'
        if old!=new:
            r['back']['meanings_fa_provisional']=new
            meaning_fixes.append({'card':r['preview_card_id'],'before':old,'after':new})
    if r['source_ordinal']==956 and r['front']['base_headword_de']=='niemals':
        old=r['back']['meanings_fa_provisional'];new='هرگز؛ در هیچ زمانی'
        if old!=new:r['back']['meanings_fa_provisional']=new;meaning_fixes.append({'card':r['preview_card_id'],'before':old,'after':new})

# Re-read from the exact bytes that will be persisted. No status or 'all reviewed' metadata
# is copied into unchanged cards to inflate changed-card counts.
def canonical(rows):return ('\n'.join(json.dumps(x,sort_keys=True,ensure_ascii=False) for x in rows)+'\n').encode()
child_main=canonical(cards)
reopened=[json.loads(x) for x in child_main.splitlines()]
assert len(reopened)==1571
assert [x['preview_card_id'] for x in original]==[x['preview_card_id'] for x in reopened]
assert [x['linked_original_source_ordinals'] for x in original]==[x['linked_original_source_ordinals'] for x in reopened]
assert all(x==y for x,y in zip(original,reopened) if x['lesson']!='L07')
changed=[(x,y) for x,y in zip(original,reopened) if x!=y]
assert all(x['lesson']=='L07' for x,y in changed)
changedIDs={r['preview_card_id'] for r,y in changed}
qa_count=sum(len(examples(x)) for x in reopened if x['lesson']=='L07')
assert qa_count==348,(qa_count, '348 before -2 misrouted +2 new for 956 -1 duplicate +1 new for 944')
assert not any(not e.get('status') for x in reopened if x['lesson']=='L07' for e in examples(x))
assert sum(bool(x['back'].get('semantic_network_sense_anchored_pending_qa')) for x in reopened if x['lesson']=='L07')==6+len(network_additions)
assert len({x['preview_card_id'] for x in reopened})==1571
assert len({x['preview_card_id'] for x in reopened if x['lesson']=='L07'})==154

# Catch unsafe copied examples posing as collocations, and v4 finite clauses.
DETERMINERS={'der','die','das','ein','eine','einen','einem','einer','diese','dieser','dieses','jener','jene'}
FINITE={'reicht','entscheidet','koordiniert','läuft','prüft','schreibt','bringt','bestimmt','öffnet','organisiert','führt','hat','ist','sind','steht','arbeitet','verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt','hält','macht','kann','wird','werden','nimmt','bietet','spricht'}
clauses=[];total=0
for r in reopened:
    for s in r['back'].get('semantic_network_sense_anchored_pending_qa',[]) or []:
        for coll in s.get('Kombinationen_DE_FA',[]) or []:
            total+=1;de=coll.get('de','');words=re.findall(r'\w+',de,re.UNICODE)
            if not de or not coll.get('fa') or '\n' in de:clauses.append({'card':r['preview_card_id'],'de':de,'kind':'BLANK_OR_MULTILINE'})
            if len(words)>=4 and words[0].casefold() in DETERMINERS and words[1][0].isupper() and words[2].casefold() in FINITE:
                clauses.append({'card':r['preview_card_id'],'de':de,'kind':'FINITE_NP_CLAUSE_V4'})
            if any(de==ex['de'] for ex in examples(r)):clauses.append({'card':r['preview_card_id'],'de':de,'kind':'EXACT_EXAMPLE_COPY'})
assert not [v for v in clauses if v['card'] in L07ids], clauses
old_total=0
for r in original:
    for s in r['back'].get('semantic_network_sense_anchored_pending_qa',[]) or []:old_total+=len(s.get('Kombinationen_DE_FA',[]))
assert total==old_total+len(combination_additions)

# Maintain an actionable card-level whole-lesson disposition, without marking unchanged
# cards as linguistically approved or automatically clearing existing HOLD flags.
queue_map={q['card_id']:q for q in queue}
decisions=[]
for r in reopened:
 if r['lesson']!='L07':continue
 q=queue_map[r['preview_card_id']]
 dec={'card_id':r['preview_card_id'],'source_ordinal':r['source_ordinal'],
  'headword_de':r['front']['base_headword_de'],'priority':q['priority'],
  'phase2_disposition':'TARGETED_CONTENT_OR_STATUS_EDIT_PERSISTED' if r['preview_card_id'] in changedIDs else 'RETAINED_WITH_CASE_LEVEL_RISK_PENDING',
  'actual_primary_card_modified':r['preview_card_id'] in changedIDs,
  'current_examples':len(examples(r)),
  'meaning_network_senses':len(r['back'].get('semantic_network_sense_anchored_pending_qa',[])),
  'unrouted_examples':[x['de'] for x in examples(r) if r['back'].get('semantic_network_sense_anchored_pending_qa') and not x.get('sense_id')],
  'inherited_curated_HOLD':r['curated_HOLD_content_disposition_exists'],
  'scoped_morphology_attested':bool(r['front']['morphology_independently_validated']),
  'bilingual_language_release_QA':'NOT_FULLY_VALIDATED',
  'formal_release_approved':False,
  'next':'PHASE3_EXPLICIT_CASE_LEVEL_QA_OR_RELEASE_BLOCKED'}
 decisions.append(dec)
assert len(decisions)==154
# Keep a full exact structured before/after for every persisted changed card for replay.
before_after=[{'card_id':x['preview_card_id'],'ordinal':x['source_ordinal'],'before':x,'after':y} for x,y in changed]

report={
 'schema':'aspekte-b1plus-L07-phase2-whole-lesson-verified-editorial@1',
 'date':'2026-11-09','lesson':'L07','phase':2,'phases_total':3,
 'status':'WHOLE_154_CARD_DISPOSITIONS_TARGETED_CHANGES_APPLIED_NONIMPORT',
 'parent_sha256':sha(PARENT.read_bytes()),'parent_primary_main_sha256':sha(orig_bytes),
 'child_primary_main_sha256':sha(child_main),'original_1548_source_row_map_sha256':sha(files[MAP]),
 'card_ids_original_unchanged':True,'source_map_byteidentical':True,
 'total_cards':1571,'L07_cards':154,'L07_original_source_rows':153,
 'per_card_decisions':154,'changed_card_objects':len(changed),
 'changed_card_ids':[r['preview_card_id'] for r,y in changed],
 'untouched_other_lesson_card_objects':1417,
 'network_cards_new':len(network_additions),'new_sense_blocks':sum(x['senses'] for x in network_additions),
 'new_explicit_example_sense_links':len(sense_links),
 'new_combinations_de_fa':len(combination_additions),
 'prior_combinationen_global':old_total,'new_combinationen_global':total,
 'statusless_examples_repaired_to_PENDING':len(status_fixes),
 'cross_lemma_misrouted_examples_replaced':misrouted,
 'duplicate_examples_consolidated':dedup,
 'persian_meaning_updates':meaning_fixes,
 'L07_examples_before':348,'L07_examples_after':qa_count,'new_example_for_missing_anstellen_sense':1,
 'unrouted_examples_in_network_cards':len(ambiguous),
 'unrouted_example_cases':ambiguous,
 'new_combinationen_regression_findings_in_L07':[c for c in clauses if c['card'] in L07ids],
 'inherited_global_finite_clause_candidates':[v for v in clauses if v['card'] not in L07ids],
 'inherited_curated_HOLDs_L07':sum(r['curated_HOLD_content_disposition_exists'] for r in L07),
 'G2_scoped_forms_attested_L07':sum(x['front']['morphology_independently_validated'] for x in L07),
 'full_bilingual_QA_complete':False,'real_German_Flashcards_Pro_import_render_test':False,
 'formal_release_approved_count':0,'import_ready':False,
 'phase3_next':'L07_PHASE3_FULL_154_CARD_CASE_LEVEL_QA_AND_REAL_APP_GATE_OR_EXPLICIT_RELEASE_BLOCKED',
 'note':'One complete 154-card disposition ledger, targeted content edits only. Unchanged cards are not language-approved; no invented source dictionary attestations or release.'
}

# QA preview of all 154 cards for editorial review; no import or release token.
rows=['<!doctype html><html lang="de"><head><meta charset="UTF-8"><title>L07 P2 154 cards NONIMPORT</title><style>body{font:15px system-ui;max-width:1000px;margin:25px auto;padding:0 10px}section{padding:12px 16px;border:1px solid #ddd;margin:15px 0;border-radius:12px}.minor{color:#666}li{margin:5px 0}h2{margin:0 0 6px}</style></head><body><h1>Aspekte B1+ L07 · Phase2 (154) · QA only · NONIMPORT</h1>']
for r in reopened:
 if r['lesson']!='L07':continue
 e=html.escape
 rows.append(f'<section><h2>{e(str(r["source_ordinal"]))} · {e(r["front"]["base_headword_de"])}</h2>')
 rows.append(f'<div class="minor">{e(r["front"]["display_de_provisional"])} · HOLD={r["curated_HOLD_content_disposition_exists"]}</div><p>{e(r["back"]["meanings_fa_provisional"])}</p><ul>')
 for ex in examples(r):rows.append(f'<li>{e(ex["de"])} — {e(ex["fa"])} <small>({e(ex.get("sense_id") or "unrouted")}; QA=PENDING)</small></li>')
 rows.append('</ul>')
 for s in r['back'].get('semantic_network_sense_anchored_pending_qa',[]):
  rows.append(f'<p><b>{e(s["sense_de"])} / {e(s["sense_fa"])}</b></p><ul>')
  for cc in s['Kombinationen_DE_FA']: rows.append(f'<li>{e(cc["de"])} — {e(cc["fa"])}</li>')
  rows.append('</ul>')
 rows.append('</section>')
rows.append('</body></html>')

# Append the actual replaced primary card file and auditable recipe / sidecars.
files[MAIN]=child_main
prefix='Lessons/L07/'
files[prefix+'L07-PHASE2-WHOLE-154-CARD-REPORT.json']=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode()
files[prefix+'L07-PHASE2-154-CARD-DISPOSITIONS.jsonl']=canonical(decisions)
files[prefix+'L07-PHASE2-CHANGED-CARD-BEFORE-AFTER.json']=(json.dumps(before_after,ensure_ascii=False,indent=2)+'\n').encode()
files[prefix+'L07-PHASE2-CONTENT-EDIT-DETAILS.json']=(json.dumps({'misrouted_examples':misrouted,'exact_duplicate_merge':dedup,'missing_status_repairs':status_fixes,'new_networks':network_additions,'new_example_sense_links':sense_links,'new_combinations':combination_additions,'meaning_fixes':meaning_fixes,'unrouted_ambiguities':ambiguous},ensure_ascii=False,indent=2)+'\n').encode()
files[prefix+'L07-PHASE2-154-CARD-FRONT-BACK-QA-ONLY.html']='\n'.join(rows).encode()
files['Tools/build_L07_phase2_v1.py']=Path(__file__).read_bytes()
files['README-L07-PHASE2-NONIMPORT.md']=(f'# L07 Phase2 - NONIMPORT\n\nParent: {sha(PARENT.read_bytes())}\nMain member SHA before: {sha(orig_bytes)}\nMain member SHA after: {sha(child_main)}\n154 lesson cases, {len(changed)} actual card edits, {len(combination_additions)} collocations, {qa_count} examples. Do not import. Source publisher CSV is not used.\n').encode()
manifest='\n'.join(f'{sha(value)}  {name}' for name,value in sorted(files.items()))+'\n'
OUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for name,value in files.items():z.writestr(name,value)
    z.writestr('SHA256SUMS.txt',manifest)
# Hard proof against L04 ghost edits; re-open actual persisted payload and compare with parent.
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    signatures={n:h for h,n in (line.split('  ',1) for line in z.read('SHA256SUMS.txt').decode().splitlines())}
    assert set(signatures)==set(z.namelist())-{'SHA256SUMS.txt'}
    assert all(sha(z.read(n))==signatures[n] for n in signatures)
    saved=[json.loads(line) for line in z.read(MAIN).splitlines()]
    assert saved==reopened
    assert sum(o!=n for o,n in zip(original,saved))==len(changed)
    assert z.read(MAP)==files[MAP]
    assert len([r for r in saved if r['lesson']=='L07'])==154
print(json.dumps({'file':str(OUT),'zip_sha256':sha(OUT.read_bytes()),'zip_bytes':OUT.stat().st_size,'members':len(files)+1,'internal_hashes':len(files),'changed_cards_saved':len(changed),'senses_added':sum(x['senses'] for x in network_additions),'network_cards_added':len(network_additions),'example_links':len(sense_links),'new_collocations':len(combination_additions),'L07_examples_after':qa_count,'status_repairs':len(status_fixes),'duplicate_merges':len(dedup),'unresolved_example_routes':len(ambiguous),'global_v4_candidate_count':len(clauses),'L07_V4_candidate_count':len([c for c in clauses if c['card'] in L07ids]),'primary_member_sha256':sha(child_main)},ensure_ascii=False,indent=2))
