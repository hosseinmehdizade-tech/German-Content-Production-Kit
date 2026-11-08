#!/usr/bin/env python3
"""Lean didactic scanner 1.1: source-bound advisory signals, no duplicate approval gate."""
import argparse,csv,hashlib,io,json,re,sys,unicodedata,zipfile
from collections import Counter
from pathlib import Path

PLACEHOLDERS={'jdn':'jemanden','jdm':'jemandem','jds':'jemandes','jd':'jemand','etw':'etwas','jmd':'jemand','jem':'jemand','jn':'jemanden'}
STOP={'sich','der','die','das','den','dem','des','ein','eine','einen','einem','einer','ich','du','er','sie','es','wir','ihr','man','mir','dir','uns','euch','ihn','ihm','ist','sind','war','wird','haben','hat','habe','und','oder','aber','im','am','zum','zur','auf','an','bei','mit','in','von','für','über','durch','um','nach','vor','als','zu'}
WORD=re.compile(r'[^\W_]+',re.U)
FIELDS={'id','front','details','examples'}

def tokens(value):
    s=unicodedata.normalize('NFKC',str(value)).casefold().replace('ß','ss')
    s=re.sub(r'\b(jdn|jdm|jds|jd|etw|jmd|jem|jn)\.',r'\1',s)
    return [PLACEHOLDERS.get(w,w) for w in WORD.findall(s)]
def normal(v): return ' '.join(tokens(v))
def meaningful(v): return [x for x in tokens(v) if x not in STOP]
def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('DUPLICATE_JSON_KEY:'+key)
        result[key]=value
    return result
def decode_json(raw,field):
    try:return json.loads(raw,object_pairs_hook=unique_object)
    except (ValueError,TypeError) as exc:raise ValueError('INVALID_'+field.upper()+'_JSON') from exc
def extract_rows(data):
    reader=csv.DictReader(io.StringIO(data.decode('utf-8-sig'),newline=''),delimiter='\t')
    if not reader.fieldnames or not FIELDS.issubset(reader.fieldnames):
        raise ValueError('INCOMPATIBLE_TSV_HEADER')
    rows=list(reader)
    if not rows:raise ValueError('EMPTY_TSV')
    ids=set()
    for row in rows:
        cid=row.get('id')
        if not cid or cid in ids:raise ValueError('EMPTY_OR_DUPLICATE_CARD_ID')
        ids.add(cid)
        if None in row:raise ValueError('INVALID_TSV_FIELD_COUNT')
    return rows
def split_lexical_bilingual_surface(item):
    """Keep German internal en dashes; split only real DE/FA display delimiters.

    An en dash inside a German pattern (e.g. 'wohin? – wo?') is not a
    translation separator. A spaced em dash remains the legacy fallback.
    """
    for match in re.finditer(r"\s+[—–]\s+",item):
        following=item[match.end():].lstrip()
        if following and re.match(r"[\u0600-\u06ff\u0750-\u077f]",following):
            return item[:match.start()].strip()
    return item.split(" — ",1)[0].strip()


def combos(row):
    sections=decode_json(row['details'],'details')
    if not isinstance(sections,list):raise ValueError('INVALID_DETAILS_SECTIONS')
    for section in sections:
        if not isinstance(section,dict):raise ValueError('INVALID_DETAILS_ITEM')
        if str(section.get('title','')).strip().casefold()!='kombinationen':continue
        items=section.get('items',[])
        if not isinstance(items,list):raise ValueError('INVALID_COMBINATION_LIST')
        for item in items:
            if isinstance(item,dict):de=item.get('de') or item.get('text') or ''
            elif isinstance(item,str):de=split_lexical_bilingual_surface(item)
            else:raise ValueError('INVALID_COMBINATION_ITEM')
            if str(de).strip():yield str(de).strip()
def german_examples(row):
    entries=decode_json(row['examples'],'examples')
    if not isinstance(entries,list):raise ValueError('INVALID_EXAMPLES')
    for item in entries:
        if isinstance(item,str):
            if not item.strip():raise ValueError('EMPTY_GERMAN_EXAMPLE')
            yield item
        elif isinstance(item,dict):
            if str(item.get('lang','de-DE')).lower().startswith('de'):
                de=item.get('text',item.get('text_de',item.get('de','')))
                if not isinstance(de,str) or not de.strip():
                    raise ValueError('EMPTY_GERMAN_EXAMPLE')
                yield de
        else:
            raise ValueError('UNKNOWN_EXAMPLE_FORMAT')
