#!/usr/bin/env python3
"""Build a read-only Menschen portfolio from actual checked-out Git checkpoint files.
Only writes into --out; never writes content workstream, canonical, app or SRS.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

WORK={'A1':'Workspaces/menschen-a1-reaudit-v336','A2':'Workspaces/menschen-a2-24-lessons-v336','B1':'Workspaces/menschen-b1-24-lessons-v336'}
REPO='hosseinmehdizade-tech/German-Content-Production-Kit'
WEB=f'https://github.com/{REPO}/blob/main/'
BASELINE={'A1':list(range(2,25)),'A2':list(range(1,20)),'B1':list(range(1,19))}


def load(root, relative):
    if not relative or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError(f'UNSAFE_EVIDENCE_PATH:{relative}')
    path=root/relative
    if not path.is_file():raise ValueError(f'MISSING_AUTHORITY:{relative}')
    data=path.read_bytes()
    if len(data)>3_000_000:raise ValueError(f'EVIDENCE_TOO_LARGE:{relative}')
    obj=json.loads(data)
    if not isinstance(obj,dict):raise ValueError(f'INVALID_EVIDENCE:{relative}')
    sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    return obj,sha


def stage7_path(level,num):
    base=WORK[level]
    if level=='A1':return f'{base}/A1-L{num:02}-STAGE7-CHECKPOINT.json'
    if level=='A2':return f'{base}/L{num:02}-STAGE7.json'
    return f'{base}/'+('STAGE7.json' if num==1 else f'B1-L{num:02}-STAGE7.json')


def check_locked(obj, path):
    status=str(obj.get('status') or obj.get('quality_state') or '').upper()
    lock=obj.get('content_lock_state')
    if lock is not None:return lock=='LOCKED' and not status.startswith(('BLOCKED','NOT_LOCKED','UNLOCKED'))
    return 'LOCKED' in status and not status.startswith(('BLOCKED','NOT_LOCKED','UNLOCKED'))


def artifact_sha(obj):
    for key in ('release','artifact','delivery','final_delivery','package'):
        block=obj.get(key)
        if isinstance(block,dict):
            value=block.get('sha256') or block.get('artifact_sha256')
            if isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value):return value
    return None


def current_lesson(level,latest):
    if level=='A1':return 24
    raw=latest.get('current_lesson') if level=='A2' else latest.get('lesson')
    if isinstance(raw,int):n=raw
    else:
        found=re.search(rf'\b{level}-L(\d\d)\b',str(raw or latest.get('current_stage') or latest.get('latest_milestone') or ''))
        if not found:raise ValueError(f'UNKNOWN_ACTIVE_LESSON:{level}')
        n=int(found.group(1))
    if not 1<=n<=24:raise ValueError(f'ACTIVE_LESSON_OUT_OF_RANGE:{level}:{n}')
    return n


def generate(repo_root,previous=None):
    root=Path(repo_root)
    work={};refs={};alerts=[]
    for lvl,base in WORK.items():
        lp=f'{base}/LATEST.json'; latest,sha=load(root,lp)
        n=current_lesson(lvl,latest)
        stage=latest.get('current_stage') or latest.get('latest_milestone') or latest.get('latest_completed_milestone') or latest.get('latest_verified_milestone')
        if lvl=='A1':stage=latest.get('latest_verified_milestone',stage)
        rec=latest.get('receipt') or latest.get('milestone_receipt')
        if lvl=='B1' and not rec:raise ValueError('B1_LATEST_RECEIPT_MISSING')
        if lvl=='A2' and not rec:raise ValueError('A2_LATEST_RECEIPT_MISSING')
        if rec:
            rec_obj,rec_sha=load(root,rec)
            src_sha=latest.get('artifact_sha256') or latest.get('artifact',{}).get('sha256')
            if src_sha and artifact_sha(rec_obj)!=src_sha:raise ValueError(f'LATEST_RECEIPT_ARTIFACT_CONFLICT:{lvl}')
            refs[rec]={'git_blob_sha':rec_sha,'kind':'milestone_receipt'}
        work[lvl]={'latest_path':lp,'latest_blob_sha':sha,'active_lesson':f'{lvl}-L{n:02}','active_stage':str(stage),'status':str(latest.get('status') or latest.get('quality') or stage),'next_action':latest.get('next_action'), 'current_artifact_sha256':latest.get('artifact_sha256') or latest.get('artifact',{}).get('sha256'), 'receipt':rec}
        refs[lp]={'git_blob_sha':sha,'kind':'workstream_latest'}
    audit_path=f"{WORK['A1']}/AUDITS/LATEST-AUDIT.json";audit,audit_sha=load(root,audit_path)
    refs[audit_path]={'git_blob_sha':audit_sha,'kind':'global_audit'}
    if not audit.get('latest_receipt'):raise ValueError('A1_AUDIT_RECEIPT_MISSING')
    audit_rec,audit_rec_sha=load(root,audit['latest_receipt'])
    refs[audit['latest_receipt']]={'git_blob_sha':audit_rec_sha,'kind':'audit_receipt'}
    if audit.get('latest_portable_sha256') not in (audit_rec.get('artifact',{}).get('sha256'), audit_rec.get('portable',{}).get('sha256')):
        raise ValueError('A1_AUDIT_POINTER_ARTIFACT_CONFLICT')
    work['A1']['audit_milestone']=audit.get('latest_read_only_audit_milestone')
    work['A1']['audit_status']=audit.get('quality','OPEN')
    central_path=f"{WORK['A2']}/CHECKPOINT.json";central,central_sha=load(root,central_path)
    refs[central_path]={'git_blob_sha':central_sha,'kind':'central_checkpoint_non_authoritative'}
    if 'L19' in str(central.get('scope','')) and work['A2']['active_lesson']!='A2-L19':
        alerts.append({'code':'A2_CENTRAL_CHECKPOINT_STALE','detail':'Workstream LATEST outranks central CHECKPOINT'})
    rows=[];locked={}
    prior_entries={r['id']:r for r in (previous or {}).get('lessons',[]) if r['content_lock']=='LOCKED'}
    if not prior_entries:
        frozen=root/'Portfolio/Menschen/P0-BASELINE-EVIDENCE.json'
        if frozen.is_file():
            original=json.loads(frozen.read_text('utf8'))
            for lvl,compact in original['stage7_git_blob_sha'].items():
                for entry in compact.split():
                    number,sha=entry.split(':',1)
                    prior_entries[f'{lvl}-L{int(number):02}']={'evidence_git_blob_sha':sha}
    prior=set(prior_entries)
    for lvl in ('A1','A2','B1'):
        locked[lvl]=0
        for n in range(1,25):
            cid=f'{lvl}-L{n:02}'; path=stage7_path(lvl,n)
            f=root/path
            found=f.is_file()
            entry={'id':cid,'level':lvl,'lesson_number':n,'content_lock':'NOT_LOCKED','stage':'NOT_STARTED_OR_IN_PROGRESS','evidence_path':None,'evidence_git_blob_sha':None,'artifact_sha256_reported_in_git':None,'runtime_final':False}
            if found:
                obj,sha=load(root,path)
                if not check_locked(obj,path):
                    if cid in prior or n in BASELINE[lvl]:raise ValueError(f'PREVIOUS_LOCK_LOST:{cid}')
                else:
                    if cid in prior_entries and prior_entries[cid].get('evidence_git_blob_sha') not in (None,sha):
                        raise ValueError(f'LOCKED_RECEIPT_EDIT_REQUIRES_EXPLICIT_SUCCESSOR:{cid}')
                    locked[lvl]+=1
                    entry.update(content_lock='LOCKED',stage='STAGE7_LOCKED',evidence_path=path,evidence_git_blob_sha=sha,artifact_sha256_reported_in_git=artifact_sha(obj))
                    refs[path]={'git_blob_sha':sha,'kind':'locked_stage7'}
            elif cid in prior or n in BASELINE[lvl]:
                raise ValueError(f'PREVIOUS_LOCK_RECEIPT_MISSING:{cid}')
            if cid=='A1-L01' and not found:entry.update(content_lock='HISTORICAL_V332_ONLY',stage='V336_REAUDIT_INCOMPLETE')
            if entry['content_lock']=='NOT_LOCKED' and cid==work[lvl]['active_lesson']:
                entry['stage']=work[lvl]['active_stage']
            entry['audit']='GLOBAL_OPEN_NO_IMPORT' if lvl=='A1' else 'LEVEL_FINAL_NOT_VERIFIED'
            entry['evidence_url']=WEB+path if entry['evidence_path'] else None
            rows.append(entry)
        if locked[lvl]<len(BASELINE[lvl]):raise ValueError(f'BASELINE_REGRESSION:{lvl}')
        if lvl!='A1' and locked[lvl]>0:
            latest_num=int(work[lvl]['active_lesson'].split('-L')[1])
            if latest_num<=locked[lvl] and not re.search(r'STAGE.?7|LOCKED',work[lvl]['active_stage'],re.I):
                raise ValueError(f'STAGE7_AHEAD_OF_WORKSTREAM_LATEST:{lvl}')
        if work[lvl]['active_lesson']!=f'{lvl}-L{min(24,locked[lvl]+1):02}' and lvl!='A1':
            alerts.append({'code':f'{lvl}_NONCONTIGUOUS_ACTIVE_LESSON','detail':'Review lesson authority and duplicate/reuse lineage'})
    if locked['A1']<23 or locked['A2']<19 or locked['B1']<18:raise ValueError('BASELINE_LOCK_REGRESSION')
    alerts.append({'code':'A1_L01_REAUDIT_OPEN','detail':'Historical v3.3.2 not promoted to v3.3.6'})
    alerts.append({'code':'A1_GLOBAL_AUDIT_NOT_APPLIED','detail':work['A1']['audit_milestone']})
    fingerprint=hashlib.sha256(json.dumps(refs,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'schema':'gcpk-menschen-portfolio-live@1.0.0','authority':'DERIVED_READ_ONLY','source_repository':REPO,
        'captured_utc':datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        'source_fingerprint':fingerprint,'counts':{'total_lessons':72,'locked_total':sum(locked.values()),'by_level':{k:{'total':24,'locked':v} for k,v in locked.items()}},
        'workstreams':work,'lessons':rows,'warnings':alerts,'evidence':refs,
        'verification_boundary':{'stage7_git_receipts_checked':sum(locked.values()),'content_zip_bytes_checked':False,'live_browser_srs_checked':False,'global_final':False}}


def render_md(d):
    lines=['# Menschen portfolio — live Git checkpoint view','',f"Source fingerprint: `{d['source_fingerprint']}`",'', '| Level | Stage7 LOCKED | Active | Stage |', '|---|---:|---|---|']
    for lvl,w in d['workstreams'].items():lines.append(f"| {lvl} | {d['counts']['by_level'][lvl]['locked']}/24 | {w['active_lesson']} | {w['active_stage']} |")
    lines+=['','> Read-only derived report; no global FINAL/import claims.','', '## All 72 lessons','', '| Lesson | Lock | Git evidence |','|---|---|---|']
    for row in d['lessons']:
        path=row['evidence_path'];link=f"[Stage7 receipt]({WEB+path})" if path else '—'
        lines.append(f"| {row['id']} | {row['content_lock']} | {link} |")
    lines+=['','## Open warnings']+[f"- {x['code']}: {x['detail']}" for x in d['warnings']]
    return '\n'.join(lines)+'\n'


def render_html(d):
    payload=json.dumps(d,ensure_ascii=False).replace('<','\\u003c').replace('&','\\u0026')
    return '''<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Menschen portfolio — live Git snapshot</title><style>body{font:15px system-ui,Tahoma,sans-serif;background:#f7f9fc;color:#18243e;max-width:1060px;margin:auto;padding:24px}header{background:#18325f;color:white;padding:23px;border-radius:16px}header h1{margin:0 0 8px}nav{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}input,select{padding:10px;border:1px solid #ccd4e2;border-radius:9px}input{flex:1}table{width:100%;border-collapse:collapse;background:white}td,th{padding:10px;border-bottom:1px solid #e8edf5;text-align:right}a{color:#176bd0}code{direction:ltr}small{color:#53667c}section{overflow:auto;border-radius:12px} .w{background:#fff3de;padding:10px;margin:8px 0;border-radius:9px}</style><header><h1>داشبورد مرکزی Menschen</h1><div id="totals"></div><small>فقط‌خواندنی؛ گزارش از وضعیت Git، نه تأیید محتوای ZIP یا مرورگر</small></header><nav><input id="q" placeholder="جست‌وجوی درس یا مرحله"><select id="lv"><option value="">همه سطوح</option><option>A1</option><option>A2</option><option>B1</option></select><select id="lock"><option value="">همه وضعیت‌ها</option><option>LOCKED</option><option>OPEN</option></select></nav><section><table><thead><tr><th>درس</th><th>مرحله</th><th>محتوا</th><th>رسید</th></tr></thead><tbody id="rows"></tbody></table></section><h3>هشدارها</h3><div id="warnings"></div><script id="data" type="application/json">''' +payload+ '''</script><script>const d=JSON.parse(document.getElementById('data').textContent),g=id=>document.getElementById(id);g('totals').textContent='۷۲ درس | A1 '+d.counts.by_level.A1.locked+'/24 | A2 '+d.counts.by_level.A2.locked+'/24 | B1 '+d.counts.by_level.B1.locked+'/24';function paint(){let q=g('q').value.toLowerCase(),lv=g('lv').value,lk=g('lock').value;g('rows').replaceChildren();for(let r of d.lessons){if(lv&&r.level!==lv)continue;if(lk==='LOCKED'&&r.content_lock!=='LOCKED')continue;if(lk==='OPEN'&&r.content_lock==='LOCKED')continue;if(q&&!`${r.id} ${r.stage}`.toLowerCase().includes(q))continue;let tr=document.createElement('tr');for(let v of [r.id,r.stage,r.content_lock]){let td=document.createElement('td');td.textContent=v;tr.append(td)}let td=document.createElement('td');if(r.evidence_url){let a=document.createElement('a');a.href=r.evidence_url;a.textContent='GitHub';td.append(a)}tr.append(td);g('rows').append(tr)}}for(let id of ['q','lv','lock'])g(id).addEventListener('input',paint);paint();for(let w of d.warnings){let e=document.createElement('div');e.className='w';e.textContent=w.code+' — '+w.detail;g('warnings').append(e)}</script></html>'''


def main():
    p=argparse.ArgumentParser();p.add_argument('--repo-root',required=True);p.add_argument('--out',required=True);p.add_argument('--check',action='store_true');a=p.parse_args()
    out=Path(a.out);prior=None
    if (out/'PORTFOLIO-STATUS.json').is_file():prior=json.loads((out/'PORTFOLIO-STATUS.json').read_text('utf-8'))
    d=generate(a.repo_root,prior)
    if a.check:
        print(json.dumps({'ok':True,'counts':d['counts'],'fingerprint':d['source_fingerprint']},ensure_ascii=False));return
    out.mkdir(parents=True,exist_ok=True)
    old_fp=prior.get('source_fingerprint') if prior else None
    if old_fp==d['source_fingerprint']:
        print('UNCHANGED_EVIDENCE_NO_REWRITE');return
    (out/'PORTFOLIO-STATUS.json').write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n','utf8')
    (out/'DASHBOARD.md').write_text(render_md(d),'utf8')
    (out/'DASHBOARD.html').write_text(render_html(d),'utf8')
    (out/'REFRESH-STATE.json').write_text(json.dumps({'schema':'gcpk-menschen-portfolio-refresh@1','fingerprint':d['source_fingerprint'],'captured_utc':d['captured_utc'],'authority':'DERIVED_READ_ONLY','locked':d['counts']['locked_total'],'status':'PASS_SNAPSHOT_ONLY_NOT_GLOBAL_FINAL'},indent=2)+'\n','utf8')
    print(json.dumps({'ok':True,'counts':d['counts'],'fingerprint':d['source_fingerprint'],'written':4},ensure_ascii=False))

if __name__=='__main__':main()