#!/usr/bin/env python3
"""Read-only lexical display-maintenance gate; never full Stage4/5 or app acceptance."""
import argparse, copy, csv, hashlib, io, json, re, zipfile
from pathlib import Path

def sha(b): return hashlib.sha256(b).hexdigest()
def encoded(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
def need(ok, label):
    if not ok: raise ValueError(label)
def obj(b):
    def unique(pairs):
        result = {}
        for k,v in pairs:
            need(k not in result, 'duplicate JSON key: '+k)
            result[k]=v
        return result
    return json.loads(b, object_pairs_hook=unique)
def member(z, prefix, suffix):
    found=[n for n in z.namelist() if n.startswith(prefix) and n.endswith(suffix)]
    need(len(found)==1, 'ambiguous member: '+prefix+' '+suffix)
    return z.read(found[0])
def archive(z):
    names=z.namelist(); need(len(names)==len(set(names)), 'duplicate ZIP member')
    need(all(not n.startswith('/') and '\\' not in n and '..' not in n.split('/') for n in names), 'unsafe ZIP path')
    need(z.testzip() is None, 'ZIP CRC')
    m=obj(z.read('07-Checkpoint-State/MANIFEST.json'))['members']; checks=z.read('07-Checkpoint-State/SHA256SUMS.txt').decode().splitlines()
    sums={}
    for line in checks:
        digest,name=line.split(None,1); name=name.lstrip('*'); need(name not in sums, 'duplicate checksum'); sums[name]=digest
    actual={n for n in names if not n.endswith('/')}; special={'07-Checkpoint-State/MANIFEST.json','07-Checkpoint-State/SHA256SUMS.txt'}
    need(set(m)==actual-special and set(sums)==actual-{'07-Checkpoint-State/SHA256SUMS.txt'}, 'manifest coverage')
    for name,digest in sums.items():
        raw=z.read(name); need(sha(raw)==digest, 'SHA: '+name)
        if name in m: need(m[name]['sha256']==digest and m[name]['bytes']==len(raw), 'manifest: '+name)
    return len(sums)
def rows(raw):
    r=csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline=''),delimiter='\t'); out=list(r)
    need(r.fieldnames and len(r.fieldnames)==len(set(r.fieldnames)) and {'id','details','examples','custom_fields'}.issubset(r.fieldnames),'columns')
    need(out and all(None not in row and all(v is not None for v in row.values()) and row['id'] for row in out), 'row shape')
    need(len({x['id'] for x in out})==len(out),'duplicate ID')
    return r.fieldnames,out
NOTE_TITLES={'Grammatik','Struktur','Rektionshinweis','Stilhinweis zu Zielangaben','Sinngrenze bei den Verbformen','Gebrauchsabgrenzung','Bedeutungshinweis','Wortgeschichte'}
MARKER=re.compile(r'\b(?:Synonym-Grenze|Argument-Rahmen)\s*\(R\d+\)|\bscreenshot-\d+\s+row-\d+\b',re.I)
def plain_marker(before,after): return re.sub(r' \(R\d+\)', '',before)==after and bool(re.search(r' \(R\d+\)',before))
def replay(old,new,delta,review):
    f,a=rows(old); g,b=rows(new); need(f==g and [r['id'] for r in a]==[r['id'] for r in b],'identity/order/schema changed')
    by={r['id']:r for r in a}; after={r['id']:r for r in b}; edits={}; manual={}; count=0
    for c in delta['changes']:
        cid,title,i=c['id'],c['section'],c['item_index']; key=(cid,title,i)
        need(cid in by and title in NOTE_TITLES and type(i) is int and i>=0 and key not in edits,'unsupported/duplicate edit')
        need(isinstance(c['before'],str) and (c['after'] is None or isinstance(c['after'],str) and c['after'].strip()) and c['before']!=c['after'],'bad item')
        edits[key]=c
        if not plain_marker(c['before'],c['after']): manual[sha(encoded(c))]=c
    decisions=review['manual_decisions']; need(set(decisions)==set(manual) and all(isinstance(v,str) and v.strip() for v in decisions.values()),'exact manual note review missing')
    changed=[]; ex_count=0
    for cid,x in by.items():
        y=after[cid]; need(all(x[k]==y[k] for k in f if k!='details'),'non-details field changed: '+cid)
        for key in ('custom_fields','examples','related','opposites'):
            if key in y: obj(y[key])
        ex_count+=len(obj(y['examples']))
        d=obj(x['details']); target=obj(y['details']); result=copy.deepcopy(d)
        for section in result:
            title=section['title']; olditems=section['items']; newitems=[]
            for i,item in enumerate(olditems):
                edit=edits.pop((cid,title,i),None)
                if edit:
                    need(item==edit['before'],'before mismatch'); item=edit['after']; count+=1
                if item is not None: newitems.append(item)
            section['items']=newitems
            need(newitems and not any(isinstance(v,str) and MARKER.search(v) for v in newitems),'empty tile or remaining marker: '+cid)
        need(result==target,'unrecorded details edit: '+cid)
        if d!=target: changed.append(cid)
    need(not edits and count==delta['changed_items'] and sorted(changed)==sorted(delta['changed_card_ids']),'delta count mismatch')
    need(count>0,'empty delta')
    return {'cards':len(a),'changed_cards':len(changed),'unchanged_cards':len(a)-len(changed),'changed_items':count,'manual_note_reviews':len(manual),'example_sets':ex_count}
