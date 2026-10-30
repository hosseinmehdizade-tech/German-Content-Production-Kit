#!/usr/bin/env python3
"""OP02 typed envelope v2: shadow-only, domain-specific, NEVER a release gate.

This deliberately does not parse or rewrite legacy receipts in production.
The independently supplied observed anchor is *not authenticated* here.
"""
from __future__ import annotations
import re

SCHEMA = "gcpk-op02-typed-envelope@2"
TOP = {"schema", "workstream", "domain", "contract", "anchor",
       "sources", "payload", "gates"}
ANCHOR = {"kind", "path", "blob_sha", "milestone"}
SRC = {"source_id", "modality", "sha256"}
GATES = {"stage4", "stage5_7", "release", "issuer"}
BOUNDARY = {"stage4": "NOT_APPROVED", "stage5_7": "NOT_AUTHORIZED",
            "release": "NOT_AUTHORIZED", "issuer": "UNAUTHENTICATED"}
SHA = re.compile(r"^[0-9a-f]{64}$")
BLOB = re.compile(r"^[0-9a-f]{40}$")
WIP = re.compile(r"^WIP([1-9][0-9]*)_")
ID = re.compile(r"^ahl-lu-[0-9]{4}$")
DOMAINS = {
    "aber-hallo-listen-tabellen": {
        "domain": "grammar", "contract": "grammar-wip-open@1",
        "anchor_kind": "latest", "anchor_file": "LATEST.json",
        "sources": [
            ("deutsch-aber-hallo-listen-tabellen-a1-a2", "pdf", "4125ed49efa3c4e72500a9c80b8d39021c8933d9a387fc96a637fd4b457e3cf3"),
            ("deutsch-aber-hallo-listen-tabellen-b1-c2", "pdf", "ebaa3896c3c383808b832241afaf6c38ef4f498eb4dc1b38f26c12087cc97a04")
        ],
        "payload": {"wip", "zip_sha256", "parent_sha256", "size_bytes",
                    "zip_members", "attested", "holds", "governed_patterns",
                    "units", "lexical_cards", "changed_card_ids"},
    },
    "menschen-b1-24-lessons-v336": {
        "domain": "vocabulary", "contract": "vocabulary-audio-source@1",
        "anchor_kind": "checkpoint", "anchor_file": "CHECKPOINT.json",
        "sources": [
            ("menschen-a1a2b1-memrise-full-audio", "rar5", "a2ffb791c29ddaa43e27bb944f430bff6896dc3156115f8989eee3056d5471c1"),
            ("menschen-a1a2b1-memrise-full-audio-csv", "csv", "52f8bb896f5aa1c8f878aeb0ea74ef07ddbeee75261af89dfb2fcad624fc1222"),
        ],
        "payload": {"csv_rows", "lessons", "lesson_id", "lesson_rows",
                    "audio_refs", "unique_audio_refs", "missing_audio"},
    },
    "lesen-praesentation": {
        "domain": "reading", "contract": "reading-stage1-inventory@1",
        "anchor_kind": "checkpoint", "anchor_file": "CHECKPOINT.json",
        "sources": [
            ("presentation-topics-b2-c1", "pdf", "7abebcb70213a89a50a3bab35695618adde0b44a9975fdf9cdba33c296ef5523")
        ],
        "payload": {"source_pages", "topics", "stages"},
    },
}

def _sha(s):
    return type(s) is str and bool(SHA.fullmatch(s)) and s != "0"*64

def _int(x):
    return type(x) is int and x >= 0

def _same_keys(x, keys):
    return type(x) is dict and set(x) == keys

def report(errors, domain):
    return {
        "schema": "gcpk-op02-v2-nonactive-diagnostic@1",
        "domain": domain,
        "status": ("PASS_NONACTIVE_TYPED_METADATA_ONLY_NOT_RELEASE"
                   if not errors else "BLOCKED_NONACTIVE_METADATA"),
        "errors": sorted(set(errors)),
        "independent_anchor_authenticated": False,
        "issuer_authenticated": False,
        "source_bytes_verified": False,
        "portable_zip_bytes_verified": False,
        "stage4_semantic_pass": False,
        "stage5_allowed": False,
        "stage6_pass": False,
        "stage7_final": False,
        "production_migration_authorized": False,
        "writer_granted": False,
        "performed_writes": False,
    }

