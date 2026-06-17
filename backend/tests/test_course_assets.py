from pathlib import Path
import unittest


class CourseAssetsTest(unittest.TestCase):
    def test_course_docs_and_examples_exist(self):
        root = Path(__file__).resolve().parents[2]
        required = [
            "examples/mcp_article.txt",
            "examples/ai_product_article.txt",
            "examples/paper_abstract.txt",
            "docs/evaluation.md",
            "docs/model-products-survey.md",
            "docs/design-decisions.md",
            "scripts/run_tests.ps1",
            "scripts/start_backend.ps1",
            "scripts/build_docs.ps1",
            ".github/workflows/tests.yml",
        ]

        for relative in required:
            self.assertTrue((root / relative).is_file(), relative)

    def test_visual_assets_exist(self):
        root = Path(__file__).resolve().parents[2]
        required = [
            "docs/screenshots/web-demo.png",
            "docs/screenshots/agent-trace.png",
            "docs/screenshots/demo.gif",
        ]

        for relative in required:
            path = root / relative
            self.assertTrue(path.is_file(), relative)
            self.assertGreater(path.stat().st_size, 100, relative)


if __name__ == "__main__":
    unittest.main()
