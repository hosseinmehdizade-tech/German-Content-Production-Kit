"""Nonactive OP-02 cross-domain read-only source and rollback probes."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"Verification"))
from audit_op02_cross_domain_shadow import evaluate,rollback_diagnostic,ALH,B1,READ

BASE="Workspaces/"
def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def grammar():
    source=read(BASE+ALH+"/00-source/SOURCE-MANIFEST.json")
    receipt=read(BASE+ALH+"/60-wip64-exact-lexicon/WIP64-CHECKPOINT.json")
    p={k:receipt[k] for k in
       ("size_bytes","library_file_id","library_path","canonical_sha256","import_sha256")}
    p.update(filename=receipt["zip"],sha256=receipt["zip_sha256"],stage4="OPEN")
    pkg={"name":p["filename"],"sha256":p["sha256"],"bytes":p["size_bytes"],
         "library_file_id":p["library_file_id"],"library_path":p["library_path"],
         "member_count":receipt["zip_members"],
         "parent_sha256":receipt["parent_sha256"],
         "stage4":"OPEN","stage5_6_7":"NOT_RUN"}
    latest={"schema":"gcpk-workstream-latest@1.0.0",
            "workstream":ALH,
            "latest_milestone":"WIP64_HISTORICAL_READONLY_TEST",
            "latest_receipt_path":BASE+ALH+"/60-wip64-exact-lexicon/WIP64-CHECKPOINT.json",
            "authority":{"current_portable":p},
            "complete_working_content_package":pkg,
            "previous_wip64_source_current":{
                "portable":{"sha256":receipt["parent_sha256"]}},
            "progress":{"rektion_independent_external_attested_cumulative":
                        receipt["cumulative_attested"],
                        "rektion_external_holds_remaining":receipt["remaining_holds"]}}
    checkpoint=read(BASE+ALH+"/CHECKPOINT.json")
    return ALH,source,checkpoint,latest,receipt

def lesson():
    return B1,read(BASE+"menschen-a1a2b1-memrise/00-source/SOURCE-MANIFEST.json"),read(
        BASE+B1+"/CHECKPOINT.json"),None,None

def reading():
    return READ,read(BASE+READ+"/00-source/SOURCE-MANIFEST.json"),read(
        BASE+READ+"/CHECKPOINT.json"),None,None

class DomainSmoke(unittest.TestCase):
    def check(self, maker, fn=None):
        args=copy.deepcopy(maker())
        if fn:fn(args)
        return evaluate(args[0],args[1],args[2],latest=args[3],receipt=args[4])

    def no_release(self,r):
        for k in ("source_binary_bytes_verified","portable_zip_bytes_verified",
                  "issuer_authenticated","stage4_semantic_accepted",
                  "stage5_7_accepted","production_schema_activated",
                  "writer_granted","performed_writes"):
            self.assertIs(r[k],False,k)

    def blocked(self,maker,fn,code):
        result=self.check(maker,fn)
        self.assertEqual(result["status"],"BLOCKED_SCOPED_METADATA",result)
        self.assertIn(code,result["errors"],result)
        self.no_release(result)

    def test_three_actual_format_positive_shadow_only(self):
        for maker in (grammar,lesson,reading):
            with self.subTest(maker=maker.__name__):
                r=self.check(maker)
                self.assertEqual(r["status"],"PASS_SCOPED_READONLY_METADATA_ONLY_NOT_RELEASE",r)
                self.no_release(r)

    def test_grammar_source_hash_tamper(self):
        self.blocked(grammar,lambda x:x[1]["source_set"][0].update(sha256="f"*64),
                     "GRAMMAR_ORIGINAL_SOURCE_PIN_DRIFT")

    def test_grammar_source_order_tamper(self):
        self.blocked(grammar,lambda x:x[1]["source_set"].reverse(),
                     "GRAMMAR_ORIGINAL_SOURCE_PIN_DRIFT")

    def test_grammar_role_zip_hash_tamper(self):
        self.blocked(grammar,lambda x:x[3]["authority"]["current_portable"].update(sha256="f"*64),
                     "GRAMMAR_THREE_ROLE_DRIFT:sha256")

    def test_grammar_role_library_path_tamper(self):
        self.blocked(grammar,lambda x:x[3]["complete_working_content_package"].update(
            library_path="/forged"),"GRAMMAR_THREE_ROLE_DRIFT:library_path")

    def test_grammar_parent_tamper(self):
        self.blocked(grammar,lambda x:x[3]["previous_wip64_source_current"]["portable"].update(
            sha256="f"*64),"GRAMMAR_PARENT_LINEAGE_DRIFT")

    def test_grammar_count_tamper(self):
        self.blocked(grammar,lambda x:x[4].update(remaining_holds=159),
                     "GRAMMAR_COUNTS_NOT_CONSERVED")

    def test_grammar_bool_as_int_tamper(self):
        self.blocked(grammar,lambda x:x[4].update(cumulative_attested=True),
                     "GRAMMAR_COUNTS_NOT_INTEGERS")

    def test_grammar_changed_ids_duplicate(self):
        self.blocked(grammar,lambda x:x[4]["changed_card_ids"].__setitem__(
            0,x[4]["changed_card_ids"][1]),"GRAMMAR_CHANGED_ID_LEDGER_INVALID")

    def test_grammar_changed_ids_omitted(self):
        self.blocked(grammar,lambda x:x[4].pop("changed_card_ids"),
                     "GRAMMAR_CHANGED_ID_LEDGER_INVALID")

    def test_grammar_stage4_false_claim(self):
        self.blocked(grammar,lambda x:x[4].update(full_stage4="PASS"),
                     "GRAMMAR_SCOPED_SOURCE_OR_STAGE_DRIFT")

    def test_grammar_stale_milestone(self):
        self.blocked(grammar,lambda x:x[3].update(latest_milestone="WIP63_OLD"),
                     "GRAMMAR_CURRENT_MILESTONE_INVALID")

    def test_lesson_archive_tamper(self):
        self.blocked(lesson,lambda x:x[1]["raw_archive"].update(sha256="f"*64),
                     "LESSON_MEMRISE_ARCHIVE_CSV_SOURCE_DRIFT")

    def test_lesson_csv_tamper(self):
        self.blocked(lesson,lambda x:x[1]["export_csv"].update(rows=9108),
                     "LESSON_MEMRISE_ARCHIVE_CSV_SOURCE_DRIFT")

    def test_lesson_cross_checkpoint_mismatch(self):
        self.blocked(lesson,lambda x:x[2]["source"].update(export_csv_sha256="f"*64),
                     "LESSON_SCOPE_AUDIO_AND_SOURCE_BRIDGE_DRIFT")

    def test_lesson_audio_missing_tamper(self):
        self.blocked(lesson,lambda x:x[2]["source"].update(b1_l01_missing_archive_audio=1),
                     "LESSON_SCOPE_AUDIO_AND_SOURCE_BRIDGE_DRIFT")

    def test_lesson_fake_grammar_current_attachment(self):
        self.blocked(lesson,lambda x:x.__setitem__(3,{"latest_milestone":"WIP64_FAKE"}),
                     "LESSON_FOREIGN_GRAMMAR_ROLES_FORBIDDEN")

    def test_reading_source_digest(self):
        self.blocked(reading,lambda x:x[1].update(sha256="f"*64),
                     "READING_PDF_TOPIC_INVENTORY_PIN_DRIFT")

    def test_reading_invented_topic_count(self):
        self.blocked(reading,lambda x:x[1]["inventory"].update(topics=69),
                     "READING_PDF_TOPIC_INVENTORY_PIN_DRIFT")

    def test_reading_source_checkpoint_split(self):
        self.blocked(reading,lambda x:x[2]["dataset"].update(
            authoritative_source="other file"),"READING_STAGE_STRUCTURE_DRIFT")

    def test_reading_fake_stage7_pass(self):
        self.blocked(reading,lambda x:x[2]["stages"][6].update(state="PASS"),
                     "READING_NO_FAKE_DOWNSTREAM_PASS")

    def test_reading_stage_order_changed(self):
        self.blocked(reading,lambda x:x[2]["stages"][1].update(stage=4),
                     "READING_STAGE_STRUCTURE_DRIFT")

    def test_reading_fake_zip_assignment(self):
        self.blocked(reading,lambda x:x.__setitem__(4,{"zip":"impossible"}),
                     "READING_NO_SYNTHETIC_PORTABLE_OR_RELEASE")

    def test_profile_substitution_between_domains(self):
        a=lesson()
        r=evaluate(READ,a[1],a[2])
        self.assertEqual(r["status"],"BLOCKED_SCOPED_METADATA")
        self.no_release(r)

    def test_unregistered_domain_blocks(self):
        r=evaluate("schreiben-unregistered",{}, {})
        self.assertEqual(r["errors"],["UNREGISTERED_DOMAIN_PROFILE"])
        self.no_release(r)

    def test_malformed_source_never_passes(self):
        for kind in (ALH,B1,READ):
            r=evaluate(kind,None,{})
            self.assertEqual(r["status"],"BLOCKED_SCOPED_METADATA")
            self.no_release(r)

    def test_rollback_no_owner_authority_blocks(self):
        a,b="a"*64,"b"*64
        r=rollback_diagnostic(a,b,b)
        self.assertIn("INDEPENDENT_ISSUER_AUTHORIZATION_MISSING",r["errors"])
        self.assertIs(r["safe_to_write"],False)

    def test_rollback_wrong_postimage_blocks(self):
        r=rollback_diagnostic("a"*64,"b"*64,"c"*64,issuer_authenticated=True)
        self.assertIn("CONCURRENT_HEAD_OR_POSTIMAGE_DRIFT",r["errors"])
        self.assertFalse(r["performed_writes"])

    def test_rollback_even_claimed_issuer_never_writes(self):
        r=rollback_diagnostic("a"*64,"b"*64,"b"*64,issuer_authenticated=True)
        self.assertEqual(r["status"],"BLOCKED_NO_ROLLBACK_WRITER")
        self.assertFalse(r["safe_to_write"])

    def test_rollback_force_request_never_writes(self):
        r=rollback_diagnostic("a"*64,"b"*64,"b"*64,mutation_requested=True)
        self.assertIn("MUTATION_FORBIDDEN_IN_NONACTIVE_DIAGNOSTIC",r["errors"])
        self.assertFalse(r["performed_writes"])

if __name__=="__main__":
    unittest.main()
