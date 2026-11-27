---
name: remake-deploy
description: >-
  Ships the remake live on the user's own domain: a preflight check of
  secrets, migrations, environment and monitoring, the first deploy to the
  host chosen in the architecture, a smoke test against the live URL, and
  the rollback path written down before it is needed. Last step of the
  Remake pack. Use when the user says "deploy it", "put it live", "ship
  it", or after /remake-launch.
---

# remake-deploy

Input: the running app, `remake/architecture.md` (hosting choice),
`remake/test-plan.md` (sign-off), `remake/listing.json`. Output: a live URL
on the user's domain, and `remake/preflight.md` (template: preflight.md in
this folder) filled in with real values.

## The rules

- **Deploy only after sign-off.** If the test plan's boxes are not ticked,
  the answer is "not yet", and the open S1/S2 bugs are listed.
- **Secrets stay in the host's store.** Nothing secret goes into image
  layers, build logs, or the repo. The deploy log is checked for leaks
  before it is shared.
- **One host, as architected.** The deploy follows `remake/architecture.md`.
  A different platform is a change to the architecture, not a detour.

## Step 1: preflight

Work through `remake/preflight.md` top to bottom and fill it in:

- secrets present in the host's store, `.env.example` current
- migrations apply clean against a fresh database copy
- the build runs from a clean checkout, not the working tree
- error tracking wired (anything quiet enough to be free)
- the domain resolves, TLS on, http redirected

## Step 2: first deploy

Deploy to staging or the host's preview environment first. The database has
its own credentials, the integration providers run in test mode, and the
seed data is obviously fake.

## Step 3: smoke test the live URL

The happy path of the core loop, executed against the live URL with test
data: sign up, do the thing, see the result, sign out. Any failure is fixed
and re-deployed; the smoke test re-runs from the top.

## Step 4: go live

Point the real domain, switch providers from test to live keys one at a
time, re-running the smoke test after each switch. Payments go last and are
tested with a real small charge the user approves.

## Step 5: write down the way back

The rollback: the previous known-good deploy, how to restore the database
(with the backup taken just before go-live), and who flips the switch. A
rollback that needs research at 2am is not a rollback.

## Output

The live URL, `remake/preflight.md` filled in, the rollback note, then a
closing summary of the whole remake: parity score, bugs fixed, the angle,
the URL. The pack is done; new feature requests start a fresh pass through
the relevant skills.
