#!/usr/bin/env python3
"""Fail-closed candidate gate for unpunctuated German full clauses in Kombinationen.

Targeted regression upgrade of v3 (which omitted reicht/entscheidet/koordiniert/läuft).
Reports exact candidates for editorial classification; only examples of simple NPs
followed by a known finite verb are auto-blocked. Other constructions are NOT
certified by a pass. Run as a corpus gate before a new owner is claimed clean.
"""
import collections,json,re,sys,zipfile
from pathlib import Path
from argparse import ArgumentParser

MAIN='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
DETERMINERS={'der','die','das','ein','eine','einen','einem','einer','diese','dieser','dieses','jener','jene'}
FINITE={'reicht','entscheidet','koordiniert','läuft','prüft','schreibt','bringt','bestimmt','öffnet','organisiert','führt','hat','ist','sind','steht','arbeitet','verwendet','liefert','besucht','zeichnet','braucht','stellt','kommt','zeigt','hält','macht','kann','wird','werden','nimmt','bietet','spricht'}

def audit(cards):
    result=[];total=0
    for c in cards:
        for n in c['back'].get('semantic_network_sense_anchored_pending_qa',[]) or []:
            for x in n.get('Kombinationen_DE_FA',[]) or []:
                total+=1
                de=x.get('de','')
                w=re.findall(r'\w+',de,re.UNICODE)
                if (len(w)>=4 and w[0].casefold() in DETERMINERS and w[1][0].isupper() and w[2].casefold() in FINITE):
                    result.append({'lesson':c.get('lesson'),'ordinal':c.get('source_ordinal'),'headword':c['front']['base_headword_de'],'de':de,'reason':'SIMPLE_NP_FOLLOWED_BY_FINITE_VERB','resolution':'EDITORIAL_REPLACE_WITH_GENUINE_COLLOCATION_OR_RECLASSIFY_AS_EXAMPLE'})
    return {'schema':'aspekte-b1plus-finite-clause-combinationen-gate@4','cards_scanned':len(cards),'combinations_scanned':total,'possible_full_sentence_collocations':len(result),'issues':result,'strict_corpus_pass':len(result)==0,'scope_limit':'Known-verb pattern: PASS is not a comprehensive semantic or grammatical certification.'}

if __name__=='__main__':
    a=ArgumentParser();a.add_argument('owner');a.add_argument('--report');args=a.parse_args()
    with zipfile.ZipFile(args.owner) as z:cards=[json.loads(x) for x in z.read(MAIN).splitlines()]
    r=audit(cards)
    if args.report:Path(args.report).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False,indent=2))
    sys.exit(0 if r['strict_corpus_pass'] else 1)
