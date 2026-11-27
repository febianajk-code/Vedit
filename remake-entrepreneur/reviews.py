#!/usr/bin/env python3
"""Review bucketing for remake-entrepreneur. Standard library only.

Reads app reviews as CSV or plain text, buckets each review into themes from
themes.json by keyword match, and ranks the complaints so the remake can fix
what users hate first.

    python3 reviews.py reviews.csv --themes themes.json
    python3 reviews.py reviews.csv --markdown
    python3 reviews.py reviews.txt --top 5

CSV needs a column holding the review text (looks for review, text, body or
content; falls back to the longest column). Extra columns are ignored. A text
file is read as one review per line. Ratings, when a rating or stars column
exists, are averaged per theme.

Exit codes: 0 ok, 2 bad input.
"""

import argparse
import csv
import json
import re
import sys

TEXT_COLUMNS = ("review", "text", "body", "content", "title")
RATING_COLUMNS = ("rating", "stars", "score")


def read_reviews(path):
    reviews = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        first = fh.readline()
        fh.seek(0)
        is_csv = "," in first and first.lower().find(
            "review") != -1 or first.lower().startswith(('"', "review"))
    if is_csv:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            for raw in csv.DictReader(fh):
                row = {(k or "").strip().lower(): (v or "").strip()
                       for k, v in raw.items()}
                text = next((row[c] for c in TEXT_COLUMNS if row.get(c)), "")
                if not text:
                    text = max((v for v in row.values() if v), key=len, default="")
                rating = None
                for c in RATING_COLUMNS:
                    if row.get(c):
                        try:
                            rating = float(re.sub(r"[^0-9.]", "", row[c]))
                        except ValueError:
                            rating = None
                        if rating is not None:
                            break
                if text:
                    reviews.append({"text": text, "rating": rating})
    else:
        with open(path, encoding="utf-8-sig") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    reviews.append({"text": line, "rating": None})
    return reviews


def bucket(reviews, themes):
    out = []
    for theme in themes:
        words = [re.escape(w.lower()) for w in theme.get("keywords", [])]
        pattern = re.compile(r"(?<![a-z])(%s)" % "|".join(words)) if words else None
        hits, ratings = [], []
        for review in reviews:
            if pattern and pattern.search(review["text"].lower()):
                hits.append(review["text"])
                if review["rating"] is not None:
                    ratings.append(review["rating"])
        out.append({"theme": theme.get("name", "?"), "count": len(hits),
                    "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
                    "examples": hits[:3]})
    out.sort(key=lambda t: (-t["count"],
                            99.0 if t["avg_rating"] is None else t["avg_rating"]))
    return out


def render(buckets, total, markdown=False):
    out, h = [], "## " if markdown else ""
    out.append("%sWhat users hate (%d reviews read)" % (h, total))
    out.append("")
    for t in buckets:
        if not t["count"]:
            continue
        rating = ("  avg rating %.2f" % t["avg_rating"]) if t["avg_rating"] is not None else ""
        out.append("- %-18s %3d reviews%s" % (t["theme"], t["count"], rating))
    quiet = [t["theme"] for t in buckets if not t["count"]]
    if quiet:
        out.append("")
        out.append("quiet themes: %s" % ", ".join(quiet))
    out.append("")
    out.append("%sFix in this order" % h)
    ranked = [t for t in buckets if t["count"]]
    for i, t in enumerate(ranked, 1):
        out.append("%d. %s" % (i, t["theme"]))
        for e in t["examples"]:
            out.append("   \"%s\"" % (e[:100] + ("..." if len(e) > 100 else "")))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("reviews", help="reviews.csv or reviews.txt")
    ap.add_argument("--themes", default="themes.json")
    ap.add_argument("--top", type=int, help="themes to show in the fix order")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args(argv)
    try:
        with open(args.themes, encoding="utf-8") as fh:
            themes = json.load(fh).get("themes", [])
        reviews = read_reviews(args.reviews)
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as exc:
        print("reviews: %s" % exc, file=sys.stderr)
        return 2
    buckets = bucket(reviews, themes)
    if args.top:
        for t in buckets:
            t["examples"] = t["examples"][:args.top]
    if args.json:
        print(json.dumps({"reviews": len(reviews), "themes": buckets}, indent=2))
    else:
        print(render(buckets, len(reviews), markdown=args.markdown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
