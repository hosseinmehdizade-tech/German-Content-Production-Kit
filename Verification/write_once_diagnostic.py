#!/usr/bin/env python3
"""OP-02 diagnostic sink: new JSON report only, never an existing user file.

This limits accidental output-path data loss. It is NOT a filesystem sandbox
against a hostile process with simultaneous write/rename privileges.
"""
from __future__ import annotations

from pathlib import Path
import re


class DiagnosticOutputBlocked(Exception):
    """A diagnostic destination is unsafe; no report was written."""


_RESERVED = {
    "latest.json", "checkpoint.json", "project-state.json",
    "runtime-authority-pin.json", "current-portable-authority.json",
    "source-manifest.json", "writer-scopes.json", "project-memory.json",
    "release-policy.json", "final-verification-status.json",
}
_PROTECTED = {
    "workspaces", "locked", "source", "sources", "original", "originals",
    "01-app", "00-source", "archive", "archives", "recovery",
    "protected-history",
}


def write_once_json_report(target: Path, raw: str, *,
                           protected_inputs: tuple[Path, ...] = ()) -> None:
    """Write a brand-new .json diagnostic; refuse old/protected input paths.

    The exclusive 'x' mode is the final atomic no-clobber barrier even
    if a file is created between preliminary checks and the open call.
    """
    if not isinstance(target, Path) or not isinstance(raw, str):
        raise DiagnosticOutputBlocked("INVALID_DIAGNOSTIC_ARGUMENTS")
    if target.suffix.lower() != ".json" or target.name.lower() in _RESERVED:
        raise DiagnosticOutputBlocked("OUTPUT_MUST_BE_NEW_NONAUTHORITY_JSON")
    if ".." in target.parts:
        raise DiagnosticOutputBlocked("OUTPUT_PARENT_TRAVERSAL")
    dest = target.absolute()
    components = [part.lower() for part in dest.parts]
    if any(
        part in _PROTECTED or any(
            token in _PROTECTED
            for token in re.split(r"[-_.]+", part) if token
        )
        for part in components
    ):
        raise DiagnosticOutputBlocked("OUTPUT_IN_WORKSPACE_SOURCE_OR_LOCKED_PATH")
    if dest.is_symlink() or any(parent.is_symlink() for parent in dest.parents):
        raise DiagnosticOutputBlocked("OUTPUT_SYMLINK_PATH_REFUSED")
    if any(dest == Path(item).absolute() for item in protected_inputs):
        raise DiagnosticOutputBlocked("OUTPUT_EQUALS_INPUT_PATH")
    if not dest.parent.is_dir():
        raise DiagnosticOutputBlocked("OUTPUT_PARENT_NOT_A_DIRECTORY")
    try:
        with dest.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(raw)
    except FileExistsError as exc:
        raise DiagnosticOutputBlocked("OUTPUT_EXISTS_NO_CLOBBER") from exc
