#!/usr/bin/env python3
"""Aspekte B1+ L08: whole-lesson scoped editorial and saved-owner proof; NONIMPORT.
Replays from exactly the SHA-pinned L07 Phase3 ZIP. No external reviewer, no publisher CSV.
"""
from __future__ import annotations
import collections, copy, csv, hashlib, html, io, json, re, zipfile
from pathlib import Path
BASE=Path('/mnt/data/aspekte_b1plus_l08_phase2')
PARENT=BASE/'Aspekte-B1plus-L07-PHASE3-FINAL-154-CARD-RELEASE-BLOCKED-NONIMPORT-20261109.zip'
QUEUE=BASE/'L08-PHASE1-157-CARD-DECISION-QUEUE-20261109.jsonl'
OUT=BASE/'Aspekte-B1plus-L08-PHASE2-WHOLE-157-CARDS-CURATED-NONIMPORT-20261109.zip'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
SRC='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
EXPECTED_OWNER='14841de70a121551121c6c1bced5cca987a659e006d0b225d980f302939dac81'
EXPECTED_MAIN='e979959fd3b10885ed8d05266e6c17101fb29302a9d626d606252aa9e684046e'
EXPECTED_MAP='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
DATE='2026-11-09'
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def jbytes(o):return (json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
def net(sid,de,fa,combos=None):
 return {'sense_id':sid,'sense_de':de,'sense_fa':fa,
  'Synonyme':[],'Antonyme':[],'Verwandte_Woerter_KEINE_Synonyme':[], 'Wortfamilie':[],
  'Kombinationen_DE_FA':[{'de':a,'fa':b} for a,b in (combos or [])],
  'source':'L08_PHASE2_EDITORIAL_CONTEXTUAL_SCOPE_NOT_DICTIONARY_CERTIFIED',
  'status':'PENDING_G4_FULL_BILINGUAL_SEMANTIC_RELATION_QA',
  'lexical_relation_policy':'NO_FORCED_SYNONYMS_OR_ANTONYMS; COMBINATIONS_SCOPE_TO_SENSE'}
# The ordered indices of actual existing+additional bilingual examples are hand-routed to concrete senses.
NEW_NETWORKS={
 1004:([('kleines Blatt einer Pflanze','برگ کوچک گیاه',[('zarte Blättchen','برگ‌های ظریف')]),('Zigarettenpapier (umgangssprachlich)','کاغذ نازک سیگارپیچی',[('ein Blättchen zum Drehen','یک کاغذ برای پیچیدن سیگار')])],[0,1,1]),
 1011:([('enger Teil einer Flasche','گردن باریک بطری',[('ein enger Flaschenhals','گردن باریک بطری')]),('Engpass bei einem Ablauf','گلوگاه یا عامل محدودکننده',[('zum Flaschenhals werden','به گلوگاه تبدیل شدن')])],[0,1,1]),
 1027:([('einen Text neu schreiben (trennbar)','بازنویسی کردن متن (فعل جداشدنی)',[('einen Satz umschreiben','جمله‌ای را بازنویسی کردن')]),('etwas mit anderen Worten beschreiben (untrennbar)','شرح دادن با واژه‌های دیگر (فعل جدانشدنی)',[('einen Begriff umschreiben','مفهومی را با کلمات دیگر بیان کردن')])],[0,1,0,1,0,1]),
 1030:([('Konfektionsgröße','سایز لباس',[('die richtige Größe wählen','سایز درست را انتخاب کردن')]),('Abmessung oder Umfang','اندازه، بزرگی یا گستره',[('die Größe eines Raums','اندازهٔ اتاق'),('die Größe eines Problems','بزرگی یک مشکل')]),('Körpergröße','قد انسان',[('die Größe messen','قد را اندازه‌گرفتن')])],[0,1,2,1]),
 1041:([('Kenntnisse oder Inhalte weitergeben','انتقال دانش یا محتوا',[('Wissen vermitteln','دانش منتقل کردن')]),('zwischen Parteien schlichten','میانجی‌گری میان طرف‌ها',[('zwischen zwei Parteien vermitteln','میان دو طرف میانجی‌گری کردن')]),('eine Stelle oder Wohnung vermitteln','پیدا یا معرفی کردن شغل یا مسکن',[('eine Wohnung vermitteln','خانه‌ای را معرفی یا فراهم کردن')])],[0,1,2,2,1]),
 1052:([('Reklamation oder Klage','شکایت یا اعتراض',[('eine Beschwerde einreichen','شکایتی ثبت کردن')]),('körperliche Beschwerden (Plural)','ناراحتی‌ها یا علائم جسمی (جمع)',[('unter Beschwerden leiden','از ناراحتی‌هایی رنج بردن')])],[0,0,1]),
 1056:([('Waren oder Leistungen bestellen','سفارش دادن کالا یا خدمات',[('online etwas bestellen','چیزی را اینترنتی سفارش دادن')]),('einen Tisch reservieren','رزرو کردن میز',[('einen Tisch bestellen','میز رزرو کردن')]),('jemanden zu einem Termin bestellen','کسی را برای حضور در وقتی تعیین‌شده فراخواندن',[('jemanden ins Büro bestellen','کسی را به دفتر فراخواندن')])],[0,1,1,2]),
 1063:([('etwas von jemandem kaufen','چیزی را از کسی خریدن',[('jemandem etwas abkaufen','چیزی از کسی خریدن')]),('jemandem eine Behauptung glauben (umgangssprachlich)','حرف یا بهانهٔ کسی را باور کردن',[('jemandem eine Ausrede nicht abkaufen','بهانهٔ کسی را باور نکردن')])],[0,1,0,1]),
 1069:([('Mitteilung oder zentrale Aussage','پیام یا مفهوم',[('eine klare Botschaft vermitteln','پیامی روشن منتقل کردن')]),('diplomatische Vertretung','سفارت',[('in der Botschaft arbeiten','در سفارت کار کردن')])],[0,0,1,1]),
 1077:([('höchster Punkt eines Berges','قلهٔ کوه',[('den Gipfel erreichen','به قله رسیدن')]),('Höhepunkt einer Entwicklung','اوج یک روند',[('den Gipfel erreichen (übertragen)','به اوج رسیدن (مجازاً)')]),('Treffen von Staats- oder Regierungschefs','اجلاس سران',[('an einem Gipfel teilnehmen','در اجلاس سران شرکت کردن')])],[0,0,2]),
 1082:([('Nerv des Körpers','عصب در بدن',[('einen Nerv verletzen','به عصب آسیب رساندن')]),('Blattader einer Pflanze','رگبرگ گیاه',[('feine Blattnerven','رگبرگ‌های ظریف')]),('Nerven als Geduld oder Belastbarkeit','اعصاب یا تحمل در اصطلاحات',[('jemandem auf die Nerven gehen','روی اعصاب کسی رفتن'),('starke Nerven haben','اعصاب قوی داشتن')])],[2,2,0,1]),
 1098:([('feine Flüssigkeitströpfchen verteilen','پاشیدن مایع به ذرات ریز',[('Parfüm versprühen','عطر اسپری کردن')]),('positive Stimmung ausstrahlen (übertragen)','شادی یا نشاط از خود نشان دادن (مجازاً)',[('gute Laune versprühen','شادابی پخش کردن')])],[0,0,1,1]),
 1124:([('Vorhandensein oder Bestehen','وجود داشتن',[('die Existenz nachweisen','وجود را اثبات کردن')]),('wirtschaftliche Lebensgrundlage','معیشت یا بقای اقتصادی',[('um die Existenz kämpfen','برای بقای اقتصادی تلاش کردن')])],[1,0]),
 1148:([('etwas tragende Person','شخص حمل‌کننده یا حامل',[('Träger einer Last','حامل یک بار')]),('betreibende oder verantwortliche Organisation','نهاد متولی یا پشتیبان',[('Träger einer Einrichtung','متولی یک مؤسسه')]),('stützendes Bauteil','عضو یا قطعهٔ باربر',[('einen Träger montieren','تیر باربر نصب کردن')])],[1,1,1]),
}
# Preexisting sense networks with example matches verified against both German and Persian contexts.
EXISTING_ROUTING={1034:[0,0],1070:[0,0],1071:[0,0],1072:[0,0],1073:[0,0],1074:[0,0,1],
 1079:[0,0],1092:[0,0],1095:[0,0],1096:[0,1],1100:[0,0],1111:[0,0],1116:[0,0],1117:[0,0],1123:[0,0]}
assert len(EXISTING_ROUTING)==15

def examples(c):
 b=c['back'];return b['existing_examples_de_fa_pending_qa']+b['additional_examples_de_fa_pending_qa']
def set_examples(c,all_examples):
 # Preserve existing/additional provenance and original distribution where possible.
 b=c['back'];old_n=len(b['existing_examples_de_fa_pending_qa']);b['existing_examples_de_fa_pending_qa']=all_examples[:old_n];b['additional_examples_de_fa_pending_qa']=all_examples[old_n:]
def make_ex(de,fa):return {'de':de,'fa':fa,'provenance':'L08_PHASE2_CONTEXTUAL_EDITORIAL_AUTHORED','status':'PENDING_G4_BILINGUAL_EXAMPLE_QA'}

def build():
 assert sha(PARENT.read_bytes())==EXPECTED_OWNER
 with zipfile.ZipFile(PARENT) as z:
  assert z.testzip() is None
  assert sha(z.read(MAIN))==EXPECTED_MAIN
  assert sha(z.read(SRC))==EXPECTED_MAP
  original={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
 queue=[json.loads(x) for x in QUEUE.read_text(encoding='utf8').splitlines()];assert len(queue)==157
 originals=[json.loads(l) for l in original[MAIN].splitlines()];before=copy.deepcopy(originals)
 lesson=[c for c in originals if c['lesson']=='L08'];assert len(lesson)==157
 ids={c['preview_card_id'] for c in lesson};assert len(ids)==157
 assert {x['card_id'] for x in queue}==ids
 qmap={x['card_id']:x for x in queue}
 counts=collections.Counter()
 changes={}
 records=[]
 for c in lesson:
  cid=c['preview_card_id'];q=qmap[cid];ordn=c['source_ordinal'];lemma=c['front']['base_headword_de'];back=c['back']
  prev=copy.deepcopy(c);cases=[]
  es=examples(c);assert all(e.get('de') and e.get('fa') for e in es)
  assert len(es)==q['example_count'],(ordn,lemma,len(es),q['example_count'])
  # 38 extra examples inherited statusless: explicit PENDING, NEVER automatic PASS.
  for e in es:
   if not e.get('status'):
    e['status']='PENDING_G4_BILINGUAL_EXAMPLE_QA';cases.append('EXAMPLE_STATUSLESS_TO_PENDING');counts['statusless_fixed']+=1
  # Existing exact duplicate German sentence: preserve distinct Persian paraphrases as alternatives.
  if ordn==1065:
   dct={};unique=[]
   for e in es:
    norm=' '.join(e['de'].split()).casefold()
    if norm in dct:
     t=dct[norm];a=t.setdefault('fa_alternatives',[])
     if e['fa'] != t['fa'] and e['fa'] not in a:a.append(e['fa'])
     cases.append('DEDUP_DE_PRESERVE_FA_ALTERNATIVE');counts['duplicates_resolved']+=1
    else:dct[norm]=e;unique.append(e)
   es=unique
  if ordn==1052:
   # Two merely reordered Magenbeschwerden sentences repeat the same sense and translation.
   # Keep one, avoid violating example diversity; the duplicate's text is retained for recovery in before/after.
   assert len(es)==4
   es.pop(3);cases.append('REMOVE_NEAR_DUPLICATE_MAGENBESCHWERDEN');counts['near_duplicates_resolved']+=1
  if ordn==1027:
   # Clearly distinguish untrennbar (paraphrasing) from trennbar (rewriting).
   assert 'hat die Aussage' in es[1]['de']
   es[1]['de']='Er umschrieb die Aussage mit einfachen Worten.'
   es[1]['fa']='او گفته را با واژه‌های ساده بیان کرد.'
   es[1]['status']='PENDING_G4_BILINGUAL_EXAMPLE_QA'
   cases.append('AMBIGUOUS_TRENNBAR_UNTRENNBAR_EXAMPLE_DISAMBIGUATED')
  if ordn==1030:
   assert len(es)==4
   es[1]['de']='Die Größe des Raums wird in Quadratmetern angegeben.'
   es[1]['fa']='اندازهٔ اتاق بر حسب متر مربع بیان می‌شود.'
   es[2]['de']='Die Größe des Kindes wird beim Arzt gemessen.'
   es[2]['fa']='قد کودک نزد پزشک اندازه‌گیری می‌شود.'
   for n in (1,2):es[n]['status']='PENDING_G4_BILINGUAL_EXAMPLE_QA'
   cases.append('REDUNDANT_JACKET_EXAMPLE_REPLACED_WITH_KOERPERGROESSE_SCOPE')
  if ordn==1142:
   # Shared ordinal but genuinely distinct lemmas. Never carry the other lemma as a target example.
   if lemma=='die Milliarde':
    es=[make_ex('Eine Milliarde entspricht tausend Millionen.','یک میلیارد برابر با هزار میلیون است.'),
        make_ex('Die Investition kostet eine Milliarde Euro.','این سرمایه‌گذاری یک میلیارد یورو هزینه دارد.')]
    expected='die Milliarde · Pl. Milliarden · 10^9';duden='https://www.duden.de/rechtschreibung/Milliarde'
   else:
    assert lemma=='die Billion'
    es=[make_ex('Eine Billion entspricht einer Million Millionen.','یک بیلیون در آلمانی برابر با یک میلیون میلیون است.'),
        make_ex('Der Betrag liegt bei einer Billion Euro.','این مبلغ یک بیلیون یورو است.')]
    expected='die Billion · Pl. Billionen · 10^12';duden='https://www.duden.de/rechtschreibung/Billion'
   assert c['front']['display_de_provisional']==expected
   c['front']['morphology_independently_validated']=True
   c['front']['morphology_origin']='L08_PHASE2_DUDEN_SCOPED_ARTICLE_PLURAL_AND_NUMBER_NOT_FULL_CARD'
   c['G2_morphology_review']['word_by_word_final_dictionary_QA_approved']=True
   c['G2_morphology_review']['L08_phase2_dictionary_attestation']={'source_url':duden,
      'scope':'FEMININE_NOUN_ARTICLE_PLURAL_AND_NUMBER_ONLY','date':DATE,'full_card_QA':False}
   c['G1_evidence_examples_not_yet_semantically_partitioned']=False
   c['G1_phase2_current_examples_partitioned_for_own_lemma_pending_G4']=True
   cases.append('SPLIT_LEMMA_TARGET_EXAMPLES_PARTITIONED_AND_FORMS_SCOPED_DUDEN')
   counts['split_scoped_forms_checked']+=1
  if ordn in NEW_NETWORKS:
   specs,routes=NEW_NETWORKS[ordn];assert len(routes)==len(es),(ordn,len(routes),len(es))
   assert not back.get('semantic_network_sense_anchored_pending_qa')
   sense_ids=[f'{cid}:L08P2:S{i+1}' for i in range(len(specs))]
   nets=[net(sense_ids[i],*specs[i]) for i in range(len(specs))]
   back['semantic_network_sense_anchored_pending_qa']=nets
   for e,slot in zip(es,routes):assert slot<len(nets);e['sense_id']=sense_ids[slot];e['sense_route_status']='CONTEXT_MATCH_PENDING_G4_SEMANTIC_QA'
   counts['new_networks']+=1;counts['new_sense_blocks']+=len(nets)
   counts['new_combinations']+=sum(len(n['Kombinationen_DE_FA']) for n in nets)
   cases.append('NEW_MEANING_SCOPED_WORDNETWORK_AND_CONTEXTUAL_EXAMPLE_ROUTES')
  if ordn in EXISTING_ROUTING:
   nets=back['semantic_network_sense_anchored_pending_qa'];routes=EXISTING_ROUTING[ordn]
   assert len(routes)==len(es),(ordn,len(routes),len(es))
   for e,slot in zip(es,routes):assert slot<len(nets);e['sense_id']=nets[slot]['sense_id'];e['sense_route_status']='CONTEXT_MATCH_PENDING_G4_SEMANTIC_QA'
   counts['existing_routes_resolved']+=len(routes)
   cases.append('EXISTING_MEANING_NETWORK_EXAMPLES_ROUTED')
  set_examples(c,es)
  # No unexplained form claim or premature release.
  c['formal_release_approved']=False;c['import_ready']=False
  for e in examples(c):
   assert e['de'].strip() and e['fa'].strip()
   assert e.get('status') and 'FULL_CARD_APPROVED' not in e['status']
  assert back['Formen_section'] is None
  if c!=prev:
   changes[cid]={'ordinal':ordn,'lemma':lemma,'actions':cases,'before':prev,'after':copy.deepcopy(c)}
  records.append({'preview_card_id':cid,'source_ordinal':ordn,'lemma':lemma,'phase1_priority':q['priority'],
   'editorial_scope':'ALL_157_CARDS_CURRENT_SAVED_FRONT_MEANINGS_EXAMPLES_NETWORK_HOLDS_CHECKED',
   'source_mapping_preserved':c['linked_original_source_ordinals']==prev['linked_original_source_ordinals'],
   'examples':len(examples(c)),'example_statuses_complete':all(e.get('status') for e in examples(c)),
   'all_de_fa_nonblank':all(e['de'] and e['fa'] for e in examples(c)),
   'sense_network_count':len(back.get('semantic_network_sense_anchored_pending_qa') or []),
   'sense_examples_unrouted':sum(bool(back.get('semantic_network_sense_anchored_pending_qa') and e.get('sense_id') not in {n['sense_id'] for n in back['semantic_network_sense_anchored_pending_qa']}) for e in examples(c)),
   'inherited_HOLD':bool(c.get('curated_HOLD_content_disposition_exists')),
   'object_changed':c!=prev,'actual_changed_fields':cases,
   'linguistic_final_approval':False,'phase2_disposition':'EDITORIAL_APPLIED_PENDING_G4' if c!=prev else 'KEEP_PROVISIONAL_AFTER_RULED_SCREEN_PENDING_G4',
   'import_ready':False})
 # Verify original data and only L08 modifications at object granularity.
 assert len(originals)==1571 and {c['preview_card_id'] for c in originals}=={c['preview_card_id'] for c in before}
 assert len(records)==157 and len({c['preview_card_id'] for c in records})==157
 assert len({c['source_ordinal'] for c in lesson})==156 # one source yields Milliarde + Billion
 untouched=[(b,a) for b,a in zip(before,originals) if b['lesson']!='L08'];assert len(untouched)==1414 # 1571-157
 assert all(b==a for b,a in untouched)
 after_by_id={c['preview_card_id']:c for c in originals};before_by_id={c['preview_card_id']:c for c in before}
 assert set(changes)=={cid for cid in before_by_id if before_by_id[cid]!=after_by_id[cid]}
 assert all(before_by_id[cid]['linked_original_source_ordinals']==after_by_id[cid]['linked_original_source_ordinals'] for cid in changes)
 assert all(c['import_ready'] is False and c['formal_release_approved'] is False for c in lesson)
 assert counts['statusless_fixed']==38 and counts['existing_routes_resolved']==31 and counts['duplicates_resolved']==1
 assert counts['split_scoped_forms_checked']==2
 assert all(not x['sense_examples_unrouted'] for x in records)
 assert all(x['example_statuses_complete'] and x['all_de_fa_nonblank'] for x in records)
 # No forms section created in back; no accidental copied full sentences as collocations.
 combos=[]
 for c in originals:
  for n in c['back'].get('semantic_network_sense_anchored_pending_qa') or []:
   for co in n.get('Kombinationen_DE_FA') or []:combos.append((c,co))
 local=[(c,co) for c,co in combos if c['lesson']=='L08']
 assert len(local)>=32
 assert all(co['de'].strip() and co['fa'].strip() for c,co in combos)
 assert all(not re.search(r'[.!?]$',co['de'].strip()) for c,co in local)
 # Global finite-verb-pattern regression: preserve known three non-L08 candidates, no new obvious L08 complete clauses.
 def finite_hits(c,co):
  return bool(re.search(r'\b(läuft|entscheidet|geht|arbeitet|macht|wird|sind|ist|hat)\b',co['de'],re.I))
 new_flagged=[(c['source_ordinal'],co['de']) for c,co in local if finite_hits(c,co)]
 assert not new_flagged,new_flagged
 # Current examples duplicates cross cards permitted; same-card exact DE duplicate count must be zero L08.
 duplicate=[]
 for c in originals:
  ds=collections.Counter(' '.join(e['de'].split()).casefold() for e in examples(c))
  for de,n in ds.items():
   if n>1:duplicate.append((c['lesson'],c['source_ordinal'],de,n))
 assert not [d for d in duplicate if d[0]=='L08']
 # No accidental split cross-copy:
 for c in [c for c in lesson if c['source_ordinal']==1142]:
  own='Milliarde' if c['front']['base_headword_de']=='die Milliarde' else 'Billion'
  other='Billion' if own=='Milliarde' else 'Milliarde'
  assert all(own in e['de'] and other not in e['de'] for e in examples(c))
 # Compose new primary JSONL using the same JSONL formatting mode as original.
 orig_lines=original[MAIN].splitlines();new_lines=[]
 for b,a,line in zip(before,originals,orig_lines):
  if b==a:new_lines.append(line)
  else:new_lines.append(json.dumps(a,ensure_ascii=False,sort_keys=True).encode('utf8'))
 new_primary=b'\n'.join(new_lines)+b'\n'
 assert new_primary!=original[MAIN]
 assert len(new_primary.splitlines())==1571
 assert sha(original[SRC])==EXPECTED_MAP
 # Current learner-data owner excludes stale generated QA projections as authority; new limited scoped projection included.
 updated={MAIN:new_primary}
 report={'schema':'aspekte-b1plus-L08-phase2-whole-157-card-editorial@1','date':DATE,'lesson':'L08',
  'phase':2,'phases_total':3,'status':'WHOLE_157_CARD_EDITORIAL_DISPOSITION_PERSISTED_PRIMARY_NONIMPORT',
  'source':{'parent_zip_sha256':EXPECTED_OWNER,'parent_main_sha256':EXPECTED_MAIN,'source_map_sha256':EXPECTED_MAP,
            'current_primary_sha256':sha(new_primary),'stable_card_ids':1571,'original_source_map_rows':1548},
  'coverage':{'cards':len(records),'phase1_priorities':dict(collections.Counter(x['phase1_priority'] for x in records)),
              'changed_primary_card_objects':len(changes),'unchanged_L08_cards':157-len(changes),'unchanged_other_lesson_objects':len(untouched),
              'new_meaning_networks':counts['new_networks'],'new_sense_blocks':counts['new_sense_blocks'],
              'new_meaning_scoped_combinations':counts['new_combinations'],
              'existing_network_example_routes_fixed':counts['existing_routes_resolved'],
              'statusless_to_PENDING':counts['statusless_fixed'],'duplicate_exact_German_groups_removed':counts['duplicates_resolved'],
              'near_duplicate_paraphrase_removed':counts['near_duplicates_resolved'],
              'two_1142_lexemes_partitioned':counts['split_scoped_forms_checked'],
              'L08_examples_before':sum(len(examples(c)) for c in before if c['lesson']=='L08'),
              'L08_examples_after':sum(len(examples(c)) for c in lesson),
              'L08_combinations_after':len(local),'global_combinations_after':len(combos),
              'L08_unrouted_network_examples_after':sum(x['sense_examples_unrouted'] for x in records),
              'L08_statusless_examples_after':0,'L08_exact_same_card_duplicate_groups_after':0,
              'global_exact_same_card_duplicate_groups_after':len(duplicate),
              'inherited_L08_release_HOLDS':sum(x['inherited_HOLD'] for x in records)},
  'scoped_dictionary_attestations':[
   {'lemma':'die Milliarde','url':'https://www.duden.de/rechtschreibung/Milliarde','scope':'feminine, plural Milliarden, 10^9'},
   {'lemma':'die Billion','url':'https://www.duden.de/rechtschreibung/Billion','scope':'feminine, plural Billionen, 10^12'}],
  'release':{'formal_approved_cards':0,'import_ready':False,'real_app_import_tested':False,
             'phase3_full_case_level_bilingual_semantic_signoff':'PENDING','phase3_actual_runtime_import':'PENDING',
             'status':'RELEASE_BLOCKED_NONIMPORT'},
  'limitations':['157 structured editorial dispositions are not 157 fully verified bilingual cards',
                 'Existing 38 L08 curated HOLDs remain; content corrections do not auto-clear them',
                 'Other lessons global finite-clause candidates remain 3 at L02/158 L03/232 L09/1266',
                 'Preexisting historical G5 QA snapshots in archive are not authority; use the new Phase2 L08 views',
                 'No cross-level CSV or textbook source was re-imported',
                 'Synonym/antonym sections in new networks intentionally empty until supported, not artificially filled'],
  'next':'L08_PHASE3_STRICT_CASE_LEVEL_BILINGUAL_RELATION_AND_RUNTIME_GATE_OR_BLOCKED'}
 # Output strict technical QA, no falsely rendered G4 signoff.
 page=['<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Aspekte B1+ L08 Phase2 NONIMPORT</title>',
 '<style>body{font-family:system-ui;max-width:1100px;margin:auto;padding:26px;color:#222}section{border-bottom:1px solid #ddd;padding:14px 0}.fa{direction:rtl;text-align:right}aside{color:#986600}summary{cursor:pointer}.network{background:#f4f6f7;padding:10px;margin:8px 0}</style></head><body><h1>Aspekte B1+ · Lektion 08 · Phase2</h1>',
 '<aside>QA ONLY · NONIMPORT · 157 editorial dispositions are not 157 fully approved cards.</aside>']
 tsv=io.StringIO();writer=csv.writer(tsv,delimiter='\t',lineterminator='\n')
 writer.writerow(['card_id','source_ordinal','front_de','meaning_fa','example_count','sense_count','release'])
 for c in lesson:
  b=c['back'];es=examples(c);nets=b.get('semantic_network_sense_anchored_pending_qa') or []
  writer.writerow([c['preview_card_id'],c['source_ordinal'],c['front']['display_de_provisional'],b['meanings_fa_provisional'],len(es),len(nets),'BLOCKED_NONIMPORT'])
  page.append('<section><h2>'+html.escape(c['front']['display_de_provisional'])+'</h2><p class="fa">'+html.escape(b['meanings_fa_provisional'])+'</p><ol>')
  for e in es:
   page.append('<li>'+html.escape(e['de'])+'<p class="fa">'+html.escape(e['fa'])+'</p><small>'+html.escape(e['status'])+'</small></li>')
  page.append('</ol>')
  for n in nets:
   page.append('<div class="network"><strong>'+html.escape(n['sense_de'])+'</strong><p class="fa">'+html.escape(n['sense_fa'])+'</p>')
   for co in n.get('Kombinationen_DE_FA',[]):page.append('<p>'+html.escape(co['de'])+' — '+html.escape(co['fa'])+'</p>')
   page.append('</div>')
  page.append('</section>')
 page.append('</body></html>')
 newfiles={
  'Lessons/L08/L08-PHASE2-WHOLE-157-CARD-REPORT.json':jbytes(report),
  'Lessons/L08/L08-PHASE2-157-CARD-EDITORIAL-DISPOSITIONS.jsonl':(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in records)).encode(),
  'Lessons/L08/L08-PHASE2-CHANGED-CARD-BEFORE-AFTER.json':jbytes(changes),
  'Lessons/L08/L08-PHASE2-157-CARD-FRONT-BACK-QA-ONLY.html':'\n'.join(page).encode(),
  'Lessons/L08/L08-PHASE2-157-CARD-OFFLINE-TSV-QA-ONLY.tsv':tsv.getvalue().encode(),
  'README-L08-PHASE2-NONIMPORT.md':('\n'.join([
   '# Aspekte B1+ Lektion 08, Phase 2/3 — NONIMPORT',
   'Whole-lesson editorial record for 157 existing card IDs; current learner data is '+MAIN,
   'L08 Phase1 audit is historical. Phase2 edited and persisted primary 1571-card JSONL.',
   'Historical G5 QA-only projections and inherited reports do not represent the revised Phase2 card data.',
   'The new L08 QA-only HTML and TSV are NOT German Flashcards Pro runtime import results.',
   '38 original L08 HOLD markers remain; all final G4 semantic QA and real app import are pending.',
   'No publisher CSV reimport, no forced extra reviewer, no deletion, no release.',
   'Canonical source map '+SRC+' is SHA-identical to parent.',
   ])+'\n').encode()
 }
 # Persist the ACTUAL full-corpus v2 and v4 QA results into the new authoritative package.
 import importlib.util
 for module_name,script_name,archive_report in [
   ('finite_v4','qa_combinationen_finite_clause_v4.py','Lessons/L08/L08-PHASE2-GLOBAL-FINITE-CLAUSE-V4.json'),
   ('strict_v2','qa_combinationen_strict_v2.py','Lessons/L08/L08-PHASE2-GLOBAL-COLLOCATION-STRUCTURAL-V2.json')]:
  spec=importlib.util.spec_from_file_location(module_name,BASE/script_name);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  r=mod.audit(originals)
  if module_name=='finite_v4':
   assert r['possible_full_sentence_collocations']==3
   assert all(x['lesson']!='L08' for x in r['issues'])
  else:assert r['structural_gate_passed'] is True
  newfiles[archive_report]=jbytes(r)
 original.update(updated);original.update(newfiles)
 lines=[]
 for n in sorted(original):lines.append(f'{sha(original[n])}  {n}\n')
 original['SHA256SUMS.txt']=''.join(lines).encode()
 with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as dest:
  for n,b in original.items():dest.writestr(n,b)
 # Reopen the ACTUAL finished artifact from disk rather than trusting only an in-memory sidecar.
 with zipfile.ZipFile(OUT) as zz:
  assert zz.testzip() is None
  listed=zz.read('SHA256SUMS.txt').decode().splitlines();assert len(listed)==len(zz.namelist())-1
  for line in listed:
   h,n=line.split('  ',1);assert sha(zz.read(n))==h,(n,h)
  new=[json.loads(l) for l in zz.read(MAIN).splitlines()]
  assert len(new)==1571
  assert zz.read(SRC)==original[SRC]
  assert sha(zz.read(MAIN))==sha(new_primary)
  assert all(before[i]==new[i] for i in range(1571) if before[i]['lesson']!='L08')
  assert sum(before[i]!=new[i] for i in range(1571))==len(changes)
  assert sum(len(examples(x)) for x in new if x['lesson']=='L08')==report['coverage']['L08_examples_after']
  assert len(list(csv.reader(io.StringIO(zz.read('Lessons/L08/L08-PHASE2-157-CARD-OFFLINE-TSV-QA-ONLY.tsv').decode()),delimiter='\t')))==158
  assert all(not x['import_ready'] for x in new)
 summary={'output_file':str(OUT),'output_sha256':sha(OUT.read_bytes()),'output_bytes':OUT.stat().st_size,
          'archive_members':len(original),'internal_member_sha256_verified':len(listed),'zip_crc':'PASS',
          'primary_sha256':sha(new_primary),'source_map_sha256':sha(original[SRC]),
          'changed_primary_card_ids':len(changes),'changed_ordinals':sorted({x['ordinal'] for x in changes.values()}),
          'counts':report['coverage'],'release':report['release']}
 (BASE/'L08-PHASE2-REPORT.json').write_bytes(jbytes(report))
 (BASE/'L08-PHASE2-SAVED-OWNER-VERIFICATION.json').write_bytes(jbytes(summary))
 (BASE/'L08-PHASE2-157-DISPOSITIONS.jsonl').write_bytes(newfiles['Lessons/L08/L08-PHASE2-157-CARD-EDITORIAL-DISPOSITIONS.jsonl'])
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':build()