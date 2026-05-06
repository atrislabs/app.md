# APP.md Vision

APP.md exists to make AI apps portable.

The mission is a small one on purpose: define the app contract that survives when the runtime changes. An APP.md folder should be understandable to a human, parseable by a machine, safe to review in a diff, and runnable by any platform that chooses to implement the spec.

## The Problem

Agent apps are becoming real software, but their shape is still trapped inside each runtime.

One platform stores the app as database rows. Another uses JSON. Another asks for Python classes, deployment decorators, or marketplace forms. That means the app is not really portable: changing runtimes means rewriting the manifest, retesting behavior, and re-explaining the app to every tool in the chain.

APP.md is the runtime-independent layer below that fragmentation.

## The Contract

An APP.md is not the runtime, marketplace, billing system, scheduler, or sandbox.

It is the portable app contract:

- what the app is called
- where it can run
- what secrets it expects
- what surfaces it can reach
- how it is scheduled
- what permissions and authentication shape it needs
- what instructions the runtime hands to the agent

The runtime still decides how to execute. The manifest gives every runtime the same starting point.

## Principles

1. **One folder is the source of truth.** The app should be inspectable, forkable, and movable without exporting hidden platform state.
2. **Human-readable first, machine-verifiable always.** Markdown makes the app legible; schema and fixtures make it implementable.
3. **Portability beats ownership.** APP.md should compose with existing runtimes instead of trying to replace them.
4. **Security boundaries are explicit.** Secrets, auth, endpoints, and monetization are declared, not buried in prompt text.
5. **Versioning is part of the contract.** A `schema_version: 1` parser should keep working as v1 grows, and breaking changes should ship as a new version with migration notes.

## What v1 Proves

v1 proves that an agent-runnable app can be represented as one markdown file with a typed frontmatter contract, a free-form instruction body, a stable schema, a reference validator, and a conformance suite.

That is enough for runtime builders to parse APP.md today, map it onto their own execution model, and tell authors exactly which fields failed validation.

## Where This Goes

If APP.md works, AI apps become easier to move, audit, publish, remix, and archive.

An app could start as a local automation, move to a hosted runtime, appear in a marketplace, or be inspected by an agent without losing its core declaration. The important outcome is not that every runtime behaves the same. The important outcome is that every runtime can understand the same app contract.
