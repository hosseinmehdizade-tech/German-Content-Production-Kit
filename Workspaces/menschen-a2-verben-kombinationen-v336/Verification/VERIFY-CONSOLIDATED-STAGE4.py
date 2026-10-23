#!/usr/bin/env python3
"""Verify exact consolidated Menschen A2 Verben Stage4 WIP archive.
Read-only stdlib validator. PASS is *technical only*, never independent linguistic approval.
Usage: python VERIFY-CONSOLIDATED-STAGE4.py ARCHIVE.zip [EXPECTED_SHA256]
"""
import csv, hashlib, io, json, pathlib, sys, zipfile

def die(m): raise ValueError(m)
def sha(b): return hashlib.sha256(b).hexdigest()
def table(z,n): return list(csv.DictReader(io.StringIO(z.read(n).decode('utf-8-sig')),delimiter='\t'))
def assert_eq(a,b,msg):
    if a!=b: die(f'{msg}: {str(a)[:110]} != {str(b)[:110]}')

def verify(path, expected=None):
    package=pathlib.Path(path)
    outer_sha=sha(package.read_bytes())
    if expected: assert_eq(outer_sha,expected,'outer SHA256')
    with zipfile.ZipFile(package) as z:
        assert_eq(z.testzip(),None,'zip CRC')
        names=z.namelist()
        if len(names)!=len(set(names)): die('duplicate ZIP names')
        if any(n.startswith('/') or '..' in pathlib.PurePosixPath(n).parts or '\\' in n for n in names): die('unsafe ZIP path')
        manifest_name='07-Checkpoint-State/SHA256SUMS.json'
        m=json.loads(z.read(manifest_name)); files=m['file_sha256']
        assert_eq(set(files),set(names)-{manifest_name},'manifest member set')
        for name,digest in files.items():
            assert_eq(sha(z.read(name)),digest,'member SHA256 '+name)
        canon=z.read('02-Canonical-Data/CURRENT-CANONICAL-AND-PROJECTION.tsv')
        assert_eq(sha(canon),m['source_candidate_sha256'],'active candidate digest')
        assert_eq(z.read('01-Final-Import/NOT-FINAL-NOT-IMPORT-AUTHORIZED.tsv'),canon,'working TSV mirror')
        cards=table(z,'02-Canonical-Data/CURRENT-CANONICAL-AND-PROJECTION.tsv')
        queue=table(z,'04-Independent-Review/REVIEW-QUEUE-1423-PENDING.tsv')
        ex=table(z,'04-Independent-Review/EXAMPLES-1168-UNREVIEWED.tsv')
        syn=table(z,'04-Independent-Review/SYNONYMS-243-UNREVIEWED.tsv')
        dsp=table(z,'04-Independent-Review/DISPLAY-12-PENDING.tsv')
        assert_eq(len(cards),292,'card count')
        assert_eq(len({r['id'] for r in cards}),292,'unique card IDs')
        assert_eq((len(ex),len(syn),len(dsp),len(queue)),(1168,243,12,1423),'review queues')
        assert_eq(len({r['review_id'] for r in queue}),1423,'review ID uniqueness')
        by_q={x['review_id']:x for x in queue}
        assert_eq({x['id'] for x in ex},set(k for k,v in by_q.items() if v['kind']=='EXAMPLE'),'example membership')
        assert_eq({x['id'] for x in syn},set(k for k,v in by_q.items() if v['kind']=='SYNONYM'),'synonym membership')
        assert_eq({x['item_id'] for x in dsp},set(k for k,v in by_q.items() if v['kind']=='DISPLAY_SYNONYM_SUPPLEMENT'),'display membership')
        if any(q['review_status']!='NOT_REVIEWED' or q['qualified_reviewer_id'] for q in queue): die('unverified external review state changed')
        byex={x['id']:x for x in ex}; bysyn={x['id']:x for x in syn}
        rels=set(); typed=set(); visible=0
        for r in cards:
            f=json.loads(r['custom_fields']); cid=r['id']; data=json.loads(r['examples'])
            assert_eq(data,f['canonical_unit']['examples'],'canonical example parity '+cid)
            assert_eq(data,f['presentation_examples'],'presentation example parity '+cid)
            assert_eq(len(data),4,'four examples '+cid)
            assert_eq((r['back'],f['vnext_translation_fa']),(f['canonical_unit']['persian_meaning'],)*2,'FA mirror '+cid)
            for e in data:
                rid=e['id'];q=by_q[rid];v=byex[rid]; tt={x['lang']:x['text'] for x in e['translations']}
                assert_eq((q['card_id'],q['de'],q['fa'],q['en'],q['fingerprint']),
                  (cid,e['text'],tt['fa-IR'],tt['en-US'],v['fingerprint']),'example queue parity '+rid)
            canonical=f['canonical_relations']; vn=[x for g in f['vnext_relations'] for x in g['items']]
            assert_eq({x['relation_id'] for x in vn},{x['relation_id'] for x in canonical},'relation IDs '+cid)
            for x in canonical:
                rid=x['relation_id']
                if rid in rels: die('duplicate relation '+rid)
                rels.add(rid)
                if x['relation_type']=='SYNONYM':
                    typed.add(rid);v=by_q[rid];ss=bysyn[rid]
                    term=x['value'].get('term') or x['value'].get('text') if isinstance(x['value'],dict) else x['value']
                    scope=x['value'].get('scope') if isinstance(x['value'],dict) else x.get('scope')
                    assert_eq((v['card_id'],v['term'],v['scope'],v['fingerprint']),(cid,term,scope,ss['fingerprint']),'synonym parity '+rid)
            visible+=sum(len(x['items']) for x in json.loads(r['details']) if x['title']=='Synonyme')
        assert_eq((len(rels),len(typed),visible),(1209,243,255),'relation/display counts')
        assert_eq(set(bysyn),typed,'typed synonym exact ids')
        for d in dsp:
            q=by_q[d['item_id']]
            assert_eq((q['card_id'],q['term']),(d['card_id'],d['display_synonym']),'display supplement '+d['item_id'])
        state=json.loads(z.read('07-Checkpoint-State/CHECKPOINT.json'))
        assert_eq(state['stage'],'STAGE4_WIP','not FINAL')
        assert_eq(state['independent_review']['unreviewed'],1423,'review gate')
        return {'technical':'PASS','linguistic_external':'BLOCKED','import_authorized':False,
                'outer_sha256':outer_sha,'verified_manifest_members':len(files),
                'cards':len(cards),'trilingual_examples':len(ex),'typed_synonyms':len(syn),
                'display_synonym_supplements':len(dsp),'relations':len(rels),'review_queue':len(queue)}

if __name__=='__main__':
    try:
        if len(sys.argv) not in (2,3): die('usage: verifier ARCHIVE.zip [EXPECTED_SHA256]')
        print(json.dumps(verify(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else None),indent=2))
    except Exception as e:
        print('FAIL:',str(e),file=sys.stderr);sys.exit(1)
