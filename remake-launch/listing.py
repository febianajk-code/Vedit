#!/usr/bin/env python3
"""Store listing validator for remake-launch. Standard library only.

Checks a listing.json against the field rules most stores enforce, before
the store does it for you at submission time.

    python3 listing.py remake/listing.json
    python3 listing.py remake/listing.json --strict
    python3 listing.py remake/listing.json --json

Checks: required fields present, name and subtitle length (30), description
non-empty with the first 170 characters able to stand alone, at least one
screenshot with a caption, support and privacy URLs present and https, and
forbidden phrases (rival comparisons, "free forever" on a paid tier) absent
from every text field. --strict also fails on missing keywords or a pricing
block without tiers.

Exit codes: 0 valid, 1 problems found, 2 bad input.
"""

import argparse
import json
import re
import sys

NAME_LIMIT = 30
SUBTITLE_LIMIT = 30
DESCRIPTION_FIRST = 170
REQUIRED = ("name", "subtitle", "description", "screenshots",
            "support_url", "privacy_policy_url")
FORBIDDEN = (r"\bbetter than\b", r"\bcheaper than\b", r"\bvs\.?\b",
             r"free forever")


class ListingError(Exception):
    pass


def check(data, strict):
    problems = []
    if not isinstance(data, dict):
        raise ListingError("listing must be a JSON object")
    for field in REQUIRED:
        if not str(data.get(field) or "").strip() and field != "screenshots":
            problems.append("missing field: %s" % field)
    name = data.get("name", "")
    if len(name) > NAME_LIMIT:
        problems.append("name is %d characters, limit %d" % (len(name), NAME_LIMIT))
    subtitle = data.get("subtitle", "")
    if len(subtitle) > SUBTITLE_LIMIT:
        problems.append("subtitle is %d characters, limit %d"
                        % (len(subtitle), SUBTITLE_LIMIT))
    description = data.get("description", "")
    if description:
        first = description.strip().splitlines()[0]
        if len(first) > DESCRIPTION_FIRST:
            problems.append("description first line is %d characters, keep it "
                            "under %d" % (len(first), DESCRIPTION_FIRST))
    shots = data.get("screenshots", [])
    if not isinstance(shots, list) or not shots:
        problems.append("at least one screenshot is required")
    else:
        for i, shot in enumerate(shots, 1):
            if not isinstance(shot, dict) or not shot.get("file"):
                problems.append("screenshot %d has no file" % i)
            elif not shot.get("caption"):
                problems.append("screenshot %d has no caption" % i)
    for field in ("support_url", "privacy_policy_url"):
        url = data.get(field, "")
        if url and not url.startswith("https://"):
            problems.append("%s must be https" % field)
    for pattern in FORBIDDEN:
        rx = re.compile(pattern, re.I)
        for field in ("name", "subtitle", "description"):
            value = str(data.get(field) or "")
            if rx.search(value):
                problems.append("forbidden phrase %r in %s" % (pattern, field))
        for i, shot in enumerate(shots if isinstance(shots, list) else [], 1):
            caption = str((shot or {}).get("caption") or "")
            if rx.search(caption):
                problems.append("forbidden phrase %r in screenshot %d caption"
                                % (pattern, i))
    pricing = data.get("pricing") or {}
    if isinstance(pricing, dict) and pricing.get("model") == "freemium":
        tiers = pricing.get("tiers") or []
        if any(str(t.get("price")) in ("0", "0.0") and not t.get("includes")
               for t in tiers if isinstance(t, dict)):
            problems.append("a free tier must list what it includes")
    if strict:
        if not data.get("keywords"):
            problems.append("strict: keywords are required")
        if not pricing.get("tiers"):
            problems.append("strict: pricing needs at least one tier")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("listing", help="path to listing.json")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        with open(args.listing, encoding="utf-8") as fh:
            data = json.load(fh)
        problems = check(data, args.strict)
    except (OSError, ValueError, ListingError, json.JSONDecodeError) as exc:
        print("listing: %s" % exc, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"valid": not problems, "problems": problems}, indent=2))
    elif problems:
        print("%d problem(s):" % len(problems))
        for p in problems:
            print("  - %s" % p)
    else:
        print("valid. Ready to submit.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
