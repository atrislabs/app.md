---
schema_version: 1
name: stripe-daily
slug: stripe-daily
description: 'Template: stripe-daily'
access: business
runtime: ec2
vault: atris-kms
runtime_auth: jwt
schedule: 0 9 * * *
secrets:
- STRIPE_KEY
- SLACK_BOT_TOKEN
member: treasury
skills:
- stripe-analytics
- slack
wiki_paths: []
surfaces:
- slack
- email
render: inline
events_schema:
  daily_revenue_computed:
    revenue_cents: int
    currency: string
    date: string
created_by_agent: apps-cli
monetization:
  price_credits: 0
---
# stripe-daily

Daily 09:00 Stripe digest. Pull yesterday's charges/refunds, compute net revenue, post to #treasury.
