# Changelog

All notable APP.md spec changes land here. Breaking changes must bump
`schema_version` and include a migration note before the new schema is treated
as current.

## v1.0.0 - 2026-05-05

- Published the normative v1 spec in `SPEC.md`.
- Published the versioned JSON Schema at `schema/app.v1.schema.json`.
- Added the stable current schema alias at `schema/app.schema.json`.
- Shipped the public validator in `scripts/validate.py`.
- Shipped the conformance runner in `scripts/run_fixtures.py`.
- Pinned 11 valid fixtures, 85 invalid fixtures, 43 direct schema constraint
  paths, 11 parser-smoke checks, and 12 example/template manifests.
- Added `RECEIPTS.md` to define the proof loop for app runs: status, owner,
  verifier, decision, and learned fields.
- Defined v1 schema evolution: optional top-level fields may remain compatible
  under Rule 4c; renamed required fields, removed enum values, new enum values,
  semantic shifts, or additions inside closed sub-schemas require the next
  `schema_version`.
