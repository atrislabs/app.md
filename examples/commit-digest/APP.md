---
schema_version: 1
name: commit-digest
slug: commit-digest
description: End-of-day rollup of every commit across local git repos. Runs entirely on the customer's machine — no cloud, no tokens, no secrets.
access: private
runtime: local
vault: local
schedule: "0 18 * * 1-5"
secrets: []
surfaces:
  - cli
  - email
render: inline
artifact_dir: ~/Documents/commit-digests
events_schema:
  digest_emitted:
    repo_count: int
    commit_count: int
    flagged_count: int   # WIP / fixup / forgotten branches
  forgotten_branch_detected:
    repo_path: string
    branch: string
    age_hours: int
---

# commit-digest

A local end-of-day digest. At 18:00 on weekdays it walks every git repo under `~/code` (configurable), collects today's commits, and writes a one-page summary you can read in 30 seconds.

Designed to run with `runtime: local` — no API keys, no vaults, no network calls. The whole thing executes as a subprocess on the customer's laptop.

## What it does

1. Discover repos: every directory under `~/code` containing a `.git` folder. Configurable via the `COMMIT_DIGEST_ROOT` environment variable.
2. For each repo with commits today:
   - List commits as `<short-sha> <author> — <subject>`
   - Write a one-paragraph synthesis: what shipped, what's in flight, what stalled
3. Flag suspicious patterns:
   - Commits whose subject contains `WIP`, `fixup!`, `squash!`, or `tmp`
   - Branches with uncommitted changes older than 24 hours (forgotten work)
   - Repos with unpushed commits older than 48 hours (stuck on local)
4. If more than 20 repos have activity, group by top-level folder under `~/code` and summarize per group instead of per repo.
5. Render the digest to the terminal. Also write a dated markdown file to `~/Documents/commit-digests/YYYY-MM-DD.md`.
6. If `SMTP_HOST` is set in the environment, email a copy to the user's git `user.email`.

## Inputs

- The local filesystem under `COMMIT_DIGEST_ROOT` (default `~/code`).
- Local `git` binary (any version ≥ 2.0).
- Optional: `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` from the environment for email delivery. Stored by the OS, not by the app.

No secrets declared in `secrets:` because nothing crosses the network on the app's behalf — the SMTP variables (if used) are read directly from `os.environ` by the runtime.

## Outputs

- Terminal: full digest, color-coded by flag severity.
- File: `~/Documents/commit-digests/YYYY-MM-DD.md` (also the `artifact_dir`).
- Email (optional): plain-text copy of the markdown file.
- Event: `digest_emitted` with counts so a downstream observer can chart productivity over time.
- Event: `forgotten_branch_detected` per stale branch — the runtime can route these to a follow-up app (e.g. a "remind me Monday" reminder).

## Guardrails

- `access: private` — never shared, never indexed.
- Reads only — never runs `git commit`, `git push`, or any state-mutating git operation.
- Skips repos where the working tree contains files matching the user's global `.gitignore` patterns marked secret (e.g. `.env`, `*.pem`).
- If a repo's HEAD detached or in an interactive rebase, the digest notes the state and skips the commit walk for that repo.
- If `~/code` does not exist, the app exits cleanly with `digest_emitted{repo_count: 0}` rather than erroring.

## Why `local`

This is the canonical case for `runtime: local`: an app that touches files the customer wouldn't want crossing a network boundary (their commit history, authored code, in-flight branches), needs no shared infrastructure, and benefits from running where the source of truth already lives.

Compare to `subprocess` (shared backend) or `ec2` (sandboxed cloud) — both would require shipping the customer's git history off-machine to be useful, which most engineers will not do for a digest tool.
