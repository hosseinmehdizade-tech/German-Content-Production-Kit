#!/usr/bin/env python3
"""Reproducible whole-lesson QA: compares curated parent to L02 phase2 ZIP, no release approval.
Usage: python qa_L02_phase2_verify_v1.py <parent-owner.zip> <new-owner.zip> [report.json]
"""
import sys,zipfile,json,hashlib,re,collections,pathlib
PRE='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
MAP='G2-LEXICAL-BATCH13-1548-SOURCE-MAP-UNMODIFIED.tsv'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def norm(x):return re.sub(r'\W+','',x.casefold())
def cards(z):return [json.loads(s) for s in z.read(PRE).splitlines()]
def run(p,q):
 with zipfile.ZipFile(p) as a, zipfile.ZipFile(q) as archive:
  assert a.testzip() is None and archive.testzip() is None,'corrupt ZIP'
  assert a.read(MAP)==archive.read(MAP),'source map changed'
  ar=cards(a);br=cards(archive);assert len(ar)==len(br)==1571
  lookup={c['preview_card_id']:c for c in ar}
  assert set(lookup)=={c['preview_card_id'] for c in br}
  before={c['source_ordinal']:c for c in ar if c['lesson']=='L02'}
  after={c['source_ordinal']:c for c in br if c['lesson']=='L02'}
  assert len(before)==len(after)==91 and set(after)==set(range(72,163))
  changed=[];oldmissing=0;newmissing=0;en_before=en_after=0
  sense_new=0;extra_network_cards=0;attested_added=0;dup_local=0;linked=0
  for c in br:
   if c['lesson']!='L02':
    assert c==lookup[c['preview_card_id']],('non-L02 changed',c['preview_card_id'])
    continue
   prev=before[c['source_ordinal']]
   if prev!=c:changed.append(c['source_ordinal'])
   assert c['source_row_provenance']==prev['source_row_provenance']
   assert c['curated_HOLD_content_disposition_exists']==prev['curated_HOLD_content_disposition_exists']
   assert not c['formal_release_approved'] and not c['import_ready']
   b=c['back'];pb=prev['back'];now=(b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
   old=(pb.get('existing_examples_de_fa_pending_qa') or [])+(pb.get('additional_examples_de_fa_pending_qa') or [])
   en_before+=len(old);en_after+=len(now)
   oldmissing+=sum(not e.get('status') for e in old);newmissing+=sum(not e.get('status') for e in now)
   for e in now:assert e.get('de') and e.get('fa')
   nets=b.get('semantic_network_sense_anchored_pending_qa') or []
   prenets=pb.get('semantic_network_sense_anchored_pending_qa') or []
   if nets and not prenets:extra_network_cards+=1;sense_new+=len(nets)
   if nets:
    ids={n['sense_id'] for n in nets};assert all(e.get('sense_id') in ids for e in now),(c['source_ordinal'],'sense route')
    linked+=len(now)
   assert b.get('Formen_section') is None
   if not prev['front'].get('morphology_independently_validated') and c['front'].get('morphology_independently_validated'):attested_added+=1
   ct=collections.Counter(norm(e['de']) for e in now)
   dup_local+=sum(1 for v in ct.values() if v>1)
  assert len(changed)==32,(len(changed),changed)
  assert en_before==197 and en_after==199
  assert oldmissing==12 and newmissing==0
  assert extra_network_cards==27 and sense_new==60
  assert attested_added==11 and dup_local==0
  oldglob=sum(1 for c in ar for n in collections.Counter(norm(e['de']) for e in ((c['back'].get('existing_examples_de_fa_pending_qa') or [])+(c['back'].get('additional_examples_de_fa_pending_qa') or []))).values() if n>1)
  glob=sum(1 for c in br for n in collections.Counter(norm(e['de']) for e in ((c['back'].get('existing_examples_de_fa_pending_qa') or [])+(c['back'].get('additional_examples_de_fa_pending_qa') or []))).values() if n>1)
  assert oldglob==7 and glob==6
  members=[s for s in archive.namelist() if s!='SHA256SUMS.txt']
  entries=archive.read('SHA256SUMS.txt').decode().splitlines()
  assert len(members)==len(entries)
  for ln in entries:
   digest,name=ln.split('  ',1);assert sha(archive.read(name))==digest,(name,'manifest hash')
  return {'schema':'aspekte-b1plus-L02-phase2-whole-lesson-gates@1','result':'PASS_STRUCTURAL_EDITORIAL_NONIMPORT','parent_owner_sha256':sha(pathlib.Path(p).read_bytes()),'new_owner_sha256':sha(pathlib.Path(q).read_bytes()),'cards_scanned_global':len(br),'L02_cards_scanned':len(after),'L02_changed_card_count':len(changed),'L02_unchanged':91-len(changed),'L02_new_network_cards':extra_network_cards,'L02_new_sense_blocks':sense_new,'L02_examples_before':en_before,'L02_examples_after':en_after,'L02_missing_example_status_before':oldmissing,'L02_missing_example_status_after':newmissing,'L02_new_Duden_scoped_form_attestations':attested_added,'L02_local_duplicate_groups':dup_local,'corpus_legacy_duplicate_groups_before':oldglob,'corpus_legacy_duplicate_groups_after':glob,'original_source_map_byte_identical':True,'outside_L02_objects_unchanged':True,'zip_crc_pass':True,'manifest_checks':len(entries),'full_independent_release_approved':0,'real_app_import_tested':False,'import_ready':False}
if __name__=='__main__':
 out=run(sys.argv[1],sys.argv[2]); print(json.dumps(out,ensure_ascii=False,indent=2))
 if len(sys.argv)>3:pathlib.Path(sys.argv[3]).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')