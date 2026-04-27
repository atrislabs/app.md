# atris-revenue

Daily Stripe revenue summary for Atris Labs.

- **Runs:** 9:00 America/Los_Angeles, every day.
- **Output:** Slack `#ops` summary + email to treasury.
- **Operator:** `treasury` member (see `atris/team/treasury/MEMBER.md`).
- **Skill:** `stripe-analytics` (see `.claude/skills/stripe-analytics/SKILL.md`).

Manifest: `APP.md` (the source of truth — the DB row is an index).

See `atris/features/apps/apps-as-folders.md` for the folder-is-the-app model.
