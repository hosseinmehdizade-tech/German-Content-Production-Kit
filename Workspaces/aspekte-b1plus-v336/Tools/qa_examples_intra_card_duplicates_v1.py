#!/usr/bin/env python3
"""Corpus-wide DE example duplicate gate. Iteration: --max-inherited 7; release: --release (requires zero).
Usage: qa_examples_intra_card_duplicates_v1.py owner.zip [--max-inherited N | --release]
"""
import collections,json,re,sys,zipfile,argparse
PRE='G2-LEXICAL-BATCH13-1571-FRONT-BACK-PREVIEWS-NONIMPORT.jsonl'
def normalize(s):return re.sub(r'\W+','',str(s).casefold())
def audit(cards):
 issues=[]
 for card in cards:
  b=card['back'];ex=(b.get('existing_examples_de_fa_pending_qa') or [])+(b.get('additional_examples_de_fa_pending_qa') or [])
  group=collections.defaultdict(list)
  for e in ex:group[normalize(e['de'])].append(e['de'])
  for key,entries in group.items():
   if key and len(entries)>1:issues.append({'card_id':card['preview_card_id'],'source_ordinal':card.get('source_ordinal'),'text_de':entries[0],'count':len(entries)})
 return {'schema':'aspekte-b1plus-examples-intracard-duplicates@1','cards_scanned':len(cards),'duplicate_groups':len(issues),'issues':issues}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('owner');g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--max-inherited',type=int);g.add_argument('--release',action='store_true');a=ap.parse_args()
 with zipfile.ZipFile(a.owner) as z:cards=[json.loads(x) for x in z.read(PRE).splitlines()]
 res=audit(cards);limit=0 if a.release else a.max_inherited
 res['threshold']=limit;res['passed']=len(res['issues'])<=limit
 print(json.dumps(res,ensure_ascii=False,indent=2))
 return 0 if res['passed'] else 1
if __name__=='__main__':sys.exit(main())
