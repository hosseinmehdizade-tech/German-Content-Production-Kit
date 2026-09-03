#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import argparse, json, threading, functools, hashlib, re


def clean(v):
    return str(v or '').strip()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--app-root',required=True,type=Path)
    ap.add_argument('--app-html',default='01-App/index.html')
    ap.add_argument('--tsv',required=True,type=Path)
    ap.add_argument('--canonical',required=True,type=Path)
    ap.add_argument('--runtime-report',required=True,type=Path)
    ap.add_argument('--presentation-report',required=True,type=Path)
    ap.add_argument('--product-presentation-report',required=True,type=Path)
    ap.add_argument('--imported-canonical',required=True,type=Path)
    ap.add_argument('--runtime-commit',required=True)
    ap.add_argument('--screenshots-dir',type=Path)
    ns=ap.parse_args()

    html=ns.app_root/ns.app_html
    assert html.exists(), html
    ds=json.loads(ns.canonical.read_text(encoding='utf-8'))
    units=ds.get('learning_units') or []
    expected=len(units); expected_ids=[u['id'] for u in units]
    expected_examples=sum(len(u.get('examples') or []) for u in units)
    expected_example_ids=[e['id'] for u in units for e in (u.get('examples') or [])]
    byid={u['id']:u for u in units}

    def detail(u,k):
        d=u.get('details') if isinstance(u.get('details'),dict) else {}
        v=d.get(k)
        return [clean(x) for x in v if clean(x)] if isinstance(v,list) else []
    def colls(u):
        return [clean(c.get('text')) for c in (u.get('connections') or []) if isinstance(c,dict) and c.get('kind')=='collocation' and clean(c.get('text'))]

    verb_sample=next(u for u in units if u.get('type')=='verb' and clean(u.get('definition_de')) and len(u.get('examples') or [])>=4)
    phrase_sample=next(u for u in units if u.get('type')=='phrase' and len(u.get('examples') or [])>=4)
    relation_sample=next((u for u in units if u.get('type')=='verb' and (len(detail(u,'synonyms'))>=2 or len(detail(u,'antonyms'))>=2)),verb_sample)
    colloc_sample=next((u for u in units if u.get('type')=='verb' and len(colls(u))>=2),verb_sample)

    handler=functools.partial(SimpleHTTPRequestHandler,directory=str(html.parent))
    server=ThreadingHTTPServer(('127.0.0.1',0),handler); port=server.server_address[1]
    th=threading.Thread(target=server.serve_forever,daemon=True); th.start()
    runtime_checks=[]; presentation_checks=[]; product_checks=[]; rendered=[]
    def ck(bucket,name,cond,detailv=None):
        bucket.append({'name':name,'pass':bool(cond),'detail':detailv if detailv is not None else ''})
        if not cond: raise AssertionError(f'{name}: {detailv}')

    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1366,'height':768})
        errors=[]; page.on('pageerror',lambda e:errors.append(str(e))); page.on('dialog',lambda d:d.accept())
        page.goto(f'http://127.0.0.1:{port}/{html.name}',wait_until='domcontentloaded',timeout=60000); page.wait_for_timeout(900)
        title=page.title()
        ck(runtime_checks,'current runtime HTML loaded',bool(title and 'German Flashcards Pro' in title),title)
        ck(runtime_checks,'no boot JavaScript errors',not errors,errors[:5])
        ck(runtime_checks,'unified import file input exists',page.locator('#tsvImportInput').count()==1)
        page.locator('#tsvImportInput').set_input_files(str(ns.tsv.resolve())); page.wait_for_timeout(1800)
        friendly=page.locator('#importFriendlyStatusV352').inner_text() if page.locator('#importFriendlyStatusV352').count() else ''
        tech=page.locator('#tsvImportReport').inner_text() if page.locator('#tsvImportReport').count() else ''
        ck(runtime_checks,'exact TSV preview accepted','فایل معتبر و آماده ورود است' in friendly,{'friendly':friendly,'tech':tech[:700]})
        ck(runtime_checks,'Universal v2 detected','Universal Card v2' in tech,tech[:700])
        ck(runtime_checks,'import button enabled',not page.locator('#tsvImportBtn').is_disabled())
        opts=page.locator('#tsvImportMode option').evaluate_all('(els)=>els.map(e=>({value:e.value,text:e.textContent}))')
        vals=[x['value'] for x in opts]; preferred='replace-reset-progress' if 'replace-reset-progress' in vals else next((v for v in vals if 'replace' in v and 'reset' in v),None)
        ck(runtime_checks,'replace/reset import mode available',preferred is not None,opts)
        page.locator('#tsvImportMode').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("change",{bubbles:true}));}',preferred)
        page.locator('#tsvImportBtn').evaluate('(el)=>el.click()'); page.wait_for_timeout(3000)

        cards=page.evaluate('()=>GFP_TEST_API.cards()')
        ck(runtime_checks,'transaction imported exact physical unit count',len(cards)==expected,{'expected':expected,'actual':len(cards)})
        ids=[c.get('id') for c in cards]
        ck(runtime_checks,'imported physical ID order exact',ids==expected_ids,{'expected_first':expected_ids[:5],'actual_first':ids[:5]})
        imported_units=[]; missing_bridge=[]
        for c in cards:
            cf=c.get('customFields') if isinstance(c.get('customFields'),dict) else c.get('custom_fields') if isinstance(c.get('custom_fields'),dict) else {}
            cu=cf.get('canonical_unit') if isinstance(cf,dict) else None
            if not isinstance(cu,dict): missing_bridge.append(c.get('id'))
            else: imported_units.append(cu)
        ck(runtime_checks,'canonical bridge present on every imported card',not missing_bridge,missing_bridge[:20])
        ck(runtime_checks,'canonical bridge is lossless deep copy',imported_units==units,{'imported_units':len(imported_units)})
        imp={k:v for k,v in ds.items() if k!='learning_units'}; imp['learning_units']=imported_units
        ns.imported_canonical.parent.mkdir(parents=True,exist_ok=True); ns.imported_canonical.write_text(json.dumps(imp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

        page.reload(wait_until='domcontentloaded',timeout=60000); page.wait_for_timeout(1800)
        cards2=page.evaluate('()=>GFP_TEST_API.cards()'); ids2=[c.get('id') for c in cards2]
        ck(runtime_checks,'persistent commit survives reload',len(cards2)==expected and ids2==expected_ids,{'count':len(cards2)})
        ck(runtime_checks,'no runtime JS errors after reload',not errors,errors[:10])

        # Presentation Model cardinality for the exact persisted import.
        for mode in ['study','quick','typing','audio']:
            page.evaluate("([m])=>GFP_PRACTICE_CONTENT_V350.setAxis(m,'word',{rebuild:false,announce:false})",[mode])
            word=page.evaluate('([m])=>GFP_PRACTICE_CONTENT_V350.resolve(GFP_TEST_API.cards(),m).map(x=>x.id)',[mode])
            ck(presentation_checks,f'{mode} word model exact',word==expected_ids,{'count':len(word)})
            page.evaluate("([m])=>GFP_PRACTICE_CONTENT_V350.setAxis(m,'sentence',{rebuild:false,announce:false})",[mode])
            sent=page.evaluate('([m])=>GFP_PRACTICE_CONTENT_V350.resolve(GFP_TEST_API.cards(),m).map(x=>x.id)',[mode])
            ck(presentation_checks,f'{mode} sentence model exact example count',len(sent)==expected_examples,{'expected':expected_examples,'actual':len(sent)})
            ck(presentation_checks,f'{mode} sentence stable ID set exact',set(sent)==set(expected_example_ids),{'count':len(sent)})
            page.evaluate("([m])=>GFP_PRACTICE_CONTENT_V350.setAxis(m,'mixed',{rebuild:false,announce:false})",[mode])
            mixed=page.evaluate('([m])=>GFP_PRACTICE_CONTENT_V350.resolve(GFP_TEST_API.cards(),m).map(x=>x.id)',[mode])
            ck(presentation_checks,f'{mode} mixed model preserves all units',len(mixed)==expected+expected_examples and set(mixed)==set(expected_ids+expected_example_ids),{'count':len(mixed)})

        primary=units[0]['examples'][0]
        sid=primary['id']; ans=page.evaluate("(id)=>GFP_PRACTICE_CONTENT_V350.answerFor(id,'study')",sid)
        fa=next((t.get('text') for t in primary.get('translations',[]) if t.get('lang')=='fa-IR'),None)
        ck(presentation_checks,'primary sentence identity registered',page.evaluate('(id)=>GFP_PRACTICE_CONTENT_V350.virtualRegistered(id)',sid),sid)
        ck(presentation_checks,'primary Persian sentence answer preserved',clean(fa) and clean(ans.get('text'))==clean(fa),ans)

        if ns.screenshots_dir: ns.screenshots_dir.mkdir(parents=True,exist_ok=True)
        def render_word(u,label):
            page.evaluate("()=>GFP_PRACTICE_CONTENT_V350.setAxis('study','word',{rebuild:false,announce:false})")
            page.evaluate("id=>GFP_TEST_API.practiceRouterV202.launch({intent:'single',origin:'library',scope:{cardIds:[id]},title:'Rich-card acceptance'})",u['id'])
            page.wait_for_timeout(250)
            front=page.evaluate("()=>document.getElementById('flashCard')?.innerText||''")
            if ns.screenshots_dir: page.screenshot(path=str((ns.screenshots_dir/f'{label}-front.png').resolve()),full_page=False)
            page.evaluate("()=>document.getElementById('flashCard')?.click()"); page.wait_for_timeout(180)
            back=page.evaluate("()=>document.getElementById('flashCard')?.innerText||''")
            spans=page.evaluate("()=>[...document.querySelectorAll('#flashCard span')].map(x=>(x.innerText||'').trim()).filter(Boolean)")
            syn_spans=page.evaluate("()=>[...document.querySelectorAll('#flashCard [data-detail-kind=\"synonyms\"] span')].map(x=>(x.innerText||'').trim()).filter(Boolean)")
            ant_spans=page.evaluate("()=>[...document.querySelectorAll('#flashCard [data-detail-kind=\"antonyms\"] span')].map(x=>(x.innerText||'').trim()).filter(Boolean)")
            if ns.screenshots_dir: page.screenshot(path=str((ns.screenshots_dir/f'{label}-back.png').resolve()),full_page=False)
            rendered.append({'id':u['id'],'label':label,'front_text':front[:2000],'back_text':back[:7000],'span_count':len(spans),'synonym_spans':syn_spans,'antonym_spans':ant_spans})
            return front,back,spans,syn_spans,ant_spans

        fv,bv,sp,ss,aa=render_word(verb_sample,'verb')
        combined=fv+'\n'+bv
        ck(product_checks,'rendered verb headword visible',clean(verb_sample['headword']) in combined,verb_sample['id'])
        ck(product_checks,'rendered verb Persian meaning visible',clean(verb_sample['persian_meaning']) in combined,verb_sample['id'])
        ck(product_checks,'rendered verb definition visible',clean(verb_sample['definition_de']) in combined,verb_sample['id'])
        for key in ['present_3sg','preterite_3sg','perfect']:
            val=clean((verb_sample.get('core') or {}).get(key)); ck(product_checks,f'rendered verb {key} visible',not val or val in combined,{'id':verb_sample['id'],'value':val})
        dexs=[clean(e.get('text')) for e in (verb_sample.get('examples') or [])[:4]]
        ck(product_checks,'rendered verb exposes at least four German examples',sum(x in combined for x in dexs)>=4,{'id':verb_sample['id'],'examples':dexs})
        en=next((clean(t.get('text')) for t in verb_sample['examples'][0].get('translations',[]) if t.get('lang')=='en-US' and clean(t.get('text'))),'')
        ck(product_checks,'rendered verb exposes reviewed primary English example translation',bool(en and en in combined),{'id':verb_sample['id'],'english':en})
        ck(product_checks,'rendered verb has no raw canonical JSON leakage','canonical_unit' not in combined and '"learning_units"' not in combined and '{"id"' not in combined,combined[:1000])

        fp,bp,spp,_,_=render_word(phrase_sample,'phrase'); combinedp=fp+'\n'+bp
        ck(product_checks,'rendered phrase headword visible',clean(phrase_sample['headword']) in combinedp,phrase_sample['id'])
        ck(product_checks,'rendered phrase Persian meaning visible',clean(phrase_sample['persian_meaning']) in combinedp,phrase_sample['id'])
        pex=[clean(e.get('text')) for e in (phrase_sample.get('examples') or [])[:4]]
        ck(product_checks,'rendered phrase exposes at least four German examples',sum(x in combinedp for x in pex)>=4,{'id':phrase_sample['id'],'examples':pex})
        pen=next((clean(t.get('text')) for t in phrase_sample['examples'][0].get('translations',[]) if t.get('lang')=='en-US' and clean(t.get('text'))),'')
        ck(product_checks,'rendered phrase exposes reviewed primary English example translation',bool(pen and pen in combinedp),{'id':phrase_sample['id'],'english':pen})
        ck(product_checks,'rendered phrase has no raw JSON leakage','canonical_unit' not in combinedp and '{"id"' not in combinedp,combinedp[:1000])

        fr,br,spr,synsp,antsp=render_word(relation_sample,'relations'); comb=fr+'\n'+br
        syn=detail(relation_sample,'synonyms'); ant=detail(relation_sample,'antonyms')
        if len(syn)>=2:
            ck(product_checks,'synonym array renders as separate learner items',len(synsp)>=len(syn) and all(x in synsp for x in syn),{'id':relation_sample['id'],'expected':syn,'rendered':synsp})
        if len(ant)>=2:
            ck(product_checks,'antonym array renders as separate learner items',len(antsp)>=len(ant) and all(x in antsp for x in ant),{'id':relation_sample['id'],'expected':ant,'rendered':antsp})
        fc,bc,spc,_,_=render_word(colloc_sample,'collocations'); combc=fc+'\n'+bc
        coll=colls(colloc_sample)
        if len(coll)>=2:
            ck(product_checks,'collocations render as separate learner spans',all(x in spc for x in coll[:2]),{'id':colloc_sample['id'],'expected':coll[:2],'span_sample':spc[:80]})
        ck(product_checks,'rich lexical details are learner-visible',any(clean(x) in (comb+'\n'+combc) for x in (syn+ant+coll)),{'relation_id':relation_sample['id'],'collocation_id':colloc_sample['id']})
        ck(product_checks,'final rendered UI has no JavaScript errors',not errors,errors[:10])
        browser.close()
    finally:
      server.shutdown()

    app_sha=hashlib.sha256(html.read_bytes()).hexdigest()
    rr={'status':'PASS','runtime_title':title,'runtime_commit':ns.runtime_commit,'runtime_sha256':app_sha,'artifact':ns.tsv.name,'artifact_sha256':hashlib.sha256(ns.tsv.read_bytes()).hexdigest(),'canonical_sha256':hashlib.sha256(ns.canonical.read_bytes()).hexdigest(),'expected_units':expected,'expected_examples':expected_examples,'import_state':'IMPORT_VERIFIED','canonical_roundtrip':'LOSSLESS_DEEP_COPY','persistence':'reload-survived','checks':runtime_checks}
    pr={'status':'PASS','presentation_model':'GFP_PRACTICE_CONTENT_V350 on current runtime','runtime_commit':ns.runtime_commit,'word_units':expected,'sentence_units':expected_examples,'modes':['study','quick','typing','audio'],'checks':presentation_checks}
    pp={'status':'PASS','runtime_commit':ns.runtime_commit,'representative_types':['verb','phrase'],'sample_ids':{'verb':verb_sample['id'],'phrase':phrase_sample['id'],'relations':relation_sample['id'],'collocations':colloc_sample['id']},'rendered':rendered,'checks':product_checks}
    for p,obj in [(ns.runtime_report,rr),(ns.presentation_report,pr),(ns.product_presentation_report,pp)]:
        p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'runtime':'PASS','presentation':'PASS','product_presentation':'PASS','units':expected,'examples':expected_examples,'runtime_commit':ns.runtime_commit},ensure_ascii=False))

if __name__=='__main__': main()
