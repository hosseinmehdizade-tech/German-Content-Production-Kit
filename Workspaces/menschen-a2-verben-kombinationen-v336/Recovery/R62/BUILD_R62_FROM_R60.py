#!/usr/bin/env python3
"""Exact-source-bound R62 successor of Menschen A2 Verben R60 (not an expert signoff).
Requires the exact R60 outer ZIP SHA and R61 candidate preview SHA. Creates a portable
content-only ZIP with all 1035 parent members preserved and a new independently bound
review workbench, review inventory, decision intake gate and scoped QA receipt.
"""
import csv, io, json, hashlib, zipfile, re, pathlib, copy, shutil, argparse
ROOT=pathlib.Path('/mnt/data')
R60_SHA='6a95c2b405f6fb425ffceb222bf2518092757fba49f0b440be163d5c60655337'
R61_PATCH_SHA='f6639703f9753afcfe84ee53ff0687b69281a557f681dcb5a0c1d85c9fff35e6'
SRC='91-Stage4-Origin-Training-Synonym-Scope-R60/'
DST='92-Stage4-Verbessern-Optimieren-Scope-Rebind-R62/'
TARGET='ma2-lu-0117'; RID='ma2-lu-0117-rel-v336-syn-001'
OLD='improve quality/performance'
NEW='Nur bei gezielter Verbesserung eines Prozesses, einer Methode, Qualität oder Leistung in Richtung eines möglichst günstigen/optimalen Zustands. verbessern ist allgemeiner und umfasst auch kleine Verbesserungen oder reine Fehlerkorrekturen (z. B. einen Rechtschreibfehler verbessern); optimieren ist dafür nicht pauschal austauschbar.'
H=lambda b:hashlib.sha256(b).hexdigest()
C=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
J=lambda x:(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
def tsvread(b):return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t'))
def tsvwrite(rows,headers):
 out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=headers,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return out.getvalue().encode('utf-8')

def build(parent,out):
 assert H(parent.read_bytes())==R60_SHA,'Unrecognized R60 parent ZIP'; assert not out.exists(),'Refusing overwrite'
 with zipfile.ZipFile(parent) as z:
  assert z.testzip() is None
  orig=z.namelist();assert len(orig)==1035==len(set(orig))
  original=z.read(SRC+'CANDIDATE-IMPORT-NOT-FINAL.tsv')
  parts=original.decode().splitlines(keepends=True)
  hits=[i for i,s in enumerate(parts) if s.startswith(TARGET+'\t')]
  assert len(hits)==1 and parts[hits[0]].count(OLD)==2
  parts[hits[0]]=parts[hits[0]].replace(OLD,NEW)
  candidate=''.join(parts).encode('utf-8')
  assert H(candidate)==R61_PATCH_SHA,'R61 proposed candidate differs'
  old_rows=tsvread(original);rows=tsvread(candidate)
  assert len(rows)==292 and len({r['id'] for r in rows})==292
  assert all(a==b for a,b in zip(old_rows,rows) if a['id']!=TARGET)
  orig_target=next(r for r in old_rows if r['id']==TARGET)
  new_target=next(r for r in rows if r['id']==TARGET)
  assert all(new_target[k]==orig_target[k] for k in orig_target if k!='custom_fields')
  fc=json.loads(new_target['custom_fields'])
  c=[x for x in fc['canonical_relations'] if x['relation_id']==RID];assert len(c)==1 and c[0]['value']['scope']==NEW and c[0]['value']['term']=='optimieren'
  v=[x for group in fc['vnext_relations'] if group['type']=='SYNONYM' for x in group['items'] if x['relation_id']==RID];assert len(v)==1 and v[0]['scope']==NEW
  old_review=json.loads(z.read(SRC+'REVIEW-DATA.json'));review=copy.deepcopy(old_review)
  assert len(review['examples'])==1168 and len(review['synonyms'])==243
  touched=[x for x in review['synonyms'] if x['id']==RID];assert len(touched)==1 and touched[0]['scope']==OLD
  touched[0]['scope']=NEW
  touched[0]['fingerprint']=H(C({k:v for k,v in touched[0].items() if k!='fingerprint'}))
  review['parent_zip_sha256']=R60_SHA
  review['candidate_sha256']=H(candidate)
  review['data_fingerprint']=H(C({'candidate_sha256':H(candidate),'items':[[x['id'],x['fingerprint']] for x in review['examples']+review['synonyms']]}))
  fp=review['data_fingerprint']
  assert all(x['fingerprint']==y['fingerprint'] for x,y in zip(old_review['examples'],review['examples']))
  assert sum(x['fingerprint']!=y['fingerprint'] for x,y in zip(old_review['synonyms'],review['synonyms']))==1
  syn=tsvread(z.read(SRC+'SYNONYMS-243-INDEPENDENT-REVIEW.tsv'))
  examples=z.read(SRC+'EXAMPLES-1168-INDEPENDENT-REVIEW.tsv')
  priority=tsvread(z.read(SRC+'REVIEW-PRIORITY-1411-R60.tsv'))
  s=[x for x in syn if x['relation_id']==RID];assert len(s)==1 and s[0]['sense_scope']==OLD
  s[0]['sense_scope']=NEW;s[0]['fingerprint']=touched[0]['fingerprint'];s[0]['independent_review_status']='NOT_REVIEWED';s[0]['independent_reviewer_note']=''
  rp=[x for x in priority if x['item_id']==RID];assert len(rp)==1
  rp[0]['fingerprint']=touched[0]['fingerprint'];rp[0]['qa_disposition']='R62_MODEL_EDITORIAL_SCOPE_CLARIFICATION_NOT_EXPERT_SIGNOFF'
  sybytes=tsvwrite(syn,list(syn[0]));pbytes=tsvwrite(priority,list(priority[0]))
  html=z.read(SRC+'OFFLINE-REVIEW-WORKBENCH.html').decode('utf-8')
  assert 'Independent Review R60' in html
  html=html.replace('Independent Review R60','Independent Review R62',1)
  pattern=r'(<script id="payload" type="application/json">)(.*?)(</script>)'
  assert len(re.findall(pattern,html,re.S))==1
  payload=json.dumps(review,ensure_ascii=False).replace('</','<\\/')
  html=re.sub(pattern,lambda m:m.group(1)+payload+m.group(3),html,count=1,flags=re.S)
  assert json.loads(re.search(pattern,html,re.S).group(2))==review
  intake=z.read(SRC+'VALIDATE_R60_REVIEW_EXPORT.py').decode('utf-8')
  assert "EXPECTED_CANDIDATE_SHA = '60bad9a382e1430bec1bf5dd700f83933db415e5b55eba451f4b13d734c8f877'" in intake
  assert "EXPECTED_REVIEW_FINGERPRINT = 'e1f81870781465be2623ffb6becbfb58ea58f25dcd2cf59c4746c578776fc9d4'" in intake
  intake=intake.replace("EXPECTED_CANDIDATE_SHA = '60bad9a382e1430bec1bf5dd700f83933db415e5b55eba451f4b13d734c8f877'",f"EXPECTED_CANDIDATE_SHA = '{H(candidate)}'")
  intake=intake.replace("EXPECTED_REVIEW_FINGERPRINT = 'e1f81870781465be2623ffb6becbfb58ea58f25dcd2cf59c4746c578776fc9d4'",f"EXPECTED_REVIEW_FINGERPRINT = '{fp}'")
  intake=intake.replace('R60','R62').replace('r60','r62').replace("R62 = '91-Stage4-Origin-Training-Synonym-Scope-R62/'",f"R62 = '{DST}'")
  assert f"R62 = '{DST}'" in intake and H(candidate) in intake and fp in intake
  test=z.read(SRC+'TEST_R60_REVIEW_INTAKE.py').decode('utf-8').replace('R60','R62').replace('r60','r62')
  check={'schema':'ma2-stage4-r62-content-wip@1.0.0','milestone':'R62_SCOPE_PARITY_AND_REVIEW_FINGERPRINT_REBIND','date':'2026-10-23','parent_r60_zip_sha256':R60_SHA,'candidate_sha256':H(candidate),'candidate_path':DST+'CANDIDATE-IMPORT-NOT-FINAL.tsv','data_fingerprint':fp,'review_data_fingerprint':fp,'cards':292,'examples':1168,'synonyms':243,'relations':1209,'changed_card_ids':[TARGET],'unchanged_parent_members':1035,'independent_approvals':0,'independent_unreviewed':1411,'stage4':'BLOCKED_NOT_FINAL','stage5':'NOT_RUN','stage6':'NOT_RUN','stage7':'NOT_RUN','import_authorized':False,'app_ui_changed':False,'source_attestation':'Course screenshots attest lexical entry and source listing; detailed restriction corroborated by dictionary, not independently expert certified'}
  evidence={'schema':'ma2-r62-lexical-scope@1','date':'2026-10-23','source_artifact_sha256':R60_SHA,'r61_preview_candidate_sha256':R61_PATCH_SHA,'card_id':TARGET,'relation_id':RID,'synonym':'optimieren','old_scope':OLD,'new_scope':NEW,'dictionary':['https://www.duden.de/rechtschreibung/verbessern','https://www.duden.de/rechtschreibung/optimieren'],'provenance_preserved':True,'candidate_rows_other_291_unchanged':True,'original_1168_examples_unchanged':True,'review_item_fingerprints_changed':1,'model_editorial_not_expert_signoff':True}
  readme=f'''# Menschen A2 Verben — Stage4 R62 full-content WIP\n\nR60 exact parent SHA-256: `{R60_SHA}`.\n\nR61 proposal was applied to card `{TARGET}` / synonym `{RID}` only. Two nested structural mirrors are now identical, without touching registered course-source provenance, all 1168 examples or other 291 cards. Total synonyms 243, relations 1209. All 1035 R60 ZIP members remain.\n\nOffline review dataset, HTML, priority TSV and strict review export validator rebound to the R62 candidate and new item fingerprint. Earlier exports must fail. 0/1411 external expert approvals. Stage4 BLOCKED; Stage5/6/7 not run; no import authorized.\n\nفارسی: این نسخه تنها اصلاح محدودهٔ معناییِ رابطه را تثبیت می‌کند و تأیید مستقل زبان‌شناسی محسوب نمی‌شود.\n'''
  additions={
   'CANDIDATE-IMPORT-NOT-FINAL.tsv':candidate,'REVIEW-DATA.json':J(review),'EXAMPLES-1168-INDEPENDENT-REVIEW.tsv':examples,'SYNONYMS-243-INDEPENDENT-REVIEW.tsv':sybytes,
   'REVIEW-PRIORITY-1411-R62.tsv':pbytes,'OFFLINE-REVIEW-WORKBENCH.html':html.encode(),'VALIDATE_R62_REVIEW_EXPORT.py':intake.encode(),'TEST_R62_REVIEW_INTAKE.py':test.encode(),
   'SCOPED-RELATION-CORRECTION-EVIDENCE.json':J(evidence),'R61-100-MODEL-REVIEW-LEDGER-SOURCE-REFERENCE.json':J({'source':'R61 report and ZIP','R61_sha256':'572f64ebb6859d498abf6fad532ad5155ea244437b560883749af737b055a254','model_screened_examples':100,'qualified_approvals':0,'note':'Original R61 auxiliary archive is not embedded to avoid duplication'}),'CHECKPOINT.json':J(check),'README-FA-DE.md':readme.encode(),
  }
  manifest={'schema':'ma2-r62-new-member-sha256@1','members':{DST+k:H(v) for k,v in additions.items()}}
  additions['ADDED-MANIFEST-SHA256.json']=J(manifest)
  shutil.copyfile(parent,out)
  with zipfile.ZipFile(out,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as w:
   for k,v in additions.items():
    info=zipfile.ZipInfo(DST+k,date_time=(2026,10,23,3,35,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=25165824
    info.create_system=3
    w.writestr(info,v,compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
  with zipfile.ZipFile(out) as q:
   assert q.testzip() is None
   assert len(q.namelist())==1035+len(additions)==len(set(q.namelist()))
   assert all(q.read(n)==z.read(n) for n in orig)
   assert all(q.read(DST+k)==v for k,v in additions.items())
   assert json.loads(q.read(DST+'REVIEW-DATA.json'))==review
   assert len(tsvread(q.read(DST+'EXAMPLES-1168-INDEPENDENT-REVIEW.tsv')))==1168
   assert len(tsvread(q.read(DST+'SYNONYMS-243-INDEPENDENT-REVIEW.tsv')))==243
  return{'parent_sha256':R60_SHA,'zip_sha256':H(out.read_bytes()),'size_bytes':out.stat().st_size,'members':1035+len(additions),'candidate_sha256':H(candidate),'review_fingerprint':fp,'old_item_fp':next(x['fingerprint'] for x in old_review['synonyms'] if x['id']==RID),'new_item_fp':touched[0]['fingerprint'],'changed_ids':[TARGET],'added_members':len(additions)}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('parent_zip',type=pathlib.Path);a.add_argument('out_zip',type=pathlib.Path);args=a.parse_args();print(json.dumps(build(args.parent_zip,args.out_zip),ensure_ascii=False,indent=2))