def run(parent,candidate,review):
    ph=sha(parent.read_bytes()); ch=sha(candidate.read_bytes()); need(ph==review['parent_zip_sha256'] and ch==review['candidate_zip_sha256'],'owner package hash mismatch')
    with zipfile.ZipFile(parent) as p, zipfile.ZipFile(candidate) as c:
        pc,cc=archive(p),archive(c); old=member(p,'01-Final-Import/','.tsv'); new=member(c,'01-Import-Candidate/','.tsv'); oh,nh=sha(old),sha(new)
        need(oh==review['parent_import_sha256'] and nh==review['candidate_import_sha256']==review['user_import_sha256'] and review['user_import']=='PASS_USER_REPORTED','exact import acceptance missing')
        s4=obj(member(p,'05-QA-Tests/','OFFICIAL-STAGE4-GATE-PASS.json')); s5=obj(member(p,'05-QA-Tests/','OFFICIAL-STAGE5-QUALITY-GATE-PASS.json'))
        need(s4['status']=='PASS_RISK_BASED_STAGE4' and s4['source_sha256']==oh and not s4['blockers'],'parent Stage4 evidence')
        need(s5['status']=='PASS_STAGE5_CANDIDATE_WITH_EXACT_SOURCE_STAGE4_AND_RULE_COVERAGE' and s5['quality_gate']['source_tsv_sha256']==oh and not s5['quality_gate']['blockers'],'parent Stage5 evidence')
        d=obj(member(c,'05-QA-Tests/','display-cleanup-delta.json')); need(d['parent_zip_sha256']==ph and d['parent_import_sha256']==oh and d['candidate_import_sha256']==nh,'delta hash mismatch')
        counts=replay(old,new,d,review)
        need(member(p,'03-Source-Provenance/','.tsv')==member(c,'03-Source-Provenance/','.tsv'),'source map changed')
        for prefix,suffix,key in [('02-Canonical-Data/','canonical.json','cards'),('04-Enrichment-Work/','enrichment-ledger.json','candidates')]:
            x=obj(member(p,prefix,suffix)); y=obj(member(c,prefix,suffix)); need(x[key]==y[key],'semantic authority changed: '+key)
            extra=set(y)-set(x); need(len(extra)==1 and next(iter(extra)).endswith('_display_cleanup_overlay'),'unexpected overlay')
            overlay=y.pop(next(iter(extra))); need(overlay['changes']==d['changes'] and overlay['candidate_import_sha256']==nh,'overlay mismatch')
            allowed={'status','metadata_only_repack'} | ({'canonical_sha256'} if key=='candidates' else set())
            need({k:v for k,v in x.items() if k not in allowed}=={k:v for k,v in y.items() if k not in allowed},'authority metadata changed')
        need(member(c,'06-Reports/Historical-Parent/','.zip')==parent.read_bytes(),'rollback parent missing')
        return {'schema':'gcpk-display-delta-maintenance@1','status':'PASS_CONTENT_ONLY_DISPLAY_DELTA','parent_zip_sha256':ph,'candidate_zip_sha256':ch,'parent_import_sha256':oh,'candidate_import_sha256':nh,'parent_manifest_checks':pc,'candidate_manifest_checks':cc,**counts,'prior_stage4_stage5':'INHERITED_UNCHANGED_SCOPE_ONLY','new_full_stage4_stage5':'NOT_CLAIMED','native_stage6_stage7':'NOT_CLAIMED','user_import':'PASS_USER_REPORTED'}
def main():
    a=argparse.ArgumentParser(); a.add_argument('parent',type=Path); a.add_argument('candidate',type=Path); a.add_argument('review',type=Path); a.add_argument('--receipt',type=Path,required=True); v=a.parse_args()
    result=run(v.parent,v.candidate,obj(v.review.read_bytes())); v.receipt.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
