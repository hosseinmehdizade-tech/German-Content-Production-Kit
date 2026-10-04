import pathlib, json, hashlib, zipfile, shutil, csv, io, copy, sys
sys.stdout.reconfigure(encoding='utf-8')
O=pathlib.Path(__file__).resolve().parent; B=O.parent
sys.path.insert(0,str(B/'German-Content-Production-Kit/Verification'))
from bounded_content_preflight import unique_display, sha
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def h(p):return sha(p.read_bytes())
def j(d):return json.dumps(d,ensure_ascii=False,separators=(',',':'))
def diff(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  for k in sorted(a.keys()|b.keys()):
   yield from diff(a.get(k,'<ABSENT>'),b.get(k,'<ABSENT>'),path+'.'+k)
 elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
  for i,(x,y) in enumerate(zip(a,b)):yield from diff(x,y,path+f'[{i}]')
 elif a!=b:yield {'field':path,'before':a,'after':b}
def rehash(d,old,new):
 if isinstance(d,dict):return {k:rehash(v,old,new) for k,v in d.items()}
 if isinstance(d,list):return [rehash(v,old,new) for v in d]
 return new if d==old else d
cp=load(O/'CHECKPOINT.json')
cp.update(project_memory='PROJECT-MEMORY.json',git_sync_policy='GIT-SYNC-POLICY.json',prevention_refs=['CP-MEM-001','CP-MEM-003','CP-MEM-004','CP-MEM-006'])
spec={'ma1m-lu-0308':'hat gekostet','ma1m-lu-0335':'hat geholfen','ma1m-lu-0339':'hat gebraucht','ma1m-lu-0340':'hat gefunden','ma1m-lu-0341':'hat gesagt'}
identity={'starting_runtime':load(B/'German-Flashcards-Pro/RUNTIME-AUTHORITY-PIN.json')['current_runtime'],'inputs':{}}
summary={}
for level in ['A1','A2','B1']:
 root=O/'parents'/level/'GFP-v451-R85';src=next((root/'02-Source').glob('Menschen-'+level+'*'));dest=O/'staging'/level;dest.mkdir(parents=True,exist_ok=True)
 for p in src.iterdir():
  if p.is_file() and p.name not in ['SOURCE-IDENTITY.json','IMMUTABLE-PARENT-LINEAGE-SNAPSHOT.json'] and 'STAGE4-INDEPENDENT-QA' not in p.name:shutil.copy2(p,dest/p.name)
 can=next(dest.glob('*CANONICAL*.json'));occ=next(dest.glob('*SOURCE-OCCURRENCES*.json'));clo=next(dest.glob('*IDENTITY-CLOSURE*.json'));matrix=next(dest.glob('*ENRICHMENT-COMPLETENESS*.json'));ledger=next(dest.glob('*CANDIDATE-LEDGER*.json'))
 original=load(can);canonical=copy.deepcopy(original);original_occ=load(occ);occurrences=copy.deepcopy(original_occ)
 old_sha=h(can);rows=load(O/(level+'-parent-rows.json'));newrows=copy.deepcopy(rows)
 tsv=next((root/'06-Content').rglob('*UNIVERSAL*.tsv'));newtsv=dest/tsv.name
 if level=='A1':
  affected_lex={x['lexeme_id'] for x in canonical['senses'] if x['sense_id'] in spec}
  for x in canonical['lexemes']:
   if x['lexeme_id'] in affected_lex:
    target=next(s for s in canonical['senses'] if s['lexeme_id']==x['lexeme_id']);x['morphology']['perfect']=spec[target['sense_id']]
  for x in canonical['senses']:
   if x['sense_id'] in spec:x['structure']['morphology']['perfect']=spec[x['sense_id']]
  save(can,canonical);new_sha=h(can)
  for p in [clo,matrix,ledger]:save(p,rehash(load(p),old_sha,new_sha))
  md=load(matrix);md['identity_closure_sha256']=h(clo);save(matrix,md)
  for r in newrows:
   cf=json.loads(r['custom_fields']);cf['stage4_canonical_sha256']=new_sha
   if r['id'] in spec:
    value=spec[r['id']];cf['perfect']=value
    cf['canonical_lexeme']['morphology']['perfect']=value
    cf['canonical_target']['structure']['morphology']['perfect']=value
    cf['vnext_morphology']['perfect']=value;cf['vnext_structure']['morphology']['perfect']=value
   r['custom_fields']=j(cf)
 if level=='A2':
  finding=next(x for x in load(B/'German-Content-Production-Kit/Workspaces/menschen-verben-independent-final-audit-2026-10-01/FINDINGS.json')['findings'] if x['finding_id']=='AUD-004')
  binding={'schema':'source-raw-evidence-binding@1','finding':'AUD-004','review':'Independent audit plus direct visual recheck 2026-10-03','scope':'two confirmed raw_text defects; no full transcription certification','bindings':[]}
  registered=load(B/'German-Content-Production-Kit/Workspaces/menschen-a2/00-source/SOURCE-MANIFEST.json')
  for x in finding['actual_behavior']:
   image=B/'Audit-Menschen-Final-2026-10-01/source-evidence/A2'/x['source_image'];assert h(image)==x['source_image_sha256']
   o=next(o for o in occurrences['occurrences'] if o['occurrence_id']==x['occurrence_id']);assert o['raw_text']==x['packaged_raw_text'];o['raw_text']=x['registered_transcription']
   assert next(i for i in registered['screenshots'] if i['image_index']==o['locator']['screenshot_index'])['sha256']==h(image)
   binding['bindings'].append({'occurrence_id':o['occurrence_id'],'raw_text':o['raw_text'],'raw_text_sha256':sha(o['raw_text'].encode()),'locator':{k:o['locator'][k] for k in ['source_order','screenshot_index','row_index']},'source_image':image.name,'source_image_sha256':h(image)})
  save(dest/'SOURCE-RAW-BINDING.json',binding);save(occ,occurrences)
  d=load(clo);d['source_occurrences_sha256']=h(occ);d['source_raw_binding_sha256']=h(dest/'SOURCE-RAW-BINDING.json');save(clo,d)
  d=load(matrix);d['identity_closure_sha256']=h(clo);save(matrix,d)
  cp['a2_source_binding_sha256']=h(dest/'SOURCE-RAW-BINDING.json')
 if level=='B1':
  for r in newrows:
   cf=json.loads(r['custom_fields']);assert r['notes'].strip()==cf['germanDefinition'].strip();r['notes']=''
   if r['id']=='mb1m-lu-0200':
    related=json.loads(r['related']);assert related==['nachdenken','nachdenken','nachsinnen'];r['related']=j(unique_display(related))
    details=json.loads(r['details'])
    for s in details:
     if s['title']=='Synonyme':s['items']=unique_display(s['items'])
    r['details']=j(details)
 # A2 transport bytes remain exact. Other levels retain all unaffected columns.
 if newrows==rows:shutil.copy2(tsv,newtsv)
 else:
  stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(newrows);newtsv.write_text(stream.getvalue(),encoding='utf-8')
 deltas=[]
 for a,b in zip(rows,newrows):
  for key in a:
   av,bv=a[key],b[key]
   if key in ['custom_fields','details','related','opposites','examples']:av,bv=json.loads(av),json.loads(bv)
   deltas.extend({'id':a['id'],'column':key,**x} for x in diff(av,bv))
 report={'level':level,'parent':cp['parents'][level],'canonical_delta':list(diff(original,canonical)),'occurrence_delta':list(diff(original_occ,occurrences)),'projection_delta':deltas,'counts':{'cards':len(rows),'verbs':sum(r['category']=='Verb' for r in rows),'expressions':sum(r['category']=='Expression' for r in rows),'examples':sum(len(json.loads(r['examples'])) for r in rows),'canonical_relations':len(original.get('relations',[])) or sum(len(json.loads(r['custom_fields'])['canonical_relations']) for r in rows)},'canonical_sha256':h(can),'source_occurrences_sha256':h(occ),'projection_sha256':h(newtsv),'finding_ids':{'A1':['AUD-003'],'A2':['AUD-004'],'B1':['AUD-005','AUD-006']}[level],'runtime_acceptance_target':'v455-R89','unexpected_changes':'PENDING_INDEPENDENT_CHECK'}
 save(dest/'BOUNDED-DIFFERENTIAL.json',report)
 save(dest/'STAGE4-BOUNDED-VERIFICATION.json',{'schema':'bounded-repair-independent-verification@1','status':'PENDING','canonical_sha256':h(can),'scope':report['finding_ids'],'not_exhaustive_linguistic_certification':True})
 (dest/'README.md').write_text(f'Menschen {level} Verben bounded repair successor. Framework v3.3.6. Parent {cp["parents"][level]["filename"]}, SHA256 {cp["parents"][level]["sha256"]}. Runtime acceptance target CURRENT v455-R89, runtime finality separate. Import the ZIP through the current app Vocabulary import. Only {", ".join(report["finding_ids"])} are repaired. Canonical/native differences retained.\n',encoding='utf-8')
 # Inherited native importer metadata, refreshed only for this new dataset.
 z=zipfile.ZipFile(cp['parents'][level]['path']);nested=next(n for n in z.namelist() if '/06-Content/vocabulary/Menschen-'+level in n and n.endswith('.zip'))
 nz=zipfile.ZipFile(io.BytesIO(z.read(nested)));meta=json.loads(nz.read('BUILD-METADATA.json').decode('utf-8-sig'))
 meta.update(data_build_id=f'menschen-{level.lower()}-bounded-repair-20261003',prompt_version='v3.3.6',validator_version='GCPK-v3.3.6-BOUNDED-CONTENT-REPAIR',build_timestamp='2026-10-03',runtime_projection_target='CURRENT-v455-R89',note='Bounded AUD-003..AUD-006 repair successor from exact immutable parent; minimal content delta; exact runtime acceptance recorded in external sidecar.')
 meta['data_file']['filename']=newtsv.name;meta['data_file']['sha256']=h(newtsv)
 meta['immutable_parent']={k:cp['parents'][level][k] for k in ['filename','sha256','bytes']};meta['repair_findings']=report['finding_ids'];save(dest/'BUILD-METADATA.json',meta)
 save(O/(level+'-rows.json'),newrows);identity['inputs'][level]={'count':len(rows),'path':str(newtsv),'sha256':h(newtsv),'parent_sha256':cp['parents'][level]['sha256']}
 summary[level]={'cards':len(rows),'canonical_changes':len(report['canonical_delta']),'raw_changes':len(report['occurrence_delta']),'projection_changes':len(deltas),'changed_ids':sorted(set(x['id'] for x in deltas if x['field']!='.stage4_canonical_sha256'))}
cp.update(status='REPAIRED_CANDIDATE_PENDING_VALIDATION',next_action='Run official and differential gates, exact CURRENT runtime acceptance, package and independent post-package reaudit',summary=summary)
save(O/'CHECKPOINT.json',cp);save(O/'INPUT-IDENTITY.json',identity)
print(json.dumps({l:{k:v for k,v in d.items() if k!='changed_ids'} for l,d in summary.items()},indent=2))
