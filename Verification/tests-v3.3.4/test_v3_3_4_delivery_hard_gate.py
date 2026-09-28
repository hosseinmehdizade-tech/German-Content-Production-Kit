from pathlib import Path
import json, subprocess, sys, zipfile

ROOT=Path(__file__).resolve().parents[2]
BUILDER=ROOT/'Tools/build_clean_delivery.py'
PROJECTOR=ROOT/'Tools/project_v411_vocabulary_cards.py'
VALIDATOR=ROOT/'Verification/validate_unified_vocabulary_projection_v1_0_0.py'

def write_common(d):
    (d/'canonical.json').write_text('{}\n',encoding='utf-8')
    (d/'source-output-map.tsv').write_text('source_row\tstatus\n1\tPASS\n',encoding='utf-8')
    (d/'verification.json').write_text('{"status":"PASS"}\n',encoding='utf-8')

def run_builder(d):
    out=d/'delivery.zip'
    cp=subprocess.run([sys.executable,str(BUILDER),str(d),str(out)],text=True,capture_output=True)
    return cp,out

def test_active_prompt_is_v334_and_hard_gate_is_mandatory():
    assert (ROOT/'Prompt/ACTIVE-PROMPT.txt').read_text().strip()=='START-PROMPT-v3.3.4.md'
    s=(ROOT/'Prompt/START-PROMPT-v3.3.4.md').read_text(encoding='utf-8')
    assert 'builder' in s.lower() and 'card_type' in s and 'de-vocabulary' in s

def test_builder_rejects_missing_card_type_column(tmp_path):
    write_common(tmp_path)
    (tmp_path/'A1-UNIVERSAL-v2.tsv').write_text('id\tcategory\tfront\tback\n1\tVerb\tgehen\tرفتن\n',encoding='utf-8')
    cp,out=run_builder(tmp_path)
    assert cp.returncode!=0 and not out.exists() and 'card_type' in (cp.stdout+cp.stderr)

def test_builder_rejects_legacy_german_verb(tmp_path):
    write_common(tmp_path)
    (tmp_path/'A1-UNIVERSAL-v2.tsv').write_text('id\tcard_type\tcategory\tfront\tback\n1\tgerman-verb\tVerb\tgehen\tرفتن\n',encoding='utf-8')
    cp,out=run_builder(tmp_path)
    assert cp.returncode!=0 and not out.exists() and 'de-vocabulary' in (cp.stdout+cp.stderr)

def test_builder_rejects_mixed_neutral_and_legacy_rows(tmp_path):
    write_common(tmp_path)
    (tmp_path/'A1-UNIVERSAL-v2.tsv').write_text('id\tcard_type\tcategory\tfront\tback\n1\tde-vocabulary\tNoun\tHaus\tخانه\n2\tgerman-verb\tVerb\tgehen\tرفتن\n',encoding='utf-8')
    cp,out=run_builder(tmp_path)
    assert cp.returncode!=0 and not out.exists() and 'german-verb' in (cp.stdout+cp.stderr)

def test_builder_rejects_missing_semantic_category_via_embedded_validator(tmp_path):
    write_common(tmp_path)
    (tmp_path/'A1-UNIVERSAL-v2.tsv').write_text('id\tcard_type\tcategory\tfront\tback\n1\tde-vocabulary\t\tgehen\tرفتن\n',encoding='utf-8')
    cp,out=run_builder(tmp_path)
    assert cp.returncode!=0 and not out.exists() and 'MISSING_SEMANTIC_CATEGORY' in (cp.stdout+cp.stderr)

def test_builder_accepts_only_neutral_rows_and_records_gate(tmp_path):
    write_common(tmp_path)
    (tmp_path/'A1-UNIVERSAL-v2.tsv').write_text('id\tcard_type\tcategory\tfront\tback\n1\tde-vocabulary\tNoun\tHaus\tخانه\n2\tde-vocabulary\tVerb\tgehen\tرفتن\n3\tde-vocabulary\tAdjective\tgut\tخوب\n4\tde-vocabulary\tExpression\tGuten Morgen\tصبح بخیر\n',encoding='utf-8')
    cp,out=run_builder(tmp_path)
    assert cp.returncode==0,cp.stdout+cp.stderr
    with zipfile.ZipFile(out) as z:
        m=json.loads(z.read('CONTENT-DELIVERY/DELIVERY-MANIFEST.json'))
        assert m['unified_vocabulary_validation']=='PASS_EMBEDDED_BUILDER_GATE'
        assert m['required_card_type']=='de-vocabulary'

def test_projector_output_survives_both_validator_and_builder_contract(tmp_path):
    projected=tmp_path/'projected.json'
    cp=subprocess.run([sys.executable,str(PROJECTOR),str(ROOT/'Examples/GOLDEN-VERB-warten-auf-v1.0.0.json'),str(projected)],text=True,capture_output=True)
    assert cp.returncode==0
    cards=json.loads(projected.read_text(encoding='utf-8'))
    assert cards and {c['cardType'] for c in cards}=={'de-vocabulary'}
    cp2=subprocess.run([sys.executable,str(VALIDATOR),str(projected)],text=True,capture_output=True)
    assert cp2.returncode==0

def test_delivery_policy_records_non_bypassable_builder_rules():
    p=json.loads((ROOT/'Tools/DELIVERY-HYGIENE-POLICY.json').read_text(encoding='utf-8')); r=p['rules']
    assert p['kit_version']=='3.3.4'
    assert r['unified_vocabulary_card_type_column_required'] is True
    assert r['unified_vocabulary_neutral_card_type']=='de-vocabulary'
    assert r['builder_must_invoke_projection_validator'] is True
    assert r['builder_must_fail_before_zip_on_projection_violation'] is True

def test_builder_role_resolution_accepts_real_uppercase_universal_filename(tmp_path):
    write_common(tmp_path)
    (tmp_path/'A1-VERBEN-UNIVERSAL-v2.tsv').write_text('id\tcard_type\tcategory\tfront\tback\n1\tde-vocabulary\tVerb\tgehen\tرفتن\n',encoding='utf-8')
    cp,out=run_builder(tmp_path)
    assert cp.returncode==0,cp.stdout+cp.stderr
    assert out.exists()
