import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'Tools/refresh.py'
spec=importlib.util.spec_from_file_location('portfolio_refresh',SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class PortfolioRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'git';self.root.mkdir()
        self.out=Path(self.temp.name)/'out'
        for level,base in m.WORK.items():
            target=f'{base}/LATEST.json'
            if level=='A1':d={'latest_verified_milestone':'STAGE7_LOCKED','milestone_receipt':f'{base}/L24-RECEIPT.json','artifact':{'sha256':'a'*64}}
            elif level=='A2':d={'current_lesson':'A2-L20','current_stage':'Stage3C PASS Stage4 NEXT','receipt':f'{base}/L20-STAGE3C.json','artifact_sha256':'a'*64}
            else:d={'lesson':'B1-L19','latest_milestone':'Stage4 Repair3 BLOCKED','receipt':f'{base}/B1-L19-STAGE4-REPAIR3.json','artifact_sha256':'a'*64}
            self.write(target,d)
            self.write(d.get('receipt') or d.get('milestone_receipt'),{'release':{'sha256':'a'*64},'artifact':{'sha256':'a'*64}})
        self.write(f"{m.WORK['A1']}/AUDITS/LATEST-AUDIT.json",{'latest_read_only_audit_milestone':'M12','latest_receipt':f"{m.WORK['A1']}/AUDITS/M12.json",'latest_portable_sha256':'b'*64})
        self.write(f"{m.WORK['A1']}/AUDITS/M12.json",{'artifact':{'sha256':'b'*64}})
        self.write(f"{m.WORK['A2']}/CHECKPOINT.json",{'scope':'A2-L01..L18 Stage7, A2-L19 Stage3B'})
        for lvl,ids in m.BASELINE.items():
            for n in ids:self.write(m.stage7_path(lvl,n),{'status':'LOCKED','content_lock_state':'LOCKED','artifact':{'sha256':'c'*64}})
    def write(self,p,obj):
        f=self.root/p;f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(json.dumps(obj,sort_keys=True)+'\n','utf8')
    def test_all_72_lessons_and_60_locks(self):
        d=m.generate(self.root)
        self.assertEqual(d['counts']['total_lessons'],72)
        self.assertEqual(d['counts']['locked_total'],60)
        self.assertEqual([d['counts']['by_level'][x]['locked'] for x in ('A1','A2','B1')],[23,19,18])
    def test_a1_historical_not_promoted(self):
        d=m.generate(self.root);r=next(x for x in d['lessons'] if x['id']=='A1-L01')
        self.assertEqual(r['content_lock'],'HISTORICAL_V332_ONLY')
    def test_current_lesson_not_locked(self):
        d=m.generate(self.root)
        self.assertIn('Stage3C',next(x['stage'] for x in d['lessons'] if x['id']=='A2-L20'))
        self.assertEqual(next(x['content_lock'] for x in d['lessons'] if x['id']=='B1-L19'),'NOT_LOCKED')
    def test_a2_stale_checkpoint_detected(self):
        self.assertIn('A2_CENTRAL_CHECKPOINT_STALE',[w['code'] for w in m.generate(self.root)['warnings']])
    def test_missing_locked_ref_fails(self):
        (self.root/m.stage7_path('B1',8)).unlink()
        with self.assertRaisesRegex(ValueError,'PREVIOUS_LOCK_RECEIPT_MISSING'):m.generate(self.root)
    def test_revoked_lock_fails(self):
        self.write(m.stage7_path('A2',8),{'status':'NOT_LOCKED','content_lock_state':'NOT_LOCKED'})
        with self.assertRaisesRegex(ValueError,'PREVIOUS_LOCK_LOST'):m.generate(self.root)
    def test_locked_tamper_against_prior_fails(self):
        prev=m.generate(self.root)
        self.write(m.stage7_path('A1',3),{'status':'LOCKED','content_lock_state':'LOCKED','artifact':{'sha256':'e'*64}})
        with self.assertRaisesRegex(ValueError,'LOCKED_RECEIPT_EDIT_REQUIRES_EXPLICIT_SUCCESSOR'):m.generate(self.root,prev)
    def test_new_locked_accepted_without_retroactive_edit(self):
        prev=m.generate(self.root)
        self.write(m.stage7_path('A2',20),{'status':'LOCKED','content_lock_state':'LOCKED','artifact':{'sha256':'c'*64}})
        self.write(f"{m.WORK['A2']}/LATEST.json",{'current_lesson':'A2-L20','current_stage':'Stage7 LOCKED','receipt':f"{m.WORK['A2']}/L20-STAGE3C.json",'artifact_sha256':'a'*64})
        d=m.generate(self.root,prev);self.assertEqual(d['counts']['locked_total'],61)
    def test_premature_stage7_fails_closed(self):
        self.write(m.stage7_path('A2',20),{'status':'LOCKED','content_lock_state':'LOCKED','artifact':{'sha256':'c'*64}})
        with self.assertRaisesRegex(ValueError,'STAGE7_AHEAD_OF_WORKSTREAM_LATEST'):m.generate(self.root)
    def test_baseline_sha_detects_mutated_receipt_before_first_live(self):
        original=m.generate(self.root)
        p0=self.root/'Portfolio/Menschen/P0-BASELINE-EVIDENCE.json'
        baselines={}
        for level in ('A1','A2','B1'):
            baselines[level]=' '.join(f"{r['lesson_number']}:{r['evidence_git_blob_sha']}" for r in original['lessons'] if r['level']==level and r['content_lock']=='LOCKED')
        self.write('Portfolio/Menschen/P0-BASELINE-EVIDENCE.json',{'stage7_git_blob_sha':baselines})
        self.write(m.stage7_path('A1',2),{'status':'LOCKED','content_lock_state':'LOCKED','new_unapproved_field':True})
        with self.assertRaisesRegex(ValueError,'LOCKED_RECEIPT_EDIT_REQUIRES_EXPLICIT_SUCCESSOR'):m.generate(self.root)
    def test_receipt_missing_fails(self):
        (self.root/f"{m.WORK['B1']}/B1-L19-STAGE4-REPAIR3.json").unlink()
        with self.assertRaisesRegex(ValueError,'MISSING_AUTHORITY'):m.generate(self.root)
    def test_receipt_sha_mismatch_fails(self):
        self.write(f"{m.WORK['A2']}/L20-STAGE3C.json",{'artifact':{'sha256':'f'*64}})
        with self.assertRaisesRegex(ValueError,'LATEST_RECEIPT_ARTIFACT_CONFLICT'):m.generate(self.root)
    def test_audit_sha_mismatch_fails(self):
        self.write(f"{m.WORK['A1']}/AUDITS/M12.json",{'artifact':{'sha256':'f'*64}})
        with self.assertRaisesRegex(ValueError,'A1_AUDIT_POINTER_ARTIFACT_CONFLICT'):m.generate(self.root)
    def test_path_traversal_fails(self):
        with self.assertRaisesRegex(ValueError,'UNSAFE_EVIDENCE_PATH'):m.load(self.root,'../../private')
    def test_read_only_sources_and_render(self):
        before={f.relative_to(self.root):f.read_bytes() for f in self.root.rglob('*') if f.is_file()}
        d=m.generate(self.root)
        self.assertEqual(len(m.render_md(d).splitlines())>72,True)
        self.assertIn('application/json',m.render_html(d))
        after={f.relative_to(self.root):f.read_bytes() for f in self.root.rglob('*') if f.is_file()}
        self.assertEqual(before,after)
    def test_cli_idempotent_no_rewrites(self):
        cmd=[sys.executable,'-B',str(SCRIPT),'--repo-root',str(self.root),'--out',str(self.out)]
        subprocess.run(cmd,check=True,capture_output=True,text=True)
        pre=(self.out/'PORTFOLIO-STATUS.json').read_bytes()
        ret=subprocess.run(cmd,check=True,capture_output=True,text=True)
        self.assertIn('UNCHANGED_EVIDENCE',ret.stdout)
        self.assertEqual(pre,(self.out/'PORTFOLIO-STATUS.json').read_bytes())
    def test_cli_check_no_mutation(self):
        cmd=[sys.executable,'-B',str(SCRIPT),'--repo-root',str(self.root),'--out',str(self.out),'--check']
        subprocess.run(cmd,check=True,capture_output=True)
        self.assertFalse(self.out.exists())

if __name__=='__main__':unittest.main()