def evaluate(envelope, observed):
    """Compare a proposed typed envelope to a *separately supplied* snapshot.

    The observed object must be fetched and authenticated by another component.
    No result of this function grants that authority or attests source bytes.
    """
    errors = []
    domain = envelope.get("domain") if type(envelope) is dict else None
    if type(envelope) is not dict or type(observed) is not dict:
        return report(["DOCUMENT_NOT_OBJECT"], domain)
    workstream = envelope.get("workstream")
    cfg = DOMAINS.get(workstream) if type(workstream) is str else None
    if cfg is None:
        return report(["UNREGISTERED_WORKSTREAM"], domain)
    if (not _same_keys(envelope, TOP) or envelope.get("schema") != SCHEMA or
            domain != cfg["domain"] or envelope.get("contract") != cfg["contract"]):
        errors.append("ENVELOPE_SCHEMA_OR_DOMAIN_INVALID")
    a = envelope.get("anchor")
    o = observed.get("anchor")
    if not _same_keys(a, ANCHOR) or not _same_keys(o, ANCHOR):
        errors.append("ANCHOR_SHAPE_INVALID")
    else:
        path = "Workspaces/" + workstream + "/" + cfg["anchor_file"]
        if (a != o or a["kind"] != cfg["anchor_kind"] or a["path"] != path
                or not type(a["blob_sha"]) is str
                or not bool(BLOB.fullmatch(a["blob_sha"]))
                or not type(a["milestone"]) is str or not a["milestone"]):
            errors.append("ANCHOR_MISMATCH_OR_UNPINNED")
        if cfg["domain"] == "grammar" and not WIP.match(a["milestone"]):
            errors.append("GRAMMAR_MILESTONE_INVALID")
    sources = envelope.get("sources")
    expected = [{"source_id": i, "modality": m, "sha256": h}
                for i,m,h in cfg["sources"]]
    if (type(sources) is not list or
            len(sources) != len(expected) or
            any(not _same_keys(v, SRC) for v in sources) or
            sources != expected):
        errors.append("TYPED_SOURCE_ID_MODALITY_OR_ORDER_DRIFT")
    if type(observed.get("sources")) is not list or observed["sources"] != expected:
        errors.append("OBSERVED_SOURCE_IDENTITY_DRIFT")
    p = envelope.get("payload")
    recorded = observed.get("payload")
    if (type(p) is not dict or set(p) != cfg["payload"] or
            type(recorded) is not dict or set(recorded) != cfg["payload"]):
        errors.append("DOMAIN_PAYLOAD_SHAPE_INVALID")
    elif p != recorded:
        errors.append("DOMAIN_PAYLOAD_NOT_BOUND_TO_OBSERVED")
    # All domain-specific checks are applied even to a forged matching snapshot;
    # authenticated currentness and byte verification are *not* claimed.
    if type(p) is dict and set(p) == cfg["payload"]:
        if cfg["domain"] == "grammar":
            numeric = ("wip", "size_bytes", "zip_members", "attested", "holds",
                       "governed_patterns", "units", "lexical_cards")
            ids = p.get("changed_card_ids")
            if (not all(_int(p.get(k)) for k in numeric) or
                    p["wip"] == 0 or p["size_bytes"] == 0 or
                    p["zip_members"] == 0 or p["units"] != 788 or
                    p["lexical_cards"] != 787 or p["governed_patterns"] != 981 or
                    p["attested"] + p["holds"] != 981 or
                    not _sha(p.get("zip_sha256")) or
                    not _sha(p.get("parent_sha256")) or
                    p["zip_sha256"] == p["parent_sha256"] or
                    type(ids) is not list or len(ids) > 787 or
                    any(type(s) is not str or not ID.fullmatch(s) for s in ids) or
                    len(set(str(s) for s in ids)) != len(ids)):
                errors.append("GRAMMAR_PATTERN_LINEAGE_OR_LEDGER_INVALID")
            if (_same_keys(a, ANCHOR) and type(a.get("milestone")) is str and
                    WIP.match(a["milestone"]) and
                    p.get("wip") != int(WIP.match(a["milestone"]).group(1))):
                errors.append("GRAMMAR_WIP_ANCHOR_VERSION_DRIFT")
        elif cfg["domain"] == "vocabulary":
            nums = ("csv_rows", "lessons", "lesson_rows", "audio_refs",
                    "unique_audio_refs", "missing_audio")
            if (not all(_int(p.get(k)) for k in nums) or
                    p["csv_rows"] != 9109 or p["lessons"] != 24 or
                    p["lesson_id"] != "B1-L01" or p["lesson_rows"] != 126 or
                    p["audio_refs"] != 126 or p["unique_audio_refs"] != 126 or
                    p["missing_audio"] != 0):
                errors.append("VOCABULARY_CSV_LESSON_AUDIO_COUNTS_INVALID")
        elif cfg["domain"] == "reading":
            stages = p.get("stages")
            if (not _int(p.get("topics")) or not _int(p.get("source_pages")) or
                    p["topics"] != 68 or p["source_pages"] != 76 or
                    type(stages) is not list or len(stages) != 7 or
                    stages != ["PASS"] + ["NOT_STARTED"]*6):
                errors.append("READING_STAGE1_ONLY_INVENTORY_INVALID")
    gates = envelope.get("gates")
    if not _same_keys(gates, GATES) or gates != BOUNDARY:
        errors.append("NONACTIVE_RELEASE_BOUNDARY_VIOLATION")
    return report(errors, domain)
