---
schema_version: 1
name: deck
slug: deck
description: 'Template: deck'
access: public
runtime: web
vault: local
runtime_auth: none
endpoints:
  frontend: https://atris.ai/deck
capabilities:
- render_deck
- export_pdf
secrets: []
skills: []
wiki_paths: []
artifact_dir: decks/deck-v1
surfaces:
- web
render: fullscreen
ui_spec:
  layout: slides
  theme: atris-dark
  transitions: none
  nav: keyboard+arrows
  export:
  - pdf
  - png-per-slide
created_by_agent: apps-cli
monetization:
  price_credits: 0
---
# deck

A deck is a folder. Author slides in Markdown; the renderer ships them.
