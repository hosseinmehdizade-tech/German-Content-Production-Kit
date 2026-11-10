#!/usr/bin/env python3
"""Aspekte B1+ risk-scoped P1 83-case editorial corrections from exact curated owner.
Use: python build_P1_remaining83_v1.py
No old publisher content restoration. Does not assert app import or blanket language approval.
"""
import copy, hashlib, json, pathlib, re, zipfile, collections, itertools
ROOT=pathlib.Path(__file__).parent
PARENT=ROOT/'Aspekte-B1plus-P1-SCOPED-131-HOLD-RESOLUTION-CURATED-NONIMPORT-20261110.zip'
LEDGER=ROOT/'P1-131-CASE-DECISION-LEDGER-20261110.jsonl'
OUT=ROOT/'Aspekte-B1plus-P1-REMAINING83-SCOPED-CONTENT-REPAIRS-NONIMPORT-20261110.zip'
PRIMARY='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
EXPECT_PARENT='d7550a83387b41d3f1efa61297b926c24fdca692ea8a8d5b5288743ef20d563d'
EXPECT_PRIMARY='dd229a97dcfe82d82361ab417f048a43bb3185a946c94046b11b0ef2ea44b96b'
EXPECT_MAP='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
sha=lambda b:hashlib.sha256(b).hexdigest()
dump=lambda o:json.dumps(o,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
short=lambda n:(n['sense_id'].split(':')[-1])
# Scope decisions: each key identifies one reviewed P1 case, not blanket card release.
# Each held case not listed stays content-HOLD. Closing a scoped legacy content flag
# never changes import_ready/formal_release_approved or unrelated QA statuses.
CLOSE={
60:'Separate mit + Dativ scolding from über + Akkusativ complaint; contextual examples and both phrase slots agree.',
75:'Strong verb finite forms and transitive/intransitive perfect split retained; tear, become torn, harsh critical metaphor have independently routed bilingual examples.',
78:'Four incoming/context/death/shrinkage senses have discrete bilingual examples; finite-sentence pseudo-combination repaired.',
165:'Rest/temporary suspension/burial/support senses have separate DE–FA contexts with aligned literal vs elevated labels.',
177:'Peppered food, steep price and harsh retort are separately glossed and exemplified.',
241:'Intransitive landing, metaphorical destination and transitive landing of aircraft have separately correct examples and auxiliaries.',
315:'Method, funding resources and medication meanings are separated with contextual bilingual examples.',
348:'Market stall, current status and social estate senses are distinguished; plurality restricted by sense using Duden.',
362:'Cancellation, forgotten name and distributive share are distinct patterns; Duden confirms entfallen forms and valency.',
363:'alle, alles, superlative-forming aller- are distinguished; mixed example explicitly has two sense_ids; standalone alles example added.',
408:'Set aside, sit exam and archive files distinguished; original missing archive-sense example added.',
410:'Playing card, map, ticket, menu and identification card are distinctly exemplified and routed.',
439:'Piece, dramatic work and countable unit separate; count unit now explicitly exemplified.',
547:'Sport/drive/do mischief/rare dough rise/drive into mental state separate, with missing psychological sense exemplified; Duden verifies rare yeast sense.',
598:'Act methodically, move ahead, happen and take priority distinct; missing literal move-ahead sense exemplified.',
620:'Look up/check, forgive a minor fault, and watch depart separately glossed; Duden examples align with all three.',
625:'Lay out, interpret, design for load, advance money and cover surface sense blocks separate; missing covering-surface sense exemplified.',
629:'Retell, reproduce sound and depict visually separate, missing visual reproduction example added.',
637:'Prepare mentally, join singing, tune musical instrument each has separate German–Persian evidence; Duden confirms Kammerton construction.',
686:'Minutes of meeting, diplomatic protocol and network communication protocol all separately contextualized.',
717:'Reschedule, mislay, install physical flooring/cables and publish books each have sound example and meaning-specific collocation.',
831:'Physical fishnet, social support network and data/Internet senses independently exemplified.',
886:'Guestbook is not necessarily a memorial book; erroneous Persian sample corrected using Duden meaning, plural retained.',
895:'Capability/disposition to get enthusiastic, not temporary excited state; comparison forms corrected to Duden paradigm.',
919:'Eat quickly, devour a novel and interweave strands are contrasted; Duden homographs and metaphorical reading distinguished in one lemma card.',
953:'Joyful adjective and omitted past participle clearly differentiated; pseudo-collocation from infinitive auslassen replaced.',
967:'Banal as commonplace/unremarkable not obscene; examples and comparative match Duden.',
1056:'Order goods, reserve a table and summon someone are distinct; Duden directly confirms reserving a table with bestellen.',
1077:'Mountain summit, apex of a development and summit of officials; new standalone figurative example fills sense S2.',
1148:'Human carrier, sponsoring body and structural load-bearing girder separately evidenced; feminine Trägerin is not inferred for metal beam.',
1157:'Memento with plural versus commemorative memory predominantly without plural, each independently exemplified.',
1167:'Put back, save money, cover a distance and tilt head backwards now all sense-routed in one card.',
1214:'Five receiving/topic/shrinkage/perish/commitment contexts separately DE–FA exemplified with matching prepositions.',
1256:'Duden explicitly lists Seeleute as plural of Seemann; no second mandatory singular lemma card is missing. Collective plural example retained within same card.',
1282:'Covered arcade, paragraph of text and sea passage now independently exemplified.',
1352:'Leave switched on, leave clothes on and start engine have separate direct DE–FA examples.',
1364:'Tip/tilt, ventilate by tilting window and pour away liquid have separate examples, plus auxiliary split.',
1377:'Burn something, be burned and metabolically burn calories are disambiguated in bilingual examples.',
1435:'Kleider generic clothes vs plural das Kleid (one-piece dresses) differentiated with appropriate examples.',
1449:'Carrying out, verbal explanation and particular execution/design separately exemplified after adding missing explanation context.',
1538:'Romantic affection and idealizing/romanticized landscape are independently evidenced and routed, no false cross-sense example.',
}
# Strong concrete case-level changes. None converts pending -> PASS.
EXAMPLES={
363:[('Alles ist für die Prüfung vorbereitet.','همه‌چیز برای امتحان آماده شده است.','S2')],
408:[('Die Sekretärin hat die unterschriebenen Verträge im Ordner abgelegt.','منشی قراردادهای امضاشده را در زونکن بایگانی کرد.','S3')],
439:[('Wir brauchen noch drei Stück von diesem Ersatzteil.','ما هنوز به سه عدد از این قطعهٔ یدکی نیاز داریم.','S3')],
547:[('Der ständige Stress trieb ihn fast in den Wahnsinn.','فشار روانی مداوم تقریباً او را به مرز جنون کشاند.','S5')],
598:[('Gehen Sie bitte ein paar Schritte vor, damit die anderen vorbeikommen.','لطفاً چند قدم جلو بروید تا دیگران بتوانند عبور کنند.','S2')],
625:[('Die Handwerker haben den Boden mit neuen Fliesen ausgelegt.','کارگران کف را با کاشی‌های جدید پوشاندند.','S5')],
629:[('Die Zeichnung gibt den Aufbau der Maschine genau wieder.','نقشه ساختار دستگاه را دقیق نشان می‌دهد.','S3')],
1077:[('Auf dem Gipfel ihrer Karriere gewann sie einen wichtigen Preis.','او در اوج دوران حرفه‌ای خود جایزهٔ مهمی دریافت کرد.','S2')],
1148:[('Zwei Träger brachten die schweren Kisten ins Lager.','دو باربر جعبه‌های سنگین را به انبار بردند.','S1'),('Der Stahlträger stützt die Decke der Halle.','تیر فولادی سقف سالن را نگه می‌دارد.','S3')],
1167:[('Sie legte den Kopf zurück und schaute in den Himmel.','او سرش را به عقب برد و به آسمان نگاه کرد.','S4')],
1256:[('Viele Seeleute arbeiten monatelang auf See.','بسیاری از دریانوردان ماه‌ها در دریا کار می‌کنند.','S1')],
1282:[('Während der Passage durch die Meerenge blieb das Schiff auf Kurs.','کشتی هنگام عبور از تنگهٔ دریایی مسیر خود را حفظ کرد.','S3')],
1449:[('Ihre Ausführungen zum Projekt waren klar und verständlich.','توضیحات او دربارهٔ پروژه روشن و قابل‌فهم بود.','S2')]
}
# Rectify a questionable Persian example, lemma form, or lexical pseudo-combination.
TRANSFORMS={
60:'sense_de and usage label corrected (the old label Lernersatz was production metadata, not German lexical content)',
78:'Pflanzen gehen ein finite independent sentence replaced by an infinitival lexical combination',
363:'legacy mixed alle/alles German sentence additionally routed to S2 without duplicate data',
886:'Gästebuch generic visitor message must not be translated as memorial-only دفتر یادبود',
895:'positive/comparative/superlative front supplied with attested German adjective inflection',
919:'two homographic verschlingen verbs noted without splitting one accepted learning card',
953:'ausgelassen Partizip-II combination made a phrase of that form instead of a different infinitive',
1167:'back-listed head-tilt meaning given a sense block and dedicated German–Persian example',
1256:'Seeleute explicitly noted as collective plural from Duden; no artificial separate card',
1148:'Trägerin valid for human/institutional referents, not grammatical feminine of construction element',
}
SOURCES={
60:['https://www.duden.de/rechtschreibung/schimpfen'],
75:['https://www.duden.de/rechtschreibung/zerreiszen'],
78:['https://www.duden.de/rechtschreibung/eingehen'],
165:['https://www.duden.de/rechtschreibung/ruhen'],
177:['https://www.duden.de/rechtschreibung/gepfeffert'],
241:['https://www.duden.de/rechtschreibung/landen'],
315:['https://www.duden.de/rechtschreibung/Mittel'],
348:['https://www.duden.de/rechtschreibung/Stand'],
362:['https://www.duden.de/rechtschreibung/entfallen'],
547:['https://www.duden.de/rechtschreibung/treiben'],
620:['https://www.duden.de/rechtschreibung/nachsehen'],
637:['https://www.duden.de/rechtschreibung/einstimmen'],
831:['https://www.duden.de/rechtschreibung/Netz'],
886:['https://www.duden.de/rechtschreibung/Gaestebuch'],
895:['https://www.duden.de/deklination/adjektive/begeisterungsfaehig'],
919:['https://www.duden.de/rechtschreibung/verschlingen_essen','https://www.duden.de/rechtschreibung/verschlingen_verknuepfen'],
953:['https://www.duden.de/rechtschreibung/ausgelassen'],
967:['https://www.duden.de/rechtschreibung/banal'],
1056:['https://www.duden.de/rechtschreibung/bestellen'],
1148:['https://www.duden.de/rechtschreibung/Traeger','https://www.duden.de/rechtschreibung/Traegerin'],
1157:['https://www.duden.de/rechtschreibung/Andenken'],
1256:['https://www.duden.de/rechtschreibung/Seemann','https://www.duden.de/rechtschreibung/Seeleute'],
1435:['https://www.duden.de/rechtschreibung/Kleid'],
}
# URLs in SOURCES are optional case references; a source URL is not itself proof of having
# read every page in this execution. Receipt separates directly opened Duden refs.
DIRECTLY_CHECKED_DUDEN=[
 'https://www.duden.de/rechtschreibung/treiben','https://www.duden.de/rechtschreibung/Stand',
 'https://www.duden.de/rechtschreibung/entfallen','https://www.duden.de/rechtschreibung/nachsehen',
 'https://www.duden.de/rechtschreibung/einstimmen','https://www.duden.de/rechtschreibung/Gaestebuch',
 'https://www.duden.de/rechtschreibung/Seemann','https://www.duden.de/rechtschreibung/Seeleute',
 'https://www.duden.de/deklination/adjektive/begeisterungsfaehig',
 'https://www.duden.de/rechtschreibung/verschlingen_essen','https://www.duden.de/rechtschreibung/verschlingen_verknuepfen',
 'https://www.duden.de/rechtschreibung/Traeger','https://www.duden.de/rechtschreibung/Traegerin',
 'https://www.duden.de/rechtschreibung/bestellen','https://www.duden.de/rechtschreibung/banal']

# All 83 are triaged, but only explicit CLOSE keys are allowed to clear scoped HOLD.

def build():
 assert sha(PARENT.read_bytes())==EXPECT_PARENT
 with zipfile.ZipFile(PARENT) as arc:
  assert arc.testzip() is None
  old_member={n:arc.read(n) for n in arc.namelist() if n!='SHA256SUMS.txt'}
  lines=old_member[PRIMARY].decode('utf-8').splitlines()
  assert sha(old_member[PRIMARY])==EXPECT_PRIMARY
  assert sha(old_member[MAP])==EXPECT_MAP
  orig=[json.loads(s) for s in lines]
  assert len(orig)==1571
  indices={c['preview_card_id']:i for i,c in enumerate(orig)}
  prev_queue=[json.loads(s) for s in LEDGER.read_text(encoding='utf-8').splitlines()]
  remaining=[q for q in prev_queue if q['HOLD_after']]
  assert len(remaining)==83
  assert len(CLOSE)==len(set(CLOSE)) and all(n in {q['source_ordinal'] for q in remaining} for n in CLOSE)
  source_id_by_ord={q['source_ordinal']:q['card_id'] for q in remaining}
  changed=[];closures=[];rows=[];new_examples=[];wrong=[];old_ex_count=0;new_ex_count=0
  for q in remaining:
   o=q['source_ordinal'];i=indices[q['card_id']];c=copy.deepcopy(orig[i]);front=c['front'];back=c['back']
   senses=back.get('semantic_network_sense_anchored_pending_qa') or []
   existing=back.get('existing_examples_de_fa_pending_qa') or []
   added=back.get('additional_examples_de_fa_pending_qa') or []
   new_ex=[];edits=[];prior_sense_map={k['sense_id'].split(':')[-1]:k for k in senses}
   if o==60:
    assert 'Lernersatz' in senses[0]['sense_de']
    senses[0]['sense_de']='jemanden tadeln; mit jemandem schimpfen (+ Dativ)'
    senses[0]['usage_distinction_de']='mit + Dativ: jemanden für ein Verhalten tadeln; über + Akkusativ: sich über etwas beschweren'
    edits.append('removed nonlexical editor placeholder from S1 German definition')
   if o==78:
    s=next(s for s in senses if s['sense_id'].endswith(':S3'))
    combos=s['Kombinationen_DE_FA']
    hits=[x for x in combos if x['de']=='Pflanzen gehen ein']
    assert len(hits)==1
    hits[0]['de']='ohne Wasser eingehen';hits[0]['fa']='بدون آب از بین رفتن (گیاه)'
    edits.append('finite sentence removed from Kombinationen and replaced with infinitive phrase')
   if o==363:
    target=[e for e in existing+added if 'Alle waren da, aber nicht alles hat funktioniert.' in e.get('de','')]
    assert len(target)==1 and target[0]['sense_id'].endswith(':S1')
    target[0]['sense_ids']=[prior_sense_map['S1']['sense_id'],prior_sense_map['S2']['sense_id']]
    target[0]['sense_routing_status']='EXPLICIT_TWO_SENSE_GERMAN_CLAUSE_COVERAGE__PENDING_FULL_G4_QA'
    edits.append('bilingual mixed clause explicitly linked to alle and alles sense IDs; legacy sense_id retained')
   if o==886:
    matches=[e for e in existing+added if e['de']=='Die Besucher schrieben einen Gruß ins Gästebuch.']
    assert len(matches)==1 and 'یادبود' in matches[0]['fa']
    matches[0]['fa']='بازدیدکنندگان پیامی در دفتر مهمانان نوشتند.'
    edits.append('removed inaccurate memorial-only Persian gloss in a generic visitor guestbook sample')
   if o==895:
    front['display_de_provisional']='begeisterungsfähig – begeisterungsfähiger – am begeisterungsfähigsten (Adjektiv)'
    front['scoped_form_evidence']={'source':'Duden','url':'https://www.duden.de/deklination/adjektive/begeisterungsfaehig','scope':'positive/comparative/superlative only; no full semantic release'}
    edits.append('front adjective comparative and superlative supplied from explicit Duden declension table')
   if o==919:
    net=senses[2]
    net['usage_distinction_de']='Andere lexikalische Bedeutung gleichen Schriftbilds: verschlingen = ineinanderwinden; Perfekt ebenfalls hat verschlungen. Kein separater Lernkarten-Split.'
    net['lexicographic_evidence_urls']=['https://www.duden.de/rechtschreibung/verschlingen_verknuepfen','https://www.duden.de/rechtschreibung/verschlingen_essen']
    edits.append('explicitly documented two Duden homographs without destructive card duplication')
   if o==953:
    s=prior_sense_map['S2']; matches=[v for v in s['Kombinationen_DE_FA'] if v['de']=='einen Absatz auslassen']
    assert len(matches)==1
    matches[0].update(de='ein versehentlich ausgelassener Absatz',fa='بندی که به‌اشتباه حذف شده است')
    edits.append('infinitive auslassen in past-participle card replaced with an actual ausgelassen participle collocation')
   if o==1167:
    assert len(senses)==3
    sid=c['preview_card_id']+':P1R83:S4'
    senses.append({'sense_id':sid,'sense_de':'den Kopf oder einen Körperteil nach hinten bewegen','sense_fa':'سر یا عضوی از بدن را به عقب بردن',
      'usage_distinction_de':'Kopf zurücklegen (physische Bewegung), getrennt von Geld sparen und eine Strecke absolvieren',
      'lexical_relation_policy':'NO_FORCED_SYNONYMS_ANTONYMS_OR_FAMILY_SIMILARITY',
      'Kombinationen_DE_FA':[{'de':'den Kopf zurücklegen','fa':'سر را به عقب بردن'}],
      'Synonyme':[],'Antonyme':[],'Feste_Wendungen_DE_FA':[],'Satzmuster_DE_FA':[],
      'Verwandte_Woerter_KEINE_Synonyme':[],'Wortfamilie':[],
      'status':'PENDING_G4_SENSE_SPECIFIC_DE_FA_CONTENT_QA','source':'P1_REMAINING83_SCOPED_EDITORIAL_NONIMPORT'})
    prior_sense_map['S4']=senses[-1]
    edits.append('explicit fourth sense for head/body reclining was named in Persian back but had no structured sense')
   if o==1256:
    assert senses[0]['sense_de']=='männlicher Matrose'
    senses[0]['sense_de']='Seemann als männliche Berufsbezeichnung; Sammelplural Seeleute kann alle Geschlechter umfassen'
    senses[0]['sense_fa']='ملوان یا دریانورد مرد؛ جمعِ Seeleute شامل دریانوردان زن و مرد هم می‌شود'
    front['display_de_provisional']='der Seemann – Gen. des Seemanns/Seemannes – Pl. die Seeleute (Sammelplural); männlich: Seemänner'
    front['scoped_form_evidence']={'source':'Duden','url':'https://www.duden.de/rechtschreibung/Seemann','scope':'Seeleute is grammatical plural and collective form of Seemann; Seemänner masculine explicitly'}
    edits.append('obsolete split-card requirement corrected: Seeleute is grammatical plural of Seemann, not independent mandatory learner lemma')
   if o==1148:
    net=prior_sense_map['S3'];net['usage_distinction_de']='Träger (technisches Bauteil) ist maskulin; Trägerin gilt für weibliche Personen und Institutionen, nicht als feminine Form für den Stahlträger.'
    net['lexicographic_evidence_urls']=['https://www.duden.de/rechtschreibung/Traeger','https://www.duden.de/rechtschreibung/Traegerin']
    edits.append('feminine structural-girder overgeneralization blocked with sense-specific usage note')
   if o in EXAMPLES:
    for de,fa,local_id in EXAMPLES[o]:
     assert local_id in prior_sense_map,(o,local_id)
     assert not any(e['de'].casefold()==de.casefold() for e in existing+added),de
     e={'de':de,'fa':fa,'status':'PENDING_G4_DE_FA_SEMANTIC_QA','provenance':'P1_REMAINING83_MEANING_SCOPED_EDITORIAL_NONIMPORT','sense_id':prior_sense_map[local_id]['sense_id'],'sense_routing_status':'CASE_LEVEL_P1_SCOPE_ROUTED_PENDING_FULL_QA'}
     back['additional_examples_de_fa_pending_qa'].append(e)
     new_ex.append({'sense':local_id,'de':de,'fa':fa});new_examples.append({'card_id':q['card_id'],'ordinal':o,'lesson':q['lesson'],**e})
    edits.append('added '+str(len(EXAMPLES[o]))+' unique contextual bilingual example(s) to individually selected sense(s)')
   if o in CLOSE:
    assert c['curated_HOLD_content_disposition_exists'] is True
    c['curated_HOLD_content_disposition_exists']=False
    record={'date':'2026-11-10','scope':'SCOPED_CONTENT_HOLD_ONLY_NOT_FULL_CARD_LINGUISTIC_RELEASE','status':'CLOSED_WITH_CASE_SPECIFIC_EVIDENCE_NONIMPORT',
      'source_case':'P1_REMAINING83_WHEN_303_HOLDS_OPEN',
      'specific_case_reason':CLOSE[o],
      'reviewed_sense_count':len(senses),
      'reviewed_bilingual_evidence_count':len(existing)+len(back['additional_examples_de_fa_pending_qa']),
      'case_example_evidence':[{'de':e['de'],'fa':e['fa'],'sense_id':e.get('sense_id')} for e in (existing+back['additional_examples_de_fa_pending_qa'])[:4]],
      'related_lexicographic_urls_references_only':SOURCES.get(o,[]),
      'dictionary_entries_opened_this_session':sorted(set(SOURCES.get(o,[])) & set(DIRECTLY_CHECKED_DUDEN)),
      'full_DE_FA_semantics_approved':False,'real_app_import_or_display_verified':False,
      'formal_release_approved':False}
    c['P1_83_scoped_HOLD_resolution']=record
    closures.append({'source_ordinal':o,'card_id':q['card_id'],'lesson':q['lesson'],'lemma':q['headword'],**record})
   # Status at release unaffected; never use passed structural tests to mark language approved.
   assert c['import_ready'] is False and c['formal_release_approved'] is False
   if c!=orig[i]:
    changed.append({'source_ordinal':o,'card_id':q['card_id'],'lesson':q['lesson'],'lemma':q['headword'],
                    'scope_edited':edits+(['scoped_content_HOLD_flag_closed'] if o in CLOSE else []),
                    'before':orig[i],'after':c,'before_sha256':sha(dump(orig[i]).encode()),'after_sha256':sha(dump(c).encode())})
    lines[i]=json.dumps(c,ensure_ascii=False,sort_keys=True)
   rows.append({'card_id':q['card_id'],'source_ordinal':o,'lesson':q['lesson'],'headword':q['headword'],
               'previous_hold':True,'current_hold':c['curated_HOLD_content_disposition_exists'],'case_disposition':('SCOPED_LEXICAL_CONTENT_HOLD_CLOSED_NOT_RELEASE' if o in CLOSE else 'RETAIN_HOLD_PENDING_SPECIFIC_CONTENT_CHECK'),
               'case_reason':CLOSE[o] if o in CLOSE else specific_unresolved_reason(q,c,original=orig[i]),
               'primary_changed':c!=orig[i], 'content_edits':edits,'new_example_count':len(new_ex),
               'parent_sha256_card':sha(dump(orig[i]).encode()),'current_sha256_card':sha(dump(c).encode()),
               'case_example_evidence':[{'de':e['de'],'fa':e['fa'],'sense_id':e.get('sense_id')} for e in existing[:2]],
               'lexicographic_reference_urls':SOURCES.get(o,[]),
               'formal_release_approved':False})
  assert len(rows)==83 and len(closures)==len(CLOSE)
  newcards=[json.loads(t) for t in lines]
  assert len(newcards)==1571
  assert len(set(c['preview_card_id'] for c in newcards))==1571
  assert [(c['preview_card_id'],c['source_ordinal'],c['lesson']) for c in newcards]==[(c['preview_card_id'],c['source_ordinal'],c['lesson']) for c in orig]
  assert all(newcards[i]==orig[i] for i in range(1571) if orig[i]['preview_card_id'] not in {q['card_id'] for q in remaining})
  assert all(newcards[i]==orig[i] for i in range(1571) if orig[i]['preview_card_id'] not in {x['card_id'] for x in changed})
  assert not any(newcards[i]['formal_release_approved'] or newcards[i]['import_ready'] for i in range(1571))
  assert sum(c['curated_HOLD_content_disposition_exists'] for c in orig)==303
  assert sum(c['curated_HOLD_content_disposition_exists'] for c in newcards)==303-len(CLOSE)
  def examples(c):return c['back'].get('existing_examples_de_fa_pending_qa',[])+c['back'].get('additional_examples_de_fa_pending_qa',[])
  old_example_ids=collections.Counter((c['preview_card_id'],e['de'],e['fa']) for c in orig for e in examples(c))
  new_example_ids=collections.Counter((c['preview_card_id'],e['de'],e['fa']) for c in newcards for e in examples(c))
  removed=old_example_ids-new_example_ids
  assert len(removed)==1 and sum(removed.values())==1 and list(removed.keys())[0][0]==source_id_by_ord[886]  # edited inaccurate Persian translation
  assert sum(new_example_ids.values())==sum(old_example_ids.values())+len(new_examples)
  for c in newcards:
   ex=examples(c);all_de=collections.Counter(e['de'].strip().lower() for e in ex)
   assert max(all_de.values(),default=0)==1,(c['preview_card_id'],all_de)
   if c['preview_card_id'] in {q['card_id'] for q in remaining}:
    nets=c['back'].get('semantic_network_sense_anchored_pending_qa') or []
    ids={n['sense_id'] for n in nets}
    for e in ex:
     if ids:
      assert e.get('sense_id') in ids,(c['preview_card_id'],e)
      assert all(v in ids for v in e.get('sense_ids',[])),(c['preview_card_id'],e)
     assert e['de'].strip() and e['fa'].strip() and 'PENDING' in e.get('status',''),(c['preview_card_id'],e)
    assert not c['back'].get('Formen_section')
  # global known finite-clause cases must not regress; narrow pattern gate only
  finite_re=re.compile(r'\b(?:ich|du|er|sie|es|wir|ihr|Sie|die|der|das|ein|eine|Pflanzen)\s+(?:geht|gehen|läuft|laufen|hat|haben|ist|sind|schreibt|schreiben|tritt|treten|steht|stehen|zeigt|zeigen|beginnt|beginnen|wird|werden|kann|können)\b',re.I)
  flagged=[]
  for c in newcards:
   for sn in c['back'].get('semantic_network_sense_anchored_pending_qa') or []:
    for combo in sn.get('Kombinationen_DE_FA') or []:
     if finite_re.search(combo['de']):flagged.append((c['preview_card_id'],combo['de']))
  assert not flagged,flagged
  # Compare sibling and source map unchanged, continue to allow 1548 source rows mapped into 1571 cards.
  primary_bytes=('\n'.join(lines)+'\n').encode('utf8')
  report={'schema':'aspekte-b1plus-P1-remaining83-substantive-editorial@1',
          'date':'2026-11-10','status':'P1_83_CASES_REVIEWED_SCOPED_CONTENT_REPAIRS_NONIMPORT',
          'parent_zip_sha256':EXPECT_PARENT,'parent_primary_sha256':EXPECT_PRIMARY,
          'new_primary_sha256':sha(primary_bytes),
          'original_HOLDs_at_parent':303,'P1_open_at_parent':83,
          'P1_cases_reviewed':83,'scoped_content_HOLDs_closed_in_this_pass':len(CLOSE),
          'global_open_HOLDs_after':303-len(CLOSE),'P1_open_after':83-len(CLOSE),
          'P2_open_after':190,'P3_open_after':30,
          'actual_primary_card_objects_changed':len(changed),'unchanged_card_objects':1571-len(changed),
          'new_bilingual_DE_FA_examples':len(new_examples),
          'existing_examples_unchanged_excluding_one_corrected_translation':sum(old_example_ids.values())-1,
          'corrected_existing_Persian_example_count':1,
          'new_example_total':sum(new_example_ids.values()),
          'new_semantic_sense_blocks':1, 'known_narrow_finite_clause_combinations_after':len(flagged),
          'all_1571_IDs_preserved':True,'source_map_sha256_preserved':EXPECT_MAP,
          'full_before_after_for_changed_cards':True,'all_83_dispositions_saved':True,
          'Duden_links_opened_in_this_session':DIRECTLY_CHECKED_DUDEN,
          'important_interventions':TRANSFORMS,
          'all_new_examples_Pending':True,'all_release_flags_false':True,
          'real_app_import_or_render_tested':False,
          'full_linguistic_signoff_claimed':False,
          'formal_card_release_approvals':0,'release':'RELEASE_BLOCKED_NONIMPORT',
          'next':'PRIORITIZED_REVIEW_OF_REMAINING_P1_AND_P2_CASES_WITH_ACTUAL_CONTENT_FIXES_NOT_FLAG_AUTOCLOSURE'}
  # New current-status ledger supersedes, without destroying, the prior historical 359-case ledger.
  previous_all_359=[json.loads(v) for v in old_member['Global-Backlog/P1-HOLD-FOLLOWUP/P1-359-CURRENT-STATUS-LEDGER.jsonl'].decode('utf8').splitlines()]
  assert len(previous_all_359)==359
  current_by_id={c['preview_card_id']:c for c in newcards}
  closed_now={r['card_id'] for r in closures}
  current_status=[]
  for oldrow in previous_all_359:
   row=copy.deepcopy(oldrow)
   cid=row['card_id']
   card=current_by_id[cid]
   row['HOLD_after_P1_remaining83']=card['curated_HOLD_content_disposition_exists']
   row['HOLD_resolution_in_P1_remaining83']='CLOSED_SCOPED_CONTENT_NONIMPORT' if cid in closed_now else 'NO_NEW_CLOSURE'
   row['current_example_count']=len(examples(card))
   row['current_primary_card_SHA256']=sha(dump(card).encode())
   row['current_canonical_owner_state']='P1_REMAINING83_PRIMARY_VERIFIED_NONIMPORT'
   current_status.append(row)
  assert sum(r['HOLD_after_P1_remaining83'] for r in current_status)==303-len(CLOSE)
  latest_content={'status':'CURRENT_SCOPED_CONTENT_GATE_P1_REMAINING83_NONIMPORT',
   'parent_owner_zip_sha256':EXPECT_PARENT,'primary_sha256':sha(primary_bytes),
   'source_map_sha256':EXPECT_MAP,'total_cards':1571,'inherited_HOLD_id_count':359,
   'current_content_HOLD_count':303-len(CLOSE),'newly_closed_content_HOLDs':len(CLOSE),
   'P1_remaining':83-len(CLOSE),'P2_remaining':190,'P3_remaining':30,
   'current_status_ledger':'Global-Backlog/P1-REMAINING83/P1-ALL-359-CURRENT-STATUS-LEDGER.jsonl',
   'formal_release_approvals':0,'real_app_import_tested':False,'release':'RELEASE_BLOCKED_NONIMPORT'}
  new_members={
  'Global-Backlog/P1-REMAINING83/P1-ALL-359-CURRENT-STATUS-LEDGER.jsonl':(''.join(json.dumps(t,ensure_ascii=False,sort_keys=True)+'\n' for t in current_status)).encode(),
  'Global-Backlog/LATEST-CONTENT-STATE.json':dump(latest_content).encode(),
  'Global-Backlog/P1-REMAINING83/P1-83-CASE-DECISION-LEDGER.jsonl':(''.join(json.dumps(t,ensure_ascii=False,sort_keys=True)+'\n' for t in rows)).encode(),
  'Global-Backlog/P1-REMAINING83/P1-CASE-SCOPED-CLOSURES.json':dump(closures).encode(),
  'Global-Backlog/P1-REMAINING83/P1-SUBSTANTIVE-EDIT-BEFORE-AFTER.json':dump(changed).encode(),
  'Global-Backlog/P1-REMAINING83/P1-NEW-DE-FA-EXAMPLES.json':dump(new_examples).encode(),
  'Global-Backlog/P1-REMAINING83/P1-CONTENT-AND-RELEASE-REPORT.json':dump(report).encode(),
  'Global-Backlog/P1-REMAINING83/qa_P1_remaining83_v1.py':pathlib.Path(__file__).read_bytes(),
  'Global-Backlog/P1-REMAINING83/verify_P1_remaining83_v1.py':(ROOT/'verify_P1_remaining83_v1.py').read_bytes(),
  'G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl':primary_bytes}
  for k,v in new_members.items():old_member[k]=v
  manifest=''.join(sha(b)+'  '+n+'\n' for n,b in sorted(old_member.items())).encode()
  with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as dest:
   for n,b in sorted(old_member.items()):dest.writestr(n,b)
   dest.writestr('SHA256SUMS.txt',manifest)
  with zipfile.ZipFile(OUT) as val:
   assert val.testzip() is None
   for row in val.read('SHA256SUMS.txt').decode().splitlines():
    a,n=row.split('  ',1);assert sha(val.read(n))==a,(n,a)
  report['new_zip_sha256']=sha(OUT.read_bytes())
  report['new_zip_size_bytes']=OUT.stat().st_size
  report['archive_members']=len(old_member)+1;report['sha256_verified_member_count']=len(old_member)
  report['sha_manifest_check']='PASS'
  report['archive_crc_check']='PASS'
  for name,obj in [('P1-83-CASE-DECISION-LEDGER.jsonl',rows),('P1-SCOPED-CLOSURES.json',closures),('P1-SUBSTANTIVE-EDIT-BEFORE-AFTER.json',changed),('P1-NEW-DE-FA-EXAMPLES.json',new_examples),('P1-CONTENT-AND-RELEASE-REPORT.json',report)]:
   b=(''.join(json.dumps(t,ensure_ascii=False,sort_keys=True)+'\n' for t in obj) if name.endswith('.jsonl') else dump(obj)).encode()
   (ROOT/name).write_bytes(b)
  print(json.dumps({k:report[k] for k in ['new_zip_sha256','new_primary_sha256','new_zip_size_bytes','archive_members','sha256_verified_member_count','P1_cases_reviewed','scoped_content_HOLDs_closed_in_this_pass','global_open_HOLDs_after','P1_open_after','actual_primary_card_objects_changed','new_bilingual_DE_FA_examples','new_example_total']},ensure_ascii=False,indent=2))


def specific_unresolved_reason(q,c,original):
 o=q['source_ordinal'];b=c['back']; nets=b.get('semantic_network_sense_anchored_pending_qa') or []
 examples=b.get('existing_examples_de_fa_pending_qa',[])+b.get('additional_examples_de_fa_pending_qa',[])
 hits=collections.Counter(e.get('sense_id') for e in examples)
 uncovered=[(n.get('sense_id','').split(':')[-1],n.get('sense_de','')) for n in nets if hits.get(n.get('sense_id'),0)==0]
 if o==1487:return 'Newly added tidal/coastal Hochwasser interpretation requires precise B1+ discourse/context check; did not auto-close after provisional example.'
 if o==1162:return 'Pension guesthouse/retirement income/retirement status includes newly added sense with PENDING status; keep until scoped word-sense morphology and idiomatic QA is completed.'
 if o==1183:return 'Independent shop/Handlung use is rare and only mentioned in compounds; no verified standalone current-context example, so preserve HOLD instead of inventing one.'
 if o==882:return 'Singular/plural marking das Vielfache (Sg.) needs case-specific German declension evidence before changing form; existing quantitative examples alone do not certify number restriction.'
 if o==870:return 'Dienst shifts and service examples exist but current Persian front includes service/institutional duty with unresolved scope boundaries; no forced approval.'
 if uncovered:return 'Missing real DE–FA contextual example for sense(s): '+repr(uncovered)+'; original content left unchanged until example quality confirmed.'
 if 'REJECTED_OR_UNRESOLVED_PREVIOUS_EDITORIAL_OVERLAY' in q['risk_signals']:
  return 'Previous rejected overlay was not reconciled with current sense/grammar evidence; no confident deltas, keep HOLD rather than equating a valid-looking card with full content resolution.'
 if not nets:return 'One-sense examples exist but no explicit sense-map and unresolved historical CONTENT-HOLD decision; no semantic evidence sufficient to close without adding unjustified field.'
 return 'Meaning/sense examples present, but scoped final issue is not established from available provenance; case stays HOLD to avoid false closure.'
if __name__=='__main__':build()
