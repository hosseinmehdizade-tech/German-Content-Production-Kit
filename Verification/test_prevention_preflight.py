import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
import prevention_preflight as gate


def card():
    return {'id':'target-1','cardType':'de-vocabulary','category':'Verb','front':'hören','notes':'',
            'customFields':{'presentation_contract':'gfp-vocabulary-neutral@1','vnext_pos':'verb',
                            'vnext_morphology':{'present_3sg':'hört','preterite':'hörte','perfect':'hat gehört'},
                            'canonical_unit':{'core':{'present_3sg':'hört','preterite':'hörte','perfect':'hat gehört'},
                                              'definition_de':'mit den Ohren wahrnehmen','details':{}},
                            'vnext_structure':{'role':'accusative_object'}}}


class PreventionTests(unittest.TestCase):
    def test_split_authority_lineage_and_loss(self):
        prior=card();cf=prior['customFields'];cf.pop('canonical_unit')
        cf.update(canonical_target={'sense_id':'target-1'},canonical_lexeme={'lemma':'hören'},canonical_examples=[{'example_id':'example-1'}],canonical_relations=[],present='hört',preterite='hörte',perfect='hat gehört')
        self.assertEqual(gate.lineage_errors([copy.deepcopy(prior)],[prior]),[])
        missing=copy.deepcopy(prior);missing['customFields'].pop('canonical_examples')
        self.assertTrue(any('MISSING_CANONICAL_UNIT' in e for e in gate.lineage_errors([missing],[prior])))

    def test_finite_perfect_and_synonym_surface_gate(self):
        prior=card();cf=prior['customFields'];cf['vnext_morphology']['auxiliary']='haben';cf['perfect']='haben gehört'
        self.assertTrue(any('NONFINITE_OR_MISMATCHED_PERFECT' in e for e in gate.projection_errors([prior])))
        cf['perfect']='hat gehört';prior['related']=['vernehmen','vernehmen']
        self.assertTrue(any('DUPLICATE_RELATION_DISPLAY' in e for e in gate.projection_errors([prior])))

    def test_positive_semantic_enums_preserved(self):
        self.assertEqual(gate.projection_errors([card()]), [])

    def test_duplicate_id(self):
        self.assertIn('target-1: DUPLICATE_CANONICAL_ID',gate.projection_errors([card(),card()]))

    def test_successor_lineage_without_density_requirement(self):
        value=card();cf=value['customFields'];cf['canonical_relations']=[]
        cf['source_audio_refs']=[{'filename':'source.mp3'}];cf['course_memberships']=[{'book':'Mutable seed'}]
        value.update(source='Mutable seed',lesson='Generic lesson',deck='Generic deck',order=1)
        self.assertEqual(gate.lineage_errors([copy.deepcopy(value)],[value]),[])

    def test_neutral_successor_cannot_drop_parent_lineage(self):
        prior=card();prior['customFields'].update(canonical_relations=[],source_audio_refs=[{'filename':'source.mp3'}],course_memberships=[{'book':'Seed'}])
        prior.update(source='Seed',lesson='Lesson',deck='Deck',order=1)
        value=copy.deepcopy(prior);cf=value['customFields'];cf.pop('canonical_unit');cf.pop('canonical_relations');cf['source_audio_refs']=[]
        value['lesson']=''
        errors=gate.lineage_errors([value],[prior])
        for code in ['MISSING_CANONICAL_UNIT','MISSING_CANONICAL_RELATIONS','PARENT_LINEAGE_LOST source_audio_refs','PARENT_SEED_OR_ORDER_CHANGED_REVIEW_REQUIRED lesson']:
            self.assertTrue(any(code in e for e in errors),code)

    def test_same_front_distinct_ids_require_review_not_merge(self):
        other=card(); other['id']='homograph-2'
        self.assertEqual(gate.projection_errors([card(),other]),[])

    def test_no_empty_projection(self):
        self.assertIn('EMPTY_PROJECTION_OR_ID',gate.projection_errors([]))

    def test_definition_note(self):
        value=card();value['notes']='mit den Ohren wahrnehmen'
        self.assertTrue(any('DUPLICATE_DEFINITION_NOTE' in e for e in gate.projection_errors([value])))

    def test_literal_rektion(self):
        value=card();value['customFields']['canonical_unit']['details']['rection']=['REKTION']
        self.assertTrue(any('LITERAL_REKTION' in e for e in gate.projection_errors([value])))

    def test_internal_role_leak(self):
        value=card();value['customFields']['canonical_unit']['details']['structure']=['accusative_object']
        self.assertTrue(any('INTERNAL_ENUM' in e for e in gate.projection_errors([value])))

    def test_morphology_bridge(self):
        value=card();value['customFields']['canonical_unit']['core']={}
        self.assertEqual(sum('MISSING_MORPHOLOGY_BRIDGE' in e for e in gate.projection_errors([value])),3)

    def test_typed_related_is_not_synonym(self):
        value=card();value['related']=[{'type':'RELATED','text':'Musik'}]
        self.assertTrue(any('NON_SYNONYM' in e for e in gate.projection_errors([value])))

    def test_hidden_case_insensitive_selector(self):
        value=card();value['customFields']['nested']=[{'LAYOUT_Profile':'verb'}]
        self.assertTrue(any('PRESENTATION_SELECTOR_CONFLICT' in e for e in gate.projection_errors([value])))

    def test_legacy_type_rejected_new_projection(self):
        value=card();value['cardType']='german-verb'
        self.assertTrue(gate.projection_errors([value]))

    def test_archive_positive_and_contamination(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'candidate.zip'
            with zipfile.ZipFile(path,'w') as z:z.writestr('delivery/cards.tsv','id\n1\n')
            self.assertEqual(gate.package_errors(path),[])
            with zipfile.ZipFile(path,'a') as z:
                z.writestr('delivery\\__PYCACHE__\\test.pyc','bad')
                z.writestr('../escape','bad')
            errors=gate.package_errors(path)
            self.assertTrue(any('PACKAGE_CONTAMINATION' in e for e in errors))
            self.assertTrue(any('UNSAFE_ZIP_PATH' in e for e in errors))

    def test_duplicate_archive_member(self):
        import warnings
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'candidate.zip'
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',UserWarning)
                with zipfile.ZipFile(path,'w') as z:
                    z.writestr('cards.tsv','a');z.writestr('cards.tsv','b')
            self.assertTrue(any('DUPLICATE_ZIP_MEMBER' in e for e in gate.package_errors(path)))

    def test_checkpoint_pointers(self):
        self.assertTrue(gate.checkpoint_errors({'next_action':'continue'}))
        self.assertEqual(gate.checkpoint_errors({'project_memory':'PROJECT-MEMORY.json','git_sync_policy':'GIT-SYNC-POLICY.json','next_action':'complete'}),[])

    def test_unknown_checkpoint_lesson(self):
        data={'project_memory':'PROJECT-MEMORY.json','git_sync_policy':'GIT-SYNC-POLICY.json','next_action':'complete','prevention_refs':['invented']}
        self.assertIn('UNKNOWN_PREVENTION_REFERENCE: invented',gate.checkpoint_errors(data,{'decisions':[]}))

    def test_legacy_projector_cannot_bypass_learner_gate(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('legacy_projector',gate.ROOT/'Tools/project_v411_vocabulary_cards.py')
        projector=importlib.util.module_from_spec(spec);spec.loader.exec_module(projector)
        data={'lexemes':[{'lexeme_id':'l1','lemma':'hören','pos':'verb'}],
              'senses':[{'sense_id':'s1','lexeme_id':'l1','definition_de':'mit den Ohren wahrnehmen','translations':{'fa':'شنیدن'}}]}
        self.assertTrue(any('DUPLICATE_DEFINITION_NOTE' in e for e in gate.projection_errors(projector.project(data))))

    def test_real_memory_and_preserved_decision_mutation(self):
        memory=json.loads((gate.ROOT/'PROJECT-MEMORY.json').read_text(encoding='utf-8'))
        self.assertEqual(gate.memory_errors(memory,gate.ROOT),[])
        memory['decisions'][0]['decision']='silently replaced'
        self.assertTrue(any('PRESERVED_DECISION_CHANGED' in e for e in gate.memory_errors(memory,gate.ROOT)))

    def test_stale_sync_coordination(self):
        state=json.loads((gate.ROOT/'PROJECT-STATE.json').read_text(encoding='utf-8'))
        sync=json.loads((gate.ROOT/'GIT-SYNC-POLICY.json').read_text(encoding='utf-8'))
        self.assertEqual(gate.coordination_errors(state,sync),[])
        state['git_sync_policy']['mode']='BOUNDED_DEFERRED_COALESCED'
        state['operating_mode']['git_retry_budget_per_normal_turn']=1
        self.assertEqual(len(gate.coordination_errors(state,sync)),2)
        state['git_sync_policy'].pop('mode')
        self.assertEqual(len(gate.coordination_errors(state,sync)),2)

    def test_supersession_and_duplicate_memory_ids(self):
        memory=json.loads((gate.ROOT/'PROJECT-MEMORY.json').read_text(encoding='utf-8'))
        broken=copy.deepcopy(memory);broken['decisions'][0]['superseded_by']=[]
        self.assertTrue(any('BROKEN_SUPERSESSION' in e for e in gate.memory_errors(broken,gate.ROOT)))
        memory['decisions'].append(copy.deepcopy(memory['decisions'][0]))
        self.assertIn('MEMORY_IDS_EMPTY_OR_DUPLICATED',gate.memory_errors(memory,gate.ROOT))


if __name__=='__main__':unittest.main()
