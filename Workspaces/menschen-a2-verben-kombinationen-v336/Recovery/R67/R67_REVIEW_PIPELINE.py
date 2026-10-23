#!/usr/bin/env python3
"""Menschen A2 R66: partition qualified-review work and merge audited partial exports.

No operation grants independent expert sign-off or Stage4 final status.
"""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import re
import sys
import types
import zipfile
from collections import Counter

R66_ZIP_SHA = '630bfcd30be7439f397c634ed7c5f197db54833455a88569b27b7ef79c73a21b'
R66_CANDIDATE_SHA = '77e29cbe28803b8534ad4e6cc0ece16df639a8aa01c98c116fd3ce114ebe59a7'
R66_DATA_FP = '794ade6af612bce219d47a0b90f0ebff90f40ef9cf09f65b774c4f7e277886df'
R62_PARENT_SHA = '4915e69dd77444f3103a5679aee43a2600cea7ab9b2bd438a0fe723da42a16d7'
INNER = '93-Stage4-Rechnung-Translation-And-Synonym-Triage-R66/'
BATCHES = 10
SCHEMA = 'menschen-a2-r67-qualified-review-assignment@1.0.0'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def canonical(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')

def load_source(path):
    path=pathlib.Path(path)
    if digest(path.read_bytes())!=R66_ZIP_SHA:
        raise ValueError('R66 outer ZIP mismatch; never use stale or altered review data')
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError('R66 ZIP CRC failed')
        validator=z.read(INNER+'VALIDATE_R66_REVIEW_EXPORT.py')
        m=types.ModuleType('r66_exact_upstream_gate')
        exec(compile(validator,'R66/VALIDATE_R66_REVIEW_EXPORT.py','exec'),m.__dict__)
        review,ids=m.load_authority(path,R66_ZIP_SHA)
    assert len(ids)==1411
    if review['parent_zip_sha256']!=R62_PARENT_SHA or review['data_fingerprint']!=R66_DATA_FP or review['candidate_sha256']!=R66_CANDIDATE_SHA:
        raise ValueError('R66 lineage/candidate mismatch')
    return review,ids,m

def assignments(review):
    items=review['examples']+review['synonyms']
    bycard={}
    for item in items:bycard.setdefault(item['card_id'],[]).append(item)
    cards=sorted(bycard)
    assert len(cards)==292
    groups=[]
    for ix in range(BATCHES):
        selected=cards[(len(cards)*ix)//BATCHES:(len(cards)*(ix+1))//BATCHES]
        records=[v for c in selected for v in bycard[c]]
        # Card grouping protects DE/FA/EN example + synonym sense consistency.
        groups.append({'batch_id':f'A2-R66-B{ix+1:02d}','cards':selected,'item_ids':[x['id'] for x in records],
                       'item_count':len(records),'examples':sum(x['review_kind']=='EXAMPLE' for x in records),
                       'synonyms':sum(x['review_kind']=='SYNONYM' for x in records)})
    document={'schema':SCHEMA,'source_r66_zip_sha256':R66_ZIP_SHA,'candidate_sha256':R66_CANDIDATE_SHA,
              'data_fingerprint':R66_DATA_FP,'parent_r62_zip_sha256':R62_PARENT_SHA,
              'items_total':len(items),'cards_total':len(cards),'batches':groups,
              'independent_qualified_approvals':0,'stage4_final':False,
              'assignment_rule':'Nonoverlapping complete card groups; each item belongs to exactly one batch'}
    for batch in groups:batch['item_set_sha256']=digest(canonical(batch['item_ids']))
    assert sum(g['item_count'] for g in groups)==1411
    assert len(set(i for g in groups for i in g['item_ids']))==1411
    return document

HTML = r'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/><title>__BATCH__ · Menschen A2 R66</title>
<style>body{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;background:#f5f6f8;color:#172033;margin:0}
header{background:#152945;color:white;padding:20px 4%}h1{font-size:1.35rem;margin:0 0 10px}main{max-width:1150px;margin:auto;padding:20px}
.tools{background:white;border:1px solid #dbe1e9;padding:16px;border-radius:12px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px}
input,select,textarea,button{font:inherit;padding:8px;border:1px solid #b8c3d0;border-radius:7px}
button{cursor:pointer;background:#eaf0f7}button.primary{background:#164777;color:white;border-color:#164777}
label{font-size:.88rem}.entry{background:white;border:1px solid #dbe1e9;border-radius:10px;padding:15px;margin:12px 0}
.entry h2{font-size:1.02rem;margin:0 0 10px}.item{padding:8px 0}.tag{font-size:.8rem;color:#526174}
.de{font-weight:650}.fa{direction:rtl;text-align:right;font-size:1.06rem}.meta{color:#536174;font-size:.86rem}
.controls{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:10px}.controls textarea{width:min(100%,520px);min-height:50px}
.warn{color:#7e3b18}.ok{color:#176247}.danger{color:#a02228}
</style></head><body><header><h1>Menschen A2 Verben · R66 · __BATCH__</h1>
<div>External qualified linguistic review · __ITEMS__ items · __CARDS__ complete cards · exact R66 candidate-bound</div></header>
<main><section class="tools"><label>Reviewer name / Kennung / نام بازبین<br><input id="reviewer" placeholder="Full reviewer name or controlled ID" size="30"></label>
<label>Search card, lemma or ID<br><input id="filter" placeholder="Search…"></label>
<button class="primary" id="export">Export decisions JSON</button><button id="import">Import previous JSON</button>
<input id="pick" type="file" accept=".json,application/json" hidden><span id="summary"></span></section>
<div class="meta">Source R66 SHA256 <code>__SOURCE__</code>. This is a *partial* review packet. An export is not verified professional accreditation and never finalizes Stage 4. For FIX_NEEDED/UNSURE, explain the issue (at least 8 characters). Keep the supplied file unchanged; export from this batch after recording decisions.</div>
<section id="items"></section></main><script id="payload" type="application/json">__DATA__</script><script>
'use strict';const DATA=JSON.parse(document.getElementById('payload').textContent);
const $=id=>document.getElementById(id);const key='a2-r67-'+DATA.batch_id+'-'+DATA.data_fingerprint;
const byid=new Map(DATA.items.map(x=>[x.id,x]));let decisions={}, reviewer='';
try{const c=JSON.parse(localStorage.getItem(key)||'{}');if(c.fingerprint===DATA.data_fingerprint){for(const [id,d] of Object.entries(c.decisions||{}))if(byid.has(id)&&byid.get(id).fingerprint===d.fingerprint)decisions[id]=d;reviewer=c.reviewer||'';}}catch(e){}
$('reviewer').value=reviewer;
function persist(){try{localStorage.setItem(key,JSON.stringify({fingerprint:DATA.data_fingerprint,reviewer,decisions}));}catch(e){}}
function say(){let counts={PASS:0,FIX_NEEDED:0,UNSURE:0};for(const d of Object.values(decisions))if(d.status in counts)counts[d.status]++;$('summary').textContent=`${Object.keys(decisions).length}/${DATA.items.length} reviewed · ${counts.PASS} PASS · ${counts.FIX_NEEDED} FIX · ${counts.UNSURE} UNSURE`;}
function node(tag,cl,text){const x=document.createElement(tag);if(cl)x.className=cl;if(text!==undefined)x.textContent=String(text);return x;}
function render(){const area=$('items');area.replaceChildren();const q=$('filter').value.toLowerCase().trim();let last='';let cardDiv=null;
for(const item of DATA.items){const searchable=[item.id,item.headword,item.de,item.fa,item.en,item.term,item.scope].join(' ').toLowerCase();if(q&&!searchable.includes(q))continue;
if(last!==item.card_id){last=item.card_id;cardDiv=node('article','entry');const h=node('h2','',item.card_id+' · '+item.headword);cardDiv.append(h);area.append(cardDiv);}
const box=node('section','item');box.append(node('div','tag',item.review_kind+' · '+item.id));
if(item.review_kind==='EXAMPLE'){box.append(node('div','de',item.de),node('div','fa',item.fa),node('div','',item.en));}
else{box.append(node('div','de',item.headword+' ↔ '+item.term),node('div','',item.scope),node('div','meta',item.definition_de||''));}
const ctr=node('div','controls');const select=node('select');for(const [v,t] of [['','Not reviewed'],['PASS','PASS'],['FIX_NEEDED','FIX NEEDED'],['UNSURE','UNSURE']]){const opt=node('option','',t);opt.value=v;select.append(opt);}select.value=decisions[item.id]?.status||'';
const note=node('textarea');note.placeholder='Evidence / translation correction / reasoning';note.value=decisions[item.id]?.note||'';
function update(){const name=$('reviewer').value.trim();if(!name){alert('Enter reviewer name before recording decisions');select.value=decisions[item.id]?.status||'';return;}
const old=decisions[item.id];if(old&&old.reviewer!==name){alert('Reviewer identity is locked for recorded decisions. Export then clear this batch in a different browser profile for a new reviewer.');select.value=old.status;return;}
reviewer=name;if(!select.value)delete decisions[item.id];else decisions[item.id]={fingerprint:item.fingerprint,status:select.value,note:note.value,reviewer:name,reviewed_at:new Date().toISOString()};persist();say();}
select.onchange=update;note.onchange=()=>{if(select.value)update();};ctr.append(select,note);box.append(ctr);cardDiv.append(box);
}say();}
$('filter').oninput=render;$('reviewer').onchange=()=>{if(Object.keys(decisions).length&&Object.values(decisions).some(d=>d.reviewer!==$('reviewer').value.trim())){alert('Do not relabel decisions of an earlier reviewer.');$('reviewer').value=reviewer;return;}reviewer=$('reviewer').value.trim();persist();};
$('export').onclick=()=>{const name=$('reviewer').value.trim();if(!name){alert('Reviewer name is required');return;}
for(const [id,d] of Object.entries(decisions)){if(d.reviewer!==name){alert('Inconsistent reviewer identity: '+id);return;}if(['UNSURE','FIX_NEEDED'].includes(d.status)&&String(d.note).trim().length<8){alert('Add a substantial note to '+id);return;}}
const out={schema:'menschen-a2-expert-review-decisions@1.0.0',candidate_sha256:DATA.candidate_sha256,data_fingerprint:DATA.data_fingerprint,parent_zip_sha256:DATA.parent_zip_sha256,
reviewer_label:name,exported_at:new Date().toISOString(),batch_id:DATA.batch_id,batch_item_set_sha256:DATA.batch_item_set_sha256,decisions,counts:{total:1411,recorded:Object.keys(decisions).length,unreviewed:1411-Object.keys(decisions).length},warning:'Structural validity does not prove qualified independent linguistic signoff.'};
const a=node('a');const url=URL.createObjectURL(new Blob([JSON.stringify(out,null,2)],{type:'application/json'}));a.href=url;a.download=DATA.batch_id+'-review-decisions.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);};
$('import').onclick=()=>$('pick').click();$('pick').onchange=async e=>{try{const f=e.target.files?.[0];if(!f)return;const data=JSON.parse(await f.text());
if(data.candidate_sha256!==DATA.candidate_sha256||data.data_fingerprint!==DATA.data_fingerprint||data.parent_zip_sha256!==DATA.parent_zip_sha256||data.batch_id!==DATA.batch_id)throw Error('R66 identity or batch mismatch');
const ds=data.decisions||{};for(const [id,d] of Object.entries(ds))if(!byid.has(id)||byid.get(id).fingerprint!==d.fingerprint)throw Error('Bad item fingerprint / wrong assignment: '+id);
if(Object.keys(decisions).length&&!confirm('Replace currently recorded decisions for this batch?'))return;
decisions=ds;reviewer=data.reviewer_label||'';$('reviewer').value=reviewer;persist();render();}catch(err){alert('Import rejected: '+err.message);}finally{$('pick').value='';}};
render();</script></body></html>'''

def html_for(batch,records,review):
    payload={'batch_id':batch['batch_id'],'batch_item_set_sha256':batch['item_set_sha256'],'items':records,
             'candidate_sha256':review['candidate_sha256'],'data_fingerprint':review['data_fingerprint'],
             'parent_zip_sha256':review['parent_zip_sha256']}
    data=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('&','\\u0026')
    return (HTML.replace('__DATA__',data).replace('__BATCH__',batch['batch_id'])
            .replace('__ITEMS__',str(len(records))).replace('__CARDS__',str(len(batch['cards']))).replace('__SOURCE__',R66_ZIP_SHA)).encode('utf-8')

def csv_for(records):
    s=io.StringIO();cols=['review_kind','id','card_id','headword','de','fa','en','term','scope','fingerprint','status','note']
    w=csv.DictWriter(s,fieldnames=cols,delimiter='\t',lineterminator='\n');w.writeheader()
    for x in records:w.writerow({**{k:x.get(k,'') for k in cols},'status':'NOT_REVIEWED','note':''})
    return s.getvalue().encode('utf-8')

def prepare(source,dest):
    review,ids,gate=load_source(source);groups=assignments(review);byid={x['id']:x for x in review['examples']+review['synonyms']}
    docs={}
    docs['R67-ASSIGNMENTS.json']=json.dumps(groups,ensure_ascii=False,indent=2).encode('utf-8')+b'\n'
    docs['README-FA-DE.md']=('''# R67 — partitioned qualified reviewer handoff for R66

This is an **auxiliary workflow**, NOT a new content version. Authoritative data: R66 SHA256 '''+R66_ZIP_SHA+'''. Ten disjoint, complete-card batches cover every one of 1168 DE/FA/EN examples and 243 scoped synonyms.

فارسی: هر پوشه مربوط به یک دسته از کارت‌هاست. فایل `REVIEW-BATCH.html` را آفلاین باز کنید، نام بازبین واجد صلاحیت را ثبت کنید، برای تک‌تک موارد PASS/FIX_NEEDED/UNSURE انتخاب کنید و در انتها JSON خروجی بگیرید. تأیید خودکار صلاحیت یا استقلال بازبین ممکن نیست. در هر نوبت از خروجی‌ها بکاپ بگیرید. برای ادامهٔ کار JSON قبلی همان دسته را Import کنید.

For each batch: open HTML offline, enter named reviewer, examine each source-specific example and synonym, record decision + evidence, export JSON. PASS must be an intentional expert judgment, not a pre-filled response. For FIX_NEEDED or UNSURE explain why. Batch exports may be partial and completed over multiple sittings.

Use the merge validator with the **exact R66 complete ZIP** and this R67-ASSIGNMENTS.json. Example:

`python R67_REVIEW_PIPELINE.py merge --source R66.zip --assignments R67-ASSIGNMENTS.json --input-dir reviewer-exports --report R67-MERGE-REPORT.json`

Merge rejects stale candidate/fingerprint, incorrect batches, duplicate decisions, unrecognized IDs, mixed reviewer identity, and invalid notes. A structurally complete result **never** establishes qualified independent sign-off and **never** authorizes Stage4 final, Stage5, or import. Independent reviewer qualifications, provenance fidelity, substantive language quality and unresolved FIX/UNSURE decisions require human attestation/repair.

**Metadata erratum, inherited from older schema**: The R66 `REVIEW-DATA.json` has a legacy schema name and explanatory `review_requirement` referencing R57. These strings are stale descriptions, not authority. R66 actual source ZIP SHA, R66 candidate SHA and R66 data fingerprint above are mandatory. The `parent_zip_sha256` field identifies **R62**, R66's direct parent, and is *not* the R66 outer SHA; this is by design of the inherited export schema. Strict source validation separately verifies the R66 outer SHA.

No card, example, relation, source screenshot or application runtime changed by R67. The original R66 validator is reused directly for each individual export. Source textbook screenshots remain inside R66 (not bundled into this reviewer handoff); reviewer should check available original source/provenance where required.
''').encode('utf-8')
    for b in groups['batches']:
        rows=[byid[x] for x in b['item_ids']]
        base=f"Batches/{b['batch_id']}/"
        docs[base+'REVIEW-BATCH.html']=html_for(b,rows,review)
        docs[base+'ITEMS.tsv']=csv_for(rows)
        docs[base+'IDENTITY.json']=json.dumps({k:v for k,v in b.items() if k!='item_ids'},ensure_ascii=False,indent=2).encode() + b'\n'
    docs['R67_REVIEW_PIPELINE.py']=pathlib.Path(__file__).read_bytes()
    manifest={k:digest(v) for k,v in sorted(docs.items())}
    docs['SHA256SUMS.json']=json.dumps({'schema':'r67-internal-sha256@1.0.0','hashes':manifest},indent=2).encode('utf-8')+b'\n'
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(docs):
            zi=zipfile.ZipInfo(name,date_time=(2026,10,23,6,0,0));zi.compress_type=zipfile.ZIP_DEFLATED
            zi.create_system=3;zi.external_attr=0o644 << 16
            z.writestr(zi,docs[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        for name,h in manifest.items():assert digest(z.read(name))==h
    print(json.dumps({'status':'PASS','source':R66_ZIP_SHA,'batches':BATCHES,'items':1411,'members':len(docs),'zip_sha256':digest(pathlib.Path(dest).read_bytes()),'zip_bytes':pathlib.Path(dest).stat().st_size},indent=2))

def merge_documents(gate,review,ids,assignment,rawdocs):
    if assignment.get('schema')!=SCHEMA or assignment.get('source_r66_zip_sha256')!=R66_ZIP_SHA or assignment.get('candidate_sha256')!=R66_CANDIDATE_SHA or assignment.get('data_fingerprint')!=R66_DATA_FP:
        raise ValueError('Assignment manifest does not match authoritative R66')
    batches={b['batch_id']:b for b in assignment['batches']};lookup={}
    for b in batches.values():
        assert digest(canonical(b['item_ids']))==b['item_set_sha256']
        for it in b['item_ids']:
            if it in lookup: raise ValueError('Overlapping assignment item '+it)
            lookup[it]=b['batch_id']
    if set(lookup)!=set(ids):raise ValueError('Missing or extra assignment item IDs')
    merged={};per_export=[];errors=[];seen_names=set()
    for name,data in rawdocs:
        try:
            parsed=gate.json_bytes(data)
            if parsed.get('batch_id') not in batches:raise ValueError('Unknown or missing batch_id')
            b=batches[parsed['batch_id']]
            if parsed.get('batch_item_set_sha256')!=b['item_set_sha256']:raise ValueError('Stale batch item-set identity')
            gate_result=gate.parse_review(parsed,review,ids)
            if not parsed['decisions']:raise ValueError('Empty export has no reviewer decisions')
            for id,d in parsed['decisions'].items():
                if lookup[id]!=b['batch_id']:raise ValueError('Item outside declared batch: '+id)
                if id in merged:raise ValueError('Duplicate decision ID across exports: '+id)
                merged[id]={**d,'item_id':id,'batch_id':b['batch_id'],'export_file':name}
            seen_names.add(gate_result['reviewer_label']);per_export.append({'file':name,'batch_id':b['batch_id'],'reviewer_label':gate_result['reviewer_label'],'recorded':gate_result['recorded'],'status':gate_result['classification']})
        except Exception as e:
            raise ValueError('INVALID_REVIEW_EXPORT '+name+': '+str(e)) from e
    states=Counter(d['status'] for d in merged.values());remaining=[x for x in lookup if x not in merged]
    report={'schema':'menschen-a2-r67-merged-review-audit@1.0.0',
            'technical_input':'R66 authoritative source and individual exports validated with strict R66 validator',
            'r66_zip_sha256':R66_ZIP_SHA,'candidate_sha256':R66_CANDIDATE_SHA,'data_fingerprint':R66_DATA_FP,
            'unique_items_total':len(ids),'decisions_recorded':len(merged),'unreviewed':len(remaining),'status_counts':dict(states),
            'reviewer_labels':sorted(seen_names),'exports':per_export,'unreviewed_ids':remaining,
            'decisions':{x:merged[x] for x in sorted(merged)},
            'classification':('NO_EXPORTS' if not merged else 'INCOMPLETE_REVIEW' if remaining else 'REVIEW_FLAGS_REQUIRE_RESOLUTION' if (states['FIX_NEEDED'] or states['UNSURE']) else 'STRUCTURALLY_COMPLETE_MANUAL_EXPERT_ATTESTATION_REQUIRED'),
            'expert_independence_or_qualification_verified':False,'stage4_final':False,'stage5_eligible':False,'import_authorized':False,
            'warning':'All syntactically valid PASS decisions do NOT authenticate a qualified independent expert or source fidelity; attest manually.'}
    return report

def do_merge(args):
    review,ids,gate=load_source(args.source)
    assignment=json.loads(pathlib.Path(args.assignments).read_text(encoding='utf-8'))
    docs=[]
    for p in sorted(pathlib.Path(args.input_dir).glob('*.json')):
        if p.stat().st_size>20_000_000:raise ValueError('Oversized decision export')
        docs.append((p.name,p.read_bytes()))
    report=merge_documents(gate,review,ids,assignment,docs)
    if args.report:
        pathlib.Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['classification','unique_items_total','decisions_recorded','unreviewed','status_counts','reviewer_labels','stage4_final']},ensure_ascii=False,indent=2))

def selftest(args):
    review,ids,gate=load_source(args.source);a=assignments(review);byid={x['id']:x for x in review['examples']+review['synonyms']}
    def export(batchid,ids_to_review,who='EXTERNAL_TEST_FIXTURE_NOT_REAL'):
        b=next(b for b in a['batches'] if b['batch_id']==batchid)
        ds={i:{'status':'PASS','note':'','reviewer':who,'reviewed_at':'2026-10-23T08:00:00+02:00','fingerprint':byid[i]['fingerprint']} for i in ids_to_review}
        return {'schema':gate.REVIEW_SCHEMA,'candidate_sha256':R66_CANDIDATE_SHA,'data_fingerprint':R66_DATA_FP,'parent_zip_sha256':R62_PARENT_SHA,'reviewer_label':who,'exported_at':'2026-10-23T09:00:00+02:00','batch_id':batchid,'batch_item_set_sha256':b['item_set_sha256'],'decisions':ds,'counts':{'total':1411,'recorded':len(ds),'unreviewed':1411-len(ds)}}
    def raw(v):return json.dumps(v).encode()
    x=a['batches'][0];y=a['batches'][1];d1=export(x['batch_id'],[x['item_ids'][0]]);d2=export(y['batch_id'],[y['item_ids'][0]])
    ok=merge_documents(gate,review,ids,a,[('first',raw(d1)),('second',raw(d2))]);assert ok['decisions_recorded']==2 and ok['unreviewed']==1409 and ok['stage4_final'] is False
    cases=[]
    def reject(label,docs):
        try:merge_documents(gate,review,ids,a,docs)
        except ValueError:cases.append(label);return
        raise AssertionError('Accepted invalid export '+label)
    reject('duplicate_decision',[('a',raw(d1)),('b',raw(d1))])
    malformed=json.loads(raw(d1));malformed['candidate_sha256']='0'*64
    reject('stale_candidate',[('a',raw(malformed))])
    malformed=json.loads(raw(d1));malformed['batch_id']=y['batch_id']
    reject('wrong_batch',[('a',raw(malformed))])
    malformed=json.loads(raw(d1));malformed['decisions'][x['item_ids'][0]]['fingerprint']='0'*64
    reject('item_fingerprint_tamper',[('a',raw(malformed))])
    malformed=json.loads(raw(d1));malformed['decisions'][x['item_ids'][0]]['status']='UNSURE';malformed['decisions'][x['item_ids'][0]]['note']=''
    reject('missing_uncertainty_explanation',[('a',raw(malformed))])
    malformed=json.loads(raw(d1));malformed['reviewer_label']='Wrong reviewer'
    reject('mixed_reviewer',[('a',raw(malformed))])
    malformed=json.loads(raw(d1));malformed['decisions']={}
    reject('zero_decisions',[('a',raw(malformed))])
    # A completely artificial 1411 PASS dataset is structurally complete but NEVER an expert signoff.
    synthetic=[(b['batch_id'],export(b['batch_id'],b['item_ids'])) for b in a['batches']]
    allp=merge_documents(gate,review,ids,a,[(i,raw(v)) for i,v in synthetic]);assert allp['decisions_recorded']==1411 and allp['classification'].startswith('STRUCTURALLY_COMPLETE') and not allp['stage4_final'] and not allp['expert_independence_or_qualification_verified']
    assert len(cases)==7
    print(json.dumps({'selftest':'PASS','negative_cases':cases,'positive_partial':True,'synthetic_full_does_not_approve':True,'batches':len(a['batches']),'review_items':len(ids)},indent=2))

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('prepare');p.add_argument('--source',required=True);p.add_argument('--output',required=True)
    m=sub.add_parser('merge');m.add_argument('--source',required=True);m.add_argument('--assignments',required=True);m.add_argument('--input-dir',required=True);m.add_argument('--report')
    t=sub.add_parser('selftest');t.add_argument('--source',required=True)
    a=ap.parse_args()
    try:
        if a.cmd=='prepare':prepare(a.source,a.output)
        if a.cmd=='merge':do_merge(a)
        if a.cmd=='selftest':selftest(a)
    except (ValueError,AssertionError,KeyError,zipfile.BadZipFile,FileNotFoundError) as e:
        print('FAIL:',str(e),file=sys.stderr);sys.exit(2)
if __name__=='__main__':main()