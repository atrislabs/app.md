# APP.md Receipts

Receipts are how an app becomes part of a self-correcting loop.

An APP.md manifest says what capability exists. A receipt says what happened when that capability ran, who owns the next step, how the result was verified, and what should improve next.

## Why Receipts Matter

Without receipts, an app is just a callable action.

With receipts, every run can become evidence:

- success can be trusted
- failure can be assigned
- regressions can be reproduced
- human approvals can be audited
- future apps can learn from the outcome

This is the loop APP.md is designed to support:

```
observe -> understand -> decide -> act -> verify
-> receive feedback -> learn -> improve the loop
-> repeat
```

## Receipt Packet

v1 does not require one global receipt schema. Different runtimes can store receipts as JSON, Markdown, events, database rows, or UI cards.

The portable shape is:

| Field | Meaning |
|---|---|
| `app_slug` | Which APP.md app ran |
| `run_id` | Runtime-specific execution id |
| `status` | `ok`, `failed`, `blocked`, or `needs_approval` |
| `started_at` / `completed_at` | Time bounds for the run |
| `inputs_summary` | Safe summary of what the app was asked to do |
| `outputs` | Links or paths to user-visible artifacts |
| `events` | Structured events emitted from `events_schema` |
| `owner` | Human, team, agent, or app responsible for the next step |
| `verifier` | Check, command, reviewer, or app that judged the result |
| `decision` | What should happen next |
| `learned` | What future runs should do differently |

See [`examples/app-composition-coordinator/receipts/sample-receipt.json`](./examples/app-composition-coordinator/receipts/sample-receipt.json) for an approval-gated receipt packet example, and [`examples/app-composition-coordinator/receipts/sample-failure-receipt.json`](./examples/app-composition-coordinator/receipts/sample-failure-receipt.json) for a failure-to-learning example. `scripts/run_fixtures.py` validates public receipt examples for these portable fields and basic example quality.

## Status Semantics

- `ok`: the app completed and the verifier accepted the result.
- `failed`: the app attempted the work and produced an error or bad output.
- `blocked`: the app found a missing dependency, unclear instruction, or unavailable tool.
- `needs_approval`: the app reached a human gate such as sending externally, mutating production data, spending money, or changing credentials.

## Ownership

Every non-`ok` receipt should name an owner.

The owner can be a person, team, agent member, or another app. The point is not bureaucracy. The point is to prevent failures from becoming orphaned observations.

## Verification

Every receipt should say how the result was checked.

Examples:

- `python3 scripts/run_fixtures.py`
- human review in a Review Inbox
- a billing reconciliation app
- a screenshot diff
- a Slack approval
- another APP.md verifier app

## Learning

The `learned` field is where the system compounds.

For example:

- A YouTube app fails on a private video.
- The receipt records `status: failed`, the URL class, the error, and owner `youtube-skill`.
- A fallback is patched.
- A verifier is added.
- Future runs check privacy/access before charging credits.

The app did not merely fail. It improved the loop.

The public failure receipt example makes that concrete: a transcript-dependent run fails on access, records an owner, names the verifier to add, and stores the lesson future runs should apply.

## Relationship to APP.md v1

APP.md v1 already has the hooks receipts need:

- `slug` identifies the app.
- `events_schema` defines structured app events.
- `artifact_dir` gives runs a place to write durable outputs.
- `surfaces` and `render` define where a user may see the result.
- `capabilities` help routers find verifier and fallback apps.
- The markdown body can name owner, approval, and verification rules.

Future schema versions may standardize receipt fields directly. v1 keeps receipts as a runtime convention so implementations can learn before the standard freezes too much.
