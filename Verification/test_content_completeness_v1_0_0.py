#!/usr/bin/env python3
import importlib.util, json, pathlib, unittest
HERE=pathlib.Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("v",HERE/"validate_content_completeness_v1_0_0.py")
v=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(v)
PROFILE=json.loads((HERE.parent/"Prompt"/"MENSCHEN-A1-CONTENT-COMPLETENESS-v1.0.0.json").read_text(encoding="utf-8"))

def src(*claims): return {"sources":[{"verification_status":"verified","what_was_verified":list(claims),"locator":"fixture://evidence"}]}
def unit(conns=None,syn=None,ant=None,prov=None,headword="machen",rection=None):
    d={}
    if syn is not None:d["synonyms"]=syn
    if ant is not None:d["antonyms"]=ant
    if rection is not None:d["rection"]=rection
    return {"id":"MEN-A1-00001","type":"verb","headword":headword,"core":{"present_3sg":"macht","preterite_3sg":"machte","perfect":"hat gemacht","auxiliary":"haben","reflexive":False,"separability":"non_prefixed"},"details":d,"connections":conns or [],"examples":[],"metadata":{},"provenance":prov or {"sources":[]}}

class CompletenessTests(unittest.TestCase):
    def report(self,u):return v.validate({"learning_units":[u]},PROFILE)
    def test_missing_collocations_is_hard_fail(self):
        r=self.report(unit(prov=src("collocation")));self.assertEqual(r["status"],"FAIL");self.assertTrue(any(i["code"]=="COMPLETENESS_MINIMUM" for i in r["issues"]))
    def test_three_collocations_with_explicit_evidence_pass_hard_gate(self):
        c=[{"kind":"collocation","text":x} for x in ["eine Pause machen","Sport machen","einen Fehler machen"]];self.assertEqual(self.report(unit(c,prov=src("collocation")))["errors"],0)
    def test_generic_usage_does_not_prove_collocation(self):
        c=[{"kind":"collocation","text":x} for x in ["eine Pause machen","Sport machen","einen Fehler machen"]];r=self.report(unit(c,prov=src("usage")));self.assertEqual(r["status"],"FAIL")
    def test_synonym_present_requires_synonymy_evidence(self):
        c=[{"kind":"collocation","text":x} for x in ["eine Pause machen","Sport machen","einen Fehler machen"]];r=self.report(unit(c,syn=["tun"],prov=src("collocation")));self.assertTrue(any(i["path"].endswith("details.synonyms") and i["severity"]=="error" for i in r["issues"]))
    def test_missing_synonym_is_only_warning(self):
        c=[{"kind":"collocation","text":x} for x in ["eine Pause machen","Sport machen","einen Fehler machen"]];r=self.report(unit(c,prov=src("collocation")));self.assertEqual(r["errors"],0);self.assertGreaterEqual(r["warnings"],2)
    def test_rection_present_requires_evidence(self):
        c=[{"kind":"collocation","text":x} for x in ["auf den Bus warten","lange warten","draußen warten"]];self.assertEqual(self.report(unit(c,prov=src("collocation"),rection=["auf + Akk"],headword="warten auf etw."))["status"],"FAIL")
    def test_rection_explicit_evidence_passes(self):
        c=[{"kind":"collocation","text":x} for x in ["auf den Bus warten","lange warten","draußen warten"]];self.assertEqual(self.report(unit(c,prov=src("collocation","rection"),rection=["auf + Akk"],headword="warten auf etw."))["errors"],0)
    def test_nvv_does_not_count_as_collocation(self):
        c=[{"kind":"nvv","text":x} for x in ["eine Pause machen","Sport machen","einen Fehler machen"]];self.assertEqual(self.report(unit(c,prov=src("collocation")))["status"],"FAIL")

if __name__=="__main__":unittest.main(verbosity=2)
