#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from collections import Counter

META_RE=re.compile(r'(Verzeichnis:Deutsch|Alle Angaben hierzu|Ergänzungen/Veränderungen|\bBearbeiten\b|^siehe(?:\s|$))',re.I)
PLACEHOLDER_RE=re.compile(r'\b(?:jdn|jdm|etw)\.',re.I)
FIXED_PREP_RE=re.compile(r'\b(an|auf|aus|bei|durch|für|gegen|in|mit|nach|über|um|unter|von|vor|zu|zwischen|ohne|seit)\s+(?:jdn\./etw\.|jdm\./etw\.|jdn\.|jdm\.|etw\.)',re.I)
HEADERS=['id','card_type','domain','category','source','level','lesson','deck','front','back','front_label','back_label','front_lang','back_lang','typing_target','examples','related','opposites','details','custom_fields','tags','notes','order']

def it(sev,code,uid,path,msg): return {'severity':sev,'code':code,'id':uid,'path':path,'message':msg}
def verified(unit):
    claims=set();srcs=[]
    for s in (unit.get('provenance') or {}).get('sources',[]) or []:
        if isinstance(s,dict) and s.get('verification_status')=='verified':
            srcs.append(s);claims.update(str(x).casefold() for x in (s.get('what_was_verified') or []))
    return claims,srcs

def validate_dataset(ds):
    units=ds.get('learning_units') if isinstance(ds,dict) else None
    if not isinstance(units,list): raise ValueError('dataset.learning_units must be an array')
    issues=[];coverage=Counter();coll_total=0;relation_units=0;rection_units=0
    for i,u in enumerate(units):
        if not isinstance(u,dict): issues.append(it('error','UNIT_INVALID',f'index-{i}',f'learning_units[{i}]','Unit is not an object.'));continue
        uid=str(u.get('id') or f'index-{i}');typ=u.get('type');coverage[typ or '<missing>']+=1;claims,srcs=verified(u)
        if typ=='verb':
            core=u.get('core') if isinstance(u.get('core'),dict) else {}
            for f in ('present_3sg','preterite_3sg','perfect','auxiliary','reflexive','separability'):
                if f not in core or core.get(f) in (None,''): issues.append(it('error','VERB_CORE_MISSING',uid,f'core.{f}','Required verb core field missing.'))
        examples=u.get('examples')
        if not isinstance(examples,list) or not examples: issues.append(it('error','EXAMPLES_MISSING',uid,'examples','Canonical examples must be a non-empty structured array.'))
        else:
            for j,e in enumerate(examples):
                if not isinstance(e,dict) or not str(e.get('text','')).strip(): issues.append(it('error','EXAMPLE_INVALID',uid,f'examples[{j}]','Example must be an object with text.'));continue
                langs={str(t.get('lang')) for t in (e.get('translations') or []) if isinstance(t,dict) and str(t.get('text','')).strip()}
                if not {'fa-IR','en-US'}.issubset(langs): issues.append(it('error','EXAMPLE_TRANSLATION_MISSING',uid,f'examples[{j}].translations','German example must retain FA and EN translations.'))
        details=u.get('details') if isinstance(u.get('details'),dict) else {}
        for field,accepted in [('synonyms',{'synonymy','synonyms'}),('antonyms',{'antonymy','antonyms'})]:
            vals=details.get(field)
            if vals:
                relation_units+=1
                if not isinstance(vals,list) or not all(isinstance(x,str) and x.strip() for x in vals): issues.append(it('error','RELATION_INVALID',uid,f'details.{field}','Relation must be a non-empty string array.'))
                if not (claims & accepted): issues.append(it('error','RELATION_EVIDENCE_MISSING',uid,f'details.{field}','Relation lacks explicit verified relation evidence.'))
                for s in srcs:
                    sc={str(x).casefold() for x in (s.get('what_was_verified') or [])}
                    if sc & accepted and s.get('source_id')=='de_wiktionary_pos_scoped_wikitext': issues.append(it('error','RELATION_BROAD_SENSE_SOURCE',uid,f'details.{field}','Broad POS-block relation extraction is not sufficient sense evidence.'))
        if typ=='verb' and PLACEHOLDER_RE.search(str(u.get('headword',''))):
            r=details.get('rection')
            if not isinstance(r,list) or not any(isinstance(x,str) and x.strip() for x in r): issues.append(it('error','RECTION_REQUIRED',uid,'details.rection','Headword encodes valency notation; explicit Rektion is required.'))
            else:
                rection_units+=1
                if not (claims & {'rection','valency','government_pattern'}): issues.append(it('error','RECTION_EVIDENCE_MISSING',uid,'details.rection','Rektion lacks explicit verified evidence.'))
        conns=u.get('connections') or []
        if not isinstance(conns,list): issues.append(it('error','CONNECTIONS_INVALID',uid,'connections','connections must be an array.'));conns=[]
        coll=[c for c in conns if isinstance(c,dict) and c.get('kind')=='collocation'];coll_total+=len(coll)
        if coll:
            if not (claims & {'collocation','collocations','collocational_usage'}): issues.append(it('error','COLLOCATION_EVIDENCE_MISSING',uid,'connections','Collocations lack explicit verified evidence.'))
            head=str(u.get('headword',''));pm=FIXED_PREP_RE.search(head);reflexive=bool(re.search(r'\bsich\b',head,re.I))
            for j,c in enumerate(coll):
                text=str(c.get('text') or '').strip();path=f'connections.collocation[{j}]'
                if not text: issues.append(it('error','COLLOCATION_EMPTY',uid,path,'Empty collocation.'));continue
                if len(text)>100 or any(ch in text for ch in ':,;/') or META_RE.search(text): issues.append(it('error','COLLOCATION_NOT_ATOMIC',uid,path,'Bundled/editorial collocation text is forbidden.'))
                if reflexive and 'sich' not in text.casefold(): issues.append(it('error','COLLOCATION_REFLEXIVE_MISMATCH',uid,path,'Reflexive card requires reflexive sense alignment.'))
                if pm and pm.group(1).casefold() not in text.casefold(): issues.append(it('error','COLLOCATION_FIXED_PREP_MISMATCH',uid,path,'Fixed/prepositional collocation does not preserve the encoded preposition.'))
            for s in srcs:
                if str(s.get('source_id','')).startswith('current_card_examples_') and ({str(x).casefold() for x in (s.get('what_was_verified') or [])}&{'collocation','collocations','collocational_usage'}): issues.append(it('error','EXAMPLE_DERIVED_AS_COLLOCATION',uid,'provenance','Example-derived fallback may not be verified as collocation.'))
    verbs=[u for u in units if isinstance(u,dict) and u.get('type')=='verb'];counts=[sum(1 for c in (u.get('connections') or []) if isinstance(c,dict) and c.get('kind')=='collocation' and str(c.get('text','')).strip()) for u in verbs]
    errors=sum(x['severity']=='error' for x in issues)
    return {'validator':'gfp-lexical-quality','validator_version':'1.0.0','status':'FAIL' if errors else 'PASS','errors':errors,'warnings':0,'coverage_by_type':dict(coverage),'metrics':{'units':len(units),'verbs':len(verbs),'collocations':coll_total,'verbs_with_any_collocation':sum(n>0 for n in counts),'verbs_with_3plus_collocations':sum(n>=3 for n in counts),'relation_units':relation_units,'rection_units':rection_units},'issues':issues}

