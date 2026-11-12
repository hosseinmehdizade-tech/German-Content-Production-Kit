#!/usr/bin/env python3
"""Exact deterministic reconstruction of Menschen A2 S8 from immutable S7 + bounded delta.
No network, no app, no edits to S7. Exits nonzero on any parent/child SHA mismatch.
"""
import argparse, base64, collections, copy, csv, hashlib, json, pathlib, zlib

NAMES={
'master': ('Menschen-A2-L01-L07-FIVE-SECTIONS-S7-1778-MASTER-WIP-20261112.tsv','Menschen-A2-L01-L08-FIVE-SECTIONS-S8-1778-MASTER-WIP-20261112.tsv'),
'canonical': ('Menschen-A2-L01-L07-FIVE-SECTIONS-S7-1778-CANONICAL-WIP-20261112.json','Menschen-A2-L01-L08-FIVE-SECTIONS-S8-1778-CANONICAL-WIP-20261112.json'),
'ledger': ('Menschen-A2-L01-L07-FIVE-SECTIONS-S7-CUMULATIVE-LEDGER-20261112.json','Menschen-A2-L01-L08-FIVE-SECTIONS-S8-CUMULATIVE-LEDGER-20261112.json')}

def sha256(p):
  hasher=hashlib.sha256()
  with p.open('rb') as f:
    for chunk in iter(lambda:f.read(1024*1024),b''):hasher.update(chunk)
  return hasher.hexdigest()

def load_delta(path):
  content=path.read_bytes()
  if path.name.endswith('.b64.txt'):
    content=zlib.decompress(base64.b64decode(content))
  elif path.suffix in ('.zlib','.zz'):
    content=zlib.decompress(content)
  return json.loads(content)

def replay(root, delta_path, outdir):
  data=load_delta(delta_path)
  assert data['schema']=='gcpk-a2-l08-recovery-delta@1'
  for kind,(parent_name,_) in NAMES.items():
    source=root/parent_name
    assert source.is_file(),source
    assert sha256(source)==data['parent'][f'{kind}_sha256'], f'{kind} parent SHA mismatch'
  delta=data['changed_tsv_cells_by_id']
  assert len(delta)==76 and all(k.startswith('ma2m-lu-') for k in delta)
  src=root/NAMES['master'][0]
  with src.open('r',encoding='utf-8',newline='') as f:
    reader=csv.DictReader(f,delimiter='\t')
    fields=reader.fieldnames; rows=list(reader)
  assert len(rows)==1778 and len({r['id'] for r in rows})==1778
  seen=set()
  for row in rows:
    key=row['id']
    if key in delta:
      assert row['lesson']=='A2-L08'
      assert set(delta[key]).issubset({'details','custom_fields'})
      row.update(delta[key]); seen.add(key)
  assert seen==set(delta)
  outdir.mkdir(parents=True,exist_ok=True)
  output=outdir/NAMES['master'][1]
  with output.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,delimiter='\t',fieldnames=fields,quoting=csv.QUOTE_MINIMAL,lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
  assert sha256(output)==data['child']['master_sha256'],'master child SHA mismatch'
  canonical=json.loads((root/NAMES['canonical'][0]).read_text('utf-8'))
  assert len(canonical['rows'])==1778
  extra=data['changed_canonical_fields_by_id']; found=set()
  for row in canonical['rows']:
    if row['id'] in extra:
      assert row['id'] in delta
      row.update(extra[row['id']]);found.add(row['id'])
  assert found==set(extra)
  canonical.update(data['canonical_top_level_updates'])
  output=outdir/NAMES['canonical'][1]
  output.write_text(json.dumps(canonical,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
  assert sha256(output)==data['child']['canonical_sha256'],'canonical child SHA mismatch'
  ledger=json.loads((root/NAMES['ledger'][0]).read_text('utf-8'))
  ledger.update(data['ledger_top_level_updates'])
  output=outdir/NAMES['ledger'][1]
  output.write_text(json.dumps(ledger,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
  assert sha256(output)==data['child']['ledger_sha256'],'ledger child SHA mismatch'
  assert len(ledger['L08_decisions'])==76
  return {'status':'PASS_RECONSTRUCT_S8_EXACT_FROM_S7_PLUS_DELTA','changed_cards':len(delta),
          'rebuilt_sha256':{kind:data['child'][f'{kind}_sha256'] for kind in NAMES},
          'parent_sha256':data['parent'],
          'delta_sha256':sha256(delta_path),'outdir':str(outdir)}

if __name__=='__main__':
  parser=argparse.ArgumentParser();parser.add_argument('--parent-dir',default='/mnt/data/a2_work');parser.add_argument('--delta',default='/mnt/data/a2_work/L08-S8-RECOVERY-DELTA-20261112.zlib');parser.add_argument('--output-dir',default='/mnt/data/a2_work/s8_replay_verified'); args=parser.parse_args()
  print(json.dumps(replay(pathlib.Path(args.parent_dir),pathlib.Path(args.delta),pathlib.Path(args.output_dir)),indent=2))
