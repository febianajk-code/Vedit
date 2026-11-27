---
name: remake-architect
description: >-
  Turns the recon map into a build plan: picks the stack, writes the database
  schema with real constraints, defines the API surface, orders the build and
  flags the risky parts. Second step of the Remake pack. Use when the user
  says "plan the remake", "pick a stack", "design the schema", "architect
  this", or after /remake-recon has produced remake/recon.md.
---

# remake-architect

Input: `remake/recon.md` and `remake/features.csv`. Output: `remake/architecture.md`
(template: architecture.md in this folder). If the recon map is missing, send
the user back to `/remake-recon` first. Guessing at screens produces a schema
that guesses too.

## Step 1: read before you write

Read the whole recon map. Note: the core loop, the entities and their
confidence labels, the flows and their edge cases, the size guess, and every
skip row. The architecture serves the slice, not the whole app.

## Step 2: pick the stack

Choose the boring option that fits the slice, and say why in one line each:

- **Framework and language.** Default to what the user already knows.
- **Database.** Postgres unless a document model earns its keep.
- **Hosting.** One platform that can hold the app, the database and the
  background jobs. Fewer moving parts at launch.
- **Third-party services.** Email, payments, file storage, search: hosted
  providers with free tiers, each behind one interface so it can be swapped.

Constraints beat preferences: offline-first pushes toward local-first storage,
realtime pushes toward websockets or a hosted channel, and regulated data
pushes toward a region-pinned database.

## Step 3: write the schema

One table per entity from the recon map, plus the boring ones the recon map
skipped: users, sessions, and an audit or events table if money or permissions
are involved.

For every table: columns with types, indexes on what flows query, and the
constraints that make bugs impossible:

- uniqueness where duplicates would corrupt state (one booking per slot)
- foreign keys with deliberate on-delete behaviour
- check constraints on status fields and amounts
- timestamps that store time zones, not local wall clocks

Every constraint traces back to a flow edge case in the recon map. A flow that
says "slot taken while typing" becomes a unique index plus a transaction, not
a hope.

## Step 4: define the API surface

One line per endpoint: method, path, who may call it, what it returns, which
flow it serves. Group by flow, in flow order. Leave out anything no flow
needs; an endpoint nobody calls is attack surface with tests.

## Step 5: order the build

Number the milestones so that each one ends in something clickable:

```
M1 shell + auth                     (a user can sign up and land somewhere)
M2 the core loop end to end         (the flow people pay for, ugly but real)
M3 the rest of the must rows        (every must in features.csv is done)
M4 shoulds, then coulds
M5 polish: states, empty views, mobile
```

Map each milestone to its `features.csv` rows so remake-build can tick them
off, and remake-diff can score the same rows later.

## Step 6: name the risks

The three to five things most likely to sink the schedule, each with the
cheapest way to find out early: a spike, a hosted service, a cut scope. Paying
users' data, payments correctness and realtime sync usually live here.

## Output

`remake/architecture.md`, then a short summary: stack in one line, table and
endpoint counts, the milestone list, the top risk, and the next step:
`/remake-design`.
