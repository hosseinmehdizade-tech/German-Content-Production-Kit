#!/usr/bin/env python3
"""Aspekte B1+ reusable strict non-copy QA for sense-level Kombinationen."""
import json, sys, zipfile, re, unicodedata
from pathlib import Path
PREVIEW='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
def normalize(s):
    s=unicodedata.normalize('NFKC',str(s)).casefold().strip()
    s=re.sub(r'[^\w\s]', ' ', s,flags=re.UNICODE)
    return ' '.join(s.split())
def audit(cards):
    exact=[]; near=[]; sentence=[]; n_comb=0; cards_with_network=0
    for c in cards:
        back=c.get('back',{})
        nets=back.get('semantic_network_sense_anchored_pending_qa',[]) or []
        if nets: cards_with_network+=1
        examples=(back.get('existing_examples_de_fa_pending_qa',[]) or [])+(back.get('additional_examples_de_fa_pending_qa',[]) or [])
        ex=[normalize(x.get('de','')) for x in examples]
        for net in nets:
            for comb in net.get('Kombinationen_DE_FA',[]) or []:
                phrase=comb.get('de',''); norm=normalize(phrase); n_comb+=1
                ref={'card_id':c['preview_card_id'],'source_ordinal':c.get('source_ordinal'),'sense_id':net.get('sense_id'),'kombination_de':phrase}
                if norm and norm in ex: exact.append(ref)
                if len(norm.split())>=4 and any(norm in e and norm!=e for e in ex): near.append(ref)
                if phrase.strip().endswith(('.','!','?')) or len(phrase.split())>10: sentence.append(ref)
    return {'cards_scanned':len(cards),'cards_with_semantic_network':cards_with_network,
            'sense_level_kombinationen_scanned':n_comb,'exact_example_copy_count':len(exact),
            'exact_example_copies':exact,'full_phrase_as_example_substring_count':len(near),
            'phrase_substring_candidates':near,'sentence_like_combination_count':len(sentence),
            'sentence_like_candidates_for_manual_review':sentence,
            'exact_noncopy_gate_pass':len(exact)==0,'manual_sentence_review_gate':'OPEN' if sentence else 'PASS',
            'limitations':'Only explicit sense-level combinations; paraphrases and inflected variants need linguistic review.'}
if __name__=='__main__':
    with zipfile.ZipFile(sys.argv[1]) as z:
        cards=[json.loads(x) for x in z.read(PREVIEW).splitlines()]
    out=audit(cards)
    if len(sys.argv)>2:Path(sys.argv[2]).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))
    raise SystemExit(0 if out['exact_noncopy_gate_pass'] else 1)
