# APP.md v1 — launch

> Press release + FAQ for the v1 spec. Working-backwards format. Two-minute read.

---

## APP.md v1 — one manifest format for agent-runnable apps, available today

**An app written for one AI runtime now runs unchanged on another.** APP.md v1 is a markdown file with YAML frontmatter that fully describes an agent-runnable app — runtime, schedule, secrets, surfaces, monetization. Every agent platform today invents its own app shape (Postgres rows, JSON configs, Python classes, GPT Actions schemas); none survive a move to a different runtime. APP.md fixes that with a single open spec, a normative JSON Schema, a conformance corpus, and a reference validator small enough to read in one sitting.

The v1 release ships four artifacts together: the [normative spec](./SPEC.md), a [JSON Schema](./schema/app.v1.schema.json) (Draft 2020-12, `$id: https://atris.ai/schema/app.v1.schema.json`), a [conformance corpus](./fixtures/) (10 valid + 13 invalid YAML fixtures, SHA-256 pinned), and a [65-line reference validator](./scripts/validate.py) any implementer can copy as their starting parser.

> *"v1 was designed so a `schema_version: 1` parser keeps working when the spec adds new optional fields. Forward-compat (Rule 4c), closed-block discipline for security-relevant sub-schemas, and explicit `schema_version` semantics mean adopters can ship and extend without waiting on the spec maintainers."* — Atris team

**Available now.** Clone [`github.com/atrislabs/app.md`](https://github.com/atrislabs/app.md), run `python3 scripts/validate.py examples/atris-revenue/APP.md`, get exit 0 + canonical JSON. Run `python3 scripts/run_fixtures.py` to verify the conformance corpus passes against your copy of the schema. The schema, fixtures, validator, and seven production-shipping example apps are MIT-licensed.

---

## FAQ

### Who is the customer for v1?

Anyone shipping an agent runtime, agent framework, or agent platform. Specifically: the engineer responsible for "what shape is an app on our platform?" If you have a config schema, a registration table, or a "manifest spec" that's currently a Notion doc, you are the customer. End users do not interact with APP.md directly — runtimes do.

### What's the most important benefit?

**One manifest format means apps survive a runtime change.** Today, an app on Wordware doesn't run on Lindy without a rewrite, and neither runs on a homegrown EC2 dispatcher without two rewrites. APP.md makes "rewrite the manifest" disappear from that list — runtimes parse the same markdown file and apply their own dispatch logic. The portability is the benefit; everything else (schema validation, registry support, AI-readable format, human-editable diffs) is downstream of it.

### What does adoption look like in practice?

The v1 design target is one work-day for a runtime engineer (the spec, schema, and 65-line parser are deliberately scoped to make this plausible; we'll publish actual times once the first external adoption lands):

1. Clone the repo. Read [SPEC.md](./SPEC.md) (15 min).
2. Copy [`scripts/validate.py`](./scripts/validate.py) into your repo as your v1 parser. It's 65 lines including the docstring; it depends only on `PyYAML` and `jsonschema`.
3. Wire your runtime's existing app registration step to call the parser; on `valid`, persist the manifest; on `invalid`, surface the structured error path to your authoring UX.
4. Run [`scripts/run_fixtures.py`](./scripts/run_fixtures.py) against your installed copy of the schema. Exit 0 = your runtime is v1-conformant for schema shape. Exit non-zero tells you exactly which case fails.

The sample reference runtime in [`atrislabs/atrisos-backend`](https://github.com/atrislabs/atrisos-backend) executes `local`, `subprocess`, `ec2`, and `web` apps today; `webhook`, `external`, and `ios` are scaffolded.

### How does v1 evolve without breaking adopters?

Three rules, encoded in [SPEC.md §Validation rules](./SPEC.md):

- **`schema_version`** is part of the manifest. The reference parser pins schema validation to whatever `schema_version` declares — old apps keep parsing under their old version.
- **Rule 4c (forward-compat).** Non-strict parsers MUST tolerate unknown frontmatter keys at the top level (warn, continue, preserve verbatim on re-emit). This is what lets v1 add new optional fields like `description` or `timezone` without breaking parsers built before those fields existed.
- **Closed/open sub-schemas.** The closed blocks (`secrets`, `auth`, `endpoints.*`, `monetization`) reject unknown nested keys — adding a key inside one bumps `schema_version`. The open blocks (`events_schema`, `ui_spec`) accept arbitrary app-defined keys — those are the manifest's contract with its runtime, not the spec's with the world.

A breaking change ships as `schema_version: 2` with a CHANGELOG migration note, never as a quiet field rename.

### What is NOT in v1 scope?

APP.md v1 defines the **manifest format**: what an app declares about itself, in a shape that any runtime can parse. **APP.md is not a runtime, and APP.md is not a marketplace.** It does NOT define:

- **Runtime semantics.** How `runtime: ec2` resolves to a sandbox, how secrets are injected, how schedules fire — those live in each runtime's implementation. The reference runtime is one example; others are encouraged.
- **Dispatch.** How a manifest's body is handed to an LLM, how tools are invoked, how outputs are persisted. Out of scope.
- **Identity, billing, marketplaces.** APP.md declares `monetization.price_credits` and `creator_share`; the actual billing layer and marketplace registry are separate products built on top of the spec.
- **Body content.** The markdown body after the closing `---` is free-form prompt material — excluded from `spec_digest`, validated only as "is there a body section." Body conventions are app-author and runtime concerns.
- **YAML pre-canonicalization checks beyond JSON Schema.** Duplicate keys, anchors, tags, NaN — these live in the parser, above the JSON Schema layer (see SPEC §Canonicalization).

If your platform needs any of the above, you build it on top of APP.md, not by extending v1's surface.

---

## Adoption signals (track here)

Reference implementation first; external rows added only after public adoption lands.

| Runtime | Status | Manifest count | Notes |
|---|---|---|---|
| atrisos-backend (reference) | shipped | 7 production apps | parses every example in this repo |

To add your runtime, open a PR against this table once your runtime publicly parses APP.md v1.
