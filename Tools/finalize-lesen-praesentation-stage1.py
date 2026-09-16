#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
WS=ROOT/'Workspaces'/'lesen-praesentation';INV=WS/'01-inventory'/'SOURCE-INVENTORY.json';MAP=WS/'01-inventory'/'STABLE-ID-MAP.json';QA=WS/'01-inventory'/'INVENTORY-QA.json';MAN=WS/'00-source'/'SOURCE-MANIFEST.json';CP=WS/'CHECKPOINT.json'
SOURCE_ID='presentation-topics-b2-c1';SOURCE_SHA='7abebcb70213a89a50a3bab35695618adde0b44a9975fdf9cdba33c296ef5523'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def analyze(inv):
    topics=inv.get('topics') or [];counts=inv.get('counts') or {};sp=inv.get('special_cases') or {}
    ids=[str(x.get('stable_id') or '') for x in topics];orders=[x.get('source_order') for x in topics];starts=[x.get('page_start') for x in topics]
    cont=[x.get('page') for x in sp.get('continuation_pages') or []];blank=list(sp.get('blank_pages') or []);dupes=[x.get('page') for x in sp.get('duplicate_occurrences') or []]
    all_classified=starts+cont+blank+dupes
    checks={
      'source_id_matches':inv.get('source_id')==SOURCE_ID,
      'source_sha256_matches':inv.get('source_sha256')==SOURCE_SHA,
      'topic_count_68':len(topics)==68 and counts.get('topics')==68,
      'stable_ids_unique':len(ids)==len(set(ids))==68,
      'stable_ids_sequential':ids==[f'lesen-praes-{i:04d}' for i in range(1,69)],
      'source_order_sequential':orders==list(range(1,69)),
      'topic_start_pages_unique':len(starts)==len(set(starts))==68 and counts.get('topic_start_pages')==68,
      'continuation_pages_match':cont==[18,20,22,26,32,38] and counts.get('continuation_pages')==6,
      'blank_page_match':blank==[3] and counts.get('blank_pages')==1,
      'duplicate_page_match':dupes==[69] and counts.get('duplicate_occurrence_pages')==1,
      'unnumbered_topic_start_match':list(sp.get('unnumbered_topic_start_pages') or [])==[35],
      'all_pdf_pages_classified_once':len(all_classified)==76 and len(set(all_classified))==76 and sorted(all_classified)==list(range(1,77)) and counts.get('pdf_pages')==76,
      'page_ranges_valid':all(isinstance(x.get('page_start'),int) and isinstance(x.get('page_end'),int) and 1<=x['page_start']<=x['page_end']<=76 for x in topics),
      'labels_present':all(str(x.get('label_text_nfc') or '').strip() for x in topics),
    }
    return topics,checks

