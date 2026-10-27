"""Non-destructive packaging guard for content ZIP builders."""
from contextlib import contextmanager
from pathlib import Path
import hashlib
import json
import os
import re
import tempfile
import zipfile

PURPOSES = ("stage5_acceptance", "final_delivery", "validated_major_checkpoint", "required_recovery", "explicit_user_checkpoint")
WIP = re.compile(r"(?:^|[-_.])(wip\d*|batch\d+|per[-_]?edit|scratch|micro[-_]?edit)(?:[-_.]|$)", re.I)

class PackageGuardError(ValueError):
    pass

def check_intent(output, purpose, evidence=None, user_request=None):
    out = Path(output)
    if out.suffix.lower() != ".zip" or purpose not in PURPOSES:
        raise PackageGuardError("invalid archive path or purpose")
    if out.exists() or out.is_symlink():
        raise PackageGuardError("existing archive is immutable")
    if WIP.search(out.stem) and purpose not in ("required_recovery", "explicit_user_checkpoint"):
        raise PackageGuardError("routine WIP/batch ZIP refused")
    if purpose in ("required_recovery", "validated_major_checkpoint"):
        if evidence is None or not Path(evidence).is_file():
            raise PackageGuardError("missing milestone/recovery evidence")
        try:
            data = json.loads(Path(evidence).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise PackageGuardError("invalid evidence") from exc
        if not isinstance(data, dict):
            raise PackageGuardError("evidence must be object")
        if purpose == "required_recovery" and not str(data.get("recovery_gap") or "").strip():
            raise PackageGuardError("documented recovery gap required")
        if purpose == "validated_major_checkpoint" and data.get("status") not in ("PASS", "CLOSED", "VERIFIED"):
            raise PackageGuardError("validated milestone required")
    if purpose == "explicit_user_checkpoint" and not (user_request or "").strip():
        raise PackageGuardError("explicit user scope required")

def fingerprint(purpose, inputs):
    h = hashlib.sha256(purpose.encode())
    for path in inputs:
        path = Path(path)
        h.update(b"\0")
        h.update(path.name.encode("utf-8"))
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1048576), b""):
                h.update(block)
    return h.hexdigest()

def read_index(path):
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PackageGuardError("unreadable package index") from exc
    if not isinstance(data, dict):
        raise PackageGuardError("invalid package index")
    return data
