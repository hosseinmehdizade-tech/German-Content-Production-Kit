#!/usr/bin/env python3
"""Independent deterministic structural + negative mutation tests for P1 scoped HOLD owner.
No language truth claims; supports exact Library byte-readback verification.
"""
import copy,hashlib,json,pathlib,zipfile,collections,sys
R=pathlib.Path(__file__).resolve().parent
PARENT=R/'Aspekte-B1plus-GLOBAL-HOLD-GATE02-359-CASE-PRIORITY-REPAIRS-NONIMPORT-20261110.zip'
NEW=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else R/'Aspekte-B1plus-P1-SCOPED-131-HOLD-RESOLUTION-CURATED-NONIMPORT-20261110.zip'
P1='Global-Backlog/P1-HOLD-FOLLOWUP/'
def sha(b):return hashlib.sha256(b).hexdigest()
def check(condition,label):
 if not condition:raise AssertionError(label)
def load(path):
 with zipfile.ZipFile(path) as z:
  files={p:z.read(p) for p in z.namelist()}
  check(z.testzip() is None,'ZIP_CRC')
  manifests={p:h for h,p in (row.split('  ',1) for row in files['SHA256SUMS.txt'].decode().splitlines())}
  check(set(manifests)==set(files)-{'SHA256SUMS.txt'},'MANIFEST_COMPLETE')
  check(all(sha(files[p])==h for p,h in manifests.items()),'MEMBER_SHA_MATCH')
  return files
parent=load(PARENT);child=load(NEW)
check(sha(PARENT.read_bytes())=='0d4f4716c2df5df5670c5262d28ed73cf0c9fdb01fd868e4dbb27d8690583d2e','PARENT_PIN')
pc=next(x for x in parent if '1571-FRONT-BACK' in x)
mp=next(x for x in parent if x.endswith('1548-SOURCE-MAP-UNMODIFIED.tsv'))
check(parent[mp]==child[mp] and sha(parent[mp])=='c8177816bc27004ca574f0011a03a880e4aa6505487847dc28a2af43afa09882','SOURCE_MAP_IDENTICAL')
oldlines=parent[pc].decode().splitlines();newlines=child[pc].decode().splitlines()
a=[json.loads(x) for x in oldlines];b=[json.loads(x) for x in newlines]
check(len(a)==len(b)==1571 and len({x['preview_card_id'] for x in b})==1571,'CARD_IDENTITY')
check([x['preview_card_id'] for x in a]==[x['preview_card_id'] for x in b],'EXACT_ORDER_IDENTICAL')
changed=[(x,y) for x,y in zip(a,b) if x!=y]
changed_id={y['preview_card_id'] for x,y in changed}
check(len(changed)==58,'58_CHANGED_CARD_OBJECTS')
check(all(oldlines[i]==newlines[i] for i,(x,y) in enumerate(zip(a,b)) if x==y),'ALL_UNCHANGED_CARD_LINES_EXACT_BYTES')
check(sum(c['curated_HOLD_content_disposition_exists'] for c in a)==351,'PARENT_HOLDS_351')
check(sum(c['curated_HOLD_content_disposition_exists'] for c in b)==303,'CURRENT_HOLDS_303')
check(len([1 for x,y in changed if x['curated_HOLD_content_disposition_exists'] and not y['curated_HOLD_content_disposition_exists']])==48,'EXACT_48_CASE_CLOSURES')
check(all(y['formal_release_approved'] is False and y['import_ready'] is False for y in b),'NO_RELEASE_APPROVAL')
q=[json.loads(x) for x in child[P1+'P1-131-CASE-DECISION-LEDGER.jsonl'].decode().splitlines()]
closures=json.loads(child[P1+'P1-48-SCOPED-CLOSURES.json'])
actions=json.loads(child[P1+'P1-11-LINGUISTIC-EDITORIAL-REPAIRS.json'])
changes=json.loads(child[P1+'P1-ALL-CHANGED-CARDS-FULL-BEFORE-AFTER.json'])
report=json.loads(child[P1+'P1-WHOLE-CORPUS-QA-REPORT.json'])
check(len(q)==131 and len({r['card_id'] for r in q})==131,'131_P1_CASES')
check(len(closures)==48 and len({x['card_id'] for x in closures})==48,'48_SCOPED_CLOSURES')
check(len(actions)==11 and len(changes)==58,'11_EDITS_58_AB_CHANGES')
check({x['card_id'] for x in changes}==changed_id,'BEFORE_AFTER_IDS_IDENTICAL')
check(all(any(x['card_id']==id and x['old']==old and x['new']==new for x in changes) for old,new in changed for id in [new['preview_card_id']]),'BEFORE_AFTER_OBJECTS_EXACT')
check(report['new_primary_SHA256']==sha(child[pc]),'PRIMARY_SHA_IN_REPORT')
check(all(x['HOLD_before'] is True for x in q) and sum(not x['HOLD_after'] for x in q)==48,'QUEUE_STATUS_EXACT')
check(all(x['formal_release_approved'] is False and x['import_ready'] is False for x in b),'RELEASE_LOCKS')
def examples(c):return c['back'].get('existing_examples_de_fa_pending_qa',[])+c['back'].get('additional_examples_de_fa_pending_qa',[])
old_ex=sum(len(examples(c)) for c in a);new_ex=sum(len(examples(c)) for c in b)
check(old_ex==3526 and new_ex==3539,'EXAMPLE_COUNTS_3526_TO_3539')
check(all(set((s['sense_id'] for s in c['back'].get('semantic_network_sense_anchored_pending_qa',[]))).issuperset({e['sense_id'] for e in examples(c) if e.get('sense_id')}) for c in b),'SENSE_ROUTES')
for x,y in zip(a,b):
 ori={(e['de'],e['fa']) for e in examples(x)}
 now={(e['de'],e['fa']) for e in examples(y)}
 check(ori.issubset(now),'EXISTING_DE_FA_RETAINED:'+y['preview_card_id'])
