#!/usr/bin/env python3
"""Aspekte B1+ global curated HOLD risk triage + strictly scoped editorial repairs.
Never auto-approve cards or relabel a generic missing attestation as an error.
Input is the exact SHA-pinned Gate01 learner archive; original CSV is not consulted.
"""
import collections, copy, hashlib, io, json, pathlib, re, zipfile, sys
from datetime import date

ROOT=pathlib.Path('/mnt/data/aspekte_b1plus_global_hold_resolution')
PARENT=ROOT/'Aspekte-B1plus-GLOBAL-BACKLOG-GATE01-1571-CARD-REPAIRS-NONIMPORT-20261110.zip'
OUT=ROOT/'Aspekte-B1plus-GLOBAL-HOLD-GATE02-359-CASE-PRIORITY-REPAIRS-NONIMPORT-20261110.zip'
PARENT_SHA='a2fa93f3389b43db12e562331cc3302e24e51f0cb028a494ce61b3e825e6a50b'
PRIMARY='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
SRC_MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
MAP_SHA='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
OLD_PRIMARY_SHA='829a1d9e16df96cf1467659835f7fcaa14aefa705f7d639910a150e9d37bfe22'
assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==PARENT_SHA

def sha(x):return hashlib.sha256(x).hexdigest()
def jd(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def pretty(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def jl(items):return ('\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in items)+'\n').encode()

def match(x,lesson,ordinal,stem):return x['lesson']==lesson and x['source_ordinal']==ordinal and (x['front'].get('base_headword_de','')==stem)

# Each changes lexical base lemma only; the reader-facing full declension/conjugation display stays unchanged.
HEADWORDS={
 ('L01',10,'der Stichpunkt, -e'):'der Stichpunkt',
 ('L01',60,'Der Vater schimpfte mit dem Kind.'):'schimpfen',
 ('L02',78,'eingehen auf + Akkusativ'):'eingehen',
 ('L03',253,'umgehen (trennbar: mit + Dat. / ein Gerücht geht um; untrennbar: + Akk.)'):'umgehen',
 ('L03',296,'beschäftigt mit + Dativ'):'beschäftigt',
 ('L05',650,'der/die Gestalter/in, -/-nen'):'der Gestalter / die Gestalterin',
 ('L05',651,'der/die Hirnforscher/in, -/-nen'):'der Hirnforscher / die Hirnforscherin',
 ('L05',653,'das Industriezeitalter, -'):'das Industriezeitalter',
 ('L05',656,'der/die Manager/in, -/-nen'):'der Manager / die Managerin',
 ('L05',657,'das Maschinenzeitalter, -'):'das Maschinenzeitalter',
 ('L06',672,'der/die Erntehelfer/in'):'der Erntehelfer / die Erntehelferin',
 ('L06',693,'der/die Unternehmensgründer/in'):'der Unternehmensgründer / die Unternehmensgründerin',
 ('L06',769,'der/die Türsteher/in'):'der Türsteher / die Türsteherin',
 ('L06',827,'der/die Ladenbesitzer/in'):'der Ladenbesitzer / die Ladenbesitzerin',
 ('L06',836,'der/die Schneider/in'):'der Schneider / die Schneiderin',
}
HEADWORD_EVIDENCE={
 'L01-10':'https://www.duden.de/deklination/substantive/Stichpunkt',
 'L03-253':'https://www.duden.de/rechtschreibung/umgehen_umgangen',
}
# Distinct fully reviewed lexical-content HOLDs. These are releases of *content-disposition HOLDs*,
# never formal release, import, or blanket independently-certified quality of entire corpus.
CLOSE={
 ('L01',10,'der Stichpunkt, -e'):{'evidence':['https://www.duden.de/deklination/substantive/Stichpunkt'],'reason':'Validated masculine form, full plural, contextual two German–Persian examples; abbreviated canonical lemma repaired.'},
 ('L03',253,'umgehen (trennbar: mit + Dat. / ein Gerücht geht um; untrennbar: + Akk.)'):{'evidence':['https://www.duden.de/rechtschreibung/umgehen_umgegangen','https://www.duden.de/rechtschreibung/umgehen_umgangen'],'reason':'Both separable/inseparable paradigms, three sense nodes, all six routed bilingual examples and collocations checked against valency.'},
 ('L08',1027,'umschreiben'):{'evidence':['https://www.duden.de/rechtschreibung/umschreiben_umgeschrieben','https://www.duden.de/rechtschreibung/umschreiben_umschrieben'],'reason':'Both conjugation paradigms and six sense-routed bilingual examples checked: rewrite versus paraphrase.'},
 ('L08',1142,'die Milliarde'):{'evidence':['https://www.duden.de/rechtschreibung/Milliarde'],'reason':'Validated 10^9, plural Milliarden, two numerically correct bilingual examples, distinct from Billion.'},
 ('L08',1142,'die Billion'):{'evidence':['https://shop.duden.de/media/24/62/c6/1687426846/Leseprobe_9783411721757_Wissen_%E2%80%93_%C3%9Cben_%E2%80%93_Testen_Mathematik_5_Klasse.pdf','https://www.duden.de/deklination/substantive/Billion'],'reason':'Validated 10^12 and plural Billionen; explicitly disambiguated from Milliarde and English billion; both examples retained.'},
 ('L10',1487,'die Überschwemmung'):{'evidence':['https://www.duden.de/rechtschreibung/Ueberschwemmung'],'reason':'Flooded-area sense, gender/plural, dedicated example and natural collocation verified; distinct identity preserved from Hochwasser.'},
 ('L10',1494,'der Wassermangel'):{'evidence':['https://www.duden.de/rechtschreibung/Wassermangel'],'reason':'Meaning, genitive, distinct canonical lemma, source-specific German/Persian example and collocation checked.'},
 ('L10',1494,'die Wasserknappheit'):{'evidence':['https://www.duden.de/rechtschreibung/Knappheit','https://zbw.eu/beta/skosmos/stw/de/page/stw/en/page/stw/de/page/stw/de/page/stw/de/page/stw/de/page/stw/de/page/stw/de/page/stw/de/page/?uri=http%3A%2F%2Fzbw.eu%2Fstw%2Fdescriptor%2F18377-5'],'reason':'Water scarcity lemma preserved separately from Wassermangel, own bilingual example and usage collocation reviewed.'}
}

with zipfile.ZipFile(PARENT) as z:
 original_members={name:z.read(name) for name in z.namelist() if name!='SHA256SUMS.txt'}
 assert z.testzip() is None
 assert sha(original_members[PRIMARY])==OLD_PRIMARY_SHA
 assert sha(original_members[SRC_MAP])==MAP_SHA
 old=[json.loads(s) for s in original_members[PRIMARY].splitlines() if s]
 assert len(old)==1571
 cards=copy.deepcopy(old)
 hold_before=[x for x in cards if x.get('curated_HOLD_content_disposition_exists') is True]
 assert len(hold_before)==359
 fixes=[];resolved=[]
 orig_by_id={x['preview_card_id']:x for x in old}
 for c in cards:
  before=copy.deepcopy(c)
  key=(c['lesson'],c['source_ordinal'],c['front'].get('base_headword_de',''))
  actions=[]
  if key in HEADWORDS:
   c['front']['base_headword_de']=HEADWORDS[key];actions.append('NORMALIZED_CANONICAL_LEMMA_NO_ID_CHANGE')
  if key==('L08',1142,'die Billion'):
   c['back']['meanings_fa_provisional']='بیلیون در آلمانی؛ هزار میلیارد (۱۰^۱۲)، نه میلیارد (۱۰^۹)'
   actions.append('CLARIFIED_GERMAN_BILLION_10_TO_12_FALSE_FRIEND')
  if key==('L09',1162,'die Pension'):
   b=c['back'];n=b['semantic_network_sense_anchored_pending_qa'];assert len(n)==2
   s3=copy.deepcopy(n[1]);s3.update({'sense_id':n[1]['sense_id'].replace(':S2',':S3'),
    'sense_de':'Ruhestand im öffentlichen Dienst (ohne Plural)',
    'sense_fa':'بازنشستگی، به‌ویژه کارمندان دولت (در این معنی بدون جمع)',
    'usage_distinction_de':'Ruhestand (in Pension gehen) ist eine andere Bedeutung als Pension als monatliches Geld.',
    'Kombinationen_DE_FA':[{'de':'in Pension gehen','fa':'بازنشسته شدن (به‌ویژه کارمند دولت)','status':'PENDING_SCOPE_DE_FA_QA'}],
    'source':'GLOBAL_HOLD_GATE02_MEANING_3_FROM_DUDEN_SCOPED_EDITORIAL','status':'PENDING_SCOPE_DE_FA_QA'})
   assert s3['sense_id'] not in {v['sense_id'] for v in n}
   n.append(s3)
   assert 'بازنشستگی' in b['meanings_fa_provisional']
   b['additional_examples_de_fa_pending_qa'].append({'de':'Nach vierzig Dienstjahren ging sie in Pension.', 'fa':'پس از چهل سال خدمت، بازنشسته شد.', 'sense_id':s3['sense_id'], 'status':'PENDING_SCOPE_DE_FA_QA', 'provenance':'GLOBAL_HOLD_GATE02_AUTHORIAL_DE_FA_CASE_EXAMPLE'})
   c['front']['display_de_provisional']='die Pension · Pl. Pensionen (Unterkunft/Ruhegehalt); Ruhestand: ohne Plural (in Pension gehen)'
   actions.append('COMPLETED_MISSING_RETIREMENT_SENSE_AND_NONCOUNT_GRAMMAR')
  if key==('L10',1487,'das Hochwasser'):
   b=c['back'];n=b['semantic_network_sense_anchored_pending_qa'];assert len(n)==1
   s2=copy.deepcopy(n[0]);s2.update({'sense_id':n[0]['sense_id'].replace(':S1',':S2'),
    'sense_de':'höchster Wasserstand bei der Flut (Gezeiten)',
    'sense_fa':'مد دریا؛ بالاترین سطح آب هنگام مد',
    'Kombinationen_DE_FA':[{'de':'Hochwasser an der Nordseeküste','fa':'مد در ساحل دریای شمال','status':'PENDING_SCOPE_DE_FA_QA'}],
    'source':'GLOBAL_HOLD_GATE02_DUDEN_TIDAL_HIGH_WATER_MEANING_SCOPED','status':'PENDING_SCOPE_DE_FA_QA'})
   assert s2['sense_id'] not in {v['sense_id'] for v in n}
   n.append(s2)
   b['meanings_fa_provisional']='سیلاب؛ بالاآمدن شدید سطح آب رودخانه یا دریاچه؛ همچنین مدِ دریا (بسته به بافت)'
   b['additional_examples_de_fa_pending_qa'].append({'de':'An der Nordseeküste ist um 14 Uhr Hochwasser.', 'fa':'در ساحل دریای شمال، ساعت ۱۴ زمان مد دریاست.', 'sense_id':s2['sense_id'],'status':'PENDING_SCOPE_DE_FA_QA','provenance':'GLOBAL_HOLD_GATE02_AUTHORIAL_DE_FA_CASE_EXAMPLE'})
   actions.append('COMPLETED_MISSING_TIDAL_HIGH_WATER_SENSE')
  if key in CLOSE:
   assert c['curated_HOLD_content_disposition_exists'] is True
   # A case-level *lexical HOLD* can be dispositioned without changing global release flags.
   c['curated_HOLD_content_disposition_exists']=False
   c['global_HOLD_resolution']={'status':'CASE_SPECIFIC_CONTENT_HOLD_CLOSED_NOT_FORMAL_RELEASE',
      'date':'2026-11-10','scope':CLOSE[key]['reason'], 'sources':CLOSE[key]['evidence'],
      'all_existing_examples_de_fa_preserved':True,'release_status':'RELEASE_BLOCKED_NONIMPORT'}
   actions.append('CLOSED_SCOPED_LEXICAL_HOLD_NOT_FORMAL_CARD_RELEASE')
   resolved.append({'lesson':key[0],'source_ordinal':key[1],'headword_before':key[2],
      'card_id':c['preview_card_id'],'reason':CLOSE[key]['reason'],'sources':CLOSE[key]['evidence']})
  if actions:
   assert c['preview_card_id']==before['preview_card_id'] and c['source_id']==before['source_id']
   assert c.get('formal_release_approved') is False and c.get('import_ready') is False
   fixes.append({'lesson':c['lesson'],'source_ordinal':c['source_ordinal'],'card_id':c['preview_card_id'],
    'actions':actions,'exact_before':before,'exact_after':c,'before_sha256':sha(jd(before)),'after_sha256':sha(jd(c))})
 assert len(resolved)==8,(len(resolved),resolved)
 assert len(fixes)==len({x['card_id'] for x in fixes})
 edits_by_id={x['card_id']:x for x in fixes}

 # Read full 359 row universe from Gate01 and make a stable, explicit per-card risk disposition.
 riskrows=[];before_counts=collections.Counter();after_counts=collections.Counter();tiers=collections.Counter();decisions=collections.Counter()
 for i,prev in enumerate(hold_before):
  cur=next(x for x in cards if x['preview_card_id']==prev['preview_card_id'])
  flags=prev.get('audit_flags',[]);b=prev['back'];senses=b.get('semantic_network_sense_anchored_pending_qa',[])
  oldlemma=prev['front']['base_headword_de']
  signals=[]
  if any('OLD_OVERLAY_REJECTED_OR_REQUIRES_REWRITE' in q for q in flags):signals.append('REJECTED_OR_UNRESOLVED_PREVIOUS_EDITORIAL_OVERLAY')
  if any('PENDING' in q or 'CONTENT_UPDATED' in q for q in flags):signals.append('INHERITED_CONTENT_EDIT_WITH_PENDING_MEANING_QA')
  if prev.get('G1_split_source_sense_coverage_requires_G4'):signals.append('SHARED_SOURCE_LEMMAS_REQUIRE_DISTINCT_EXAMPLE_SCOPE')
  if len(senses)>=2:signals.append('MULTISENSE_RELATIONS_REQUIRE_CASE_LEVEL_DE_FA_VALIDATION')
  if len(senses)==0:signals.append('NO_STRUCTURED_WORDNET_NOT_AUTOMATICALLY_ERROR')
  if prev.get('G1_evidence_examples_not_yet_semantically_partitioned'):signals.append('LEGACY_UNPARTITIONED_SOURCE_EXAMPLE_FLAG')
  if any('OVERLAY_CONTENT_RULING_HAS_NO_MACHINE_APPLICABLE_DELTA' in q for q in flags):signals.append('LEGACY_OVERLAY_WITHOUT_MACHINE_APPLICABLE_DELTA')
  if prev['preview_card_id'] in edits_by_id:signals.append('THIS_GATE_ACTUALLY_CHANGED_PRIMARY_CARD')
  if cur['curated_HOLD_content_disposition_exists'] is False:decision='CLOSED_SCOPED_LEXICAL_DISPOSITION';tier='P1' if ('MULTISENSE_RELATIONS_REQUIRE_CASE_LEVEL_DE_FA_VALIDATION' in signals or 'SHARED_SOURCE_LEMMAS_REQUIRE_DISTINCT_EXAMPLE_SCOPE' in signals) else 'P2'
  elif ('REJECTED_OR_UNRESOLVED_PREVIOUS_EDITORIAL_OVERLAY' in signals
        or 'SHARED_SOURCE_LEMMAS_REQUIRE_DISTINCT_EXAMPLE_SCOPE' in signals
        or len(senses)>=3
        or cur['preview_card_id'] in edits_by_id):
   decision='KEEP_HOLD_CASE_SPECIFIC_SEMANTIC_OR_MORPHOLOGY_FOLLOWUP';tier='P1'
  elif not flags and len(senses)<2:decision='KEEP_HOLD_UNTIL_SCOPED_CASE_EVIDENCE_NOT_AN_ERROR_PROVEN';tier='P2'
  elif 'LEGACY_OVERLAY_WITHOUT_MACHINE_APPLICABLE_DELTA' in signals and len(flags)==1:
   decision='KEEP_HOLD_LEGACY_NO_DELTA_REEVALUATE_IF_RISK_APPEARS';tier='P3'
  else:decision='KEEP_HOLD_CONTEXTUAL_EDITORIAL_QA';tier='P2'
  tiers[tier]+=1;decisions[decision]+=1;before_counts[prev['lesson']]+=1
  if cur['curated_HOLD_content_disposition_exists']:after_counts[prev['lesson']]+=1
  ex=b.get('existing_examples_de_fa_pending_qa',[])+b.get('additional_examples_de_fa_pending_qa',[])
  riskrows.append({'card_id':prev['preview_card_id'],'lesson':prev['lesson'],'source_ordinal':prev['source_ordinal'],
    'headword_before':oldlemma,'headword_after':cur['front']['base_headword_de'],
    'hold_at_gate01':True,'hold_after_gate02':bool(cur['curated_HOLD_content_disposition_exists']),
    'priority':tier,'risk_signals':signals,'source_identification_type':prev.get('G1_source_identity_type'),
    'inherited_audit_flags':flags,'source_linked_originals':prev.get('linked_original_source_ordinals') or [prev['source_ordinal']],
    'meaning_fa':cur['back'].get('meanings_fa_provisional'),
    'sense_count_before':len(senses),'sense_count_after':len(cur['back'].get('semantic_network_sense_anchored_pending_qa',[])),
    'example_count_before':len(ex),'example_count_after':sum(len(cur['back'].get(k,[])) for k in ['existing_examples_de_fa_pending_qa','additional_examples_de_fa_pending_qa']),
    'specific_decision':decision,'actual_primary_changes':edits_by_id.get(cur['preview_card_id'],{}).get('actions',[]),
    'case_closure_source_evidence':cur.get('global_HOLD_resolution',{}).get('sources',[]),
    'remaining_action_if_open':('Verify all DE/FA examples and sense-collocations, reconcile rejected overlays and only then release *content HOLD*' if tier=='P1' else 'Require a grounded concrete issue or complete case evidence before removing inherited HOLD') if cur['curated_HOLD_content_disposition_exists'] else 'NONE_CLOSED_CONTENT_DISPOSITION',
    'unchanged_card_object_sha256_before':sha(jd(prev))})
 # Regression: preserve all preexisting other objects, original keys, source map, example pairs except two added.
 assert len(cards)==1571 and len({x['preview_card_id'] for x in cards})==1571
 assert {x['preview_card_id'] for x in cards}=={x['preview_card_id'] for x in old}
 assert len(fixes)>10
 assert sum(x.get('curated_HOLD_content_disposition_exists') is True for x in cards)==351
 assert len(riskrows)==359 and sum(x['hold_after_gate02'] for x in riskrows)==351
 assert all(x['formal_release_approved'] is False and x['import_ready'] is False for x in cards)
 assert all(x['source_id']==orig_by_id[x['preview_card_id']]['source_id'] for x in cards)
 assert all(x['lesson']==orig_by_id[x['preview_card_id']]['lesson'] for x in cards)
 assert sum(bool(x['preview_card_id'] in edits_by_id) for x in cards)==len(fixes)
 assert all(x==orig_by_id[x['preview_card_id']] for x in cards if x['preview_card_id'] not in edits_by_id)
 # Every pair of existing examples preserved without overwriting even on edited cards.
 for oldobj,newobj in zip(old,cards):
  for k in ('existing_examples_de_fa_pending_qa','additional_examples_de_fa_pending_qa'):
   prev=oldobj['back'].get(k,[]);new=newobj['back'].get(k,[])
   assert new[:len(prev)]==prev,(oldobj['preview_card_id'],k)
 assert all(x['source_ordinal'] == y['source_ordinal'] for x,y in zip(old,cards))
 total_pairs_before=sum(len(x['back'].get(k,[])) for x in old for k in ('existing_examples_de_fa_pending_qa','additional_examples_de_fa_pending_qa'))
 total_pairs_after=sum(len(x['back'].get(k,[])) for x in cards for k in ('existing_examples_de_fa_pending_qa','additional_examples_de_fa_pending_qa'))
 assert total_pairs_after-total_pairs_before==2
 report={'schema':'aspekte-b1plus-global-hold-gate02@1','date':'2026-11-10','status':'359_HOLD_PRIORITIZED_8_SCOPED_CLOSED_PRIMARY_REAL_EDITS_NONIMPORT',
  'baseline':{'parent_owner_sha256':PARENT_SHA,'primary_sha256':OLD_PRIMARY_SHA,'source_map_sha256':MAP_SHA,'total_learner_cards':1571,'source_map_rows':1548},
  'hold_universe_before':359,'risk_tiers_all_359':dict(tiers),'case_dispositions_all_359':dict(decisions),
  'HOLDs_closed_with_scoped_case_evidence':len(resolved),'HOLDs_remaining_after':351,'HOLD_before_by_lesson':dict(before_counts),'HOLD_after_by_lesson':dict(after_counts),
  'cards_with_real_primary_edits':len(fixes),'headwords_canonicalized':len(HEADWORDS),'two_actual_semantic_network_gaps_completed':['L09/1162 Pension: Ruhestand','L10/1487 Hochwasser: Gezeiten'],
  'one_numeric_false_friend_Persian_gloss_clarified':True,'new_example_pairs':2,
  'release_blocked_nonimport':True,'formal_publication_approvals':0,'real_app_import_tested':False,
  'qa_limits':'Risk tiers are heuristic metadata triage, not proof that unresolved content is wrong. Case closures are explicit scoped lexical dispositions, not app release or third party signoff. Newly added examples and sense relations remain PENDING; both those cards remain HOLD.',
  'case_level_HOLD_closures':resolved,'external_dictionary_evidence':['https://www.duden.de/rechtschreibung/Pension','https://www.duden.de/rechtschreibung/Hochwasser','https://www.duden.de/rechtschreibung/umgehen_umgegangen','https://www.duden.de/rechtschreibung/umschreiben_umgeschrieben','https://www.duden.de/rechtschreibung/umschreiben_umschrieben','https://www.duden.de/rechtschreibung/Milliarde','https://www.duden.de/deklination/substantive/Billion','https://www.duden.de/rechtschreibung/Ueberschwemmung','https://www.duden.de/rechtschreibung/Wassermangel'],
  'next':'Scope remaining 351 by proven P1 errors; do not reopen structurally closed Gate01 or reuse old textbook CSV; verify native importer and UI separately.'}
 report['example_pairs_before']=total_pairs_before;report['example_pairs_after']=total_pairs_after
 edits_report=[{'card_id':x['card_id'],'lesson':x['lesson'],'source_ordinal':x['source_ordinal'],'actions':x['actions'],'before_sha256':x['before_sha256'],'after_sha256':x['after_sha256']} for x in fixes]
 new_primary=jl(cards)
 report['new_primary_sha256']=sha(new_primary)
 report['source_map_sha256']=sha(original_members[SRC_MAP])
 report['source_map_rows']=len([x for x in original_members[SRC_MAP].splitlines() if x.strip()])-1
 assert report['source_map_rows']==1548
 additional={
  'Global-Backlog/GATE02-HOLDS/GATE02-359-CARD-RISK-DECISION-LEDGER.jsonl':jl(riskrows),
  'Global-Backlog/GATE02-HOLDS/GATE02-8-EVIDENCED-HOLD-CLOSURES.json':pretty(resolved),
  'Global-Backlog/GATE02-HOLDS/GATE02-ALL-CHANGED-PRIMARY-CARDS-EXACT-BEFORE-AFTER.json':pretty(fixes),
  'Global-Backlog/GATE02-HOLDS/GATE02-EDITORIAL-ACTIONS-SUMMARY.json':pretty(edits_report),
  'Global-Backlog/GATE02-HOLDS/GATE02-359-HOLD-PRIORITIZATION-AND-REPAIR-REPORT.json':pretty(report),
  'Global-Backlog/GATE02-HOLDS/GATE02-RELEASE-GATE-NONIMPORT.md':('# HOLD content disposition is not a formal Flashcards Pro import approval.\n\n339? See JSON report for exact pending count.\n\nAll 1571 IDs and 1548 source map rows retained. New Pension and Hochwasser senses stay PENDING. Use only current verified owner; no original CSV reset.\n').encode(),
 }
 additional['Global-Backlog/GATE02-HOLDS/GATE02-RELEASE-GATE-NONIMPORT.md']=('# HOLD Gate02 status\n\n- 359 inherited HOLDs individually prioritized.\n- 8 scoped lexical content HOLDs closed with case evidence; 351 remain.\n- {} actual primary card objects changed; 2 meaning-specific examples newly added, both pending QA.\n- 1571 ID cards; 1548 source map unchanged.\n- No native app importer tested. No card formally released.\n- This Gate is fail-closed: RELEASE_BLOCKED_NONIMPORT.\n'.format(len(fixes))).encode()
 original_members[PRIMARY]=new_primary
 original_members.update(additional)
 original_members['Global-Backlog/GATE02-HOLDS/build_hold_priority_gate02.py']=pathlib.Path(__file__).read_bytes()
 names=sorted(original_members)
 sums=b''.join((sha(original_members[n])+'  '+n+'\n').encode() for n in names)
 with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as o:
  for n in names:o.writestr(n,original_members[n])
  o.writestr('SHA256SUMS.txt',sums)
 with zipfile.ZipFile(OUT) as chk:
  assert chk.testzip() is None
  assert len(chk.namelist())==len(names)+1
  assert all(sha(chk.read(n))==sha(original_members[n]) for n in names)
  assert chk.read(SRC_MAP)==original_members[SRC_MAP]
 for filename,blob in [('GATE02-359-HOLD-RISK-DECISION-LEDGER.jsonl',jl(riskrows)),('GATE02-359-HOLD-REPAIR-REPORT.json',pretty(report)),('GATE02-8-HOLD-CLOSURES.json',pretty(resolved)),('GATE02-CHANGED-PRIMARY-CARDS-BEFORE-AFTER.json',pretty(fixes))]:
  (ROOT/filename).write_bytes(blob)
 print(json.dumps({'output':str(OUT),'zip_sha256':sha(OUT.read_bytes()),'zip_bytes':OUT.stat().st_size,'zip_members':len(names)+1,'verified_manifest_entries':len(names),'new_primary_sha256':sha(new_primary),'changed_cards':len(fixes),'HOLD_closures':len(resolved),'hold_remaining':351,'by_lesson_before':dict(before_counts),'by_lesson_after':dict(after_counts),'risk_tiers':dict(tiers),'decisions':dict(decisions),'examples_before':total_pairs_before,'examples_after':total_pairs_after},ensure_ascii=False,indent=2))
