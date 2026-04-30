#!/usr/bin/env python3
"""Reference validator for one APP.md manifest. Copy this as your starting parser.

Usage:  python3 scripts/validate.py <APP.md | manifest.yaml | ->
Exit:   0 = valid (canonical JSON on stdout)
        1 = usage / file error
        2 = invalid (one `<path>: <msg>` per line on stderr)
Deps:   PyYAML>=6,<7 ; jsonschema>=4,<5
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).resolve().parents[1] / "schema" / "app.v1.schema.json"


def extract_frontmatter(text: str) -> dict:
    lines = text.splitlines()
    if lines and lines[0].rstrip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), -1)
        if end != -1:
            return yaml.safe_load("\n".join(lines[1:end])) or {}
    return yaml.safe_load(text) or {}


def normalize_path(error) -> str:
    parts = [str(p) for p in error.absolute_path]
    if error.validator in ("required", "additionalProperties"):
        q = error.message.split("'", 2)
        if len(q) >= 2:
            parts.append(q[1])
    return ".".join(parts) if parts else "<root>"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate.py <APP.md | manifest.yaml | ->", file=sys.stderr)
        return 1
    if argv[1] == "-":
        src = sys.stdin.read()
    else:
        path = Path(argv[1])
        if not path.exists():
            print(f"error: not found: {argv[1]}", file=sys.stderr)
            return 1
        src = path.read_text(encoding="utf-8")
    try:
        manifest = extract_frontmatter(src)
    except (yaml.YAMLError, ValueError) as exc:
        print(f"<root>: parse error: {exc}", file=sys.stderr)
        return 2
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(manifest), key=lambda e: list(e.absolute_path))
    if errors:
        for e in errors:
            print(f"{normalize_path(e)}: {e.message}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
