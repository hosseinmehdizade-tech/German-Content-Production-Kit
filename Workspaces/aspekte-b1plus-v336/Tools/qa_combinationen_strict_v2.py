#!/usr/bin/env python3
"""Aspekte B1+ strict gate: reject full sentences and exact example copies in Kombinationen.
Run: python Tools/qa_combinationen_strict_v2.py <owner.zip> [qa-report.json]
Exit 0 PASS, 1 FAIL, 2 invalid input. Structural validation is not complete linguistic QA.
"""
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
PREVIEW='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
def normalize(s):
    s=unicodedata.normalize('NFKC',str(s)).casefold().strip()
    s=re.sub(r'[^\w\s]', ' ', s, flags=re.UNICODE)
    return ' '.join(s.split())
def sentence_like(s):
    s=s.strip()
    return s.endswith(('.', '!', '?')) or len(s.split())>10
def audit(cards):
    exact=[]; sentences=[]; substrings=[]; fields=[]; count=0; network_cards=0
    for c in cards:
        back=c.get('back',{})
        nets=back.get('semantic_network_sense_anchored_pending_qa',[]) or []
        if nets:network_cards+=1
        examples=(back.get('existing_examples_de_fa_pending_qa',[]) or [])+(back.get('additional_examples_de_fa_pending_qa',[]) or [])
        norm_examples=[normalize(x.get('de','')) for x in examples if isinstance(x,dict)]
        for net in nets:
            sid=net.get('sense_id','')
            for k in ('Kombinationen_DE_FA','Feste_Wendungen_DE_FA','Satzmuster_DE_FA'):
                vals=net.get(k,[]) or []
                if not isinstance(vals,list):
                    fields.append({'source_ordinal':c.get('source_ordinal'),'sense_id':sid,'invalid_field':k})
                    continue
                for pair in vals:
                    if not isinstance(pair,dict) or not str(pair.get('de','')).strip() or not str(pair.get('fa','')).strip():
                        fields.append({'source_ordinal':c.get('source_ordinal'),'sense_id':sid,'invalid_pair_in':k})
            for pair in net.get('Kombinationen_DE_FA',[]) or []:
                if not isinstance(pair,dict): continue
                raw=pair.get('de',''); norm=normalize(raw); count+=1
                ref={'source_ordinal':c.get('source_ordinal'),'card_id':c.get('preview_card_id'),'sense_id':sid,'de':raw}
                if norm and norm in norm_examples: exact.append(ref)
                if len(norm.split())>=4 and any(norm in e and norm != e for e in norm_examples): substrings.append(ref)
                if sentence_like(raw): sentences.append(ref)
    passed=not exact and not sentences and not fields
    return {'schema':'aspekte-b1plus-kombinationen-strict@2','cards_scanned':len(cards),'network_cards':network_cards,
            'combinations_scanned':count,'critical_exact_example_copies':exact,
            'critical_sentence_like_combinations':sentences,'critical_invalid_fields':fields,
            'nonblocking_phrase_substring_candidates':substrings,'structural_gate_passed':passed,
            'limits':'This tests explicit sense-level fields; paraphrase/collocation naturalness must be independently reviewed.'}
def main(argv):
    if len(argv)<2:
        print('Usage: qa_combinationen_strict_v2.py owner.zip [report.json]',file=sys.stderr)
        return 2
    try:
        with zipfile.ZipFile(argv[1]) as z:
            cards=[json.loads(line) for line in z.read(PREVIEW).splitlines()]
        result=audit(cards)
        if len(argv)>2: Path(argv[2]).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['structural_gate_passed'] else 1
    except (KeyError,ValueError,zipfile.BadZipFile) as ex:
        print(f'Invalid preview input: {ex}',file=sys.stderr)
        return 2
if __name__=='__main__':sys.exit(main(sys.argv))
