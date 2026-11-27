import os
import tempfile
import unittest

from _load import load

sweep = load("remake-brand", "sweep")


class Sweep(unittest.TestCase):
    def test_finds_leftover_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "app.py"), "w", encoding="utf-8") as fh:
                fh.write("TITLE = 'OriginalApp rocks'\nCLEAN = 'fine'\n")
            hits = sweep.scan(tmp, ["OriginalApp"], {"node_modules", ".git"})
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["line"], 1)

    def test_skips_junk_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            junk = os.path.join(tmp, "node_modules")
            os.mkdir(junk)
            with open(os.path.join(junk, "x.js"), "w", encoding="utf-8") as fh:
                fh.write("OriginalApp\n")
            self.assertEqual(sweep.scan(tmp, ["OriginalApp"],
                                        set(sweep.DEFAULT_SKIP)), [])

    def test_case_insensitive(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "a.md"), "w", encoding="utf-8") as fh:
                fh.write("made with originalapp.com\n")
            hits = sweep.scan(tmp, ["originalapp.com"], set())
            self.assertEqual(len(hits), 1)


if __name__ == "__main__":
    unittest.main()
