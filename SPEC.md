# APP.md — Spec v1

An `APP.md` is a markdown file with YAML frontmatter that fully describes an agent-runnable app. The frontmatter is the manifest; the body is the instructions the runtime hands to the agent.

```
---
{{ frontmatter — typed fields below }}
---

{{ markdown body — instructions for the agent }}
```

Parsers MUST reject any APP.md whose frontmatter is missing, unclosed, or fails schema validation. Reference parser: `backend/services/app_folder_service.py:load_from_folder` in `atrislabs/atrisos-backend`.

## Required fields

| Field | Type | Notes |
|---|---|---|
| `schema_version` | int ≥ 1 | Bump on breaking change |
| `name` | string | Human-readable |
| `slug` | string | Identifier used in URLs, vaults, run keys. MUST match regex `^[a-z][a-z0-9]*(-[a-z0-9]+)*$` (lowercase letter to start; groups of `[a-z0-9]+` joined by single hyphens; no leading digit, no underscores, no double hyphens, no trailing hyphen) and MUST be 1–64 characters long. The same grammar applies to `member`, `skills[]`, and `created_by_agent`. |
| `access` | enum | `private` \| `business` \| `public` |
| `runtime` | enum | One of the 8 runtimes (see below) |
| `vault` | enum | `atris-kms` \| `app_secrets` \| `byo-aws` \| `local` |

## Optional metadata

| Field | Type | Notes |
|---|---|---|
| `description` | string | Plain-text one-line summary of what the app does. Surfaced in registries, marketplaces, CLI listings, and search. Single-line; for longer copy use the markdown body. |

## Runtime enum

| Value | Where the code runs |
|---|---|
| `local` | Customer's machine as a subprocess |
| `subprocess` | Shared backend process (default for lightweight apps) |
| `ec2` | Atris-managed EC2 sandbox |
| `webhook` | Customer-hosted HTTP endpoint |
| `external` | Full-stack external service (multiple endpoints) |
| `web` | Web app + optional MCP |
| `ios` | Native iOS via App Intents + deep links |
| `template` | Marketplace spec, no execution until installed |

## Execution binding

