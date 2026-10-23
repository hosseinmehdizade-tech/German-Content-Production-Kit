#!/usr/bin/env python3
"""R74 strict, no-auto-signoff supplemental adjudication validator (safe under python -O)."""
import argparse,hashlib,json
from pathlib import Path
from BUILD_R74_SUPPLEMENT import fetch,canonical,H,SRC_SHA,R70_SHA,CAN_SHA,REVIEW_FINGERPRINT,ensure
VALID={'NOT_REVIEWED','SCOPED_SYNONYM','KEEP_RELATED_REMOVE_SYNONYM_DISPLAY','REMOVE_FROM_SYNONYM_DISPLAY','NEEDS_CORRECTION','UNSURE'}
def original_match(src,workspace,datafile):
 expected=fetch(src,workspace); actual=json.loads(Path(datafile).read_text('utf-8'))
 ensure(actual.get('source_r66_sha256')==SRC_SHA,'WRONG_SOURCE_ID')
 ensure(actual.get('source_r70_sha256')==R70_SHA,'WRONG_WORKSPACE_ID')
 ensure(actual.get('candidate_sha256')==CAN_SHA and actual.get('source_review_fingerprint')==REVIEW_FINGERPRINT,'WRONG_R66_VERSION')
 ensure(actual.get('source_1411_review_count')==1411 and actual.get('supplement_items')==12,'REVIEW_UNIVERSE_MISMATCH')
 ensure(actual.get('items')==expected,'SUPPLEMENT_TAMPER_OR_STALE')
 fingerprint=H(canonical([{k:v for k,v in i.items() if k!='fingerprint'} for i in expected]))
 ensure(actual.get('supplement_fingerprint')==fingerprint,'SUPPLEMENT_FINGERPRINT_MISMATCH')
 ensure(actual.get('final_stage4') is False,'FALSE_STAGE4_SIGNOFF')
 return actual

def validate(src,workspace,datafile,exportfile,reportfile=None):
 d=original_match(src,workspace,datafile);e=json.loads(Path(exportfile).read_text('utf-8'))
 ensure(e.get('schema')=='ma2-r74-extra-visible-synonym-decisions@1.0.0','BAD_EXPORT_SCHEMA')
 ensure(e.get('source_r66_sha256')==SRC_SHA and e.get('source_candidate_sha256')==CAN_SHA,'BAD_EXPORT_PARENT_SHA')
 ensure(e.get('source_review_fingerprint')==REVIEW_FINGERPRINT and e.get('supplement_fingerprint')==d['supplement_fingerprint'],'BAD_EXPORT_REVIEW_FINGERPRINT')
 rv=e.get('reviewer');ensure(isinstance(rv,dict),'REVIEWER_MISSING')
 ensure(len(str(rv.get('reviewer_id','')).strip())>=3 and len(str(rv.get('qualification_claim','')).strip())>=6,'REVIEWER_DECLARATION_MISSING')
 ensure(rv.get('independent_attestation') is True and rv.get('qualification_external_verified') is False,'REVIEWER_FIELD_INVALID_OR_PRETEND_VERIFIED')
 ds=e.get('decisions');ensure(isinstance(ds,list) and len(ds)==12,'REQUIRE_EXPLICIT_12_DECISIONS')
 idmap={x['id']:x for x in d['items']};seen=set();counts={i:0 for i in sorted(VALID)}
 for x in ds:
  ensure(isinstance(x,dict),'MALFORMED_DECISION');id=x.get('item_id');ensure(id in idmap and id not in seen,'UNKNOWN_OR_DUPLICATE_ID');seen.add(id)
  ensure(x.get('item_fingerprint')==idmap[id]['fingerprint'],'STALE_OR_TAMPERED_ITEM_FINGERPRINT')
  dec=x.get('decision');ensure(dec in VALID,'BAD_DECISION');counts[dec]+=1
  rationale=x.get('rationale','');ensure(isinstance(rationale,str),'NON_TEXT_REASON')
  scope=x.get('proposed_scope','');ensure(isinstance(scope,str),'NON_TEXT_SCOPE')
  if dec!='NOT_REVIEWED':ensure(len(rationale.strip())>=15,'MISSING_REASON '+id)
  if dec=='SCOPED_SYNONYM':ensure(len(scope.strip())>=15,'MISSING_SCOPE '+id)
  if dec=='KEEP_RELATED_REMOVE_SYNONYM_DISPLAY':ensure(idmap[id]['relation_status']=='RELATED_ONLY','CANNOT_KEEP_NONEXISTENT_RELATED '+id)
 ensure(seen==set(idmap),'DECISION_ID_SET_MISMATCH')
 report={'schema':'ma2-r74-review-export-structure-validation@1.0.0','structural_validation':'PASS','item_count':len(ds),'reviewer_claim_id':rv['reviewer_id'],'decision_counts':counts,'total_decisions_not_default':12-counts['NOT_REVIEWED'],'source_r66_sha256':SRC_SHA,'supplement_fingerprint':d['supplement_fingerprint'],'human_qualification_verified':False,'independence_verified':False,'qualified_review_approvals_counted':0,'stage4_complete':False,'stage5_authorized':False,'import_authorized':False,'warning':'Structural JSON validity is not linguistic signoff. All content dispositions require independent qualified human authentication.'}
 if reportfile:Path(reportfile).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return report

