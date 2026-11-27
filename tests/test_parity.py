import os
import tempfile
import unittest

from _load import load

parity = load("remake-diff", "parity")
HEADER = "feature,area,priority,original,clone,notes\n"


def matrix(rows):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(HEADER + rows)
        return fh.name


class Parity(unittest.TestCase):
    def test_weighted_score(self):
        path = matrix("A,core,must,yes,yes,\n"
                      "B,core,should,yes,no,\n"
                      "C,extra,could,yes,partial,\n")
        result = parity.score(parity.load(path))
        self.assertAlmostEqual(result["feature_score"], (3 + 0 + 0.5) / 6 * 100, places=1)
        self.assertEqual(result["must_have_done"], 1)
        self.assertEqual(result["must_have_total"], 1)
        self.assertEqual(result["missing"][0]["feature"], "B")

    def test_skip_and_extras_are_not_scored(self):
        path = matrix("A,core,must,yes,yes,\n"
                      "B,core,must,yes,skip,licensed content\n"
                      "C,extra,could,no,yes,our idea\n")
        result = parity.score(parity.load(path))
        self.assertEqual(result["counted"], 1)
        self.assertAlmostEqual(result["feature_score"], 100.0)
        self.assertEqual(result["skipped"][0]["feature"], "B")
        self.assertEqual(result["extras"][0]["feature"], "C")

    def test_bad_rows_are_flagged_not_crashing(self):
        path = matrix("A,core,huge,yes,yes,\nB,core,must,yes,maybe,\n")
        result = parity.score(parity.load(path))
        self.assertEqual(len(result["problems"]), 2)

    def test_missing_column_is_an_error(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                         encoding="utf-8") as fh:
            fh.write("feature,priority\nA,must\n")
            path = fh.name
        with self.assertRaises(parity.MatrixError):
            parity.load(path)

    def test_visual_combines_80_20(self):
        path = matrix("A,core,must,yes,yes,\n")
        result = parity.combine(parity.score(parity.load(path)),
                                [{"file": "x.png", "score": 50.0, "mode": "layout"}])
        self.assertAlmostEqual(result["overall"], 90.0, places=1)


if __name__ == "__main__":
    unittest.main()
