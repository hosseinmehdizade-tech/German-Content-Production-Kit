#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import defaultdict

def project(data):
 lex={x["lexeme_id"]:x for x in data.get("lexemes",[]) if x.get("lexeme_id")}; sources={x["source_id"]:x for x in data.get("sources",[]) if x.get("source_id")}; examples=defaultdict(list); rels=defaultdict(list)
 for ex in data.get("examples",[]):
  for tid in ex.get("target_object_ids") or []: examples[str(tid)].append(ex)
 for r in data.get("relations",[]): rels[str(r.get("source_id") or "")].append(r)
 def source_refs(obj):
  out=[]
  for sr in (obj.get("provenance") or {}).get("source_refs") or []:
   s=sources.get(sr.get("source_id"),{}); out.append({"source_id":sr.get("source_id"),"source_title":s.get("title") or sr.get("source_id"),"locator":sr.get("locator") or "","version":sr.get("version") or s.get("version") or ""})
  return out
 def relation_groups(tid):
  groups=defaultdict(list)
  for r in rels.get(tid,[]):
   typ=str(r.get("relation_type") or "RELATED").upper(); val=r.get("value"); label=(val.get("text") if isinstance(val,dict) else val) or r.get("target_id") or typ
   groups[typ].append({"relation_id":r.get("relation_id"),"label":str(label),"meaning":(val.get("meaning") if isinstance(val,dict) else "") or "","target_id":r.get("target_id")})
  labels={"NVV":"Nomen-Verb-Verbindungen","COLLOCATION":"Kollokationen","RELATED":"Verwandt","SYNONYM":"Synonyme","ANTONYM":"Antonyme","REKTION":"Rektion","COMPONENT":"Bestandteile","WORD_FAMILY":"Wortfamilie"}
  return [{"type":k,"label":labels.get(k,k),"items":v} for k,v in groups.items()]
 def ex_projection(tid):
  rows=sorted(examples.get(tid,[]),key=lambda x:x.get("example_id",""))
  return [{"id":x.get("example_id"),"de":x.get("text_de"),"fa":(x.get("translations") or {}).get("fa",""),"en":(x.get("translations") or {}).get("en",""),"annotations":x.get("annotations") or []} for x in rows]
 def membership(obj):
  ms=obj.get("course_memberships") or ([] if not obj.get("course_membership") else [obj.get("course_membership")])
  return [m for m in ms if isinstance(m,dict)]
 def primary_membership(obj):
  ms=membership(obj); return ms[0] if ms else {}
 def media(obj): return [m for m in (obj.get("media_refs") or []) if isinstance(m,dict)]
 def common_card(tid,obj,title,pos,target_type,entry_type,definition,translations,structure,etype=None,esub=None):
  nonlocal order
  order+=1; exs=ex_projection(tid); srefs=source_refs(obj); pm=primary_membership(obj); allm=membership(obj); aud=media(obj)
  cefr=pm.get("cefr") or obj.get("cefr") or ""; lesson=pm.get("lesson_id") or pm.get("lesson_title") or ""; deck=(f"{pm.get('course')} {cefr}".strip() if pm.get("course") else "v411 Canonical")
  src_order=pm.get("source_row_ordinal"); ordval=src_order if isinstance(src_order,int) else order
  cf={"entry_type":entry_type,"vnext_target_id":tid,"vnext_target_type":target_type,"vnext_definition_de":definition or "","vnext_translation_fa":translations.get("fa","") ,"vnext_translation_en":translations.get("en","") ,"vnext_structure":structure,"vnext_source_refs":srefs,"vnext_relations":relation_groups(tid),"presentation_examples":exs,"germanDefinition":definition or "","english":translations.get("en","") ,"typingCore":title,"course_memberships":allm,"source_audio_refs":aud}
  if etype: cf["vnext_expression_type"]=etype
  if esub is not None: cf["vnext_expression_subtype"]=esub
  return {"id":tid,"cardType":"de-vocabulary","schemaProfile":"german-v411-lexical","domain":"German","category":pos.title() if target_type=='sense' else "Expression","source":(srefs[0].get("source_title") if srefs else (pm.get("course") or "Canonical v411")),"level":cefr,"lesson":lesson,"deck":deck,"front":title,"back":translations.get("fa","") ,"frontLabel":pos.title() if target_type=='sense' else "Expression","backLabel":"فارسی","frontLang":"de-DE","backLang":"fa-IR","frontDir":"ltr","backDir":"rtl","typingTarget":"custom:typingCore","examples":[x["de"] for x in exs],"related":[],"opposites":[],"details":[],"customFields":cf,"notes":definition or "","order":ordval}
 cards=[]; order=0
 for s in data.get("senses",[]):
  lx=lex.get(s.get("lexeme_id"),{}); tid=s["sense_id"]; pos=lx.get("pos") or "phrase"; title=lx.get("lemma") or tid; tr=s.get("translations") or {}
  cards.append(common_card(tid,s,title,pos,"sense",pos,s.get("definition_de"),tr,s.get("structure")))
 for e in data.get("expressions",[]):
  tid=e["expression_id"]; tr=e.get("translations") or {}; etype=e.get("expression_type") or "multiword_expression"; entry={"nvv":"nvv","idiom":"idiom","collocation":"collocation"}.get(etype,"phrase")
  cards.append(common_card(tid,e,e.get("canonical_form") or tid,"expression","expression",entry,e.get("definition_de"),tr,e.get("structure"),etype,e.get("expression_subtype")))
 cards.sort(key=lambda c:(c.get("order",0),c["id"]))
 return cards

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("registry"); ap.add_argument("output"); a=ap.parse_args(); d=json.loads(Path(a.registry).read_text(encoding="utf-8")); cards=project(d); Path(a.output).write_text(json.dumps(cards,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"status":"PASS","cards":len(cards),"output":a.output}))
if __name__=="__main__": main()
