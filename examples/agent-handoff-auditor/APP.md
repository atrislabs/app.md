---
schema_version: 1
name: agent-handoff-auditor
slug: agent-handoff-auditor
description: Local preflight that audits repo state, handoff files, and blockers before an agent continues work.
access: private
runtime: local
vault: local
runtime_auth: none
secrets: []
surfaces:
  - cli
  - email
render: inline
artifact_dir: ~/Documents/agent-handoff-audits
capabilities:
  - repo-audit
  - handoff
  - next-action
events_schema:
  handoff_audit_written:
    repo_count: int
    blocker_count: int
    next_action: string
  dirty_repo_detected:
    repo_path: string
    dirty_file_count: int
  blocked_gate_detected:
    gate: string
    required_input: string
---

# agent-handoff-auditor

A local preflight for long-running agent work. It reads the workspace state, detects whether the next action is implementation, review, or a human approval gate, and writes a concise handoff audit for the next agent turn.

Designed for `runtime: local`: the app only reads local files and git metadata. It does not need tokens, does not call external APIs, and must never mutate the working tree.

## What it does

1. Discover the active workspace:
   - Current git repo.
   - Known sibling repos named in local task files, handoff logs, or recent commands.
   - Atris files when present: `atris/TODO.md`, `atris/MAP.md`, today's `atris/logs/YYYY/YYYY-MM-DD.md`.
2. For each repo:
   - Run read-only git checks: branch, upstream, ahead/behind count, dirty paths, untracked paths, submodule dirtiness.
   - List only file paths and counts by default. Do not print file contents unless the user asks for a deeper audit.
3. Read handoff artifacts:
   - `HANDOFF.md`, `PICK_SHEET.md`, `OUTREACH.md`, `README.md`, or task-specific files explicitly referenced by TODO/MAP.
   - Extract the current objective, done criteria, open gates, and the next concrete action.
4. Classify the state:
   - `ready-to-build`: no human gate, local files identify a safe next edit.
   - `ready-to-review`: implementation exists and only verification remains.
   - `blocked-on-input`: the next action requires a user choice, credential, outbound approval, or destructive action.
   - `blocked-on-sync`: upstream divergence or overlapping dirty files would make a pull unsafe.
5. Write a markdown audit to `~/Documents/agent-handoff-audits/YYYY-MM-DD-HHMM.md` and print the same summary to stdout.

## Output format

The audit must fit on one screen:

```markdown
# Agent handoff audit

State: blocked-on-input
Next action: ask Keshav to pick row 1 or row 2

Evidence:
- app.md: clean, 0 ahead / 0 behind
- atrisos-backend: dirty local logs preserved, 0 ahead / 0 behind
- Gate: T14 outbound send requires explicit approval

Risk:
- Sending without approval violates the project gate.

Safe command:
- none until approval is given
```

## Guardrails

- Read-only by default. Never run `git reset`, `git checkout --`, `git clean`, `rm`, `git push`, or outbound network sends.
- Do not open secret files (`.env`, `.pem`, credentials stores, local vault paths). Report that they exist only by name pattern and count.
- Treat user-edited dirty files as owned by the user. Preserve them and describe them; do not clean them.
- If a task requires an irreversible side effect, classify the state as `blocked-on-input`.
- If evidence conflicts, say exactly which files disagree and stop at `blocked-on-input`.

## Why this is useful to an agent

Most wasted agent time comes from continuing the wrong thread: redoing closed work, pulling over dirty files, or acting past a human approval gate. This app gives the agent a compact, evidence-backed state snapshot before it edits anything.
