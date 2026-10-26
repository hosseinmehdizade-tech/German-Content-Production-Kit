// Mensch B1 L01-L24 v3.3.6 nonmutating dry-run identity/SRS guard.
// No live IndexedDB, file writes, or ID aliases. Receives normalized JSON memberships.
// Important: synthetically tested, NOT executed on user profile or actual final B1 ZIP.
export function planB1Import(memberships, srsSnapshot=null, opts={}) {
  const expected=opts.expected??{membershipRows:3137,distinctIds:3089,exampleGroups:12548,reusedIdGroups:43,reusedMembershipRows:48,exampleIdCollisions:192};
  const heldAliases=[
    {lemma:"allumfassend",pos:"adjective",items:[["B1-L15","mb1m-lu-2293"],["B1-L19","mb1m-lu-2839"]]},
    {lemma:"trotzdem",pos:"adverb",items:[["B1-L04","mb1m-lu-0918"],["B1-L12","mb1m-lu-1900"]]},
    {lemma:"Vorschrift",pos:"noun",items:[["B1-L20","mb1m-lu-2974"],["B1-L23","mb1m-lu-4049"]]}
  ];
  function fail(message){throw new Error("B1_FAIL_CLOSED:"+message)}
  if(!Array.isArray(memberships)||!memberships.length)fail("EMPTY_OR_INVALID_MEMBERSHIPS");
  if(opts.target!=="NEW_LIBRARY_DRY_RUN"&&opts.target!=="EXISTING_PROFILE_DRY_RUN")fail("EXPLICIT_DRY_RUN_TARGET_REQUIRED");
  const ids=new Map(),members=new Set(),exampleSeen=new Map(),examples=[],countsByLesson=new Map();
  for(const m of memberships){
    if(!m||typeof m.id!=="string"||!/^mb1m-lu-\d{4}$/.test(m.id))fail("MALFORMED_ID");
    if(typeof m.lesson!=="string"||!/^B1-L(0[1-9]|1[0-9]|2[0-4])$/.test(m.lesson))fail("MALFORMED_LESSON");
    if(!Array.isArray(m.examples)||m.examples.length!==4)fail("FOUR_EXAMPLES_REQUIRED");
    if(!String(m.lemma||"").trim()||!String(m.pos||"").trim())fail("LEMMA_POS_REQUIRED");
    const membershipKey=m.lesson+"|"+m.id;
    if(members.has(membershipKey))fail("DUPLICATE_MEMBERSHIP:"+membershipKey);
    members.add(membershipKey);
    if(!ids.has(m.id))ids.set(m.id,[]);
    ids.get(m.id).push(m);
    countsByLesson.set(m.lesson,(countsByLesson.get(m.lesson)||0)+1);
    const perMembershipIds=new Set();
    for(let i=0;i<4;i++){
      const e=m.examples[i];
      if(!e||typeof e.id!=="string"||!e.id.trim())fail("EXAMPLE_ID_MISSING");
      for(const lang of ["de","fa","en"])if(typeof e[lang]!=="string"||!e[lang].trim())fail("TRILINGUAL_FIELD_MISSING:"+lang);
      if(perMembershipIds.has(e.id))fail("DUPLICATE_SOURCE_EXAMPLE_ID_WITHIN_MEMBERSHIP");
      perMembershipIds.add(e.id);
      const perLessonKey=m.lesson+"|"+e.id;
      if(exampleSeen.has(perLessonKey))fail("EXAMPLE_ID_COLLISION_WITHIN_LESSON:"+perLessonKey);
      exampleSeen.set(perLessonKey,true);
      examples.push({lesson:m.lesson,cardId:m.id,sourceExampleId:e.id,de:e.de,fa:e.fa,en:e.en});
    }
  }
  const reused=[...ids.values()].filter(x=>x.length>1);
  const reuseExtra=reused.reduce((s,x)=>s+x.length-1,0);
  if(memberships.length!==expected.membershipRows)fail("CARD_ROW_COUNT_EXPECTED_"+expected.membershipRows);
  if(ids.size!==expected.distinctIds)fail("DISTINCT_ID_COUNT_EXPECTED_"+expected.distinctIds);
  if(examples.length!==expected.exampleGroups)fail("EXAMPLE_COUNT_EXPECTED_"+expected.exampleGroups);
  if(reused.length!==expected.reusedIdGroups||reuseExtra!==expected.reusedMembershipRows)fail("REUSE_GROUP_COUNT_MISMATCH");
  if(countsByLesson.size!==24)fail("NOT_ALL_24_LESSONS");
  for(const pair of heldAliases){
    for(const [lesson,id] of pair.items) {
      const records=ids.get(id)||[];
      if(!records.some(x=>x.lesson===lesson))fail("REQUIRED_PROTECTED_ALIAS_ID_MISSING:"+lesson+"|"+id);
    }
    if(pair.items[0][1]===pair.items[1][1])fail("PROTECTED_ALIAS_MERGED");
  }
  // Four examples per card membership must remain independently recoverable.
  // A repeated example source-ID is scoped to a lesson, never silently overwritten.
  const exampleFrequency=new Map();
  for(const e of examples)exampleFrequency.set(e.sourceExampleId,(exampleFrequency.get(e.sourceExampleId)||0)+1);
  const duplicatedSourceExampleRows=[...exampleFrequency.values()].reduce((s,n)=>s+Math.max(0,n-1),0);
  if(duplicatedSourceExampleRows!==expected.exampleIdCollisions)fail("EXAMPLE_COLLISION_COUNT_MISMATCH");
  const used=new Set(),derived=[];
  for(const e of examples){
    const id=exampleFrequency.get(e.sourceExampleId)>1?e.sourceExampleId+"@"+e.lesson:e.sourceExampleId;
    if(used.has(id))fail("DERIVED_EXAMPLE_ID_COLLISION:"+id);
    used.add(id);
    derived.push({sourceId:e.sourceExampleId,id,lesson:e.lesson,cardId:e.cardId});
  }
  const snapshotProvided=srsSnapshot!==null;
  if(opts.target==="EXISTING_PROFILE_DRY_RUN"&&!snapshotProvided)fail("PROFILE_BACKUP_REQUIRED");
  if(snapshotProvided&&(!srsSnapshot||!Array.isArray(srsSnapshot.records)))fail("PROFILE_SNAPSHOT_SCHEMA_UNSUPPORTED");
  const state=snapshotProvided?srsSnapshot.records:[];
  const snapshotCopy=JSON.stringify(srsSnapshot);
  const srsIds=new Set(),overlap=[];
  for(const record of state) {
    if(!record||typeof record.id!=="string"||!record.id.trim())fail("MALFORMED_SRS_RECORD");
    if(srsIds.has(record.id))fail("DUPLICATE_SRS_RECORD_ID");
    srsIds.add(record.id);
  }
  for(const id of ids.keys())if(srsIds.has(id))overlap.push(id);
  if(snapshotProvided&&JSON.stringify(srsSnapshot)!==snapshotCopy)fail("SRS_INPUT_MUTATED");
  const allowNew=opts.target==="NEW_LIBRARY_DRY_RUN"&&!snapshotProvided;
  const status=allowNew?"PASS_READONLY_NEW_LIBRARY_PREFLIGHT":
    opts.target==="EXISTING_PROFILE_DRY_RUN"?"HOLD_EXISTING_PROFILE_ALL_WRITES_DISABLED":"HOLD_NEW_LIBRARY_WITH_SRS_PRESENT";
  return {
    schema:"b1-24-import-preflight@1.0.0",status,mutation_performed:false,
    old_legacy_ids_preserved:true,auto_alias_executed:false,source_examples_preserved:true,
    counts:{lessonCount:countsByLesson.size,membershipRows:memberships.length,distinctIds:ids.size,exampleGroups:examples.length,reusedIdGroups:reused.length,reusedMembershipRows:reuseExtra,sourceExampleIdCollisionRows:duplicatedSourceExampleRows,derivedExampleIdsUnique:used.size,srsSeedRecords:state.length,preexistingSrsOverlappingIds:overlap.length},
    holds:heldAliases.map(x=>({lemma:x.lemma,pos:x.pos,memberships:x.items.map(([lesson,id])=>({lesson,id})),status:"HOLD_NO_ALIAS_NO_SRS_MERGE"})),
    instructions:["DRY-RUN ONLY. No writes, no ID alias, no IndexedDB modification.","For an active profile require a protected and independently verified full backup plus a separate live rollback rehearsal.","Missing L24 historical PASS0023 binary is a strict identity release boundary. Any new install must retain original 24 lesson source mapping."],
    exampleIdMapping:derived
  };
}

