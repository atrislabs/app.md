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

---

## Tick 1 — 2026-04-29 (app-T1: define `description`)

**Horizon:** APP.md becomes a real public standard.

**Task:** app-T1 — Add `description` field to SPEC.md as a defined optional string field.

**Metric:** SPEC.md `description` references = 0 → 1 (typed-field row in new `## Optional metadata` section between Required fields and Runtime enum). 10/10 manifests now have a defined home for their existing top-level `description:` line.

**BS check:** ran. Verified all 10 manifests use single-line top-level `description:` (frontmatter, not body, not nested) before editing — codex's flagged falsifier was clean. After edit, grep -c "description" SPEC.md = 1, content matches typed row.

**Codex plan review:** APPROVED. "Real but incomplete: grep proves the doc delta; placement in the normative field table proves the spec delta… T1 is tiny, high-confidence, and unblocks all fixtures from one fail-closed error." Falsifier flagged: confirm description is top-level frontmatter, not nested. Verified clean before edit.

**Codex output review:** APPROVED with one wording nit. "Metric: real but weak; acceptable tick signal, not proof of conformance. Placement is correct. Tighten 'Free-form' → 'Plain text' if schema will enforce scalar string only." Applied: "Free-form" → "Plain-text". No max length added (schema churn).

**Gap closed:** Validation rule #4 (fail-closed on unknown fields) no longer flags the universal `description:` usage in 10/10 manifests. Removes one of 8 codex punch-list issues. JSON Schema work in app-T9 now has a typed-field row to mirror as source of intent.

**Next:** app-T2 — Define execution binding for `local` and `template` runtimes. SPEC.md has bindings for subprocess/ec2/webhook/external/web/ios but `local` (commit-digest example) and `template` (3 templates) are silent. Local likely wants `entrypoint:` (shell command) or `script:` (relative path). Template should be explicit "no execution binding required, fork-only".

**Signal:** [TICK_COMPLETE] metric=spec_field_description_defined=1

---

## Tick 2 — 2026-04-29 (app-T2: bindings for local + template)

**Horizon:** APP.md becomes a real public standard.

**Task:** app-T2 — Define execution binding for `local` and `template` runtimes (previously silent).

**Metric:** SPEC.md execution-binding section now covers all 8 runtime enum values. Added: 1 table row (`_none_` for local + template), 1 normative validator sentence, 1 `### No-binding runtimes` subsection with per-runtime rules. commit-digest (only `local` example, zero binding fields) now conforms; rule for `template` is forward-looking (no `runtime: template` manifests in repo today).

**BS check:** ran. grep verified table row, validator sentence, and subsection heading each appear once. Confirmed commit-digest still validates (no binding fields = legal). Confirmed no `runtime: template` manifest exists, so rule cannot break anything that ships today.

**Codex plan review:** APPROVED with three tweaks: (a) add explicit table row for local/template instead of hiding them in prose only, (b) defer `entrypoint:` without naming v2 ("a future schema version may add deterministic local entrypoints"), (c) prep app-T7 by adding "validators MUST reject required bindings on wrong runtimes and executable bindings on template." All three applied.

**Codex output review:** APPROVED with one MUST-stronger fix on template wording. Applied: "no execution binding permitted" → "runtime: template MUST NOT include any execution-binding field (block_pipeline_id, any endpoints.*, etc.)". Codex flagged "optional-binding runtimes" as a future-category gap; not closing tonight, will revisit if a real example emerges.

**Gap closed:** 2 of 8 codex punch-list issues now resolved (T1 description, T2 local+template binding). Spec is closer to internally consistent. JSON Schema work in app-T9 has a clean translation target: `if runtime in {local, template}, no binding fields permitted; on template, executable bindings explicitly disallowed (encode via not/anyOf).`

**Next:** app-T3 — Decide and lock timezone policy for `schedule:`. SPEC.md says UTC. Examples (commit-digest "0 18 * * 1-5", daily-standup "0 7 * * *", etc.) are described in plain English referencing LA times in their bodies but use UTC-style cron. Need to either (a) lock to UTC + rewrite example bodies, or (b) add optional `timezone:` IANA field with default UTC. Pick (b) — adding an optional field is safer and matches how real cron systems work. Falsifier: if any cron expression in examples is currently mis-aligned (i.e. body says "7am LA" but cron is "0 7 * * *" UTC = midnight LA), that's a real bug to fix during the same edit.

**Signal:** [TICK_COMPLETE] metric=spec_runtime_binding_coverage=8/8
