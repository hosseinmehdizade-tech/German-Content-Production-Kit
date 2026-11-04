#!/usr/bin/env python3
"""Read-only risk queue on source-derived related display; no semantic auto-retagging."""
import csv,json,re,pathlib,sys,collections
from repair_verwandt_categories_v1 import norm,de_text

def triage(tsv,out):
 with open(tsv,encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
 byid={r['id']:r for r in rows};holds=[];stats=collections.Counter();kept=0
 for r in rows:
  ds=json.loads(r['details']);cf=json.loads(r['custom_fields']);edges=cf.get('canonical_relations',[])
  for d in ds:
   if d.get('title') not in ('Verwandt','Verwandte Wörter'):continue
   for value in d.get('items',[]):
    kept+=1;de=de_text(value);k=norm(value)
    matching=[]
    for edge in edges:
     to=byid.get(edge.get('target_id'))
     if not to:continue
     target_unit=json.loads(to['custom_fields']).get('canonical_unit',{})
     if k in {norm(to['front']),norm(target_unit.get('headword',''))}:
      matching.append({'target_id':to['id'],'target_front':to['front'],'type':edge.get('relation_type',edge.get('type'))})
    reasons=[]
    if not matching:reasons.append('NO_EXACT_RESOLVED_LEXICAL_TARGET')
    if re.search(r'[.!?]$',de.strip()) and len(de.split())>=5:reasons.append('SENTENCE_OR_REDEMITTEL_NEEDS_ROLE_REVIEW')
    if matching and len({e['type'] for e in matching})>1:reasons.append('MULTIPLE_TYPED_RELATIONS_FOR_SAME_TARGET')
    if reasons:
     entry={'card_id':r['id'],'front':r['front'],'section':d['title'],'value':value,'flags':reasons,'matching_targets':matching,'decision':'HOLD_NO_AUTOMATIC_SEMANTIC_MOVE'}
     holds.append(entry);stats.update(reasons)
 report={'schema':'gcpk-related-hold-queue@1','scope':'source-derived A1 V25 candidate','total_related_items_retained':kept,'hold_item_count':len(holds),'hold_unique_cards':len({x['card_id'] for x in holds}),'counts':dict(stats),'holds':holds,'policy':'Do not infer synonym, word-family, grammatic slot or collocation from punctuation or word overlap alone; require source/independent evidence. No original/LOCKED mutation.'}
 pathlib.Path(out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return report
if __name__=='__main__':print(triage(sys.argv[1],sys.argv[2])['counts'])