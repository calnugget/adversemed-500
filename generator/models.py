"""Model registry — inlined from `inference_pipeline/run_inference.py`.

This module ships inside the `adversemed-gen` wheel so that the CLI can advertise
the supported model IDs (via `--baseline` / `--verifiers` argparse choices) without
having to import the full inference pipeline (which lives at repo root as
`inference_pipeline/` and is not shipped on PyPI in v0.1.x).

Factories are lazy: importing this module does NOT import provider SDKs
(anthropic, openai, google-genai, boto3, etc.). Providers are only imported
when a factory is actually invoked (i.e. during generation, not `--help`).

If the pipeline package is not importable on the user's PYTHONPATH when a
factory is called, a clear `ImportError` is raised pointing users at the
project's GitHub repo where the pipeline lives.

To use the real generation pipeline end-to-end in v0.1.x you must run from a
checkout of `calnugget/adversemed-500` (see V0_1_LIMITATIONS.md).
"""
from __future__ import annotations

from typing import Any, Callable

_PIPELINE_HINT = (
    "The inference_pipeline/ package is not importable. In adversemed-gen v0.1.x "
    "end-to-end generation requires running from a checkout of "
    "https://github.com/calnugget/adversemed-500 (see V0_1_LIMITATIONS.md)."
)


def _lazy_import(module_path: str, attr: str) -> Any:
    """Import an attribute from a pipeline module, raising a helpful error if missing."""
    try:
        # Prefer the shipped package name (`inference_pipeline`), fall back to
        # legacy `_pipeline` for callers running from a checkout that still uses
        # the historical path.
        try:
            mod = __import__(f"inference_pipeline.{module_path}", fromlist=[attr])
        except ModuleNotFoundError:
            mod = __import__(f"_pipeline.{module_path}", fromlist=[attr])
    except ModuleNotFoundError as e:
        raise ImportError(f"{_PIPELINE_HINT} (original error: {e})") from e
    return getattr(mod, attr)


def _get_secret(name: str) -> str:
    get_secret = _lazy_import("secrets_helper", "get_secret")
    return get_secret(name)


def _make_claude_opus():
    ClaudeOpusProvider = _lazy_import("providers.anthropic", "ClaudeOpusProvider")
    return ClaudeOpusProvider(_get_secret("anthropic"))


def _make_claude_haiku():
    ClaudeHaikuProvider = _lazy_import("providers.anthropic", "ClaudeHaikuProvider")
    return ClaudeHaikuProvider(_get_secret("anthropic"))


def _make_claude_haiku_bedrock():
    Cls = _lazy_import("providers.bedrock_proxy", "ClaudeHaikuBedrockProvider")
    return Cls()


def _make_claude_sonnet_bedrock():
    Cls = _lazy_import("providers.bedrock_proxy", "ClaudeSonnetBedrockProvider")
    return Cls()


def _make_gpt():
    GPT54MiniProvider = _lazy_import("providers.openai", "GPT54MiniProvider")
    return GPT54MiniProvider(_get_secret("openai"))


def _make_gemini():
    Gemini25ProProvider = _lazy_import("providers.google", "Gemini25ProProvider")
    return Gemini25ProProvider(_get_secret("gemini"))


def _make_deepseek():
    DeepSeekProvider = _lazy_import("providers.deepseek", "DeepSeekProvider")
    return DeepSeekProvider(_get_secret("deepseek"))


MODEL_REGISTRY: dict[str, Callable[[], Any]] = {
    # Native Anthropic
    "claude-opus-4-7": _make_claude_opus,
    "claude-haiku-4-5": _make_claude_haiku,
    # Bedrock proxy
    "claude-haiku-4-5-bedrock": _make_claude_haiku_bedrock,
    "claude-sonnet-4-bedrock": _make_claude_sonnet_bedrock,
    # Other providers
    "gpt-5.4-mini": _make_gpt,
    "gemini-2.5-pro": _make_gemini,
    "deepseek-chat": _make_deepseek,
}
