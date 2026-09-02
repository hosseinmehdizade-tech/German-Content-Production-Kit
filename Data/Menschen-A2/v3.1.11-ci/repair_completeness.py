#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

HEADERS=['id','card_type','domain','category','source','level','lesson','deck','front','back','front_label','back_label','front_lang','back_lang','typing_target','examples','related','opposites','details','custom_fields','tags','notes','order']

REPAIRS={
    'MEN-A2-00005': {
        'rection':['etwas (Akk.) an jemanden (Akk.) übergeben'],
        'locator':'https://www.duden.de/rechtschreibung/uebergeben_uebergeben',
        'note':'Duden meaning/example evidence explicitly attests the transfer sense with an + accusative recipient, including the same source sentence used in Menschen A2.'
    },
    'MEN-A2-00027': {
        'rection':['sich (Akk.) auf jemanden/etwas (Akk.) einrichten'],
        'locator':'https://www.duden.de/rechtschreibung/einrichten',
        'note':'Duden meaning 5 explicitly attests sich auf jemanden, etwas einrichten and the example darauf bin ich nicht eingerichtet.'
    },
    'MEN-A2-00150': {
        'rection':['sich (Akk.) über jemanden/etwas (Akk.) wundern'],
        'locator':'https://www.duden.de/rechtschreibung/wundern',
        'note':'Duden meaning 2 explicitly attests sich über jemanden, etwas wundern and the same source example ich wundere mich über gar nichts mehr.'
    },
}

def compact(x): return json.dumps(x,ensure_ascii=False,separators=(',',':'))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--canonical',required=True,type=Path)
    ap.add_argument('--tsv',required=True,type=Path)
    ns=ap.parse_args()
    ds=json.loads(ns.canonical.read_text(encoding='utf-8'))
    byid={u['id']:u for u in ds['learning_units']}
    for uid,spec in REPAIRS.items():
        u=byid[uid]
        u.setdefault('details',{})['rection']=spec['rection']
        srcs=u.setdefault('provenance',{}).setdefault('sources',[])
        srcs=[s for s in srcs if not (s.get('source_id')=='duden_online' and 'rection' in (s.get('what_was_verified') or []))]
        srcs.append({
            'source_id':'duden_online','source_kind':'lexicon','what_was_verified':['rection'],
            'verification_status':'verified','locator':spec['locator'],'accessed_at':'2026-09-02','evidence_note':spec['note']
        })
        u['provenance']['sources']=srcs
    ns.canonical.write_text(json.dumps(ds,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    lines=ns.tsv.read_text(encoding='utf-8').splitlines()
    if lines[0].lstrip('\ufeff').split('\t')!=HEADERS: raise SystemExit('TSV header mismatch')
    out=[lines[0]]
    for lineno,line in enumerate(lines[1:],2):
        parts=line.split('\t')
        if len(parts)!=23: raise SystemExit(f'column count {lineno}: {len(parts)}')
        row=dict(zip(HEADERS,parts)); uid=row['id']
        if uid in REPAIRS:
            u=byid[uid]; spec=REPAIRS[uid]
            details=json.loads(row['details'])
            details=[x for x in details if not (isinstance(x,dict) and x.get('title')=='Rektion')]
            details.append({'title':'Rektion','items':spec['rection']})
            row['details']=compact(details)
            cf=json.loads(row['custom_fields'])
            cf['rection']='; '.join(spec['rection'])
            cf['canonical_unit']=u
            row['custom_fields']=compact(cf)
        out.append('\t'.join(row[h] for h in HEADERS))
    ns.tsv.write_text('\n'.join(out)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','repaired_ids':sorted(REPAIRS),'canonical':str(ns.canonical),'tsv':str(ns.tsv)},ensure_ascii=False))

if __name__=='__main__': main()
