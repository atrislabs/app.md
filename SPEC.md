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

Exactly one of these tells the runtime how to actually execute. The required shape depends on `runtime`.

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

## Resources

| Field | Type | Notes |
|---|---|---|
| `secrets` | list[string] | Names only — values resolve from `vault` at run time |
| `schedule` | cron string | Optional. UTC. `"0 7 * * *"` = 07:00 daily |
| `runtime_auth` | enum | How Atris authenticates the runtime *back* to itself: `none` \| `jwt` \| `api_key`. Default `jwt` |

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
