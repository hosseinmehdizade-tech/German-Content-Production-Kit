#!/usr/bin/env python3
"""Aspekte B1+ L06 Phase3 fail-closed lesson QA, real primary-card edits and source preservation.

Single whole-lesson phase. Reuses the SHA-verified Phase2 learner-data owner, never the obsolete book CSV.
Every claimed change must survive ZIP save/re-open at its original primary JSONL member.
Language review is explicitly scoped; no fake complete 177-card semantic signoff or app-runtime receipt.
"""
import collections,copy,hashlib,html,io,json,re,sys,zipfile
from pathlib import Path

ROOT=Path('/mnt/data/aspekte_b1plus_l06')
PARENT=ROOT/'Aspekte-B1plus-L06-PHASE2-177-CARDS-CURATED-CORRECTED-NONIMPORT-20261109.zip'
OUT=ROOT/'Aspekte-B1plus-L06-PHASE3-177-CARD-STRICT-GATE-AND-LANGUAGE-FIXES-NONIMPORT-20261109.zip'
DIR=ROOT/'phase3'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
EXPECTED_PARENT_SHA='bba74617aae6abfb849c28a03b2f279ed75171075c9717c2e6f3ad4c2d9f7d8f'
DUDEN_FORMAL='https://www.duden.de/rechtschreibung/formal'
DUDEN_FORMELL='https://www.duden.de/rechtschreibung/formell'
DUDEN_PER='https://www.duden.de/rechtschreibung/per'
DUDEN_SELBST='https://www.duden.de/rechtschreibung/selbst_gemacht'
DUDEN_ERWUENSCHT='https://www.duden.de/deklination/adjektive/erwuenscht'
CLAUSE_VERBS={'reicht','entscheidet','koordiniert','läuft','prüft','schreibt','bringt','bestimmt','öffnet','organisiert','führt','hat','ist','sind','steht','arbeitet','verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt','hält','macht','kann','wird','werden','nimmt','bietet','spricht'}
ART={'der','die','das','ein','eine','einen','einem','einer','dieser','diese','dieses'}

def digest(b):return hashlib.sha256(b).hexdigest()
def dump(x):return json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
def serial(cards):return ''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in cards).encode('utf-8')
def get_records(z):return [json.loads(x) for x in z.read(MAIN).splitlines()]
def examples(c):
 b=c['back'];return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
def net_by_ordinal(cards,ordinal):return next(c for c in cards if c['lesson']=='L06' and c['source_ordinal']==ordinal)
def replace_combo(card,old_de,new_de,new_fa):
 matched=[]
 for net in card['back'].get('semantic_network_sense_anchored_pending_qa',[]):
  for x in net.get('Kombinationen_DE_FA',[]):
   if x['de']==old_de:
    matched.append({'before':copy.deepcopy(x),'sense_id':net['sense_id']})
    x['de']=new_de;x['fa']=new_fa;x['L06_phase3_review']='FINITE_MAIN_CLAUSE_REPLACED_BY_COLLOCATION';
 assert len(matched)==1,(card['source_ordinal'],old_de,len(matched))
 return {'ordinal':card['source_ordinal'],'kind':'KOMBINATIONEN_FULL_FINITE_CLAUSE_TO_LEXICAL_COLLOCATION',
         'before':matched[0]['before'],'after':{'de':new_de,'fa':new_fa},'sense_id':matched[0]['sense_id']}
def finite_candidates(cs):
 out=[]
 for card in cs:
  for net in card['back'].get('semantic_network_sense_anchored_pending_qa',[]) or []:
   for x in net.get('Kombinationen_DE_FA',[]) or []:
    t=re.findall(r'\w+',x['de'],flags=re.UNICODE)
    if (len(t)>=4 and t[0].casefold() in ART and len(t)>2 and t[1][:1].isupper() and t[2].casefold() in CLAUSE_VERBS):
     out.append({'lesson':card['lesson'],'ordinal':card['source_ordinal'],'headword':card['front']['base_headword_de'],'de':x['de'],'reason':'DETERMINER_NOUN_FINITE_VERB_PATTERN','status':'NEEDS_EDITORIAL_SAME_SENSE_CHECK'})
 return out

