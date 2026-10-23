#!/usr/bin/env python3
"""Read-only corpus-wide source morphology/source attribution gate for R83 Menschen A2.

This verifies the *registered source transcriptions* against the active card's
Perfekt where the source actually provides one. It does not certify linguistic
correctness, verb-sense correspondence, or independent Stage4 signoff.
Usage: python VERIFY_R83_SOURCE_PERFEKT.py R83.zip [EXPECTED_OUTER_SHA256]
"""
from __future__ import annotations
import csv, hashlib, io, json, re, sys, zipfile
from pathlib import Path

KNOWN_EXCEPTION = {
    "id": "ma2-lu-0297", "front": "ausrasten",
    "source": "hat ausgerastet", "working": "ist ausgerastet",
    "sense": "die Beherrschung verlieren", "source_locator": (11, 9),
}
EXPECTED = {"MATCH":224,"UNCONJUGATED_CONSTRUCTION":64,"SOURCE_NO_AUXILIARY":3,
            "DOCUMENTED_SENSE_CONFLICT":1}


def sha(b): return hashlib.sha256(b).hexdigest()


def inspect(path, expected_outer=None):
    blob=Path(path).read_bytes()
    outer=sha(blob)
    if expected_outer is not None and outer!=expected_outer:
        raise ValueError("R83 outer SHA mismatch")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or any(n.startswith('/') or '..' in n.split('/') for n in names):
            raise ValueError('unsafe/duplicate member')
        if z.testzip() is not None: raise ValueError('ZIP CRC failure')
        tsv_name=next(n for n in names if n.endswith('/CURRENT-STAGE4-CANDIDATE-NOT-FINAL.tsv'))
        ix_name=next(n for n in names if n.endswith('/SOURCE-EVIDENCE-AND-REVIEW-INDEX.json'))
        raw=z.read(tsv_name)
        tsv_sha=sha(raw)
        index=json.loads(z.read(ix_name))
        if index['authority']['active_candidate_sha256']!=tsv_sha:
            raise ValueError('source index candidate SHA no longer matches working TSV')
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), delimiter='\t'))
        ci={x['card_id']:x for x in index['cards']}
        if len(rows)!=292 or len(ci)!=292 or len({r['id'] for r in rows})!=292:
            raise ValueError('card inventory changed unexpectedly')
        counters={k:0 for k in EXPECTED}; conflicts=[]; omission=[]
        for r in rows:
            card_id=r['id']; front=r['front']
            if card_id not in ci: raise ValueError('unmapped card: '+card_id)
            f=json.loads(r['custom_fields'])
            perfect=f['canonical_unit']['core'].get('perfect','')
            source_entries=ci[card_id]['source_entries']
            # No source text is synthesized: use *registered original source row*.
            source=' '.join(s['raw_text'] for s in source_entries)
            candidates=[f'{a} {b}' for a,b in re.findall(
                r'\b(hat|ist)\s+(?:sich\s+)?(\w+)\b',source,flags=re.I)]
            normalized=re.sub(r'^(hat|ist) sich ',r'\1 ',perfect)
            if not perfect:
                counters['UNCONJUGATED_CONSTRUCTION']+=1; continue
            if not candidates:
                counters['SOURCE_NO_AUXILIARY']+=1
                omission.append(card_id); continue
            if normalized in candidates:
                counters['MATCH']+=1;continue
            if card_id==KNOWN_EXCEPTION['id'] and front==KNOWN_EXCEPTION['front'] and \
                 KNOWN_EXCEPTION['source'] in candidates and normalized==KNOWN_EXCEPTION['working'] and \
                 any(s['screenshot_index']==11 and s['row_index']==9 for s in source_entries) and \
                 'Beherrschung' in f['canonical_unit']['definition_de'] and 'verlieren' in f['canonical_unit']['definition_de'] and \
                 any(KNOWN_EXCEPTION['working'] in i for x in json.loads(r['details'])
                     if x['title']=='Formen' for i in x['items']) and \
                 any('historischen Quelle' in i and 'Hilfsverbangabe' in i for x in json.loads(r['details'])
                     if x['title']=='Grammatik' for i in x['items']):
                counters['DOCUMENTED_SENSE_CONFLICT']+=1
                conflicts.append({"card_id":card_id,"source_aux":KNOWN_EXCEPTION['source'],
                                  "working_aux":normalized,"disposition":"KEEP_FOR_CURRENT_SENSE_WITH_SOURCE_CONFLICT_NOTED"})
                continue
            raise ValueError(f'UNREVIEWED SOURCE MORPHOLOGY CONFLICT: {card_id} {front}: source={candidates}, content={perfect}')
        if counters!=EXPECTED:
            raise ValueError(f'corpus source morphology coverage drift: {counters} != {EXPECTED}')
        return {"status":"SCOPED_TECHNICAL_SOURCE_PERFEKT_GATE_PASS_NOT_STAGE4",
                "outer_sha256":outer,"active_tsv_sha256":tsv_sha,
                "counts":counters,"source_aux_missing_ids":omission,"conflicts":conflicts,
                "qualified_independent_approvals":0,"stage4_final":False}

if __name__=='__main__':
    try:
        if len(sys.argv) not in (2,3):raise ValueError('Usage: script R83.zip [outer_SHA256]')
        print(json.dumps(inspect(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else None),ensure_ascii=False,indent=2))
    except Exception as exc:
        print('FAIL:',exc,file=sys.stderr);sys.exit(1)
