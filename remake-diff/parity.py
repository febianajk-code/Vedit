#!/usr/bin/env python3
"""Feature parity score for remake-diff. Standard library only.

Reads the feature matrix that remake-recon wrote and the build has been
ticking off, and reports how much of the original your remake does, what is
missing, and in what order to build it.

    python3 parity.py remake/features.csv
    python3 parity.py remake/features.csv --visual remake/diffs/*.json
    python3 parity.py remake/features.csv --markdown > remake/parity.md
    python3 parity.py remake/features.csv --fail-under 80

CSV columns (extra columns are ignored):

    feature    what it does, in plain words
    area       the screen or flow it belongs to
    priority   must | should | could   (P0 | P1 | P2 also work)
    original   yes | no     does the original app have it
    clone      yes | partial | no | skip
    notes      anything; for skip, say why

Weights: must 3, should 2, could 1. yes 1, partial 0.5, no 0. skip and rows
where original is "no" (your own ideas) stay out of the score, so the number
only measures parity. With --visual, imgdiff.py --json layout scores are
averaged and folded in: overall = 80% features + 20% layout.
"""

import argparse
import csv
import json
import sys

WEIGHT = {"must": 3, "should": 2, "could": 1, "p0": 3, "p1": 2, "p2": 1}
CREDIT = {"yes": 1.0, "done": 1.0, "partial": 0.5, "no": 0.0, "": 0.0, "todo": 0.0}
PRIORITY_NAME = {3: "must", 2: "should", 1: "could"}


class MatrixError(Exception):
    pass


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise MatrixError("%s is empty" % path)
        fields = [f.strip().lower() for f in reader.fieldnames]
        for need in ("feature", "priority", "clone"):
            if need not in fields:
                raise MatrixError("%s has no '%s' column. Columns needed: "
                                  "feature, area, priority, original, clone, notes"
                                  % (path, need))
        rows = []
        for i, raw in enumerate(reader, start=2):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
            if not row.get("feature"):
                continue
            row["line"] = i
            rows.append(row)
    return rows


def score(rows):
    counted, skipped, extras, problems = [], [], [], []
    for row in rows:
        original = row.get("original", "yes").lower() or "yes"
        clone = row.get("clone", "").lower()
        prio = row.get("priority", "").lower()
        if original in ("no", "n", "false"):
            extras.append(row)
            continue
        if clone == "skip":
            skipped.append(row)
            continue
        if prio not in WEIGHT:
            problems.append("line %d: priority '%s' is not must/should/could, "
                            "counted as could" % (row["line"], row.get("priority", "")))
        if clone not in CREDIT:
            problems.append("line %d: clone '%s' is not yes/partial/no/skip, "
                            "counted as no" % (row["line"], row.get("clone", "")))
        counted.append(dict(row, weight=WEIGHT.get(prio, 1),
                            credit=CREDIT.get(clone, 0.0)))

    total = sum(r["weight"] for r in counted)
    got = sum(r["weight"] * r["credit"] for r in counted)
    feature_score = 100.0 * got / total if total else 0.0

    areas = {}
    for r in counted:
        key = r.get("area") or "(no area)"
        got_a, tot_a, n = areas.setdefault(key, [0.0, 0.0, 0])
        areas[key] = [got_a + r["weight"] * r["credit"], tot_a + r["weight"], n + 1]
    by_area = sorted(({"area": a, "score": round(100.0 * g / t, 1) if t else 0.0,
                       "features": n} for a, (g, t, n) in areas.items()),
                     key=lambda d: d["score"])

    missing = sorted((r for r in counted if r["credit"] < 1.0),
                     key=lambda r: (-r["weight"], r["credit"],
                                    r.get("area", ""), r["feature"]))

    def brief(r):
        return {"feature": r["feature"], "area": r.get("area", ""),
                "priority": PRIORITY_NAME.get(r.get("weight", 1), "could"),
                "clone": r.get("clone", "") or "no", "notes": r.get("notes", "")}

    musts = [r for r in counted if r["weight"] == 3]
    return {
        "feature_score": round(feature_score, 1),
        "counted": len(counted),
        "must_have_done": sum(1 for r in musts if r["credit"] == 1.0),
        "must_have_total": len(musts),
        "by_area": by_area,
        "missing": [brief(r) for r in missing],
        "skipped": [brief(r) for r in skipped],
        "extras": [brief(r) for r in extras],
        "problems": problems,
    }


def visual_scores(paths):
    scores = []
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if "score" not in data:
            raise MatrixError("%s is not imgdiff.py --json output" % path)
        scores.append({"file": data.get("files", {}).get("remake", path),
                       "score": float(data["score"]),
                       "mode": data.get("mode", "layout")})
    return scores


def combine(result, visuals):
    if visuals:
        layout = sum(v["score"] for v in visuals) / len(visuals)
        result["visual"] = visuals
        result["layout_score"] = round(layout, 1)
        result["overall"] = round(0.8 * result["feature_score"] + 0.2 * layout, 1)
    else:
        result["overall"] = result["feature_score"]
    return result


def render(result, markdown=False):
    out, h = [], "## " if markdown else ""
    out.append("%sParity: %.1f / 100" % (h, result["overall"]))
    out.append("")
    out.append("features %.1f  (%d counted, must-haves %d of %d done)" % (
        result["feature_score"], result["counted"],
        result["must_have_done"], result["must_have_total"]))
    if "layout_score" in result:
        out.append("layout   %.1f  (%d screens compared)" % (
            result["layout_score"], len(result["visual"])))
    if result["must_have_done"] < result["must_have_total"]:
        out.append("")
        out.append("Not shippable yet: %d must-have feature(s) are not done."
                   % (result["must_have_total"] - result["must_have_done"]))
    out.append("")
    out.append("%sBy area, weakest first" % h)
    for a in result["by_area"]:
        out.append("- %-28s %5.1f  (%d features)" % (a["area"], a["score"], a["features"]))
    out.append("")
    out.append("%sMissing, in build order" % h)
    if not result["missing"]:
        out.append("- nothing. Every counted feature is done.")
    for m in result["missing"]:
        note = ("  (%s)" % m["notes"]) if m["notes"] else ""
        out.append("- [%s] %s: %s, %s%s" % (m["priority"], m["area"] or "-",
                                            m["feature"], m["clone"], note))
    for key, title in (("skipped", "Left out on purpose (not scored)"),
                       ("extras", "Yours, not in the original (not scored)")):
        if result[key]:
            out.append("")
            out.append("%s%s" % (h, title))
            for m in result[key]:
                out.append("- %s%s" % (m["feature"],
                                       (": %s" % m["notes"]) if m["notes"] else ""))
    if result.get("visual"):
        out.append("")
        out.append("%sScreens" % h)
        for v in sorted(result["visual"], key=lambda d: d["score"]):
            out.append("- %-40s %5.1f" % (v["file"], v["score"]))
    if result["problems"]:
        out.append("")
        out.append("%sFix in the matrix" % h)
        for p in result["problems"]:
            out.append("- %s" % p)
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("matrix", help="the feature matrix CSV")
    ap.add_argument("--visual", nargs="*", default=[],
                    help="imgdiff.py --json outputs to fold in")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--fail-under", type=float)
    args = ap.parse_args(argv)
    try:
        result = combine(score(load(args.matrix)), visual_scores(args.visual))
    except (MatrixError, OSError, ValueError, json.JSONDecodeError) as exc:
        print("parity: %s" % exc, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render(result, markdown=args.markdown))
    if args.fail_under is not None and result["overall"] < args.fail_under:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
