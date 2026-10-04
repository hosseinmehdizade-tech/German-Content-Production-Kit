"""Independent exact-ZIP differential audit; does not call repair functions."""
import pathlib,json,hashlib,zipfile,csv,io,copy,sys,re,subprocess,collections
O=pathlib.Path(__file__).resolve().parent;B=O.parent;PY=sys.executable;K=B/'German-Content-Production-Kit';F=O/'framework'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def rows(b):return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t'))
def read(z,fragment):
 n=next(n for n in z.namelist() if fragment in pathlib.PurePosixPath(n).name and not n.endswith('/'));return n,z.read(n)
spec={'ma1m-lu-0308':'hat gekostet','ma1m-lu-0335':'hat geholfen','ma1m-lu-0339':'hat gebraucht','ma1m-lu-0340':'hat gefunden','ma1m-lu-0341':'hat gesagt'}
receipts=load(O/'PACKAGE-CANDIDATES.json');checkpoint=load(O/'CHECKPOINT.json');out={}
for level,item in receipts.items():
 p=pathlib.Path(item['path']);assert sha(p.read_bytes())==item['sha256'];z=zipfile.ZipFile(p);assert not z.testzip();names=z.namelist();assert len(names)==len(set(names))
 assert all(not re.search(r'__pycache__|\.pyc$|\.pytest_cache|\.git/|\.tmp$|\.bak$|\.DS_Store|Thumbs.db|GFP-v451|CANDIDATE.*\.zip$',n,re.I) for n in names)
 checked=[]
 for line in z.read('SHA256SUMS.txt').decode().splitlines():
  m=re.fullmatch(r'([0-9a-f]{64})  (.+)',line);assert m;digest,name=m.groups();assert sha(z.read(name))==digest;checked.append(name)
 assert sorted(checked)==sorted(n for n in names if n!='SHA256SUMS.txt')
 for n in names:
  if n.endswith('.json'):json.loads(z.read(n).decode('utf-8-sig'))
 manifest=json.loads(z.read('DELIVERY-MANIFEST.json'));meta=json.loads(z.read('BUILD-METADATA.json'))
 assert manifest['runtime_acceptance_target']==checkpoint['CURRENT']=='v455-R89'
 assert meta['data_file']['sha256']==sha(z.read(meta['data_file']['filename']))
 parent=zipfile.ZipFile(checkpoint['parents'][level]['path']);assert sha(pathlib.Path(checkpoint['parents'][level]['path']).read_bytes())==checkpoint['parents'][level]['sha256']
 parent_src=[n for n in parent.namelist() if '/02-Source/Menschen-'+level in n]
 parent_can=next(n for n in parent_src if 'CANONICAL' in n);canname,canbytes=read(z,'CANONICAL');a=json.loads(parent.read(parent_can));b=json.loads(canbytes)
 assert manifest['canonical_sha256']==sha(canbytes)
 pt=next(n for n in parent.namelist() if '/06-Content/vocabulary/' in n and 'UNIVERSAL' in n and n.endswith('.tsv'));before=rows(parent.read(pt));after=rows(z.read(meta['data_file']['filename']))
 assert [x['id'] for x in before]==[x['id'] for x in after]
 canonical_changed=[]
 if level=='A1':
  restored=copy.deepcopy(b)
  for kind,idkey in [('senses','sense_id'),('lexemes','lexeme_id')]:
   by={x[idkey]:x for x in a[kind]}
   for x in restored[kind]:
    original=by[x[idkey]];m=x['structure']['morphology'] if kind=='senses' else x['morphology'];prior=original['structure']['morphology'] if kind=='senses' else original['morphology']
    if m!=prior:
     uid=x['sense_id'] if kind=='senses' else next(s['sense_id'] for s in a['senses'] if s['lexeme_id']==x['lexeme_id'])
     assert uid in spec and m['perfect']==spec[uid] and 'perfect' not in prior;m.pop('perfect');assert m==prior;canonical_changed.append(uid)
  assert restored==a and collections.Counter(canonical_changed)==collections.Counter({k:2 for k in spec})
 else:assert canbytes==parent.read(parent_can),'Native canonical authority bytes drifted'
 note_before=note_after=0;changed_ids=[];relations=vnextgroups=vnextitems=audio=0;zero_audio=[]
 for x,y in zip(before,after):
  ca=json.loads(x['custom_fields']);cb=json.loads(y['custom_fields']);rest=copy.deepcopy(y)
  if x['notes'] and x['notes'].strip()==ca['germanDefinition'].strip():note_before+=1
  if y['notes'] and y['notes'].strip()==cb['germanDefinition'].strip():note_after+=1
  if level=='A1':
   assert cb['stage4_canonical_sha256']==sha(canbytes);cb['stage4_canonical_sha256']=ca['stage4_canonical_sha256']
   if x['id'] in spec:
    assert cb['perfect']==spec[x['id']];cb['perfect']=ca['perfect']
    for morph in [cb['canonical_lexeme']['morphology'],cb['canonical_target']['structure']['morphology'],cb['vnext_morphology'],cb['vnext_structure']['morphology']]:assert morph.pop('perfect')==spec[x['id']]
    changed_ids.append(x['id'])
   assert cb==ca
   rest['custom_fields']=x['custom_fields'];assert rest==x
  elif level=='A2':assert x==y
  else:
   assert ca==cb and x['notes']==ca['germanDefinition'] and y['notes']==''
   rest['notes']=x['notes'];changed_ids.append(x['id'])
   if x['id']=='mb1m-lu-0200':
    assert json.loads(x['related'])==['nachdenken','nachdenken','nachsinnen'];assert json.loads(y['related'])==['nachdenken','nachsinnen'];rest['related']=x['related']
    da,db=json.loads(x['details']),json.loads(y['details']);assert len(da)==len(db)
    for sa,sb in zip(da,db):
     if sa['title']=='Synonyme':assert sa['items']==['nachdenken','nachdenken','nachsinnen'];assert sb['items']==['nachdenken','nachsinnen'];sb['items']=sa['items']
    assert da==db;rest['details']=x['details']
   assert rest==x
  relations+=len(ca['canonical_relations']);groups=ca['vnext_relations'];vnextgroups+=len(groups);vnextitems+=sum(len(g.get('items',[])) for g in groups) if isinstance(groups,list) else 0
  ar=ca.get('source_audio_refs',[]);audio+=len(ar)
  if not ar:zero_audio.append(x['id'])
 assert len(after)=={'A1':310,'A2':292,'B1':395}[level];assert sum(r['category']=='Verb' for r in after)=={'A1':247,'A2':228,'B1':279}[level]
 occname,occbytes=read(z,'SOURCE-OCCURRENCES');oldocc=json.loads(parent.read(next(n for n in parent_src if 'SOURCE-OCCURRENCES' in n)));newocc=json.loads(occbytes)
 if level=='A2':
  restored=copy.deepcopy(newocc);oby={o['occurrence_id']:o for o in oldocc['occurrences']};raw_changes=[]
  for o in restored['occurrences']:
   if o['raw_text']!=oby[o['occurrence_id']]['raw_text']:
    assert o['occurrence_id'] in ['ma2-occ-0070-01','ma2-occ-0154-01'];raw_changes.append({'occurrence_id':o['occurrence_id'],'before':oby[o['occurrence_id']]['raw_text'],'after':o['raw_text']});o['raw_text']=oby[o['occurrence_id']]['raw_text']
  assert restored==oldocc and len(raw_changes)==2 and len(newocc['occurrences'])==336
  assert sha(z.read('SOURCE-RAW-BINDING.json'))==checkpoint['a2_source_binding_sha256']
 else:assert newocc==oldocc;raw_changes=[]
 # Source mapping and source-audio files preserve exact parent bytes.
 for n in names:
  if 'SOURCE-OUTPUT-MAP' in n or 'SOURCE-AUDIO-MAP' in n:
   assert z.read(n)==parent.read(next(x for x in parent_src if pathlib.PurePosixPath(x).name==n))
 fresh=O/'fresh-final'/level;fresh.mkdir(parents=True,exist_ok=True);z.extractall(fresh)
 registry=F/'Architecture/06-REFERENCE-SOURCES/GFP-APPROVED-LANGUAGE-SOURCES-v1.1.0.json';roles={k:fresh/v for k,v in manifest['roles'].items()}
 can=roles['canonical-json'];oc=roles['source-occurrences'];cl=roles['identity-closure'];pol=roles['resolved-enrichment-policy'];ma=roles['enrichment-completeness'];le=roles['enrichment-candidate-ledger'];ts=roles['direct-import-tsv']
 commands=[['validate_source_occurrences_v1_0_0.py',oc],['validate_identity_closure_v1_0_0.py',oc,cl,'--canonical',can],['validate_enrichment_candidate_ledger_v1_0_0.py',le,'--canonical',can,'--policy',pol,'--source-registry',registry,'--mode','closure'],['validate_enrichment_completeness_v1_0_0.py',ma,'--policy',pol,'--mode','closure','--canonical',can,'--source-registry',registry],['validate_unified_vocabulary_projection_v1_1_0.py',ts]]
 executed=[]
 for args in commands:
  cmd=[PY,'-B',str(F/'Verification'/args[0]),*map(str,args[1:])];r=subprocess.run(cmd,capture_output=True,text=True,timeout=60);assert r.returncode==0,r.stdout+r.stderr;executed.append({'command':cmd,'status':'PASS'})
 for args in [['projection',ts],['package',p],['lineage',ts,'--baseline',O/(level+'-parent-rows.json')]]:
  cmd=[PY,'-B',str(K/'Verification/prevention_preflight.py'),*map(str,args)];r=subprocess.run(cmd,capture_output=True,text=True,timeout=30);assert r.returncode==0,r.stdout+r.stderr;executed.append({'command':cmd,'status':'PASS'})
 if level=='B1':assert relations==2526 and audio==439 and zero_audio==['mb1m-lu-0030','mb1m-lu-0363']
 out[level]={'status':'PASS','artifact_sha256':item['sha256'],'checksums':len(checked),'json_parsed':sum(n.endswith('.json') for n in names),'hygiene':'PASS','unexpected_changes':'NONE','stable_ids':'UNCHANGED','cards':len(after),'verbs':sum(r['category']=='Verb' for r in after),'expressions':sum(r['category']=='Expression' for r in after),'examples':sum(len(json.loads(r['examples'])) for r in after),'canonical_relations':relations,'vnext_groups':vnextgroups,'vnext_items':vnextitems,'source_audio_occurrences':audio,'zero_audio_targets':zero_audio,'duplicate_definition_notes_before':note_before,'duplicate_definition_notes_after':note_after,'changed_card_ids':changed_ids,'source_changes':raw_changes,'gates':executed}
 print(level,'PASS',len(after),'cards',relations,'relations',len(checked),'checksums')
(O/'INDEPENDENT-POSTPACKAGE-REAUDIT.json').write_text(json.dumps({'status':'PASS','method':'Independent whitelist and direct exact-parent archive differential; official validators rerun on freshly extracted final bytes','levels':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
