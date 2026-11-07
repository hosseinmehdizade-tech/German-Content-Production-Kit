/* Execute the exact v505 reading-content-import-v38.js from the current runtime ZIP.
 * Browser DOM/IndexedDB are deliberately NOT invoked; this tests only its actual
 * pre-entry source validator and explicitly does NOT claim Stage6 native import.
 */
'use strict';
const fs=require('fs'), vm=require('vm'),crypto=require('crypto');
const [,,modulePath,oldPath,newPath,outputPath]=process.argv;
function check(b, message){if(!b)throw new Error(message)}
const src=fs.readFileSync(modulePath,'utf8');
const window={GFP_LEARNING_CORE_V48:{readingUnits:()=>[],readingExercises:()=>[],readingUnitById:()=>null,readingForTarget:()=>[],registryStats:()=>({}),gradeExercise:()=>null}};
const doc={readyState:'loading',addEventListener:()=>{},getElementById:()=>null};
const ctx={window,document:doc,console,structuredClone,setTimeout,clearTimeout,MutationObserver:class {observe(){}}};
vm.createContext(ctx);vm.runInContext(src,ctx,{filename:'exact-v505-reading-content-import-v38.js'});
const api=window.GFP_READING_CONTENT_V423;check(api&&typeof api.validate==='function','Native v505 validator unavailable');
const old=JSON.parse(fs.readFileSync(oldPath,'utf8'));
const pack=JSON.parse(fs.readFileSync(newPath,'utf8'));
const oldRes=api.validate(old),good=api.validate(pack);
const probes=[];
function neg(label,edit){const p=structuredClone(pack);edit(p);const got=api.validate(p);const row={name:label,rejected:got.status==='FAIL',errors:got.errors.slice(0,4)};probes.push(row);check(row.rejected,'negative probe NOT rejected: '+label)}
neg('duplicate source_item_id',p=>{p.entries[1].source_item_id=p.entries[0].source_item_id});
neg('missing Persian section translation',p=>{p.entries[34].unit.passages[0].translations.fa=''});
neg('wrong comprehension exercise id reference',p=>{p.entries[34].unit.comprehension_exercise_ids[1]='lesen_broken_q02'});
neg('broken r38 grammar offset',p=>{p.entries[34].unit.r38.grammar.full_text_occurrences[0].start+=1});
neg('missing question answer',p=>{p.entries[50].exercises[3].answer_spec.model_answer=''});
neg('wrong declared fulltext grammar count',p=>{p.counts.full_text_grammar+=1});
neg('invalid R9 changed p04 grammar offset',p=>{const g=p.entries[10].unit.r38.grammar.full_text_occurrences.find(x=>x.id==='ftg-r9-011-p04-k2-advice');g.start+=1});
check(oldRes.status==='PASS','Historical payload should PASS exact native parser');
check(good.status==='PASS','New payload rejected: '+good.errors.join('; '));
check(good.warnings.length===0,'New pack unexpected native warnings: '+good.warnings.join('; '));
check(good.counts.entries===68&&good.counts.questions===340&&good.counts.fullTextGrammar===pack.counts.full_text_grammar,'Incorrect native reported counts');
const isolatedRecord={id:'runtime',version:4,revision:1,updated_at:'2026-11-07T00:00:00Z',entries:pack.entries,lexical_targets:[],imports:[]};
api.validateRecord(isolatedRecord);
const memoryProjection=api.adoptCommittedMirrorV505(isolatedRecord);
check(memoryProjection.units===68&&memoryProjection.exercises===340,'In-memory isolated v505 record projection counts mismatch');
check(api.snapshot().units===68&&api.snapshot().exercises===340,'v505 snapshot inconsistency');
const evidence={schema:'lesen-v505-native-source-preentry@1',module_sha256:crypto.createHash('sha256').update(src).digest('hex'),source_module:'exact CURRENT v505 Wordlinks R3 01-App/modules/reading-content-import-v38.js',checks:{baseline_pack_status:oldRes.status,candidate_pack_status:good.status,candidate_warnings:good.warnings,actual_native_counts:good.counts,negative_cases:probes,all_7_negative_rejected:probes.length===7&&probes.every(x=>x.rejected),isolated_record_validation:"PASS",in_memory_projection:memoryProjection,actual_db_transaction:"NOT_RUN"},status:'PASS_EXACT_CURRENT_V505_JS_VALIDATOR_ONLY__NO_BROWSER_STAGE6',source_import_or_db_mutations:false};
fs.writeFileSync(outputPath,JSON.stringify(evidence,null,2)+'\n');
console.log(JSON.stringify(evidence,null,2));