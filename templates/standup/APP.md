---
schema_version: 1
name: standup
slug: standup
description: 'Template: standup'
access: private
runtime: subprocess
vault: atris-kms
runtime_auth: jwt
schedule: 0 7 * * *
secrets: []
member: chief-of-staff
skills:
- memory
wiki_paths: []
surfaces:
- slack
- email
render: inline
events_schema:
  standup_delivered:
    overnight_summary: string
    top_moves: list
created_by_agent: apps-cli
monetization:
  price_credits: 0
---
# standup

Daily 07:00 standup. Summarize overnight activity + inbox + top-3 moves, post to Slack and email.