def exact_duplicates(cs):
 groups=[]
 for c in cs:
  grp=collections.defaultdict(list)
  for e in examples(c):grp[re.sub(r'\W+','',e['de'].casefold())].append(e)
  for k,v in grp.items():
   if k and len(v)>1:groups.append({'lesson':c['lesson'],'ordinal':c['source_ordinal'],'headword':c['front']['base_headword_de'],'de':v[0]['de'],'count':len(v)})
 return groups

def check_source_integrity(before,after,z):
 assert len(before)==len(after)==1571
 assert len({x['preview_card_id'] for x in after})==1571
 assert [x['preview_card_id'] for x in before]==[x['preview_card_id'] for x in after]
 assert [x['linked_original_source_ordinals'] for x in before]==[x['linked_original_source_ordinals'] for x in after]
 assert all(a==b for a,b in zip(before,after) if a['lesson']!='L06')
 assert sum(c['lesson']=='L06' for c in after)==177
 assert z.read(MAP)
 return [a for a,b in zip(before,after) if a!=b]


def assemble():
 assert digest(PARENT.read_bytes())==EXPECTED_PARENT_SHA,'UNEXPECTED_PARENT_OWNER_HASH'
 with zipfile.ZipFile(PARENT) as z:
  assert z.testzip() is None,'BAD_PARENT_CRC'
  old=get_records(z)
  stored={n:z.read(n) for n in z.namelist() if n not in ('SHA256SUMS.txt',)}
  old_map=z.read(MAP)
  old_main=z.read(MAIN)
 new=copy.deepcopy(old); changes=[]; evid=[]
 for ordinal,od,nd,fa in [
  (737,'die Bewerberin reicht Unterlagen ein','eine Bewerberin zum Vorstellungsgespräch einladen','دعوت‌کردن یک متقاضی زن به مصاحبهٔ شغلی'),
  (751,'der Personalchef entscheidet über Einstellungen','mit dem Personalchef über Einstellungen sprechen','با مدیر منابع انسانی دربارهٔ استخدام‌ها صحبت کردن'),
  (846,'die Projektleiterin koordiniert das Team','mit der Projektleiterin den Zeitplan abstimmen','هماهنگ‌کردن برنامهٔ زمانی با مدیر پروژهٔ زن')]:
  c=net_by_ordinal(new,ordinal)
  changes.append(replace_combo(c,od,nd,fa))
  c.setdefault('L06_phase3_language_review',{})['full_sentence_collocation_fixed']=True
 c=net_by_ordinal(new,742);old_c=net_by_ordinal(old,742)
 b=c['back'];old_n=copy.deepcopy(b['semantic_network_sense_anchored_pending_qa']);old_ex=copy.deepcopy(examples(c));old_mean=b['meanings_fa_provisional']
 n1,n2=b['semantic_network_sense_anchored_pending_qa']
 sid_form=n1['sense_id'];sid_subst=n2['sense_id']
 n1['sense_de']='die äußere Form, den Aufbau oder formale Voraussetzungen betreffend'
 n1['sense_fa']='مربوط به شکل، ساختار یا الزامات شکلی'
 n1['Kombinationen_DE_FA']=[x for x in n2['Kombinationen_DE_FA']]
 n1['usage_distinction_de']='formal ≠ formell: formal bezieht sich auf Form und Struktur; formell auf offiziellen oder gesellschaftlich förmlichen Umgang.'
 n1['L06_phase3_review_evidence']=[DUDEN_FORMAL,DUDEN_FORMELL]
 n2['sense_de']='nur der äußeren Form nach vorhanden, ohne entsprechende inhaltliche Wirkung'
 n2['sense_fa']='صرفاً صوری، فقط روی کاغذ و نه در عمل'
 n2['Kombinationen_DE_FA']=[{'de':'eine rein formale Zustimmung','fa':'موافقتی صرفاً صوری','source':'L06_PHASE3_EVIDENCED_FORMAL_FORMELL_DISTINCTION','status':'PENDING_CONTEXT_QA_NO_RELEASE'}]
 n2['usage_distinction_de']='Die formale Zustimmung ist gegeben; ein inhaltlicher Konsens muss damit nicht vorliegen.'
 n2['L06_phase3_review_evidence']=[DUDEN_FORMAL]
 b['meanings_fa_provisional']='۱) شکلی، مربوط به ظاهر و ساختار؛ ۲) صوری، فقط از نظر ظاهر و نه در عمل'
 ex=examples(c)
 assert len(ex)==2
 assert ex[0]['de']=='Seine Bewerbung war formal korrekt.'
 ex[0]['sense_id']=sid_form
 assert ex[1]['de']=='Die Einladung klang ziemlich formal.'
 ex[1]['de']='Die Zustimmung war nur formal; inhaltlich gab es keine Einigung.'
 ex[1]['fa']='موافقت فقط صوری بود؛ از نظر محتوایی توافقی حاصل نشد.'
 ex[1]['sense_id']=sid_subst
 ex[1]['L06_phase3_review_evidence']=[DUDEN_FORMAL,DUDEN_FORMELL]
 c.setdefault('L06_phase3_language_review',{})['formal_vs_formell_scope']='TWO_SENSES_CORRECTED_WITH_DUDEN_LINKS_NOT_FULL_RELEASE'
 changes.append({'ordinal':742,'kind':'FORMAL_FORMELL_FALSE_FRIEND_FIXED','before':{'meanings_fa_provisional':old_mean,'examples':old_ex,'networks':old_n},'after':{'meanings_fa_provisional':b['meanings_fa_provisional'],'examples':copy.deepcopy(ex),'networks':copy.deepcopy(b['semantic_network_sense_anchored_pending_qa'])},'source_urls':[DUDEN_FORMAL,DUDEN_FORMELL]})
 # One morphology *scope* can be truthfully attested: uninflected preposition per accepts Akk./Dat. (Duden)
 c=net_by_ordinal(new,750);assert c['front']['base_headword_de']=='per [+Dat. od. +Akk.]'
 prev=copy.deepcopy(c['front']);c['front']['display_de_provisional']='per + Akkusativ oder Dativ (Präposition; nicht flektierbar)'
 c['front']['morphology_independently_validated']=True
 c['front']['L06_phase3_form_attestation']={'scope':'PREPOSITION_CASE_GOVERNMENT_AND_NONINFLECTABILITY_ONLY','source':DUDEN_PER,'attested':'Akkusativ oder Dativ; unveränderliche Präposition','full_card_release_approved':False}
 c.setdefault('L06_phase3_language_review',{})['case_form_evidence']='SCOPED_VERIFIED_WITH_DUDEN_NOT_A_COMPLETE_LANGUAGE_RELEASE'
 changes.append({'ordinal':750,'kind':'DUDEN_SCOPED_CASE_GOVERNMENT_ATTESTATION','before':prev,'after':copy.deepcopy(c['front']),'source_url':DUDEN_PER})
 assert len(changes)==5
 assert sum(a!=b for a,b in zip(old,new))==5,'ACTUAL_PERSISTED_EDITS_NOT_EQUAL_5'
 check_source_integrity(old,new,zipfile.ZipFile(PARENT))
 l=[c for c in new if c['lesson']=='L06']
 assert sum(len(examples(c)) for c in l)==378
 assert all(not c.get('formal_release_approved') and not c.get('import_ready') for c in new)
 assert all(c['back']['Formen_section'] is None for c in new)
 new_main=serial(new)
 assert digest(new_main)!=digest(old_main)
 flagged=finite_candidates(new)
 local_bad=[f for f in flagged if f['lesson']=='L06']
 assert not local_bad,local_bad
 corpus_issues=flagged
 duplicate_groups=exact_duplicates(new)
 assert len(duplicate_groups)==3,duplicate_groups
 # Whole-lesson decision ledger: conservative unverified items stay open, not just passing static checks
 ledger=[];blockers=collections.Counter();forms=0;hold=0;routed=0;network_cards=0;total_combinationen=0
 for cr in new:
  for n in cr['back'].get('semantic_network_sense_anchored_pending_qa',[]) or []:total_combinationen+=len(n.get('Kombinationen_DE_FA',[]) or [])
 for cr in l:
  bl=[];b=cr['back'];ex=examples(cr);n=b.get('semantic_network_sense_anchored_pending_qa') or [];ids={x['sense_id'] for x in n}
  if not cr['front'].get('morphology_independently_validated'):bl.append('G2_FORM_SCOPED_ATTESTATION_NOT_PRESENT')
  else:forms+=1
  if cr.get('curated_HOLD_content_disposition_exists'):bl.append('INHERITED_CONTENT_HOLD_NEEDS_CASE_LEVEL_RESOLUTION');hold+=1
  if any(e.get('status')!='FULL_INDEPENDENT_G4_DE_FA_APPROVED' for e in ex):bl.append('DE_FA_EXAMPLES_FULL_G4_NOT_APPROVED')
  if n:
   network_cards+=1
   for e in ex:
    if e.get('sense_id') in ids:routed+=1
   if any(e.get('sense_id') not in ids for e in ex):bl.append('EXAMPLE_SENSE_ID_INCOMPLETE')
   if any(nn.get('status') not in ('FULL_INDEPENDENT_G4_SENSE_APPROVED',) for nn in n):bl.append('MEANING_RELATIONS_FULL_G4_NOT_APPROVED')
  if not ex:bl.append('NO_DE_FA_EXAMPLE')
  if not cr.get('formal_release_approved') or not cr.get('import_ready'):bl.append('CARD_NOT_FORMALLY_APPROVED')
  bl.append('REAL_APP_IMPORT_RENDER_RECEIPT_ABSENT')
  for x in set(bl):blockers[x]+=1
  ledger.append({'source_ordinal':cr['source_ordinal'],'card_id':cr['preview_card_id'],'headword':cr['front']['base_headword_de'],'examples':len(ex),'sense_blocks':len(n),'formal_approval':False,'app_import_verified':False,'decision':'RELEASE_BLOCKED_NONIMPORT','blockers':sorted(set(bl)),'targeted_change_in_phase3':cr['source_ordinal'] in {737,742,750,751,846}})
 assert len(ledger)==177
 assert forms==109 and hold==33 and network_cards==37
 assert total_combinationen==722,total_combinationen
 assert sum(1 for cr in l if cr['source_ordinal'] in [737,742,750,751,846])==5
 # Audit-only HTML, no claim to real app runtime
 body=[]
 for cr in l:
  b=cr['back'];ex=examples(cr);nets=b.get('semantic_network_sense_anchored_pending_qa') or []
  body.append(f'<section class="card"><h2 lang="de">{html.escape(cr["front"]["base_headword_de"])}</h2><p class="front">{html.escape(cr["front"]["display_de_provisional"])}</p><p lang="fa" dir="rtl">{html.escape(b["meanings_fa_provisional"])}</p>')
  if nets:
   for n in nets:
    body.append('<h3>'+html.escape(n['sense_de'])+'</h3><p dir="rtl" lang="fa">'+html.escape(n['sense_fa'])+'</p>')
    for e in ex:
     if e.get('sense_id')==n['sense_id']:
      body.append('<p class="pair"><span lang="de">'+html.escape(e['de'])+'</span><span dir="rtl" lang="fa">'+html.escape(e['fa'])+'</span></p>')
    for k in n.get('Kombinationen_DE_FA',[]) or []:
     body.append('<p class="combo">'+html.escape(k['de'])+' <span dir="rtl" lang="fa">'+html.escape(k['fa'])+'</span></p>')
   for e in ex:
    if e.get('sense_id') not in {n['sense_id'] for n in nets}:
     body.append('<p class="unresolved"><span lang="de">'+html.escape(e['de'])+'</span> <span lang="fa" dir="rtl">'+html.escape(e['fa'])+'</span></p>')
  else:
   for e in ex:body.append('<p class="pair"><span lang="de">'+html.escape(e['de'])+'</span><span dir="rtl" lang="fa">'+html.escape(e['fa'])+'</span></p>')
  body.append('</section>')
 page='''<!doctype html><html lang="de"><head><meta charset="UTF-8"><title>B1+ L06 Phase3 QA only</title><style>body{font:14px system-ui;background:#f2f4f8;max-width:1180px;margin:auto;padding:25px}.card{background:white;border-radius:12px;padding:20px;margin:15px 0;border:1px solid #ddd}.pair{display:grid;grid-template-columns:1fr 1fr;gap:15px}.combo{background:#eee;padding:5px}.front{color:#555}[lang=fa]{text-align:right}.unresolved{border-left:4px solid orange;padding:8px}</style></head><body><h1>Aspekte B1+ L06 — 177 Karten QA ONLY · NONIMPORT</h1><p>NOT the real German-Flashcards-Pro renderer; unapproved cards remain blocked.</p>'''+''.join(body)+'</body></html>'
 # Count projection independently through simple tags by insertion and all 378 original examples
 assert page.count('class="card"')==177
 assert page.count('class="pair"')+page.count('class="unresolved"')==378
 # offline importer-format simulation, 177 line TSV (no formal import)
 import csv
 tab=io.StringIO();w=csv.writer(tab,delimiter='\t',lineterminator='\n')
 for cr in l:w.writerow([cr['preview_card_id'],cr['front']['display_de_provisional'],cr['back']['meanings_fa_provisional'],str(len(examples(cr)))])
 tsv=tab.getvalue();rows=list(csv.reader(io.StringIO(tsv),delimiter='\t'))
 assert len(rows)==177 and all(len(v)==4 for v in rows)
 report={'schema':'aspekte-b1plus-L06-phase3-qa@1','date':'2026-11-09','phase':3,'status':'WHOLE_LESSON_GATE_EVALUATED_RELEASE_BLOCKED_NONIMPORT',
   'lesson':'L06','source_owner_sha256':EXPECTED_PARENT_SHA,'source_primary_member_sha256':digest(old_main),
   'new_primary_member_sha256':digest(new_main),'actual_targeted_lesson_card_objects_modified':5,
   'modified_ordinals':[737,742,750,751,846],
   'language_fixes':{'finite_full_clauses_in_combinations_corrected':3,'formal_vs_formell_false_sense_corrected':1,'scoped_preposition_case_attested_with_Duden':1,'new_example_pairs':0,'L06_examples_preserved':378},
   'lesson_cards':177,'all_corpus_cards':1571,'source_rows':1548,'source_map_exact_bytes_preserved':True,'all_non_L06_card_objects_preserved':True,
   'forms_scoped_attested_L06':forms,'forms_unattested_L06':177-forms,'inherited_content_HOLDs_L06':hold,'network_cards_L06':network_cards,'examples_routed_within_L06_networks':routed,
   'global_Kombinationen':total_combinationen,'finite_clause_review_candidates_L06':len(local_bad),'finite_clause_review_candidates_other_lessons':corpus_issues,
   'global_exact_duplicate_example_groups':len(duplicate_groups),'global_duplicate_groups_detail':duplicate_groups,
   'final_gate_blocked_cards':177,'blocker_counts':dict(blockers),
   'real_app_import_tested':False,'formal_cards_approved':0,'import_ready':False,
   'scope':'The 5 case-level edits are evidence-checked; the 177-card decision ledger is primarily a fail-closed audit, NOT a 177-card human/linguistic certification.',
   'source_urls':[DUDEN_FORMAL,DUDEN_FORMELL,DUDEN_PER,DUDEN_SELBST,DUDEN_ERWUENSCHT],
   'offline_tsv_roundtrip':'PASS_177_RECORDS_QA_ONLY', 'HTML_QA_projection':'PASS_177_CARDS_378_EXAMPLES_QA_ONLY'}
 sidecars={
  'Lessons/L06/L06-PHASE3-177-CARD-RELEASE-GATE-REPORT.json':dump(report).encode(),
  'Lessons/L06/L06-PHASE3-177-CARD-BLOCKER-LEDGER.jsonl':(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in ledger)).encode(),
  'Lessons/L06/L06-PHASE3-5-CARD-SCOPED-CORRECTIONS.json':dump(changes).encode(),
  'Lessons/L06/L06-PHASE3-GLOBAL-FINITE-CLAUSE-CANDIDATES.json':dump(corpus_issues).encode(),
  'Lessons/L06/L06-PHASE3-177-CARD-FRONT-BACK-QA-ONLY.html':page.encode(),
  'Lessons/L06/L06-PHASE3-177-CARD-OFFLINE-TSV-QA-ONLY.tsv':tsv.encode(),
  'Tools/build_L06_phase3_v1.py':Path(__file__).read_bytes()
 }
 stored[MAIN]=new_main
 stored.update(sidecars)
 stored.pop('SHA256SUMS.txt',None)
 manifest=''.join(digest(value)+'  '+name+'\n' for name,value in sorted(stored.items())).encode()
 with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for name,value in stored.items():z.writestr(name,value)
  z.writestr('SHA256SUMS.txt',manifest)
 with zipfile.ZipFile(OUT) as z:
  assert z.testzip() is None,'BAD_NEW_ZIP_CRC'
  assert z.read(MAP)==old_map
  assert z.read(MAIN)==new_main
  inside={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
  check={n.split('  ',1)[1]:n.split('  ',1)[0] for n in z.read('SHA256SUMS.txt').decode().splitlines()}
  assert set(check)==set(inside)
  assert all(digest(v)==check[k] for k,v in inside.items())
  actual=[json.loads(s) for s in z.read(MAIN).splitlines()]
  diffs=[(a['source_ordinal'],a['lesson']) for a,b in zip(old,actual) if a!=b]
  assert len(diffs)==5 and set(x for x,_ in diffs)=={737,742,750,751,846} and all(l=='L06' for _,l in diffs)
  assert len(z.namelist())==len(stored)+1
  assert all(not c['formal_release_approved'] and not c['import_ready'] for c in actual)
 report['owner_sha256']=digest(OUT.read_bytes());report['bytes']=OUT.stat().st_size;report['zip_members']=len(stored)+1;report['internal_manifest_entries_verified']=len(stored);report['zip_crc_pass']=True
 (DIR/'L06-PHASE3-177-CARD-RELEASE-GATE-REPORT.json').write_text(dump(report),encoding='utf-8')
 (DIR/'L06-PHASE3-5-CARD-SCOPED-CORRECTIONS.json').write_text(dump(changes),encoding='utf-8')
 (DIR/'L06-PHASE3-177-CARD-BLOCKER-LEDGER.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in ledger),encoding='utf-8')
 (DIR/'L06-PHASE3-GLOBAL-FINITE-CLAUSE-CANDIDATES.json').write_text(dump(corpus_issues),encoding='utf-8')
 (DIR/'L06-PHASE3-177-CARD-FRONT-BACK-QA-ONLY.html').write_text(page,encoding='utf-8')
 (DIR/'L06-PHASE3-177-CARD-OFFLINE-TSV-QA-ONLY.tsv').write_text(tsv,encoding='utf-8')
 print(dump(report))

if __name__=='__main__':assemble()
