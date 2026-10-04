"""Windows-portable equivalent of the mandatory v3.3.6 anti-bypass builder.

Runs the same five authoritative validators plus supplemental prevention and
lineage gates BEFORE creating any ZIP. No alternative bypass flag exists.
"""
import pathlib,json,hashlib,sys,subprocess,zipfile,shutil
O=pathlib.Path(__file__).resolve().parent;B=O.parent;F=O/'framework';K=B/'German-Content-Production-Kit';PY=sys.executable
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert load(O/'GATE-RESULTS.json')['status']=='PASS'
receipts={};output=O/'artifacts';output.mkdir(exist_ok=True)
for level,repair in [('A1',3),('A2',3),('B1',2)]:
 d=O/'staging'/level;pick=lambda text:next(d.glob('*'+text+'*'))
 roles={'direct-import-tsv':pick('UNIVERSAL'),'canonical-json':pick('CANONICAL'),'source-output-map-tsv':pick('SOURCE-OUTPUT-MAP'),'qa-report':d/'STAGE4-BOUNDED-VERIFICATION.json','source-occurrences':pick('SOURCE-OCCURRENCES'),'identity-closure':pick('IDENTITY-CLOSURE'),'resolved-enrichment-policy':next(x for x in d.glob('*POLICY*.json') if 'LEDGER' not in x.name),'enrichment-completeness':pick('COMPLETENESS'),'enrichment-candidate-ledger':pick('CANDIDATE-LEDGER')}
 c=roles;registry=F/'Architecture/06-REFERENCE-SOURCES/GFP-APPROVED-LANGUAGE-SOURCES-v1.1.0.json'
 commands=[['validate_source_occurrences_v1_0_0.py',c['source-occurrences']],['validate_identity_closure_v1_0_0.py',c['source-occurrences'],c['identity-closure'],'--canonical',c['canonical-json']],['validate_enrichment_candidate_ledger_v1_0_0.py',c['enrichment-candidate-ledger'],'--canonical',c['canonical-json'],'--policy',c['resolved-enrichment-policy'],'--mode','closure','--source-registry',registry],['validate_enrichment_completeness_v1_0_0.py',c['enrichment-completeness'],'--policy',c['resolved-enrichment-policy'],'--mode','closure','--canonical',c['canonical-json'],'--source-registry',registry],['validate_unified_vocabulary_projection_v1_1_0.py',c['direct-import-tsv']]]
 for args in commands:
  p=subprocess.run([PY,'-B',str(F/'Verification'/args[0]),*map(str,args[1:])],capture_output=True,text=True,timeout=60);assert p.returncode==0,p.stdout+p.stderr
 for mode,args in [('projection',[]),('lineage',['--baseline',O/(level+'-parent-rows.json')])]:
  p=subprocess.run([PY,'-B',str(K/'Verification/prevention_preflight.py'),mode,str(c['direct-import-tsv']),*map(str,args)],capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stdout+p.stderr
 assert load(c['qa-report'])['status']=='PASS'
 meta=load(d/'BUILD-METADATA.json');meta['note']='Bounded AUD-003..AUD-006 repair successor from exact immutable parent; minimal delta; exact runtime acceptance and finality recorded in external sidecar.';save(d/'BUILD-METADATA.json',meta)
 cp=load(O/'CHECKPOINT.json');lineage={'schema':'bounded-content-lineage@1','immutable_parent':cp['parents'][level],'framework':'v3.3.6','repair_number':repair,'finding_ids':load(d/'BOUNDED-DIFFERENTIAL.json')['finding_ids'],'canonical_sha256':h(c['canonical-json']),'source_occurrences_sha256':h(c['source-occurrences']),'projection_sha256':h(c['direct-import-tsv']),'runtime_target':cp['CURRENT'],'runtime_artifact_sha256':'d571005eee6a5445d31569ed55c106ac754a42ba1736bad978c26d152e9bae2e','LAST_FULLY_VERIFIED':cp['LAST_FULLY_VERIFIED'],'presentation_changed':False,'canonical_relation_authority_preserved':True}
 save(d/'SOURCE-LINEAGE.json',lineage)
 shutil.copy2(K/'Verification/bounded_content_preflight.py',d/'bounded_content_preflight.py')
 man={'artifact_type':'clean-content-delivery','delivery_policy':'v3.3.6-source-agnostic-enrichment-completeness','builder':'package_repair.py equivalent: identical official five gates before ZIP, plus current projection/lineage gates','unified_vocabulary_validation':'PASS_EMBEDDED_BUILDER_GATE','enrichment_completeness_validation':'PASS_EMBEDDED_BUILDER_GATE','identity_closure_validation':'PASS_EMBEDDED_BUILDER_GATE','candidate_ledger_validation':'PASS_EMBEDDED_BUILDER_GATE','required_card_type':'de-vocabulary','required_presentation_contract':'gfp-vocabulary-neutral@1','canonical_sha256':h(c['canonical-json']),'roles':{k:v.name for k,v in c.items()},'runtime_acceptance_target':cp['CURRENT'],'package_control':'CANDIDATE; final post-package acceptance is external sidecar','immutable_parent_sha256':cp['parents'][level]['sha256']}
 save(d/'DELIVERY-MANIFEST.json',man)
 files=sorted(p for p in d.iterdir() if p.is_file() and p.name!='SHA256SUMS.txt');(d/'SHA256SUMS.txt').write_text(''.join(f'{h(p)}  {p.name}\n' for p in files),encoding='utf-8')
 name=f'Menschen-{level}-Verben-v3.3.6-Repair{repair}-GFP-v455-CANDIDATE.zip';out=output/name
 assert not out.exists(),'Immutable output already exists: choose a new attempt identity'
 with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(d.iterdir()):
   if p.is_file():
    info=zipfile.ZipInfo(p.name,date_time=(2026,10,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 shutil.copy2(out,O/(level+'-input.zip'))
 receipts[level]={'filename':name,'path':str(out),'sha256':h(out),'bytes':out.stat().st_size,'repair':repair,'status':'CANDIDATE_POSTPACKAGE_ACCEPTANCE_REQUIRED'}
 print(level,receipts[level]['sha256'],receipts[level]['bytes'])
save(O/'PACKAGE-CANDIDATES.json',receipts)
