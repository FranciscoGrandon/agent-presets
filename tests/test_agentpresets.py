# -*- coding: utf-8 -*-
"""
AgentPresets Test Suite
Verifies core engine, fragment compilation, traversal security,
cumulative backups, heading segmentation, and auto-harvesting.

Creado por Francisco Grandón Vergara
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import agentpresets as ap


class TestAgentPresets(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="agentpresets_test_"))
        self.orig_app = ap.APP_DIR
        self.orig_frag = ap.FRAGMENTS_DIR
        self.orig_pres = ap.PRESETS_DIR
        self.orig_back = ap.BACKUPS_DIR

        ap.APP_DIR = self.test_dir
        ap.FRAGMENTS_DIR = self.test_dir / "fragments"
        ap.PRESETS_DIR = self.test_dir / "presets"
        ap.BACKUPS_DIR = self.test_dir / "backups"
        ap.ensure_dirs()

    def tearDown(self):
        ap.APP_DIR = self.orig_app
        ap.FRAGMENTS_DIR = self.orig_frag
        ap.PRESETS_DIR = self.orig_pres
        ap.BACKUPS_DIR = self.orig_back
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_ensure_dirs(self):
        self.assertTrue(ap.FRAGMENTS_DIR.is_dir())
        self.assertTrue(ap.PRESETS_DIR.is_dir())

    def test_valid_preset_name(self):
        self.assertTrue(ap.valid_preset_name("python-dev"))
        self.assertTrue(ap.valid_preset_name("sec_123"))
        self.assertFalse(ap.valid_preset_name("bad/name"))
        self.assertFalse(ap.valid_preset_name("bad:name"))
        self.assertFalse(ap.valid_preset_name(".."))
        self.assertFalse(ap.valid_preset_name(""))

    def test_path_traversal_guard(self):
        ap.create_fragment("safe-rule", "# Safe Rule\nContent")
        self.assertTrue(ap.fragment_exists("safe-rule.md"))
        self.assertIsNotNone(ap.fragment_path("safe-rule.md"))
        self.assertIsNone(ap.fragment_path("../secret.md"))
        self.assertFalse(ap.fragment_exists("../secret.md"))

    def test_exclusive_creation_and_collision_suffix(self):
        n1 = ap.create_fragment("rule-alpha", "# Alpha 1")
        n2 = ap.create_fragment("rule-alpha", "# Alpha 2")
        n3 = ap.create_fragment("rule-alpha", "# Alpha 3")
        self.assertEqual(n1, "rule-alpha.md")
        self.assertEqual(n2, "rule-alpha-2.md")
        self.assertEqual(n3, "rule-alpha-3.md")

    def test_save_and_load_preset(self):
        ap.save_preset("web-preset", ["rule-1.md", "rule-2.md"], "GEMINI.md")
        data = ap.load_preset("web-preset")
        self.assertEqual(data["destino"], "GEMINI.md")
        self.assertEqual(data["fragmentos"], ["rule-1.md", "rule-2.md"])

    def test_compile_fragments(self):
        ap.create_fragment("frag-a", "# Alpha\nAlpha body")
        content_marked, missing = ap.compile_fragments(["frag-a.md", "missing.md"], markers=True)
        self.assertEqual(missing, ["missing.md"])
        self.assertIn("<!-- fragment: frag-a.md -->", content_marked)
        self.assertIn("# Alpha\nAlpha body", content_marked)

        content_unmarked, _ = ap.compile_fragments(["frag-a.md"], markers=False)
        self.assertNotIn("<!-- fragment: frag-a.md -->", content_unmarked)
        self.assertIn("# Alpha\nAlpha body", content_unmarked)

    def test_cumulative_backups(self):
        target = self.test_dir / "target.md"
        target.write_text("initial", encoding="utf-8")
        b1 = ap.archive_copy(target, "salidas")
        b2 = ap.archive_copy(target, "salidas")
        self.assertTrue(b1.exists())
        self.assertTrue(b2.exists())
        self.assertNotEqual(b1, b2)

    def test_split_by_headings_and_code_fences(self):
        doc = "# Title 1\n```python\n# not a heading\n```\n# Title 2\nBody"
        blocks = ap.split_by_headings(doc)
        self.assertEqual(len(blocks), 2)
        self.assertIn("# Title 1", blocks[0])
        self.assertIn("# Title 2", blocks[1])

    def test_harvest_workflow(self):
        target = self.test_dir / "GEMINI.md"
        target.write_text("# Auto Section 1\nBody 1\n# Auto Section 2\nBody 2\n", encoding="utf-8")
        created = ap.harvest(target)
        self.assertTrue(any("auto-section-1" in c for c in created))
        self.assertTrue(any("auto-section-2" in c for c in created))

        # Re-running harvest on same content produces no duplicates
        created_again = ap.harvest(target)
        self.assertEqual(len(created_again), 0)


if __name__ == "__main__":
    unittest.main()