def build_evidence():
    inv=load(INV);topics,checks=analyze(inv);failed=[k for k,v in checks.items() if not v]
    if failed:raise SystemExit('Inventory QA failed: '+', '.join(failed))
    stable={'schema_version':'gcpk.stable-id-map.v1','dataset':'lesen-praesentation','source_id':SOURCE_ID,'source_sha256':SOURCE_SHA,'identity_policy':'Stable IDs are source-order identities and do not depend on transient ChatGPT file IDs.','count':len(topics),'mappings':[{'stable_id':x['stable_id'],'source_order':x['source_order'],'page_start':x['page_start'],'page_end':x['page_end'],'label_text_nfc':x['label_text_nfc'],'source_number_token':x.get('source_number_token'),'heading_kind':x.get('heading_kind')} for x in topics]};write(MAP,stable)
    qa={'schema_version':'gcpk.inventory-qa.v1','dataset':'lesen-praesentation','source_id':SOURCE_ID,'source_sha256':SOURCE_SHA,'status':'PASS','checks':checks,'summary':{'pdf_pages':76,'topics':68,'topic_start_pages':68,'continuation_pages':6,'blank_pages':1,'duplicate_occurrence_pages':1,'unnumbered_topic_start_pages':[35]},'evidence':{'source_inventory':'01-inventory/SOURCE-INVENTORY.json','source_inventory_sha256':sha(INV),'stable_id_map':'01-inventory/STABLE-ID-MAP.json','stable_id_map_sha256':sha(MAP)},'scope':'Stage 1 source boundary/order/identity QA only; no claim is made about Stage 2+ canonical learning content.'};write(QA,qa)
    cp=load(CP);s1=cp['stages'][0];s1['state']='RUNNING';s1['summary']='Source inventory, stable ID map and inventory QA evidence are generated and pass local deterministic checks. Stage 1 remains RUNNING until this evidence is committed; a subsequent promotion commit must reference that durable evidence commit.';s1['pass_commit']=None;cp['resume_instruction']='Commit Stage 1 inventory evidence, then promote Stage 1 to PASS using the exact evidence commit. Do not begin Stage 2 before that durable promotion.';write(CP,cp)
    man=load(MAN);man['stage1_status'].update({'state':'RUNNING','source_identity_verified':True,'project_library_byte_equivalence_verified':True,'inventory_built':True,'stable_id_map_built':True,'inventory_qa_passed':True,'evidence_committed':False});man['inventory']={'pdf_pages':76,'topics':68,'topic_start_pages':68,'continuation_pages':[18,20,22,26,32,38],'blank_pages':[3],'duplicate_occurrence_pages':[69],'unnumbered_topic_start_pages':[35],'source_inventory':'../01-inventory/SOURCE-INVENTORY.json','stable_id_map':'../01-inventory/STABLE-ID-MAP.json','inventory_qa':'../01-inventory/INVENTORY-QA.json'};man['notes']='Source identity and Project Source/Library byte equivalence are verified. Stage 1 evidence is generated from the committed source-faithful inventory; promotion to PASS is deferred until that evidence itself has a durable Git commit.';write(MAN,man)
    print(json.dumps({'status':'EVIDENCE_PASS_PENDING_GIT','topics':68,'stable_id_map_sha256':sha(MAP),'inventory_qa_sha256':sha(QA)},ensure_ascii=False))

def promote(evidence_commit):
    inv=load(INV);_,checks=analyze(inv)
    if not all(checks.values()):raise SystemExit('Cannot promote: inventory checks no longer pass')
    if not MAP.exists() or not QA.exists() or load(QA).get('status')!='PASS':raise SystemExit('Cannot promote: durable QA artifacts missing')
    cp=load(CP);s1=cp['stages'][0];s1['state']='PASS';s1['summary']='Source identity and byte equivalence verified; source-faithful inventory has 68 topics across 76 PDF pages; stable IDs lesen-praes-0001..0068 are durable; inventory QA passes including continuation, blank, duplicate-occurrence and unnumbered-topic special cases.';s1['pass_commit']=evidence_commit;cp['resume_instruction']='Stage 1 is PASS. Continue with Stage 2 Canonicalization only when new canonical reading-content work is required; do not overwrite Grammar/Vocabulary workstreams. R45 may reuse already validated R43 derived runtime content while keeping this source lineage authoritative.';cp['stage1_evidence_commit']=evidence_commit;cp['stage1_evidence']=['01-inventory/SOURCE-INVENTORY.json','01-inventory/STABLE-ID-MAP.json','01-inventory/INVENTORY-QA.json'];write(CP,cp)
    man=load(MAN);man['stage1_status'].update({'state':'PASS','inventory_built':True,'stable_id_map_built':True,'inventory_qa_passed':True,'evidence_committed':True,'evidence_commit':evidence_commit});man['notes']='Stage 1 Source & Inventory is durably PASS. Raw copyrighted PDF remains outside Git; Git stores source identity/provenance and derived inventory evidence only.';write(MAN,man)
    print(json.dumps({'status':'STAGE1_PASS','evidence_commit':evidence_commit,'checkpoint':str(CP.relative_to(ROOT))},ensure_ascii=False))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--promote-pass',metavar='EVIDENCE_COMMIT');a=ap.parse_args();promote(a.promote_pass) if a.promote_pass else build_evidence()
if __name__=='__main__':main()