Exactly one of these tells the runtime how to actually execute. The required shape depends on `runtime`. Two runtimes (`local`, `template`) are deliberately bindingless — see the [No-binding runtimes](#no-binding-runtimes) section after the table.

| Field | Type | Required for | Notes |
|---|---|---|---|
| `block_pipeline_id` | uuid | optional, `subprocess` and `ec2` only | If absent, the runtime treats the manifest body + member + skills + secrets + remaining manifest context (`wiki_paths`, `schedule`, `surfaces`, etc.) as an **implicit pipeline**. Set explicitly to point at a compiled, version-pinned pipeline. Implementer rule: omitted ⇒ implicit; present ⇒ non-null UUID. Explicit `null` is rejected by [Rule 4b](#fail-closed-scope) ("known-but-misused"). |
| `endpoints.api` | URL | `external`, optional for `webhook` / `web` | Primary HTTP API |
| `endpoints.frontend` | URL | `web` | Where users see the UI |
| `endpoints.mcp` | URL | optional | MCP server URL |
| `endpoints.webhook` | URL | `webhook` | Where the runtime POSTs |
| `endpoints.bundle_id` | string | `ios` | iOS bundle id (`com.example.app`) |
| `endpoints.deep_link_scheme` | string | `ios` | URL scheme |
| `auth.type` | enum | `webhook`, `external`, `web` if non-public | `none` \| `api_key` \| `bearer` \| `hmac` \| `oauth` \| `jwt` |
| `auth.issuer` | URL | when `auth.type=oauth` / `jwt` | OIDC issuer |
| `auth.secret_ref` | string | when auth needs a key | Vault secret name |
| `capabilities` | list[string] | optional | Free-form labels for routers |
| _none_ | — | `local`, `template` | No execution-binding field is required or permitted; see below |

Validators MUST reject manifests that omit a required binding for their declared runtime, AND reject any executable binding (`block_pipeline_id`, `endpoints.*`) on `runtime: template`.

### No-binding runtimes

- `local`: no execution-binding field is required. The markdown body of APP.md is treated as the agent system prompt; the runtime spawns an LLM subprocess on the customer's machine with shell access (the "agent + shell" model). Apps that need a deterministic local script are out of scope for v1; a future schema version may add deterministic local entrypoints.
- `template`: a manifest with `runtime: template` MUST NOT include any execution-binding field (`block_pipeline_id`, any `endpoints.*`, etc.). A template is a starting point to fork into a runnable app; the runtime cannot execute it directly. Forking flips `runtime` to `subprocess` / `ec2` / `web` / etc. and adds the appropriate binding field.

## Resources

| Field | Type | Notes |
|---|---|---|
| `secrets` | list[string] | Names only — values resolve from `vault` at run time |
| `schedule` | cron string | Optional. Standard 5-field cron. Default TZ is UTC; override with `timezone:` below. `"0 7 * * *"` = 07:00 daily in the resolved TZ. |
| `timezone` | IANA TZ string | Optional. e.g. `America/Los_Angeles`, `Europe/London`. Default `UTC` for every runtime (including `local`). When set, `schedule` is interpreted in this TZ. |
| `runtime_auth` | enum | How Atris authenticates the runtime *back* to itself: `none` \| `jwt` \| `api_key`. Default `jwt` |

### Schedule + timezone

- Cron expressions are standard 5-field (`min hour dom mon dow`). Optional fields like seconds or year are not part of v1.
- Default TZ for every runtime is **UTC**. Customer-machine local time is NOT a default — leaving `timezone` unset on `runtime: local` still means UTC, to keep behavior identical across CI / dev / prod and stop the "works on my laptop, fires at 3am in CI" footgun. Apps that want customer-local firing MUST declare `timezone:` explicitly.
- DST handling (when `timezone:` resolves to a TZ that observes DST):
  - **Nonexistent local times** (e.g. `02:30` on the spring-forward morning) MUST be skipped. The runtime SHOULD log the skip for observability; specific event names are runtime-defined.
  - **Repeated local times** (e.g. `01:30` on the fall-back morning) MUST fire **once**, not twice. The runtime SHOULD log the fold for observability.
- `timezone:` MUST be a value parsable by the IANA Time Zone Database (the runtime's `tzdata` source). Validators MUST reject manifests with an `Etc/GMT±N` style fixed offset that does not exist, or any free-form string that is not a valid IANA zone. Empty or missing → defaults to UTC (no error).
- `timezone:` was introduced in `schema_version: 1`. v1 parsers MUST allow it; failing-closed on it is a parser bug, not a manifest bug.

## Inheritance (optional)

| Field | Type | Notes |
|---|---|---|
| `member` | slug | `MEMBER.md` to inherit persona / tools from |
| `skills` | list[slug] | `SKILL.md`s to load |
| `wiki_paths` | list[path] | Paths under workspace root that the runtime injects into the agent's context. E.g. `wiki/customers/megan` |
| `created_by_agent` | slug | The agent that authored this APP.md (provenance) |
| `artifact_dir` | path | Override for output writes. Defaults to `{folder}/data/`. Use when an app writes into a shared wiki path or mounted volume |

## Surfaces and rendering

| Field | Type | Notes |
|---|---|---|
| `surfaces` | list[enum] | Where the app shows up: `web` \| `slack` \| `mcp` \| `voice` \| `mobile` \| `email` \| `cli` |
| `render` | enum | `inline` \| `embed` \| `fullscreen` \| `voice` \| `none`. Defaults to `none` |
| `ui_spec` | dict | Free-form layout / theme / component hints when `render` is not `none` (future: typed React spec) |
| `events_schema` | dict | Declared shape of events this app emits to `app_events`. Arbitrary JSON-compatible dict today |

## Monetization (optional)

| Field | Type | Notes |
|---|---|---|
| `monetization.price_credits` | int ≥ 0 | Credits charged per successful run. `0` = free |
| `monetization.creator_share` | float 0..1 | Revenue share back to the manifest author |
| `monetization.stripe_connect_account` | string | `acct_xxx` — where the share lands |

## Body

Everything after the closing `---` is the instructions block. The runtime injects it as the agent's working prompt at run time, alongside the resolved secrets, member persona, skills, wiki_paths, and any prior `data/` state.

There's no required structure for the body; treat it as the briefing you'd give a competent operator: what the goal is, what to do when X, what the failure mode looks like.

## Validation rules

A conforming parser:

1. MUST reject APP.md without YAML frontmatter delimited by `---` on its own line.
2. MUST validate `slug` against the regex `^[a-z][a-z0-9]*(-[a-z0-9]+)*$` and a length of 1–64 characters. The regex is anchored and case-sensitive (Unicode and uppercase are implicitly rejected). No coercion (lowercasing, hyphen-collapsing, etc.) is permitted — invalid slugs are rejected, not normalized.
2a. MUST apply the same regex + length rule to `member`, every item of `skills[]`, and `created_by_agent`. They are slug-typed; mismatched values reject the manifest.
3. MUST validate `runtime` is one of the 8 enum values.
4. **Fail-closed scope** — three rules that together replace the prior single "unknown = error" rule:
   - **4a.** MUST reject manifests missing any **required** field, or with a required field of the wrong type / enum value.
   - **4b.** MUST reject **known-but-misused** fields — e.g. `block_pipeline_id` on `runtime: web`, any executable binding on `runtime: template`, an invalid IANA timezone, an unknown enum value for a known field.
   - **4c.** Non-strict parsers MUST tolerate unknown frontmatter keys at the top level (warn, continue parsing) and MUST preserve unknown fields verbatim when re-emitting a manifest that parsed successfully. This is what lets a `schema_version: 1` parser keep working when the spec adds new optional fields within v1 (e.g. `description`, `timezone`). Strict conformance mode (e.g. a CI lint flag) MAY reject unknown keys before re-emission; in strict mode preservation is not required on a failed parse. Strict mode is OPTIONAL and not part of the runtime contract.
   - **Closed sub-schemas:** rule 4c does NOT apply inside `secrets`, `auth`, `endpoints.*`, or `monetization`. These blocks have a fixed key shape and are treated as closed; unknown nested keys MUST be rejected. Adding new keys inside a closed block bumps `schema_version`.
   - **Open user-defined blocks:** `events_schema` and `ui_spec` are open by design — their keys are app-defined (event names; layout hints). Parsers MUST NOT reject unknown keys inside these blocks. They are part of the manifest's contract, not the spec's.
5. MUST treat `secrets` as names only — never resolve values during parse.
6. MUST surface a stable `spec_digest` — see [Canonicalization](#canonicalization) for the exact algorithm. The digest lets callers detect drift between APP.md and any cached registration in a parser-agnostic way.

## Canonicalization

The `spec_digest` is `SHA-256(canonical_record)`, lowercase hex. `canonical_record` is defined as follows.

**Source.** The parsed YAML frontmatter MUST map cleanly into the JSON value space (objects, arrays, strings, integers, floats, booleans, nulls). YAML's null spellings (`~`, `null`, empty) all normalize to JSON `null` via the parser. The markdown body — everything after the closing `---` — is **excluded** from the digest: bodies are agent prompts that churn constantly during development. Body drift is tracked separately (file hash / git SHA / content hash).

**Pre-canonicalization rejects.** A parser MUST reject the manifest before computing a digest if any of these are present:
- Duplicate object keys at any nesting level.
- YAML tags (`!Foo`), anchors (`&a`), or aliases (`*a`).
- Non-JSON scalars (e.g. dates as YAML date type — represent as ISO 8601 strings instead).
- `NaN`, `+Infinity`, `-Infinity`.
- An unsupported `schema_version`. Validate version before digesting; do not digest a manifest a parser cannot interpret.

**Strings.** Fed byte-for-byte into JCS. **No Unicode normalization** (NFC/NFD/NFKC/NFKD) is applied — two visually-identical strings with different code-point sequences MUST yield different digests.

**JSON serialization (RFC 8785, JCS).** Apply RFC 8785 to the tree:
- Object keys sorted lexicographically by Unicode code point, recursively.
- No insignificant whitespace.
- Strings written as literal UTF-8 (no `\uXXXX` escapes for non-ASCII).
- Integers as decimal digits with no leading zeros (sign prefixed `-`).
- Floats use the shortest round-trippable decimal per ECMAScript `Number.prototype.toString` (RFC 8785 §3.2.2.3).
- `true` / `false` / `null` for booleans and null. `[]` empty array. `{}` empty object.

**Exclusion.** If the manifest contains a top-level `spec_digest` field, exclude it from the canonical record before serialization (so an app can store its own digest without recursion). Nested `spec_digest` keys are not excluded.

**Forward-compat.** Unknown top-level keys preserved by [Rule 4c](#fail-closed-scope) **DO** participate in the digest. The digest reflects the actual manifest, not the spec's known-keys subset.

**Implementation.** Implementations MUST conform to RFC 8785; conformance tests SHOULD pin a specific JCS library and version. The algorithm itself fits in ~60 lines for languages without a JCS library — the worked example below is a sufficient self-test for any implementation.

**Worked example.**

```yaml
---
schema_version: 1
name: x
slug: x
access: private
runtime: local
vault: local
---
```

Canonical bytes:

```
{"access":"private","name":"x","runtime":"local","schema_version":1,"slug":"x","vault":"local"}
```

Expected digest: `eb9beb40790eeab0329641e230043e058e5819dfb5d526e81e7997af35b978a3`.

A parser whose `spec_digest` differs from this on the example above is non-conforming.

## Spec evolution

This is `schema_version: 1`. Field additions that are backwards-compatible (new optional fields at the top level, new enum values that callers can ignore) do not bump the version — they are forward-compatible per Rule 4c (parsers warn-and-continue and preserve the field on re-emit). Anything that requires existing parsers to change (renamed required field, removed enum value, semantic shift, additions inside a closed sub-schema) bumps to `schema_version: 2` and ships a migration note in CHANGELOG.

The reference parser pins schema validation to `schema_version`, so old apps keep parsing under their declared version.
