#!/usr/bin/env python3
from copy import deepcopy
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('q',HERE/'validate_lexical_quality_v1_0_0.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)

def base():
    return {'learning_units':[{
      'id':'T-1','type':'verb','headword':'warten','definition_de':'bleiben, bis etwas geschieht',
      'core':{'present_3sg':'wartet','preterite_3sg':'wartete','perfect':'hat gewartet','auxiliary':'haben','reflexive':False,'separability':'non_prefixed'},
      'examples':[{'id':'e1','text':'Ich warte hier.','translations':[{'lang':'fa-IR','text':'منتظر می‌مانم.'},{'lang':'en-US','text':'I wait here.'}]}],
      'provenance':{'sources':[]}
    }]}

def codes(report): return {x['code'] for x in report['issues']}

def run():
    d=base();assert q.validate_dataset(d)['status']=='PASS'  # no count-forcing
    d=base();u=d['learning_units'][0];u['connections']=[{'kind':'collocation','text':'auf Antwort warten, auf den Bus warten'}];u['provenance']['sources']=[{'verification_status':'verified','what_was_verified':['collocation']}];r=q.validate_dataset(d);assert 'COLLOCATION_NOT_ATOMIC' in codes(r)
    d=base();u=d['learning_units'][0];u['connections']=[{'kind':'collocation','text':'auf Antwort warten'}];u['provenance']['sources']=[{'source_id':'current_card_examples_v3','verification_status':'verified','what_was_verified':['collocation']}];r=q.validate_dataset(d);assert 'EXAMPLE_DERIVED_AS_COLLOCATION' in codes(r)
    d=base();u=d['learning_units'][0];u['headword']='auf etw. warten';u['connections']=[{'kind':'collocation','text':'lange warten'}];u['details']={'rection':['auf etw. (Akk.) warten']};u['provenance']['sources']=[{'verification_status':'verified','what_was_verified':['collocation','rection']}];r=q.validate_dataset(d);assert 'COLLOCATION_FIXED_PREP_MISMATCH' in codes(r)
    d=base();u=d['learning_units'][0];u['headword']='auf etw. warten';r=q.validate_dataset(d);assert 'RECTION_REQUIRED' in codes(r)
    d=base();u=d['learning_units'][0];u['details']={'synonyms':['abwarten']};u['provenance']['sources']=[{'source_id':'de_wiktionary_pos_scoped_wikitext','verification_status':'verified','what_was_verified':['synonymy']}];r=q.validate_dataset(d);assert 'RELATION_BROAD_SENSE_SOURCE' in codes(r)
    print('PASS lexical-quality regression tests')
if __name__=='__main__':run()
