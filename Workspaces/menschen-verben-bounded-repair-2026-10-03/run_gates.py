import pathlib,json,sys,subprocess,collections,zipfile,io,csv,copy,hashlib
O=pathlib.Path(__file__).resolve().parent;B=O.parent;F=O/'framework';K=B/'German-Content-Production-Kit';PY=sys.executable
sys.path.insert(0,str(K/'Verification'))
from bounded_content_preflight import self_test,sha,source_errors
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
results=[]
def run(label,args,cwd=None):
 p=subprocess.run([PY,'-B',*map(str,args)],cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
 logs=O/'gate-logs';logs.mkdir(exist_ok=True);(logs/(label+'.txt')).write_text(p.stdout+p.stderr,encoding='utf-8')
 results.append({'name':label,'command':[PY,'-B',*map(str,args)],'exit_status':p.returncode,'status':'PASS' if p.returncode==0 else 'FAIL','log':str(logs/(label+'.txt'))});print(label,results[-1]['status'])
run('kit-memory',[K/'Verification/prevention_preflight.py','memory'])
run('kit-checkpoint',[K/'Verification/prevention_preflight.py','checkpoint',O/'CHECKPOINT.json'])
run('app-currentness',[B/'German-Flashcards-Pro/03-Tests/test-runtime-currentness-policy.py'])
run('app-prevention',[B/'German-Flashcards-Pro/03-Tests/test-prevention-gates.py'])
run('repair-negative-fixtures',[K/'Verification/bounded_content_preflight.py','self-test'])
registry=F/'Architecture/06-REFERENCE-SOURCES/GFP-APPROVED-LANGUAGE-SOURCES-v1.1.0.json'
for level in ['A1','A2','B1']:
 d=O/'staging'/level;pick=lambda text:next(d.glob('*'+text+'*'))
 can=pick('CANONICAL');occ=pick('SOURCE-OCCURRENCES');clo=pick('IDENTITY-CLOSURE');pol=next(x for x in d.glob('*POLICY*.json') if 'LEDGER' not in x.name);matrix=pick('COMPLETENESS');ledger=pick('CANDIDATE-LEDGER');tsv=pick('UNIVERSAL')
 commands=[('source',['validate_source_occurrences_v1_0_0.py',occ]),('identity',['validate_identity_closure_v1_0_0.py',occ,clo,'--canonical',can]),('candidates',['validate_enrichment_candidate_ledger_v1_0_0.py',ledger,'--canonical',can,'--policy',pol,'--source-registry',registry,'--mode','closure']),('completeness',['validate_enrichment_completeness_v1_0_0.py',matrix,'--policy',pol,'--mode','closure','--canonical',can,'--source-registry',registry]),('envelope',['validate_unified_vocabulary_projection_v1_1_0.py',tsv])]
 for n,args in commands:run(level+'-'+n,[F/'Verification'/args[0],*args[1:]])
 run(level+'-projection',[K/'Verification/prevention_preflight.py','projection',tsv])
 run(level+'-lineage',[K/'Verification/prevention_preflight.py','lineage',tsv,'--baseline',O/(level+'-parent-rows.json')])
 if level=='A2':run('A2-source-binding',[K/'Verification/bounded_content_preflight.py','source',occ,'--binding',d/'SOURCE-RAW-BINDING.json','--binding-sha256',load(O/'CHECKPOINT.json')['a2_source_binding_sha256'],'--evidence-root',B/'Audit-Menschen-Final-2026-10-01/source-evidence/A2'])
 # Strict whitelist is independent of the script that changed the content.
 rep=load(d/'BOUNDED-DIFFERENTIAL.json');errors=[]
 allowed_a1={'ma1m-lu-0308':'hat gekostet','ma1m-lu-0335':'hat geholfen','ma1m-lu-0339':'hat gebraucht','ma1m-lu-0340':'hat gefunden','ma1m-lu-0341':'hat gesagt'}
 for x in rep['projection_delta']:
  ok=(level=='A1' and ((x['column']=='custom_fields' and x['field']=='.stage4_canonical_sha256') or (x['id'] in allowed_a1 and x['column']=='custom_fields' and x['field'] in ['.perfect','.canonical_lexeme.morphology.perfect','.canonical_target.structure.morphology.perfect','.vnext_morphology.perfect','.vnext_structure.morphology.perfect'] and x['after']==allowed_a1[x['id']]))) or (level=='B1' and ((x['column']=='notes' and x['after']=='') or (x['id']=='mb1m-lu-0200' and x['column'] in ['related','details'])))
  if not ok:errors.append(x)
 if level in ['A2','B1'] and rep['canonical_delta']:errors.append('UNAUTHORIZED_CANONICAL_CHANGE')
 if level!='A2' and rep['occurrence_delta']:errors.append('UNAUTHORIZED_SOURCE_CHANGE')
 if level=='A1':
  if len(rep['canonical_delta'])!=10 or any(x['after'] not in allowed_a1.values() or not x['field'].endswith('.perfect') for x in rep['canonical_delta']):errors.append('A1_CANONICAL_DELTA')
 if level=='A2':
  if len(rep['occurrence_delta'])!=2 or any(not x['field'].endswith('.raw_text') for x in rep['occurrence_delta']):errors.append('A2_RAW_DELTA')
 before=load(O/(level+'-parent-rows.json'));after=load(O/(level+'-rows.json'));assert [r['id'] for r in before]==[r['id'] for r in after]
 for a,b in zip(before,after):
  for key in ['examples','front','back','source','lesson','deck','order']:
   if a[key]!=b[key]:errors.append(f'{a["id"]}:UNAUTHORIZED_{key}')
  ca,cb=json.loads(a['custom_fields']),json.loads(b['custom_fields'])
  for key in ['canonical_relations','vnext_relations','source_audio_refs','course_memberships','canonical_examples','presentation_examples']:
   if ca.get(key)!=cb.get(key):errors.append(f'{a["id"]}:UNAUTHORIZED_{key}')
 results.append({'name':level+'-strict-differential','status':'FAIL' if errors else 'PASS','errors':errors});print(level+'-strict-differential',results[-1]['status'])
 rep['unexpected_changes']='NONE' if not errors else errors;save(d/'BOUNDED-DIFFERENTIAL.json',rep)
 save(d/'STAGE4-BOUNDED-VERIFICATION.json',{'schema':'bounded-repair-independent-verification@1','status':'PASS' if not errors else 'FAIL','canonical_sha256':rep['canonical_sha256'],'scope':rep['finding_ids'],'path':'strict before/after protected-field comparison separate from repair implementation','not_exhaustive_linguistic_certification':True})
save(O/'GATE-RESULTS.json',{'status':'PASS' if all(r['status']=='PASS' for r in results) else 'FAIL','results':results})
if any(r['status']!='PASS' for r in results):raise SystemExit(1)
