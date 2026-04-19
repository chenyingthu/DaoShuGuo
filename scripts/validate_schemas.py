#!/usr/bin/env python3
"""Project-local schema validator.

Checks:
1. Required fields
2. Simple type validation
3. Controlled enum validation
4. Nested substructure required fields
5. Reference existence
6. A small set of semantic compatibility rules
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


OBJECT_TYPE_TO_PREFIX = {
    "task": "task",
    "baseline": "baseline",
    "evaluator": "evaluator",
    "run": "run",
    "skill": "skill",
    "cognition": "cognition",
    "agent_trace": "agent_trace",
    "prompt_observation": "prompt_observation",
    "taste_assessment": "taste",
    "evidence_bundle": "evidence",
    "strategy_comparison": "comparison",
    "report": "report",
}

PREFIX_TO_OBJECT_TYPE = {v: k for k, v in OBJECT_TYPE_TO_PREFIX.items()}

GRADE_TO_ALLOWED_REPORT_TYPES = {
    "tuoyu": {"paper_draft", "technical_note"},
    "zhuoshi": {"paper_draft", "technical_note"},
    "diaomu": {"technical_note", "experiment_record"},
    "huimo": {"discussion_memo"},
}


@dataclass
class ValidationError:
    source: str
    message: str


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a mapping")
    return data


def collect_schema_files(schema_root: Path) -> list[Path]:
    groups = ["core", "assets", "quality", "reporting"]
    files: list[Path] = []
    for group in groups:
        files.extend(sorted((schema_root / group).glob("*.yaml")))
    return files


def collect_sample_files(schema_root: Path) -> list[Path]:
    return sorted((schema_root / "samples").glob("*.yaml"))


def schema_map(schema_files: list[Path]) -> dict[str, dict[str, Any]]:
    by_object_type: dict[str, dict[str, Any]] = {}
    for path in schema_files:
        schema = load_yaml(path)
        object_type = schema.get("object_type")
        if not isinstance(object_type, str):
            raise ValueError(f"{path} missing object_type")
        by_object_type[object_type] = schema
    return by_object_type


def object_map(sample_files: list[Path]) -> dict[str, dict[str, Any]]:
    objects: dict[str, dict[str, Any]] = {}
    for path in sample_files:
        obj = load_yaml(path)
        object_id = obj.get("object_id")
        if not isinstance(object_id, str):
            raise ValueError(f"{path} missing object_id")
        objects[object_id] = obj
    return objects


def validate_required_fields(data: dict[str, Any], required_fields: list[str], source: str):
    errors: list[ValidationError] = []
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(ValidationError(source, f"missing required field `{field}`"))
    return errors


def is_iso_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def type_matches(spec_type: str, value: Any) -> bool:
    if spec_type == "string":
        return isinstance(value, str)
    if spec_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if spec_type == "datetime":
        return isinstance(value, str) and is_iso_datetime(value)
    if spec_type == "object":
        return isinstance(value, dict)
    if spec_type == "array[string]":
        return isinstance(value, list) and all(isinstance(v, str) for v in value)
    if spec_type == "array[object]":
        return isinstance(value, list) and all(isinstance(v, dict) for v in value)
    if spec_type == "enum":
        return True
    return True


def candidate_subschema_name(field_name: str, substructures: dict[str, Any]) -> str | None:
    if field_name in substructures:
        return field_name
    if field_name.endswith("s") and field_name[:-1] in substructures:
        return field_name[:-1]
    return None


def validate_value_against_spec(
    value: Any,
    spec: dict[str, Any],
    source: str,
    field_name: str,
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    spec_type = spec.get("type")
    if spec_type and not type_matches(spec_type, value):
        errors.append(
            ValidationError(
                source,
                f"field `{field_name}` expected type `{spec_type}` but got `{type(value).__name__}`",
            )
        )
        return errors
    if spec_type == "enum":
        allowed = spec.get("allowed", [])
        if value not in allowed:
            errors.append(
                ValidationError(
                    source,
                    f"field `{field_name}` has invalid enum value `{value}`; allowed={allowed}",
                )
            )
    return errors


def validate_substructure(data: dict[str, Any], schema: dict[str, Any], source: str):
    errors: list[ValidationError] = []
    errors.extend(validate_required_fields(data, schema.get("required_fields", []), source))
    field_specs = schema.get("field_specs", {})

    for field_name, spec in field_specs.items():
        if field_name not in data:
            continue
        value = data[field_name]
        errors.extend(validate_value_against_spec(value, spec, source, field_name))
        nested_required = spec.get("required_fields")
        if nested_required and isinstance(value, dict):
            errors.extend(validate_required_fields(value, nested_required, f"{source}:{field_name}"))
    return errors


def validate_object(data: dict[str, Any], schema: dict[str, Any], source: str):
    errors: list[ValidationError] = []
    errors.extend(validate_required_fields(data, schema.get("required_fields", []), source))

    field_specs = schema.get("field_specs", {})
    substructures = schema.get("substructures", {})

    for field_name, spec in field_specs.items():
        if field_name not in data:
            continue
        value = data[field_name]
        errors.extend(validate_value_against_spec(value, spec, source, field_name))

        spec_type = spec.get("type")
        if spec_type == "object" and isinstance(value, dict):
            sub_name = candidate_subschema_name(field_name, substructures)
            if sub_name:
                errors.extend(
                    validate_substructure(value, substructures[sub_name], f"{source}:{field_name}")
                )

        if spec_type == "array[object]" and isinstance(value, list):
            sub_name = candidate_subschema_name(field_name, substructures)
            if sub_name:
                for idx, item in enumerate(value):
                    errors.extend(
                        validate_substructure(
                            item, substructures[sub_name], f"{source}:{field_name}[{idx}]"
                        )
                    )

    errors.extend(validate_object_identity(data, source))
    return errors


def validate_object_identity(data: dict[str, Any], source: str):
    errors: list[ValidationError] = []
    object_type = data.get("object_type")
    object_id = data.get("object_id")
    if not isinstance(object_type, str) or not isinstance(object_id, str):
        return errors
    expected_prefix = OBJECT_TYPE_TO_PREFIX.get(object_type)
    if expected_prefix and not object_id.startswith(expected_prefix + "."):
        errors.append(
            ValidationError(
                source,
                f"object_id `{object_id}` does not match expected prefix `{expected_prefix}.` for object_type `{object_type}`",
            )
        )
    return errors


def looks_like_object_id(value: str) -> bool:
    if "." not in value:
        return False
    prefix = value.split(".", 1)[0]
    return prefix in PREFIX_TO_OBJECT_TYPE


def iter_references(node: Any, path: str = ""):
    if isinstance(node, dict):
        if "object_id" in node and isinstance(node["object_id"], str):
            yield path + ".object_id", node["object_id"]
        for key, value in node.items():
            next_path = f"{path}.{key}" if path else key
            if key.endswith("_ref") and isinstance(value, str):
                yield next_path, value
            elif key.endswith("_refs") and isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, str):
                        yield f"{next_path}[{idx}]", item
                    elif isinstance(item, dict):
                        yield from iter_references(item, f"{next_path}[{idx}]")
            else:
                yield from iter_references(value, next_path)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            yield from iter_references(item, f"{path}[{idx}]")


def validate_references(data: dict[str, Any], objects_by_id: dict[str, dict[str, Any]], source: str):
    errors: list[ValidationError] = []
    for ref_path, ref_value in iter_references(data):
        if not looks_like_object_id(ref_value):
            continue
        if ref_value not in objects_by_id:
            errors.append(
                ValidationError(source, f"reference `{ref_path}` points to missing object `{ref_value}`")
            )
    return errors


def validate_semantics(objects_by_id: dict[str, dict[str, Any]]) -> list[ValidationError]:
    errors: list[ValidationError] = []

    for object_id, obj in objects_by_id.items():
        object_type = obj.get("object_type")

        if object_type == "report":
            taste_ref = obj.get("taste_assessment_ref")
            report_type = obj.get("report_type")
            if isinstance(taste_ref, str) and taste_ref in objects_by_id:
                taste = objects_by_id[taste_ref]
                grade = taste.get("grade")
                allowed = GRADE_TO_ALLOWED_REPORT_TYPES.get(grade)
                if allowed and report_type not in allowed:
                    errors.append(
                        ValidationError(
                            object_id,
                            f"report_type `{report_type}` is incompatible with taste grade `{grade}`; allowed={sorted(allowed)}",
                        )
                    )

        if object_type == "taste_assessment":
            grade = obj.get("grade")
            recommended = obj.get("recommended_report_type")
            if grade in GRADE_TO_ALLOWED_REPORT_TYPES and recommended is not None:
                allowed = GRADE_TO_ALLOWED_REPORT_TYPES[grade]
                if recommended not in allowed:
                    errors.append(
                        ValidationError(
                            object_id,
                            f"recommended_report_type `{recommended}` is incompatible with grade `{grade}`; allowed={sorted(allowed)}",
                        )
                    )

        if object_type == "cognition":
            cognition_type = obj.get("cognition_type")
            evidence_refs = obj.get("evidence_refs", [])
            if cognition_type == "stable" and not evidence_refs:
                errors.append(
                    ValidationError(object_id, "stable cognition must include non-empty evidence_refs")
                )

    return errors


def validate_samples(schema_root: Path) -> list[ValidationError]:
    schema_files = collect_schema_files(schema_root)
    sample_files = collect_sample_files(schema_root)
    schemas = schema_map(schema_files)
    objects = object_map(sample_files)
    errors: list[ValidationError] = []

    for sample_path in sample_files:
        data = load_yaml(sample_path)
        object_type = data.get("object_type")
        if object_type not in schemas:
            errors.append(
                ValidationError(str(sample_path), f"no schema found for object_type `{object_type}`")
            )
            continue
        schema = schemas[object_type]
        errors.extend(validate_object(data, schema, str(sample_path)))
        errors.extend(validate_references(data, objects, str(sample_path)))

    errors.extend(validate_semantics(objects))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate local schema samples.")
    parser.add_argument(
        "--schema-root",
        default="schemas",
        help="Root directory containing schema specs and samples.",
    )
    args = parser.parse_args()

    schema_root = Path(args.schema_root)
    errors = validate_samples(schema_root)

    if errors:
        print("Schema validation failed:\n")
        for err in errors:
            print(f"- {err.source}: {err.message}")
        return 1

    print("Schema validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
