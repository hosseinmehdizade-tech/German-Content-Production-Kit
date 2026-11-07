#!/usr/bin/env python3
"""R17 -> R18: 26 individually authored p02/p03 conclusions in 15 lessons 053-068.
Based exclusively on latest user-curated R17 content, not historical book source.
No change outside the concluding sentence and its translations, grammar, quality metadata.
"""
import json, pathlib, copy, hashlib, collections, re
P=pathlib.Path('/mnt/data/lesen_r18_20261107')
BASE=pathlib.Path('/mnt/data/lesen_r17_20261107/Lesen-Production-Master-v1.3.0-R17-23CONCLUSIONS-TRILINGUAL-CANDIDATE.json')
OUT=P/'Lesen-Production-Master-v1.3.0-R18-26CONCLUSIONS-TRILINGUAL-CANDIDATE.json'
LED=P/'LESEN-R18-26CONCLUSIONS-EDITORIAL-GRAMMAR-LEDGER.json'
BASESHA='593deb6e5ec7cdba2d95f7445589ae5bf6cf17750eb0f8cdbb9c3f4f1a605ad7'
sha=lambda b:hashlib.sha256(b).hexdigest()
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert sha(BASE.read_bytes())==BASESHA
A=json.loads(BASE.read_text());B=copy.deepcopy(A)
G={'p02':'Dadurch kann ein Nutzen entstehen, der über den unmittelbaren Einzelfall hinausgeht.',
   'p03':'Ein Vorteil auf der einen Seite kann also durchaus neue Probleme auf der anderen Seite erzeugen.'}
