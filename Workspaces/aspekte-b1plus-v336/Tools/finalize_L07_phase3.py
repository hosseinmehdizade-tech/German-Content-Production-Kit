#!/usr/bin/env python3
"""Finalize L07 Phase3 with actual independent gate outputs, without altering learner data."""
import collections,csv,hashlib,io,json,zipfile
from pathlib import Path
BASE=Path('/mnt/data/aspekte_b1plus_l07_phase3')
PRE=BASE/'Aspekte-B1plus-L07-PHASE3-154-CARDS-STRICT-QA-BLOCKED-NONIMPORT-20261109.zip'
FINAL=BASE/'Aspekte-B1plus-L07-PHASE3-FINAL-154-CARD-RELEASE-BLOCKED-NONIMPORT-20261109.zip'
MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
def sha(b):return hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(PRE) as z:
 assert z.testzip() is None
 a={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
parent_main_sha=sha(a[MAIN]);parent_map_sha=sha(a[MAP])
for ext,dst in [
 ('L07-PHASE3-STRICT-RELEASE-GATE-RAW.json','Lessons/L07/L07-PHASE3-INDEPENDENT-154-CARD-RELEASE-GATE.json'),
 ('L07-PHASE3-V4-FINITE-CLAUSE-REPORT.json','Lessons/L07/L07-PHASE3-GLOBAL-FINITE-CLAUSE-GATE-v4.json')]:
 a[dst]=(BASE/ext).read_bytes()
a['Tools/finalize_L07_phase3.py']=Path(__file__).read_bytes()
a['SHA256SUMS.txt']=''.join(sha(v)+'  '+n+'\n' for n,v in sorted(a.items())).encode()
with zipfile.ZipFile(FINAL,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for n,v in sorted(a.items()):z.writestr(n,v)
with zipfile.ZipFile(FINAL) as z:
 assert z.testzip() is None
 b={n:z.read(n) for n in z.namelist() if n!='SHA256SUMS.txt'}
 manifest=dict((n,h) for h,n in (x.split('  ',1) for x in z.read('SHA256SUMS.txt').decode().splitlines()))
 assert set(b)==set(manifest) and all(sha(b[n])==manifest[n] for n in b)
 assert sha(b[MAIN])==parent_main_sha
 assert sha(b[MAP])==parent_map_sha
 cards=[json.loads(x) for x in b[MAIN].splitlines()];l=[x for x in cards if x['lesson']=='L07']
 assert len(cards)==1571 and len(l)==154
 assert len(set(x['preview_card_id'] for x in cards))==len(cards)
 assert sum(len(x['back'].get(k) or []) for x in l for k in ('existing_examples_de_fa_pending_qa','additional_examples_de_fa_pending_qa'))==351
 assert len([x for x in l if x['front'].get('morphology_independently_validated')])==10
 htmls=b['Lessons/L07/L07-PHASE3-154-CARD-QA-ONLY.html'].decode()
 assert htmls.count('<article>')==154 and htmls.count('<small>pending / ')==351
 tsv=b['Lessons/L07/L07-PHASE3-154-CARD-OFFLINE-TSV-QA-ONLY.tsv'].decode('utf-8-sig')
 assert len(list(csv.DictReader(io.StringIO(tsv),delimiter='\t')))==154
 rel=json.loads(b['Lessons/L07/L07-PHASE3-INDEPENDENT-154-CARD-RELEASE-GATE.json']);assert rel['selected_cards']==154 and not rel['release_allowed']
 assert rel['blocker_counts_by_card']['FORM_NOT_INDEPENDENTLY_ATTESTED']==144
 assert rel['blocker_counts_by_card']['INHERITED_HOLD_NOT_EXPLICITLY_RESOLVED']==38
 glob=json.loads(b['Lessons/L07/L07-PHASE3-GLOBAL-FINITE-CLAUSE-GATE-v4.json'])
 assert glob['possible_full_sentence_collocations']==3 and not glob['strict_corpus_pass']
 print(json.dumps({'file':str(FINAL),'sha256':sha(FINAL.read_bytes()),'bytes':FINAL.stat().st_size,
                   'zip_members':len(z.namelist()),'manifest_verified':len(manifest),
                   'primary_sha256':parent_main_sha,'source_map_sha256':parent_map_sha,
                   'lesson_cards':len(l),'example_pairs':351,'scope_attestations':10,
                   'release_blocked':154,'legacy_global_finite_clause_findings':3,
                   'offline_html_tsv_verified':True,'CRC':'PASS'},ensure_ascii=False,indent=2))
