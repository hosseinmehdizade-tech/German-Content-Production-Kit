#!/usr/bin/env python3
"""Aspekte B1+ L07 Phase3: evidence-scoped language corrections, all-154 release gate.

Never reimport the publisher source CSV. Input must be latest curated L07 Phase2
Library owner ZIP (SHA specified below). Reopen the output main JSONL and check
actual per-object deltas BEFORE claiming saved-card changes. Fail closed.
"""
import argparse,collections,copy,csv,hashlib,html,io,json,re,sys,zipfile
from pathlib import Path
PARENT_SHA='fa13137b65c7e071da8eb857a01a82e0709c60874978df42ceb00d021e66ead6'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
DATE='2026-11-09'
SOURCE={
 852:{'rule':'der Lebensgefährte (des Lebensgefährten, Pl. Lebensgefährten); die Lebensgefährtin (Pl. Lebensgefährtinnen)','urls':['https://www.duden.de/rechtschreibung/Lebensgefaehrte','https://www.duden.de/rechtschreibung/Lebensgefaehrtin']},
 855:{'rule':'der Elternteil, Gen. des Elternteils / des Elternteiles, Pl. die Elternteile','urls':['https://www.duden.de/deklination/substantive/Elternteil']},
 860:{'rule':'sich zusammenraufen – raufte sich zusammen – hat sich zusammengerauft (ugs.)','urls':['https://www.duden.de/konjugation/zusammenraufen']},
 861:{'rule':'sich mit jdm. verloben – verlobte sich – hat sich verlobt','urls':['https://www.duden.de/rechtschreibung/verloben']},
 889:{'rule':'trennbar durchlesen – liest durch – las durch – hat durchgelesen; Gegensatz zum seltenen untrennbaren durchlesen','urls':['https://www.duden.de/konjugation/durchlesen_durchgelesen']},
 891:{'rule':'schweben – schwebte – hat geschwebt (schwebender Zustand); ist geschwebt (gerichtete Bewegung)','urls':['https://www.duden.de/rechtschreibung/schweben']},
 904:{'rule':'schmieden – schmiedete – hat geschmiedet; Planschmieden ist eine übertragene Bedeutung','urls':['https://www.duden.de/rechtschreibung/schmieden','https://www.duden.de/rechtschreibung/Plan_Vorhaben']},
 948:{'rule':'elementar – elementarer – am elementarsten','urls':['https://www.duden.de/deklination/adjektive/elementar']},
 987:{'rule':'pendeln – pendelte – ist gependelt (zwischen Orten unterwegs sein); hat gependelt (hin und her schwingen)','urls':['https://www.duden.de/rechtschreibung/pendeln']},
 999:{'rule':'verschweigen – verschwieg – hat verschwiegen; jdm. etw. verschweigen','urls':['https://www.duden.de/rechtschreibung/verschweigen']}
}

