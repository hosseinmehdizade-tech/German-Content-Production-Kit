#!/usr/bin/env python3
"""Read-only parent -> new versioned source-bound TSV successor for reviewed duplicate display.

Never overwrites source or LOCKED payload. Does not mutate typed graph or SRS.
"""
from __future__ import annotations
import csv, io, json, re, hashlib, zipfile, pathlib, collections, copy, sys, argparse

PARENT_TSV='Content/Menschen-A1-V24-FULL-2997-IMPORT.tsv'
RELATED={'Verwandt','Verwandte Wörter'}
BASE_COMBO={'Kombinationen','Kollokationen'}
# Independently justified: the full sentence is either a separate stable expression card
# (ma1m-lu-1305), or an exact same-card example. No other semantic guesses.
REMOVE_FROM_COMBOS={
 'ma1m-lu-1301':{'Bitte senden Sie uns eine Beschreibung.':'SEPARATE_EXPRESSION_CARD:ma1m-lu-1305'},
 'ma1m-lu-1656':{'Die Tür ist hinten.':'EXACT_SAME_CARD_EXAMPLE'},
 'ma1m-lu-1664':{'Ich muss dich dringend sprechen.':'EXACT_SAME_CARD_EXAMPLE'},
}

def de_text(v):
 if isinstance(v,dict): return str(v.get('de',''))
 return str(v).split(' — ',1)[0]
def norm(v):
 s=de_text(v).casefold().strip()
 s=re.sub(r'\s+',' ',s)
 return re.sub(r'[.?!]+$','',s).strip()

def extract_examples(r):
 examples=json.loads(r['examples'])
 return {norm(e.get('text_de',e.get('text',''))) for e in examples if isinstance(e,dict) and e.get('text_de',e.get('text',''))}

def combo_values(ds,cf):
 got=set()
 for d in ds:
  if d.get('title') in BASE_COMBO:
   got.update(norm(x) for x in d.get('items',[]))
 v=cf.get('kombinationen_v1',[])
 items=v.get('items',[]) if isinstance(v,dict) else v if isinstance(v,list) else []
 got.update(norm(x) for x in items)
 return got

def semantic_target_route(item,relations,target_rows):
    """Only exact text/target-id and pre-existing typed canonical relation permits reclassification."""
    key=norm(item)
    accepted=[]
    type_map={'WORD_FAMILY':'Wortfamilie','SYNONYM':'Synonyme','ANTONYM':'Antonyme'}
    for edge in relations:
        typ=edge.get('relation_type',edge.get('type'))
        if typ not in type_map: continue
        target=target_rows.get(edge.get('target_id'))
        if not target:continue
        info=json.loads(target['custom_fields']).get('canonical_unit',{})
        if key not in {norm(target['front']),norm(info.get('headword',''))}:continue
        accepted.append((type_map[typ],edge.get('relation_id'),edge.get('target_id')))
    kinds={a[0] for a in accepted}
    if len(kinds)!=1:return None
    return accepted[0]


