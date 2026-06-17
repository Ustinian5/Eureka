from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    base_url: str
    api_key: str
    model: str
    cors_origins: list[str]
    search_timeout_seconds: float
    llm_timeout_seconds: float


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def load_settings(env_file: str | Path = ".env") -> Settings:
    env_values = _read_env_file(Path(env_file))
    values = {**env_values, **os.environ}
    return Settings(
        base_url=values.get("BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        api_key=values.get("API_KEY", ""),
        model=values.get("MODEL", "gpt-4o-mini"),
        cors_origins=_split_csv(values.get("CORS_ORIGINS", "chrome-extension://*,http://localhost:*,http://127.0.0.1:*")),
        search_timeout_seconds=float(values.get("SEARCH_TIMEOUT_SECONDS", "10")),
        llm_timeout_seconds=float(values.get("LLM_TIMEOUT_SECONDS", "60")),
    )


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values