# Individually composed German end sentences, grounded in each section's two prior sentences.
# Twelve of the 26 end sentences retain already-specific FA/EN? The actual validated count is seven.
E={
 53:{'p02':'Gute Bildung verbindet fachliches Wissen mit Fähigkeiten, die weit über das bloße Speichern von Informationen hinausgehen.'},
 54:{'p02':'Zufall und Vorbereitung ergänzen einander gerade bei Menschen, die unerwartete Möglichkeiten erkennen und ergreifen.',
     'p03':'Wer Karriere nur als Ergebnis des Zufalls versteht, unterschätzt leicht, dass Vorbereitung, Entscheidungen und Ausdauer ebenfalls wichtig sind.'},
 55:{'p02':'Dauerhafter Stress lässt sich besser begrenzen, wenn Lernende ihre Zeit realistisch planen und Pausen einlegen.',
     'p03':'Ein gewisses Maß an Druck kann manche Menschen kurzfristig aktivieren, während anhaltende Belastung das Lernen erschwert.'},
 56:{'p02':'Digitale Angebote schaffen damit Zugänge zu Wissen, das sich unabhängig vom Standort schneller auffinden lässt.',
     'p03':'Digitale Angebote ersetzen Bibliotheken deshalb nicht vollständig, weil diese auch Lernräume, Beratung und Zugang ohne eigene teure Abonnements bereitstellen.'},
 57:{'p02':'Flexible Studienmodelle schaffen Wege zum Abschluss, die sich mit Beruf, Familienarbeit oder Pflege besser vereinbaren lassen.'},
 58:{'p02':'Ein Internat bietet damit einigen Jugendlichen eine Lernumgebung, die durch feste Abläufe und gemeinschaftliche Aktivitäten geprägt ist.',
     'p03':'Ob ein Internat sinnvoll ist, hängt deshalb von der Persönlichkeit und der familiären Situation der Jugendlichen ab.'},
 60:{'p02':'Fachliche Kontakte über soziale Netzwerke können einen Austausch ermöglichen, der auch außerhalb formeller Sprechstunden stattfindet.',
     'p03':'Weil Lehrende Leistungen bewerten, können private Online-Kontakte den Eindruck von Bevorzugung entstehen lassen.'},
 61:{'p02':'Fantasy-Geschichten eröffnen Perspektiven, die Leserinnen und Leser über Moral, Macht und Verantwortung nachdenken lassen.'},
 62:{'p02':'Öffentliche Kulturförderung kann Angebote ermöglichen, weil sich manche Museen, Theater und Kulturprojekte nicht allein durch Einnahmen finanzieren lassen.',
     'p03':'Damit Kulturförderung gerecht bleibt, müssen Vergabekriterien transparent und öffentliche Mittel nachvollziehbar verteilt sein.'},
 63:{'p02':'Gerade bei Sachtexten ist eine Übersetzung gelungen, wenn sie Informationen klar und inhaltlich zuverlässig vermittelt.',
     'p03':'Bei literarischen Texten kann die Wirkung des Originals verloren gehen, wenn Rhythmus, Ton und Mehrdeutigkeit nicht mitbedacht werden.'},
 64:{'p02':'Gute Beziehungen zwischen Lehrenden und Lernenden können ein Lernklima schaffen, das Fragen und konstruktive Rückmeldungen erleichtert.',
     'p03':'Auch sympathische Lehrende müssen fachlich überzeugend sein, weil persönliche Zuneigung allein noch keinen Lernerfolg garantiert.'},
 65:{'p02':'Gemeinsames Vorlesen schafft Gesprächsanlässe, die den Wortschatz erweitern und das Verständnis für Gefühle fördern.'},
 66:{'p02':'Regelmäßige Zusammenarbeit kann einen Dialog schaffen, der Schwierigkeiten früh sichtbar macht und Vertrauen zwischen Schule und Eltern stärkt.',
     'p03':'Eltern können die Schule unterstützen, wenn sie Hinweise geben, ohne die pädagogischen Entscheidungen der Lehrkräfte zu übernehmen.'},
 67:{'p02':'Frühe Medienbildung ist vor allem hilfreich, wenn Eltern klare Regeln vereinbaren und digitale Inhalte mit ihren Kindern besprechen.',
     'p03':'Medienbildung im Vorschulalter muss deshalb Grenzen setzen, damit Spielen, Bewegung und persönliche Begegnungen nicht zu kurz kommen.'},
 68:{'p02':'Elternkurse können Wissen vermitteln, das Familien im Umgang mit alltäglichen Belastungen mehr Sicherheit gibt.',
     'p03':'Eine staatlich vorgeschriebene Elternlizenz wäre deshalb problematisch, weil sie die persönliche Freiheit einschränken könnte und kaum fair zu kontrollieren wäre.'}
}
# Seven existing, specific translation endings are intentionally preserved:
KEEP={(53,'p02'),(54,'p02'),(56,'p02'),(56,'p03'),(58,'p02'),(58,'p03'),(60,'p03')}
# Only the 19 formerly templated conclusions below change in translation; original first two sentences remain verbatim.
T={
 (54,'p03'):{'fa':'اگر مسیر شغلی را فقط نتیجهٔ شانس بدانیم، نقش آمادگی، تصمیم‌های شخصی و پشتکار را دست‌کم می‌گیریم.', 'en':'Treating a career as a matter of chance alone can underestimate the importance of preparation, personal choices, and perseverance.'},
 (55,'p02'):{'fa':'بنابراین وقتی زبان‌آموزان زمان خود را واقع‌بینانه برنامه‌ریزی می‌کنند و استراحت دارند، بهتر می‌توانند فشار طولانی‌مدت را کنترل کنند.', 'en':'Prolonged stress is easier to manage when learners plan their time realistically and take regular breaks.'},
 (55,'p03'):{'fa':'مقداری فشار ممکن است بعضی افراد را برای مدت کوتاهی فعال‌تر کند، در حالی که فشار ادامه‌دار یادگیری را دشوار می‌کند.', 'en':'Some pressure may briefly motivate certain people, whereas prolonged strain can make learning harder.'},
 (57,'p02'):{'fa':'به این ترتیب، برنامه‌های انعطاف‌پذیر تحصیلی به دانشجویان کمک می‌کنند تحصیل را با کار، مسئولیت‌های خانوادگی یا مراقبت از دیگران هماهنگ کنند.', 'en':'Flexible study models therefore help students combine education with work, family responsibilities, or caring duties.'},
 (60,'p02'):{'fa':'ارتباط علمی در شبکه‌های اجتماعی می‌تواند گفت‌وگویی ایجاد کند که بیرون از ساعت‌های رسمی مشاوره نیز ادامه یابد.', 'en':'Professional contacts on social networks can enable exchanges that continue beyond formal office hours.'},
 (61,'p02'):{'fa':'داستان‌های فانتزی دیدگاه‌هایی پیش روی خوانندگان می‌گذارند که آنان را به اندیشیدن دربارهٔ اخلاق، قدرت و مسئولیت تشویق می‌کند.', 'en':'Fantasy stories offer perspectives that encourage readers to reflect on morality, power, and responsibility.'},
 (62,'p02'):{'fa':'حمایت عمومی از فرهنگ می‌تواند برنامه‌هایی را ممکن کند که موزه‌ها، تئاترها و پروژه‌ها بدون این حمایت قادر به تأمین هزینهٔ آن‌ها نیستند.', 'en':'Public cultural funding can sustain programs that museums, theatres, and projects could not finance through their own revenue alone.'},
 (62,'p03'):{'fa':'برای عادلانه‌ماندن حمایت فرهنگی، معیارهای تخصیص بودجه باید شفاف و توزیع منابع عمومی قابل پیگیری باشد.', 'en':'For cultural funding to remain fair, allocation criteria must be transparent and the distribution of public funds accountable.'},
 (63,'p02'):{'fa':'به‌ویژه در متن‌های اطلاعاتی، ترجمه زمانی موفق است که اطلاعات را روشن و از نظر محتوا قابل اعتماد منتقل کند.', 'en':'Especially in informational texts, a translation succeeds when it conveys information clearly and faithfully.'},
 (63,'p03'):{'fa':'در متن ادبی، اگر آهنگ، لحن و چندمعنایی نادیده گرفته شوند، ممکن است تأثیر متن اصلی از بین برود.', 'en':'In literature, the original’s effect may be lost if rhythm, tone, and ambiguity are overlooked.'},
 (64,'p02'):{'fa':'رابطهٔ خوب میان معلم و یادگیرنده می‌تواند فضای یادگیری‌ای ایجاد کند که پرسش‌گری و بازخورد سازنده را آسان‌تر کند.', 'en':'A positive relationship between teachers and learners can create a learning environment that makes questions and constructive feedback easier.'},
 (64,'p03'):{'fa':'حتی معلمان محبوب هم باید از نظر علمی شایستگی داشته باشند، زیرا علاقهٔ شخصی به‌تنهایی موفقیت در یادگیری را تضمین نمی‌کند.', 'en':'Even likable teachers need subject expertise, because personal affection alone does not guarantee learning success.'},
 (65,'p02'):{'fa':'بلندخوانی مشترک فرصت‌هایی برای گفت‌وگو فراهم می‌کند که دایرهٔ واژگان را گسترش می‌دهد و فهم احساسات را در کودکان تقویت می‌کند.', 'en':'Reading aloud together creates opportunities for conversation that expand vocabulary and help children understand feelings.'},
 (66,'p02'):{'fa':'همکاری منظم می‌تواند گفت‌وگویی سازنده ایجاد کند که مشکلات را زود آشکار سازد و اعتماد میان مدرسه و والدین را تقویت کند.', 'en':'Regular cooperation can create a constructive dialogue that reveals problems early and strengthens trust between schools and parents.'},
 (66,'p03'):{'fa':'والدین می‌توانند با ارائهٔ اطلاعات مفید از مدرسه حمایت کنند، بی‌آنکه جای تصمیم‌گیری تخصصی معلمان را بگیرند.', 'en':'Parents can support schools by sharing useful information without overriding teachers’ professional educational decisions.'},
 (67,'p02'):{'fa':'آموزش رسانه‌ای زودهنگام زمانی مفید است که والدین قوانین روشنی تعیین کنند و دربارهٔ محتوای دیجیتال با فرزندانشان گفت‌وگو کنند.', 'en':'Early media education is most useful when parents set clear rules and discuss digital content with their children.'},
 (67,'p03'):{'fa':'آموزش رسانه‌ای در دورهٔ پیش‌دبستانی باید حد و مرز داشته باشد تا بازی، فعالیت بدنی و ارتباط‌های حضوری به حاشیه نروند.', 'en':'Media education in preschool must set limits so that play, physical activity, and face-to-face interaction are not neglected.'},
 (68,'p02'):{'fa':'دوره‌های آموزشیِ والدگری می‌توانند دانشی منتقل کنند که به خانواده‌ها در رویارویی با فشارهای روزمره اطمینان بیشتری بدهد.', 'en':'Parenting courses can provide knowledge that helps families feel more confident in dealing with everyday pressures.'},
 (68,'p03'):{'fa':'الزام دولتی به دریافت مجوز والدگری مسئله‌ساز است، زیرا می‌تواند آزادی‌های فردی را محدود کند و نظارت عادلانه بر آن دشوار باشد.', 'en':'A state-mandated parenting license would be problematic because it could restrict individual freedoms and be difficult to enforce fairly.'},
}
# Explicit exact substring to anchor one actually present linguistic construction per revised sentence.
# Do NOT assert a full grammar re-derive. All 11 inherited curated g06 anchors stay real Relativsatz.
AN={
 (53,'p02'):('relative_clauses_all','die weit über das bloße Speichern von Informationen hinausgehen'),
 (54,'p02'):('relative_clauses_all','die unerwartete Möglichkeiten erkennen und ergreifen'),
 (54,'p03'):('subordinate_clauses_all','dass Vorbereitung, Entscheidungen und Ausdauer ebenfalls wichtig sind'),
 (55,'p02'):('subordinate_clauses_all','wenn Lernende ihre Zeit realistisch planen und Pausen einlegen'),
 (55,'p03'):('subordinate_clauses_all','während anhaltende Belastung das Lernen erschwert'),
 (56,'p02'):('relative_clauses_all','das sich unabhängig vom Standort schneller auffinden lässt'),
 (56,'p03'):('subordinate_clauses_all','weil diese auch Lernräume, Beratung und Zugang ohne eigene teure Abonnements bereitstellen'),
 (57,'p02'):('relative_clauses_all','die sich mit Beruf, Familienarbeit oder Pflege besser vereinbaren lassen'),
 (58,'p02'):('relative_clauses_all','die durch feste Abläufe und gemeinschaftliche Aktivitäten geprägt ist'),
 (58,'p03'):('subordinate_clauses_all','Ob ein Internat sinnvoll ist'),
 (60,'p02'):('relative_clauses_all','der auch außerhalb formeller Sprechstunden stattfindet'),
 (60,'p03'):('subordinate_clauses_all','Weil Lehrende Leistungen bewerten'),
 (61,'p02'):('relative_clauses_all','die Leserinnen und Leser über Moral, Macht und Verantwortung nachdenken lassen'),
 (62,'p02'):('subordinate_clauses_all','weil sich manche Museen, Theater und Kulturprojekte nicht allein durch Einnahmen finanzieren lassen'),
 (62,'p03'):('subordinate_clauses_all','Damit Kulturförderung gerecht bleibt'),
 (63,'p02'):('subordinate_clauses_all','wenn sie Informationen klar und inhaltlich zuverlässig vermittelt'),
 (63,'p03'):('subordinate_clauses_all','wenn Rhythmus, Ton und Mehrdeutigkeit nicht mitbedacht werden'),
 (64,'p02'):('relative_clauses_all','das Fragen und konstruktive Rückmeldungen erleichtert'),
 (64,'p03'):('subordinate_clauses_all','weil persönliche Zuneigung allein noch keinen Lernerfolg garantiert'),
 (65,'p02'):('relative_clauses_all','die den Wortschatz erweitern und das Verständnis für Gefühle fördern'),
 (66,'p02'):('relative_clauses_all','der Schwierigkeiten früh sichtbar macht und Vertrauen zwischen Schule und Eltern stärkt'),
 (66,'p03'):('infinitive_with_zu','ohne die pädagogischen Entscheidungen der Lehrkräfte zu übernehmen'),
 (67,'p02'):('subordinate_clauses_all','wenn Eltern klare Regeln vereinbaren und digitale Inhalte mit ihren Kindern besprechen'),
 (67,'p03'):('subordinate_clauses_all','damit Spielen, Bewegung und persönliche Begegnungen nicht zu kurz kommen'),
 (68,'p02'):('relative_clauses_all','das Familien im Umgang mit alltäglichen Belastungen mehr Sicherheit gibt'),
 (68,'p03'):('subordinate_clauses_all','weil sie die persönliche Freiheit einschränken könnte und kaum fair zu kontrollieren wäre')
}
assert len(E)==15 and sum(map(len,E.values()))==26
assert len(KEEP)==7 and len(T)==19 and len(AN)==26
assert set(T)==set(AN)-KEEP
assert set(AN)=={(n,sid) for n,m in E.items() for sid in m}
# Exactly those inherited g06 curated relative clauses, no gratuitous new curated annotations.
CURATED_G06={53,54,56,57,58,60,61,64,65,66,68}
assert len(CURATED_G06)==11
old_retired=0;new_exact=0;cur_retarg=0;modified_tr=0;changes=[]
for n,edits in E.items():
 old=A['items'][n-1];u=B['items'][n-1]
 assert old['id']==u['id']==f'LES-PRES-{n:03d}'
 for sid,new_de in edits.items():
  sec=next(z for z in u['reading']['sections'] if z['id']==sid)
  oldsec=next(z for z in old['reading']['sections'] if z['id']==sid)
  assert len(sec['sentences'])==3 and sec['sentences'][-1]['text']==G[sid],(n,sid)
  assert new_de!=G[sid] and len(new_de)>85 and new_de.endswith('.'),(n,sid)
  before=copy.deepcopy(sec)
  old_trans={lang:re.split(r'(?<=[.!?؟])\s+',sec['translations'][lang]) for lang in ('fa','en')}
  assert len(old_trans['fa'])==len(old_trans['en'])==3,(n,sid,old_trans)
  sec['sentences'][-1]['text']=new_de
  sec['text']=' '.join(s['text'] for s in sec['sentences'])
  if (n,sid) in T:
   for lang in ('fa','en'):
    last=T[n,sid][lang]
    assert last!=old_trans[lang][-1] and last.endswith('.'),(n,sid,lang)
    sec['translations'][lang]=' '.join(old_trans[lang][:2]+[last])
   modified_tr+=1
  else:
   assert (n,sid) in KEEP and sec['translations']==before['translations']
  vanished=[g for g in old['grammar']['full_text_occurrences'] if g['section_id']==sid and g['sentence_id']==sid+'-s03']
  assert len(vanished)==(4 if sid=='p02' else 2),(n,sid,len(vanished))
  old_retired+=len(vanished)
  ids={g['id'] for g in vanished}
  u['grammar']['full_text_occurrences']=[g for g in u['grammar']['full_text_occurrences'] if g['id'] not in ids]
  grammar_key,target=AN[(n,sid)]
  assert new_de.count(target)==1,(n,sid,target)
  assert (sid=='p02' and n in CURATED_G06)==(grammar_key=='relative_clauses_all'),(n,sid,grammar_key)
  old_cur=[c for c in u['grammar']['curated_annotations'] if c['section_id']==sid and c['sentence_id']==sid+'-s03']
  assert len(old_cur)==int(sid=='p02' and n in CURATED_G06),(n,sid,old_cur)
  if old_cur:
   c=old_cur[0];assert c['grammar_key']=='relative_clause' and c['id']=='g06'
   c['target_text']=new_de
   c['annotation_source']='editorial_source_aligned_relative_clause_r18'
   c['derivation_method']='existing_curated_g06_retargeted_to_attested_r18_relative_clause_not_native_nine_lens'
   cur_retarg+=1
  anchor=sec['text'].index(target,sec['text'].index(new_de))
  deex={'relative_clauses_all':'Der Relativsatz beschreibt ein Nomen genauer; das finite Verb steht am Ende der Relativstruktur.',
        'subordinate_clauses_all':'Die Nebensatzkonjunktion leitet einen Nebensatz ein, etwa für Gründe, Bedingungen, Gegensätze, Ziele oder indirekte Fragen; das finite Verb steht am Ende.',
        'infinitive_with_zu':'Die Konstruktion „ohne … zu“ drückt aus, dass eine Handlung unterbleibt.'}[grammar_key]
  faex={'relative_clauses_all':'جملهٔ موصولی اسمِ مرجع را توضیح می‌دهد و فعل صرف‌شده در پایان ساختار موصولی می‌آید.',
        'subordinate_clauses_all':'حرف ربط وابسته می‌تواند دلیل، شرط، تقابل، هدف یا پرسش غیرمستقیم را نشان دهد و فعل صرف‌شده در انتهای جملهٔ وابسته می‌آید.',
        'infinitive_with_zu':'ساختار «ohne … zu» بیان می‌کند که یک کار بدون انجام کار دیگری صورت می‌گیرد.'}[grammar_key]
  g={'id':f'ftg-r18-{n:03d}-{sid}-scoped','grammar_key':grammar_key,'label_de':('Relativsatz' if grammar_key=='relative_clauses_all' else 'Nebensatz' if grammar_key=='subordinate_clauses_all' else 'Infinitivgruppe mit „ohne … zu“')+' (redaktionell geprüft)',
     'section_id':sid,'sentence_id':sid+'-s03','start':anchor,'end':anchor+len(target),'target_text':target,
     'explanation_de':deex,'explanation_fa':faex,'confidence':'high','annotation_source':'manual_scoped_r18',
     'details':{'scope':'26_topic_grounded_conclusions_r18','is_full_nine_lens_rerun':False},
     'derivation_method':'attested_exact_source_span_manual_not_full_native_engine'}
  assert sec['text'][g['start']:g['end']]==target and target in sec['sentences'][-1]['text']
  u['grammar']['full_text_occurrences'].append(g);new_exact+=1
  changes.append({'lesson_id':u['id'],'title_de':u['title_de'],'section_id':sid,'sentence_id':sid+'-s03',
    'before_de':before['sentences'][-1]['text'],'after_de':new_de,
    'before_fa_tail':old_trans['fa'][-1],'after_fa_tail':re.split(r'(?<=[.!?؟])\s+',sec['translations']['fa'])[-1],
    'before_en_tail':old_trans['en'][-1],'after_en_tail':re.split(r'(?<=[.!?؟])\s+',sec['translations']['en'])[-1],
    'translation_action':'PRESERVE_ALREADY_SPECIFIC' if (n,sid) in KEEP else 'REVISE_BOTH_FA_EN_TO_MATCH_DE',
    'first_two_sentences_unchanged':before['sentences'][:2]==sec['sentences'][:2],
    'old_grammar_retired_ids':sorted(ids),'new_manually_attested_grammar_key':grammar_key,'new_scoped_grammar_target':target,
    'old_curated_relative_retargeted':bool(old_cur),'review_reason':'Individual concluding claim based on the accepted prior German sentences and relevant FA/EN meaning, not a token-swapped template.'})
 u['reading']['word_count_de']=len(' '.join(s['text'] for s in u['reading']['sections']).split())
 u['quality']['content_hash']=sha(' '.join(s['text'] for s in u['reading']['sections']).encode())[:16]
 u['quality']['app_mapping_status']='r18_scoped_26_p02_p03_conclusions_preentry_only'
 gsum=u['grammar']['full_text_lens_summary']
 gsum['occurrences']=len(u['grammar']['full_text_occurrences'])
 gsum['counts']=dict(collections.Counter(g['grammar_key'] for g in u['grammar']['full_text_occurrences']))
 gsum['scope_note_de']='R18: 26 pauschale Schlusssätze punktuell ersetzt, deren alte Grammatikspannen entfernt; je ein echter, manuell überprüfter Nebensatz/Relativsatz/Infinitiv je Änderung ergänzt. Kein vollständiger Neun-Linsen-Lauf.'
 gsum['scope_note_fa']='R18: پایان‌های کلی اصلاح و نشانگرهای نامعتبر حذف شدند؛ به‌ازای هر جملهٔ جدید یک ساختار واقعی به‌صورت دستی نشانه‌گذاری شد. استخراج کامل نه‌گانهٔ گرامر انجام نشده است.'
 for c in u['grammar']['curated_annotations']:
  s=next(z for z in u['reading']['sections'] if z['id']==c['section_id'])
  ss=next(z for z in s['sentences'] if z['id']==c['sentence_id'])
  assert c['target_text'] in ss['text'],(n,c['id'],c['target_text'])
