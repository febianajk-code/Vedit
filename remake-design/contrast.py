#!/usr/bin/env python3
"""Contrast checker for remake-design. Standard library only.

Reads tokens.json, computes the WCAG 2 contrast ratio for every text colour
against every surface it plausibly sits on, and fails with a list of the
pairs that fall below the threshold.

    python3 contrast.py remake/tokens.json
    python3 contrast.py remake/tokens.json --min 4.5
    python3 contrast.py remake/tokens.json --json

Roles named "text" and "text.muted" are checked against "surface" and
"background"; "primary.text" is checked against "primary", where it lives.
Anything else is treated as decoration and skipped, so borders and focus
rings do not create noise.

Exit codes: 0 all pairs pass, 1 at least one pair fails, 2 bad input.
"""

import argparse
import json
import re
import sys

DEFAULT_MIN = 4.5
TEXT_ROLES = ("text", "text.muted", "primary.text")
BACKDROP_ROLES = ("surface", "background", "primary")


def parse_hex(value):
    raw = value.strip().lstrip("#")
    if re.fullmatch(r"[0-9a-fA-F]{3}", raw):
        raw = "".join(ch * 2 for ch in raw)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", raw):
        raise ValueError("not a hex colour: %r" % value)
    return tuple(int(raw[i:i + 2], 16) for i in (0, 2, 4))


def channel(value):
    scaled = value / 255.0
    return scaled / 12.92 if scaled <= 0.04045 else ((scaled + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (channel(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    lo, hi = sorted((luminance(fg), luminance(bg)))
    return (hi + 0.05) / (lo + 0.05)


def pairs(roles):
    for text in ("text", "text.muted"):
        if text not in roles:
            continue
        for backdrop in ("surface", "background"):
            if backdrop in roles:
                yield text, backdrop
    if "primary.text" in roles and "primary" in roles:
        yield "primary.text", "primary"


def run(path, minimum):
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    roles = doc.get("roles")
    if not isinstance(roles, dict) or not roles:
        raise ValueError("%s has no non-empty 'roles' object" % path)
    results, failures = [], []
    for text, backdrop in pairs(roles):
        try:
            score = ratio(parse_hex(roles[text]), parse_hex(roles[backdrop]))
        except ValueError as exc:
            raise ValueError("%s: %s" % (path, exc))
        entry = {"text": text, "backdrop": backdrop,
                 "ratio": round(score, 2), "passes": score >= minimum}
        results.append(entry)
        if not entry["passes"]:
            failures.append(entry)
    return results, failures


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("tokens", help="path to tokens.json")
    ap.add_argument("--min", type=float, default=DEFAULT_MIN,
                    help="minimum WCAG ratio (default 4.5)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        results, failures = run(args.tokens, args.min)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("contrast: %s" % exc, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"pairs": results, "failures": failures,
                          "min": args.min}, indent=2))
    else:
        for entry in results:
            mark = "ok  " if entry["passes"] else "FAIL"
            print("%s %-14s on %-12s %.2f" % (
                mark, entry["text"], entry["backdrop"], entry["ratio"]))
        if failures:
            print("\n%d pair(s) below %.1f. Fix the tokens, not the tool."
                  % (len(failures), args.min))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
