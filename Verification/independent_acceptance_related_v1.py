"""Independent structural check on exact source parent and derived TSV. Read-only."""
import argparse,csv,json,hashlib,collections,io,zipfile,pathlib,sys
p=argparse.ArgumentParser();p.add_argument('parent');p.add_argument('candidate');p.add_argument('ledger');a=p.parse_args()
with zipfile.ZipFile(a.parent) as z: origin=list(csv.DictReader(io.TextIOWrapper(z.open('Content/Menschen-A1-V24-FULL-2997-IMPORT.tsv'),'utf8'),delimiter='\t'))
with open(a.candidate,encoding='utf8') as f:candidate=list(csv.DictReader(f,delimiter='\t'))
assert len(candidate)==len(origin)==2997
assert [r['id'] for r in candidate]==[r['id'] for r in origin]
assert all(len(r)==23 for r in candidate)
ledger=json.load(open(a.ledger,encoding='utf8'));eids={x['id'] for x in ledger['changes']}
assert len(eids)==ledger['counts']['card_changes']==75
changed=[];mut=collections.Counter()
for r,b in zip(origin,candidate):
 bad=[key for key in r if r[key]!=b[key]]
 if bad:changed.append(r['id']);mut.update(bad)
 assert set(bad).issubset({'details','custom_fields'})
 if r['id'] not in eids:assert r==b,('unledgered edit',r['id'])
 cf0=json.loads(r['custom_fields']);cf1=json.loads(b['custom_fields'])
 for key in cf0:
  if key not in ('canonical_unit','kombinationen_v1','kombinationen_v336'):assert cf0[key]==cf1[key],('inadvertent custom field edit',r['id'],key)
 c0=cf0.get('canonical_unit');c1=cf1.get('canonical_unit');
 if isinstance(c0,dict):
  for key in c0:
   if key!='details':assert c0[key]==c1[key],('inadvertent core canonical mutation',r['id'],key)
 if cf0.get('canonical_relations')!=cf1.get('canonical_relations') or cf0.get('vnext_relations')!=cf1.get('vnext_relations'):raise AssertionError(('graph changed',r['id']))
 if cf0.get('kombinationen_v1')!=cf1.get('kombinationen_v1') and r['id'] not in ('ma1m-lu-1301','ma1m-lu-1656','ma1m-lu-1664'):raise AssertionError(('unexpected combination edit',r['id']))
 if cf0.get('kombinationen_v336')!=cf1.get('kombinationen_v336') and r['id'] not in ('ma1m-lu-1301','ma1m-lu-1656','ma1m-lu-1664'):raise AssertionError(('unexpected combination edit',r['id']))
assert len(changed)==75 and set(changed)==eids
# deliberate semantics backed by exact source A1 and typed graph
check={r['id']:r for r in candidate}
for card,item,section in [('ma1m-lu-0811','durstig','Wortfamilie'),('ma1m-lu-0846','Gleichfalls!','Synonyme')]:
 assert item in [x for d in json.loads(check[card]['details']) if d['title']==section for x in d['items']]
assert not any(x['title']=='Verwandte Wörter' for x in json.loads(check['ma1m-lu-1301']['details']))
report={'result':'PASS_SCOPED_STRUCTURAL_NOT_STAGE4','parent_count':len(origin),'successor_count':len(candidate),'changed_ids':len(changed),'changed_field_counts':dict(mut),'typed_graph_preserved':True,'examples_identity_preserved':True,'source_and_id_columns_preserved':True,'ledger_counts':ledger['counts']}
print(json.dumps(report,ensure_ascii=False,indent=2))