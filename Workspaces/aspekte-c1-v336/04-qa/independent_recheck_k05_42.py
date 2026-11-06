#!/usr/bin/env python3
"""Read-only provenance and integrity check (not independent dictionary-certified translations)."""
import pathlib,zipfile,hashlib,collections,re,unicodedata,json,os
import fitz
W=pathlib.Path(os.environ.get('C1_WORK_DIR','/mnt/data/aspekte_c1_work'))
parent=W/'Aspekte-C1-STAGE1-K04-62-EXPLICIT-DEFA-20261106.zip'
pdf=W/'aspekte-neu-c1-lb-kapitelwortschatz.pdf'
oldfile=W/'C1-66-PENDING-EXPLICIT-BILINGUAL-SENSE-REVIEWS-20261106.jsonl'
newfile=W/'C1-K05-42-EXPLICIT-BILINGUAL-FIRSTPASS-20261106.jsonl'
pendingfile=W/'C1-24-PENDING-EXPLICIT-BILINGUAL-SENSE-REVIEWS-20261106.jsonl'
PDF_SHA='b05c90320ad75dc19be12a374087830bd2c379206a5711e604a6aea699e189cf'
PARENT_SHA='3ece116478895536c4aefacb89224116fbc64674f9c5de6951430ad4f72c8898'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:[json.loads(s) for s in p.read_text().splitlines() if s.strip()]
norm=lambda s:''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if c.isalnum())
def need(cond,why):
 if not cond:raise AssertionError(why)
need(sha(pdf)==PDF_SHA,'authoritative user PDF hash mismatch')
need(sha(parent)==PARENT_SHA,'parent checkpoint hash mismatch')
old,new,rem=read(oldfile),read(newfile),read(pendingfile)
previous=[r for r in old if r['chapter']==5]
rest=[r for r in old if r['chapter']!=5]
need(len(old)==66 and len(previous)==42 and len(rest)==24,'parent 66/42/24 backlog invalid')
need(len(new)==42 and len(rem)==24,'child 42/24 backlog invalid')
need([r['id'] for r in new]==[r['id'] for r in previous],'source ID order changed')
need([r['id'] for r in rem]==[r['id'] for r in rest],'unchanged chapter 6 backlog corrupted')
need(len(set(r['id'] for r in new))==42,'duplicate source ids')
with zipfile.ZipFile(parent) as z:
 need(z.testzip() is None,'parent ZIP CRC failed')
 need(len(z.namelist())==189,'parent ZIP member count wrong')
 manifest=z.read('SHA256SUMS').decode().splitlines()
 need(len(manifest)==188,'parent manifest count wrong')
 for line in manifest:
  digest,name=line.split('  ',1)
  need(hashlib.sha256(z.read(name)).hexdigest()==digest,'parent SHA entry corrupted '+name)
 source_index={r['id']:r for r in map(json.loads,z.read('Stage1/C1-SOURCE-HEADWORD-INDEX-3270-CORRECTED-20261105.jsonl').decode().splitlines())}
 need(len(source_index)==3270,'source index not 3270')
 w40={}
 for s in z.read('Reviews/C1-40-B1B2-RECLASSIFICATION-20261105.jsonl').decode().splitlines():
  x=json.loads(s)
  if x['id'] in {r['id'] for r in new}:w40[x['id']]=x
 holdx={}
 for s in z.read('Reviews/C1-9-SOURCE-CONTEXT-HOLD-FOLLOWUP-20261105.jsonl').decode().splitlines():
  x=json.loads(s)
  if x['id'] in {r['id'] for r in new}:holdx[x['id']]=x
 need(len(w40)==4,'historical direct B1/B2 witnesses not 4')
 need(list(holdx)==['C1-P19-E070'],'original context hold not present')
