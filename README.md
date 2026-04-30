# APP.md

A markdown-with-frontmatter manifest format for **agent-runnable apps**.

Inspired by [agentskills.io](https://agentskills.io)'s `SKILL.md`. Where `SKILL.md` answers *"how does an agent do X"*, `APP.md` answers *"what does the customer get"* — a self-contained, schedulable, vault-aware app that any agent runtime can pick up and execute.

```yaml
---
schema_version: 1
name: daily-standup
slug: daily-standup
access: private
runtime: subprocess
vault: atris-kms
schedule: "0 7 * * *"
member: chief-of-staff
skills: [memory, slack]
secrets: []
surfaces: [slack, voice, email]
render: none
---

Pull yesterday's commits, top inbox items, and meetings. Post a 5-line briefing to #ops and email me the long version.
```

That's the whole app. The folder it lives in is the source of truth; the runtime is whatever picks up the spec.

## Why a standard

Today every agent platform invents its own app shape — Postgres rows, JSON configs, Python classes, GPT Actions schemas. None survive moving to a different runtime. APP.md is markdown + YAML, runtime-agnostic, diffable, AI-readable, human-editable. If your runtime can parse it, the app runs.

## Anatomy

An app is a folder:

```
my-app/
├── APP.md          # manifest (frontmatter) + instructions (body)
├── README.md       # human-facing description (optional)
├── data/           # app-owned state — runs, caches, outputs
└── logs/           # run history
```

Secrets are **not** in the folder. They live in a vault (`atris-kms`, `byo-aws`, `app_secrets`, or `local`) and are injected into the runtime at run time. APP.md only declares which secret *names* the app needs.

## Eight runtimes, one schema

| `runtime:` | Where it executes | When to use |
|---|---|---|
| `local` | Customer's machine, subprocess | Personal automations, no shared state |
| `subprocess` | Shared backend process | Lightweight digests, scoring, simple agents |
| `ec2` | Atris-hosted sandbox | Multi-vendor data pulls, long-running work |
| `webhook` | Customer-hosted HTTP endpoint | Wrap an existing service as an app |
| `external` | Full-stack external service | Bring an existing app under the spec |
| `web` | Web app + optional MCP | Decks, dashboards, anything that renders |
| `ios` | Native iOS via App Intents | Voice / share-sheet / Shortcuts targets |
| `template` | Marketplace spec, not yet installed | Forkable starting points |

Same frontmatter, different execution binding. See [SPEC.md](./SPEC.md) for the field reference.

## 30-second quickstart

```bash
# Copy a template
cp -r templates/standup my-standup

# Edit the frontmatter + instructions
$EDITOR my-standup/APP.md

# That's it. Hand the folder to any APP.md-aware runtime.
```

To validate or run the manifest, use the reference runtime in [`atrislabs/atrisos-backend`](https://github.com/atrislabs/atrisos-backend):

```bash
git clone https://github.com/atrislabs/atrisos-backend.git
cd atrisos-backend/backend
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -r requirements.txt

python3 -m scripts.apps_cli validate /path/to/my-standup   # parse + lint
python3 -m scripts.apps_cli run      /path/to/my-standup   # execute (local / subprocess)
```

The folder path can be absolute or relative — the CLI resolves it. The commands above use Atris as the reference runtime; APP.md itself is runtime-agnostic, see [SPEC.md](./SPEC.md).

For a no-runtime, validate-only check, this repo ships a 65-line reference parser (`scripts/validate.py`) — copy it as the starting point for your own implementation:

```bash
pip install "PyYAML>=6,<7" "jsonschema>=4,<5"
python3 scripts/validate.py examples/atris-revenue/APP.md   # → exit 0 + canonical JSON
python3 scripts/validate.py path/to/broken.yaml             # → exit 2 + per-error lines
cat APP.md | python3 scripts/validate.py -                  # stdin
```

Run the full conformance suite (10 valid + 13 invalid fixtures) with `python3 scripts/run_fixtures.py`. The schema lives at [`schema/app.v1.schema.json`](./schema/app.v1.schema.json) (`$id: https://atris.ai/schema/app.v1.schema.json`).

## Examples

Seven real apps that ship in production, illustrating most of the schema surface:

| App | Runtime | Demonstrates |
|---|---|---|
| [`commit-digest`](./examples/commit-digest/APP.md) | `local` | Runs entirely on the customer's machine, no secrets, no network |
| [`atris-revenue`](./examples/atris-revenue/APP.md) | `ec2` | Stripe → Slack daily digest, secret declaration |
| [`burn-rate`](./examples/burn-rate/APP.md) | `ec2` | Multi-vendor finance pull (Ramp + Mercury + Brex + Stripe) |
| [`daily-standup`](./examples/daily-standup/APP.md) | `subprocess` | Cron schedule, multi-surface rendering (`[slack, voice, email]`) |
| [`customer-pulse`](./examples/customer-pulse/APP.md) | `subprocess` | `wiki_paths` for per-customer context injection |
| [`atris-pitch-deck`](./examples/atris-pitch-deck/APP.md) | `web` | `render: fullscreen`, `ui_spec`, `artifact_dir` for shared writes |
| [`atris`](./examples/atris/APP.md) | `external` | The framework treated as an instance of its own spec |

## Templates

Start a new app from a built-in scaffold:

| Template | Runtime | Use |
|---|---|---|
| [`deck`](./templates/deck/APP.md) | `web` + `render: fullscreen` | Pitch / sales / data decks |
| [`standup`](./templates/standup/APP.md) | `subprocess` + `schedule: 0 7 * * *` | Daily briefings |
| [`stripe-daily`](./templates/stripe-daily/APP.md) | `ec2` + `[STRIPE_KEY, SLACK_BOT_TOKEN]` | Revenue → Slack |

## Status

Schema v1, in production use at [Atris Labs](https://atris.ai). The reference runtime parses 251 tests' worth of edge cases and dispatches to subprocess + web runtimes today; ec2 / ios / external are scaffolded.

This repo is the spec + examples. The reference parser, dispatcher, and CLI live in [`atrislabs/atrisos-backend`](https://github.com/atrislabs/atrisos-backend) under `backend/services/app_folder_service.py` and `backend/scripts/apps_cli.py`.

## License

MIT — see [LICENSE](./LICENSE). Fork the spec, adapt it for your runtime, ship apps.
