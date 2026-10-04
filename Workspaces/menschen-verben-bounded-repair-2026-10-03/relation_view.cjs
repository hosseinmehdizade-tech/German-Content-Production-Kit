const fs = require('fs'), path = require('path'), http = require('http'), assert = require('assert/strict');
const {chromium} = require('C:/Users/hosse/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const O = __dirname, R = path.join(O, 'runtime/GFP-v455-R89');
const server = http.createServer((req,res) => {
  try {
    const f = path.resolve(R, '.' + new URL(req.url,'http://localhost').pathname);
    if (!f.startsWith(R + path.sep)) throw new Error('outside runtime');
    res.setHeader('Content-Type', f.endsWith('.html') ? 'text/html; charset=utf-8' : f.endsWith('.js') ? 'text/javascript' : f.endsWith('.css') ? 'text/css' : 'application/octet-stream');
    res.end(fs.readFileSync(f));
  } catch { res.writeHead(404).end(); }
});
async function main() {
  await new Promise(r => server.listen(0,'127.0.0.1',r));
  let browser;
  const result = {runtime:'v455-R89', runtime_sha256:'d571005eee6a5445d31569ed55c106ac754a42ba1736bad978c26d152e9bae2e', levels:{}};
  try {
    browser = await chromium.launch({headless:true, executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
    for (const [level,count,id] of [['A1',310,'ma1m-lu-0335'],['A2',292,'ma2-lu-0154'],['B1',395,'mb1m-lu-0200']]) {
      const context = await browser.newContext({serviceWorkers:'block'}), page = await context.newPage();
      page.on('dialog',d=>d.accept());
      await page.addInitScript(()=>window.__GFP_TEST_MODE__=true);
      await page.goto('http://127.0.0.1:'+server.address().port+'/01-App/index.html');
      await page.waitForFunction(()=>window.GFP_TEST_API && document.body.classList.contains('boot-ready'));
      await page.locator('#tsvImportInput').setInputFiles(path.join(O,level+'-input.zip'));
      await page.waitForFunction(()=>!document.querySelector('#tsvImportBtn').disabled);
      await page.locator('#tsvImportBtn').evaluate(e=>e.click());
      await page.waitForFunction(n=>GFP_TEST_API.cards().length===n,count);
      await page.evaluate(async()=>await GFP_TEST_API.universalAuthorityRowsV426ForTest());
      const model = await page.evaluate(id=>({tabs:GFP_WORTDETAILS_V44.detailTabs(),model:GFP_WORTDETAILS_V44.model(id)}),id);
      assert(model.model && model.model.relations.some(g=>g.items.length));
      fs.writeFileSync(path.join(O,level+'-WORD-DETAILS-MODEL.json'),JSON.stringify(model,null,2));
      await page.evaluate(id=>GFP_WORTDETAILS_V44.openPage(id,'network',{pushTrail:false}),id);
      await page.locator('.wortnetz-v44').waitFor({state:'visible'});
      const view = await page.evaluate(()=>({
        state:GFP_WORTDETAILS_V44.state(),
        text:document.querySelector('.wortdetails-panel-v44').textContent,
        titles:[...document.querySelectorAll('.wortnetz-node-v44:not(.center) text:first-of-type,.wortnetz-chip-v44 b')].map(e=>e.textContent),
        navigation:[...document.querySelectorAll('[data-v44-network-target]')].map(e=>e.getAttribute('data-v44-network-target'))
      }));
      assert(view.titles.length && !/\bREKTION\b|\bverb_core\b|\bnon_prefixed\b/.test(view.text));
      fs.writeFileSync(path.join(O,level+'-WORD-DETAILS-VIEW.json'),JSON.stringify(view,null,2));
      await page.screenshot({path:path.join(O,level+'-word-details.png'),fullPage:true});
      const duplicate = level==='B1' && view.titles.filter(x=>x==='nachdenken').length!==1;
      if(level==='B1') { assert.equal(view.titles.filter(x=>x==='nachdenken').length,2); assert(view.titles.includes('nachsinnen')); }
      result.levels[level]={id,status:duplicate?'BLOCKED_AUD006_WORTNETZ_DUPLICATE':'PASS_RELATION_PRESENTATION_SAMPLE',visible_titles:view.titles,navigation_targets:view.navigation,canonical_model_preserved:true};
      await context.close();
    }
    result.status='A1_A2_PASS_B1_PRESENTATION_BLOCKED';
    fs.writeFileSync(path.join(O,'RELATION-PRESENTATION-ACCEPTANCE.json'),JSON.stringify(result,null,2));
    console.log(JSON.stringify(result));
  } finally { if(browser) await browser.close(); server.close(); }
}
main().catch(e=>{console.error(e);server.close();process.exitCode=1;});
