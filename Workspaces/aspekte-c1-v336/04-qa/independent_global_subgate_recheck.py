#!/usr/bin/env python3
"""Independent read-only verifier for Aspekte C1 global lower-source subgate; no releases."""
from pathlib import Path
from collections import Counter, defaultdict
from zipfile import ZipFile
from hashlib import sha256
import io,csv,json,re,unicodedata,fitz
W=Path('/mnt/data/aspekte_c1_work')
D=W/'global_stage1_recheck'
P=W/'Aspekte-C1-STAGE1-K06-24-EXPLICIT-DEFA-COVERAGE-20261106.zip'
PDF=W/'aspekte-neu-c1-lb-kapitelwortschatz.pdf'
RAR=W/'comparison_sources/menschen-a1a2b1-full-audio by Hossein_mehdizade [5692974].rar'
MZIP=W/'comparison_sources/menschen-a1a2b1-full-audio by Hossein_mehdizade [5692974].zip'
B1=W/'comparison_sources/Aspekte-B1plus-CSV-ONLY-SOURCE-SANITIZED.csv'
B2=W/'comparison_sources/Aspekte-B2-CSV-ONLY-SOURCE-SANITIZED.csv'
H={'pdf':'b05c90320ad75dc19be12a374087830bd2c379206a5711e604a6aea699e189cf',
 'parent':'9ba5f357b046d05860cd7cfcc78bff110a3fa8a6a440ce7beb184a0cba36a501',
 'rar':'a2ffb791c29ddaa43e27bb944f430bff6896dc3156115f8989eee3056d5471c1',
 'menschen':'52f8bb896f5aa1c8f878aeb0ea74ef07ddbeee75261af89dfb2fcad624fc1222',
 'b1':'cca32df935397a81367b38f9b51ee33aac357ea135947a131b712969f0339033',
 'b2':'e907d0f882b4b9d02f2c631d9a93b1c4e671f6231e7c0deb257ebc26434011c5'}
def hashpath(p):
 h=sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()
for label,p in [('pdf',PDF),('parent',P),('rar',RAR),('b1',B1),('b2',B2)]:assert hashpath(p)==H[label],label
with ZipFile(MZIP) as z:
 assert z.testzip() is None
 members=[n for n in z.namelist() if n.endswith('.csv')];assert len(members)==1
 b=z.read(members[0]);assert sha256(b).hexdigest()==H['menschen']
 men=list(csv.reader(io.StringIO(b.decode('utf-8-sig')))); assert len(men)==9113
 assert [x[0] for x in men[:3]]==['#separator:comma','#html:true','#tags column:5']
 men=men[4:]
with B1.open(encoding='utf-8-sig',newline='') as f:b1=list(csv.DictReader(f))
with B2.open(encoding='utf-8-sig',newline='') as f:b2=list(csv.DictReader(f))
assert len(men)==9109 and len(b1)==1548 and len(b2)==1726
lower_rows={int(r['source_csv_ordinal']):r for r in b1+b2}
assert set(lower_rows)==set(range(1,3275))
with ZipFile(P) as z:
 assert z.testzip() is None
 old=[json.loads(l) for l in z.read('Stage1/C1-SOURCE-OCCURRENCES-3270.jsonl').splitlines()]
 index=[json.loads(l) for l in z.read('Stage1/C1-SOURCE-HEADWORD-INDEX-3270-CORRECTED-20261105.jsonl').splitlines()]
 m24={json.loads(l)['c1_id'] for l in z.read('Reviews/C1-24-MENSCHEN-WITNESS-SENSE-REVIEWS-20261105.jsonl').splitlines()}
 b40={json.loads(l)['id'] for l in z.read('Reviews/C1-40-B1B2-RECLASSIFICATION-20261105.jsonl').splitlines()}
assert len(old)==3270==len(index) and len({r['id'] for r in old})==3270
assert sum(r['triage_preflight']=='C1_NEW_LEMMA_CANDIDATE' for r in index)==2219
# Independent original source coordinate verification from the actual PDF (not only saved QA flags).
def normfirst(s):return re.sub(r'[^\wäöüÄÖÜß]','',s,flags=re.UNICODE).casefold()
with fitz.open(PDF) as doc:
 assert len(doc)==37
 words=[page.get_text('words') for page in doc]
 for r in old:
  at=[v for v in words[r['page']-1] if abs(v[0]-r['x'])<0.5 and abs(v[1]-r['y'])<0.5]
  assert at,(r['id'],'missing anchored token')
  assert normfirst(at[0][4])==normfirst(r['source_raw'].split()[0]),(r['id'],'source first word discrepancy')

def s(x):return re.sub(r'\s+',' ',str(x or '').replace('\xa0',' ').strip())
cnt=Counter()
for r in old:
 for v in r.get('prior_evidence',[]):
  n=v['source_row'];src=v['source_id'];
  if src=='Menschen_9109':a=men[n-5];expected=(a[0],a[1],a[3]);cnt['M']+=1
  else:
   assert src=='Aspekte_B1plus_B2_3275'
   a=lower_rows[n-4];expected=(a['Learnable'],a['Definition'],a['Beispiel']);cnt['A']+=1
  assert (s(v['headword']),s(v['fa']),s(v['example']))==tuple(map(s,expected)),(r['id'],src,n)