assert len(changes)==26 and len(E)==15 and old_retired==82 and new_exact==26 and cur_retarg==11 and modified_tr==19,(len(changes),old_retired,new_exact,cur_retarg,modified_tr)
assert [i+1 for i,(a,b) in enumerate(zip(A['items'],B['items'])) if a!=b]==sorted(E)
allg=[g for u in B['items'] for g in u['grammar']['full_text_occurrences']]
assert len(allg)==4041,len(allg)
for u in B['items']:
 for g in u['grammar']['full_text_occurrences']:
  sec=next(s for s in u['reading']['sections'] if s['id']==g['section_id'])
  ss=next(s for s in sec['sentences'] if s['id']==g['sentence_id'])
  assert sec['text'][g['start']:g['end']]==g['target_text'] and g['target_text'] in ss['text'],(u['id'],g['id'])
 assert len({g['id'] for g in u['grammar']['full_text_occurrences']})==len(u['grammar']['full_text_occurrences'])
qa=B['full_text_grammar_qa'];qa['occurrences']=len(allg);qa['offset_exact_matches']=len(allg);qa['counts']=dict(collections.Counter(g['grammar_key'] for g in allg));qa['result']='R18_ALL_26_ORIGINAL_GENERIC_CONCLUSIONS_REVISED__SCOPED_NOT_FULL_NATIVE'
qa['r18_scope']={'units':15,'sections':26,'obsolete_original_grammar_retired':82,'new_attested_manual_spans':26,'curated_relative_retargets':11,'native_nine_lens_rerun':False,'semantic_stage4':'HOLD'}
ws=[u['reading']['word_count_de'] for u in B['items']];B['qa_summary']['word_count_de']={'min':min(ws),'mean':round(sum(ws)/len(ws),1),'max':max(ws)}
B['qa_summary']['r18_scope']='26_FINAL_P02_P03_GENERIC_CONCLUSIONS_REVISED_053_TO_068__19_TRANSLATION_PAIRS_REVISED_7_PRESERVED'
B['translation_qa']['r18_review_status']='19_ORIGINALLY_GENERIC_FA_EN_CONCLUSION_PAIRS_REVISED__7_APPROVED_SPECIFIC_PAIRS_PRESERVED__NOT_HOLISTIC_STAGE4'
B['content_version']='1.3.0-R18-CANDIDATE';B['status']='R18_ALL_ORIGINAL_GENERIC_P02_P03_CONCLUSIONS_REVISED__SCOPED_QA_STAGE4_6_7_HOLD'
write(OUT,B)
rem={sid:sum(next(s for s in u['reading']['sections'] if s['id']==sid)['sentences'][-1]['text']==G[sid] for u in B['items']) for sid in G}
assert rem=={'p02':0,'p03':0},rem
ledger={'schema':'lesen-r18-26-conclusions-grammar-ledger@1','date':'2026-11-07','parent_r17_sha256':BASESHA,'candidate_sha256':sha(OUT.read_bytes()),'bytes':OUT.stat().st_size,'changed_units':sorted(E),'changed_sections':26,'unchanged_units':53,'preserved_specific_fa_en_tail_pairs':7,'revised_fa_en_tail_pairs':19,'grammar_before':4097,'obsolete_old_markers_retired':old_retired,'new_manual_attested_spans':new_exact,'curated_g06_relative_retargets':cur_retarg,'grammar_after':len(allg),'remaining_original_generic_p02':rem['p02'],'remaining_original_generic_p03':rem['p03'],'formal_semantic_stage4':'HOLD','native_browser_stage6':'NOT_RUN','full_nine_lens_rerun':False,'changes':changes}
write(LED,ledger)
print(json.dumps({k:v for k,v in ledger.items() if k!='changes'},ensure_ascii=False,indent=2))