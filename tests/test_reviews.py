import json
import os
import tempfile
import unittest

from _load import ROOT, load

reviews = load("remake-entrepreneur", "reviews")
THEMES = os.path.join(ROOT, "remake-entrepreneur", "themes.json")


class Reviews(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def csv(self, rows):
        path = os.path.join(self.tmp.name, "reviews.csv")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("review,rating,source\n" + rows)
        return path

    def test_buckets_by_keyword(self):
        path = self.csv("It crashed twice today,1,store\n"
                        "Too expensive for what it does,2,store\n"
                        "Fine overall,4,store\n")
        with open(THEMES, encoding="utf-8") as fh:
            themes = json.load(fh)["themes"]
        result = reviews.bucket(reviews.read_reviews(path), themes)
        top = result[0]
        self.assertEqual(top["theme"], "performance")
        self.assertEqual(top["count"], 1)
        self.assertEqual(top["avg_rating"], 1.0)

    def test_text_file_one_review_per_line(self):
        path = os.path.join(self.tmp.name, "reviews.txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("no reply from support\napp is slow on my phone\n")
        got = reviews.read_reviews(path)
        self.assertEqual(len(got), 2)
        self.assertIsNone(got[0]["rating"])

    def test_quiet_themes_rank_last(self):
        path = self.csv("app keeps crashing,1,store\n")
        with open(THEMES, encoding="utf-8") as fh:
            themes = json.load(fh)["themes"]
        result = reviews.bucket(reviews.read_reviews(path), themes)
        self.assertEqual(result[0]["theme"], "performance")
        support = next(t for t in result if t["theme"] == "support")
        self.assertEqual(support["count"], 0)
        self.assertEqual([t["theme"] for t in result][-1], "support")


if __name__ == "__main__":
    unittest.main()
