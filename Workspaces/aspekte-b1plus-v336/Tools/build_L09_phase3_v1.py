#!/usr/bin/env python3
"""Reproducible whole-L09 Phase3 editorial quality/release gate, fail-closed NONIMPORT.

Input authority is EXACT saved L09 Phase2 curated owner, never source/publisher CSV.
A positive structural gate does not establish full bilingual semantic approval.
Output contains actual edited canonical PRIMARY JSONL, 185 card-specific records,
all before-after objects, exact source map, original archive evidence and SHA manifest.
Usage: python build_L09_phase3_v1.py INPUT.zip OUTPUT_DIR
"""
from __future__ import annotations
import collections, copy, hashlib, html, json, re, sys, zipfile
from pathlib import Path

PARENT_SHA='d0fa7a144065ef49536f359fe17d23a6c2edca95f0ad6d6ce3cea396b42618d6'
PARENT_PRIMARY_SHA='063cdebed6bcf10c2b50adba205b1907d8574c2d8dfbd1bc76edcf339593962b'
SOURCE_MAP_SHA='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
BUNDLE='Aspekte-B1plus-L09-PHASE3-185-CARD-QUALITY-GATE-RELEASE-BLOCKED-NONIMPORT-20261109.zip'
ROOT='Lessons/L09/'

EVIDENCE={
 1203:('https://www.duden.de/rechtschreibung/Flug','Flugdaten refers to multiple details of a flight, not the plural of the date of flight; semantic category distinction'),
 1214:('https://www.duden.de/rechtschreibung/eingehen','eingehen has multiple senses with different case/preposition patterns; bei + Dativ is one usage only'),
 1254:('https://www.duden.de/rechtschreibung/Reeder','shipowner or shipping entrepreneur; do not restrict to company ownership'),
 1257:('https://www.duden.de/rechtschreibung/vornehm','priority sense is normally superlative: vornehmste Aufgabe'),
 1310:('https://www.duden.de/rechtschreibung/Assessor','legal title after second legal state examination; higher civil-service candidate is older usage')
}

