#!/usr/bin/env python3
"""Rebuild finalized L06 Phase3 owner from locally tested Phase3 candidate + v4 global gate.

Re-run build_L06_phase3_v1.py to generate initial owner, then add new v4 gate,
run it expecting 3 global cases outside L06, and finalize report+manifest here.
Does not alter any primary-card learner-data object after the 5 scoped v1 changes.
"""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path('/mnt/data/aspekte_b1plus_l06')
DIR=ROOT/'phase3'
BASE=ROOT/'Aspekte-B1plus-L06-PHASE3-177-CARD-STRICT-GATE-AND-LANGUAGE-FIXES-NONIMPORT-20261109-REGRESSION-GATE-v4.zip'
FINAL=ROOT/'Aspekte-B1plus-L06-PHASE3-FINAL-177-CARD-RELEASE-BLOCKED-NONIMPORT-20261109.zip'
REPORT=DIR/'L06-PHASE3-V4-GLOBAL-COMBINATIONS-CANDIDATES.json'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
def sha(b):return hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(BASE) as z:
 assert z.testzip() is None
 src={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
 old_main=z.read(MAIN)
r=json.loads(REPORT.read_text(encoding='utf-8'))
assert r['combinations_scanned']==722 and r['possible_full_sentence_collocations']==3 and not r['strict_corpus_pass']
assert {x['lesson'] for x in r['issues']}=={'L02','L03','L09'}
src['Lessons/L06/L06-PHASE3-V4-GLOBAL-FINITE-CLAUSE-GATE.json']=REPORT.read_bytes()
src['Tools/build_L06_phase3_v4_finalize.py']=Path(__file__).read_bytes()
manifest=''.join(sha(v)+'  '+k+'\n' for k,v in sorted(src.items()))
with zipfile.ZipFile(FINAL,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for k,v in src.items():z.writestr(k,v)
 z.writestr('SHA256SUMS.txt',manifest.encode())
with zipfile.ZipFile(FINAL) as z:
 assert z.testzip() is None
 assert z.read(MAIN)==old_main
 contained={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
 files={line.split('  ',1)[1]:line.split('  ',1)[0] for line in z.read('SHA256SUMS.txt').decode().splitlines()}
 assert files.keys()==contained.keys() and all(sha(v)==files[n] for n,v in contained.items())
 assert len(contained)==250
final={'owner_sha256':sha(FINAL.read_bytes()),'owner_bytes':FINAL.stat().st_size,'zip_members':251,
 'verified_manifest_members':250,'zip_crc_pass':True,'primary_card_member_sha256':sha(old_main),
 'structural_gate_v4_corpus':'FAIL_3_UNPUNCTUATED_FULL_SENTENCES_OUTSIDE_L06',
 'structural_gate_v4_L06':'PASS_0_REMAINING',
 'app_import_tested':False,'learner_release_allowed':False}
(DIR/'L06-PHASE3-FINAL-OWNER-RECEIPT-LOCAL.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(final,ensure_ascii=False,indent=2))
