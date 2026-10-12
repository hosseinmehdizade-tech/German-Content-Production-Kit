from pathlib import Path
import csv,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
VALIDATOR=ROOT/'Verification/validate_learner_visible_lexical_front_v1_1_0.py'
def run(row,tmp_path):
 p=tmp_path/'x.tsv'
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=row.keys(),delimiter='\t');w.writeheader();w.writerow(row)
 return subprocess.run([sys.executable,str(VALIDATOR),str(p)],text=True,capture_output=True)
def cf(core,head,type='noun'): return json.dumps({'canonical_unit':{'type':type,'headword':head,'core':core}},ensure_ascii=False)
def test_simple_noun_pass(tmp_path):
 assert run({'id':'n','category':'Noun','front':'der Bart, Bärte','custom_fields':cf({'article':'der','plural':'Bärte'},'Bart')},tmp_path).returncode==0
def test_missing_article_fails(tmp_path):
 cp=run({'id':'n','category':'Noun','front':'Promi, Promis','custom_fields':cf({'plural':'Promis'},'Promi')},tmp_path);assert cp.returncode!=0 and 'NOUN_ARTICLE_METADATA_MISSING' in cp.stdout
def test_multi_gender_noun_pass(tmp_path):
 assert run({'id':'n','category':'Noun','front':'der Prominente / die Prominente, die Prominenten','custom_fields':cf({'singular_forms':['der Prominente','die Prominente'],'plural':'die Prominenten'},'Prominente')},tmp_path).returncode==0
def test_nested_substantivized_requires_neuter_form(tmp_path):
 core={'person_forms':{'singular_forms':['der Neue','die Neue'],'plural':'die Neuen'},'thing_forms':{'article':'das','forms':['das Neue','etwas Neues'],'plural':None}}
 cp=run({'id':'n','category':'Noun','front':'der Neue / die Neue, die Neuen','custom_fields':cf(core,'Neue')},tmp_path);assert cp.returncode!=0 and 'das Neue' in cp.stdout
def test_nested_substantivized_pass(tmp_path):
 core={'person_forms':{'singular_forms':['der Neue','die Neue'],'plural':'die Neuen'},'thing_forms':{'article':'das','forms':['das Neue','etwas Neues'],'plural':None}}
 assert run({'id':'n','category':'Noun','front':'der Neue / die Neue / das Neue, die Neuen','custom_fields':cf(core,'Neue')},tmp_path).returncode==0
def test_placeholder_after_sich_fails(tmp_path):
 cp=run({'id':'v','category':'Verb','front':'sich etw. ansehen, sieht sich an, sah sich an, hat sich angesehen','custom_fields':cf({'present_3sg':'sieht sich an','preterite':'sah sich an','perfect':'hat sich angesehen'},'sich etw. ansehen','verb')},tmp_path);assert cp.returncode!=0 and 'VERB_LEMMA_CONTAINS_ARGUMENT_PLACEHOLDER' in cp.stdout
def test_gender_enum_maps_to_article(tmp_path):
 r={'id':'n','category':'Noun','front':'der Tisch, Tische','custom_fields':json.dumps({'vnext_gender':'masculine','canonical_unit':{'type':'noun','headword':'Tisch','core':{'plural':'Tische'}}},ensure_ascii=False)};assert run(r,tmp_path).returncode==0
