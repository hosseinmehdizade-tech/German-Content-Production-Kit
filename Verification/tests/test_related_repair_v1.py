#!/usr/bin/env python3
"""Source-bound, negative-guard tests on real Menschen A1 V24 parent bytes."""
import unittest,sys,pathlib,json,csv,copy,io,os
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools' if (ROOT/'Tools').is_dir() else ROOT))
from repair_verwandt_categories_v1 import load_parent,successor_row,semantic_target_route,norm
from triage_related_semantics_v1 import triage
PARENT=pathlib.Path(os.environ.get('GCPK_PARENT_ZIP','/mnt/data/Menschen-A1-V24-COMPLETE-DELIVERY-v505-R141-20261102(1).zip'))

class RelatedRepair(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not PARENT.exists():raise unittest.SkipTest('Exact user-uploaded parent not mounted; this test never guesses an archive')
  cls.rows,cls.header,cls.raw=load_parent(PARENT);cls.map={r['id']:r for r in cls.rows}
 @classmethod
 def convert(cls,card_id):
  r=cls.map[card_id];return r,successor_row(r,cls.map)
 def test_full_identity_count(self):self.assertEqual(len(self.rows),2997);self.assertEqual(len(self.map),2997)
 def test_no_original_mutation(self):
  r=self.map['ma1m-lu-1301'];before=copy.deepcopy(r);successor_row(r,self.map);self.assertEqual(r,before)
 def test_description_no_related_duplicate(self):
  a,(b,rec)=self.convert('ma1m-lu-1301');self.assertNotIn('Verwandte Wörter',b['details']);self.assertEqual(len(rec['related_display_suppressed']),2)
 def test_description_keeps_actual_combo(self):
  _,(b,rec)=self.convert('ma1m-lu-1301');items=json.loads(b['custom_fields'])['kombinationen_v1']['items'];self.assertEqual([x['de'] for x in items],['allgemeine Beschreibung'])
 def test_description_standalone_rede_mittel_preserved(self):
  _,(b,_)=self.convert('ma1m-lu-1301');cf=json.loads(b['custom_fields']);self.assertTrue(any(r.get('target_id')=='ma1m-lu-1305' for r in cf['canonical_relations']));self.assertEqual(self.map['ma1m-lu-1305']['front'],'Bitte senden Sie uns eine Beschreibung.')
 def test_reclass_durst_to_wordfamily(self):
  _,(b,rec)=self.convert('ma1m-lu-0811');d=json.loads(b['details']);self.assertIn('durstig',[x for s in d if s['title']=='Wortfamilie' for x in s['items']]);self.assertEqual(rec['reclassified_to_typed_section'][0]['target_id'],'ma1m-lu-0815')
 def test_reclass_synonym(self):
  _,(b,rec)=self.convert('ma1m-lu-0846');self.assertEqual(rec['reclassified_to_typed_section'][0]['to_title'],'Synonyme');self.assertTrue(any(s['title']=='Synonyme' and 'Gleichfalls!' in s['items'] for s in json.loads(b['details'])))
 def test_related_greeting_stays(self):
  a,(b,rec)=self.convert('ma1m-lu-0001');self.assertIsNone(rec);self.assertEqual(a,b)
 def test_no_fuzzy_substring_promotion(self):
  self.assertIsNone(semantic_target_route('nicht durstig',[{'type':'WORD_FAMILY','target_id':'ma1m-lu-0815'}],self.map))
 def test_graph_bytes_equal_edited(self):
  for id in ['ma1m-lu-1301','ma1m-lu-0811','ma1m-lu-0846','ma1m-lu-1656','ma1m-lu-1664']:
   a,(b,_) = self.convert(id);x=json.loads(a['custom_fields']);y=json.loads(b['custom_fields']);self.assertEqual(x.get('canonical_relations'),y.get('canonical_relations'));self.assertEqual(x.get('vnext_relations'),y.get('vnext_relations'))
 def test_four_examples_untouched(self):
  for id in ['ma1m-lu-1301','ma1m-lu-1656','ma1m-lu-1664']:
   a,(b,_) = self.convert(id);self.assertEqual(a['examples'],b['examples'])
 def test_core_unchanged(self):
  for id in ['ma1m-lu-1301','ma1m-lu-0811','ma1m-lu-0846','ma1m-lu-1656']:
   a,(b,_) = self.convert(id)
   for field in self.header:
    if field not in ('details','custom_fields'):self.assertEqual(a[field],b[field])
 def test_no_word_family_from_syntax_only(self):
  self.assertIsNone(semantic_target_route('Hallo Welt',[{'type':'RELATED','target_id':'ma1m-lu-0001'}],self.map))
 def test_redundant_example_removed_from_combo(self):
  for id,txt in [('ma1m-lu-1656','Die Tür ist hinten.'),('ma1m-lu-1664','Ich muss dich dringend sprechen.')]:
   _,(b,rec)=self.convert(id);cf=json.loads(b['custom_fields']);self.assertNotIn(norm(txt),[norm(x['de']) for x in cf['kombinationen_v1']['items']]);self.assertTrue(rec['combo_removed'])
 def test_canonical_detail_mirrors_reclassified(self):
  _,(b,_)=self.convert('ma1m-lu-0811');detail=json.loads(b['custom_fields'])['canonical_unit']['details'];self.assertEqual(detail['Wortfamilie'],['durstig']);self.assertNotIn('Verwandt',detail)

if __name__=='__main__':unittest.main(verbosity=2)