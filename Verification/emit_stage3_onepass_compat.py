#!/usr/bin/env python3
"""Stage3A/3B/3C legacy VIEW emitter from ONE approved workstream authoring ledger.

No semantic conclusions or new work are inferred. Existing consumer schemas are
workstream-specific; these views are lossless intermediate compatibility records,
NOT reconstructed historical Stage3C certified receipts.
"""
import argparse,hashlib,json,re,sys
from pathlib import Path

SHA=re.compile(r'[0-9a-f]{64}\Z')
DECISIONS={'VERIFIED_PRESENT','CLOSED_NO_FORCE','NOT_APPLICABLE','HOLD'}
SCHEMA='gcpk-stage3-onepass@1.0'
def unique(pairs):
    out={}
    for key,value in pairs:
        if key in out:raise ValueError('DUPLICATE_JSON_KEY:'+key)
        out[key]=value
    return out

def sha(data):return hashlib.sha256(data).hexdigest()

def project(ledger, current_bytes):
    if not isinstance(ledger,dict) or ledger.get('schema')!=SCHEMA:
        raise ValueError('INVALID_ONEPASS_SCHEMA')
    declared=ledger.get('working_sha256')
    if not isinstance(declared,str) or not SHA.fullmatch(declared) or sha(current_bytes)!=declared:
        raise ValueError('WORKING_BYTES_SHA_MISMATCH')
    source=ledger.get('registered_source_sha256')
    if not isinstance(source,str) or not SHA.fullmatch(source):
        raise ValueError('SOURCE_UNPINNED')
    cards=ledger.get('cards')
    if not isinstance(cards,list) or not cards:
        raise ValueError('EMPTY_CARD_UNIVERSE')
    a=[];b=[];c=[];ids=set();open_holds=0
    for row in cards:
        if not isinstance(row,dict):raise ValueError('INVALID_CARD')
        uid=row.get('id')
        if not isinstance(uid,str) or not uid.strip() or uid in ids:
            raise ValueError('EMPTY_OR_DUPLICATE_ID')
        ids.add(uid)
        baseline=row.get('baseline')
        changes=row.get('changes',[])
        decisions=row.get('decisions',{})
        if not isinstance(baseline,dict) or not isinstance(changes,list) or not isinstance(decisions,dict):
            raise ValueError('INVALID_ONEPASS_CARD_FIELDS')
        if not decisions:
            raise ValueError('MISSING_CARD_DECISIONS:'+uid)
        for key,record in decisions.items():
            if not isinstance(key,str) or not key.strip() or not isinstance(record,dict):
                raise ValueError('INVALID_FACET_DECISION:'+uid)
            choice=record.get('decision')
            if choice not in DECISIONS:raise ValueError('INVALID_FACET_DECISION:'+uid+':'+key)
            if choice in {'CLOSED_NO_FORCE','NOT_APPLICABLE','HOLD'} and not str(record.get('reason','')).strip():
                raise ValueError('MISSING_EXCEPTION_REASON:'+uid+':'+key)
            if choice=='HOLD':open_holds+=1
        if any(not isinstance(change,dict) or not str(change.get('field','')).strip() or
               not str(change.get('reason_code','')).strip() for change in changes):
            raise ValueError('INVALID_CHANGE_RECORD:'+uid)
        a.append({'id':uid,'baseline':baseline})
        b.append({'id':uid,'changes':changes})
        c.append({'id':uid,'decisions':decisions})
    common={'schema':'gcpk-stage3-onepass-compatible-view@1.0','workstream':ledger.get('workstream'),
            'working_sha256':declared,'registered_source_sha256':source,
            'cards':len(ids),'original_onepass_input_sha256':ledger.get('_ledger_sha256'),
            'status':'COMPATIBILITY_VIEW_NOT_OFFICIAL_STAGE_PASS'}
    return {'3A':dict(common,stage='3A',items=a),
            '3B':dict(common,stage='3B',items=b),
            '3C':dict(common,stage='3C',items=c,open_holds=open_holds)}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--onepass',type=Path,required=True)
    p.add_argument('--current-bytes',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True,help='One JSON bundle; no per-card files')
    p.add_argument('--emit-legacy-views',action='store_true',
                   help='Emit optional 3A/3B/3C view files into output parent, not certified old schemas')
    args=p.parse_args(argv)
    try:
        data=args.onepass.read_bytes()
        doc=json.loads(data.decode('utf-8'),object_pairs_hook=unique)
        doc['_ledger_sha256']=sha(data)
        views=project(doc,args.current_bytes.read_bytes())
        result={'schema':'gcpk-stage3-onepass-output@1.0',
                'compatibility_status':'VIEWS_READY_NOT_WORKSTREAM_CONSUMER_APPROVED',
                'views':views}
        if args.output.resolve() in {args.onepass.resolve(),args.current_bytes.resolve()}:
            raise ValueError('OUTPUT_MUST_NOT_OVERWRITE_SOURCE')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
        if args.emit_legacy_views:
            for label,view in views.items():
                path=args.output.parent/('stage'+label.lower()+'-view.json')
                if path.resolve() in {args.onepass.resolve(),args.current_bytes.resolve()}:
                    raise ValueError('VIEW_PATH_CONFLICT')
                path.write_text(json.dumps(view,ensure_ascii=False,indent=2)+'\n','utf-8')
        print(json.dumps({'status':result['compatibility_status'],'cards':views['3A']['cards'],
                          'holds':views['3C']['open_holds']}))
        return 0
    except (ValueError,TypeError,KeyError,OSError,UnicodeError) as exc:
        print(json.dumps({'status':'BLOCKED_ONEPASS_INTEGRITY','reason':str(exc)}),file=sys.stderr)
        return 3
if __name__=='__main__':raise SystemExit(main())
