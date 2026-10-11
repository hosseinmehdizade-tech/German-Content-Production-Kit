from pathlib import Path
import csv,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PROJECTOR=ROOT/'Tools/project_v411_vocabulary_cards.py'
VALIDATOR=ROOT/'Verification/validate_learner_visible_lexical_front_v1_0_0.py'

def project(name,tmp):
 out=tmp/(name+'.json'); subprocess.run([sys.executable,str(PROJECTOR),str(ROOT/'Examples'/name),str(out)],check=True); return json.loads(out.read_text(encoding='utf-8'))

def test_noun_front_has_article_and_plural(tmp_path):
 c=project('GOLDEN-NOUN-Entscheidung-v1.0.0.json',tmp_path)[0]
 assert c['front']=='die Entscheidung, Entscheidungen'

def test_verb_front_has_principal_forms_but_typing_core_is_lemma(tmp_path):
 c=project('GOLDEN-VERB-warten-auf-v1.0.0.json',tmp_path)[0]
 assert c['front']=='warten, wartet, wartete, hat gewartet'
 assert c['customFields']['typingCore']=='warten'

def test_adjective_front_has_comparison(tmp_path):
 c=project('GOLDEN-ADJECTIVE-zuverlaessig-v1.0.0.json',tmp_path)[0]
 assert c['front']=='zuverlässig, zuverlässiger, am zuverlässigsten'

def test_validator_rejects_hidden_noun_morphology(tmp_path):
 row={'id':'n','card_type':'de-vocabulary','category':'Noun','front':'Bart','custom_fields':json.dumps({'canonical_unit':{'type':'noun','headword':'Bart','core':{'article':'der','plural':'Bärte'}}})}
 p=tmp_path/'x.tsv';
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=row.keys(),delimiter='\\t');w.writeheader();w.writerow(row)
 cp=subprocess.run([sys.executable,str(VALIDATOR),str(p)],text=True,capture_output=True)
 assert cp.returncode!=0 and 'NOUN_ARTICLE_NOT_LEARNER_VISIBLE' in cp.stdout and 'NOUN_PLURAL_NOT_LEARNER_VISIBLE' in cp.stdout

def test_validator_rejects_argument_placeholder_in_verb_lemma(tmp_path):
 row={'id':'v','card_type':'de-vocabulary','category':'Verb','front':'etw. auseinanderhalten, hält auseinander, hielt auseinander, hat auseinandergehalten','custom_fields':json.dumps({'canonical_unit':{'type':'verb','headword':'etw. auseinanderhalten','core':{'present_3sg':'hält auseinander','preterite':'hielt auseinander','perfect':'hat auseinandergehalten'}}})}
 p=tmp_path/'x.tsv';
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=row.keys(),delimiter='\\t');w.writeheader();w.writerow(row)
 cp=subprocess.run([sys.executable,str(VALIDATOR),str(p)],text=True,capture_output=True)
 assert cp.returncode!=0 and 'VERB_LEMMA_CONTAINS_ARGUMENT_PLACEHOLDER' in cp.stdout
