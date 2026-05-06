# Conformance fixtures

Machine-checkable conformance corpus for `schema/app.v1.schema.json`. `schema/app.schema.json` is the stable current-version alias and MUST point at the canonical v1 schema while v1 is current. Any APP.md parser SHOULD pass this suite before claiming v1 schema-shape conformance.

```
fixtures/
  conformance.json   index of every fixture, pinned by SHA-256
  valid/             11 manifests that MUST validate clean
  invalid/           85 manifests that MUST fail; conformance.json names
                     the keyword + expected_paths each case asserts
```

`scripts/run_fixtures.py` also runs a small parser-level smoke section against `scripts/validate.py` for checks JSON Schema cannot express: missing/unclosed APP.md frontmatter, duplicate keys, anchors/aliases/tags, non-JSON scalars, NaN/Infinity, invalid IANA timezone, and `spec_digest` worked-example/self-exclusion behavior. It also validates all 12 example/template manifests through the same reference-parser path.

`fixtures/valid/unknown-top-level.yaml` proves the Rule 4c schema-shape boundary: v1 validators tolerate unknown top-level fields. It does not prove byte-for-byte YAML re-emission.

## Run

From the repo root with Python 3.10+:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/run_fixtures.py
```

Exit `0` = full conformance for the schema-shape corpus, bundled parser-level smoke, and public examples/templates. The final line is `OK: all conformance checks pass`. Any other exit code is a failure with a per-fixture, parser-smoke, or example/template reason.

## conformance.json contract

The runner is index-driven, not filesystem-driven. `conformance.json` is the source of truth for which fixtures exist, what their pinned SHA-256 is, and what each invalid case must surface as failing. The runner:

1. Verifies every listed fixture exists with the pinned hash → catches vendored / offline drift.
2. Verifies the filesystem has no fixtures outside the index → catches orphan adds.
3. Validates each `valid/*.yaml` → must produce zero schema errors.
4. Validates each `invalid/*.yaml` → must produce at least one error AND the normalized failing path must contain at least one of the case's `expected_paths` with the indexed `keyword`.
5. Audits direct schema constraint paths → every field with a direct JSON Schema constraint (`type`, `enum`, `const`, `pattern`, bounds, length, or `$ref`) must have at least one invalid fixture `expected_paths` witness.
6. Validates the index contract itself → schema path, fixture locations, lowercase SHA-256 hashes, duplicate fixture paths, invalid-case `keyword`, and non-empty `expected_paths` lists are checked before metadata is trusted.

`expected_paths` is implementation-agnostic: dotted property paths like `auth.issuer` or `monetization.rebate_pct`. The runner extracts these from the validator's structured errors:

- `required` → `parent.<missing_field>` (from the error's missing-property metadata)
- `additionalProperties` → `parent.<unknown_field>`
- `not` → walks the violated `not.required` (or `not.anyOf[].required`) sub-schema and surfaces every forbidden field name. *Caveat:* this trick is sufficient for the conditionals encoded in v1 schema today; future runtime conditionals using more elaborate `not` shapes may need richer index entries.
- everything else → the dotted absolute path from the validator

`keyword` in each invalid entry is enforced against the validator's structured `error.validator`, so a case that fails for the right path but the wrong rule still fails the corpus.

## Tampering test

Any fixture/index drift MUST flip `run_fixtures.py` to a non-zero exit. The current gates catch:

- fixture hash drift,
- fixtures on disk but not in the index,
- indexed fixtures missing on disk,
- valid fixtures that fail schema validation,
- invalid fixtures that pass unexpectedly,
- invalid fixtures that fail at the wrong path,
- invalid fixtures that fail with the wrong keyword,
- schema coverage gaps where a direct schema constraint path lacks an invalid fixture witness.
- malformed index metadata such as invalid JSON, a non-object top level, duplicate paths, bad hashes, missing keywords, or empty expected path lists.

## Adding fixtures

When the schema gains a v1-compatible new rule:

1. Add the YAML under `valid/` or `invalid/`.
2. Compute its SHA-256 (`shasum -a 256 fixtures/valid/<name>.yaml`).
3. Append to `conformance.json` with `path`, `sha256`, and (for invalid) `keyword` + `expected_paths`.
4. Re-run the suite — exit must be 0.

v2 schemas will live in `schema/app.v2.schema.json` with their own fixtures directory and their own index.

## What this corpus does NOT prove

This is still primarily the schema-shape corpus. It does not prove:

- Full cron token semantics beyond the v1 five-field, single-line shape.
- Unknown-top-level preservation across re-emit (Rule 4c) — needs a parser round-trip test, not a shape check.
- Body content — the body is excluded from the digest and out of schema scope.

The remaining unchecked items are tracked as future ticks; a file-backed parser-level conformance corpus is still a separate (and larger) deliverable.
