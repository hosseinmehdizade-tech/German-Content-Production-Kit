"""Real v1.1 scanner regression; safety tests, not automatic Stage4 approval."""
import csv,hashlib,importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCANNER=ROOT/"Verification/audit_kombinationen_lean_v1_1.py"
spec=importlib.util.spec_from_file_location("lean_didactic_scanner",SCANNER)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
ROW={"id":"demo","front":"sich engagieren","details":json.dumps([
    {"title":"Kombinationen","items":["sich engagieren —x",
        "jdn. finanziell unterstützen — y","jemanden finanziell unterstützen — z",
        "sich ehrenamtlich engagieren — a"]}]),
    "examples":json.dumps([{"lang":"de-DE","text":"Sie möchte sich ehrenamtlich engagieren."}])}

class LeanScannerRegression(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tsv=Path(self.tmp.name)/"rows.tsv"
        self.write([ROW])
    def write(self,rows):
        with self.tsv.open("w",encoding="utf-8",newline="") as out:
            writer=csv.DictWriter(out,fieldnames=list(ROW),delimiter="\t")
            writer.writeheader();writer.writerows(rows)
    def run_cli(self,*arguments):
        return subprocess.run([sys.executable,str(SCANNER),str(self.tsv),*arguments],
                              capture_output=True,text=True)
    def test_placeholder_normalized(self):
        self.assertEqual(mod.normal("jdn. unterstützen"),mod.normal("jemanden unterstützen"))
    def test_flags_are_advisory_and_detect_existing_repetition(self):
        report=mod.analyze_input(self.tsv)[0]
        self.assertIn("NORMALIZED_WITHIN_CARD_DUPLICATE",report["rule_counts"])
        self.assertTrue(all(x["disposition"]=="ADVISORY_UNDECIDED" for x in report["flags"]))
    def test_advisory_does_not_block_benign_signals(self):
        x=self.run_cli()
        self.assertEqual(x.returncode,0)
        self.assertIn("NOT_REQUESTED_NO_STAGE4_PASS",x.stdout)
    def test_gate_requires_official_stage4_receipt(self):
        self.assertEqual(self.run_cli("--gate").returncode,2)
    def test_legacy_decisions_cannot_substitute_stage4_receipt(self):
        self.assertEqual(self.run_cli("--gate","--decisions",str(self.tsv)).returncode,2)
    def test_fake_stage4_receipt_cannot_pass(self):
        bogus=Path(self.tmp.name)/"claim.json";bogus.write_text('{"status":"PASS_RISK_BASED_STAGE4"}')
        self.assertNotEqual(self.run_cli("--gate","--stage4-receipt",str(bogus)).returncode,0)
    def test_duplicate_card_ids_block(self):
        self.write([ROW,ROW]);self.assertEqual(self.run_cli().returncode,3)
    def test_empty_source_blocks(self):
        self.write([]);self.assertEqual(self.run_cli().returncode,3)
    def test_invalid_details_blocks(self):
        self.write([dict(ROW,details="{broken")]);self.assertEqual(self.run_cli().returncode,3)
    def test_duplicate_json_keys_blocks(self):
        self.write([dict(ROW,details='[{"title":"Kombinationen","items":[],"items":[]}]')])
        self.assertEqual(self.run_cli().returncode,3)
    def test_missing_combinations_is_not_forced_fill(self):
        self.write([dict(ROW,details="[]")])
        self.assertEqual(mod.analyze_input(self.tsv)[0]["items"],0)
        self.assertEqual(self.run_cli().returncode,0)
    def test_zero_combination_never_fakes_stage4(self):
        self.write([dict(ROW,details="[]")])
        self.assertEqual(self.run_cli("--gate").returncode,2)
    def test_output_is_pinned_to_input_bytes(self):
        file=Path(self.tmp.name)/"out.json"
        self.assertEqual(self.run_cli("--output",str(file)).returncode,0)
        self.assertEqual(json.loads(file.read_text())["input_sha256"],
                         hashlib.sha256(self.tsv.read_bytes()).hexdigest())
    def test_zip_advisory_and_gate_boundary(self):
        import zipfile
        path=Path(self.tmp.name)/"data.zip"
        with zipfile.ZipFile(path,"w") as archive:archive.write(self.tsv,"rows.tsv")
        cmd=[sys.executable,str(SCANNER),str(path),"--member","rows.tsv"]
        self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
        self.assertNotEqual(subprocess.run(cmd+["--gate","--stage4-receipt",str(self.tsv)],
                                            capture_output=True).returncode,0)

if __name__=="__main__":unittest.main()
