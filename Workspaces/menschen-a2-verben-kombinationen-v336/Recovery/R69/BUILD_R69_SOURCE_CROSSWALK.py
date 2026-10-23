#!/usr/bin/env python3
"""Build an audit-only R69 course evidence crosswalk for exact R66 + R67.

Never attests examples, relations, reviewer qualification, or Stage4 finality.
Does not redistribute user-supplied textbook image bytes.
"""
import argparse,csv,hashlib,io,json,re,zipfile,pathlib,collections
R66_SHA='630bfcd30be7439f397c634ed7c5f197db54833455a88569b27b7ef79c73a21b'
R67_SHA='84299acfdd23649c114d01068724e3ffcc404a24950ea0f9dbdd1286353b328d'
R66_DIR='93-Stage4-Rechnung-Translation-And-Synonym-Triage-R66/'
IMAGES='03-Source-Provenance/Raw-Screenshots-Verified/'
OCC_PATH='03-Source-Provenance/A2-VERBEN-SOURCE-OCCURRENCES.json'
TSV_PATH=R66_DIR+'CANDIDATE-IMPORT-NOT-FINAL.tsv'
REVIEW_PATH=R66_DIR+'REVIEW-DATA.json'

def sha(b):return hashlib.sha256(b).hexdigest()
def text_json(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2).encode('utf-8')+b'\n'
def tsv(rows,columns):
 out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=columns,delimiter='\t',lineterminator='\n',extrasaction='ignore');w.writeheader();w.writerows(rows);return out.getvalue().encode('utf-8')
def verified(p,s):
 data=pathlib.Path(p).read_bytes()
 if sha(data)!=s:raise ValueError(f'SHA256 does not match {p}')
 return zipfile.ZipFile(io.BytesIO(data),'r')
