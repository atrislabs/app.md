---
schema_version: 1
name: customer-pulse
slug: customer-pulse
description: Weekday digest of signals from top customers — email threads, Slack mentions, Notion edits, calendar invites. Scored + ranked, posted to Keshav.
access: business
runtime: subprocess
vault: atris-kms
runtime_auth: jwt
secrets:
  - GMAIL_TOKEN
  - SLACK_TOKEN
  - NOTION_TOKEN
  - GOOGLE_CALENDAR_TOKEN
schedule: "0 9 * * 1-5"
member: gtm
skills:
  - email-agent
  - slack
  - notion
  - calendar
  - memory
wiki_paths:
  - wiki/customers/sachin
  - wiki/customers/aditya
  - wiki/customers/sushanth
  - wiki/customers/gracie
  - wiki/customers/jonathan
surfaces:
  - slack
  - email
render: inline
created_by_agent: gtm
events_schema:
  customer_signal:
    customer_slug: string
    channel: string   # "email" | "slack" | "notion" | "calendar"
    score: float      # 0..1 urgency
    summary: string
  pulse_posted:
    top_customers: list
    total_signals: int
monetization:
  price_credits: 0
---

# customer-pulse

The GTM member's eyes on every signal from customers who matter — so nothing goes 48h unacknowledged.

## What it does

Every weekday at 09:00:

1. Load per-customer context from each `wiki_paths/customers/<slug>` — what they want, what they've bought, what they've complained about.
2. Pull last 24h of signals:
   - Gmail threads `from:<customer domain>` or mentioning them.
   - Slack messages in customer channels or DMs.
   - Notion edits in customer pages.
   - Calendar invites involving them.
3. Score each signal for urgency (0..1) using the member's context.
4. Rank customers by total unresolved signal weight.
5. Post a Slack summary + email to Keshav: "Sachin has 3 high-urgency threads, one open since Tuesday."

## Inputs

- `GMAIL_TOKEN`, `SLACK_TOKEN`, `NOTION_TOKEN`, `GOOGLE_CALENDAR_TOKEN` — read scopes only.
- Wiki paths — customer context, not credentials.

## Outputs

- Slack post in `#gtm` with ranked customer list + top signals.
- Email to Keshav with the same digest.
- `customer_signal` events per individual signal (for trend analysis).
- `pulse_posted` event per run.

## Guardrails

- Read-only across every integration.
- Never quote customer email verbatim in public channels — paraphrase + link.
- If a customer hasn't sent a signal in 14 days, flag "silent, investigate" rather than skipping.
- The member resolves scoring disagreements between signals; ties broken by most-recent.
