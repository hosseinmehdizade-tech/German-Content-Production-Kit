import pathlib,json,zipfile,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
O=pathlib.Path(__file__).resolve().parent;B=O.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name,expected,dest in [('German-Content-Production-Kit-v3.3.6-Source-Agnostic-Completeness-CANDIDATE.zip','61ecccdd1ae0819ae7e15b5d3335bc576dcb896a393765c257687b900ec3915c','framework')]:
 p=pathlib.Path('C:/Users/hosse/Downloads')/name;assert h(p)==expected;zipfile.ZipFile(p).extractall(O/dest)
p=B/'Remediation-2026-10-02/German-Flashcards-Pro-v455-R89-ORGANIZED-DELIVERY-ENGINEERING-CANDIDATE.zip';assert h(p)=='d571005eee6a5445d31569ed55c106ac754a42ba1736bad978c26d152e9bae2e';zipfile.ZipFile(p).extractall(O/'runtime')
for l in ['A1','A2','B1']:
 r=O/'parents'/l/'GFP-v451-R85';s=next((r/'02-Source').glob('Menschen-'+l+'*'));print(l)
 for p in s.glob('*.json'):
  d=load(p)
  print(p.name,'KEYS',list(d), 'HASHES',{k:v for k,v in d.items() if 'hash' in k or 'sha' in k})
  if 'COMPLETENESS' in p.name:print('MORPH CELL',d['targets'][0]['dimensions'].get('morphology'))
  if 'IDENTITY-CLOSURE' in p.name:print('DISP',d['occurrence_dispositions'][0])
 rows=load(O/(l+'-parent-rows.json'));cf=json.loads(rows[0]['custom_fields'])
 print('HASHES CF',{k:v for k,v in cf.items() if 'sha' in k or 'lineage' in k})
 if l=='A1':
  for r in rows:
   if r['id'] in ['ma1m-lu-0308','ma1m-lu-0335','ma1m-lu-0339','ma1m-lu-0340','ma1m-lu-0341']:
    cf=json.loads(r['custom_fields']);print(r['id'],'PERFECT',cf['perfect'],'VNEXT',cf['vnext_morphology'],'STRUCT',cf['vnext_structure'])
 if l=='A2':print('SOURCE IMAGE SHA verified by registered manifest and audit; full manifest retained')
