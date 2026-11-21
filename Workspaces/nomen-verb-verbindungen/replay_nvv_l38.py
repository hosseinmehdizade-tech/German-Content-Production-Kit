#!/usr/bin/env python3
"""Reconstruct byte-exact R16 L38 Master/ledger from preserved L37 and recovery delta.
python replay_nvv_l38.py L37.tsv L37-ledger.json L38-delta.gz.b64.txt new-L38.tsv new-L38-ledger.json
Never overwrites an existing file; SHA guards prevent stale source mixing.
"""
import pathlib,json,hashlib,csv,io,base64,gzip,sys
assert len(sys.argv)==6,'Arguments: L37 TSV, L37 Ledger JSON, Delta gzip-base64, new Master TSV, new Ledger JSON'
p,l,d,om,ol=map(pathlib.Path,sys.argv[1:]);assert p.exists() and l.exists() and d.exists();assert not om.exists() and not ol.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=p.read_bytes();ledraw=l.read_bytes()
patch=json.loads(gzip.decompress(base64.b64decode(d.read_bytes())).decode('utf8'))
assert patch['schema']=='nvv-r16-l38-lossless-recovery@1'
assert sha(raw)==patch['parent_master_sha256'] and sha(ledraw)==patch['parent_ledger_sha256'],'Wrong L37 parent'
lines=raw.splitlines(keepends=True);assert len(lines)==2493
with p.open(encoding='utf8',newline='') as f:rr=csv.DictReader(f,delimiter='\t');fields=rr.fieldnames;rows=list(rr)
assert len(rows)==2492 and len(patch['modified'])==26
orders=[]
for edit in patch['modified']:
 order=edit['order'];orders.append(order);assert 1099<=order<=1128
 row=rows[order-1];assert row['id']==edit['id'] and row['front']==edit['front'] and int(row['order'])==order
 assert sha(row['details'].encode())==edit['before_details_sha256'] and sha(row['custom_fields'].encode())==edit['before_custom_sha256']
 details=json.loads(edit['after_details']);custom=json.loads(edit['after_custom_fields']);assert isinstance(details,list) and isinstance(custom,dict)
 row['details']=edit['after_details'];row['custom_fields']=edit['after_custom_fields']
 o=io.StringIO(newline='');csv.DictWriter(o,fieldnames=fields,delimiter='\t',lineterminator='\n').writerow(row)
 lines[order]=o.getvalue().encode('utf8')
assert len(orders)==len(set(orders))
master=b''.join(lines);assert sha(master)==patch['output_master_sha256']
ledger=json.loads(ledraw);assert len(ledger['cards'])==1098
app=patch['ledger_append'];assert len(app)==30 and [q['order'] for q in app]==list(range(1099,1129))
ledger['cards'].extend(app)
for k,v in patch['ledger_overrides'].items():ledger[k]=v
assert len(ledger['cards'])==1128
new_led=(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n').encode('utf8')
assert sha(new_led)==patch['output_ledger_sha256']
om.write_bytes(master);ol.write_bytes(new_led)
print(json.dumps({'master_sha256':sha(master),'ledger_sha256':sha(new_led),'reviewed':1128,'output_files':[str(om),str(ol)]}))
