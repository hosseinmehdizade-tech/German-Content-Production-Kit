#!/usr/bin/env python3
"""Case-level P1 content hold remediation from exact verified Gate02 owner.

Scoped: legacy shared-source lemma identity vs true language holds, plus
nontrivial meaning/exemplar routing repairs. Not publication signoff.
"""
import collections, copy, datetime, hashlib, json, os, pathlib, re, zipfile

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / 'Aspekte-B1plus-GLOBAL-HOLD-GATE02-359-CASE-PRIORITY-REPAIRS-NONIMPORT-20261110.zip'
LEDGER = ROOT / 'GATE02-359-HOLD-RISK-DECISION-LEDGER-20261110.jsonl'
OUTPUT = ROOT / 'Aspekte-B1plus-P1-SCOPED-131-HOLD-RESOLUTION-CURATED-NONIMPORT-20261110.zip'
EXPECTED_ZIP_SHA = '0d4f4716c2df5df5670c5262d28ed73cf0c9fdb01fd868e4dbb27d8690583d2e'
EXPECTED_PRIMARY_SHA = '150dd8da7a30107e87dc328f533bf52b75cea2c26699d497bc4c1bba795702e8'
EXPECTED_MAP_SHA = 'c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
DATE = '2026-11-10'
P1_FOLDER='Global-Backlog/P1-HOLD-FOLLOWUP'

SOURCE_LINKS = {
 'die Heimat':'https://www.duden.de/rechtschreibung/Heimat',
 'die Heimatstadt':'https://www.duden.de/rechtschreibung/Heimatstadt',
 'abschließen':'https://www.duden.de/rechtschreibung/abschlieszen',
 'aufhören':'https://www.duden.de/rechtschreibung/aufhoeren',
 'der Service':'https://www.duden.de/rechtschreibung/Service_Dienstleistung',
 'das Kaffeeservice':'https://www.duden.de/rechtschreibung/Service_Geschirr',
 'weitgehend':'https://www.duden.de/rechtschreibung/weitgehend',
 'weitergehend':'https://www.duden.de/rechtschreibung/weitergehend',
 'die Kleider':'https://www.duden.de/rechtschreibung/Kleid',
 'die Kochshow':'https://www.duden.de/rechtschreibung/Kochshow',
}
# When available, dictionary URLs are *scoped*, not blanket card signoff.
EDITORIAL_EVIDENCE = {
 ('L01',13,'der Kontakt'):'Social/technical Kontakt is not a synonym of menschliche Beziehung; all current social examples are clearly routed; add a technical example for second existing sense.',
 ('L01',60,'schimpfen'):'Existing mit+Dat. scolding and over+Acc. complaining are distinct valencies; create dedicated sense and example.',
 ('L04',410,'die Karte'):'Source-sense map has five valid contextual interpretations but examples cover only game card and map; add ticket/menu/ID-card examples, each routed separately.',
 ('L09',1214,'eingehen'):'Existing five senses include perishing and entering obligations without independent DE/FA examples; add to their established sense IDs.',
 ('L10',1538,'romantisch'):'The existing idealized-Landleben example is wrongly routed to the love sense; separate idealization with own meaning and phrase.',
 ('L10',1448,'anhalten'):'Duration sense S2 lacks any example despite accurate existing S1 stop and S3 urge.',
 ('L10',1445,'ergreifen'):'Physical grasp S1 lacks example, but Wort ergreifen/Gelegenheit ergreifen/being moved are other distinct senses.',
 ('L10',1435,'die Kleider'):'Differentiate plural of das Kleid (one-piece dresses) from generic Kleidung; existing examples only cover generic clothing.',
 ('L10',1377,'verbrennen'):'Distinct energy/calorie sense S3 was left without bilingual example, while burning/injury examples are routed.',
 ('L10',1364,'kippen'):'Liquid-pouring sense S3 has no example, distinct from tilt and window position.',
 ('L10',1352,'anlassen'):'Engine starting S3 needs a separate context rather than only leaving lights/clothing on.'
}


