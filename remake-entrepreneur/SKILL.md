---
name: remake-entrepreneur
description: >-
  Reads what the original app's users hate in their real public reviews and
  turns it into fixes in your remake plus a positioning angle: the one
  complaint everyone repeats becomes your headline feature. Ninth step of the
  Remake pack. Use when the user says "read the reviews", "what do users
  hate", "find the angle", "how do I beat X", or after /remake-diff.
---

# remake-entrepreneur

Input: public reviews of the original (app store listings, public review
sites, the user's own exports), `remake/features.csv`. Output: a complaints
report, fixes added to `remake/features.csv`, and a positioning paragraph.

## The rules

- **Public reviews only.** App store pages, public review sites, reviews the
  user exports from their own data. No scraping loops, no private review
  dumps, no accounts that are not the user's.
- **Quote, do not invent.** Every claimed complaint traces to a real review
  the reader can open. If the sample is thin, say so.
- **The user's words, not yours.** "I lost my work twice" beats "data
  reliability concerns".

## Step 1: collect

Gather what is reachable: the store listing's review page, public review
sites, Reddit and forum threads the user points at. Save the source URL with
every quote. Twenty honest reviews beat five hundred paraphrased ones.

## Step 2: bucket

Save the reviews as CSV (columns: review, rating, source, date) and run:

```bash
python3 reviews.py reviews.csv --themes themes.json
python3 reviews.py reviews.csv --markdown > remake/complaints.md
```

Edit `themes.json` to fit the app before trusting the buckets: a design tool
complains about "layers" and "fonts", a booking app about "time zones" and
"reminders". The tool counts; you judge.

## Step 3: rank the pain

Re-read the top bucket by hand and split each theme into: broken things (fix
them), missing things (build them), and price feelings (position against
them). One theme per fix, each fix written as a plain feature row.

## Step 4: add the fixes

Append rows to `remake/features.csv` with `original: no`, priority `must` for
anything in the top two themes, `should` for the rest. These rows are your
edge; remake-diff keeps them out of the parity score so they show up as
"yours, not in the original".

## Step 5: find the angle

One paragraph: who the remake is for, the complaint it fixes in the first
sentence, and the plain claim it can defend. Test the claim against the
feature matrix: if no `must` row backs it, the angle is marketing fiction.

## Output

`remake/complaints.md`, new rows in `features.csv`, the positioning
paragraph, then the next step: `/remake-brand`.