assert cnt=={'M':979,'A':511},cnt

# Cross-check all produced status data; exact headword coincidence never implies equal sense.
auth=json.loads((D/'STAGE1-ORIGINAL-MENSCHEN-9109-ASPEKTE-3274-SOURCE-AUTH-20261106.json').read_text())
assert auth['menschen']['cross_level_original_9109_attested'] is True
assert auth['aspekte_b1b2']['original_binary_current_readback'].startswith('UNAVAILABLE')
assert auth['aspekte_b1b2']['original_filename_candidates_found_in_library'][0]['raw_bytes_materialization']=='DENIED_CURRENT_PROJECT_REFERENCE'
witness=json.loads((D/'STAGE1-1490-PRIOR-WITNESS-EXACT-TRIPLET-AUDIT-20261106.json').read_text())
assert witness['checked_witness_count']==1490 and witness['unmatched_witnesses']==0
coll=[json.loads(x) for x in (D/'STAGE1-68-NEW-EXACT-HEADWORD-COLLISION-QUEUE-20261106.jsonl').read_text().splitlines()]
manual25=[json.loads(x) for x in (D/'STAGE1-25-NEWLY-SURFACED-SENSE-COMPARISONS-20261106.jsonl').read_text().splitlines()]
manual18=[json.loads(x) for x in (D/'STAGE1-18-HIGH-PRIORITY-SEMANTIC-PROPOSALS-20261106.jsonl').read_text().splitlines()]
manual41=[json.loads(x) for x in (D/'STAGE1-41-UNIQUE-SCOPED-SEMANTIC-REVIEW-PROPOSALS-20261106.jsonl').read_text().splitlines()]
assert len(coll)==68 and len(manual25)==25 and len(manual18)==18 and len(manual41)==41
assert len({c['id'] for c in coll})==68
assert len({x['id'] for x in manual41})==41
assert sum(c['already_in_menschen24_targeted_review'] for c in coll)==21
assert sum(c['already_in_b1b2_40_targeted_review'] for c in coll)==22
assert sum(not(c['already_in_menschen24_targeted_review'] or c['already_in_b1b2_40_targeted_review']) for c in coll)==25
index_byid={r['id']:r for r in index}
for r in coll:
 assert r['id'] in index_byid and r['source_raw_exact']==index_byid[r['id']]['source_raw']
 assert r['preflight_triage']=='C1_NEW_LEMMA_CANDIDATE'
 assert r['decision']=='HOLD_SENSE_AND_EXPRESSION_COMPARISON'
 assert all(r[k] is False for k in ['automatic_keep','automatic_drop','automatic_merge','card_approved','original_aspekte_b1b2_3275_sha_verified'])
for r in manual41:
 assert r['id'] in {c['id'] for c in coll}
 assert r['c1_source_raw_exact']==index_byid[r['id']]['source_raw']
 assert len(r['analysis_de'])>=70 and len(r['analysis_fa'])>=60
 assert re.search(r'[\u0600-\u06ff]',r['analysis_fa'])
 assert r['approved_final_keep_drop_merge'] is False and r['approved_learner_card'] is False
assert all(not(r['already_in_menschen24_targeted_review'] or r['already_in_b1b2_40_targeted_review']) for r in coll if r['id'] in {x['id'] for x in manual25})
for k in ('C1-P12-E033','C1-P22-E068','C1-P13-E039','C1-P36-E005'):
 assert k in {x['id'] for x in manual41}

result={
 'schema':'aspekte-c1-global-stage1-independent-readonly-qa@1.0.0','date':'2026-11-06','result':'PASS_STRUCTURAL_SOURCE_AND_SCOPED_SENSE_SCREEN_ONLY',
 'pdf_coordinate_anchors_revalidated':3270,'pdf_coordinate_mismatches':0,
 'original_menschen_rows':9109,'original_menschen_sha256':H['menschen'],'original_menschen_raw_archive_sha256':H['rar'],
 'sanitized_aspekte_rows':3274,'original_aspekte_expected_rows':3275,'original_aspekte_binary_sha_verified':False,
 'historical_witnesses_checked':1490,'historical_witness_mismatches':0,
 'strict_same_headword_new_label_hits':68,'overlap_with_prior_two_targeted_queues':43,'not_in_previous_two_targeted_queues':25,
 'fresh_de_fa_proposals':25,'unique_de_fa_scoped_proposals':41,'source_NEW_label_record_count':2219,
 'not_final_keep_drop_merge':True,'approved_learner_cards':0,'stage1_pass':False,
 'blockers':['Original full 3275-row Aspekte CSV bytes cannot be independently read from current Project.',
 'Global 3270 C1 sense/idiom synonym and expression adjudication incomplete; 68 headword collisions are only first strict screen.',
 'Source context holds and intra-C1 aliases unresolved.']}
(D/'STAGE1-INDEPENDENT-LIVE-RECHECK-20261106.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['result','pdf_coordinate_anchors_revalidated','historical_witnesses_checked','strict_same_headword_new_label_hits','unique_de_fa_scoped_proposals','stage1_pass']},indent=2))