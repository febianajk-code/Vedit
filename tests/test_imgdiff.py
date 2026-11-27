import os
import struct
import tempfile
import unittest
import zlib

from _load import load

imgdiff = load("remake-diff", "imgdiff")


def write_png(path, w, h, pixels):
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for (r, g, b) in row:
            raw.extend((r, g, b))

    def chunk(ctype, body):
        return (struct.pack(">I", len(body)) + ctype + body
                + struct.pack(">I", zlib.crc32(ctype + body) & 0xFFFFFFFF))

    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)))
        fh.write(chunk(b"IDAT", zlib.compress(bytes(raw))))
        fh.write(chunk(b"IEND", b""))


def solid(w, h, rgb):
    return [[rgb] * w for _ in range(h)]


def with_box(pixels, x0, y0, x1, y1):
    out = [list(row) for row in pixels]
    for y in range(y0, y1):
        for x in range(x0, x1):
            out[y][x] = (0, 0, 0)
    return out


class Imgdiff(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.a = os.path.join(self.tmp.name, "a.png")
        self.b = os.path.join(self.tmp.name, "b.png")

    def test_identical_images_score_100(self):
        px = with_box(solid(120, 120, (255, 255, 255)), 10, 10, 60, 60)
        self.assertEqual(imgdiff.layout_score(imgdiff.scale(px, 480),
                                              imgdiff.scale(px, 480)), 100.0)

    def test_structure_shift_lowers_score(self):
        base = solid(160, 160, (255, 255, 255))
        write_png(self.a, 160, 160, with_box(base, 10, 10, 80, 80))
        write_png(self.b, 160, 160, with_box(base, 85, 10, 155, 80))
        a = imgdiff.scale(imgdiff.to_rgb(self.a, *imgdiff.read_png(self.a)), 480)
        b = imgdiff.scale(imgdiff.to_rgb(self.b, *imgdiff.read_png(self.b)), 480)
        self.assertLess(imgdiff.layout_score(a, b), 99.0)

    def test_pixel_mode_counts_exactness(self):
        write_png(self.a, 40, 40, solid(40, 40, (10, 20, 30)))
        write_png(self.b, 40, 40, solid(40, 40, (12, 22, 32)))
        a = imgdiff.to_rgb(self.a, *imgdiff.read_png(self.a))
        b = imgdiff.to_rgb(self.b, *imgdiff.read_png(self.b))
        self.assertEqual(imgdiff.pixel_score(a, b, 8), 100.0)
        self.assertEqual(imgdiff.pixel_score(a, b, 0), 0.0)

    def test_rejects_non_png(self):
        with open(self.a, "wb") as fh:
            fh.write(b"not a png")
        with self.assertRaises(imgdiff.PngError):
            imgdiff.read_png(self.a)

    def test_diff_png_round_trip(self):
        px = with_box(solid(60, 60, (255, 255, 255)), 0, 0, 30, 30)
        write_png(self.a, 60, 60, px)
        write_png(self.b, 60, 60, solid(60, 60, (255, 255, 255)))
        out = os.path.join(self.tmp.name, "d.png")
        a = imgdiff.to_rgb(self.a, *imgdiff.read_png(self.a))
        b = imgdiff.to_rgb(self.b, *imgdiff.read_png(self.b))
        imgdiff.write_png(out, b, imgdiff.changed_map(a, b, 8))
        self.assertEqual(imgdiff.read_png(out)[0], 60)
        self.assertTrue(os.path.getsize(out) > 8)


if __name__ == "__main__":
    unittest.main()
