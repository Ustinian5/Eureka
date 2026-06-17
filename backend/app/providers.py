from __future__ import annotations

import os
from pathlib import Path

from backend.app.config import Settings, load_settings
from backend.app.models import ProviderCatalog, ProviderPreset


def load_provider_catalog(path: str | Path = "providers.yaml") -> ProviderCatalog:
    yaml = _load_yaml()
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    providers: dict[str, ProviderPreset] = {}
    for provider_id, data in (payload.get("providers") or {}).items():
        providers[provider_id] = ProviderPreset(
            id=provider_id,
            name=str(data.get("name") or provider_id),
            base_url=str(data.get("base_url") or ""),
            model=str(data.get("model") or ""),
            api_key_env=str(data.get("api_key_env") or ""),
        )
    return ProviderCatalog(providers=providers)


def resolve_provider_settings(provider_id: str, path: str | Path = "providers.yaml") -> Settings:
    base_settings = load_settings()
    catalog = load_provider_catalog(path)
    preset = catalog.providers.get(provider_id) or catalog.providers["custom"]
    base_url = _expand_env(preset.base_url) or base_settings.base_url
    model = _expand_env(preset.model) or base_settings.model
    api_key = os.getenv(preset.api_key_env, "") if preset.api_key_env else ""
    if preset.id == "custom":
        api_key = base_settings.api_key
    return Settings(
        base_url=base_url.rstrip("/"),
        api_key=api_key,
        model=model,
        cors_origins=base_settings.cors_origins,
        search_timeout_seconds=base_settings.search_timeout_seconds,
        llm_timeout_seconds=base_settings.llm_timeout_seconds,
    )


def public_provider_list(path: str | Path = "providers.yaml") -> list[dict[str, str]]:
    catalog = load_provider_catalog(path)
    return [
        {"id": preset.id, "name": preset.name, "model": _expand_env(preset.model) or preset.model}
        for preset in catalog.providers.values()
    ]


def _expand_env(value: str) -> str:
    result = value
    for key, env_value in os.environ.items():
        result = result.replace("${" + key + "}", env_value)
    return result


def _load_yaml():
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required. Install dependencies from environment.yml.") from exc
    return yaml
