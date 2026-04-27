---
schema_version: 1
name: atris-pitch-deck
slug: atris-pitch-deck
description: The Atris Labs fundraising + recruiting + design-partner pitch deck. Rendered full-screen, exportable to PDF, updated by the fundraiser member.
access: public
runtime: web
vault: atris-kms
runtime_auth: none
endpoints:
  frontend: https://atris.ai/deck
capabilities:
  - render_deck
  - export_pdf
  - version_history
secrets: []
member: fundraiser
skills:
  - deck-design
  - writing
  - slides
surfaces:
  - web
render: fullscreen
artifact_dir: decks/atris-pitch-v3
ui_spec:
  layout: slides
  theme: atris-dark
  transitions: none
  nav: keyboard+arrows
  export:
    - pdf
    - png-per-slide
wiki_paths:
  - wiki/company/vision
  - wiki/company/traction
  - wiki/company/team
created_by_agent: fundraiser
monetization:
  price_credits: 0
---

# atris-pitch-deck

Proves `runtime: web` + `render: fullscreen` + `artifact_dir` cover the "a deck is an app" claim.

## What it does

- Serves the live deck at `atris.ai/deck` — slides rendered from Markdown in `decks/atris-pitch-v3/`.
- Exports to PDF on demand (endpoint: POST to `/export`).
- Tracks open rate per slide when shared publicly (`app_events` emits `slide_viewed`).
- Hot-reloads on edits from the fundraiser member.

## Inputs

No secrets; the deck is public.

## Outputs

- Hosted at `https://atris.ai/deck` — read via browser.
- PDF in `decks/atris-pitch-v3/exports/`.
- `slide_viewed` events in `app_events` for the analytics layer.

## Guardrails

- Public access; nothing confidential should land in `decks/atris-pitch-v3/` (private decks go to a different app with `access: private`).
- Version history kept in git; never edit the "current" file — branch + merge.
