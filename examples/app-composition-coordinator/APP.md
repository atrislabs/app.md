---
schema_version: 1
name: app-composition-coordinator
slug: app-composition-coordinator
description: Coordinates a customer issue by calling other APP.md apps, collecting receipts, and proposing the next action.
access: business
runtime: subprocess
vault: atris-kms
runtime_auth: jwt
secrets:
  - GMAIL_TOKEN
  - SLACK_TOKEN
surfaces:
  - cli
  - slack
  - mcp
render: inline
capabilities:
  - app-composition
  - customer-support
  - receipt-review
skills:
  - memory
  - slack
  - email-agent
events_schema:
  app_called:
    app_slug: string
    reason: string
    receipt_path: string
  composition_completed:
    app_count: int
    recommendation: string
    needs_human_approval: bool
monetization:
  price_credits: 0
---

# app-composition-coordinator

This app turns a customer issue into owned motion by coordinating other APP.md apps.

It does not replace the called apps. It reads their manifests, decides which capability to invoke, passes each app the smallest useful context, waits for receipts, and produces one recommendation a human or agent can act on.

## What it composes

For a refund complaint, this app may call:

1. `customer-pulse` to summarize recent account signals.
2. `agent-handoff-auditor` to inspect the current workspace and approval gates.
3. A future `refund-policy-checker` app to verify policy, billing state, and risk.
4. A future `reply-draft` app to prepare the customer-facing response.

The output is not "the answer." The output is a decision packet with evidence, receipts, and the next safe action.

## Inputs

- Customer or account slug.
- Issue summary.
- Optional candidate app slugs to call.
- Optional hard gate, such as "do not send externally without approval."

## Outputs

- `app_called` event for every composed app.
- `composition_completed` event with the recommendation.
- Slack summary with receipt links.
- CLI summary for the operator or next agent.

## Guardrails

- Never hide a called app's receipt.
- If a called app fails, include the failure receipt and choose a fallback or stop.
- If the next step sends money, contacts a customer, mutates production data, or changes credentials, mark `needs_human_approval: true`.
- Do not invent a capability. If no installed APP.md app matches the need, say which app should exist next.