// Node integration:
//   node B1-24-SRS-LOSSLESS-DRYRUN-PREFLIGHT-v1.mjs INPUT.json NEW_LIBRARY_DRY_RUN
//   node B1-24-SRS-LOSSLESS-DRYRUN-PREFLIGHT-v1.mjs INPUT.json EXISTING_PROFILE_DRY_RUN PROFILE_SNAPSHOT.json
// INPUT.json must be {"memberships":[{"id":"...","lesson":"B1-L01","lemma":"...","pos":"...","examples":[{"id":"...","de":"...","fa":"...","en":"..."},...]},...]}
// This is a fail-closed *normalized input* guard; it does not convert arbitrary historical 17/23/32 column files.
if (typeof process !== "undefined" && process.argv?.[1]?.endsWith("B1-24-SRS-LOSSLESS-DRYRUN-PREFLIGHT-v1.mjs")) {
  const {readFileSync}=await import("node:fs");
  const [inputPath,target,snapshotPath]=process.argv.slice(2);
  if(!inputPath||!target){console.error("Usage: node FILE INPUT.json NEW_LIBRARY_DRY_RUN|EXISTING_PROFILE_DRY_RUN [PROFILE_SNAPSHOT.json]"); process.exitCode=2}
  else {
    try {
      const input=JSON.parse(readFileSync(inputPath,"utf8"));
      const snapshot=snapshotPath?JSON.parse(readFileSync(snapshotPath,"utf8")):null;
      const plan=planB1Import(input.memberships,snapshot,{target});
      // Summarize without writing entire 12,548 example map to stdout.
      const {exampleIdMapping,...summary}=plan;
      console.log(JSON.stringify({...summary,exampleIdMappingEntries:exampleIdMapping.length},null,2));
    } catch(e) {console.error(String(e));process.exitCode=1}
  }
}
