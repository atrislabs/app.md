---
schema_version: 1
name: atris
slug: atris
description: The Atris framework itself — orchestrator of members, skills, apps, knowledge. Proves that Atris is just another app in its own registry.
access: private
runtime: external
vault: atris-kms
runtime_auth: jwt
endpoints:
  api: http://localhost:8001
  frontend: https://atris.ai
  mcp: https://atrismail.com/mcp
auth:
  type: jwt
  issuer: https://atris.ai/auth
capabilities:
  - orchestrate_members
  - execute_skills
  - manage_apps
  - route_messages
  - run_pulse_cycle
secrets: []
member: cabinet
skills:
  - atris
  - meta
  - create-app
surfaces:
  - web
  - slack
  - mcp
  - voice
  - email
  - cli
render: none
created_by_agent: keshav
monetization:
  price_credits: 0
  creator_share: 0.0
---

# atris

Atris is the operating system for human + AI teams. This manifest proves Atris is an instance of its own schema — no primitive is special.

## What it does

- Routes messages from every surface (Slack, email, MCP, voice, CLI, web) through the message router into member agents.
- Runs the pulse cycle (DECIDE → EXECUTE → CRITIQUE) for every active agent.
- Owns the registry of apps, members, skills, wiki content.
- Serves the HTTP API at `:8001` for every operation.

## Why this APP.md exists

The schema has to cover the biggest case: the entire framework. If Atris itself can be expressed as a folder with `APP.md`, then anything smaller — a cron script, a pitch deck, a customer CRM — trivially can.

## Guardrails

- `access: private` — only the admin user (Keshav) can trigger it.
- No scheduled runs; triggered by surface traffic, not cron.
- Secrets are empty at the manifest level because Atris composes per-app secrets at run time, not framework-level ones.
