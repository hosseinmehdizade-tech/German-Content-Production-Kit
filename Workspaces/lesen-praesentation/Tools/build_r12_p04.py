#!/usr/bin/env python3
"""R11 -> R12: learner-facing p04 trilingual editorial in 041–050, 10 manually written lessons.
The R11 CURRENT CANDIDATE is authority, not the initial presentation textbook.
No native 9-lens source producer or browser/IndexedDB import is claimed.
"""
import copy, hashlib, json, pathlib, collections
ROOT=pathlib.Path('/mnt/data/lesen_r12_20261107')
SRC=pathlib.Path('/mnt/data/lesen_r11_20261107/Lesen-Production-Master-v1.3.0-R11-9P04-TRILINGUAL-CANDIDATE.json')
OUT=ROOT/'Lesen-Production-Master-v1.3.0-R12-10P04-TRILINGUAL-CANDIDATE.json'
LEDGER=ROOT/'LESEN-R12-10P04-TRILINGUAL-GRAMMAR-LEDGER.json'
PIN='8a0bf2d16ce51b39501e5b6bc26b912cb47d9a4a14c0f42699e6b49b4ba3e3fe'
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Every translation renders new DE-s01, the unchanged authoritative DE-s02, and new DE-s03, in order.
# Individual claims are anchored in the curated source owner's p02/p03/p05, not externally invented source material.
EDITS={
41:{'s01':'Die Pflege älterer Menschen darf nicht davon abhängen, ob Angehörige genug Zeit, Geld und Kraft haben.',
    's03':'Der Staat müsste eine verlässliche Versorgung sichern und pflegende Angehörige durch Beratung und Entlastungsangebote unterstützen.', 'k2':'müsste',
    'fa':'مراقبت از سالمندان نباید به این وابسته باشد که اعضای خانواده وقت، پول و توان کافی دارند یا نه. اگر خدمات حرفه‌ای و حمایت داوطلبانهٔ خانواده با یکدیگر ترکیب شوند، می‌توان بخشی از این تعارض را کاهش داد. دولت باید خدمات مراقبتی قابل‌اعتماد را تضمین کند و از اعضای خانواده‌ای که مراقبت می‌کنند، با مشاوره و خدمات حمایتیِ کاهش فشار پشتیبانی کند.',
    'en':'Care for older people should not depend on whether relatives have enough time, money and energy. If professional services and voluntary family support are combined, part of the conflict can be eased. The state would need to ensure reliable care and support family caregivers through advice and respite services.'},
42:{'s01':'Ein Job im Ausland ist nicht automatisch ein Karrieresprung, wenn Wohnkosten, Bürokratie oder ein unsicherer Vertrag die Vorteile aufzehren.',
    's03':'Bewerberinnen und Bewerber sollten vor einer Zusage Arbeitsrecht, Krankenversicherung und sprachliche Anforderungen klären.', 'k2':'sollten',
    'fa':'کار در خارج از کشور لزوماً جهشی در مسیر شغلی نیست، اگر هزینهٔ مسکن، کارهای اداری یا قرارداد نامطمئن مزیت‌های آن را از بین ببرند. اگر هدف‌ها، شرایط قرارداد و وضعیت زندگی شخصی پیشاپیش واقع‌بینانه بررسی شوند، می‌توان بخشی از این تعارض را کاهش داد. متقاضیان بهتر است پیش از پذیرش پیشنهاد، قوانین کار، بیمهٔ درمانی و نیازهای زبانی را روشن کنند.',
    'en':'A job abroad is not automatically a career leap if housing costs, bureaucracy or an insecure contract eat up its advantages. If goals, contract conditions and personal circumstances are assessed realistically in advance, part of the conflict can be eased. Applicants should clarify employment law, health insurance and language requirements before accepting an offer.'},
43:{'s01':'Barrierefreiheit an Hochschulen betrifft digitale Unterlagen und faire Prüfungsbedingungen ebenso wie den Zugang zu Gebäuden.',
    's03':'Eine Hochschule müsste barrierefreie PDFs, erreichbare Seminarräume und passende Prüfungsbedingungen von Anfang an mitplanen.', 'k2':'müsste',
    'fa':'دسترس‌پذیری در دانشگاه‌ها فقط به ورود به ساختمان محدود نیست؛ جزوه‌ها و فایل‌های دیجیتال و شرایط منصفانهٔ امتحان را هم دربرمی‌گیرد. اگر افراد دارای معلولیت به‌طور نظام‌مند مشارکت داده شوند و تسهیلات جبرانیِ آزمون به‌طور قابل‌اعتماد اجرا شوند، می‌توان بخشی از این تعارض را کاهش داد. دانشگاه باید از همان ابتدا فایل‌های PDF دسترس‌پذیر، کلاس‌های قابل‌دسترسی و شرایط امتحانی متناسب را در برنامه‌ریزی بگنجاند.',
    'en':'Accessibility at universities concerns digital materials and fair exam conditions just as much as access to buildings. If affected students are systematically involved and accommodations are implemented reliably, part of the conflict can be eased. A university would need to plan for accessible PDFs, accessible seminar rooms and suitable examination conditions from the outset.'},
44:{'s01':'Wer wenig verdient oder lange unbezahlte Sorgearbeit leistet, kann finanzielle Sicherheit im Alter nicht allein durch privates Sparen erreichen.',
    's03':'Eine verlässliche Grundsicherung müsste auch diejenigen schützen, die wegen Arbeitslosigkeit oder Pflegezeiten kaum vorsorgen konnten.', 'k2':'müsste',
    'fa':'کسی که درآمد کمی دارد یا مدت طولانی بدون دستمزد از دیگران مراقبت می‌کند، نمی‌تواند امنیت مالی دوران سالمندی را فقط با پس‌انداز شخصی به دست آورد. اگر تأمین پایهٔ دولتی با پس‌انداز تکمیلیِ خصوصی یا شغلی ترکیب شود، می‌توان بخشی از این تعارض را کاهش داد. یک نظام مطمئنِ تأمین پایه باید از کسانی هم حمایت کند که به‌دلیل بیکاری یا دوره‌های مراقبت، فرصت اندکی برای پس‌انداز داشته‌اند.',
    'en':'People who earn little or spend long periods providing unpaid care cannot secure their old age through private savings alone. If state basic protection is combined with additional private or occupational provision, part of the conflict can be eased. Reliable basic protection would also need to cover those who could save very little because of unemployment or periods of caregiving.'},
45:{'s01':'Schulische und berufliche Wege hängen nicht nur vom Einsatz ab: Herkunft, Kontakte und Zufälle eröffnen Menschen unterschiedliche Chancen.',
    's03':'Beratungsangebote könnten helfen, Bildungswege sichtbar zu machen, die ohne Unterstützung leicht übersehen werden.', 'k2':'könnten',
    'fa':'مسیر تحصیلی و شغلی فقط به تلاش فرد وابسته نیست؛ پیشینهٔ خانوادگی، ارتباطات و اتفاق‌های پیش‌بینی‌نشده برای افراد فرصت‌های متفاوتی ایجاد می‌کنند. اگر مسئولیت فردی و شرایط ساختاری با هم در نظر گرفته شوند، می‌توان بخشی از این تعارض را کاهش داد. خدمات مشاوره می‌توانند به شناساندن مسیرهای آموزشی کمک کنند؛ مسیرهایی که بدون پشتیبانی به‌راحتی نادیده گرفته می‌شوند.',
    'en':'Educational and career paths depend on more than effort: family background, contacts and chance create different opportunities for people. If individual responsibility and structural conditions are considered together, part of the conflict can be eased. Guidance services could help make educational pathways visible that might otherwise be overlooked.'},
46:{'s01':'Künstlerische Fächer sind mehr als eine Pause vom Prüfungsstoff, weil sie Ausdruck, Zusammenarbeit und eigene Entscheidungen fördern.',
    's03':'Schulen könnten Gestaltungsaufgaben mit handwerklichen Grundlagen verbinden, statt nur fertige Ergebnisse zu benoten.', 'k2':'könnten',
    'fa':'درس‌های هنری صرفاً زنگ تفریحی از مطالب امتحانی نیستند، چون بیان فردی، همکاری و تصمیم‌گیری مستقل را تقویت می‌کنند. اگر مدارس حوزه‌های موردتوجه را مشخص کنند و پیشنهادهای گوناگون هنری را با هم ترکیب کنند، می‌توان بخشی از این تعارض را کاهش داد. مدارس می‌توانند تکلیف‌های خلاقانه را با آموزش مهارت‌های پایه پیوند دهند، به‌جای آنکه فقط نتیجهٔ نهایی را نمره بدهند.',
    'en':'Arts subjects are more than a break from exam material because they encourage expression, collaboration and independent choices. If schools set priorities and combine different artistic activities, part of the conflict can be eased. Schools could combine creative tasks with practical foundations instead of grading only finished results.'},
47:{'s01':'Bei Klimawandel und künstlicher Intelligenz reichen technische Daten allein nicht aus, um gesellschaftliche Entscheidungen zu treffen.',
    's03':'Naturwissenschaftliche Befunde könnten so mit historischen, rechtlichen und ethischen Perspektiven verbunden werden.', 'k2':'könnten',
    'fa':'برای تصمیم‌گیری‌های اجتماعی دربارهٔ تغییرات اقلیمی و هوش مصنوعی، داده‌های فنی به‌تنهایی کافی نیستند. اگر همکاری میان‌رشته‌ای به‌طور هدفمند تقویت شود، می‌توان بخشی از این تعارض را کاهش داد. به این ترتیب می‌توان یافته‌های علوم طبیعی را با دیدگاه‌های تاریخی، حقوقی و اخلاقی پیوند داد.',
    'en':'Technical data alone are not enough for social decisions about climate change and artificial intelligence. If interdisciplinary collaboration is deliberately encouraged, part of the conflict can be eased. Scientific findings could then be connected with historical, legal and ethical perspectives.'},
48:{'s01':'Bei alternativen Heilmethoden muss zwischen einem angenehmen Behandlungserlebnis und wissenschaftlich belegter Wirksamkeit unterschieden werden.',
    's03':'Behandelnde müssten offenlegen, welche Aussagen belegt sind, und notwendige medizinische Diagnostik ausdrücklich unangetastet lassen.', 'k2':'müssten',
    'fa':'در روش‌های درمانی جایگزین باید میان تجربهٔ خوشایندِ درمان و اثربخشیِ اثبات‌شدهٔ علمی تفاوت گذاشت. اگر دربارهٔ شواهد، محدودیت‌ها و خطرهای احتمالی روش‌ها شفاف اطلاع‌رسانی شود و تشخیص پزشکیِ ضروری کنار گذاشته نشود، می‌توان بخشی از این تعارض را کاهش داد. درمانگران باید روشن کنند کدام ادعاها پشتوانهٔ علمی دارند و صریحاً اجازه ندهند تشخیص پزشکیِ ضروری کنار گذاشته شود.',
    'en':'With alternative treatments, a pleasant treatment experience must be distinguished from scientifically demonstrated effectiveness. If methods provide transparent information about evidence, limits and possible risks, and do not replace necessary medical diagnostics, part of the conflict can be eased. Practitioners would need to disclose which claims are supported by evidence and explicitly leave necessary medical diagnosis in place.'},
49:{'s01':'Soziales Engagement kann Jugendlichen Verantwortung vermitteln, doch eine allgemeine Pflicht kann gerade ihre freiwillige Motivation schwächen.',
    's03':'Schulen könnten erreichbare Projekte und flexible Zeiten anbieten, damit auch Jugendliche mit familiären Verpflichtungen mitmachen können.', 'k2':'könnten',
    'fa':'فعالیت اجتماعی می‌تواند حس مسئولیت را در نوجوانان تقویت کند، اما اجبار همگانی ممکن است انگیزهٔ داوطلبانهٔ آنان را تضعیف کند. اگر فرصت‌های داوطلبانهٔ متنوع به‌راحتی در دسترس باشند و همراهی مناسبی دریافت کنند، می‌توان بخشی از این تعارض را کاهش داد. مدارس می‌توانند پروژه‌های در دسترس و زمان‌بندی انعطاف‌پذیر فراهم کنند تا نوجوانانی که مسئولیت خانوادگی دارند نیز بتوانند شرکت کنند.',
    'en':'Community engagement can teach young people responsibility, but a general requirement may weaken their voluntary motivation. If a variety of voluntary opportunities are easily accessible and well supported, part of the conflict can be eased. Schools could offer accessible projects and flexible schedules so that young people with family responsibilities can also take part.'},
50:{'s01':'Einfluss ist nicht mit Bekanntheit gleichzusetzen: Entscheidend ist, ob die Handlungen einer Person langfristige Folgen haben.',
    's03':'Eine Person mit wenigen Followern könnte nachhaltiger wirken als jemand, der nur kurzfristig weltweite Aufmerksamkeit erhält.', 'k2':'könnte',
    'fa':'نفوذ و تأثیرگذاری را نباید با شهرت یکسان دانست؛ مهم این است که رفتارهای یک فرد پیامدهای بلندمدت داشته باشند. اگر تأثیرگذاری بر اساس گسترهٔ اثر، دوام، پیامدهای مشخص و مسئولیت ارزیابی شود، می‌توان بخشی از این تعارض را کاهش داد. فردی با دنبال‌کنندگان کم ممکن است اثری ماندگارتر از کسی داشته باشد که فقط برای مدتی کوتاه توجه جهانی را جلب می‌کند.',
    'en':'Influence should not be equated with fame: what matters is whether a person’s actions have lasting consequences. If influence is evaluated by its reach, duration, concrete effects and responsibility, part of the conflict can be eased. A person with few followers could have a more lasting impact than someone who attracts worldwide attention only briefly.'}
}

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    assert sha(SRC.read_bytes())==PIN,'parent R11 candidate mismatch'
    old=json.loads(SRC.read_text(encoding='utf8'));new=copy.deepcopy(old)
    assert set(EDITS)==set(range(41,51));ledger=[];dropped=[];new_anchors=[];retargeted=[];reanchored=0;preserved_middle=0
    for n,edit in EDITS.items():
        a=old['items'][n-1];b=new['items'][n-1]
        assert a['id']==b['id']==f'LES-PRES-{n:03d}'
        before=a['reading']['sections'][3];after=b['reading']['sections'][3]
        assert before['id']=='p04' and len(before['sentences'])==3
        assert before['sentences'][0]['text']=='Entscheidend ist deshalb die konkrete Ausgestaltung.'
        assert before['sentences'][2]['text'].startswith('Statt nur zwischen Zustimmung und Ablehnung zu wählen')
        assert before['sentences'][1]==after['sentences'][1]
        after['sentences'][0]['text']=edit['s01'];after['sentences'][2]['text']=edit['s03']
        after['text']=' '.join(s['text'] for s in after['sentences'])
        after['translations']={'fa':edit['fa'],'en':edit['en']}
        assert after['text']!=before['text'] and len(edit['fa'])>160 and len(edit['en'])>190
        oldstart=len(before['sentences'][0]['text'])+1;newstart=len(after['sentences'][0]['text'])+1
        full=[];drop=[];kept=[]
        for occ in a['grammar']['full_text_occurrences']:
            if occ['section_id']!='p04':full.append(copy.deepcopy(occ));continue
            assert before['text'][occ['start']:occ['end']]==occ['target_text']
            if occ['sentence_id']!='p04-s02':
                dropped.append((a['id'],occ['id']));drop.append({'id':occ['id'],'grammar_key':occ['grammar_key'],'target_text':occ['target_text']});continue
            cloned=copy.deepcopy(occ)
            rel=occ['start']-oldstart
            assert rel>=0 and before['sentences'][1]['text'][rel:rel+len(occ['target_text'])]==occ['target_text']
            cloned['start']=newstart+rel;cloned['end']=cloned['start']+len(cloned['target_text'])
            assert after['text'][cloned['start']:cloned['end']]==cloned['target_text']
            reanchored+=int(cloned['start']!=occ['start']);preserved_middle+=1
            kept.append({'id':cloned['id'],'old':occ['start'],'new':cloned['start']});full.append(cloned)
        marker=edit['k2'];s03=edit['s03'];assert s03.count(marker)==1,(n,marker)
        offset=len(after['sentences'][0]['text'])+1+len(after['sentences'][1]['text'])+1+s03.index(marker)
        ann={'id':f'ftg-r12-{n:03d}-p04-k2','grammar_key':'konjunktiv_ii','label_de':'Konjunktiv II: Möglichkeit oder vorsichtige Empfehlung',
             'section_id':'p04','sentence_id':'p04-s03','start':offset,'end':offset+len(marker),'target_text':marker,
             'explanation_de':f'Die Form „{marker}“ steht hier im Konjunktiv II und kennzeichnet eine denkbare Handlung oder vorsichtige Empfehlung, nicht eine feststehende Tatsache.',
             'explanation_fa':f'«{marker}» در این جمله ساخت Konjunktiv II است و یک امکان یا پیشنهاد سنجیده را بیان می‌کند، نه یک واقعیت قطعی.',
             'details':{'scope':'manual_scoped_r12_p04_s03','form':marker},'confidence':'high','annotation_source':'editorial_scoped_r12',
             'derivation_method':'manual_exact_form_attestation_not_full_native_grammar_engine'}
        assert after['text'][ann['start']:ann['end']]==marker and ann['id'] not in {z['id'] for z in full}
        full.append(ann);new_anchors.append((a['id'],ann['id']))
        b['grammar']['full_text_occurrences']=full
        sm=b['grammar']['full_text_lens_summary'];sm['occurrences']=len(full);sm['counts']=dict(collections.Counter(z['grammar_key'] for z in full))
        sm['scope_note_de']='R12: Alte Kontextmarker in den bearbeiteten Sätzen p04-s01/s03 entfernt, Marker aus dem unveränderten p04-s02 exakt repositioniert; eine manuell geprüfte Konjunktiv-II-Form ergänzt. Native Neun-Linsen-Grammatik nicht neu generiert.'
        sm['scope_note_fa']='R12: نشانگرهای جمله‌های حذف‌شده کنار گذاشته شدند، نشانگرهای جملهٔ دومِ حفظ‌شده با دقت جابه‌جا شدند و یک نمونهٔ دست‌بررسی‌شده از Konjunktiv II اضافه شد؛ موتور کامل گرامر اجرا نشده است.'
        ret=[]
        for cur in b['grammar']['curated_annotations']:
            if cur['section_id']=='p04' and cur['sentence_id']=='p04-s03':
                assert cur['id']=='g07' and cur['grammar_key']=='konjunktiv_ii'
                cur['target_text']=s03;cur['annotation_source']='editorial_retarget_r12'
                ret.append(cur['id']);retargeted.append((b['id'],cur['id']))
        for cur in b['grammar']['curated_annotations']:
            sec=next(s for s in b['reading']['sections'] if s['id']==cur['section_id'])
            sent=next(s for s in sec['sentences'] if s['id']==cur['sentence_id'])
            assert cur['target_text'] in sent['text'],(b['id'],cur['id'])
        b['reading']['word_count_de']=len(' '.join(sec['text'] for sec in b['reading']['sections']).split())
        b['quality']['content_hash']=sha(' '.join(sec['text'] for sec in b['reading']['sections']).encode('utf8'))[:16]
        b['quality']['app_mapping_status']='r12_scoped_p04_candidate_preentry_only'
        ledger.append({'unit_id':b['id'],'title_de':b['title_de'],'evidence_sections':['p02','p03','p05'],
                       'before_p04':before,'after_p04':after,'removed_old_p04_grammar':drop,
                       'unchanged_middle_grammar_reanchored':kept,'added_scoped_grammar':ann,'curated_g07_retargets':ret,
                       'parent_unit_sha256':sha(canon(a)),'candidate_unit_sha256':sha(canon(b))})
    changed=[n for n,(a,b) in enumerate(zip(old['items'],new['items']),1) if a!=b]
    assert changed==list(range(41,51)),changed
    allgrammar=[z for unit in new['items'] for z in unit['grammar']['full_text_occurrences']]
    qa=new['full_text_grammar_qa'];qa['occurrences']=len(allgrammar);qa['counts']=dict(collections.Counter(z['grammar_key'] for z in allgrammar));qa['offset_exact_matches']=len(allgrammar)
    qa['result']='R12_SCOPED_GRAMMAR_EXACT_OFFSETS__NATIVE_9_LENS_NOT_RERUN__STAGE4_HOLD'
    qa['r12_scope']={'changed_units':10,'retired_old_anchors':len(dropped),'reanchored_middle':reanchored,'new_scoped_K2':len(new_anchors),'nine_lens_rerun':False}
    wc=[unit['reading']['word_count_de'] for unit in new['items']]
    new['qa_summary']['word_count_de']={'min':min(wc),'mean':round(sum(wc)/len(wc),1),'max':max(wc)}
    new['qa_summary']['r12_scope']='10_P04_TRILINGUAL_SECTIONS_041_TO_050__ALL_OTHER_SOURCE_FIELDS_PRESERVED'
    new['translation_qa']['r12_review_status']='SOURCE_GROUNDED_AI_EDITORIAL_NOT_INDEPENDENT_STAGE4'
    new['translation_qa']['result']='R12_10_P04_SECTIONS_REVIEWED_WITH_STAGE4_HOLD'
    new['content_version']='1.3.0-R12-CANDIDATE'
    new['status']='R12_10_P04_TRILINGUAL_SCOPED_GRAMMAR_CANDIDATE_STAGE4_6_7_HOLD'
    for a,b in zip(old['items'],new['items']):
        assert a['id']==b['id'] and a['questions']==b['questions'] and a['vocabulary']==b['vocabulary']
        for g in b['grammar']['full_text_occurrences']:
            s=next(q for q in b['reading']['sections'] if q['id']==g['section_id'])
            assert s['text'][g['start']:g['end']]==g['target_text'],(b['id'],g['id'])
    write(OUT,new)
    summary={'schema':'lesen-r12-10-p04-multilingual-edit-ledger@1.0.0','date':'2026-11-07','parent_sha256':PIN,'candidate_sha256':sha(OUT.read_bytes()),'candidate_bytes':OUT.stat().st_size,
             'changed_units':[f'LES-PRES-{n:03d}' for n in changed], 'changed_sections':10,'changed_german_sentences':20,'original_middle_sentences_preserved':10,'untouched_units':58,
             'grammar_before':sum(len(u['grammar']['full_text_occurrences']) for u in old['items']),'grammar_after':len(allgrammar),
             'old_invalid_context_occurrences_retired':len(dropped),'middle_grammar_reanchored':reanchored,'middle_grammar_retained':preserved_middle,
             'new_scoped_K2_occurrences':len(new_anchors),'curated_g07_retargets':len(retargeted),'native_9_lens_engine_rerun':False,
             'original_current_modified':False,'semantic_stage4':'HOLD','browser_stage6':'NOT_RUN','stage7':'NOT_FINAL',
             'before_after':ledger}
    write(LEDGER,summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='before_after'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()