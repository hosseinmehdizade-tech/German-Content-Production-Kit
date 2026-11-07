/* Executes exact currently pinned v505 reading-content-import-v38.js source in Node vm.
 * Only pre-entry validation/in-memory projection; NO actual browser or IndexedDB stage6.
 */
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const [,,modulePath,oldPath,newPath,outPath]=process.argv;
function check(ok,label){if(!ok)throw new Error(label)}
const src=fs.readFileSync(modulePath,'utf8');
const window={GFP_LEARNING_CORE_V48:{readingUnits:()=>[],readingExercises:()=>[],readingUnitById:()=>null,readingForTarget:()=>[],registryStats:()=>({}),gradeExercise:()=>null}};
const doc={readyState:'loading',addEventListener:()=>{},getElementById:()=>null};
const ctx={window,document:doc,console,structuredClone,setTimeout,clearTimeout,MutationObserver:class {observe(){}}};
vm.createContext(ctx);vm.runInContext(src,ctx,{filename:'exact-current-v505-reading-content-import-v38.js'});
const api=window.GFP_READING_CONTENT_V423;
check(api&&typeof api.validate==='function','v505 source validator missing');
const old=JSON.parse(fs.readFileSync(oldPath,'utf8'));
const pack=JSON.parse(fs.readFileSync(newPath,'utf8'));
const oldRes=api.validate(old),good=api.validate(pack);
const neg=[];
function probe(name,mut){const p=structuredClone(pack);mut(p);const r=api.validate(p);const z={name,rejected:r.status==='FAIL',errors:r.errors.slice(0,4)};neg.push(z);check(z.rejected,'BAD INPUT ACCEPTED: '+name)}
probe('duplicate lesson source id',p=>p.entries[1].source_item_id=p.entries[0].source_item_id);
probe('missing Persian translation',p=>p.entries[52].unit.passages[1].translations.fa='');
probe('wrong comprehension exercise id',p=>p.entries[52].unit.comprehension_exercise_ids[1]='broken_q02');
probe('corrupt grammar position',p=>p.entries[52].unit.r38.grammar.full_text_occurrences[0].start+=1);
probe('remove model answer',p=>p.entries[52].exercises[3].answer_spec.model_answer='');
probe('corrupt grammar declared total',p=>p.counts.full_text_grammar+=1);
probe('corrupt new r18 manual relative span',p=>{const g=p.entries[52].unit.r38.grammar.full_text_occurrences.find(x=>x.id==='ftg-r18-053-p02-scoped');check(Boolean(g),'R18 exact grammar span not found');g.start+=1});
check(oldRes.status==='PASS','Previously verified R17 parent failed v505 source validator');
check(good.status==='PASS','Candidate failed v505 source validation: '+good.errors.join(';'));
check(good.warnings.length===0,'Unexpected native warnings: '+good.warnings.join(';'));
check(good.counts.entries===68&&good.counts.questions===340&&good.counts.fullTextGrammar===4041,'Native validated counts mismatch');
const isolatedRecord={id:'runtime',version:4,revision:1,updated_at:'2026-11-07T00:00:00Z',entries:pack.entries,lexical_targets:[],imports:[]};
api.validateRecord(isolatedRecord);
const projection=api.adoptCommittedMirrorV505(isolatedRecord);
check(projection.units===68&&projection.exercises===340,'In memory current v505 projection mismatch');
check(api.snapshot().units===68&&api.snapshot().exercises===340,'In memory v505 snapshot mismatch');
const evidence={schema:'lesen-v505-native-source-preentry-r18@1',date:'2026-11-07',module_sha256:crypto.createHash('sha256').update(src).digest('hex'),
source_module:'exact pinned v505 Wordlinks R3 01-App/modules/reading-content-import-v38.js',
checks:{baseline_pack_status:oldRes.status,candidate_pack_status:good.status,candidate_warnings:good.warnings,
actual_native_counts:good.counts,negative_cases:neg,all_7_negative_rejected:neg.length===7&&neg.every(x=>x.rejected),
isolated_record_validation:'PASS',in_memory_projection:projection,actual_db_transaction:'NOT_RUN'},
status:'PASS_EXACT_CURRENT_V505_JS_VALIDATOR_ONLY__NO_BROWSER_STAGE6',source_import_or_db_mutations:false};
fs.writeFileSync(outPath,JSON.stringify(evidence,null,2)+'\n');console.log(JSON.stringify(evidence,null,2));