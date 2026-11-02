#!/usr/bin/env python3
"""12 safety checks for direct ChatGPT Library destination preflight."""
import importlib.util
from pathlib import Path
import unittest

module_path = Path(__file__).resolve().parent.parent / "Tools" / "resolve_direct_library_destination.py"
spec = importlib.util.spec_from_file_location("direct_router", module_path)
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)

REGISTRY = {"project_folders": [
    {"name": "Menschen-A1", "library_path": "/Flasch kart/German-Content-Production-Kit/Content/Menschen-A1"},
    {"name": "Menschen-A1-Verben", "library_path": "/Flasch kart/German-Content-Production-Kit/Content/Menschen-A1-Verben"},
    {"name": "Menschen-A2", "library_path": "/Flasch kart/German-Content-Production-Kit/Content/Menschen-A2"},
    {"name": "Menschen-A2-Verben", "library_path": "/Flasch kart/German-Content-Production-Kit/Content/Menschen-A2-Verben"},
    {"name": "00-Unclassified", "library_path": "/Flasch kart/German-Content-Production-Kit/Content/00-Unclassified"},
]}


class DirectSaveRouterTests(unittest.TestCase):
    def test_a1_report(self):
        x = router.resolve_destination("content:Menschen-A1", "report", "V24.json", REGISTRY)
        self.assertEqual(x["destination_path"],
            "/Flasch kart/German-Content-Production-Kit/Content/Menschen-A1/Reports/V24.json")
        self.assertEqual(x["status"], "ROUTED_NOT_SAVED")

    def test_a1_verben_separate(self):
        x = router.resolve_destination("content:Menschen-A1-Verben", "checkpoint", "WIP.tsv", REGISTRY)
        self.assertIn("/Menschen-A1-Verben/Checkpoints/", x["destination_path"])
        self.assertNotIn("/Menschen-A1/Checkpoints/", x["destination_path"])

    def test_a2_verben_separate(self):
        x = router.resolve_destination("content:Menschen-A2-Verben", "release", "bundle.zip", REGISTRY)
        self.assertIn("/Menschen-A2-Verben/Releases/", x["destination_path"])

    def test_op02_report_folder(self):
        x = router.resolve_destination("optimization:OP02", "report", "analysis.md", None)
        self.assertEqual(x["destination_path"],
            "/Flasch kart/German-Content-Production-Kit/Optimization-Program/OP02/Reports/analysis.md")

    def test_op01(self):
        x = router.resolve_destination("optimization:OP01", "report", "policy.md", None)
        self.assertIn("/Optimization-Program/OP01/Reports/", x["destination_path"])

    def test_runtime_not_content(self):
        x = router.resolve_destination("app:runtime", "release", "v505.zip", None)
        self.assertIn("/German-Flashcards-Pro/Releases/v505.zip", x["destination_path"])

    def test_no_unknown_owner_root_fallback(self):
        with self.assertRaises(ValueError):
            router.resolve_destination("some-other-project", "report", "x.md", REGISTRY)

    def test_no_unclassified_ambiguity_fallback(self):
        with self.assertRaises(ValueError):
            router.resolve_destination("content:00-Unclassified", "report", "x.md", REGISTRY)

    def test_no_unsafe_filename(self):
        for filename in ["../x.md", "/x.md", "x/y.md", "x\\y.md", ".env", "", " x.md"]:
            with self.subTest(filename=filename):
                with self.assertRaises(ValueError):
                    router.resolve_destination("content:Menschen-A1", "report", filename, REGISTRY)

    def test_no_invalid_role(self):
        with self.assertRaises(ValueError):
            router.resolve_destination("content:Menschen-A1", "unknown", "x.md", REGISTRY)

    def test_registry_must_be_present(self):
        with self.assertRaises(ValueError):
            router.resolve_destination("content:Menschen-A1", "report", "x.md", None)

    def test_bad_registry_path_and_duplicate(self):
        bad = {"project_folders": [{"name":"Menschen-A1","library_path":"/Flasch kart"}]}
        with self.assertRaises(ValueError):
            router.resolve_destination("content:Menschen-A1", "report", "x.md", bad)
        dup = {"project_folders": REGISTRY["project_folders"] * 2}
        with self.assertRaises(ValueError):
            router.resolve_destination("content:Menschen-A1", "report", "x.md", dup)


if __name__ == "__main__":
    unittest.main()
