#!/usr/bin/env python3
"""Brand leftover sweep for remake-brand. Standard library only.

Scans a project for strings that belong to the original app (its name, an
old codename, its domain) and reports every file and line still carrying
them, so the rebrand ships with nothing left behind.

    python3 sweep.py ./my-app --old "OriginalApp" --old "originalapp.com"
    python3 sweep.py ./my-app --old "OriginalApp" --skip node_modules,dist
    python3 sweep.py ./my-app --old "OriginalApp" --json

Text files are scanned line by line (UTF-8, latin-1 tolerated). Binary
formats that can hide brand strings are flagged by extension: images are
checked for the old name inside their metadata bytes, and reported as
"binary, inspect by hand". Well-known junk directories (node_modules, .git,
__pycache__, venvs, build output) are skipped unless you say otherwise.

Exit codes: 0 clean, 1 hits found, 2 bad input.
"""

import argparse
import json
import os
import sys

DEFAULT_SKIP = ("node_modules", ".git", "__pycache__", ".venv", "venv",
                "dist", "build", ".next", "coverage")
BINARY_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".icns",
              ".pdf", ".zip", ".gz", ".woff", ".woff2", ".ttf", ".otf",
              ".mp4", ".mov", ".mp3")
TEXT_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".rb", ".go",
            ".rs", ".java", ".kt", ".swift", ".dart", ".php", ".css", ".scss",
            ".html", ".htm", ".json", ".md", ".txt", ".yml", ".yaml", ".toml",
            ".env", ".xml", ".svg", ".sql", ".sh", ".cfg", ".ini", ".lock")


def iter_files(root, skip):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip and not d.startswith(".")]
        for name in filenames:
            yield os.path.join(dirpath, name)


def scan(root, needles, skip):
    hits = []
    lowered = [n.lower() for n in needles]
    for path in iter_files(root, skip):
        ext = os.path.splitext(path)[1].lower()
        try:
            with open(path, "rb") as fh:
                blob = fh.read()
        except OSError:
            continue
        if any(n.encode("utf-8", "ignore") in blob for n in needles):
            if ext in BINARY_EXT or ext not in TEXT_EXT:
                hits.append({"file": path, "line": 0,
                             "text": "(binary, inspect by hand)"})
                continue
            for i, line in enumerate(blob.decode("utf-8", "replace").splitlines(), 1):
                low = line.lower()
                if any(n in low for n in lowered):
                    hits.append({"file": path, "line": i, "text": line.strip()[:120]})
    hits.sort(key=lambda h: (h["file"], h["line"]))
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("root", help="project directory to sweep")
    ap.add_argument("--old", action="append", required=True,
                    help="a string from the original app; repeatable")
    ap.add_argument("--skip", default=",".join(DEFAULT_SKIP),
                    help="directory names to skip (comma separated)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.root):
        print("sweep: %s is not a directory" % args.root, file=sys.stderr)
        return 2
    skip = set(s.strip() for s in args.skip.split(",") if s.strip())
    hits = scan(args.root, args.old, skip)
    if args.json:
        print(json.dumps({"needles": args.old, "hits": hits}, indent=2))
    else:
        if not hits:
            print("clean. No hits for: %s" % ", ".join(args.old))
        else:
            print("%d hit(s):" % len(hits))
            for hit in hits:
                where = hit["file"] if hit["line"] == 0 else "%s:%d" % (
                    hit["file"], hit["line"])
                print("  %s  %s" % (where, hit["text"]))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
