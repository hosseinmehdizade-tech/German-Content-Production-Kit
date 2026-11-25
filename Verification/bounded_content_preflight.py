"""Finite principal-form, attested raw-source and display-only regression gates.

These gates verify controlled contracts and exact evidence bindings, not general
German linguistic truth. Canonical relations are never deleted or rewritten.
"""
import argparse, csv, hashlib, io, json, pathlib, copy, re

def sha(data):
    return hashlib.sha256(data).hexdigest()

def unique_display(items):
    """Collapse identical strings in order; preserve structured authority items."""
    out, seen = [], set()
    for value in items:
        if isinstance(value, str):
            if value in seen:
                continue
            seen.add(value)
        out.append(value)
    return out

# Exact production-marker families, not a general German-language blacklist.
# Inspect only explicit learner-facing details, never canonical audit metadata.
LEARNER_REVIEW_MARKER = re.compile(
    r'\b(?:Synonym-Grenze|Argument-Rahmen)\s*\(R\d+\)'
    r'|\bscreenshot-\d+\s+row-\d+\b'
    r'|\b(?:Originalquelle|Quellenzeile|Lehrwerkszeile|Kurszeile)\b.{0,100}\b(?:belegt|dokumentiert|enthält|formuliert)\b',
    re.I,
)

def learner_review_marker_errors(rows):
    errors = []
    for row in rows:
        details = row.get('details') or []
        if isinstance(details, str):
            details = json.loads(details)
        for section in details:
            for index, item in enumerate(section.get('items', [])):
                if isinstance(item, str) and LEARNER_REVIEW_MARKER.search(item):
                    errors.append(f'{row.get("id")}: LEARNER_INTERNAL_REVIEW_MARKER:{section.get("title")}:{index}')
    return errors

def projection_errors(rows):
    errors = learner_review_marker_errors(rows)
    for row in rows:
        cf = row.get('custom_fields') or row.get('customFields') or {}
        if isinstance(cf, str):
            cf = json.loads(cf)
        cid = row.get('id')
        morph = cf.get('vnext_morphology') or {}
        perfect = cf.get('perfect') or morph.get('perfect')
        auxiliary = morph.get('auxiliary')
        # Single, explicitly declared auxiliaries only. Mixed auxiliaries and
        # exceptional principal-part contracts need their own reviewed binding.
        if perfect and auxiliary in {'haben', 'sein'}:
            head = perfect.strip().split()[0]
            if head in {'haben', 'sein', 'hat', 'ist'} and head != {'haben':'hat','sein':'ist'}[auxiliary]:
                errors.append(f'{cid}: NONFINITE_OR_MISMATCHED_PERFECT')
        if morph.get('perfect') and cf.get('perfect') and morph['perfect'] != cf['perfect']:
            errors.append(f'{cid}: PERFECT_CANONICAL_BRIDGE_MISMATCH')
        for key in ['related', 'opposites']:
            values = row.get(key) or []
            if isinstance(values, str):
                values = json.loads(values)
            if values != unique_display(values):
                errors.append(f'{cid}: DUPLICATE_RELATION_DISPLAY:{key}')
        details = row.get('details') or []
        if isinstance(details, str):
            details = json.loads(details)
        for section in details:
            if section.get('title') in {'Synonyme', 'Antonyme'} and section.get('items', []) != unique_display(section.get('items', [])):
                errors.append(f'{cid}: DUPLICATE_RELATION_DISPLAY:{section["title"]}')
    return errors

def source_errors(occurrences, binding, evidence_root=None):
    errors = []
    by = {x['occurrence_id']:x for x in occurrences['occurrences']}
    for item in binding['bindings']:
        oid = item['occurrence_id']
        row = by.get(oid)
        if row is None or row['raw_text'] != item['raw_text']:
            errors.append(f'{oid}: SOURCE_RAW_TEXT_BINDING_MISMATCH')
        if row is None or any(row['locator'].get(k) != v for k,v in item['locator'].items()):
            errors.append(f'{oid}: SOURCE_LOCATOR_BINDING_MISMATCH')
        if sha(item['raw_text'].encode('utf-8')) != item['raw_text_sha256']:
            errors.append(f'{oid}: TRANSCRIPTION_HASH_MISMATCH')
        if evidence_root and sha((pathlib.Path(evidence_root)/item['source_image']).read_bytes()) != item['source_image_sha256']:
            errors.append(f'{oid}: SOURCE_IMAGE_HASH_MISMATCH')
    return errors

