#!/usr/bin/env python3
import zipfile,io,csv,json,tempfile,hashlib,sys,os
from pathlib import Path
from VERIFY_R83_SOURCE_PERFEKT import inspect
SOURCE=Path('/mnt/data/a2-verben-review/Menschen-A2-Verben-R83-Integrated-Stage4-WIP-Reviewer-NOT-FINAL.zip')
OUTER='a0b2f5029fefdf147262f4af7d68873430fea1192960b54d340b351c8198afe3'
with zipfile.ZipFile(SOURCE) as z:
 data={n:z.read(n) for n in z.namelist()}
tsv_name=next(n for n in data if n.endswith('CURRENT-STAGE4-CANDIDATE-NOT-FINAL.tsv'))
idx_name=next(n for n in data if n.endswith('SOURCE-EVIDENCE-AND-REVIEW-INDEX.json'))
passes=[]

def should_fail(label,mods=None,expected_sha=None):
    d={**data,**(mods or {})}
    with tempfile.NamedTemporaryFile(suffix='.zip') as f:
      with zipfile.ZipFile(f.name,'w',compression=zipfile.ZIP_DEFLATED) as out:
       for n,b in d.items():out.writestr(n,b)
      try:inspect(f.name,expected_sha)
      except Exception as e:passes.append((label,'PASS',str(e)[:100]));return
      raise AssertionError(label+' unexpectedly accepted')

def index_mut(fn):
 idx=json.loads(data[idx_name]);fn(idx);return {idx_name:json.dumps(idx,ensure_ascii=False).encode()}

pass_0=inspect(SOURCE,OUTER)
passes.append(('original_exact_SHA','PASS',pass_0['status']))
should_fail('wrong_outer_sha',expected_sha='0'*64)
should_fail('candidate_sha_tamper',index_mut(lambda j:j['authority'].update(active_candidate_sha256='0'*64)))

def source_change(j):
 c=next(c for c in j['cards'] if c['card_id']=='ma2-lu-0010')
 for e in c['source_entries']:e['raw_text']=e['raw_text'].replace('hat verkauft','ist verkauft')
should_fail('unexpected_source_aux_change',index_mut(source_change))

def exception_change(j):
 c=next(c for c in j['cards'] if c['card_id']=='ma2-lu-0297')
 for e in c['source_entries']:e['raw_text']=e['raw_text'].replace('hat ausgerastet','ist ausgerastet')
should_fail('exception_unexpected_change',index_mut(exception_change))

def source_ablation(j):
 c=next(c for c in j['cards'] if c['card_id']=='ma2-lu-0297')
 for e in c['source_entries']:e['row_index']=8
should_fail('exception_locator_change',index_mut(source_ablation))

def source_missing(j):
 j['cards']=[c for c in j['cards'] if c['card_id']!='ma2-lu-0197']
should_fail('source_missing_card',index_mut(source_missing))
result={'test_count':len(passes),'tests':passes,'valid_positive':1,'negative_rejected':len(passes)-1,'parent_original_sha256':OUTER,'scope':'source morphology parser only, no independent linguistic signoff'}
p=Path('/mnt/data/a2-verben-review/r84-verification/R84-NEGATIVE-TEST-RESULTS.json');p.write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
