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

---

## Tick 3 — 2026-04-29 (app-T3: timezone policy + real bug fix)

**Horizon:** APP.md becomes a real public standard.

**Task:** app-T3 — Decide and lock timezone policy for `schedule:`. Picked option (b): add optional `timezone:` IANA field with default UTC for ALL runtimes.

**Metric:** SPEC.md `timezone` mention count 0 → 6 (table row + intro line + DST handling + IANA validation rule + parser-allowance note + body line). 1 real bug fixed: examples/burn-rate/APP.md body says "Runs every morning at 08:00 America/Los_Angeles" but cron `0 8 * * *` under spec UTC default = midnight LA. Added `timezone: America/Los_Angeles` so cron actually fires when body claims it does.

**BS check:** ran. grep verified all SPEC.md additions. burn-rate frontmatter now has both `schedule:` and `timezone:`. 6/7 schedule-using manifests left default UTC (correct — body intent is ambiguous in the others; not invented intent).

**Codex plan review:** APPROVED with one major correction: default UTC for ALL runtimes including `local` (machine-local default would be a CI/dev/prod drift footgun). Applied. Codex also flagged DST handling as essential, parser-allowlist reconciliation as needed (see app-T7), and "do not touch ambiguous examples" (correct boundary).

**Codex output review:** APPROVED with two tightening fixes: (a) soften DST event names — runtimes-defined, not spec-defined ("SHOULD log the skip/fold"); (b) add invalid-IANA validation rule. Applied both. Codex confirmed app-T7 still needed to fully reconcile fail-closed.

**Gap closed:** 3 of 8 codex punch-list issues. SPEC.md now has a coherent timezone story (default UTC, IANA override, DST semantics, validation rule). Real bug shipped: 1 example was 8 hours off its body claim. JSON Schema work in app-T9 inherits a clear contract.

