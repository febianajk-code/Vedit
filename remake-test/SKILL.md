---
name: remake-test
description: >-
  Clicks through every flow in the recon map and tests the remake for bugs:
  writes a test plan from the flows, automates the happy paths and the edge
  cases, walks every screen state, and logs bugs by severity until no S1 or
  S2 remains. Seventh step of the Remake pack. Use when the user says "test
  it", "find the bugs", "click through everything", or after /remake-backend.
---

# remake-test

Input: `remake/recon.md` (flows and states), `remake/features.csv`, the
running app. Output: `remake/test-plan.md` and `remake/bugs.md`
(templates: test-plan.md and bug-report.md in this folder), plus automated
specs in the project's test directory.

## Step 1: plan from flows, not from code

One row per flow from the recon map, then one test per step plus one test per
edge case the flow lists. The edge cases are the value: double submit, slot
taken while typing, expired session, time zone crossing, empty states.

## Step 2: automate the happy paths

Write the runner's specs (Playwright if the project has none; a starter is
`e2e.example.spec.ts` in this folder). One spec file per flow, named after
the flow ID. Specs run against the app with test data the script creates and
cleans up after itself.

## Step 3: walk the states by hand

Automated specs cover logic; states need eyes. For every must-have screen,
visit each state from the recon map: empty, loading, filled, error,
permission denied, mobile width. Screenshot what looks wrong and log it.

## Step 4: log the bugs

Every defect goes in `remake/bugs.md` with severity, screen, what happens,
what should happen. Severity: S1 data loss, crash, or core loop broken for
everyone. S2 a must-have flow broken for a case. S3 annoying with a
workaround. S4 polish.

## Step 5: fix loop

Fix S1 and S2 first, re-run the specs, and add a regression case for every
fix. A bug fixed without a test is a bug scheduled to return. Stop when no
S1 or S2 is open; S3 and S4 go on a list for after launch.

## Step 6: sign off

Tick the sign-off boxes in the test plan only when true: all F-flows
automated, no S1 or S2 open, states visited for every must-have screen.

## The rules

- **Test data is disposable, user data is sacred.** Never test against real
  user accounts or production data.
- **Report, do not soften.** A broken flow reads as broken in the log, not
  as "mostly working with rough edges".
- **Keep the specs in CI.** If the project has no CI, say so and leave a
  one-line command in the test plan for running them by hand.

## Output

`remake/test-plan.md`, `remake/bugs.md`, specs committed, then a summary:
flows covered, bugs by severity, what is still open, and the next step:
`/remake-diff`.
