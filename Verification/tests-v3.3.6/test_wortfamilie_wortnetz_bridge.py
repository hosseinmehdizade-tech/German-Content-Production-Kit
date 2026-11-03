"""Verified Wortfamilie -> canonical WORD_FAMILY -> standard v411 Wortnetz projection."""
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

bridge = load("Tools/bridge_verified_wortfamilie_to_wortnetz.py", "wf_bridge")
projector = load("Tools/project_v411_vocabulary_cards.py", "v411_projector")

CANON = {"lexemes": [
    {"lexeme_id":"lx-f","lemma":"fahren","pos":"verb","morphology":{}},
    {"lexeme_id":"lx-r","lemma":"Fahrt","pos":"noun","morphology":{}},
    {"lexeme_id":"lx-d","lemma":"der Fahrer","pos":"noun","morphology":{}},
    {"lexeme_id":"lx-w","lemma":"reisen","pos":"verb","morphology":{}}],
    "senses":[
    {"sense_id":"s-f","lexeme_id":"lx-f","translations":{"fa":"رفتن با وسیله","en":"drive"}},
    {"sense_id":"s-r","lexeme_id":"lx-r","translations":{"fa":"سفر","en":"journey"}},
    {"sense_id":"s-d","lexeme_id":"lx-d","translations":{"fa":"راننده","en":"driver"}},
    {"sense_id":"s-w","lexeme_id":"lx-w","translations":{"fa":"سفر کردن","en":"travel"}}],
    "expressions":[], "relations":[],
    "sources":[{"source_id":"dict-verified","title":"Reference source"}]}

EVIDENCE={"source_refs":[{"source_id":"dict-verified","locator":"entry/fahren-Fahrt"}],
          "method":"verified_stage3_derivational_review"}

