# tests/test_registry_schema.py
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "registry_schema.json"
EXAMPLES_PATH = ROOT / "examples" / "registry_sample.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def collect_errors(validator, instance):
    return sorted(validator.iter_errors(instance), key=lambda e: list(e.path))


def format_errors(errors):
    lines = []
    for e in errors:
        path = ".".join(map(str, e.path)) or "<root>"
        lines.append(f"{path}: {e.message}")
    return "\n".join(lines)


def test_registry_examples_against_schema():
    schema = load_json(SCHEMA_PATH)
    examples = load_json(EXAMPLES_PATH)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert isinstance(examples, list), "registry_sample.json must be a JSON array of function records."

    all_failures = []
    for idx, entry in enumerate(examples):
        errors = collect_errors(validator, entry)
        if errors:
            msg = f"Example index {idx} (id={entry.get('id')}) failed schema validation:\n{format_errors(errors)}"
            all_failures.append(msg)

    if all_failures:
        pytest.fail("\n\n".join(all_failures))

