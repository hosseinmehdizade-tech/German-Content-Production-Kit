// Full deterministic production DOM projection + actual native click/key interactions.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/hosse/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const I=path.resolve(process.argv[2]),R=path.resolve(process.argv[3]),OUT=path.resolve(process.argv[4]);
const baseline=process.argv.includes('--baseline'),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const result={status:'RUNNING',baseline,runtime_entry_sha256:hash(path.join(R,'01-App/index.html')),relation_module_sha256:hash(path.join(R,'01-App/modules/library-reference-v44.js')),levels:{}};
function save(){fs.writeFileSync(OUT,JSON.stringify(result,null,2))}
const server=http.createServer((req,res)=>{const f=path.resolve(R,'.'+new URL(req.url,'http://localhost').pathname);if(!f.startsWith(R+path.sep))return res.writeHead(403).end();try{res.setHeader('Content-Type',f.endsWith('.html')?'text/html;charset=utf-8':f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':'application/octet-stream');res.end(fs.readFileSync(f))}catch{res.writeHead(404).end()}});
async function ready(p,n,expected){const deadline=Date.now()+60000;let state;while(Date.now()<deadline){state=await p.evaluate(async()=>({count:GFP_TEST_API.activeCardCount(),manifest:await GFP_TEST_API.readCommitManifestForTest(),startup:GFP_TEST_API.performanceV427()}));const m=state.manifest;if(state.count===n&&m?.cardCount===n&&m.commitStatus==='VERIFIED'&&m.activeGeneration&&Number.isFinite(m.commitRevision)&&(!expected||(m.activeGeneration===expected.activeGeneration&&m.commitRevision===expected.commitRevision)))return m;await new Promise(r=>setTimeout(r,100))}throw Error('bounded readiness '+JSON.stringify(state))}
async function main(){await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;try{
browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--disable-extensions','--disable-background-networking']});
for(const [level,count,focus]of [['A1',310,'ma1m-lu-0335'],['A2',292,'ma2-lu-0154'],['B1',395,'mb1m-lu-0200']]){
 const ctx=await browser.newContext({serviceWorkers:'block',viewport:{width:1516,height:1000}}),p=await ctx.newPage();p.on('dialog',d=>d.accept());await p.addInitScript(()=>window.__GFP_TEST_MODE__=true);
 try{await p.goto(`http://127.0.0.1:${server.address().port}/01-App/index.html`);await p.waitForFunction(()=>window.GFP_TEST_API&&document.body.classList.contains('boot-ready'));
 await p.locator('#tsvImportMode').evaluate(e=>{e.value='add';e.dispatchEvent(new Event('change',{bubbles:true}))});
 await p.locator('#tsvImportInput').setInputFiles(path.join(I,level+'-input.zip'));await p.waitForFunction(()=>!document.querySelector('#tsvImportBtn').disabled);await p.locator('#tsvImportBtn').evaluate(e=>e.click());const commit=await ready(p,count);
 await p.reload({waitUntil:'domcontentloaded'});await p.waitForFunction(()=>window.GFP_TEST_API&&document.body.classList.contains('boot-ready'));await ready(p,count,commit);
 const startup=await p.evaluate(()=>GFP_TEST_API.performanceV427());assert.equal(startup.authorityReleased,true);
 const authority=await p.evaluate(async()=>await GFP_TEST_API.universalAuthorityRowsV426ForTest());assert.equal(authority.count,count,JSON.stringify(startup));
 const ids=authority.cards.map(c=>c.customFields?.vnext_target_id||c.id);
 const scan=await p.evaluate(({baseline,ids})=>{
   const norm=s=>String(s||'').replace(/\s+/gu,' ').trim(),lexical=t=>['SYNONYM','ANTONYM','RELATED'].includes(t);
   const host=document.createElement('div');document.body.append(host);
   const info={cards:0,relation_types:{},rows_before:0,rows_after:0,canonical_surface_collisions:[],collapsed_display_cases:[],remaining_visible_duplicates:[],authority_changed:[],target_rows:0,value_rows:0,markup_comparisons:0,projection_ms:0};
   for(const id of ids){
     const m=GFP_WORTDETAILS_V44.model(id);if(!m)throw Error('missing '+id);info.cards++;
     const sealed=JSON.stringify(m.relations),old=[],oldSeen=new Set(),surface=new Map();
     for(const g of m.relations||[])for(const it of g.items||[]){info.relation_types[g.type]=(info.relation_types[g.type]||0)+1;
       const r={type:g.type,label:g.label||g.type,targetId:it.target_id||'',title:it.title||it.target_id||'',meaning:it.meaning||''};
       const k=JSON.stringify([g.type,it.target_id||'',it.title||'']);if(!oldSeen.has(k)){oldSeen.add(k);old.push(r)}
       if(lexical(g.type)){const s=JSON.stringify([g.type,norm(r.title),norm(r.meaning)]);const arr=surface.get(s)||[];arr.push({relation_id:it.relation_id,target_id:it.target_id,derived_reverse:it.derived_reverse});surface.set(s,arr)}
     }
     for(const [key,records]of surface)if(records.length>1)info.canonical_surface_collisions.push({id,key,records});
     const expected=[],slots=new Map();for(const r of old){const key=lexical(r.type)?JSON.stringify([r.type,norm(r.title),norm(r.meaning)]):JSON.stringify([r.type,r.targetId,r.title]);if(!slots.has(key)){slots.set(key,expected.length);expected.push(r)}else if(lexical(r.type)&&!expected[slots.get(key)].targetId&&r.targetId)expected[slots.get(key)]=r}
     if(old.length!==expected.length)info.collapsed_display_cases.push({id,before:old.length,after:expected.length,types:old.filter(r=>lexical(r.type)).map(r=>r.type)});
     const rows=baseline?old:expected,start=performance.now();host.innerHTML=GFP_WORTDETAILS_V44.renderMarkup(id,'network');info.projection_ms+=performance.now()-start;
     const shown=[...rows.filter(r=>r.targetId).slice(0,18),...rows.filter(r=>!r.targetId)];
     const nodes=[...host.querySelectorAll('.wortnetz-node-v44:not(.center)')],chips=[...host.querySelectorAll('.wortnetz-chip-v44')];
     const actual=[...nodes.map(e=>({title:e.querySelector('text').textContent,targetId:e.dataset.v44NetworkTarget,sub:e.querySelector('text.sub').textContent})),...chips.map(e=>({title:e.querySelector('b').textContent,targetId:'',sub:e.querySelector('small').textContent}))];
     if(actual.length!==shown.length)throw Error('DOM count '+id);
     const seen=new Map();actual.forEach((r,i)=>{const x=shown[i];if(r.title!==(x.targetId?String(x.title).slice(0,20):x.title)||r.targetId!==x.targetId||r.sub!==(x.targetId?String(x.label).slice(0,18):x.label+(x.meaning?' · '+x.meaning:'')))throw Error('DOM text/action '+id+' '+i);const key=JSON.stringify([x.type,norm(r.title),norm(x.meaning)]);if(seen.has(key))info.remaining_visible_duplicates.push({id,type:x.type,title:r.title,reason:lexical(x.type)?'full-title or displayed-meaning review required':'structural category outside bounded lexical repair'});seen.set(key,i)});
     if(JSON.stringify(GFP_WORTDETAILS_V44.model(id).relations)!==sealed)info.authority_changed.push(id);
     info.rows_before+=old.length;info.rows_after+=rows.length;info.target_rows+=nodes.length;info.value_rows+=chips.length;info.markup_comparisons++;
   }host.remove();return info;
 },{baseline,ids});
 assert.equal(scan.cards,count);assert.equal(scan.markup_comparisons,count);assert.deepEqual(scan.authority_changed,[]);
 if(!baseline)assert.equal(scan.remaining_visible_duplicates.filter(x=>['SYNONYM','ANTONYM','RELATED'].includes(x.type)).length,0,'lexical visible duplicates');
 await p.evaluate(id=>GFP_WORTDETAILS_V44.openPage(id,'network',{pushTrail:false}),focus);await p.locator('.wortnetz-v44').waitFor({state:'visible'});
 const view=await p.evaluate(()=>({state:GFP_WORTDETAILS_V44.state(),titles:[...document.querySelectorAll('.wortnetz-node-v44:not(.center) text:first-of-type,.wortnetz-chip-v44 b')].map(e=>e.textContent),targets:[...document.querySelectorAll('[data-v44-network-target]')].map(e=>e.dataset.v44NetworkTarget),duplicate_overlay_count:document.querySelectorAll('.wortnetz-v44').length}));
 assert.equal(view.duplicate_overlay_count,1);
 const actions=[];
 if(level==='B1'){
   assert.equal(view.titles.filter(t=>t==='nachdenken').length,baseline?2:1);assert.equal(view.titles.filter(t=>t==='nachsinnen').length,1);
   for(const mode of ['click','Enter',' ']){
     await p.evaluate(id=>GFP_WORTDETAILS_V44.openPage(id,'network',{pushTrail:false}),focus);
     const target=p.locator('[data-v44-network-target="mb1m-lu-0138"]');assert.equal(await target.count(),1);
     if(mode==='click')await target.click();else {await target.focus();await target.press(mode)}
     const state=await p.evaluate(()=>GFP_WORTDETAILS_V44.state());assert.equal(state.targetId,'mb1m-lu-0138');assert.equal(state.detailTab,'network');actions.push({mode,target:state.targetId});
   }
   const other=ids.find(id=>id!=='mb1m-lu-0200'&&id!=='mb1m-lu-0138');
   await p.evaluate(id=>GFP_WORTDETAILS_V44.openPage(id,'network',{pushTrail:false}),other);const otherHtml=await p.locator('.wortdetails-panel-v44').innerHTML();
   await p.evaluate(id=>GFP_WORTDETAILS_V44.openPage(id,'network',{pushTrail:false}),focus);const reset=await p.locator('.wortdetails-panel-v44').innerHTML();
   assert.notEqual(otherHtml,reset);assert.equal((await p.locator('.wortnetz-node-v44:not(.center) text:first-of-type,.wortnetz-chip-v44 b').allTextContents()).filter(t=>t==='nachdenken').length,baseline?2:1);
 }
 await p.screenshot({path:path.join(path.dirname(OUT),level+(baseline?'-before':'-after')+'-wortnetz.png'),fullPage:true});
 result.levels[level]={status:'PASS',focus,scan,view,actions,authority_preserved:true};save();console.log(level,JSON.stringify({cards:scan.cards,rows_before:scan.rows_before,rows_after:scan.rows_after,collapse_cases:scan.collapsed_display_cases.length,remaining_duplicates:scan.remaining_visible_duplicates.length,focus:view.titles,actions}));
 }finally{await ctx.close()}
}
result.status='PASS';save();
}finally{if(browser)await browser.close();server.close()}}
main().catch(e=>{result.status='FAIL';result.error=String(e.stack||e);save();console.error(e);server.close();process.exitCode=1});