def packed(o):
    return (json.dumps(o, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")

def ledger_for(canon, members=None, decision="VERIFIED_PRESENT"):
    return {"schema":"gcpk-stage3-onepass@1.0",
            "working_sha256":bridge.digest(packed(canon)),
            "registered_source_sha256":"a"*64,
            "cards":[{"id":"s-f","decisions":{"word_family":{
                "decision":decision,
                "members":members if members is not None else [
                    {"de":"die Fahrt","target_id":"s-r","provenance":copy.deepcopy(EVIDENCE)}]}}}]}

class TestVerifiedWortfamilieWortnetzBridge(unittest.TestCase):
    def run_bridge(self, canon=None, ledger=None):
        canon = copy.deepcopy(canon if canon is not None else CANON)
        ledger = copy.deepcopy(ledger if ledger is not None else ledger_for(canon))
        return bridge.apply_bridge(canon, ledger, packed(canon))

    def test_verified_entry_creates_one_canonical_relation(self):
        updated, report = self.run_bridge()
        self.assertEqual(report["counts"]["edges_added"], 1)
        relation=updated["relations"][0]
        self.assertEqual(relation["relation_type"], "WORD_FAMILY")
        self.assertEqual((relation["source_id"],relation["target_id"]),("s-f","s-r"))
        self.assertEqual(relation["source_type"], "sense")
        self.assertEqual(relation["target_type"], "sense")
        self.assertEqual(relation["value"]["meaning"], "سفر")

    def test_normal_v411_projection_exposes_link_in_wortnetz(self):
        updated,_=self.run_bridge()
        cards=projector.project(updated)
        source=next(c for c in cards if c["id"]=="s-f")
        group=next(g for g in source["customFields"]["vnext_relations"]
                   if g["type"]=="WORD_FAMILY")
        self.assertEqual(group["label"],"Wortfamilie")
        self.assertEqual(group["items"][0]["target_id"],"s-r")

    def test_no_fabricated_reverse_canonical_relation(self):
        updated,_=self.run_bridge()
        self.assertEqual(len(updated["relations"]),1)
        self.assertFalse(any(r["source_id"]=="s-r" for r in updated["relations"]))

    def test_registry_original_is_not_mutated(self):
        original=copy.deepcopy(CANON)
        self.run_bridge(CANON)
        self.assertEqual(CANON,original)

    def test_exact_accepted_link_idempotent(self):
        updated,_=self.run_bridge()
        again,report=self.run_bridge(updated,ledger_for(updated))
        self.assertEqual(len(again["relations"]),1)
        self.assertEqual(report["counts"]["existing_edges_reused"],1)

    def test_deterministic_relation_id(self):
        a,_=self.run_bridge()
        b,_=self.run_bridge()
        self.assertEqual(a["relations"][0]["relation_id"],
                         b["relations"][0]["relation_id"])

    def test_unresolved_member_does_not_link(self):
        family=[{"de":"die Fahrt","target_id":"unknown","provenance":EVIDENCE}]
        updated, report=self.run_bridge(ledger=ledger_for(CANON,family))
        self.assertEqual(updated["relations"],[])
        self.assertEqual(report["counts"]["unresolved_target"],1)

    def test_no_fuzzy_word_to_target_fallback(self):
        family=[{"de":"die Fahrt","provenance":EVIDENCE}]
        updated,_=self.run_bridge(ledger=ledger_for(CANON,family))
        self.assertEqual(updated["relations"],[])

    def test_german_surface_mismatch_blocks_wrong_target(self):
        family=[{"de":"der Fahrer","target_id":"s-r","provenance":EVIDENCE}]
        updated,report=self.run_bridge(ledger=ledger_for(CANON,family))
        self.assertEqual(updated["relations"],[])
        self.assertEqual(report["counts"]["unmatched_german_target"],1)

    def test_homonym_evidence_does_not_self_link(self):
        family=[{"de":"fahren","target_id":"s-f","provenance":EVIDENCE}]
        updated,report=self.run_bridge(ledger=ledger_for(CANON,family))
        self.assertEqual(updated["relations"],[])
        self.assertEqual(report["counts"]["self_link_rejected"],1)

    def test_missing_provenance_keeps_text_only(self):
        family=[{"de":"die Fahrt","target_id":"s-r"}]
        updated,report=self.run_bridge(ledger=ledger_for(CANON,family))
        self.assertEqual(updated["relations"],[])
        self.assertEqual(report["counts"]["no_registered_evidence"],1)

    def test_unregistered_reference_does_not_create_false_claim(self):
        family=[{"de":"die Fahrt","target_id":"s-r",
                 "provenance":{"source_refs":[{"source_id":"invented","locator":"X"}]}}]
        updated,report=self.run_bridge(ledger=ledger_for(CANON,family))
        self.assertEqual(updated["relations"],[])
        self.assertEqual(report["counts"]["no_registered_evidence"],1)

    def test_hold_is_not_promoted(self):
        updated,report=self.run_bridge(ledger=ledger_for(CANON,decision="HOLD"))
        self.assertEqual(updated["relations"],[])
        self.assertEqual(report["counts"]["nonverified_family_decisions"],1)

    def test_not_applicable_is_not_promoted(self):
        updated,report=self.run_bridge(ledger=ledger_for(CANON,decision="NOT_APPLICABLE"))
        self.assertEqual(updated["relations"],[])
        self.assertEqual(report["counts"]["nonverified_family_decisions"],1)

    def test_member_individually_rejected_is_not_promoted(self):
        family=[{"de":"die Fahrt","target_id":"s-r","provenance":EVIDENCE,
                 "decision":"HOLD"}]
        updated,report=self.run_bridge(ledger=ledger_for(CANON,family))
        self.assertEqual(updated["relations"],[])
        self.assertEqual(report["counts"]["unreviewed_member"],1)

    def test_duplicate_member_not_duplicate_edge(self):
        m={"de":"die Fahrt","target_id":"s-r","provenance":EVIDENCE}
        updated,report=self.run_bridge(ledger=ledger_for(CANON,[m,m]))
        self.assertEqual(len(updated["relations"]),1)
        self.assertEqual(report["counts"]["existing_edges_reused"],1)

    def test_known_non_word_family_edge_unchanged(self):
        canon=copy.deepcopy(CANON)
        canon["relations"]=[{"relation_id":"prior","relation_type":"SYNONYM",
                             "source_id":"s-f","target_id":"s-w","provenance":{}}]
        updated,_=self.run_bridge(canon,ledger_for(canon))
        self.assertEqual(updated["relations"][0],canon["relations"][0])
        self.assertEqual(len(updated["relations"]),2)

    def test_source_pin_drift_fails(self):
        ledger=ledger_for(CANON)
        canon=copy.deepcopy(CANON)
        canon["relations"].append({"relation_id":"new","relation_type":"RELATED"})
        with self.assertRaisesRegex(ValueError,"SHA_MISMATCH"):
            bridge.apply_bridge(canon,ledger,packed(canon))

    def test_unregistered_card_blocks(self):
        ledger=ledger_for(CANON)
        ledger["cards"][0]["id"]="nonexistent"
        with self.assertRaisesRegex(ValueError,"SOURCE_NOT_IN_CANONICAL"):
            bridge.apply_bridge(CANON,ledger,packed(CANON))

    def test_duplicate_review_card_blocks(self):
        ledger=ledger_for(CANON)
        ledger["cards"].append(copy.deepcopy(ledger["cards"][0]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_STAGE3_CARD"):
            bridge.apply_bridge(CANON,ledger,packed(CANON))

    def test_duplicate_registry_relation_id_blocks(self):
        canon=copy.deepcopy(CANON)
        canon["relations"]=[{"relation_id":"same"},{"relation_id":"same"}]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_RELATION_ID"):
            self.run_bridge(canon,ledger_for(canon))

    def test_invalid_stage3_schema_blocks(self):
        ledger=ledger_for(CANON)
        ledger["schema"]="unknown"
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_STAGE3_LEDGER"):
            bridge.apply_bridge(CANON,ledger,packed(CANON))

    def test_bad_source_authority_pin_blocks(self):
        ledger=ledger_for(CANON)
        ledger["registered_source_sha256"]="fake"
        with self.assertRaisesRegex(ValueError,"SOURCE_AUTHORITY_NOT_PINNED"):
            bridge.apply_bridge(CANON,ledger,packed(CANON))

    def test_only_dry_run_is_default_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            canonical=p/"registry.json"; ledger=p/"ledger.json"
            canonical.write_bytes(packed(CANON))
            ledger.write_bytes(packed(ledger_for(CANON)))
            cmd=[sys.executable,str(ROOT/"Tools/bridge_verified_wortfamilie_to_wortnetz.py"),
                 "--canonical",str(canonical),"--onepass",str(ledger),
                 "--expected-sha256",bridge.digest(packed(CANON))]
            result=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse((p/"successor.json").exists())
            self.assertEqual(json.loads(result.stdout)["counts"]["edges_added"],1)
            successor=p/"successor.json"
            result=subprocess.run(cmd+["--output",str(successor),"--apply"],
                                  capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(successor.read_text())["relations"][0]["target_id"],"s-r")
            self.assertEqual(canonical.read_bytes(),packed(CANON))
            repeat=subprocess.run(cmd+["--output",str(successor),"--apply"],
                                  capture_output=True,text=True)
            self.assertEqual(repeat.returncode,3)

if __name__=="__main__":
    unittest.main()
