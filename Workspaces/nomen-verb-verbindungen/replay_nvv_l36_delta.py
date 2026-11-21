#!/usr/bin/env python3
"""Restore exact R16 L36 Master from exact verified L35 TSV and approved Git delta.
Usage: python replay_nvv_l36_delta.py L35.tsv L36-DELTA.json OUTPUT.tsv
No originals are overwritten unless OUTPUT points to an existing path (prohibited).
"""
import csv,io,json,pathlib,hashlib,sys
if len(sys.argv)!=4:raise SystemExit('usage: replay_nvv_l36_delta.py PARENT_L35.tsv DELTA.json NEW_L36.tsv')
base,delta_path,out=map(pathlib.Path,sys.argv[1:]);assert not out.exists() and out.resolve()!=base.resolve()
blob=base.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();patch=json.loads(delta_path.read_text(encoding='utf8'))
assert sha(blob)==patch['parent_l35_sha256'], 'Wrong parent, refusing to downgrade/patch'
lines=blob.splitlines(keepends=True)
with base.open(encoding='utf8',newline='') as f:r=csv.DictReader(f,delimiter='\t');fields=r.fieldnames;rows=list(r)
assert len(rows)==2492 and len(lines)==2493
for entry in patch['new_items']:
 i=entry['order'];row=rows[i-1];assert row['id']==entry['id'] and row['front']==entry['front'] and 1040<=i<=1068
 details=json.loads(row['details']);custom=json.loads(row['custom_fields'])
 for a in entry['append_items']:
  title=a['tile'];display=a['display_item'];kind=a['kind'];rel=a['sidecar']
  assert rel['display_item']==display and rel['kind']==kind
  group=next((x for x in details if x['title']==title),None)
  if group is None:group={'title':title,'items':[]};details.append(group)
  assert display not in group['items'];group['items'].append(display)
  custom.setdefault('lexical_relations_v1',{}).setdefault(kind,[]).append(rel)
 row['details']=json.dumps(details,ensure_ascii=False,separators=(',',':'))
 row['custom_fields']=json.dumps(custom,ensure_ascii=False,separators=(',',':'))
 h=io.StringIO();w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writerow(row);lines[i]=h.getvalue().encode('utf8')
new=b''.join(lines);assert sha(new)==patch['expected_l36_sha256'],'Replayed SHA mismatch'
out.write_bytes(new);print('PASS',out,sha(new),len(new))