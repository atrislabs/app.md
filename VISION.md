# APP.md Vision

APP.md exists to make AI apps portable.

The mission is a small one on purpose: define the app contract that survives when the runtime changes. An APP.md folder should be understandable to a human, parseable by a machine, safe to review in a diff, and runnable by any platform that chooses to implement the spec.

## The Problem

Agent apps are becoming real software, but their shape is still trapped inside each runtime.

One platform stores the app as database rows. Another uses JSON. Another asks for Python classes, deployment decorators, or marketplace forms. That means the app is not really portable: changing runtimes means rewriting the manifest, retesting behavior, and re-explaining the app to every tool in the chain.

APP.md is the runtime-independent layer below that fragmentation.

## The Contract

An APP.md is not the runtime, marketplace, billing system, scheduler, or sandbox.

It is the portable app contract for a capability surface:

- what the app is called
- where it can run
- what secrets it expects
- what surfaces it can reach
- how it is scheduled
- what permissions and authentication shape it needs
- what instructions the runtime hands to the agent

The runtime still decides how to execute. The manifest gives every runtime the same starting point.

## What an App Can Be

An APP.md app can be a workflow, tool, agent skill, UI, webhook wrapper, scheduled job, local automation, marketplace template, CLI command, MCP-facing capability, or another app's dependency.

The important rule is that it has a boundary. Something can call it, render it, schedule it, inspect it, and verify what happened.

That means one app can also connect to another app. A customer support app can call a refund-policy app. A daily briefing app can call a calendar app and a commit-summary app. A review app can call a verifier app, then write the receipt another agent uses next time. The [`app-composition-coordinator`](./examples/app-composition-coordinator/APP.md) example shows app-to-app composition, and [`learning-loop-reviewer`](./examples/learning-loop-reviewer/APP.md) shows the Review Inbox / Learning Loop pattern as an APP.md manifest.

## Who Does What

Customers can package a repeatable capability, connect it to their runtime, expose it in a UI or CLI, publish it as a template, move it between platforms, and audit its behavior through logs and receipts.

Users and agents can run an app, schedule it, click it, call it through an API or MCP tool, chain it from another app, inspect its manifest, approve sensitive actions, and review the output.

Runtime builders can parse the same manifest, map it onto their own execution model, and decide how to render, secure, bill, schedule, and observe it.

## Where an App Shows Up

At rest, an app is a folder with an `APP.md` manifest.

At execution time, it runs in a runtime: local process, shared backend, sandbox, webhook, external service, web app, iOS app, or template install flow.

At use time, it can show up as a UI, CLI command, scheduled job, webhook, API endpoint, MCP tool, agent-callable function, marketplace listing, or another app's internal dependency.

## Apps in the Improvement Loop

An app should not only do work. It should make work easier to improve.

The loop is: observe -> understand -> decide -> act -> verify -> receive feedback -> learn -> improve the loop -> repeat.

In APP.md terms, that means the manifest declares the capability, the runtime executes it, the app writes outputs and receipts, a human or agent reviews the result, and the next version becomes easier to trust. [`RECEIPTS.md`](./RECEIPTS.md) defines the receipt packet that makes this self-correcting loop auditable; [`learning-loop-reviewer`](./examples/learning-loop-reviewer/APP.md) shows how receipts become owner-routed improvement tasks.

## Principles

1. **One folder is the source of truth.** The app should be inspectable, forkable, and movable without exporting hidden platform state.
2. **Human-readable first, machine-verifiable always.** Markdown makes the app legible; schema and fixtures make it implementable.
3. **Portability beats ownership.** APP.md should compose with existing runtimes and other apps instead of trying to replace them.
4. **Security boundaries are explicit.** Secrets, auth, endpoints, and monetization are declared, not buried in prompt text.
5. **Versioning is part of the contract.** A `schema_version: 1` parser should keep working as v1 grows, and breaking changes should ship as a new version with migration notes.

## What v1 Proves

v1 proves that an agent-runnable app can be represented as one markdown file with a typed frontmatter contract, a free-form instruction body, a stable schema, a reference validator, and a conformance suite.

That is enough for runtime builders to parse APP.md today, map it onto their own execution model, and tell authors exactly which fields failed validation.

## Where This Goes

If APP.md works, AI apps become easier to move, audit, publish, call, compose, improve, and archive.

An app could start as a local automation, move to a hosted runtime, appear in a marketplace, or be inspected by an agent without losing its core declaration. The important outcome is not that every runtime behaves the same. The important outcome is that every runtime can understand the same app contract.
