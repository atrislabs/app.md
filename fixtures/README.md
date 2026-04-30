# Conformance fixtures

Machine-checkable conformance corpus for `schema/app.v1.schema.json`. Any APP.md parser SHOULD pass this suite before claiming v1 schema-shape conformance.

```
fixtures/
  conformance.json   index of every fixture, pinned by SHA-256
  valid/             10 manifests that MUST validate clean
  invalid/           13 manifests that MUST fail; conformance.json names
                     the keyword + expected_paths each case asserts
```

## Run

From the repo root:

```bash
pip install "PyYAML>=6,<7" "jsonschema>=4,<5"
python3 scripts/run_fixtures.py
```

Exit `0` = full conformance for the schema-shape corpus. Any other exit code is a failure with a per-fixture reason.

## conformance.json contract

The runner is index-driven, not filesystem-driven. `conformance.json` is the source of truth for which fixtures exist, what their pinned SHA-256 is, and what each invalid case must surface as failing. The runner:

1. Verifies every listed fixture exists with the pinned hash → catches vendored / offline drift.
2. Verifies the filesystem has no fixtures outside the index → catches orphan adds.
3. Validates each `valid/*.yaml` → must produce zero schema errors.
4. Validates each `invalid/*.yaml` → must produce at least one error AND the normalized failing path must contain at least one of the case's `expected_paths`.

`expected_paths` is implementation-agnostic: dotted property paths like `auth.issuer` or `monetization.rebate_pct`. The runner extracts these from the validator's structured errors:

- `required` → `parent.<missing_field>` (from the error's missing-property metadata)
- `additionalProperties` → `parent.<unknown_field>`
- `not` → walks the violated `not.required` (or `not.anyOf[].required`) sub-schema and surfaces every forbidden field name. *Caveat:* this trick is sufficient for the conditionals encoded in v1 schema today; future runtime conditionals using more elaborate `not` shapes may need richer index entries.
- everything else → the dotted absolute path from the validator

`keyword` in each invalid entry is annotation-only — it documents which JSON Schema keyword should fail, so a non-Python implementation can independently sanity-check it picked up the same rule.

## Tampering test

Editing any fixture, removing one, adding an orphan, or making an invalid case unexpectedly pass MUST flip `run_fixtures.py` to a non-zero exit. Verified via 4 tamper scenarios in tick 10's BS check.

## Adding fixtures

When the schema gains a v1-compatible new rule:

1. Add the YAML under `valid/` or `invalid/`.
2. Compute its SHA-256 (`shasum -a 256 fixtures/valid/<name>.yaml`).
3. Append to `conformance.json` with `path`, `sha256`, and (for invalid) `keyword` + `expected_paths`.
4. Re-run the suite — exit must be 0.

v2 schemas will live in `schema/app.v2.schema.json` with their own fixtures directory and their own index.

## What this corpus does NOT prove

This is the schema-shape corpus. It does not prove:

- YAML pre-canonicalization rejects (duplicate keys, anchors, tags, NaN) — these live above JSON Schema in the parser.
- `spec_digest` byte-equivalence — see SPEC.md §Canonicalization for the worked example.
- IANA timezone validity — JSON Schema can't enforce IANA membership.
- Cron syntax — same.
- Unknown-top-level preservation across re-emit (Rule 4c) — needs a parser round-trip test, not a shape check.
- Body content — the body is excluded from the digest and out of schema scope.

These are tracked as future ticks; the parser-level conformance corpus is a separate (and larger) deliverable.
