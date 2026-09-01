#!/usr/bin/env python3
"""Typed, dependency-free validator for GFP German Content Architecture v3.1.3."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


VALIDATOR_VERSION = "2.2.0"
LANGUAGE_TAG = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
TYPE_ID = re.compile(r"^[a-z][a-z0-9_]*$")
SENSE_ID = re.compile(r"^sense-[A-Za-z0-9][A-Za-z0-9._-]*$")
CONNECTION_KINDS = {
    "collocation",
    "nvv",
    "pattern",
    "fixed_expression",
    "prepositional_pattern",
    "common_combination",
    "other",
}

# Learner-facing fields whose presence requires explicit claim-level provenance.
# Required roles are OR-ed; source allowed_claims still applies independently.
LEARNER_FIELD_CLAIM_BINDINGS = {
    ("details", "rection"): {
        "claim": "rection",
        "required_roles": {"german_grammar_authority", "german_monolingual"},
        "minimum_verified_sources": 1,
    },
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_type_rules(directory: Path) -> list[dict[str, Any]]:
    return [load_json(path) for path in sorted(directory.glob("*.json"))]


def add_issue(issues: list[dict[str, str]], severity: str, code: str, path: str, message: str) -> None:
    issues.append({"severity": severity, "code": code, "path": path, "message": message})


def nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if value is None:
        return False
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def json_identity(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def type_matches(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return False


def validate_field_spec_configuration(spec: dict[str, Any], path: str, issues: list[dict[str, str]]) -> None:
    expected = spec.get("type")
    if expected not in {"string", "boolean", "integer", "number", "array", "object"}:
        add_issue(issues, "error", "FIELD_SPEC_TYPE", f"{path}.type", "Unknown field-spec type.")
        return
    if "enum" in spec:
        for index, enum_value in enumerate(spec["enum"]):
            if not type_matches(enum_value, expected):
                add_issue(issues, "error", "FIELD_SPEC_ENUM_TYPE", f"{path}.enum[{index}]", f"Enum value does not match {expected}.")
    if expected == "array":
        if not isinstance(spec.get("items"), dict):
            add_issue(issues, "error", "FIELD_SPEC_ITEMS", f"{path}.items", "Array field spec requires an item spec.")
        else:
            validate_field_spec_configuration(spec["items"], f"{path}.items", issues)
    if expected == "object":
        properties = spec.get("properties")
        if not isinstance(properties, dict):
            add_issue(issues, "error", "FIELD_SPEC_PROPERTIES", f"{path}.properties", "Object field spec requires properties.")
            properties = {}
        for name, child in properties.items():
            validate_field_spec_configuration(child, f"{path}.properties.{name}", issues)
        for required_name in spec.get("required_properties", []):
            if required_name not in properties:
                add_issue(issues, "error", "FIELD_SPEC_REQUIRED_UNKNOWN", f"{path}.required_properties", f"Unknown property {required_name!r}.")


def validate_typed_value(value: Any, spec: dict[str, Any], path: str, issues: list[dict[str, str]]) -> None:
    if value is None:
        if not spec.get("nullable", False):
            add_issue(issues, "error", "VALUE_NULL_FORBIDDEN", path, "Field is not nullable.")
        return

    expected = spec.get("type")
    if not type_matches(value, expected):
        add_issue(issues, "error", "VALUE_TYPE", path, f"Expected {expected}; found {type(value).__name__}.")
        return
    if "enum" in spec and value not in spec["enum"]:
        add_issue(issues, "error", "VALUE_ENUM", path, f"Value {value!r} is not in the declared enum.")

    if expected == "string":
        if "min_length" in spec and len(value) < spec["min_length"]:
            add_issue(issues, "error", "VALUE_MIN_LENGTH", path, "String is shorter than declared minimum.")
        if "max_length" in spec and len(value) > spec["max_length"]:
            add_issue(issues, "error", "VALUE_MAX_LENGTH", path, "String is longer than declared maximum.")
        if "pattern" in spec:
            try:
                if re.fullmatch(spec["pattern"], value) is None:
                    add_issue(issues, "error", "VALUE_PATTERN", path, "String does not match declared pattern.")
            except re.error as exc:
                add_issue(issues, "error", "FIELD_SPEC_PATTERN_INVALID", path, str(exc))
    elif expected in {"integer", "number"}:
        if "minimum" in spec and value < spec["minimum"]:
            add_issue(issues, "error", "VALUE_MINIMUM", path, "Number is below declared minimum.")
        if "maximum" in spec and value > spec["maximum"]:
            add_issue(issues, "error", "VALUE_MAXIMUM", path, "Number is above declared maximum.")
    elif expected == "array":
        if "min_items" in spec and len(value) < spec["min_items"]:
            add_issue(issues, "error", "VALUE_MIN_ITEMS", path, "Array is shorter than declared minimum.")
        if "max_items" in spec and len(value) > spec["max_items"]:
            add_issue(issues, "error", "VALUE_MAX_ITEMS", path, "Array is longer than declared maximum.")
        if spec.get("unique_items") and len({json_identity(item) for item in value}) != len(value):
            add_issue(issues, "error", "VALUE_ITEMS_NOT_UNIQUE", path, "Array items must be unique.")
        for index, item in enumerate(value):
            validate_typed_value(item, spec["items"], f"{path}[{index}]", issues)
    elif expected == "object":
        properties = spec.get("properties", {})
        for required_name in spec.get("required_properties", []):
            if required_name not in value:
                add_issue(issues, "error", "VALUE_OBJECT_REQUIRED", f"{path}.{required_name}", "Required object property is missing.")
        for name, child_value in value.items():
            if name not in properties:
                if not spec.get("additional_properties", False):
                    add_issue(issues, "error", "VALUE_OBJECT_UNKNOWN", f"{path}.{name}", "Undeclared object property.")
                continue
            validate_typed_value(child_value, properties[name], f"{path}.{name}", issues)


def find_rule(unit_type: str, profile: dict[str, Any], rules: list[dict[str, Any]]) -> dict[str, Any] | None:
    for rule in rules:
        if unit_type in rule.get("applies_to", []):
            return rule
    if profile.get("allow_generic_type_rule"):
        return next((rule for rule in rules if rule.get("rule_id", "").startswith("generic@")), None)
    return None


def resolve_count_policy(profile: dict[str, Any], unit_type: str) -> dict[str, Any]:
    policy = dict(profile.get("examples", {}).get("default", {}))
    policy.update(profile.get("examples", {}).get("by_type", {}).get(unit_type, {}))
    return policy


def check_count_policy(policy: dict[str, Any], path: str, issues: list[dict[str, str]]) -> None:
    target = policy.get("target")
    minimum = policy.get("minimum")
    maximum = policy.get("maximum")
    if not isinstance(target, int) or isinstance(target, bool) or target < 0:
        add_issue(issues, "error", "COUNT_TARGET_INVALID", f"{path}.target", "target must be a non-negative integer.")
    if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 0:
        add_issue(issues, "error", "COUNT_MINIMUM_INVALID", f"{path}.minimum", "minimum must be a non-negative integer.")
    if maximum is not None and (not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 0):
        add_issue(issues, "error", "COUNT_MAXIMUM_INVALID", f"{path}.maximum", "maximum must be null or a non-negative integer.")
    if isinstance(minimum, int) and isinstance(maximum, int) and minimum > maximum:
        add_issue(issues, "error", "COUNT_RANGE_INVALID", path, "minimum exceeds maximum.")
    if isinstance(target, int) and isinstance(minimum, int) and target < minimum:
        add_issue(issues, "error", "COUNT_TARGET_OUTSIDE", path, "target is below minimum.")
    if isinstance(target, int) and isinstance(maximum, int) and target > maximum:
        add_issue(issues, "error", "COUNT_TARGET_OUTSIDE", path, "target exceeds maximum.")


def validate_configuration(profile: dict[str, Any], rules: list[dict[str, Any]], issues: list[dict[str, str]], source_registry: dict[str, Any] | None = None) -> None:
    if profile.get("profile_schema_version") != "2.1.0":
        add_issue(issues, "error", "PROFILE_VERSION", "profile.profile_schema_version", "Expected 2.1.0.")
    check_count_policy(profile.get("examples", {}).get("default", {}), "profile.examples.default", issues)
    for unit_type in profile.get("examples", {}).get("by_type", {}):
        check_count_policy(resolve_count_policy(profile, unit_type), f"profile.examples.by_type.{unit_type}", issues)

    source_policy = profile.get("source_policy", {})
    if source_registry is None:
        add_issue(issues, "error", "SOURCE_REGISTRY_MISSING", "source_registry", "Source Registry is required by v3.1.3.")
    else:
        if source_registry.get("registry_id") != source_policy.get("registry_id"):
            add_issue(issues, "error", "SOURCE_REGISTRY_ID_MISMATCH", "profile.source_policy.registry_id", "Loaded Source Registry does not match Profile.")
        source_ids = [item.get("source_id") for item in source_registry.get("sources", []) if isinstance(item, dict)]
        if len(source_ids) != len(set(source_ids)):
            add_issue(issues, "error", "SOURCE_REGISTRY_DUPLICATE_ID", "source_registry.sources", "Duplicate source_id in Source Registry.")

    owners: dict[str, str] = {}
    for index, rule in enumerate(rules):
        base = f"type_rules[{index}]"
        if rule.get("type_rule_schema_version") != "2.0.0":
            add_issue(issues, "error", "TYPE_RULE_VERSION", f"{base}.type_rule_schema_version", "Expected 2.0.0.")
        rendered = json.dumps(rule, ensure_ascii=False).lower()
        for forbidden in ("target_examples", "count_policy", "required_translation_languages", "layout", "practice_mode"):
            if forbidden in rendered:
                add_issue(issues, "error", "TYPE_RULE_WRONG_OWNER", base, f"Type Rule contains Profile/UI concept {forbidden!r}.")
        for unit_type in rule.get("applies_to", []):
            if unit_type in owners:
                add_issue(issues, "error", "TYPE_RULE_OVERLAP", f"{base}.applies_to", f"{unit_type!r} already owned by {owners[unit_type]}.")
            owners[unit_type] = rule.get("rule_id", base)
        for scope_name in ("core_fields", "detail_fields"):
            fields = rule.get(scope_name, {})
            for field_name, spec in fields.items():
                validate_field_spec_configuration(spec, f"{base}.{scope_name}.{field_name}", issues)
        for constraint_index, constraint in enumerate(rule.get("conditional_requirements", [])):
            scope_name = "core_fields" if constraint.get("scope") == "core" else "detail_fields"
            declared = rule.get(scope_name, {})
            if constraint.get("when_field") not in declared:
                add_issue(issues, "error", "CONDITIONAL_FIELD_UNKNOWN", f"{base}.conditional_requirements[{constraint_index}].when_field", "Condition references an undeclared field.")
            for required_name in constraint.get("require_fields", []):
                if required_name not in declared:
                    add_issue(issues, "error", "CONDITIONAL_REQUIRED_UNKNOWN", f"{base}.conditional_requirements[{constraint_index}].require_fields", f"Undeclared field {required_name!r}.")

    for unit_type, requirements in profile.get("type_requirements", {}).items():
        rule = find_rule(unit_type, profile, rules)
        if rule is None:
            add_issue(issues, "error", "PROFILE_REQUIREMENT_RULE_MISSING", f"profile.type_requirements.{unit_type}", "No Type Rule resolves this Profile requirement.")
            continue
        for field_name in requirements.get("required_core_fields", []):
            if field_name not in rule.get("core_fields", {}):
                add_issue(issues, "error", "PROFILE_CORE_REQUIREMENT_UNKNOWN", f"profile.type_requirements.{unit_type}.required_core_fields", f"Undeclared typed field {field_name!r}.")
        for field_name in requirements.get("required_detail_fields", []):
            if field_name not in rule.get("detail_fields", {}):
                add_issue(issues, "error", "PROFILE_DETAIL_REQUIREMENT_UNKNOWN", f"profile.type_requirements.{unit_type}.required_detail_fields", f"Undeclared typed field {field_name!r}.")


def collect_snapshot(dataset: dict[str, Any]) -> dict[str, Any]:
    by_id: dict[str, tuple[str, str]] = {}
    card_examples: dict[str, set[str]] = {}
    retired: set[str] = set()
    for unit in dataset.get("learning_units", []):
        card_id = unit.get("id", "")
        ids: set[str] = set()
        retired.update(unit.get("metadata", {}).get("retired_example_ids", []))
        for example in unit.get("examples", []):
            example_id = example.get("id", "")
            if example_id:
                by_id[example_id] = (card_id, example.get("text", ""))
                ids.add(example_id)
        card_examples[card_id] = ids
    return {"by_id": by_id, "card_examples": card_examples, "retired": retired}


def compare_identity(previous: dict[str, Any], current: dict[str, Any], issues: list[dict[str, str]]) -> None:
    old = collect_snapshot(previous)
    new = collect_snapshot(current)
    for example_id, (card_id, _text) in new["by_id"].items():
        if example_id in old["retired"]:
            add_issue(issues, "error", "RETIRED_ID_REUSED", f"examples[{example_id}]", "Retired Example ID was reused.")
        if example_id in old["by_id"] and old["by_id"][example_id][0] != card_id:
            add_issue(issues, "error", "EXAMPLE_OWNER_CHANGED", f"examples[{example_id}]", "Example ID moved to another Learning Unit.")
    for card_id, old_ids in old["card_examples"].items():
        if card_id not in new["card_examples"]:
            continue
        new_ids = new["card_examples"][card_id]
        removed = old_ids - new_ids
        unretired = removed - new["retired"]
        for example_id in sorted(unretired):
            add_issue(issues, "error", "REMOVED_ID_NOT_RETIRED", f"learning_units[{card_id}].metadata.retired_example_ids", f"Removed ID {example_id!r} must be retired.")
        if removed and (new_ids - old_ids) and len(old_ids) == len(new_ids):
            add_issue(issues, "error", "POSSIBLE_ID_REPLACEMENT", f"learning_units[{card_id}].examples", "Preserve IDs across text edits and reorders.")


def validate_dataset(
    dataset: dict[str, Any],
    profile: dict[str, Any],
    rules: list[dict[str, Any]],
    previous: dict[str, Any] | None = None,
    source_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    validate_configuration(profile, rules, issues, source_registry)

    if dataset.get("contract_version") != "3.1.3":
        add_issue(issues, "error", "CONTRACT_VERSION", "contract_version", "Expected 3.1.3.")
    if dataset.get("profile_id") != profile.get("profile_id"):
        add_issue(issues, "error", "PROFILE_MISMATCH", "profile_id", "Dataset and loaded Profile differ.")
    units = dataset.get("learning_units")
    if not isinstance(units, list):
        add_issue(issues, "error", "LEARNING_UNITS_TYPE", "learning_units", "learning_units must be an array.")
        units = []

    try:
        card_pattern = re.compile(profile.get("id_policy", {}).get("card_id_pattern", r"(?!)"))
        suffix_pattern = profile.get("id_policy", {}).get("example_id_suffix_pattern", r"(?!)")
        re.compile(suffix_pattern)
    except re.error as exc:
        add_issue(issues, "error", "ID_PATTERN_INVALID", "profile.id_policy", str(exc))
        card_pattern = re.compile(r"(?!)")
        suffix_pattern = r"(?!)"

    allowed_types = set(profile.get("allowed_types", []))
    required_unit_fields = profile.get("required_unit_fields", [])
    source_language = profile.get("languages", {}).get("source", {}).get("lang")
    required_translation_languages = [item["lang"] for item in profile.get("languages", {}).get("translations", []) if item.get("required")]
    source_policy = profile.get("source_policy", {})
    card_ids: set[str] = set()
    example_ids: set[str] = set()
    duplicate_example_ids: set[str] = set()
    translation_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    connection_counts: Counter[str] = Counter()
    total_examples = 0

    for unit_index, unit in enumerate(units):
        base = f"learning_units[{unit_index}]"
        if not isinstance(unit, dict):
            add_issue(issues, "error", "LEARNING_UNIT_TYPE", base, "Learning Unit must be an object.")
            continue
        card_id = unit.get("id")
        if not isinstance(card_id, str) or not card_id:
            add_issue(issues, "error", "CARD_ID_REQUIRED", f"{base}.id", "Learning Unit ID is required.")
            card_id = ""
        elif card_id in card_ids:
            add_issue(issues, "error", "CARD_ID_DUPLICATE", f"{base}.id", f"Duplicate ID {card_id!r}.")
        else:
            card_ids.add(card_id)
        if card_id and card_pattern.fullmatch(card_id) is None:
            add_issue(issues, "error", "CARD_ID_PATTERN", f"{base}.id", "ID does not match Profile policy.")

        unit_type = unit.get("type")
        if not isinstance(unit_type, str) or TYPE_ID.fullmatch(unit_type) is None:
            add_issue(issues, "error", "TYPE_INVALID", f"{base}.type", "Invalid Type identifier.")
            unit_type = ""
        else:
            type_counts[unit_type] += 1
            if unit_type not in allowed_types:
                add_issue(issues, "error", "TYPE_NOT_ALLOWED", f"{base}.type", f"Type {unit_type!r} is not allowed by Profile.")
        rule = find_rule(unit_type, profile, rules) if unit_type else None
        if rule is None:
            add_issue(issues, "error", "TYPE_RULE_MISSING", f"{base}.type", f"No Type Rule resolves {unit_type!r}.")

        if not nonempty(unit.get("headword")):
            add_issue(issues, "error", "HEADWORD_REQUIRED", f"{base}.headword", "headword is required.")
        for field_name in required_unit_fields:
            if not nonempty(unit.get(field_name)):
                add_issue(issues, "error", "PROFILE_FIELD_REQUIRED", f"{base}.{field_name}", f"Profile requires {field_name}.")
        if profile.get("definition_policy") == "forbidden" and "definition_de" in unit:
            add_issue(issues, "error", "DEFINITION_FORBIDDEN", f"{base}.definition_de", "Profile forbids definition_de.")

        senses = unit.get("senses", [])
        if not isinstance(senses, list):
            add_issue(issues, "error", "SENSES_TYPE", f"{base}.senses", "senses must be an array.")
            senses = []
        sense_ids: set[str] = set()
        for sense_index, sense in enumerate(senses):
            sense_base = f"{base}.senses[{sense_index}]"
            sense_id = sense.get("id") if isinstance(sense, dict) else None
            if not isinstance(sense_id, str) or SENSE_ID.fullmatch(sense_id) is None:
                add_issue(issues, "error", "SENSE_ID_INVALID", f"{sense_base}.id", "Invalid sense ID.")
            elif sense_id in sense_ids:
                add_issue(issues, "error", "SENSE_ID_DUPLICATE", f"{sense_base}.id", "Duplicate sense ID.")
            else:
                sense_ids.add(sense_id)

        for scope_key, rule_key, profile_key in (("core", "core_fields", "required_core_fields"), ("details", "detail_fields", "required_detail_fields")):
            values = unit.get(scope_key, {})
            if not isinstance(values, dict):
                add_issue(issues, "error", f"{scope_key.upper()}_TYPE", f"{base}.{scope_key}", f"{scope_key} must be an object.")
                values = {}
            if rule:
                specs = rule.get(rule_key, {})
                required_names = {name for name, spec in specs.items() if spec.get("required")}
                required_names.update(profile.get("type_requirements", {}).get(unit_type, {}).get(profile_key, []))
                for required_name in sorted(required_names):
                    if required_name not in values:
                        add_issue(issues, "error", "TYPED_FIELD_REQUIRED", f"{base}.{scope_key}.{required_name}", "Required typed field is missing.")
                allow_undeclared = rule.get(f"allow_undeclared_{'core' if scope_key == 'core' else 'detail'}_fields", False)
                for field_name, value in values.items():
                    if field_name not in specs:
                        if not allow_undeclared:
                            add_issue(issues, "error", "TYPED_FIELD_UNKNOWN", f"{base}.{scope_key}.{field_name}", "Field is not declared by the Type Rule.")
                        continue
                    validate_typed_value(value, specs[field_name], f"{base}.{scope_key}.{field_name}", issues)
                for constraint in rule.get("conditional_requirements", []):
                    if constraint.get("scope") == scope_key and values.get(constraint.get("when_field")) == constraint.get("equals"):
                        for required_name in constraint.get("require_fields", []):
                            if required_name not in values:
                                add_issue(issues, "error", "TYPED_FIELD_CONDITIONAL", f"{base}.{scope_key}.{required_name}", "Conditional typed field is missing.")

        connections = unit.get("connections", [])
        if not isinstance(connections, list):
            add_issue(issues, "error", "CONNECTIONS_TYPE", f"{base}.connections", "connections must be an array.")
            connections = []
        for connection_index, connection in enumerate(connections):
            conn_base = f"{base}.connections[{connection_index}]"
            if not isinstance(connection, dict):
                add_issue(issues, "error", "CONNECTION_TYPE", conn_base, "Connection must be an object.")
                continue
            unknown = set(connection) - {"text", "kind", "sense_id"}
            if unknown:
                add_issue(issues, "error", "CONNECTION_FIELD_UNKNOWN", conn_base, f"Unknown connection fields: {sorted(unknown)}.")
            if not nonempty(connection.get("text")):
                add_issue(issues, "error", "CONNECTION_TEXT_REQUIRED", f"{conn_base}.text", "Connection text is required.")
            kind = connection.get("kind")
            if kind not in CONNECTION_KINDS:
                add_issue(issues, "error", "CONNECTION_KIND_INVALID", f"{conn_base}.kind", f"Invalid connection kind {kind!r}.")
            else:
                connection_counts[kind] += 1
            sense_id = connection.get("sense_id")
            if sense_id is not None and sense_id not in sense_ids:
                add_issue(issues, "error", "CONNECTION_SENSE_UNKNOWN", f"{conn_base}.sense_id", "Connection sense_id does not reference this Unit.")

        examples = unit.get("examples")
        if not isinstance(examples, list):
            add_issue(issues, "error", "EXAMPLES_TYPE", f"{base}.examples", "examples must be an array.")
            examples = []
        total_examples += len(examples)
        count_policy = resolve_count_policy(profile, unit_type)
        enforcement = count_policy.get("enforcement")
        target = count_policy.get("target")
        minimum = count_policy.get("minimum")
        maximum = count_policy.get("maximum")
        if enforcement == "exact" and len(examples) != target:
            add_issue(issues, "error", "EXAMPLE_COUNT_EXACT", f"{base}.examples", f"Effective Profile target is exactly {target}; found {len(examples)}.")
        elif enforcement == "range":
            if isinstance(minimum, int) and len(examples) < minimum:
                add_issue(issues, "error", "EXAMPLE_COUNT_MIN", f"{base}.examples", f"Effective minimum is {minimum}; found {len(examples)}.")
            if isinstance(maximum, int) and len(examples) > maximum:
                add_issue(issues, "error", "EXAMPLE_COUNT_MAX", f"{base}.examples", f"Effective maximum is {maximum}; found {len(examples)}.")
        elif enforcement == "advisory" and len(examples) != target:
            add_issue(issues, "warning", "EXAMPLE_COUNT_ADVISORY", f"{base}.examples", f"Effective target is {target}; found {len(examples)}.")

        orders: list[int] = []
        retired_ids = set(unit.get("metadata", {}).get("retired_example_ids", [])) if isinstance(unit.get("metadata"), dict) else set()
        for example_index, example in enumerate(examples):
            ex_base = f"{base}.examples[{example_index}]"
            if not isinstance(example, dict):
                add_issue(issues, "error", "EXAMPLE_TYPE", ex_base, "Example must be an object.")
                continue
            unknown = set(example) - {"id", "lang", "text", "order", "sense_id", "translations"}
            if unknown:
                add_issue(issues, "error", "EXAMPLE_FIELD_UNKNOWN", ex_base, f"Unknown Example fields: {sorted(unknown)}.")
            example_id = example.get("id")
            if not isinstance(example_id, str) or not example_id:
                add_issue(issues, "error", "EXAMPLE_ID_REQUIRED", f"{ex_base}.id", "Example ID is required.")
                example_id = ""
            elif example_id in example_ids:
                duplicate_example_ids.add(example_id)
                add_issue(issues, "error", "EXAMPLE_ID_DUPLICATE", f"{ex_base}.id", f"Duplicate Example ID {example_id!r}.")
            else:
                example_ids.add(example_id)
            if example_id in retired_ids:
                add_issue(issues, "error", "RETIRED_ID_ACTIVE", f"{ex_base}.id", "Active ID is listed as retired.")
            if card_id and example_id:
                try:
                    if re.fullmatch(re.escape(card_id) + suffix_pattern, example_id) is None:
                        add_issue(issues, "error", "EXAMPLE_ID_PATTERN", f"{ex_base}.id", "Example ID does not belong to its Learning Unit.")
                except re.error:
                    pass
            lang = example.get("lang")
            if not isinstance(lang, str) or LANGUAGE_TAG.fullmatch(lang) is None:
                add_issue(issues, "error", "LANGUAGE_TAG_INVALID", f"{ex_base}.lang", "Invalid language tag.")
            elif lang != source_language:
                add_issue(issues, "error", "EXAMPLE_SOURCE_LANGUAGE", f"{ex_base}.lang", f"Expected {source_language!r}.")
            if not nonempty(example.get("text")):
                add_issue(issues, "error", "EXAMPLE_TEXT_REQUIRED", f"{ex_base}.text", "German source text is required.")
            order = example.get("order")
            if not isinstance(order, int) or isinstance(order, bool) or order < 1:
                add_issue(issues, "error", "ORDER_INVALID", f"{ex_base}.order", "order must be a positive integer.")
            else:
                orders.append(order)
            sense_id = example.get("sense_id")
            if sense_id is not None and sense_id not in sense_ids:
                add_issue(issues, "error", "EXAMPLE_SENSE_UNKNOWN", f"{ex_base}.sense_id", "Example sense_id does not reference this Unit.")
            if len(sense_ids) > 1 and sense_id is None:
                add_issue(issues, "error", "EXAMPLE_SENSE_REQUIRED", f"{ex_base}.sense_id", "Multi-sense Unit examples require sense_id.")

            translations = example.get("translations")
            if not isinstance(translations, list):
                add_issue(issues, "error", "TRANSLATIONS_TYPE", f"{ex_base}.translations", "translations must be an array.")
                translations = []
            languages: set[str] = set()
            for translation_index, translation in enumerate(translations):
                tr_base = f"{ex_base}.translations[{translation_index}]"
                if not isinstance(translation, dict):
                    add_issue(issues, "error", "TRANSLATION_TYPE", tr_base, "Translation must be an object.")
                    continue
                unknown = set(translation) - {"lang", "text"}
                if unknown:
                    add_issue(issues, "error", "TRANSLATION_FIELD_UNKNOWN", tr_base, f"Unknown translation fields: {sorted(unknown)}.")
                tr_lang = translation.get("lang")
                if not isinstance(tr_lang, str) or LANGUAGE_TAG.fullmatch(tr_lang) is None:
                    add_issue(issues, "error", "LANGUAGE_TAG_INVALID", f"{tr_base}.lang", "Invalid language tag.")
                    continue
                if tr_lang in languages:
                    add_issue(issues, "error", "TRANSLATION_LANGUAGE_DUPLICATE", f"{tr_base}.lang", f"Duplicate language {tr_lang!r}.")
                languages.add(tr_lang)
                translation_counts[tr_lang] += 1
                if tr_lang == source_language:
                    add_issue(issues, "error", "SOURCE_AS_TRANSLATION", f"{tr_base}.lang", "Source language cannot be duplicated as a translation.")
                if not nonempty(translation.get("text")):
                    add_issue(issues, "error", "TRANSLATION_TEXT_REQUIRED", f"{tr_base}.text", "Translation text is required.")
            for required_lang in required_translation_languages:
                if required_lang not in languages:
                    add_issue(issues, "error", "TRANSLATION_REQUIRED", f"{ex_base}.translations", f"Missing required translation {required_lang!r}.")
        if len(orders) != len(set(orders)):
            add_issue(issues, "error", "ORDER_DUPLICATE", f"{base}.examples", "Example orders must be unique.")
        if sorted(orders) != list(range(1, len(examples) + 1)):
            add_issue(issues, "error", "ORDER_NOT_CONTIGUOUS", f"{base}.examples", "Example orders must be contiguous from 1.")

        metadata = unit.get("metadata")
        if not isinstance(metadata, dict):
            add_issue(issues, "error", "METADATA_TYPE", f"{base}.metadata", "metadata must be an object.")
        elif metadata.get("dataset_id") != profile.get("dataset", {}).get("id"):
            add_issue(issues, "error", "DATASET_ID_MISMATCH", f"{base}.metadata.dataset_id", "Dataset ID differs from Profile.")

        provenance = unit.get("provenance")
        if not isinstance(provenance, dict):
            add_issue(issues, "error", "PROVENANCE_TYPE", f"{base}.provenance", "provenance must be an object.")
        else:
            sources = provenance.get("sources")
            if not isinstance(sources, list):
                add_issue(issues, "error", "SOURCES_TYPE", f"{base}.provenance.sources", "sources must be an array.")
                sources = []
            risk_flags = provenance.get("risk_flags", [])
            if not isinstance(risk_flags, list):
                add_issue(issues, "error", "RISK_FLAGS_TYPE", f"{base}.provenance.risk_flags", "risk_flags must be an array.")
                risk_flags = []
            configured_risky = set(source_policy.get("risky_flags", []))
            is_risky = bool(set(risk_flags) & configured_risky)
            registry_map = {}
            if isinstance(source_registry, dict):
                registry_map = {item.get("source_id"): item for item in source_registry.get("sources", []) if isinstance(item, dict) and item.get("source_id")}
            verified_records = []
            verified_claim_sources: dict[str, list[dict[str, Any]]] = {}
            for source_index, source in enumerate(sources):
                src_base = f"{base}.provenance.sources[{source_index}]"
                if not isinstance(source, dict):
                    add_issue(issues, "error", "SOURCE_TYPE", src_base, "Source must be an object.")
                    continue
                source_id = source.get("source_id")
                registry_entry = registry_map.get(source_id)
                if registry_entry is None:
                    if source_policy.get("require_registered_source", True):
                        add_issue(issues, "error", "SOURCE_UNKNOWN", f"{src_base}.source_id", f"Unknown source_id {source_id!r}.")
                    continue
                if source.get("source_kind") != registry_entry.get("kind"):
                    add_issue(issues, "error", "SOURCE_KIND_MISMATCH", f"{src_base}.source_kind", "source_kind differs from Source Registry.")
                if source.get("source_kind") not in source_policy.get("allowed_kinds", []):
                    add_issue(issues, "error", "SOURCE_KIND_NOT_ALLOWED", f"{src_base}.source_kind", "Source kind is not allowed by Profile.")
                approval = registry_entry.get("approval_status")
                if approval == "deprecated":
                    add_issue(issues, "error", "SOURCE_DEPRECATED", f"{src_base}.source_id", "Deprecated source cannot satisfy current policy.")
                if approval == "test_only" and not source_policy.get("allow_test_only_sources", False):
                    add_issue(issues, "error", "SOURCE_TEST_ONLY_FORBIDDEN", f"{src_base}.source_id", "Test-only source is forbidden by this Profile.")
                if source_policy.get("require_approved_source") and approval != "approved":
                    add_issue(issues, "error", "SOURCE_NOT_APPROVED", f"{src_base}.source_id", "Profile requires an approved source.")
                claims = source.get("what_was_verified")
                if not isinstance(claims, list):
                    add_issue(issues, "error", "SOURCE_CLAIMS_TYPE", f"{src_base}.what_was_verified", "what_was_verified must be an array.")
                    claims = []
                allowed_claims = set(registry_entry.get("allowed_claims", []))
                for claim in claims:
                    if claim not in allowed_claims:
                        add_issue(issues, "error", "SOURCE_CLAIM_NOT_ALLOWED", f"{src_base}.what_was_verified", f"Source {source_id!r} is not approved to verify claim {claim!r}.")
                status = source.get("verification_status")
                if status == "verified":
                    if not claims:
                        add_issue(issues, "error", "VERIFIED_SOURCE_WITHOUT_CLAIM", f"{src_base}.what_was_verified", "A verified source must name at least one verified claim.")
                    verified_records.append(registry_entry)
                    for claim in claims:
                        verified_claim_sources.setdefault(claim, []).append(registry_entry)
                elif status not in {"unverified", "blocked", "not_found"}:
                    add_issue(issues, "error", "SOURCE_VERIFICATION_STATUS", f"{src_base}.verification_status", "Invalid verification_status.")
            if source_policy.get("require_verified_source") and len(verified_records) < source_policy.get("minimum_verified_sources", 0):
                add_issue(issues, "error", "VERIFIED_SOURCE_REQUIRED", f"{base}.provenance.sources", "Profile minimum verified source count is not met.")
            for claim, requirement in source_policy.get("claim_requirements", {}).items():
                candidates = verified_claim_sources.get(claim, [])
                required_roles = set(requirement.get("required_roles", []))
                eligible = [entry for entry in candidates if not required_roles or set(entry.get("roles", [])) & required_roles]
                if len(eligible) < requirement.get("minimum_verified_sources", 0):
                    add_issue(issues, "error", "SOURCE_CLAIM_MIN", f"{base}.provenance.sources", f"Claim {claim!r} lacks the required number of verified authoritative sources.")
                if is_risky:
                    groups = {entry.get("independence_group") for entry in eligible if entry.get("independence_group")}
                    if len(groups) < requirement.get("minimum_independent_sources_when_risky", 0):
                        add_issue(issues, "error", "SOURCE_CLAIM_INDEPENDENCE", f"{base}.provenance.sources", f"Risky claim {claim!r} lacks independent source groups.")

            # Presence-sensitive evidence binding: do not allow a learner-facing
            # field to survive with only a generic/adjacent claim. Architecture
            # proof profiles that explicitly do not require verified sources are
            # intentionally exempt.
            if source_policy.get("require_verified_source", False):
                for field_path, binding in LEARNER_FIELD_CLAIM_BINDINGS.items():
                    container = unit
                    for segment in field_path:
                        if not isinstance(container, dict) or segment not in container:
                            container = None
                            break
                        container = container[segment]
                    if not nonempty(container):
                        continue
                    claim = binding["claim"]
                    candidates = verified_claim_sources.get(claim, [])
                    required_roles = set(binding.get("required_roles", set()))
                    eligible = [entry for entry in candidates if not required_roles or set(entry.get("roles", [])) & required_roles]
                    if len(eligible) < binding.get("minimum_verified_sources", 1):
                        dotted = ".".join(field_path)
                        add_issue(issues, "error", "SOURCE_FIELD_CLAIM_MIN", f"{base}.{dotted}", f"Learner-facing field {dotted!r} requires an explicit verified {claim!r} claim from an approved German authority.")

    if previous is not None:
        compare_identity(previous, dataset, issues)

    errors = sum(item["severity"] == "error" for item in issues)
    warnings = sum(item["severity"] == "warning" for item in issues)
    return {
        "validator_version": VALIDATOR_VERSION,
        "contract_version": dataset.get("contract_version"),
        "profile_id": profile.get("profile_id"),
        "counts": {
            "learning_units": len(units),
            "learning_units_by_type": dict(sorted(type_counts.items())),
            "examples": total_examples,
            "unique_example_ids": len(example_ids),
            "duplicate_example_ids": len(duplicate_example_ids),
            "translations_by_language": dict(sorted(translation_counts.items())),
            "connections_by_kind": dict(sorted(connection_counts.items())),
            "errors": errors,
            "warnings": warnings,
        },
        "structural_typed_status": "PASS" if errors == 0 else "FAIL",
        "linguistic_status": "NOT_RUN",
        "source_policy_status": "PASS" if not any(item["severity"] == "error" and item["code"].startswith("SOURCE_") for item in issues) else "FAIL",
        "source_truth_status": "NOT_VERIFIED_BY_THIS_VALIDATOR",
        "issues": issues,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--type-rules", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--source-registry", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = validate_dataset(
        load_json(args.dataset),
        load_json(args.profile),
        load_type_rules(args.type_rules),
        load_json(args.previous) if args.previous else None,
        load_json(args.source_registry),
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["structural_typed_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
