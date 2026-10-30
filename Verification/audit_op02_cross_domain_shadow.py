#!/usr/bin/env python3
"""OP-02 cross-domain read-only compatibility probes; never publish or migrate.

The actual domain checkpoint formats stay separate and immutable. These
adapters test source/role assumptions before proposing a future typed envelope.
Positive output means only scoped Git metadata consistency, never linguistic,
original source/ZIP-byte, trusted CURRENT issuer, or Stage5-7 acceptance.
"""
from __future__ import annotations

import re

SHA = re.compile(r"^[0-9a-f]{64}$")
WIP = re.compile(r"^WIP([1-9][0-9]*)_")
ALH = "aber-hallo-listen-tabellen"
B1 = "menschen-b1-24-lessons-v336"
READ = "lesen-praesentation"
PINS = {
    ALH: {
        "source_ids": ["deutsch-aber-hallo-listen-tabellen-a1-a2",
                       "deutsch-aber-hallo-listen-tabellen-b1-c2"],
        "source_hashes": ["4125ed49efa3c4e72500a9c80b8d39021c8933d9a387fc96a637fd4b457e3cf3",
                          "ebaa3896c3c383808b832241afaf6c38ef4f498eb4dc1b38f26c12087cc97a04"],
        "units": 788, "cards": 787, "governed": 981,
    },
    B1: {
        "source_id": "menschen-a1a2b1-memrise-full-audio",
        "archive_hash": "a2ffb791c29ddaa43e27bb944f430bff6896dc3156115f8989eee3056d5471c1",
        "csv_hash": "52f8bb896f5aa1c8f878aeb0ea74ef07ddbeee75261af89dfb2fcad624fc1222",
        "rows": 9109, "lessons": 24, "l01_rows": 126,
    },
    READ: {
        "source_id": "presentation-topics-b2-c1",
        "source_hash": "7abebcb70213a89a50a3bab35695618adde0b44a9975fdf9cdba33c296ef5523",
        "topics": 68, "pages": 76, "stage": 1,
    },
}

def _sha(value):
    return isinstance(value, str) and bool(SHA.fullmatch(value)) and value != "0"*64

def _int(value):
    return type(value) is int and value >= 0

def _get(data, *path):
    for part in path:
        if not isinstance(data, dict):
            return None
        data = data.get(part)
    return data

def _report(kind, errors):
    return {
        "schema": "gcpk-op02-cross-domain-shadow@1",
        "profile": kind,
        "status": ("PASS_SCOPED_READONLY_METADATA_ONLY_NOT_RELEASE" if not errors
                   else "BLOCKED_SCOPED_METADATA"),
        "errors": sorted(set(errors)),
        "source_binary_bytes_verified": False,
        "portable_zip_bytes_verified": False,
        "issuer_authenticated": False,
        "stage4_semantic_accepted": False,
        "stage5_7_accepted": False,
        "production_schema_activated": False,
        "writer_granted": False,
        "performed_writes": False,
    }

