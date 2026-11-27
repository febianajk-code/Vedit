import json
import os
import tempfile
import unittest

from _load import ROOT, load

listing = load("remake-launch", "listing")
EXAMPLE = os.path.join(ROOT, "remake-launch", "listing.example.json")


class Listing(unittest.TestCase):
    def test_bundled_example_is_valid(self):
        with open(EXAMPLE, encoding="utf-8") as fh:
            self.assertEqual(listing.check(json.load(fh), True), [])

    def test_missing_fields(self):
        self.assertIn("missing field: name", listing.check({"description": "x"}, False))

    def test_length_limits(self):
        with open(EXAMPLE, encoding="utf-8") as fh:
            data = json.load(fh)
        data["name"] = "x" * 31
        data["subtitle"] = "y" * 31
        problems = listing.check(data, False)
        self.assertEqual(len(problems), 2)

    def test_forbidden_phrases(self):
        with open(EXAMPLE, encoding="utf-8") as fh:
            data = json.load(fh)
        data["description"] = "Better than EverythingApp, free forever!"
        problems = listing.check(data, False)
        self.assertEqual(sum(1 for p in problems if p.startswith("forbidden")), 2)

    def test_screenshots_need_captions(self):
        with open(EXAMPLE, encoding="utf-8") as fh:
            data = json.load(fh)
        data["screenshots"] = [{"file": "a.png"}]
        problems = listing.check(data, False)
        self.assertTrue(any("caption" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
