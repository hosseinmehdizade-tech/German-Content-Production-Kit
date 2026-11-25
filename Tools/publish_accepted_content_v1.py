#!/usr/bin/env python3
"""One accepted-content publication: owner pointer + derived management mirrors.

No automatic acceptance, no remote writes, no workflow/Ruleset changes. A local
Git transaction uses an isolated index and creates a new branch with one commit.
Without --publish-branch, emit a complete plan for GitHub tree/commit connectors.
The existing read-only reconciliation and protected PR checks remain authoritative.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import zipfile

from reconcile_dynamic_content_portfolio_v1 import (
    REGISTRY, CATALOG, HEX40, HEX64, git_blob_sha, json_pointer, validate_registry,
)

ROUTING = "Optimization-Program/Control-Center/CANONICAL-FAMILY-WORKSPACE-ROUTING-v1.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def obj(raw):
    x = json.loads(raw)
    require(isinstance(x, dict), "expected JSON object")
    return x


def encode(x):
    return (json.dumps(x, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def valid_path(path):
    require(isinstance(path, str) and path and "\\" not in path
            and not path.startswith("/") and all(p not in ("", ".", "..")
                                                 for p in path.split("/")),
            "unsafe repository path")
    return path


def explicit_accepted(status):
    # This is a source-owner evidence shape check, not issuer authentication.
    # Never accept merely FINAL, candidate, working, or a date.
    if not isinstance(status, str):
        return False
    s = status.upper()
    return ("USER_ACCEPTED" in s and not any(
        x in s for x in ("NOT_USER_ACCEPTED", "UNACCEPTED", "PENDING_USER_ACCEPTANCE",
                        "USER_ACCEPTED_FALSE", "CANDIDATE_ONLY", "NOT_ACCEPTED")))


def archive_identity(raw):
    digest = hashlib.sha256(raw).hexdigest()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        require(bool(names) and len(names) == len(set(names)), "empty or duplicate ZIP")
        for name in names:
            valid_path(name.rstrip("/"))
        require(z.testzip() is None, "ZIP CRC failure")
    return digest, len(raw)



OBSERVATIONS = "Optimization-Program/Control-Center/COP-CURRENTNESS-OBSERVATIONS-v1.json"

def historical_pin(read, registry, family, prior):
    """Keep immutable dated byte evidence bound to its own historical artifact."""
    evidence_path = valid_path(registry["byte_evidence_bridge"]["receipt"])
    report = obj(read(evidence_path))
    require(report.get("schema") == "gfp-opt-curated-portfolio-exact-byte-evidence@1.0.0",
            "historical evidence schema")
    date = report.get("observation_date")
    require(isinstance(date,str) and re.fullmatch(r"20\d{2}-\d{2}-\d{2}",date),
            "historical evidence date missing")
    stored = prior.get("historical_asof_observation")
    pin = copy.deepcopy(stored) if stored is not None else {
        "artifact_name":prior["artifact_name"], "artifact_sha256":prior["artifact_sha256"],
        "artifact_size_bytes":prior["artifact_size_bytes"], "receipt_path":evidence_path,
        "observation_date":date,
    }
    require(pin.get("receipt_path")==evidence_path and pin.get("observation_date")==date,
            "historical evidence pointer/date mismatch")
    entries=[x for x in report["evidence"] if x.get("family_id")==family]
    require(bool(entries) and all(
        x.get("artifact_name")==pin.get("artifact_name") and
        x.get("expected_sha256")==x.get("measured_sha256")==pin.get("artifact_sha256") and
        x.get("measured_size_bytes")==pin.get("artifact_size_bytes") and
        x.get("comparison")=="PASS_EXACT_SOURCE_ACCEPTED_SHA256" and
        x.get("zip_crc_test")=="PASS_ALL_MEMBERS" for x in entries),
        "historical evidence does not match pinned prior artifact")
    return pin

def sync_observation(read, family, owner_path, new_owner, *, metadata_only, receipt_path,
                     sha_pointer, successor, name=None, location=None, provider=None, observed_as_of=None):
    """Derive existing COP mirror; never invent a provider readback."""
    raw=read(OBSERVATIONS)
    require(raw is not None,"COP observation ledger missing")
    evidence=obj(raw)
    require(evidence.get("schema")=="gcpk-cop-currentness-observations@1.0.0"
            and evidence.get("data_edit_authorized") is False,"COP observation schema")
    items=evidence["items"]
    rows=[x for x in items if x.get("family_id")==family]
    require(len(rows)<=1,"duplicate family observation")
    previous=rows[0] if rows else None
    if metadata_only:
        if previous and previous.get("evidence_path")==owner_path:
            require(json_pointer(obj(new_owner),previous["evidence_json_pointer"])==previous["sha256"],
                    "metadata edit would invalidate recorded working evidence")
        return raw,raw
    require(provider in ("conversation","library","google_drive") and isinstance(observed_as_of,str)
            and re.fullmatch(r"20\d{2}-\d{2}-\d{2}",observed_as_of),
            "accepted successor needs explicit provider and observation date")
    if previous:
        require(observed_as_of>=previous["observed_as_of"],"new observation predates existing evidence")
    current={"family_id":family,"kind":"accepted_successor","provider":provider,
             "observed_as_of":observed_as_of,"name":name,"sha256":successor,
             "evidence_path":receipt_path,"evidence_json_pointer":sha_pointer,
             "evidence_scope":"LOCAL_RAW_ZIP_SHA256_AND_CRC__OWNER_ACCEPTANCE__AS_OF_ONLY",
             "locator":location,"accepted_successor_decision":True,"approval_receipt":receipt_path}
    if previous: items[items.index(previous)]=current
    else: items.append(current)
    evidence["date"]=max(evidence.get("date",observed_as_of),observed_as_of)
    return raw,encode(evidence)

def build_plan(read, *, family, expected_parent, expected_owner_blob,
               new_owner, receipt_path=None, receipt_bytes=None, archive=None,
               sha_pointer=None, name_pointer=None, cards_pointer=None,
               status_pointer="/status", location=None, metadata_only=False,
               provider=None, observed_as_of=None):
    """Pure, fail-closed plan over an immutable base reader (path -> bytes/None).

    Native source receipt fields are mapped explicitly; no generic guessed SHA.
    Only existing registered canonical owners are eligible. A separate
    owner decision must already have occurred; this command does not grant it.
    """
    require(HEX64.fullmatch(expected_parent) and HEX40.fullmatch(expected_owner_blob),
            "invalid expected parent identity")
    reg_raw, route_raw = read(REGISTRY), read(ROUTING)
    registry, routing = obj(reg_raw), obj(route_raw)
    validate_registry(registry, obj(read(CATALOG)))
    candidates = [i for i in registry["items"] if i["id"] == family]
    routes = [i for i in routing["families"] if i["family_id"] == family]
    require(len(candidates) == len(routes) == 1, "family not uniquely registered")
    item, route = candidates[0], routes[0]
    locator, prior = item["owner_locator"], item["active_baseline"]
    owner_path = valid_path(locator["path"])
    workspace = valid_path(route["canonical_git_workspace"])
    require(owner_path.startswith(workspace + "/") and
            route["canonical_source_owner_document"] == owner_path,
            "canonical owner mismatch; no reassignment")
    old_owner = read(owner_path)
    require(old_owner is not None and
            git_blob_sha(old_owner) == locator["git_blob_observed"] == expected_owner_blob,
            "HOLD_CONCURRENT_UPDATE: owner blob differs")
    pointer = locator["artifact_sha_json_pointer"]
    require(json_pointer(obj(old_owner), pointer) ==
            prior["artifact_sha256"] == route["active_content_sha256"] == expected_parent,
            "HOLD_CONCURRENT_UPDATE: accepted parent differs")
    successor = json_pointer(obj(new_owner), pointer)
    require(isinstance(successor, str) and HEX64.fullmatch(successor), "bad successor SHA")
    require(new_owner != old_owner, "no owner change; no publication needed")
    changes = {owner_path: new_owner}
    old = {owner_path: old_owner}
    locator["git_blob_observed"] = git_blob_sha(new_owner)

    if metadata_only:
        require(successor == expected_parent, "metadata-only cannot change accepted artifact")
        require(all(x is None for x in (archive, receipt_path, receipt_bytes)),
                "metadata-only does not issue new acceptance evidence")
        sync_observation(read, family, owner_path, new_owner, metadata_only=True,
                         receipt_path=None,sha_pointer=None,successor=successor)
        # Preserve all selected release details and the canonical route exactly.
    else:
        require(successor != expected_parent, "same artifact: use metadata-only")
        require(archive is not None and receipt_path and receipt_bytes is not None
                and sha_pointer and name_pointer and cards_pointer and location,
                "accepted successor requires exact archive and native receipt mappings")
        receipt_path = valid_path(receipt_path)
        require(receipt_path.startswith(workspace + "/") and receipt_path != owner_path
                and receipt_path.endswith(".json"), "receipt must be separate and source-owned")
        existing = read(receipt_path)
        require(existing is None or existing == receipt_bytes, "immutable receipt conflict")
        receipt = obj(receipt_bytes)
        require(explicit_accepted(json_pointer(receipt, status_pointer)),
                "native receipt does not record explicit user acceptance")
        digest, size = archive_identity(archive)
        require(digest == successor == json_pointer(receipt, sha_pointer),
                "archive/receipt/owner SHA mismatch")
        name = json_pointer(receipt, name_pointer)
        require(isinstance(name, str) and name.lower().endswith(".zip") and
                "/" not in name and "\\" not in name, "invalid receipt ZIP name")
        cards = json_pointer(receipt, cards_pointer)
        require(type(cards) is int and cards > 0, "invalid receipt card count")
        prior = copy.deepcopy(prior)
        item["previous_accepted_baseline"] = prior
        # Keep historical byte-audit compatibility; never rewrite a past observation.
        historical = historical_pin(read,registry,family,prior)
        item["active_baseline"] = {
            "label": "User-accepted content",
            "artifact_name": name,
            "artifact_sha256": digest,
            "artifact_location": location,
            "selection": "LATEST_SOURCE_OWNER_SELECTED_CURATED_CONTENT",
            "byte_reverification_this_registry_pass": "PASS_LOCAL_EXACT_ZIP_SHA256_AND_CRC",
            "artifact_size_bytes": size,
            "size_provenance": "LOCAL_RAW_ZIP_BYTES",
            "source_receipt": receipt_path,
            "source_receipt_git_blob": git_blob_sha(receipt_bytes),
            "historical_asof_observation": historical,
        }
        item["metrics"]["cards"] = cards
        item["content_stage"] = "SCOPED_USER_ACCEPTED_CONTENT_RELEASE"
        item["runtime_stage"] = "NO_NEW_INDEPENDENT_RUNTIME_OR_SRS_ATTESTATION"
        item["next_action"] = "Preserve exact owner-accepted content; no repetitive audit."
        registry["total_cards_including_cross_family_overlap"] = sum(
            x["metrics"]["cards"] for x in registry["items"])
        route["previous_accepted_content_sha256"] = expected_parent
        route["active_content_sha256"] = successor
        if existing is None:
            changes[receipt_path], old[receipt_path] = receipt_bytes, None
        changes[ROUTING], old[ROUTING] = encode(routing), route_raw
        obs_old,obs_new=sync_observation(read,family,owner_path,new_owner,metadata_only=False,
            receipt_path=receipt_path,sha_pointer=sha_pointer,successor=successor,name=name,
            location=location,provider=provider,observed_as_of=observed_as_of)
        changes[OBSERVATIONS],old[OBSERVATIONS]=obs_new,obs_old
    validate_registry(registry, obj(read(CATALOG)))
    changes[REGISTRY], old[REGISTRY] = encode(registry), reg_raw
    return {
        "family": family, "parent_sha256": expected_parent,
        "successor_sha256": successor,
        "scope": "METADATA_ONLY_NO_NEW_ACCEPTANCE" if metadata_only
                 else "EXISTING_EXPLICIT_OWNER_ACCEPTANCE__NO_NEW_RUNTIME_ATTESTATION",
        "files": [{"path": p, "expected_blob": git_blob_sha(old[p]) if old[p] is not None else None,
                   "new_blob": git_blob_sha(raw), "content": raw.decode("utf-8")}
                  for p, raw in sorted(changes.items())],
    }


def git(root, *args, data=None, env=None):
    return subprocess.run(["git", "-C", str(root), *args], input=data,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=True, env=env).stdout


def base_reader(root, base):
    require(HEX40.fullmatch(base), "base must be an exact Git commit SHA")
    require(git(root, "rev-parse", base + "^{commit}").decode().strip() == base,
            "base commit mismatch")

    def read(path):
        spec = base + ":" + valid_path(path)
        # Distinguish missing paths from failures reading the repository.
        entries = git(root, "ls-tree", base, "--", path).decode().splitlines()
        if not entries:
            return None
        require(len(entries) == 1 and entries[0].startswith("100644 blob "),
                "expected regular tracked file")
        return git(root, "show", spec)
    return read


def publish_branch(root, base, plan, branch):
    """Create one local commit/ref; never touch main, index or working tree."""
    require(branch.startswith(("content/", "release/")) and
            bool(re.fullmatch(r"(?:content|release)/[A-Za-z0-9][A-Za-z0-9._/-]*", branch)),
            "use a new content/ or release/ branch")
    ref = "refs/heads/" + branch
    git(root, "check-ref-format", ref)
    read = base_reader(root, base)
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
        git(root, "read-tree", base, env=env)
        for f in plan["files"]:
            raw = read(f["path"])
            require((git_blob_sha(raw) if raw is not None else None) == f["expected_blob"],
                    "HOLD_CONCURRENT_UPDATE: base file differs")
            data = f["content"].encode("utf-8")
            digest = git(root, "hash-object", "-w", "--stdin", data=data).decode().strip()
            require(digest == f["new_blob"], "new blob mismatch")
            git(root, "update-index", "--add", "--cacheinfo",
                "100644," + digest + "," + f["path"], env=env)
        tree = git(root, "write-tree", env=env).decode().strip()
        commit = git(root, "commit-tree", tree, "-p", base, "-m",
                     "Publish accepted content: " + plan["family"]).decode().strip()
        # CAS create-only: cannot overwrite another chat's branch or main.
        git(root, "update-ref", ref, commit, "0" * 40)
    for f in plan["files"]:
        require(git(root, "show", commit + ":" + f["path"]) ==
                f["content"].encode("utf-8"), "commit readback mismatch")
    return commit


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--base", required=True)
    p.add_argument("--family", required=True)
    p.add_argument("--expected-parent", required=True)
    p.add_argument("--expected-owner-blob", required=True)
    p.add_argument("--new-owner", type=Path, required=True)
    p.add_argument("--receipt-path")
    p.add_argument("--receipt-file", type=Path)
    p.add_argument("--archive", type=Path)
    p.add_argument("--receipt-sha-pointer")
    p.add_argument("--receipt-name-pointer")
    p.add_argument("--receipt-cards-pointer")
    p.add_argument("--receipt-status-pointer", default="/status")
    p.add_argument("--location")
    p.add_argument("--provider", choices=("conversation","library","google_drive"))
    p.add_argument("--observed-as-of", help="Date of actual raw artifact observation (YYYY-MM-DD)")
    p.add_argument("--metadata-only", action="store_true")
    p.add_argument("--publish-branch", help="Optional new local content/ or release/ branch")
    a = p.parse_args(argv)
    try:
        read = base_reader(a.repo_root, a.base)
        receipt = (a.receipt_file.read_bytes() if a.receipt_file else
                   read(a.receipt_path) if a.receipt_path else None)
        plan = build_plan(read, family=a.family, expected_parent=a.expected_parent,
                          expected_owner_blob=a.expected_owner_blob,
                          new_owner=a.new_owner.read_bytes(), receipt_path=a.receipt_path,
                          receipt_bytes=receipt, archive=a.archive.read_bytes() if a.archive else None,
                          sha_pointer=a.receipt_sha_pointer, name_pointer=a.receipt_name_pointer,
                          cards_pointer=a.receipt_cards_pointer, status_pointer=a.receipt_status_pointer,
                          location=a.location, metadata_only=a.metadata_only,
                          provider=a.provider, observed_as_of=a.observed_as_of)
        plan["base_commit"] = a.base
        if a.publish_branch:
            commit = publish_branch(a.repo_root, a.base, plan, a.publish_branch)
            print(json.dumps({"status": "LOCAL_ATOMIC_COMMIT__PR_CI_PENDING",
                              "branch": a.publish_branch, "commit": commit,
                              "files": [f["path"] for f in plan["files"]]}, indent=2))
        else:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError,
            zipfile.BadZipFile, RuntimeError) as exc:
        print(json.dumps({"status": "HOLD_NO_PUBLICATION", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
