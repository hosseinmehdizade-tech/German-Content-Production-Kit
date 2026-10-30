"""OP02 v2: exact historical source-snapshot-derived nonactive tests only."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"Verification"))
from audit_op02_typed_envelope_v2 import (
    evaluate, DOMAINS, SCHEMA, BOUNDARY, parse_strict)

BASE="Workspaces/"
GRAM="aber-hallo-listen-tabellen"
VOC="menschen-b1-24-lessons-v336"
READ="lesen-praesentation"
REFS={
    GRAM: ("latest","LATEST.json","d209c8f454f123deca252fc8056ff6fa892bb787"),
    VOC: ("checkpoint","CHECKPOINT.json","d848968ea7b6a5fb87fc47835caf94e6949f7b70"),
    READ:("checkpoint","CHECKPOINT.json","dbef4181425c12ee8f254673ada7f393c5edeba9"),
}

def file(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def make(workstream):
    cfg=DOMAINS[workstream]
    kind,name,blob=REFS[workstream]
    milestone={GRAM:"WIP65_SYNTHETIC_HISTORICAL_ONLY",
               VOC:"B1-L01-SOURCE-SNAPSHOT-ONLY",
               READ:"STAGE1-SOURCE-INVENTORY-ONLY"}[workstream]
    anchor={"kind":kind,"path":BASE+workstream+"/"+name,
            "blob_sha":blob,"milestone":milestone}
    sources=[{"source_id":i,"modality":m,"sha256":h}
             for i,m,h in cfg["sources"]]
    if workstream==GRAM:
        rec=file(BASE+GRAM+"/61-wip65-exact-lexicon/WIP65-CHECKPOINT.json")
        payload={
            "wip":65,"zip_sha256":rec["zip_sha256"],
            "parent_sha256":rec["parent_sha256"],
            "size_bytes":rec["size_bytes"],"zip_members":rec["zip_members"],
            "attested":rec["cumulative_attested"],"holds":rec["remaining_holds"],
            "governed_patterns":rec["governed_patterns"],"units":rec["units"],
            "lexical_cards":rec["lexical_cards"],
            "changed_cards":rec["changed_cards"],
            "changed_card_ids":rec["changed_card_ids"],
        }
    elif workstream==VOC:
        manifest=file(BASE+"menschen-a1a2b1-memrise/00-source/SOURCE-MANIFEST.json")
        ck=file(BASE+VOC+"/CHECKPOINT.json")
        src=ck["source"]
        payload={"csv_rows":manifest["export_csv"]["rows"],
                 "lessons":ck["scope"]["lessons"],"lesson_id":"B1-L01",
                 "lesson_rows":src["b1_l01_source_rows"],
                 "audio_refs":src["b1_l01_audio_refs"],
                 "unique_audio_refs":src["b1_l01_unique_audio_refs"],
                 "missing_audio":src["b1_l01_missing_archive_audio"]}
    else:
        manifest=file(BASE+READ+"/00-source/SOURCE-MANIFEST.json")
        ck=file(BASE+READ+"/CHECKPOINT.json")
        payload={"source_pages":manifest["inventory"]["pdf_pages"],
                 "topics":manifest["inventory"]["topics"],
                 "stages":[s["state"] for s in ck["stages"]]}
    envelope={"schema":SCHEMA,"workstream":workstream,"domain":cfg["domain"],
              "contract":cfg["contract"],"anchor":anchor,
              "sources":sources,"payload":payload,"gates":dict(BOUNDARY)}
    observed={"anchor":copy.deepcopy(anchor),"sources":copy.deepcopy(sources),
              "payload":copy.deepcopy(payload)}
    return envelope,observed

class EnvelopeV2(unittest.TestCase):
    def no_release(self,r):
        for k in ("independent_anchor_authenticated","issuer_authenticated",
                  "source_bytes_verified","portable_zip_bytes_verified",
                  "stage4_semantic_pass","stage5_allowed","stage6_pass",
                  "stage7_final","production_migration_authorized",
                  "writer_granted","performed_writes"):
            self.assertIs(r[k],False,k)

    def check(self,workstream,mutate=None):
        e,o=copy.deepcopy(make(workstream))
        if mutate:
            mutate(e,o)
        return evaluate(e,o)

    def block(self,workstream,mutate,code):
        x=self.check(workstream,mutate)
        self.assertEqual(x["status"],"BLOCKED_NONACTIVE_METADATA",x)
        self.assertIn(code,x["errors"],x)
        self.no_release(x)

    def test_three_types_scoped_pass_no_authority(self):
        for name in (GRAM,VOC,READ):
            with self.subTest(name=name):
                x=self.check(name)
                self.assertEqual(x["status"],
                    "PASS_NONACTIVE_TYPED_METADATA_ONLY_NOT_RELEASE",x)
                self.no_release(x)

    def test_grammar_future_wip66_same_schema(self):
        def change(e,o):
            e["anchor"]["milestone"]="WIP66_SYNTHETIC"
            o["anchor"]["milestone"]="WIP66_SYNTHETIC"
            e["payload"]["wip"]=o["payload"]["wip"]=66
            e["payload"]["parent_sha256"]=o["payload"]["parent_sha256"]=e["payload"]["zip_sha256"]
            e["payload"]["zip_sha256"]=o["payload"]["zip_sha256"]="a"*64
        x=self.check(GRAM,change)
        self.assertEqual(x["status"],
            "PASS_NONACTIVE_TYPED_METADATA_ONLY_NOT_RELEASE",x)
        self.no_release(x)

    def test_unknown_schema_blocks(self):
        self.block(GRAM,lambda e,o:e.update(schema="auto-migrate"),
                   "ENVELOPE_SCHEMA_OR_DOMAIN_INVALID")

    def test_unknown_domain_blocks(self):
        self.block(GRAM,lambda e,o:e.update(domain="writing"),
                   "ENVELOPE_SCHEMA_OR_DOMAIN_INVALID")

    def test_unknown_workstream_blocks(self):
        x=evaluate({"workstream":"unregistered","domain":"grammar"}, {})
        self.assertEqual(x["errors"],["UNREGISTERED_WORKSTREAM"])
        self.no_release(x)

    def test_swapped_contract_blocks(self):
        self.block(VOC,lambda e,o:e.update(contract=DOMAINS[GRAM]["contract"]),
                   "ENVELOPE_SCHEMA_OR_DOMAIN_INVALID")

    def test_extra_envelope_key_blocks(self):
        self.block(READ,lambda e,o:e.update(release_approved=True),
                   "ENVELOPE_SCHEMA_OR_DOMAIN_INVALID")

    def test_missing_envelope_key_blocks(self):
        self.block(GRAM,lambda e,o:e.pop("sources"),
                   "ENVELOPE_SCHEMA_OR_DOMAIN_INVALID")

    def test_wrong_anchor_blob_blocks(self):
        self.block(GRAM,lambda e,o:e["anchor"].update(blob_sha="f"*40),
                   "ANCHOR_MISMATCH_OR_UNPINNED")

    def test_fake_head_and_self_attested_anchor_still_no_authentication(self):
        def mutate(e,o):
            e["anchor"]["blob_sha"]=o["anchor"]["blob_sha"]="f"*40
        x=self.check(GRAM,mutate)
        self.assertEqual(x["status"],
            "PASS_NONACTIVE_TYPED_METADATA_ONLY_NOT_RELEASE",x)
        self.no_release(x)

    def test_anchor_path_traversal_blocks(self):
        self.block(VOC,lambda e,o:e["anchor"].update(path="../CHECKPOINT.json"),
                   "ANCHOR_MISMATCH_OR_UNPINNED")

    def test_anchor_workstream_path_swap_blocks(self):
        self.block(READ,lambda e,o:e["anchor"].update(path=BASE+GRAM+"/LATEST.json"),
                   "ANCHOR_MISMATCH_OR_UNPINNED")

    def test_anchor_unknown_key_blocks(self):
        self.block(READ,lambda e,o:e["anchor"].update(issuer="yes"),
                   "ANCHOR_SHAPE_INVALID")

    def test_missing_observed_anchor_blocks(self):
        self.block(GRAM,lambda e,o:o.pop("anchor"),"ANCHOR_SHAPE_INVALID")

    def test_grammar_wip_forgery_blocks(self):
        self.block(GRAM,lambda e,o:e["payload"].update(wip=64),
                   "DOMAIN_PAYLOAD_NOT_BOUND_TO_OBSERVED")

    def test_grammar_wip_anchor_mismatch_with_coordinated_payload(self):
        def mutate(e,o):
            e["payload"]["wip"]=o["payload"]["wip"]=64
        self.block(GRAM,mutate,"GRAMMAR_WIP_ANCHOR_VERSION_DRIFT")

    def test_source_order_swap_blocks(self):
        self.block(GRAM,lambda e,o:e["sources"].reverse(),
                   "TYPED_SOURCE_ID_MODALITY_OR_ORDER_DRIFT")

    def test_source_modality_mismatch_blocks(self):
        self.block(VOC,lambda e,o:e["sources"][0].update(modality="pdf"),
                   "TYPED_SOURCE_ID_MODALITY_OR_ORDER_DRIFT")

    def test_source_hash_mismatch_blocks(self):
        self.block(READ,lambda e,o:e["sources"][0].update(sha256="f"*64),
                   "TYPED_SOURCE_ID_MODALITY_OR_ORDER_DRIFT")

    def test_observed_source_swap_blocks(self):
        self.block(READ,lambda e,o:o["sources"][0].update(sha256="f"*64),
                   "OBSERVED_SOURCE_IDENTITY_DRIFT")

    def test_coordinated_source_forgery_still_detected_by_code_profile(self):
        def mutate(e,o):
            e["sources"][0]["sha256"]=o["sources"][0]["sha256"]="f"*64
        self.block(GRAM,mutate,"TYPED_SOURCE_ID_MODALITY_OR_ORDER_DRIFT")

    def test_missing_source_list_blocks(self):
        self.block(GRAM,lambda e,o:e.update(sources=None),
                   "TYPED_SOURCE_ID_MODALITY_OR_ORDER_DRIFT")

    def test_foreign_grammar_payload_blocks_vocabulary(self):
        def mutate(e,o):
            e["payload"]=make(GRAM)[0]["payload"]
        self.block(VOC,mutate,"DOMAIN_PAYLOAD_SHAPE_INVALID")

    def test_unknown_payload_field_blocks(self):
        self.block(READ,lambda e,o:e["payload"].update(final_zip="forged"),
                   "DOMAIN_PAYLOAD_SHAPE_INVALID")

    def test_removed_payload_field_blocks(self):
        self.block(GRAM,lambda e,o:e["payload"].pop("changed_cards"),
                   "DOMAIN_PAYLOAD_SHAPE_INVALID")

    def test_payload_not_bound_to_observed_blocks(self):
        self.block(GRAM,lambda e,o:e["payload"].update(attested=847),
                   "DOMAIN_PAYLOAD_NOT_BOUND_TO_OBSERVED")

    def test_changed_card_duplicate_even_coordinated_blocks(self):
        def mutate(e,o):
            ids=e["payload"]["changed_card_ids"]
            ids[0]=ids[1]
            o["payload"]["changed_card_ids"]=copy.deepcopy(ids)
        self.block(GRAM,mutate,"GRAMMAR_PATTERN_LINEAGE_OR_LEDGER_INVALID")

    def test_changed_card_count_inflation_blocks(self):
        def mutate(e,o):
            e["payload"]["changed_cards"]=o["payload"]["changed_cards"]=99
        self.block(GRAM,mutate,"GRAMMAR_PATTERN_LINEAGE_OR_LEDGER_INVALID")

    def test_grammar_pattern_conservation_blocks(self):
        def mutate(e,o):
            e["payload"]["holds"]=o["payload"]["holds"]=135
        self.block(GRAM,mutate,"GRAMMAR_PATTERN_LINEAGE_OR_LEDGER_INVALID")

    def test_grammar_bool_counts_blocks(self):
        def mutate(e,o):
            e["payload"]["units"]=o["payload"]["units"]=True
        self.block(GRAM,mutate,"GRAMMAR_PATTERN_LINEAGE_OR_LEDGER_INVALID")

    def test_grammar_bad_parent_blocks(self):
        def mutate(e,o):
            e["payload"]["parent_sha256"]=o["payload"]["parent_sha256"]=e["payload"]["zip_sha256"]
        self.block(GRAM,mutate,"GRAMMAR_PATTERN_LINEAGE_OR_LEDGER_INVALID")

    def test_grammar_bad_zip_sha_blocks(self):
        def mutate(e,o):
            e["payload"]["zip_sha256"]=o["payload"]["zip_sha256"]="z"*64
        self.block(GRAM,mutate,"GRAMMAR_PATTERN_LINEAGE_OR_LEDGER_INVALID")

    def test_grammar_member_bool_blocks(self):
        def mutate(e,o):
            e["payload"]["zip_members"]=o["payload"]["zip_members"]=True
        self.block(GRAM,mutate,"GRAMMAR_PATTERN_LINEAGE_OR_LEDGER_INVALID")

    def test_vocabulary_wrong_rows_blocks(self):
        def mutate(e,o):
            e["payload"]["csv_rows"]=o["payload"]["csv_rows"]=9000
        self.block(VOC,mutate,"VOCABULARY_CSV_LESSON_AUDIO_COUNTS_INVALID")

    def test_vocabulary_wrong_audio_blocks(self):
        def mutate(e,o):
            e["payload"]["missing_audio"]=o["payload"]["missing_audio"]=1
        self.block(VOC,mutate,"VOCABULARY_CSV_LESSON_AUDIO_COUNTS_INVALID")

    def test_vocabulary_wrong_lesson_blocks(self):
        def mutate(e,o):
            e["payload"]["lesson_id"]=o["payload"]["lesson_id"]="B1-L24"
        self.block(VOC,mutate,"VOCABULARY_CSV_LESSON_AUDIO_COUNTS_INVALID")

    def test_vocabulary_boolean_audio_count_blocks(self):
        def mutate(e,o):
            e["payload"]["audio_refs"]=o["payload"]["audio_refs"]=True
        self.block(VOC,mutate,"VOCABULARY_CSV_LESSON_AUDIO_COUNTS_INVALID")

    def test_reading_invented_topics_blocks(self):
        def mutate(e,o):
            e["payload"]["topics"]=o["payload"]["topics"]=69
        self.block(READ,mutate,"READING_STAGE1_ONLY_INVENTORY_INVALID")

    def test_reading_false_stage7_blocks(self):
        def mutate(e,o):
            e["payload"]["stages"][-1]=o["payload"]["stages"][-1]="PASS"
        self.block(READ,mutate,"READING_STAGE1_ONLY_INVENTORY_INVALID")

    def test_reading_premature_stage2_blocks(self):
        def mutate(e,o):
            e["payload"]["stages"][1]=o["payload"]["stages"][1]="PASS"
        self.block(READ,mutate,"READING_STAGE1_ONLY_INVENTORY_INVALID")

    def test_reading_no_fabricated_zip_role(self):
        self.block(READ,lambda e,o:e["payload"].update(zip_sha256="f"*64),
                   "DOMAIN_PAYLOAD_SHAPE_INVALID")

    def test_forged_stage4_acceptance_blocks(self):
        self.block(GRAM,lambda e,o:e["gates"].update(stage4="PASS"),
                   "NONACTIVE_RELEASE_BOUNDARY_VIOLATION")

    def test_forged_issuer_acceptance_blocks(self):
        self.block(VOC,lambda e,o:e["gates"].update(issuer="TRUSTED"),
                   "NONACTIVE_RELEASE_BOUNDARY_VIOLATION")

    def test_forged_stage7_release_blocks(self):
        self.block(READ,lambda e,o:e["gates"].update(release="FINAL"),
                   "NONACTIVE_RELEASE_BOUNDARY_VIOLATION")

    def test_extra_gate_blocks(self):
        self.block(GRAM,lambda e,o:e["gates"].update(write=True),
                   "NONACTIVE_RELEASE_BOUNDARY_VIOLATION")

    def test_duplicate_json_key_blocks_before_audit(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_JSON_KEY"):
            parse_strict(b'{"schema":"first","schema":"second"}')

    def test_nan_blocks_before_audit(self):
        with self.assertRaisesRegex(ValueError,"NONFINITE_JSON"):
            parse_strict(b'{"count":NaN}')

    def test_malformed_document_blocks(self):
        for a,b in ((None,{}),({},[]),({},{})):
            x=evaluate(a,b)
            self.assertEqual(x["status"],"BLOCKED_NONACTIVE_METADATA")
            self.no_release(x)

if __name__=="__main__":
    unittest.main()
