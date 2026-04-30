#!/usr/bin/env python3
"""Conformance test runner for APP.md schema fixtures.

Reads fixtures/conformance.json (the corpus contract) and:
  - verifies every listed fixture exists with the pinned SHA-256
  - verifies the filesystem has no fixtures outside the index
  - validates every valid/*.yaml against schema/app.v1.schema.json (must pass)
  - validates every invalid/*.yaml (must fail) AND the failure path must
    contain at least one of the index's expected_paths for that case

Exits 0 only on a clean run.

Deps: PyYAML>=6,<7 ; jsonschema>=4,<5
Run from repo root: python3 scripts/run_fixtures.py
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "fixtures" / "conformance.json"


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


def all_paths(errors) -> list[str]:
    out = []
    for e in errors:
        out.extend(normalize_path(e))
        out.extend(all_paths(e.context))
    return out


def main() -> int:
    if not INDEX.exists():
        print(f"FAIL: missing index {INDEX.relative_to(ROOT)}")
        return 1
    index = json.loads(INDEX.read_text())
    schema_path = ROOT / index["schema"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    failures: list[str] = []

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
        paths = all_paths(errors)
        if not any(any(exp in pth for pth in paths) for exp in expected):
            failures.append(
                f"invalid/{p.name} failed but no path matched any of {expected}; got paths={paths}"
            )
            print(f"  FAIL {p.name}: expected one of {expected}, got {paths}")
        else:
            matched = next(exp for exp in expected if any(exp in pth for pth in paths))
            print(f"  reject {p.name} (matched {matched!r}, keyword={entry['keyword']})")

    print(f"\n{len(failures)} failures")
    if failures:
        for f in failures:
            print(f"  - {f}")
        return 1
    print("OK: all fixtures conform")
    return 0


if __name__ == "__main__":
    sys.exit(main())
