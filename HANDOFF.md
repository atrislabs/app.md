# app.md endgame — forgepilot handoff log

**Endgame:** `app-md-spec` (seeded 2026-04-29)
**Source of truth for tasks:** `~/arena/empire/atrisos-backend/atris/TODO.md` § Endgame § app-md-spec
**Acceptance:** see TODO.md endgame block (5 criteria, 14 tasks).

## Tick 0 — 2026-04-29 (seed)

**Horizon:** APP.md becomes a real public standard.

**State at seed:**
- Repo: `github.com/atrislabs/app.md` — 2 commits, 17 tracked files, 0 stars/forks.
- SPEC.md v1 published but unvalidated. Codex flagged 8 issues (app-T1..T8 in TODO.md).
- 7 examples committed (`commit-digest`, `atris-revenue`, `burn-rate`, `daily-standup`, `customer-pulse`, `atris-pitch-deck`, `atris`).
- 3 templates (`deck`, `standup`, `stripe-daily`).
- README claims `python -m scripts.apps_cli` works but `scripts/` directory does not exist in this repo.

**Next tick (tick 1):**
- Pick one of `[app-T1]`..`[app-T8]` from TODO.md.
- Default order if codex review doesn't redirect: T1 (description field) is the cheapest single-file fix and unblocks every example from fail-closed rejection. Start there.
- Work happens in `~/arena/app.md/`. Commit + push from this repo, not from atrisos-backend.

**Conventions for this endgame:**
- One commit per tick on `~/arena/app.md/master`. Push immediately. Trailing co-author line per CLAUDE.md.
- Append a tick block to this file at the END of every tick (do not rewrite earlier blocks).
- Codex plan-review BEFORE building, output-review AFTER. Both `codex exec` runs from `~/arena/app.md/`.
- BS check: every spec edit must be backed by either (a) an example that exercises it, or (b) a fixture in `fixtures/valid/` or `fixtures/invalid/`. No spec text without a witness.

**Cross-repo note (2026-04-29):** atrisos-backend pre-push hook is currently blocking pushes from this machine due to an orphaned test (`backend/tests/test_vitalize_brain_benchmark.py` references a missing `scripts/vitalize_brain_benchmark.py`). Local commits to `atris/TODO.md` and daily logs there will accumulate but not push tonight. The `~/arena/app.md/` repo has no such hook — its pushes succeed. Forgepilot ticks should:
- Read `atris/TODO.md` locally (no fetch needed).
- Write per-tick handoff blocks to THIS file (`~/arena/app.md/HANDOFF.md`), not to `atris/team/.../forgepilot.md`. This keeps the endgame self-contained and visible via the public app.md repo.
- Push the app.md repo every tick. Skip atrisos-backend pushes silently — Keshav will resolve the orphan-test hook in the morning.

**Signal:** seeded — first real tick fires from cron `/forgepilot`.