def analyze_rows(rows,name,source_sha):
    flags=[];total=0
    for row in rows:
        seen={};exs=list(german_examples(row))
        for item in combos(row):
            total+=1
            n=normal(item);words=tokens(item);important=meaningful(item)
            def flag(rule,risk,evidence):
                flags.append({'card_id':row['id'],'item_de':item,'rule':rule,'risk_signal':risk,
                              'evidence':evidence,'disposition':'ADVISORY_UNDECIDED'})
            if n in seen:flag('NORMALIZED_WITHIN_CARD_DUPLICATE','MEDIUM',seen[n])
            seen[n]=item
            if n==normal(row['front']):flag('BARE_HEADWORD_REPACKAGED','LOW','matches front')
            if len(words)<3 and n!=normal(row['front']):flag('VERY_SHORT_GENERIC','INFO','under three tokens')
            overlap=False
            if len(words)>=2:
                for e in exs:
                    et=tokens(e)
                    if any(et[k:k+len(words)]==words for k in range(len(et)-len(words)+1)):
                        flag('LITERAL_EXAMPLE_SUBSPAN','LOW',e[:180]);overlap=True;break
            if not overlap and len(important)>=3:
                for e in exs:
                    ew=meaningful(e)
                    if len(set(important)&set(ew))>=3 and len(set(important)&set(ew))/max(1,len(set(important)))>=.8:
                        flag('EXAMPLE_OVERLAP_POSSIBLE','INFO',e[:180]);break
    return {'source_tsv':name,'source_tsv_sha256':source_sha,'cards':len(rows),'items':total,
            'flags':flags,'rule_counts':dict(Counter(x['rule'] for x in flags)),
            'note':'Advisory; no per-signal editorial approval required.'}
def analyze_input(path,member=None):
    if path.suffix.lower()!='.zip':
        if member:raise ValueError('MEMBER_ONLY_FOR_ZIP')
        raw=path.read_bytes()
        return [analyze_rows(extract_rows(raw),path.name,hashlib.sha256(raw).hexdigest())]
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError('ZIP_CRC_FAILURE')
        names=[n for n in z.namelist() if n.lower().endswith('.tsv') and not n.startswith('__MACOSX/')]
        if member:
            if member not in names:raise ValueError('TSV_MEMBER_NOT_PRESENT')
            names=[member]
        tables=[]
        for name in names:
            data=z.read(name)
            try:rows=extract_rows(data)
            except ValueError as exc:
                if not member and str(exc)=='INCOMPATIBLE_TSV_HEADER':continue
                raise
            tables.append(analyze_rows(rows,name,hashlib.sha256(data).hexdigest()))
        if not tables:raise ValueError('NO_VALID_TSV_MEMBER')
        return tables
def accept_existing_stage4(path,receipt):
    root=Path(__file__).resolve().parents[1]
    policy=root/'STAGE4-RISK-BASED-ACCEPTANCE-POLICY-v1.0.1.json'
    verified_module=root/'Verification/RiskBasedStage4/risk_based_stage4_gate.py'
    if path.suffix.lower()=='.zip':raise ValueError('RISK_GATE_REQUIRES_EXACT_TSV')
    if not verified_module.is_file() or not policy.is_file():raise ValueError('OFFICIAL_STAGE4_VERIFIER_REQUIRED')
    from importlib.util import spec_from_file_location,module_from_spec
    spec=spec_from_file_location('existing_stage4',verified_module)
    module=module_from_spec(spec);spec.loader.exec_module(module)
    decision=module.evaluate(decode_json(policy.read_text('utf-8'),'policy'),
                             decode_json(receipt.read_text('utf-8'),'stage4_receipt'),str(path))
    return {'status':decision.get('status','BLOCKED_RISK_BASED_STAGE4'),
            'blockers':decision.get('blockers',[])}
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path)
    p.add_argument('--member')
    p.add_argument('--output',type=Path)
    p.add_argument('--gate',action='store_true',help='Use official Stage4 risk acceptance; not legacy per-flag closure')
    p.add_argument('--stage4-receipt',type=Path)
    p.add_argument('--decisions',type=Path,help='Legacy argument ignored for new acceptance; Stage4 evidence is required')
    a=p.parse_args(argv)
    try:
        if not a.input.is_file():raise ValueError('INPUT_MISSING')
        tables=analyze_input(a.input,a.member)
        result={'schema':'gcpk-kombinationen-didactic-lean@1.1','mode':'ADVISORY_ONLY',
                'input_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),
                'tables':tables,'summary':{'flags':sum(len(x['flags']) for x in tables),
                'unreviewed_flags_as_blockers':0}}
        code=0
        if a.gate:
            if not a.stage4_receipt:
                result['acceptance']={'status':'BLOCKED_NO_OFFICIAL_STAGE4_RECEIPT'};code=2
            else:
                result['acceptance']=accept_existing_stage4(a.input,a.stage4_receipt)
                code=0 if result['acceptance']['status']=='PASS_RISK_BASED_STAGE4' else 2
        else:result['acceptance']={'status':'NOT_REQUESTED_NO_STAGE4_PASS'}
        if a.decisions:
            result['legacy_decisions_note']='Legacy decisions cannot replace Stage4 source-bound risk review'
        if a.output:a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
        print(json.dumps({k:result[k] for k in ('schema','input_sha256','summary','acceptance')},ensure_ascii=False))
        return code
    except (OSError,ValueError,KeyError,UnicodeError,json.JSONDecodeError,zipfile.BadZipFile) as exc:
        print(json.dumps({'status':'BLOCKED_BAD_INPUT','error':str(exc)}),file=sys.stderr)
        return 3
if __name__=='__main__':raise SystemExit(main())
