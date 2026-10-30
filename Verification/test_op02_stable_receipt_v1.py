"""OP-02 nonactive *proposed* stable schema; never changes CURRENT or release."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Verification"))
from audit_op02_stable_receipt_v1 import evaluate, parse_strict, SCHEMA

BASE = "Workspaces/aber-hallo-listen-tabellen/"
SOURCE = BASE + "00-source/SOURCE-MANIFEST.json"
LEGACY = BASE + "59-wip63-exact-lexicon/WIP63-CHECKPOINT.json"
PROFILE = ("Optimization-Program/Verification/"
           "OP02-ABER-HALLO-TYPED-RECEIPT-PROFILE-v1.json")


def fixture():
    """Frozen real WIP63 legacy receipt -> explicitly synthetic typed candidate.

    Conversion is TEST-ONLY and not part of the production tool. A legacy
    receipt can never be automatically treated as the proposed stable schema.
    """
    old = json.loads((ROOT / LEGACY).read_text(encoding="utf-8"))
    source = json.loads((ROOT / SOURCE).read_text(encoding="utf-8"))
    profile = json.loads((ROOT / PROFILE).read_text(encoding="utf-8"))
    portable = {key: old[key] for key in
                ("size_bytes", "library_file_id", "library_path",
                 "canonical_sha256", "import_sha256")}
    portable.update(filename=old["zip"], sha256=old["zip_sha256"])
    typed = {
        "schema": SCHEMA,
        "workstream": "aber-hallo-listen-tabellen",
        "milestone": "WIP63_SYNTHETIC_TEST_ONLY",
        "receipt_path": LEGACY,
        "status": "PASS_SCOPED_STAGE4_OPEN",
        "portable": portable,
        "parent_sha256": old["parent_sha256"],
        "source_sha256": old["source_sha256"],
        "counts": {
            "learning_units": old["units"],
            "import_cards": old["lexical_cards"],
            "attested": old["cumulative_attested"],
            "holds": old["remaining_holds"],
            "governed_patterns": old["governed_patterns"],
            "new_attested": old["new_attested"],
            "changed_cards": old["changed_cards"],
            "changed_card_ids": old["changed_card_ids"],
        },
        "zip_members": old["zip_members"],
        "gates": {
            "stage4": "OPEN", "stage5_7": "NOT_RUN",
            "import_parity": "PASS_SCOPED_CANONICAL_IMPORT_CLAIM",
        },
    }
    latest = {
        "schema": "gcpk-workstream-latest@1.0.0",
        "workstream": "aber-hallo-listen-tabellen",
        "latest_milestone": typed["milestone"],
        "latest_receipt_path": LEGACY,
        "latest_receipt_commit_sha": "a"*40,
        "authority": {"current_portable": {**portable, "stage4": "OPEN"}},
        "complete_working_content_package": {
            "name": portable["filename"], "sha256": portable["sha256"],
            "bytes": portable["size_bytes"],
            "library_file_id": portable["library_file_id"],
            "library_path": portable["library_path"],
            "member_count": old["zip_members"],
            "parent_sha256": old["parent_sha256"],
            "stage4": "OPEN", "stage5_6_7": "NOT_RUN",
        },
        "previous_wip63_source_current": {
            "portable": {"sha256": old["parent_sha256"]}},
        "progress": {
            "rektion_independent_external_attested_cumulative": old["cumulative_attested"],
            "rektion_external_holds_remaining": old["remaining_holds"],
            "pending_independent_expert_stage4": True,
            "independent_expert_unreviewed_units": old["units"],
        },
    }
    return latest, typed, source, profile


class StableReceipt(unittest.TestCase):
    def result(self, mutate=None, fixture_maker=fixture):
        args = copy.deepcopy(fixture_maker())
        if mutate:
            mutate(*args)
        return evaluate(*args)

    def blocked(self, mutate, code):
        r = self.result(mutate)
        self.assertEqual(r["status"], "BLOCKED_NONACTIVE_METADATA", r)
        self.assertIn(code, r["errors"], r)
        self.no_release(r)

    def no_release(self, r):
        for key in ("trusted_issuer", "source_pdf_bytes_verified",
                    "zip_bytes_verified", "stage4_semantic_pass",
                    "stage5_allowed", "stage6_accepted", "stage7_final",
                    "writer_granted", "performed_writes"):
            self.assertIs(r[key], False, key)

    def test_wip63_synthetic_typed_candidate_scoped_positive(self):
        result = self.result()
        self.assertEqual(result["status"],
                         "PASS_NONACTIVE_TYPED_METADATA_ONLY_NOT_RELEASE", result)
        self.no_release(result)

    def test_newer_wip64_same_typed_schema_needs_no_code_change(self):
        def advance(latest, receipt, source, profile):
            latest["latest_milestone"] = "WIP64_SYNTHETIC_TEST_ONLY"
            receipt["milestone"] = latest["latest_milestone"]
            latest["latest_receipt_path"] = BASE + "60-wip64/WIP64-CHECKPOINT.json"
            receipt["receipt_path"] = latest["latest_receipt_path"]
            latest["previous_wip64_source_current"] = {
                "portable": {"sha256": receipt["parent_sha256"]}}
            name = receipt["portable"]["filename"].replace("WIP63-", "WIP64-")
            receipt["portable"]["filename"] = name
            receipt["portable"]["library_path"] = "/synthetic/" + name
            latest["authority"]["current_portable"].update(
                filename=name, library_path="/synthetic/" + name)
            latest["complete_working_content_package"].update(
                name=name, library_path="/synthetic/" + name)
        result = self.result(advance)
        self.assertEqual(result["status"],
                         "PASS_NONACTIVE_TYPED_METADATA_ONLY_NOT_RELEASE", result)
        self.no_release(result)

    def test_real_legacy_wip63_receipt_never_auto_adopts_stable(self):
        def legacy(latest, receipt, source, profile):
            receipt.clear()
            receipt.update(json.loads((ROOT / LEGACY).read_text()))
        self.blocked(legacy, "TYPED_SCHEMA_OR_FIELDS_INVALID")

    def test_unknown_version_schema_blocks(self):
        self.blocked(lambda l,r,s,p: r.update(schema="typed-receipt@2"),
                     "TYPED_SCHEMA_OR_FIELDS_INVALID")

    def test_extra_unrecognized_top_level_field_blocks(self):
        self.blocked(lambda l,r,s,p: r.update(issuer_claim="trusted"),
                     "TYPED_SCHEMA_OR_FIELDS_INVALID")

    def test_missing_top_level_field_blocks(self):
        self.blocked(lambda l,r,s,p: r.pop("source_sha256"),
                     "TYPED_SCHEMA_OR_FIELDS_INVALID")

    def test_nested_extra_portable_field_blocks(self):
        self.blocked(lambda l,r,s,p: r["portable"].update(tampered="x"),
                     "PORTABLE_PACKAGE_SCHEMA_INVALID")

    def test_source_hash_order_blocks(self):
        self.blocked(lambda l,r,s,p: r["source_sha256"].reverse(),
                     "RECEIPT_SOURCE_ORDER_OR_HASH_DRIFT")

    def test_source_and_receipt_coordinated_forgery_blocks_against_profile(self):
        def attack(latest, receipt, sources, profile):
            receipt["source_sha256"][0] = "f"*64
            sources["source_set"][0]["sha256"] = "f"*64
        self.blocked(attack, "SOURCE_MANIFEST_PROFILE_PIN_DRIFT")

    def test_profile_source_pin_mismatch_blocks(self):
        self.blocked(lambda l,r,s,p: p["source_sha256"].reverse(),
                     "SOURCE_MANIFEST_PROFILE_PIN_DRIFT")

    def test_profile_schema_mismatch_blocks(self):
        self.blocked(lambda l,r,s,p: p.update(schema="evil"),
                     "TRUSTED_PROFILE_IDENTITY_INVALID")

    def test_profile_forbidden_production_adoption_blocks(self):
        self.blocked(lambda l,r,s,p: p.update(production_adoption="ACTIVE"),
                     "TRUSTED_PROFILE_IDENTITY_INVALID")

    def test_profile_unexpected_field_blocks(self):
        self.blocked(lambda l,r,s,p: p.update(override_issuer=True),
                     "TRUSTED_PROFILE_IDENTITY_INVALID")

    def test_profile_malformed_counts_blocks(self):
        self.blocked(lambda l,r,s,p: p.update(governed_patterns=True),
                     "TRUSTED_PROFILE_IDENTITY_INVALID")

    def test_profile_malformed_id_prefix_blocks(self):
        self.blocked(lambda l,r,s,p: p.update(card_id_prefix="^.*"),
                     "TRUSTED_PROFILE_IDENTITY_INVALID")

    def test_wrong_source_manifest_id_blocks(self):
        self.blocked(lambda l,r,s,p: s.update(dataset="other"),
                     "SOURCE_MANIFEST_IDENTITY_MISMATCH")

    def test_milestone_receipt_replay_blocks(self):
        self.blocked(lambda l,r,s,p: r.update(milestone="WIP62_OLD"),
                     "MILESTONE_PATH_OR_VERSION_DRIFT")

    def test_path_traversal_blocks(self):
        self.blocked(lambda l,r,s,p: (
            l.update(latest_receipt_path=BASE+"../WIP63.json"),
            r.update(receipt_path=BASE+"../WIP63.json")),
            "MILESTONE_PATH_OR_VERSION_DRIFT")

    def test_bad_commit_format_blocks(self):
        self.blocked(lambda l,r,s,p: l.update(latest_receipt_commit_sha="bad"),
                     "LATEST_COMMIT_POINTER_FORMAT_INVALID")

    def test_role_hash_mismatch_blocks(self):
        self.blocked(lambda l,r,s,p: l["authority"]["current_portable"].update(
            sha256="f"*64), "RECEIPT_PORTABLE_DRIFT:sha256")

    def test_same_synthetic_zip_hash_with_stale_package_blocks(self):
        self.blocked(lambda l,r,s,p: l["complete_working_content_package"].update(
            sha256="f"*64), "CURRENT_PACKAGE_ROLE_DRIFT:sha256")

    def test_canonical_hash_drift_blocks(self):
        self.blocked(lambda l,r,s,p: r["portable"].update(
            canonical_sha256="f"*64), "RECEIPT_PORTABLE_DRIFT:canonical_sha256")

    def test_wrong_zip_parent_blocks(self):
        self.blocked(lambda l,r,s,p: l["complete_working_content_package"].update(
            parent_sha256="f"*64), "PARENT_LINEAGE_INVALID")

    def test_stale_predecessor_blocks(self):
        self.blocked(lambda l,r,s,p: l["previous_wip63_source_current"][
            "portable"].update(sha256="f"*64), "PARENT_LINEAGE_INVALID")

    def test_missing_predecessor_blocks(self):
        self.blocked(lambda l,r,s,p: l.pop("previous_wip63_source_current"),
                     "PARENT_LINEAGE_INVALID")

    def test_self_parent_blocks(self):
        def mutate(l,r,s,p):
            r["parent_sha256"] = r["portable"]["sha256"]
            l["complete_working_content_package"]["parent_sha256"] = r["parent_sha256"]
            l["previous_wip63_source_current"]["portable"]["sha256"] = r["parent_sha256"]
        self.blocked(mutate, "PARENT_LINEAGE_INVALID")

    def test_zip_member_count_blocks(self):
        self.blocked(lambda l,r,s,p: r.update(zip_members=429),
                     "ZIP_MEMBER_COUNT_DRIFT")

    def test_zip_member_boolean_blocks(self):
        self.blocked(lambda l,r,s,p: r.update(zip_members=True),
                     "ZIP_MEMBER_COUNT_DRIFT")

    def test_count_conservation_blocks(self):
        self.blocked(lambda l,r,s,p: r["counts"].update(holds=184),
                     "COUNTS_PROFILE_OR_CONSERVATION_DRIFT")

    def test_count_boolean_blocks(self):
        self.blocked(lambda l,r,s,p: r["counts"].update(attested=True),
                     "COUNTS_NUMERIC_INVALID")

    def test_count_profile_guard_blocks(self):
        self.blocked(lambda l,r,s,p: r["counts"].update(learning_units=787),
                     "COUNTS_PROFILE_OR_CONSERVATION_DRIFT")

    def test_count_progress_guard_blocks(self):
        self.blocked(lambda l,r,s,p: l["progress"].update(
            rektion_independent_external_attested_cumulative=797),
            "COUNTS_LATEST_PROGRESS_DRIFT")

    def test_changed_ids_duplicate_blocks(self):
        self.blocked(lambda l,r,s,p: r["counts"]["changed_card_ids"].__setitem__(
            0, r["counts"]["changed_card_ids"][1]), "CHANGED_CARD_IDS_INVALID")

    def test_changed_ids_count_blocks(self):
        self.blocked(lambda l,r,s,p: r["counts"].update(changed_cards=17),
                     "CHANGED_CARD_IDS_INVALID")

    def test_changed_ids_wrong_prefix_blocks(self):
        self.blocked(lambda l,r,s,p: r["counts"]["changed_card_ids"].__setitem__(
            0, "other-lu-0001"), "CHANGED_CARD_IDS_INVALID")

    def test_change_count_inflation_blocks(self):
        self.blocked(lambda l,r,s,p: r["counts"].update(changed_cards=788),
                     "COUNTS_PROFILE_OR_CONSERVATION_DRIFT")

    def test_stage4_false_pass_blocks(self):
        self.blocked(lambda l,r,s,p: r["gates"].update(stage4="PASS"),
                     "STAGE_BOUNDARY_OR_SCOPED_PARITY_CLAIM_INVALID")

    def test_stage5_false_pass_blocks(self):
        self.blocked(lambda l,r,s,p: r["gates"].update(stage5_7="PASS"),
                     "STAGE_BOUNDARY_OR_SCOPED_PARITY_CLAIM_INVALID")

    def test_parity_claim_false_pass_blocks(self):
        self.blocked(lambda l,r,s,p: r["gates"].update(import_parity="FINAL"),
                     "STAGE_BOUNDARY_OR_SCOPED_PARITY_CLAIM_INVALID")

    def test_stage4_review_claim_false_blocks(self):
        self.blocked(lambda l,r,s,p: l["progress"].update(
            independent_expert_unreviewed_units=0),
            "STAGE_BOUNDARY_OR_SCOPED_PARITY_CLAIM_INVALID")

    def test_unexpected_gates_namespace_blocks(self):
        self.blocked(lambda l,r,s,p: r["gates"].update(stage6="PASS"),
                     "STAGE_BOUNDARY_OR_SCOPED_PARITY_CLAIM_INVALID")

    def test_duplicate_json_key_rejected_before_validation(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
            parse_strict(b'{"schema":"a","schema":"b"}')

    def test_nonfinite_json_rejected_before_validation(self):
        with self.assertRaisesRegex(ValueError, "NONFINITE_JSON"):
            parse_strict(b'{"counts":{"attested":NaN}}')

    def test_malformed_documents_never_success(self):
        result = evaluate([], {}, {}, {})
        self.assertEqual(result["status"], "BLOCKED_NONACTIVE_METADATA")
        self.no_release(result)


if __name__ == "__main__":
    unittest.main()
