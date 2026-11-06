#!/usr/bin/env python3
"""Independent read-only structural/provenance audit of Aspekte C1 Kapitel 4.
Does not claim to prove correctness of every translation or final dedupe.
"""
import hashlib, collections, json, pathlib, re, unicodedata, zipfile, os
import fitz
W=pathlib.Path(os.environ.get('C1_WORK_DIR',str(pathlib.Path(__file__).resolve().parent)))
PDF=W/'aspekte-neu-c1-lb-kapitelwortschatz.pdf'
PARENT=W/'Aspekte-C1-STAGE1-K03-60-EXPLICIT-DEFA-20261106.zip'
BEFORE=W/'C1-128-PENDING-EXPLICIT-BILINGUAL-SENSE-REVIEWS-20261106.jsonl'
REVIEWS=W/'C1-K04-62-EXPLICIT-BILINGUAL-FIRSTPASS-20261106.jsonl'
AFTER=W/'C1-66-PENDING-EXPLICIT-BILINGUAL-SENSE-REVIEWS-20261106.jsonl'
PDF_SHA='b05c90320ad75dc19be12a374087830bd2c379206a5711e604a6aea699e189cf'
PARENT_SHA='bff467db312732e6e744ded73a75180f19d0db913ea9e555754a98a92f123801'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:[json.loads(s) for s in p.read_text().splitlines() if s.strip()]
norm=lambda x:''.join(c for c in unicodedata.normalize('NFKD',x.casefold()) if c.isalnum())
def need(ok,label):
 if not ok:raise AssertionError(label)
need(H(PDF)==PDF_SHA,'PDF source hash mismatch')
need(H(PARENT)==PARENT_SHA,'parent archive hash mismatch')
old,new,rem=load(BEFORE),load(REVIEWS),load(AFTER)
old4=[x for x in old if x['chapter']==4]
old_other=[x for x in old if x['chapter']!=4]
need(len(old)==128 and len(old4)==62 and len(old_other)==66,'parent backlog miscount')
need(len(new)==62 and len(rem)==66,'child backlog miscount')
need([r['id'] for r in rem]==[r['id'] for r in old_other],'remaining backlog was mutated')
need([r['id'] for r in new]==[r['id'] for r in old4],'new ID order/source not preserved')
need(len(set(r['id'] for r in new))==62,'duplicated new ids')
with zipfile.ZipFile(PARENT) as archive:
 need(archive.testzip() is None,'parent zip CRC failure')
 source_index={r['id']:r for r in map(json.loads,archive.read('Stage1/C1-SOURCE-HEADWORD-INDEX-3270-CORRECTED-20261105.jsonl').decode().splitlines())}
 need(len(source_index)==3270,'source index count not 3270')
 # Validate parent's internal checksum manifest, not merely zip CRC
 manifest=archive.read('SHA256SUMS').decode().splitlines()
 need(len(manifest)==182,'parent manifest count')
 for rec in manifest:
  sha,name=rec.split('  ',1)
  need(hashlib.sha256(archive.read(name)).hexdigest()==sha,'parent manifest failure: '+name)
 orig40={}
 for s in archive.read('Reviews/C1-40-B1B2-RECLASSIFICATION-20261105.jsonl').decode().splitlines():
  r=json.loads(s)
  if r.get('id') in set(v['id'] for v in new):orig40[r['id']]=r