def validate_tsv(path,ds):
    issues=[];lines=Path(path).read_text(encoding='utf-8').splitlines();hdr=lines[0].split('\t') if lines else []
    if hdr!=HEADERS: issues.append({'severity':'error','code':'TSV_HEADER_MISMATCH'})
    byid={u.get('id'):u for u in ds.get('learning_units',[]) if isinstance(u,dict)};seen=set()
    for n,line in enumerate(lines[1:],2):
        parts=line.split('\t')
        if len(parts)!=23: issues.append({'severity':'error','code':'TSV_COLUMN_COUNT','line':n,'found':len(parts)});continue
        r=dict(zip(HEADERS,parts));uid=r['id']
        if uid in seen: issues.append({'severity':'error','code':'TSV_DUPLICATE_ID','id':uid})
        seen.add(uid);u=byid.get(uid)
        if not u: issues.append({'severity':'error','code':'TSV_ID_NOT_CANONICAL','id':uid});continue
        parsed={}
        for k in ('examples','related','opposites','details','custom_fields'):
            try: parsed[k]=json.loads(r[k])
            except Exception: issues.append({'severity':'error','code':'TSV_JSON_INVALID','id':uid,'field':k})
        if parsed.get('examples')!=u.get('examples'): issues.append({'severity':'error','code':'TSV_EXAMPLE_PARITY','id':uid})
        cf=parsed.get('custom_fields')
        if not isinstance(cf,dict) or cf.get('canonical_unit')!=u: issues.append({'severity':'error','code':'TSV_CANONICAL_PARITY','id':uid})
        if not isinstance(parsed.get('related'),list) or not isinstance(parsed.get('opposites'),list): issues.append({'severity':'error','code':'TSV_RELATION_SHAPE','id':uid})
        if r['front']!=str(u.get('headword','')) or r['back']!=str(u.get('persian_meaning','')): issues.append({'severity':'error','code':'TSV_FACE_PARITY','id':uid})
    errors=sum(x.get('severity')=='error' for x in issues)
    return {'validator':'gfp-v354-universal-v2-transport','status':'FAIL' if errors else 'PASS','errors':errors,'rows':max(0,len(lines)-1),'columns':len(hdr),'issues':issues}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('dataset');ap.add_argument('--tsv');ap.add_argument('--output');ns=ap.parse_args();ds=json.loads(Path(ns.dataset).read_text(encoding='utf-8'));q=validate_dataset(ds);report={'quality':q}
    if ns.tsv: report['transport']=validate_tsv(ns.tsv,ds)
    report['status']='PASS' if q['status']=='PASS' and report.get('transport',{'status':'PASS'})['status']=='PASS' else 'FAIL';text=json.dumps(report,ensure_ascii=False,indent=2)+'\n';print(text,end='')
    if ns.output: Path(ns.output).write_text(text,encoding='utf-8')
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
