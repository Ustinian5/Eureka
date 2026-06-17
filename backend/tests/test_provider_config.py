import os
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app.providers import load_provider_catalog, resolve_provider_settings


class ProviderConfigTest(unittest.TestCase):
    def test_load_provider_catalog_contains_course_required_models(self):
        catalog = load_provider_catalog(Path("providers.yaml"))

        self.assertIn("qwen", catalog.providers)
        self.assertIn("kimi", catalog.providers)
        self.assertIn("deepseek", catalog.providers)
        self.assertIn("zhipu", catalog.providers)
        self.assertIn("custom", catalog.providers)

    def test_resolve_provider_uses_env_api_key_without_storing_secret_in_yaml(self):
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "secret-key"}, clear=False):
            settings = resolve_provider_settings("deepseek", Path("providers.yaml"))

        self.assertEqual(settings.api_key, "secret-key")
        self.assertIn("deepseek", settings.base_url)
        self.assertTrue(settings.model)


if __name__ == "__main__":
    unittest.main()
