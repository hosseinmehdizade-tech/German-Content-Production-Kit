#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--workspace',required=True,type=Path); ap.add_argument('--zip',required=True,type=Path); ap.add_argument('--manifest',required=True,type=Path); ap.add_argument('--sha256s',required=True,type=Path); ap.add_argument('--postverify',required=True,type=Path); ns=ap.parse_args(); w=ns.workspace
 members=[
  ('DIRECT-IMPORT/MENSCHEN-A2-UNIVERSAL-v2.tsv',w/'05-delivery/MENSCHEN-A2-UNIVERSAL-v2.tsv'),
  ('CANONICAL/CANONICAL-ENRICHED.json',w/'02-canonical/CANONICAL-ENRICHED.json'),
  ('SOURCE/SOURCE-INVENTORY.json',w/'01-inventory/SOURCE-INVENTORY.json'),
  ('SOURCE/STABLE-ID-MAP.json',w/'01-inventory/STABLE-ID-MAP.json'),
  ('QA/LINGUISTIC-QA.json',w/'04-qa/LINGUISTIC-QA.json'),
  ('QA/LEXICAL-QUALITY.json',w/'04-qa/LEXICAL-QUALITY.json'),
  ('QA/COVERAGE-REPORT.json',w/'04-qa/COVERAGE-REPORT.json'),
  ('DELIVERY/DELIVERY-VALIDATION.json',w/'05-delivery/DELIVERY-VALIDATION.json'),
  ('DELIVERY/DELIVERY-LOSS-CHECK.json',w/'05-delivery/DELIVERY-LOSS-CHECK.json'),
  ('RUNTIME/RUNTIME-ACCEPTANCE.json',w/'06-runtime/RUNTIME-ACCEPTANCE.json'),
  ('RUNTIME/PRESENTATION-ACCEPTANCE.json',w/'06-runtime/PRESENTATION-ACCEPTANCE.json'),
  ('BUILD/BUILD-METADATA.json',w/'05-delivery/BUILD-METADATA.json'),
 ]
 missing=[str(p) for _,p in members if not p.exists()]
 if missing: raise SystemExit('missing release payload: '+', '.join(missing))
 payload=[{'path':arc,'size':p.stat().st_size,'sha256':sha(p)} for arc,p in members]
 manifest={'artifact_type':'gfp-content-release-manifest','manifest_version':'1.0.0','dataset':'menschen-a2','title':'Menschen A2','runtime':'German Flashcards Pro v354','runtime_commit':'49a28187e82734e92bc407276eb0d2ee0cbbbd55','semantic_contract':'gfp-german-language-content@3.1.3','delivery_profile':'flashcards-pro-universal-v2@1.0.1','payload':payload}
 ns.manifest.parent.mkdir(parents=True,exist_ok=True); ns.manifest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 ns.zip.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(ns.zip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for arc,p in members: z.write(p,arc)
  z.writestr('MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 # independent post-package verification
 problems=[]
 with zipfile.ZipFile(ns.zip,'r') as z:
  names=set(z.namelist())
  for arc,p in members:
   if arc not in names: problems.append(f'missing {arc}'); continue
   data=z.read(arc); h=hashlib.sha256(data).hexdigest(); exp=sha(p)
   if h!=exp: problems.append(f'hash mismatch {arc}')
   if len(data)!=p.stat().st_size: problems.append(f'size mismatch {arc}')
  try:
   mz=json.loads(z.read('MANIFEST.json').decode('utf-8'))
   if mz!=manifest: problems.append('embedded manifest mismatch')
  except Exception as e: problems.append('manifest parse: '+str(e))
  tsv=z.read('DIRECT-IMPORT/MENSCHEN-A2-UNIVERSAL-v2.tsv').decode('utf-8-sig').splitlines()
  if len(tsv)-1!=292: problems.append(f'TSV row count {len(tsv)-1}')
  try:
   can=json.loads(z.read('CANONICAL/CANONICAL-ENRICHED.json').decode('utf-8'))
   if len(can.get('learning_units',[]))!=292: problems.append('canonical count mismatch')
  except Exception as e: problems.append('canonical parse: '+str(e))
 post={'status':'PASS' if not problems else 'FAIL','zip':ns.zip.name,'zip_sha256':sha(ns.zip),'verified_payload_files':len(members),'tsv_rows':292,'canonical_units':292,'problems':problems}
 ns.postverify.write_text(json.dumps(post,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 sums=[f"{sha(ns.zip)}  {ns.zip.name}"]+[f"{x['sha256']}  {x['path']}" for x in payload]
 ns.sha256s.write_text('\n'.join(sums)+'\n',encoding='utf-8')
 print(json.dumps(post,ensure_ascii=False,indent=2)); raise SystemExit(0 if post['status']=='PASS' else 1)
if __name__=='__main__': main()
