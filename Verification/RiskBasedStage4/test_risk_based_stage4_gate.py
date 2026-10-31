import copy, hashlib, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from risk_based_stage4_gate import evaluate

H='a'*64
P={'sampling':{'min_strata':1,'min_cards_per_stratum':1,'min_examples_per_stratum':1,'min_combos_per_stratum':1},'profiles':{},'acceptance':{'max_documented_noncritical_holds':1,'min_negative_controls':5}}
E={'workstream':'test','authority':{'working_sha256':H,'registered_source_sha256':'b'*64,'source_unchanged':True},'mechanical':{'full_population_checked':True,'counts':{'cards':1,'examples':1,'visible_combos':1},'checks':{x:'PASS' for x in ('identity','source_fidelity','examples','translations_present','relationships','render_projection','source_immutability')}},'risk_scan':{'full_population_checked':True,'flagged_ids':['a1:c1']},'risk_dispositions':[{'id':'a1:c1','severity':'HIGH','decision':'KEEP_WITH_REASON','reason':'Authenticated example gives appropriate case and unambiguous sense','evidence_sha256':H}], 'sample':{'method':'HASH_DETERMINISTIC_STRATIFIED','seed':H,'strata':[{'name':'L01','population':{'cards':1,'examples':1,'visible_combos':1},'reviewed':{x:[{'id':x,'decision':'KEEP_WITH_REASON','reason':'Independently checked source meaning','evidence_sha256':H}] for x in ('cards','examples','visible_combos')}}]},'adversarial':{'separate_method':True,'challenge_evidence_sha256':H,'seeded_negative_controls_passed':5,'systemic_error_clusters_resolved':True},'scope_is_exact_current':True}
class RiskGateTests(unittest.TestCase):
    def check(self,r,expected):self.assertEqual(evaluate(P,r)['status'],expected)
    def test_positive_synthetic_evidence(self):self.check(copy.deepcopy(E),'PASS_RISK_BASED_STAGE4')
    def test_missing_risk(self):
        d=copy.deepcopy(E);d['risk_dispositions']=[];self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_high_severity_hold(self):
        d=copy.deepcopy(E);d['risk_dispositions'][0]['decision']='HOLD';self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_no_blanket_low_risk_acceptance(self):
        d=copy.deepcopy(E);d['risk_dispositions'][0]['reason']='';self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_false_source_claim(self):
        d=copy.deepcopy(E);d['risk_dispositions'][0]['source_claim']='VERBATIM';self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_incomplete_sample(self):
        d=copy.deepcopy(E);d['sample']['strata'][0]['reviewed']['examples']=[];self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_no_adversarial(self):
        d=copy.deepcopy(E);d['adversarial']['separate_method']=False;self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_old_evidence_hash(self):
        d=copy.deepcopy(E);d['risk_dispositions'][0]['evidence_sha256']='c'*64;self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_tampered_working_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'x';p.write_bytes(b'tampered');self.check_with_bytes(copy.deepcopy(E),p)
    def check_with_bytes(self,d,p):self.assertEqual(evaluate(P,d,p)['status'],'BLOCKED_RISK_BASED_STAGE4')
    def test_stratum_missing_in_real_profile(self):
        d=copy.deepcopy(E);d['workstream']='menschen-a1-final-consolidation-v336';p=copy.deepcopy(P);p['profiles']={'menschen-a1-final-consolidation-v336':{'min_strata':24,'expected_strata':['L%02d'%i for i in range(1,25)]}};self.assertEqual(evaluate(p,d)['status'],'BLOCKED_RISK_BASED_STAGE4')
    def test_bounded_low_hold(self):
        d=copy.deepcopy(E);d['risk_dispositions'][0].update(severity='LOW',decision='HOLD',owner='editor',followup_trigger='New learner report');self.check(d,'PASS_RISK_BASED_STAGE4')
    def test_family_blanket_not_accepted(self):
        d=copy.deepcopy(E);d['risk_dispositions']=[];d['risk_scan']['flagged_items']=[{'id':'a1:c1','flags':['VERY_SHORT']}];d['risk_family_dispositions']=[{'rule_id':'short','affected_ids':['a1:c1'],'trigger_flags':['VERY_SHORT'],'severity':'LOW','reason':'too generic','evidence_sha256':H,'independent_challenge':False,'representative_reviews':[]}];self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_family_evidence_can_pass(self):
        d=copy.deepcopy(E);d['risk_dispositions']=[];d['risk_scan']['flagged_items']=[{'id':'a1:c1','flags':['VERY_SHORT']}];d['risk_family_dispositions']=[{'rule_id':'short','affected_ids':['a1:c1'],'trigger_flags':['VERY_SHORT'],'severity':'LOW','reason':'Locative phrase teaches case, independently checked','evidence_sha256':H,'independent_challenge':True,'representative_reviews':[{'id':'a1:c1','decision':'KEEP_WITH_REASON','reason':'specific case benefit','evidence_sha256':H}]}];self.check(d,'PASS_RISK_BASED_STAGE4')
    def test_family_unverified_trigger(self):
        d=copy.deepcopy(E);d['risk_dispositions']=[];d['risk_scan']['flagged_items']=[{'id':'a1:c1','flags':['VERY_SHORT']}];d['risk_family_dispositions']=[{'rule_id':'short','affected_ids':['a1:c1'],'trigger_flags':['IN_EXAMPLE_SPAN'],'severity':'LOW','reason':'No matching trigger','evidence_sha256':H,'independent_challenge':True,'representative_reviews':[{'id':'a1:c1','decision':'KEEP_WITH_REASON','reason':'specific case benefit','evidence_sha256':H}]}];self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_family_scan_high_not_masked(self):
        d=copy.deepcopy(E);d['risk_dispositions']=[];d['risk_scan']['flagged_items']=[{'id':'a1:c1','flags':['VERY_SHORT'],'severity':'HIGH'}];d['risk_family_dispositions']=[{'rule_id':'short','affected_ids':['a1:c1'],'trigger_flags':['VERY_SHORT'],'severity':'LOW','reason':'cannot relabel confirmed high','evidence_sha256':H,'independent_challenge':True,'representative_reviews':[{'id':'a1:c1','decision':'KEEP_WITH_REASON','reason':'checked','evidence_sha256':H}]}];self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_planned_sample_must_actually_be_reviewed(self):
        d=copy.deepcopy(E);d['sample']['strata'][0]['planned_ids']={'cards':['missing-card'],'examples':['examples'],'visible_combos':['visible_combos']};self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_no_critical_in_family(self):
        d=copy.deepcopy(E);d['risk_dispositions']=[];d['risk_scan']['flagged_items']=[{'id':'a1:c1','flags':['SOURCE_FAKE']}];d['risk_family_dispositions']=[{'rule_id':'source','affected_ids':['a1:c1'],'trigger_flags':['SOURCE_FAKE'],'severity':'HIGH','reason':'cannot group','evidence_sha256':H,'independent_challenge':True,'representative_reviews':[{'id':'a1:c1','decision':'KEEP_WITH_REASON','reason':'not checked','evidence_sha256':H}]}];self.check(d,'BLOCKED_RISK_BASED_STAGE4')
    def test_unmanaged_low_hold(self):
        d=copy.deepcopy(E);d['risk_dispositions'][0].update(severity='LOW',decision='HOLD');self.check(d,'BLOCKED_RISK_BASED_STAGE4')
if __name__=='__main__':unittest.main()