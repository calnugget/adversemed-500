"""Fetch API keys from GCP Secret Manager.

Uses the VM's default service account (already granted access to the canonical
secrets on 2026-07-06). Cached per-process to avoid repeated API calls.
"""
from __future__ import annotations

import functools
import os

# Canonical secret names — keys already in pinkgenie project Secret Manager
SECRET_NAMES = {
    "anthropic": "ANTHROPIC_API_KEY",           # native — unfunded as of 2026-08-01
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "bedrock_proxy_api_key": "BEDROCK_PROXY_API_KEY",  # x-api-key header value
    "bedrock_proxy_url": "BEDROCK_PROXY_URL",          # full POST URL for API Gateway
}

PROJECT_ID = os.environ.get("PROJECT_ID", "pinkgenie")


@functools.lru_cache(maxsize=16)
def get_secret(provider: str) -> str:
    """Fetch the API key for a provider from Secret Manager. Cached per-process."""
    if provider not in SECRET_NAMES:
        raise ValueError(f"Unknown provider {provider!r}. Known: {list(SECRET_NAMES)}")

    # Lazy import — google-cloud-secret-manager not always needed at module load
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{SECRET_NAMES[provider]}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("utf-8").strip()