def sha(data):return hashlib.sha256(data).hexdigest()
def dump(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
def jsonl(rows):return ''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows).encode()
def contexts(card):return card['back'].get('existing_examples_de_fa_pending_qa',[])+card['back'].get('additional_examples_de_fa_pending_qa',[])
def senses(card):return card['back'].get('semantic_network_sense_anchored_pending_qa') or []
def card_of(cards,key):
 matches=[c for c in cards if (c['lesson'],c['source_ordinal'],c['front']['base_headword_de'])==key]
 if len(matches)!=1:raise ValueError((key,'AMBIGUOUS',len(matches)))
 return matches[0]
def add_example(card,de,fa,index,why):
 sc=senses(card)
 assert 1<=index<=len(sc),(card['preview_card_id'],index)
 assert not any(e.get('de')==de for e in contexts(card))
 new={'de':de,'fa':fa,'sense_id':sc[index-1]['sense_id'],'status':'PENDING_G4_DE_FA_SEMANTIC_QA',
      'provenance':'P1_CASE_SPECIFIC_BILINGUAL_EDITORIAL_20261110',
      'P1_case_scope':why}
 card['back'].setdefault('additional_examples_de_fa_pending_qa',[]).append(new)
 return {'de':de,'fa':fa,'sense_id':new['sense_id'],'status':new['status']}
def add_sense(card,n,de,fa,combos,why):
 ss=senses(card)
 assert len(ss)==n-1,(card['preview_card_id'],len(ss),n)
 if not ss: raise ValueError('Cannot template empty sense network')
 base=copy.deepcopy(ss[0]);
 for k in ['Antonyme','Feste_Wendungen_DE_FA','Satzmuster_DE_FA','Synonyme','Verwandte_Woerter_KEINE_Synonyme','Wortfamilie']:
  if k in base:base[k]=[]
 base.update({'sense_id':card['preview_card_id']+':'+card['lesson']+'P1:S'+str(n),
 'sense_de':de,'sense_fa':fa,'Kombinationen_DE_FA':[{'de':a,'fa':b,'status':'PENDING_G4_DE_FA_COLLOCATION_QA'} for a,b in combos],
 'source':'P1_CASE_SCOPED_EDITORIAL_20261110','status':'PENDING_G4_DE_FA_SEMANTIC_EXAMPLE_RELATION_QA',
 'P1_case_scope':why})
 card['back']['semantic_network_sense_anchored_pending_qa'].append(base)
 return base

# Explicit independent-lemma boundary decisions, checked in this run against
# actual DE/FA examples and front wording. We do NOT certify full card release.
SPLIT_REASON={
 2:'Heimat means homeland/home region, Heimatstadt means home town: each dedicated bilingual example uses its own lemma and distinct location scope.',
 6:'notieren records information, aufschreiben writes something down: independent separability, conjugation and dedicated German–Persian examples.',
 9:'mäßig shows degree/mediocre evaluation, moderat expresses mild/appropriate values: separate usages and bilingual examples, not blindly interchangeable.',
 11:'anhand example-evidence, mithilfe assistance, aufgrund causal basis are distinct genitive constructions with different example meanings.',
 12:'beenden ends an activity, abschließen also locks/signs, aufhören stops continuing: original combined row already split into contextually correct learner lemmas.',
 13:'Kontakt vs Beziehung differ; relationship and technical-contact meanings are independent; add Kontakt technical example to cover its existing second sense.',
 17:'ehrgeizig ambition as personality vs ambitioniert ambitious project: examples distinguish intended adjective use.',
 21:'heldenhaft heroic vs mutig courageous vs tapfer enduring hardship: three nonidentical but related adjectives with dedicated examples.',
 36:'tätig means professionally active; aktiv is general participation; example contexts distinguish them.',
 40:'Rabe raven and Krähe crow are distinct birds; independent nouns and fauna examples, no false synonym merge.',
 44:'The Reichtum card covers wealth vs abundance as two sense-specific examples; inherited shared-row label does not contradict current per-lemma content.',
 47:'Schlüsselwort and Stichwort are related but differ in typical text keyword vs cue/heading contexts; examples are independent.',
 48:'widersprechen governs dative and means contradict/argue against; ablehnen governs accusative and means reject, with separate correct examples.',
 49:'Aussehen appearance, Äußere exterior and Erscheinung occurrence/appearance: distinct nouns, appropriate gender/plural distinctions and bilingual examples.',
 65:'weitgehend largely/very extensive vs weitergehend going further: examples establish nonidentical uses; weitestgehend usage is lexicographically attested.',
 70:'Ausnahme exception to a rule vs Sonderfall special case: dedicated examples, not duplicate unit.',
 358:'Freizeitbeschäftigung pastime, Freizeitaktivität leisure activity, Freizeitgestaltung organization of leisure: independent compounds and translations.',
 714:'der Service is service/maintenance; das Kaffeeservice is matching coffee crockery; distinct gender and pronunciation/meaning.',
 771:'denkbar imaginable vs undenkbar unthinkable: distinct polar adjectives, clear context examples.',
 773:'erwünscht desired vs unerwünscht unwanted: distinct polar adjectives in examples.',
 956:'jemals ever vs niemals never: distinct adverbs with different negative polarity.',
 1256:'der Seemann male seafarer with independent shipboard context; source-shared identity already partitioned.',
 1302:'Kochshow cooking entertainment show vs Kochsendung cooking TV/radio programme; each has its own validated-topic example, no unsupported merger.',
 1487:'Hochwasser high water/flood tide added in Gate02 is still pending scoped review: DO NOT CLOSE its hold.'
}

