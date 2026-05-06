---
schema_version: 1
name: learning-loop-reviewer
slug: learning-loop-reviewer
description: Reviews app receipts, routes owner decisions, and turns failures into verified improvement tasks.
access: business
runtime: subprocess
vault: atris-kms
runtime_auth: jwt
secrets:
  - SLACK_TOKEN
surfaces:
  - cli
  - slack
  - mcp
render: inline
capabilities:
  - receipt-review
  - review-inbox
  - learning-loop
skills:
  - memory
  - slack
events_schema:
  receipt_reviewed:
    app_slug: string
    receipt_status: string
    owner: string
    verifier: string
  improvement_task_created:
    task_slug: string
    source_receipt: string
    verifier: string
    needs_human_approval: bool
monetization:
  price_credits: 0
---

# learning-loop-reviewer

This app is the Review Inbox for APP.md receipts.

It reads new run receipts, groups them by owner and verifier, separates accepted work from failed or approval-gated work, and proposes the smallest next task that would improve future runs.

## Inputs

- Receipt paths or receipt packet JSON.
- Optional focus app slug.
- Optional owner filter.
- Optional instruction such as "only create tasks that have a verifier."

## Outputs

- `receipt_reviewed` event for each receipt inspected.
- `improvement_task_created` event when a failure becomes owned work.
- Slack summary for the owner queue.
- CLI summary for the current operator or next agent.

## Guardrails

- Never mark a receipt resolved without a verifier.
- If a receipt has `status: needs_approval`, route it to the owner instead of taking the action.
- If the next task changes production, sends externally, spends money, or changes credentials, set `needs_human_approval: true`.
- Prefer one small task with a concrete verify command over a broad rewrite.
- Preserve the original receipt link so the improvement can be audited later.
