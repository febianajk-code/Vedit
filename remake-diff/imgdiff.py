#!/usr/bin/env python3
"""Screenshot diff for remake-diff. Standard library only.

Compares a screenshot of the original app with the same screen in your
remake and reports how close the layout is and where it differs.

    python3 imgdiff.py original.png remake.png
    python3 imgdiff.py original.png remake.png --out diff.png --json
    python3 imgdiff.py original.png remake.png --mode pixel --fail-under 95

Two modes:

  layout (default)  Compares structure, not colour. Both images become edge
                    maps, cut into a grid, and each cell's edge density is
                    compared. A rebrand changes every colour on purpose, so
                    colour is ignored here. Only cells with content in either
                    image are scored, so empty margins do not pad the number.
  pixel             Exact pixel comparison with a tolerance. For your own
                    regressions (remake today vs remake yesterday), not for
                    chasing the original's pixels.

Both images are scaled to the same width (--width, default 480) and compared
over the shared height. A height difference is reported, not hidden.

Reads 8 and 16 bit PNGs (grey, RGB, palette, with or without alpha),
non-interlaced. Interlaced PNGs are refused with a message.
"""

import argparse
import json
import struct
import sys
import zlib

GRID = 24
EDGE_THRESHOLD = 24


class PngError(Exception):
    pass


def read_png(path):
    """Decode a PNG into (width, height, pixels) with pixels as rows of
    (r, g, b) tuples, 8 bits per channel."""
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise PngError("%s is not a PNG" % path)
    pos, width, height, depth, color, interlace, palette = 8, 0, 0, 8, 0, 0, b""
    idat = bytearray()
    while pos < len(data):
        if pos + 8 > len(data):
            raise PngError("%s: truncated chunk header" % path)
        (length,), ctype = struct.unpack(">I", data[pos:pos + 4]), data[pos + 4:pos + 8]
        body, crc = data[pos + 8:pos + 8 + length], data[pos + 8 + length:pos + 12 + length]
        if ctype == b"IHDR":
            width, height, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif ctype == b"PLTE":
            palette = body
        elif ctype == b"IDAT":
            idat.extend(body)
        elif ctype == b"IEND":
            break
        pos += 12 + length
    if not width or not height:
        raise PngError("%s: no IHDR" % path)
    if interlace:
        raise PngError("%s is interlaced: re-save the screenshot without "
                       "interlacing" % path)
    if depth not in (8, 16):
        raise PngError("%s: unsupported bit depth %d" % (path, depth))
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color)
    if channels is None:
        raise PngError("%s: unsupported colour type %d" % (path, color))
    return width, height, depth, color, channels, bytes(palette), bytes(idat)


