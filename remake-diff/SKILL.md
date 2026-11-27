---
name: remake-diff
description: >-
  Scores the remake against the original: a parity number from the feature
  matrix, layout scores from screenshot pairs, the must-haves still missing,
  and the build order for the gap. Eighth step of the Remake pack. Use when
  the user says "how close is it", "score the remake", "what's missing", or
  after /remake-test.
---

# remake-diff

Input: `remake/features.csv` (ticked during the build) and screenshot pairs
from `remake/screens/` against the remake. Output: a parity report, optionally
saved as `remake/parity.md`.

## The score

Two numbers, weighted 80/20. Features are what users pay for.

- **Feature parity** comes from `parity.py` reading `remake/features.csv`.
  Weights: must 3, should 2, could 1. `yes` counts 1, `partial` 0.5, `no` 0.
  `skip` rows and rows where `original` is `no` are excluded, so the number
  only measures parity.
- **Layout parity** comes from `imgdiff.py` per screenshot pair, comparing
  structure rather than colour, so the rebrand does not punish the score.

## Step 1: score the features

```bash
python3 parity.py remake/features.csv
python3 parity.py remake/features.csv --fail-under 80
```

Read the by-area list weakest first: that is the build order. Check the
problems section too; rows with typos in `priority` or `clone` are counted
conservatively and flagged.

## Step 2: score the screens

One pair per key screen, same viewport, same content state:

```bash
python3 imgdiff.py remake/screens/S07-original.png remake/screens/S07-clone.png --json
python3 parity.py remake/features.csv --visual remake/diffs/*.json --markdown > remake/parity.md
```

A low layout score on a screen whose features all pass means the structure
drifted: compare the two images and name what moved.

## Step 3: read the must-haves

The report states plainly whether every must row is done. A remake with an
unfinished must is not shippable, whatever the total says.

## Step 4: report honestly

Present: the parity number, must-haves done out of total, the three weakest
areas, the skipped rows with reasons, and what to build next. Never round up
for morale; the number exists to steer work.

## Output

The parity report (and `remake/parity.md` when asked), then the next step:
`/remake-entrepreneur` if there is appetite to outdo the original,
`/remake-brand` when the feature gap is closed.
