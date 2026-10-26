// Pure synthetic/nonmutating regression suite. Never reads user's browser profile.
// Run: node B1-24-SRS-LOSSLESS-DRYRUN-PREFLIGHT-v1.TEST.mjs
import {planB1Import} from "./B1-24-SRS-LOSSLESS-DRYRUN-PREFLIGHT-v1.mjs";
const protectedSix=[
  ["mb1m-lu-2293","B1-L15","allumfassend","adjective"],
  ["mb1m-lu-2839","B1-L19","allumfassend","adjective"],
  ["mb1m-lu-0918","B1-L04","trotzdem","adverb"],
  ["mb1m-lu-1900","B1-L12","trotzdem","adverb"],
  ["mb1m-lu-2974","B1-L20","Vorschrift","noun"],
  ["mb1m-lu-4049","B1-L23","Vorschrift","noun"]
];
const seeded=protectedSix.map(([id,lesson,lemma,pos])=>({id,lesson,lemma,pos}));
for(let n=1;seeded.length<3089;n++){
  const id="mb1m-lu-"+String(n).padStart(4,"0");
  if(seeded.some(x=>x.id===id))continue;
  seeded.push({id,lesson:"B1-L"+String((n-1)%24+1).padStart(2,"0"),lemma:"fixture-"+n,pos:"fixture"});
}
const records=[...seeded];
for(let i=0;i<43;i++)records.push({...seeded[i+6],lesson:"B1-L"+String((i+10)%24+1).padStart(2,"0")});
for(let i=0;i<5;i++)records.push({...seeded[i+6],lesson:"B1-L"+String((i+17)%24+1).padStart(2,"0")});
for(const m of records)m.examples=Array.from({length:4},(_,i)=>({
  id:"E:"+m.id+":"+i,de:"Test Deutsch "+i,fa:"آزمایش فارسی "+i,en:"Test English "+i
}));
const assertions=[];
function check(name,fn,expectFail=false){
  try{fn();assertions.push({name,passed:!expectFail})}
  catch(e){assertions.push({name,passed:expectFail,error:String(e).slice(0,140)})}
}
const fresh={target:"NEW_LIBRARY_DRY_RUN"},live={target:"EXISTING_PROFILE_DRY_RUN"};
const good=planB1Import(records,null,fresh);
const assert=x=>{if(!x)throw Error("ASSERTION_FAILURE")};
check("3137 rows / 3089 distinct IDs / 12548 complete trilingual groups",()=>assert(good.counts.membershipRows===3137&&good.counts.distinctIds===3089&&good.counts.exampleGroups===12548));
check("43 reused ID groups / 48 extra memberships",()=>assert(good.counts.reusedIdGroups===43&&good.counts.reusedMembershipRows===48));
check("three real alias pairs blocked; no automatic alias",()=>assert(good.holds.length===3&&!good.auto_alias_executed));
check("192 scoped source example ID collisions repaired only in dryrun map",()=>assert(good.counts.sourceExampleIdCollisionRows===192&&good.counts.derivedExampleIdsUnique===12548));
const srs={records:Array.from({length:101},(_,i)=>({id:records[i].id,rating:i%5,interval:i+1,history:[i,i+1]}))},snapshot=JSON.stringify(srs);
const livePlan=planB1Import(records,srs,live);
check("dry-run never changes snapshot JSON",()=>assert(JSON.stringify(srs)===snapshot&&!livePlan.mutation_performed));
check("101 seeded SRS records held for separate protected import",()=>assert(livePlan.counts.preexistingSrsOverlappingIds===101&&livePlan.status==="HOLD_EXISTING_PROFILE_ALL_WRITES_DISABLED"));
check("missing existing profile snapshot rejected",()=>planB1Import(records,null,live),true);
check("same lesson+card duplicate rejected",()=>planB1Import([...records,records[0]],null,fresh),true);
check("missing learner Persian translation rejected",()=>{const c=records.slice();c[0]={...c[0],examples:c[0].examples.map((e,i)=>i?e:{...e,fa:""})};planB1Import(c,null,fresh)},true);
check("lesson outside B1-L01..L24 rejected",()=>{const c=records.slice();c[0]={...c[0],lesson:"B1-L25"};planB1Import(c,null,fresh)},true);
check("three instead of four examples rejected",()=>{const c=records.slice();c[0]={...c[0],examples:c[0].examples.slice(0,3)};planB1Import(c,null,fresh)},true);
check("protected Vorschrift L23 membership missing rejected",()=>planB1Import(records.filter(x=>!(x.id==="mb1m-lu-4049"&&x.lesson==="B1-L23")),null,fresh),true);
check("protected historic stable card ID rewrite rejected",()=>{const c=records.slice();c[0]={...c[0],id:"mb1m-lu-9999"};planB1Import(c,null,fresh)},true);
check("wrong profile schema rejected",()=>planB1Import(records,{cards:[]},live),true);
check("duplicate existing SRS record rejected",()=>planB1Import(records,{records:[{id:"x"},{id:"x"}]},live),true);
check("duplicate source example ID within same lesson rejected",()=>{const c=records.slice();c[1]={...c[1],lesson:c[0].lesson,examples:c[1].examples.map((e,i)=>i?e:{...e,id:c[0].examples[0].id})};planB1Import(c,null,fresh)},true);
const failed=assertions.filter(x=>!x.passed);
console.log(JSON.stringify({schema:"b1-24-synthetic-srs-regression@1.0.0",scope:"SYNTHETIC_ONLY_NO_REAL_SRS_NO_ZIP_EXECUTED",passed:assertions.length-failed.length,total:assertions.length,failed},null,2));
if(failed.length)process.exitCode=1;