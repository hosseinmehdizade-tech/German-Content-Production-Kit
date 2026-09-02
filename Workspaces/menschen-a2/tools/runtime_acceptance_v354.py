#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import argparse, json, os, threading, functools, time, hashlib

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--app-root',required=True,type=Path)
    ap.add_argument('--tsv',required=True,type=Path)
    ap.add_argument('--canonical',required=True,type=Path)
    ap.add_argument('--runtime-report',required=True,type=Path)
    ap.add_argument('--presentation-report',required=True,type=Path)
    ns=ap.parse_args()
    html=ns.app_root/'01-App/German-Flashcards-Pro-v354.html'
    assert html.exists(), html
    ds=json.loads(ns.canonical.read_text(encoding='utf-8'))
    expected=len(ds['learning_units'])
    expected_ids=[u['id'] for u in ds['learning_units']]
    handler=functools.partial(SimpleHTTPRequestHandler,directory=str(html.parent))
    server=ThreadingHTTPServer(('127.0.0.1',0),handler)
    port=server.server_address[1]
    th=threading.Thread(target=server.serve_forever,daemon=True);th.start()
    runtime_checks=[];presentation_checks=[]
    def ck(bucket,name,cond,detail=None):
        bucket.append({'name':name,'pass':bool(cond),'detail':detail if detail is not None else ''})
        if not cond: raise AssertionError(f'{name}: {detail}')
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1366,'height':768})
        errors=[]; page.on('pageerror',lambda e: errors.append(str(e)))
        page.on('dialog',lambda d: d.accept())
        page.goto(f'http://127.0.0.1:{port}/{html.name}',wait_until='domcontentloaded',timeout=60000)
        page.wait_for_timeout(900)
        ck(runtime_checks,'v354 exact runtime loaded',page.title()=='German Flashcards Pro v354',page.title())
        ck(runtime_checks,'no boot JavaScript errors',not errors,errors[:5])
        ck(runtime_checks,'unified import file input exists',page.locator('#tsvImportInput').count()==1)
        page.locator('#tsvImportInput').set_input_files(str(ns.tsv.resolve()))
        page.wait_for_timeout(1600)
        friendly=page.locator('#importFriendlyStatusV352').inner_text() if page.locator('#importFriendlyStatusV352').count() else ''
        tech=page.locator('#tsvImportReport').inner_text() if page.locator('#tsvImportReport').count() else ''
        ck(runtime_checks,'exact TSV preview accepted','فایل معتبر و آماده ورود است' in friendly,{'friendly':friendly,'tech':tech[:600]})
        ck(runtime_checks,'Universal v2 detected','Universal Card v2' in tech,tech[:600])
        ck(runtime_checks,'import button enabled',not page.locator('#tsvImportBtn').is_disabled())
        opts=page.locator('#tsvImportMode option').evaluate_all("(els)=>els.map(e=>({value:e.value,text:e.textContent}))")
        values=[x['value'] for x in opts]
        preferred='replace-reset-progress' if 'replace-reset-progress' in values else next((v for v in values if 'replace' in v and 'reset' in v),None)
        ck(runtime_checks,'destructive replace/reset import mode available',preferred is not None,opts)
        page.locator('#tsvImportMode').select_option(preferred)
        page.locator('#tsvImportBtn').click()
        page.wait_for_timeout(2500)
        count=page.evaluate("()=>GFP_TEST_API.cards().length")
        ck(runtime_checks,'transaction imported exact unit count',count==expected,{'expected':expected,'actual':count})
        ids=page.evaluate("()=>GFP_TEST_API.cards().map(c=>c.id)")
        ck(runtime_checks,'imported ID set exact',set(ids)==set(expected_ids),{'actual_count':len(ids)})
        card=page.evaluate("(id)=>GFP_TEST_API.cards().find(c=>c.id===id)",expected_ids[0])
        blob=json.dumps(card,ensure_ascii=False)
        ck(runtime_checks,'canonical bridge survived importer','canonical_unit' in blob and 'gfp-german-language-content@3.1.3' in blob,blob[:800])
        ck(runtime_checks,'verb morphology survived importer',all(x in blob for x in ['kuschelt','kuschelte','hat gekuschelt']),blob[:1000])
        ck(runtime_checks,'Persian face survived importer','بغل کردن' in blob,blob[:1000])
        # Durable persistence: reload the same origin and re-read the store.
        page.reload(wait_until='domcontentloaded',timeout=60000);page.wait_for_timeout(1800)
        count2=page.evaluate("()=>GFP_TEST_API.cards().length")
        ids2=page.evaluate("()=>GFP_TEST_API.cards().map(c=>c.id)")
        ck(runtime_checks,'persistent commit survives reload',count2==expected and set(ids2)==set(expected_ids),{'count':count2})
        ck(runtime_checks,'no runtime JS errors after reload',not errors,errors[:10])

        # Presentation Model acceptance against the exact canonical payload embedded losslessly in the TSV.
        page.evaluate("(d)=>GFP_PRACTICE_CONTENT_V350.stageCanonicalForTest(d,'replace-reset-progress')",ds)
        page.wait_for_timeout(500)
        for mode in ['study','quick','typing','audio']:
            page.evaluate("([m])=>GFP_PRACTICE_CONTENT_V350.setAxis(m,'word',{rebuild:false,announce:false})",[mode])
            words=page.evaluate("([m])=>GFP_PRACTICE_CONTENT_V350.resolve(GFP_TEST_API.cards(),m).map(x=>x.id)",[mode])
            ck(presentation_checks,f'{mode} word model contains all physical units',len(words)==expected,{'count':len(words)})
            page.evaluate("([m])=>GFP_PRACTICE_CONTENT_V350.setAxis(m,'sentence',{rebuild:false,announce:false})",[mode])
            sent=page.evaluate("([m])=>GFP_PRACTICE_CONTENT_V350.resolve(GFP_TEST_API.cards(),m).map(x=>x.id)",[mode])
            ck(presentation_checks,f'{mode} sentence model exposes stable examples',len(sent)==expected and all('-ex-' in x for x in sent),{'count':len(sent),'first':sent[:3]})
        sid='ma2-lu-0001-ex-001'
        ck(presentation_checks,'stable example identity registered',page.evaluate("(id)=>GFP_PRACTICE_CONTENT_V350.virtualRegistered(id)",sid))
        ans=page.evaluate("(id)=>GFP_PRACTICE_CONTENT_V350.answerFor(id,'study')",sid)
        ck(presentation_checks,'Persian sentence translation selected',str(ans.get('lang','')).lower().startswith('fa') and 'بغل' in str(ans.get('text','')),ans)
        word=page.evaluate("(id)=>GFP_TEST_API.cards().find(c=>c.id===id)",'ma2-lu-0001')
        wblob=json.dumps(word,ensure_ascii=False)
        ck(presentation_checks,'front/back preserved for German-Persian card','kuscheln' in wblob and 'بغل کردن' in wblob,wblob[:700])
        ck(presentation_checks,'verb form aliases available to presentation','kuschelt' in wblob and 'kuschelte' in wblob and 'hat gekuschelt' in wblob,wblob[:900])
        ck(presentation_checks,'final presentation JS clean',not errors,errors[:10])
        browser.close()
    server.shutdown()
    app_sha=hashlib.sha256(html.read_bytes()).hexdigest()
    rr={
      'status':'PASS','runtime':'German Flashcards Pro v354','runtime_commit':'49a28187e82734e92bc407276eb0d2ee0cbbbd55',
      'runtime_sha256':app_sha,'artifact':ns.tsv.name,'expected_units':expected,
      'import_state':'IMPORT_VERIFIED','persistence':'reload-survived','checks':runtime_checks
    }
    pr={
      'status':'PASS','presentation_model':'GFP_PRACTICE_CONTENT_V350 on v354','runtime_commit':'49a28187e82734e92bc407276eb0d2ee0cbbbd55',
      'word_units':expected,'stable_examples':expected,'modes':['study','quick','typing','audio'],'checks':presentation_checks
    }
    ns.runtime_report.parent.mkdir(parents=True,exist_ok=True)
    ns.runtime_report.write_text(json.dumps(rr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ns.presentation_report.write_text(json.dumps(pr,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'runtime':rr['status'],'presentation':pr['status'],'units':expected},ensure_ascii=False))

if __name__=='__main__':
    main()
