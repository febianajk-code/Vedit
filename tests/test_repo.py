import json
import os
import re
import unittest

from _load import ROOT

SKILLS = ["remake-recon", "remake-architect", "remake-design", "remake-build",
          "remake-backend", "remake-test", "remake-diff", "remake-entrepreneur",
          "remake-brand", "remake-launch", "remake-deploy"]
ABOUT = ("Eleven free Claude skills that remake any app: reverse-engineer it, "
         "rebuild it, test it for bugs, then fix what its users hate. Free, MIT.")


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


class Repo(unittest.TestCase):
    def test_eleven_skill_folders_at_the_root(self):
        found = sorted(d for d in os.listdir(ROOT)
                       if os.path.isfile(os.path.join(ROOT, d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS))

    def test_frontmatter_name_and_description(self):
        for s in SKILLS:
            fm, text = frontmatter(os.path.join(ROOT, s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            self.assertRegex(fm, r"description: ", s)
            self.assertGreater(len(fm), 200, "%s description is too thin" % s)
            self.assertGreater(len(text.splitlines()), 60, s)

    def test_plugin_manifest_points_at_the_root_skills(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json")) as fh:
            plugin = json.load(fh)
        self.assertEqual(plugin["name"], "remake-skill")
        self.assertEqual(plugin["skills"], "./")
        self.assertEqual(plugin["description"], ABOUT)
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as fh:
            market = json.load(fh)
        self.assertEqual(market["name"], "remake-skill")
        self.assertEqual(market["plugins"][0]["name"], "remake-skill")

    def test_readme_introduces_the_pack(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = " ".join(fh.read().split())
        self.assertTrue(readme.startswith("# The Remake skill"))
        for line in ("/plugin marketplace add febianajk-code/Vedit",
                     "## Fine print", "## The eleven"):
            self.assertIn(line, readme)

    def test_every_tool_has_a_shebang_and_a_docstring(self):
        for folder, name in (("remake-design", "contrast"), ("remake-diff", "parity"),
                             ("remake-diff", "imgdiff"),
                             ("remake-entrepreneur", "reviews"),
                             ("remake-brand", "sweep"), ("remake-launch", "listing")):
            with open(os.path.join(ROOT, folder, name + ".py"), encoding="utf-8") as fh:
                text = fh.read()
            self.assertTrue(text.startswith("#!"), folder + "/" + name)
            self.assertIn('"""', text, folder + "/" + name)

    def test_templates_exist(self):
        for path in ("remake-recon/recon-map.md", "remake-recon/features.csv",
                     "remake-architect/architecture.md", "remake-design/tokens.json",
                     "remake-test/test-plan.md", "remake-test/bug-report.md",
                     "remake-test/e2e.example.spec.ts", "remake-launch/listing.example.json",
                     "remake-deploy/preflight.md", "remake-entrepreneur/themes.json"):
            self.assertTrue(os.path.isfile(os.path.join(ROOT, path)), path)

    def test_license_is_mit_with_credit(self):
        with open(os.path.join(ROOT, "LICENSE"), encoding="utf-8") as fh:
            license_text = fh.read()
        self.assertIn("MIT License", license_text)
        self.assertIn("Jake Schincariol", license_text)


if __name__ == "__main__":
    unittest.main()
