import unittest
import os
from pathlib import Path
from unittest.mock import patch

from backend.app.config import load_settings


class ConfigTest(unittest.TestCase):
    def test_load_settings_reads_env_file(self):
        env_text = (
            "BASE_URL=https://models.example.test/v1\n"
            "API_KEY=test-key\n"
            "MODEL=deepseek-r1\n"
        )
        env_file = Path(".env")
        with patch.dict(os.environ, {}, clear=True), patch.object(Path, "is_file", return_value=True), patch.object(Path, "read_text", return_value=env_text):
            settings = load_settings(env_file=env_file)

        self.assertEqual(settings.base_url, "https://models.example.test/v1")
        self.assertEqual(settings.api_key, "test-key")
        self.assertEqual(settings.model, "deepseek-r1")


if __name__ == "__main__":
    unittest.main()
