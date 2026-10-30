#!/usr/bin/env python3
"""OP-02 independent-read, nonactive archive role and embedded-CURRENT audit.

Verifies actual archive bytes against externally supplied metadata snapshot.
No network fetch, mutation, CURRENT promotion, issuer authentication or release.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
from zipfile import ZipFile, BadZipFile

SHA = re.compile(r"[0-9a-f]{64}\Z")
WIP = re.compile(r"^WIP([1-9][0-9]*)_")
SUM = re.compile(r"([0-9a-f]{64})  (.+)\Z")
IMPORT = "01-Final-Import/IMPORT.WORKING.tsv"
CANONICAL = "02-Canonical-Data/CANONICAL-ENRICHED.WORKING.json"
POINTER = "07-Checkpoint-State/CURRENT-WORKSTREAM-POINTER.json"
MANIFEST = "MANIFEST.json"
SOURCES = "03-Source-Provenance/SOURCE-MANIFEST.json"
SUMS = "SHA256SUMS"
LINES = {
    "examples": "02-Canonical-Data/ALL-TRILINGUAL-EXAMPLES.jsonl",
    "kombinationen": "04-Enrichment-Work/ALL-KOMBINATIONEN.jsonl",
    "relations": "04-Enrichment-Work/ALL-LEXICAL-RELATIONS.jsonl",
}
MAX_ARCHIVE = 256_000_000
MAX_UNCOMPRESSED = 512_000_000
MAX_MEMBERS = 2000


def h(raw):
    return hashlib.sha256(raw).hexdigest()


def valid_hash(x):
    return type(x) is str and bool(SHA.fullmatch(x)) and x != "0" * 64


def strict_json(raw):
    def pairs(values):
        obj = {}
        for key, value in values:
            if key in obj:
                raise ValueError("DUPLICATE_JSON_FIELD")
            obj[key] = value
        return obj
    def nonfinite(value):
        raise ValueError("NONFINITE_JSON")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=nonfinite)


def audit(path, expected):
    """Read-only. Even a passing audit is not a release or an issuer."""
    err, ptr = [], []
    out = {
        "schema": "gcpk-op02-real-archive-integrity@1",
        "status": "BLOCKED",
        "binary_integrity": "NOT_VERIFIED",
        "embedded_current_consistency": "NOT_VERIFIED",
        "errors": err,
        "pointer_errors": ptr,
        "members_checked": 0,
        "hash_entries_checked": 0,
        "original_sources_checked": 0,
        "import_cards": None,
        "canonical_units": None,
        "issuer_authenticated": False,
        "git_current_authorized": False,
        "stage4_semantic_pass": False,
        "stage5_7_pass": False,
        "writer_granted": False,
        "performed_writes": False,
    }
    required = {"workstream", "milestone", "zip_sha256", "zip_size_bytes",
                "member_count", "canonical_sha256", "import_sha256",
                "source_sha256", "canonical_units", "import_cards",
                "examples", "kombinationen", "relations"}
    if (type(expected) is not dict or set(expected) != required
            or not all(valid_hash(expected.get(x)) for x in
                       ("zip_sha256", "canonical_sha256", "import_sha256"))
            or type(expected.get("milestone")) is not str or
            not WIP.match(expected["milestone"]) or
            expected.get("workstream") != "aber-hallo-listen-tabellen"
            or type(expected.get("source_sha256")) is not list
            or len(expected["source_sha256"]) != 2
            or not all(valid_hash(x) for x in expected["source_sha256"])
            or any(type(expected.get(k)) is not int or expected[k] < 0 for k in
                   ("zip_size_bytes", "member_count", "canonical_units",
                    "import_cards", "examples", "kombinationen", "relations"))):
        err.append("EXPECTED_AUTHORITY_SHAPE_INVALID")
        return out
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_ARCHIVE:
        err.append("ARCHIVE_NOT_REGULAR_OR_TOO_LARGE")
        return out
    raw = p.read_bytes()
    out["observed_zip_sha256"] = h(raw)
    out["observed_size_bytes"] = len(raw)
    if len(raw) != expected["zip_size_bytes"] or h(raw) != expected["zip_sha256"]:
        err.append("EXTERNAL_ZIP_SHA_SIZE_DRIFT")
        return out
    try:
        with ZipFile(io.BytesIO(raw)) as z:
            infos = z.infolist()
            names = [i.filename for i in infos]
            out["members_checked"] = len(infos)
            if len(infos) > MAX_MEMBERS or len(infos) != expected["member_count"]:
                err.append("MEMBER_COUNT_OR_LIMIT_DRIFT")
            if len(names) != len(set(names)):
                err.append("DUPLICATE_ARCHIVE_MEMBER")
            if sum(i.file_size for i in infos) > MAX_UNCOMPRESSED:
                err.append("ZIP_UNCOMPRESSED_SIZE_LIMIT")
            for i in infos:
                n = i.filename
                bits = PurePosixPath(n).parts
                if (not n or n.startswith("/") or "\\" in n
                        or any(part in (".", "..") for part in bits)
                        or n.endswith("/") or
                        stat.S_ISLNK((i.external_attr >> 16) & 0xffff)
                        or i.flag_bits & 1):
                    err.append("ARCHIVE_MEMBER_UNSAFE")
            if err:
                return out
            required_files = {IMPORT,CANONICAL,POINTER,MANIFEST,SOURCES,SUMS,*LINES.values()}
            if not required_files.issubset(names):
                err.append("REQUIRED_MEMBER_MISSING")
                return out
            # Full byte read verifies CRC, not just central-directory metadata.
            by_name = {n: z.read(n) for n in names}
            digest = {n: h(data) for n,data in by_name.items()}
            checks = {}
            for line in by_name[SUMS].decode("utf-8").splitlines():
                match = SUM.fullmatch(line)
                if not match:
                    err.append("SHA256SUMS_MALFORMED")
                    continue
                sha, name = match.groups()
                if name in checks:
                    err.append("SHA256SUMS_DUPLICATE")
                checks[name] = sha
            out["hash_entries_checked"] = len(checks)
            if set(checks) != set(names) - {SUMS}:
                err.append("SHA256SUMS_COVERAGE_DRIFT")
            if any(digest.get(n) != sha for n,sha in checks.items()):
                err.append("SHA256SUMS_MEMBER_BYTE_DRIFT")
            manifest = strict_json(by_name[MANIFEST])
            summary = manifest.get("summary")
            file_list = manifest.get("files")
            if (type(file_list) is not list or
                    manifest.get("file_count_excluding_manifest_and_checksums") != len(names)-2
                    or len(file_list) != len(names)-2):
                err.append("MANIFEST_MEMBER_COUNT_DRIFT")
            else:
                seen = set()
                for entry in file_list:
                    if type(entry) is not dict or set(entry) != {"path","size_bytes","sha256"}:
                        err.append("MANIFEST_FILE_ENTRY_SCHEMA_DRIFT")
                        continue
                    n = entry["path"]
                    if n in seen or n not in by_name or n in {MANIFEST,SUMS}:
                        err.append("MANIFEST_FILE_MEMBER_DRIFT")
                    seen.add(n)
                    if (entry["size_bytes"] != len(by_name.get(n,b""))
                            or entry["sha256"] != digest.get(n)):
                        err.append("MANIFEST_FILE_SHA_OR_SIZE_DRIFT")
                if seen != set(names)-{MANIFEST,SUMS}:
                    err.append("MANIFEST_FILE_COVERAGE_DRIFT")
            if (digest[CANONICAL] != expected["canonical_sha256"]
                    or digest[IMPORT] != expected["import_sha256"]):
                err.append("CANONICAL_IMPORT_EXACT_SHA_DRIFT")
            if (type(summary) is not dict or
                    summary.get("canonical_sha256") != digest[CANONICAL] or
                    summary.get("import_sha256") != digest[IMPORT] or
                    summary.get("status", "").startswith("CURRENT_WIP"+
                        WIP.match(expected["milestone"]).group(1)+"_") is not True):
                err.append("MANIFEST_CURRENT_HASH_OR_VERSION_DRIFT")
            canonical = strict_json(by_name[CANONICAL])
            units = canonical.get("learning_units") if type(canonical) is dict else None
            out["canonical_units"] = len(units) if type(units) is list else None
            if out["canonical_units"] != expected["canonical_units"]:
                err.append("CANONICAL_UNIT_COUNT_DRIFT")
            rows = list(csv.reader(io.StringIO(by_name[IMPORT].decode("utf-8-sig")),
                                   delimiter="\t"))
            out["import_cards"] = max(0,len(rows)-1)
            if (not rows or rows[0][:2] != ["id","card_type"]
                    or out["import_cards"] != expected["import_cards"]
                    or any(len(row) != len(rows[0]) for row in rows)
                    or len({row[0] for row in rows[1:]}) != len(rows)-1):
                err.append("IMPORT_ROW_COUNT_SCHEMA_OR_ID_DRIFT")
            sidecar = "01-Final-Import/IMPORT.WORKING.tsv.sha256"
            if (sidecar not in by_name or
                    not by_name[sidecar].decode("utf-8").startswith(digest[IMPORT] + "  ")):
                err.append("IMPORT_SIDECAR_HASH_DRIFT")
            for metric, name in LINES.items():
                lines = by_name[name].splitlines()
                if len(lines) != expected[metric]:
                    err.append("DATA_COUNT_DRIFT:" + metric)
                for line in lines:
                    strict_json(line)
            sm = strict_json(by_name[SOURCES])
            sources = sm.get("sources") if type(sm) is dict else None
            if type(sources) is not list or len(sources) != 2:
                err.append("SOURCE_MANIFEST_COUNT_DRIFT")
            else:
                observed = []
                for source in sources:
                    if type(source) is not dict or source.get("archive_file") not in by_name:
                        err.append("SOURCE_PDF_MISSING")
                        continue
                    n = source["archive_file"]
                    content = by_name[n]
                    observed.append(digest[n])
                    if source.get("sha256") != digest[n] or not content.startswith(b"%PDF-"):
                        err.append("SOURCE_PDF_BYTE_MISMATCH")
                out["original_sources_checked"] = len(observed)
                if observed != expected["source_sha256"]:
                    err.append("ORIGINAL_PDF_SOURCE_ORDER_OR_HASH_DRIFT")
            wp = strict_json(by_name[POINTER])
            curr = wp.get("current") if type(wp) is dict else None
            expected_version = int(WIP.match(expected["milestone"]).group(1))
            actual_version = int(WIP.match(curr).group(1)) if type(curr) is str and WIP.match(curr) else None
            out["pointer_claimed_milestone"] = curr
            if actual_version != expected_version:
                ptr.append("EMBEDDED_CURRENT_WIP_VERSION_STALE")
            if (type(wp) is not dict or wp.get("canonical_sha256") != digest[CANONICAL]
                    or wp.get("import_sha256") != digest[IMPORT]):
                ptr.append("EMBEDDED_CURRENT_CANONICAL_IMPORT_HASH_STALE")
            if type(wp) is not dict or wp.get("workstream") != expected["workstream"]:
                ptr.append("EMBEDDED_CURRENT_WORKSTREAM_DRIFT")
    except (BadZipFile, OSError, UnicodeError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        err.append("ARCHIVE_PARSE_OR_CRC_FAILURE:"+type(exc).__name__)
    out["binary_integrity"] = "PASS" if not err else "BLOCKED"
    out["embedded_current_consistency"] = "PASS" if not ptr and not err else "BLOCKED"
    out["status"] = "PASS_SCOPED_ARCHIVE_AND_POINTER_NOT_RELEASE" if not err and not ptr else "BLOCKED"
    return out
