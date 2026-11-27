---
name: remake-brand
description: >-
  Names the remake and gives it a brand of its own: name candidates with a
  trademark sanity check, a voice, a palette shifted from the tokens, and a
  sweep of the codebase for leftover strings and assets from the original.
  Tenth step of the Remake pack. Use when the user says "name it", "rebrand
  it", "make it ours", "check for leftovers", or after
  /remake-entrepreneur.
---

# remake-brand

Input: the codebase, `remake/tokens.json`, the positioning paragraph from
remake-entrepreneur. Output: a brand note in `remake/brand.md`, updated
tokens, and a clean sweep.

## The rules

- **The original's name, logo and copy are theirs.** Nothing about them
  survives into the remake: not the name with one letter changed, not the
  tagline reworded, not the logo recoloured.
- **Check before you fall in love.** A quick trademark sanity check
  (searchable registries, app stores, domain availability) happens before
  the user repaints the whole product.
- **One voice.** Pick three adjectives, write them in the brand note, and
  make every string in the app answer to them.

## Step 1: name it

Generate candidates that pass three filters: pronounceable on a phone call,
no collision with apps in the same category, and a plausible domain. Present
five to eight, grouped by idea, with the top pick justified against the
positioning paragraph. The user picks; the skill never ships a name the user
did not choose.

## Step 2: sanity check

For the shortlist: search app stores for collisions, check trademark
databases at a first-pass level, check domain availability. Report the
collisions found and flag them; this is a filter, not legal advice, and the
brand note says so.

## Step 3: voice

Three adjectives and what they forbid. If the voice is "calm, plain,
exact", then no exclamation marks, no "supercharge your workflow", no
sentence longer than two clauses in UI copy. Rewrite the strings the build
inherited from placeholder copy.

## Step 4: make the tokens yours

Shift the palette in `remake/tokens.json` far enough from the original that
side by side they read as different products, while the contrast check still
passes:

```bash
python3 contrast.py remake/tokens.json --min 4.5
```

New logo as an original mark, openly licensed typeface, and the theme map
pointing at the new roles.

## Step 5: sweep the codebase

Hunt the leftovers: the original's name in strings, comments, config,
`package.json`, error messages, favicons, placeholder text. Run:

```bash
python3 sweep.py <project dir> --old "<original name>" --old "<old codename>"
```

The tool lists file and line for every hit. Fix them all, then re-run for a
clean report. Also sweep binary assets: favicons and logos are strings too.

## Output

`remake/brand.md` (name, voice, palette, the check results), swept
codebase, updated tokens, then the next step: `/remake-launch`.
