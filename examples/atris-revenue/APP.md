---
schema_version: 1
name: atris-revenue
slug: atris-revenue
description: Daily Stripe revenue summary for Atris Labs — new charges, churned subs, balance delta, posted to #ops.
access: business
runtime: ec2
vault: atris-kms
runtime_auth: jwt

capabilities:
  - pull_stripe_charges
  - pull_stripe_subscriptions
  - post_slack_summary

secrets:
  - STRIPE_KEY
schedule: "0 9 * * *"

member: treasury
skills:
  - stripe-analytics

surfaces:
  - web
  - slack
render: inline

monetization:
  price_credits: 0
  creator_share: 0.0
---

# atris-revenue

Daily revenue pulse for Atris Labs. One run per morning, 9:00 America/Los_Angeles.

## What it does

1. Fetch new charges from Stripe for the last 24h.
2. Fetch subscription state — new, renewed, churned.
3. Compute delta vs the prior day's balance.
4. Post a summary to Slack `#ops` and email the treasury member's inbox.

## Inputs

- `STRIPE_KEY` (live restricted key, read-only scopes: charges, subscriptions, balance).

## Outputs

- Slack message in `#ops` with MRR, new subs, churned subs, balance.
- Run row in `app_runs` with `result.summary` and `result.metrics`.
- Artifact in `data/` — `yyyy-mm-dd.json` with the raw numbers for audit.

## Guardrails

- Read-only Stripe scopes. No write calls.
- If balance delta > 5σ of the 30-day rolling delta, flag instead of post — treasury reviews before the Slack message goes out.
- On Stripe API error, write a `failed` run with the error string. Do not retry inside the run — the next scheduled tick will try again.
- If `STRIPE_KEY` is missing from the vault, the run exits early with `error=missing_secret`. No partial Slack post.

## Why it's here

This is the first `APP.md` on disk. It is the dogfood app for the apps-as-folders migration (see `atris/features/apps/apps-as-folders.md`). The parser in `backend/services/app_folder_service.py` reads this file; Stage 4 sync will upsert it into the cloud `apps` table.