**Next:** app-T7 — Reconcile fail-closed rule (#4) with version-bump policy. Currently they self-contradict: rule #4 says reject any unknown frontmatter field; spec evolution says new optional fields don't bump version (so old parsers see "unknown" and reject). Two-tick chain: define a "reserved word allowlist" or scope fail-closed to required-unknown only. This is the keystone of forward-compatible spec evolution. Falsifier check: does any other field besides timezone hit this same rock? (`description` from app-T1 had the same issue; `_none_` table row from app-T2 doesn't introduce a new field.) Both v1-introduced; both need the same reconciliation.

**Signal:** [TICK_COMPLETE] metric=spec_timezone_field_defined=1,bugs_fixed=1

---

## Tick 4 — 2026-04-29 (app-T7: fail-closed reconcile)

**Horizon:** APP.md becomes a real public standard.

**Task:** app-T7 — Reconcile rule #4 ("MUST treat unknown frontmatter fields as errors") with spec evolution policy ("new optional fields don't bump version"). The two were a direct contradiction; ticks 1 and 3 silently relied on a parser model that did not exist.

**Metric:** Validation rule 4 split from a single self-contradicting line into 4a (missing/wrong-typed required), 4b (known-but-misused), 4c (unknown top-level: warn + continue + preserve verbatim on re-emit). Closed-block carve-out for security/fixed-shape (`secrets`, `auth`, `endpoints.*`, `monetization`). Open-block carve-out for user-defined (`events_schema`, `ui_spec`). Spec evolution clause cites Rule 4c by name. Tick 1 (`description`) + tick 3 (`timezone`) fields are now legal under v1 forward-compat.

**BS check:** ran. Every existing key inside closed blocks (auth.type/issuer, monetization.price_credits/creator_share) matches a SPEC-declared key — no manifest will reject under the new closed-schema rule. Caught a near-miss during this check: codex's plan review suggested adding `events_schema` + `ui_spec` to the closed list, but those are explicitly "free-form / app-defined" per their SPEC rows. Closing them would reject every manifest with custom event names. Reverted before commit and added an explicit "Open user-defined blocks" carve-out instead.

**Codex plan review:** APPROVED option C (split rule 4 into 4a/4b/4c). Strengthened wording: SHOULD → MUST tolerate (SHOULD too weak when evolution depends on it); "passthrough dict" → behavior-level "MUST preserve verbatim on re-emit"; clarified `--strict` is OPTIONAL conformance mode, not required CLI shape.

**Codex output review:** APPROVED with three fixes (extend closed list with `runtime_auth`/events_schema/ui_spec/monetization; clarify strict-mode preservation rule; flagged spec_digest drift risk for app-T6). Applied fixes 1+2 with a correction caught during BS check (events_schema and ui_spec stay OPEN, not closed). Risk #3 (spec_digest drift on preserved unknowns) deferred to app-T6.

**Gap closed:** 4 of 8 codex punch-list issues. The keystone for v1 forward-compat is in place — JSON Schema work in app-T9 has a clean translation: root `additionalProperties: true` + closed sub-schemas with `additionalProperties: false` + per-runtime conditional rules. Without this tick, ticks 1 and 3 were spec changes that no parser could honor.

**Next:** app-T6 — Define `spec_digest` canonicalization. Currently SPEC.md says "SHA-256 of the canonicalized record" without defining canonicalization. Codex flagged this in tick 4 output review as the open risk: if preserved-unknown fields participate in the digest, every parser computes a different hash; if they don't, the digest doesn't reflect the manifest's actual content. Need to specify: (a) JSON serialization (sorted keys, no whitespace, UTF-8), (b) which fields are excluded from the digest (likely none — preserve = participate), (c) handling of float ordering / null fields. Falsifier: pick one example, hand-compute a digest, see if SPEC.md prescribes a unique answer.

**Signal:** [TICK_COMPLETE] metric=fail_closed_rules_split=3

---

## Tick 5 — 2026-04-29 (app-T6: spec_digest canonicalization)

**Horizon:** APP.md becomes a real public standard.

**Task:** app-T6 — Define `spec_digest` canonicalization. Was 1 line ("SHA-256 of the canonicalized record") with "canonicalized" undefined; two parsers would compute different digests. This was flagged as the open risk in tick 4 output review (preserved-unknown fields' digest behavior).

**Metric:** SPEC.md has new `## Canonicalization` section: source (frontmatter only, body excluded), pre-canonicalization rejects (duplicate keys, YAML tags/anchors/aliases, non-JSON scalars, NaN/Infinity, unsupported schema_version), no Unicode normalization rule, RFC 8785 (JCS) JSON form, top-level spec_digest excluded if present, Rule 4c-preserved unknowns DO participate, worked example with computed digest `eb9beb40790eeab0329641e230043e058e5819dfb5d526e81e7997af35b978a3` reproducible from python3 stdlib.

**BS check:** ran. python3 stdlib (`json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False)` + hashlib.sha256) computed the same digest as written in SPEC.md byte-for-byte. Reproducible from any RFC 8785 implementation. Conformance test exists.

**Codex plan review:** APPROVED. Confirmed JCS over `json.dumps(sort_keys=True)` (the latter doesn't lock down Unicode escaping or float rendering). Confirmed pre-canonicalization rejects for duplicate keys, YAML anchors/tags/aliases, NaN, Infinity. Confirmed body-exclusion and self-exclusion of top-level spec_digest. Suggested: cite RFC 8785 generically; not normalizing Unicode is correct.

**Codex output review:** APPROVED with two tightening fixes: (a) drop unvetted JCS library citations (canonicaljson is for Matrix, not vetted as APP.md cite); cite RFC 8785 + behavior only. (b) Add explicit "schema_version validated before digesting" + "YAML null spellings normalize through parsing" lines. Both applied.

**Gap closed:** 5 of 8 codex punch-list issues. The risk codex flagged in tick 4 (preserved-unknown digest behavior) is now explicitly handled — unknowns participate, no recursion via self-exclusion, byte-for-byte string handling. JSON Schema work in app-T9 is fully unblocked: schema validates shape/types; canonicalization/digest is downstream.

**Next:** app-T4 — Make `block_pipeline_id` optional or remove the required-for-ec2 claim. Codex flagged that 5 examples either omit it or set null, but spec says required for `subprocess` and `ec2`. Falsifier: grep examples to see actual usage. Likely fix: change "Required for subprocess, ec2" to something like "Required for subprocess; optional for ec2 (when execution is implicit via member/skills inheritance)". Need to inspect first.

**Signal:** [TICK_COMPLETE] metric=spec_digest_canonical_defined=1,test_vector_reproducible=true

---

## Tick 6 — 2026-04-29 (app-T4: block_pipeline_id reconciled)

**Horizon:** APP.md becomes a real public standard.

**Task:** app-T4 — Reconcile `block_pipeline_id` "required for subprocess, ec2" claim with reality (0 of 6 such examples populate it).

**Metric:** Spec compliance for subprocess+ec2 manifests: 0/6 → 6/6. SPEC.md row updated to "optional, subprocess and ec2 only" with explicit implicit-pipeline default ("body + member + skills + secrets + manifest context"). Cosmetic `block_pipeline_id: null` removed from atris-revenue (was the only manifest with explicit null; now canonical absence). Implementer rule added: omitted ⇒ implicit, present ⇒ non-null UUID. Explicit null rejected by Rule 4b.

**BS check:** ran. Audited every subprocess/ec2 manifest (6 total). All 6 now absent block_pipeline_id (the new canonical "implicit pipeline" representation). atris-revenue's null line gone. Rule 4b cross-reference visible in SPEC.md.

**Codex plan review:** APPROVED. Confirmed keeping `subprocess, ec2` in the row (don't broaden without auditing); confirmed removing null absolutely (omit/null/UUID would be three states); confirmed implicit-pipeline definition includes "manifest context" to cover wiki_paths/schedule/surfaces without listing every field; confirmed no separate freezing concept needed.

**Codex output review:** APPROVED with two normative fixes: (a) cite Rule 4b explicitly so "null is not legal" is normative, not implied; (b) add implementer line "omitted ⇒ implicit; present ⇒ non-null UUID". Both applied.

**Gap closed:** 6 of 8 codex punch-list issues. The fictional "required" was the deepest spec-vs-reality gap; closing it makes the spec honestly describe how every existing manifest already works. JSON Schema work in app-T9 now has clean rules: `block_pipeline_id` optional + uuid format + non-null + only on `runtime in [subprocess, ec2]`.

**Next:** app-T5 — Tighten `slug` grammar in SPEC.md. Currently "Lowercase, no spaces" — underspecified. Codex flagged this. Likely fix: add regex `^[a-z][a-z0-9-]*$` to Validation Rules and to the slug row in the Required-fields table. Falsifier: grep all 10 manifest slugs to confirm they match the proposed regex; if any don't (e.g. starts with digit, has underscore), spec must accommodate or examples must change.

**Signal:** [TICK_COMPLETE] metric=block_pipeline_id_compliance=6/6

---

## Tick 7 — 2026-04-29 (app-T5: slug grammar tightened)

**Horizon:** APP.md becomes a real public standard.

**Task:** app-T5 — Tighten slug grammar. SPEC said "lowercase, no spaces" — admits abc_def, 1abc, abc--def, abc.io, etc.

**Metric:** Slug rule pinned to regex `^[a-z][a-z0-9]*(-[a-z0-9]+)*$` + 1–64 chars + no coercion. 10/10 existing manifest slugs pass; the worked-example single-letter `x` from canonicalization passes; 9 negative controls correctly rejected (caps, underscore, leading digit, leading/trailing/double hyphen, empty, 65-char, dot). Same rule normatively applied to member, skills[] items, created_by_agent (added rule 2a so prose cross-reference can't be missed by validator authors).

**BS check:** ran. python3 `re` module verified: 10/10 + worked-example PASS, 9 negative controls REJECTED, length cap enforced. Rule is provably consistent and auditable.

**Codex plan review:** APPROVED. Confirmed regex `^[a-z][a-z0-9]*(-[a-z0-9]+)*$` over the looser `^[a-z0-9-]+$`. Added 1-64 char length cap (codex suggestion). Confirmed no reserved-slug rule needed in v1; uniqueness is registry-layer, not grammar.

**Codex output review:** APPROVED with one normative-cite fix: add explicit rule line for member/skills[]/created_by_agent rather than just a prose cross-reference. Applied as rule 2a. Codex confirmed JSON Schema translation: `pattern`, `minLength: 1`, `maxLength: 64`, no coercion.

**Gap closed:** 7 of 8 codex punch-list issues. Slug grammar is now byte-level conformance-checkable, with a provably-correct test suite (verified live). JSON Schema work in app-T9 inherits a one-liner pattern field.

**Next:** app-T8 — Resolve README/CLI mismatch. README says `python -m scripts.apps_cli validate my-standup` but no `scripts/` directory exists in the app.md repo (the CLI lives in atrisos-backend). Three options codex flagged: (a) remove the references, (b) ship a tiny `scripts/apps_cli.py` in this repo, (c) make README explicit that the CLI lives in atrisos-backend. Best choice: probably (c) for honesty + maybe a minimal validator stub for app-T11. Don't pre-empt the validator work though — keep this tick to the README fix.

**Signal:** [TICK_COMPLETE] metric=slug_regex_pinned=1,manifests_pass=10/10,negative_controls_reject=9/9


---

## Tick 8 — 2026-04-29 (app-T8: README/CLI mismatch resolved)

**Horizon:** APP.md becomes a real public standard.

**Task:** app-T8 — Resolve README/CLI mismatch. README quickstart (lines 75-78) said `python -m scripts.apps_cli validate my-standup` but no `scripts/` directory exists in the app.md repo (the CLI lives in atrisos-backend/backend/scripts/apps_cli.py). Anyone copy-pasting from the public repo got `No module named scripts`.

**Metric:** Stale `python -m scripts.apps_cli` references in README: 1 → 0 (2 instances replaced). Working `python3 -m scripts.apps_cli` invocations now point at the correct working directory (`atrisos-backend/backend/`) with venv + pip install steps. Live smoke test (running the README's exact command path with venv active): `valid=True` for examples/burn-rate, examples/atris-revenue, examples/commit-digest. Three of seven public examples roundtrip to canonical JSON via the documented command. Quickstart is now copy-pasteable.

**BS check:** ran. (a) Read the actual `apps_cli.py` source — its docstring confirms `python -m scripts.apps_cli ...` invocation (run from `backend/`), not `python -m backend.scripts.apps_cli ...` as the first plan draft proposed. Codex caught this in plan review. (b) Live execution from `atrisos-backend/backend/` with venv active produced `valid=True` JSON output for all three tested examples. (c) `run` comment originally said "subprocess execution" but the CLI supports both `local` and `subprocess` runtimes (per `_CLI_SUPPORTED_RUNTIMES`); fixed comment to "execute (local / subprocess)" to avoid misleading readers with `runtime: local` manifests like commit-digest. (d) Verified CLI resolves both relative and absolute paths.

**Codex plan review:** APPROVED option C with one correction: the proposed module path `python -m backend.scripts.apps_cli` was wrong — the CLI's own usage docstring imports as `scripts.apps_cli` (run from `backend/`). Applied codex's corrected snippet. Also confirmed: option (b) (ship a stub CLI in app.md repo) creates a maintenance fork; option (a) (just delete the snippet) loses real signal. Option (c) is the honest fix.

**Codex output review:** APPROVED with three normative fixes: (a) add `python3 -m venv .venv && source .venv/bin/activate` before pip install (cargo-cult installs into system python is the #1 bug on first contact); (b) note that the path can be relative or absolute (CLI resolves it) instead of forcing absolute; (c) sharpen the "other runtimes" line to "The commands above use Atris as the reference runtime; APP.md itself is runtime-agnostic." All three applied. Also flagged the misleading `# subprocess execution` comment, addressed in BS check (c).

**Gap closed:** 8 of 8 codex punch-list issues. The keystone for v1 credibility is in place: a stranger cloning github.com/atrislabs/app.md can copy-paste the quickstart and get a working `valid=True` JSON output in under 60 seconds. No more "module not found" first-contact failure. The spec is now fit for OUTREACH.md's target list.

**Next:** Phase pivot. All 8 punch-list items closed → spec hardening + distribution. Next tick = app-T9: publish normative JSON Schema at `schema/app.schema.json` derived from SPEC.md (root `additionalProperties: true` + closed sub-schemas with `additionalProperties: false` for secrets/auth/endpoints.*/monetization + `pattern: ^[a-z][a-z0-9]*(-[a-z0-9]+)*$` for slug/member/skills[]/created_by_agent + per-runtime conditional rules). Falsifier: validate all 7 public examples + 4 templates against the schema; expect 11/11 pass. After T9: T10 (fixtures/valid|invalid/), T11 (50-line reference validator), T12 (LAUNCH.md), T13 (OUTREACH.md), T14 (1 outbound notification — REQUIRES Keshav confirm).

**Signal:** [TICK_COMPLETE] metric=cli_quickstart_works_end_to_end=3/3,stale_refs_in_readme=0/0


---

## Tick 9 — 2026-04-29 (app-T9: normative JSON Schema published)

**Horizon:** APP.md becomes a real public standard.

**Task:** app-T9 — Publish normative JSON Schema for APP.md spec v1 at `schema/app.v1.schema.json`. Until now SPEC.md was prose-only; any third party wanting to add APP.md support had to read the spec and guess. Now the schema is machine-checkable in any JSON Schema Draft 2020-12 validator (Python jsonschema, ajv, go-jsonschema, etc.).

**Metric:**
- Schema file: `schema/app.v1.schema.json`, 168 lines, single self-contained file (no external $refs).
- `Draft202012Validator.check_schema()` PASSES — schema is a valid JSON Schema 2020-12 document.
- 10/10 in-repo manifests validate (7 examples + 3 templates).
- 21/21 negative controls REJECT, covering: missing-required, bad-enum, 5 slug-grammar variants, slug rule on member/skills[]/created_by_agent, multiline description, block_pipeline_id null, block_pipeline_id on wrong runtime, schema_version=2, template-with-binding, private-web-no-auth, oauth-without-issuer, jwt-without-issuer, bad-URL, unknown key inside auth, unknown key inside monetization.
- $id pinned to `https://atris.ai/schema/app.v1.schema.json` (version-pinnable; v2 will get a new file).

**BS check:** ran on novel inputs not in training data:
- (a) `schema_version: 2` correctly rejects (const:1 enforces this v1 schema doesn't accept v2 manifests — codex's plan-review correction).
- (b) `auth.type: oauth` without `issuer` correctly rejects (the conditional codex flagged as missing in output review, then added).
- (c) Closed sub-schema rejection works on novel field names ("rebate" inside monetization, "extra_field" inside auth).
- (d) `description: "line1\nline2"` correctly rejects (multiline → spec says single-line, codex flagged in output review, added).
- (e) URL pattern `^https?://[^\s/$.?#][^\s]*$` rejects "not-a-url" but accepts every example endpoint URL.
- All 21 rejections produced human-readable jsonpath error messages — not just opaque "validation failed".

**Codex plan review:** APPROVED with 4 corrections all applied: (1) `schema_version: const: 1` (not minimum), (2) version-pinned `$id`, (3) UUID regex (not `format: uuid`), (4) auth-conditional for non-public web/webhook/external + forbid block_pipeline_id on local. Codex also flagged collision check clean (no pytest, no MAP, no Slack — sibling repo write only).

**Codex output review:** APPROVED with 5 tightening fixes all applied: (1) tighter URL pattern (host required), (2) issuer-required-for-oauth/jwt conditional, (3) single-line description, (4) bad-slug coverage for member/skills/created_by_agent, (5) cite schema $id from SPEC.md. Bumped negative controls 8 → 21. Codex correctly flagged that the metric proves "valid Draft 2020-12 schema + 10 fixtures pass" but NOT "schema fully machine-checks SPEC v1" — IANA TZ validity, RFC 8785 canonicalization, and body content are out of JSON Schema's expressive range and remain parser-level (now stated explicitly in SPEC.md).

**Gap closed:** A third party can now `pip install jsonschema && python3 -c "import json,jsonschema,yaml,sys; m=yaml.safe_load(open(sys.argv[1]).read().split('---',2)[1]); jsonschema.Draft202012Validator(json.load(open('app.v1.schema.json'))).validate(m)" path/to/APP.md` and either get silence (valid) or a structured error path (invalid). The credibility-blocker for OUTREACH.md is removed: every prospective implementer can build a parser without reading 200 lines of prose.

**Next:** app-T10 — Ship `fixtures/valid/` and `fixtures/invalid/` directories. Today the validator has fixtures inline in the test script; they need to live as committed JSON/YAML files so any conformance-test suite can pick them up. Plan: `fixtures/valid/{minimal,with-secrets,with-schedule,subprocess-with-pipeline,template,web-public,webhook-private}.yaml` (~7 fixtures showing each conformance shape) + `fixtures/invalid/{missing-required,bad-runtime,uppercase-slug,multiline-description,oauth-without-issuer,template-with-binding,private-web-no-auth,monetization-unknown-key}.yaml` with a sibling `expected-error.txt` per file documenting the expected jsonpath that fails. Falsifier: a 30-line conformance-test runner over the fixtures directory exits 0 only when every valid passes + every invalid fails with the documented path.

**Signal:** [TICK_COMPLETE] metric=schema_valid=1,manifests_pass=10/10,negative_controls_reject=21/21


---

## Tick 10 — 2026-04-29 (app-T10: conformance fixtures + index-driven runner)

**Horizon:** APP.md becomes a real public standard.

**Task:** app-T10 — Ship `fixtures/valid/` + `fixtures/invalid/` + `fixtures/conformance.json` (index) + `scripts/run_fixtures.py` (runner). Until now the v1 schema published in tick 9 had only inline test cases in /tmp; a third party building a parser had no public conformance corpus to test against.

**Metric:**
- 10 valid YAML fixtures, every shape that v1 admits: minimal-local, subprocess-with-pipeline, subprocess-implicit, ec2-with-schedule (timezone: America/Los_Angeles), web-public, webhook-private (auth.type:hmac), external-oauth (auth.type:oauth + issuer), template, ios (bundle_id+deep_link_scheme), with-events-schema (open ui_spec + events_schema).
- 13 invalid YAML fixtures, each failing under a different schema rule: missing-required, bad-enum, 2 slug-grammar variants, multiline-description, block_pipeline_id-null, block_pipeline_id-on-web, schema_version=2, template-with-binding, private-web-no-auth, oauth-without-issuer, auth-additionalProperties, monetization-additionalProperties.
- `conformance.json` (index) pins SHA-256 of every fixture + structured `expected_paths` (e.g. `auth.issuer`, `monetization.rebate_pct`) + `keyword` annotation per invalid case.
- `scripts/run_fixtures.py` is index-driven (not filesystem-driven): asserts FS exactly matches index, sha256 matches, every valid passes, every invalid fails with at least one path matching the case's expected_paths.
- Live results: 10/10 valid pass + 13/13 invalid reject + 0 failures + exit 0.

**BS check:** 4 tamper scenarios on the tightened (index-driven) runner:
- (a) modify a valid fixture body → sha256 mismatch → exit 1 ✓
- (b) add an orphan .yaml file → orphan check fires → exit 1 ✓
- (c) tamper an invalid fixture so it now passes schema → unexpected-pass → exit 1 ✓
- (d) clean re-run → exit 0 ✓

**Codex plan review:** APPROVED with 3 corrections all applied: (1) Fixtures are YAML, runner needs PyYAML — declared in deps + README. (2) `.expected.txt` was too implementation-loose — replaced with structured `expected_paths` array per case in `conformance.json`. (3) Runner must also fail on missing `.expected.txt`, count mismatch, and unexpected pass — all enforced.

**Codex output review:** Pushed back on the conformance-scope claim (correctly). Approved as a "Python schema-fixture runner" after 4 tightenings, all applied: (1) Replaced `.expected.txt` files with structured `conformance.json` index containing `keyword` + `expected_paths`. (2) Replaced fragile `not.anyOf[].required` walking — it's still in `normalize_path` as a best-effort, but the index's `expected_paths` is now the source of truth, so future conditionals using exotic `not` shapes can name the forbidden field directly in the index without parser changes. (3) Added SHA-256 hashes per fixture to `conformance.json` to catch vendored/offline drift. (4) Removed hard-coded counts from runner; everything derives from the index.

Codex correctly flagged that this corpus does NOT prove FULL v1 conformance — that's what fixtures/README.md's "What this corpus does NOT prove" section now documents explicitly: YAML pre-canonicalization rejects (duplicate keys/anchors/tags/NaN), `spec_digest` byte-equivalence vectors, IANA timezone validity, cron syntax, unknown-top-level preservation across re-emit (Rule 4c), and body content are all out of JSON Schema's expressive range. They are tracked as future ticks under the umbrella "parser-level conformance corpus" — likely T10b (YAML rejects), T10c (spec_digest vectors), T10d (frontmatter+body fixtures with re-emit round-trip).

**Gap closed:** A third party can now `pip install jsonschema PyYAML && python3 scripts/run_fixtures.py` from a clone of the spec repo and either get exit 0 (their copy of the schema is conformant + the corpus is intact) or a structured per-fixture failure. The schema-shape conformance contract is now machine-enforceable. Quality bar for schema mods: any future schema change MUST keep the suite at exit 0; if not, the schema or the corpus index is wrong.

**Next:** app-T11 — Ship a 50-line reference validator at `scripts/validate.py` in the app.md repo. Public-facing example: parse APP.md frontmatter, validate against schema, print clean JSON or structured error. Different from `scripts/run_fixtures.py` (which validates the corpus); this is "validate ONE manifest" — the simplest possible APP.md tool, the thing OUTREACH.md (T13) recipients can copy as their starting parser. Pure stdlib + 2 deps (PyYAML, jsonschema). Falsifier: piping any of the 10 valid fixtures should print canonical JSON exit 0; piping any of the 13 invalid fixtures should print the failing path and exit non-zero.

**Signal:** [TICK_COMPLETE] metric=valid_pass=10/10,invalid_reject=13/13,tamper_caught=4/4