def unfilter(raw, width, height, channels, depth):
    """Undo PNG scanline filters. Only byte-aligned depths (8, 16) here."""
    bpp = channels * (depth // 8)
    stride = width * bpp
    if len(raw) != (stride + 1) * height:
        raise PngError("truncated image data")
    out, prev = bytearray(stride * height), bytearray(stride)
    for y in range(height):
        base = y * (stride + 1)
        kind, line = raw[base], bytearray(raw[base + 1:base + 1 + stride])
        if kind == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif kind == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif kind == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif kind == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 0xFF
        elif kind != 0:
            raise PngError("unknown filter type %d" % kind)
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return out, stride


def to_rgb(path, width, height, depth, color, channels, palette, idat):
    raw, _ = unfilter(zlib.decompress(idat), width, height, channels, depth)
    step = depth // 8
    rows = []
    for y in range(height):
        row, base = [], y * width * channels * step
        for x in range(width):
            o = base + x * channels * step
            if color == 0:
                v = raw[o] if depth == 8 else raw[o]
                row.append((v, v, v))
            elif color == 2:
                row.append((raw[o], raw[o + step], raw[o + 2 * step])
                           if depth == 16 else (raw[o], raw[o + 1], raw[o + 2]))
            elif color == 3:
                idx = raw[o] * 3
                if idx + 2 >= len(palette):
                    raise PngError("%s: pixel outside palette" % path)
                row.append((palette[idx], palette[idx + 1], palette[idx + 2]))
            elif color == 4:
                v = raw[o]
                row.append((v, v, v))
            else:
                row.append((raw[o], raw[o + step], raw[o + 2 * step])
                           if depth == 16 else (raw[o], raw[o + 1], raw[o + 2]))
        rows.append(row)
    return rows


def scale(rows, target_w):
    """Nearest-neighbour scale to target_w, preserving aspect."""
    h, w = len(rows), len(rows[0])
    if w == target_w:
        return rows
    out_h = max(1, round(h * target_w / w))
    out = []
    for y in range(out_h):
        src = rows[min(h - 1, y * h // out_h)]
        out.append([src[min(w - 1, x * w // target_w)] for x in range(target_w)])
    return out


def edges(rows):
    """Binary edge map from luminance gradients."""
    lum = [[(r * 299 + g * 587 + b * 114) // 1000 for (r, g, b) in row]
           for row in rows]
    h, w = len(lum), len(lum[0])
    out = [[0] * w for _ in range(h)]
    for y in range(h - 1):
        for x in range(w - 1):
            if (abs(lum[y][x] - lum[y][x + 1]) + abs(lum[y][x] - lum[y + 1][x])
                    >= EDGE_THRESHOLD):
                out[y][x] = 1
    return out


def densities(edge, gw=GRID, gh=GRID):
    h, w = len(edge), len(edge[0])
    cells = []
    for gy in range(gh):
        row = []
        for gx in range(gw):
            y0, y1 = h * gy // gh, max(h * (gy + 1) // gh, h * gy // gh + 1)
            x0, x1 = w * gx // gw, max(w * (gx + 1) // gw, w * gx // gw + 1)
            n = (y1 - y0) * (x1 - x0)
            row.append(sum(edge[y][x] for y in range(y0, y1)
                           for x in range(x0, x1)) / n)
        cells.append(row)
    return cells


def layout_score(a, b):
    ea, eb = edges(a), edges(b)
    da, db = densities(ea), densities(eb)
    gh, gw = len(da), len(da[0])
    diffs = []
    for gy in range(gh):
        for gx in range(gw):
            if da[gy][gx] > 0.01 or db[gy][gx] > 0.01:
                diffs.append(abs(da[gy][gx] - db[gy][gx]))
    base = 100.0 * (1.0 - sum(diffs) / len(diffs)) if diffs else 0.0
    return base


def pixel_score(a, b, tolerance):
    h, w = min(len(a), len(b)), min(len(a[0]), len(b[0]))
    total, same = h * w, 0
    for y in range(h):
        for x in range(w):
            if all(abs(p - q) <= tolerance for p, q in zip(a[y][x], b[y][x])):
                same += 1
    return 100.0 * same / total if total else 0.0


def write_png(path, rows, changed):
    """Write a diff image: the remake dimmed, differing pixels marked red."""
    h, w = len(rows), len(rows[0])
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            if changed[y][x]:
                raw.extend((255, 0, 0))
            else:
                r, g, b = rows[y][x]
                raw.extend((r // 3, g // 3, b // 3))
    def chunk(ctype, body):
        return (struct.pack(">I", len(body)) + ctype + body
                + struct.pack(">I", zlib.crc32(ctype + body) & 0xFFFFFFFF))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(chunk(b"IHDR", ihdr))
        fh.write(chunk(b"IDAT", zlib.compress(bytes(raw), 6)))
        fh.write(chunk(b"IEND", b""))


def changed_map(a, b, tolerance):
    h, w = min(len(a), len(b)), min(len(a[0]), len(b[0]))
    return [[any(abs(p - q) > tolerance for p, q in zip(a[y][x], b[y][x]))
             for x in range(w)] for y in range(h)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("original")
    ap.add_argument("remake")
    ap.add_argument("--mode", choices=("layout", "pixel"), default="layout")
    ap.add_argument("--width", type=int, default=480)
    ap.add_argument("--tolerance", type=int, default=8)
    ap.add_argument("--out", help="write a diff image here")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-under", type=float)
    args = ap.parse_args(argv)
    try:
        a = to_rgb(args.original, *read_png(args.original))
        b = to_rgb(args.remake, *read_png(args.remake))
    except (PngError, OSError, zlib.error, ValueError) as exc:
        print("imgdiff: %s" % exc, file=sys.stderr)
        return 2
    a, b = scale(a, args.width), scale(b, args.width)
    h_diff = abs(len(a) - len(b))
    h, w = min(len(a), len(b)), min(len(a[0]), len(b[0]))
    a, b = a[:h], b[:h]
    if args.mode == "pixel":
        score, extra = pixel_score(a, b, args.tolerance), {"tolerance": args.tolerance}
    else:
        score, extra = layout_score(a, b), {"grid": GRID}
    if args.out:
        write_png(args.out, b, changed_map(a, b, args.tolerance))
        extra["diff"] = args.out
    result = dict({"score": round(score, 1), "mode": args.mode,
                   "files": {"original": args.original, "remake": args.remake},
                   "compared": "%dx%d" % (w, h),
                   "height_difference_px": h_diff}, **extra)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("%s  %.1f / 100  (%s, %s, height diff %dpx)"
              % (args.mode, score, args.original, args.remake, h_diff))
        if args.out:
            print("diff image: %s" % args.out)
    if args.fail_under is not None and score < args.fail_under:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