pdf=fitz.open(PDF)
need(len(pdf)==37,'PDF page count')
source_pages={p:norm(pdf[p-1].get_text('text')) for p in range(13,19)}
fa=re.compile('[\u0600-\u06ff]')
counts=collections.Counter();clauses=0;witness_count=0
for r,prior in zip(new,old4):
 key=r['id']; idx=source_index[key]
 need(idx['chapter']==4==r['chapter'],'chapter '+key)
 need(r['pdf_page']==prior['pdf_page'] and 13<=r['pdf_page']<=18,'page '+key)
 need(idx['source_raw']==r['source_raw_exact']==prior['source_raw_exact'],'unaltered source '+key)
 need(r['preflight_class']==idx['triage_preflight'],'preflight '+key)
 need(r['source_usage_clauses_exact']==idx['usage_clauses_preserved'],'source clauses '+key)
 need(r['corrected_lookup_key']==idx['corrected_lookup_key'],'corrected lookup key '+key)
 need(norm(idx['corrected_lookup_key']) in source_pages[r['pdf_page']],'headword absent on actual PDF page '+key)
 need(r['source_pdf_sha256']==PDF_SHA,'row source hash '+key)
 need(r['pdf_source_lookup_verified'] is True,'missing source check '+key)
 need(len(r['meaning_de'])>=45 and len(r['meaning_fa'])>=30,'brief context definition '+key)
 need(len(r['comparative_decision_rationale_de'])>=45 and len(r['comparative_decision_rationale_fa'])>=30,'brief contrast '+key)
 need(fa.search(r['meaning_fa']) and fa.search(r['comparative_decision_rationale_fa']),'missing FA '+key)
 need(r['original_aspekte_b1b2_3275_verified'] is False and r['original_menschen_9109_verified'] is False,'original baseline was silently approved '+key)
 need(all(r[k] is False for k in ['automatic_drop','automatic_keep','card_approved','stage1_pass','final_semantic_dedupe_approved']),'impermissible final card approval '+key)
 need(r['status']=='SOURCE_EXACT_EXPLICIT_BILINGUAL_FIRST_PASS_ONLY_NO_RELEASE','incorrect stage status '+key)
 need(bool(r['first_pass_class']),'empty first pass class '+key)
 for phrase in r['source_usage_clauses_exact']:
  if len(phrase)>15 and '+ A.' not in phrase and '+ D.' not in phrase:
   need(norm(phrase) in source_pages[r['pdf_page']],'quoted example missing on PDF page '+key)
   clauses+=1
 if key in orig40:
  w=r['historical_cross_level_provisional_witnesses']
  need(len(w)==1 and w[0]['provisional_state']==orig40[key]['provisional_state'],'historic lower witness was silently altered '+key)
  need(w[0]['approved_for_final_exclusion'] is False,'historic witness finalized '+key)
  witness_count+=1
 else:need(not r['historical_cross_level_provisional_witnesses'],'new unsupported historical witness '+key)
 counts[r['pdf_page']]+=1
need(len(set(x['meaning_de'] for x in new))==62,'identical DE meanings')
need(len(set(x['meaning_fa'] for x in new))==62,'identical FA meanings')
need(sum(counts.values())==62,'per-page total mismatch')
need(collections.Counter(x['chapter'] for x in rem)=={5:42,6:24},'unexpected remaining chapter')
need(new[[v['id'] for v in new].index('C1-P15-E071')]['source_context_hold'] is True,'Kellerstück unknown sense not held')
need(witness_count==6,'six prior direct witnesses unaccounted')
report={
 'schema':'aspekte-c1-k04-62-independent-readonly-check@1.0.0','date':'2026-11-06',
 'result':'PASS_SOURCE_STRUCTURAL_ONLY_NO_STAGE1_RELEASE',
 'scope':'PDF-EXACT PROVENANCE ID/CLAUSE STRUCTURE HISTORY COVERAGE FLAGS; NOT INDEPENDENT HUMAN LEXICAL CERTIFICATION',
 'original_pdf_sha256':PDF_SHA,'parent_checkpoint_sha256':PARENT_SHA,
 'source_index_occurrences':3270,'actual_pdf_page_count':37,
 'source_headword_original_page_checks':62,'source_index_raw_exact_checks':62,
 'source_usage_example_checks':clauses,'individually_written_de_fa_pairs':62,
 'unique_ids':len(set(x['id'] for x in new)),'distinct_de_meanings':62,'distinct_fa_meanings':62,
 'pages':dict(sorted(counts.items())),'historical_provisional_lower_witnesses_preserved':6,
 'explicit_context_unknown_hold_ids':['C1-P15-E071'],
 'risky_grammar_or_sense_usage_held':['C1-P14-E077','C1-P15-E043','C1-P17-E034','C1-P18-E020'],
 'before_pending':128,'after_pending':66,'after_pending_by_chapter':{'5':42,'6':24},
 'previous_explicit_reviews':2091,'current_explicit_reviews_with_holds':2153,
 'current_explicit_coverage_pct':round(2153/2219*100,2),'chapter4_review_records':279,'chapter4_source_new_total':279,
 'global_duplicate_adjudication_final':False,'original_menschen_9109_readback_verified':False,
 'original_b1b2_3275_readback_verified':False,'independent_human_semantic_quality_certified':False,
 'cards_approved':0,'auto_keep':0,'auto_drop':0,'stage1_pass':False,
 'source_pdf_or_historical_archive_modified':False,
}
(W/'INDEPENDENT-RECHECK-K04-62-GLOBAL-DEFA-CENSUS-20261106.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True))