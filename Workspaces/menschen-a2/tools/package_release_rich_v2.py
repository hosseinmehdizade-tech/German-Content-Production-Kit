#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path

def sha(p:Path):
    h=hashlib.sha256();
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workspace',required=True,type=Path);ap.add_argument('--zip',required=True,type=Path);ap.add_argument('--runtime-commit',required=True);ap.add_argument('--runtime-title',required=True);ns=ap.parse_args();w=ns.workspace
    members=[
      ('DIRECT-IMPORT/MENSCHEN-A2-UNIVERSAL-v2.tsv',w/'05-delivery/MENSCHEN-A2-UNIVERSAL-v2.tsv'),
      ('CANONICAL/CANONICAL-ENRICHED.json',w/'02-canonical/CANONICAL-ENRICHED.json'),
      ('CANONICAL/CANONICAL-VALIDATION.json',w/'02-canonical/CANONICAL-VALIDATION.json'),
      ('CANONICAL/NORMALIZATION-DECISIONS.json',w/'02-canonical/NORMALIZATION-DECISIONS.json'),
      ('SOURCE/SOURCE-MANIFEST.json',w/'00-source/SOURCE-MANIFEST.json'),('SOURCE/SOURCE-INVENTORY.json',w/'01-inventory/SOURCE-INVENTORY.json'),('SOURCE/STABLE-ID-MAP.json',w/'01-inventory/STABLE-ID-MAP.json'),('SOURCE/INVENTORY-QA.json',w/'01-inventory/INVENTORY-QA.json'),
      ('EVIDENCE/EVIDENCE-INDEX.json',w/'03-evidence/EVIDENCE-INDEX.json'),('EVIDENCE/EXTERNAL-EVIDENCE-CACHE.json',w/'03-evidence/EXTERNAL-EVIDENCE-CACHE.json'),('EVIDENCE/ENRICHMENT-VALIDATION.json',w/'03-evidence/ENRICHMENT-VALIDATION.json'),('EVIDENCE/PRODUCT-FLOOR-PREFLIGHT.json',w/'03-evidence/PRODUCT-FLOOR-PREFLIGHT.json'),
      ('QA/LINGUISTIC-QA.json',w/'04-qa/LINGUISTIC-QA.json'),('QA/LEXICAL-QUALITY.json',w/'04-qa/LEXICAL-QUALITY.json'),('QA/COVERAGE-REPORT.json',w/'04-qa/COVERAGE-REPORT.json'),('QA/PRODUCT-FLOOR-VALIDATION.json',w/'04-qa/PRODUCT-FLOOR-VALIDATION.json'),
      ('DELIVERY/DELIVERY-VALIDATION.json',w/'05-delivery/DELIVERY-VALIDATION.json'),('DELIVERY/DELIVERY-LOSS-CHECK.json',w/'05-delivery/DELIVERY-LOSS-CHECK.json'),('DELIVERY/LEXICAL-TRANSPORT-VALIDATION.json',w/'05-delivery/LEXICAL-TRANSPORT-VALIDATION.json'),('DELIVERY/BUILD-METADATA.json',w/'05-delivery/BUILD-METADATA.json'),
      ('RUNTIME/RUNTIME-ACCEPTANCE.json',w/'06-runtime/RUNTIME-ACCEPTANCE.json'),('RUNTIME/PRESENTATION-ACCEPTANCE.json',w/'06-runtime/PRESENTATION-ACCEPTANCE.json'),('RUNTIME/PRODUCT-PRESENTATION-ACCEPTANCE.json',w/'06-runtime/PRODUCT-PRESENTATION-ACCEPTANCE.json'),('RUNTIME/IMPORTED-PRODUCT-FLOOR.json',w/'06-runtime/IMPORTED-PRODUCT-FLOOR.json'),('RUNTIME/STAGE6-PROVENANCE.json',w/'06-runtime/STAGE6-PROVENANCE.json'),
      ('AUDIT/THIN-CARD-ROOT-CAUSE-2026-09-02.json',w/'04-qa/THIN-CARD-ROOT-CAUSE-2026-09-02.json'),
      ('BUILD/BUILD-METADATA.json',w/'07-release/BUILD-METADATA.json'),
    ]
    missing=[str(p) for _,p in members if not p.exists()]
    if missing:raise SystemExit('missing release payload: '+', '.join(missing))
    gates=['01-inventory/INVENTORY-QA.json','02-canonical/CANONICAL-VALIDATION.json','03-evidence/ENRICHMENT-VALIDATION.json','03-evidence/PRODUCT-FLOOR-PREFLIGHT.json','04-qa/LINGUISTIC-QA.json','04-qa/LEXICAL-QUALITY.json','04-qa/COVERAGE-REPORT.json','04-qa/PRODUCT-FLOOR-VALIDATION.json','05-delivery/DELIVERY-VALIDATION.json','05-delivery/DELIVERY-LOSS-CHECK.json','05-delivery/LEXICAL-TRANSPORT-VALIDATION.json','06-runtime/RUNTIME-ACCEPTANCE.json','06-runtime/PRESENTATION-ACCEPTANCE.json','06-runtime/PRODUCT-PRESENTATION-ACCEPTANCE.json','06-runtime/IMPORTED-PRODUCT-FLOOR.json','06-runtime/STAGE6-PROVENANCE.json']
    for rel in gates:
        o=load(w/rel);st=o.get('status') or o.get('structural_typed_status')
        if st!='PASS':raise SystemExit(f'gate not PASS: {rel}: {st}')
    rr=load(w/'06-runtime/RUNTIME-ACCEPTANCE.json')
    if rr.get('runtime_commit')!=ns.runtime_commit or rr.get('import_state')!='IMPORT_VERIFIED' or rr.get('canonical_roundtrip')!='LOSSLESS_DEEP_COPY' or rr.get('persistence')!='reload-survived':raise SystemExit('runtime acceptance identity/state mismatch')
    payload=[{'path':a,'size':p.stat().st_size,'sha256':sha(p)} for a,p in members]
    manifest={'artifact_type':'gfp-content-release-manifest','manifest_version':'2.0.0','dataset':'menschen-a2','title':'Menschen A2','cards':292,'source_rows':297,'runtime':ns.runtime_title,'runtime_commit':ns.runtime_commit,'runtime_sha256':rr.get('runtime_sha256'),'semantic_contract':'gfp-german-language-content@3.1.3','delivery_profile':'flashcards-pro-universal-v2@1.0.1','product_floor':'german-rich-card-product-floor@1.0.0','direct_import_sha256':sha(w/'05-delivery/MENSCHEN-A2-UNIVERSAL-v2.tsv'),'canonical_sha256':sha(w/'02-canonical/CANONICAL-ENRICHED.json'),'stage6_import_state':'IMPORT_VERIFIED','canonical_roundtrip':'LOSSLESS_DEEP_COPY','payload':payload}
    rdir=w/'07-release';rdir.mkdir(parents=True,exist_ok=True);(rdir/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(ns.zip,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for a,p in members:z.write(p,a)
        z.writestr('MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');z.writestr('README.txt','Menschen A2 rich-card release\nDirect import: DIRECT-IMPORT/MENSCHEN-A2-UNIVERSAL-v2.tsv\nCanonical: CANONICAL/CANONICAL-ENRICHED.json\n')
    problems=[]
    with zipfile.ZipFile(ns.zip,'r') as z:
        names=z.namelist()
        if len(names)!=len(set(names)):problems.append('duplicate member')
        for e in payload:
            if e['path'] not in names:problems.append('missing '+e['path']);continue
            b=z.read(e['path'])
            if hashlib.sha256(b).hexdigest()!=e['sha256']:problems.append('hash '+e['path'])
            if len(b)!=e['size']:problems.append('size '+e['path'])
        emb=json.loads(z.read('MANIFEST.json').decode('utf-8'))
        if emb!=manifest:problems.append('embedded manifest mismatch')
        tsv=z.read('DIRECT-IMPORT/MENSCHEN-A2-UNIVERSAL-v2.tsv').decode('utf-8-sig').splitlines();can=json.loads(z.read('CANONICAL/CANONICAL-ENRICHED.json').decode('utf-8'))
        if len(tsv)-1!=292:problems.append('TSV row count')
        if len(can.get('learning_units',[]))!=292:problems.append('canonical unit count')
    post={'status':'PASS' if not problems else 'FAIL','verifier':'package_release_rich_v2 internal close-reopen verifier','zip':ns.zip.name,'zip_sha256':sha(ns.zip),'zip_size':ns.zip.stat().st_size,'payload_files_verified':len(payload),'problems':problems}
    (rdir/'POST-PACKAGE-VERIFICATION.json').write_text(json.dumps(post,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sums=[f'{sha(ns.zip)}  {ns.zip.name}']+[f"{e['sha256']}  {e['path']}" for e in payload];(rdir/'SHA256SUMS.txt').write_text('\n'.join(sums)+'\n',encoding='utf-8')
    print(json.dumps(post,ensure_ascii=False,indent=2));return 0 if not problems else 1
if __name__=='__main__':raise SystemExit(main())
