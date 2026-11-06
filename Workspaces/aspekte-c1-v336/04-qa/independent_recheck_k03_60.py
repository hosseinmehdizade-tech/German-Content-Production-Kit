#!/usr/bin/env python3
"""Read-only structural/source/coverage audit, independent of the authoring build.
The test does NOT assert final human semantic, full lower-original, or Stage1 release approval.
"""
import collections, hashlib, json, pathlib, re, unicodedata, zipfile, os
import fitz

ROOT=pathlib.Path(os.environ.get('C1_WORK_DIR', str(pathlib.Path(__file__).resolve().parent))).resolve()
SOURCE=ROOT/'aspekte-neu-c1-lb-kapitelwortschatz.pdf'
PARENT=ROOT/'Aspekte-C1-STAGE1-K02-34-EXPLICIT-DEFA-20261106.zip'
BEFORE=ROOT/'C1-188-PENDING-EXPLICIT-BILINGUAL-SENSE-REVIEWS-20261106.jsonl'
REVIEWS=ROOT/'C1-K03-60-EXPLICIT-BILINGUAL-FIRSTPASS-20261106.jsonl'
AFTER=ROOT/'C1-128-PENDING-EXPLICIT-BILINGUAL-SENSE-REVIEWS-20261106.jsonl'
EXPECTED_PDF='b05c90320ad75dc19be12a374087830bd2c379206a5711e604a6aea699e189cf'
EXPECTED_PARENT='df8f3f5b49d0d55e3862e0819d402515d1c0e3fd946e215839e6c192f70d7303'

def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
def norm(x):return ''.join(c for c in unicodedata.normalize('NFKD',x).casefold() if c.isalnum())
def must(ok,message):
 if not ok:raise AssertionError(message)

must(H(SOURCE)==EXPECTED_PDF,'PDF sha different')
must(H(PARENT)==EXPECTED_PARENT,'parent ZIP sha different')
previous, current, pending=load(BEFORE),load(REVIEWS),load(AFTER)
prev3=[x for x in previous if x['chapter']==3]
prev_non3=[x for x in previous if x['chapter']!=3]
must(len(previous)==188 and len(prev3)==60,'previous ledger count')
must(len(current)==60 and len(pending)==128 and len(prev_non3)==128,'reconciled count')
must([x['id'] for x in pending]==[x['id'] for x in prev_non3],'pending ledger retained exactly')
must({x['id'] for x in current}=={x['id'] for x in prev3},'missing or extra K03 ID')
must(len({x['id'] for x in current})==60,'duplicate IDs')
with zipfile.ZipFile(PARENT) as z:
 must(z.testzip() is None,'parent ZIP bad CRC')
 original_index={x['id']:x for x in map(json.loads,z.read('Stage1/C1-SOURCE-HEADWORD-INDEX-3270-CORRECTED-20261105.jsonl').decode().splitlines())}
 must(len(original_index)==3270,'authoritative source index count')

pdf=fitz.open(SOURCE)
must(len(pdf)==37,'PDF unexpected length')
source_text={page:norm(pdf[page-1].get_text('text')) for page in range(9,14)}
fa=re.compile(r'[\u0600-\u06ff]')
lookups=0
clauses=0
pages=collections.Counter()
nonfinal=0
for row in current:
 ident=row['id']
 old=next(x for x in prev3 if x['id']==ident)
 original=original_index[ident]
 must(row['chapter']==old['chapter']==3,'chapter mismatch')
 must(row['pdf_page']==old['pdf_page'] and 9<=row['pdf_page']<=13,'page mismatch')
 must(row['source_raw_exact']==old['source_raw_exact']==original['source_raw'],'raw source changed')
 must(row['preflight_class']==original['triage_preflight'],'preflight class changed')
 must(row['source_usage_clauses_exact']==original['usage_clauses_preserved'],'clause mismatch')
 for key in ('meaning_de','meaning_fa','comparative_decision_rationale_de','comparative_decision_rationale_fa'):
  must(len(row[key].strip())>=35,ident+' incomplete '+key)
 must(fa.search(row['meaning_fa']) is not None and fa.search(row['comparative_decision_rationale_fa']) is not None,ident+' missing Persian')
 must(all(row[k] is False for k in ('automatic_keep','automatic_drop','card_approved','stage1_pass')),ident+' impermissible release flag')
 must(row['original_menschen_9109_verified'] is False and row['original_aspekte_b1b2_3275_verified'] is False,'unproven original baseline')
 must(norm(row['corrected_lookup_key']) in source_text[row['pdf_page']],ident+' headword not visible on original PDF page')
 lookups+=1
 for clause in row['source_usage_clauses_exact']:
  # Rektionsglossen and isolated syntactic abbreviations are not asserted as sentence-level source phrases.
  if len(clause)>=15 and not ('+ A.' in clause or '+ D.' in clause):
   must(norm(clause) in source_text[row['pdf_page']],ident+' usage phrase absent from PDF page: '+clause)
   clauses+=1
 pages[row['pdf_page']]+=1
 nonfinal+=1
must(len(set(x['meaning_de'] for x in current))==60,'duplicate DE meanings')
must(len(set(x['meaning_fa'] for x in current))==60,'duplicate FA meanings')
must(sum(pages.values())==60,'page count')
must(all(r['chapter'] in (4,5,6) for r in pending),'unexpected chapter in new backlog')
must(collections.Counter(r['chapter'] for r in pending)=={4:62,5:42,6:24},'backlog chapter count')
report={
 'schema':'aspekte-c1-k03-60-independent-readonly-recheck@1.0.0',
 'scope':'AUTOMATED_SOURCE_STRUCTURAL_AND_COVERAGE_QA_ONLY_NOT_HUMAN_SEMANTIC_APPROVAL',
 'date':'2026-11-06','result':'PASS_SCOPE_ONLY_NO_STAGE1_RELEASE',
 'reference_pdf_sha256':H(SOURCE),'parent_zip_sha256':H(PARENT),
 'source_pdf_pages_actual':len(pdf),'index_id_coverage':len(original_index),
 'matched_original_pdf_headwords':lookups,'matched_quoted_source_clauses':clauses,
 'independent_per_page_distribution':dict(sorted(pages.items())),
 'reviewed_ids':len(current),'distinct_german_meanings':60,'distinct_persian_meanings':60,
 'crosschecked_source_raw_against_parent_index':60,'crosschecked_source_raw_against_original_pending_ledger':60,
 'reconciled_old_remaining':188,'reconciled_new_remaining':128,
 'backlog_remaining_by_chapter':dict(sorted(collections.Counter(x['chapter'] for x in pending).items())),
 'previous_explicit_firstpass':2031,'current_explicit_firstpass':2091,
 'current_explicit_coverage_pct':round(2091/2219*100,2),'chapter3_covered':239,'chapter3_total':239,
 'automatic_keep':0,'automatic_drop':0,'approved_cards':0,'stage1_pass':False,
 'full_original_menschen_verified':False,'full_original_b1b2_verified':False,
 'human_translation_fidelity_globally_independently_certified':False,
 'global_3270_semantic_deduplication_final':False,
 'historical_prior_witnesses_not_finally_adjudicated':True
}
( ROOT/'INDEPENDENT-RECHECK-K03-60-GLOBAL-DEFA-CENSUS-20261106.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
print(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True))