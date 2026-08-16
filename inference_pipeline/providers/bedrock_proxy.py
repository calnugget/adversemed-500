"""Bedrock-proxy provider — Claude models via dad's AWS Bedrock API Gateway.

Background: Anthropic-direct credits are exhausted for Paper 1 as of 2026-08-01.
Bedrock access via a custom API Gateway → Lambda → Bedrock chain in dad's AWS
account (Waltair Tech billing) remains available. This adapter routes Paper 1's
Claude calls through that proxy instead of the native Anthropic SDK.

Two secrets needed (both in `pinkgenie` GCP project):
  - `BEDROCK_PROXY_API_KEY` — the API Gateway key (`x-api-key` header)
  - `BEDROCK_PROXY_URL` — the POST endpoint, e.g.
    https://<id>.execute-api.us-east-1.amazonaws.com/prod/invoke

Request shape (mirrors Bedrock's `InvokeModel` for Anthropic):
  {"model_id": "<bedrock-model-id>",
   "payload": {"anthropic_version": "bedrock-2023-05-31",
               "messages": [{"role": "user", "content": "..."}],
               "max_tokens": N, "temperature": T}}

Response shape is Anthropic-native, so parsing reuses `_parse_answer_and_confidence`.

Bedrock model IDs (validated in Paper 0 F-14 tests):
  - us.anthropic.claude-haiku-4-5-20251001-v1:0   ← direct match for PROTOCOL §4 Haiku 4.5
  - us.anthropic.claude-sonnet-4-20250514-v1:0    ← substitutes for Opus 4.7 (OSF Amendment #2)

Substituting Sonnet 4 for Opus 4.7 requires an OSF pre-registration amendment;
see PROTOCOL §14 Amendment #2 (draft).
"""
from __future__ import annotations

import time

from _pipeline.secrets_helper import get_secret

from .base import InferenceResponse, Provider
from .deepseek import _parse_answer_and_confidence


class _BedrockProxyBase(Provider):
    """Common Bedrock-proxy call machinery. Subclasses set model_id / _api_model / pricing."""
    provider_id = "AWS Bedrock (via proxy)"
    supports_logprobs = False  # Anthropic API on Bedrock does not expose per-token logprobs

    _api_model: str = ""  # override

    def __init__(self, api_key: str | None = None, proxy_url: str | None = None) -> None:
        # api_key = x-api-key header value; proxy_url = full POST URL
        self._api_key = api_key or get_secret("bedrock_proxy_api_key")
        self._proxy_url = proxy_url or get_secret("bedrock_proxy_url")

    def infer(
        self,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 128,
        return_logprobs: bool = False,
    ) -> InferenceResponse:
        # return_logprobs is a no-op for Bedrock/Anthropic (unsupported)
        import httpx

        body = {
            "model_id": self._api_model,
            "payload": {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        }

        t_start = time.perf_counter()
        try:
            with httpx.Client(timeout=120.0) as client:
                r = client.post(
                    self._proxy_url,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self._api_key,
                    },
                    json=body,
                )
                r.raise_for_status()
                raw = r.json()
        except Exception as e:
            wall_ms = int((time.perf_counter() - t_start) * 1000)
            return InferenceResponse(
                raw_text="",
                chosen_answer="parse_failure",
                wall_clock_ms=wall_ms,
                error=repr(e),
            )
        wall_ms = int((time.perf_counter() - t_start) * 1000)

        # Anthropic response shape: {"content": [{"type": "text", "text": "..."}], "usage": {...}}
        raw_text = "".join(
            block.get("text", "")
            for block in raw.get("content", [])
            if block.get("type") == "text"
        )
        answer_letter, verbal_conf, _raw_token = _parse_answer_and_confidence(raw_text)

        usage = raw.get("usage", {}) or {}
        prompt_tokens = int(usage.get("input_tokens", 0) or 0)
        completion_tokens = int(usage.get("output_tokens", 0) or 0)
        cost = (
            prompt_tokens / 1000 * self.input_cost_per_1k_usd
            + completion_tokens / 1000 * self.output_cost_per_1k_usd
        )

        return InferenceResponse(
            raw_text=raw_text,
            chosen_answer=answer_letter,
            verbal_confidence=verbal_conf,
            log_probability=None,
            wall_clock_ms=wall_ms,
            cost_usd=cost,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            raw_metadata={"stop_reason": raw.get("stop_reason"), "bedrock_id": self._api_model},
        )


class ClaudeHaikuBedrockProvider(_BedrockProxyBase):
    """Claude Haiku 4.5 via Bedrock proxy — direct match for PROTOCOL §4 Haiku 4.5 slot."""
    model_id = "Claude Haiku 4.5 (Bedrock)"
    _api_model = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    # AWS Bedrock pricing (verified aws.amazon.com/bedrock/pricing 2026-08-01):
    # Claude Haiku 4.5: $1/1M in, $5/1M out — parity with native Anthropic list.
    input_cost_per_1k_usd = 0.001
    output_cost_per_1k_usd = 0.005


class ClaudeSonnetBedrockProvider(_BedrockProxyBase):
    """Claude Sonnet 4 via Bedrock proxy — SUBSTITUTES for Claude Opus 4.7 in PROTOCOL §4.

    Substitution rationale: Bedrock catalog does not include Opus 4.7 as of 2026-08-01;
    Sonnet 4 is the closest available frontier-tier Claude. OSF Amendment #2 covers this
    substitution. See PROTOCOL §14 Amendment #2.
    """
    model_id = "Claude Sonnet 4 (Bedrock, substituting Opus 4.7)"
    _api_model = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    # AWS Bedrock pricing: Claude Sonnet 4: $3/1M in, $15/1M out
    input_cost_per_1k_usd = 0.003
    output_cost_per_1k_usd = 0.015
