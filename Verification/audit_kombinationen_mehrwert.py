#!/usr/bin/env python3
"""ACTIVE compatibility entrypoint for old scanner path.
The immutable 2026-10-26 ZIP remains unchanged for historical replay.
New active use delegates to v1.1; heuristic flags do not block release.
"""
from audit_kombinationen_lean_v1_1 import main

if __name__ == "__main__":
    raise SystemExit(main())