def sha(b):return hashlib.sha256(b).hexdigest()
def dump(obj,indent=2):return (json.dumps(obj,ensure_ascii=False,indent=indent,sort_keys=True)+'\n').encode('utf-8')
def jj(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def examples(card):
 b=card['back'];return (b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
def add_example(card,de,fa,sense_id):
 card['back'].setdefault('additional_examples_de_fa_pending_qa',[]).append({'de':de,'fa':fa,'sense_id':sense_id,'status':'PENDING_INDEPENDENT_DE_FA_SEMANTIC_QA','provenance':'L07_PHASE3_EDITORIAL_AI_AUTHORED_NOT_SOURCE_TEXTBOOK','L07_phase3_review':'EXAMPLE_ADDED_WITH_SCOPE_PENDING_QA'})
def scoped_attestation(card,ordinal):
 f=card['front'];entry=SOURCE[ordinal]
 assert not f.get('morphology_independently_validated'),('already_attested',ordinal)
 f['morphology_independently_validated']=True
 f['morphology_origin']='L07_PHASE3_SCOPED_DIRECT_DUDEN_ATTESTATION'
 f['form_qa_state']='G2_SCOPE_GRAMMAR_ATTESTED_G4_CONTENT_RELEASE_BLOCKED_NONIMPORT'
 f['G2_L07_phase3_scoped_grammatical_attestation']={
  'date':DATE,'evidence_urls':entry['urls'],'rule':entry['rule'],
  'scope':'THE_LISTED_FORM_RULE_ONLY_NOT_WHOLE_CARD','status':'DUDEN_CASE_SCOPED_ATTESTED','release_approved':False}
 card['L07_phase3_language_QA']={
 'status':'CASE_SPECIFIC_CORRECTION_OR_GRAMMAR_EVIDENCE_NO_FULL_CARD_SIGNOFF',
 'external_grammatical_evidence_checked':True,
 'morphology_attestation_scope_only':True,
 'full_DE_FA_semantic_release_approval':False,
 'real_app_import_render_verified':False}

def sense(card,i,de,fa,colls):
 return {'sense_id':card['preview_card_id']+f':L07P3:S{i}', 'sense_de':de,'sense_fa':fa,
  'Kombinationen_DE_FA':[{'de':p,'fa':q} for p,q in colls],
  'Synonyme':[],'Antonyme':[],'Wortfamilie':[],'Verwandte_Woerter_KEINE_Synonyme':[],
  'status':'PENDING_G4_INDEPENDENT_SENSE_AND_RELATION_QA','source':'L07_PHASE3_DUDEN_SCOPED_SEMANTIC_SPLIT_NOT_FULL_CARD_ATTESTATION'}

def route(e,sid):
 e['sense_id']=sid;e['L07_phase3_review']='REVIEWED_CONTEXTUAL_MEANING_ROUTING_NOT_FINAL_RELEASE'

def changes(cards):
 lesson=[c for c in cards if c['lesson']=='L07'];assert len(lesson)==154
 selected={c['source_ordinal']:c for c in lesson if c['source_ordinal']!=956}
 assert len(selected)==152,(len(selected), 'expected 152 other ordinal rows plus 2 cards from 956')
 for o in SOURCE:scoped_attestation(selected[o],o)
 # A previously inverted meaning link in schmieden: Plan was wrongly assigned to metalworking.
 metal,plans=selected[904]['back']['semantic_network_sense_anchored_pending_qa']
 assert 'Metall' in metal['sense_de'] and 'Pläne' in plans['sense_de']
 ex=examples(selected[904]);assert len(ex)==2
 assert 'Pläne' in ex[0]['de'] and 'Schmied' in ex[1]['de']
 assert ex[0]['sense_id']==metal['sense_id'] and ex[1]['sense_id']==metal['sense_id']
 route(ex[0],plans['sense_id'])
 # Literal molten-iron example was already correctly assigned to metalworking.
 # 'schweben' has different perfect auxiliaries in a hovering STATE and directional MOTION.
 hover=selected[891];nets=hover['back'].get('semantic_network_sense_anchored_pending_qa') or []
 assert not nets
 s1=sense(hover,1,'in der Luft oder an einer Stelle gehalten sein, ohne zu sinken','معلق یا شناور ماندن در هوا',
          [('über dem Boden schweben','بالای زمین معلق ماندن')])
 s2=sense(hover,2,'sich leicht und schwebend in eine Richtung bewegen','سبک و شناور به سویی حرکت کردن',
          [('langsam zu Boden schweben','آهسته در هوا به سوی زمین پایین آمدن')])
 hover['back']['semantic_network_sense_anchored_pending_qa']=[s1,s2]
 old=examples(hover);assert len(old)==2 and 'Ballon' in old[0]['de'] and 'Duft' in old[1]['de']
 route(old[0],s1['sense_id']);route(old[1],s2['sense_id'])
 add_example(hover,'Ein Blatt ist langsam zu Boden geschwebt.','برگی آرام در هوا به سوی زمین پایین آمد.',s2['sense_id'])
 hover['front']['display_de_provisional']='schweben – schwebt – schwebte – hat geschwebt (Zustand) / ist geschwebt (Richtung)'
 # The old auxiliary description was linguistically incomplete, and the second meaning lacked an independent example.
 pend=selected[987];pn=pend['back']['semantic_network_sense_anchored_pending_qa'];assert len(pn)==2
 pend['front']['display_de_provisional']='pendeln – pendelt – pendelte – ist gependelt (Fahrt zwischen Orten) / hat gependelt (Schwingung)'
 add_example(pend,'Der Zeiger hat eine Weile hin und her gependelt.','عقربه مدتی به این سو و آن سو نوسان کرد.',pn[1]['sense_id'])
 # Elementar: explicitly demonstrate the basic/beginner sense instead of treating it as identical to 'fundamental'.
 elem=selected[948];en=elem['back']['semantic_network_sense_anchored_pending_qa'];assert len(en)==2
 add_example(elem,'Der Kurs vermittelt elementare Kenntnisse für Anfänger.','این دوره به مبتدیان دانش مقدماتی می‌آموزد.',en[1]['sense_id'])
 return sorted(SOURCE)

def verify_base(z):
 assert z.testzip() is None,'PARENT_CRC_FAIL'
 data={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
 refs=dict((name,d) for d,name in [x.split('  ',1) for x in z.read('SHA256SUMS.txt').decode().splitlines() if x])
 assert set(refs)==set(data),'PARENT_MANIFEST_SET_MISMATCH'
 assert all(sha(data[n])==h for n,h in refs.items()),'PARENT_MEMBER_HASH_FAIL'
 return data

def duplicates(cards):
 out=[]
 for c in cards:
  v=collections.defaultdict(list)
  for e in examples(c):
   de=re.sub(r'\s+',' ',e.get('de','').strip()).casefold()
   if de:v[de].append(e)
  for de,arr in v.items():
   if len(arr)>1:out.append({'lesson':c['lesson'],'ordinal':c['source_ordinal'],'card_id':c['preview_card_id'],'normalized_de':de,'repetitions':len(arr)})
 return out

def audit_global(cards):
 n=0;issues=[]
 # The same conservative v4 known finite-verb detector used in previous phase. New checks are not full semantic certification.
 det={'der','die','das','ein','eine','einen','einem','einer','diese','dieser','dieses','jener','jene'}
 finite={'reicht','entscheidet','koordiniert','läuft','prüft','schreibt','bringt','bestimmt','öffnet','organisiert','führt','hat','ist','sind','steht','arbeitet','verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt','hält','macht','kann','wird','werden','nimmt','bietet','spricht'}
 for c in cards:
  for s in c['back'].get('semantic_network_sense_anchored_pending_qa',[]) or []:
   for k in s.get('Kombinationen_DE_FA',[]) or []:
    n+=1;de=k.get('de','');w=re.findall(r'\w+',de,re.UNICODE)
    if len(w)>=4 and w[0].casefold() in det and w[1][0].isupper() and w[2].casefold() in finite:
     issues.append({'lesson':c['lesson'],'ordinal':c['source_ordinal'],'collocation':de})
 return n,issues

def html_preview(lesson):
 out=['<!doctype html><html lang="de"><meta charset="utf-8"><title>Aspekte B1+ L07 Phase3 QA ONLY NONIMPORT</title>',
 '<style>body{font-family:system-ui,Arial;max-width:1120px;margin:auto;padding:24px;background:#f8f9fc}article{background:white;border:1px solid #ddd;border-radius:12px;margin:12px 0;padding:17px}h2{color:#20385e}p{line-height:1.5}small{color:#744}</style><h1>Aspekte B1+ Lektion 07 – QA ONLY · NONIMPORT</h1><p>154 cards. Not a validated app runtime or approval.</p>']
 for c in lesson:
  f=c['front'];b=c['back'];out.append('<article><h2>'+html.escape(str(c['source_ordinal'])+' · '+f['display_de_provisional'])+'</h2>');out.append('<p lang="fa" dir="rtl">'+html.escape(b['meanings_fa_provisional'])+'</p>')
  out.append('<p><small>Form-Evidence: '+('CASE-SCOPED ONLY' if f.get('morphology_independently_validated') else 'UNATTESTED')+' · HOLD '+str(c.get('curated_HOLD_content_disposition_exists'))+'</small></p>')
  for e in examples(c):out.append('<p>'+html.escape(e['de'])+'<span lang="fa" dir="rtl"> — '+html.escape(e['fa'])+'</span><br><small>pending / '+html.escape(str(e.get('sense_id','')))+'</small></p>')
  for s in b.get('semantic_network_sense_anchored_pending_qa',[]) or []:
   out.append('<p><b>'+html.escape(s['sense_de'])+'</b> — '+html.escape(s['sense_fa'])+'</p>')
   for x in s.get('Kombinationen_DE_FA',[]) or []:out.append('<p>• '+html.escape(x['de'])+' — '+html.escape(x['fa'])+'</p>')
  out.append('</article>')
 return ('\n'.join(out)+ '</html>').encode()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('parent');ap.add_argument('output');a=ap.parse_args()
 parent=Path(a.parent);assert sha(parent.read_bytes())==PARENT_SHA,'NOT_CURRENT_CANONICAL_PARENT_SHA'
 with zipfile.ZipFile(parent) as z:data=verify_base(z)
 old=[json.loads(x) for x in data[MAIN].splitlines()];before=copy.deepcopy(old)
 assert len(old)==1571;ids=[x['preview_card_id'] for x in old];assert len(ids)==len(set(ids))
 modified_ord=changes(old)
 new_primary=('\n'.join(jj(x) for x in old)+'\n').encode('utf-8')
 # Parent and child may have different global canonical formatting, so evaluate per-card actual differences.
 changed=[(x,y) for x,y in zip(before,old) if x!=y];assert len(changed)==10,len(changed)
 assert {y['source_ordinal'] for x,y in changed}==set(modified_ord)
 assert all(x==y for x,y in zip(before,old) if x['lesson']!='L07')
 assert [x['preview_card_id'] for x in old]==ids
 assert all(x['linked_original_source_ordinals']==y['linked_original_source_ordinals'] for x,y in zip(before,old))
 lesson=[x for x in old if x['lesson']=='L07'];assert len(lesson)==154
 old_examples=sum(len(examples(x)) for x in before if x['lesson']=='L07')
 current_examples=sum(len(examples(x)) for x in lesson)
 assert old_examples==348 and current_examples==351,(old_examples,current_examples)
 attest=sum(bool(x['front'].get('morphology_independently_validated')) for x in lesson)
 assert attest==10,attest
 holds=sum(bool(x.get('curated_HOLD_content_disposition_exists')) for x in lesson);assert holds==38
 net=[x for x in lesson if x['back'].get('semantic_network_sense_anchored_pending_qa')]
 assert len(net)==41,len(net)
 orphans=[(x['source_ordinal'],e['de']) for x in net for e in examples(x) if e.get('sense_id') not in {s['sense_id'] for s in x['back']['semantic_network_sense_anchored_pending_qa']}]
 assert not orphans,orphans
 global_count,finite=audit_global(old);dups=duplicates(old)
 assert global_count==834,global_count
 assert len(finite)==3,finite;assert not any(x['lesson']=='L07' for x in finite)
 assert len(dups)==2,dups
 assert sum(len(examples(x)) for x in old if x['lesson']!='L07')==sum(len(examples(x)) for x in before if x['lesson']!='L07')
 change_log=[{'card_id':y['preview_card_id'],'ordinal':y['source_ordinal'],'headword':y['front']['base_headword_de'],
              'prior':x,'after':y,'form_scope_source':SOURCE[y['source_ordinal']]} for x,y in changed]
 decisions=[]
 for c in lesson:
  f=c['front'];is_att=bool(f.get('morphology_independently_validated'))
  reasons=['FULL_BILINGUAL_CARD_CONTENT_QA_NOT_CERTIFIED','REAL_APP_IMPORT_FRONT_BACK_RENDER_NOT_EXECUTED','FORMAL_CARD_RELEASE_NOT_APPROVED']
  if c['curated_HOLD_content_disposition_exists']:reasons.append('INHERITED_EDITORIAL_HOLD_NOT_CLEARED')
  if not is_att:reasons.append('NO_SCOPED_LEXICOGRAPHIC_FORM_ATTESTATION_RECORDER')
  decisions.append({'id':c['preview_card_id'],'ordinal':c['source_ordinal'],'headword':f['base_headword_de'],
                    'release':'BLOCKED','all_current_examples':len(examples(c)),
                    'morphology_scope_attested':is_att,'is_curated_HOLD':c['curated_HOLD_content_disposition_exists'],
                    'L07_phase3_primary_data_changed':c['source_ordinal'] in modified_ord,
                    'release_blockers':reasons})
 report={
 'schema':'aspekte-b1plus-L07-phase3-actual-gate@1','date':DATE,'lesson':'L07','stage':'PHASE3_154_CARD_RELEASE_GATE_EVALUATED_BLOCKED_NONIMPORT',
 'input_parent_sha256':PARENT_SHA,'input_main_sha256':sha(data[MAIN]),'output_main_sha256':sha(new_primary),
 'current_cards':1571,'current_original_map_rows':1548,'current_L07_cards':len(lesson),
 'cards_with_actual_object_edits_after_reopen':10,'scoped_Duden_form_attestations_new':10,
 'L07_scoped_form_attestations_total':attest,'L07_form_scopes_not_individually_attested':len(lesson)-attest,
 'L07_curated_HOLDs_kept':holds,'L07_example_pairs_before':old_examples,'L07_example_pairs_after':current_examples,
 'new_bilingual_examples_scoped_pending_QA':3,'meaning_routing_fixed':'schmieden plans example S1=>S2',
 'schweben_new_network_senses':2,'networked_L07_cards_after':len(net),
 'L07_network_example_unrouted':len(orphans),'global_collocations':global_count,
 'global_finite_clause_v4_findings':len(finite),'global_finite_clause_v4_issues':finite,
 'global_exact_same_card_DE_duplicate_groups_remaining':len(dups),'global_duplicate_group_cases':dups,
 'all_other_lessons_card_objects_unchanged':True,'source_map_exact_bytes_unchanged':True,'all_IDs_and_links_unchanged':True,
 'L07_release_gate':'BLOCKED_ALL_154','formally_released_cards':0,'real_German_Flashcards_Pro_runtime_import_tested':False,
 'offline_qa_html':'QA_ONLY_NOT_APP_RENDER','offline_tsv_records':154,
 'caveat':'Duden attestations are strictly case-scoped grammar evidence, not whole-card bilingual QA. 38 HOLDs preserved; 144 cards have no scoped G2 evidence. Existing global v4 three candidate clauses and two duplicate groups persist outside L07.'}
 data[MAIN]=new_primary
 data['Lessons/L07/L07-PHASE3-154-CARD-QA-REPORT.json']=dump(report)
 data['Lessons/L07/L07-PHASE3-10-CARD-BEFORE-AFTER.json']=dump({'changes':change_log})
 data['Lessons/L07/L07-PHASE3-154-CARD-BLOCKER-LEDGER.jsonl']=(''.join(jj(x)+'\n' for x in decisions)).encode()
 data['Lessons/L07/L07-PHASE3-LANGUAGE-SCOPE-SOURCES.json']=dump({'date':DATE,'Duden_urls':SOURCE,'whole_card_approvals':0})
 data['Lessons/L07/L07-PHASE3-154-CARD-QA-ONLY.html']=html_preview(lesson)
 buf=io.StringIO();writer=csv.writer(buf,delimiter='\t');writer.writerow(['card_id','front_de','back_fa','example_count','status'])
 for c in lesson:writer.writerow([c['preview_card_id'],c['front']['display_de_provisional'],c['back']['meanings_fa_provisional'],len(examples(c)),'QA_ONLY_NONIMPORT'])
 data['Lessons/L07/L07-PHASE3-154-CARD-OFFLINE-TSV-QA-ONLY.tsv']=buf.getvalue().encode('utf-8-sig')
 data['Tools/build_L07_phase3_v1.py']=Path(__file__).read_bytes()
 data['README-L07-PHASE3-NONIMPORT.md']=(f'# L07 Phase3 release gate evaluated — BLOCKED\n\nParent canonical ZIP SHA256: {PARENT_SHA}\n154 card decisions, 10 saved actual edits, 10 scoped Duden grammatical attestations, 351 examples. No real application runtime import/render tested. Global known 3 finite-clause and 2 example-duplicate failures remain; 38 L07 curated HOLDs not auto-cleared. Primary learner data member is updated, not just sidecar.\n').encode()
 sums=''.join(sha(v)+'  '+n+'\n' for n,v in sorted(data.items())).encode();data['SHA256SUMS.txt']=sums
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for n,v in sorted(data.items()):z.writestr(n,v)
 # Absolute physical proof by reopening the *new* ZIP and comparison with original parent.
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None,'CHILD_ZIP_CRC_FAILED'
  after={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
  manifest=dict((n,h) for h,n in (x.split('  ',1) for x in z.read('SHA256SUMS.txt').decode().splitlines() if x))
  assert set(after)==set(manifest)
  assert all(sha(v)==manifest[k] for k,v in after.items()),'CHILD_ZIP_MANIFEST_FAIL'
  reread=[json.loads(x) for x in after[MAIN].splitlines()]
  real_changed=[(x,y) for x,y in zip(before,reread) if x!=y]
  assert len(real_changed)==10
  assert all(x==y for x,y in zip(before,reread) if x['lesson']!='L07')
  assert after[MAP]==data[MAP]
  assert [c['preview_card_id'] for c in reread]==ids
  assert len([x for x in reread if x['lesson']=='L07'])==154
  assert len([c for c in reread if c['lesson']=='L07' and c.get('formal_release_approved')])==0
  report.update({'child_zip_sha256':sha(out.read_bytes()),'child_zip_bytes':out.stat().st_size,
                 'child_zip_members':len(z.namelist()),'manifest_internal_sha256_verified':len(manifest),
                 'crc_pass':True,'saved_primary_reopened_actual_card_object_changes':len(real_changed)})
 # The matching receipt/report with ZIP hash is intentionally external to the ZIP, to avoid a self-hash cycle.
 rpt=out.parent/'L07-PHASE3-FINAL-VERIFICATION-RECEIPT.json';rpt.write_bytes(dump(report))
 print(json.dumps({k:v for k,v in report.items() if k not in ('global_finite_clause_v4_issues','global_duplicate_group_cases')},ensure_ascii=False,indent=2))
 print('OUTPUT',out)

if __name__=='__main__':main()
