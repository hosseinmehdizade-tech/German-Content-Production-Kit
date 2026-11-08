// Exact v505 source-native preentry validation in an isolated Node VM.
// NO browser, IndexedDB transaction or user progress. Source SHA verified by launcher.
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const dir='/mnt/data/lesen_r19_20261108';
const modulePath=dir+'/reading-content-import-v38.js';
const runtimePath=dir+'/Lesen-R19-v505-10P06-RUNTIME-PREENTRY-CANDIDATE.json';
const source=fs.readFileSync(modulePath,'utf8');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
if(sha(source)!=='b03f954a9e617d918d42eeddbf0cd4da5a3c1bc3d43d9e57977312dbbde071bc') throw Error('Native v505 source mismatched');
const pack=JSON.parse(fs.readFileSync(runtimePath,'utf8'));
const env={window:{GFP_LEARNING_CORE_V48:{readingUnits:()=>[],readingExercises:()=>[],readingUnitById:()=>null,readingForTarget:()=>[],registryStats:()=>({})}},document:{readyState:'loading',addEventListener:()=>{},getElementById:()=>null},console:{warn:()=>{},log:()=>{},error:()=>{}},setTimeout:()=>0,clearTimeout:()=>{}};
vm.createContext(env);
vm.runInContext(source,env,{filename:modulePath,timeout:2000});
const api=env.window.GFP_READING_CONTENT_V423;
if(!api||typeof api.validate!=='function') throw Error('Exact current v505 importer validate unavailable');
let res=api.validate(pack);
if(res.status!=='PASS'||res.errors.length||res.warnings.length)throw Error('R19 v505 source validator failure: '+JSON.stringify(res).slice(0,1800));
if(res.counts.entries!==68||res.counts.passages!==478||res.counts.questions!==340||res.counts.vocabulary!==350||res.counts.fullTextGrammar!==4011)throw Error('Unexpected native validation counts '+JSON.stringify(res.counts));
const clone=x=>JSON.parse(JSON.stringify(x));
const variants=[
 ['wrong schema',p=>{p.schema_version='lesen.content.v1.3.0'}],
 ['duplicate item id',p=>{p.entries[11].source_item_id=p.entries[10].source_item_id}],
 ['duplicate runtime unit',p=>{p.entries[11].unit.reading_unit_id=p.entries[10].unit.reading_unit_id}],
 ['missing Persian',p=>{p.entries[10].unit.passages[5].translations.fa=''}],
 ['missing English',p=>{p.entries[10].unit.passages[5].translations.en=''}],
 ['broken p06 fulltext offset',p=>{p.entries[10].unit.r38.grammar.full_text_occurrences[0].start=9999}],
 ['wrong question count',p=>{p.entries[10].exercises.pop()}],
 ['wrong exercise target',p=>{p.entries[10].exercises[0].target_object_ids=['unknown_unit']}],
 ['wrong grammar count',p=>{p.counts.full_text_grammar++}],
 ['invalid source title',p=>{p.entries[10].unit.title=''}],
];
const negatives=variants.map(([name,mutate])=>{const x=clone(pack);mutate(x);const test=api.validate(x);return {name,rejected:test.status==='FAIL'&&test.errors.length>0,errors:test.errors.slice(0,2)};});
if(negatives.some(x=>!x.rejected))throw Error('v505 native negative test not detected '+JSON.stringify(negatives));
const snapshot={id:'runtime',version:4,revision:1,updated_at:'2026-11-08T00:00:00.000Z',entries:pack.entries,lexical_targets:pack.lexical_targets||[],imports:[]};
api.validateRecord(snapshot);
const projection=api.adoptCommittedMirrorV505(snapshot);
if(projection.units!==68||projection.exercises!==340)throw Error('In-memory projection failure '+JSON.stringify(projection));
const diag=api.diagnostics();
if(diag.units!==68||diag.exercises!==340)throw Error('In-memory native diagnostic mismatch');
const report={schema:'lesen-r19-current-v505-native-source-preentry@1',date:'2026-11-08',status:'PASS_EXACT_CURRENT_V505_JS_VALIDATOR_ONLY__NO_BROWSER_STAGE6',current_v505_source_sha256:sha(source),candidate_runtime_sha256:sha(fs.readFileSync(runtimePath)),validation:res,negative_probes:negatives.map(v=>({name:v.name,rejected:v.rejected,errors:v.errors})),in_memory_projection:projection,diagnostics:{units:diag.units,exercises:diag.exercises},boundaries:['Exact current v505 JS source validated (not emulated hand-written importer)','Node VM only; no live browser, IndexedDB persistence, user data or Stage6 transaction','No full independent semantic Stage4 or final Stage7 release']};
fs.writeFileSync(dir+'/LESEN-R19-v505-NATIVE-PREENTRY.json',JSON.stringify(report,null,2)+'\n');
process.stdout.write(JSON.stringify({status:report.status,source_sha:report.current_v505_source_sha256,counts:res.counts,warnings:res.warnings.length,native_negatives_rejected:negatives.filter(v=>v.rejected).length,projection},null,2)+'\n');