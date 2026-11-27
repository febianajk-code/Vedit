---
name: remake-build
description: >-
  Rebuilds the app screen by screen from the recon map and the architecture:
  shell first, then the core loop end to end, then every remaining screen
  with all of its states, ticking off remake/features.csv as it goes. Fifth
  step of the Remake pack. Use when the user says "build it", "start the
  remake", "build screen S07", or after /remake-design.
---

# remake-build

Input: `remake/recon.md`, `remake/architecture.md`, `remake/tokens.json`,
`remake/features.csv`. Output: the app itself, in the user's project, plus
ticked rows in `features.csv`.

## Order of work

Follow the milestones in `remake/architecture.md` exactly. Each one ends in
something a human can click:

1. **Project shell.** Repository layout, theme wired to tokens.json, routing,
   a home screen that renders. Nothing else.
2. **Auth.** Sign up, sign in, sign out, the protected route wrapper.
3. **The core loop, end to end.** The flow people pay for, straight through
   the happy path with real data. Ugly is fine; fake is not.
4. **The rest of the must rows.** Every `must` in features.csv, one flow at a
   time.
5. **Shoulds, then coulds**, in the same order.
6. **States.** Empty, loading, error, permission denied, and mobile for every
   screen in the recon map's states column.

## How to build a screen

1. Find its row in the recon map: ID, purpose, components, states.
2. Build only from components in the design system. A one-off style is a
   token that wants a name.
3. Wire it to the real API from the architecture's surface list. Mocks are
   allowed for one session and then deleted.
4. Tick the `clone` column in `remake/features.csv`: `yes`, `partial`, or
   leave `no`. Be honest; remake-diff reads this file.
5. Stop and run the app. Every milestone ends with the user clicking through
   the new flow before the next one starts.

## The rules

- **No stub screens in the final pass.** A screen that renders "TODO" is a
  `partial`, and `partial` rows are named in the diff report.
- **Keep the constraints.** If the schema says one booking per slot, the UI
  still handles the rejection. The database is not the UX.
- **Commit per screen.** One screen, one commit, message citing the screen
  ID (`S07: booking page`). Rollbacks stay cheap.
- **Do not touch `remake/screens/`.** Reference only, never shipped.

## When the map is wrong

Screens drift from the recon map while building. When reality disagrees:
fix the code, then update `remake/recon.md` the same day, so remake-diff and
remake-test read the truth.

## Output

A running app at the current milestone, `features.csv` ticked, then a
summary: screens done, rows still `no`, the next milestone, and the next
step: `/remake-backend` if services remain, otherwise `/remake-test`.