check(all(c['global_HOLD_resolution'].get('formal_release_approved',False) is False for c in b if c.get('global_HOLD_resolution')),'SCOPED_NOT_RELEASE')
for key in [('L10',1487,'das Hochwasser'),('L09',1162,'die Pension')]:
 hits=[x for x in b if (x['lesson'],x['source_ordinal'],x['front']['base_headword_de'])==key]
 check(len(hits)==1 and hits[0]['curated_HOLD_content_disposition_exists'],'KEEP_NEW_SENSE_PENDING_HOLD')
check(sum(x['lesson']=='L01' for x in b)==sum(x['lesson']=='L01' for x in a),'DONT_DROP_LESSONS')
# Adversarial mutations: these MUST be rejected by relevant invariants.
checks=[]
def reject(label,mutator,valid):
 v=copy.deepcopy(b);mutator(v)
 try:assert valid(v),label
 except AssertionError:checks.append({'name':label,'correctly_rejected':True})
 else:raise AssertionError('NEGATIVE_DID_NOT_REJECT:'+label)
reject('duplicated_card_ID',lambda v:v[1].update(preview_card_id=v[0]['preview_card_id']),lambda v:len(set(x['preview_card_id'] for x in v))==1571)
reject('lost_card',lambda v:v.pop(),lambda v:len(v)==1571)
reject('unauthorized_import_approval',lambda v:v[0].update(import_ready=True),lambda v:all(x['import_ready'] is False for x in v))
reject('unverified_formal_release',lambda v:v[0].update(formal_release_approved=True),lambda v:all(x['formal_release_approved'] is False for x in v))
reject('lost_bilingual_example',lambda v:next(x for x in v if x['preview_card_id']=='AB1P-EFFECTIVE-QA-PASS02-0410')['back']['existing_examples_de_fa_pending_qa'].clear(),lambda v:sum(len(examples(x)) for x in v)==3539)
reject('invalid_sense_id',lambda v:next(x for x in v if x['preview_card_id']=='AB1P-EFFECTIVE-QA-PASS02-0410')['back']['additional_examples_de_fa_pending_qa'][-1].update(sense_id='UNKNOWN'),lambda v:all({e['sense_id'] for e in examples(x) if e.get('sense_id')}.issubset({s['sense_id'] for s in x['back'].get('semantic_network_sense_anchored_pending_qa',[])}) for x in v))
reject('reopen_closed_HOLD',lambda v:next(x for x in v if x['preview_card_id']==closures[0]['card_id']).update(curated_HOLD_content_disposition_exists=True),lambda v:sum(x['curated_HOLD_content_disposition_exists'] for x in v)==303)
reject('blank_new_Persian_example',lambda v:next(x for x in v if x['preview_card_id']=='AB1P-EFFECTIVE-QA-PASS02-0410')['back']['additional_examples_de_fa_pending_qa'][-1].update(fa=''),lambda v:all(e['de'].strip() and e['fa'].strip() for x in v for e in examples(x)))
reject('wrong_new_example_QA_status',lambda v:next(x for x in v if x['preview_card_id']=='AB1P-EFFECTIVE-QA-PASS02-0410')['back']['additional_examples_de_fa_pending_qa'][-1].update(status='PASS'),lambda v:all(e['status'].startswith('PENDING') for x in v for e in examples(x) if e.get('provenance')=='P1_CASE_SPECIFIC_BILINGUAL_EDITORIAL_20261110'))
reject('shared_source_example_clone',lambda v:next(x for x in v if x['preview_card_id']=='AB1P-G1-0002-02')['back']['additional_examples_de_fa_pending_qa'][0].update(de='Nach vielen Jahren kehrte sie in ihre Heimat zurück.'),lambda v:not any(e['de']=='Nach vielen Jahren kehrte sie in ihre Heimat zurück.' for x in v if x['preview_card_id']=='AB1P-G1-0002-02' for e in examples(x)))
reject('romantisch_wrong_routing',lambda v:next(x for x in v if x['preview_card_id']=='AB1P-EFFECTIVE-QA-PASS02-1538')['back']['existing_examples_de_fa_pending_qa'][-1].update(sense_id='AB1P-EFFECTIVE-QA-PASS02-1538:L10P2:S1'),lambda v:next(x for x in v if x['preview_card_id']=='AB1P-EFFECTIVE-QA-PASS02-1538')['back']['existing_examples_de_fa_pending_qa'][-1]['sense_id'].endswith('P1:S2'))
check(len(checks)==11,'ALL_11_MUTATIONS')
res={'status':'PASS','verified_zip_sha256':sha(NEW.read_bytes()),'verified_primary_sha256':sha(child[pc]),'parent_zip_sha256':sha(PARENT.read_bytes()),'original_map_sha256':sha(child[mp]),'zip_members':len(child),'zip_manifest_entries':len(child)-1,'cards':len(b),'actual_changed_card_objects':len(changed),'unchanged_card_raw_lines':1571-len(changed),'P1_cases':len(q),'P1_scoped_HOLD_closed':len(closures),'P1_remaining':83,'remaining_total_HOLD':303,'new_bilingual_examples':new_ex-old_ex,'test_cases':checks,'synthetic_negative_tests_passed':len(checks),'real_importer_tested':False,'full_bilingual_semantic_signoff':False,'release':'RELEASE_BLOCKED_NONIMPORT'}
(R/'P1-INDEPENDENT-STRUCTURAL-VERIFICATION.json').write_text(json.dumps(res,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:res[k] for k in ('status','verified_zip_sha256','verified_primary_sha256','actual_changed_card_objects','P1_scoped_HOLD_closed','P1_remaining','remaining_total_HOLD','synthetic_negative_tests_passed')},indent=2))