pages={p:norm(fitz.open(pdf)[p-1].get_text('text')) for p in range(18,22)}
fa=re.compile(r'[\u0600-\u06FF]')
usage_checks=0;prior_links=0;counts=collections.Counter()
for r,s in zip(new,previous):
 ident=r['id'];x=source_index[ident]
 need(r['chapter']==x['chapter']==5,'chapter mismatch '+ident)
 need(r['pdf_page']==s['pdf_page'] and 18<=r['pdf_page']<=21,'PDF page mismatch '+ident)
 need(r['source_raw_exact']==s['source_raw_exact']==x['source_raw'],'source text changed '+ident)
 need(r['source_usage_clauses_exact']==x['usage_clauses_preserved'],'source usage changed '+ident)
 need(r['corrected_lookup_key']==x['corrected_lookup_key'],'lookup changed '+ident)
 need(r['preflight_class']==x['triage_preflight'],'historical preflight status changed '+ident)
 need(r['existing_targeted_review_artifacts']==s['existing_targeted_review_artifacts'],'targeted references lost '+ident)
 need(norm(r['corrected_lookup_key']) in pages[r['pdf_page']],'lemma not visible on original PDF page '+ident)
 need(r['pdf_source_lookup_verified'] is True and r['source_pdf_sha256']==PDF_SHA,'source proof missing '+ident)
 need(len(r['meaning_de'])>=50 and len(r['meaning_fa'])>=30,'DE/FA gloss too short '+ident)
 need(len(r['comparative_decision_rationale_de'])>=50 and len(r['comparative_decision_rationale_fa'])>=35,'contrast too short '+ident)
 need(bool(fa.search(r['meaning_fa'])) and bool(fa.search(r['comparative_decision_rationale_fa'])),'FA script absent '+ident)
 need(r['meaning_de'] != r['comparative_decision_rationale_de'],'duplicated comparison wording '+ident)
 need(r['original_menschen_9109_verified'] is False and r['original_aspekte_b1b2_3275_verified'] is False,'unverified lower originals marked verified '+ident)
 need(all(r[k] is False for k in ('automatic_keep','automatic_drop','card_approved','final_semantic_dedupe_approved','stage1_pass')),'unauthorized card release '+ident)
 need(r['status']=='SOURCE_EXACT_EXPLICIT_BILINGUAL_FIRST_PASS_ONLY_NO_RELEASE','wrong QA stage label '+ident)
 for example in r['source_usage_clauses_exact']:
  if len(example)>12 and '+ A.' not in example and '+ D.' not in example:
   need(norm(example) in pages[r['pdf_page']],'source example not in PDF page '+ident+' '+example)
   usage_checks+=1
 if ident in w40:
  w=r['historical_cross_level_provisional_witnesses']
  need(len(w)==1 and w[0]['provisional_state']==w40[ident]['provisional_state'],'prior B1B2 witness status altered '+ident)
  need(w[0]['final_keep_drop_authorized'] is False,'prior witness silently finalized '+ident)
  prior_links+=1
 else:
  need(not r['historical_cross_level_provisional_witnesses'],'invented prior B1B2 witness '+ident)
 counts[r['pdf_page']]+=1
need(len({r['meaning_de'] for r in new})==42 and len({r['meaning_fa'] for r in new})==42,'repeated generic glosses')
need(counts=={18:3,19:11,20:16,21:12},'unexpected page distribution')
need(prior_links==4,'prior cross-level witness tally')
need(all(x['chapter']==6 for x in rem),'unexpected backlog chapter')
need({r['id'] for r in new if r['source_context_hold']}=={'C1-P19-E070','C1-P21-E053'},'source context uncertainty suppressed')
need({r['id'] for r in new if r['source_usage_caution']}=={'C1-P20-E052','C1-P21-E020'},'contextual caution missing')
need(new[[v['id'] for v in new].index('C1-P19-E070')]['historical_source_context_and_teachability_witnesses'],'old aufgehoeben HOLD dropped')
report={
 'schema':'aspekte-c1-k05-42-independent-source-exact-provenance-audit@1.0.0',
 'date':'2026-11-06','result':'PASS_PDF_SOURCE_STRUCTURAL_AND_HISTORICAL_PROVENANCE_ONLY',
 'scope':'ORIGINAL PDF LEMMA/USAGE, SOURCE INDEX ID, PRE-FLIGHT LABEL, HISTORICAL WITNESS, DE/FA EVIDENCE PRESENCE AND NO-RELEASE. NOT INDEPENDENT HUMAN SEMANTIC CERTIFICATION.',
 'original_pdf_sha256':PDF_SHA,'previous_checkpoint_sha256':PARENT_SHA,
 'source_index_total':3270,'pdf_physical_pages':37,'pdf_source_page_exact_lemma_matches':42,'pdf_exact_source_usage_checked':usage_checks,
 'distinct_individual_DE_meanings':42,'distinct_individual_FA_meanings':42,'previous_open':66,'chapter5_records':42,'remaining_open':24,
 'verified_review_record_total_with_HOLDs':2195,'original_new_candidate_total':2219,'firstpass_de_fa_percent':round(2195/2219*100,2),
 'page_counts':dict(sorted(counts.items())),'historical_provisional_lower_witnesses_preserved':4,
 'preexisting_hold_preserved':['C1-P19-E070'],'new_context_uncertainty':['C1-P21-E053'],
 'caution_context_limited':['C1-P20-E052','C1-P21-E020'],
 'original_menschen_9109_readback_verified':False,'original_b1b2_3275_readback_verified':False,
 'whole_c1_3270_global_sense_and_idiom_dedupe_complete':False,
 'human_semantic_translation_certified_independently':False,
 'approved_cards':0,'automatic_drop':0,'automatic_keep':0,'stage1_pass':False,'release_allowed':False,
 'parent_archive_or_pdf_modified':False
}
(W/'INDEPENDENT-RECHECK-K05-42-GLOBAL-DEFA-CENSUS-20261106.json').write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2))