#!/usr/bin/env python3
"""Read-only independent source/provenance audit of Aspekte-C1 K06 scoped DE/FA; NOT external translation certification."""
from pathlib import Path
import hashlib,zipfile,json,collections,re,unicodedata
import fitz
W=Path('/mnt/data/aspekte_c1_work')
source=W/'aspekte-neu-c1-lb-kapitelwortschatz.pdf'
parent=W/'Aspekte-C1-STAGE1-K05-42-EXPLICIT-DEFA-20261106.zip'
newfile=W/'C1-K06-24-EXPLICIT-BILINGUAL-FIRSTPASS-20261106.jsonl'
oldfile=W/'C1-24-PENDING-EXPLICIT-BILINGUAL-SENSE-REVIEWS-20261106.jsonl'
empty=W/'C1-0-PENDING-EXPLICIT-BILINGUAL-SENSE-REVIEWS-20261106.jsonl'
PDF_SHA='b05c90320ad75dc19be12a374087830bd2c379206a5711e604a6aea699e189cf'
PARENT_SHA='de87f5c316e21160e8d58b320616a0d4045dd815474df51af4369611cb81308e'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
N=lambda s:''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if c.isalnum())
read=lambda p:[json.loads(s) for s in p.read_text(encoding='utf8').splitlines() if s.strip()]
need=lambda cond,msg:None if cond else (_ for _ in ()).throw(AssertionError(msg))
need(SHA(source)==PDF_SHA,'source PDF has changed')
need(SHA(parent)==PARENT_SHA,'parent ZIP SHA changed')
old=read(oldfile);rows=read(newfile);pending=read(empty)
need(len(old)==len(rows)==24 and not pending,'backlog split 24 -> 24 reviewed/0 outstanding mismatch')
need([r['id'] for r in rows]==[r['id'] for r in old],'IDs/order mismatch')
need(len({r['id'] for r in rows})==24,'duplicate new ID')
with zipfile.ZipFile(parent) as z:
 need(z.testzip() is None and len(z.namelist())==195,'parent ZIP CRC or member count invalid')
 manifest=z.read('SHA256SUMS').decode().splitlines()
 need(len(manifest)==194,'bad historical manifest size')
 for l in manifest:
  h,n=l.split('  ',1)
  need(hashlib.sha256(z.read(n)).hexdigest()==h,'historical SHA mismatch '+n)
 idx={r['id']:r for l in z.read('Stage1/C1-SOURCE-HEADWORD-INDEX-3270-CORRECTED-20261105.jsonl').decode().splitlines() if l for r in [json.loads(l)]}
 need(len(idx)==3270 and len([r for r in idx.values() if r['triage_preflight']=='C1_NEW_LEMMA_CANDIDATE'])==2219,'C1 source index/preflight count mismatch')
 seen={};fieldpairs=(('meaning_de','meaning_fa'),('meaning_de_scoped','meaning_fa_scoped'),('de_provisional_sense','fa_provisional_sense'))
 for name in z.namelist():
  if not (name.startswith('Reviews/') and name.endswith('.jsonl')):continue
  for ln in z.read(name).decode().splitlines():
   if not ln.strip():continue
   r=json.loads(ln)
   if not r.get('id','').startswith('C1-'): continue
   if not any(r.get(de) and r.get(fa) for de,fa in fieldpairs):continue
   need(r['id'] in idx, 'bad ID '+r['id'])
   need(r['id'] not in seen,'duplicate prior explicit DE/FA for '+r['id'])
   seen[r['id']]=name
 need(len(seen)==2195,'preexisting actual 2195 source-specific DE/FA artifacts not evidenced; found '+str(len(seen)))
 for r in rows:
  need(r['id'] not in seen and r['id'] in idx,'new DE/FA duplicate or missing from index '+r['id'])
  seen[r['id']]='NEW_K06'
 need(len(seen)==2219,'unique source-specific DE/FA total not 2219')
 source_new={id for id,record in idx.items() if record['triage_preflight']=='C1_NEW_LEMMA_CANDIDATE'}
 need(set(seen)==source_new,'actual unique source-specific firstpass IDs not equal C1 NEW source ID set')
 w40={}
 for l in z.read('Reviews/C1-40-B1B2-RECLASSIFICATION-20261105.jsonl').decode().splitlines():
  r=json.loads(l)
  if r['id'] in {x['id'] for x in rows}:w40[r['id']]=r
 need(list(w40)==['C1-P24-E015'] and w40['C1-P24-E015']['provisional_state']=='EXCLUDE_SAME_PRIOR_LEXEME','prior source duplicate witness missing')
 doc=fitz.open(source)
 need(len(doc)==37,'source PDF length mismatch')
 pages={p:N(doc[p-1].get_text('text')) for p in (21,22,23,24)}
 fa_pat=re.compile('[\u0600-\u06FF]')
 count=collections.Counter();phrase_checked=0
 for r,oldrow in zip(rows,old):
  id=r['id']; ix=idx[id];p=r['pdf_page'];count[p]+=1
  need(r['chapter']==6 and ix['chapter']==6 and 21<=p<=24,'bad chapter/page')
  need(oldrow['pdf_page']==p,'old page changed')
  need(r['source_raw_exact']==oldrow['source_raw_exact']==ix['source_raw'],'PDF index/source mismatch '+id)
  need(r['source_usage_clauses_exact']==ix['usage_clauses_preserved'],'source usage changed '+id)
  need(r['corrected_lookup_key']==ix['corrected_lookup_key'],'source lookup changed '+id)
  need(r['preflight_class']==oldrow['triage_preflight']==ix['triage_preflight'],'preflight modified '+id)
  need(r['existing_targeted_review_artifacts']==oldrow['existing_targeted_review_artifacts'],'previous artifacts lost '+id)
  need(r['pdf_source_lookup_verified'] is True and r['source_pdf_sha256']==PDF_SHA,'PDF proof lost '+id)
  need(N(ix['corrected_lookup_key']) in pages[p],'headword not visible on original PDF page '+id)
  for k in ('meaning_de','meaning_fa','comparative_decision_rationale_de','comparative_decision_rationale_fa'):
   need(isinstance(r[k],str) and len(r[k])>=65,'too-short individual context gloss '+k+' '+id)
  need(fa_pat.search(r['meaning_fa']) and fa_pat.search(r['comparative_decision_rationale_fa']),'Persian script absent '+id)
  need(r['meaning_de']!=r['comparative_decision_rationale_de'],'comparison copied from gloss '+id)
  need(not any(r[k] for k in ('original_menschen_9109_verified','original_aspekte_b1b2_3275_verified','automatic_keep','automatic_drop','card_approved','stage1_pass','final_semantic_dedupe_approved')),'unauthorized release or source status '+id)
  need(r['status']=='SOURCE_EXACT_EXPLICIT_BILINGUAL_FIRST_PASS_ONLY_NO_RELEASE','wrong stage scope '+id)
  for phrase in r['source_usage_clauses_exact']:
   need(N(phrase) in pages[p],'PDF-quoted usage not found '+id+' '+phrase)
   phrase_checked+=1
  need(set(x['artifact'] for x in r['historical_provisional_witnesses']).issubset(set(oldrow['existing_targeted_review_artifacts'])),'added unlisted historical witness '+id)
 need(dict(count)=={21:5,22:8,23:6,24:5},'wrong page distribution')
 need(phrase_checked==3,'expected 3 exact PDF usage/rektions to be checked')
 need([r['id'] for r in rows if r['potential_exact_prior_duplicate_hold']]==['C1-P24-E015'],'B1B2 duplicate HOLD missing')
 need([r['id'] for r in rows if r['source_context_inferred_hold']]==['C1-P22-E072'],'source-context inference HOLD missing')
 need(len({r['meaning_de'] for r in rows})==24 and len({r['meaning_fa'] for r in rows})==24,'recycled generic meaning rows')
 verdict={
  'schema':'aspekte-c1-k06-independent-source-exact-provenance-audit@1.0.0','date':'2026-11-06',
  'result':'PASS_ALL_2219_EXPLICIT_BILINGUAL_ARTIFACT_IDS_SOURCE_EXACT_NO_STAGE1_RELEASE',
  'scope':'READ-ONLY ARTIFACT CENSUS, USER PDF SOURCE INDEX MATCH, EXACT CLAUSES, HISTORICAL WITNESS/HOLD PRESERVATION. NOT INDEPENDENT LEXICOGRAPHIC HUMAN CERTIFICATION.',
  'source_pdf_sha256':PDF_SHA,'parent_archive_sha256':PARENT_SHA,
  'source_index_occurrences':3270,'source_new_id_total':2219,
  'historical_explicit_de_fa_distinct_ids':2195,'new_individual_de_fa_records':24,
  'all_explicit_de_fa_distinct_source_ids_verified':2219,'remaining_without_explicit_de_fa':0,
  'new_source_id_lemma_page_verifications':24,'source_exact_usage_clauses_rechecked':phrase_checked,
  'page_count':dict(sorted(count.items())),
  'historical_duplicate_proposal_retained':'C1-P24-E015',
  'context_inference_hold_retained':'C1-P22-E072',
  'prior_archive_crc_and_manifest':'PASS','source_pdf_unchanged':True,'parent_archive_unchanged':True,
  'original_menschen_9109_readback_verified':False,'original_b1b2_3275_readback_verified':False,
  'global_3270_cross_level_and_intra_c1_semantic_dedupe_complete':False,
  'human_semantic_translation_certified_independently':False,
  'approved_cards':0,'automatic_keep':0,'automatic_drop':0,'stage1_pass':False,'release_allowed':False
 }
(W/'INDEPENDENT-RECHECK-K06-24-GLOBAL-DEFA-CENSUS-20261106.json').write_text(json.dumps(verdict,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
print(json.dumps(verdict,ensure_ascii=False,sort_keys=True,indent=2))