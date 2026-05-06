#!/usr/bin/env python3
"""Reference validator for one APP.md manifest. Copy this as your starting parser.

Usage:  python3 scripts/validate.py <APP.md | manifest.yaml | ->
Exit:   0 = valid (canonical JSON on stdout)
        1 = usage / file error
        2 = invalid (one `<path>: <msg>` per line on stderr)
Python: 3.10+
Deps:   PyYAML>=6,<7 ; jsonschema>=4,<5 ; tzdata>=2024.1
"""
from __future__ import annotations
import hashlib
import json, math, sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import yaml
from jsonschema import Draft202012Validator
from yaml.tokens import AliasToken, AnchorToken, TagToken

SCHEMA_ALIAS = Path(__file__).resolve().parents[1] / "schema" / "app.schema.json"


class AppYamlLoader(yaml.SafeLoader):
    pass


def construct_json_mapping(loader: AppYamlLoader, node, deep=False) -> dict:
    loader.flatten_mapping(node)
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ValueError("YAML object keys must be strings")
        if key in seen:
            raise ValueError(f"duplicate YAML key: {key}")
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


AppYamlLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_json_mapping,
)


def load_manifest_yaml(src: str) -> dict:
    for token in yaml.scan(src):
        if isinstance(token, AnchorToken):
            raise ValueError("YAML anchors are not supported")
        if isinstance(token, AliasToken):
            raise ValueError("YAML aliases are not supported")
        if isinstance(token, TagToken):
            raise ValueError("YAML tags are not supported")
    loaded = yaml.load(src, Loader=AppYamlLoader) or {}
    if not isinstance(loaded, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return loaded


def extract_frontmatter(text: str, *, require_frontmatter: bool = False) -> dict:
    lines = text.splitlines()
    if lines and lines[0].rstrip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), -1)
        if end != -1:
            return load_manifest_yaml("\n".join(lines[1:end]))
        raise ValueError("APP.md frontmatter is not closed with '---'")
    if require_frontmatter:
        raise ValueError("APP.md frontmatter is missing; first line must be '---'")
    return load_manifest_yaml(text)


def normalize_path(error) -> str:
    parts = [str(p) for p in error.absolute_path]
    if error.validator in ("required", "additionalProperties"):
        q = error.message.split("'", 2)
        if len(q) >= 2:
            parts.append(q[1])
    return ".".join(parts) if parts else "<root>"


def parser_lints(manifest: dict) -> list[tuple[str, str]]:
    """Rules from SPEC.md that JSON Schema cannot express."""
    errors = json_value_lints(manifest)
    tz = manifest.get("timezone")
    if not tz:
        return errors
    try:
        ZoneInfo(tz)
    except ZoneInfoNotFoundError:
        errors.append(("timezone", f"{tz!r} is not a valid IANA timezone"))
    return errors


def json_value_lints(value, path: str = "<root>") -> list[tuple[str, str]]:
    if value is None or isinstance(value, (str, bool)):
        return []
    if isinstance(value, int):
        return []
    if isinstance(value, float):
        if math.isfinite(value):
            return []
        return [(path, "NaN and Infinity are not JSON-compatible")]
    if isinstance(value, list):
        errors: list[tuple[str, str]] = []
        for idx, item in enumerate(value):
            errors.extend(json_value_lints(item, f"{path}[{idx}]"))
        return errors
    if isinstance(value, dict):
        errors = []
        for key, item in value.items():
            child = key if path == "<root>" else f"{path}.{key}"
            errors.extend(json_value_lints(item, child))
        return errors
    return [(path, f"{type(value).__name__} is not JSON-compatible")]


def canonical_json(value) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("NaN and Infinity are not JSON-compatible")
        return jcs_float(value)
    if isinstance(value, list):
        return "[" + ",".join(canonical_json(item) for item in value) + "]"
    if isinstance(value, dict):
        items = []
        for key in sorted(value):
            items.append(canonical_json(key) + ":" + canonical_json(value[key]))
        return "{" + ",".join(items) + "}"
    raise ValueError(f"{type(value).__name__} is not JSON-compatible")


def spec_digest(manifest: dict) -> str:
    canonical_record = {k: v for k, v in manifest.items() if k != "spec_digest"}
    canonical = canonical_json(canonical_record).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def output_manifest(manifest: dict) -> dict:
    out = dict(manifest)
    out["spec_digest"] = spec_digest(manifest)
    return out


def _decimal_from_repr(raw: str) -> str:
    sign = ""
    if raw.startswith("-"):
        sign = "-"
        raw = raw[1:]
    mantissa, exp_text = raw.lower().split("e", 1)
    exp = int(exp_text)
    if "." in mantissa:
        head, tail = mantissa.split(".", 1)
        digits = head + tail
        point = len(head) + exp
    else:
        digits = mantissa
        point = len(mantissa) + exp
    digits = digits.lstrip("0") or "0"
    if point <= 0:
        out = "0." + ("0" * abs(point)) + digits
    elif point >= len(digits):
        out = digits + ("0" * (point - len(digits)))
    else:
        out = digits[:point] + "." + digits[point:]
    if "." in out:
        out = out.rstrip("0").rstrip(".")
    return sign + out


def _exponent_from_repr(raw: str) -> str:
    sign = ""
    if raw.startswith("-"):
        sign = "-"
        raw = raw[1:]
    if "e" in raw.lower():
        mantissa, exp_text = raw.lower().split("e", 1)
        exp = int(exp_text)
        mantissa = mantissa.rstrip("0").rstrip(".")
    else:
        plain = raw.rstrip("0").rstrip(".") if "." in raw else raw
        digits = plain.replace(".", "")
        before = plain.find(".")
        exp = (len(plain) if before == -1 else before) - 1
        mantissa = digits[0] + (("." + digits[1:]) if len(digits) > 1 else "")
        mantissa = mantissa.rstrip("0").rstrip(".")
    exp_sign = "+" if exp >= 0 else ""
    return f"{sign}{mantissa}e{exp_sign}{exp}"


def jcs_float(value: float) -> str:
    if value == 0:
        return "0"
    if value.is_integer() and abs(value) < 1e21:
        return str(int(value))
    raw = repr(value)
    magnitude = abs(value)
    if 1e-6 <= magnitude < 1e21:
        return _decimal_from_repr(raw) if "e" in raw.lower() else raw
    return _exponent_from_repr(raw)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate.py <APP.md | manifest.yaml | ->", file=sys.stderr)
        return 1
    if argv[1] == "-":
        src = sys.stdin.read()
        require_frontmatter = False
    else:
        path = Path(argv[1])
        if not path.exists():
            print(f"error: not found: {argv[1]}", file=sys.stderr)
            return 1
        src = path.read_text(encoding="utf-8")
        require_frontmatter = path.name.lower() == "app.md" or path.suffix.lower() in {".md", ".markdown"}
    try:
        manifest = extract_frontmatter(src, require_frontmatter=require_frontmatter)
    except (yaml.YAMLError, ValueError) as exc:
        print(f"<root>: parse error: {exc}", file=sys.stderr)
        return 2
    schema = json.loads(SCHEMA_ALIAS.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(manifest), key=lambda e: list(e.absolute_path))
    if errors:
        for e in errors:
            print(f"{normalize_path(e)}: {e.message}", file=sys.stderr)
        return 2
    parser_errors = parser_lints(manifest)
    if parser_errors:
        for path, message in parser_errors:
            print(f"{path}: {message}", file=sys.stderr)
        return 2
    print(json.dumps(output_manifest(manifest), sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