def successor_row(row,target_rows=None):
 r=row.copy();ds=json.loads(r['details']);cf=json.loads(r['custom_fields']);target_rows=target_rows or {};before=(copy.deepcopy(ds),copy.deepcopy(cf))
 combos=combo_values(ds,cf);exs=extract_examples(r)
 removals=[];relocations=[]
 newds=[]
 for d in ds:
  if d.get('title') not in RELATED:
   newds.append(d);continue
  kept=[]
  for raw in d.get('items',[]):
   k=norm(raw)
   # Strict exact equivalence; no substrings, no morphology, no language heuristic.
   reason='EXACT_OTHER_SECTION_KOMBINATIONEN' if k in combos else 'EXACT_SAME_CARD_BEISPIEL' if k in exs else None
   if reason:
    removals.append({'title':d['title'],'value':raw,'normalized_de':k,'reason':reason})
   else:
    route=semantic_target_route(raw,cf.get('canonical_relations',[]),target_rows)
    if route:
     to_title,rel_id,target_id=route
     relocations.append({'from_title':d['title'],'to_title':to_title,'value':raw,'relation_id':rel_id,'target_id':target_id,'reason':'EXACT_TYPED_CANONICAL_TARGET_MATCH'})
    else:kept.append(raw)
  if kept:
   e=d.copy();e['items']=kept;newds.append(e)
 # Move verified member to existing or new correct learner-facing physical details section.
 for m in relocations:
  destination=next((d for d in newds if d.get('title')==m['to_title']),None)
  if destination is None:
   destination={'title':m['to_title'],'items':[]};newds.append(destination)
  if norm(m['value']) not in {norm(x) for x in destination['items']}:
   destination['items'].append(m['value'])
 # Canonical mirrored legacy details are synchronized using same exact original strings.
 canon=cf.get('canonical_unit',{})
 if isinstance(canon,dict) and isinstance(canon.get('details'),dict):
  core=canon['details']
  for title in RELATED:
   if isinstance(core.get(title),list):
    flagged=collections.Counter((m['title'],norm(m['value'])) for m in removals)
    flagged.update((m['from_title'],norm(m['value'])) for m in relocations)
    remain=[]
    for item in core[title]:
     key=(title,norm(item))
     if flagged[key]:flagged[key]-=1
     else:remain.append(item)
    if remain:core[title]=remain
    else:del core[title]
  for m in relocations:
   dest=core.setdefault(m['to_title'],[])
   if norm(m['value']) not in {norm(x) for x in dest}:dest.append(m['value'])
 # Evidence-backed exceptional removal from unrelated enrichment family
 combo_removed=[]
 exceptional=REMOVE_FROM_COMBOS.get(r['id'],{})
 if exceptional:
  for field in ('kombinationen_v1','kombinationen_v336'):
   payload=cf.get(field)
   if not isinstance(payload,dict) or not isinstance(payload.get('items'),list):continue
   before_items=payload['items'];kept=[];removed=[]
   for obj in before_items:
    text=de_text(obj)
    matched=next((why for key,why in exceptional.items() if norm(text)==norm(key)),None)
    if matched:removed.append({'field':field,'de':text,'reason':matched})
    else:kept.append(obj)
   if removed:
    payload['items']=kept
    combo_removed.extend(removed)
    if not kept:
     payload['disposition']='CLOSED_NO_FORCE' if field=='kombinationen_v1' else payload.get('disposition','CLOSED_NO_FORCE')
     payload['status']='CLOSED_NO_FORCE'
     payload['reason']='REMOVED_DUPLICATE_EXAMPLE_OR_INDEPENDENT_REDEMITTEL'
    # Retain historical origin/provenance and all other metadata; successor is NOT Stage4 accepted.
 if removals or relocations or combo_removed:
  r['details']=json.dumps(newds,ensure_ascii=False,separators=(',',':'))
  r['custom_fields']=json.dumps(cf,ensure_ascii=False,separators=(',',':'))
  return r,{'id':r['id'],'front':r['front'],'related_display_suppressed':removals,'reclassified_to_typed_section':relocations,'combo_removed':combo_removed,'graph_preserved':True}
 return r,None

def load_parent(zip_path):
 with zipfile.ZipFile(zip_path) as z:
  z.testzip()
  raw=z.read(PARENT_TSV)
 rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')),delimiter='\t'))
 if len(rows)!=2997:raise ValueError('unexpected parent A1 row count')
 return rows,list(rows[0]),raw

def run(zip_path,out_tsv,ledger_path):
 rows,header,raw=load_parent(zip_path)
 changed=[];successor=[];cnt=collections.Counter()
 target_rows={r['id']:r for r in rows}
 for row in rows:
  new,edit=successor_row(row,target_rows);successor.append(new)
  if edit:
   changed.append(edit)
   cnt['card_changes']+=1
   cnt['related_suppressed']+=len(edit['related_display_suppressed'])
   cnt['typed_relations_reclassified']+=len(edit['reclassified_to_typed_section'])
   cnt['combination_suppressed_fields']+=len(edit['combo_removed'])
 # explicit safeguard: source/sense/learned core unchanged, all typed edges identical, no field removals
 for old,new in zip(rows,successor):
  for key in header:
   if key not in ('details','custom_fields') and old[key]!=new[key]:raise AssertionError(('unexpected core edit',old['id'],key))
  a=json.loads(old['custom_fields']);b=json.loads(new['custom_fields'])
  for field in ('canonical_relations','vnext_relations','presentation_examples','vnext_target_id','source_audio_refs','vnext_source_refs'):
   if a.get(field)!=b.get(field):raise AssertionError(('graph or evidence mutation',old['id'],field))
 assert len(set(x['id'] for x in successor))==len(successor)==2997
 out_tsv=pathlib.Path(out_tsv);out_tsv.parent.mkdir(parents=True,exist_ok=True)
 with out_tsv.open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=header,delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(successor)
 ledger={'schema':'gcpk-related-categories-v1.0.0','status':'SOURCE_DERIVED_EDITABLE_SUCCESSOR_PRE_STAGE4_NOT_IMPORT_READY','parent_zip_sha256':hashlib.sha256(pathlib.Path(zip_path).read_bytes()).hexdigest(),'parent_tsv_sha256':hashlib.sha256(raw).hexdigest(),'successor_tsv_sha256':hashlib.sha256(out_tsv.read_bytes()).hexdigest(),'parent_cards':len(rows),'successor_cards':len(successor),'counts':dict(cnt),'changes':changed,'identity_and_graph': 'PRESERVED_EXACT','removed_values':'DISPLAY_ONLY_IN_RELATED_MIRRORS_OR_REDUNDANT_COMBO_PROJECTIONS; ORIGINAL_PARENT_REMITS_AUTHORITATIVE','Stage4':'PENDING_INDEPENDENT_REVIEW'}
 pathlib.Path(ledger_path).write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return ledger
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('parent');a.add_argument('successor');a.add_argument('ledger')
 x=a.parse_args();print(json.dumps(run(x.parent,x.successor,x.ledger)['counts'],indent=2))