def sha(b):return hashlib.sha256(b).hexdigest()
def jb(x):return (json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode('utf-8')
def lines(x):return b''.join(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')+b'\n' for v in x)
def ex(c):
 b=c['back'];return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
def ns(c):return c['back'].get('semantic_network_sense_anchored_pending_qa') or []
def combos(c):return [v for n in ns(c) for v in (n.get('Kombinationen_DE_FA') or [])]
def normalize(s):return re.sub(r'\W+','',str(s).casefold())
def norm_head(c):return str(c['front']['base_headword_de'])
def check(condition,reason):
 if not condition:raise AssertionError(reason)

def scoped_edits(cards):
 by={(c['lesson'],c['source_ordinal']):c for c in cards}
 for n in EVIDENCE:check(('L09',n) in by,'missing evidence target '+str(n))
 # 1203: misleading headword inflection note confused flight details with date-of-flight.
 a=by['L09',1203];check(norm_head(a)=='die Flugdaten','1203 lemma changed');
 before='die Flugdaten (Plural; Singular das Flugdatum technisch möglich, nicht als Hauptkarte)'
 check(a['front']['display_de_provisional']==before,'1203 unexpected prior front')
 a['front']['display_de_provisional']='die Flugdaten (Plural: Angaben zu einem Flug; das Flugdatum = Datum des Fluges, anderes Wort)'
 # 1214: canonical lemma must be the separable infinitive; "bei + Dat" is sense-only valency.
 a=by['L09',1214];check(a['front']['base_headword_de']=='eingehen (bei + Dativ)','1214 unexpected prior base')
 a['front']['base_headword_de']='eingehen'
 check('bei + Dat.' in a['front']['display_de_provisional'],'1214 lost input valency')
 # 1254: Reeder is ship-owner/operator / shipping entrepreneur, not necessarily owner of shipping corporation.
 a=by['L09',1254];check(norm_head(a)=='der Reeder / die Reederin','1254 headword changed')
 check(a['back']['meanings_fa_provisional']=='مالک یا اداره‌کننده شرکت کشتیرانی','1254 unexpected meaning')
 a['back']['meanings_fa_provisional']='کشتی‌دار؛ مالک کشتی یا کارآفرین/بهره‌بردار اقتصادی در حوزهٔ کشتیرانی'
 # 1257: priority/importance sense is *normally superlative*.
 a=by['L09',1257];n=[n for n in ns(a) if 'besonders wichtig' in n.get('sense_de','')]
 check(len(n)==1,'1257 priority sense not unique')
 check(n[0]['Kombinationen_DE_FA']==[{'de':'eine vornehme Aufgabe','fa':'وظیفه‌ای برجسته یا مهم'}],'1257 unexpected collocation')
 n[0]['Kombinationen_DE_FA']=[{'de':'unsere vornehmste Aufgabe','fa':'مهم‌ترین وظیفهٔ ما'}]
 n[0]['usage_distinction_de']='Gehoben; in dieser Bedeutung meist im Superlativ (z. B. unsere vornehmste Aufgabe).'
 # 1310: disambiguate obsolete higher service-candidate sense and contemporary legal qualification.
 a=by['L09',1310];check(norm_head(a)=='der Assessor / die Assessorin','1310 unexpected lemma')
 n=ns(a);check(len(n)==1,'1310 changed sense count')
 check(n[0]['Kombinationen_DE_FA']==[{'de':'als Assessor im öffentlichen Dienst','fa':'به‌عنوان دارندهٔ عنوان اسسور در بخش دولتی'}],'1310 unexpected old combo')
 n[0]['Kombinationen_DE_FA']=[{'de':'juristischer Assessor nach der zweiten Staatsprüfung','fa':'دارندهٔ عنوان اسسور حقوقی پس از قبولی در دومین آزمون دولتی'}]
 n[0]['usage_distinction_de']='Im juristischen Bereich nach der zweiten Staatsprüfung; Bedeutung als Anwärter im höheren Beamtenlaufbahndienst ist historisch.'
 # Evidence metadata is scoped, not automatic approval, in saved data for exactly 5 altered objects.
 for i in EVIDENCE:
  c=by['L09',i];url,scope=EVIDENCE[i]
  c['L09_phase3_scoped_edit_evidence']={'reference_url':url,'scope':scope,
     'status':'EVIDENCE_LIMITED_TO_THIS_CORRECTION_NOT_FULL_CARD_APPROVAL'}
 return by

def stats(cards):
 L=[c for c in cards if c['lesson']=='L09']
 ids=[c['preview_card_id'] for c in cards]
 check(len(cards)==1571 and len(set(ids))==1571,'1571 identities lost/duplicated')
 check(len(L)==185,'L09 exact count mismatch')
 check(all(c.get('formal_release_approved') is False and c.get('import_ready') is False for c in cards),'prematurely released cards')
 orig=collections.defaultdict(list)
 for c in L:
  for o in c['linked_original_source_ordinals']:orig[o].append(norm_head(c))
 check(set(orig)==set(range(1157,1342)),'L09 source mapping incomplete')
 check(sorted(orig[1302])==['die Kochsendung','die Kochshow'],'1302 2-lemma split lost')
 check(orig[1240]==['zurückhaben'] and orig[1241]==['zurückhaben'],'1240/41 link broken')
 missingstatus=[]; missingroute=[]; bad=[];dup=[];no_example=[];formback=[]; finite=[];missingfa=[]
 allcombos=0;words_first={'der','die','das','ein','eine','einen','einem','einer','diese','dieser','dieses','jener','jene'}
 finite_words={'reicht','entscheidet','koordiniert','läuft','prüft','schreibt','bringt','bestimmt','öffnet','organisiert','führt','hat','ist','sind','steht','arbeitet','verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt','hält','macht','kann','wird','werden','nimmt','bietet','spricht'}
 for c in cards:
  b=c['back']; nets=ns(c)
  if b.get('Formen_section'):formback.append(c['preview_card_id'])
  if c['lesson']=='L09':
   ee=ex(c)
   if not ee:no_example.append(c['preview_card_id'])
   senses={n.get('sense_id') for n in nets}
   bucket=collections.defaultdict(list)
   for j,e in enumerate(ee):
    if not str(e.get('de','')).strip() or not str(e.get('fa','')).strip():missingfa.append([c['source_ordinal'],j]);continue
    if not e.get('status'):missingstatus.append([c['source_ordinal'],j])
    if nets and e.get('sense_id') not in senses:missingroute.append([c['source_ordinal'],j,e.get('sense_id')])
    bucket[normalize(e['de'])].append(j)
   dup.extend([{'source_ordinal':c['source_ordinal'],'indices':v} for k,v in bucket.items() if k and len(v)>1])
   for n in nets:
    for pair in n.get('Kombinationen_DE_FA') or []:
     if not isinstance(pair,dict) or not str(pair.get('de','')).strip() or not str(pair.get('fa','')).strip():bad.append([c['source_ordinal'],pair]);continue
     s=pair['de'].strip();w=re.findall(r'\w+',s)
     if s[-1:] in ('.','!','?'):bad.append([c['source_ordinal'],s,'sentence punctuation'])
     if len(w)>=4 and w[0].lower() in words_first and w[1][:1].isupper() and w[2].lower() in finite_words:finite.append([c['source_ordinal'],s])
  allcombos+=len(combos(c))
 Lcombo=sum(len(combos(c)) for c in L)
 res={'global_cards':len(cards),'L09_cards':len(L),'L09_ordinal_range':[min(orig),max(orig)],'L09_mapped_source_rows':len(orig),
    'L09_example_pairs':sum(len(ex(c)) for c in L),'L09_collocations':Lcombo,'global_collocations':allcombos,
    'L09_semantic_network_cards':sum(bool(ns(c)) for c in L),'L09_sense_blocks':sum(len(ns(c)) for c in L),
    'L09_curated_HOLDs':sum(bool(c.get('curated_HOLD_content_disposition_exists')) for c in L),
    'L09_missing_example_statuses':missingstatus,'L09_missing_examples':no_example,'L09_missing_example_FA_DE':missingfa,
    'L09_unrouted_semantic_examples':missingroute,'L09_duplicate_DE_example_groups':dup,
    'L09_collocation_structural_failures':bad,'L09_finite_clause_candidates':finite,'global_back_Formen_violations':formback,
    'L09_recorded_morphology_attestations':sum(bool(c.get('front',{}).get('morphology_independently_validated')) for c in L)}
 return res

def known_global_finite_cases(cards):
 # Corpus-wide known conservative v4 rules; intentionally don't claim semantic naturalness.
 det={'der','die','das','ein','eine','einen','einem','einer','diese','dieser','dieses','jener','jene'}
 fv={'reicht','entscheidet','koordiniert','läuft','prüft','schreibt','bringt','bestimmt','öffnet','organisiert','führt','hat','ist','sind','steht','arbeitet','verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt','hält','macht','kann','wird','werden','nimmt','bietet','spricht'}
 o=[]
 for c in cards:
  for k in combos(c):
   w=re.findall(r'\w+',k.get('de',''))
   if len(w)>=4 and w[0].lower() in det and w[1][:1].isupper() and w[2].lower() in fv:o.append({'lesson':c['lesson'],'source_ordinal':c['source_ordinal'],'de':k['de']})
 return o

def quality_record(c):
 ee=ex(c);nets=ns(c)
 return {'card_id':c['preview_card_id'],'lesson':'L09','source_ordinal':c['source_ordinal'],
 'linked_original_source_ordinals':c['linked_original_source_ordinals'],'headword':norm_head(c),
 'front_display_de':c['front'].get('display_de_provisional'),'meanings_fa':c['back'].get('meanings_fa_provisional'),
 'DE_FA_examples':[{'de':e.get('de'),'fa':e.get('fa'),'sense_id':e.get('sense_id'),'status':e.get('status'),'fa_alternatives':e.get('fa_alternatives',[])} for e in ee],
 'sense_scoped_combinations':[{'sense_id':n.get('sense_id'),'sense_de':n.get('sense_de'),'sense_fa':n.get('sense_fa'),
 'Kombinationen_DE_FA':n.get('Kombinationen_DE_FA',[]),'status':n.get('status')} for n in nets],
 'form_QA_recorded':bool(c.get('front',{}).get('morphology_independently_validated')),
 'curated_HOLD':bool(c.get('curated_HOLD_content_disposition_exists')),
 'L09_phase3_scoped_evidence':c.get('L09_phase3_scoped_edit_evidence'),
 'structural_QA':'PASS','full_bilingual_semantic_QA':'NOT_ATTESTED',
 'collocations_idiomatic_QA':'NOT_FORMALLY_ATTESTED','real_app_import_render':'NOT_TESTED',
 'release_gate':'BLOCKED_NONIMPORT','human_independent_reviewer_required':False}

def render_html(records):
 s=['<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Aspekte B1+ L09 Phase3 – QA ONLY, NONIMPORT</title><style>body{max-width:1100px;margin:25px auto;font:15px/1.45 system-ui}article{margin:10px 0;padding:15px;border:1px solid #ccc;border-radius:9px}h2{font-size:18px}small{color:#555}.pair{margin:7px 0;padding:6px;border-left:2px solid #aaa}.hold{color:#973b18}</style></head><body><h1>Lektion 09 — 185 Karten / Phase3 QA ONLY</h1><p>Offline-Vorschau. <strong>KEINE Import-/Releasefreigabe</strong>, keine vollständige sprachliche Zertifizierung. Semantische/idiomatische Prüfungen bleiben offen.</p>']
 for r in records:
  e=html.escape;s.append('<article><h2>'+e(str(r['source_ordinal'])+' — '+r['headword'])+'</h2>')
  s.append('<small>'+e(r['front_display_de'] or '')+'</small><p><strong>فارسی:</strong> '+e(str(r['meanings_fa'] or ''))+'</p>')
  if r['curated_HOLD']:s.append('<div class="hold"><b>HOLD retained</b></div>')
  for exx in r['DE_FA_examples']:s.append('<div class="pair">'+e(str(exx['de']))+' → '+e(str(exx['fa']))+' <small>'+e(str(exx.get('status')))+'</small></div>')
  for n in r['sense_scoped_combinations']:
   s.append('<p><strong>'+e(str(n['sense_de']))+'</strong> — '+e(str(n['sense_fa']))+'</p>')
   for p in n['Kombinationen_DE_FA']:s.append('<div class="pair">'+e(p['de'])+' → '+e(p['fa'])+'</div>')
  s.append('</article>')
 s.append('</body></html>');return '\n'.join(s).encode('utf-8')

def negative_checks(cards):
 # Test detection (not just assert current dataset passes). Nine synthetic mutations.
 base=copy.deepcopy(cards)
 chosen=next(c for c in base if c['lesson']=='L09' and ns(c) and ex(c) and combos(c))
 def must_reject(fn,why):
  tmp=copy.deepcopy(base); fn(tmp)
  try: st=stats(tmp)
  except AssertionError: return  # The validator rejected corrupt data directly.
  check(not clean(st),"synthetic corruption was not rejected: "+why)
 def break_id(x):x[0]['preview_card_id']=x[1]['preview_card_id']
 def drop_card(x):x.pop()
 def rel(x):x[0]['import_ready']=True
 def dis(x):next(c for c in x if c['preview_card_id']==chosen['preview_card_id'])['back']['existing_examples_de_fa_pending_qa'][0]['status']=''
 def emptyfa(x):next(c for c in x if c['preview_card_id']==chosen['preview_card_id'])['back']['existing_examples_de_fa_pending_qa'][0]['fa']=''
 def route(x):next(c for c in x if c['preview_card_id']==chosen['preview_card_id'])['back']['existing_examples_de_fa_pending_qa'][0]['sense_id']='INVALID'
 def duplicate(x):
  c=next(c for c in x if c['preview_card_id']==chosen['preview_card_id']);c['back']['existing_examples_de_fa_pending_qa'].append(copy.deepcopy(c['back']['existing_examples_de_fa_pending_qa'][0]))
 def fullsent(x):next(c for c in x if c['preview_card_id']==chosen['preview_card_id'])['back']['semantic_network_sense_anchored_pending_qa'][0]['Kombinationen_DE_FA'][0]['de']='Der Kunde bezahlt das Ticket.'
 def backformen(x):next(c for c in x if c['preview_card_id']==chosen['preview_card_id'])['back']['Formen_section']='duplicated front forms'
 out=[]
 for why,fn in [('duplicate_card_id',break_id),('missing_card',drop_card),('premature_import',rel),('missing_example_status',dis),('missing_Persian_translation',emptyfa),('orphan_sense_id',route),('same_card_duplicate_DE_example',duplicate),('finite_sentence_in_collocation',fullsent),('back_side_redundant_Formen',backformen)]:
  try:must_reject(fn,why);out.append({'mutation':why,'expected':'BLOCK','observed':'BLOCK','pass':True})
  except Exception as e:out.append({'mutation':why,'expected':'BLOCK','observed':'FAIL','pass':False,'reason':str(e)})
 check(all(x['pass'] for x in out),'failed negative validations')
 return out

def clean(s):
 return s['global_cards']==1571 and s['L09_cards']==185 and not any(s[k] for k in (
 'L09_missing_example_statuses','L09_missing_examples','L09_missing_example_FA_DE','L09_unrouted_semantic_examples',
 'L09_duplicate_DE_example_groups','L09_collocation_structural_failures','L09_finite_clause_candidates','global_back_Formen_violations'))

def main(parent,out):
 out.mkdir(parents=True,exist_ok=True)
 check(sha(parent.read_bytes())==PARENT_SHA,'PARENT_OWNER_SHA_MISMATCH')
 with zipfile.ZipFile(parent) as z:
  check(z.testzip() is None,'PARENT_ZIP_CRC_FAILURE')
  oldinfo=[x for x in z.infolist() if x.filename!='SHA256SUMS.txt']
  data={inf.filename:z.read(inf.filename) for inf in oldinfo}
  manifest={name:d for d,name in (l.split('  ',1) for l in z.read('SHA256SUMS.txt').decode().splitlines() if l)}
  check(set(manifest)==set(data) and all(sha(data[n])==d for n,d in manifest.items()),'PARENT_MANIFEST_INVALID')
 check(sha(data[MAIN])==PARENT_PRIMARY_SHA,'PARENT_PRIMARY_HASH_FAILED')
 check(sha(data[MAP])==SOURCE_MAP_SHA,'PARENT_SOURCE_MAP_CHANGED')
 cards=[json.loads(s) for s in data[MAIN].splitlines()];before=copy.deepcopy(cards)
 bstat=stats(before);check(clean(bstat),'PARENT_STRUCTURAL_ERRORS')
 scoped_edits(cards);astat=stats(cards);check(clean(astat),'PHASE3_STRUCTURAL_ERRORS')
 check(astat['L09_curated_HOLDs']==43,'HOLD_COUNT_CHANGED')
 check(astat['L09_example_pairs']==423 and astat['L09_collocations']==237,'EXAMPLE_OR_COLLOCATION_COUNT_CHANGED')
 check(astat['global_collocations']==1086,'GLOBAL_COLLOCATION_COUNT_CHANGED')
 check(not astat['L09_missing_example_statuses'],'L09_MISSING_STATUS')
 outside=[(x['preview_card_id'],x) for x in before if x['lesson']!='L09'];outsidea=[(x['preview_card_id'],x) for x in cards if x['lesson']!='L09'];check(outside==outsidea and len(outside)==1386,'NON_L09_OBJECT_MODIFIED')
 check([x['preview_card_id'] for x in before]==[x['preview_card_id'] for x in cards],'IDS_CHANGED')
 bmap={c['preview_card_id']:c for c in before}
 edits=[{'card_id':c['preview_card_id'],'source_ordinal':c['source_ordinal'],'headword_before':norm_head(bmap[c['preview_card_id']]),'headword_after':norm_head(c),'before':bmap[c['preview_card_id']],'after':c,'scoped_external_evidence':c.get('L09_phase3_scoped_edit_evidence')} for c in cards if c!=bmap[c['preview_card_id']]]
 check(len(edits)==5 and set(x['source_ordinal'] for x in edits)==set(EVIDENCE),'UNEXPECTED_CONTENT_DIFF')
 row=[quality_record(c) for c in cards if c['lesson']=='L09'];check(len(row)==185,'185_LEDGER_INVALID')
 mut=negative_checks(cards)
 oldissues=known_global_finite_cases(before);issues=known_global_finite_cases(cards)
 check(oldissues==issues and len(issues)==2 and all(x['lesson']!='L09' for x in issues),'GLOBAL_FINITE_REGRESSION_OR_BAD_BASELINE')
 report={'schema':'aspekte-b1plus-l09-phase3-185-card-case-qa-release-gate@1','date':'2026-11-09','lesson':'L09',
 'phase':3,'phases_total':3,'status':'PHASE3_COMPLETE_RELEASE_BLOCKED_NONIMPORT',
 'parent_SHA256':PARENT_SHA,'parent_primary_SHA256':PARENT_PRIMARY_SHA,'source_map_SHA256':SOURCE_MAP_SHA,
 'actual_saved_primary_changed_cards':len(edits),'actual_saved_edited_source_ordinals':sorted(EVIDENCE),
 'all_185_case_QA_ledger_rows':len(row),'all_1386_other_lesson_objects_unchanged':True,'all_1548_source_map_rows_unchanged':True,
 'before_statistics':bstat,'after_statistics':astat,'known_global_finite_clause_candidates':issues,
 'scoped_Duden_pointers':[{ 'source_ordinal':i,'url':url,'scope':scope} for i,(url,scope) in EVIDENCE.items()],
 'negative_mutation_tests':mut,'negative_pass_count':len(mut),
 'all_case_structure_pass':True,'all_semantic_sense_fa_and_collocation_signoffs':False,
 'L09_unresolved_HOLDs':43,'real_German_Flashcards_Pro_import_tested':False,
 'formal_approved_cards':0,'release_status':'BLOCKED_NONIMPORT',
 'note':'Pass means deterministic structural integrity plus five scoped editorial corrections; NOT full expert DE/FA meaning, collocation or app signoff.',
 'next':'L10_PHASE1_FULL_LESSON_NONIMPORT__GLOBAL_ISSUES_AND_43_L09_HOLDS_REMAIN'}
 data[MAIN]=lines(cards)
 data[ROOT+'L09-PHASE3-185-CARD-CASE-QA-RELEASE-BLOCKERS.jsonl']=lines(row)
 data[ROOT+'L09-PHASE3-5-CARD-EXACT-BEFORE-AFTER.json']=jb(edits)
 data[ROOT+'L09-PHASE3-QUALITY-AND-RELEASE-REPORT.json']=jb(report)
 data[ROOT+'L09-PHASE3-OFFLINE-QA-ONLY.html']=render_html(row)
 data[ROOT+'L09-PHASE3-9-NEGATIVE-TESTS.json']=jb(mut)
 note='''# Aspekte B1+ Lektion 09 — Phase 3 (nonimport)\n\n185 case-level structural QA records. 5 saved actual scoped edits. All 43 HOLDs retained.\nExternal scoped Duden sources for individual changes, NOT full bilingual semantic signoff.\nNo German Flashcards Pro import test was performed, hence RELEASE BLOCKED.\nThe 185-card HTML is an offline *QA-only* view, not the real application.\nOriginal 1571 card identity and 1548 source-row map preserved.\nNext stage: Lektion 10 Phase 1; keep global release blockers open.\n'''
 data[ROOT+'L09-PHASE3-README-NONIMPORT.md']=note.encode()
 finalzip=out/BUNDLE
 with zipfile.ZipFile(finalzip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8,allowZip64=True) as z:
  for info in oldinfo:
   if info.filename in data:z.writestr(info,data[info.filename])
  remaining=set(data)-{i.filename for i in oldinfo}
  for name in sorted(remaining):
   info=zipfile.ZipInfo(name,date_time=(2026,11,9,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644 <<16
   z.writestr(info,data[name])
  hashes=''.join(f'{sha(data[n])}  {n}\n' for n in sorted(data)).encode()
  info=zipfile.ZipInfo('SHA256SUMS.txt',date_time=(2026,11,9,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(info,hashes)
 with zipfile.ZipFile(finalzip) as z:
  check(z.testzip() is None,'FINAL_BAD_ZIP_CRC')
  hashes={n:d for d,n in (line.split('  ',1) for line in z.read('SHA256SUMS.txt').decode().splitlines() if line)}
  check(set(hashes)==set(z.namelist())-{'SHA256SUMS.txt'},'FINAL_MANIFEST_SET_MISMATCH')
  check(all(sha(z.read(n))==v for n,v in hashes.items()),'FINAL_MANIFEST_HASH_MISMATCH')
  check(sha(z.read(MAIN))==sha(data[MAIN]),'PRIMARY_NOT_SAVED')
  check(z.read(MAP)==data[MAP],'SOURCE_MAP_NOT_SAVED')
 report['new_curated_owner_SHA256']=sha(finalzip.read_bytes())
 report['new_primary_SHA256']=sha(data[MAIN]);report['archive_bytes']=finalzip.stat().st_size
 report['archive_members']=len(data)+1;report['archive_SHA256_entries_verified']=len(hashes)
 report['output_zip']=str(finalzip)
 (out/'L09-PHASE3-FINAL-REPORT.json').write_bytes(jb(report))
 (out/'L09-PHASE3-5-CARD-EXACT-BEFORE-AFTER.json').write_bytes(jb(edits))
 (out/'L09-PHASE3-185-CARD-CASE-QA-RELEASE-BLOCKERS.jsonl').write_bytes(lines(row))
 (out/'L09-PHASE3-9-NEGATIVE-TESTS.json').write_bytes(jb(mut))
 print(json.dumps({'zip':str(finalzip),'sha256':report['new_curated_owner_SHA256'],'primary_sha256':report['new_primary_SHA256'],'size_bytes':report['archive_bytes'],'members':report['archive_members'],'manifest_members':len(hashes),'changed_cards':len(edits),'case_qa':len(row),'L09_hold':astat['L09_curated_HOLDs'],'L09_examples':astat['L09_example_pairs'],'L09_combinations':astat['L09_collocations'],'negative_passed':len(mut),'global_old_issues':issues,'release':report['release_status']},ensure_ascii=False,indent=2))

if __name__=='__main__':
 check(len(sys.argv)>=3,'usage: builder parent.zip outputdir')
 main(Path(sys.argv[1]),Path(sys.argv[2]))