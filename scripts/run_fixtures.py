#!/usr/bin/env python3
"""Conformance test runner for APP.md schema fixtures.

Reads fixtures/conformance.json (the corpus contract) and:
  - verifies every listed fixture exists with the pinned SHA-256
  - verifies the filesystem has no fixtures outside the index
  - validates every valid/*.yaml against schema/app.v1.schema.json (must pass)
  - validates every invalid/*.yaml (must fail) AND the failure path must
    contain at least one of the index's expected_paths for that case, with
    the indexed JSON Schema keyword observed at that path
  - verifies every direct schema constraint path has at least one invalid
    fixture expected_path witness
  - validates the index contract before trusting fixture metadata
  - validates public example/template manifests with the reference parser
  - validates public receipt packet examples for the portable proof-loop fields
    and basic example quality

Exits 0 only on a clean run.

Python: 3.10+
Deps: PyYAML>=6,<7 ; jsonschema>=4,<5 ; tzdata>=2024.1
Run from repo root: python3 scripts/run_fixtures.py
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

import yaml
from jsonschema import Draft202012Validator
import validate as validator_cli

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "fixtures" / "conformance.json"
SCHEMA_ALIAS = ROOT / "schema" / "app.schema.json"
SCHEMA_V1 = ROOT / "schema" / "app.v1.schema.json"
CONSTRAINT_KEYS = {
    "$ref",
    "type",
    "enum",
    "const",
    "pattern",
    "minimum",
    "maximum",
    "minLength",
    "maxLength",
}
HEX_DIGITS = set("0123456789abcdef")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _extract_quoted(message: str) -> str | None:
    parts = message.split("'", 2)
    return parts[1] if len(parts) >= 2 else None


def normalize_path(error) -> list[str]:
    """Render a jsonschema error as one or more implementation-agnostic paths.

    Some validators don't put the offending field in absolute_path:
      - required          → append the missing field
      - additionalProperties → append the unknown field
      - not (used for "field forbidden under this runtime") → walk the
        violated `not` sub-schema and surface every field name it forbids
    """
    parent = ".".join(str(p) for p in error.absolute_path)
    out: list[str] = []
    keyword = error.validator

    if keyword in ("required", "additionalProperties"):
        field = _extract_quoted(error.message)
        if field:
            out.append(f"{parent}.{field}" if parent else field)
    elif keyword == "not":
        not_clause = error.schema.get("not", {})
        clauses = not_clause.get("anyOf", [not_clause])
        for sub in clauses:
            for f in sub.get("required", []):
                out.append(f"{parent}.{f}" if parent else f)

    if not out:
        out.append(parent or "<root>")
    return out


def all_error_markers(errors) -> list[tuple[str, list[str]]]:
    out = []
    for e in errors:
        out.append((str(e.validator), normalize_path(e)))
        out.extend(all_error_markers(e.context))
    return out


def path_matches(paths: list[str], expected_paths: list[str]) -> bool:
    return any(exp in pth for exp in expected_paths for pth in paths)


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX_DIGITS


def validate_index_contract(index: object, failures: list[str]) -> None:
    if not isinstance(index, dict):
        failures.append("malformed index: top-level JSON value must be an object")
        return

    if index.get("schema") != "schema/app.v1.schema.json":
        failures.append("malformed index: schema must be schema/app.v1.schema.json")

    seen_paths: set[str] = set()
    for section in ("valid", "invalid"):
        entries = index.get(section)
        if not isinstance(entries, list):
            failures.append(f"malformed index: {section} must be a list")
            continue
        for pos, entry in enumerate(entries):
            if not isinstance(entry, dict):
                failures.append(f"malformed index: {section}[{pos}] must be an object")
                continue
            path = entry.get("path")
            if not isinstance(path, str) or not path.startswith(f"fixtures/{section}/") or not path.endswith(".yaml"):
                failures.append(f"malformed index: {section}[{pos}].path has wrong fixture location")
            elif path in seen_paths:
                failures.append(f"duplicate fixture path in index: {path}")
            else:
                seen_paths.add(path)
            if not is_sha256(entry.get("sha256")):
                failures.append(f"malformed index: {section}[{pos}].sha256 must be lowercase SHA-256")
            if section == "invalid":
                keyword = entry.get("keyword")
                expected_paths = entry.get("expected_paths")
                if not isinstance(keyword, str) or not keyword:
                    failures.append(f"malformed index: invalid[{pos}].keyword must be a non-empty string")
                if not (
                    isinstance(expected_paths, list)
                    and expected_paths
                    and all(isinstance(p, str) and p for p in expected_paths)
                ):
                    failures.append(
                        f"malformed index: invalid[{pos}].expected_paths must be a non-empty string list"
                    )


def collect_schema_constraint_paths(schema_node: dict, name: str = "") -> set[str]:
    paths: set[str] = set()
    if name and any(key in schema_node for key in CONSTRAINT_KEYS):
        paths.add(name)

    properties = schema_node.get("properties")
    if isinstance(properties, dict):
        for prop, child in properties.items():
            if isinstance(child, dict):
                child_name = f"{name}.{prop}" if name else prop
                paths.update(collect_schema_constraint_paths(child, child_name))

    if schema_node.get("type") == "array" and isinstance(schema_node.get("items"), dict):
        paths.update(collect_schema_constraint_paths(schema_node["items"], f"{name}.0"))

    return paths


def validate_schema_path_coverage(index: dict, schema: dict, failures: list[str]) -> None:
    constraint_paths = collect_schema_constraint_paths(schema)
    expected_paths = {
        path
        for entry in index["invalid"]
        for path in entry.get("expected_paths", [])
    }
    missing = sorted(constraint_paths - expected_paths)
    print(f"\n== schema path coverage ({len(constraint_paths)}) ==")
    if missing:
        failures.append(f"missing direct invalid fixture coverage for schema paths: {missing}")
        print(f"  FAIL missing direct invalid fixture coverage: {missing}")
    else:
        print("  pass all direct schema constraint paths have invalid fixture coverage")


def parser_smoke_cases() -> list[dict[str, object]]:
    return [
        {
            "name": "unclosed-frontmatter",
            "src": "---\nschema_version: 1\nname: unclosed\nslug: unclosed\naccess: private\nruntime: local\nvault: local\n",
            "error": "frontmatter is not closed",
        },
        {
            "name": "missing-frontmatter-app-md",
            "src": "schema_version: 1\nname: missing frontmatter\nslug: missing-frontmatter\naccess: private\nruntime: local\nvault: local\n",
            "error": "frontmatter is missing",
            "require_frontmatter": True,
        },
        {
            "name": "duplicate-key",
            "src": "schema_version: 1\nname: duplicate\nslug: duplicate\nslug: duplicate-two\naccess: private\nruntime: local\nvault: local\n",
            "error": "duplicate YAML key",
        },
        {
            "name": "anchors-aliases",
            "src": "schema_version: 1\nname: alias\nslug: alias\naccess: private\nruntime: local\nvault: local\nsecrets: &names []\nskills: *names\n",
            "error": "YAML anchors",
        },
        {
            "name": "tags",
            "src": "schema_version: 1\nname: tagged\nslug: tagged\naccess: private\nruntime: local\nvault: local\nx: !Foo tagged\n",
            "error": "YAML tags",
        },
        {
            "name": "date-scalar",
            "src": "schema_version: 1\nname: date scalar\nslug: date-scalar\naccess: private\nruntime: local\nvault: local\ncreated_at: 2026-05-05\n",
            "error": "date is not JSON-compatible",
        },
        {
            "name": "nan-scalar",
            "src": "schema_version: 1\nname: nan scalar\nslug: nan-scalar\naccess: private\nruntime: local\nvault: local\nscore: .nan\n",
            "error": "NaN and Infinity",
        },
        {
            "name": "bad-timezone",
            "src": "schema_version: 1\nname: bad timezone\nslug: bad-timezone\naccess: private\nruntime: local\nvault: local\ntimezone: Mars/Base\n",
            "error": "valid IANA timezone",
        },
    ]


def validate_parser_smoke(failures: list[str]) -> None:
    print("\n== parser-level smoke ==")
    for case in parser_smoke_cases():
        expected_error = str(case["error"])
        try:
            manifest = validator_cli.extract_frontmatter(
                str(case["src"]),
                require_frontmatter=bool(case.get("require_frontmatter")),
            )
            parser_errors = validator_cli.parser_lints(manifest)
            if parser_errors:
                message = "; ".join(msg for _, msg in parser_errors)
                raise ValueError(message)
        except (yaml.YAMLError, ValueError) as exc:
            message = str(exc)
            if expected_error in message:
                print(f"  reject {case['name']} ({expected_error})")
            else:
                failures.append(f"parser/{case['name']} failed with wrong error: {message}")
                print(f"  FAIL {case['name']}: {message}")
            continue
        failures.append(f"parser/{case['name']} unexpectedly passed")
        print(f"  FAIL {case['name']}: passed")

    valid = "schema_version: 1\nname: raw yaml\nslug: raw-yaml\naccess: private\nruntime: local\nvault: local\n"
    manifest = validator_cli.extract_frontmatter(valid)
    if validator_cli.parser_lints(manifest):
        failures.append("parser/raw-yaml unexpectedly failed parser lints")
        print("  FAIL raw-yaml: parser lint failure")
    else:
        print("  pass raw-yaml")

    worked = validator_cli.extract_frontmatter(
        "---\nschema_version: 1\nname: x\nslug: x\naccess: private\nruntime: local\nvault: local\n---\n"
    )
    expected = "eb9beb40790eeab0329641e230043e058e5819dfb5d526e81e7997af35b978a3"
    got = validator_cli.spec_digest(worked)
    if got == expected:
        print("  pass spec-digest-worked-example")
    else:
        failures.append(f"parser/spec-digest-worked-example expected {expected}, got {got}")
        print(f"  FAIL spec-digest-worked-example: got {got}")

    with_digest = dict(worked)
    with_digest["spec_digest"] = "0" * 64
    if validator_cli.spec_digest(with_digest) == got:
        print("  pass spec-digest-self-exclusion")
    else:
        failures.append("parser/spec-digest-self-exclusion changed the digest")
        print("  FAIL spec-digest-self-exclusion")


def public_manifest_paths() -> list[Path]:
    paths: list[Path] = []
    for base in (ROOT / "examples", ROOT / "templates"):
        if not base.exists():
            continue
        paths.extend(base.rglob("APP.md"))
        paths.extend(base.rglob("*.yaml"))
        paths.extend(base.rglob("*.yml"))
    return sorted(set(paths))


def validate_public_manifests(schema_validator: Draft202012Validator, failures: list[str]) -> None:
    paths = public_manifest_paths()
    print(f"\n== examples/templates ({len(paths)}) ==")
    for p in paths:
        rel = p.relative_to(ROOT)
        try:
            manifest = validator_cli.extract_frontmatter(
                p.read_text(encoding="utf-8"),
                require_frontmatter=p.name.lower() == "app.md" or p.suffix.lower() in {".md", ".markdown"},
            )
        except (yaml.YAMLError, ValueError) as exc:
            failures.append(f"{rel} failed parse: {exc}")
            print(f"  FAIL {rel}: parse error: {exc}")
            continue

        errors = sorted(schema_validator.iter_errors(manifest), key=lambda e: list(e.absolute_path))
        if errors:
            failures.append(f"{rel} failed schema validation: {errors[0].message}")
            print(f"  FAIL {rel}: {errors[0].message}")
            continue

        parser_errors = validator_cli.parser_lints(manifest)
        if parser_errors:
            path, message = parser_errors[0]
            failures.append(f"{rel} failed parser lint at {path}: {message}")
            print(f"  FAIL {rel}: {path}: {message}")
            continue

        print(f"  pass {rel}")


RECEIPT_REQUIRED_FIELDS = {
    "app_slug",
    "run_id",
    "status",
    "started_at",
    "completed_at",
    "inputs_summary",
    "outputs",
    "events",
    "owner",
    "verifier",
    "decision",
    "learned",
}
RECEIPT_STATUSES = {"ok", "failed", "blocked", "needs_approval"}
RECEIPT_STRING_FIELDS = RECEIPT_REQUIRED_FIELDS - {"outputs", "events"}


def receipt_example_paths() -> list[Path]:
    roots = [ROOT / "examples", ROOT / "templates"]
    paths: list[Path] = []
    for base in roots:
        if base.exists():
            paths.extend(base.rglob("receipts/*.json"))
    return sorted(paths)


def validate_receipt_examples(failures: list[str]) -> None:
    paths = receipt_example_paths()
    print(f"\n== receipt examples ({len(paths)}) ==")
    if not paths:
        failures.append("no public receipt packet examples found")
        print("  FAIL no public receipt packet examples found")
        return

    for p in paths:
        rel = p.relative_to(ROOT)
        try:
            receipt = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{rel} is invalid JSON at line {exc.lineno}, column {exc.colno}")
            print(f"  FAIL {rel}: invalid JSON")
            continue

        if not isinstance(receipt, dict):
            failures.append(f"{rel} must be a JSON object")
            print(f"  FAIL {rel}: not an object")
            continue

        missing = sorted(RECEIPT_REQUIRED_FIELDS - receipt.keys())
        if missing:
            failures.append(f"{rel} missing receipt fields: {', '.join(missing)}")
            print(f"  FAIL {rel}: missing {', '.join(missing)}")
            continue

        status = receipt.get("status")
        if status not in RECEIPT_STATUSES:
            failures.append(f"{rel} status must be one of {sorted(RECEIPT_STATUSES)}")
            print(f"  FAIL {rel}: invalid status {status!r}")
            continue

        bad_strings = [
            field
            for field in sorted(RECEIPT_STRING_FIELDS)
            if not isinstance(receipt.get(field), str) or not receipt.get(field).strip()
        ]
        if bad_strings:
            failures.append(f"{rel} receipt fields must be non-empty strings: {', '.join(bad_strings)}")
            print(f"  FAIL {rel}: empty string fields {', '.join(bad_strings)}")
            continue

        events = receipt.get("events")
        if not isinstance(events, list):
            failures.append(f"{rel} events must be a list")
            print(f"  FAIL {rel}: events not list")
            continue
        if any(not isinstance(event, dict) for event in events):
            failures.append(f"{rel} events must contain only objects")
            print(f"  FAIL {rel}: event not object")
            continue

        outputs = receipt.get("outputs")
        if not isinstance(outputs, list):
            failures.append(f"{rel} outputs must be a list")
            print(f"  FAIL {rel}: outputs not list")
            continue
        if any(not isinstance(output, dict) for output in outputs):
            failures.append(f"{rel} outputs must contain only objects")
            print(f"  FAIL {rel}: output not object")
            continue

        print(f"  pass {rel}")


def main() -> int:
    if not INDEX.exists():
        print(f"FAIL: missing index {INDEX.relative_to(ROOT)}")
        return 1
    try:
        index = json.loads(INDEX.read_text())
    except json.JSONDecodeError as exc:
        print("== index contract ==")
        print(f"  FAIL malformed index: invalid JSON at line {exc.lineno}, column {exc.colno}")
        return 1

    index_failures: list[str] = []
    validate_index_contract(index, index_failures)
    print("== index contract ==")
    if index_failures:
        for failure in index_failures:
            print(f"  FAIL {failure}")
        return 1
    print("  pass conformance.json metadata shape")

    schema_path = ROOT / index["schema"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    failures: list[str] = []
    if not SCHEMA_ALIAS.exists():
        failures.append("missing stable schema alias schema/app.schema.json")
    else:
        if SCHEMA_ALIAS.read_bytes() != SCHEMA_V1.read_bytes():
            failures.append("schema/app.schema.json must match schema/app.v1.schema.json byte-for-byte")
        alias = json.loads(SCHEMA_ALIAS.read_text())
        if alias.get("$id") != "https://atris.ai/schema/app.v1.schema.json":
            failures.append("schema/app.schema.json must resolve to the canonical v1 schema body")
        try:
            Draft202012Validator.check_schema(alias)
        except Exception as exc:
            failures.append(f"schema/app.schema.json is not a valid Draft 2020-12 schema: {exc}")

    listed: dict[str, str] = {}
    for entry in index["valid"]:
        listed[entry["path"]] = entry["sha256"]
    for entry in index["invalid"]:
        listed[entry["path"]] = entry["sha256"]

    for rel, expected_hash in listed.items():
        p = ROOT / rel
        if not p.exists():
            failures.append(f"index references missing file {rel}")
            continue
        got = sha256(p)
        if got != expected_hash:
            failures.append(f"sha256 drift on {rel}: index={expected_hash[:12]}… disk={got[:12]}…")

    fs_yamls = set()
    for sub in ("fixtures/valid", "fixtures/invalid"):
        for p in (ROOT / sub).glob("*.yaml"):
            fs_yamls.add(str(p.relative_to(ROOT)))
    listed_yamls = set(listed.keys())
    orphan = sorted(fs_yamls - listed_yamls)
    if orphan:
        failures.append(f"fixtures on disk but not in index: {orphan}")
    missing = sorted(listed_yamls - fs_yamls)
    if missing:
        failures.append(f"fixtures in index but not on disk: {missing}")

    print(f"== valid ({len(index['valid'])}) ==")
    for entry in index["valid"]:
        p = ROOT / entry["path"]
        if not p.exists():
            continue
        manifest = yaml.safe_load(p.read_text())
        errors = list(validator.iter_errors(manifest))
        if errors:
            failures.append(f"valid/{p.name} unexpectedly failed: {errors[0].message}")
            print(f"  FAIL {p.name}: {errors[0].message}")
        else:
            print(f"  pass {p.name}")

    print(f"\n== invalid ({len(index['invalid'])}) ==")
    for entry in index["invalid"]:
        p = ROOT / entry["path"]
        expected = entry["expected_paths"]
        if not p.exists():
            continue
        manifest = yaml.safe_load(p.read_text())
        errors = list(validator.iter_errors(manifest))
        if not errors:
            failures.append(f"invalid/{p.name} unexpectedly passed schema")
            print(f"  FAIL {p.name}: passed (should fail at {expected})")
            continue
        markers = all_error_markers(errors)
        paths = [path for _, marker_paths in markers for path in marker_paths]
        if not path_matches(paths, expected):
            failures.append(
                f"invalid/{p.name} failed but no path matched any of {expected}; got paths={paths}"
            )
            print(f"  FAIL {p.name}: expected one of {expected}, got {paths}")
            continue
        keyword_matches = [
            (keyword, marker_paths)
            for keyword, marker_paths in markers
            if keyword == entry["keyword"] and path_matches(marker_paths, expected)
        ]
        if not keyword_matches:
            got = sorted({keyword for keyword, marker_paths in markers if path_matches(marker_paths, expected)})
            failures.append(
                f"invalid/{p.name} failed at {expected} but keyword mismatch: "
                f"expected {entry['keyword']!r}, got {got}"
            )
            print(f"  FAIL {p.name}: expected keyword {entry['keyword']!r}, got {got}")
        else:
            matched_paths = keyword_matches[0][1]
            matched = next(exp for exp in expected if any(exp in pth for pth in matched_paths))
            print(f"  reject {p.name} (matched {matched!r}, keyword={entry['keyword']})")

    validate_schema_path_coverage(index, schema, failures)
    validate_parser_smoke(failures)
    validate_public_manifests(validator, failures)
    validate_receipt_examples(failures)

    print(f"\n{len(failures)} failures")
    if failures:
        for f in failures:
            print(f"  - {f}")
        return 1
    print("OK: all conformance checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
