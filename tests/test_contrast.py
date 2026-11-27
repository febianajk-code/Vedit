import json
import os
import tempfile
import unittest

from _load import ROOT, load

contrast = load("remake-design", "contrast")
TOKENS = os.path.join(ROOT, "remake-design", "tokens.json")


class Contrast(unittest.TestCase):
    def test_bundled_tokens_pass(self):
        results, failures = contrast.run(TOKENS, 4.5)
        self.assertTrue(results)
        self.assertEqual(failures, [])

    def test_known_ratio(self):
        self.assertAlmostEqual(
            contrast.ratio((0, 0, 0), (255, 255, 255)), 21.0, places=1)
        self.assertAlmostEqual(contrast.ratio((255, 255, 255), (255, 255, 255)), 1.0)

    def test_failing_pair_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "tokens.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({"roles": {"text": "#aaaaaa", "surface": "#ffffff",
                                     "background": "#fefefe"}}, fh)
            _, failures = contrast.run(path, 4.5)
            self.assertEqual(len(failures), 2)

    def test_primary_text_is_only_checked_on_primary(self):
        roles = {"primary.text": "#ffffff", "primary": "#0f766e"}
        got = list(contrast.pairs(roles))
        self.assertEqual(got, [("primary.text", "primary")])

    def test_bad_hex_is_rejected(self):
        with self.assertRaises(ValueError):
            contrast.parse_hex("nothex")


if __name__ == "__main__":
    unittest.main()
