---
name: remake-recon
description: >-
  Reverse-engineers any app into a recon map: screen inventory, user flows,
  component list, inferred data model and a feature matrix, built from public
  pages, screenshots, app store listings, help docs and the user's own
  account. The opening move of the Remake pack. Use when the user says
  "remake this app", "clone X", "reverse engineer X", "how does X work",
  "map out X", "what screens does X have", "I want my own version of X", or
  pastes an app URL or store link and wants to rebuild it.
---

# remake-recon

Every other skill in the pack reads what this one writes. A thin recon map
produces a thin remake, so spend the time here.

Output lands in the user's project:

```
remake/recon.md         the recon map (template: recon-map.md in this folder)
remake/features.csv     the feature matrix (template: features.csv in this folder)
remake/screens/         reference screenshots of the original. Never shipped.
```

## The rules, before anything else

This skill rebuilds **what an app does**, clean-room style. It studies
features and the way users move through them. It never takes what the app
owns.

- **Public sources and the user's own account only.** Never touch an account
  that is not the user's, never ask for credentials, never bypass a login or
  a paywall by any means.
- **Read like a person, not a crawler.** No bulk scraping, no download loops.
  If a browser tool is attached to the user's own browser, walk the pages at
  human speed with the user watching.
- **No source code, no private endpoints.** Do not save the app's JavaScript
  bundles, decompile its binary, or record network traffic to lift endpoints.
  Reading public API documentation is fine.
- **Check the terms.** Some products forbid using an account to build a
  competitor. If the user's account carries terms like that, say so out loud
  and fall back to public sources.
- **Screenshots are reference only.** They stay in `remake/screens/`, drive
  layout comparisons, and never end up inside the remake.

## Step 1: scope

Ask three questions, or propose answers and get a yes:

1. **Which app, which platform.** Web, iOS, Android, desktop.
2. **Which slice.** "All of Slack" is not a project. "Slack's channels,
   messages and search" is. Default to the core loop: the flow people pay
   for.
3. **Who it serves.** The user's own business, a niche, a product to sell.

## Step 2: list the sources

Write a sources table first, one URL per row. In rough order of value:

| source | what it gives you |
| --- | --- |
| help center / docs | the fullest feature list there is, plus settings |
| pricing page | which features matter, because they gate them |
| changelog | what the team ships and cares about now |
| app store listing | screenshots of key screens, the pitch, ratings |
| public walkthroughs | real flows, click by click |
| marketing site | positioning and the core loop in their words |
| the user's own account | the real thing, every state, user-driven |
| public API docs | the data model, nearly for free |

## Step 3: screen inventory

One row per screen. IDs are stable: S01, S02... every other file cites them.

`ID | screen | route or how you reach it | purpose | key components | states seen`

States matter: empty, loading, filled, error, permission denied, mobile. A
state you did not write down is a state you will not build.

## Step 4: user flows

F01, F02... each is a goal plus the screens it passes through:

```
F01 Guest books a session
    S07 booking page -> S08 choose a slot -> S09 details form -> S10 confirmed
    edge: no slots left, time zone mismatch, slot taken while typing
```

Count the clicks on the happy path. That number is the one to beat.

## Step 5: components

Every repeated UI piece: buttons, inputs, pickers, modals, tables, toasts,
nav. Name, variants, states, screens used on. This list feeds
remake-design.

## Step 6: inferred data model

Entities, fields, relationships, each with evidence and a confidence:

```
Session  id, event_type_id, starts_at, ends_at, guest_name, guest_email,
         status (confirmed | cancelled | moved), answers (json)
         evidence: S09 form fields, S10 confirmation, help doc "Cancel a session"
         confidence: high
```

Label guesses as guesses. remake-architect turns this into a real schema.

## Step 7: feature matrix

Write `remake/features.csv` (columns: feature, area, priority, original,
clone, notes). Priority is must / should / could. `clone` starts at `no` on
every row and fills in during the build. remake-diff scores it.

## Step 8: what cannot be remade

Be honest, as `skip` rows with a reason: licensed content (a music catalogue,
a stock library), the network and its users, data the app owns, partner
deals, hardware, regulated licences (banking, health). "Remake any app" means
the features and the flows, never the property.

## Step 9: size it

Screens, flows, entities, and the hard parts (realtime, sync, payments,
calendar or mail integrations, offline). Give a size: S (a weekend), M (a few
weeks), L (a quarter), XL (rescope). Promise progress, not a perfect clone.

## Output

`remake/recon.md` and `remake/features.csv`, then a five-line summary: the
core loop, screen and flow counts, the three hardest parts, what is out of
scope, and the next step: `/remake-architect`.