def main():
 assert sha(SOURCE.read_bytes())==EXPECTED_ZIP_SHA
 with zipfile.ZipFile(SOURCE) as z:
  names=z.namelist(); assert z.testzip() is None
  manifest={n:s for s,n in [line.split('  ',1) for line in z.read('SHA256SUMS.txt').decode().splitlines()]}
  assert set(manifest)==set(names)-{'SHA256SUMS.txt'}
  assert all(sha(z.read(n))==manifest[n] for n in manifest)
  cp=next(n for n in names if '1571-FRONT-BACK' in n)
  mp=next(n for n in names if n.endswith('1548-SOURCE-MAP-UNMODIFIED.tsv'))
  assert sha(z.read(cp))==EXPECTED_PRIMARY_SHA and sha(z.read(mp))==EXPECTED_MAP_SHA
  initial=z.read(cp).decode().splitlines()
  cards=[json.loads(s) for s in initial]
  files={n:z.read(n) for n in names if n!='SHA256SUMS.txt'}
 assert len(cards)==1571 and len({c['preview_card_id'] for c in cards})==1571
 byid={c['preview_card_id']:c for c in cards}
 p1q=[json.loads(s) for s in LEDGER.read_text().splitlines() if s.strip()]
 assert len(p1q)==359
 p1=[q for q in p1q if q['priority']=='P1' and q['hold_after_gate02']]
 assert len(p1)==131
 split=[q for q in p1 if 'SHARED_SOURCE_LEMMAS_REQUIRE_DISTINCT_EXAMPLE_SCOPE' in q['risk_signals']]
 assert len(split)==50
 # Verify that these candidates have genuinely distinct contextual German examples
 # from their own original-source siblings, no cross-lemma example swaps.
 original_source_groups=collections.defaultdict(list)
 for c in cards:
  for source in c['linked_original_source_ordinals']:
   original_source_groups[source].append(c)
 closure_ids=[]; case_evidence=[]; editorial_actions=[]
 for q in split:
  c=byid[q['card_id']]; original=q['source_ordinal']; assert c['source_ordinal']==original
  if original in (1256,1487): continue # 1256 has no independent sibling; 1487 has new pending tidal sense
  assert len(original_source_groups[original])>=2,(original,c['preview_card_id'])
  a=contexts(c);assert a and all(e['de'].strip() and e['fa'].strip() for e in a)
  other={e['de'].strip().casefold() for sib in original_source_groups[original] if sib['preview_card_id']!=c['preview_card_id'] for e in contexts(sib)}
  assert not any(e['de'].strip().casefold() in other for e in a),(original,c['preview_card_id'],'DUPLICATED_SOURCE_EXAMPLE')
  assert original in SPLIT_REASON
  sc=senses(c)
  if sc:
   valid={s['sense_id'] for s in sc}
   assert all(e.get('sense_id') in valid for e in a),(c['preview_card_id'],'UNROUTED')
  else:assert all(e.get('sense_id') is None for e in a)
  old=c['curated_HOLD_content_disposition_exists'];assert old is True
  c['curated_HOLD_content_disposition_exists']=False
  rationale=SPLIT_REASON[original]
  c['global_HOLD_resolution']={'date':DATE,'status':'CASE_SPECIFIC_LEGACY_SHARED_SOURCE_HOLD_CLOSED_NOT_FULL_CARD_RELEASE',
   'scope':'Dedicated learner lemma identity, DE example scope, FA semantic relevance and relevant source split are case-reviewed; old editorial overlay flags are historical. Full G4 morphology/idiom and importer acceptance still pending.',
   'case_reason':rationale,'case_example_evidence':[{'de':e['de'],'fa':e['fa'],'sense_id':e.get('sense_id')} for e in a],
   'source_row_ordinal':original,'scope_only':'legacy shared-row/unpartitioned DE example hold',
   'lexicographic_support_urls':[SOURCE_LINKS[c['front']['base_headword_de']]] if c['front']['base_headword_de'] in SOURCE_LINKS else [],
   'formal_release_approved':False,'release':'RELEASE_BLOCKED_NONIMPORT'}
  closure_ids.append(c['preview_card_id'])
  case_evidence.append({'card_id':c['preview_card_id'],'lesson':c['lesson'],'source_ordinal':original,'lemma':c['front']['base_headword_de'],'reason':rationale,'bilingual_context_examples':c['global_HOLD_resolution']['case_example_evidence'],'old_legacy_flags_preserved':c['audit_flags'],'scoped_content_HOLD_closed':True,'formal_release_approved':False})
 # 11 distinct P1 semantic editorial cases, all retained HOLD even when edited (except Kontakt scoped split)
 for key,reason in EDITORIAL_EVIDENCE.items():
  c=card_of(cards,key); assert c['curated_HOLD_content_disposition_exists'] is True or c['front']['base_headword_de']=='der Kontakt',key
  made=[]
  if key==('L01',13,'der Kontakt'):
   made.append(add_example(c,'Die Kontakte am Stecker sind verschmutzt.','کنتاکت‌های دوشاخه کثیف شده‌اند.',2,reason))
  elif key==('L01',60,'schimpfen'):
   add_sense(c,2,'über eine Sache schimpfen (über + Akkusativ)','از چیزی گله یا شکایت کردن',[('über die lange Wartezeit schimpfen','از انتظار طولانی شکایت کردن')],reason)
   made.append(add_example(c,'Die Gäste schimpften über die lange Wartezeit.','مهمانان از انتظار طولانی شکایت کردند.',2,reason))
  elif key==('L04',410,'die Karte'):
   made.extend([add_example(c,'Hast du schon eine Karte für das Konzert?','برای کنسرت بلیت گرفته‌ای؟',3,reason),
     add_example(c,'Im Restaurant bat er den Kellner um die Karte.','در رستوران از پیشخدمت منوی غذا را خواست.',4,reason),
     add_example(c,'Zeigen Sie bitte Ihre Karte zur Identitätsprüfung.','لطفاً کارت خود را برای بررسی هویت نشان دهید.',5,reason)])
  elif key==('L09',1214,'eingehen'):
   made.extend([add_example(c,'Die Blumen sind ohne Wasser eingegangen.','گل‌ها بدون آب خشک شدند و از بین رفتند.',4,reason),
     add_example(c,'Die beiden Firmen sind eine Partnerschaft eingegangen.','دو شرکت وارد یک همکاری مشترک شدند.',5,reason)])
  elif key==('L10',1538,'romantisch'):
   add_sense(c,2,'die Wirklichkeit idealisierend, schwärmerisch','آرمانی و خیال‌پردازانه؛ با نگاهی ایده‌آل‌سازی‌شده به واقعیت',
    [('romantische Vorstellungen vom Landleben haben','تصوری آرمانی از زندگی روستایی داشتن')],reason)
   c['back']['meanings_fa_provisional']='عاشقانه و احساسی؛ خیال‌پردازانه یا آرمانی (ایده‌آل‌سازی واقعیت)'
   es=[e for e in contexts(c) if e['de']=='Sie hat romantische Vorstellungen vom Leben auf dem Land.']
   assert len(es)==1 and es[0]['sense_id']==senses(c)[0]['sense_id']
   es[0]['sense_id']=senses(c)[1]['sense_id'];es[0]['P1_route_correction']='IDEALIZED_RURAL_LIFE_NOT_LOVE_OR_ROMANCE'
   made.append({'rerouted_existing':es[0]['de'],'new_sense':senses(c)[1]['sense_id']})
  elif key==('L10',1448,'anhalten'):
   made.append(add_example(c,'Die Schmerzen haben mehrere Tage angehalten.','دردها چند روز ادامه داشتند.',2,reason))
  elif key==('L10',1445,'ergreifen'):
   made.append(add_example(c,'Sie ergriff seine Hand und zog ihn hoch.','او دستش را گرفت و او را بلند کرد.',1,reason))
  elif key==('L10',1435,'die Kleider'):
   made.append(add_example(c,'Im Schaufenster hängen drei lange Kleider.','در ویترین سه پیراهن بلند یک‌تکه آویزان است.',2,reason))
  elif key==('L10',1377,'verbrennen'):
   made.append(add_example(c,'Beim Radfahren verbrennt sie viele Kalorien.','او هنگام دوچرخه‌سواری کالری زیادی می‌سوزاند.',3,reason))
  elif key==('L10',1364,'kippen'):
   made.append(add_example(c,'Er kippte das Wasser in den Ausguss.','او آب را در راه‌آب خالی کرد.',3,reason))
  elif key==('L10',1352,'anlassen'):
   made.append(add_example(c,'Der Fahrer ließ den Motor an und fuhr los.','راننده موتور را روشن کرد و راه افتاد.',3,reason))
  else:raise ValueError(key)
  c['P1_case_level_editorial_20261110']={'reason':reason,'actions':made,'full_release_approved':False,'new_examples_status':'PENDING_G4_DE_FA_SEMANTIC_QA'}
  editorial_actions.append({'lesson':key[0],'source_ordinal':key[1],'headword':key[2],'card_id':c['preview_card_id'],'reason':reason,'actions':made,'HOLD_after':c['curated_HOLD_content_disposition_exists']})
 assert len(closure_ids)==48 and len(editorial_actions)==11
 assert len(set(closure_ids))==48
 for c in cards:
  assert c['formal_release_approved'] is False and c['import_ready'] is False
  ss=senses(c)
  if ss:
   valid={x['sense_id'] for x in ss}
   for e in contexts(c):
    # preserve existing multi-sense association if sense_ids used
    ids=e.get('sense_ids',[])
    if ids: assert set(ids).issubset(valid)
    elif e.get('sense_id') is not None: assert e['sense_id'] in valid,(c['preview_card_id'],e)
 # Validate exact corpus identities and byte-preserve all unaffected JSONL rows
 changed=[];modified_ids=[];updated_lines=[]
 for orig,c in zip(initial,cards):
  old=json.loads(orig)
  if old==c:updated_lines.append(orig);continue
  changed.append({'card_id':c['preview_card_id'],'lesson':c['lesson'],'original_ordinal':c['source_ordinal'],'old':old,'new':c})
  modified_ids.append(c['preview_card_id']);updated_lines.append(json.dumps(c,ensure_ascii=False,sort_keys=True))
 assert len(changed)>=49 and all(c['card_id'] in set(closure_ids)|set(a['card_id'] for a in editorial_actions) for c in changed)
 mainnew=('\n'.join(updated_lines)+'\n').encode()
 assert len(cards)==1571 and len({x['preview_card_id'] for x in cards})==1571
 holds_before=sum(json.loads(x)['curated_HOLD_content_disposition_exists'] for x in initial)
 holds_after=sum(c['curated_HOLD_content_disposition_exists'] for c in cards)
 assert holds_before==351 and holds_after==303
 p1remaining=[q for q in p1 if byid[q['card_id']]['curated_HOLD_content_disposition_exists']]
 assert len(p1remaining)==83
 # Evidence for EACH one of 131 P1s, with specific current DE/FA examples,
 # reason, actual modified fields, and deterministic account of any closure.
 decisions=[]
 for q in p1:
  c=byid[q['card_id']];new=next((d for d in changed if d['card_id']==q['card_id']),None)
  before_hash=q.get('unchanged_card_object_sha256_before')
  decisions.append({'card_id':q['card_id'],'lesson':q['lesson'],'headword':c['front']['base_headword_de'],
   'source_ordinal':c['source_ordinal'],'priority_original':'P1','risk_signals':q['risk_signals'],
   'scope_completed':'SEPARATE_LEXEME_AND_DE_FA_EXAMPLE_IDENTITY' if q['card_id'] in closure_ids else 'CASE_LEVEL_REVIEW_AND_PENDING_SUBSTANTIVE_CORRECTIONS',
   'HOLD_before':True,'HOLD_after':c['curated_HOLD_content_disposition_exists'],
   'resolution':'SCOPED_CONTENT_HOLD_CLOSED' if q['card_id'] in closure_ids else 'RETAIN_HOLD_FULL_SEMANTIC_CASE_QA_PENDING',
   'evidence_DE_FA':[{'de':e['de'],'fa':e['fa'],'sense_id':e.get('sense_id')} for e in contexts(c)],
   'current_senses':[{'id':s['sense_id'],'de':s['sense_de'],'fa':s['sense_fa']} for s in senses(c)],
   'actual_primary_card_modified':bool(new),
   'specific_case_reason':(SPLIT_REASON.get(q['source_ordinal']) if q['card_id'] in closure_ids else ('Source-row shared-lexeme risk flagged, but actual canonical 1571-card set contains no independent sibling for Seemann; retain HOLD pending explicit lemma/usage review.' if q['source_ordinal']==1256 and c['front']['base_headword_de']=='der Seemann' else ('Gate02 authored new coastal-tidal Hochwasser sense/example; retain HOLD pending semantic case-level QA.' if q['source_ordinal']==1487 and c['front']['base_headword_de']=='das Hochwasser' else EDITORIAL_EVIDENCE.get((q['lesson'],q['source_ordinal'],c['front']['base_headword_de']),q['remaining_action_if_open'])))),
   'release_approved':False})
 assert len(decisions)==131
 q_next=[]
 for q in p1q:
  d=copy.deepcopy(q);c=byid[q['card_id']];d['hold_after_P1']=c['curated_HOLD_content_disposition_exists'];d['P1_followup_scoped_closed']=q['card_id'] in closure_ids;d['case_evidence_ref']=P1_FOLDER+'/P1-131-CASE-DECISION-LEDGER.jsonl';q_next.append(d)
 corpus_examples=sum(len(contexts(c)) for c in cards)
 report={'schema':'aspekte-b1plus-P1-131-case-evidence-fix@1','date':DATE,'status':'P1_SHARED_SPLIT_SCOPED_HOLDS_CLOSED_WITH_PROOF_NONIMPORT',
   'input_owner_SHA256':EXPECTED_ZIP_SHA,'input_primary_SHA256':EXPECTED_PRIMARY_SHA,'new_primary_SHA256':sha(mainnew),
   'L01_to_L10_cards':1571,'original_source_mapping_sha256':EXPECTED_MAP_SHA,
   'P1_current_cases_reviewed':131,'P1_legacy_independent_lemma_scope_cases':50,'P1_legacy_cases_held_due_new_unverified_sense':1,'P1_legacy_cases_held_due_no_sibling_1256':1,
   'P1_scoped_content_hold_closures':len(closure_ids),'P1_remaining':len(p1remaining),
   'all_HOLDs_before':holds_before,'all_HOLDs_after':holds_after,
   'other_priority_hold_cases_preserved':220, 'actual_primary_changed_cards':len(changed),'real_semantic_editorial_card_actions':len(editorial_actions),
   'L10_morphology_or_semantics_global_APPROVED':0,'full_semantic_QA_done':False,'native_app_import_run':False,'release':'RELEASE_BLOCKED_NONIMPORT',
   'bilingual_example_pairs_after':corpus_examples,'new_P1_examples':sum(1 for a in editorial_actions for e in a['actions'] if 'de' in e),
   'existing_example_reroutes':1,
   'lexical_reference_urls':['https://www.duden.de/rechtschreibung/Karte','https://www.duden.de/rechtschreibung/abschlieszen','https://www.duden.de/rechtschreibung/romantisch','https://www.duden.de/rechtschreibung/anhalten','https://www.duden.de/rechtschreibung/ergreifen','https://www.duden.de/rechtschreibung/Kleid','https://www.duden.de/rechtschreibung/verbrennen','https://www.duden.de/rechtschreibung/schimpfen','https://www.duden.de/rechtschreibung/eingehen','https://www.duden.de/rechtschreibung/Service_Geschirr','https://www.duden.de/rechtschreibung/weitgehend'],
   'disclaimer':'These are scoped legacy source-division HOLD closures, not independent all-content proof and not app release approval. P1 risk tier does not mean 131 mistakes. Zero re-import from original publisher files.'}
 files[cp]=mainnew
 files.update({
  P1_FOLDER+'/P1-131-CASE-DECISION-LEDGER.jsonl':jsonl(decisions),
  P1_FOLDER+'/P1-48-SCOPED-CLOSURES.json':dump(case_evidence).encode(),
  P1_FOLDER+'/P1-11-LINGUISTIC-EDITORIAL-REPAIRS.json':dump(editorial_actions).encode(),
  P1_FOLDER+'/P1-ALL-CHANGED-CARDS-FULL-BEFORE-AFTER.json':dump(changed).encode(),
  P1_FOLDER+'/P1-359-CURRENT-STATUS-LEDGER.jsonl':jsonl(q_next),
  P1_FOLDER+'/P1-WHOLE-CORPUS-QA-REPORT.json':dump(report).encode(),
  P1_FOLDER+'/build_P1_scope_v1.py':pathlib.Path(__file__).read_bytes(),
 })
 if OUTPUT.exists():OUTPUT.unlink()
 manifest=b''.join((sha(b)+'  '+n+'\n').encode() for n,b in sorted(files.items()))
 files['SHA256SUMS.txt']=manifest
 with zipfile.ZipFile(OUTPUT,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for n,b in files.items():z.writestr(n,b)
 with zipfile.ZipFile(OUTPUT) as z:
  assert z.testzip() is None and all(sha(z.read(n))==h for h,n in (row.split('  ',1) for row in z.read('SHA256SUMS.txt').decode().splitlines()))
 report['zip_sha256']=sha(OUTPUT.read_bytes());report['zip_size_bytes']=OUTPUT.stat().st_size;report['zip_member_count']=len(files);report['zip_manifest_member_count']=len(files)-1
 (ROOT/'P1-WHOLE-131-CARD-REPORT.json').write_text(dump(report))
 (ROOT/'P1-131-CASE-DECISION-LEDGER.jsonl').write_bytes(jsonl(decisions))
 (ROOT/'P1-48-SCOPED-CLOSURES.json').write_text(dump(case_evidence))
 (ROOT/'P1-11-LINGUISTIC-EDITORIAL-REPAIRS.json').write_text(dump(editorial_actions))
 print(dump({k:report[k] for k in ('zip_sha256','new_primary_SHA256','P1_scoped_content_hold_closures','P1_remaining','all_HOLDs_after','actual_primary_changed_cards','real_semantic_editorial_card_actions','bilingual_example_pairs_after','new_P1_examples','existing_example_reroutes','zip_member_count')}))
if __name__=='__main__':main()
