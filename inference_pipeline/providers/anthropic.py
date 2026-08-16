"""Anthropic (Claude) provider. Covers both Opus 4.7 and Haiku 4.5."""
from __future__ import annotations

import time

from .base import InferenceResponse, Provider
from .deepseek import _parse_answer_and_confidence  # reuse the same parser


class ClaudeOpusProvider(Provider):
    """Claude Opus 4.7 — top-tier generalist."""
    model_id = "Claude Opus 4.7"
    provider_id = "Anthropic"
    # Verified 2026-07-06 anthropic.com/pricing (list): $15/1M in, $75/1M out.
    # Batch API is 50% off — recorded separately in PROTOCOL.md §11.
    input_cost_per_1k_usd = 0.015
    output_cost_per_1k_usd = 0.075
    supports_logprobs = False  # Anthropic API does not expose per-token log-probabilities
    # Opus 4.7 rejects the `temperature` parameter with 400
    # `invalid_request_error: temperature is deprecated for this model`
    # (extended-thinking models don't accept it). Behavior is deterministic
    # regardless of temperature request. Set to False so infer() omits the
    # kwarg entirely; self-consistency will produce n identical responses on
    # Opus (confidence collapses to 1.0), which is a faithful reflection of
    # the model's capability and gets logged transparently in §Methods.
    _accepts_temperature = False

    _api_model = "claude-opus-4-7"

    def __init__(self, api_key: str):
        from anthropic import Anthropic
        self._client = Anthropic(api_key=api_key)

    def infer(
        self,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 128,
        return_logprobs: bool = False,
    ) -> InferenceResponse:
        # return_logprobs is a no-op for Anthropic (unsupported)
        t_start = time.perf_counter()
        try:
            kwargs: dict = {
                "model": self._api_model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if self._accepts_temperature:
                kwargs["temperature"] = temperature
            resp = self._client.messages.create(**kwargs)
        except Exception as e:
            wall_ms = int((time.perf_counter() - t_start) * 1000)
            return InferenceResponse(
                raw_text="", chosen_answer="parse_failure", wall_clock_ms=wall_ms, error=repr(e)
            )
        wall_ms = int((time.perf_counter() - t_start) * 1000)

        raw_text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        answer_letter, verbal_conf, _raw_token = _parse_answer_and_confidence(raw_text)

        prompt_tokens = resp.usage.input_tokens
        completion_tokens = resp.usage.output_tokens
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
            raw_metadata={"stop_reason": resp.stop_reason},
        )


class ClaudeHaikuProvider(ClaudeOpusProvider):
    """Claude Haiku 4.5 — cheap generalist for cost-conscious smoke tests."""
    model_id = "Claude Haiku 4.5"
    # Verified 2026-07-06: $1/1M in, $5/1M out
    input_cost_per_1k_usd = 0.001
    output_cost_per_1k_usd = 0.005
    # Haiku 4.5 still accepts `temperature` (verified 2026-08-01 smoke).
    _accepts_temperature = True
    _api_model = "claude-haiku-4-5-20251001"
