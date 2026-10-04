import json, pathlib, zipfile, hashlib, csv, io, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE=pathlib.Path(__file__).resolve().parents[1]
OUT=pathlib.Path(__file__).resolve().parent
def load(p): return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def digest(b): return hashlib.sha256(b).hexdigest()
def save(p,v): pathlib.Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
parents={}
for level,sha in [('A1','6b00aa750b182403bc6cd0cb33d45feca354d811501833cb9fa0960f1af4956c'),('A2','6fc8ce3de42c3914856c8e4225a1c1b842aa7d7379b1e7a3c8707ab862a19366'),('B1','ed2d61a01abcbc27791c80519a4bccefa0325a008fc5ebbf3e1042739a523c57')]:
 p=next(pathlib.Path('C:/Users/hosse/Downloads').glob(f'German-Flashcards-Pro-v451-R85-Menschen-{level}-Verben-v3.3.6*RELOCKED (1).zip'))
 assert digest(p.read_bytes())==sha
 parents[level]={'path':str(p),'filename':p.name,'sha256':sha,'bytes':p.stat().st_size,'immutable':True}
 z=zipfile.ZipFile(p); assert z.testzip() is None
 dst=OUT/'parents'/level; dst.mkdir(parents=True,exist_ok=True);z.extractall(dst)
 root=dst/'GFP-v451-R85'; src=next((root/'02-Source').glob(f'Menschen-{level}*'))
 files=[x for x in src.iterdir() if x.is_file()]
 print(level,'SOURCE FILES',[x.name for x in files])
 can=next(x for x in files if 'CANONICAL' in x.name);d=load(can)
 print('CANONICAL',can.name,[(k,len(v) if isinstance(v,(list,dict)) else str(v)[:80]) for k,v in d.items()])
 tsv=next((root/'06-Content').rglob('*UNIVERSAL*.tsv'));rows=list(csv.DictReader(io.StringIO(tsv.read_text(encoding='utf-8-sig')),delimiter='\t'))
 print('TSV',str(tsv.relative_to(root)),len(rows))
 save(OUT/(level+'-parent-rows.json'),rows)
 ids={'A1':['ma1m-lu-0308','ma1m-lu-0335','ma1m-lu-0339','ma1m-lu-0340','ma1m-lu-0341'],'A2':['ma2-lu-0070','ma2-lu-0154'],'B1':['mb1m-lu-0200']}[level]
 for r in rows:
  if r['id'] in ids:
   cf=json.loads(r['custom_fields']); print('TARGET',r['id'],{k:r[k] for k in ['front','notes','related','details']})
   print('CF KEYS',list(cf))
   for k in ['morphology','canonical_lexeme','canonical_target','canonical_unit','canonical_relations']:
    if k in cf: print(k,json.dumps(cf[k],ensure_ascii=False)[:2000])
 if level=='A2':
  occ=load(next(x for x in files if 'SOURCE-OCCURRENCES' in x.name))
  for x in occ['occurrences']:
   if x['occurrence_id'] in ['ma2-occ-0070-01','ma2-occ-0154-01']: print('OCC',json.dumps(x,ensure_ascii=False))
checkpoint={'schema':'bounded-content-repair@1','date':'2026-10-03','scope':['AUD-003','AUD-004','AUD-005','AUD-006'],'status':'AUTHORITY_RESOLVED_REPAIR_NOT_STARTED','parents':parents,'starting_authority':{'app':{'branch':'main','head':'32659a6eda14851f8443a14a0781708c3c13e030','remote':'32659a6eda14851f8443a14a0781708c3c13e030','worktree':'untracked 06-Runtime preserved'},'kit':{'branch':'main','head':'cab6ae364b7dc24f724bc7eb684959d722d4ffa4','remote':'268b434e273fb0f39a0fb4ffd90131fcd3d3675c','worktree':'clean; fast-forwarded to fetched remote'}},'CURRENT':'v455-R89','LAST_FULLY_VERIFIED':'v451-R85','framework':'v3.3.6','next_action':'Apply bounded content delta after exact source and contract inspection','persistence':{'git':'PENDING'}}
save(OUT/'CHECKPOINT.json',checkpoint)
f=load(BASE/'German-Content-Production-Kit/Workspaces/menschen-verben-independent-final-audit-2026-10-01/FINDINGS.json')
for x in f['findings']:
 if x['finding_id']=='AUD-004':print('AUD004',json.dumps(x,ensure_ascii=False))
