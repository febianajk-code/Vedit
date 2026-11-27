---
name: remake-backend
description: >-
  Wires up the parts the UI cannot fake: authentication, the database with
  its constraints, payments, email and third-party integrations, plus the
  environment and secret handling for all of it. Sixth step of the Remake
  pack. Use when the user says "add auth", "hook up the database", "add
  payments", "wire up the integrations", or after /remake-build.
---

# remake-backend

Input: `remake/architecture.md` (stack, schema, API surface) and the current
state of the app. Output: working services, a `.env.example` checked into
the repo, and real secrets in the user's environment only.

## The rules

- **Secrets never enter the repo, the logs, or the chat.** Keys go in the
  user's environment or the host's secret store. The repo gets
  `.env.example` with empty values and a comment on each line.
- **Users own their data.** Authed endpoints filter by the caller's user id.
  A missing `where user_id =` is a breach, not a bug.
- **Payments follow the provider.** Prices and products live in the
  provider's dashboard, webhooks are verified, and the app never trusts a
  price sent by the client.
- **Fail closed.** An integration that errors must not silently degrade into
  pretending success.

## Step 1: authentication

Sessions or tokens per the architecture, password hashing with a modern
algorithm, email verification if the original app has it, and the protected
routes from the build. Sign-out must actually invalidate, not just delete a
cookie.

## Step 2: database

Run the schema from `remake/architecture.md` as migrations, never as hand-edited
state. Seed scripts live in the repo and are idempotent. Every constraint in
the schema section ships; a constraint left out to make a test pass is a bug
in the test.

## Step 3: API hardening

Walk the API surface one line at a time: input validation, authorization,
rate limits on anything a guest can reach, and error responses that say what
happened without leaking internals.

## Step 4: integrations

One module per provider, behind the interface from the architecture, with
the keys read from the environment. Email (verification, notifications),
payments (checkout, webhook, plan gating), and whatever the core loop needs
(calendar, file storage, search). If the provider offers a test mode, the
default configuration uses it.

## Step 5: background work

Anything slower than a click becomes a job: emails, exports, syncs. The job
queue, retries and a dead-letter story all come from the architecture doc.

## Output

Working services against the running app, `.env.example`, and a summary:
integration count, what runs in test mode, any constraint that had to move,
and the next step: `/remake-test`.
