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
| `slug` | string | Lowercase, no spaces. Identifies the app in URLs / vaults / runs |
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
| `block_pipeline_id` | uuid | `subprocess`, `ec2` | The compiled pipeline to invoke |
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
2. MUST validate `slug` is lowercase with no spaces.
3. MUST validate `runtime` is one of the 8 enum values.
4. MUST treat unknown frontmatter fields as **errors** (fail-closed) until a `schema_version` bump explicitly relaxes this.
5. MUST treat `secrets` as names only — never resolve values during parse.
6. MUST surface a stable `spec_digest` (SHA-256 of the canonicalized record) so callers can detect drift between APP.md and any cached registration.

## Spec evolution

This is `schema_version: 1`. Field additions that are backwards-compatible (new optional fields, new enum values that callers can ignore) do not bump the version. Anything that requires existing parsers to change (renamed required field, removed enum value, semantic shift) bumps to `schema_version: 2` and ships a migration note in CHANGELOG.

The reference parser pins schema validation to `schema_version`, so old apps keep parsing under their declared version.