def evaluate(kind, manifest, checkpoint, *, latest=None, receipt=None):
    errors = []
    if kind not in PINS:
        return _report(str(kind), ["UNREGISTERED_DOMAIN_PROFILE"])
    if not isinstance(manifest, dict) or not isinstance(checkpoint, dict):
        return _report(kind, ["DOCUMENT_NOT_OBJECT"])
    if kind == ALH:
        pin = PINS[ALH]
        src = manifest.get("source_set")
        if (manifest.get("schema") != "gcpk-source-manifest@1.1.0"
            or manifest.get("dataset") != ALH
            or not isinstance(src, list) or len(src) != 2
            or any(not isinstance(x, dict) for x in src)
            or [x.get("source_id") for x in src] != pin["source_ids"]
            or [x.get("sha256") for x in src] != pin["source_hashes"]
            or [x.get("source_type") for x in src] != ["pdf","pdf"]):
            errors.append("GRAMMAR_ORIGINAL_SOURCE_PIN_DRIFT")
        if not isinstance(latest, dict) or not isinstance(receipt, dict):
            errors.append("GRAMMAR_LATEST_RECEIPT_REQUIRED")
        else:
            m = latest.get("latest_milestone")
            version = WIP.match(m) if isinstance(m, str) else None
            n = int(version.group(1)) if version else None
            path = latest.get("latest_receipt_path")
            if (n is None or latest.get("workstream") != ALH
                or receipt.get("workstream") != ALH
                or not isinstance(path, str)
                or ".." in path.split("/")
                or not path.startswith("Workspaces/" + ALH + "/")
                or f"WIP{n}" not in path
                or not path.endswith(".json")):
                errors.append("GRAMMAR_CURRENT_MILESTONE_INVALID")
            p = _get(latest, "authority", "current_portable")
            pkg = latest.get("complete_working_content_package")
            if not isinstance(p, dict) or not isinstance(pkg, dict):
                errors.append("GRAMMAR_PORTABLE_ROLES_REQUIRED")
            else:
                fields = (("zip","filename","name"),("zip_sha256","sha256","sha256"),
                          ("size_bytes","size_bytes","bytes"),
                          ("library_file_id","library_file_id","library_file_id"),
                          ("library_path","library_path","library_path"))
                for rec_key, cur_key, pkg_key in fields:
                    if (not p.get(cur_key) or p.get(cur_key) != pkg.get(pkg_key)
                        or p.get(cur_key) != receipt.get(rec_key)):
                        errors.append("GRAMMAR_THREE_ROLE_DRIFT:" + cur_key)
                if (not _sha(p.get("sha256")) or not _sha(p.get("canonical_sha256"))
                    or not _sha(p.get("import_sha256"))
                    or p.get("canonical_sha256") != receipt.get("canonical_sha256")
                    or p.get("import_sha256") != receipt.get("import_sha256")
                    or not _int(p.get("size_bytes")) or p.get("size_bytes") == 0
                    or not _int(pkg.get("member_count"))
                    or pkg["member_count"] != receipt.get("zip_members")):
                    errors.append("GRAMMAR_PORTABLE_HASH_OR_MEMBER_DRIFT")
                prev = _get(latest, f"previous_wip{n}_source_current", "portable")
                parent = receipt.get("parent_sha256")
                if (not _sha(parent) or not isinstance(prev,dict)
                    or prev.get("sha256") != parent
                    or pkg.get("parent_sha256") != parent or p.get("sha256") == parent):
                    errors.append("GRAMMAR_PARENT_LINEAGE_DRIFT")
                if (p.get("stage4") != "OPEN" or pkg.get("stage4") != "OPEN"
                    or pkg.get("stage5_6_7") != "NOT_RUN"):
                    errors.append("GRAMMAR_STAGE_BOUNDARY_DRIFT")
            if (receipt.get("status") != "PASS_SCOPED_STAGE4_OPEN"
                or receipt.get("source_sha256") != pin["source_hashes"]
                or receipt.get("full_stage4") != "OPEN"
                or receipt.get("stage5_to_7") != "NOT_RUN"):
                errors.append("GRAMMAR_SCOPED_SOURCE_OR_STAGE_DRIFT")
            fields = ("units","lexical_cards","governed_patterns",
                      "cumulative_attested","remaining_holds","new_attested",
                      "changed_cards","zip_members")
            if not all(_int(receipt.get(x)) for x in fields):
                errors.append("GRAMMAR_COUNTS_NOT_INTEGERS")
            else:
                if (receipt["units"] != pin["units"] or receipt["lexical_cards"] != pin["cards"]
                    or receipt["governed_patterns"] != pin["governed"]
                    or receipt["cumulative_attested"] + receipt["remaining_holds"] != pin["governed"]
                    or receipt["new_attested"] > receipt["cumulative_attested"]
                    or receipt["changed_cards"] > pin["cards"]
                    or receipt["cumulative_attested"] != _get(latest,"progress","rektion_independent_external_attested_cumulative")
                    or receipt["remaining_holds"] != _get(latest,"progress","rektion_external_holds_remaining")):
                    errors.append("GRAMMAR_COUNTS_NOT_CONSERVED")
            ids=receipt.get("changed_card_ids")
            if (not isinstance(ids,list) or len(ids) != receipt.get("changed_cards")
                or any(not isinstance(x,str) or not re.fullmatch(r"ahl-lu-[0-9]{4}", x) for x in ids)
                or len(set(str(x) for x in ids)) != len(ids)):
                errors.append("GRAMMAR_CHANGED_ID_LEDGER_INVALID")
    elif kind == B1:
        pin=PINS[B1]
        arc=manifest.get("raw_archive")
        csv=manifest.get("export_csv")
        if (manifest.get("schema") != "gcpk-source-manifest@1.1.0"
            or manifest.get("source_id") != pin["source_id"]
            or manifest.get("source_type") != "memrise-export-archive"
            or not isinstance(arc,dict) or arc.get("sha256") != pin["archive_hash"]
            or arc.get("archive_format") != "RAR5" or not _int(arc.get("size_bytes"))
            or not isinstance(csv,dict) or csv.get("sha256") != pin["csv_hash"]
            or csv.get("rows") != pin["rows"]
            or _get(manifest, "course_membership", "numbered_lessons", "B1") != pin["lessons"]):
            errors.append("LESSON_MEMRISE_ARCHIVE_CSV_SOURCE_DRIFT")
        source=checkpoint.get("source")
        scope=checkpoint.get("scope")
        if (checkpoint.get("schema") != "menschen-b1-24-lessons-checkpoint@1.0.0"
            or checkpoint.get("workstream") != B1
            or not isinstance(source,dict) or not isinstance(scope,dict)
            or source.get("source_id") != pin["source_id"]
            or source.get("raw_archive_sha256") != pin["archive_hash"]
            or source.get("export_csv_sha256") != pin["csv_hash"]
            or source.get("b1_l01_source_rows") != pin["l01_rows"]
            or source.get("b1_l01_audio_refs") != pin["l01_rows"]
            or source.get("b1_l01_unique_audio_refs") != pin["l01_rows"]
            or source.get("b1_l01_missing_archive_audio") != 0
            or scope.get("level") != "B1" or scope.get("lessons") != pin["lessons"]
            or _get(checkpoint,"production_contract","exact_examples_per_final_sense_or_expression") != 4):
            errors.append("LESSON_SCOPE_AUDIO_AND_SOURCE_BRIDGE_DRIFT")
        if latest is not None or receipt is not None:
            errors.append("LESSON_FOREIGN_GRAMMAR_ROLES_FORBIDDEN")
    elif kind == READ:
        pin=PINS[READ]
        if (manifest.get("schema_version") != "1.0.0"
            or manifest.get("dataset") != READ
            or manifest.get("source_id") != pin["source_id"]
            or manifest.get("sha256") != pin["source_hash"]
            or manifest.get("source_kind") != "user-provided-pdf"
            or _get(manifest,"inventory","topics") != pin["topics"]
            or _get(manifest,"inventory","pdf_pages") != pin["pages"]):
            errors.append("READING_PDF_TOPIC_INVENTORY_PIN_DRIFT")
        stages=checkpoint.get("stages")
        if (checkpoint.get("checkpoint_schema_version") != "2.0.0"
            or _get(checkpoint,"dataset","id") != READ
            or pin["source_hash"] not in str(_get(checkpoint,"dataset","authoritative_source"))
            or not isinstance(stages,list) or len(stages) != 7
            or any(not isinstance(x,dict) for x in stages)
            or [x.get("stage") for x in stages] != list(range(1,8))
            ):
            # The actual stage values are verified separately below.
            errors.append("READING_STAGE_STRUCTURE_DRIFT")
        if isinstance(stages,list) and len(stages)==7 and all(isinstance(x,dict) for x in stages):
            if (stages[0].get("state") != "PASS"
                or any(x.get("state") != "NOT_STARTED" for x in stages[1:])):
                errors.append("READING_NO_FAKE_DOWNSTREAM_PASS")
        else:
            errors.append("READING_STAGE_STRUCTURE_DRIFT")
        if latest is not None or receipt is not None:
            errors.append("READING_NO_SYNTHETIC_PORTABLE_OR_RELEASE")
    return _report(kind, errors)


def rollback_diagnostic(expected_before_sha, proposed_after_sha,
                        observed_head_sha, *, issuer_authenticated=False,
                        mutation_requested=False):
    """Plan only. Never grants a write or performs rollback."""
    errors = []
    if not all(_sha(x) for x in (expected_before_sha,proposed_after_sha,observed_head_sha)):
        errors.append("INVALID_HASH_OR_PREIMAGE")
    elif observed_head_sha != proposed_after_sha:
        errors.append("CONCURRENT_HEAD_OR_POSTIMAGE_DRIFT")
    if expected_before_sha == proposed_after_sha:
        errors.append("NO_CHANGE_NOT_A_ROLLBACK")
    if not issuer_authenticated:
        errors.append("INDEPENDENT_ISSUER_AUTHORIZATION_MISSING")
    if mutation_requested:
        errors.append("MUTATION_FORBIDDEN_IN_NONACTIVE_DIAGNOSTIC")
    return {"status":"BLOCKED_NO_ROLLBACK_WRITER", "errors":sorted(set(errors)),
            "safe_to_write":False, "performed_writes":False,
            "needs_new_explicit_approval":True, "requires_fresh_remote_cas":True}