def selftest(src,workspace,datafile):
 d=original_match(src,workspace,datafile);tests=[]
 payload={'schema':'ma2-r74-extra-visible-synonym-decisions@1.0.0','source_r66_sha256':SRC_SHA,'source_candidate_sha256':CAN_SHA,'source_review_fingerprint':REVIEW_FINGERPRINT,'supplement_fingerprint':d['supplement_fingerprint'],'reviewer':{'reviewer_id':'TEST-EXTERNAL-01','qualification_claim':'TEST ONLY - NOT A REAL REVIEWER','independent_attestation':True,'qualification_external_verified':False},'decisions':[{'item_id':x['id'],'item_fingerprint':x['fingerprint'],'decision':'NOT_REVIEWED','proposed_scope':'','rationale':''} for x in d['items']]}
 from tempfile import TemporaryDirectory
 with TemporaryDirectory() as td:
  f=Path(td)/'export.json';f.write_text(json.dumps(payload),encoding='utf-8'); validate(src,workspace,datafile,f);tests.append('valid_sample_structural_only')
  def reject(label,mutation):
   clone=json.loads(json.dumps(payload));mutation(clone);f.write_text(json.dumps(clone),encoding='utf-8')
   try:validate(src,workspace,datafile,f)
   except (ValueError,KeyError,TypeError):tests.append(label);return
   raise ValueError('SELFTEST_WRONGLY_ACCEPTED_'+label)
  reject('bad_parent',lambda x:x.update(source_r66_sha256='0'*64))
  reject('bad_supplement_fingerprint',lambda x:x.update(supplement_fingerprint='0'*64))
  reject('duplicate_id',lambda x:x['decisions'][1].update(item_id=x['decisions'][0]['item_id']))
  reject('tamper_item_hash',lambda x:x['decisions'][0].update(item_fingerprint='0'*64))
  reject('fake_qualification',lambda x:x['reviewer'].update(qualification_claim=''))
  reject('claim_external_verification',lambda x:x['reviewer'].update(qualification_external_verified=True))
  reject('attestation_missing',lambda x:x['reviewer'].update(independent_attestation=False))
  reject('bad_status',lambda x:x['decisions'][0].update(decision='EXPERT_PASS'))
  reject('silent_scope_approval',lambda x:x['decisions'][0].update(decision='SCOPED_SYNONYM'))
  reject('impossible_keep_related',lambda x:(x['decisions'][0].update(decision='KEEP_RELATED_REMOVE_SYNONYM_DISPLAY',rationale='This is a long technical justification.')))
  reject('short_reason',lambda x:x['decisions'][0].update(decision='UNSURE',rationale='short'))
  reject('missing_decision',lambda x:x['decisions'].pop())
  reject('repeated_item',lambda x:x['decisions'].append(x['decisions'][0]))
 print(json.dumps({'tests_passed':len(tests),'test_names':tests,'source_r66_sha256':SRC_SHA,'external_review_recorded':0,'stage4':False}))
if __name__=='__main__':
 p=argparse.ArgumentParser();q=p.add_subparsers(dest='command',required=True)
 for name in ('selftest','validate'):
  z=q.add_parser(name);z.add_argument('--source',required=True);z.add_argument('--workspace',required=True);z.add_argument('--data',required=True)
  if name=='validate':z.add_argument('--export',required=True);z.add_argument('--report')
 a=p.parse_args()
 if a.command=='selftest':selftest(a.source,a.workspace,a.data)
 else:print(json.dumps(validate(a.source,a.workspace,a.data,a.export,a.report),ensure_ascii=False,indent=2))
