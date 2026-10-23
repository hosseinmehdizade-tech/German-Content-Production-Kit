import csv,io,json,hashlib,zipfile,re,pathlib,copy,collections,sys
assert len(sys.argv)==3, 'Usage: python REBUILD_R60.py EXACT_R59.zip R60_output.zip'
BASE=pathlib.Path(sys.argv[1])
OUT=pathlib.Path(sys.argv[2])
assert BASE.is_file() and hashlib.sha256(BASE.read_bytes()).hexdigest()=='0f0de9d320cce775c639d0098a3fc001cd22d597a287044ff8e7dd41039cc8bc', 'Wrong R59 authority' 
OLD='90-Stage4-Scoped-Synonym-And-Provenance-R59/'
NEW='91-Stage4-Origin-Training-Synonym-Scope-R60/'
H=lambda b:hashlib.sha256(b).hexdigest()
C=lambda o:json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
J=lambda o:(json.dumps(o,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode('utf-8')
T=lambda b:list(csv.DictReader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t'))
def tsv(rows,headers):
 o=io.StringIO(newline='');w=csv.DictWriter(o,fieldnames=headers,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return o.getvalue().encode('utf-8')
SCOPES={
 'ma2-lu-0077':{'relation_id':'ma2-lu-0077-rel-v336-syn-001','term':'herrühren von','scope':'Nur wenn herkommen von eine Ursache oder den Ursprung einer Sache bezeichnet (z. B. Das Problem kommt von einem Fehler her ≈ rührt von einem Fehler her). Nicht pauschal für räumliche Richtung/Bewegung (Von den Bergen her kommt ein Wind) oder jede Angabe zur persönlichen Herkunft: herrühren benennt primär Ursache/Ursprung, nicht die Bewegungsrichtung.','source_ref':{'source_id':'DUDEN_ONLINE','locator':'Duden herrühren: seine Ursache, seinen Ursprung haben; https://www.duden.de/rechtschreibung/herruehren','version':None},'prior':'originate/derive from','rationale':'German example 003 expresses spatial direction whereas herrühren denotes cause/origin.'},
 'ma2-lu-0078':{'relation_id':'ma2-lu-0078-rel-v336-syn-001','term':'üben','scope':'Nur beim wiederholten Einüben einer konkreten Fertigkeit oder Bewegung, z. B. einen Aufschlag trainieren ≈ üben. Nicht allgemein für Sport treiben oder Kondition/Ausdauer trainieren und nicht für jemanden/eine Mannschaft als Trainer betreuen: eine Jugendmannschaft trainieren ≠ eine Jugendmannschaft üben.','source_ref':{'source_id':'DUDEN_ONLINE','locator':'Duden trainieren senses 1–4 (Mannschaft trainieren / Sport treiben / Fertigkeiten); https://www.duden.de/rechtschreibung/trainieren','version':None},'prior':'train/practise regularly','rationale':'German example 003 is coaching a youth team; üben cannot replace transitive coaching use.'}
}
assert not OUT.exists()
with zipfile.ZipFile(BASE) as z:
 assert z.testzip() is None
 parent_names=z.namelist(); assert len(parent_names)==1022==len(set(parent_names))
 candidate=z.read(OLD+'CANDIDATE-IMPORT-NOT-FINAL.tsv');rows=T(candidate);assert len(rows)==292
 headers=list(rows[0]); unchanged=[]
 for row in rows:
  if row['id'] not in SCOPES:unchanged.append(copy.deepcopy(row));continue
  f=json.loads(row['custom_fields']);spec=SCOPES[row['id']];rid=spec['relation_id'];canon=[x for x in f['canonical_relations'] if x.get('relation_id')==rid];assert len(canon)==1
  rel=canon[0];assert rel['relation_type']=='SYNONYM' and rel['value']['term']==spec['term'] and rel['value']['scope']==spec['prior'];rel['value']['scope']=spec['scope']
  # Course screenshots document the lemma, NOT this enriched synonym. Use direct lexicon authority on the relation.
  rel['provenance']['source_refs']=[spec['source_ref']]
  rel['provenance']['verification']='Duden online semantic scope model-editorial correction R60; NOT independent expert approval'
  vn=[x for g in f['vnext_relations'] if g['type']=='SYNONYM' for x in g['items'] if x['relation_id']==rid]; assert len(vn)==1 and vn[0]['scope']==spec['prior'];vn[0]['scope']=spec['scope']
  # Learner-visible caveats already correct. No UI change.
  row['custom_fields']=json.dumps(f,ensure_ascii=False,separators=(',',':'))
 newcandidate=tsv(rows,headers); ch=H(newcandidate);assert ch!=H(candidate)
 original_others={r['id']:r for r in T(candidate) if r['id'] not in SCOPES}
 assert all(r==original_others[r['id']] for r in rows if r['id'] not in SCOPES)
 review=json.loads(z.read(OLD+'REVIEW-DATA.json'));oldreview=copy.deepcopy(review)
 assert len(review['examples'])==1168 and len(review['synonyms'])==243
 touched=[]
 for item in review['synonyms']:
  spec=SCOPES.get(item['card_id']);
  if not spec:continue
  assert item['id']==spec['relation_id'] and item['scope']==spec['prior'];item['scope']=spec['scope'];item['sources']=[{'source_id':spec['source_ref']['source_id'],'locator':spec['source_ref']['locator']}]
  item['fingerprint']=H(C({k:v for k,v in item.items() if k!='fingerprint'}));touched.append(item['id'])
 assert len(touched)==2
 review['candidate_sha256']=ch;review['parent_zip_sha256']=H(BASE.read_bytes());review['data_fingerprint']=H(C({'candidate_sha256':ch,'items':[[x['id'],x['fingerprint']] for x in review['examples']+review['synonyms']]}))
 newfp=review['data_fingerprint']
 assert all(x['fingerprint']==y['fingerprint'] for x,y in zip(review['examples'],oldreview['examples']))
 assert sum(x['fingerprint']!=y['fingerprint'] for x,y in zip(review['synonyms'],oldreview['synonyms']))==2
 oldex=T(z.read(OLD+'EXAMPLES-1168-INDEPENDENT-REVIEW.tsv'));oldsy=T(z.read(OLD+'SYNONYMS-243-INDEPENDENT-REVIEW.tsv'));oldpriority=T(z.read(OLD+'REVIEW-PRIORITY-1411-R59.tsv'))
 example_bytes=z.read(OLD+'EXAMPLES-1168-INDEPENDENT-REVIEW.tsv')
 synced={x['id']:x for x in review['synonyms']}
 for s in oldsy:
  if s['relation_id'] in touched:
   a=synced[s['relation_id']];s['sense_scope']=a['scope'];s['source_refs']=json.dumps(a['sources'],ensure_ascii=False,separators=(',',':'));s['fingerprint']=a['fingerprint'];s['independent_review_status']='NOT_REVIEWED';s['independent_reviewer_note']=''
 for s in oldpriority:
  if s['item_id'] in touched:
   s['fingerprint']=synced[s['item_id']]['fingerprint'];s['qa_disposition']='R60_DICTIONARY_MODEL_EDIT_NOT_QUALIFIED_INDEPENDENT_SIGNOFF'
 synonym_bytes=tsv(oldsy,list(oldsy[0]));priority_bytes=tsv(oldpriority,list(oldpriority[0]))
 # Embed exact new R60 JSON into the *offline* reviewer, no network/UI/app changes.
 html=z.read(OLD+'OFFLINE-REVIEW-WORKBENCH.html').decode('utf-8'); assert 'Independent Review R59' in html
 html=html.replace('Independent Review R59','Independent Review R60',1)
 pattern=r'(<script id="payload" type="application/json">)(.*?)(</script>)'
 assert len(re.findall(pattern,html,re.S))==1
 payload=json.dumps(review,ensure_ascii=False).replace('</','<\\/')
 html=re.sub(pattern,lambda m:m.group(1)+payload+m.group(3),html,count=1,flags=re.S)
 # Rebind R59 strict intake validator and negative test suite to new inventory.
 intake=z.read(OLD+'VALIDATE_R59_REVIEW_EXPORT.py').decode('utf-8').replace('R57','R60').replace('R59','R60')
 intake=intake.replace("EXPECTED_CANDIDATE_SHA = 'e5c380c7aaac5569571849cdfb1f253874c15105ab84dddcf3782d607eb3c4cd'",f"EXPECTED_CANDIDATE_SHA = '{ch}'")
 intake=intake.replace("EXPECTED_REVIEW_FINGERPRINT = '54ee0a8c3c3ad80c91b188a043daf75cc29faaaff43412e53a22241ad99eb3de'",f"EXPECTED_REVIEW_FINGERPRINT = '{newfp}'")
 intake=intake.replace('r59','r60').replace('r57','r60')
 intake=intake.replace("R60 = '90-Stage4-Scoped-Synonym-And-Provenance-R60/'",f"R60 = '{NEW}'")
 assert f"R60 = '{NEW}'" in intake and f"EXPECTED_CANDIDATE_SHA = '{ch}'" in intake
 intake_tests=z.read(OLD+'TEST_R59_REVIEW_INTAKE.py').decode('utf-8').replace('R59','R60')
 # Ensure test suite uses supplied ZIP path without guessing an unverified one.
 assert "sys.argv[1]" in intake_tests
 cases=[
  ('ma2-lu-0165-ex-003','EXAMPLE','TRANSLATION_OK','nicht stimmt = something was wrong; Persian reads something is not right'),
  ('ma2-lu-0003-rel-v336-syn-001','SYNONYM','SCOPE_ACCEPTABLE','steigen only movement upward; not all climbing'),
  ('ma2-lu-0012-rel-v336-syn-001','SYNONYM','SCOPE_ACCEPTABLE','eingeben / eintragen restricted to form/list context'),
  ('ma2-lu-0016-rel-v336-syn-001','SYNONYM','SCOPE_ACCEPTABLE','renovieren and erneuern only in building renewal context'),
  ('ma2-lu-0077-rel-v336-syn-001','SYNONYM','CORRECTED_BY_R60','Cause vs purely geographic direction clarified'),
  ('ma2-lu-0078-rel-v336-syn-001','SYNONYM','CORRECTED_BY_R60','Skill practice vs coaching/sport conditioning clarified'),
  ('ma2-lu-0110-rel-v336-syn-001','SYNONYM','PRIOR_R59_SCOPE_PRESERVED','Lack vs anstreichen contextual overlap retained'),
  ('ma2-lu-0117-rel-v336-syn-001','SYNONYM','NEEDS_QUALIFIED_CONTEXT_JUDGMENT','optimieren implies targeted optimization, not general improvement'),
  ('ma2-lu-0144-rel-v336-syn-001','SYNONYM','PRIOR_R56_SCOPE_PRESERVED','aufbrauchen requires complete consumption'),
  ('ma2-lu-0146-rel-v336-syn-001','SYNONYM','PRIOR_R59_SCOPE_PRESERVED','consumer goods not all technical/media uses'),
  ('ma2-lu-0150-rel-v336-syn-001','SYNONYM','PRIOR_R57_SCOPE_PRESERVED','staunen real surprise/intensity nuance'),
  ('ma2-lu-0181-rel-v336-syn-001','SYNONYM','SCOPE_ACCEPTABLE','die Produktion einstellen approximately stop producing'),
  ('ma2-lu-0251-rel-v336-syn-001','SYNONYM','NEEDS_QUALIFIED_CONTEXT_JUDGMENT','blockieren vs sperren usage across road/account varies'),
  ('ma2-lu-0267-rel-v336-syn-001','SYNONYM','SCOPE_ACCEPTABLE','digital form entry only, not search/password generally'),
  ('ma2-lu-0260-ex-004','EXAMPLE','CASE_FRAME_ACCEPTABLE','mir die Fingernägel schneiden valid dative possessor construction')]
 eid={x['id'] for x in review['examples']};sid={x['id'] for x in review['synonyms']};assert all((k in eid if typ=='EXAMPLE' else k in sid) for k,typ,_,_ in cases)
 ledger={'schema':'ma2-r60-bounded-model-semantic-triage@1','date':'2026-10-23','status':'MODEL_EDITORIAL_NOT_INDEPENDENT_EXPERT','basis':{'r59_sha256':H(BASE.read_bytes()),'R60_candidate_sha256':ch,'source_screenshots_preserved':True},'inspected_count':len(cases),'cases':[{'item_id':i,'kind':kind,'model_disposition':disposition,'reason':reason,'fingerprint':next(t['fingerprint'] for t in review['examples']+review['synonyms'] if t['id']==i)} for i,kind,disposition,reason in cases], 'external_dictionary_links':['https://www.duden.de/rechtschreibung/herruehren','https://www.duden.de/rechtschreibung/trainieren','https://www.duden.de/rechtschreibung/ueben_wiederholen_lernen_aneignen'],'independent_qualified_approvals':0,'independent_unreviewed':1411,'warning':'Model scoped triage is not an independent qualified linguistic signoff.'}
 evidence={'schema':'ma2-r60-bounded-corrections@1','source_relation_lemma_only':True,'changes':[{'card_id':id,'relation_id':d['relation_id'],'term':d['term'],'before_scope':d['prior'],'after_scope':d['scope'],'reason':d['rationale'],'dictionary_reference':d['source_ref']} for id,d in SCOPES.items()],'unchanged_cards':290,'examples_unchanged':1168,'relation_ids_unchanged':True,'stage4_final':False,'independent_approvals':0}
 checkpoint={'schema':'ma2-stage4-r60-workstream-checkpoint@1','milestone':'R60_TWO_DICTIONARY_GROUNDED_SCOPE_PARITY_REPAIRS','date':'2026-10-23','status':'PASS_SCOPED_MODEL_EDITORIAL_CANDIDATE_QA_NOT_EXPERT','parent_r59_zip_sha256':H(BASE.read_bytes()),'candidate_sha256':ch,'review_data_fingerprint':newfp,'data_fingerprint':newfp,'candidate_path':NEW+'CANDIDATE-IMPORT-NOT-FINAL.tsv','cards':292,'examples':1168,'synonyms':243,'total_relations':1209,'changed_card_ids':list(SCOPES),'parent_members_preserved':1022,'independent_approvals':0,'independent_unreviewed':1411,'stage4':'BLOCKED_NOT_FINAL','stage5':'NOT_RUN','stage6':'NOT_RUN','stage7':'NOT_RUN','import_authorized':False,'no_ui_changes':True}
 readme=f'''# Menschen A2 Verben — R60 scoped lexical synonym repair (WIP)\n\nParent R59 ZIP SHA256: {checkpoint['parent_r59_zip_sha256']}\n\nEdited card IDs: {', '.join(SCOPES)}. Two SYNONYM scopes and their provenance in canonical/vnext mirror changed. Original course screenshots, all 1168 examples, 290 other card rows and 1209 relation IDs are unchanged. No app/UI change.\n\nExternal dictionary evidence is Duden online; the course screenshots attest headwords, not these curated synonyms. 15 model editorial priority cases annotated; **0 of 1411 independently approved**. Offline review and intake validator are exact R60 candidate-bound; R59 exports must be rejected. Stage4 blocked, no import.\n\nفارسی: این بسته نسخه کاری است. اصلاح دو رابطهٔ مترادف به معنی تأیید مستقل ۱۴۱۱ مورد نیست. ابزار تأیید صرفاً تطبیق ساختار/اثر انگشت انجام می‌دهد.\n'''
 additions={
  'CANDIDATE-IMPORT-NOT-FINAL.tsv':newcandidate,
  'REVIEW-DATA.json':J(review),
  'EXAMPLES-1168-INDEPENDENT-REVIEW.tsv':example_bytes,
  'SYNONYMS-243-INDEPENDENT-REVIEW.tsv':synonym_bytes,
  'REVIEW-PRIORITY-1411-R60.tsv':priority_bytes,
  'OFFLINE-REVIEW-WORKBENCH.html':html.encode('utf-8'),
  'VALIDATE_R60_REVIEW_EXPORT.py':intake.encode('utf-8'),
  'TEST_R60_REVIEW_INTAKE.py':intake_tests.encode('utf-8'),
  'BOUND-DICTIONARY-REPAIR-EVIDENCE.json':J(evidence),
  '15-HIGH-PRIORITY-MODEL-TRIAGE-NOT-EXPERT.json':J(ledger),
  'CHECKPOINT.json':J(checkpoint),
  'README-FA-DE.md':readme.encode('utf-8'),
 }
 manifest={'schema':'ma2-r60-added-member-sha256@1','members':{NEW+k:H(v) for k,v in additions.items()}}
 additions['ADDED-MANIFEST-SHA256.json']=J(manifest)
 import shutil
 shutil.copyfile(BASE,OUT)
 with zipfile.ZipFile(OUT,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as w:
  for k,v in additions.items():
   info=zipfile.ZipInfo(NEW+k, date_time=(2026,10,23,1,26,22))
   info.compress_type=zipfile.ZIP_DEFLATED
   info.external_attr=25165824
   info.create_system=3
   w.writestr(info,v,compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
 with zipfile.ZipFile(OUT) as q:
  assert q.testzip() is None
  assert len(q.namelist())==1022+len(additions)==len(set(q.namelist()))
  assert all(q.read(name)==z.read(name) for name in parent_names)
  assert all(H(q.read(NEW+k))==H(v) for k,v in additions.items())
  assert T(q.read(NEW+'CANDIDATE-IMPORT-NOT-FINAL.tsv'))==rows
  assert json.loads(q.read(NEW+'REVIEW-DATA.json'))==review
 print(json.dumps({'target_zip':str(OUT),'size_bytes':OUT.stat().st_size,'sha256':H(OUT.read_bytes()),'parent_sha256':H(BASE.read_bytes()),'members':1022+len(additions),'new_members':len(additions),'candidate_sha256':ch,'review_data_fingerprint':newfp,'two_changed':list(SCOPES),'triaged':len(cases)},indent=2))
