#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
HEADERS=['id','card_type','domain','category','source','level','lesson','deck','front','back','front_label','back_label','front_lang','back_lang','typing_target','examples','related','opposites','details','custom_fields','tags','notes','order']

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--tsv',required=True,type=Path); ap.add_argument('--canonical',required=True,type=Path); ap.add_argument('--output',required=True,type=Path); ns=ap.parse_args()
 ds=json.loads(ns.canonical.read_text(encoding='utf-8')); byid={u['id']:u for u in ds['learning_units']}; issues=[]
 lines=ns.tsv.read_text(encoding='utf-8-sig').splitlines(); hdr=lines[0].split('\t') if lines else []
 if hdr!=HEADERS: issues.append({'code':'HEADER','message':f'Expected exact 23-column header; got {hdr}'})
 seen=set()
 for n,line in enumerate(lines[1:],2):
  parts=line.split('\t')
  if len(parts)!=23: issues.append({'code':'COLUMN_COUNT','line':n,'found':len(parts)}); continue
  r=dict(zip(HEADERS,parts)); uid=r['id']; u=byid.get(uid)
  if uid in seen: issues.append({'code':'DUPLICATE_ID','id':uid})
  seen.add(uid)
  if not u: issues.append({'code':'UNKNOWN_ID','id':uid}); continue
  parsed={}
  for f in ('examples','related','opposites','details','custom_fields'):
   raw=r[f]
   if len(raw)>=2 and raw[0]=='"' and raw[-1]=='"': issues.append({'code':'CSV_QUOTING_FORBIDDEN','id':uid,'field':f})
   try: parsed[f]=json.loads(raw)
   except Exception as e: issues.append({'code':'JSON_INVALID','id':uid,'field':f,'error':str(e)}); parsed[f]=None
  details=u.get('details') if isinstance(u.get('details'),dict) else {}
  syn=details.get('synonyms') if isinstance(details.get('synonyms'),list) else []
  ant=details.get('antonyms') if isinstance(details.get('antonyms'),list) else []
  if parsed.get('related')!=syn: issues.append({'code':'RELATED_PARITY','id':uid})
  if parsed.get('opposites')!=ant: issues.append({'code':'OPPOSITES_PARITY','id':uid})
  cf=parsed.get('custom_fields')
  if not isinstance(cf,dict) or cf.get('canonical_unit')!=u: issues.append({'code':'CANONICAL_DEEP_COPY','id':uid})
  if r['front']!=u.get('headword','') or r['back']!=u.get('persian_meaning',''): issues.append({'code':'FACE_PARITY','id':uid})
  if not isinstance(parsed.get('details'),list): issues.append({'code':'DETAILS_SHAPE','id':uid})
  if not isinstance(parsed.get('examples'),list): issues.append({'code':'EXAMPLES_SHAPE','id':uid})
 if seen!=set(byid): issues.append({'code':'ID_SET_PARITY','missing':sorted(set(byid)-seen),'extra':sorted(seen-set(byid))})
 report={'validator':'menschen-a2-delivery-loss-check','validator_version':'1.0.0','status':'PASS' if not issues else 'FAIL','rows':len(lines)-1,'canonical_units':len(byid),'tsv_sha256':hashlib.sha256(ns.tsv.read_bytes()).hexdigest(),'canonical_sha256':hashlib.sha256(ns.canonical.read_bytes()).hexdigest(),'issues':issues}
 ns.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if report['status']=='PASS' else 1)
if __name__=='__main__': main()
