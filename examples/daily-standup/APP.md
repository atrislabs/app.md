---
schema_version: 1
name: daily-standup
slug: daily-standup
description: Morning briefing for Keshav — overnight fleet activity, inbox signals, today's top 3 moves. Shipped to Slack + voice (read aloud on demand).
access: private
runtime: subprocess
vault: atris-kms
runtime_auth: jwt
secrets:
  - GMAIL_TOKEN
  - SLACK_TOKEN
  - LINEAR_TOKEN
  - GITHUB_TOKEN
schedule: "0 7 * * *"
member: chief-of-staff
skills:
  - email-agent
  - slack
  - linear
  - github
  - memory
wiki_paths:
  - wiki/keshav/goals
  - wiki/keshav/operating-principles
  - wiki/company/current-phase
surfaces:
  - slack
  - voice
  - email
render: inline
created_by_agent: chief-of-staff
events_schema:
  standup_delivered:
    top_moves: list   # top-3 actions for today
    overnight_summary: string
    fleet_health: string   # "green" | "yellow" | "red"
  move_accepted:
    move_index: int
  move_rejected:
    move_index: int
    reason: string
ui_spec:
  layout: briefing
  sections:
    - overnight
    - inbox
    - top-3-moves
    - fleet-status
  theme: atris-dark
monetization:
  price_credits: 0
---

# daily-standup

The chief-of-staff member's 07:00 briefing — the one message Keshav reads before anything else.

## What it does

Runs 07:00 America/Los_Angeles every day:

1. **Overnight fleet activity:** agent runs since midnight (Swarlo + app_runs). Any failures? Any silent scheduled apps? Any new blockers?
2. **Inbox signals:** high-priority emails flagged overnight; Slack DMs unread > 12h; PR review requests.
3. **Today's top 3 moves:** ranked from `wiki/keshav/goals` + open Linear issues + customer-pulse output + calendar.
4. **Fleet health:** Swarlo hub score, orchestrator coordination score, error rate.

Post to Slack DM, email the briefing, and prime the voice interface ("Hey Atris, read me the standup") to read it aloud on request.

## Inputs

- `GMAIL_TOKEN`, `SLACK_TOKEN`, `LINEAR_TOKEN`, `GITHUB_TOKEN` — read-only.
- Wiki paths — Keshav's goals + operating principles (so the ranking matches his priorities, not a generic urgency score).

## Outputs

- Slack DM to Keshav with the full briefing.
- Email copy to keshav@atris.ai for archival.
- `standup_delivered` event with the top-3 moves so acceptance can be tracked.
- `move_accepted` / `move_rejected` events fired when Keshav reacts to the DM.

## Guardrails

- `access: private` — nobody but Keshav.
- Top-3 must include at least one GTM move if any customer signal is > 0.7 urgency.
- Never post work-in-progress from drafts unless the draft's owner has opted in.
- If fleet health is red for > 24h, escalate to a blocking alert instead of a standup line.
