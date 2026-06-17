import json
import pathlib
import unittest


class ExtensionManifestTest(unittest.TestCase):
    def test_manifest_declares_required_mv3_entries(self):
        manifest_path = pathlib.Path(__file__).resolve().parents[2] / "extension" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["manifest_version"], 3)
        self.assertEqual(manifest["action"]["default_popup"], "popup.html")
        self.assertIn("activeTab", manifest["permissions"])
        self.assertIn("scripting", manifest["permissions"])
        self.assertIn("http://127.0.0.1:8000/*", manifest["host_permissions"])


if __name__ == "__main__":
    unittest.main()
