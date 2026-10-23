#!/usr/bin/env python3
"""Menschen A2 Stage4 R66 source-bound English invoice correction & synonym triage.

Run: python BUILD_R66_FROM_R62.py exact-R62.zip output-R66.zip
Fail closed on parent SHA, candidate hash, per-example identities, or review
fingerprint mismatch. Does not conduct independent expert signoff or import.
"""
import pathlib, hashlib, json, csv, io, zipfile, shutil, re, copy, argparse
PARENT_SHA='4915e69dd77444f3103a5679aee43a2600cea7ab9b2bd438a0fe723da42a16d7'
PARENT_CAND='f6639703f9753afcfe84ee53ff0687b69281a557f681dcb5a0c1d85c9fff35e6'
PARENT_REVIEW='b8f2c12484dac9b6f7143c76f9e48bebb2144f56818d38dd9d80d47c31339306'
SRC='92-Stage4-Verbessern-Optimieren-Scope-Rebind-R62/'
DST='93-Stage4-Rechnung-Translation-And-Synonym-Triage-R66/'
CARD='ma2-lu-0131'; ITEM='ma2-lu-0131-ex-003'
OLD='I threw away the old receipt.'
NEW='I threw away the old invoice.'
SHA=lambda v:hashlib.sha256(v).hexdigest()
CANON=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
JSON=lambda x:(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def readtab(b):return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t'))
def writetab(rows,fields):
 s=io.StringIO(newline=''); w=csv.DictWriter(s,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue().encode()
def build(parent,out):
 assert parent.is_file() and SHA(parent.read_bytes())==PARENT_SHA,'Unexpected R62 SHA'
 assert not out.exists(),'Will not overwrite target'
 with zipfile.ZipFile(parent) as z:
  assert z.testzip() is None and len(z.namelist())==1048 and len(set(z.namelist()))==1048
  parent_names=z.namelist()
  original=z.read(SRC+'CANDIDATE-IMPORT-NOT-FINAL.tsv')
  assert SHA(original)==PARENT_CAND
  lines=original.decode('utf-8').splitlines(keepends=True)
  idx=[i for i,line in enumerate(lines) if line.startswith(CARD+'\t')]
  assert len(idx)==1 and lines[idx[0]].count(OLD)==3
  lines[idx[0]]=lines[idx[0]].replace(OLD,NEW)
  candidate=''.join(lines).encode('utf-8')
  assert candidate != original
  old_cards=readtab(original); cards=readtab(candidate)
  assert len(cards)==292 and len(set(r['id'] for r in cards))==292
  assert [(r['id'],r) for r in old_cards if r['id']!=CARD]==[(r['id'],r) for r in cards if r['id']!=CARD]
  old_target=next(x for x in old_cards if x['id']==CARD); target=next(x for x in cards if x['id']==CARD)
  assert all(target[k]==old_target[k] for k in target if k not in ('examples','custom_fields'))
  json_example=json.loads(target['examples'])
  cf=json.loads(target['custom_fields'])
  for seq in (json_example,cf['canonical_unit']['examples'],cf['presentation_examples']):
   only=[r for r in seq if r['id']==ITEM]
   assert len(only)==1 and only[0]['text']=='Ich habe die alte Rechnung weggeworfen.'
   assert [(v['lang'],v['text']) for v in only[0]['translations']]==[('fa-IR','فاکتور قدیمی را دور انداختم.'),('en-US',NEW)]
  old_r=json.loads(z.read(SRC+'REVIEW-DATA.json'))
  assert old_r['data_fingerprint']==PARENT_REVIEW and old_r['candidate_sha256']==PARENT_CAND
  review=copy.deepcopy(old_r)
  assert len(review['examples'])==1168 and len(review['synonyms'])==243
  hit=[x for x in review['examples'] if x['id']==ITEM]
  assert len(hit)==1 and hit[0]['en']==OLD
  old_fp=hit[0]['fingerprint'];hit[0]['en']=NEW
  hit[0]['fingerprint']=SHA(CANON({k:v for k,v in hit[0].items() if k!='fingerprint'}))
  new_fp=hit[0]['fingerprint']
  review['parent_zip_sha256']=PARENT_SHA
  review['candidate_sha256']=SHA(candidate)
  review['data_fingerprint']=SHA(CANON({'candidate_sha256':SHA(candidate),'items':[[x['id'],x['fingerprint']] for x in review['examples']+review['synonyms']]}))
  assert sum(x['fingerprint']!=y['fingerprint'] for x,y in zip(old_r['examples'],review['examples']))==1
  assert all(x['fingerprint']==y['fingerprint'] for x,y in zip(old_r['synonyms'],review['synonyms']))
  ex=readtab(z.read(SRC+'EXAMPLES-1168-INDEPENDENT-REVIEW.tsv'))
  row=[x for x in ex if x['example_id']==ITEM];assert len(row)==1 and row[0]['en']==OLD and row[0]['fingerprint']==old_fp
  row[0]['en']=NEW;row[0]['fingerprint']=new_fp
  exbytes=writetab(ex,list(ex[0]))
  synbytes=z.read(SRC+'SYNONYMS-243-INDEPENDENT-REVIEW.tsv');syn=readtab(synbytes)
  assert len(syn)==243 and all(x['independent_review_status']=='NOT_REVIEWED' for x in syn)
  assert {x['relation_id']:x['fingerprint'] for x in syn}=={x['id']:x['fingerprint'] for x in review['synonyms']}
  priority=readtab(z.read(SRC+'REVIEW-PRIORITY-1411-R62.tsv'))
  assert len(priority)==1411
  pr=[x for x in priority if x['item_id']==ITEM];assert len(pr)==1 and pr[0]['fingerprint']==old_fp
  pr[0]['fingerprint']=new_fp;pr[0]['qa_disposition']='R66_MODEL_EDITORIAL_EN_INVOICE_CORRECTION_NOT_EXPERT_SIGNOFF'
  prioritybytes=writetab(priority,list(priority[0]))
  html=z.read(SRC+'OFFLINE-REVIEW-WORKBENCH.html').decode()
  assert 'Independent Review R62' in html
  html=html.replace('Independent Review R62','Independent Review R66',1)
  pat=r'(<script id="payload" type="application/json">)(.*?)(</script>)'
  assert len(re.findall(pat,html,re.S))==1
  payload=json.dumps(review,ensure_ascii=False).replace('</','<\\/')
  html=re.sub(pat,lambda m:m.group(1)+payload+m.group(3),html,count=1,flags=re.S)
  assert json.loads(re.search(pat,html,re.S).group(2))==review
  gate=z.read(SRC+'VALIDATE_R62_REVIEW_EXPORT.py').decode()
  assert "EXPECTED_CANDIDATE_SHA = 'f6639703f9753afcfe84ee53ff0687b69281a557f681dcb5a0c1d85c9fff35e6'" in gate
  assert "EXPECTED_REVIEW_FINGERPRINT = 'b8f2c12484dac9b6f7143c76f9e48bebb2144f56818d38dd9d80d47c31339306'" in gate
  gate=gate.replace(PARENT_CAND,SHA(candidate)).replace(PARENT_REVIEW,review['data_fingerprint']).replace('R62','R66').replace('r62','r66')
  assert f"R66 = '{DST}'" not in gate
  gate=gate.replace("R66 = '92-Stage4-Verbessern-Optimieren-Scope-Rebind-R66/'",f"R66 = '{DST}'")
  assert f"R66 = '{DST}'" in gate
  tests=z.read(SRC+'TEST_R62_REVIEW_INTAKE.py').decode().replace('R62','R66').replace('r62','r66')
  # Ensure test harness binds the passed ZIP and doesn't invoke historical defaults.
  assert "root/'VALIDATE_R66_REVIEW_EXPORT.py'" in tests
  # Word sense scopes do not imply broad synonym interchangeability.
  notes={
   'ma2-lu-0085':{'risk':'LENDER_BORROWER_AMBIGUITY','decision':'EXPERT_CHECK_RECOMMENDED','why':'leihen, borgen and ausleihen each have lending and borrowing senses. English scope label "lending" is narrower than complete headword. Review role/argument frames and style/register.','sources':['https://www.duden.de/rechtschreibung/leihen','https://www.duden.de/rechtschreibung/borgen']},
   'ma2-lu-0049':{'risk':'FOOD_TASTING_FALSE_POSITIVE_GUARD','decision':'DO_NOT_AUTO_REJECT','why':'Duden lists "hast du den Kuchen ... schon versucht?" for versuchen, so food taste overlap is attested; naturalness varies.','sources':['https://www.duden.de/rechtschreibung/versuchen','https://www.duden.de/rechtschreibung/probieren']},
   'ma2-lu-0213':{'risk':'FOOD_TASTING_FALSE_POSITIVE_GUARD','decision':'DO_NOT_AUTO_REJECT','why':'The food-taste sense of versuchen/probieren is dictionary-attested and not automatically an error.','sources':['https://www.duden.de/rechtschreibung/versuchen','https://www.duden.de/rechtschreibung/probieren']},
   'ma2-lu-0216':{'risk':'SICH_ANHOEREN_TWO_CONSTRUCTIONS','decision':'SCOPE_CONTEXT_CHECK','why':'The synonym klingen applies to the sound/appear-to-the-ear sense, not to sich etwas anhoeren in the act-of-listening sense.','sources':['https://www.duden.de/rechtschreibung/anhoeren']},
   'ma2-lu-0172':{'risk':'SIGNIEREN_VS_UNTERSCHREIBEN','decision':'REGISTER_CHECK','why':'Signing artistic works vs signing documents, check register and object senses before broad approval.','sources':['https://www.duden.de/rechtschreibung/signieren']},
   'ma2-lu-0131':{'risk':'SOURCE_TRANSLATION_RECEIPT_INVOICE','decision':'CORRECTED_EN_R66_MODEL_NOT_EXPERT','why':'Rechnung is a bill/invoice, while Quittung indicates an acknowledgment/receipt. Persian was already فاکتور.','sources':['https://www.duden.de/rechtschreibung/Rechnung','https://www.duden.de/rechtschreibung/Quittung']},
   'ma2-lu-0252':{'risk':'SAVE_VS_BACKUP_CONTEXT','decision':'REVIEW_ONLY_NO_AUTO_EDIT','why':'Duden explicitly attests sichern in an IT sense as long-term storage; backup interpretation of data securing remains contextual.','sources':['https://www.duden.de/rechtschreibung/sichern']},
  }
  synledger=[]
  for x in syn:
   risklist=json.loads(x['risk_flags']) if x['risk_flags'] else []
   c=notes.get(x['card_id'],{})
   # Do not replace the original expert-review status or mutate the source-bound item.
   synledger.append({**x,'model_screen_kind':'SOURCE_BOUND_SCOPE_LENGTH_AND_CONTEXT_TRIAGE',
    'model_heuristic_short_scope':len(x['sense_scope'])<70,'source_risk_flags':risklist,
    'model_priority':c.get('risk','') or ('SOURCE_RISK_FLAGS' if risklist else 'SHORT_SCOPE_REVIEW' if len(x['sense_scope'])<70 else 'REGULAR_CONTEXT_REVIEW'),
    'model_note':c.get('why',''),'dictionary_support_for_note':c.get('sources',[]),'human_expert_signoff':False})
  assert len(synledger)==243 and len({x['relation_id'] for x in synledger})==243
  # static high-priority ledger is not a verdict or qualification proof
  attention={'schema':'ma2-r66-attention@1.0.0','review_data_fingerprint':review['data_fingerprint'],
   'content_change':{'item_id':ITEM,'card_id':CARD,'de':'Ich habe die alte Rechnung weggeworfen.',
    'fa':'فاکتور قدیمی را دور انداختم.','before_en':OLD,'after_en':NEW,'old_fingerprint':old_fp,'new_fingerprint':new_fp,
    'source_word_not_mutated':'Rechnung','status':'MODEL_EDITORIAL_CORRECTION_NOT_EXTERNAL_QUALIFIED_SIGNOFF'},
   'prior_language_issues':[{'item_id':'ma2-lu-0252-ex-004','status':'EXTERNAL_REVIEW_HOLD','note':'saved vs backed up contextual interpretation; no automatic change'}],
   'synonym_model_notes':[{'card_id':k,**v} for k,v in notes.items() if k not in (CARD,'ma2-lu-0252')],
   'all_243_synonyms_preserved_exactly':True,'qualified_approvals':0}
  checkpoint={'schema':'ma2-r66-scoped-translation-successor@1.0.0','milestone':'R66_RECHNUNG_INVOICE_EXAMPLE_TRANSLATION_AND_REVIEW_REBIND',
   'date':'2026-10-23','parent_r62_zip_sha256':PARENT_SHA,'candidate_sha256':SHA(candidate),
   'candidate_path':DST+'CANDIDATE-IMPORT-NOT-FINAL.tsv','data_fingerprint':review['data_fingerprint'],
   'review_data_fingerprint':review['data_fingerprint'],'cards':292,'examples':1168,'synonyms':243,'relations':1209,
   'changed_card_ids':[CARD],'changed_example_id':ITEM,'other_1167_example_fingerprints_unchanged':True,
   'unchanged_parent_members':1048,'independent_approvals':0,'independent_unreviewed':1411,
   'stage4':'BLOCKED_NOT_FINAL','stage5':'NOT_RUN','stage6':'NOT_RUN','stage7':'NOT_RUN',
   'import_authorized':False,'app_ui_changed':False,'source_attestation':'Duden supports lexical distinction; course screenshots and original German/Persian content preserved; model editorial change only'}
  evidence={'schema':'ma2-r66-bilingual-rechnung@1.0.0','parent_zip_sha256':PARENT_SHA,
   'card_id':CARD,'example_id':ITEM,'de':'Ich habe die alte Rechnung weggeworfen.',
   'fa':'فاکتور قدیمی را دور انداختم.','old_en':OLD,'new_en':NEW,
   'changed_exact_en_occurrences':3,'unchanged_card_rows':291,'synonyms_and_relation_ids_unchanged':True,
   'sources':['https://www.duden.de/rechtschreibung/Rechnung','https://www.duden.de/rechtschreibung/Quittung'],
   'provenance':'dictionary clarification, not independent qualified review or change to original course evidence'}
  readme='''# Menschen A2 Verben Stage4 R66 — invoice-translation repair\n\nSource: exact R62, SHA-256: `'''+PARENT_SHA+'''`.\n\nOne confirmed model-editorial translation correction: **Ich habe die alte Rechnung weggeworfen.** Persian **فاکتور قدیمی را دور انداختم.** remains. English **I threw away the old receipt.** was corrected to **I threw away the old invoice.** See Duden Rechnung/Quittung for different document roles.\n\nAll 1048 R62 members stay byte-exact. 292 cards, 1168 German/Persian texts, 243 synonyms and original source imagery unchanged. Exactly ONE English example item and its SHA-bound review fingerprint change. The offline reviewer and strict intake are rebound, older exports invalid. 0/1411 qualified external expert judgments. Stage4 remains BLOCKED; Stage5/6/7 not run; no import allowed.\n\nR66 also includes the mechanical and selected dictionary-grounded triage of all 243 source-bound synonym scope entries. It does NOT certify synonyms linguistically and does NOT mark them as human PASS.\n\nفارسی: تنها ترجمهٔ انگلیسی یک مثال تصحیح شده است. هیچ تأیید مستقلی صادر نشده و بسته مجوز ورود به اپلیکیشن نیست.\n'''
  additions={
  'CANDIDATE-IMPORT-NOT-FINAL.tsv':candidate,'REVIEW-DATA.json':JSON(review),
  'EXAMPLES-1168-INDEPENDENT-REVIEW.tsv':exbytes,'SYNONYMS-243-INDEPENDENT-REVIEW.tsv':synbytes,
  'REVIEW-PRIORITY-1411-R66.tsv':prioritybytes,'OFFLINE-REVIEW-WORKBENCH.html':html.encode(),
  'VALIDATE_R66_REVIEW_EXPORT.py':gate.encode(),'TEST_R66_REVIEW_INTAKE.py':tests.encode(),
  'SYNONYM-SCOPE-MODEL-TRIAGE-243.json':JSON(synledger),'REVIEW-ATTENTION-RECHNUNG-AND-SYNONYMS.json':JSON(attention),
  'SCOPED-EXAMPLE-CORRECTION-EVIDENCE.json':JSON(evidence),'CHECKPOINT.json':JSON(checkpoint),
  'README-FA-DE.md':readme.encode()
  }
  manifest={'schema':'ma2-r66-added-members-sha256@1.0.0','members':{DST+k:SHA(v) for k,v in additions.items()}}
  additions['ADDED-MANIFEST-SHA256.json']=JSON(manifest)
  shutil.copyfile(parent,out)
  with zipfile.ZipFile(out,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as w:
   for k,v in additions.items():
    info=zipfile.ZipInfo(DST+k,date_time=(2026,10,23,5,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=25165824;info.create_system=3
    w.writestr(info,v,compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
  with zipfile.ZipFile(out) as w:
   assert w.testzip() is None and len(w.namelist())==1048+len(additions)==len(set(w.namelist()))
   assert all(w.read(n)==z.read(n) for n in parent_names)
   assert all(w.read(DST+k)==v for k,v in additions.items())
  return {'parent_sha256':PARENT_SHA,'zip_sha256':SHA(out.read_bytes()),'size':out.stat().st_size,
    'members':1048+len(additions),'candidate_sha256':SHA(candidate),'review_fingerprint':review['data_fingerprint'],
    'old_example_fingerprint':old_fp,'new_example_fingerprint':new_fp,'changed_card':CARD,'changed_example':ITEM,
    'other_examples_unmodified':1167,'synonyms_unmodified':243,'synonym_triage_records':243,'added_members':len(additions)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('parent',type=pathlib.Path);p.add_argument('output',type=pathlib.Path);a=p.parse_args()
 print(json.dumps(build(a.parent,a.output),indent=2,ensure_ascii=False))
