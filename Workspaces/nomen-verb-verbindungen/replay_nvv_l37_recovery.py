#!/usr/bin/env python3
"""Reconstruct exact L37 TSV and cumulative Ledger from verified L36 parent files.
Usage: python replay_nvv_l37_recovery.py L36.tsv L36-LEDGER.json L37-COMPACT-RECOVERY.json OUTPUT_DIR
No original file overwritten. Verifies SHA256, IDs, source scope, and final bytes.
"""
import csv,json,hashlib,pathlib,io,sys,base64,gzip
SHA=lambda b:hashlib.sha256(b).hexdigest()
if len(sys.argv)!=5: raise SystemExit('Usage: replay_nvv_l37_recovery.py PARENT.tsv PARENT-LEDGER.json RECOVERY.json OUTPUT_DIR')
a,b,d,o=map(pathlib.Path,sys.argv[1:]);outdir=o;outdir.mkdir(parents=True,exist_ok=True)
data=d.read_bytes()
if d.name.endswith('.gz.b64.txt'):
 data=gzip.decompress(base64.b64decode(data))
p=json.loads(data.decode('utf8'))
parent=a.read_bytes();parent_ld=b.read_bytes()
assert SHA(parent)==p['parent_master_sha256'] and SHA(parent_ld)==p['ledger_parent_sha256']
assert p['scope']==[1069,1098] and p['reviewed']==30
lines=parent.splitlines(keepends=True);assert len(lines)==2493
with io.StringIO(parent.decode('utf8'),newline='') as f:r=csv.DictReader(f,delimiter='\t');fields=r.fieldnames;rows=list(r)
assert len(rows)==2492 and len(set(x['id'] for x in rows))==2492
assert len({e['order'] for e in p['new_items']})==p['changed']
for entry in p['new_items']:
 i=entry['order'];assert 1069<=i<=1098
 row=rows[i-1].copy();assert row['id']==entry['id'] and row['front']==entry['front']
 assert SHA(row['details'].encode())==entry['before_details_sha256']
 assert SHA(row['custom_fields'].encode())==entry['before_custom_sha256']
 details=json.loads(row['details']);custom=json.loads(row['custom_fields'])
 for e in entry['append_items']:
  group=next((x for x in details if x['title']==e['tile']),None)
  if group is None:group={'title':e['tile'],'items':[]};details.append(group)
  assert e['display_item'] not in group['items']
  group['items'].append(e['display_item'])
  assert e['sidecar']['kind']==e['kind'] and e['sidecar']['display_item']==e['display_item']
  custom.setdefault('lexical_relations_v1',{}).setdefault(e['kind'],[]).append(e['sidecar'])
 row['details']=json.dumps(details,ensure_ascii=False,separators=(',',':'))
 row['custom_fields']=json.dumps(custom,ensure_ascii=False,separators=(',',':'))
 f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writerow(row)
 lines[i]=f.getvalue().encode('utf8')
master=b''.join(lines);assert SHA(master)==p['current_master_sha256']
ledger=json.loads(parent_ld.decode('utf8'));assert len(ledger['cards'])==1068
for k,v in p['ledger_updates'].items(): ledger[k]=v
ledger['cards'].extend(p['ledger_card_append'])
assert len(ledger['cards'])==1098
led=(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n').encode('utf8')
assert SHA(led)==p['ledger_sha256']
mp=outdir/'NVV-R16-FIVE-SECTIONS-L37-CURRENT-WORKING.tsv';lp=outdir/'NVV-R16-FIVE-SECTIONS-L37-LEDGER.json'
assert not mp.exists() and not lp.exists()
mp.write_bytes(master);lp.write_bytes(led)
print(json.dumps({'master_sha256':SHA(master),'ledger_sha256':SHA(led),'cards':2492,'reviewed':1098},ensure_ascii=False))