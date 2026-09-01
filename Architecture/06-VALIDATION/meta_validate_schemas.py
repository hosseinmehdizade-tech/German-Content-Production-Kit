#!/usr/bin/env python3
"""Draft 2020-12 meta-validation and instance validation for prompt/delivery gate v3.1.4."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
from pathlib import Path
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def error_record(kind: str, artifact: str, error: Exception) -> dict[str, str]:
    return {"kind": kind, "artifact": artifact, "message": str(error)}


def run_meta_validation(package_root: Path) -> dict[str, Any]:
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
    except ImportError as exc:
        return {
            "status": "NOT_RUN",
            "reason": f"Required dependency unavailable: {exc}",
            "meta_schema_status": "NOT_RUN",
            "instance_schema_status": "NOT_RUN",
            "errors": [],
        }

    schema_dir = package_root / "02-SCHEMAS"
    schemas = {path.name: load(path) for path in sorted(schema_dir.glob("*.json"))}
    errors: list[dict[str, str]] = []
    for name, schema in schemas.items():
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # jsonschema emits several concrete schema exceptions
            errors.append(error_record("meta_schema", name, exc))

    registry = Registry()
    for schema in schemas.values():
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))

    profile_schema = schemas["PROFILE-SCHEMA.json"]
    type_rule_schema = schemas["TYPE-RULE-SCHEMA.json"]
    learning_schema = schemas["LEARNING-UNIT-SCHEMA.json"]
    source_registry_schema = schemas["SOURCE-REGISTRY-SCHEMA.json"]
    runtime_evidence_schema = schemas["RUNTIME-IMPORT-EVIDENCE-SCHEMA.json"]
    instances: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    instances.extend((f"03-PROFILES/{path.name}", load(path), profile_schema) for path in sorted((package_root / "03-PROFILES").glob("*.json")))
    instances.extend((f"04-TYPE-RULES/{path.name}", load(path), type_rule_schema) for path in sorted((package_root / "04-TYPE-RULES").glob("*.json")))
    registry_path = package_root / "03-SOURCES" / "SOURCE-REGISTRY.json"
    instances.append(("03-SOURCES/SOURCE-REGISTRY.json", load(registry_path), source_registry_schema))
    sample_path = package_root / "05-SAMPLES" / "MULTI-TYPE-CANONICAL-SAMPLE.json"
    instances.append(("05-SAMPLES/MULTI-TYPE-CANONICAL-SAMPLE.json", load(sample_path), learning_schema))
    runtime_sample_path = package_root / "05-SAMPLES" / "RUNTIME-IMPORT-EVIDENCE-ISOLATED-SAMPLE.json"
    instances.append(("05-SAMPLES/RUNTIME-IMPORT-EVIDENCE-ISOLATED-SAMPLE.json", load(runtime_sample_path), runtime_evidence_schema))

    for artifact, instance, schema in instances:
        validator = Draft202012Validator(schema, registry=registry)
        for validation_error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
            location = ".".join(str(part) for part in validation_error.absolute_path)
            errors.append({
                "kind": "instance_schema",
                "artifact": artifact,
                "path": location,
                "message": validation_error.message,
            })

    meta_errors = sum(item["kind"] == "meta_schema" for item in errors)
    instance_errors = sum(item["kind"] == "instance_schema" for item in errors)
    return {
        "tool": "jsonschema.Draft202012Validator",
        "jsonschema_version": importlib.metadata.version("jsonschema"),
        "draft": "2020-12",
        "schema_count": len(schemas),
        "instance_count": len(instances),
        "meta_schema_status": "PASS" if meta_errors == 0 else "FAIL",
        "instance_schema_status": "PASS" if instance_errors == 0 else "FAIL",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = run_meta_validation(args.package_root.resolve())
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