def build(source,batches,dest):
 z=verified(source,R66_SHA);q=verified(batches,R67_SHA)
 if z.testzip() is not None or q.testzip() is not None: raise ValueError('Source archive CRC failed')
 candidate=z.read(TSV_PATH);review=json.loads(z.read(REVIEW_PATH));assignment=json.loads(q.read('R67-ASSIGNMENTS.json'))
 if sha(candidate)!='77e29cbe28803b8534ad4e6cc0ece16df639a8aa01c98c116fd3ce114ebe59a7':raise ValueError('R66 candidate mismatch')
 if review['data_fingerprint']!='794ade6af612bce219d47a0b90f0ebff90f40ef9cf09f65b774c4f7e277886df':raise ValueError('R66 review fingerprint mismatch')
 originals=json.loads(z.read(OCC_PATH))['occurrences'];byocc={r['occurrence_id']:r for r in originals}
 if len(byocc)!=len(originals):raise ValueError('Duplicated original occurrence ID')
 img={}
 for idx in range(1,12):
  path=f'{IMAGES}A2-source-{idx:02}.png';data=z.read(path)
  img[idx]={'index':idx,'zip_member':path,'sha256':sha(data),'bytes':len(data),'outside_bundle_redistribution':False}
 bycard={};claims={};all_links=[];orphan=[]
 cards=list(csv.DictReader(io.StringIO(candidate.decode('utf-8-sig')),delimiter='\t'))
 if len(cards)!=292 or len(set(r['id'] for r in cards))!=292:raise ValueError('Card identity mismatch')
 records=[]
 for row in cards:
  key=row['id'];c=json.loads(row['custom_fields']);locs=[]
  for link in c['course_memberships']:
   occurrence=byocc.get(link['occurrence_id'])
   if occurrence is None:raise ValueError('Missing source occurrence '+link['occurrence_id'])
   location=occurrence['locator'];ix=location['screenshot_index'];order=location['source_order']
   if link['source_row_ordinal']!=order or ix not in img:raise ValueError('Source locator conflict '+key)
   if occurrence.get('target_hint') not in (None,key):raise ValueError('Source target conflicts with card '+key)
   locs.append({'occurrence_id':link['occurrence_id'],'source_order':order,'source_screenshot_index':ix,'source_screenshot_row_index':location['row_index'],'screenshot_sha256':img[ix]['sha256'],'source_raw_text':occurrence['raw_text'],'historical_identity_actions':occurrence.get('historical_identity_actions',[])})
   all_links.append(link['occurrence_id'])
  course_refs=[x for x in c['vnext_source_refs'] if x.get('source_id')=='MENSCHEN_A2_SCREENSHOTS' and x.get('source_kind')=='course']
  if len(course_refs)!=1:raise ValueError('Expected one course locator claim '+key)
  ref=course_refs[0];m=re.fullmatch(r'screenshot-(\d+):row-(\d+);source-order=(\d+)',ref.get('locator',''))
  if not m:raise ValueError('Bad course locator string '+key)
  loc_tuple=tuple(map(int,m.groups()))
  if not any((x['source_screenshot_index'],x['source_screenshot_row_index'],x['source_order'])==loc_tuple for x in locs):raise ValueError('Course locator not linked to occurrence '+key)
  bycard[key]=locs;claims[key]=ref
  flags=c.get('source_review_flags') or []
  book_mirror=sum(1 for x in c['vnext_source_refs'] if x.get('source_id')=='MENSCHEN_A2_SCREENSHOTS' and x.get('source_kind')=='book')
  records.append({'card_id':key,'headword':c['canonical_unit']['headword'],'source_occurrences':len(locs),'primary_source_screenshot':loc_tuple[0], 'primary_source_row':loc_tuple[1], 'source_original_ordinals':';'.join(str(x['source_order']) for x in locs), 'all_occurrence_ids':';'.join(x['occurrence_id'] for x in locs), 'all_image_row_locators':'; '.join(f"A2-source-{x['source_screenshot_index']:02}.png:row-{x['source_screenshot_row_index']}" for x in locs), 'all_raw_source_rows':' | '.join(x['source_raw_text'].replace('\t',' ') for x in locs), 'primary_image_sha256':img[loc_tuple[0]]['sha256'], 'source_claim_tags':';'.join(ref.get('what_was_verified',[])), 'course_row_claim_not_equal_authored_example_signoff':'TRUE', 'additional_same_id_book_refs':book_mirror, 'source_review_flags':json.dumps(flags,ensure_ascii=False), 'independent_source_review_status':'NOT_REVIEWED'})
  
 if len(all_links)!=335 or len(set(all_links))!=335:raise ValueError('Course occurrence membership count unexpected')
 source_left=set(byocc)-set(all_links)
 if source_left!={'ma2-occ-0286-00'}:raise ValueError('Unexpected unlinked occurrence(s): '+str(source_left))
 retired=byocc['ma2-occ-0286-00']
 if 'RETIRE_LEGACY_CARD' not in retired.get('historical_identity_actions',[]):raise ValueError('Unlinked occurrence is not an intentional retired identity')
 reviewitems=review['examples']+review['synonyms'];byid={x['id']:x for x in reviewitems}
 if len(reviewitems)!=1411 or len(byid)!=1411:raise ValueError('Review inventory identity count unexpected')
 batches_list=assignment['batches'];all_assigned=[x for b in batches_list for x in b['item_ids']]
 if len(batches_list)!=10 or len(all_assigned)!=1411 or set(all_assigned)!=set(byid) or len(set(all_assigned))!=1411:raise ValueError('Reviewer item partition not complete')
 bybatch={k:batch['batch_id'] for batch in batches_list for k in batch['item_ids']}
 for b in batches_list:
  cards_in_batch=set(b['cards'])
  if any(byid[x]['card_id'] not in cards_in_batch for x in b['item_ids']):raise ValueError('Review batch card grouping changed')
 lookup={r['card_id']:r for r in records}
 for r in records:
  matching={bybatch[x['id']] for x in reviewitems if x['card_id']==r['card_id']}
  if len(matching)!=1:raise ValueError('Card split across review batches')
  r['batch_id']=next(iter(matching))
 itemrows=[]
 for item in reviewitems:
  x=lookup[item['card_id']]
  itemrows.append({'batch_id':bybatch[item['id']],'review_item_id':item['id'],'review_kind':item['review_kind'],'review_item_fingerprint':item['fingerprint'],'card_id':item['card_id'],'headword':item['headword'],'source_occurrence_ids':x['all_occurrence_ids'],'source_image_row_locators':x['all_image_row_locators'],'source_claim_tags':x['source_claim_tags'],'claim_boundary':'SOURCE_ROW_DOES_NOT_ATTEST_ALL_AUTHORED_EXAMPLES_OR_SYNONYMS','reviewer_source_verification':'NOT_REVIEWED'})
 with zipfile.ZipFile(dest,'w') as out:
  docs={}
  card_fields=['batch_id','card_id','headword','source_occurrences','primary_source_screenshot','primary_source_row','source_original_ordinals','all_occurrence_ids','all_image_row_locators','all_raw_source_rows','primary_image_sha256','source_claim_tags','course_row_claim_not_equal_authored_example_signoff','additional_same_id_book_refs','source_review_flags','independent_source_review_status']
  item_fields=['batch_id','review_item_id','review_kind','review_item_fingerprint','card_id','headword','source_occurrence_ids','source_image_row_locators','source_claim_tags','claim_boundary','reviewer_source_verification']
  docs['R69-SOURCE-LOCATORS-BY-CARD-292.tsv']=tsv(records,card_fields)
  docs['R69-SOURCE-LOCATORS-BY-REVIEW-ITEM-1411.tsv']=tsv(itemrows,item_fields)
  docs['R69-SOURCE-SCREENSHOT-INVENTORY-11.json']=text_json({'images':list(img.values()),'image_bytes_embedded':False,'original_source_zip_sha256':R66_SHA})
  docs['R69-RETIRED-SOURCE-IDENTITY-0286.json']=text_json({'id':retired['occurrence_id'],'reason':'Historically retired, not missing active card','historical_identity_actions':retired['historical_identity_actions'],'source_locator':retired['locator'],'source_raw_text':retired['raw_text'],'not_linked_to_active_card':True})
  for b in batches_list:
   key=b['batch_id']
   docs[f'Batches/{key}/SOURCE-REFERENCE-{key}.tsv']=tsv([x for x in records if x['batch_id']==key],card_fields)
  report={'schema':'ma2-r69-provenance-companion-report@1','R66_source_sha256':R66_SHA,'R67_batch_zip_sha256':R67_SHA,'R66_review_fingerprint':review['data_fingerprint'],'cards':len(records),'source_occurrences_in_archive':len(originals),'linked_occurrences':len(set(all_links)),'retired_unlinked_occurrences':len(source_left),'distinct_review_items':len(itemrows),'example_items':sum(x['review_kind']=='EXAMPLE' for x in itemrows),'synonym_items':sum(x['review_kind']=='SYNONYM' for x in itemrows),'source_screenshots':len(img),'batch_shards':len(batches_list),'unverified_independent_items':1411,'independent_expert_approvals':0,'content_modified':False,'source_images_repackaged':False,'stage4_final':False,'checks':{'source_hash':'PASS','partition_and_review_fingerprints':'PASS','292_course_source_reference_locators':'PASS','335_links_to_original_occurrences':'PASS','retired_286_explicit':'PASS','11_source_images_SHA256':'PASS'}}
  docs['R69-QA-REPORT.json']=text_json(report)
  docs['README-FA-DE.md']=("""# Menschen A2 Verben — R69 source-fidelity reviewer companion\n\n**Auxiliary, non-content, non-approval tool.** R66 content authoritative; R67 original reviewer batches unchanged; R68 hardened merge remains the acceptance gate.\n\nThis archive maps all 292 active cards and all 1,411 reviewer items to exact course image positions from R66. **Images from the course are not recopied into this handoff**. Authorized reviewers must refer to the 11 unchanged image members in the exact R66 ZIP or user-authorized licensed materials. Image hashes allow local verification.\n\nImportant: source-row attestation is evidence of the **particular original source wording / form**. It does NOT independently verify every newly authored example, Persian/English translation, synonym, sense or register. For all those, make separate qualified judgments. A row can be a collocation or a phrase rather than a full sentence. Do not infer image-visible examples unless you inspect that exact row.\n\n`ma2-occ-0286-00` is deliberately retired in original source occurrence identity actions. No synthetic card added. `source_kind=book` mirrors are not counted as additional images. Historical provenance flags are preserved, not adjudicated by this index.\n\nفارسی: نقشهٔ ارجاع منبع به معنای تأیید مثال‌های نوشته‌شده یا مترادف‌ها نیست. بازبین واجد صلاحیت باید خود تصویر و متن را تطبیق دهد. شناسهٔ ۰۲۸۶ عمداً تاریخی و کنارگذاشته‌شده است. هیچ تصویر یا دادهٔ کارت بازنویسی نشده است.\n\n## Workflow\n1. Take your assigned R67 offline HTML and corresponding `Batches/.../SOURCE-REFERENCE-*.tsv`.\n2. Look up each original source screenshot (`A2-source-NN.png`) and row in the authorized exact R66 archive. Check SHA256 from `R69-SOURCE-SCREENSHOT-INVENTORY-11.json`.\n3. Separately assess semantic DE/FA/EN accuracy and synonyms; export actual reviewer JSON from R67.\n4. Use the R68 hardened merge for actual decision JSON; manual reviewer qualification and independent provenance review are mandatory.\n\n**Never treat this crosswalk, model screening, synthetic PASS, or a checked source locator as independent expert signoff.** Stage4 remains BLOCKED; Stages5/6/7 not run; runtime import unauthorized.\n""").encode('utf8')
  docs['BUILD_R69_SOURCE_CROSSWALK.py']=pathlib.Path(__file__).read_bytes()
  manifest={k:sha(v) for k,v in sorted(docs.items())}
  docs['SHA256SUMS.json']=text_json({'schema':'r69-sha256-manifest@1','hashes':manifest})
  for name in sorted(docs):
   zi=zipfile.ZipInfo(name,date_time=(2026,10,23,9,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.create_system=3;zi.external_attr=0o644<<16
   out.writestr(zi,docs[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 with zipfile.ZipFile(dest) as zz:
  if zz.testzip() is not None:raise ValueError('R69 ZIP CRC failed')
  for n,h in manifest.items():
   if sha(zz.read(n))!=h:raise ValueError('R69 manifest parity '+n)
 print(json.dumps({**report,'artifact_sha256':sha(pathlib.Path(dest).read_bytes()),'artifact_bytes':pathlib.Path(dest).stat().st_size,'artifact_members':len(docs)},indent=2))

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--source',required=True);a.add_argument('--batches',required=True);a.add_argument('--output',required=True);args=a.parse_args();build(args.source,args.batches,args.output)
