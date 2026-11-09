#!/usr/bin/env python3
"""Reproducible exact-owner L09 whole-185-card editorial (primary learner JSONL changes).
NONIMPORT: no full German/Persian semantic signoff and no invented human reviewer.
"""
from __future__ import annotations
import collections,copy,hashlib,html,json,re,sys,zipfile
from pathlib import Path
SRC=Path('/mnt/data/aspekte_b1plus_l09_phase1/Aspekte-B1plus-L08-PHASE3-157-CARD-QUALITY-GATE-RELEASE-BLOCKED-NONIMPORT-20261109.zip')
OUT=Path('/mnt/data/aspekte_b1plus_l09_phase2')
EXPECTED_ZIP='577770549cf2a93feb86bc0197079c3580c8b73becaa20d7b65decf0f6d437e0'
EXPECTED_MAIN='89171eeea1e5b0aba9182ebe36418265b756ae6caab8fa45b0878579120608e0'
EXPECTED_MAP='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
PENDING='PENDING_DE_FA_SEMANTIC_QA'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def pretty(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def examples(c):return c['back'].get('existing_examples_de_fa_pending_qa',[])+c['back'].get('additional_examples_de_fa_pending_qa',[])
def nets(c):return c['back'].get('semantic_network_sense_anchored_pending_qa') or []
def ex(de,fa,tag):return {'de':de,'fa':fa,'provenance':tag,'status':PENDING}
def norm(s):return re.sub(r'\W+','',s.casefold())

# One explicitly authored, meaning-scoped, short lexical combination per entry.
# No automatic synonym/antonym generation. Meaning labels are editorial clues, not certified definitions.
# These cover core contexts, *not* every sense of a polysemous lemma; no false claim of full coverage.
SPECS={
 1158:('fremdartig oder aus fernen Ländern','غیربومی یا نامأنوس',[('exotische Früchte probieren','میوه‌های استوایی یا غیرمعمول را امتحان کردن')]),
 1160:('Reise mit mehreren Teilnehmenden','سفر گروهی',[('an einer Gruppenreise teilnehmen','در یک سفر گروهی شرکت کردن')]),
 1161:('kleines Geschenk von einem Besuch oder einer Reise','سوغاتی کوچک',[('ein Mitbringsel aus dem Urlaub','سوغاتی کوچکی از تعطیلات')]),
 1165:('etwas in einem Text erneut zur Information lesen','برای یافتن اطلاعات به متن مراجعه کردن',[('eine Information nachlesen','اطلاعاتی را در متن جست‌وجو و دوباره خواندن')]),
 1166:('Reise um die Welt','سفر دور دنیا',[('eine Weltreise unternehmen','سفری به دور دنیا رفتن')]),
 1168:('Geld für eine Sache bereitstellen','تأمین مالی کردن',[('ein Studium finanzieren','هزینهٔ تحصیل را تأمین کردن')]),
 1169:('Ziel für anzusparendes Geld','هدف پس‌انداز',[('ein Sparziel erreichen','به هدف پس‌انداز رسیدن')]),
 1170:('etwas organisieren und besorgen','تهیه و تدارک',[('die Beschaffung von Materialien','تهیهٔ مواد و تجهیزات')]),
 1171:('mit vielen Einzelheiten','با جزئیات',[('etwas detailliert beschreiben','چیزی را با جزئیات شرح دادن')]),
 1173:('Land, das besucht wird','کشور مقصد سفر',[('ein beliebtes Reiseland','کشور محبوب برای سفر')]),
 1174:('umgangssprachliche Bezeichnung für das Abitur','آبیتور (محاوره‌ای)',[('das Abi machen','مدرک آبیتور گرفتن')]),
 1175:('Person, die per Anhalter reist','مسافر هیچ‌هایک',[('per Anhalter reisen','با خودروهای عبوری و بدون برنامهٔ قبلی سفر کردن')]),
 1176:('Haus- und Wohnungseinrichtung als Besitz','اثاثیهٔ منزل',[('den Hausrat versichern','لوازم منزل را بیمه کردن')]),
 1177:('vollständig','کامل',[('komplett ausgebucht sein','کاملاً رزروشده بودن')]),
 1178:('Ausflug mit dem Fahrrad','گردش با دوچرخه',[('eine Radtour planen','یک گردش با دوچرخه برنامه‌ریزی کردن')]),
 1179:('Vorbereitung einer Reise','آماده‌سازی سفر',[('mit den Reisevorbereitungen beginnen','آماده‌سازی سفر را شروع کردن')]),
 1180:('anfänglich verfügbares Kapital','سرمایهٔ اولیه',[('Startkapital für eine Firma','سرمایهٔ اولیه برای شرکت')]),
 1181:('Reihenfolge mehrerer Schritte','توالی',[('die zeitliche Abfolge schildern','ترتیب زمانی را شرح دادن')]),
 1182:('Ereignisse, die sich abspielen','اتفاقات در حال وقوع',[('das politische Geschehen verfolgen','رویدادهای سیاسی را دنبال کردن')]),
 1184:('bestimmte Zeitspanne','بازهٔ زمانی',[('innerhalb eines kurzen Zeitraums','در یک بازهٔ زمانی کوتاه')]),
 1185:('großes Wüstentier','شتر',[('auf einem Kamel reiten','بر شتر سوار شدن')]),
 1186:('auf einem Tier sitzen und sich fortbewegen','سوارکاری کردن',[('durch die Wüste reiten','در بیابان سواری کردن')]),
 1187:('Ärmel nach oben rollen','آستین بالا زدن',[('die Ärmel hochkrempeln','آستین‌ها را بالا زدن')]),
 1188:('Teil eines Kleidungsstücks für den Arm','آستین',[('kurze Ärmel tragen','لباس آستین‌کوتاه پوشیدن')]),
 1189:('die Gesellschaft betreffend','اجتماعی',[('gesellschaftliche Verantwortung übernehmen','مسئولیت اجتماعی بر عهده گرفتن')]),
 1190:('schwer arbeiten','سخت و با زحمت کار کردن',[('den ganzen Tag schuften','تمام روز سخت کار کردن')]),
 1191:('jemandem bei Fortschritt helfen','به پیشرفت کمک کردن',[('jemanden beruflich weiterbringen','به پیشرفت شغلی کسی کمک کردن')]),
 1192:('vorübergehender Lager- oder Gruppenort','اردوگاه یا کمپ',[('in einem Camp übernachten','در یک کمپ شب ماندن')]),
 1195:('etwas in Zweifel ziehen','در چیزی شک کردن',[('die Aussage bezweifeln','درستی یک گفته را زیر سؤال بردن')]),
 1196:('ungerechte Ausnutzung','استثمار',[('Ausbeutung von Arbeitskräften','بهره‌کشی از نیروی کار')]),
 1198:('Person für Kinderbetreuung in einer Gastfamilie','فرد آوپر',[('als Au-pair arbeiten','به‌عنوان آوپر کار کردن')]),
 1199:('Familie, die jemanden aufnimmt','خانوادهٔ میزبان',[('bei einer Gastfamilie wohnen','نزد خانوادهٔ میزبان زندگی کردن')]),
 1200:('Kurs zum Erlernen einer Sprache','دورهٔ زبان',[('einen Sprachkurs besuchen','در دورهٔ زبان شرکت کردن')]),
 1201:('Abfahrt oder Wegreise','عزیمت',[('vor der Abreise','پیش از عزیمت')]),
 1202:('Flug ohne Zwischenlandung','پرواز بدون توقف',[('einen Direktflug buchen','پرواز مستقیم رزرو کردن')]),
 1203:('Angaben zu einem Flug','اطلاعات پرواز',[('die Flugdaten überprüfen','اطلاعات پرواز را بررسی کردن')]),
 1204:('Flug zum Reiseziel','پرواز رفت',[('den Hinflug umbuchen','پرواز رفت را تغییر رزرو دادن')]),
 1205:('Flug vom Reiseziel zurück','پرواز برگشت',[('der Rückflug nach Berlin','پرواز برگشت به برلین')]),
 1207:('mit guten Verkehrsverbindungen','با دسترسی مناسب به حمل‌ونقل',[('verkehrsgünstig gelegen','دارای موقعیت مکانی با دسترسی مناسب')]),
 1208:('eineinhalb','یک و نیم',[('anderthalb Stunden warten','یک ساعت و نیم منتظر ماندن')]),
 1209:('Liste mehrerer Elemente','فهرست موارد',[('eine Auflistung erstellen','فهرستی تهیه کردن')]),
 1211:('leichte Schuhe für Bad und Schwimmbad','دمپایی استخر یا حمام',[('Badelatschen mitnehmen','دمپایی استخر همراه بردن')]),
 1212:('Ort von Bauarbeiten','محل کار ساختمانی',[('eine Baustelle absichern','محوطهٔ ساخت‌وساز را ایمن‌سازی کردن')]),
 1213:('mit Recht oder Befugnis ausgestattet','مجاز یا محق',[('zu einer Rückerstattung berechtigt sein','حق بازپرداخت داشتن')]),
 1215:('ohne Schadenersatz','بدون پرداخت غرامت',[('entschädigungslos enteignet werden','بدون پرداخت غرامت سلب مالکیت شدن')]),
 1216:('durch unerfüllte Erwartungen traurig','سرخورده',[('von der Reise enttäuscht sein','از سفر سرخورده بودن')]),
 1217:('beträchtlich','قابل توجه',[('erhebliche Kosten verursachen','هزینه‌های قابل‌توجه ایجاد کردن')]),
 1218:('wie man es sich gewünscht hatte','مورد انتظار و امید',[('anders als erhofft','برخلاف آنچه امید می‌رفت')]),
 1220:('Ort für den Urlaub','محل گذراندن تعطیلات',[('ein ruhiger Ferienort','محل تعطیلاتی آرام')]),
 1222:('von kleiner Bedeutung oder Menge','ناچیز',[('geringfügige Mängel','نقص‌های جزئی')]),
 1223:('vielbefahrene Hauptstraße','خیابان اصلی پرتردد',[('an einer Hauptverkehrsstraße wohnen','در کنار خیابان پرتردد زندگی کردن')]),
 1224:('Produkt- oder Angebotsverzeichnis','فهرست محصولات',[('im Katalog blättern','کاتالوگ را ورق زدن')]),
 1225:('Blick auf das Meer','چشم‌انداز دریا',[('ein Zimmer mit Meerblick','اتاقی رو به دریا')]),
 1226:('zur Klärung noch einmal fragen','دوباره پرسیدن',[('bei der Rezeption nachfragen','از پذیرش پرس‌وجوی بیشتر کردن')]),
 1227:('Herabsetzung des Preises','کاهش قیمت',[('eine Preisminderung verlangen','کاهش قیمت مطالبه کردن')]),
 1228:('Preis einer Reise','هزینهٔ سفر',[('den Reisepreis erstatten','هزینهٔ سفر را بازپرداخت کردن')]),
 1229:('Anbieter einer Pauschalreise','برگزارکنندهٔ سفر',[('sich an den Reiseveranstalter wenden','به برگزارکنندهٔ سفر مراجعه کردن')]),
 1230:('steile Felsküste','ساحل پرتگاهی',[('an der Steilküste wandern','در کنار ساحل پرتگاهی پیاده‌روی کردن')]),
 1231:('kleiner oder wiederholter Streit','جر و بحث',[('ständige Streitereien','جر و بحث‌های مداوم')]),
 1232:('mehr Buchungen als verfügbare Plätze','بیش‌ازظرفیت رزروشده',[('ein überbuchter Flug','پرواز بیش‌ازظرفیت رزروشده')]),
 1233:('informelle Alltagssprache','زبان محاوره',[('in der Umgangssprache üblich','رایج در زبان محاوره')]),
 1234:('etwas Unangenehmes','دردسر یا ناراحتی',[('sich für Unannehmlichkeiten entschuldigen','برای ناراحتی‌های پیش‌آمده عذرخواهی کردن')]),
 1236:('nicht rechtzeitig','دیررسیده یا با تأخیر',[('verspätet ankommen','با تأخیر رسیدن')]),
 1237:('einen Zugang versperrend','راه را مسدود کرده',[('den Eingang verstellen','جلوی ورودی را گرفتن')]),
 1238:('Zeit des Wartens','زمان انتظار',[('lange Wartezeiten vermeiden','از زمان‌های انتظار طولانی جلوگیری کردن')]),
 1239:('etwas Gegebenes wieder verlangen','پس‌مطالبه کردن',[('die Anzahlung zurückfordern','پیش‌پرداخت را پس‌مطالبه کردن')]),
 1242:('Landung während eines Fluges','فرود بین‌راهی',[('eine Zwischenlandung in Wien','توقف و فرود میان‌راهی در وین')]),
 1243:('weit entfernt von anderen Orten','دورافتاده',[('ein abgelegenes Dorf','روستایی دورافتاده')]),
 1244:('über etwas als Ausstattung verfügen','مجهز به چیزی بودن',[('mit Klimaanlage ausgestattet sein','به دستگاه تهویهٔ مطبوع مجهز بودن')]),
 1246:('Unterkunftskomplex für Feriengäste','مجتمع اقامتی',[('in einer Ferienanlage wohnen','در یک مجتمع تعطیلاتی اقامت داشتن')]),
 1247:('Belästigung durch Lärm','مزاحمت صوتی',[('sich über Lärmbelästigung beschweren','از مزاحمت صوتی شکایت کردن')]),
 1248:('gemietetes oder geliehenes Auto','خودروی اجاره‌ای',[('einen Leihwagen mieten','خودرویی اجاره کردن')]),
 1249:('nicht aufdringlich','بدون تحمیل و جلب توجه',[('unaufdringlich auftreten','بدون تحمیل خود رفتار کردن')]),
 1250:('für einen Zweck geeignet','مناسب و کاربردی',[('eine zweckmäßige Einrichtung','چیدمان کاربردی')]),
 1251:('Gruppe gleichartiger Dinge','دسته یا رده',[('in verschiedene Kategorien einteilen','به دسته‌های مختلف تقسیم کردن')]),
 1252:('auf Richtigkeit kontrollieren','بررسی صحت',[('die Angaben überprüfen','درستی اطلاعات را بررسی کردن')]),
 1253:('Zentrum für verschiedene Dienstleistungen','مرکز خدمات',[('im Dienstleistungszentrum arbeiten','در مرکز خدمات کار کردن')]),
 1255:('unangenehm nasses und trübes Wetter','هوای نمناک و بد',[('bei Schmuddelwetter zu Hause bleiben','در هوای بارانی و نامطبوع در خانه ماندن')]),
 1256:('männlicher Matrose','ملوان مرد',[('ein erfahrener Seemann','دریانوردی باتجربه')]),
 1258:('jemanden irgendwo finden','کسی را در جایی یافتن',[('jemanden zu Hause antreffen','کسی را در خانه پیدا کردن')]),
 1259:('mit einer Last versehen','بارگیری کردن',[('ein Schiff mit Containern beladen','کشتی را با کانتینر بارگیری کردن')]),
 1260:('Straße mit Einkaufsgeschäften','خیابان خرید',[('durch die Einkaufsstraße bummeln','در خیابان خرید قدم زدن')]),
 1261:('geschmackvoll und stilvoll','شیک و خوش‌سلیقه',[('elegant gekleidet sein','شیک لباس پوشیده بودن')]),
 1263:('etwas in einem Gespräch nennen','اشاره کردن',[('etwas beiläufig erwähnen','گذرا به چیزی اشاره کردن')]),
 1264:('Markt für frischen Fisch','بازار ماهی',[('frischen Fisch auf dem Fischmarkt kaufen','از بازار ماهی، ماهی تازه خریدن')]),
 1265:('auf dem neuesten Stand der Technik','بسیار مدرن',[('hochmodern ausgestattet','مجهز به فناوری بسیار پیشرفته')]),
 1267:('äußere Begrenzung','لبه یا حاشیه',[('am Rand der Stadt','در حاشیهٔ شهر')]),
 1268:('nur schwach beleuchtet','کم‌نور',[('in schummrigem Licht','در نور کم و نیمه‌تاریک')]),
 1269:('Schiff mit Segeln','کشتی بادبانی',[('mit einem Segelschiff reisen','با کشتی بادبانی سفر کردن')]),
 1270:('Morgen eines Sonntags','صبح یکشنبه',[('am frühen Sonntagmorgen','صبح زود یکشنبه')]),
 1271:('große Eingangsöffnung','دروازه',[('durch das Tor gehen','از دروازه عبور کردن')]),
 1273:('Aufforderung zum Aufbruch','بزن بریم',[('Auf geht’s! Wir fahren los.','بزن بریم! راه می‌افتیم.')]),
 1274:('Ausflug zum Erkunden','گردش کشف مکان‌های تازه',[('auf Entdeckungstour gehen','به گردش و کشف جاهای تازه رفتن')]),
 1275:('eine feste Position gewinnen','جا افتادن',[('sich am Markt etablieren','در بازار جایگاه ثابتی پیدا کردن')]),
 1276:('ungewöhnlich und auffällig','غیرمعمول و چشمگیر',[('ein extravaganter Stil','سبکی پرزرق‌وبرق و غیرمعمول')]),
 1277:('wirtschaftlicher Schwerpunkt für Finanzdienstleistungen','مرکز مالی',[('ein internationales Finanzzentrum','مرکز مالی بین‌المللی')]),
 1278:('Stadt mit Hafen','شهر بندری',[('eine bedeutende Hafenstadt','شهری بندری و مهم')]),
 1279:('Austausch von Waren','تجارت',[('Handel mit Waren treiben','با کالاها تجارت کردن')]),
 1280:('historisches kaufmännisches Büro','دفتر بازرگانی تاریخی',[('in einem alten Kontor arbeiten','در دفتر بازرگانی قدیمی کار کردن')]),
 1281:('Unternehmen im Medienbereich','شرکت رسانه‌ای',[('eine Medienfirma gründen','شرکت رسانه‌ای تأسیس کردن')]),
 1283:('Anlage, in der Tiere gehalten werden','پارک حیوانات',[('einen Tierpark besuchen','از پارک حیوانات دیدن کردن')]),
 1284:('sich verändern','دگرگون شدن',[('sich im Laufe der Zeit wandeln','در گذر زمان تغییر کردن')]),
 1286:('für jemanden frei halten','رزرو کردن',[('einen Tisch reservieren','میز رزرو کردن')]),
 1287:('zum Zielort hinreisen','به مقصد سفر رسیدن',[('mit dem Zug anreisen','با قطار به مقصد سفر کردن')]),
 1288:('Bestätigung einer Angabe oder Buchung','تأیید',[('eine schriftliche Bestätigung erhalten','تأییدیهٔ کتبی دریافت کردن')]),
 1289:('mit Klimaanlage ausgestattet','دارای تهویهٔ مطبوع',[('ein klimatisiertes Zimmer','اتاق مجهز به تهویهٔ مطبوع')]),
 1290:('Dokument einer bestätigten Reservierung','تأییدیهٔ رزرو',[('die Reservierungsbestätigung vorlegen','تأییدیهٔ رزرو را ارائه کردن')]),
 1291:('durch Nachfragen erfahren','با پرس‌وجو فهمیدن',[('die Öffnungszeiten erfragen','ساعات کاری را بپرسید و به دست آوردن')]),
 1292:('im Wechsel','به‌نوبت',[('abwechselnd fahren und pausieren','یکی در میان رانندگی و استراحت کردن')]),
 1293:('nicht vorhanden','غایب یا موجودنبودن',[('fehlende Unterlagen nachreichen','مدارک ناقص را بعداً ارائه کردن')]),
 1294:('Rundreise mit einem Verkehrsmittel','گشت با وسیلهٔ نقلیه',[('eine Stadtrundfahrt machen','گشت شهری رفتن')]),
 1296:('kurzer Umweg für einen Besuch','سرزدن کوتاه میان راه',[('einen Abstecher nach Lübeck machen','در مسیر، سر کوتاهی به لوبک زدن')]),
 1298:('nach einer Pause wieder mit Kraft','نیروگرفته',[('frisch gestärkt weiterfahren','با نیروی تازه به مسیر ادامه دادن')]),
 1300:('Theaterperson für die technische Ablaufkoordination','مسئول هماهنگی پشت صحنه',[('als Inspizient arbeiten','به‌عنوان مسئول هماهنگی صحنه کار کردن')]),
 1301:('Buch mit Kochrezepten','کتاب آشپزی',[('ein Rezept im Kochbuch finden','دستور غذایی را در کتاب آشپزی پیدا کردن')]),
 1304:('geradezu, in vollem Sinn','به معنای واقعی کلمه',[('regelrecht begeistert sein','واقعاً شیفته و هیجان‌زده بودن')]),
 1306:('begeistert erzählen','با شور و شوق تعریف کردن',[('von der Reise schwärmen','با اشتیاق از سفر تعریف کردن')]),
 1307:('Fest für viele Menschen','جشن مردمی',[('ein Volksfest besuchen','در جشنوارهٔ مردمی شرکت کردن')]),
 1308:('Anfahrt zu einem Ziel','راه رسیدن به مقصد',[('eine unkomplizierte Anreise','مسیر رسیدن ساده و بی‌دردسر')]),
 1309:('Fachperson für Arzneimittel in der Apotheke','داروساز متخصص',[('sich beim Apotheker beraten lassen','از داروساز مشورت گرفتن')]),
 1311:('Wissenschaft von Sternen und Himmelskörpern','اخترشناسی',[('sich für Astronomie interessieren','به اخترشناسی علاقه داشتن')]),
 1313:('eine verstorbene Person bestatten','به خاک سپردن',[('einen Verstorbenen beisetzen','متوفی را به خاک سپردن')]),
 1314:('durch ein Gebiet reisen','در ناحیه‌ای سفر کردن',[('ein Land bereisen','در کشوری سفر کردن و جاهای مختلفش را دیدن')]),
 1315:('sehr erfolgreich verkauftes Werk','اثر پرفروش',[('einen Bestseller schreiben','کتابی پرفروش نوشتن')]),
 1316:('Wissenschaft von Pflanzen','گیاه‌شناسی',[('Botanik studieren','گیاه‌شناسی تحصیل کردن')]),
 1317:('staatliche Person im auswärtigen Dienst','دیپلمات',[('einen Diplomaten entsenden','دیپلماتی اعزام کردن')]),
 1318:('aus einem Nachlass erhalten','به ارث بردن',[('ein Haus erben','خانه‌ای را به ارث بردن')]),
 1319:('ein Gebiet gründlich untersuchen','اکتشاف و شناسایی',[('die Umgebung erkunden','محیط اطراف را کشف و بررسی کردن')]),
 1321:('Jahr nach dem genannten Jahr','سال بعد',[('im darauffolgenden Folgejahr','در سالِ پس از آن')]),
 1322:('Reise zur wissenschaftlichen Forschung','سفر پژوهشی',[('eine Forschungsreise unternehmen','سفری پژوهشی انجام دادن')]),
 1323:('Lehre von Räumen und Erde','جغرافیا',[('Geografie unterrichten','جغرافیا تدریس کردن')]),
 1324:('Wissenschaft vom Aufbau der Erde','زمین‌شناسی',[('Geologie studieren','زمین‌شناسی تحصیل کردن')]),
 1326:('sechsbeiniges Gliedertier','حشره',[('ein Insekt bestimmen','گونهٔ یک حشره را شناسایی کردن')]),
 1327:('aus mehreren Bänden bestehend','چندجلدی',[('ein mehrbändiges Werk','اثری چندجلدی')]),
 1328:('Person, die zusammen mit anderen etwas gründet','هم‌بنیان‌گذار',[('Mitbegründer einer Organisation','هم‌بنیان‌گذار یک سازمان')]),
  1329:('Person, die die Natur wissenschaftlich untersucht','طبیعت‌پژوه',[('als Naturforscher arbeiten','به‌عنوان طبیعت‌پژوه کار کردن')]),
 1330:('Gegenstand aus der Natur','شیء طبیعی',[('Naturgegenstände sammeln','اشیای طبیعی جمع کردن')]),
 1332:('jemanden achten','احترام گذاشتن',[('die Meinung anderer respektieren','به نظر دیگران احترام گذاشتن')]),
 1333:('Person, die Sprachen untersucht','زبان‌پژوه',[('als Sprachforscher arbeiten','به‌عنوان زبان‌پژوه کار کردن')]),
 1334:('staatlich ausgerichtete Beisetzung','خاکسپاری رسمی دولتی',[('ein Staatsbegräbnis ausrichten','مراسم خاکسپاری دولتی برگزار کردن')]),
 1336:('jenseits eines bestimmten Umfangs','فراتر از یک حد',[('über das normale Maß hinaus','فراتر از حد معمول')]),
 1338:('wissenschaftliche Untersuchung von Vulkanen','آتشفشان‌شناسی',[('Vulkanologie studieren','آتشفشان‌شناسی خواندن')]),
 1339:('Wissenschaft von Tieren','جانورشناسی',[('Zoologie studieren','جانورشناسی تحصیل کردن')]),
 1340:('bei jeder wiederholten Bedingung','هر بار که',[('immer wenn es regnet','هر وقت باران می‌بارد')]),
}
# Sense-split, high-risk lemmas: each sense gets its own combinations and its own example route.
MULTI={
 1157:[('Souvenir, Erinnerungsstück','یادگاری',[('ein Andenken mitbringen','سوغاتی یا یادگاری آوردن')]),('Gedenken an eine Person','یاد و خاطرهٔ شخص',[('jemandes Andenken in Ehren halten','یاد کسی را گرامی داشتن')])],
 1162:[('kleines Hotel für Gäste','مهمان‌خانه',[('in einer Pension übernachten','در مهمان‌خانه‌ای شب ماندن')]),('regelmäßiges Ruhegehalt','مستمری بازنشستگی',[('eine Pension beziehen','مستمری بازنشستگی گرفتن')])],
 1163:[('wertvoller Fund, Kostbarkeit','گنج',[('einen Schatz entdecken','گنجی کشف کردن')]),('liebevolle Anrede','عزیزم',[('mein Schatz','عزیز من')])],
 1164:[('kurzer Ausflug','سفر کوتاه',[('einen Trip nach Prag machen','سفر کوتاهی به پراگ داشتن')]),('Rauscherlebnis im Drogenkontext','تجربهٔ نشئگی',[('auf einem Trip sein (Drogenkontext)','در حالت نشئگی بودن (بافت مواد مخدر)')])],
 1167:[('zurück an den alten Platz legen','سر جایش بازگذاشتن',[('das Buch zurücklegen','کتاب را سر جایش برگرداندن')]),('Geld sparen','پس‌انداز کردن',[('monatlich Geld zurücklegen','هر ماه مقداری پول پس‌انداز کردن')]),('eine Strecke absolvieren','مسافت پیمودن',[('viele Kilometer zurücklegen','کیلومترهای زیادی پیمودن')])],
 1183:[('Tun oder Tat','عمل',[('eine unüberlegte Handlung','اقدامی نسنجیده')]),('Geschehen in einem Buch oder Film','پیرنگ',[('die Handlung eines Romans','پیرنگ یک رمان')]),('Geschäft, v. a. in Zusammensetzungen','فروشگاه',[('eine Buchhandlung eröffnen','کتاب‌فروشی افتتاح کردن')])],
 1194:[('gute Nutzung einer Gelegenheit','خوب استفاده کردن',[('eine Chance ausnutzen','از فرصتی استفاده کردن')]),('zum eigenen Vorteil missbrauchen','سوءاستفاده کردن',[('jemanden ausnutzen','از کسی سوءاستفاده کردن')])],
 1197:[('Gewächse in den Boden setzen','کاشتن',[('einen Baum pflanzen','درختی کاشتن')])],
 1206:[('Fahrdienst zwischen Orten','ترانسفر مسافر',[('den Flughafentransfer organisieren','سرویس انتقال فرودگاهی ترتیب دادن')]),('Geldübertragung','انتقال پول',[('der Transfer von Geld','انتقال پول')]),('Wechsel eines Sportlers','نقل و انتقال بازیکن',[('der Transfer eines Spielers','انتقال یک بازیکن')])],
 1210:[('jemanden nicht teilnehmen lassen','محروم کردن یا بیرون گذاشتن',[('jemanden von einer Veranstaltung ausschließen','کسی را از رویدادی کنار گذاشتن')]),('Unmöglichkeit feststellen','منتفی دانستن',[('einen Fehler ausschließen','احتمال خطا را منتفی دانستن')])],
 1214:[('ankommen oder empfangen werden','وصول شدن',[('eine Beschwerde geht ein','شکایتی وصول می‌شود')]),('sich mit etwas beschäftigen','به موضوعی پرداختن',[('auf eine Frage eingehen','به پرسشی پرداختن')]),('kleiner werden beim Waschen','آب رفتن',[('beim Waschen eingehen','در شست‌وشو آب رفتن')]),('zugrunde gehen','از بین رفتن',[('eine Pflanze geht ein','گیاهی از بین می‌رود')]),('eine Verpflichtung übernehmen','وارد تعهد شدن',[('einen Vertrag eingehen','قراردادی منعقد کردن')])],
 1221:[('Flugzeug, umgangssprachlich','هواپیما در گفتار روزمره',[('den Flieger verpassen','از هواپیما جا ماندن')]),('Person, die fliegt','خلبان یا پروازکننده',[('ein erfahrener Flieger','فرد پروازکنندهٔ باتجربه')])],
 1240:[('etwas zurückbekommen wollen','پس‌خواستن',[('sein Geld zurückhaben wollen','خواستنِ پس گرفتن پول خود')])],
 1245:[('möbliert oder gestaltet','مبله و چیده‌شده',[('modern eingerichtet sein','چیدمان مدرن داشتن')]),('technisch vorbereitet','تنظیم یا راه‌اندازی‌شده',[('ein eingerichtetes Benutzerkonto','حساب کاربری راه‌اندازی‌شده')])],
 1257:[('gehoben und stilvoll','اعیانی و باوقار',[('ein vornehmes Hotel','هتلی اعیانی')]),('moralisch edel','بزرگ‌منش و شریف',[('eine vornehme Geste','رفتاری بزرگ‌منشانه')])],
 1262:[('Ladung ausladen','بار تخلیه کردن',[('ein Schiff entladen','کشتی را تخلیهٔ بار کردن')]),('Waffe ungefährlich machen','سلاح را خالی کردن',[('eine Waffe entladen','سلاح را خالی کردن')]),('elektrische Ladung abgeben','تخلیهٔ الکتریکی',[('einen Akku vollständig entladen','باتری را کاملاً تخلیه کردن')])],
 1272:[('Geld und Besitz','دارایی و ثروت',[('ein großes Vermögen erben','دارایی هنگفتی به ارث بردن')]),('Fähigkeit zu etwas','توانایی',[('das Vermögen, Probleme zu lösen','توانایی حل مسائل')])],
 1282:[('überdachte Einkaufsgalerie','پاساژ یا گذرگاه سرپوشیده',[('durch eine Passage schlendern','در پاساژی قدم زدن')]),('Abschnitt eines Textes','بخشی از متن',[('eine Passage im Text markieren','بخشی از متن را علامت زدن')]),('Durchfahrt oder Durchgang','عبور یا گذر',[('die Passage durch eine Meerenge','عبور از یک تنگهٔ دریایی')])],
 1285:[('mit Farbe überziehen','رنگ زدن',[('die Wände streichen','دیوارها را رنگ زدن')]),('aus einer Liste entfernen','خط زدن',[('einen Termin streichen','یک قرار را حذف کردن')]),('mit der Hand liebkosen','نوازش کردن',[('jemandem über das Haar streichen','موهای کسی را نوازش کردن')])],
 1295:[('Fahrkarte für einen Tag','بلیت روزانه',[('eine Tageskarte für die Bahn','بلیت روزانهٔ قطار')]),('wechselndes Speisenangebot','منوی روز',[('die Tageskarte des Restaurants','منوی روز رستوران')])],
 1297:[('eine Gruppe leiten','رهبری کردن',[('eine Gruppe anführen','گروهی را رهبری کردن')]),('als Grund nennen','دلیلی بیان کردن',[('ein Argument anführen','استدلالی مطرح کردن')])],
 1299:[('stark leuchtend oder auffällig','تند و خیره‌کننده',[('grelles Licht','نور خیره‌کننده')]),('unangenehm schrill','گوش‌خراش',[('ein greller Schrei','جیغی گوش‌خراش')])],
 1303:[('Anteil oder Verhältnis','نسبت یا میزان',[('eine hohe Erfolgsquote','نرخ موفقیت بالا')]),('verbindlich festgelegter Anteil','سهمیه',[('eine festgelegte Quote erfüllen','سهمیهٔ تعیین‌شده را رعایت کردن')]),('Zuschauerzahlen','میزان بیننده',[('hohe Einschaltquoten erzielen','آمار بینندهٔ بالا به دست آوردن')])],
 1305:[('Volksfest mit Buden und Fahrgeschäften','بازار مکاره یا شهربازی',[('über den Rummel bummeln','در بازار مکاره قدم زدن')]),('Wirbel und Aufregung','سر و صدا و هیاهو',[('viel Rummel um etwas machen','دربارهٔ چیزی هیاهوی زیادی به راه انداختن')])],
 1310:[('beruflicher Titel nach staatlicher Prüfung','دارندهٔ عنوان آزمون دولتی',[('als Assessor im öffentlichen Dienst','به‌عنوان دارندهٔ عنوان اسسور در بخش دولتی')])],
 1312:[('ein Thema aufnehmen','موضوعی را مطرح یا پیگیری کردن',[('ein Thema aufgreifen','موضوعی را مطرح کردن')]),('eine Person polizeilich ergreifen','بازداشت کردن',[('einen Verdächtigen aufgreifen','فرد مظنونی را دستگیر کردن')])],
 1325:[('wichtigstes wissenschaftliches oder künstlerisches Werk','اثر اصلی',[('das Hauptwerk eines Autors','اثر اصلی یک نویسنده')]),('zentrales Werk einer Firma','کارخانهٔ مرکزی',[('das Hauptwerk des Herstellers','کارخانهٔ اصلی تولیدکننده')])],
 1335:[('berufliche Tätigkeit für den Staat','خدمت دولتی',[('in den Staatsdienst eintreten','وارد خدمت دولتی شدن')])],
 1337:[('räumliche Umgebung','محیط پیرامونی',[('das unmittelbare Umfeld','محیط اطراف نزدیک')]),('soziale Kontakte und Verhältnisse','محیط اجتماعی',[('das soziale Umfeld','محیط اجتماعی')])],
 1341:[('Ablauf oder Prozess','روند یا فرایند',[('einen Vorgang dokumentieren','یک فرایند را مستندسازی کردن')]),('Verwaltungssache','پروندهٔ اداری',[('einen Vorgang bearbeiten','به یک پرونده رسیدگی کردن')])],
}
# Do not use a full sentence as a combination; connectors alone do not need forced combinations.
SPECS.pop(1273,None)
SPECS.pop(1340,None)
SPECS[1321]=('Jahr nach dem betreffenden Jahr','سال بعد',[('im Folgejahr','در سال بعد')])
SPECS[1291]=('durch Nachfragen erfahren','با پرس‌وجو فهمیدن',[('die Öffnungszeiten erfragen','ساعات کاری را با پرس‌وجو به دست آوردن')])
MULTI[1197].append(('Fahne oder Symbol aufrichten','برافراشتن نماد یا پرچم',[('eine Fahne auf den Gipfel pflanzen','پرچمی بر فراز قله برافراشتن')]))
MULTI[1210].append(('ein einzelnes Element ausnehmen','مستثنا کردن',[('bestimmte Leistungen ausschließen','خدمات مشخصی را مستثنا کردن')]))
MULTI[1257].append(('besonders wichtig (gehoben)','مهم و برجسته (ادبی)',[('eine vornehme Aufgabe','وظیفه‌ای برجسته یا مهم')]))
MULTI[1262].append(('Gefühle explosionsartig ausbrechen lassen','خشم یا تنش را بروز دادن',[('sich in einem Schrei entladen','در قالب فریادی تخلیه شدن')]))
MULTI[1297].append(('an erster Stelle stehen','در صدر فهرست بودن',[('die Bestsellerliste anführen','در صدر فهرست پرفروش‌ها بودن')]))
MULTI[1214][0]=('ankommen oder empfangen werden','وصول شدن',[('bei der Rezeption eingehen','به پذیرش وصول شدن')])
MULTI[1214][3]=('zugrunde gehen','از بین رفتن',[('bei Trockenheit eingehen','بر اثر خشکی از بین رفتن')])
# 'Buchhandlung' is a distinct compound, not a collocation with 'die Handlung'; retain the sense but do not force a false lexical combination.
MULTI[1183][2]=('Geschäft, v. a. in Zusammensetzungen','فروشگاه (بیشتر در واژه‌های مرکب)',[])
# Every example in a multi-sense network receives an explicit meaning route, not a guessed global one.
ROUTE_MULTI={
1157:[0,1,0],1162:[0,1,1],1163:[0,1,1],1164:[0,0,1],1167:[2,1,0,0],
1183:[0,0,1,1],1194:[0,1],1197:[0,0,1],1206:[0,0,1,2],1210:[2,1,0,0],
1214:[0,0,1,2],1221:[0,0,1,1],1240:[0,0,0,0,0],1245:[0,0,1],1257:[0,2,1],
1262:[0,0,2,1,1,3],1272:[0,0,1],1282:[0,0,1],1285:[1,1,0,2],
1295:[0,0,1],1297:[2,1,0,1],1299:[0,1,1],1303:[2,0,1,1],1305:[0,0,1],
1310:[0,0,0],1312:[0,0,1,1],1325:[0,0,1,1],1335:[0,0,0],1337:[0,1,0],1341:[0,0,1,1]
}
ROUTE_EXISTING={
1159:[2,1],1172:[0,0],1193:[0,0],1219:[0,0],1235:[0,0],1254:[0,0],1266:[0,0],1331:[0,0]}
NEW_EXAMPLES={
'die Kochshow':[
 ('In der Kochshow bereiten drei Köche ein regionales Gericht zu.','در برنامهٔ نمایشی آشپزی، سه آشپز یک غذای محلی آماده می‌کنند.'),
 ('Die neue Kochshow verbindet Rezepte mit einem Wettbewerb.','برنامهٔ جدید آشپزی، دستورهای غذایی را با مسابقه ترکیب می‌کند.')],
'die Kochsendung':[
 ('In der Kochsendung erklärt die Moderatorin jeden Arbeitsschritt.','در برنامهٔ آشپزی، مجری هر مرحلهٔ کار را توضیح می‌دهد.'),
 ('Ich habe das Rezept in einer Kochsendung gesehen.','من این دستور غذا را در یک برنامهٔ آشپزی دیدم.')],
}
MULTI_SPECIAL={
'die Kochshow':[('unterhaltsame Fernsehshow über Kochen','برنامهٔ نمایشی آشپزی',[('eine Kochshow moderieren','اجرای یک برنامهٔ نمایشی آشپزی را بر عهده داشتن'),('an einer Kochshow teilnehmen','در یک برنامهٔ نمایشی آشپزی شرکت کردن')])],
'die Kochsendung':[('Radio- oder Fernsehsendung über Kochen','برنامهٔ رادیویی یا تلویزیونی آشپزی',[('eine Kochsendung ansehen','یک برنامهٔ آشپزی تماشا کردن'),('in einer Kochsendung ein Rezept vorstellen','دستور غذایی در برنامهٔ آشپزی معرفی کردن')])],
}
SCOPED_SOURCES={
'das Andenken':{'url':'https://www.duden.de/rechtschreibung/Andenken','scope':'plural only for souvenir sense; remembrance without plural; two distinct meanings retained'},
'die Pension':{'url':'https://www.duden.de/rechtschreibung/Pension','scope':'distinct accommodation vs retirement benefit meanings'},
'zurückhaben':{'url':'https://www.duden.de/konjugation/zurueckhaben','scope':'present hatte zurück, perfect zurückgehabt; not full-card attestation'},
'der Ozeanriese':{'url':'https://www.duden.de/rechtschreibung/Ozeanriese','scope':'very large ocean liner; scoped lexical meaning'},
'die Kochshow':{'url':'https://www.duden.de/rechtschreibung/Kochshow','scope':'television cooking show, separate from general Kochsendung'},
'die Kochsendung':{'url':'https://www.duden.de/rechtschreibung/Fernsehkoch','scope':'Kochsendung used in Duden example; radio/TV usage separately described, not full Duden headword validation'},
}


def create_network(card,spec,marker):
 # L09P2 scope may be 1 or more senses, with stable IDs (never split a lemma into extra flashcards).
 new=[]
 for i,(de,fa,combos) in enumerate(spec,1):
  assert de.strip() and fa.strip() and (combos or (card['source_ordinal']==1183 and i==3))
  assert len({norm(x[0]) for x in combos})==len(combos)
  assert not any(re.search(r'\b(?:geht|läuft|kommt|hat|ist|sind|gibt|macht|kann|wird)\b',d,flags=re.I) for d,f in combos), (card['source_ordinal'],combos)
  new.append({'sense_id':card['preview_card_id']+f':L09P2:S{i}',
   'sense_de':de,'sense_fa':fa,'usage_distinction_de':'',
   'Synonyme':[],'Antonyme':[],'Wortfamilie':[],'Verwandte_Woerter_KEINE_Synonyme':[],
   'Kombinationen_DE_FA':[{'de':d,'fa':f} for d,f in combos],
   'lexical_relation_policy':'STRICT_NO_FORCED_SYNONYMS_ANTONYMS_WORD_FAMILY; SENSE_LINKED_COLLOCATIONS',
   'source':'L09_PHASE2_MANUAL_EDITORIAL_SCOPED_LEARNER_ENRICHMENT_NOT_PUBLISHER_REIMPORT',
   'status':'PENDING_DE_FA_SENSE_COLLOCATION_EDITORIAL_QA'})
 return new

def finite_gate(cards):
 D={'der','die','das','ein','eine','einen','einem','einer','diese','dieser','dieses','jener','jene'}
 V={'reicht','entscheidet','koordiniert','läuft','prüft','schreibt','bringt','bestimmt','öffnet','organisiert','führt','hat','ist','sind','steht','arbeitet','verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt','hält','macht','kann','wird','werden','nimmt','bietet','spricht'}
 issues=[];cnt=0
 for c in cards:
  for n in nets(c):
   for x in n.get('Kombinationen_DE_FA',[]) or []:
    cnt+=1;w=re.findall(r'\w+',x['de'])
    if len(w)>=4 and w[0].casefold() in D and w[1][0].isupper() and w[2].casefold() in V:
     issues.append({'lesson':c['lesson'],'ordinal':c['source_ordinal'],'lemma':c['front']['base_headword_de'],'de':x['de']})
 return cnt,issues

def run():
 OUT.mkdir(parents=True,exist_ok=True)
 assert sha(SRC.read_bytes())==EXPECTED_ZIP
 with zipfile.ZipFile(SRC) as z:
  assert z.testzip() is None
  data={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
  manifest={n:dig for dig,n in (line.split('  ',1) for line in z.read('SHA256SUMS.txt').decode().splitlines() if line)}
  assert set(data)==set(manifest) and all(sha(v)==manifest[k] for k,v in data.items())
 assert sha(data[MAIN])==EXPECTED_MAIN and sha(data[MAP])==EXPECTED_MAP
 old=[json.loads(r) for r in data[MAIN].splitlines() if r]
 assert len(old)==1571 and len({c['preview_card_id'] for c in old})==1571
 assert len(data[MAP].decode('utf-8-sig').splitlines())-1==1548
 lesson=[c for c in old if c['lesson']=='L09'];assert len(lesson)==185
 other={c['preview_card_id']:js(c) for c in old if c['lesson']!='L09'}
 assert {j for c in lesson for j in c['linked_original_source_ordinals']}==set(range(1157,1342))
 assert len([c for c in lesson if c['source_ordinal']==1302])==2
 assert len([c for c in lesson if c['source_ordinal']==1240 and c['linked_original_source_ordinals']==[1240,1241]])==1
 current=copy.deepcopy(old)
 new_lexical_counts=collections.Counter();dispositions=[];diffs=[];new_examples=0;status_fixed=0;routes_fixed=0;dupes=0;full_clause_repaired=0;altered=[]
 mapping=(set(SPECS)|set(MULTI))
 assert set(SPECS).isdisjoint(set(MULTI))
 assert mapping.issubset({c['source_ordinal'] for c in lesson})
 assert set(ROUTE_MULTI)==set(MULTI)
 for idx,c in enumerate(current):
  if c['lesson']!='L09':continue
  before=copy.deepcopy(c)
  o=c['source_ordinal'];h=c['front']['base_headword_de'];b=c['back'];notes=[]
  e0=examples(c)
  for e in e0:
   if not e.get('status'):
    e['status']=PENDING;e['L09_phase2_status_note']='MISSING_STATUS_RESTORED_AS_PENDING_NOT_APPROVED';status_fixed+=1
  if h in NEW_EXAMPLES:
   assert not e0
   for d,f in NEW_EXAMPLES[h]:b.setdefault('existing_examples_de_fa_pending_qa',[]).append(ex(d,f,'L09_PHASE2_EDITORIAL_NEW_PAIR_PENDING_QA'));new_examples+=1
   notes.append('ADDED_TWO_DISTINCT_DE_FA_EXAMPLES')
  if o==1157:
   existing=b['existing_examples_de_fa_pending_qa'];addition=b['additional_examples_de_fa_pending_qa']
   assert len(existing)==3 and len(addition)==1 and norm(existing[1]['de'])==norm(addition[0]['de'])
   e=existing[1];e.setdefault('fa_alternatives',[]).append(addition[0]['fa'])
   e['L09_phase2_duplicate_resolution']='MERGED_IDENTICAL_GERMAN_EXAMPLE_WITH_PERSIAN_ALT_PRESERVED'
   addition.clear();dupes+=1;notes.append('ANDENKEN_DUPLICATE_MERGED_ALT_FA_RETAINED')
  if o==1266:
   n=nets(c);assert len(n)==1;comb=n[0]['Kombinationen_DE_FA'];assert len(comb)==2 and comb[0]['de']=='ein Ozeanriese läuft im Hafen ein'
   oldcomb=comb[0].copy();comb[0]={'de':'einen Ozeanriesen im Hafen bestaunen','fa':'یک کشتی عظیم اقیانوس‌پیما را در بندر تماشا کردن'}
   # preserve the pedagogically valuable full clause under examples, no broken back copying
   b['additional_examples_de_fa_pending_qa'].append(ex('Ein Ozeanriese läuft im Hafen ein.','یک کشتی بزرگ اقیانوس‌پیما وارد بندر می‌شود.','L09_PHASE2_MOVED_FULL_CLAUSE_FROM_COMBINATIONEN_TO_BEISPIELE'))
   new_examples+=1;full_clause_repaired+=1;notes.append('OZEANRIESE_FINITE_CLAUSE_MOVED_TO_EXAMPLE_AND_COLLOCATION_REPLACED')
  if nets(c):
   # Route all existing networks to known sense IDs based on explicit lemma/example context.
   if o in ROUTE_EXISTING:
    rr=ROUTE_EXISTING[o];ee=examples(c);nn=nets(c)
    if o==1266:rr=[0,0,0]
    assert len(rr)==len(ee),(o,len(rr),len(ee))
    for e,k in zip(ee,rr):
     assert k<len(nn)
     if e.get('sense_id')!=nn[k]['sense_id']:
      e['sense_id']=nn[k]['sense_id'];e['sense_routing_status']='L09P2_EXPLICIT_CONTEXTUAL_EDITORIAL_PENDING_FULL_QA';routes_fixed+=1
    notes.append('ROUTED_EXISTING_NETWORK_EXAMPLES_BY_SENSE')
  elif o in MULTI or h in MULTI_SPECIAL:
   spec=MULTI_SPECIAL[h] if h in MULTI_SPECIAL else MULTI[o]
   b['semantic_network_sense_anchored_pending_qa']=create_network(c,spec,'MULTI')
   nn=nets(c);ee=examples(c)
   rr=[0]*len(ee) if h in MULTI_SPECIAL else ROUTE_MULTI[o]
   assert len(rr)==len(ee),(o,h,len(rr),len(ee))
   for e,k in zip(ee,rr):
    assert k<len(nn);e['sense_id']=nn[k]['sense_id'];e['sense_routing_status']='L09P2_MANUALLY_CONTEXT_ROUTED_PENDING_FULL_QA';routes_fixed+=1
   new_lexical_counts['new_networks']+=1;new_lexical_counts['new_sense_blocks']+=len(nn);new_lexical_counts['new_combinations']+=sum(len(n['Kombinationen_DE_FA']) for n in nn)
   notes.append('NEW_MEANING_SCOPED_NETWORK_MULTISENSE' if len(nn)>1 else 'NEW_SINGLE_SENSE_NETWORK')
  elif o in SPECS:
   b['semantic_network_sense_anchored_pending_qa']=create_network(c,[SPECS[o]],'ONE_SENSE')
   nn=nets(c)
   for e in examples(c):
    e['sense_id']=nn[0]['sense_id'];e['sense_routing_status']='L09P2_SINGLE_SENSE_ILLUSTRATION_PENDING_FULL_QA';routes_fixed+=1
   new_lexical_counts['new_networks']+=1;new_lexical_counts['new_sense_blocks']+=1;new_lexical_counts['new_combinations']+=len(SPECS[o][2]);notes.append('NEW_SINGLE_SENSE_NETWORK')
  if h in SCOPED_SOURCES:
   # Reference scoped evidence only for the cited fact; never claim whole-card Duden approval.
   c['L09_phase2_scoped_evidence']=SCOPED_SOURCES[h]
   notes.append('SCOPED_LEXICOGRAPHIC_EVIDENCE_NOT_FULL_CARD_SIGNOFF')
  if c!=before:
   assert c['import_ready'] is False and c['formal_release_approved'] is False
   assert c.get('curated_HOLD_content_disposition_exists')==before.get('curated_HOLD_content_disposition_exists')
   altered.append(o)
   diffs.append({'source_ordinal':o,'headword':h,'card_id':c['preview_card_id'],'before':before,'after':c,'changed_section_topkeys':sorted(k for k in set(c)|set(before) if c.get(k)!=before.get(k))})
  ee=examples(c);nn=nets(c);ids={n['sense_id'] for n in nn};no_status=sum(not e.get('status') for e in ee)
  unrouted=sum(bool(nn) and e.get('sense_id') not in ids for e in ee)
  disp={'source_ordinal':o,'card_id':c['preview_card_id'],'headword':h,'source_links':c['linked_original_source_ordinals'],
        'priority':'P1' if c.get('curated_HOLD_content_disposition_exists') or not ee or no_status or unrouted else ('P2' if nn else 'P3'),
        'bilingual_example_count':len(ee),'sense_network_count':len(nn),'sense_blocks':[{'sense_id':n['sense_id'],'sense_de':n['sense_de'],'combinationen':n.get('Kombinationen_DE_FA',[])} for n in nn],
        'example_statusless_count':no_status,'unrouted_example_count':unrouted,
        'curated_hold_preserved':c.get('curated_HOLD_content_disposition_exists',False),
        'content_saved_primary_changed':c!=before,'edit_reasons':notes,
        'lexical_language_signoff':'PENDING_CASE_LEVEL_QA','release':'BLOCKED_NONIMPORT'}
  dispositions.append(disp)
 assert len(dispositions)==185
 assert len(diffs)==len({d['card_id'] for d in diffs})
 assert len([c for c in current if c['lesson']=='L09'])==185
 assert {c['preview_card_id'] for c in current}=={c['preview_card_id'] for c in old}
 assert all(js(c)==other[c['preview_card_id']] for c in current if c['lesson']!='L09')
 assert data[MAP] and sha(data[MAP])==EXPECTED_MAP
 assert sum(bool(c.get('curated_HOLD_content_disposition_exists')) for c in lesson)==sum(bool(c.get('curated_HOLD_content_disposition_exists')) for c in current if c['lesson']=='L09')==43
 assert all(c['import_ready'] is False and c['formal_release_approved'] is False for c in current)
 l9=[c for c in current if c['lesson']=='L09'];l9e=[e for c in l9 for e in examples(c)]
 assert not [c['preview_card_id'] for c in l9 if not examples(c)]
 assert not [e for e in l9e if not e.get('status') or not e.get('de') or not e.get('fa')]
 assert all(not nets(c) or all(e.get('sense_id') in {n['sense_id'] for n in nets(c)} for e in examples(c)) for c in l9)
 dup=[]
 for c in l9:
  seen=collections.Counter(norm(e['de']) for e in examples(c))
  dup.extend((c['source_ordinal'],k,v) for k,v in seen.items() if v>1)
 assert not dup,dup
 assert all(c['back'].get('Formen_section') is None for c in l9)
 assert all(c['front'].get('forms_rendered_on_front_only') is True for c in l9)
 before_combos,old_finite=finite_gate(old)
 after_combos,remaining_finite=finite_gate(current)
 assert before_combos==870,(before_combos,'expected 870')
 assert after_combos==before_combos+new_lexical_counts['new_combinations']
 assert {(x['lesson'],x['ordinal']) for x in old_finite}=={('L02',158),('L03',232),('L09',1266)}
 assert {(x['lesson'],x['ordinal']) for x in remaining_finite}=={('L02',158),('L03',232)}
 assert len(l9e)==419+new_examples-dupes
 assert len([c for c in current if c['lesson']!='L09'])==1386
 assert len(current)==1571
 # Preserve all old ZIP members; add auditable reports and update only learner main + manifest.
 main_bytes=b''.join(js(c) for c in current)
 data[MAIN]=main_bytes
 report={
 'schema':'aspekte-b1plus-l09-phase2-full-185-card-editorial@1','date':'2026-11-09','status':'L09_PHASE2_EDITORIAL_SAVED_PRIMARY_LEARNER_JSONL_NONIMPORT',
 'input':{'library_owner_id':'libfile_417fe423eb6c8191bb50a3ba7b6f6352','zip_sha256':EXPECTED_ZIP,'primary_sha256':EXPECTED_MAIN,'map_sha256':EXPECTED_MAP},
 'lesson':{'cards_triaged':185,'priorities_from_phase1':{'P1':44,'P2':18,'P3':123},'changed_unique_primary_cards':len(diffs),'unchanged_L09_cards':185-len(diffs),'outside_L09_objects_unchanged':1386,
           'curated_HOLDs_retained':43,'bilingual_examples_before':419,'bilingual_examples_after':len(l9e),'added_new_bilingual_examples':new_examples,
           'duplicates_removed':dupes,'missing_example_statuses_set_PENDING':status_fixed,'sense_example_routes_added_or_fixed':routes_fixed,
           'new_semantic_network_cards':new_lexical_counts['new_networks'],'new_meaning_blocks':new_lexical_counts['new_sense_blocks'],
           'new_bilingual_lexical_combinations':new_lexical_counts['new_combinations'],
           'zero_example_cards_after':0,'missing_statuses_after':0,'unrouted_network_examples_after':0,'same_card_exact_duplicate_DE_examples_after':0,
           'L09_combos_before':21,'L09_combos_after':sum(len(n.get('Kombinationen_DE_FA') or []) for c in l9 for n in nets(c)),
           'finite_clause_cases_L09_after':0,'L09_formen_on_back_count':sum(c['back'].get('Formen_section') is not None for c in l9)},
 'global':{'card_ids_preserved':1571,'other_lessons_unchanged_exact':1386,'original_source_mapping_rows_preserved':1548,
           'global_combinations_before':before_combos,'global_combinations_after':after_combos,
           'global_known_full_finite_clause_cases_before':old_finite,'global_known_full_finite_clause_cases_after':remaining_finite,
           'release_blocked':True,'actual_app_import_tested':False,'formal_release_approved':0},
 'limitations':['All 185 card objects covered by explicit saved-case dispositions; unmodified items remain not approved.',
                'New examples, meaning links, collocations are still PENDING full DE/FA idiomatic contextual QA.',
                'Legacy HOLDs are preserved; the absence of a morphology attestation does not imply forms are wrong.',
                'No independent human reviewer is required by the workflow; legacy status strings are not a request for an outside reviewer.',
                'No real runtime/importer tested. Nonimport until later strict Phase3 gate.'],
 'next':'L09_PHASE3_WHOLE_185_CARD_STRICT_QA_RELEASE_GATE_OR_BLOCKED'
 }
 files={
 'Lessons/L09/L09-PHASE2-185-CARD-EDITORIAL-DISPOSITIONS.jsonl':b''.join(js(d) for d in dispositions),
 'Lessons/L09/L09-PHASE2-ALL-CHANGED-PRIMARY-BEFORE-AFTER.json':pretty(diffs),
 'Lessons/L09/L09-PHASE2-WHOLE-185-CARD-REPORT.json':pretty(report),
 'Lessons/L09/L09-PHASE2-FINITE-CLAUSE-GLOBAL-V4.json':pretty({'before':old_finite,'after':remaining_finite,'count_before':before_combos,'count_after':after_combos,'strict_corpus_gate':'FAIL_2_OLD_NON_L09'}),
 'Lessons/L09/L09-PHASE2-185-CARD-OFFLINE-QA-ONLY.html':('<!doctype html><html lang="de"><meta charset="utf-8"><title>Aspekte B1+ L09 Phase2 185 cards - QA ONLY / NONIMPORT</title><style>body{font:16px system-ui;margin:24px;max-width:1100px}article{border-bottom:1px solid #ddd;padding:12px 0}small{color:#666}ul{margin:.4em 0}li{margin:.2em 0}b{font-weight:650}</style><h1>L09 · 185 Karten · OFFLINE QA ONLY / NONIMPORT</h1>'+''.join('<article><h3>'+html.escape(c['front']['base_headword_de'])+'</h3><p>'+html.escape(c['front']['display_de_provisional'])+' — '+html.escape(c['back']['meanings_fa_provisional'])+'</p><ul>'+''.join('<li><b>'+html.escape(e['de'])+'</b> — '+html.escape(e['fa'])+' <small>'+html.escape(e.get('status',''))+'</small></li>' for e in examples(c))+'</ul><details><summary>Sense-linked combinations</summary>'+''.join('<p><b>'+html.escape(n['sense_de'])+'</b>: '+html.escape(n['sense_fa'])+'</p><ul>'+''.join('<li>'+html.escape(x['de'])+' — '+html.escape(x['fa'])+'</li>' for x in n.get('Kombinationen_DE_FA',[]))+'</ul>' for n in nets(c))+'</details></article>' for c in l9)+'</html>').encode('utf-8'),
 'README-L09-PHASE2-NONIMPORT.md':('Aspekte B1+ L09 Phase2 - 185-card saved-editorial, **NOT IMPORTABLE**. Parent SHA '+EXPECTED_ZIP+'; '+str(len(diffs))+' changed primary cards, '+str(1386)+' outside same, 43 inherited HOLDs remain. Release must stay blocked pending semantic QA and real app import. See exact 185 dispositions, all changed-card before/after, HTML QA-only and global finite-clause v4.\n').encode(),
 'Tools/build_L09_phase2_v1.py':Path(__file__).read_bytes(),
 }
 for name,value in files.items():
  assert name not in data
  data[name]=value
 archive=OUT/'Aspekte-B1plus-L09-PHASE2-WHOLE-185-CARDS-CURATED-NONIMPORT-20261109.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for n in sorted(data):z.writestr(n,data[n])
  z.writestr('SHA256SUMS.txt',''.join(f'{sha(data[n])}  {n}\n' for n in sorted(data)).encode())
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  mm={n:hash_ for hash_,n in (l.split('  ',1) for l in z.read('SHA256SUMS.txt').decode().splitlines())}
  assert set(mm)==set(z.namelist())-{'SHA256SUMS.txt'}
  assert all(sha(z.read(n))==h for n,h in mm.items())
  assert z.read(MAP)==Path('/mnt/data/aspekte_b1plus_l09_phase1/Aspekte-B1plus-L08-PHASE3-157-CARD-QUALITY-GATE-RELEASE-BLOCKED-NONIMPORT-20261109.zip').read_bytes()[:0]+data[MAP]
  assert z.read(MAIN)==main_bytes
 receipt={'archive':str(archive),'sha256':sha(archive.read_bytes()),'bytes':archive.stat().st_size,'members':len(mm)+1,'manifest_entries_verified':len(mm),
          'primary_sha256':sha(main_bytes),'source_map_sha256':sha(data[MAP]),
          'report':report,'unique_changed_ordinals':sorted(set(altered)),'unique_changed_card_ids':[d['card_id'] for d in diffs]}
 (OUT/'L09-PHASE2-REPORT.json').write_bytes(pretty(report))
 (OUT/'L09-PHASE2-VERIFICATION.json').write_bytes(pretty(receipt))
 (OUT/'L09-PHASE2-185-DISPOSITIONS.jsonl').write_bytes(files['Lessons/L09/L09-PHASE2-185-CARD-EDITORIAL-DISPOSITIONS.jsonl'])
 print(json.dumps({'receipt':{k:v for k,v in receipt.items() if k!='report'},'lesson':report['lesson'],'global':report['global']},ensure_ascii=False,indent=2))
 return receipt
if __name__=='__main__':run()