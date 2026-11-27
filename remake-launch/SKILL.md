---
name: remake-launch
description: >-
  Writes the launch materials for the remake: a landing page with a real
  headline, pricing that matches the original's gaps, and an app store or
  product listing, all validated by the bundled listing tool. Eleventh step
  of the Remake pack. Use when the user says "write the landing page", "set
  the pricing", "write the store listing", "prepare the launch", or after
  /remake-brand.
---

# remake-launch

Input: `remake/brand.md`, the positioning paragraph, `remake/features.csv`,
the original's pricing page. Output: `remake/landing.md` (copy, page by
page), `remake/pricing.md`, and `remake/listing.json` validated by
`listing.py`.

## The rules

- **Never name the original as a rival in the listing.** Store rules and
  taste agree here. "A calendar that respects your morning" wins; "better
  than X" gets the listing pulled.
- **Claims trace to rows.** Every feature claim on the landing page points at
  a `yes` row in features.csv. A claim without a row is a refund waiting to
  happen.
- **The voice is the brand's.** The three adjectives from remake-brand edit
  every headline; exclamation marks do not survive.

## Step 1: landing page

One screen of copy per section, in this order: hero (the complaint from
remake-entrepreneur, answered in the headline), three benefits with the
feature that backs each, one screenshot-anchored section per core flow, the
price, the FAQ (the three questions support will otherwise answer weekly),
and the footer with the legal pages. Write the copy, not the HTML; the build
turns it into the page.

## Step 2: pricing

Read the original's pricing page and decide on one of three moves, saying
which and why: cheaper for the same slice, freer where they gate a must, or
pricier with the fixes from the complaints report bundled in. At most three
tiers, one number per tier, and the free tier never hands over data the user
cannot export.

## Step 3: listing

Write `remake/listing.json` following `listing.example.json` in this folder,
then validate:

```bash
python3 listing.py remake/listing.json
python3 listing.py remake/listing.json --strict --json
```

The tool checks required fields, hard length limits (name 30, subtitle 30,
description first line 170), forbidden phrases ("better than", rival names,
"free forever" on a paid tier), and that the description's first paragraph
matches the positioning angle.

## Step 4: screenshots

Plan the shot list: one per core flow, same device frame, real data, the
states from the test plan that look best. Caption each with a plain sentence.
Store image limits come from the store; the listing notes them.

## Output

`remake/landing.md`, `remake/pricing.md`, a valid `remake/listing.json`,
then the next step: `/remake-deploy`.
