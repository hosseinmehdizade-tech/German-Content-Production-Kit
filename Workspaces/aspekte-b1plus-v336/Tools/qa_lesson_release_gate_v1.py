#!/usr/bin/env python3
"""Fail-closed lesson release gate for curated Aspekte B1+ owner ZIPs.

This verifier intentionally cannot convert an editorial draft into a formal release.
It requires independently approved examples, evidence-scoped morphology,
explicit HOLD disposition, and an externally generated real app-import receipt.

Usage: python qa_lesson_release_gate_v1.py <owner.zip> --lesson L05 [--app-receipt verified.json] [--out report.json]
Exit: 0 only if ALL cards have formally approved flags AND genuine app receipt; 1 BLOCKED; 2 invalid input.
"""
import argparse,collections,json,zipfile,sys,hashlib
from pathlib import Path
PRE='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
def qa(zip_path,lesson,app_receipt_path=None):
 with zipfile.ZipFile(zip_path) as z:
  raw=z.read(PRE)
  cards=[json.loads(s) for s in raw.splitlines()]
  integrity=z.testzip()
 selected=[x for x in cards if x.get('lesson')==lesson]
 if not selected:raise ValueError('No cards for '+lesson)
 seen=set();rows=[];summary=collections.Counter()
 app_receipt=None
 if app_receipt_path:
  receipt=json.loads(Path(app_receipt_path).read_text(encoding='utf-8'))
  # Receipt must originate from actual application E2E, not QA-only renderer.
  if (receipt.get('application')=='German-Flashcards-Pro' and receipt.get('test_type')=='ACTUAL_RUNTIME_IMPORT_RENDER'
     and receipt.get('lesson')==lesson and receipt.get('verified') is True
     and receipt.get('imported_card_count')==len(selected)
     and receipt.get('owner_sha256')==hashlib.sha256(Path(zip_path).read_bytes()).hexdigest()):
   app_receipt=receipt
 for c in selected:
  cid=c.get('preview_card_id');f=c.get('front',{});b=c.get('back',{});issues=[]
  if cid in seen:issues.append('DUPLICATE_ID')
  seen.add(cid)
  if not f.get('morphology_independently_validated'):issues.append('FORM_NOT_INDEPENDENTLY_ATTESTED')
  if c.get('curated_HOLD_content_disposition_exists'):issues.append('INHERITED_HOLD_NOT_EXPLICITLY_RESOLVED')
  ex=(b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
  if not ex:issues.append('EXAMPLES_EMPTY')
  if any(not e.get('de') or not e.get('fa') for e in ex):issues.append('EMPTY_EXAMPLE_TRANSLATION')
  # Formal G4 release must be explicit and distinguish exact scope from editorial review.
  allowed_exact_statuses={'FULL_INDEPENDENT_G4_DE_FA_APPROVED'}
  if any(e.get('status') not in allowed_exact_statuses for e in ex):issues.append('EXAMPLE_TRANSLATION_INDEPENDENT_QA_NOT_COMPLETE')
  nets=b.get('semantic_network_sense_anchored_pending_qa') or []
  ids={n.get('sense_id') for n in nets}
  if nets and any(e.get('sense_id') not in ids for e in ex):issues.append('EXAMPLE_SENSE_ROUTING_INCOMPLETE_OR_AMBIGUOUS')
  if b.get('Formen_section') is not None:issues.append('REDUNDANT_BACK_FORMS')
  if not c.get('formal_release_approved') or not c.get('import_ready'):issues.append('FULL_CARD_APPROVAL_NOT_PRESENT')
  if not app_receipt:issues.append('REAL_APP_IMPORT_RENDER_RECEIPT_NOT_VERIFIED')
  for item in set(issues):summary[item]+=1
  rows.append({'source_ordinal':c.get('source_ordinal'),'id':cid,'release':'BLOCKED' if issues else 'APPROVED','blockers':issues})
 return {'schema':'aspekte-b1plus-lesson-release-gate@1','lesson':lesson,'selected_cards':len(selected),
         'all_card_ids_unique':len(seen)==len(selected),'zip_crc_pass':integrity is None,
         'verified_app_runtime_receipt':app_receipt is not None,'blocker_counts_by_card':dict(summary),
         'release_allowed':not any(r['blockers'] for r in rows),'card_decisions':rows,
         'warning':'The app receipt must be independently produced by real runtime; this script does not perform the app test.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('owner');p.add_argument('--lesson',default='L05');p.add_argument('--app-receipt');p.add_argument('--out');a=p.parse_args()
 try:r=qa(a.owner,a.lesson,a.app_receipt)
 except (KeyError,ValueError,zipfile.BadZipFile) as ex: print(str(ex),file=sys.stderr);return 2
 text=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
 if a.out:Path(a.out).write_text(text,encoding='utf-8')
 print(json.dumps({k:v for k,v in r.items() if k!='card_decisions'},ensure_ascii=False,indent=2))
 return 0 if r['release_allowed'] else 1
if __name__=='__main__':sys.exit(main())