def self_test():
    fixture={'id':'fixture','custom_fields':{'vnext_morphology':{'auxiliary':'sein','perfect':'ist gegangen'},'perfect':'ist gegangen'},'related':['gehen'],'details':[]}
    assert projection_errors([fixture]) == []
    for value in ['sein gegangen','hat gegangen']:
        bad=copy.deepcopy(fixture);bad['custom_fields']['perfect']=value
        assert projection_errors([bad])
    bad=copy.deepcopy(fixture);bad['related']=['gehen','gehen'];assert projection_errors([bad])
    bad=copy.deepcopy(fixture);bad['details']=[{'title':'Synonyme','items':['gehen','gehen']}];assert projection_errors([bad])
    authority=[{'relation_id':'one','scope':'first'},{'relation_id':'two','scope':'second'}]
    assert unique_display(authority)==authority
    occ={'occurrences':[{'occurrence_id':'fixture','raw_text':'faszinierte','locator':{'source_order':70}}]}
    bind={'bindings':[{'occurrence_id':'fixture','raw_text':'faszinierte','raw_text_sha256':sha(b'faszinierte'),'locator':{'source_order':70}}]}
    assert source_errors(occ,bind)==[]
    bad=copy.deepcopy(occ);bad['occurrences'][0]['raw_text']='fasziniert';assert source_errors(bad,bind)
    bad=copy.deepcopy(occ);bad['occurrences'][0]['locator']['source_order']=71;assert source_errors(bad,bind)
    # Learner output vs internal evidence: reject markers without rewriting data.
    for marker in ['Synonym-Grenze (R23): beide mit Akkusativ',
                   'Argument-Rahmen (R43): an + Dat.',
                   'Originalquelle in screenshot-10 row-2 enthält die Kollokation',
                   'Die Kurszeile ist im Original belegt.']:
        bad=copy.deepcopy(fixture);bad['details']=[{'title':'Grammatik','items':[marker]}]
        assert learner_review_marker_errors([bad]) and projection_errors([bad])
    good=copy.deepcopy(fixture)
    good['details']=[{'title':'Grammatik','items':['Synonym-Grenze: beide mit Akkusativ','hoffen, dass ...','Modell R2','Rektion: auf + Akkusativ']}]
    good['custom_fields']['internal_review']='Synonym-Grenze (R23): screenshot-10 row-2'
    assert not learner_review_marker_errors([good])
    assert not projection_errors([good])
    return {'status':'PASS','negative_fixtures':10,'positive_sein_and_distinct_scopes':'PASS','learner_review_marker_positive':'PASS'}

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['projection','source','self-test']);p.add_argument('path',nargs='?');p.add_argument('--binding');p.add_argument('--binding-sha256');p.add_argument('--evidence-root');a=p.parse_args()
    if a.mode=='self-test':
        print(json.dumps(self_test()));return 0
    path=pathlib.Path(a.path)
    if a.mode=='projection':
        rows=list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8-sig')),delimiter='\t')) if path.suffix=='.tsv' else json.loads(path.read_text(encoding='utf-8-sig'))
        errors=projection_errors(rows)
    else:
        b=pathlib.Path(a.binding);errors=[]
        if not a.binding_sha256 or sha(b.read_bytes()) != a.binding_sha256:
            errors.append('UNPINNED_OR_CHANGED_SOURCE_BINDING')
        errors+=source_errors(json.loads(path.read_text(encoding='utf-8-sig')),json.loads(b.read_text(encoding='utf-8-sig')),a.evidence_root)
    print(json.dumps({'status':'FAIL' if errors else 'PASS','gate':a.mode,'errors':errors},ensure_ascii=False,indent=2));return bool(errors)

if __name__=='__main__':
    raise SystemExit(main())
