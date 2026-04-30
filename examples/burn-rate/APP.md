---
schema_version: 1
name: burn-rate
slug: burn-rate
description: Daily cash-position pulse — Ramp spend + Mercury balance + Brex spend + Stripe inflow → computed runway. Slack #treasury + email to Keshav.
access: business
runtime: ec2
vault: atris-kms
runtime_auth: jwt
secrets:
  - RAMP_API_KEY
  - MERCURY_API_KEY
  - BREX_API_KEY
  - STRIPE_KEY
  - SLACK_BOT_TOKEN
schedule: "0 8 * * *"
timezone: America/Los_Angeles
member: treasury
skills:
  - ramp
  - mercury
  - brex
  - stripe-analytics
  - slack
surfaces:
  - slack
  - email
render: inline
created_by_agent: treasury
events_schema:
  daily_burn_computed:
    cash_on_hand_cents: int
    monthly_burn_cents: int
    monthly_inflow_cents: int
    runway_months: float
    date: string
  runway_alert:
    level: string   # "info" | "warn" | "critical"
    runway_months: float
    message: string
monetization:
  price_credits: 0
---

# burn-rate

One of the highest-leverage apps: never let Keshav be surprised by the cash position.

## What it does

Runs every morning at 08:00 America/Los_Angeles:

1. Pull yesterday's spend from Ramp (card transactions, approvals).
2. Pull current balance + inflows from Mercury (primary checking/savings).
3. Pull yesterday's spend from Brex (reimbursements, cards).
4. Pull yesterday's Stripe inflow (new MRR + one-time revenue).
5. Compute: `cash_on_hand`, `monthly_burn` (30-day rolling), `runway_months = cash / burn`.
6. Post a summary to Slack `#treasury` and email the treasury member.
7. Fire a `runway_alert` event if runway crosses thresholds (12mo=info, 9mo=warn, 6mo=critical).

## Inputs

- `RAMP_API_KEY` — read-only transactions + balances
- `MERCURY_API_KEY` — read-only balances
- `BREX_API_KEY` — read-only transactions
- `STRIPE_KEY` — live restricted, read-only
- `SLACK_BOT_TOKEN` — post to `#treasury`

## Outputs

- Slack post in `#treasury` with the day's numbers.
- Email to treasury inbox.
- `data/YYYY-MM-DD.json` with the raw pull for audit.
- Events: `daily_burn_computed` every day, `runway_alert` when thresholds cross.

## Guardrails

- Read-only scopes across every integration. No transfer, no charge, no write.
- If any integration fails, post a degraded summary with `sources_missing: [...]` instead of silence.
- Runway crossing a threshold fires the alert *once per threshold*, not every day below it.
- Never log raw account numbers or card-last-4 outside the encrypted data/ artifact.
