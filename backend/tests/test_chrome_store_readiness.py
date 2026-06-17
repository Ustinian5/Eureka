import json
from pathlib import Path
import unittest


class ChromeStoreReadinessTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        self.extension = self.root / "extension"
        self.manifest = json.loads((self.extension / "manifest.json").read_text(encoding="utf-8"))

    def test_manifest_uses_minimal_permissions_and_dynamic_injection(self):
        self.assertEqual(self.manifest["manifest_version"], 3)
        self.assertIn("activeTab", self.manifest["permissions"])
        self.assertIn("scripting", self.manifest["permissions"])
        self.assertIn("storage", self.manifest["permissions"])
        self.assertNotIn("content_scripts", self.manifest)
        self.assertNotIn("<all_urls>", json.dumps(self.manifest))

    def test_manifest_declares_icons_options_and_csp(self):
        self.assertEqual(self.manifest["options_page"], "options.html")
        self.assertIn("content_security_policy", self.manifest)
        for size in ("16", "32", "48", "128"):
            self.assertIn(size, self.manifest["icons"])
            self.assertTrue((self.extension / self.manifest["icons"][size]).is_file())
        self.assertIn("default_icon", self.manifest["action"])

    def test_options_page_and_store_docs_exist(self):
        options_html = (self.extension / "options.html").read_text(encoding="utf-8")
        options_js = (self.extension / "options.js").read_text(encoding="utf-8")
        self.assertIn("apiEndpointInput", options_html)
        self.assertIn("chrome.storage", options_js)

        required_docs = [
            "docs/privacy-policy.md",
            "docs/chrome-store-readiness.md",
            "docs/store-listing.md",
            "scripts/package_extension.ps1",
        ]
        for relative in required_docs:
            self.assertTrue((self.root / relative).is_file(), relative)

    def test_popup_has_market_ready_controls(self):
        html = (self.extension / "popup.html").read_text(encoding="utf-8")
        js = (self.extension / "popup.js").read_text(encoding="utf-8")
        self.assertIn("cancelButton", html)
        self.assertIn("settingsButton", html)
        self.assertIn("sourceList", html)
        self.assertIn("AbortController", js)
        self.assertIn("chrome.storage", js)
        self.assertIn("exportMarkdown", js)


if __name__ == "__main__":
    unittest.main()
